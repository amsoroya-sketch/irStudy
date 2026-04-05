"""
Unit tests for Mock Exam Pydantic schemas

Tests input validation, field constraints, and data serialization
without requiring database or FastAPI app.

Coverage:
- PersonaInfo validation
- MockExamCreateResponse
- MockExamStatusResponse
- StationCompleteRequest validation
- MockExamResultsResponse

Usage:
    pytest tests/test_mock_exam/test_schemas.py -v
"""

import pytest
from pydantic import ValidationError
from datetime import datetime

from src.schemas.mock_exam import (
    PersonaInfo,
    MockExamCreateRequest,
    MockExamCreateResponse,
    MockExamStatusResponse,
    StationCompleteRequest,
    StationCompleteResponse,
    StationResult,
    SummaryStatistics,
    MockExamResultsResponse,
)


# ============================================================================
# TESTS: PersonaInfo
# ============================================================================


def test_persona_info_valid():
    """Test valid PersonaInfo creation"""
    persona = PersonaInfo(
        persona_id="550e8400-e29b-41d4-a716-446655440000",
        persona_code="CARD-001-CHEST-PAIN",
        name="John Smith",
        specialty="Cardiology",
        chief_complaint="Chest pain for 2 hours",
        difficulty_level="intermediate"
    )

    assert persona.persona_id == "550e8400-e29b-41d4-a716-446655440000"
    assert persona.specialty == "Cardiology"
    assert persona.difficulty_level == "intermediate"


def test_persona_info_invalid_uuid():
    """Test PersonaInfo with invalid UUID"""
    with pytest.raises(ValidationError) as exc_info:
        PersonaInfo(
            persona_id="invalid-uuid",
            persona_code="CARD-001",
            name="John Smith",
            specialty="Cardiology",
            chief_complaint="Chest pain",
            difficulty_level="intermediate"
        )

    assert "persona_id must be a valid UUID" in str(exc_info.value)


def test_persona_info_invalid_difficulty():
    """Test PersonaInfo with invalid difficulty level"""
    with pytest.raises(ValidationError):
        PersonaInfo(
            persona_id="550e8400-e29b-41d4-a716-446655440000",
            persona_code="CARD-001",
            name="John Smith",
            specialty="Cardiology",
            chief_complaint="Chest pain",
            difficulty_level="invalid_level"  # Must be foundation, intermediate, or advanced
        )


# ============================================================================
# TESTS: MockExamCreateRequest
# ============================================================================


def test_mock_exam_create_request_valid():
    """Test valid MockExamCreateRequest"""
    request = MockExamCreateRequest(exam_name="AMC Practice Exam #1")
    assert request.exam_name == "AMC Practice Exam #1"


def test_mock_exam_create_request_empty():
    """Test MockExamCreateRequest with no exam_name (optional field)"""
    request = MockExamCreateRequest()
    assert request.exam_name is None


def test_mock_exam_create_request_too_short():
    """Test MockExamCreateRequest with name too short"""
    with pytest.raises(ValidationError):
        MockExamCreateRequest(exam_name="AB")  # Min length is 3


# ============================================================================
# TESTS: MockExamCreateResponse
# ============================================================================


def test_mock_exam_create_response_valid():
    """Test valid MockExamCreateResponse"""
    personas = [
        PersonaInfo(
            persona_id="550e8400-e29b-41d4-a716-446655440000",
            persona_code=f"CARD-{i:03d}-CHEST-PAIN",
            name=f"Patient {i}",
            specialty="Cardiology",
            chief_complaint="Chest pain for 2 hours",
            difficulty_level="intermediate"
        )
        for i in range(16)
    ]

    response = MockExamCreateResponse(
        exam_id="660e8400-e29b-41d4-a716-446655440001",
        stations_config=personas,
        estimated_duration_minutes=150,
        start_url="/api/v1/osce/session/exam-123/station/1",
        created_at=datetime.utcnow()
    )

    assert response.exam_id == "660e8400-e29b-41d4-a716-446655440001"
    assert len(response.stations_config) == 16
    assert response.estimated_duration_minutes == 150


def test_mock_exam_create_response_wrong_station_count():
    """Test MockExamCreateResponse with wrong number of stations"""
    personas = [
        PersonaInfo(
            persona_id="550e8400-e29b-41d4-a716-446655440000",
            persona_code="CARD-001-CHEST-PAIN",
            name="Patient 1",
            specialty="Cardiology",
            chief_complaint="Chest pain",
            difficulty_level="intermediate"
        )
    ] * 10  # Only 10 stations, need 16

    with pytest.raises(ValidationError) as exc_info:
        MockExamCreateResponse(
            exam_id="660e8400-e29b-41d4-a716-446655440001",
            stations_config=personas,
            estimated_duration_minutes=150,
            start_url="/api/v1/osce/session/exam-123/station/1",
            created_at=datetime.utcnow()
        )

    assert "at least 16 items" in str(exc_info.value).lower()


# ============================================================================
# TESTS: MockExamStatusResponse
# ============================================================================


def test_mock_exam_status_response_valid():
    """Test valid MockExamStatusResponse"""
    status = MockExamStatusResponse(
        exam_id="660e8400-e29b-41d4-a716-446655440001",
        exam_state="IN_PROGRESS",
        current_station_number=5,
        stations_completed=4,
        total_score=48,
        max_possible_score=240,
        time_elapsed_minutes=42,
        started_at=datetime.utcnow(),
        completed_at=None,
        exam_name="Test Exam"
    )

    assert status.current_station_number == 5
    assert status.stations_completed == 4
    assert status.exam_state == "IN_PROGRESS"


def test_mock_exam_status_response_invalid_state():
    """Test MockExamStatusResponse with invalid exam_state"""
    with pytest.raises(ValidationError):
        MockExamStatusResponse(
            exam_id="660e8400-e29b-41d4-a716-446655440001",
            exam_state="INVALID_STATE",  # Must be IN_PROGRESS, COMPLETED, or ABANDONED
            current_station_number=5,
            stations_completed=4,
            total_score=48,
            time_elapsed_minutes=42
        )


def test_mock_exam_status_response_invalid_station_number():
    """Test MockExamStatusResponse with out-of-range station_number"""
    with pytest.raises(ValidationError):
        MockExamStatusResponse(
            exam_id="660e8400-e29b-41d4-a716-446655440001",
            exam_state="IN_PROGRESS",
            current_station_number=20,  # Max is 16
            stations_completed=4,
            total_score=48
        )


# ============================================================================
# TESTS: StationCompleteRequest
# ============================================================================


def test_station_complete_request_valid():
    """Test valid StationCompleteRequest"""
    request = StationCompleteRequest(
        attempt_id="770e8400-e29b-41d4-a716-446655440002",
        station_score=12,
        pass_fail="PASS"
    )

    assert request.attempt_id == "770e8400-e29b-41d4-a716-446655440002"
    assert request.station_score == 12
    assert request.pass_fail == "PASS"


def test_station_complete_request_invalid_score():
    """Test StationCompleteRequest with out-of-range score"""
    with pytest.raises(ValidationError):
        StationCompleteRequest(
            attempt_id="770e8400-e29b-41d4-a716-446655440002",
            station_score=20,  # Max is 15
            pass_fail="PASS"
        )


def test_station_complete_request_negative_score():
    """Test StationCompleteRequest with negative score"""
    with pytest.raises(ValidationError):
        StationCompleteRequest(
            attempt_id="770e8400-e29b-41d4-a716-446655440002",
            station_score=-5,  # Min is 0
            pass_fail="FAIL"
        )


def test_station_complete_request_invalid_pass_fail():
    """Test StationCompleteRequest with invalid pass_fail value"""
    with pytest.raises(ValidationError):
        StationCompleteRequest(
            attempt_id="770e8400-e29b-41d4-a716-446655440002",
            station_score=12,
            pass_fail="MAYBE"  # Must be PASS or FAIL
        )


# ============================================================================
# TESTS: StationCompleteResponse
# ============================================================================


def test_station_complete_response_continue():
    """Test StationCompleteResponse for continuing exam"""
    response = StationCompleteResponse(
        next_station_number=6,
        station_score=12,
        overall_progress=0.3125,
        exam_complete=False,
        total_score=60
    )

    assert response.next_station_number == 6
    assert response.exam_complete is False
    assert 0.0 <= response.overall_progress <= 1.0


def test_station_complete_response_exam_complete():
    """Test StationCompleteResponse for completed exam"""
    response = StationCompleteResponse(
        next_station_number=None,
        station_score=13,
        overall_progress=1.0,
        exam_complete=True,
        total_score=198
    )

    assert response.next_station_number is None
    assert response.exam_complete is True
    assert response.overall_progress == 1.0


# ============================================================================
# TESTS: StationResult
# ============================================================================


def test_station_result_valid():
    """Test valid StationResult"""
    result = StationResult(
        station_number=5,
        persona_name="John Smith",
        specialty="Cardiology",
        score=12,
        pass_fail="PASS",
        duration_minutes=8
    )

    assert result.station_number == 5
    assert result.score == 12
    assert result.pass_fail == "PASS"


def test_station_result_invalid_station_number():
    """Test StationResult with out-of-range station_number"""
    with pytest.raises(ValidationError):
        StationResult(
            station_number=20,  # Max is 16
            persona_name="John Smith",
            specialty="Cardiology",
            score=12,
            pass_fail="PASS",
            duration_minutes=8
        )


# ============================================================================
# TESTS: SummaryStatistics
# ============================================================================


def test_summary_statistics_valid():
    """Test valid SummaryStatistics"""
    stats = SummaryStatistics(
        stations_passed=14,
        stations_failed=2,
        average_score_per_station=12.375,
        percentage=82.5,
        performance_by_specialty={
            "Cardiology": {
                "stations": 2,
                "average_score": 13.0,
                "passed": 2
            }
        }
    )

    assert stats.stations_passed == 14
    assert stats.stations_failed == 2
    assert stats.percentage == 82.5


def test_summary_statistics_invalid_percentage():
    """Test SummaryStatistics with out-of-range percentage"""
    with pytest.raises(ValidationError):
        SummaryStatistics(
            stations_passed=14,
            stations_failed=2,
            average_score_per_station=12.375,
            percentage=150.0,  # Max is 100.0
            performance_by_specialty={}
        )


# ============================================================================
# TESTS: MockExamResultsResponse
# ============================================================================


def test_mock_exam_results_response_pass():
    """Test MockExamResultsResponse with passing score"""
    stations = [
        StationResult(
            station_number=i+1,
            persona_name=f"Patient {i+1}",
            specialty="Cardiology",
            score=12,
            pass_fail="PASS",
            duration_minutes=8
        )
        for i in range(16)
    ]

    results = MockExamResultsResponse(
        exam_id="660e8400-e29b-41d4-a716-446655440001",
        overall_score=198,
        max_score=240,
        percentage=82.5,
        overall_pass_fail="PASS",
        stations=stations,
        summary_statistics=SummaryStatistics(
            stations_passed=16,
            stations_failed=0,
            average_score_per_station=12.375,
            percentage=82.5,
            performance_by_specialty={}
        ),
        total_duration_minutes=148,
        completed_at=datetime.utcnow(),
        exam_name="Test Exam"
    )

    assert results.overall_score == 198
    assert results.overall_pass_fail == "PASS"
    assert len(results.stations) == 16


def test_mock_exam_results_response_fail():
    """Test MockExamResultsResponse with failing score"""
    stations = [
        StationResult(
            station_number=i+1,
            persona_name=f"Patient {i+1}",
            specialty="Cardiology",
            score=10,
            pass_fail="PASS" if i % 2 == 0 else "FAIL",
            duration_minutes=8
        )
        for i in range(16)
    ]

    results = MockExamResultsResponse(
        exam_id="660e8400-e29b-41d4-a716-446655440001",
        overall_score=160,
        max_score=240,
        percentage=66.7,
        overall_pass_fail="FAIL",
        stations=stations,
        summary_statistics=SummaryStatistics(
            stations_passed=8,
            stations_failed=8,
            average_score_per_station=10.0,
            percentage=66.7,
            performance_by_specialty={}
        ),
        total_duration_minutes=148,
        completed_at=datetime.utcnow()
    )

    assert results.overall_score == 160
    assert results.overall_pass_fail == "FAIL"


def test_mock_exam_results_response_wrong_station_count():
    """Test MockExamResultsResponse with wrong number of stations"""
    stations = [
        StationResult(
            station_number=i+1,
            persona_name=f"Patient {i+1}",
            specialty="Cardiology",
            score=12,
            pass_fail="PASS",
            duration_minutes=8
        )
        for i in range(10)  # Only 10, need 16
    ]

    with pytest.raises(ValidationError):
        MockExamResultsResponse(
            exam_id="660e8400-e29b-41d4-a716-446655440001",
            overall_score=120,
            max_score=240,
            percentage=50.0,
            overall_pass_fail="FAIL",
            stations=stations,
            summary_statistics=SummaryStatistics(
                stations_passed=10,
                stations_failed=0,
                average_score_per_station=12.0,
                percentage=50.0,
                performance_by_specialty={}
            ),
            total_duration_minutes=80,
            completed_at=datetime.utcnow()
        )
