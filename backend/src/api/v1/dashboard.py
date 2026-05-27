"""
Unified Dashboard API
Aggregates data from MCQ, OSCE, EMR, and Mock Exam modules

SECURITY:
- JWT authentication required
- User can only access their own data
- No PHI exposed in responses

PERFORMANCE:
- Target: <200ms response time
- Uses optimized database queries
- Caches specialty breakdowns
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

from src.db.base import get_db
from src.db.models import User
from src.auth.dependencies import get_current_active_user


# ============================================================================
# RESPONSE MODELS
# ============================================================================


class OverallProgress(BaseModel):
    """Overall progress across all modules"""
    total_sessions: int
    completion_percentage: float
    avg_score: float
    total_time_minutes: int
    last_activity: str


class MCQStats(BaseModel):
    """MCQ module statistics"""
    attempts: int = 0
    correct: int = 0
    total_questions: int = 0
    avg_score: float = 0.0
    last_activity: Optional[str] = None
    time_spent_minutes: int = 0


class OSCEStats(BaseModel):
    """OSCE module statistics"""
    attempts: int = 0
    completed: int = 0
    avg_score: float = 0.0
    last_activity: Optional[str] = None
    time_spent_minutes: int = 0


class EMRStats(BaseModel):
    """EMR module statistics"""
    sessions: int = 0
    completed: int = 0
    avg_soap_score: float = 0.0
    last_activity: Optional[str] = None
    time_spent_minutes: int = 0


class MockExamStats(BaseModel):
    """Mock Exam module statistics"""
    exams_taken: int = 0
    exams_completed: int = 0
    avg_score: float = 0.0
    stations_completed: int = 0
    last_activity: Optional[str] = None
    time_spent_minutes: int = 0


class ModulesBreakdown(BaseModel):
    """Breakdown of all modules"""
    mcq: MCQStats
    osce: OSCEStats
    emr: EMRStats
    mock_exam: MockExamStats


class SpecialtyBreakdown(BaseModel):
    """Performance breakdown by specialty"""
    specialty: str
    attempts: int
    avg_score: float
    strength: str  # "weak" | "average" | "good" | "excellent"


class RecentActivity(BaseModel):
    """Recent activity item"""
    type: str  # "mcq" | "osce" | "emr" | "mock_exam"
    description: str
    score: float
    timestamp: str


class Recommendation(BaseModel):
    """Study recommendation"""
    module: str
    specialty: str
    reason: str
    priority: str  # "high" | "medium" | "low"


class DashboardOverview(BaseModel):
    """Complete dashboard overview"""
    overall_progress: OverallProgress
    modules: ModulesBreakdown
    specialty_breakdown: List[SpecialtyBreakdown]
    recent_activity: List[RecentActivity]
    recommendations: List[Recommendation]


# ============================================================================
# ROUTER
# ============================================================================

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/overview", response_model=DashboardOverview)
async def get_dashboard_overview(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get unified dashboard overview for current user.

    Aggregates data from:
    - MCQ attempts
    - OSCE attempts (individual practice)
    - EMR sessions
    - Mock exam attempts

    SECURITY:
    - User can only view their own data
    - No PHI exposed

    PERFORMANCE:
    - Optimized queries with indexes
    - Target: <200ms response time

    Returns:
        DashboardOverview: Complete dashboard data
    """
    # Get stats from each module
    mcq_stats = get_mcq_stats(db, current_user.id)
    osce_stats = get_osce_stats(db, current_user.id)
    emr_stats = get_emr_stats(db, current_user.id)
    mock_exam_stats = get_mock_exam_stats(db, current_user.id)

    # Calculate overall progress
    overall = calculate_overall_progress(mcq_stats, osce_stats, emr_stats, mock_exam_stats)

    # Get specialty breakdown
    specialty_breakdown = get_specialty_breakdown(db, current_user.id)

    # Get recent activity
    recent_activity = get_recent_activity(db, current_user.id)

    # Generate recommendations
    recommendations = generate_recommendations(specialty_breakdown, mcq_stats, osce_stats, emr_stats)

    return DashboardOverview(
        overall_progress=overall,
        modules=ModulesBreakdown(
            mcq=mcq_stats,
            osce=osce_stats,
            emr=emr_stats,
            mock_exam=mock_exam_stats
        ),
        specialty_breakdown=specialty_breakdown,
        recent_activity=recent_activity,
        recommendations=recommendations
    )


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def get_mcq_stats(db: Session, user_id: int) -> MCQStats:
    """
    Get MCQ module statistics.

    Args:
        db: Database session
        user_id: Current user ID

    Returns:
        MCQStats: MCQ statistics
    """
    from src.db.models import MCQAttempt

    attempts = db.query(MCQAttempt).filter(MCQAttempt.user_id == user_id).all()

    if not attempts:
        return MCQStats()

    total_attempts = len(attempts)
    correct_count = sum(1 for a in attempts if a.is_correct)
    avg_score = (correct_count / total_attempts * 100) if total_attempts > 0 else 0.0
    last_activity = max(a.attempted_at for a in attempts).isoformat() if attempts else None

    # Sum actual time taken
    time_spent = sum(a.time_taken_seconds for a in attempts) // 60  # Convert to minutes

    return MCQStats(
        attempts=total_attempts,
        correct=correct_count,
        total_questions=total_attempts,
        avg_score=round(avg_score, 1),
        last_activity=last_activity,
        time_spent_minutes=time_spent
    )


def get_osce_stats(db: Session, user_id: int) -> OSCEStats:
    """
    Get OSCE module statistics.

    Args:
        db: Database session
        user_id: Current user ID

    Returns:
        OSCEStats: OSCE statistics
    """
    from src.db.models import OSCEAttempt

    attempts = db.query(OSCEAttempt).filter(OSCEAttempt.user_id == user_id).all()

    if not attempts:
        return OSCEStats()

    total_attempts = len(attempts)

    # Calculate average score (convert to percentage: score/15 * 100)
    avg_score = sum(a.total_score for a in attempts) / total_attempts if total_attempts > 0 else 0.0
    avg_score_percentage = (avg_score / 15) * 100

    # Count completed (passed) attempts
    completed = sum(1 for a in attempts if a.passed)

    last_activity = max(a.attempted_at for a in attempts).isoformat() if attempts else None

    # Estimate time (8 min per OSCE station)
    time_spent = total_attempts * 8

    return OSCEStats(
        attempts=total_attempts,
        completed=completed,
        avg_score=round(avg_score_percentage, 1),
        last_activity=last_activity,
        time_spent_minutes=time_spent
    )


def get_emr_stats(db: Session, user_id: int) -> EMRStats:
    """
    Get EMR module statistics.

    Args:
        db: Database session
        user_id: Current user ID

    Returns:
        EMRStats: EMR statistics
    """
    from src.db.models import EMRSession

    sessions = db.query(EMRSession).filter(EMRSession.user_id == user_id).all()

    if not sessions:
        return EMRStats()

    total_sessions = len(sessions)
    completed = sum(1 for s in sessions if s.status == "graded")

    # Calculate average score from validation_score field
    scored_sessions = [s for s in sessions if s.validation_score is not None]
    avg_score = sum(s.validation_score for s in scored_sessions) / len(scored_sessions) if scored_sessions else 0.0

    last_activity = max(s.started_at for s in sessions).isoformat() if sessions else None

    # Sum elapsed time
    time_spent = sum(s.elapsed_time_seconds for s in sessions if s.elapsed_time_seconds) // 60  # Convert to minutes

    return EMRStats(
        sessions=total_sessions,
        completed=completed,
        avg_soap_score=round(avg_score, 1),
        last_activity=last_activity,
        time_spent_minutes=time_spent
    )


def get_mock_exam_stats(db: Session, user_id: int) -> MockExamStats:
    """
    Get Mock Exam module statistics.

    Args:
        db: Database session
        user_id: Current user ID

    Returns:
        MockExamStats: Mock exam statistics
    """
    from src.db.models import MockExam

    # MockExam.user_id is stored as string
    exams = db.query(MockExam).filter(MockExam.user_id == str(user_id)).all()

    if not exams:
        return MockExamStats()

    total_exams = len(exams)
    completed = sum(1 for e in exams if e.exam_state == "COMPLETE")

    # Calculate average score (convert to percentage: total_score/240 * 100)
    completed_exams = [e for e in exams if e.total_score is not None and e.exam_state == "COMPLETE"]
    avg_score = sum(e.total_score for e in completed_exams) / len(completed_exams) if completed_exams else 0.0
    avg_score_percentage = (avg_score / 240) * 100 if avg_score > 0 else 0.0

    # Count total stations completed
    stations_completed = sum(e.current_station_number - 1 for e in exams)

    last_activity = max(e.started_at for e in exams).isoformat() if exams else None

    # Sum actual duration
    time_spent = sum(e.total_duration_minutes for e in exams if e.total_duration_minutes) or 0

    return MockExamStats(
        exams_taken=total_exams,
        exams_completed=completed,
        avg_score=round(avg_score_percentage, 1),
        stations_completed=stations_completed,
        last_activity=last_activity,
        time_spent_minutes=time_spent
    )


def calculate_overall_progress(
    mcq: MCQStats, osce: OSCEStats, emr: EMRStats, mock_exam: MockExamStats
) -> OverallProgress:
    """
    Calculate overall progress across all modules.

    Args:
        mcq: MCQ statistics
        osce: OSCE statistics
        emr: EMR statistics
        mock_exam: Mock exam statistics

    Returns:
        OverallProgress: Overall progress metrics
    """
    total_sessions = mcq.attempts + osce.attempts + emr.sessions + mock_exam.exams_taken

    # Calculate weighted average score
    scores = []
    if mcq.attempts > 0:
        scores.append(mcq.avg_score)
    if osce.attempts > 0:
        scores.append(osce.avg_score)
    if emr.sessions > 0:
        scores.append(emr.avg_soap_score)
    if mock_exam.exams_taken > 0:
        scores.append(mock_exam.avg_score)

    avg_score = sum(scores) / len(scores) if scores else 0.0

    # Estimate completion percentage (arbitrary targets: 100 MCQs, 30 OSCEs, 20 EMR, 3 mock exams)
    completion = (
        min(mcq.attempts / 100 * 100, 100) * 0.3 +
        min(osce.attempts / 30 * 100, 100) * 0.3 +
        min(emr.sessions / 20 * 100, 100) * 0.2 +
        min(mock_exam.exams_completed / 3 * 100, 100) * 0.2
    )

    # Find most recent activity
    activities = [
        mcq.last_activity,
        osce.last_activity,
        emr.last_activity,
        mock_exam.last_activity
    ]
    last_activity = max(a for a in activities if a) if any(activities) else datetime.utcnow().isoformat()

    total_time = mcq.time_spent_minutes + osce.time_spent_minutes + emr.time_spent_minutes + mock_exam.time_spent_minutes

    return OverallProgress(
        total_sessions=total_sessions,
        completion_percentage=round(completion, 1),
        avg_score=round(avg_score, 1),
        total_time_minutes=total_time,
        last_activity=last_activity
    )


def get_specialty_breakdown(db: Session, user_id: int) -> List[SpecialtyBreakdown]:
    """
    Get performance breakdown by specialty.

    Args:
        db: Database session
        user_id: Current user ID

    Returns:
        List[SpecialtyBreakdown]: Specialty performance data
    """
    from src.db.models import EMRSession, OSCEAttempt, MCQ, MCQAttempt

    specialty_data = {}

    # Aggregate from EMR sessions
    emr_sessions = db.query(EMRSession).filter(EMRSession.user_id == user_id).all()
    for session in emr_sessions:
        if session.specialty:
            if session.specialty not in specialty_data:
                specialty_data[session.specialty] = {"attempts": 0, "scores": []}
            specialty_data[session.specialty]["attempts"] += 1
            if session.validation_score:
                specialty_data[session.specialty]["scores"].append(session.validation_score)

    # Aggregate from OSCE attempts
    osce_attempts = db.query(OSCEAttempt).filter(OSCEAttempt.user_id == user_id).all()
    for attempt in osce_attempts:
        # Get specialty from OSCE relationship
        if attempt.osce and attempt.osce.specialty:
            specialty = attempt.osce.specialty
            if specialty not in specialty_data:
                specialty_data[specialty] = {"attempts": 0, "scores": []}
            specialty_data[specialty]["attempts"] += 1
            # Convert score to percentage
            score_percentage = (attempt.total_score / 15) * 100
            specialty_data[specialty]["scores"].append(score_percentage)

    # Aggregate from MCQ attempts
    mcq_attempts = db.query(MCQAttempt).join(MCQ).filter(MCQAttempt.user_id == user_id).all()
    for attempt in mcq_attempts:
        if attempt.mcq and attempt.mcq.specialty:
            specialty = attempt.mcq.specialty
            if specialty not in specialty_data:
                specialty_data[specialty] = {"attempts": 0, "scores": []}
            specialty_data[specialty]["attempts"] += 1
            # Convert correct/incorrect to percentage
            score = 100.0 if attempt.is_correct else 0.0
            specialty_data[specialty]["scores"].append(score)

    # Convert to list
    breakdown = []
    for specialty, data in specialty_data.items():
        avg_score = sum(data["scores"]) / len(data["scores"]) if data["scores"] else 0.0

        # Classify strength
        if avg_score >= 80:
            strength = "excellent"
        elif avg_score >= 70:
            strength = "good"
        elif avg_score >= 60:
            strength = "average"
        else:
            strength = "weak"

        breakdown.append(SpecialtyBreakdown(
            specialty=specialty,
            attempts=data["attempts"],
            avg_score=round(avg_score, 1),
            strength=strength
        ))

    # Sort by attempts (most practiced first)
    breakdown.sort(key=lambda x: x.attempts, reverse=True)

    return breakdown[:10]  # Top 10 specialties


def get_recent_activity(db: Session, user_id: int, limit: int = 10) -> List[RecentActivity]:
    """
    Get recent activity across all modules.

    Args:
        db: Database session
        user_id: Current user ID
        limit: Maximum number of activities to return

    Returns:
        List[RecentActivity]: Recent activities
    """
    from src.db.models import MCQAttempt, EMRSession, OSCEAttempt, MockExam

    activities = []

    # Get recent MCQ attempts
    mcq_attempts = db.query(MCQAttempt).filter(
        MCQAttempt.user_id == user_id
    ).order_by(desc(MCQAttempt.attempted_at)).limit(5).all()

    for attempt in mcq_attempts:
        activities.append(RecentActivity(
            type="mcq",
            description=f"Answered MCQ question",
            score=100.0 if attempt.is_correct else 0.0,
            timestamp=attempt.attempted_at.isoformat()
        ))

    # Get recent EMR sessions
    emr_sessions = db.query(EMRSession).filter(
        EMRSession.user_id == user_id
    ).order_by(desc(EMRSession.started_at)).limit(5).all()

    for session in emr_sessions:
        specialty_name = session.specialty or "General"
        activities.append(RecentActivity(
            type="emr",
            description=f"SOAP note - {specialty_name} patient",
            score=session.validation_score or 0.0,
            timestamp=session.started_at.isoformat()
        ))

    # Get recent OSCE attempts
    osce_attempts = db.query(OSCEAttempt).filter(
        OSCEAttempt.user_id == user_id
    ).order_by(desc(OSCEAttempt.attempted_at)).limit(5).all()

    for attempt in osce_attempts:
        score_percentage = (attempt.total_score / 15) * 100
        station_type = attempt.osce.station_type if attempt.osce else "practice"
        activities.append(RecentActivity(
            type="osce",
            description=f"Practiced {station_type} station",
            score=score_percentage,
            timestamp=attempt.attempted_at.isoformat()
        ))

    # Get recent mock exams
    mock_exams = db.query(MockExam).filter(
        MockExam.user_id == str(user_id)
    ).order_by(desc(MockExam.started_at)).limit(3).all()

    for exam in mock_exams:
        if exam.total_score is not None:
            score_percentage = (exam.total_score / 240) * 100
        else:
            score_percentage = 0.0

        activities.append(RecentActivity(
            type="mock_exam",
            description=f"Mock exam - Station {exam.current_station_number}/16",
            score=score_percentage,
            timestamp=exam.started_at.isoformat()
        ))

    # Sort by timestamp (most recent first)
    activities.sort(key=lambda x: x.timestamp, reverse=True)

    return activities[:limit]


def generate_recommendations(
    specialty_breakdown: List[SpecialtyBreakdown],
    mcq: MCQStats,
    osce: OSCEStats,
    emr: EMRStats
) -> List[Recommendation]:
    """
    Generate personalized study recommendations.

    Args:
        specialty_breakdown: Specialty performance data
        mcq: MCQ statistics
        osce: OSCE statistics
        emr: EMR statistics

    Returns:
        List[Recommendation]: Study recommendations
    """
    recommendations = []

    # Find weak specialties
    weak_specialties = [s for s in specialty_breakdown if s.strength == "weak"]
    for specialty in weak_specialties[:2]:  # Top 2 weak areas
        recommendations.append(Recommendation(
            module="all",
            specialty=specialty.specialty,
            reason=f"Low performance ({specialty.avg_score:.1f}%) - Practice recommended",
            priority="high"
        ))

    # Check if any module is underutilized
    if mcq.attempts < 50:
        recommendations.append(Recommendation(
            module="mcq",
            specialty="all",
            reason=f"Only {mcq.attempts} MCQ attempts - Increase practice volume",
            priority="medium"
        ))

    if emr.sessions < 10:
        recommendations.append(Recommendation(
            module="emr",
            specialty="all",
            reason=f"Only {emr.sessions} EMR sessions - Practice clinical documentation",
            priority="medium"
        ))

    if osce.attempts < 15:
        recommendations.append(Recommendation(
            module="osce",
            specialty="all",
            reason=f"Only {osce.attempts} OSCE attempts - Practice clinical skills",
            priority="medium"
        ))

    # Find average specialties that could be improved
    average_specialties = [s for s in specialty_breakdown if s.strength == "average"]
    for specialty in average_specialties[:1]:  # Top 1 average area
        recommendations.append(Recommendation(
            module="all",
            specialty=specialty.specialty,
            reason=f"Average performance ({specialty.avg_score:.1f}%) - Room for improvement",
            priority="low"
        ))

    return recommendations[:5]  # Top 5 recommendations
