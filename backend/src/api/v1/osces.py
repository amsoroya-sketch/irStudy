"""
OSCE (Objective Structured Clinical Examination) endpoints

Routes:
- GET /api/v1/osces - List OSCEs (filterable by specialty, type)
- GET /api/v1/osces/{osce_id} - Get single OSCE
- POST /api/v1/osces - Create new OSCE (educator/admin only)
- PUT /api/v1/osces/{osce_id} - Update OSCE (educator/admin only)
- DELETE /api/v1/osces/{osce_id} - Delete OSCE (admin only)
- GET /api/v1/osces/{osce_id}/rubric - Get marking rubric

AMC CLINICAL EXAM FORMAT:
- 15-mark rubric system (5 categories × 3 marks each)
- 8-minute station duration
- Categories: History/Examination, Clinical Reasoning, Communication, Safety, Professionalism
- Australian medical context required
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from src.db.base import get_db
from src.db.models import User, OSCE, OSCEAttempt, UserProgress, MedicalSpecialty, OSCEType
from src.schemas.osce import (
    OSCECreate,
    OSCEUpdate,
    OSCEPublic,
    OSCEWithRubric,
    OSCEAttemptCreate,
    OSCEAttemptResponse,
)
from src.auth.dependencies import get_current_active_user, require_educator


router = APIRouter(prefix="/osces", tags=["osces"])


# ============================================================================
# GET RANDOM OSCE
# ============================================================================


@router.get("/random", response_model=OSCEPublic)
async def get_random_osce(
    specialty: Optional[MedicalSpecialty] = None,
    osce_type: Optional[OSCEType] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get random OSCE station with optional filtering.

    Query parameters:
    - specialty: Filter by medical specialty
    - osce_type: Filter by station type (history_taking, physical_exam, etc.)

    Returns:
    - Random OSCE station matching filters
    - Excludes rubric (for practice mode)

    Raises:
    - 404: No OSCEs found matching filters
    """
    import random

    query = db.query(OSCE).filter(OSCE.is_published == True)

    # Apply filters
    if specialty:
        query = query.filter(OSCE.specialty == specialty)

    if osce_type:
        query = query.filter(OSCE.station_type == osce_type)

    total = query.count()
    if total == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No OSCEs found matching filters")

    # Get random OSCE
    offset = random.randint(0, total - 1)
    return query.offset(offset).first()


# ============================================================================
# LIST OSCEs
# ============================================================================


@router.get("/", response_model=List[OSCEPublic])
async def list_osces(
    specialty: Optional[MedicalSpecialty] = None,
    osce_type: Optional[OSCEType] = None,
    tags: Optional[str] = Query(None, description="Comma-separated tags"),
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    List OSCEs with optional filtering.

    Query parameters:
    - specialty: Filter by medical specialty
    - osce_type: Filter by station type (history_taking, physical_exam, etc.)
    - tags: Comma-separated tags
    - skip: Number of records to skip (pagination)
    - limit: Maximum number of records (max 100)

    Returns:
    - List of OSCE stations with instructions
    - Includes patient instructions, candidate instructions, time limit
    - Rubric shown separately (prevents accidental viewing during practice)
    """
    query = db.query(OSCE).filter(OSCE.is_published == True)

    # Apply filters
    if specialty:
        query = query.filter(OSCE.specialty == specialty)

    if osce_type:
        query = query.filter(OSCE.station_type == osce_type)

    if tags:
        tag_list = [tag.strip() for tag in tags.split(",")]
        for tag in tag_list:
            query = query.filter(OSCE.tags.contains([tag]))

    # Pagination
    osces = query.offset(skip).limit(min(limit, 100)).all()

    return osces


# ============================================================================
# GET SINGLE OSCE
# ============================================================================


@router.get("/{osce_id}", response_model=OSCEPublic)
async def get_osce(
    osce_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get single OSCE by ID.

    Args:
    - osce_id: OSCE database ID

    Returns:
    - OSCE station details without rubric
    - Use /osces/{osce_id}/rubric to get marking criteria
    """
    osce = db.query(OSCE).filter(OSCE.id == osce_id, OSCE.is_published == True).first()

    if not osce:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="OSCE not found")

    return osce


# ============================================================================
# GET OSCE RUBRIC
# ============================================================================


@router.get("/{osce_id}/rubric", response_model=OSCEWithRubric)
async def get_osce_rubric(
    osce_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get OSCE station with marking rubric.

    Use this AFTER practice to review marking criteria.

    Args:
    - osce_id: OSCE database ID

    Returns:
    - Complete OSCE with 15-mark AMC format rubric
    - Rubric structure:
      - History/Examination: 0-3 marks
      - Clinical Reasoning: 0-3 marks
      - Communication Skills: 0-3 marks
      - Patient Safety: 0-3 marks
      - Professionalism: 0-3 marks
      - Total: 0-15 marks
    """
    osce = db.query(OSCE).filter(OSCE.id == osce_id, OSCE.is_published == True).first()

    if not osce:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="OSCE not found")

    return osce


# ============================================================================
# CREATE OSCE (Educator/Admin only)
# ============================================================================


@router.post("/", response_model=OSCEWithRubric, status_code=status.HTTP_201_CREATED)
async def create_osce(
    osce_data: OSCECreate,
    current_user: User = Depends(require_educator),
    db: Session = Depends(get_db),
):
    """
    Create new OSCE station (educator/admin only).

    Requirements:
    - osce_id: Unique identifier (format: OSCE-SPEC-XXX)
    - station_title: Descriptive title
    - station_type: Type of station (history_taking, physical_exam, etc.)
    - patient_instructions: Instructions for simulated patient
    - candidate_instructions: Instructions shown to candidate
    - rubric: 15-mark AMC format marking criteria
    - specialty: Medical specialty
    - time_limit_minutes: Default 8 minutes

    AMC Rubric Format (15 marks total):
    ```json
    {
      "history_examination": {
        "criteria": "Systematic approach, completeness, appropriate questions",
        "marks": 3,
        "0": "Did not take history/perform examination",
        "1": "Incomplete/disorganized approach",
        "2": "Good approach with minor omissions",
        "3": "Excellent systematic comprehensive approach"
      },
      "clinical_reasoning": {...},
      "communication": {...},
      "safety": {...},
      "professionalism": {...}
    }
    ```

    Returns:
    - Created OSCE with full details including rubric
    """
    # Check if osce_id already exists
    existing_osce = db.query(OSCE).filter(OSCE.osce_id == osce_data.osce_id).first()
    if existing_osce:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OSCE with osce_id '{osce_data.osce_id}' already exists",
        )

    # Validate rubric structure (should have 5 categories totaling 15 marks)
    if isinstance(osce_data.rubric, dict):
        total_marks = sum(
            category.get("marks", 0)
            for category in osce_data.rubric.values()
            if isinstance(category, dict)
        )
        if total_marks != 15:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Rubric must total 15 marks (AMC format), got {total_marks} marks",
            )

    # Create new OSCE
    new_osce = OSCE(
        osce_id=osce_data.osce_id,
        station_title=osce_data.station_title,
        station_type=osce_data.station_type,
        patient_instructions=osce_data.patient_instructions,
        candidate_instructions=osce_data.candidate_instructions,
        examiner_instructions=osce_data.examiner_instructions,
        rubric=osce_data.rubric,
        specialty=osce_data.specialty,
        time_limit_minutes=osce_data.time_limit_minutes or 8,
        learning_objectives=osce_data.learning_objectives,
        red_flags=osce_data.red_flags,
        australian_guidelines=osce_data.australian_guidelines,
        tags=osce_data.tags,
        is_published=False,  # Requires review before publishing
    )

    db.add(new_osce)
    db.commit()
    db.refresh(new_osce)

    return new_osce


# ============================================================================
# UPDATE OSCE (Educator/Admin only)
# ============================================================================


@router.put("/{osce_id}", response_model=OSCEWithRubric)
async def update_osce(
    osce_id: int,
    osce_update: OSCEUpdate,
    current_user: User = Depends(require_educator),
    db: Session = Depends(get_db),
):
    """
    Update existing OSCE (educator/admin only).

    Args:
    - osce_id: OSCE database ID
    - osce_update: Fields to update (all optional)

    Returns:
    - Updated OSCE with full details

    Note:
    - Updating rubric creates audit trail
    - Consider versioning if OSCE is actively used
    """
    osce = db.query(OSCE).filter(OSCE.id == osce_id).first()

    if not osce:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="OSCE not found")

    # Update fields
    update_data = osce_update.dict(exclude_unset=True)

    # Validate rubric if provided
    if "rubric" in update_data and update_data["rubric"]:
        total_marks = sum(
            category.get("marks", 0)
            for category in update_data["rubric"].values()
            if isinstance(category, dict)
        )
        if total_marks != 15:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Rubric must total 15 marks (AMC format), got {total_marks} marks",
            )

    for field, value in update_data.items():
        setattr(osce, field, value)

    db.commit()
    db.refresh(osce)

    return osce


# ============================================================================
# DELETE OSCE (Admin only)
# ============================================================================


@router.delete("/{osce_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_osce(
    osce_id: int, current_user: User = Depends(require_educator), db: Session = Depends(get_db)
):
    """
    Delete OSCE (soft delete for audit trail).

    Args:
    - osce_id: OSCE database ID

    Note:
    - Performs soft delete (sets deleted_at timestamp)
    - OSCE hidden from queries but data retained
    """
    osce = db.query(OSCE).filter(OSCE.id == osce_id).first()

    if not osce:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="OSCE not found")

    # Soft delete
    from datetime import datetime

    osce.deleted_at = datetime.now(datetime.now().astimezone().tzinfo)

    db.commit()

    return None


# ============================================================================
# COMPLETE OSCE STATION
# ============================================================================


@router.post("/{osce_id}/complete-station", response_model=OSCEAttemptResponse)
async def complete_osce_station(
    osce_id: int,
    attempt_data: OSCEAttemptCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Complete OSCE station and record attempt.

    Args:
    - osce_id: OSCE database ID
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
    - Updates UserProgress analytics
    - Updates OSCE statistics
    """
    # Verify OSCE exists
    if attempt_data.osce_id != osce_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OSCE ID mismatch")

    osce = db.query(OSCE).filter(OSCE.id == osce_id, OSCE.is_published == True).first()

    if not osce:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="OSCE not found")

    # Calculate total score
    total_score = sum(attempt_data.scores.values())

    # Determine if passed (9/15 = 60%)
    passed = total_score >= 9

    # Identify weak areas (score < 2)
    weak_areas = [category for category, score in attempt_data.scores.items() if score < 2]

    # Check previous attempts
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
    osce.times_practiced += 1
    if osce.average_score == 0.0:
        osce.average_score = float(total_score)
    else:
        # Running average
        osce.average_score = (osce.average_score * (osce.times_practiced - 1) + total_score) / osce.times_practiced

    # Update user progress
    progress = (
        db.query(UserProgress)
        .filter(UserProgress.user_id == current_user.id, UserProgress.specialty == osce.specialty)
        .first()
    )

    if not progress:
        # Create new progress record
        progress = UserProgress(
            user_id=current_user.id,
            specialty=osce.specialty,
            total_osces_practiced=1,
            average_osce_score=float(total_score),
            total_study_time_minutes=attempt_data.time_taken_seconds // 60,
            current_streak_days=0,
            longest_streak_days=0,
        )
        db.add(progress)
    else:
        # Update existing progress
        progress.total_osces_practiced += 1
        if progress.average_osce_score == 0.0:
            progress.average_osce_score = float(total_score)
        else:
            # Running average
            progress.average_osce_score = (
                progress.average_osce_score * (progress.total_osces_practiced - 1) + total_score
            ) / progress.total_osces_practiced
        progress.total_study_time_minutes += attempt_data.time_taken_seconds // 60
        progress.last_activity_date = datetime.now(datetime.now().astimezone().tzinfo)

    db.commit()
    db.refresh(new_attempt)

    # Return result with rubric for self-review
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


# ============================================================================
# GET ENHANCED EDUCATIONAL CONTENT (WEEK 3-4)
# ============================================================================


@router.get("/{osce_id}/educational-content", response_model=dict)
async def get_osce_educational_content(
    osce_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get enhanced educational content for OSCE including generated images and study notes.

    WEEK 3-4 FEATURE:
    - Returns educational images (comparison charts, decision trees, timelines, flowcharts)
    - Returns linked study notes
    - Returns clinical pearls and key points

    Args:
        osce_id: OSCE identifier (e.g., "GI-PUD-001")

    Returns:
        {
            "osce": {...},  # Basic OSCE data
            "educational_images": {
                "comparison_charts": [...],
                "decision_trees": [...],
                "timelines": [...],
                "flowcharts": [...]
            },
            "study_notes": [...],  # Linked study notes
            "clinical_pearls": [...],  # Key points from OSCE
            "dr_amir_format": bool  # True if enhanced format
        }

    Raises:
        404: OSCE not found or not published
    """
    from src.db.models import OSCEStudyNote

    # Get OSCE
    osce = db.query(OSCE).filter(OSCE.osce_id == osce_id, OSCE.is_published == True).first()

    if not osce:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"OSCE {osce_id} not found or not published"
        )

    # Get linked study notes
    study_notes = (
        db.query(OSCEStudyNote).filter(OSCEStudyNote.osce_id == osce.id, OSCEStudyNote.is_published == True).all()
    )

    # Format study notes
    study_notes_data = []
    for note in study_notes:
        study_notes_data.append(
            {
                "note_id": note.note_id,
                "title": note.title,
                "content_markdown": note.content_markdown,
                "word_count": note.word_count,
                "reading_time_minutes": note.reading_time_minutes,
                "topics": note.topics,
                "tags": note.tags,
                "amc_relevance": note.amc_relevance,
            }
        )

    return {
        "osce": {
            "osce_id": osce.osce_id,
            "station_title": osce.station_title,
            "specialty": osce.specialty.value,
            "station_type": osce.station_type.value,
            "difficulty": osce.difficulty.value,
            "time_limit_minutes": osce.time_limit_minutes,
        },
        "educational_images": osce.educational_images or {},
        "study_notes": study_notes_data,
        "clinical_pearls": osce.key_points or [],
        "red_flags": osce.red_flags or [],
        "dr_amir_format": osce.dr_amir_format,
    }
