"""
Progress Analytics Service

FEATURES:
- Calculate MCQ accuracy and performance metrics
- Identify weak areas for targeted improvement
- Track study card retention rates
- Generate weekly/monthly progress trends
- Specialty-specific performance breakdown

PRIVACY:
- All queries filtered by user_id
- Never exposes other users' data
- Database-level aggregations for performance

PERFORMANCE:
- Uses efficient JOIN + GROUP BY queries
- Database aggregations (func.count, func.avg, func.sum)
- Avoids N+1 queries
- Response time target: <200ms
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta

from sqlalchemy import func, case, Integer
from sqlalchemy.orm import Session
from sqlalchemy.sql import cast

from src.db.models import (
    MCQ,
    MCQAttempt,
    OSCE,
    OSCEAttempt,
    StudyCard,
    StudyCardReview,
    MedicalSpecialty,
)


class ProgressAnalytics:
    """
    Progress analytics service for user performance tracking.

    METHODS:
    - get_mcq_accuracy: Calculate overall MCQ accuracy
    - get_specialty_breakdown: Performance by specialty
    - get_weak_areas: Specialties below threshold
    - get_study_card_retention: Study Card retention rate
    - get_weekly_trends: Weekly progress trends
    - get_specialty_detail: Detailed performance for one specialty
    """

    @staticmethod
    def get_mcq_accuracy(db: Session, user_id: int) -> float:
        """
        Calculate overall MCQ accuracy for user.

        Args:
            db: Database session
            user_id: User ID (CRITICAL: Must filter by this)

        Returns:
            float: Accuracy percentage (0-100, rounded to 2 decimals)

        Privacy:
            - Filters by user_id (never cross-user data)

        Example:
            >>> accuracy = ProgressAnalytics.get_mcq_accuracy(db, user_id=1)
            >>> print(accuracy)  # 73.68
        """
        total = db.query(MCQAttempt).filter(MCQAttempt.user_id == user_id).count()
        if total == 0:
            return 0.0

        correct = (
            db.query(MCQAttempt)
            .filter(MCQAttempt.user_id == user_id, MCQAttempt.is_correct == True)
            .count()
        )

        return round((correct / total) * 100, 2)

    @staticmethod
    def get_specialty_breakdown(db: Session, user_id: int) -> List[Dict]:
        """
        Get performance breakdown by specialty.

        Uses efficient JOIN + GROUP BY for database-level aggregation.

        Args:
            db: Database session
            user_id: User ID (CRITICAL: Must filter by this)

        Returns:
            List[Dict]: Specialty performance metrics
                - specialty: Specialty name
                - total_attempts: Total MCQ attempts
                - correct_attempts: Number of correct answers
                - accuracy_rate: Success percentage (rounded to 2 decimals)
                - average_time_seconds: Average time per question

        Privacy:
            - Filters by user_id (never cross-user data)

        Performance:
            - Single database query with JOIN + GROUP BY
            - No N+1 queries
            - Database-level aggregation

        Example:
            >>> breakdown = ProgressAnalytics.get_specialty_breakdown(db, user_id=1)
            >>> print(breakdown[0])
            {
                "specialty": "cardiology",
                "total_attempts": 45,
                "correct_attempts": 32,
                "accuracy_rate": 71.11,
                "average_time_seconds": 95
            }
        """
        results = (
            db.query(
                MCQ.specialty,
                func.count(MCQAttempt.id).label("total_attempts"),
                func.sum(cast(MCQAttempt.is_correct, Integer)).label("correct_attempts"),
                func.avg(MCQAttempt.time_taken_seconds).label("avg_time"),
            )
            .join(MCQ, MCQAttempt.mcq_id == MCQ.id)
            .filter(MCQAttempt.user_id == user_id)
            .group_by(MCQ.specialty)
            .all()
        )

        breakdown = []
        for row in results:
            total = row.total_attempts
            correct = row.correct_attempts or 0
            accuracy = (correct / total * 100) if total > 0 else 0.0

            breakdown.append(
                {
                    "specialty": str(row.specialty.value),  # Convert enum to string
                    "total_attempts": total,
                    "correct_attempts": correct,
                    "accuracy_rate": round(accuracy, 2),
                    "average_time_seconds": int(row.avg_time or 0),
                }
            )

        return breakdown

    @staticmethod
    def get_weak_areas(
        db: Session, user_id: int, threshold: float = 70.0, min_attempts: int = 5
    ) -> List[Dict]:
        """
        Identify specialties needing improvement.

        CRITERIA:
        - Accuracy below threshold (default 70%)
        - Minimum attempts >= min_attempts (default 5)

        Args:
            db: Database session
            user_id: User ID (CRITICAL: Must filter by this)
            threshold: Accuracy threshold percentage (default 70.0)
            min_attempts: Minimum attempts required (default 5)

        Returns:
            List[Dict]: Weak specialties
                - specialty: Specialty name
                - accuracy_rate: Success percentage
                - total_attempts: Total attempts
                - recommended_study_cards: Available study cards count

        Privacy:
            - Filters by user_id (never cross-user data)

        Example:
            >>> weak = ProgressAnalytics.get_weak_areas(db, user_id=1, threshold=70.0)
            >>> print(weak[0])
            {
                "specialty": "neurology",
                "accuracy_rate": 58.33,
                "total_attempts": 12,
                "recommended_study_cards": 47
            }
        """
        # Get specialty performance
        results = (
            db.query(
                MCQ.specialty,
                func.count(MCQAttempt.id).label("total_attempts"),
                func.sum(cast(MCQAttempt.is_correct, Integer)).label("correct_attempts"),
            )
            .join(MCQ, MCQAttempt.mcq_id == MCQ.id)
            .filter(MCQAttempt.user_id == user_id)
            .group_by(MCQ.specialty)
            .having(func.count(MCQAttempt.id) >= min_attempts)
            .all()
        )

        weak_areas = []
        for row in results:
            total = row.total_attempts
            correct = row.correct_attempts or 0
            accuracy = (correct / total * 100) if total > 0 else 0.0

            # Only include if below threshold
            if accuracy < threshold:
                # Count available study cards for this specialty
                study_cards_count = (
                    db.query(StudyCard)
                    .filter(StudyCard.specialty == row.specialty, StudyCard.is_active == True)
                    .count()
                )

                weak_areas.append(
                    {
                        "specialty": str(row.specialty.value),
                        "accuracy_rate": round(accuracy, 2),
                        "total_attempts": total,
                        "recommended_study_cards": study_cards_count,
                    }
                )

        # Sort by accuracy (lowest first)
        weak_areas.sort(key=lambda x: x["accuracy_rate"])

        return weak_areas

    @staticmethod
    def get_study_card_retention(db: Session, user_id: int) -> float:
        """
        Calculate study card retention rate.

        CRITERIA:
        - Retention = reviews with quality >= 3 / total reviews * 100

        Args:
            db: Database session
            user_id: User ID (CRITICAL: Must filter by this)

        Returns:
            float: Retention percentage (0-100, rounded to 2 decimals)

        Privacy:
            - Filters by user_id (never cross-user data)

        Example:
            >>> retention = ProgressAnalytics.get_study_card_retention(db, user_id=1)
            >>> print(retention)  # 78.12
        """
        total_reviews = (
            db.query(StudyCardReview).filter(StudyCardReview.user_id == user_id).count()
        )

        if total_reviews == 0:
            return 0.0

        # Count reviews with quality >= 3 (successful retention)
        successful_reviews = (
            db.query(StudyCardReview)
            .filter(StudyCardReview.user_id == user_id, StudyCardReview.quality >= 3)
            .count()
        )

        return round((successful_reviews / total_reviews) * 100, 2)

    @staticmethod
    def get_weekly_trends(db: Session, user_id: int, weeks: int = 4) -> List[Dict]:
        """
        Get weekly progress trends.

        Args:
            db: Database session
            user_id: User ID (CRITICAL: Must filter by this)
            weeks: Number of weeks to retrieve (default 4, max 12)

        Returns:
            List[Dict]: Weekly trend data (most recent first)
                - week_start: Start date of the week (Monday)
                - mcq_attempts: MCQ attempts during this week
                - accuracy_rate: Success percentage for this week
                - study_cards_reviewed: Study cards reviewed during this week

        Privacy:
            - Filters by user_id (never cross-user data)

        Example:
            >>> trends = ProgressAnalytics.get_weekly_trends(db, user_id=1, weeks=4)
            >>> print(trends[0])
            {
                "week_start": datetime(2026, 2, 10),
                "mcq_attempts": 28,
                "accuracy_rate": 75.00,
                "study_cards_reviewed": 15
            }
        """
        # Limit weeks to max 12
        weeks = min(weeks, 12)

        # Calculate date range
        today = datetime.utcnow()
        start_date = today - timedelta(weeks=weeks)

        trends = []

        # Generate data for each week
        for week_offset in range(weeks):
            week_start = start_date + timedelta(weeks=week_offset)
            # Adjust to Monday
            week_start = week_start - timedelta(days=week_start.weekday())
            week_end = week_start + timedelta(days=7)

            # MCQ attempts for this week
            mcq_attempts = (
                db.query(MCQAttempt)
                .filter(
                    MCQAttempt.user_id == user_id,
                    MCQAttempt.attempted_at >= week_start,
                    MCQAttempt.attempted_at < week_end,
                )
                .count()
            )

            # MCQ accuracy for this week
            correct_attempts = (
                db.query(MCQAttempt)
                .filter(
                    MCQAttempt.user_id == user_id,
                    MCQAttempt.attempted_at >= week_start,
                    MCQAttempt.attempted_at < week_end,
                    MCQAttempt.is_correct == True,
                )
                .count()
            )

            accuracy_rate = (
                round((correct_attempts / mcq_attempts) * 100, 2) if mcq_attempts > 0 else 0.0
            )

            # Study cards reviewed this week
            study_cards_reviewed = (
                db.query(StudyCardReview)
                .filter(
                    StudyCardReview.user_id == user_id,
                    StudyCardReview.reviewed_at >= week_start,
                    StudyCardReview.reviewed_at < week_end,
                )
                .count()
            )

            trends.append(
                {
                    "week_start": week_start,
                    "mcq_attempts": mcq_attempts,
                    "accuracy_rate": accuracy_rate,
                    "study_cards_reviewed": study_cards_reviewed,
                }
            )

        # Return most recent first
        trends.reverse()

        return trends

    @staticmethod
    def get_specialty_detail(
        db: Session, user_id: int, specialty: MedicalSpecialty
    ) -> Optional[Dict]:
        """
        Get detailed performance for one specialty.

        Args:
            db: Database session
            user_id: User ID (CRITICAL: Must filter by this)
            specialty: Medical specialty

        Returns:
            Optional[Dict]: Specialty detail or None if no attempts
                - specialty: Specialty name
                - total_attempts: Total MCQ attempts
                - correct_attempts: Number of correct answers
                - accuracy_rate: Success percentage
                - average_time_seconds: Average time per question
                - osce_completions: OSCE stations practiced
                - study_cards_available: Available study cards count
                - recent_attempts: Attempts in last 7 days

        Privacy:
            - Filters by user_id (never cross-user data)

        Example:
            >>> detail = ProgressAnalytics.get_specialty_detail(
            ...     db, user_id=1, specialty=MedicalSpecialty.CARDIOLOGY
            ... )
            >>> print(detail)
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
        # MCQ statistics
        result = (
            db.query(
                func.count(MCQAttempt.id).label("total_attempts"),
                func.sum(cast(MCQAttempt.is_correct, Integer)).label("correct_attempts"),
                func.avg(MCQAttempt.time_taken_seconds).label("avg_time"),
            )
            .join(MCQ, MCQAttempt.mcq_id == MCQ.id)
            .filter(MCQAttempt.user_id == user_id, MCQ.specialty == specialty)
            .first()
        )

        if not result or result.total_attempts == 0:
            return None

        total = result.total_attempts
        correct = result.correct_attempts or 0
        accuracy = (correct / total * 100) if total > 0 else 0.0

        # OSCE completions
        osce_completions = (
            db.query(OSCEAttempt)
            .join(OSCE, OSCEAttempt.osce_id == OSCE.id)
            .filter(OSCEAttempt.user_id == user_id, OSCE.specialty == specialty)
            .count()
        )

        # Available study cards
        study_cards_available = (
            db.query(StudyCard)
            .filter(StudyCard.specialty == specialty, StudyCard.is_active == True)
            .count()
        )

        # Recent attempts (last 7 days)
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        recent_attempts = (
            db.query(MCQAttempt)
            .join(MCQ, MCQAttempt.mcq_id == MCQ.id)
            .filter(
                MCQAttempt.user_id == user_id,
                MCQ.specialty == specialty,
                MCQAttempt.attempted_at >= seven_days_ago,
            )
            .count()
        )

        return {
            "specialty": str(specialty.value),
            "total_attempts": total,
            "correct_attempts": correct,
            "accuracy_rate": round(accuracy, 2),
            "average_time_seconds": int(result.avg_time or 0),
            "osce_completions": osce_completions,
            "study_cards_available": study_cards_available,
            "recent_attempts": recent_attempts,
        }
