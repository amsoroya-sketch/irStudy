#!/usr/bin/env python3
"""
Backfill nullable ``condition_id`` links on content rows — data-grounded only.

PRD-CONDITIONS-SPINE-001.

What it does:
    - ``match_condition(item, conditions, name_fn=None)`` — a PURE function that
      links a content item to a seeded condition by normalized topic/title/
      diagnosis match, **guarded by specialty** (a specialty mismatch is never
      linked). Returns the matched ``condition["id"]`` or ``None``. Nothing is
      force-matched. ``name_fn`` selects the field-extraction order that MIRRORS
      the seed for that content type (``_mcq_name`` / ``_osce_name`` /
      ``_persona_name``); when omitted, a generic best-available order is used.
    - ``main()`` — links live content rows to conditions and writes the unmatched
      rows to ``data/amc_blueprints/_reports/unlinked.json`` (never fabricates a
      link).

CRITICAL — link via AUTHORING files, not missing DB columns:
    The ``mcqs`` table has NO ``topic`` column (conditions were DERIVED from the
    authoring-file topics by ``seed_conditions.py``). Matching a DB MCQ therefore
    requires re-deriving its authored ``topic`` from ``data/mcqs/*.json``, keyed
    by the SAME ``question_id`` the importer wrote (via ``transform_mcq``). OSCEs
    keep title-based matching (the ``osces`` table has ``station_title``).
    Personas / EMR mock patients match on specialty + chief/presenting complaint.

Correct primary keys (verified against the live schema):
    - MCQ.id (business key ``question_id``)
    - OSCE.id (business key ``osce_id``, title in ``station_title``)
    - PatientPersona.persona_id  (NOT ``.id``)
    - MockPatient.id             (UUID; business key ``mrn``)

Modes:
    --dry-run (DEFAULT): report only; the database is NOT modified.
    --apply           : UPDATE ``condition_id`` in a single transaction + commit.

Idempotent: a re-run only re-affirms existing links (matched rows are re-set to
the same id); unmatched rows are left NULL. Existing links are never nulled.

Security: no credentials are read or written; DB access uses get_database_url().
"""

from __future__ import annotations

import os
import re
import sys
import json
import argparse
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = REPO_ROOT / "backend"
DATA_DIR = REPO_ROOT / "data"
BLUEPRINT_DIR = DATA_DIR / "amc_blueprints"
REPORT_DIR = BLUEPRINT_DIR / "_reports"
UNLINKED_JSON = REPORT_DIR / "unlinked.json"

# Reuse the exact normalizers + per-type name extractors from the seed so matching
# AGREES with seeding (same specialty vocabulary, same field-precedence per type).
sys.path.insert(0, str(REPO_ROOT))
from scripts.seed_conditions import (  # noqa: E402
    normalize_name,
    normalize_specialty,
    _mcq_name,
    _osce_name,
    _persona_name,
)


def _item_name(item: Dict[str, Any]) -> Optional[str]:
    """Best available content name across the content shapes (generic fallback)."""
    return (
        normalize_name(item.get("topic"))
        or _osce_name(item)
        or _persona_name(item)
        or _mcq_name(item)
    )


def _names_match(condition_name: str, item_name: str) -> bool:
    """
    True when the condition name matches the item name (normalized, case-insensitive).

    Matches on exact equality OR when the item name CONTAINS the condition name as
    a whole word (e.g. condition "Asthma" matches item "Asthma exacerbation").
    """
    cond = re.sub(r"\s+", " ", condition_name).strip().lower()
    itm = re.sub(r"\s+", " ", item_name).strip().lower()
    if not cond or not itm:
        return False
    if cond == itm:
        return True
    # whole-word containment (word-boundary guarded, no partial-token hits)
    return bool(re.search(r"(?:^|\b)" + re.escape(cond) + r"(?:\b|$)", itm))


def match_condition(
    item: Dict[str, Any],
    conditions: List[Dict[str, Any]],
    name_fn: Optional[Callable[[Dict[str, Any]], Optional[str]]] = None,
) -> Optional[int]:
    """
    Return the id of the condition matching ``item``, or None.

    Guard: the item's specialty MUST equal the condition's specialty (a mismatch
    is never linked, even if names match). Among specialty-matching conditions,
    the longest matching name wins (most specific), for determinism.

    ``name_fn`` selects the field-extraction order (defaults to the generic
    ``_item_name``). Pass ``_mcq_name`` / ``_osce_name`` / ``_persona_name`` to
    mirror how the seed derived that content type's conditions exactly.
    """
    extractor = name_fn or _item_name
    item_spec = normalize_specialty(item.get("specialty"))
    item_name = extractor(item)
    if item_spec is None or item_name is None:
        return None

    best: Optional[Dict[str, Any]] = None
    for cond in conditions:
        cond_spec = normalize_specialty(cond.get("specialty"))
        cond_name = normalize_name(cond.get("name"))
        if cond_spec is None or cond_name is None:
            continue
        if cond_spec != item_spec:  # specialty guard
            continue
        if _names_match(cond_name, item_name):
            if best is None or len(cond_name) > len(str(best.get("name") or "")):
                best = cond

    return best.get("id") if best else None


# ---------------------------------------------------------------------------
# Best-effort DB backfill
# ---------------------------------------------------------------------------
def _db_available() -> bool:
    return bool(
        os.getenv("DATABASE_URL")
        or os.getenv("DATABASE_PASSWORD")
        or os.path.exists("/run/secrets/db_password")
    )


def _load_seeded_conditions() -> List[Dict[str, Any]]:
    fp = BLUEPRINT_DIR / "conditions.json"
    if not fp.exists():
        return []
    try:
        with open(fp, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:  # noqa: BLE001
        return []
    return data.get("conditions", []) if isinstance(data, dict) else (data or [])


def _build_mcq_authoring_map() -> Dict[str, Dict[str, Any]]:
    """
    Map ``question_id`` -> raw authored MCQ item (carrying specialty/topic/subtopic/
    title). Keyed by the SAME ``question_id`` the importer wrote, by re-running the
    importer's ``transform_mcq`` on the authoring files. This is what lets a DB MCQ
    (which has NO topic column) recover its authored topic for matching. First-seen
    wins on duplicate ids (deterministic, sorted file scan).
    """
    sys.path.insert(0, str(BACKEND_DIR / "scripts"))
    from import_mcqs import load_mcq_files, transform_mcq  # type: ignore

    mapping: Dict[str, Dict[str, Any]] = {}
    for _filename, mcq in load_mcq_files(DATA_DIR / "mcqs"):
        try:
            qid = transform_mcq(mcq)["question_id"]
        except Exception:  # noqa: BLE001
            continue
        mapping.setdefault(str(qid), mcq)
    return mapping


def main() -> int:
    """Link live content rows to conditions; emit unlinked.json."""
    parser = argparse.ArgumentParser(
        description="Backfill condition_id links on content rows (spine)."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report linked/unlinked only; do NOT modify the database (DEFAULT).",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="UPDATE condition_id in a single transaction and commit.",
    )
    args = parser.parse_args()
    apply_changes = bool(args.apply) and not args.dry_run
    mode = "APPLY (writes + commits)" if apply_changes else "DRY-RUN (no writes)"

    print("=" * 72)
    print(f"BACKFILL condition_id LINKS — {mode}")
    print("=" * 72)

    if not _db_available():
        print("[note] Database unavailable — nothing to backfill.")
        return 0

    sys.path.insert(0, str(BACKEND_DIR))
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from src.db.base import get_database_url
    from src.db.models import (  # type: ignore
        Condition,
        MCQ,
        OSCE,
        PatientPersona,
        MockPatient,
    )

    engine = create_engine(get_database_url())
    db = sessionmaker(bind=engine)()

    # Prefer live conditions; fall back to the seeded JSON.
    conditions = [
        {
            "id": c.id,
            "specialty": getattr(c.specialty, "value", str(c.specialty)),
            "name": c.name,
        }
        for c in db.query(Condition).all()
    ] or _load_seeded_conditions()
    condition_name_by_id = {
        c["id"]: c["name"] for c in conditions if c.get("id") is not None
    }

    # Recover authored MCQ topics (DB mcqs have no topic column).
    mcq_map = _build_mcq_authoring_map()
    print(f"[note] Loaded {len(mcq_map)} authored MCQ items (question_id -> topic).")

    def _mcq_item(row: Any) -> Dict[str, Any]:
        # Prefer the AUTHORED item (carries specialty + topic/subtopic/title) so
        # matching mirrors the seed. Fall back to the DB specialty when an authored
        # item is missing (e.g. IMPORTED-* ids) — that row simply fails to match.
        authored = mcq_map.get(str(row.question_id))
        if authored is not None:
            return authored
        return {"specialty": getattr(row.specialty, "value", str(row.specialty))}

    def _osce_item(row: Any) -> Dict[str, Any]:
        return {
            "specialty": getattr(row.specialty, "value", str(row.specialty)),
            "title": row.station_title,
        }

    def _persona_item(row: Any) -> Dict[str, Any]:
        # PatientPersona: match on specialty + chief_complaint (fed through the
        # persona extractor, which also considers expected_diagnosis/diagnosis).
        return {"specialty": row.specialty, "chief_complaint": row.chief_complaint}

    def _emr_item(row: Any) -> Dict[str, Any]:
        # MockPatient (EMR case): match on specialty + presenting_complaint, mapped
        # into chief_complaint so the persona extractor picks it up.
        return {"specialty": row.specialty, "chief_complaint": row.presenting_complaint}

    # (content_type, model, pk-attr, item-builder, seed name extractor)
    content_models = (
        ("mcq", MCQ, "id", _mcq_item, _mcq_name),
        ("osce", OSCE, "id", _osce_item, _osce_name),
        ("persona", PatientPersona, "persona_id", _persona_item, _persona_name),
        ("emr_case", MockPatient, "id", _emr_item, _persona_name),
    )

    unlinked: Dict[str, List[Dict[str, Any]]] = {}
    linked_counts: Dict[str, int] = {}
    changed_counts: Dict[str, int] = {}
    top_conditions: Dict[str, Dict[int, int]] = {}

    try:
        for ct, model, pk_attr, to_item, name_fn in content_models:
            linked_counts[ct] = 0
            changed_counts[ct] = 0
            unlinked[ct] = []
            top_conditions[ct] = {}
            for row in db.query(model).all():
                pk_val = getattr(row, pk_attr)
                cid = match_condition(to_item(row), conditions, name_fn=name_fn)
                if cid is None:
                    unlinked[ct].append({"pk": str(pk_val)})
                    continue
                linked_counts[ct] += 1
                top_conditions[ct][cid] = top_conditions[ct].get(cid, 0) + 1
                if getattr(row, "condition_id", None) != cid:
                    changed_counts[ct] += 1
                    if apply_changes:
                        row.condition_id = cid
            print(
                f"  {ct:<10} linked {linked_counts[ct]:>5}  "
                f"unlinked {len(unlinked[ct]):>5}  "
                f"(changed this run: {changed_counts[ct]})"
            )

        if apply_changes:
            db.commit()
            print("[OK] Committed condition_id updates in a single transaction.")
        else:
            db.rollback()
            print("[note] --dry-run: no database changes were written.")
    finally:
        db.close()

    # Which conditions receive the most links (per content type).
    print("\nTop conditions by link count:")
    for ct in ("mcq", "osce", "persona", "emr_case"):
        pairs = sorted(
            top_conditions.get(ct, {}).items(), key=lambda kv: kv[1], reverse=True
        )[:5]
        if not pairs:
            print(f"  {ct:<10} (none)")
            continue
        rendered = ", ".join(
            f"{condition_name_by_id.get(cid, cid)}={n}" for cid, n in pairs
        )
        print(f"  {ct:<10} {rendered}")

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    with open(UNLINKED_JSON, "w", encoding="utf-8") as f:
        json.dump(
            {
                "mode": "apply" if apply_changes else "dry-run",
                "linked_counts": linked_counts,
                "changed_counts": changed_counts,
                "unlinked": unlinked,
            },
            f,
            indent=2,
        )
    print(f"\n[OK] Wrote unlinked report -> {UNLINKED_JSON}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
