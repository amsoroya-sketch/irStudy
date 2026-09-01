"""Local fixtures for EMR assessment-engine tests (PRD-EMR-PRACTICE-001)."""
import os
import sys
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4
from datetime import datetime

import pytest


# ---------------------------------------------------------------------------
# Vault override (scoped to the EMR unit-test package)
# ---------------------------------------------------------------------------
# The EMR endpoint/engine tests here run entirely on the in-memory SQLite
# session (get_db is overridden by the global `client` fixture) and authenticate
# with JWTs signed by the SECRET_KEY env var. They do NOT touch HashiCorp Vault
# at runtime. The global session-scoped `setup_vault` fixture, however, skips the
# whole suite when it cannot (re)initialise Vault secrets on localhost:8200 —
# which happens whenever the shared Vault on that port isn't the project's dev
# instance. This override replaces that gate with a no-op for THIS package only,
# so these Vault-independent tests execute instead of being skipped. It does not
# weaken any assertion and leaves the global fixture untouched for other suites.
@pytest.fixture(scope="session", autouse=True)
def setup_vault():
    os.environ.setdefault("VAULT_ADDR", "http://localhost:8200")
    os.environ.setdefault("VAULT_TOKEN", "dev-only-token-change-in-prod")
    os.environ.setdefault("VAULT_ROOT_TOKEN", "dev-only-token-change-in-prod")
    yield

# Make the project root importable so tests can reach the content-gate shim
# (`scripts_emr.validate_practice_cases`) and the importer
# (`backend.scripts.import_emr_practice_cases`) — PRD-EMR-PRACTICE-002.
_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

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
