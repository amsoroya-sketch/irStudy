#!/usr/bin/env python3
"""
Fix mislabelled MCQ specialties in the LIVE PostgreSQL `mcqs` table.

CONTEXT (already diagnosed + measured — see the task brief):
    Old imports mislabelled MCQ specialties. Comparing every DB row's `specialty`
    to its authoring-file specialty (matched by question_id via transform_mcq over
    data/mcqs/*.json, ignoring *_backup_*/*_with_images*), 322 of 1,670 matched
    rows are wrong (e.g. the "respiratory=1" bug — 122 rows authored as respiratory
    were stored as general_practice).

WHAT THIS DOES:
    - Builds question_id -> authored_specialty from the authoring JSON files, reusing
      transform_mcq() and _is_ignored_file() from backend/scripts/import_mcqs.py.
    - For every DB MCQ whose question_id is in the map AND whose current specialty
      differs from the authored specialty, UPDATEs ONLY `mcqs.specialty`.
    - Never touches question_text, options, correct_answer, explanation, citations, etc.
    - Never inserts or deletes rows — this only relabels.

SAFETY:
    - --dry-run (DEFAULT): computes and prints correction counts (from->to) and the
      projected final distribution. Touches nothing.
    - --apply: performs all UPDATEs inside a SINGLE transaction, commits once, then
      prints the actual final distribution.
    - Idempotent: re-running --dry-run after --apply reports 0 corrections.
    - No hardcoded credentials: DB URL comes from get_database_url() (loads .env).

Usage:
    set -a; . backend/.env; set +a
    cd backend && source venv/bin/activate
    python ../scripts/fix_mcq_specialty_labels.py --dry-run
    python ../scripts/fix_mcq_specialty_labels.py --apply
"""

import sys
import json
import argparse
from pathlib import Path
from collections import Counter, defaultdict

# ---------------------------------------------------------------------------
# Path wiring
#   - project_root/data/mcqs/*.json ......... authoring source of truth
#   - project_root/backend .................. `src.*` imports (models, db.base)
#   - project_root/backend/scripts .......... reuse transform_mcq/_is_ignored_file
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = PROJECT_ROOT / "backend"
BACKEND_SCRIPTS_DIR = BACKEND_DIR / "scripts"
DATA_MCQS_DIR = PROJECT_ROOT / "data" / "mcqs"

sys.path.insert(0, str(BACKEND_DIR))
sys.path.insert(0, str(BACKEND_SCRIPTS_DIR))

# Reuse the authoritative transform + ignore rules (no re-implementation).
from import_mcqs import transform_mcq, _is_ignored_file  # noqa: E402


def _extract_items(data):
    """Return the list of raw MCQ dicts from either {mcqs:[...]} / {questions:[...]}
    shapes or a bare list. Mirrors import_mcqs._extract_list intent but kept local
    so a shape we don't recognise degrades to an empty list (skip), never a crash."""
    if isinstance(data, dict):
        for key in ("mcqs", "questions"):
            if isinstance(data.get(key), list):
                return data[key]
        for value in data.values():
            if isinstance(value, list) and value:
                return value
        return []
    if isinstance(data, list):
        return data
    return []


def build_authored_specialty_map() -> dict[str, str]:
    """question_id -> authored specialty (mapped enum *value* string), built from
    data/mcqs/*.json using the same transform_mcq the importer uses.

    If the same question_id appears in multiple files with conflicting specialties,
    the last-scanned (sorted, deterministic) value wins — matching importer file order.
    """
    mapping: dict[str, str] = {}
    if not DATA_MCQS_DIR.exists():
        print(f"[ERROR] Data directory not found: {DATA_MCQS_DIR}")
        return mapping

    candidates = sorted(
        p for p in DATA_MCQS_DIR.glob("*.json") if not _is_ignored_file(p)
    )
    for file_path in candidates:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"[WARN] Invalid JSON in {file_path.name}: {e}")
            continue
        except Exception as e:  # noqa: BLE001
            print(f"[WARN] Reading {file_path.name}: {e}")
            continue

        for item in _extract_items(data):
            if not isinstance(item, dict):
                continue
            rec = transform_mcq(item)
            qid = rec["question_id"]
            mapping[str(qid)] = rec["specialty"]

    return mapping


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Relabel mislabelled MCQ specialties from authoring JSON."
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--dry-run",
        action="store_true",
        help="Compute + print corrections and projected distribution. Touch nothing (DEFAULT).",
    )
    group.add_argument(
        "--apply",
        action="store_true",
        help="Perform the UPDATEs in a single committed transaction.",
    )
    args = parser.parse_args()
    apply_changes = bool(args.apply)  # default (no flag) == dry-run

    print("=" * 66)
    print("MCQ Specialty Label Correction")
    print("=" * 66)
    print(f"Mode:   {'APPLY (writes committed)' if apply_changes else 'DRY RUN (no writes)'}")
    print(f"Source: {DATA_MCQS_DIR}")
    print("")

    print("Building authored question_id -> specialty map...")
    authored = build_authored_specialty_map()
    print(f"[OK] Authored MCQs mapped: {len(authored)}\n")
    if not authored:
        print("[ERROR] No authored specialties found — aborting.")
        return 1

    # DB imports deferred so a bad import doesn't mask the map-build step.
    try:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from src.db.models import MCQ, MedicalSpecialty
        from src.db.base import get_database_url
    except Exception as e:  # noqa: BLE001
        print(f"[ERROR] Could not import DB layer: {e}")
        return 1

    try:
        engine = create_engine(get_database_url())
        db = sessionmaker(bind=engine)()
    except Exception as e:  # noqa: BLE001
        print(f"[ERROR] Database connection failed: {e}")
        return 1

    corrected = 0
    matched = 0
    transition_counts: Counter[tuple[str, str]] = Counter()
    projected: Counter[str] = Counter()
    to_update: list[tuple[MCQ, MedicalSpecialty]] = []

    try:
        total_before = db.query(MCQ).count()

        for mcq in db.query(MCQ).all():
            current = (
                mcq.specialty.value
                if isinstance(mcq.specialty, MedicalSpecialty)
                else str(mcq.specialty)
            )
            qid = str(mcq.question_id)
            authored_spec = authored.get(qid)

            if authored_spec is None:
                # No authoring record — leave untouched.
                projected[current] += 1
                continue

            matched += 1
            if authored_spec != current:
                transition_counts[(current, authored_spec)] += 1
                corrected += 1
                projected[authored_spec] += 1
                to_update.append((mcq, MedicalSpecialty(authored_spec)))
            else:
                projected[current] += 1

        # ---- Report ----
        print("-" * 66)
        print(f"DB rows total:            {total_before}")
        print(f"Matched to authoring map: {matched}")
        print(f"Corrections needed:       {corrected}")
        print("-" * 66)
        if transition_counts:
            print("Corrections (from -> to : count):")
            for (frm, to), cnt in sorted(
                transition_counts.items(), key=lambda kv: (-kv[1], kv[0])
            ):
                print(f"  {frm:<20} -> {to:<20} : {cnt}")
        else:
            print("No corrections needed (already consistent).")
        print("-" * 66)
        print("Projected final specialty distribution:")
        for spec, cnt in sorted(projected.items(), key=lambda kv: (-kv[1], kv[0])):
            print(f"  {spec:<24} {cnt}")
        print(f"  {'TOTAL':<24} {sum(projected.values())}")
        print("-" * 66)

        if not apply_changes:
            print("\nDRY RUN complete — no rows were modified.")
            return 0

        if corrected == 0:
            print("\nNothing to apply — database already consistent (idempotent).")
            return 0

        # ---- Apply inside a single transaction ----
        print(f"\nApplying {corrected} specialty corrections (single transaction)...")
        for mcq, new_specialty in to_update:
            mcq.specialty = new_specialty
        db.commit()
        print(f"[DONE] Committed {corrected} corrections.")

        # ---- Actual post-apply distribution ----
        actual: Counter[str] = Counter()
        for (spec,) in db.query(MCQ.specialty).all():
            actual[spec.value if isinstance(spec, MedicalSpecialty) else str(spec)] += 1
        print("-" * 66)
        print("Actual final specialty distribution (post-commit):")
        for spec, cnt in sorted(actual.items(), key=lambda kv: (-kv[1], kv[0])):
            print(f"  {spec:<24} {cnt}")
        print(f"  {'TOTAL':<24} {sum(actual.values())}")
        print("-" * 66)
        total_after = db.query(MCQ).count()
        print(f"Row count before: {total_before}  after: {total_after}  "
              f"({'UNCHANGED' if total_after == total_before else 'CHANGED!'})")
        return 0

    except Exception as e:  # noqa: BLE001
        db.rollback()
        print(f"[ERROR] Rolled back — no changes committed: {e}")
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
