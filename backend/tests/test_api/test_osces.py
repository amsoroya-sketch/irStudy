"""
Comprehensive test suite for OSCE endpoints (TASK_002)

Tests:
- GET /api/v1/osces/random - Get random OSCE with filters
- GET /api/v1/osces/{id} - Get specific OSCE
- POST /api/v1/osces/{id}/complete-station - Complete station
- GET /api/v1/osces - List OSCEs with filters
- AMC 15-mark rubric validation
- Response time < 200ms

AMC CLINICAL EXAM CONTEXT:
- 15-mark rubric (5 categories × 3 marks each)
- Pass mark: 9/15 (60%)
- Australian medical standards
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import time

from src.main import app
from src.db.base import Base, get_db
from src.db.models import (
    User,
    OSCE,
    OSCEAttempt,
    MedicalSpecialty,
    OSCEType,
    DifficultyLevel,
    UserRole,
)
from src.auth.security import hash_password


# ============================================================================
# TEST DATABASE SETUP
# ============================================================================

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for tests"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


# ============================================================================
# PYTEST FIXTURES
# ============================================================================


@pytest.fixture(scope="function")
def db_session():
    """Create fresh database for each test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user(db_session):
    """Create test user"""
    user = User(
        email="test@example.com",
        password_hash=hash_password("testpass123"),
        full_name="Test User",
        role=UserRole.STUDENT,
        is_active=True,
        is_verified=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user):
    """Get authentication headers"""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "testpass123"},
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_osce(db_session):
    """Create sample OSCE for testing"""
    osce = OSCE(
        osce_id="OSCE-CARD-001",
        station_title="Cardiovascular Examination",
        station_type=OSCEType.PHYSICAL_EXAMINATION,
        patient_instructions="You are a 65-year-old with known heart failure. Act short of breath on exertion.",
        candidate_instructions="Perform a complete cardiovascular examination on this patient. You have 8 minutes.",
        examiner_instructions="Assess systematic approach, correct technique, and communication.",
        rubric={
            "history_examination": {
                "marks": 3,
                "criteria": "Systematic cardiovascular examination",
                "0": "Did not perform examination",
                "1": "Incomplete/disorganized approach",
                "2": "Good approach with minor omissions",
                "3": "Excellent systematic comprehensive approach",
            },
            "clinical_reasoning": {
                "marks": 3,
                "criteria": "Identifies key findings and formulates differential",
                "0": "No differential diagnosis",
                "1": "Vague or incorrect differential",
                "2": "Reasonable differential with minor gaps",
                "3": "Comprehensive accurate differential",
            },
            "communication": {
                "marks": 3,
                "criteria": "Clear communication with patient",
                "0": "Poor communication",
                "1": "Basic communication with gaps",
                "2": "Good communication, minor issues",
                "3": "Excellent rapport and clarity",
            },
            "safety": {
                "marks": 3,
                "criteria": "Patient safety and comfort",
                "0": "Unsafe practices",
                "1": "Some safety concerns",
                "2": "Generally safe with minor issues",
                "3": "Exemplary safety and comfort",
            },
            "professionalism": {
                "marks": 3,
                "criteria": "Professional behavior and ethics",
                "0": "Unprofessional",
                "1": "Basic professionalism with gaps",
                "2": "Professional with minor lapses",
                "3": "Exemplary professionalism",
            },
        },
        specialty=MedicalSpecialty.CARDIOLOGY,
        difficulty=DifficultyLevel.MEDIUM,
        time_limit_minutes=8,
        learning_objectives=[
            "Perform systematic cardiovascular examination",
            "Identify heart failure signs",
            "Demonstrate professional communication",
        ],
        red_flags=["Severe dyspnoea", "Hypotension", "Acute pulmonary oedema"],
        tags=["cardiovascular", "heart-failure", "physical-exam"],
        is_published=True,
        times_practiced=5,
        average_score=11.2,
    )
    db_session.add(osce)
    db_session.commit()
    db_session.refresh(osce)
    return osce


@pytest.fixture
def multiple_osces(db_session):
    """Create multiple OSCEs for filtering tests"""
    osces = [
        OSCE(
            osce_id=f"OSCE-CARD-{str(i).zfill(3)}",
            station_title=f"Cardiology Station {i}",
            station_type=OSCEType.HISTORY_TAKING if i % 2 == 0 else OSCEType.PHYSICAL_EXAMINATION,
            patient_instructions=f"Patient instructions {i}",
            candidate_instructions=f"Candidate instructions {i}",
            rubric={
                "history_examination": {"marks": 3, "criteria": "Test", "0": "0", "1": "1", "2": "2", "3": "3"},
                "clinical_reasoning": {"marks": 3, "criteria": "Test", "0": "0", "1": "1", "2": "2", "3": "3"},
                "communication": {"marks": 3, "criteria": "Test", "0": "0", "1": "1", "2": "2", "3": "3"},
                "safety": {"marks": 3, "criteria": "Test", "0": "0", "1": "1", "2": "2", "3": "3"},
                "professionalism": {"marks": 3, "criteria": "Test", "0": "0", "1": "1", "2": "2", "3": "3"},
            },
            specialty=MedicalSpecialty.CARDIOLOGY,
            difficulty=DifficultyLevel.EASY if i % 2 == 0 else DifficultyLevel.HARD,
            is_published=True,
        )
        for i in range(1, 6)
    ]
    db_session.add_all(osces)
    db_session.commit()
    return osces


# ============================================================================
# TEST CASES
# ============================================================================


def test_get_random_osce_success(sample_osce, auth_headers):
    """Test GET /api/v1/osces/random returns OSCE without rubric"""
    start_time = time.time()
    response = client.get("/api/v1/osces/random", headers=auth_headers)
    elapsed_ms = (time.time() - start_time) * 1000

    assert response.status_code == 200
    data = response.json()

    # Verify OSCE structure
    assert "id" in data
    assert "osce_id" in data
    assert data["osce_id"] == "OSCE-CARD-001"
    assert "station_title" in data
    assert "station_type" in data
    assert "patient_instructions" in data
    assert "candidate_instructions" in data
    assert "specialty" in data

    # Verify rubric NOT included (practice mode)
    assert "rubric" not in data
    assert "examiner_instructions" not in data

    # Verify response time < 200ms
    assert elapsed_ms < 200, f"Response time {elapsed_ms}ms exceeds 200ms threshold"


def test_get_random_osce_with_specialty_filter(multiple_osces, auth_headers):
    """Test GET /api/v1/osces/random with specialty filter"""
    response = client.get(
        "/api/v1/osces/random?specialty=cardiology", headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["specialty"] == "cardiology"


def test_get_random_osce_with_type_filter(multiple_osces, auth_headers):
    """Test GET /api/v1/osces/random with station type filter"""
    response = client.get(
        "/api/v1/osces/random?osce_type=history_taking", headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["station_type"] == "history_taking"


def test_get_random_osce_no_results(auth_headers):
    """Test GET /api/v1/osces/random returns 404 when no OSCEs match"""
    response = client.get(
        "/api/v1/osces/random?specialty=cardiology", headers=auth_headers
    )

    assert response.status_code == 404
    assert "No OSCEs found" in response.json()["detail"]


def test_get_osce_by_id_success(sample_osce, auth_headers):
    """Test GET /api/v1/osces/{id} returns specific OSCE"""
    start_time = time.time()
    response = client.get(f"/api/v1/osces/{sample_osce.id}", headers=auth_headers)
    elapsed_ms = (time.time() - start_time) * 1000

    assert response.status_code == 200
    data = response.json()

    assert data["id"] == sample_osce.id
    assert data["osce_id"] == "OSCE-CARD-001"
    assert "cardiovascular" in data["station_title"].lower()

    # Verify rubric NOT included (practice mode)
    assert "rubric" not in data

    # Verify response time < 200ms
    assert elapsed_ms < 200, f"Response time {elapsed_ms}ms exceeds 200ms threshold"


def test_get_osce_by_id_not_found(auth_headers):
    """Test GET /api/v1/osces/{id} returns 404 for invalid ID"""
    response = client.get("/api/v1/osces/99999", headers=auth_headers)

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_get_osce_rubric(sample_osce, auth_headers):
    """Test GET /api/v1/osces/{id}/rubric returns complete OSCE with rubric"""
    response = client.get(
        f"/api/v1/osces/{sample_osce.id}/rubric", headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()

    # Verify rubric IS included
    assert "rubric" in data
    assert "examiner_instructions" in data

    # Verify rubric structure (AMC 15-mark format)
    rubric = data["rubric"]
    assert "history_examination" in rubric
    assert "clinical_reasoning" in rubric
    assert "communication" in rubric
    assert "safety" in rubric
    assert "professionalism" in rubric

    # Verify each category has 3 marks
    for category, details in rubric.items():
        assert details["marks"] == 3
        assert "criteria" in details


def test_complete_osce_station_passing_score(sample_osce, auth_headers):
    """Test POST /api/v1/osces/{id}/complete-station with passing score"""
    # Scores totaling 12/15 (80% - pass)
    completion_data = {
        "osce_id": sample_osce.id,
        "scores": {
            "history_examination": 3,
            "clinical_reasoning": 2,
            "communication": 3,
            "safety": 2,
            "professionalism": 2,
        },
        "time_taken_seconds": 480,  # 8 minutes
        "self_reflection": "I felt confident about the examination technique but could improve my differential diagnosis.",
    }

    start_time = time.time()
    response = client.post(
        f"/api/v1/osces/{sample_osce.id}/complete-station",
        json=completion_data,
        headers=auth_headers,
    )
    elapsed_ms = (time.time() - start_time) * 1000

    assert response.status_code == 200
    data = response.json()

    # Verify response structure
    assert data["total_score"] == 12
    assert data["passed"] is True
    assert data["scores"] == completion_data["scores"]
    assert data["attempt_number"] == 1
    assert "areas_for_improvement" in data

    # Verify weak areas identified (score < 2)
    weak_areas = data["areas_for_improvement"]
    assert weak_areas is None or len(weak_areas) == 0  # All scores >= 2

    # Verify rubric included for self-review
    assert "rubric" in data
    assert "examiner_instructions" in data

    # Verify response time < 200ms
    assert elapsed_ms < 200, f"Response time {elapsed_ms}ms exceeds 200ms threshold"


def test_complete_osce_station_failing_score(sample_osce, auth_headers):
    """Test POST /api/v1/osces/{id}/complete-station with failing score"""
    # Scores totaling 7/15 (47% - fail)
    completion_data = {
        "osce_id": sample_osce.id,
        "scores": {
            "history_examination": 1,
            "clinical_reasoning": 1,
            "communication": 2,
            "safety": 2,
            "professionalism": 1,
        },
        "time_taken_seconds": 420,
    }

    response = client.post(
        f"/api/v1/osces/{sample_osce.id}/complete-station",
        json=completion_data,
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()

    assert data["total_score"] == 7
    assert data["passed"] is False

    # Verify weak areas identified
    weak_areas = data["areas_for_improvement"]
    assert len(weak_areas) > 0
    assert "history_examination" in weak_areas
    assert "clinical_reasoning" in weak_areas
    assert "professionalism" in weak_areas


def test_complete_osce_station_multiple_attempts(sample_osce, auth_headers):
    """Test multiple attempts increment attempt_number"""
    completion_data = {
        "osce_id": sample_osce.id,
        "scores": {
            "history_examination": 2,
            "clinical_reasoning": 2,
            "communication": 2,
            "safety": 2,
            "professionalism": 2,
        },
        "time_taken_seconds": 480,
    }

    # First attempt
    response1 = client.post(
        f"/api/v1/osces/{sample_osce.id}/complete-station",
        json=completion_data,
        headers=auth_headers,
    )
    assert response1.json()["attempt_number"] == 1

    # Second attempt
    response2 = client.post(
        f"/api/v1/osces/{sample_osce.id}/complete-station",
        json=completion_data,
        headers=auth_headers,
    )
    assert response2.json()["attempt_number"] == 2


def test_complete_osce_station_id_mismatch(sample_osce, auth_headers):
    """Test POST /complete-station fails with ID mismatch"""
    completion_data = {
        "osce_id": 999,  # Mismatched ID
        "scores": {
            "history_examination": 2,
            "clinical_reasoning": 2,
            "communication": 2,
            "safety": 2,
            "professionalism": 2,
        },
        "time_taken_seconds": 480,
    }

    response = client.post(
        f"/api/v1/osces/{sample_osce.id}/complete-station",
        json=completion_data,
        headers=auth_headers,
    )

    assert response.status_code == 400
    assert "mismatch" in response.json()["detail"].lower()


def test_complete_osce_station_invalid_scores():
    """Test that invalid scores (not 0-3) are rejected"""
    from src.schemas.osce import OSCEAttemptCreate
    from pydantic import ValidationError

    with pytest.raises(ValidationError) as exc_info:
        OSCEAttemptCreate(
            osce_id=1,
            scores={
                "history_examination": 5,  # Invalid: max is 3
                "clinical_reasoning": 2,
                "communication": 2,
                "safety": 2,
                "professionalism": 2,
            },
            time_taken_seconds=480,
        )

    error_message = str(exc_info.value)
    assert "0-3" in error_message or "score" in error_message.lower()


def test_complete_osce_station_missing_category():
    """Test that missing rubric categories are rejected"""
    from src.schemas.osce import OSCEAttemptCreate
    from pydantic import ValidationError

    with pytest.raises(ValidationError) as exc_info:
        OSCEAttemptCreate(
            osce_id=1,
            scores={
                "history_examination": 2,
                "clinical_reasoning": 2,
                # Missing: communication, safety, professionalism
            },
            time_taken_seconds=480,
        )

    error_message = str(exc_info.value)
    assert "missing" in error_message.lower() or "required" in error_message.lower()


def test_list_osces_success(multiple_osces, auth_headers):
    """Test GET /api/v1/osces lists OSCEs with pagination"""
    response = client.get("/api/v1/osces?limit=3", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()

    assert isinstance(data, list)
    assert len(data) <= 3
    assert all("osce_id" in osce for osce in data)


def test_list_osces_with_filters(multiple_osces, auth_headers):
    """Test GET /api/v1/osces with specialty and type filters"""
    response = client.get(
        "/api/v1/osces?specialty=cardiology&osce_type=history_taking",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()

    assert all(osce["specialty"] == "cardiology" for osce in data)
    assert all(osce["station_type"] == "history_taking" for osce in data)


def test_unauthenticated_request_fails():
    """Test that requests without auth token fail"""
    response = client.get("/api/v1/osces/random")

    assert response.status_code == 401


# ============================================================================
# AMC RUBRIC VALIDATION TESTS
# ============================================================================


def test_amc_rubric_validation_15_marks():
    """Test that rubric must total exactly 15 marks (AMC format)"""
    from src.schemas.osce import OSCECreate
    from pydantic import ValidationError

    # Valid rubric (15 marks total)
    valid_rubric = {
        "history_examination": {
            "marks": 3,
            "criteria": "Test",
            "0": "0",
            "1": "1",
            "2": "2",
            "3": "3",
        },
        "clinical_reasoning": {
            "marks": 3,
            "criteria": "Test",
            "0": "0",
            "1": "1",
            "2": "2",
            "3": "3",
        },
        "communication": {
            "marks": 3,
            "criteria": "Test",
            "0": "0",
            "1": "1",
            "2": "2",
            "3": "3",
        },
        "safety": {
            "marks": 3,
            "criteria": "Test",
            "0": "0",
            "1": "1",
            "2": "2",
            "3": "3",
        },
        "professionalism": {
            "marks": 3,
            "criteria": "Test",
            "0": "0",
            "1": "1",
            "2": "2",
            "3": "3",
        },
    }

    # Should pass validation
    osce_create = OSCECreate(
        osce_id="OSCE-TEST-001",
        station_title="Test Station",
        station_type=OSCEType.HISTORY_TAKING,
        patient_instructions="Test instructions",
        candidate_instructions="Test instructions",
        rubric=valid_rubric,
        specialty=MedicalSpecialty.CARDIOLOGY,
    )
    assert osce_create.rubric == valid_rubric

    # Invalid rubric (10 marks total - should fail)
    invalid_rubric = {**valid_rubric}
    invalid_rubric["professionalism"]["marks"] = 0  # Now totals 12 marks

    with pytest.raises(ValidationError) as exc_info:
        OSCECreate(
            osce_id="OSCE-TEST-002",
            station_title="Test Station",
            station_type=OSCEType.HISTORY_TAKING,
            patient_instructions="Test instructions",
            candidate_instructions="Test instructions",
            rubric=invalid_rubric,
            specialty=MedicalSpecialty.CARDIOLOGY,
        )

    error_message = str(exc_info.value)
    assert "15 marks" in error_message


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================


def test_osce_random_response_time(sample_osce, auth_headers):
    """Test that GET /random responds in < 200ms (95th percentile)"""
    response_times = []

    # Run 20 requests
    for _ in range(20):
        start_time = time.time()
        response = client.get("/api/v1/osces/random", headers=auth_headers)
        elapsed_ms = (time.time() - start_time) * 1000
        response_times.append(elapsed_ms)
        assert response.status_code == 200

    # Calculate 95th percentile
    response_times.sort()
    p95 = response_times[int(len(response_times) * 0.95)]

    assert p95 < 200, f"95th percentile response time {p95}ms exceeds 200ms threshold"


def test_osce_complete_response_time(sample_osce, auth_headers):
    """Test that POST /complete-station responds in < 200ms (95th percentile)"""
    response_times = []
    completion_data = {
        "osce_id": sample_osce.id,
        "scores": {
            "history_examination": 2,
            "clinical_reasoning": 2,
            "communication": 2,
            "safety": 2,
            "professionalism": 2,
        },
        "time_taken_seconds": 480,
    }

    # Run 20 requests
    for _ in range(20):
        start_time = time.time()
        response = client.post(
            f"/api/v1/osces/{sample_osce.id}/complete-station",
            json=completion_data,
            headers=auth_headers,
        )
        elapsed_ms = (time.time() - start_time) * 1000
        response_times.append(elapsed_ms)
        assert response.status_code == 200

    # Calculate 95th percentile
    response_times.sort()
    p95 = response_times[int(len(response_times) * 0.95)]

    assert p95 < 200, f"95th percentile response time {p95}ms exceeds 200ms threshold"
