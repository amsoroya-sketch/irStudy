"""
User progress and analytics endpoints

Routes:
- GET /api/v1/progress/dashboard - Comprehensive dashboard analytics
- GET /api/v1/progress/specialty/{specialty} - Detailed specialty performance
- GET /api/v1/progress/weak-areas - Identify weak topics/specialties
- GET /api/v1/progress/trends/weekly - Weekly progress trends

FEATURES:
- Personalized analytics based on MCQ attempts, OSCE completions, Study Cards
- Weak area identification (topics with <70% success rate)
- Study streak tracking
- Specialty-specific progress breakdown
- Weekly/monthly trend analysis
- Australian medical context preserved

PRIVACY:
- All data scoped to current_user (never exposes other users' data)
- No raw user IDs or sensitive information exposed
- Database-level filtering for security

PERFORMANCE:
- Response time target: <200ms
- Database aggregations for efficiency
- No N+1 queries
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, status, Query
from sqlalchemy import func, case
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address

from src.db.base import get_db
from src.db.models import (
    User,
    MCQ,
    MCQAttempt,
    OSCE,
    OSCEAttempt,
    StudyCard,
    StudyCardReview,
    UserProgress,
    MedicalSpecialty,
    DifficultyLevel,
)
from src.schemas.progress import (
    DashboardResponse,
    SpecialtyDetailResponse,
    WeakAreasResponse,
    WeeklyTrendsResponse,
    SpecialtyPerformance,
    WeakArea,
    WeeklyTrend,
)
from src.auth.dependencies import get_current_active_user
from src.services.progress_analytics import ProgressAnalytics


# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

router = APIRouter(prefix="/progress", tags=["progress"])


# ============================================================================
# GET DASHBOARD ANALYTICS
# ============================================================================


@router.get("/dashboard", response_model=DashboardResponse)
@limiter.limit("60/minute")
async def get_dashboard(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get comprehensive dashboard analytics for current user.

    FEATURES:
    - MCQ performance metrics (total attempts, accuracy)
    - OSCE completion tracking (total stations practiced)
    - Study Card statistics (reviews, retention rate)
    - Specialty breakdown (performance per specialty)
    - Weak areas identification (specialties below 70% threshold)

    Returns:
    - DashboardResponse: Comprehensive analytics

    Privacy:
    - All data filtered by current_user.id
    - Never exposes other users' data

    Performance:
    - Response time: <200ms
    - Uses database aggregations
    - No N+1 queries

    Example Response:
    {
        "total_mcq_attempts": 152,
        "mcq_accuracy_rate": 73.68,
        "total_osce_completions": 8,
        "study_cards_reviewed": 64,
        "study_card_retention_rate": 78.12,
        "specialty_breakdown": [...],
        "weak_areas": [...]
    }
    """
    # MCQ statistics
    total_mcq = db.query(MCQAttempt).filter(MCQAttempt.user_id == current_user.id).count()
    mcq_accuracy = ProgressAnalytics.get_mcq_accuracy(db, current_user.id)

    # OSCE statistics
    total_osce = db.query(OSCEAttempt).filter(OSCEAttempt.user_id == current_user.id).count()

    # Study Card statistics
    cards_reviewed = (
        db.query(StudyCardReview).filter(StudyCardReview.user_id == current_user.id).count()
    )
    card_retention = ProgressAnalytics.get_study_card_retention(db, current_user.id)

    # Specialty breakdown
    specialty_breakdown_raw = ProgressAnalytics.get_specialty_breakdown(db, current_user.id)
    specialty_breakdown = [SpecialtyPerformance(**item) for item in specialty_breakdown_raw]

    # Weak areas (default threshold 70%)
    weak_areas_raw = ProgressAnalytics.get_weak_areas(db, current_user.id, threshold=70.0)
    weak_areas = [WeakArea(**item) for item in weak_areas_raw]

    return DashboardResponse(
        total_mcq_attempts=total_mcq,
        mcq_accuracy_rate=mcq_accuracy,
        total_osce_completions=total_osce,
        study_cards_reviewed=cards_reviewed,
        study_card_retention_rate=card_retention,
        specialty_breakdown=specialty_breakdown,
        weak_areas=weak_areas,
    )


# ============================================================================
# GET SPECIALTY DETAIL
# ============================================================================


@router.get("/specialty/{specialty_name}", response_model=SpecialtyDetailResponse)
@limiter.limit("60/minute")
async def get_specialty_detail(
    specialty_name: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get detailed performance for one specialty.

    Args:
    - specialty_name: Medical specialty (cardiology, respiratory, etc.)

    Returns:
    - SpecialtyDetailResponse: Detailed specialty metrics
        - total_attempts: Total MCQ attempts
        - correct_attempts: Number of correct answers
        - accuracy_rate: Success percentage
        - average_time_seconds: Average time per question
        - osce_completions: OSCE stations practiced
        - study_cards_available: Available study cards count
        - recent_attempts: Attempts in last 7 days

    Raises:
    - 400: Invalid specialty name
    - 404: No attempts found for this specialty

    Privacy:
    - All data filtered by current_user.id

    Example Response:
    {
        "specialty": "cardiology",
        "total_attempts": 45,
        "correct_attempts": 32,
        "accuracy_rate": 71.11,
        "average_time_seconds": 95,
        "osce_completions": 3,
        "study_cards_available": 82,
        "recent_attempts": 12
    }
    """
    # Validate specialty name
    try:
        specialty = MedicalSpecialty(specialty_name.lower())
    except ValueError:
        valid_specialties = [s.value for s in MedicalSpecialty]
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid specialty. Valid options: {', '.join(valid_specialties)}",
        )

    # Get specialty detail
    detail = ProgressAnalytics.get_specialty_detail(db, current_user.id, specialty)

    if not detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No attempts found for specialty: {specialty_name}",
        )

    return SpecialtyDetailResponse(**detail)


# ============================================================================
# GET WEAK AREAS
# ============================================================================


@router.get("/weak-areas", response_model=WeakAreasResponse)
@limiter.limit("60/minute")
async def get_weak_areas(
    request: Request,
    threshold: float = Query(70.0, ge=0, le=100, description="Accuracy threshold percentage"),
    min_attempts: int = Query(5, ge=1, le=50, description="Minimum attempts required"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Identify specialties needing improvement.

    CRITERIA:
    - Accuracy below threshold (default 70%)
    - Minimum attempts >= min_attempts (default 5)

    Query Parameters:
    - threshold: Accuracy threshold percentage (0-100, default 70.0)
    - min_attempts: Minimum attempts required (1-50, default 5)

    Returns:
    - WeakAreasResponse: Weak specialties with recommendations
        - threshold: Threshold used
        - min_attempts: Minimum attempts used
        - weak_areas: List of weak specialties
            - specialty: Specialty name
            - accuracy_rate: Success percentage
            - total_attempts: Total attempts
            - recommended_study_cards: Available study cards count

    Privacy:
    - All data filtered by current_user.id

    Example Response:
    {
        "threshold": 70.0,
        "min_attempts": 5,
        "weak_areas": [
            {
                "specialty": "neurology",
                "accuracy_rate": 58.33,
                "total_attempts": 12,
                "recommended_study_cards": 47
            }
        ]
    }
    """
    # Get weak areas
    weak_areas_raw = ProgressAnalytics.get_weak_areas(
        db, current_user.id, threshold=threshold, min_attempts=min_attempts
    )
    weak_areas = [WeakArea(**item) for item in weak_areas_raw]

    return WeakAreasResponse(
        threshold=threshold, min_attempts=min_attempts, weak_areas=weak_areas
    )


# ============================================================================
# GET WEEKLY TRENDS
# ============================================================================


@router.get("/trends/weekly", response_model=WeeklyTrendsResponse)
@limiter.limit("60/minute")
async def get_weekly_trends(
    request: Request,
    weeks: int = Query(4, ge=1, le=12, description="Number of weeks (max 12)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get weekly progress trends.

    Query Parameters:
    - weeks: Number of weeks to retrieve (1-12, default 4)

    Returns:
    - WeeklyTrendsResponse: Weekly trend data
        - weeks: Number of weeks
        - trends: List of weekly data (most recent first)
            - week_start: Start date of the week (Monday)
            - mcq_attempts: MCQ attempts during this week
            - accuracy_rate: Success percentage for this week
            - study_cards_reviewed: Study cards reviewed during this week

    Privacy:
    - All data filtered by current_user.id

    Example Response:
    {
        "weeks": 4,
        "trends": [
            {
                "week_start": "2026-02-10T00:00:00Z",
                "mcq_attempts": 28,
                "accuracy_rate": 75.00,
                "study_cards_reviewed": 15
            },
            {
                "week_start": "2026-02-03T00:00:00Z",
                "mcq_attempts": 35,
                "accuracy_rate": 71.43,
                "study_cards_reviewed": 22
            }
        ]
    }
    """
    # Get weekly trends
    trends_raw = ProgressAnalytics.get_weekly_trends(db, current_user.id, weeks=weeks)
    trends = [WeeklyTrend(**item) for item in trends_raw]

    return WeeklyTrendsResponse(weeks=weeks, trends=trends)
