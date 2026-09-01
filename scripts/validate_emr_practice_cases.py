#!/usr/bin/env python3
"""
Content gate for EMR challenging-case answer-key files (PRD-EMR-PRACTICE-002).

Validates each authored case in `data/emr_practice_cases/*.json` against the
answer-key contract BEFORE it can be imported into `mock_patients`.

Contract (see PRD-EMR-PRACTICE-002 "Answer-key contract"):
  top-level: mrn, name, age, gender, specialty, difficulty,
             presenting_complaint, vital_signs, medical_history, validation_criteria
  validation_criteria: presenting_scenario, task, expected, critical_errors, must_not_miss
  expected: subjective, objective, assessment, plan  (each a non-empty list)

Checks performed:
  * all contract keys present
  * `critical_errors` has >= 1 entry
  * each `expected.{subjective,objective,assessment,plan}` non-empty
  * `specialty` in MedicalSpecialty enum values
  * `difficulty` in DifficultyLevel enum values
  * `presenting_scenario` + `task` non-empty
  * unique `mrn` across a directory (validate_dir)

Pure functions, no database access. `specialty`/`difficulty` are validated
against the real enums in `backend/src/db/models.py` so the gate stays in sync
with the schema.

Usage:
    python scripts/validate_emr_practice_cases.py data/emr_practice_cases/
    # exit 0 => all cases valid ; exit 1 => one or more invalid
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

# --- make backend importable so we can read the canonical enums -------------
_PROJECT_ROOT = Path(__file__).resolve().parents[1]
_BACKEND = _PROJECT_ROOT / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

# Importing src.db.models constructs a DATABASE_URL string (no connection is
# opened at import time). Provide a harmless in-memory default so the gate can
# run without any DB credentials / environment configured.
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

from src.db.models import DifficultyLevel, MedicalSpecialty  # noqa: E402

# Enum value sets (lowercase) the gate validates against.
_SPECIALTY_VALUES = {e.value for e in MedicalSpecialty}
_DIFFICULTY_VALUES = {e.value for e in DifficultyLevel}

# Contract key definitions.
_TOP_LEVEL_KEYS = (
    "mrn", "name", "age", "gender", "specialty", "difficulty",
    "presenting_complaint", "vital_signs", "medical_history",
    "validation_criteria",
)
_VC_KEYS = (
    "presenting_scenario", "task", "expected", "critical_errors", "must_not_miss",
)
_EXPECTED_SECTIONS = ("subjective", "objective", "assessment", "plan")


def _non_empty_str(value) -> bool:
    return isinstance(value, str) and value.strip() != ""


def validate_case(case: dict) -> tuple[bool, list[str]]:
    """Validate a single case dict against the answer-key contract.

    Returns:
        (ok, errors) where `ok` is True only when `errors` is empty.
    """
    errors: list[str] = []

    if not isinstance(case, dict):
        return False, ["case is not a JSON object"]

    # 1. Top-level contract keys present.
    for key in _TOP_LEVEL_KEYS:
        if key not in case:
            errors.append(f"missing key: {key}")

    # 2. specialty / difficulty within enums (case-insensitive).
    specialty = str(case.get("specialty", "")).lower()
    if specialty not in _SPECIALTY_VALUES:
        errors.append(
            f"specialty '{case.get('specialty')}' not in MedicalSpecialty enum"
        )
    difficulty = str(case.get("difficulty", "")).lower()
    if difficulty not in _DIFFICULTY_VALUES:
        errors.append(
            f"difficulty '{case.get('difficulty')}' not in DifficultyLevel enum"
        )

    # 3. validation_criteria block.
    vc = case.get("validation_criteria")
    if not isinstance(vc, dict):
        errors.append("validation_criteria missing or not an object")
    else:
        for key in _VC_KEYS:
            if key not in vc:
                errors.append(f"missing validation_criteria.{key}")

        # scenario + task non-empty
        if not _non_empty_str(vc.get("presenting_scenario")):
            errors.append("validation_criteria.presenting_scenario is empty")
        if not _non_empty_str(vc.get("task")):
            errors.append("validation_criteria.task is empty")

        # critical_errors >= 1
        critical_errors = vc.get("critical_errors")
        if not isinstance(critical_errors, list) or len(critical_errors) < 1:
            errors.append("validation_criteria.critical_errors must have >=1 entry")

        # must_not_miss present as a list (contract key)
        if not isinstance(vc.get("must_not_miss"), list):
            errors.append("validation_criteria.must_not_miss must be a list")

        # expected sections each a non-empty list
        expected = vc.get("expected")
        if not isinstance(expected, dict):
            errors.append("validation_criteria.expected missing or not an object")
        else:
            for section in _EXPECTED_SECTIONS:
                value = expected.get(section)
                if not isinstance(value, list) or len(value) == 0:
                    errors.append(f"expected.{section} is empty")

    return (len(errors) == 0, errors)


def validate_dir(path: str) -> tuple[bool, dict]:
    """Validate every ``*.json`` case in a directory.

    Also enforces globally unique ``mrn`` across the directory.

    Returns:
        (ok, report) where `report` maps filename -> list[error] for every
        invalid file (empty dict when all files pass).
    """
    directory = Path(path)
    report: dict[str, list[str]] = {}
    seen_mrn: dict[str, str] = {}
    all_ok = True

    for json_file in sorted(directory.glob("*.json")):
        try:
            with open(json_file, "r", encoding="utf-8") as fh:
                case = json.load(fh)
        except json.JSONDecodeError as exc:
            report[json_file.name] = [f"invalid JSON: {exc}"]
            all_ok = False
            continue

        ok, errors = validate_case(case)

        # unique mrn check (directory scope)
        mrn = case.get("mrn") if isinstance(case, dict) else None
        if mrn is not None:
            if mrn in seen_mrn:
                errors = errors + [
                    f"duplicate mrn: {mrn} (also in {seen_mrn[mrn]})"
                ]
                ok = False
            else:
                seen_mrn[mrn] = json_file.name

        if not ok:
            all_ok = False
            report[json_file.name] = errors

    return all_ok, report


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    if not argv:
        print("Usage: validate_emr_practice_cases.py <directory>")
        return 2

    directory = argv[0]
    if not Path(directory).exists():
        print(f"❌ Directory not found: {directory}")
        return 2

    ok, report = validate_dir(directory)
    total = len(list(Path(directory).glob("*.json")))

    if ok:
        print(f"✅ PASSED: all {total} case(s) valid in {directory}")
        return 0

    print(f"❌ FAILED: {len(report)}/{total} invalid case(s) in {directory}")
    for filename, errors in report.items():
        print(f"  - {filename}:")
        for err in errors:
            print(f"      • {err}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
