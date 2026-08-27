"""Local fixtures for EMR assessment-engine tests (PRD-EMR-PRACTICE-001)."""
from types import SimpleNamespace
from uuid import uuid4
from datetime import datetime

import pytest

from src.db.models import MockPatient, EMRSession

# Answer-key mirrored from the STEMI hard case used in the test module.
_STEMI_CRITERIA = {
    "presenting_scenario": "58yo male, central crushing chest pain 40 min, diaphoretic.",
    "task": "Document assessment and initial management as admitting RMO.",
    "expected": {
        "subjective": ["SOCRATES of pain", "cardiac risk factors", "sildenafil/erectile-drug use"],
        "objective": ["BP in both arms", "ECG within 10 minutes"],
        "assessment": ["ACS/STEMI primary", "aortic dissection considered"],
        "plan": ["aspirin 300 mg chewed", "serial troponin", "STEMI pathway / cardiology", "analgesia"],
    },
    "critical_errors": ["nitrates given despite hypotension / inferior-RV infarct / recent sildenafil"],
    "must_not_miss": ["aortic dissection considered"],
}


@pytest.fixture
def seeded_hard_case(db_session, test_user):
    """A MockPatient carrying STEMI answer-key + an in_progress EMRSession owned by test_user."""
    patient = MockPatient(
        id=uuid4(),
        mrn=f"HARD-{uuid4().hex[:8]}",
        name="Test Patient",
        age=58,
        gender="Male",
        presenting_complaint="Central crushing chest pain",
        vital_signs={"hr": 96, "bp": "148/92"},
        medical_history=["hypertension"],
        specialty="cardiology",
        difficulty="hard",
        validation_criteria=_STEMI_CRITERIA,
    )
    db_session.add(patient)
    db_session.flush()

    session = EMRSession(
        id=uuid4(),
        user_id=test_user.id,
        patient_id=patient.id,
        emr_system="epic",
        specialty="cardiology",
        difficulty="hard",
        started_at=datetime.utcnow(),
        status="in_progress",
    )
    db_session.add(session)
    db_session.commit()

    return SimpleNamespace(session_id=session.id, patient=patient, session=session)
