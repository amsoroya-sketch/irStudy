"""
Integration tests for AI OSCE Simulation System API endpoints (PRD_AI_OSCE_001)

Tests:
- Patient persona listing and retrieval (2 endpoints)
- OSCE session creation and management (4 endpoints)
- Conversation transcript access
- AI Examiner scoring retrieval
- End-to-end OSCE practice workflow

COVERAGE REQUIREMENTS:
- All 6 endpoints tested
- Happy paths + error cases
- Authentication/authorization checks
- Data validation
- 404/400/401 status codes
- End-to-end integration flow

AMC CLINICAL EXAM CONTEXT:
- 8-minute stations (480 seconds)
- 15-mark rubric (9/15 to pass)
- Progressive disclosure patient interaction
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from uuid import uuid4
from datetime import datetime, timezone

from src.db.models import PatientPersona, OSCEAttemptAI, OSCEScoreAI, User


# ================================================================
# FIXTURES
# ================================================================

@pytest.fixture
def sample_personas(db: Session):
    """Create 3 sample patient personas for testing"""
    personas = [
        PatientPersona(
            persona_id=str(uuid4()),
            persona_code="CARD-001-CHEST-PAIN",
            name="John Smith",
            age=55,
            gender="Male",
            occupation="Office worker",
            cultural_background="Anglo-Australian",
            preferred_language="English",
            specialty="cardiology",
            chief_complaint="Chest pain for 2 hours",
            opening_statement="I've had this terrible crushing pain in my chest...",
            symptoms={"immediate": ["chest pain", "left arm pain"]},
            medical_history={"volunteer": ["Type 2 diabetes", "hyperlipidemia"]},
            emotional_profile={"baseline_state": "ANXIOUS_GUARDED"},
            rag_query_hints=["acute coronary syndrome", "STEMI"],
            key_differentials=["STEMI", "unstable angina", "PE"],
            critical_actions=["ECG within 10 minutes", "aspirin 300mg"],
            difficulty_level="intermediate",
            estimated_pass_rate=67.5,
            amc_blueprint_area="Cardiovascular - Acute Coronary Syndromes",
            amc_competencies=["Clinical reasoning", "Emergency management"],
            is_active=True,
        ),
        PatientPersona(
            persona_id=str(uuid4()),
            persona_code="RESP-002-ASTHMA",
            name="Sarah Lee",
            age=28,
            gender="Female",
            occupation="Teacher",
            cultural_background="Chinese-Australian",
            preferred_language="English",
            specialty="respiratory",
            chief_complaint="Shortness of breath",
            opening_statement="I can't breathe properly...",
            symptoms={"immediate": ["wheezing", "chest tightness"]},
            medical_history={"volunteer": ["Asthma since childhood"]},
            emotional_profile={"baseline_state": "ANXIOUS_FEARFUL"},
            rag_query_hints=["asthma exacerbation"],
            key_differentials=["Asthma exacerbation", "pneumonia"],
            critical_actions=["Peak flow measurement", "salbutamol"],
            difficulty_level="foundation",
            estimated_pass_rate=78.0,
            amc_blueprint_area="Respiratory - Asthma Management",
            amc_competencies=["Clinical reasoning"],
            is_active=True,
        ),
        PatientPersona(
            persona_id=str(uuid4()),
            persona_code="EMERG-003-SEPSIS",
            name="Margaret Wong",
            age=72,
            gender="Female",
            occupation="Retired",
            cultural_background="Vietnamese-Australian",
            preferred_language="English",
            specialty="emergency_medicine",
            chief_complaint="Fever and confusion",
            opening_statement="My daughter brought me in...",
            symptoms={"immediate": ["fever", "confusion", "hypotension"]},
            medical_history={"volunteer": ["Recurrent urinary tract infections"]},
            emotional_profile={"baseline_state": "CONFUSED_DISORIENTED"},
            rag_query_hints=["sepsis", "septic shock"],
            key_differentials=["Urosepsis", "pneumonia"],
            critical_actions=["Blood cultures", "IV antibiotics within 1 hour"],
            difficulty_level="advanced",
            estimated_pass_rate=52.5,
            amc_blueprint_area="Emergency Medicine - Sepsis Recognition",
            amc_competencies=["Emergency management", "Clinical reasoning"],
            is_active=True,
        ),
    ]
    
    for persona in personas:
        db.add(persona)
    db.commit()
    
    return personas


@pytest.fixture
def inactive_persona(db: Session):
    """Create an inactive persona for testing 404 behavior"""
    persona = PatientPersona(
        persona_id=str(uuid4()),
        persona_code="INACTIVE-001",
        name="Inactive Patient",
        age=40,
        gender="Male",
        specialty="cardiology",
        chief_complaint="Test",
        opening_statement="Test",
        symptoms={},
        medical_history={},
        emotional_profile={},
        difficulty_level="foundation",
        is_active=False,  # INACTIVE
    )
    db.add(persona)
    db.commit()
    return persona


@pytest.fixture
def test_user(db: Session):
    """Create test user from auth_headers fixture logic"""
    from src.db.models import UserRole
    
    user = User(
        email="test_osce_user@example.com",
        password_hash="$2b$12$fakehashfortest",
        full_name="Test OSCE User",
        role=UserRole.STUDENT,
        is_active=True,
        is_verified=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_user_token(test_user: User):
    """Generate JWT token for test user"""
    from src.auth.security import create_access_token
    
    token = create_access_token(data={"sub": test_user.email, "user_id": test_user.id})
    return token


@pytest.fixture
def sample_osce_session(db: Session, test_user: User, sample_personas: list):
    """Create sample OSCE session"""
    persona = sample_personas[0]
    
    attempt = OSCEAttemptAI(
        attempt_id=str(uuid4()),
        user_id=str(test_user.id),
        persona_id=persona.persona_id,
        session_type="individual",
        started_at=datetime.now(timezone.utc),
        conversation_history=[
            {"role": "patient", "message": "I've had this terrible chest pain...", "timestamp": "2026-02-23T10:30:15+00:00"},
            {"role": "student", "message": "Can you describe the pain?", "timestamp": "2026-02-23T10:30:45+00:00"},
        ],
        emotional_state_transitions=[{"state": "ANXIOUS_GUARDED", "timestamp": "2026-02-23T10:30:00+00:00"}],
        student_actions=[{"action": "introduced self", "timestamp": "2026-02-23T10:30:10+00:00"}],
        was_completed=False,
        session_state='in_progress',
    )
    
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    
    return attempt


@pytest.fixture
def completed_osce_session(db: Session, test_user: User, sample_personas: list):
    """Create completed OSCE session for scoring tests"""
    persona = sample_personas[0]
    
    attempt = OSCEAttemptAI(
        attempt_id=str(uuid4()),
        user_id=str(test_user.id),
        persona_id=persona.persona_id,
        session_type="individual",
        started_at=datetime.now(timezone.utc),
        ended_at=datetime.now(timezone.utc),
        duration_seconds=480,
        conversation_history=[
            {"role": "patient", "message": "I've had this terrible chest pain...", "timestamp": "2026-02-23T10:30:15+00:00"},
            {"role": "student", "message": "Can you describe the pain?", "timestamp": "2026-02-23T10:30:45+00:00"},
        ],
        emotional_state_transitions=[{"state": "ANXIOUS_GUARDED", "timestamp": "2026-02-23T10:30:00+00:00"}],
        student_actions=[{"action": "introduced self", "timestamp": "2026-02-23T10:30:10+00:00"}],
        was_completed=True,
        session_state='finalized',
    )
    
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    
    return attempt


@pytest.fixture
def sample_score(db: Session, completed_osce_session: OSCEAttemptAI):
    """Create sample AI Examiner score"""
    score = OSCEScoreAI(
        score_id=str(uuid4()),
        attempt_id=completed_osce_session.attempt_id,
        communication_score=2,
        clinical_reasoning_score=3,
        information_gathering_score=3,
        management_score=2,
        professionalism_score=2,
        ai_examiner_feedback={"overall": "Good systematic approach to history taking"},
        strengths=["Clear communication", "Systematic history"],
        areas_for_improvement=["Safety netting could be stronger"],
        critical_errors=[],
        scored_at=datetime.now(timezone.utc),
        scoring_model_version="claude-sonnet-4-5",
    )
    
    db.add(score)
    db.commit()
    db.refresh(score)
    
    return score


@pytest.fixture
def other_user(db: Session):
    """Create another user for authorization testing"""
    from src.db.models import UserRole
    
    user = User(
        email="other_user@example.com",
        password_hash="$2b$12$fakehashfortest",
        full_name="Other User",
        role=UserRole.STUDENT,
        is_active=True,
        is_verified=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def other_user_session(db: Session, other_user: User, sample_personas: list):
    """Create OSCE session for other user (for authorization tests)"""
    persona = sample_personas[0]
    
    attempt = OSCEAttemptAI(
        attempt_id=str(uuid4()),
        user_id=str(other_user.id),
        persona_id=persona.persona_id,
        session_type="individual",
        started_at=datetime.now(timezone.utc),
        conversation_history=[],
        emotional_state_transitions=[],
        student_actions=[],
        was_completed=False,
        session_state='initialized',
    )
    
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    
    return attempt


# ================================================================
# TESTS: Patient Personas
# ================================================================

def test_list_patient_personas(client: TestClient, test_user_token: str, sample_personas: list):
    """Test GET /api/v1/patient-personas - list all personas"""
    response = client.get(
        "/api/v1/patient-personas",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert data[0]["persona_code"] == "CARD-001-CHEST-PAIN"
    assert "persona_id" in data[0]
    assert "name" in data[0]
    assert "specialty" in data[0]
    assert data[0]["specialty"] == "cardiology"
    assert data[0]["difficulty_level"] == "intermediate"


def test_list_personas_filter_by_specialty(client: TestClient, test_user_token: str, sample_personas: list):
    """Test GET /patient-personas?specialty=cardiology"""
    response = client.get(
        "/api/v1/patient-personas?specialty=cardiology",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["specialty"] == "cardiology"
    assert data[0]["persona_code"] == "CARD-001-CHEST-PAIN"


def test_list_personas_filter_by_difficulty(client: TestClient, test_user_token: str, sample_personas: list):
    """Test GET /patient-personas?difficulty=foundation"""
    response = client.get(
        "/api/v1/patient-personas?difficulty=foundation",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["difficulty_level"] == "foundation"
    assert data[0]["persona_code"] == "RESP-002-ASTHMA"


def test_list_personas_multiple_filters(client: TestClient, test_user_token: str, sample_personas: list):
    """Test GET /patient-personas?specialty=respiratory&difficulty=foundation"""
    response = client.get(
        "/api/v1/patient-personas?specialty=respiratory&difficulty=foundation",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["specialty"] == "respiratory"
    assert data[0]["difficulty_level"] == "foundation"


def test_list_personas_pagination(client: TestClient, test_user_token: str, sample_personas: list):
    """Test GET /patient-personas?skip=1&limit=1"""
    response = client.get(
        "/api/v1/patient-personas?skip=1&limit=1",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    # Second persona (RESP-002-ASTHMA) in creation order
    assert data[0]["persona_code"] == "RESP-002-ASTHMA"


def test_list_personas_empty_result(client: TestClient, test_user_token: str, sample_personas: list):
    """Test GET /patient-personas with filter that matches nothing"""
    response = client.get(
        "/api/v1/patient-personas?specialty=nonexistent",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0


def test_list_personas_requires_auth(client: TestClient, sample_personas: list):
    """Test GET /patient-personas without token returns 401"""
    response = client.get("/api/v1/patient-personas")
    assert response.status_code == 401


def test_get_patient_persona(client: TestClient, test_user_token: str, sample_personas: list):
    """Test GET /api/v1/patient-personas/{persona_id} - get full details"""
    persona = sample_personas[0]
    
    response = client.get(
        f"/api/v1/patient-personas/{persona.persona_id}",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["persona_code"] == "CARD-001-CHEST-PAIN"
    assert data["name"] == "John Smith"
    assert data["age"] == 55
    assert data["opening_statement"] == "I've had this terrible crushing pain in my chest..."
    assert "symptoms" in data
    assert data["symptoms"]["immediate"] == ["chest pain", "left arm pain"]
    assert "medical_history" in data
    assert "emotional_profile" in data
    assert data["emotional_profile"]["baseline_state"] == "ANXIOUS_GUARDED"
    assert "key_differentials" in data
    assert "critical_actions" in data
    assert data["amc_blueprint_area"] == "Cardiovascular - Acute Coronary Syndromes"


def test_get_persona_not_found(client: TestClient, test_user_token: str):
    """Test GET /patient-personas/{invalid_id} returns 404"""
    fake_id = str(uuid4())
    
    response = client.get(
        f"/api/v1/patient-personas/{fake_id}",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    
    assert response.status_code == 404


def test_get_inactive_persona_not_found(client: TestClient, test_user_token: str, inactive_persona: PatientPersona):
    """Test GET /patient-personas/{inactive_id} returns 404 (inactive personas excluded)"""
    response = client.get(
        f"/api/v1/patient-personas/{inactive_persona.persona_id}",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    
    assert response.status_code == 404


def test_get_persona_requires_auth(client: TestClient, sample_personas: list):
    """Test GET /patient-personas/{id} without token returns 401"""
    persona = sample_personas[0]
    response = client.get(f"/api/v1/patient-personas/{persona.persona_id}")
    assert response.status_code == 401


# ================================================================
# TESTS: OSCE Sessions
# ================================================================

def test_create_osce_session(client: TestClient, test_user_token: str, sample_personas: list):
    """Test POST /api/v1/osce-sessions - create new session"""
    persona = sample_personas[0]

    response = client.post(
        "/api/v1/osce-sessions",
        headers={"Authorization": f"Bearer {test_user_token}"},
        json={"persona_id": persona.persona_id, "session_type": "individual"}
    )

    assert response.status_code == 201
    data = response.json()
    assert "attempt_id" in data
    assert data["persona_code"] == "CARD-001-CHEST-PAIN"
    assert data["patient_name"] == "John Smith"
    assert data["opening_statement"] == "I've had this terrible crushing pain in my chest..."
    assert data["time_limit_seconds"] == 480
    assert "started_at" in data


def test_create_session_default_type(client: TestClient, test_user_token: str, sample_personas: list):
    """Test POST /osce-sessions defaults to 'individual' session type"""
    persona = sample_personas[0]

    response = client.post(
        "/api/v1/osce-sessions",
        headers={"Authorization": f"Bearer {test_user_token}"},
        json={"persona_id": persona.persona_id}
    )

    assert response.status_code == 201
    data = response.json()
    assert "attempt_id" in data


def test_create_session_mock_exam_type(client: TestClient, test_user_token: str, sample_personas: list):
    """Test POST /osce-sessions with session_type='mock_exam'"""
    persona = sample_personas[0]

    response = client.post(
        "/api/v1/osce-sessions",
        headers={"Authorization": f"Bearer {test_user_token}"},
        json={"persona_id": persona.persona_id, "session_type": "mock_exam"}
    )

    assert response.status_code == 201
    data = response.json()
    assert "attempt_id" in data


def test_create_session_invalid_type(client: TestClient, test_user_token: str, sample_personas: list):
    """Test POST /osce-sessions with invalid session_type returns 400"""
    persona = sample_personas[0]

    response = client.post(
        "/api/v1/osce-sessions",
        headers={"Authorization": f"Bearer {test_user_token}"},
        json={"persona_id": persona.persona_id, "session_type": "invalid_type"}
    )

    assert response.status_code == 400


def test_create_session_invalid_persona(client: TestClient, test_user_token: str):
    """Test POST /osce-sessions with invalid persona_id returns 404"""
    fake_id = str(uuid4())

    response = client.post(
        "/api/v1/osce-sessions",
        headers={"Authorization": f"Bearer {test_user_token}"},
        json={"persona_id": fake_id, "session_type": "individual"}
    )

    assert response.status_code == 404


def test_create_session_inactive_persona(client: TestClient, test_user_token: str, inactive_persona: PatientPersona):
    """Test POST /osce-sessions with inactive persona returns 404"""
    response = client.post(
        "/api/v1/osce-sessions",
        headers={"Authorization": f"Bearer {test_user_token}"},
        json={"persona_id": inactive_persona.persona_id, "session_type": "individual"}
    )

    assert response.status_code == 404


def test_create_session_requires_auth(client: TestClient, sample_personas: list):
    """Test POST /osce-sessions without token returns 401"""
    persona = sample_personas[0]

    response = client.post(
        "/api/v1/osce-sessions",
        json={"persona_id": persona.persona_id}
    )

    assert response.status_code == 401


def test_get_osce_session(client: TestClient, test_user_token: str, sample_osce_session: OSCEAttemptAI, sample_personas: list):
    """Test GET /api/v1/osce-sessions/{attempt_id} - get session details"""
    response = client.get(
        f"/api/v1/osce-sessions/{sample_osce_session.attempt_id}",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["attempt_id"] == sample_osce_session.attempt_id
    assert data["session_type"] == "individual"
    assert "started_at" in data
    assert data["was_completed"] == False
    assert "persona" in data
    assert data["persona"]["persona_code"] == "CARD-001-CHEST-PAIN"


def test_get_session_not_found(client: TestClient, test_user_token: str):
    """Test GET /osce-sessions/{invalid_id} returns 404"""
    fake_id = str(uuid4())
    
    response = client.get(
        f"/api/v1/osce-sessions/{fake_id}",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    
    assert response.status_code == 404


def test_get_session_unauthorized_user(client: TestClient, test_user_token: str, other_user_session: OSCEAttemptAI):
    """Test GET /osce-sessions/{id} returns 404 if session belongs to different user (authorization check)"""
    # Accessing other user's session should return 404 (not 403 for security)
    response = client.get(
        f"/api/v1/osce-sessions/{other_user_session.attempt_id}",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    
    assert response.status_code == 404


def test_get_session_requires_auth(client: TestClient, sample_osce_session: OSCEAttemptAI):
    """Test GET /osce-sessions/{id} without token returns 401"""
    response = client.get(f"/api/v1/osce-sessions/{sample_osce_session.attempt_id}")
    assert response.status_code == 401


def test_get_osce_transcript(client: TestClient, test_user_token: str, sample_osce_session: OSCEAttemptAI):
    """Test GET /api/v1/osce-sessions/{attempt_id}/transcript"""
    response = client.get(
        f"/api/v1/osce-sessions/{sample_osce_session.attempt_id}/transcript",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "attempt_id" in data
    assert "conversation_history" in data
    assert len(data["conversation_history"]) == 2
    assert data["conversation_history"][0]["role"] == "patient"
    assert data["conversation_history"][0]["message"] == "I've had this terrible chest pain..."
    assert data["conversation_history"][1]["role"] == "student"
    assert "emotional_state_transitions" in data
    assert len(data["emotional_state_transitions"]) == 1
    assert "student_actions" in data
    assert len(data["student_actions"]) == 1


def test_get_transcript_empty_session(client: TestClient, test_user_token: str, db: Session, test_user: User, sample_personas: list):
    """Test GET /transcript on newly created session returns empty arrays"""
    persona = sample_personas[0]
    
    # Create session with empty history
    attempt = OSCEAttemptAI(
        attempt_id=str(uuid4()),
        user_id=str(test_user.id),
        persona_id=persona.persona_id,
        session_type="individual",
        started_at=datetime.now(timezone.utc),
        conversation_history=[],
        emotional_state_transitions=[],
        student_actions=[],
        was_completed=False,
        session_state='initialized',
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    
    response = client.get(
        f"/api/v1/osce-sessions/{attempt.attempt_id}/transcript",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["conversation_history"] == []
    assert data["emotional_state_transitions"] == []
    assert data["student_actions"] == []


def test_get_transcript_requires_auth(client: TestClient, sample_osce_session: OSCEAttemptAI):
    """Test GET /transcript without token returns 401"""
    response = client.get(f"/api/v1/osce-sessions/{sample_osce_session.attempt_id}/transcript")
    assert response.status_code == 401


def test_get_osce_score(client: TestClient, test_user_token: str, sample_score: OSCEScoreAI, completed_osce_session: OSCEAttemptAI):
    """Test GET /api/v1/osce-sessions/{attempt_id}/score"""
    response = client.get(
        f"/api/v1/osce-sessions/{completed_osce_session.attempt_id}/score",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "attempt_id" in data
    assert "scores" in data
    assert data["scores"]["communication"] == 2
    assert data["scores"]["clinical_reasoning"] == 3
    assert data["scores"]["information_gathering"] == 3
    assert data["scores"]["management"] == 2
    assert data["scores"]["professionalism"] == 2
    assert data["total_score"] == 12
    assert data["pass_fail"] == "PASS"  # 12/15 >= 9
    assert "ai_examiner_feedback" in data
    assert "strengths" in data
    assert len(data["strengths"]) == 2
    assert "areas_for_improvement" in data
    assert len(data["areas_for_improvement"]) == 1
    assert "critical_errors" in data
    assert "scored_at" in data
    assert "scoring_model_version" in data


def test_get_score_fail_threshold(client: TestClient, test_user_token: str, db: Session, test_user: User, sample_personas: list):
    """Test GET /score with failing score (< 9/15)"""
    persona = sample_personas[0]
    
    # Create completed session
    attempt = OSCEAttemptAI(
        attempt_id=str(uuid4()),
        user_id=str(test_user.id),
        persona_id=persona.persona_id,
        session_type="individual",
        started_at=datetime.now(timezone.utc),
        ended_at=datetime.now(timezone.utc),
        duration_seconds=480,
        conversation_history=[],
        emotional_state_transitions=[],
        student_actions=[],
        was_completed=True,
        session_state='finalized',
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    
    # Create failing score (8/15)
    score = OSCEScoreAI(
        score_id=str(uuid4()),
        attempt_id=attempt.attempt_id,
        communication_score=1,
        clinical_reasoning_score=2,
        information_gathering_score=2,
        management_score=2,
        professionalism_score=1,
        ai_examiner_feedback={"overall": "Needs improvement"},
        strengths=["Attempted systematic approach"],
        areas_for_improvement=["Incomplete history", "Missed red flags"],
        critical_errors=["Did not identify life-threatening condition"],
        scored_at=datetime.now(timezone.utc),
        scoring_model_version="claude-sonnet-4-5",
    )
    db.add(score)
    db.commit()
    
    response = client.get(
        f"/api/v1/osce-sessions/{attempt.attempt_id}/score",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["total_score"] == 8
    assert data["pass_fail"] == "FAIL"  # 8/15 < 9


def test_get_score_not_yet_scored(client: TestClient, test_user_token: str, sample_osce_session: OSCEAttemptAI):
    """Test GET /score on unscored session returns 404"""
    response = client.get(
        f"/api/v1/osce-sessions/{sample_osce_session.attempt_id}/score",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    
    # Should return 404 because no score exists yet
    assert response.status_code == 404


def test_get_score_requires_auth(client: TestClient, completed_osce_session: OSCEAttemptAI):
    """Test GET /score without token returns 401"""
    response = client.get(f"/api/v1/osce-sessions/{completed_osce_session.attempt_id}/score")
    assert response.status_code == 401


# ================================================================
# TESTS: End-to-End Flow
# ================================================================

def test_e2e_osce_practice_flow(client: TestClient, test_user_token: str, sample_personas: list):
    """
    Test complete OSCE practice workflow:
    1. List available personas
    2. Filter by specialty
    3. Select a persona (get full details)
    4. Create OSCE session
    5. Verify session created successfully
    6. Get transcript (should be empty initially)
    """
    # Step 1: List personas
    response = client.get(
        "/api/v1/patient-personas",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 200
    personas = response.json()
    assert len(personas) >= 1
    
    # Step 2: Filter by specialty
    response = client.get(
        "/api/v1/patient-personas?specialty=cardiology",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 200
    cardiology_personas = response.json()
    assert len(cardiology_personas) >= 1
    assert all(p["specialty"] == "cardiology" for p in cardiology_personas)
    
    # Step 3: Get full persona details
    persona_id = cardiology_personas[0]["persona_id"]
    response = client.get(
        f"/api/v1/patient-personas/{persona_id}",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 200
    persona_details = response.json()
    assert "opening_statement" in persona_details
    assert "symptoms" in persona_details
    assert "critical_actions" in persona_details
    
    # Step 4: Create session
    response = client.post(
        "/api/v1/osce-sessions",
        headers={"Authorization": f"Bearer {test_user_token}"},
        json={"persona_id": persona_id, "session_type": "individual"}
    )
    assert response.status_code == 201
    session = response.json()
    assert "attempt_id" in session
    assert session["time_limit_seconds"] == 480
    assert session["persona_code"] == "CARD-001-CHEST-PAIN"
    
    # Step 5: Verify session exists
    response = client.get(
        f"/api/v1/osce-sessions/{session['attempt_id']}",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 200
    session_details = response.json()
    assert session_details["was_completed"] == False
    assert session_details["session_type"] == "individual"
    
    # Step 6: Get transcript (should be empty for new session)
    response = client.get(
        f"/api/v1/osce-sessions/{session['attempt_id']}/transcript",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 200
    transcript = response.json()
    assert transcript["conversation_history"] == []


def test_e2e_mock_exam_creation(client: TestClient, test_user_token: str, sample_personas: list):
    """
    Test mock exam workflow:
    1. List personas by difficulty
    2. Create session with session_type='mock_exam'
    3. Verify session type correctly set
    """
    # Step 1: List intermediate difficulty personas
    response = client.get(
        "/api/v1/patient-personas?difficulty=intermediate",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 200
    personas = response.json()
    assert len(personas) >= 1
    
    # Step 2: Create mock exam session
    persona_id = personas[0]["persona_id"]
    response = client.post(
        "/api/v1/osce-sessions",
        headers={"Authorization": f"Bearer {test_user_token}"},
        json={"persona_id": persona_id, "session_type": "mock_exam"}
    )
    assert response.status_code == 201
    session = response.json()
    
    # Step 3: Verify session type
    response = client.get(
        f"/api/v1/osce-sessions/{session['attempt_id']}",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 200
    session_details = response.json()
    assert session_details["session_type"] == "mock_exam"
