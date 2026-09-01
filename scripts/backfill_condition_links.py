#!/usr/bin/env python3
"""
Backfill nullable ``condition_id`` links on content rows — data-grounded only.

PRD-CONDITIONS-SPINE-001.

What it does:
    - ``match_condition(item, conditions)`` — a PURE function that links a content
      item to a seeded condition by normalized topic/title/diagnosis match,
      **guarded by specialty** (a specialty mismatch is never linked). Returns the
      matched ``condition["id"]`` or ``None``. Nothing is force-matched.
    - ``main()`` — best-effort: loads seeded conditions + live content, links what
      it can, and writes the unmatched rows to
      ``data/amc_blueprints/_reports/unlinked.json`` (never fabricates a link).

Idempotent: re-running only re-affirms existing links / leaves nulls as null.

Security: no credentials are read or written; DB access is best-effort and uses
the project's get_database_url() only.
"""

from __future__ import annotations

import os
import re
import sys
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = REPO_ROOT / "backend"
DATA_DIR = REPO_ROOT / "data"
BLUEPRINT_DIR = DATA_DIR / "amc_blueprints"
REPORT_DIR = BLUEPRINT_DIR / "_reports"
UNLINKED_JSON = REPORT_DIR / "unlinked.json"

# Reuse the exact normalizers from the seed so matching AGREES with seeding.
sys.path.insert(0, str(REPO_ROOT))
from scripts.seed_conditions import (  # noqa: E402
    normalize_name,
    normalize_specialty,
    _mcq_name,
    _osce_name,
    _persona_name,
)


def _item_name(item: Dict[str, Any]) -> Optional[str]:
    """Best available content name across the three content shapes."""
    return (
        normalize_name(item.get("topic"))
        or _osce_name(item)
        or _persona_name(item)
        or _mcq_name(item)
    )


def _names_match(condition_name: str, item_name: str) -> bool:
    """
    True when the condition name matches the item name (normalized, case-insensitive).

    Matches on exact equality OR when the item name STARTS WITH the condition name
    as a whole word (e.g. condition "Asthma" matches item "Asthma exacerbation").
    """
    cond = re.sub(r"\s+", " ", condition_name).strip().lower()
    itm = re.sub(r"\s+", " ", item_name).strip().lower()
    if not cond or not itm:
        return False
    if cond == itm:
        return True
    # whole-word prefix / containment (word-boundary guarded, no partial-token hits)
    return bool(re.search(r"(?:^|\b)" + re.escape(cond) + r"(?:\b|$)", itm))


def match_condition(
    item: Dict[str, Any], conditions: List[Dict[str, Any]]
) -> Optional[int]:
    """
    Return the id of the condition matching ``item``, or None.

    Guard: the item's specialty MUST equal the condition's specialty (a mismatch
    is never linked, even if names match). Among specialty-matching conditions,
    the longest matching name wins (most specific), for determinism.
    """
    item_spec = normalize_specialty(item.get("specialty"))
    item_name = _item_name(item)
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


def main() -> int:
    """Link live content rows to conditions; emit unlinked.json. Best-effort."""
    if not _db_available():
        print("[note] Database unavailable — nothing to backfill.")
        return 0

    sys.path.insert(0, str(BACKEND_DIR))
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from src.db.base import get_database_url
    from src.db.models import Condition, MCQ, OSCE, PatientPersona, MockPatient  # type: ignore

    engine = create_engine(get_database_url())
    db = sessionmaker(bind=engine)()

    # Prefer live conditions; fall back to the seeded JSON.
    conditions = [
        {"id": c.id, "specialty": getattr(c.specialty, "value", str(c.specialty)), "name": c.name}
        for c in db.query(Condition).all()
    ] or _load_seeded_conditions()

    unlinked: Dict[str, List[Dict[str, Any]]] = {}
    linked_counts: Dict[str, int] = {}

    content_models = (
        ("mcq", MCQ, lambda r: {"specialty": getattr(r.specialty, "value", str(r.specialty)),
                                "topic": None, "title": None, "id": r.id}),
        ("osce", OSCE, lambda r: {"specialty": getattr(r.specialty, "value", str(r.specialty)),
                                  "title": r.station_title, "id": r.id}),
        ("persona", PatientPersona, lambda r: {"specialty": r.specialty,
                                               "chief_complaint": r.chief_complaint, "id": r.id}),
        ("emr_case", MockPatient, lambda r: {"specialty": r.specialty,
                                             "chief_complaint": r.presenting_complaint, "id": r.id}),
    )

    try:
        for ct, model, to_item in content_models:
            linked_counts[ct] = 0
            unlinked[ct] = []
            for row in db.query(model).all():
                item = to_item(row)
                cid = match_condition(item, conditions)
                if cid is None:
                    unlinked[ct].append({"id": str(item.get("id"))})
                    continue
                row.condition_id = cid
                linked_counts[ct] += 1
            print(f"  {ct}: linked {linked_counts[ct]}, unlinked {len(unlinked[ct])}")
        db.commit()
    finally:
        db.close()

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    with open(UNLINKED_JSON, "w", encoding="utf-8") as f:
        json.dump({"unlinked": unlinked, "linked_counts": linked_counts}, f, indent=2)
    print(f"[OK] Wrote unlinked report -> {UNLINKED_JSON}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
