"""
Integration tests for EMR API endpoints

COVERAGE:
- Session management (create, get, submit)
- Dashboard analytics (progress, specialty, history)
- Authentication and authorization
- Validation layers
- Error handling

TARGET: 20+ tests, 100% pass rate
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import uuid

from src.main import app
from src.db.base import Base, get_db
from src.db.models import User, UserRole
from src.auth.security import hash_password, create_access_token
from src.api.v1.emr.sessions import MockPatient, EMRSession, EMRSOAPNote


# ============================================================================
# TEST DATABASE SETUP
# ============================================================================

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_emr.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture(scope="function")
def db():
    """Create test database for each test"""
    Base.metadata.create_all(bind=engine)
    yield TestingSessionLocal()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    """FastAPI test client"""
    return TestClient(app)


@pytest.fixture
def test_user(db):
    """Create test user"""
    user = User(
        email="student@test.com",
        password_hash=hash_password("SecurePassword123!"),
        full_name="Test Student",
        role=UserRole.STUDENT,
        is_active=True,
        is_verified=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user):
    """Generate authentication headers"""
    access_token = create_access_token({"user_id": test_user.id, "email": test_user.email})
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def mock_patient(db):
    """Create mock patient for testing"""
    patient = MockPatient(
        id=uuid.uuid4(),
        mrn="MRN12345",
        name="John Doe",
        age=45,
        gender="Male",
        presenting_complaint="Chest pain",
        vital_signs={"bp": "145/90", "hr": 95, "rr": 18, "temp": 37.2, "spo2": 98},
        medical_history={"conditions": ["Hypertension"], "medications": ["Amlodipine 5mg"]},
        specialty="cardiology",
        difficulty="intermediate",
    )
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


# ============================================================================
# SESSION MANAGEMENT TESTS (9 tests)
# ============================================================================


def test_create_session_success(client, auth_headers, mock_patient):
    """Test POST /api/v1/emr/sessions - Success"""
    response = client.post(
        "/api/v1/emr/sessions",
        json={
            "mock_patient_id": str(mock_patient.id),
            "emr_system": "epic",
            "session_type": "practice",
        },
        headers=auth_headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert "session_id" in data
    assert data["emr_system"] == "epic"
    assert data["status"] == "in_progress"
    assert data["mock_patient"]["name"] == "John Doe"


def test_create_session_invalid_patient(client, auth_headers):
    """Test POST /api/v1/emr/sessions - Invalid patient UUID"""
    response = client.post(
        "/api/v1/emr/sessions",
        json={
            "mock_patient_id": str(uuid.uuid4()),  # Non-existent patient
            "emr_system": "epic",
            "session_type": "practice",
        },
        headers=auth_headers,
    )

    assert response.status_code == 404
    assert "not found" in response.json()["error"]["message"]


def test_create_session_unauthorized(client, mock_patient):
    """Test POST /api/v1/emr/sessions - No authentication"""
    response = client.post(
        "/api/v1/emr/sessions",
        json={
            "mock_patient_id": str(mock_patient.id),
            "emr_system": "epic",
            "session_type": "practice",
        },
    )

    assert response.status_code == 401


def test_get_session_success(client, auth_headers, mock_patient, test_user, db):
    """Test GET /api/v1/emr/sessions/{id} - Success"""
    # Create session first
    session = EMRSession(
        id=uuid.uuid4(),
        user_id=test_user.id,
        patient_id=mock_patient.id,
        specialty="cardiology",
        difficulty="intermediate",
        status="in_progress",
    )
    db.add(session)
    db.commit()

    response = client.get(f"/api/v1/emr/sessions/{session.id}", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == str(session.id)
    assert data["status"] == "in_progress"
    assert data["mock_patient"]["name"] == "John Doe"


def test_get_session_not_found(client, auth_headers):
    """Test GET /api/v1/emr/sessions/{id} - Session not found"""
    response = client.get(f"/api/v1/emr/sessions/{uuid.uuid4()}", headers=auth_headers)

    assert response.status_code == 404


def test_get_session_unauthorized_access(client, auth_headers, mock_patient, db):
    """Test GET /api/v1/emr/sessions/{id} - Access other user's session"""
    # Create session with different user
    other_user = User(
        email="other@test.com",
        password_hash=hash_password("OtherPassword123!"),
        full_name="Other User",
        role=UserRole.STUDENT,
        is_active=True,
        is_verified=True,
    )
    db.add(other_user)
    db.commit()

    session = EMRSession(
        id=uuid.uuid4(),
        user_id=other_user.id,  # Different user
        patient_id=mock_patient.id,
        specialty="cardiology",
        difficulty="intermediate",
        status="in_progress",
    )
    db.add(session)
    db.commit()

    response = client.get(f"/api/v1/emr/sessions/{session.id}", headers=auth_headers)

    assert response.status_code == 404  # Not found (authorization check)


def test_submit_session_success(client, auth_headers, mock_patient, test_user, db):
    """Test POST /api/v1/emr/sessions/{id}/submit - Success"""
    # Create session
    session = EMRSession(
        id=uuid.uuid4(),
        user_id=test_user.id,
        patient_id=mock_patient.id,
        specialty="cardiology",
        difficulty="intermediate",
        status="in_progress",
    )
    db.add(session)
    db.commit()

    # Submit SOAP note
    response = client.post(
        f"/api/v1/emr/sessions/{session.id}/submit",
        json={
            "soap_note": {
                "subjective": "45-year-old male presenting with 2-hour history of central chest pain, radiating to left arm. Pain started at rest, severity 8/10, associated with diaphoresis and nausea. No previous cardiac history.",
                "objective": "BP 145/90 mmHg, HR 95 bpm, RR 18/min, Temp 37.2°C, SpO2 98% on room air. Cardiovascular: S1 S2 normal, no murmurs. Chest clear bilaterally. ECG shows ST elevation in leads V2-V4.",
                "assessment": "1. Acute coronary syndrome - STEMI likely (anterior wall). 2. Differential: Unstable angina, myocarditis, aortic dissection (less likely given ECG changes). 3. High risk for complications - requires urgent intervention.",
                "plan": "1. Immediate: Activate cath lab for primary PCI. 2. Aspirin 300mg PO stat, Ticagrelor 180mg PO stat. 3. High-flow oxygen if SpO2 <94%. 4. IV access, bloods: FBC, UEC, troponin, lipids. 5. Morphine 5mg IV for pain. 6. Cardiology consult urgent.",
            },
            "prescriptions": [
                {"medication": "Aspirin", "dose": "300mg", "route": "PO", "frequency": "stat"},
                {
                    "medication": "Ticagrelor",
                    "dose": "180mg",
                    "route": "PO",
                    "frequency": "stat",
                },
            ],
            "pathology_orders": [
                {
                    "test_name": "Troponin I",
                    "urgency": "urgent",
                    "clinical_notes": "?Acute MI",
                }
            ],
        },
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert "validation_result" in data
    assert data["validation_result"]["overall_score"] > 0
    assert data["validation_result"]["pass_fail"] in ["PASS", "BORDERLINE", "FAIL"]


def test_submit_session_already_submitted(client, auth_headers, mock_patient, test_user, db):
    """Test POST /api/v1/emr/sessions/{id}/submit - Already submitted"""
    # Create submitted session
    session = EMRSession(
        id=uuid.uuid4(),
        user_id=test_user.id,
        patient_id=mock_patient.id,
        specialty="cardiology",
        difficulty="intermediate",
        status="validated",  # Already submitted
        submitted_at=datetime.utcnow(),
    )
    db.add(session)
    db.commit()

    response = client.post(
        f"/api/v1/emr/sessions/{session.id}/submit",
        json={
            "soap_note": {
                "subjective": "Test subjective content with sufficient word count to pass minimum validation requirements.",
                "objective": "Test objective content with sufficient word count to pass minimum validation requirements.",
                "assessment": "Test assessment content with sufficient word count to pass minimum validation requirements.",
                "plan": "Test plan content with sufficient word count to pass minimum validation requirements.",
            },
            "prescriptions": [],
            "pathology_orders": [],
        },
        headers=auth_headers,
    )

    assert response.status_code == 400
    assert "already submitted" in response.json()["error"]["message"]


def test_submit_session_invalid_soap_note(client, auth_headers, mock_patient, test_user, db):
    """Test POST /api/v1/emr/sessions/{id}/submit - Invalid SOAP note (too short)"""
    # Create session
    session = EMRSession(
        id=uuid.uuid4(),
        user_id=test_user.id,
        patient_id=mock_patient.id,
        specialty="cardiology",
        difficulty="intermediate",
        status="in_progress",
    )
    db.add(session)
    db.commit()

    response = client.post(
        f"/api/v1/emr/sessions/{session.id}/submit",
        json={
            "soap_note": {
                "subjective": "Short",  # Too short (< 50 chars)
                "objective": "Short",
                "assessment": "Short",
                "plan": "Short",
            },
            "prescriptions": [],
            "pathology_orders": [],
        },
        headers=auth_headers,
    )

    # Pydantic validation should reject (min_length=50)
    assert response.status_code == 422
    assert "error" in response.json()


# ============================================================================
# DASHBOARD TESTS (7 tests)
# ============================================================================


def test_overall_progress_no_sessions(client, auth_headers):
    """Test GET /api/v1/emr/dashboard/overall-progress - No sessions"""
    response = client.get("/api/v1/emr/dashboard/overall-progress", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["total_sessions"] == 0
    assert data["sessions_passed"] == 0
    assert data["average_score"] == 0.0


def test_overall_progress_with_sessions(client, auth_headers, mock_patient, test_user, db):
    """Test GET /api/v1/emr/dashboard/overall-progress - With sessions"""
    # Create multiple sessions
    for i in range(3):
        session = EMRSession(
            id=uuid.uuid4(),
            user_id=test_user.id,
            patient_id=mock_patient.id,
            specialty="cardiology",
            difficulty="intermediate",
            status="validated",
            validation_score=75.0 + i * 5,
            elapsed_time_seconds=900,
            score_breakdown={"pass_fail": "PASS"},
        )
        db.add(session)
    db.commit()

    response = client.get("/api/v1/emr/dashboard/overall-progress", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["total_sessions"] == 3
    assert data["sessions_passed"] == 3
    assert data["average_score"] > 70


def test_specialty_detail_success(client, auth_headers, mock_patient, test_user, db):
    """Test GET /api/v1/emr/dashboard/specialty-detail/{specialty} - Success"""
    # Create cardiology sessions
    for i in range(2):
        session = EMRSession(
            id=uuid.uuid4(),
            user_id=test_user.id,
            patient_id=mock_patient.id,
            specialty="cardiology",
            difficulty="intermediate",
            status="validated",
            validation_score=80.0,
            score_breakdown={"pass_fail": "PASS", "layer_1_rule_based": {"errors": []}},
        )
        db.add(session)
    db.commit()

    response = client.get(
        "/api/v1/emr/dashboard/specialty-detail/cardiology", headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["specialty"] == "cardiology"
    assert data["sessions_attempted"] == 2
    assert data["sessions_passed"] == 2


def test_specialty_detail_no_sessions(client, auth_headers):
    """Test GET /api/v1/emr/dashboard/specialty-detail/{specialty} - No sessions"""
    response = client.get(
        "/api/v1/emr/dashboard/specialty-detail/neurology", headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["specialty"] == "neurology"
    assert data["sessions_attempted"] == 0


def test_session_history_success(client, auth_headers, mock_patient, test_user, db):
    """Test GET /api/v1/emr/dashboard/session-history - Success"""
    # Create sessions
    for i in range(5):
        session = EMRSession(
            id=uuid.uuid4(),
            user_id=test_user.id,
            patient_id=mock_patient.id,
            specialty="cardiology",
            difficulty="intermediate",
            status="validated",
            submitted_at=datetime.utcnow(),
            validation_score=75.0,
            elapsed_time_seconds=900,
            score_breakdown={"pass_fail": "PASS"},
        )
        db.add(session)
    db.commit()

    response = client.get("/api/v1/emr/dashboard/session-history", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["total_count"] == 5
    assert len(data["sessions"]) == 5
    assert data["pagination"]["limit"] == 20


def test_session_history_pagination(client, auth_headers, mock_patient, test_user, db):
    """Test GET /api/v1/emr/dashboard/session-history - Pagination"""
    # Create 25 sessions
    for i in range(25):
        session = EMRSession(
            id=uuid.uuid4(),
            user_id=test_user.id,
            patient_id=mock_patient.id,
            specialty="cardiology",
            difficulty="intermediate",
            status="validated",
            submitted_at=datetime.utcnow(),
            validation_score=75.0,
        )
        db.add(session)
    db.commit()

    response = client.get(
        "/api/v1/emr/dashboard/session-history?limit=10&offset=0", headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total_count"] == 25
    assert len(data["sessions"]) == 10
    assert data["pagination"]["has_more"] is True


def test_session_history_filtering(client, auth_headers, mock_patient, test_user, db):
    """Test GET /api/v1/emr/dashboard/session-history - Filtering by specialty"""
    # Create sessions in different specialties
    cardiology_patient = mock_patient

    neurology_patient = MockPatient(
        id=uuid.uuid4(),
        mrn="MRN67890",
        name="Jane Smith",
        age=50,
        gender="Female",
        presenting_complaint="Headache",
        specialty="neurology",
        difficulty="intermediate",
    )
    db.add(neurology_patient)
    db.commit()

    # Cardiology session
    session1 = EMRSession(
        id=uuid.uuid4(),
        user_id=test_user.id,
        patient_id=cardiology_patient.id,
        specialty="cardiology",
        status="validated",
        submitted_at=datetime.utcnow(),
    )
    db.add(session1)

    # Neurology session
    session2 = EMRSession(
        id=uuid.uuid4(),
        user_id=test_user.id,
        patient_id=neurology_patient.id,
        specialty="neurology",
        status="validated",
        submitted_at=datetime.utcnow(),
    )
    db.add(session2)
    db.commit()

    response = client.get(
        "/api/v1/emr/dashboard/session-history?specialty=cardiology", headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert all(s["specialty"] == "cardiology" for s in data["sessions"])


# ============================================================================
# VALIDATION TESTS (4 tests)
# ============================================================================


def test_validation_layer1_completeness(client, auth_headers, mock_patient, test_user, db):
    """Test Layer 1 validation - Completeness checks"""
    session = EMRSession(
        id=uuid.uuid4(),
        user_id=test_user.id,
        patient_id=mock_patient.id,
        specialty="cardiology",
        status="in_progress",
    )
    db.add(session)
    db.commit()

    # Submit with incomplete SOAP note
    response = client.post(
        f"/api/v1/emr/sessions/{session.id}/submit",
        json={
            "soap_note": {
                "subjective": "Brief history that meets minimum character requirements but could be more detailed.",
                "objective": "Basic examination findings that meet minimum character requirements.",
                "assessment": "Short differential diagnosis list that meets minimum character requirements.",
                "plan": "Basic management plan that meets minimum character requirements.",
            },
            "prescriptions": [],
            "pathology_orders": [],
        },
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert "layer_1_rule_based" in data["validation_result"]
    assert data["validation_result"]["layer_1_rule_based"]["score"] >= 0


def test_validation_american_terminology_detection(
    client, auth_headers, mock_patient, test_user, db
):
    """Test Layer 1 validation - American terminology detection"""
    session = EMRSession(
        id=uuid.uuid4(),
        user_id=test_user.id,
        patient_id=mock_patient.id,
        specialty="cardiology",
        status="in_progress",
    )
    db.add(session)
    db.commit()

    # Submit with American terminology
    response = client.post(
        f"/api/v1/emr/sessions/{session.id}/submit",
        json={
            "soap_note": {
                "subjective": "Patient reports taking acetaminophen for pain relief. Good response to medication with no adverse effects noted. History spans several months.",
                "objective": "Vital signs stable. Physical examination unremarkable. No acute distress observed. Patient comfortable.",
                "assessment": "Pain management adequate with current regimen. No red flags identified. Continue monitoring response.",
                "plan": "Continue acetaminophen as needed. Call 911 if severe symptoms develop. Follow up in clinic.",
            },
            "prescriptions": [],
            "pathology_orders": [],
        },
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    layer1 = data["validation_result"]["layer_1_rule_based"]
    # Should have errors about American terminology
    assert any("paracetamol" in err or "acetaminophen" in err for err in layer1["errors"])


def test_validation_pass_threshold(client, auth_headers, mock_patient, test_user, db):
    """Test validation pass/fail thresholds (≥70 = PASS, 60-69 = BORDERLINE, <60 = FAIL)"""
    session = EMRSession(
        id=uuid.uuid4(),
        user_id=test_user.id,
        patient_id=mock_patient.id,
        specialty="cardiology",
        status="in_progress",
    )
    db.add(session)
    db.commit()

    # Submit high-quality SOAP note
    response = client.post(
        f"/api/v1/emr/sessions/{session.id}/submit",
        json={
            "soap_note": {
                "subjective": "45-year-old male presenting with acute onset central chest pain, severity 8/10, radiating to left arm. Started 2 hours ago while at rest. Associated symptoms include diaphoresis, nausea, and shortness of breath. No previous cardiac history. Denies recent trauma or exertion.",
                "objective": "BP 145/90 mmHg, HR 95 bpm regular, RR 18/min, Temp 37.2°C, SpO2 98% room air. Patient appears anxious and diaphoretic. Cardiovascular examination: JVP not elevated, S1 S2 normal, no murmurs or gallops. Chest clear to auscultation bilaterally. No peripheral oedema. ECG shows ST elevation in anteroseptal leads (V1-V4).",
                "assessment": "1. Acute STEMI (anterior wall) - ECG changes consistent with acute transmural infarction. 2. Differential diagnoses to consider but less likely given presentation: unstable angina (excluded by ECG), acute pericarditis (pattern not consistent), aortic dissection (no BP differential, no back pain). High-risk presentation requiring immediate intervention.",
                "plan": "1. Immediate cath lab activation for primary PCI (door-to-balloon <90 min). 2. Dual antiplatelet therapy: Aspirin 300mg PO stat, Ticagrelor 180mg PO stat. 3. High-flow oxygen if SpO2 <94%. 4. IV access ×2, bloods: FBC, UEC, troponin, lipids, coagulation studies. 5. Morphine 5mg IV for pain control. 6. Urgent cardiology consultation. 7. Continuous cardiac monitoring and vitals q5min. 8. Inform family of diagnosis and treatment plan.",
            },
            "prescriptions": [
                {"medication": "Aspirin", "dose": "300mg", "route": "PO", "frequency": "stat"}
            ],
            "pathology_orders": [
                {
                    "test_name": "Troponin I",
                    "urgency": "urgent",
                    "clinical_notes": "Acute STEMI - serial cardiac markers",
                }
            ],
        },
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    # Should achieve PASS status
    assert data["validation_result"]["pass_fail"] in ["PASS", "BORDERLINE"]


def test_validation_time_tracking(client, auth_headers, mock_patient, test_user, db):
    """Test validation includes accurate time tracking"""
    import time

    session = EMRSession(
        id=uuid.uuid4(),
        user_id=test_user.id,
        patient_id=mock_patient.id,
        specialty="cardiology",
        status="in_progress",
    )
    db.add(session)
    db.commit()

    # Add a small delay to ensure elapsed_time > 0
    time.sleep(1)

    response = client.post(
        f"/api/v1/emr/sessions/{session.id}/submit",
        json={
            "soap_note": {
                "subjective": "Detailed patient history covering all relevant aspects of the presenting complaint and associated symptoms.",
                "objective": "Comprehensive physical examination findings including vital signs and system-specific examination results.",
                "assessment": "Well-reasoned differential diagnosis with clear clinical reasoning and appropriate risk stratification.",
                "plan": "Evidence-based management plan with clear immediate actions, investigations, and follow-up arrangements.",
            },
            "prescriptions": [],
            "pathology_orders": [],
        },
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["validation_result"]["time_taken_seconds"] >= 1


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
