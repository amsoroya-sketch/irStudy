"""
Mock Exam API Router - 16-Station OSCE Exam Orchestration

Endpoints:
- POST /api/v1/mock-exams - Create new 16-station exam with auto-selected personas
- GET /api/v1/mock-exams/{exam_id} - Get exam status and progress
- PUT /api/v1/mock-exams/{exam_id}/station/{station_number}/complete - Mark station complete
- GET /api/v1/mock-exams/{exam_id}/results - Get comprehensive exam results

SECURITY:
- JWT authentication required on all endpoints
- User authorization verified (can only access own exams)
- UUID validation on all IDs
- No PHI exposure in error messages

AMC CLINICAL EXAM FORMAT:
- 16 stations × 8 minutes each = 128 minutes
- 2-minute breaks between stations
- Total duration: ~150 minutes (2.5 hours)
- Pass criteria: ≥198/240 (82.5%)
- Balanced distribution: 2 personas per specialty × 8 specialties

Performance Targets:
- Exam creation: <2 seconds
- Status retrieval: <500ms
- Station completion: <3 seconds
- Results generation: <1 second
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session

from src.db.base import get_db
from src.db.models import User
from src.auth.dependencies import get_current_active_user
from src.services.mock_exam import MockExamOrchestrator
from src.schemas.mock_exam import (
    MockExamCreateRequest,
    MockExamCreateResponse,
    MockExamStatusResponse,
    StationCompleteRequest,
    StationCompleteResponse,
    MockExamResultsResponse,
)

import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/mock-exams", tags=["ai-osce"], redirect_slashes=False)


@router.post(
    "/",
    response_model=MockExamCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new 16-station mock exam",
    description="""
    Create a new AMC-style mock OSCE exam with 16 auto-selected stations.

    Auto-selection logic:
    - 2 personas per specialty × 8 specialties = 16 stations
    - Specialties: Cardiology, Respiratory, Neurology, Gastroenterology,
                   Psychiatry, Paediatrics, Obstetrics, Emergency Medicine
    - Difficulty: 50% intermediate, 50% advanced
    - Station order randomized (not grouped by specialty)
    - Ensures no duplicate personas

    Returns exam_id and stations_config for frontend display.

    Performance: <2 seconds
    """
)
async def create_mock_exam(
    request: Optional[MockExamCreateRequest] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> MockExamCreateResponse:
    """
    Create a new 16-station mock exam with auto-selected personas.

    Args:
        request: Optional exam customization (exam_name)
        current_user: Authenticated user (from JWT)
        db: Database session

    Returns:
        MockExamCreateResponse with exam_id, stations_config, start_url

    Raises:
        HTTPException 500: If persona selection fails (insufficient active personas)
    """
    try:
        orchestrator = MockExamOrchestrator(db)

        exam_name = None
        if request:
            exam_name = request.exam_name

        exam = await orchestrator.create_exam(
            user_id=str(current_user.id),
            exam_name=exam_name
        )

        logger.info(
            f"Created mock exam {exam.exam_id} for user {current_user.email} "
            f"with {len(exam.stations_config)} stations"
        )

        return exam

    except ValueError as e:
        logger.error(f"Failed to create mock exam for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create mock exam: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error creating mock exam: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while creating the exam"
        )


@router.get(
    "/{exam_id}",
    response_model=MockExamStatusResponse,
    summary="Get mock exam status",
    description="""
    Get current mock exam status and progress.

    Returns:
    - exam_state: 'IN_PROGRESS', 'COMPLETED', or 'ABANDONED'
    - current_station_number: 1-16
    - stations_completed: Number of completed stations
    - total_score: Running total (max 240)
    - time_elapsed_minutes: Time since exam started

    Performance: <500ms
    """
)
async def get_mock_exam_status(
    exam_id: str = Path(..., description="UUID of mock exam"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> MockExamStatusResponse:
    """
    Get current mock exam status and progress.

    Args:
        exam_id: UUID of exam
        current_user: Authenticated user (from JWT)
        db: Database session

    Returns:
        MockExamStatusResponse with current state, progress, scores

    Raises:
        HTTPException 404: Exam not found
        HTTPException 403: User not authorized to access exam
    """
    try:
        orchestrator = MockExamOrchestrator(db)

        status_response = await orchestrator.get_exam_status(
            exam_id=exam_id,
            user_id=str(current_user.id)
        )

        return status_response

    except ValueError as e:
        error_msg = str(e).lower()
        if "not found" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Exam {exam_id} not found"
            )
        elif "not authorized" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to access this exam"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
    except Exception as e:
        logger.error(f"Unexpected error getting exam status: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while retrieving exam status"
        )


@router.put(
    "/{exam_id}/station/{station_number}/complete",
    response_model=StationCompleteResponse,
    summary="Mark station as complete and advance",
    description="""
    Mark station as complete and advance to next station.

    Flow:
    1. Validate station_number matches current_station
    2. Update exam totals (total_score, stations_passed)
    3. Increment current_station_number
    4. Check if exam complete (station_number == 16)
    5. If complete: Calculate overall pass/fail, update exam_state
    6. Return next_station_number (or null if exam complete)

    Pass/Fail Criteria:
    - Overall pass: ≥198/240 (82.5%)
    - Individual station pass: ≥9/15 (60%)

    Performance: <3 seconds
    """
)
async def complete_station(
    exam_id: str = Path(..., description="UUID of mock exam"),
    station_number: int = Path(..., ge=1, le=16, description="Completed station number (1-16)"),
    request: StationCompleteRequest = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> StationCompleteResponse:
    """
    Mark station as complete and advance to next station.

    Args:
        exam_id: UUID of exam
        station_number: Just completed station (1-16)
        request: Station completion data (attempt_id, score, pass_fail)
        current_user: Authenticated user (from JWT)
        db: Database session

    Returns:
        StationCompleteResponse with next_station, progress, exam_complete

    Raises:
        HTTPException 404: Exam not found
        HTTPException 403: User not authorized
        HTTPException 400: Invalid station number or exam state
    """
    if not request:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Request body is required"
        )

    try:
        orchestrator = MockExamOrchestrator(db)

        result = await orchestrator.advance_station(
            exam_id=exam_id,
            station_number=station_number,
            station_score=request.station_score,
            pass_fail=request.pass_fail,
            user_id=str(current_user.id)
        )

        logger.info(
            f"Completed station {station_number} for exam {exam_id}: "
            f"score={request.station_score}, pass_fail={request.pass_fail}, "
            f"exam_complete={result.exam_complete}"
        )

        return result

    except ValueError as e:
        error_msg = str(e).lower()
        if "not found" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Exam {exam_id} not found"
            )
        elif "not authorized" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to access this exam"
            )
        elif "not in progress" in error_msg or "mismatch" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
    except Exception as e:
        logger.error(f"Unexpected error completing station: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while completing the station"
        )


@router.get(
    "/{exam_id}/results",
    response_model=MockExamResultsResponse,
    summary="Get comprehensive exam results",
    description="""
    Get comprehensive exam results after completion.

    Returns:
    - overall_score: Total score out of 240
    - overall_pass_fail: 'PASS' or 'FAIL' (≥198/240 = pass)
    - stations: List of 16 station results with breakdown
    - summary_statistics: Performance by specialty, averages, etc.
    - total_duration_minutes: Actual exam duration

    Only available after exam is completed (exam_state = 'COMPLETED').

    Performance: <1 second
    """
)
async def get_exam_results(
    exam_id: str = Path(..., description="UUID of mock exam"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> MockExamResultsResponse:
    """
    Get comprehensive exam results after completion.

    Args:
        exam_id: UUID of exam
        current_user: Authenticated user (from JWT)
        db: Database session

    Returns:
        MockExamResultsResponse with full breakdown, statistics, pass/fail

    Raises:
        HTTPException 404: Exam not found
        HTTPException 403: User not authorized
        HTTPException 400: Exam not completed yet
    """
    try:
        orchestrator = MockExamOrchestrator(db)

        results = await orchestrator.get_exam_results(
            exam_id=exam_id,
            user_id=str(current_user.id)
        )

        logger.info(
            f"Retrieved results for exam {exam_id}: "
            f"{results.overall_score}/240, {results.overall_pass_fail}"
        )

        return results

    except ValueError as e:
        error_msg = str(e).lower()
        if "not found" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Exam {exam_id} not found"
            )
        elif "not authorized" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to access this exam"
            )
        elif "not completed" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Exam is not completed yet. Complete all 16 stations first."
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
    except Exception as e:
        logger.error(f"Unexpected error getting exam results: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while retrieving exam results"
        )
