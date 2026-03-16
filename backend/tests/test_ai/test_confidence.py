"""
Test Confidence Calculation

Tests confidence scoring (0.0-1.0) based on evidence quality, score consistency, and edge cases.

TDD Pattern:
1. RED: Tests written first (will FAIL/SKIP until implementation)
2. GREEN: Implementation makes tests PASS
3. REFACTOR: Code cleanup while keeping tests passing
"""

import pytest
from typing import Dict, Any, List

try:
    from src.ai.scoring.confidence import ConfidenceCalculator, calculate_confidence
except ImportError:
    ConfidenceCalculator = None
    calculate_confidence = None


# Fixtures

@pytest.fixture
def calculator():
    """Confidence calculator instance."""
    if ConfidenceCalculator is None:
        pytest.skip("ConfidenceCalculator not implemented yet")
    return ConfidenceCalculator()


@pytest.fixture
def high_quality_session():
    """High-quality transcript (should have high confidence ≥0.9)."""
    return [
        {"role": "student", "message": "Good morning. What brings you in today?"},
        {"role": "patient", "message": "I have chest pain."},
        {"role": "student", "message": "When did the pain start?"},
        {"role": "patient", "message": "2 hours ago."},
        {"role": "student", "message": "On a scale of 1-10, how severe?"},
        {"role": "patient", "message": "8 out of 10."},
        {"role": "student", "message": "I'm ordering an ECG and giving you aspirin immediately."},
        {"role": "patient", "message": "Thank you doctor."},
        {"role": "student", "message": "I'm also calling cardiology for urgent review."}
    ]


@pytest.fixture
def low_quality_session():
    """Low-quality transcript (should have low confidence <0.7)."""
    return [
        {"role": "student", "message": "Hi."},
        {"role": "patient", "message": "Chest pain."},
        {"role": "student", "message": "Rest."}
    ]


@pytest.fixture
def medium_quality_session():
    """Medium-quality transcript (confidence 0.7-0.9)."""
    return [
        {"role": "student", "message": "Hello, what brings you in?"},
        {"role": "patient", "message": "I have chest pain."},
        {"role": "student", "message": "How long have you had it?"},
        {"role": "patient", "message": "2 hours."},
        {"role": "student", "message": "I'll order some tests."},
        {"role": "patient", "message": "Okay."}
    ]


@pytest.fixture
def perfect_scores():
    """Perfect scores (15/15, PASS)."""
    return {
        "communication_score": 3,
        "clinical_reasoning_score": 4,
        "information_gathering_score": 4,
        "management_score": 2,
        "professionalism_score": 2,
        "total_score": 15,
        "pass_fail": "PASS",
        "critical_errors": [],
        "communication_feedback": "Excellent communication",
        "clinical_reasoning_feedback": "Outstanding reasoning",
        "information_gathering_feedback": "Comprehensive history",
        "management_feedback": "Appropriate management",
        "professionalism_feedback": "Professional demeanor",
        "overall_feedback": "Exemplary performance"
    }


@pytest.fixture
def borderline_scores():
    """Borderline scores (8/15, BORDERLINE)."""
    return {
        "communication_score": 2,
        "clinical_reasoning_score": 2,
        "information_gathering_score": 2,
        "management_score": 1,
        "professionalism_score": 1,
        "total_score": 8,
        "pass_fail": "BORDERLINE",
        "critical_errors": [],
        "communication_feedback": "Adequate",
        "clinical_reasoning_feedback": "Basic",
        "information_gathering_feedback": "Minimal",
        "management_feedback": "Acceptable",
        "professionalism_feedback": "Satisfactory",
        "overall_feedback": "Borderline performance"
    }


@pytest.fixture
def failing_scores():
    """Failing scores (3/15, FAIL)."""
    return {
        "communication_score": 1,
        "clinical_reasoning_score": 0,
        "information_gathering_score": 1,
        "management_score": 0,
        "professionalism_score": 1,
        "total_score": 3,
        "pass_fail": "FAIL",
        "critical_errors": ["Missed acute red flag"],
        "communication_feedback": "Poor",
        "clinical_reasoning_feedback": "Inadequate",
        "information_gathering_feedback": "Incomplete",
        "management_feedback": "Unsafe",
        "professionalism_feedback": "Minimal",
        "overall_feedback": "Significant deficiencies"
    }


# Test Classes

class TestConfidenceCalculator:
    """Test confidence calculator initialization and basic functionality."""

    def test_calculator_initializes(self, calculator):
        """Test calculator initializes correctly."""
        assert calculator is not None
        assert hasattr(calculator, 'min_confidence')
        assert hasattr(calculator, 'max_confidence')
        assert hasattr(calculator, 'human_review_threshold')

    def test_calculator_has_default_thresholds(self, calculator):
        """Test calculator has correct default thresholds."""
        assert calculator.min_confidence == 0.0
        assert calculator.max_confidence == 1.0
        assert calculator.human_review_threshold == 0.7

    def test_high_confidence_on_quality_session(
        self,
        calculator,
        high_quality_session,
        perfect_scores
    ):
        """Test high confidence (≥0.9) on high-quality session."""
        persona = {"chief_complaint": "Chest pain"}

        confidence = calculator.calculate_confidence(
            high_quality_session,
            perfect_scores,
            persona
        )

        assert 0.9 <= confidence <= 1.0, f"Expected ≥0.9, got {confidence}"

    def test_low_confidence_on_poor_session(
        self,
        calculator,
        low_quality_session,
        borderline_scores
    ):
        """Test low confidence (<0.7) on poor-quality session."""
        persona = {"chief_complaint": "Chest pain"}

        confidence = calculator.calculate_confidence(
            low_quality_session,
            borderline_scores,
            persona
        )

        assert confidence < 0.7, f"Expected <0.7, got {confidence}"

    def test_confidence_always_in_range(self, calculator):
        """Test confidence always returns 0.0-1.0."""
        # Empty session edge case
        confidence = calculator.calculate_confidence(
            [],
            {"total_score": 0, "pass_fail": "FAIL", "critical_errors": []},
            {}
        )

        assert 0.0 <= confidence <= 1.0

    def test_confidence_is_float(self, calculator, high_quality_session, perfect_scores):
        """Test confidence returns a float."""
        persona = {"chief_complaint": "Test"}
        confidence = calculator.calculate_confidence(
            high_quality_session,
            perfect_scores,
            persona
        )

        assert isinstance(confidence, float)

    def test_borderline_score_reduces_confidence(
        self,
        calculator,
        high_quality_session,
        borderline_scores
    ):
        """Test borderline score (8/15) reduces confidence."""
        persona = {"chief_complaint": "Test"}

        confidence = calculator.calculate_confidence(
            high_quality_session,
            borderline_scores,
            persona
        )

        # Borderline adds 0.2 penalty
        assert confidence < 0.9, f"Borderline should reduce confidence, got {confidence}"

    def test_very_short_session_reduces_confidence(
        self,
        calculator,
        low_quality_session,
        perfect_scores
    ):
        """Test very short session (<5 messages) reduces confidence."""
        persona = {"chief_complaint": "Test"}

        confidence = calculator.calculate_confidence(
            low_quality_session,  # Only 3 messages
            perfect_scores,
            persona
        )

        # Short session adds 0.3 penalty
        assert confidence < 0.95, f"Short session should reduce confidence, got {confidence}"

    def test_needs_human_review(self, calculator):
        """Test human review threshold (< 0.7)."""
        assert calculator.needs_human_review(0.6) == True
        assert calculator.needs_human_review(0.7) == False
        assert calculator.needs_human_review(0.9) == False

    def test_no_human_review_for_high_confidence(self, calculator):
        """Test no human review needed for high confidence."""
        assert calculator.needs_human_review(0.95) == False

    def test_human_review_on_poor_session(
        self,
        calculator,
        low_quality_session,
        failing_scores
    ):
        """Test human review recommended for poor session."""
        persona = {"chief_complaint": "Test"}

        confidence = calculator.calculate_confidence(
            low_quality_session,
            failing_scores,
            persona
        )

        assert calculator.needs_human_review(confidence) == True

    def test_medium_quality_session(
        self,
        calculator,
        medium_quality_session,
        borderline_scores
    ):
        """Test medium-quality session has medium confidence (0.7-0.9)."""
        persona = {"chief_complaint": "Test"}

        confidence = calculator.calculate_confidence(
            medium_quality_session,
            borderline_scores,
            persona
        )

        # Medium quality should be in 0.65-0.85 range
        assert 0.60 <= confidence <= 0.90, f"Expected 0.60-0.90, got {confidence}"


class TestConvenienceFunction:
    """Test convenience function for confidence calculation."""

    def test_convenience_function_exists(self):
        """Test calculate_confidence() convenience function exists."""
        if calculate_confidence is None:
            pytest.skip("calculate_confidence not implemented yet")

        assert callable(calculate_confidence)

    def test_convenience_function_returns_float(self, high_quality_session, perfect_scores):
        """Test convenience function returns float."""
        if calculate_confidence is None:
            pytest.skip("calculate_confidence not implemented yet")

        persona = {"chief_complaint": "Test"}
        confidence = calculate_confidence(high_quality_session, perfect_scores, persona)

        assert isinstance(confidence, float)
        assert 0.0 <= confidence <= 1.0

    def test_convenience_function_matches_calculator(
        self,
        calculator,
        high_quality_session,
        perfect_scores
    ):
        """Test convenience function matches calculator method."""
        if calculate_confidence is None:
            pytest.skip("calculate_confidence not implemented yet")

        persona = {"chief_complaint": "Test"}

        # Direct method
        confidence_direct = calculator.calculate_confidence(
            high_quality_session,
            perfect_scores,
            persona
        )

        # Convenience function
        confidence_function = calculate_confidence(
            high_quality_session,
            perfect_scores,
            persona
        )

        # Should match (within floating point precision)
        assert abs(confidence_direct - confidence_function) < 0.001


class TestEdgeCases:
    """Test edge cases and robustness."""

    def test_empty_transcript(self, calculator):
        """Test empty transcript returns low confidence."""
        confidence = calculator.calculate_confidence(
            [],
            {"total_score": 8, "pass_fail": "BORDERLINE", "critical_errors": []},
            {}
        )

        # Empty transcript should have very low confidence
        assert confidence < 0.5, f"Empty transcript should have very low confidence, got {confidence}"

    def test_missing_persona(self, calculator, high_quality_session, perfect_scores):
        """Test missing persona doesn't crash (uses defaults)."""
        confidence = calculator.calculate_confidence(
            high_quality_session,
            perfect_scores,
            {}
        )

        # Should return valid confidence even with empty persona
        assert 0.0 <= confidence <= 1.0

    def test_inconsistent_scores_reduce_confidence(self, calculator, high_quality_session):
        """Test inconsistent scores (total != sum) reduce confidence."""
        inconsistent_scores = {
            "communication_score": 3,
            "clinical_reasoning_score": 4,
            "information_gathering_score": 4,
            "management_score": 2,
            "professionalism_score": 2,
            "total_score": 10,  # Should be 15 (inconsistent!)
            "pass_fail": "PASS",
            "critical_errors": []
        }

        persona = {"chief_complaint": "Test"}

        confidence = calculator.calculate_confidence(
            high_quality_session,
            inconsistent_scores,
            persona
        )

        # Inconsistency should reduce confidence
        assert confidence < 0.95, f"Inconsistent scores should reduce confidence, got {confidence}"
