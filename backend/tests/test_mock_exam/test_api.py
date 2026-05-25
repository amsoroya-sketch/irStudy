"""
Integration tests for Mock Exam API endpoints

Tests:
- POST /api/v1/mock-exams (create exam)
- GET /api/v1/mock-exams/{exam_id} (get status)
- PUT /api/v1/mock-exams/{exam_id}/station/{station_number}/complete (complete station)
- GET /api/v1/mock-exams/{exam_id}/results (get results)

Coverage:
- Authentication (JWT required)
- Authorization (user can only access own exams)
- Input validation (Pydantic schemas)
- Error handling (404, 403, 400, 500)

Usage:
    pytest tests/test_mock_exam/test_api.py -v
"""

import pytest
from uuid import uuid4
from datetime import datetime, timezone

from src.db.models import MockExam
from src.schemas.mock_exam import PersonaInfo


# ============================================================================
# TESTS: POST /api/v1/mock-exams
# ============================================================================


@pytest.mark.asyncio
async def test_create_mock_exam_success(db_session, client, test_user, test_personas, auth_headers):
    """Test successful exam creation"""
    # Make request
    response = client.post(
        "/api/v1/mock-exams",
        json={"exam_name": "Test Exam"},
        headers=auth_headers
    )

    # Assertions
    assert response.status_code == 201
    data = response.json()
    assert "exam_id" in data
    assert len(data["stations_config"]) == 16
    assert data["estimated_duration_minutes"] == 150

    # Verify database record created
    db_exam = db_session.query(MockExam).filter(
        MockExam.exam_id == data["exam_id"]
    ).first()
    assert db_exam is not None
    assert str(db_exam.user_id) == str(test_user.id)


def test_create_mock_exam_no_auth(client):
    """Test exam creation without authentication"""
    response = client.post("/api/v1/mock-exams")

    # Should return 401 or 403
    assert response.status_code in [401, 403]


@pytest.mark.asyncio
async def test_create_mock_exam_insufficient_personas(db_session, client, test_user, auth_headers):
    """Test exam creation with insufficient personas (no personas in DB)"""
    # No personas created - should fail
    response = client.post(
        "/api/v1/mock-exams",
        json={"exam_name": "Test Exam"},
        headers=auth_headers
    )

    assert response.status_code == 500
    assert "Failed to create mock exam" in response.json()["detail"]


# ============================================================================
# TESTS: GET /api/v1/mock-exams/{exam_id}
# ============================================================================


@pytest.mark.asyncio
async def test_get_exam_status_success(db_session, client, test_user, test_personas, auth_headers):
    """Test getting exam status"""
    # Create a mock exam first
    from src.services.mock_exam import MockExamOrchestrator
    orchestrator = MockExamOrchestrator(db_session)
    exam = await orchestrator.create_exam(str(test_user.id), "Test Exam")

    response = client.get(
        f"/api/v1/mock-exams/{exam.exam_id}",
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["exam_id"] == exam.exam_id
    assert data["exam_state"] == "IN_PROGRESS"
    assert data["current_station_number"] == 1


@pytest.mark.asyncio
async def test_get_exam_status_not_found(db_session, client, test_user, auth_headers):
    """Test getting status of non-existent exam"""
    fake_exam_id = str(uuid4())

    response = client.get(
        f"/api/v1/mock-exams/{fake_exam_id}",
        headers=auth_headers
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_exam_status_unauthorized(db_session, client, test_user, test_personas, auth_headers):
    """Test getting status of another user's exam"""
    from src.services.mock_exam import MockExamOrchestrator
    from src.db.models import User
    from src.auth.security import hash_password

    # Create another user
    other_user = User(
        email="other@example.com",
        password_hash=hash_password("TestPassword123!"),
        full_name="Other User",
        is_active=True,
        is_verified=True
    )
    db_session.add(other_user)
    db_session.commit()
    db_session.refresh(other_user)

    # Create exam with other user
    orchestrator = MockExamOrchestrator(db_session)
    exam = await orchestrator.create_exam(str(other_user.id), "Other User's Exam")

    # Try to access with test_user's auth
    response = client.get(
        f"/api/v1/mock-exams/{exam.exam_id}",
        headers=auth_headers
    )

    assert response.status_code == 403


# ============================================================================
# TESTS: PUT /api/v1/mock-exams/{exam_id}/station/{station_number}/complete
# ============================================================================


@pytest.mark.asyncio
async def test_complete_station_success(db_session, client, test_user, test_personas, auth_headers):
    """Test marking station as complete"""
    from src.services.mock_exam import MockExamOrchestrator

    # Create exam
    orchestrator = MockExamOrchestrator(db_session)
    exam = await orchestrator.create_exam(str(test_user.id), "Test Exam")

    attempt_uuid = str(uuid4())

    response = client.put(
        f"/api/v1/mock-exams/{exam.exam_id}/station/1/complete",
        json={
            "attempt_id": attempt_uuid,
            "station_score": 12,
            "pass_fail": "PASS"
        },
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["next_station_number"] == 2
    assert data["station_score"] == 12
    assert data["exam_complete"] is False


@pytest.mark.asyncio
async def test_complete_station_exam_complete(db_session, client, test_user, test_personas, auth_headers):
    """Test completing final station (station 16)"""
    from src.services.mock_exam import MockExamOrchestrator

    # Create exam
    orchestrator = MockExamOrchestrator(db_session)
    exam = await orchestrator.create_exam(str(test_user.id), "Test Exam")

    # Fast-forward to station 16
    db_exam = db_session.query(MockExam).filter(MockExam.exam_id == exam.exam_id).first()
    db_exam.current_station_number = 16
    db_exam.total_score = 186
    db_exam.stations_passed = 15
    db_session.commit()

    attempt_uuid = str(uuid4())

    response = client.put(
        f"/api/v1/mock-exams/{exam.exam_id}/station/16/complete",
        json={
            "attempt_id": attempt_uuid,
            "station_score": 13,
            "pass_fail": "PASS"
        },
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["next_station_number"] is None
    assert data["exam_complete"] is True
    assert data["overall_progress"] == 1.0


@pytest.mark.asyncio
async def test_complete_station_invalid_score(db_session, client, test_user, test_personas, auth_headers):
    """Test completing station with invalid score (out of range)"""
    from src.services.mock_exam import MockExamOrchestrator

    # Create exam
    orchestrator = MockExamOrchestrator(db_session)
    exam = await orchestrator.create_exam(str(test_user.id), "Test Exam")

    attempt_uuid = str(uuid4())

    response = client.put(
        f"/api/v1/mock-exams/{exam.exam_id}/station/1/complete",
        json={
            "attempt_id": attempt_uuid,
            "station_score": 20,  # Invalid: max is 15
            "pass_fail": "PASS"
        },
        headers=auth_headers
    )

    # Pydantic validation should catch this
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_complete_station_missing_body(db_session, client, test_user, test_personas, auth_headers):
    """Test completing station without request body"""
    from src.services.mock_exam import MockExamOrchestrator

    # Create exam
    orchestrator = MockExamOrchestrator(db_session)
    exam = await orchestrator.create_exam(str(test_user.id), "Test Exam")

    response = client.put(
        f"/api/v1/mock-exams/{exam.exam_id}/station/1/complete",
        headers=auth_headers
    )

    assert response.status_code == 400
    assert "Request body is required" in response.json()["detail"]


# ============================================================================
# TESTS: GET /api/v1/mock-exams/{exam_id}/results
# ============================================================================


@pytest.mark.asyncio
async def test_get_exam_results_success(db_session, client, test_user, test_personas, auth_headers):
    """Test getting comprehensive exam results"""
    from src.services.mock_exam import MockExamOrchestrator
    from src.db.models import OSCEAttemptAI, OSCEScoreAI

    # Create exam
    orchestrator = MockExamOrchestrator(db_session)
    exam = await orchestrator.create_exam(str(test_user.id), "Test Exam")

    # Complete all 16 stations
    persona_ids = [p.persona_id for p in exam.stations_config]

    for i in range(16):
        # Create mock attempt
        attempt = OSCEAttemptAI(
            attempt_id=str(uuid4()),
            user_id=str(test_user.id),
            persona_id=persona_ids[i],
            mock_exam_id=exam.exam_id,
            session_type='mock_exam',
            station_number=i + 1,
            started_at=datetime.now(timezone.utc),
            ended_at=datetime.now(timezone.utc),
            was_completed=True
        )
        db_session.add(attempt)
        db_session.flush()

        # Create score (using individual components, not total_score)
        # Give passing scores to reach ≥198/240 threshold
        # Using 13 points per station: 13 × 16 = 208 (PASS)
        score = OSCEScoreAI(
            score_id=str(uuid4()),
            attempt_id=attempt.attempt_id,
            communication_score=3,
            clinical_reasoning_score=4,
            information_gathering_score=3,
            management_score=2,
            professionalism_score=1
            # total_score = 13, pass_fail = PASS
        )
        db_session.add(score)

        # Advance station
        await orchestrator.advance_station(exam.exam_id, i + 1, 13, 'PASS', str(test_user.id))

    db_session.commit()

    response = client.get(
        f"/api/v1/mock-exams/{exam.exam_id}/results",
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["exam_id"] == exam.exam_id
    assert data["overall_score"] == 208  # 13 × 16 = 208 (≥198 = PASS)
    assert data["overall_pass_fail"] == "PASS"
    assert len(data["stations"]) == 16


@pytest.mark.asyncio
async def test_get_exam_results_not_completed(db_session, client, test_user, test_personas, auth_headers):
    """Test getting results of incomplete exam"""
    from src.services.mock_exam import MockExamOrchestrator

    # Create exam but don't complete it
    orchestrator = MockExamOrchestrator(db_session)
    exam = await orchestrator.create_exam(str(test_user.id), "Test Exam")

    response = client.get(
        f"/api/v1/mock-exams/{exam.exam_id}/results",
        headers=auth_headers
    )

    assert response.status_code == 400
    assert "not completed" in response.json()["detail"]


# ============================================================================
# TESTS: INPUT VALIDATION
# ============================================================================


def test_invalid_exam_id_format(client, auth_headers):
    """Test with malformed exam_id (Pydantic validation)"""
    # This would normally be caught by UUID validation
    response = client.get(
        "/api/v1/mock-exams/invalid-uuid-format",
        headers=auth_headers
    )

    # Should still process (UUID validation happens in orchestrator)
    # But will return 404 if exam not found
    assert response.status_code in [404, 500]


@pytest.mark.asyncio
async def test_invalid_station_number(db_session, client, test_user, test_personas, auth_headers):
    """Test with out-of-range station number"""
    from src.services.mock_exam import MockExamOrchestrator

    # Create exam
    orchestrator = MockExamOrchestrator(db_session)
    exam = await orchestrator.create_exam(str(test_user.id), "Test Exam")

    attempt_uuid = str(uuid4())

    response = client.put(
        f"/api/v1/mock-exams/{exam.exam_id}/station/20/complete",  # Invalid: max is 16
        json={
            "attempt_id": attempt_uuid,
            "station_score": 12,
            "pass_fail": "PASS"
        },
        headers=auth_headers
    )

    # FastAPI path validation should catch this
    assert response.status_code == 422
