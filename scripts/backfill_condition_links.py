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
    Personas match on specialty + expected diagnosis / chief complaint. EMR mock
    patients have NO diagnosis column, so they match on the expected diagnosis
    carried in ``validation_criteria.expected.assessment[0]`` (the SOAP "A"),
    falling back to the source OSCE title then the presenting complaint — never
    the presenting complaint alone, which is a SYMPTOM, not a DIAGNOSIS.

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
    resolve_specialty,
    specialty_from_filename,
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


def _emr_diagnosis(validation_criteria: Any) -> Optional[str]:
    """Primary expected diagnosis for an EMR case, from the SOAP assessment.

    A ``MockPatient`` (EMR practice case) has NO diagnosis column — its
    ``presenting_complaint`` is a SYMPTOM (e.g. "chest pain"), which essentially
    never string-matches a condition NAME (a DIAGNOSIS, e.g. "Acute Coronary
    Syndrome"). The authoritative expected diagnosis is instead carried in
    ``validation_criteria.expected.assessment`` (the SOAP "A"): its FIRST line is
    the leading clinical impression, and later lines are explicitly differentials
    ("Consider ... as differentials"). Only the first line is used — matching on
    the whole assessment would wrongly link a case to a differential (e.g. an
    asthma case's assessment also names pneumothorax/anaphylaxis).

    The leading clause (before an em-dash / colon / parenthesis severity
    qualifier) is returned so a concise condition NAME can match it, e.g.
    "Acute coronary syndrome — likely STEMI ..." -> "Acute coronary syndrome".
    Returns None when no assessment text is present (never fabricated).
    """
    if not isinstance(validation_criteria, dict):
        return None
    expected = validation_criteria.get("expected")
    if not isinstance(expected, dict):
        return None
    assessment = expected.get("assessment")
    if isinstance(assessment, list):
        primary = next((a for a in assessment if isinstance(a, str) and a.strip()), None)
    elif isinstance(assessment, str):
        primary = assessment
    else:
        primary = None
    if not primary:
        return None
    # Keep only the leading impression clause: split at the first whitespace-led
    # em-dash / hyphen / colon / open-paren qualifier (drops severity notes and
    # confirmatory caveats), then normalize exactly as the seed does.
    lead = re.split(r"\s+[—\-:(]", primary, maxsplit=1)[0]
    return normalize_name(lead)


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
    # Mirror the seed: resolve via own specialty -> metadata.specialty ->
    # filename hint, so "unknown"/None rows from specialty-scoped files link to
    # the conditions the seed derived for them (same widened logic on both sides).
    item_spec = resolve_specialty(item)
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
        # Attach the filename-derived specialty hint so an authored MCQ whose own
        # specialty is "unknown"/None (e.g. week3_respiratory_*) still resolves —
        # exactly as the seed did when it derived that MCQ's condition.
        if isinstance(mcq, dict):
            mcq.setdefault("_specialty_hint", specialty_from_filename(_filename))
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

    # OSCE title lookup for the EMR fallback chain (source_osce_id -> station_title).
    osce_title_by_id = {
        o.id: o.station_title for o in db.query(OSCE.id, OSCE.station_title).all()
    }

    def _emr_item(row: Any) -> Dict[str, Any]:
        # MockPatient (EMR case) has NO diagnosis column. The expected diagnosis is
        # carried in validation_criteria.expected.assessment[0]; presenting_complaint
        # is only a SYMPTOM (rarely matches a condition NAME). Provide a fallback
        # chain via keys the persona extractor reads in order (expected_diagnosis ->
        # topic -> chief_complaint): expected diagnosis -> source OSCE title ->
        # presenting_complaint. resolve_specialty still specialty-guards the match.
        return {
            "specialty": row.specialty,
            "expected_diagnosis": _emr_diagnosis(row.validation_criteria),
            "topic": osce_title_by_id.get(row.source_osce_id),
            "chief_complaint": row.presenting_complaint,
        }

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
