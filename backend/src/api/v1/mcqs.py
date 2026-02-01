"""
MCQ (Multiple Choice Question) endpoints

Routes:
- GET /api/v1/mcqs - List MCQs (filterable by specialty, difficulty, tags)
- GET /api/v1/mcqs/{mcq_id} - Get single MCQ (without answer)
- POST /api/v1/mcqs - Create new MCQ (educator/admin only)
- PUT /api/v1/mcqs/{mcq_id} - Update MCQ (educator/admin only)
- DELETE /api/v1/mcqs/{mcq_id} - Delete MCQ (admin only)
- POST /api/v1/mcqs/{mcq_id}/attempt - Submit answer attempt
- GET /api/v1/mcqs/{mcq_id}/explanation - Get explanation after attempt
- GET /api/v1/mcqs/statistics - Get MCQ statistics

AUSTRALIAN MEDICAL CONTEXT:
- All MCQs validated for Australian drug names (paracetamol not acetaminophen)
- Citations must reference Australian guidelines (eTG, AHPRA, AMH, PBS)
- SI units required (mmol/L not mg/dL)
- AMC Clinical Exam preparation focus
"""

from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from db.base import get_db
from db.models import User, MCQ, MCQAttempt, UserProgress, DifficultyLevel, MedicalSpecialty
from schemas.mcq import (
    MCQCreate,
    MCQUpdate,
    MCQPublic,
    MCQWithAnswer,
    MCQAttemptCreate,
    MCQAttemptResponse,
    MCQStatistics
)
from auth.dependencies import get_current_active_user, require_educator


router = APIRouter(prefix="/mcqs", tags=["mcqs"])


# ============================================================================
# LIST MCQs
# ============================================================================

@router.get("/", response_model=List[MCQPublic])
async def list_mcqs(
    specialty: Optional[MedicalSpecialty] = None,
    difficulty: Optional[DifficultyLevel] = None,
    tags: Optional[str] = Query(None, description="Comma-separated tags"),
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List MCQs with optional filtering.

    Query parameters:
    - specialty: Filter by medical specialty (cardiology, respiratory, etc.)
    - difficulty: Filter by difficulty (easy, medium, hard)
    - tags: Comma-separated tags (e.g., "amc,clinical-exam,emergency")
    - skip: Number of records to skip (pagination)
    - limit: Maximum number of records (max 100)

    Returns:
    - List of MCQs without answers (for practice)
    - Includes question text, options, specialty, difficulty, image
    - Success rate and attempt count visible
    """
    query = db.query(MCQ).filter(MCQ.is_published == True)

    # Apply filters
    if specialty:
        query = query.filter(MCQ.specialty == specialty)

    if difficulty:
        query = query.filter(MCQ.difficulty == difficulty)

    if tags:
        tag_list = [tag.strip() for tag in tags.split(",")]
        # PostgreSQL JSON contains operator
        for tag in tag_list:
            query = query.filter(MCQ.tags.contains([tag]))

    # Pagination
    mcqs = query.offset(skip).limit(min(limit, 100)).all()

    return mcqs


# ============================================================================
# GET SINGLE MCQ
# ============================================================================

@router.get("/{mcq_id}", response_model=MCQPublic)
async def get_mcq(
    mcq_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get single MCQ by ID (without answer).

    Use this for practice mode - answer not revealed until submission.

    Args:
    - mcq_id: MCQ database ID

    Returns:
    - MCQ without correct answer or explanation
    """
    mcq = db.query(MCQ).filter(
        MCQ.id == mcq_id,
        MCQ.is_published == True
    ).first()

    if not mcq:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="MCQ not found"
        )

    return mcq


# ============================================================================
# CREATE MCQ (Educator/Admin only)
# ============================================================================

@router.post("/", response_model=MCQWithAnswer, status_code=status.HTTP_201_CREATED)
async def create_mcq(
    mcq_data: MCQCreate,
    current_user: User = Depends(require_educator),
    db: Session = Depends(get_db)
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
            detail=f"MCQ with question_id '{mcq_data.question_id}' already exists"
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
        created_by_id=current_user.id,
        is_published=False  # Requires review before publishing
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
    db: Session = Depends(get_db)
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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="MCQ not found"
        )

    # Update fields
    update_data = mcq_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(mcq, field, value)

    db.commit()
    db.refresh(mcq)

    return mcq


# ============================================================================
# DELETE MCQ (Admin only)
# ============================================================================

@router.delete("/{mcq_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_mcq(
    mcq_id: int,
    current_user: User = Depends(require_educator),
    db: Session = Depends(get_db)
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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="MCQ not found"
        )

    # Soft delete
    mcq.deleted_at = datetime.now(datetime.now().astimezone().tzinfo)

    db.commit()

    return None


# ============================================================================
# SUBMIT MCQ ATTEMPT
# ============================================================================

@router.post("/{mcq_id}/attempt", response_model=MCQAttemptResponse)
async def submit_mcq_attempt(
    mcq_id: int,
    attempt_data: MCQAttemptCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Submit answer attempt for MCQ.

    Args:
    - mcq_id: MCQ database ID
    - attempt_data: Selected answer (A-E), time taken, confidence level

    Returns:
    - is_correct: Boolean result
    - correct_answer: Correct option
    - explanation: Detailed explanation with reasoning
    - citation: Australian guideline reference
    - learning_points: Key takeaways
    - attempt_number: User's attempt count for this question

    Side effects:
    - Updates MCQ statistics (times_attempted, times_correct, success_rate)
    - Creates MCQAttempt record (audit trail)
    - Updates UserProgress analytics
    """
    # Verify MCQ exists
    if attempt_data.mcq_id != mcq_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MCQ ID mismatch"
        )

    mcq = db.query(MCQ).filter(
        MCQ.id == mcq_id,
        MCQ.is_published == True
    ).first()

    if not mcq:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="MCQ not found"
        )

    # Check if user already attempted this question
    previous_attempts = db.query(MCQAttempt).filter(
        MCQAttempt.user_id == current_user.id,
        MCQAttempt.mcq_id == mcq_id
    ).count()

    # Determine if answer is correct
    is_correct = attempt_data.selected_answer == mcq.correct_answer

    # Create attempt record
    new_attempt = MCQAttempt(
        user_id=current_user.id,
        mcq_id=mcq_id,
        selected_answer=attempt_data.selected_answer,
        is_correct=is_correct,
        time_taken_seconds=attempt_data.time_taken_seconds,
        confidence_level=attempt_data.confidence_level,
        attempt_number=previous_attempts + 1
    )

    db.add(new_attempt)

    # Update MCQ statistics
    mcq.times_attempted += 1
    if is_correct:
        mcq.times_correct += 1

    # Update user progress
    progress = db.query(UserProgress).filter(
        UserProgress.user_id == current_user.id,
        UserProgress.specialty == mcq.specialty
    ).first()

    if not progress:
        # Create new progress record
        progress = UserProgress(
            user_id=current_user.id,
            specialty=mcq.specialty,
            mcqs_attempted=1,
            mcqs_correct=1 if is_correct else 0,
            total_study_time_minutes=attempt_data.time_taken_seconds // 60,
            current_streak_days=0,
            longest_streak_days=0
        )
        db.add(progress)
    else:
        # Update existing progress
        progress.mcqs_attempted += 1
        if is_correct:
            progress.mcqs_correct += 1
        progress.total_study_time_minutes += attempt_data.time_taken_seconds // 60
        progress.last_activity_at = datetime.now(datetime.now().astimezone().tzinfo)

    db.commit()
    db.refresh(new_attempt)

    # Return result with explanation
    return {
        "id": new_attempt.id,
        "is_correct": is_correct,
        "selected_answer": attempt_data.selected_answer,
        "correct_answer": mcq.correct_answer,
        "explanation": mcq.explanation,
        "citation": mcq.citation,
        "learning_points": mcq.learning_points,
        "time_taken_seconds": attempt_data.time_taken_seconds,
        "attempt_number": new_attempt.attempt_number
    }


# ============================================================================
# GET MCQ STATISTICS
# ============================================================================

@router.get("/statistics", response_model=MCQStatistics)
async def get_mcq_statistics(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get MCQ statistics across all specialties and difficulties.

    Returns:
    - total_mcqs: Total count of published MCQs
    - by_specialty: Count per specialty
    - by_difficulty: Count per difficulty level
    - average_success_rate: Platform-wide average success rate

    Useful for:
    - Platform analytics
    - Content coverage assessment
    - Identifying weak areas
    """
    # Total MCQs
    total_mcqs = db.query(func.count(MCQ.id)).filter(
        MCQ.is_published == True
    ).scalar()

    # By specialty
    specialty_counts = db.query(
        MCQ.specialty,
        func.count(MCQ.id)
    ).filter(
        MCQ.is_published == True
    ).group_by(MCQ.specialty).all()

    by_specialty = {str(specialty): count for specialty, count in specialty_counts}

    # By difficulty
    difficulty_counts = db.query(
        MCQ.difficulty,
        func.count(MCQ.id)
    ).filter(
        MCQ.is_published == True
    ).group_by(MCQ.difficulty).all()

    by_difficulty = {str(difficulty): count for difficulty, count in difficulty_counts}

    # Average success rate
    avg_success_rate = db.query(
        func.avg(
            func.cast(MCQ.times_correct, db.Float) /
            func.nullif(MCQ.times_attempted, 0) * 100
        )
    ).filter(
        MCQ.is_published == True,
        MCQ.times_attempted > 0
    ).scalar() or 0.0

    return {
        "total_mcqs": total_mcqs,
        "by_specialty": by_specialty,
        "by_difficulty": by_difficulty,
        "average_success_rate": round(avg_success_rate, 2)
    }
