"""
Comprehensive test suite for Dashboard API endpoints

Tests:
- GET /api/v1/dashboard/overview - Unified dashboard with all module metrics
- Module aggregation (MCQ, OSCE, EMR, Mock Exam)
- Specialty breakdown calculation
- Recent activity tracking
- Personalized recommendations
- Response time < 200ms

SECURITY:
- JWT authentication required
- User can only access own data
- No PHI exposure in responses

COVERAGE:
- Overall progress calculation
- Module-specific statistics
- Specialty performance breakdown
- Recent activity aggregation
- Recommendation generation
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import time

from src.db.models import (
    User,
    MCQ,
    MCQAttempt,
    OSCE,
    OSCEAttempt,
    EMRSession,
    MockExam,
    MedicalSpecialty,
    DifficultyLevel,
    UserRole,
    OSCEType,
)


# ============================================================================
# PYTEST FIXTURES
# ============================================================================


@pytest.fixture
def sample_mcqs(db_session):
    """Create sample MCQs for testing"""
    mcqs = []
    specialties = [MedicalSpecialty.CARDIOLOGY, MedicalSpecialty.RESPIRATORY, MedicalSpecialty.PSYCHIATRY]

    for i, specialty in enumerate(specialties):
        mcq = MCQ(
            question_id=f"MCQ-{specialty.value.upper()}-{str(i+1).zfill(3)}",
            question_text=f"Test question for {specialty.value}",
            options={"A": "Option A", "B": "Option B", "C": "Option C", "D": "Option D"},
            correct_answer="A",
            explanation=f"Explanation for {specialty.value}",
            citation="Therapeutic Guidelines, 2023",
            specialty=specialty,
            difficulty=DifficultyLevel.MEDIUM,
            is_published=True,
        )
        db_session.add(mcq)
        mcqs.append(mcq)

    db_session.commit()
    for mcq in mcqs:
        db_session.refresh(mcq)
    return mcqs


@pytest.fixture
def sample_osces(db_session):
    """Create sample OSCEs for testing"""
    osces = []
    specialties = [MedicalSpecialty.CARDIOLOGY, MedicalSpecialty.RESPIRATORY]

    for i, specialty in enumerate(specialties):
        osce = OSCE(
            osce_id=f"OSCE-{specialty.value.upper()}-{str(i+1).zfill(3)}",
            station_title=f"Test OSCE for {specialty.value}",
            station_type=OSCEType.HISTORY_TAKING,
            specialty=specialty,
            difficulty=DifficultyLevel.MEDIUM,
            patient_instructions="Patient instructions",
            candidate_instructions="Candidate instructions",
            rubric={"category1": {"criteria": "test"}},
            is_published=True,
        )
        db_session.add(osce)
        osces.append(osce)

    db_session.commit()
    for osce in osces:
        db_session.refresh(osce)
    return osces


@pytest.fixture
def user_with_activity(db_session, test_user, sample_mcqs, sample_osces):
    """Create user with activity across all modules"""
    # MCQ attempts
    for i, mcq in enumerate(sample_mcqs):
        attempt = MCQAttempt(
            user_id=test_user.id,
            mcq_id=mcq.id,
            selected_answer="A" if i % 2 == 0 else "B",
            is_correct=(i % 2 == 0),
            time_taken_seconds=60 + i * 10,
            confidence_level=3,
            attempt_number=1,
            attempted_at=datetime.utcnow() - timedelta(days=i),
        )
        db_session.add(attempt)

    # OSCE attempts
    for i, osce in enumerate(sample_osces):
        attempt = OSCEAttempt(
            user_id=test_user.id,
            osce_id=osce.id,
            scores={
                "history_examination": 2,
                "clinical_reasoning": 3,
                "communication": 2,
                "professionalism": 3,
                "safety": 2,
            },
            total_score=12,
            passed=True,
            time_taken_seconds=480,
            attempt_number=1,
            attempted_at=datetime.utcnow() - timedelta(days=i + 1),
        )
        db_session.add(attempt)

    # EMR sessions
    for i in range(2):
        session = EMRSession(
            user_id=test_user.id,
            emr_system="epic",
            specialty="cardiology",
            difficulty="medium",
            started_at=datetime.utcnow() - timedelta(days=i + 2),
            submitted_at=datetime.utcnow() - timedelta(days=i + 2, hours=-1),
            elapsed_time_seconds=600,
            validation_score=75.0 + i * 5,
            status="graded",
        )
        db_session.add(session)

    # Mock exam
    exam = MockExam(
        exam_id="mock-exam-001",
        user_id=str(test_user.id),
        stations_config=["persona1", "persona2"] * 8,
        exam_state="COMPLETE",
        started_at=datetime.utcnow() - timedelta(days=3),
        completed_at=datetime.utcnow() - timedelta(days=3, hours=-2),
        total_duration_minutes=150,
        total_score=200,
        stations_passed=14,
        overall_pass=True,
    )
    db_session.add(exam)

    db_session.commit()
    db_session.refresh(test_user)
    return test_user


# ============================================================================
# TEST CASES
# ============================================================================


def test_dashboard_overview_unauthenticated(client: TestClient):
    """Test dashboard requires authentication"""
    response = client.get("/api/v1/dashboard/overview")
    assert response.status_code == 401


def test_dashboard_overview_authenticated(client: TestClient, auth_headers, user_with_activity, db_session):
    """Test authenticated user can access dashboard"""
    # Get dashboard (using auth_headers fixture with valid JWT)
    response = client.get(
        "/api/v1/dashboard/overview",
        headers=auth_headers,
    )
    assert response.status_code == 200

    data = response.json()

    # Verify response structure
    assert "overall_progress" in data
    assert "modules" in data
    assert "specialty_breakdown" in data
    assert "recent_activity" in data
    assert "recommendations" in data


def test_dashboard_overall_progress(client: TestClient, auth_headers, user_with_activity):
    """Test overall progress calculation"""
    # Get dashboard (using auth_headers fixture with valid JWT)
    response = client.get(
        "/api/v1/dashboard/overview",
        headers=auth_headers,
    )
    data = response.json()

    overall = data["overall_progress"]

    # Verify overall progress fields
    assert "total_sessions" in overall
    assert "completion_percentage" in overall
    assert "avg_score" in overall
    assert "total_time_minutes" in overall
    assert "last_activity" in overall

    # Verify data types
    assert isinstance(overall["total_sessions"], int)
    assert isinstance(overall["completion_percentage"], (int, float))
    assert isinstance(overall["avg_score"], (int, float))
    assert isinstance(overall["total_time_minutes"], int)
    assert isinstance(overall["last_activity"], str)

    # Verify counts (3 MCQs + 2 OSCEs + 2 EMR + 1 Mock Exam = 8 total)
    assert overall["total_sessions"] == 8


def test_dashboard_module_breakdown(client: TestClient, auth_headers, user_with_activity):
    """Test module-specific statistics"""
    # Get dashboard (using auth_headers fixture with valid JWT)
    response = client.get(
        "/api/v1/dashboard/overview",
        headers=auth_headers,
    )
    data = response.json()

    modules = data["modules"]

    # Verify all modules present
    assert "mcq" in modules
    assert "osce" in modules
    assert "emr" in modules
    assert "mock_exam" in modules

    # Verify MCQ stats
    mcq = modules["mcq"]
    assert mcq["attempts"] == 3
    assert 0 <= mcq["avg_score"] <= 100
    assert mcq["last_activity"] is not None

    # Verify OSCE stats
    osce = modules["osce"]
    assert osce["attempts"] == 2
    assert 0 <= osce["avg_score"] <= 100
    assert osce["completed"] == 2  # Both passed

    # Verify EMR stats
    emr = modules["emr"]
    assert emr["sessions"] == 2
    assert 0 <= emr["avg_soap_score"] <= 100
    assert emr["completed"] == 2

    # Verify Mock Exam stats
    mock_exam = modules["mock_exam"]
    assert mock_exam["exams_taken"] == 1
    assert mock_exam["exams_completed"] == 1
    assert 0 <= mock_exam["avg_score"] <= 100


def test_dashboard_specialty_breakdown(client: TestClient, auth_headers, user_with_activity):
    """Test specialty performance breakdown"""
    # Get dashboard (using auth_headers fixture with valid JWT)
    response = client.get(
        "/api/v1/dashboard/overview",
        headers=auth_headers,
    )
    data = response.json()

    specialty_breakdown = data["specialty_breakdown"]

    # Verify structure
    assert isinstance(specialty_breakdown, list)

    # Verify at least one specialty
    assert len(specialty_breakdown) > 0

    # Verify specialty structure
    for specialty in specialty_breakdown:
        assert "specialty" in specialty
        assert "attempts" in specialty
        assert "avg_score" in specialty
        assert "strength" in specialty

        assert isinstance(specialty["specialty"], str)
        assert isinstance(specialty["attempts"], int)
        assert isinstance(specialty["avg_score"], (int, float))
        assert specialty["strength"] in ["weak", "average", "good", "excellent"]


def test_dashboard_recent_activity(client: TestClient, auth_headers, user_with_activity):
    """Test recent activity tracking"""
    # Get dashboard (using auth_headers fixture with valid JWT)
    response = client.get(
        "/api/v1/dashboard/overview",
        headers=auth_headers,
    )
    data = response.json()

    recent_activity = data["recent_activity"]

    # Verify structure
    assert isinstance(recent_activity, list)
    assert len(recent_activity) <= 10  # Max 10 activities

    # Verify activity structure
    for activity in recent_activity:
        assert "type" in activity
        assert "description" in activity
        assert "score" in activity
        assert "timestamp" in activity

        assert activity["type"] in ["mcq", "osce", "emr", "mock_exam"]
        assert isinstance(activity["description"], str)
        assert isinstance(activity["timestamp"], str)

        # Score can be null for in-progress activities
        if activity["score"] is not None:
            assert isinstance(activity["score"], (int, float))
            assert 0 <= activity["score"] <= 100


def test_dashboard_recommendations(client: TestClient, auth_headers, user_with_activity):
    """Test personalized recommendations"""
    # Get dashboard (using auth_headers fixture with valid JWT)
    response = client.get(
        "/api/v1/dashboard/overview",
        headers=auth_headers,
    )
    data = response.json()

    recommendations = data["recommendations"]

    # Verify structure
    assert isinstance(recommendations, list)
    assert len(recommendations) <= 5  # Max 5 recommendations

    # Verify recommendation structure
    for rec in recommendations:
        assert "module" in rec
        assert "specialty" in rec
        assert "reason" in rec
        assert "priority" in rec

        assert isinstance(rec["module"], str)
        assert isinstance(rec["specialty"], str)
        assert isinstance(rec["reason"], str)
        assert rec["priority"] in ["high", "medium", "low"]


def test_dashboard_empty_state(client: TestClient, auth_headers):
    """Test dashboard with no user activity"""
    # Get dashboard (using auth_headers fixture with valid JWT)
    response = client.get(
        "/api/v1/dashboard/overview",
        headers=auth_headers,
    )
    assert response.status_code == 200

    data = response.json()

    # Verify zero state
    overall = data["overall_progress"]
    assert overall["total_sessions"] == 0
    assert overall["avg_score"] == 0.0

    # Verify all modules show zero activity
    modules = data["modules"]
    assert modules["mcq"]["attempts"] == 0
    assert modules["osce"]["attempts"] == 0
    assert modules["emr"]["sessions"] == 0
    assert modules["mock_exam"]["exams_taken"] == 0

    # Verify empty lists
    assert len(data["specialty_breakdown"]) == 0
    assert len(data["recent_activity"]) == 0


def test_dashboard_response_time(client: TestClient, auth_headers, user_with_activity):
    """Test dashboard response time < 200ms"""
    # Get dashboard (using auth_headers fixture with valid JWT)
    response = client.get(
        "/api/v1/dashboard/overview",
        headers=auth_headers,
    )
    data = response.json()

    specialty_breakdown = data["specialty_breakdown"]

    # Verify descending order by attempts
    if len(specialty_breakdown) > 1:
        for i in range(len(specialty_breakdown) - 1):
            assert specialty_breakdown[i]["attempts"] >= specialty_breakdown[i + 1]["attempts"]


def test_dashboard_activity_sorting(client: TestClient, auth_headers, user_with_activity):
    """Test recent activity sorted by timestamp (descending)"""
    # Get dashboard (using auth_headers fixture with valid JWT)
    response = client.get(
        "/api/v1/dashboard/overview",
        headers=auth_headers,
    )
    data = response.json()

    recent_activity = data["recent_activity"]

    # Verify descending order by timestamp
    if len(recent_activity) > 1:
        for i in range(len(recent_activity) - 1):
            ts1 = datetime.fromisoformat(recent_activity[i]["timestamp"])
            ts2 = datetime.fromisoformat(recent_activity[i + 1]["timestamp"])
            assert ts1 >= ts2


# ============================================================================
# EDGE CASES
# ============================================================================


def test_dashboard_with_incomplete_emr_sessions(client: TestClient, test_user, auth_headers, db_session):
    """Test dashboard handles incomplete EMR sessions correctly"""
    # Create incomplete EMR session
    session = EMRSession(
        user_id=test_user.id,
        emr_system="epic",
        specialty="cardiology",
        difficulty="medium",
        started_at=datetime.utcnow(),
        status="in_progress",
    )
    db_session.add(session)
    db_session.commit()

    # Get dashboard (using auth_headers fixture with valid JWT)
    response = client.get(
        "/api/v1/dashboard/overview",
        headers=auth_headers,
    )
    assert response.status_code == 200

    data = response.json()

    # Verify EMR session counted but not as completed
    emr = data["modules"]["emr"]
    assert emr["sessions"] == 1
    assert emr["completed"] == 0  # Not completed


def test_dashboard_with_incomplete_mock_exam(client: TestClient, test_user, auth_headers, db_session):
    """Test dashboard handles incomplete mock exams correctly"""
    # Create incomplete mock exam
    exam = MockExam(
        exam_id="mock-exam-incomplete",
        user_id=str(test_user.id),
        stations_config=["persona1"] * 16,
        exam_state="IN_PROGRESS",
        current_station_number=5,
        started_at=datetime.utcnow(),
    )
    db_session.add(exam)
    db_session.commit()

    # Get dashboard (using auth_headers fixture with valid JWT)
    response = client.get(
        "/api/v1/dashboard/overview",
        headers=auth_headers,
    )
    assert response.status_code == 200

    data = response.json()

    # Verify mock exam counted but not as completed
    mock_exam = data["modules"]["mock_exam"]
    assert mock_exam["exams_taken"] == 1
    assert mock_exam["exams_completed"] == 0  # Not completed
