"""
Unit tests for DashboardService

Tests aggregation logic in isolation (no database required).
Extracted from integration tests for better debuggability.

Author: testing-qa-expert
Date: 2026-05-25
"""

import pytest
from datetime import datetime, timedelta
from src.services.dashboard_service import DashboardService
from src.api.v1.dashboard import SpecialtyBreakdown


class TestOverallProgressCalculations:
    """Unit tests for dashboard aggregation logic"""

    def test_calculate_completion_percentage_all_complete(self):
        """Test 17: Completion percentage when all sessions complete"""
        # Arrange
        service = DashboardService()

        # Mock session objects
        class MockSession:
            def __init__(self, status):
                self.status = status

        sessions = [
            MockSession("graded"),
            MockSession("graded"),
            MockSession("graded"),
        ]

        # Act
        result = service.calculate_completion_percentage(sessions)

        # Assert
        assert result == 100.0
        assert isinstance(result, float)

    def test_calculate_completion_percentage_partial(self):
        """Test 18: Completion percentage with mixed status"""
        service = DashboardService()

        class MockSession:
            def __init__(self, status):
                self.status = status

        sessions = [
            MockSession("graded"),
            MockSession("in_progress"),
            MockSession("graded"),
            MockSession("in_progress"),
        ]

        result = service.calculate_completion_percentage(sessions)
        assert result == 50.0  # 2/4 = 50%

    def test_calculate_completion_percentage_none_complete(self):
        """Test 19: Completion percentage when none complete"""
        service = DashboardService()

        class MockSession:
            def __init__(self, status):
                self.status = status

        sessions = [
            MockSession("in_progress"),
            MockSession("in_progress"),
        ]

        result = service.calculate_completion_percentage(sessions)
        assert result == 0.0

    def test_calculate_completion_percentage_empty_list(self):
        """Test 20: Completion percentage with no sessions"""
        service = DashboardService()
        sessions = []

        result = service.calculate_completion_percentage(sessions)
        assert result == 0.0


class TestSpecialtyAggregation:
    """Unit tests for specialty breakdown logic"""

    def test_aggregate_specialty_scores_single_specialty(self):
        """Test 21: Aggregate scores for single specialty"""
        service = DashboardService()
        attempts = [
            {"specialty": "cardiology", "score": 85},
            {"specialty": "cardiology", "score": 90},
            {"specialty": "cardiology", "score": 75},
        ]

        result = service.aggregate_specialty_scores(attempts)

        assert len(result) == 1
        assert result[0].specialty == "cardiology"
        assert result[0].attempts == 3
        assert result[0].avg_score == pytest.approx(83.3, abs=0.1)

    def test_aggregate_specialty_scores_multiple_specialties(self):
        """Test 22: Aggregate scores for multiple specialties"""
        service = DashboardService()
        attempts = [
            {"specialty": "cardiology", "score": 80},
            {"specialty": "respiratory", "score": 90},
            {"specialty": "cardiology", "score": 70},
            {"specialty": "psychiatry", "score": 85},
        ]

        result = service.aggregate_specialty_scores(attempts)

        assert len(result) == 3
        specialties = {r.specialty for r in result}
        assert specialties == {"cardiology", "respiratory", "psychiatry"}

        # Find cardiology stats
        cardio = next(r for r in result if r.specialty == "cardiology")
        assert cardio.attempts == 2
        assert cardio.avg_score == 75.0  # (80 + 70) / 2


class TestRecommendationLogic:
    """Unit tests for recommendation generation"""

    def test_generate_weak_specialty_recommendation(self):
        """Test 23: Generate recommendation for weak specialty"""
        service = DashboardService()
        specialty_breakdown = [
            SpecialtyBreakdown(specialty="cardiology", attempts=10, avg_score=85, strength="good"),
            SpecialtyBreakdown(specialty="respiratory", attempts=10, avg_score=60, strength="weak"),  # 25 points below avg
            SpecialtyBreakdown(specialty="psychiatry", attempts=10, avg_score=80, strength="good"),
        ]
        overall_avg = 75.0

        result = service.generate_weak_specialty_recommendations(
            specialty_breakdown, overall_avg
        )

        assert len(result) == 1
        assert "respiratory" in result[0].lower()
        assert "focus" in result[0].lower() or "improve" in result[0].lower()

    def test_generate_unused_module_recommendation(self):
        """Test 24: Generate recommendation for unused module"""
        service = DashboardService()
        last_activities = {
            "mcq": datetime.now() - timedelta(days=1),
            "osce": datetime.now() - timedelta(days=3),  # 3 days ago
            "emr": datetime.now() - timedelta(hours=5),
            "mock_exam": datetime.now() - timedelta(days=5),  # 5 days ago
        }

        result = service.generate_unused_module_recommendations(
            last_activities, threshold_days=2
        )

        assert len(result) >= 2  # OSCE and Mock Exam
        assert any("osce" in r.lower() for r in result)
        assert any("mock" in r.lower() or "exam" in r.lower() for r in result)
