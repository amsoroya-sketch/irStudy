"""
Progress Tracking API Router
Endpoints for user progress, streaks, and learning analytics
"""

from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from src.db.base import get_db
from src.db.models import UserProgress, User, MedicalSpecialty
from .schemas import (
    ProgressResponse,
    AllProgressResponse,
    StreakResponse,
    WeakTopicsResponse,
    UpdateProgressRequest,
)

router = APIRouter(prefix="/progress", tags=["Progress Tracking"])


# ============================================================================
# GET ENDPOINTS
# ============================================================================


@router.get("/{user_id}", response_model=AllProgressResponse)
def get_user_progress(
    user_id: int,
    specialty: Optional[str] = Query(None, description="Filter by specialty"),
    db: Session = Depends(get_db),
):
    """
    Get user's progress across all specialties or for a specific specialty.

    **Australian Medical Context:**
    - Tracks progress across AMC Part 1 exam specialties
    - Monitors MCQ performance (AMC blueprint alignment)
    - Tracks OSCE practice (AMC Clinical Exam preparation)
    """
    # Verify user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")

    # Build query
    query = db.query(UserProgress).filter(UserProgress.user_id == user_id)

    if specialty:
        # Validate specialty
        try:
            MedicalSpecialty(specialty)
        except ValueError:
            raise HTTPException(
                status_code=422,
                detail=f"Invalid specialty: {specialty}. Must be one of: {[s.value for s in MedicalSpecialty]}",
            )
        query = query.filter(UserProgress.specialty == specialty)

    progress_records = query.all()

    # Calculate aggregate statistics
    total_mcqs = sum(p.total_mcqs_attempted for p in progress_records)
    total_correct = sum(p.total_mcqs_correct for p in progress_records)
    total_study_time = sum(p.total_study_time_minutes for p in progress_records)
    overall_success_rate = (total_correct / total_mcqs * 100) if total_mcqs > 0 else 0.0
    active_specialties = len([p for p in progress_records if p.total_mcqs_attempted > 0 or p.total_osces_practiced > 0])

    return AllProgressResponse(
        user_id=user_id,
        progress_records=[ProgressResponse.model_validate(p) for p in progress_records],
        total_mcqs_attempted=total_mcqs,
        total_study_time_minutes=total_study_time,
        overall_success_rate=round(overall_success_rate, 2),
        active_specialties=active_specialties,
    )


@router.get("/{user_id}/specialty/{specialty}", response_model=ProgressResponse)
def get_specialty_progress(
    user_id: int,
    specialty: str,
    db: Session = Depends(get_db),
):
    """
    Get user's progress for a specific specialty.

    **Example:** GET /progress/123/specialty/Cardiology
    """
    # Validate specialty
    try:
        MedicalSpecialty(specialty)
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid specialty: {specialty}. Must be one of: {[s.value for s in MedicalSpecialty]}",
        )

    progress = (
        db.query(UserProgress).filter(UserProgress.user_id == user_id, UserProgress.specialty == specialty).first()
    )

    if not progress:
        raise HTTPException(status_code=404, detail=f"No progress found for user {user_id} in {specialty}")

    return ProgressResponse.model_validate(progress)


@router.get("/{user_id}/streak", response_model=StreakResponse)
def get_user_streak(
    user_id: int,
    db: Session = Depends(get_db),
):
    """
    Get user's current and longest study streak.

    **Australian Context:**
    - Encourages consistent daily study for AMC exam preparation
    - Streak maintained by any activity (MCQ or OSCE)
    """
    # Get latest progress record (highest current_streak)
    progress = (
        db.query(UserProgress)
        .filter(UserProgress.user_id == user_id)
        .order_by(UserProgress.current_streak_days.desc())
        .first()
    )

    if not progress:
        raise HTTPException(status_code=404, detail=f"No progress found for user {user_id}")

    # Check if user has studied today
    is_active_today = False
    if progress.last_activity_date:
        today = datetime.now(timezone.utc).date()
        last_activity = progress.last_activity_date.date()
        is_active_today = today == last_activity

    return StreakResponse(
        user_id=user_id,
        current_streak_days=progress.current_streak_days,
        longest_streak_days=progress.longest_streak_days,
        last_activity_date=progress.last_activity_date,
        is_active_today=is_active_today,
    )


@router.get("/{user_id}/weak-topics", response_model=WeakTopicsResponse)
def get_weak_topics(
    user_id: int,
    db: Session = Depends(get_db),
):
    """
    Get aggregated weak topics across all specialties for targeted revision.

    **Australian Context:**
    - Identifies areas requiring additional study (aligned with eTG, AMH guidelines)
    - Supports targeted revision for AMC exam weak areas
    """
    progress_records = db.query(UserProgress).filter(UserProgress.user_id == user_id).all()

    if not progress_records:
        raise HTTPException(status_code=404, detail=f"No progress found for user {user_id}")

    weak_topics = []
    total_count = 0

    for progress in progress_records:
        if progress.weak_topics and len(progress.weak_topics) > 0:
            weak_topics.append({"specialty": progress.specialty.value, "topics": progress.weak_topics})
            total_count += len(progress.weak_topics)

    return WeakTopicsResponse(
        user_id=user_id,
        weak_topics=weak_topics,
        total_weak_topics=total_count,
    )


# ============================================================================
# POST ENDPOINTS
# ============================================================================


@router.post("/{user_id}/update", response_model=ProgressResponse)
def update_progress(
    user_id: int,
    request: UpdateProgressRequest,
    db: Session = Depends(get_db),
):
    """
    Update user progress after completing an MCQ or OSCE activity.

    **Australian Context:**
    - Records MCQ attempts (AMC Part 1 question bank simulation)
    - Records OSCE practice (AMC Clinical Exam preparation)
    - Uses Australian terminology (paracetamol, salbutamol, etc.)

    **Example MCQ Update:**
    ```json
    {
        "specialty": "Cardiology",
        "activity_type": "mcq",
        "is_correct": true,
        "study_time_minutes": 3
    }
    ```

    **Example OSCE Update:**
    ```json
    {
        "specialty": "Neurology",
        "activity_type": "osce",
        "osce_score": 12.5,
        "study_time_minutes": 8,
        "weak_topics": ["stroke assessment", "GCS"]
    }
    ```
    """
    # Validate specialty
    try:
        specialty_enum = MedicalSpecialty(request.specialty)
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid specialty: {request.specialty}. Must be one of: {[s.value for s in MedicalSpecialty]}",
        )

    # Validate activity type
    if request.activity_type not in ["mcq", "osce"]:
        raise HTTPException(status_code=422, detail="activity_type must be 'mcq' or 'osce'")

    # Validate MCQ requirements
    if request.activity_type == "mcq" and request.is_correct is None:
        raise HTTPException(status_code=422, detail="is_correct is required for MCQ activities")

    # Validate OSCE requirements
    if request.activity_type == "osce" and request.osce_score is None:
        raise HTTPException(status_code=422, detail="osce_score is required for OSCE activities")

    # Get or create progress record
    progress = (
        db.query(UserProgress).filter(UserProgress.user_id == user_id, UserProgress.specialty == specialty_enum).first()
    )

    if not progress:
        # Create new progress record
        progress = UserProgress(
            user_id=user_id,
            specialty=specialty_enum,
            total_mcqs_attempted=0,
            total_mcqs_correct=0,
            unique_mcqs_attempted=0,
            total_osces_practiced=0,
            average_osce_score=0.0,
            current_streak_days=0,
            longest_streak_days=0,
            total_study_time_minutes=0,
            weak_topics=[],
            mastery_percentage=0.0,
        )
        db.add(progress)

    # Update based on activity type
    if request.activity_type == "mcq":
        progress.total_mcqs_attempted += 1
        if request.is_correct:
            progress.total_mcqs_correct += 1

    elif request.activity_type == "osce":
        progress.total_osces_practiced += 1
        # Calculate running average OSCE score
        total_score = progress.average_osce_score * (progress.total_osces_practiced - 1) + request.osce_score
        progress.average_osce_score = round(total_score / progress.total_osces_practiced, 2)

    # Update study time
    progress.total_study_time_minutes += request.study_time_minutes

    # Update weak topics (merge with existing)
    if request.weak_topics:
        existing_topics = progress.weak_topics or []
        progress.weak_topics = list(set(existing_topics + request.weak_topics))

    # Update streak
    now = datetime.now(timezone.utc)
    if progress.last_activity_date:
        last_date = progress.last_activity_date.date()
        today = now.date()
        days_diff = (today - last_date).days

        if days_diff == 0:
            # Same day - no change to streak
            pass
        elif days_diff == 1:
            # Consecutive day - increment streak
            progress.current_streak_days += 1
            progress.longest_streak_days = max(progress.longest_streak_days, progress.current_streak_days)
        else:
            # Streak broken - reset to 1
            progress.current_streak_days = 1
    else:
        # First activity - start streak
        progress.current_streak_days = 1
        progress.longest_streak_days = 1

    progress.last_activity_date = now

    # Calculate mastery percentage (simple formula: weighted average of MCQ success rate and OSCE performance)
    mcq_weight = 0.6  # MCQ contributes 60%
    osce_weight = 0.4  # OSCE contributes 40%

    mcq_mastery = (progress.total_mcqs_correct / progress.total_mcqs_attempted * 100) if progress.total_mcqs_attempted > 0 else 0
    osce_mastery = (progress.average_osce_score / 15 * 100) if progress.average_osce_score > 0 else 0

    progress.mastery_percentage = round(mcq_weight * mcq_mastery + osce_weight * osce_mastery, 2)

    db.commit()
    db.refresh(progress)

    return ProgressResponse.model_validate(progress)
