"""
Dashboard Service Layer

Provides business logic for dashboard metrics aggregation.
Extracted from src/api/v1/dashboard.py for better testability and reusability.

Author: testing-qa-expert
Date: 2026-05-25
"""

from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from src.api.v1.dashboard import SpecialtyBreakdown


class DashboardService:
    """
    Service for aggregating dashboard metrics across all modules.

    Provides methods for:
    - Completion percentage calculation
    - Specialty score aggregation
    - Weak specialty recommendations
    - Unused module recommendations
    """

    def calculate_completion_percentage(self, sessions: List[Any]) -> float:
        """
        Calculate percentage of completed sessions.

        Args:
            sessions: List of session objects with 'status' attribute

        Returns:
            Float percentage (0.0 to 100.0)

        Example:
            >>> sessions = [MockSession("graded"), MockSession("in_progress")]
            >>> service.calculate_completion_percentage(sessions)
            50.0
        """
        if not sessions:
            return 0.0

        # Count completed sessions
        # Completed = status in ("graded", "COMPLETE", "completed")
        completed = sum(
            1 for s in sessions
            if hasattr(s, 'status') and s.status in ("graded", "COMPLETE", "completed")
        )

        return (completed / len(sessions)) * 100.0

    def aggregate_specialty_scores(
        self, attempts: List[Dict[str, Any]]
    ) -> List[SpecialtyBreakdown]:
        """
        Aggregate scores by medical specialty.

        Args:
            attempts: List of dicts with 'specialty' and 'score' keys

        Returns:
            List of SpecialtyBreakdown sorted by attempts (descending)

        Example:
            >>> attempts = [
            ...     {"specialty": "cardiology", "score": 85},
            ...     {"specialty": "cardiology", "score": 90},
            ... ]
            >>> breakdown = service.aggregate_specialty_scores(attempts)
            >>> print(breakdown[0].avg_score)
            87.5
        """
        if not attempts:
            return []

        # Group by specialty
        specialty_map: Dict[str, List[float]] = {}
        for attempt in attempts:
            specialty = attempt.get("specialty")
            score = attempt.get("score")

            if specialty and score is not None:
                if specialty not in specialty_map:
                    specialty_map[specialty] = []
                specialty_map[specialty].append(score)

        # Calculate averages and classify strength
        result = []
        for specialty, scores in specialty_map.items():
            avg_score = round(sum(scores) / len(scores), 1)
            
            # Classify strength
            if avg_score >= 80:
                strength = "excellent"
            elif avg_score >= 70:
                strength = "good"
            elif avg_score >= 60:
                strength = "average"
            else:
                strength = "weak"
            
            result.append(SpecialtyBreakdown(
                specialty=specialty,
                attempts=len(scores),
                avg_score=avg_score,
                strength=strength
            ))

        # Sort by attempts (most active first)
        result.sort(key=lambda x: x.attempts, reverse=True)

        return result

    def generate_weak_specialty_recommendations(
        self,
        specialty_breakdown: List[SpecialtyBreakdown],
        overall_avg: float,
        threshold_pct: float = 15.0
    ) -> List[str]:
        """
        Recommend focus on specialties performing below average.

        Args:
            specialty_breakdown: Specialty performance data
            overall_avg: Overall average score
            threshold_pct: Percentage below average to trigger (default 15%)

        Returns:
            List of recommendation strings

        Example:
            >>> breakdown = [
            ...     SpecialtyBreakdown(specialty="psychiatry", avg_score=60, ...),
            ... ]
            >>> recs = service.generate_weak_specialty_recommendations(breakdown, 75.0)
            >>> print(recs[0])
            "Focus on psychiatry - 15 points below average"
        """
        recommendations = []

        for specialty in specialty_breakdown:
            difference = overall_avg - specialty.avg_score

            if difference >= threshold_pct:
                recommendations.append(
                    f"Focus on {specialty.specialty} - "
                    f"{int(difference)} points below average"
                )

        return recommendations

    def generate_unused_module_recommendations(
        self,
        last_activities: Dict[str, Optional[datetime]],
        threshold_days: int = 2
    ) -> List[str]:
        """
        Recommend modules that haven't been used recently.

        Args:
            last_activities: Dict mapping module names to last activity timestamps
            threshold_days: Days of inactivity to trigger recommendation

        Returns:
            List of recommendation strings

        Example:
            >>> last_activities = {
            ...     "mcq": datetime.now() - timedelta(days=1),
            ...     "osce": datetime.now() - timedelta(days=5),
            ... }
            >>> recs = service.generate_unused_module_recommendations(last_activities, 2)
            >>> print(recs[0])
            "Try OSCE mode - unused for 5 days"
        """
        recommendations = []
        now = datetime.now()

        module_labels = {
            "mcq": "MCQ",
            "osce": "OSCE",
            "emr": "EMR",
            "mock_exam": "Mock Exam"
        }

        for module_name, last_activity in last_activities.items():
            if last_activity is None:
                # Module never used
                label = module_labels.get(module_name, module_name)
                recommendations.append(f"Try {label} mode - not yet attempted")
            else:
                days_inactive = (now - last_activity).days

                if days_inactive >= threshold_days:
                    label = module_labels.get(module_name, module_name)
                    recommendations.append(
                        f"Try {label} mode - unused for {days_inactive} days"
                    )

        return recommendations
