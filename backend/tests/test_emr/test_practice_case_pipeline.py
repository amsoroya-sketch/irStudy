# FILE: backend/tests/test_emr/test_practice_case_pipeline.py
import json, copy
from pathlib import Path
import pytest

from scripts_emr.validate_practice_cases import validate_case, validate_dir  # thin import shim
from backend.scripts.import_emr_practice_cases import build_mock_patient, import_cases

VALID = {
    "mrn": "EMRP-0001", "name": "Test Case", "age": 58, "gender": "male",
    "specialty": "cardiology", "difficulty": "hard",
    "presenting_complaint": "central chest pain",
    "vital_signs": {"bp": "150/90", "hr": 92, "spo2": 97},
    "medical_history": {"conditions": ["hypertension"]},
    "validation_criteria": {
        "presenting_scenario": "58yo male, central crushing chest pain 40 min.",
        "task": "Document assessment and initial management.",
        "expected": {"subjective": ["SOCRATES"], "objective": ["ECG <10min"],
                     "assessment": ["STEMI"], "plan": ["aspirin 300mg"]},
        "critical_errors": ["nitrates in RV infarct"],
        "must_not_miss": ["aortic dissection considered"],
    },
}

# Test 1: valid case passes the gate
def test_valid_case_passes():
    ok, errors = validate_case(VALID)
    assert ok and errors == []

# Test 2: missing critical_errors -> reject
def test_no_critical_error_rejected():
    c = copy.deepcopy(VALID); c["validation_criteria"]["critical_errors"] = []
    ok, errors = validate_case(c)
    assert not ok and any("critical_error" in e for e in errors)

# Test 3: empty expected section -> reject
def test_empty_expected_section_rejected():
    c = copy.deepcopy(VALID); c["validation_criteria"]["expected"]["plan"] = []
    ok, errors = validate_case(c)
    assert not ok and any("expected.plan" in e for e in errors)

# Test 4: bad specialty enum -> reject
def test_bad_specialty_rejected():
    c = copy.deepcopy(VALID); c["specialty"] = "wizardry"
    ok, errors = validate_case(c)
    assert not ok and any("specialty" in e for e in errors)

# Test 5: missing scenario/task -> reject
def test_missing_scenario_task_rejected():
    c = copy.deepcopy(VALID); c["validation_criteria"]["task"] = ""
    ok, errors = validate_case(c)
    assert not ok

# Test 6: build_mock_patient maps validation_criteria onto the ORM object
def test_build_mock_patient_sets_criteria():
    mp = build_mock_patient(VALID)
    assert mp.validation_criteria["critical_errors"] == ["nitrates in RV infarct"]
    assert mp.specialty == "cardiology" and mp.difficulty == "hard"

# Test 7: import is idempotent (re-run adds 0 by mrn)
def test_import_idempotent(db_session, tmp_path):
    f = tmp_path / "EMRP-0001.json"; f.write_text(json.dumps(VALID))
    n1 = import_cases(str(tmp_path), db_session)
    n2 = import_cases(str(tmp_path), db_session)
    assert n1 == 1 and n2 == 0
    from src.db.models import MockPatient
    rows = db_session.query(MockPatient).filter_by(mrn="EMRP-0001").all()
    assert len(rows) == 1 and rows[0].validation_criteria is not None

# Test 8: all 24 authored cases pass the gate (fixture dir)
def test_authored_cases_all_valid():
    d = Path("data/emr_practice_cases")
    if not d.exists():
        pytest.skip("authored cases not present in this environment")
    ok, report = validate_dir(str(d))
    assert ok, f"invalid cases: {report}"
    assert len(list(d.glob('*.json'))) >= 24
