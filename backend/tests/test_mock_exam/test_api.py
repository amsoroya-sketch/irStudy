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
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock

from src.main import app
from src.schemas.mock_exam import (
    MockExamCreateResponse,
    PersonaInfo,
    MockExamStatusResponse,
    StationCompleteResponse,
    MockExamResultsResponse,
    StationResult,
    SummaryStatistics,
)


# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def client():
    """Test client for FastAPI app"""
    return TestClient(app)


@pytest.fixture
def auth_headers():
    """Mock JWT authentication headers"""
    return {
        "Authorization": "Bearer mock_jwt_token_12345"
    }


@pytest.fixture
def mock_user():
    """Mock authenticated user"""
    user = MagicMock()
    user.id = "user-123"
    user.email = "test@example.com"
    user.is_active = True
    return user


@pytest.fixture
def mock_orchestrator():
    """Mock MockExamOrchestrator"""
    return MagicMock()


# ============================================================================
# TESTS: POST /api/v1/mock-exams
# ============================================================================


@patch("src.api.v1.mock_exams.get_current_active_user")
@patch("src.api.v1.mock_exams.MockExamOrchestrator")
def test_create_mock_exam_success(mock_orchestrator_class, mock_get_user, client, mock_user, auth_headers):
    """Test successful exam creation"""
    # Mock dependencies
    mock_get_user.return_value = mock_user

    mock_orchestrator = MagicMock()
    mock_orchestrator.create_exam = AsyncMock(return_value=MockExamCreateResponse(
        exam_id="exam-123",
        stations_config=[
            PersonaInfo(
                persona_id="persona-1",
                persona_code="CARD-001-CHEST-PAIN",
                name="John Smith",
                specialty="Cardiology",
                chief_complaint="Chest pain",
                difficulty_level="intermediate"
            )
        ] * 16,
        estimated_duration_minutes=150,
        start_url="/api/v1/osce/session/exam-123/station/1",
        created_at="2026-04-05T10:00:00Z"
    ))
    mock_orchestrator_class.return_value = mock_orchestrator

    # Make request
    response = client.post(
        "/api/v1/mock-exams",
        json={"exam_name": "Test Exam"},
        headers=auth_headers
    )

    # Assertions
    assert response.status_code == 201
    data = response.json()
    assert data["exam_id"] == "exam-123"
    assert len(data["stations_config"]) == 16
    assert data["estimated_duration_minutes"] == 150


@patch("src.api.v1.mock_exams.get_current_active_user")
def test_create_mock_exam_no_auth(mock_get_user, client):
    """Test exam creation without authentication"""
    mock_get_user.side_effect = Exception("Not authenticated")

    response = client.post("/api/v1/mock-exams")

    # Should return 401 or 403
    assert response.status_code in [401, 403]


@patch("src.api.v1.mock_exams.get_current_active_user")
@patch("src.api.v1.mock_exams.MockExamOrchestrator")
def test_create_mock_exam_insufficient_personas(mock_orchestrator_class, mock_get_user, client, mock_user, auth_headers):
    """Test exam creation with insufficient personas"""
    mock_get_user.return_value = mock_user

    mock_orchestrator = MagicMock()
    mock_orchestrator.create_exam = AsyncMock(
        side_effect=ValueError("Insufficient personas for mock exam")
    )
    mock_orchestrator_class.return_value = mock_orchestrator

    response = client.post(
        "/api/v1/mock-exams",
        headers=auth_headers
    )

    assert response.status_code == 500
    assert "Failed to create mock exam" in response.json()["detail"]


# ============================================================================
# TESTS: GET /api/v1/mock-exams/{exam_id}
# ============================================================================


@patch("src.api.v1.mock_exams.get_current_active_user")
@patch("src.api.v1.mock_exams.MockExamOrchestrator")
def test_get_exam_status_success(mock_orchestrator_class, mock_get_user, client, mock_user, auth_headers):
    """Test getting exam status"""
    mock_get_user.return_value = mock_user

    mock_orchestrator = MagicMock()
    mock_orchestrator.get_exam_status = AsyncMock(return_value=MockExamStatusResponse(
        exam_id="exam-123",
        exam_state="IN_PROGRESS",
        current_station_number=5,
        stations_completed=4,
        total_score=48,
        max_possible_score=240,
        time_elapsed_minutes=42,
        started_at="2026-04-05T10:00:00Z",
        completed_at=None,
        exam_name="Test Exam"
    ))
    mock_orchestrator_class.return_value = mock_orchestrator

    response = client.get(
        "/api/v1/mock-exams/exam-123",
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["exam_id"] == "exam-123"
    assert data["exam_state"] == "IN_PROGRESS"
    assert data["current_station_number"] == 5
    assert data["stations_completed"] == 4


@patch("src.api.v1.mock_exams.get_current_active_user")
@patch("src.api.v1.mock_exams.MockExamOrchestrator")
def test_get_exam_status_not_found(mock_orchestrator_class, mock_get_user, client, mock_user, auth_headers):
    """Test getting status of non-existent exam"""
    mock_get_user.return_value = mock_user

    mock_orchestrator = MagicMock()
    mock_orchestrator.get_exam_status = AsyncMock(
        side_effect=ValueError("Exam invalid-exam-id not found")
    )
    mock_orchestrator_class.return_value = mock_orchestrator

    response = client.get(
        "/api/v1/mock-exams/invalid-exam-id",
        headers=auth_headers
    )

    assert response.status_code == 404


@patch("src.api.v1.mock_exams.get_current_active_user")
@patch("src.api.v1.mock_exams.MockExamOrchestrator")
def test_get_exam_status_unauthorized(mock_orchestrator_class, mock_get_user, client, mock_user, auth_headers):
    """Test getting status of another user's exam"""
    mock_get_user.return_value = mock_user

    mock_orchestrator = MagicMock()
    mock_orchestrator.get_exam_status = AsyncMock(
        side_effect=ValueError("User user-123 not authorized to access exam")
    )
    mock_orchestrator_class.return_value = mock_orchestrator

    response = client.get(
        "/api/v1/mock-exams/other-user-exam",
        headers=auth_headers
    )

    assert response.status_code == 403


# ============================================================================
# TESTS: PUT /api/v1/mock-exams/{exam_id}/station/{station_number}/complete
# ============================================================================


@patch("src.api.v1.mock_exams.get_current_active_user")
@patch("src.api.v1.mock_exams.MockExamOrchestrator")
def test_complete_station_success(mock_orchestrator_class, mock_get_user, client, mock_user, auth_headers):
    """Test marking station as complete"""
    mock_get_user.return_value = mock_user

    mock_orchestrator = MagicMock()
    mock_orchestrator.advance_station = AsyncMock(return_value=StationCompleteResponse(
        next_station_number=6,
        station_score=12,
        overall_progress=0.3125,
        exam_complete=False,
        total_score=60
    ))
    mock_orchestrator_class.return_value = mock_orchestrator

    response = client.put(
        "/api/v1/mock-exams/exam-123/station/5/complete",
        json={
            "attempt_id": "attempt-123",
            "station_score": 12,
            "pass_fail": "PASS"
        },
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["next_station_number"] == 6
    assert data["station_score"] == 12
    assert data["exam_complete"] is False


@patch("src.api.v1.mock_exams.get_current_active_user")
@patch("src.api.v1.mock_exams.MockExamOrchestrator")
def test_complete_station_exam_complete(mock_orchestrator_class, mock_get_user, client, mock_user, auth_headers):
    """Test completing final station (station 16)"""
    mock_get_user.return_value = mock_user

    mock_orchestrator = MagicMock()
    mock_orchestrator.advance_station = AsyncMock(return_value=StationCompleteResponse(
        next_station_number=None,
        station_score=13,
        overall_progress=1.0,
        exam_complete=True,
        total_score=198
    ))
    mock_orchestrator_class.return_value = mock_orchestrator

    response = client.put(
        "/api/v1/mock-exams/exam-123/station/16/complete",
        json={
            "attempt_id": "attempt-123",
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


@patch("src.api.v1.mock_exams.get_current_active_user")
@patch("src.api.v1.mock_exams.MockExamOrchestrator")
def test_complete_station_invalid_score(mock_orchestrator_class, mock_get_user, client, mock_user, auth_headers):
    """Test completing station with invalid score (out of range)"""
    mock_get_user.return_value = mock_user

    response = client.put(
        "/api/v1/mock-exams/exam-123/station/5/complete",
        json={
            "attempt_id": "attempt-123",
            "station_score": 20,  # Invalid: max is 15
            "pass_fail": "PASS"
        },
        headers=auth_headers
    )

    # Pydantic validation should catch this
    assert response.status_code == 422


@patch("src.api.v1.mock_exams.get_current_active_user")
@patch("src.api.v1.mock_exams.MockExamOrchestrator")
def test_complete_station_missing_body(mock_orchestrator_class, mock_get_user, client, mock_user, auth_headers):
    """Test completing station without request body"""
    mock_get_user.return_value = mock_user

    response = client.put(
        "/api/v1/mock-exams/exam-123/station/5/complete",
        headers=auth_headers
    )

    assert response.status_code == 400
    assert "Request body is required" in response.json()["detail"]


# ============================================================================
# TESTS: GET /api/v1/mock-exams/{exam_id}/results
# ============================================================================


@patch("src.api.v1.mock_exams.get_current_active_user")
@patch("src.api.v1.mock_exams.MockExamOrchestrator")
def test_get_exam_results_success(mock_orchestrator_class, mock_get_user, client, mock_user, auth_headers):
    """Test getting comprehensive exam results"""
    mock_get_user.return_value = mock_user

    mock_orchestrator = MagicMock()
    mock_orchestrator.get_exam_results = AsyncMock(return_value=MockExamResultsResponse(
        exam_id="exam-123",
        overall_score=198,
        max_score=240,
        percentage=82.5,
        overall_pass_fail="PASS",
        stations=[
            StationResult(
                station_number=i+1,
                persona_name=f"Patient {i+1}",
                specialty="Cardiology",
                score=12,
                pass_fail="PASS",
                duration_minutes=8
            ) for i in range(16)
        ],
        summary_statistics=SummaryStatistics(
            stations_passed=14,
            stations_failed=2,
            average_score_per_station=12.375,
            percentage=82.5,
            performance_by_specialty={}
        ),
        total_duration_minutes=148,
        completed_at="2026-04-05T12:30:00Z",
        exam_name="Test Exam",
        report_pdf_url=None
    ))
    mock_orchestrator_class.return_value = mock_orchestrator

    response = client.get(
        "/api/v1/mock-exams/exam-123/results",
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["exam_id"] == "exam-123"
    assert data["overall_score"] == 198
    assert data["overall_pass_fail"] == "PASS"
    assert len(data["stations"]) == 16


@patch("src.api.v1.mock_exams.get_current_active_user")
@patch("src.api.v1.mock_exams.MockExamOrchestrator")
def test_get_exam_results_not_completed(mock_orchestrator_class, mock_get_user, client, mock_user, auth_headers):
    """Test getting results of incomplete exam"""
    mock_get_user.return_value = mock_user

    mock_orchestrator = MagicMock()
    mock_orchestrator.get_exam_results = AsyncMock(
        side_effect=ValueError("Exam exam-123 is not completed (state: IN_PROGRESS)")
    )
    mock_orchestrator_class.return_value = mock_orchestrator

    response = client.get(
        "/api/v1/mock-exams/exam-123/results",
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


def test_invalid_station_number(client, auth_headers):
    """Test with out-of-range station number"""
    response = client.put(
        "/api/v1/mock-exams/exam-123/station/20/complete",  # Invalid: max is 16
        json={
            "attempt_id": "attempt-123",
            "station_score": 12,
            "pass_fail": "PASS"
        },
        headers=auth_headers
    )

    # FastAPI path validation should catch this
    assert response.status_code == 422
