#!/usr/bin/env python3
"""
Idempotent importer for EMR challenging-case answer-key files
(PRD-EMR-PRACTICE-002).

Reads authored cases from ``data/emr_practice_cases/*.json`` and imports them
into the ``mock_patients`` table, mapping the answer-key (`validation_criteria`)
and clinical detail onto the ``MockPatient`` ORM object. Adapted from the
idempotent persona importer ``backend/scripts/import_mock_patients.py``
(``map_persona_to_mock_patient`` / ``main``).

Guarantees:
  * Each case is validated by the content gate BEFORE insert.
  * Import is idempotent: rows are skipped when a ``mrn`` already exists,
    so re-running inserts 0.
  * ``specialty`` / ``difficulty`` are stored lowercase (matching the enums).

Usage:
    # Live DB (reads DATABASE_URL from environment — no hardcoded credentials):
    export DATABASE_URL='postgresql://user:pass@localhost:5433/irstudy_medical'
    python backend/scripts/import_emr_practice_cases.py data/emr_practice_cases/
"""

from __future__ import annotations

import importlib.util
import json
import sys
from datetime import datetime
from pathlib import Path
from uuid import uuid4

# --- path setup -------------------------------------------------------------
_BACKEND_DIR = Path(__file__).resolve().parent.parent          # .../backend
_PROJECT_ROOT = _BACKEND_DIR.parent                            # .../irStudy
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))

from sqlalchemy.exc import IntegrityError  # noqa: E402

from src.db.models import MockPatient  # noqa: E402

# --- reuse the ONE canonical content gate (load by path) --------------------
_GATE_PATH = _PROJECT_ROOT / "scripts" / "validate_emr_practice_cases.py"
_gate_spec = importlib.util.spec_from_file_location(
    "validate_emr_practice_cases", _GATE_PATH
)
if _gate_spec is None or _gate_spec.loader is None:  # pragma: no cover
    raise ImportError(f"Cannot load content gate at {_GATE_PATH}")
_gate = importlib.util.module_from_spec(_gate_spec)
_gate_spec.loader.exec_module(_gate)
validate_case = _gate.validate_case


def build_mock_patient(case: dict) -> MockPatient:
    """Map an authored answer-key case onto a ``MockPatient`` ORM object.

    Mirrors the mapping style of ``import_mock_patients.map_persona_to_mock_patient``
    but adds the answer-key (`validation_criteria`) and the clinical-detail
    columns introduced by PRD-EMR-PRACTICE-001.
    """
    medical_history = case.get("medical_history") or {}
    mh_is_dict = isinstance(medical_history, dict)

    # Prefer explicit top-level fields, then fall back to medical_history.
    medications = case.get("medications")
    if medications is None and mh_is_dict:
        medications = medical_history.get("medications")

    allergies = case.get("allergies")
    if allergies is None and mh_is_dict:
        allergies = medical_history.get("allergies")

    demographics = case.get("demographics")
    if demographics is None:
        demographics = {
            "name": case.get("name"),
            "age": case.get("age"),
            "gender": case.get("gender"),
        }

    return MockPatient(
        id=uuid4(),
        mrn=case["mrn"],
        name=case.get("name", "Unknown Patient"),
        age=case.get("age"),
        gender=case.get("gender"),
        presenting_complaint=case.get("presenting_complaint"),
        vital_signs=case.get("vital_signs"),
        medical_history=medical_history,
        specialty=str(case.get("specialty", "")).lower(),
        difficulty=str(case.get("difficulty", "")).lower(),
        demographics=demographics,
        medications=medications,
        allergies=allergies,
        physical_exam_findings=case.get("physical_exam_findings"),
        investigation_results=case.get("investigation_results"),
        validation_criteria=case.get("validation_criteria"),
        created_at=datetime.utcnow(),
    )


def import_cases(directory: str, db) -> int:
    """Validate and idempotently import every ``*.json`` case in ``directory``.

    Args:
        directory: path containing authored case files.
        db: an open SQLAlchemy session.

    Returns:
        Number of NEW rows inserted (0 on a re-run — existing ``mrn`` skipped).
    """
    path = Path(directory)
    inserted = 0

    for json_file in sorted(path.glob("*.json")):
        with open(json_file, "r", encoding="utf-8") as fh:
            try:
                case = json.load(fh)
            except json.JSONDecodeError as exc:
                print(f"⚠️  SKIP {json_file.name}: invalid JSON ({exc})")
                continue

        ok, errors = validate_case(case)
        if not ok:
            print(f"⚠️  SKIP {json_file.name}: failed content gate -> {errors}")
            continue

        mrn = case["mrn"]
        existing = db.query(MockPatient).filter_by(mrn=mrn).first()
        if existing is not None:
            # Already imported — idempotent no-op.
            continue

        db.add(build_mock_patient(case))
        try:
            db.commit()
        except IntegrityError as exc:
            # A database-level CHECK/UNIQUE constraint rejected this row
            # (e.g. the mock_patients age-range constraint). Roll back that
            # single row and continue — keeps the run idempotent and resilient.
            db.rollback()
            print(f"⚠️  SKIP {json_file.name}: DB rejected row -> {exc.orig}")
            continue
        inserted += 1

    return inserted


def _get_session():
    """Build a session using the project's existing engine pattern.

    Reads DATABASE_URL from the environment (via ``src.db.base``) — no
    credentials are hardcoded here.
    """
    from src.db.base import SessionLocal

    return SessionLocal()


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    directory = argv[0] if argv else str(_PROJECT_ROOT / "data" / "emr_practice_cases")

    if not Path(directory).exists():
        print(f"❌ Directory not found: {directory}")
        return 2

    db = _get_session()
    try:
        inserted = import_cases(directory, db)
    finally:
        db.close()

    print("=" * 60)
    print("EMR Practice Case Import")
    print("=" * 60)
    print(f"Directory       : {directory}")
    print(f"Rows inserted   : {inserted}")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
