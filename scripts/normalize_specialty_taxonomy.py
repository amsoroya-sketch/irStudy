#!/usr/bin/env python3
"""
Normalize free-text ``specialty`` values onto the ``MedicalSpecialty`` enum.

Two live tables carry human-authored ``specialty`` strings that drifted from the
controlled ``MedicalSpecialty`` vocabulary (14 lowercase snake_case values in
``backend/src/db/models.py``):

    * ``patient_personas.specialty`` (String)  — feeds mock-exam specialty
      selection; 5 Title-Case values are non-conforming.
    * ``html_osce_notes.specialty`` (String)   — a free-text NOTE CATEGORY; 7
      clinical categories map cleanly onto the enum, while 3 are genuine note
      categories (NOT clinical specialties) and are LEFT UNCHANGED.

Design guarantees
-----------------
* **Format-only normalization** — casing/spelling is fixed; genuinely-different
  specialties are NEVER merged. In ``patient_personas`` the 5 non-conforming
  labels each map to an enum value that is NOT already present among the 6
  already-lowercase rows, so the distinct-specialty count stays 11 (verified in
  the summary the script prints).
* **Idempotent** — the plan is computed from the rows actually present; a value
  already equal to its target produces no UPDATE, so a re-run changes 0 rows.
* **Data-driven & precise** — each UPDATE matches the EXACT stored string
  (parameterized) and sets the enum value; nothing is fuzzy-matched.
* **Category-preserving** — ``html_osce_notes`` labels that are note categories
  rather than clinical specialties (``Medicine``, ``Ethics & Communication``,
  ``Mock OSCE Stations``) are deliberately absent from ``SPECIALTY_MAP`` and are
  reported as "intentionally left as category labels".

Modes
-----
    --dry-run (DEFAULT) : print the planned UPDATEs + counts; touch nothing.
    --apply             : run all UPDATEs in ONE transaction, then commit.

Security: no credentials are read or written; DB access uses
``get_database_url()`` (env / Docker-secret sourced), imported lazily so this
module stays importable (for unit tests) without a live database.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = REPO_ROOT / "backend"

# ---------------------------------------------------------------------------
# Canonical taxonomy map — free-text label -> MedicalSpecialty enum value.
#
# Keys are matched CASE-INSENSITIVELY (normalized via ``_norm``: strip + lower).
# Every VALUE below is a member of the ``MedicalSpecialty`` enum (asserted at
# runtime in ``main`` against the real enum, and against ``VALID_ENUM_VALUES``
# below in the unit tests). Note-category labels that are NOT clinical
# specialties are intentionally ABSENT so they are left untouched.
# ---------------------------------------------------------------------------
SPECIALTY_MAP: Dict[str, str] = {
    # --- patient_personas: the 5 Title-Case non-conforming values -----------
    "cardiology": "cardiology",            # Cardiology       -> cardiology
    "emergency": "emergency_medicine",     # Emergency        -> emergency_medicine
    "general practice": "general_practice",  # General Practice -> general_practice
    "pediatrics": "paediatrics",           # Pediatrics (US)  -> paediatrics (AU)
    "respiratory": "respiratory",          # Respiratory      -> respiratory
    # --- html_osce_notes: the 7 clinical categories -------------------------
    "musculoskeletal": "musculoskeletal",  # Musculoskeletal  -> musculoskeletal
    "ophthalmology": "ophthalmology",      # Ophthalmology    -> ophthalmology
    "psychiatry": "psychiatry",            # Psychiatry       -> psychiatry
    "surgery": "surgery",                  # Surgery          -> surgery
    "urology": "urology",                  # Urology          -> urology
    "paediatrics": "paediatrics",          # Paediatrics      -> paediatrics
    "obstetrics & gynecology": "obstetrics_gynaecology",  # -> obstetrics_gynaecology
}

# html_osce_notes labels that are genuine NOTE CATEGORIES, not clinical
# specialties. Deliberately absent from SPECIALTY_MAP; reported, never changed.
LEFT_AS_CATEGORY: frozenset = frozenset(
    {"Medicine", "Ethics & Communication", "Mock OSCE Stations"}
)

# The 14 MedicalSpecialty enum values (mirror of backend/src/db/models.py).
# Used for a dependency-free sanity check in the unit tests; ``main`` also
# cross-checks against the live enum so drift is caught at runtime.
VALID_ENUM_VALUES: frozenset = frozenset(
    {
        "cardiology",
        "respiratory",
        "gastroenterology",
        "neurology",
        "psychiatry",
        "endocrinology",
        "emergency_medicine",
        "general_practice",
        "paediatrics",
        "obstetrics_gynaecology",
        "surgery",
        "ophthalmology",
        "urology",
        "musculoskeletal",
    }
)

# Tables (+ column) to normalize. mock_patients / emr_sessions / osce_study_notes
# are intentionally excluded (already conforming / empty).
TARGET_TABLES: Tuple[Tuple[str, str], ...] = (
    ("patient_personas", "specialty"),
    ("html_osce_notes", "specialty"),
)


def _norm(value: str) -> str:
    """Normalize a label for case-insensitive lookup (strip + lower)."""
    return value.strip().lower()


def resolve_target(current_value: Optional[str]) -> Optional[str]:
    """Return the enum value ``current_value`` should become, or None.

    None means "not in the taxonomy map" -> leave the row unchanged. A value
    that maps to itself (e.g. an already-lowercase ``surgery``) returns that
    same value, which the planner treats as a no-op (keeps the run idempotent).
    """
    if current_value is None:
        return None
    return SPECIALTY_MAP.get(_norm(current_value))


def plan_table(
    counts: Dict[str, int],
) -> Tuple[List[Tuple[str, str, int]], List[Tuple[str, int]], List[Tuple[str, int]]]:
    """Compute the UPDATE plan for one table from its current value->count map.

    A value is "already conforming" (a no-op) when it is a bare
    ``MedicalSpecialty`` enum value already — whether or not it also appears as a
    self-mapping key in ``SPECIALTY_MAP`` (e.g. an already-lowercase
    ``endocrinology`` that has no map key still needs no change). Only values
    that are neither a valid enum value nor a map key are "untouched" — these are
    the genuine free-text note CATEGORIES (``LEFT_AS_CATEGORY``).

    Returns a 3-tuple:
        updates  : [(old_value, new_value, row_count), ...]  new != old
        no_ops   : [(value, row_count), ...]  already a valid enum value
        untouched: [(value, row_count), ...]  not a specialty (category label)
    """
    updates: List[Tuple[str, str, int]] = []
    no_ops: List[Tuple[str, int]] = []
    untouched: List[Tuple[str, int]] = []
    for value, n in sorted(counts.items()):
        target = resolve_target(value)
        if target is not None and target != value:
            updates.append((value, target, n))
        elif value in VALID_ENUM_VALUES:
            # Already a conforming enum value (target is self, or not in map).
            no_ops.append((value, n))
        else:
            untouched.append((value, n))
    return updates, no_ops, untouched


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Normalize free-text specialty values onto MedicalSpecialty."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the planned UPDATEs + counts; do NOT modify the DB (DEFAULT).",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Run all UPDATEs in one transaction and commit.",
    )
    args = parser.parse_args()
    apply_changes = bool(args.apply) and not args.dry_run
    mode = "APPLY (writes + commits)" if apply_changes else "DRY-RUN (no writes)"

    print("=" * 72)
    print(f"NORMALIZE specialty TAXONOMY — {mode}")
    print("=" * 72)

    # Lazy imports: keep the module importable (unit tests) without a live DB.
    sys.path.insert(0, str(BACKEND_DIR))
    from sqlalchemy import create_engine, text  # noqa: E402
    from sqlalchemy.orm import sessionmaker  # noqa: E402
    from src.db.base import get_database_url  # type: ignore  # noqa: E402
    from src.db.models import MedicalSpecialty  # type: ignore  # noqa: E402

    # Drift guard: every map target must be a real enum value.
    live_enum = {e.value for e in MedicalSpecialty}
    assert live_enum == set(VALID_ENUM_VALUES), (
        "MedicalSpecialty enum drifted from VALID_ENUM_VALUES: "
        f"{sorted(live_enum ^ set(VALID_ENUM_VALUES))}"
    )
    bad_targets = sorted(set(SPECIALTY_MAP.values()) - live_enum)
    assert not bad_targets, f"SPECIALTY_MAP has non-enum targets: {bad_targets}"

    engine = create_engine(get_database_url())
    session = sessionmaker(bind=engine)()

    total_updates = 0
    try:
        for table, column in TARGET_TABLES:
            rows = session.execute(
                text(
                    f"SELECT {column} AS v, COUNT(*) AS n "
                    f"FROM {table} GROUP BY {column}"
                )
            ).all()
            counts = {r.v: r.n for r in rows if r.v is not None}
            distinct_before = len(counts)

            updates, no_ops, untouched = plan_table(counts)

            print(f"\n--- {table}.{column} ---")
            print(f"  distinct values (before): {distinct_before}")
            if updates:
                print(f"  UPDATES ({len(updates)}):")
                for old, new, n in updates:
                    print(f"    {old!r:32} -> {new!r:24} ({n} rows)")
            else:
                print("  UPDATES (0): nothing to change")
            if no_ops:
                print(f"  already conforming ({len(no_ops)}):")
                for value, n in no_ops:
                    print(f"    {value!r:32} ({n} rows)")
            if untouched:
                print("  intentionally left as category labels "
                      f"({len(untouched)}):")
                for value, n in untouched:
                    tag = "" if value in LEFT_AS_CATEGORY else "  [WARN unmapped]"
                    print(f"    {value!r:32} ({n} rows){tag}")

            # Projected distinct count after applying updates (no merges expected).
            projected = set(counts)
            for old, new, _n in updates:
                projected.discard(old)
                projected.add(new)
            print(f"  distinct values (projected after): {len(projected)}")

            if apply_changes:
                for old, new, _n in updates:
                    session.execute(
                        text(
                            f"UPDATE {table} SET {column} = :new "
                            f"WHERE {column} = :old"
                        ),
                        {"new": new, "old": old},
                    )
            total_updates += sum(n for _o, _nw, n in updates)

        if apply_changes:
            session.commit()
            print(f"\n[APPLIED] Committed {total_updates} row updates.")
        else:
            print(f"\n[DRY-RUN] Would update {total_updates} rows. No changes made.")
    except Exception:  # noqa: BLE001 - re-raise after rollback
        session.rollback()
        raise
    finally:
        session.close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
