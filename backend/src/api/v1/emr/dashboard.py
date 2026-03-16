"""
EMR Dashboard Analytics Endpoints

ENDPOINTS:
- GET /dashboard/overall-progress - Overall student progress
- GET /dashboard/specialty-detail/{specialty} - Specialty breakdown
- GET /dashboard/session-history - Recent session history

PERFORMANCE TARGET: <300ms (p95)
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import Optional

from src.db.base import get_db
from src.db.models import User
from src.auth.dependencies import get_current_user
from .schemas import (
    OverallProgressResponse,
    SpecialtyDetailResponse,
    SessionHistoryResponse,
    SessionHistoryItem,
    PaginationInfo,
    RecommendedPracticeScenario,
)
from .sessions import EMRSession, MockPatient


router = APIRouter()


# ============================================================================
# ENDPOINT 4: OVERALL PROGRESS
# ============================================================================


@router.get("/dashboard/overall-progress", response_model=OverallProgressResponse)
async def get_overall_progress(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get overall EMR progress statistics

    METRICS:
    - Total sessions completed
    - Pass/fail rates
    - Average score
    - Total study time
    - Improvement trend
    - Current streak
    """
    # Query all user sessions (ordered by started_at)
    sessions = (
        db.query(EMRSession)
        .filter(EMRSession.user_id == current_user.id)
        .order_by(EMRSession.started_at)
        .all()
    )

    total_sessions = len(sessions)

    # Count by status
    sessions_in_progress = sum(1 for s in sessions if s.status == "in_progress")
    validated_sessions = [s for s in sessions if s.status == "validated"]

    sessions_passed = sum(
        1
        for s in validated_sessions
        if s.score_breakdown and s.score_breakdown.get("pass_fail") == "PASS"
    )
    sessions_failed = sum(
        1
        for s in validated_sessions
        if s.score_breakdown
        and s.score_breakdown.get("pass_fail") in ["FAIL", "BORDERLINE"]
    )

    # Calculate average score
    scores = [
        s.validation_score for s in validated_sessions if s.validation_score is not None
    ]
    average_score = sum(scores) / len(scores) if scores else 0.0

    # Calculate total time
    total_time_minutes = sum(
        s.elapsed_time_seconds / 60
        for s in validated_sessions
        if s.elapsed_time_seconds is not None
    )

    # Calculate improvement trend (last 10 sessions vs previous 10)
    if len(validated_sessions) >= 10:
        recent_10 = validated_sessions[-10:]
        recent_scores = [
            s.validation_score for s in recent_10 if s.validation_score is not None
        ]
        recent_avg = sum(recent_scores) / len(recent_scores) if recent_scores else 0

        if len(validated_sessions) >= 20:
            previous_10 = validated_sessions[-20:-10]
            previous_scores = [
                s.validation_score for s in previous_10 if s.validation_score is not None
            ]
            previous_avg = (
                sum(previous_scores) / len(previous_scores) if previous_scores else recent_avg
            )
        else:
            previous_avg = recent_avg

        improvement_trend = recent_avg - previous_avg
    else:
        improvement_trend = 0.0

    # Calculate current streak (consecutive passing sessions)
    current_streak = 0
    for session in reversed(validated_sessions):
        if session.score_breakdown and session.score_breakdown.get("pass_fail") == "PASS":
            current_streak += 1
        else:
            break

    # Last session date
    last_session_date = validated_sessions[-1].started_at if validated_sessions else None

    return OverallProgressResponse(
        total_sessions=total_sessions,
        sessions_passed=sessions_passed,
        sessions_failed=sessions_failed,
        sessions_in_progress=sessions_in_progress,
        average_score=round(average_score, 1),
        total_time_minutes=round(total_time_minutes, 1),
        improvement_trend=round(improvement_trend, 1),
        current_streak=current_streak,
        last_session_date=last_session_date,
    )


# ============================================================================
# ENDPOINT 5: SPECIALTY DETAIL
# ============================================================================


@router.get("/dashboard/specialty-detail/{specialty}", response_model=SpecialtyDetailResponse)
async def get_specialty_detail(
    specialty: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get specialty-specific progress breakdown

    ANALYSIS:
    - Sessions attempted/passed in specialty
    - Average score
    - Weak areas identification
    - Strong areas identification
    - Recommended practice scenarios
    """
    # Query specialty-specific sessions
    specialty_sessions = (
        db.query(EMRSession)
        .filter(EMRSession.user_id == current_user.id, EMRSession.specialty == specialty)
        .all()
    )

    sessions_attempted = len(specialty_sessions)

    # Filter validated sessions
    validated_sessions = [s for s in specialty_sessions if s.status == "validated"]

    sessions_passed = sum(
        1
        for s in validated_sessions
        if s.score_breakdown and s.score_breakdown.get("pass_fail") == "PASS"
    )

    # Calculate average score
    scores = [
        s.validation_score for s in validated_sessions if s.validation_score is not None
    ]
    average_score = sum(scores) / len(scores) if scores else 0.0

    # Identify weak areas (placeholder - requires more sophisticated analysis)
    weak_areas = []
    strong_areas = []

    if validated_sessions:
        # Analyze Layer 1 errors across sessions
        all_errors = []
        for session in validated_sessions:
            if session.score_breakdown and session.score_breakdown.get("layer_1_rule_based"):
                errors = session.score_breakdown["layer_1_rule_based"].get("errors", [])
                all_errors.extend(errors)

        # Count error types
        error_counts = {}
        for error in all_errors:
            # Extract error type (simplified)
            if "Subjective" in error:
                error_counts["History Taking"] = error_counts.get("History Taking", 0) + 1
            elif "Objective" in error:
                error_counts["Physical Examination"] = (
                    error_counts.get("Physical Examination", 0) + 1
                )
            elif "Assessment" in error:
                error_counts["Differential Diagnosis"] = (
                    error_counts.get("Differential Diagnosis", 0) + 1
                )
            elif "Plan" in error:
                error_counts["Management Planning"] = (
                    error_counts.get("Management Planning", 0) + 1
                )

        # Top 3 weak areas
        if error_counts:
            sorted_errors = sorted(error_counts.items(), key=lambda x: x[1], reverse=True)
            weak_areas = [error[0] for error in sorted_errors[:3]]

        # Strong areas (inverse of weak areas - placeholder)
        all_areas = [
            "History Taking",
            "Physical Examination",
            "Differential Diagnosis",
            "Management Planning",
        ]
        strong_areas = [area for area in all_areas if area not in weak_areas][:2]

    # Recommended practice scenarios
    recommended_practice = []
    if weak_areas:
        # Find patients in this specialty that the user hasn't practiced
        practiced_patient_ids = [s.patient_id for s in specialty_sessions]

        recommended_patients = (
            db.query(MockPatient)
            .filter(
                MockPatient.specialty == specialty, MockPatient.id.notin_(practiced_patient_ids)
            )
            .limit(3)
            .all()
        )

        for patient in recommended_patients:
            recommended_practice.append(
                RecommendedPracticeScenario(
                    patient_id=patient.id,
                    scenario_name=patient.presenting_complaint,
                    difficulty=patient.difficulty,
                )
            )

    return SpecialtyDetailResponse(
        specialty=specialty,
        sessions_attempted=sessions_attempted,
        sessions_passed=sessions_passed,
        average_score=round(average_score, 1),
        weak_areas=weak_areas,
        strong_areas=strong_areas,
        recommended_practice=recommended_practice,
    )


# ============================================================================
# ENDPOINT 6: SESSION HISTORY
# ============================================================================


@router.get("/dashboard/session-history", response_model=SessionHistoryResponse)
async def get_session_history(
    limit: int = Query(default=20, ge=1, le=100, description="Items per page"),
    offset: int = Query(default=0, ge=0, description="Offset from start"),
    specialty: Optional[str] = Query(None, description="Filter by specialty"),
    pass_fail: Optional[str] = Query(
        None, description="Filter by pass/fail status (PASS, FAIL, BORDERLINE)"
    ),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get session history with pagination and filtering

    FILTERS:
    - Specialty
    - Pass/fail status

    PAGINATION:
    - Limit (max 100)
    - Offset
    """
    # Build query
    query = db.query(EMRSession, MockPatient).join(
        MockPatient, EMRSession.patient_id == MockPatient.id
    ).filter(EMRSession.user_id == current_user.id)

    # Apply filters
    if specialty:
        query = query.filter(EMRSession.specialty == specialty)

    if pass_fail:
        # Filter by pass/fail (requires JSON query)
        query = query.filter(EMRSession.status == "validated")
        # Note: PostgreSQL JSON querying - may need adjustment
        # For simplicity, we'll filter in Python after fetching

    # Count total (before pagination)
    total_count = query.count()

    # Order by submitted_at descending (most recent first)
    query = query.order_by(desc(EMRSession.submitted_at))

    # Apply pagination
    query = query.limit(limit).offset(offset)

    # Execute query
    results = query.all()

    # Build session history items
    sessions = []
    for emr_session, mock_patient in results:
        # Apply pass_fail filter (if specified)
        if pass_fail:
            if (
                not emr_session.score_breakdown
                or emr_session.score_breakdown.get("pass_fail") != pass_fail
            ):
                continue

        # Calculate time taken in minutes
        time_taken_minutes = None
        if emr_session.elapsed_time_seconds:
            time_taken_minutes = round(emr_session.elapsed_time_seconds / 60, 1)

        sessions.append(
            SessionHistoryItem(
                session_id=emr_session.id,
                mock_patient_name=mock_patient.name,
                specialty=emr_session.specialty,
                chief_complaint=mock_patient.presenting_complaint,
                submitted_at=emr_session.submitted_at,
                score=emr_session.validation_score,
                pass_fail=(
                    emr_session.score_breakdown.get("pass_fail")
                    if emr_session.score_breakdown
                    else None
                ),
                time_taken_minutes=time_taken_minutes,
            )
        )

    # Pagination metadata
    has_more = (offset + limit) < total_count

    return SessionHistoryResponse(
        total_count=total_count,
        sessions=sessions,
        pagination=PaginationInfo(limit=limit, offset=offset, has_more=has_more),
    )
