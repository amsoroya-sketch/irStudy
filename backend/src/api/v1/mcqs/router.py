"""
MCQ API endpoints for irStudy Medical Education Platform

AUSTRALIAN CONTEXT:
- Drug names: Australian only (paracetamol NOT acetaminophen)
- Citations: eTG, PBS, AMH, AHPRA only
- All content validated against Australian medical guidelines

ENDPOINTS:
- GET /mcqs/random - Get random MCQ by specialty/difficulty (AUTH REQUIRED)
- GET /mcqs/{id} - Get specific MCQ by ID (AUTH REQUIRED)
- GET /mcqs - List MCQs with filters (AUTH REQUIRED)
- POST /mcqs - Create new MCQ (educator/admin only)
- PUT /mcqs/{id} - Update MCQ (educator/admin only)
- DELETE /mcqs/{id} - Delete MCQ (educator/admin only)
- POST /mcqs/{id}/attempt - Submit answer and get explanation (AUTH REQUIRED)
- GET /mcqs/{id}/explanation - Get explanation with citations (AUTH REQUIRED)
- GET /mcqs/statistics - Get user statistics (AUTH REQUIRED)
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
import random

from src.db.base import get_db
from src.db.models import MCQ, MCQAttempt, MedicalSpecialty, DifficultyLevel, User
from src.auth.dependencies import get_current_active_user, require_educator
from src.api.v1.mcqs import schemas
from src.schemas.mcq import MCQCreate, MCQUpdate, MCQWithAnswer

router = APIRouter(prefix="/mcqs", tags=["MCQ Practice"])


# ============================================================================
# GET MCQ STATISTICS
# ============================================================================


@router.get("/statistics", response_model=schemas.MCQStatistics)
async def get_mcq_statistics(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get platform-wide MCQ statistics.

    **Authentication Required:** JWT token

    **Returns:**
    - total_mcqs: Total number of published MCQs
    - by_specialty: Breakdown of MCQs by specialty
    - by_difficulty: Breakdown of MCQs by difficulty
    - average_success_rate: Platform-wide average success rate
    """
    # Total published MCQs
    total_mcqs = db.query(MCQ).filter(MCQ.is_published == True).count()

    # MCQs by specialty
    specialty_counts = {}
    for specialty in MedicalSpecialty:
        count = db.query(MCQ).filter(
            MCQ.is_published == True,
            MCQ.specialty == specialty
        ).count()
        if count > 0:
            specialty_counts[specialty.value] = count

    # MCQs by difficulty
    difficulty_counts = {}
    for difficulty in DifficultyLevel:
        count = db.query(MCQ).filter(
            MCQ.is_published == True,
            MCQ.difficulty == difficulty
        ).count()
        if count > 0:
            difficulty_counts[difficulty.value] = count

    # Calculate average success rate
    mcqs = db.query(MCQ).filter(MCQ.is_published == True).all()
    success_rates = [mcq.success_rate for mcq in mcqs if mcq.times_attempted > 0]
    average_success_rate = sum(success_rates) / len(success_rates) if success_rates else 0.0

    return schemas.MCQStatistics(
        total_mcqs=total_mcqs,
        by_specialty=specialty_counts,
        by_difficulty=difficulty_counts,
        average_success_rate=average_success_rate
    )


# ============================================================================
# GET RANDOM MCQ
# ============================================================================


@router.get("/random", response_model=schemas.MCQResponse)
async def get_random_mcq(
    specialty: Optional[MedicalSpecialty] = Query(None, description="Filter by medical specialty"),
    difficulty: Optional[DifficultyLevel] = Query(None, description="Filter by difficulty level"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get a random MCQ question.

    **Authentication Required:** JWT token

    **Australian Context:**
    - All questions use Australian drug names (paracetamol, salbutamol, adrenaline)
    - Citations reference Australian guidelines (eTG, PBS, AMH, AHPRA)

    **Query Parameters:**
    - specialty: Filter by specialty (cardiology, respiratory, etc.)
    - difficulty: Filter by difficulty (easy, medium, hard)
    """
    query = db.query(MCQ).filter(MCQ.is_published == True)

    if specialty:
        query = query.filter(MCQ.specialty == specialty)
    if difficulty:
        query = query.filter(MCQ.difficulty == difficulty)

    mcqs = query.all()

    if not mcqs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No MCQs found matching criteria"
        )

    selected_mcq = random.choice(mcqs)

    return schemas.MCQResponse.model_validate(selected_mcq)


# ============================================================================
# LIST MCQs
# ============================================================================


@router.get("/", response_model=schemas.MCQListResponse)
async def list_mcqs(
    specialty: Optional[MedicalSpecialty] = Query(None, description="Filter by medical specialty"),
    difficulty: Optional[DifficultyLevel] = Query(None, description="Filter by difficulty level"),
    tags: Optional[str] = Query(None, description="Comma-separated tags"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum records to return"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List MCQs with optional filters.

    **Authentication Required:** JWT token

    **Query Parameters:**
    - specialty: Filter by specialty (cardiology, respiratory, etc.)
    - difficulty: Filter by difficulty (easy, medium, hard)
    - tags: Comma-separated tags (e.g., "STEMI,ECG")
    - skip: Pagination offset (default: 0)
    - limit: Max records (default: 50, max: 100)
    """
    query = db.query(MCQ).filter(MCQ.is_published == True)

    if specialty:
        query = query.filter(MCQ.specialty == specialty)
    if difficulty:
        query = query.filter(MCQ.difficulty == difficulty)
    if tags:
        tag_list = [tag.strip() for tag in tags.split(",")]
        for tag in tag_list:
            query = query.filter(MCQ.tags.contains([tag]))

    # Get total count before pagination
    total = query.count()

    mcqs = query.offset(skip).limit(limit).all()

    return schemas.MCQListResponse(
        items=[schemas.MCQResponse.model_validate(mcq) for mcq in mcqs],
        total=total,
        skip=skip,
        limit=limit
    )


# ============================================================================
# GET SINGLE MCQ
# ============================================================================


@router.get("/{mcq_id}", response_model=schemas.MCQResponse)
async def get_mcq(
    mcq_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get specific MCQ by ID.

    **Authentication Required:** JWT token

    **Example:** GET /mcqs/1
    """
    mcq = db.query(MCQ).filter(MCQ.id == mcq_id, MCQ.is_published == True).first()

    if not mcq:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"MCQ with ID {mcq_id} not found"
        )

    return schemas.MCQResponse.model_validate(mcq)


# ============================================================================
# CREATE MCQ (Educator/Admin only)
# ============================================================================


@router.post("/", response_model=MCQWithAnswer, status_code=status.HTTP_201_CREATED)
async def create_mcq(
    mcq_data: MCQCreate,
    current_user: User = Depends(require_educator),
    db: Session = Depends(get_db),
):
    """
    Create new MCQ (educator/admin only).

    Requirements:
    - question_id: Unique identifier (format: MCQ-SPEC-XXX)
    - question_text: 50-5000 characters
    - options: 4-5 options (A-E)
    - correct_answer: Single letter (A-E)
    - explanation: 100-5000 characters
    - citation: Australian guideline reference (eTG, AHPRA, AMH, PBS)
    - specialty: Medical specialty
    - difficulty: easy/medium/hard

    Validation:
    - Rejects American drug names (acetaminophen, epinephrine, albuterol)
    - Requires Australian guideline citations
    - Validates question_id format

    Returns:
    - Created MCQ with full details including answer
    """
    # Check if question_id already exists
    existing_mcq = db.query(MCQ).filter(MCQ.question_id == mcq_data.question_id).first()
    if existing_mcq:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"MCQ with question_id '{mcq_data.question_id}' already exists",
        )

    # Create new MCQ
    new_mcq = MCQ(
        question_id=mcq_data.question_id,
        question_text=mcq_data.question_text,
        options=mcq_data.options,
        correct_answer=mcq_data.correct_answer,
        explanation=mcq_data.explanation,
        citation=mcq_data.citation,
        learning_points=mcq_data.learning_points,
        specialty=mcq_data.specialty,
        difficulty=mcq_data.difficulty,
        tags=mcq_data.tags,
        image_url=mcq_data.image_url,
        image_caption=mcq_data.image_caption,
        is_published=False,  # Requires review before publishing
    )

    db.add(new_mcq)
    db.commit()
    db.refresh(new_mcq)

    return new_mcq


# ============================================================================
# UPDATE MCQ (Educator/Admin only)
# ============================================================================


@router.put("/{mcq_id}", response_model=MCQWithAnswer)
async def update_mcq(
    mcq_id: int,
    mcq_update: MCQUpdate,
    current_user: User = Depends(require_educator),
    db: Session = Depends(get_db),
):
    """
    Update existing MCQ (educator/admin only).

    Args:
    - mcq_id: MCQ database ID
    - mcq_update: Fields to update (all optional)

    Returns:
    - Updated MCQ with full details

    Note:
    - Updating published MCQ creates audit trail
    - Consider versioning if MCQ has existing attempts
    """
    mcq = db.query(MCQ).filter(MCQ.id == mcq_id).first()

    if not mcq:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="MCQ not found")

    # Update fields
    update_data = mcq_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(mcq, field, value)

    db.commit()
    db.refresh(mcq)

    return mcq


# ============================================================================
# DELETE MCQ (Educator/Admin only)
# ============================================================================


@router.delete("/{mcq_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_mcq(
    mcq_id: int, current_user: User = Depends(require_educator), db: Session = Depends(get_db)
):
    """
    Delete MCQ (soft delete for audit trail).

    Args:
    - mcq_id: MCQ database ID

    Note:
    - Performs soft delete (sets deleted_at timestamp)
    - MCQ hidden from queries but data retained
    - Existing attempts preserved for user statistics
    """
    mcq = db.query(MCQ).filter(MCQ.id == mcq_id).first()

    if not mcq:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="MCQ not found")

    # Soft delete
    mcq.deleted_at = datetime.now(datetime.now().astimezone().tzinfo)

    db.commit()

    return None


# ============================================================================
# SUBMIT MCQ ATTEMPT
# ============================================================================


@router.post("/{mcq_id}/attempt", response_model=schemas.MCQSubmitResponse)
async def submit_mcq_attempt(
    mcq_id: int,
    submission: schemas.MCQSubmit,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Submit answer to MCQ and receive feedback.

    **Authentication Required:** JWT token

    **Returns:**
    - is_correct: Whether answer was correct
    - selected_answer: User's selected answer
    - correct_answer: The correct option letter
    - explanation: Detailed explanation with clinical reasoning
    - citation: Australian guideline reference
    - learning_points: Key learning points (if available)
    - attempt_number: Number of attempts for this MCQ by user
    """
    # Validate mcq_id in URL matches request body
    if submission.mcq_id != mcq_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"MCQ ID mismatch: URL has {mcq_id}, body has {submission.mcq_id}"
        )

    mcq = db.query(MCQ).filter(MCQ.id == mcq_id).first()

    if not mcq:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"MCQ with ID {mcq_id} not found"
        )

    is_correct = submission.selected_answer.upper() == mcq.correct_answer

    # Calculate attempt number (previous attempts + 1)
    previous_attempts = db.query(MCQAttempt).filter(
        MCQAttempt.user_id == current_user.id,
        MCQAttempt.mcq_id == mcq.id
    ).count()
    attempt_number = previous_attempts + 1

    # Record attempt
    attempt = MCQAttempt(
        user_id=current_user.id,
        mcq_id=mcq.id,
        selected_answer=submission.selected_answer.upper(),
        is_correct=is_correct,
        time_taken_seconds=submission.time_taken_seconds or 0
    )
    db.add(attempt)
    db.commit()

    return schemas.MCQSubmitResponse(
        is_correct=is_correct,
        selected_answer=submission.selected_answer.upper(),
        correct_answer=mcq.correct_answer,
        explanation=mcq.explanation,
        citation=mcq.citation,
        learning_points=mcq.learning_points,
        attempt_number=attempt_number
    )


# ============================================================================
# GET MCQ EXPLANATION
# ============================================================================


@router.get("/{mcq_id}/explanation", response_model=schemas.MCQExplanation)
async def get_mcq_explanation(
    mcq_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed explanation and citation for MCQ.

    **Authentication Required:** JWT token

    **Australian Context:**
    - All citations reference Australian medical guidelines
    - Drug names use Australian terminology
    - Emergency protocols follow Australian standards
    """
    mcq = db.query(MCQ).filter(MCQ.id == mcq_id).first()

    if not mcq:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"MCQ with ID {mcq_id} not found"
        )

    return schemas.MCQExplanation(
        correct_answer=mcq.correct_answer,
        explanation=mcq.explanation,
        citation=mcq.citation,
        learning_points=mcq.learning_points,
        specialty=mcq.specialty,
        difficulty=mcq.difficulty
    )
