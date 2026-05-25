"""
OSCE API endpoints for irStudy Medical Education Platform

AMC CLINICAL EXAM FORMAT:
- 16 stations × 8 minutes each
- Rubric-based scoring (15 marks per station, 9/15 to pass)
- Station types: History taking, physical exam, communication, procedures

AUSTRALIAN CONTEXT:
- Patient scenarios reflect Australian demographics and cultural norms
- Management plans follow Australian guidelines (eTG, NSW Health protocols)
- Communication adjusted for Australian healthcare system

ENDPOINTS:
- GET /osces - List all OSCEs with pagination
- GET /osces/random - Get random OSCE station
- GET /osces/{id} - Get specific OSCE station
- GET /osces/{id}/rubric - Get scoring rubric for station
- POST /osces/{id}/complete-station - Submit OSCE completion and receive feedback
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional, List
import random

from src.db.base import get_db
from src.db.models import OSCE, OSCEAttempt, OSCEType, MedicalSpecialty, DifficultyLevel, User
from src.api.v1.osces import schemas
from src.auth.dependencies import get_current_active_user
from src.schemas.osce import OSCEAttemptCreate, OSCEAttemptResponse

router = APIRouter(prefix="/osces", tags=["OSCE Practice"])


@router.get("/random", response_model=schemas.OSCEResponse)
async def get_random_osce(
    type: Optional[str] = Query(None, alias="type", description="Filter by station type"),
    station_type: Optional[OSCEType] = Query(None, description="Filter by station type"),
    osce_type: Optional[OSCEType] = Query(None, description="Filter by station type"),
    specialty: Optional[MedicalSpecialty] = Query(None, description="Filter by specialty"),
    difficulty: Optional[DifficultyLevel] = Query(None, description="Filter by difficulty"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get a random OSCE station.

    **AMC Clinical Exam Format:**
    - 8 minutes per station
    - 15-mark rubric (9/15 to pass)
    - Types: History taking, examination, communication, counselling, procedures

    **Australian Context:**
    - All stations use Australian medical terminology
    - Management plans follow eTG and NSW Health protocols
    """
    query = db.query(OSCE).filter(OSCE.is_published == True)

    # Support 'type', 'station_type', and 'osce_type' query parameters
    filter_type = type or station_type or osce_type
    if filter_type:
        # Convert string to OSCEType enum if needed
        if isinstance(filter_type, str):
            try:
                filter_type = OSCEType(filter_type)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid station type: {filter_type}"
                )
        query = query.filter(OSCE.station_type == filter_type)

    if specialty:
        query = query.filter(OSCE.specialty == specialty)
    if difficulty:
        query = query.filter(OSCE.difficulty == difficulty)

    osces = query.all()

    if not osces:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No OSCE stations found matching criteria"
        )

    selected_osce = random.choice(osces)

    return schemas.OSCEResponse.model_validate(selected_osce)


@router.get("/{osce_id}", response_model=schemas.OSCEResponse)
async def get_osce(
    osce_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get specific OSCE station by ID.

    Supports both:
    - Database ID (integer): GET /osces/1
    - OSCE ID (string): GET /osces/OSCE-CARD-001
    """
    # Try to parse as integer (database ID)
    try:
        id_int = int(osce_id)
        osce = db.query(OSCE).filter(OSCE.id == id_int, OSCE.is_published == True).first()
    except ValueError:
        # Not an integer, treat as osce_id string
        osce = db.query(OSCE).filter(OSCE.osce_id == osce_id, OSCE.is_published == True).first()

    if not osce:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"OSCE station with ID {osce_id} not found"
        )

    return schemas.OSCEResponse.model_validate(osce)


@router.get("/{osce_id}/rubric", response_model=schemas.OSCERubric)
async def get_osce_rubric(
    osce_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get scoring rubric for OSCE station.

    **AMC Clinical Exam Rubric:**
    - Total: 15 marks
    - Pass mark: 9/15 (60%)
    - Categories: Introduction, history/exam, diagnosis, management, communication

    **Example Rubric:**
    ```json
    {
        "introduction": {"max_marks": 1, "criteria": "Introduces self, confirms identity"},
        "history_taking": {"max_marks": 5, "criteria": "Systematic history using SOCRATES"},
        "examination": {"max_marks": 4, "criteria": "Correct technique, patient comfort"},
        "diagnosis": {"max_marks": 3, "criteria": "Appropriate differential diagnosis"},
        "management": {"max_marks": 2, "criteria": "Evidence-based management plan"}
    }
    ```
    """
    # Try to parse as integer (database ID)
    try:
        id_int = int(osce_id)
        osce = db.query(OSCE).filter(OSCE.id == id_int, OSCE.is_published == True).first()
    except ValueError:
        # Not an integer, treat as osce_id string
        osce = db.query(OSCE).filter(OSCE.osce_id == osce_id, OSCE.is_published == True).first()

    if not osce:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"OSCE station with ID {osce_id} not found"
        )

    return schemas.OSCERubric(
        osce_id=osce.osce_id,
        station_title=osce.station_title,
        station_type=osce.station_type,
        rubric=osce.rubric,
        examiner_instructions=osce.examiner_instructions,
        max_marks=15,
        pass_mark=9,
        time_limit_minutes=osce.time_limit_minutes
    )


@router.post("/{osce_id}/complete-station", response_model=OSCEAttemptResponse)
async def complete_osce_station(
    osce_id: int,
    attempt_data: OSCEAttemptCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Complete OSCE station and record attempt.

    Args:
    - osce_id: OSCE database ID (path parameter)
    - attempt_data: Scores for 5 categories (0-3 each), time taken, self-reflection

    Returns:
    - total_score: Sum of all category scores (max 15)
    - passed: Boolean (True if score >= 9)
    - scores: Category breakdown
    - areas_for_improvement: Categories where score < 2
    - rubric: Complete rubric for self-review
    - attempt_number: User's attempt count for this OSCE

    Side effects:
    - Creates OSCEAttempt record (audit trail)
    - Updates OSCE statistics
    """
    # Verify OSCE exists
    osce = db.query(OSCE).filter(OSCE.id == osce_id, OSCE.is_published == True).first()

    if not osce:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="OSCE not found")

    # Verify osce_id matches (prevent ID mismatch)
    if attempt_data.osce_id != osce_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OSCE ID mismatch between path and request body"
        )

    # Calculate total score
    total_score = sum(attempt_data.scores.values())

    # Determine if passed (9/15 = 60%)
    passed = total_score >= 9

    # Identify weak areas (score < 2)
    weak_areas = [category for category, score in attempt_data.scores.items() if score < 2]

    # Check previous attempts for this user
    previous_attempts = (
        db.query(OSCEAttempt)
        .filter(OSCEAttempt.user_id == current_user.id, OSCEAttempt.osce_id == osce_id)
        .count()
    )

    # Create attempt record
    new_attempt = OSCEAttempt(
        user_id=current_user.id,
        osce_id=osce_id,
        scores=attempt_data.scores,
        total_score=total_score,
        passed=passed,
        time_taken_seconds=attempt_data.time_taken_seconds,
        self_reflection=attempt_data.self_reflection,
        areas_for_improvement=weak_areas if weak_areas else None,
        attempt_number=previous_attempts + 1,
    )

    db.add(new_attempt)

    # Update OSCE statistics
    osce.times_practiced = (osce.times_practiced or 0) + 1
    if osce.average_score is None or osce.average_score == 0.0:
        osce.average_score = float(total_score)
    else:
        # Running average
        osce.average_score = (
            osce.average_score * (osce.times_practiced - 1) + total_score
        ) / osce.times_practiced

    db.commit()
    db.refresh(new_attempt)

    # Build response
    return OSCEAttemptResponse(
        id=new_attempt.id,
        total_score=total_score,
        passed=passed,
        scores=attempt_data.scores,
        time_taken_seconds=attempt_data.time_taken_seconds,
        attempt_number=new_attempt.attempt_number,
        areas_for_improvement=weak_areas if weak_areas else None,
        rubric=osce.rubric,
        examiner_instructions=osce.examiner_instructions,
    )


@router.get("/", response_model=List[schemas.OSCEResponse])
async def list_osces(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    specialty: Optional[MedicalSpecialty] = None,
    osce_type: Optional[OSCEType] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List OSCEs with pagination and optional filtering.

    Query parameters:
    - skip: Number of records to skip (pagination)
    - limit: Maximum number of records to return (max 100)
    - specialty: Filter by medical specialty
    - osce_type: Filter by station type

    Returns list of OSCE stations without rubric.
    """
    query = db.query(OSCE).filter(OSCE.is_published == True)

    if specialty:
        query = query.filter(OSCE.specialty == specialty)
    if osce_type:
        query = query.filter(OSCE.station_type == osce_type)

    osces = query.offset(skip).limit(limit).all()

    return [schemas.OSCEResponse.model_validate(osce) for osce in osces]
