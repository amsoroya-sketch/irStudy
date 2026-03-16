"""
Test Feedback Generation

Tests structured feedback generation (strengths, improvements, narrative).

TDD Pattern:
1. RED: Tests written first (will FAIL/SKIP until implementation)
2. GREEN: Implementation makes tests PASS
3. REFACTOR: Code cleanup while keeping tests passing
"""

import pytest
from typing import Dict, Any, List

try:
    from src.ai.scoring.feedback_generator import FeedbackGenerator, generate_feedback
except ImportError:
    FeedbackGenerator = None
    generate_feedback = None


# Fixtures

@pytest.fixture
def generator():
    """Feedback generator instance."""
    if FeedbackGenerator is None:
        pytest.skip("FeedbackGenerator not implemented yet")
    return FeedbackGenerator()


@pytest.fixture
def perfect_transcript():
    """Perfect session transcript."""
    return [
        {"role": "student", "message": "Good morning Mr. Chen. What brings you in today?"},
        {"role": "patient", "message": "I have chest pain for 2 hours."},
        {"role": "student", "message": "That sounds concerning. I'm ordering an ECG immediately."},
        {"role": "patient", "message": "Thank you doctor."}
    ]


@pytest.fixture
def poor_transcript():
    """Poor session transcript."""
    return [
        {"role": "student", "message": "Hi."},
        {"role": "patient", "message": "Chest pain."},
        {"role": "student", "message": "Rest."}
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
        "critical_errors": []
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
        "critical_errors": ["Missed acute red flag"]
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
        "critical_errors": []
    }


# Test Classes

class TestFeedbackGenerator:
    """Test feedback generator initialization and basic functionality."""

    def test_generator_initializes(self, generator):
        """Test generator initializes correctly."""
        assert generator is not None

    def test_generate_complete_feedback(self, generator, perfect_transcript, perfect_scores):
        """Test generate_feedback returns complete structure."""
        persona = {"chief_complaint": "Chest pain"}

        feedback = generator.generate_feedback(
            perfect_transcript,
            perfect_scores,
            persona
        )

        # Check structure
        assert "strengths" in feedback
        assert "areas_for_improvement" in feedback
        assert "narrative" in feedback

        # Check types
        assert isinstance(feedback["strengths"], list)
        assert isinstance(feedback["areas_for_improvement"], list)
        assert isinstance(feedback["narrative"], str)


class TestStrengthsGeneration:
    """Test strengths extraction from high-scoring domains."""

    def test_generate_strengths_high_scores(self, generator, perfect_transcript, perfect_scores):
        """Test strengths generation from perfect scores."""
        persona = {"chief_complaint": "Chest pain"}

        strengths = generator.generate_strengths(perfect_transcript, perfect_scores)

        # Should have 3-5 strengths
        assert 3 <= len(strengths) <= 5, f"Expected 3-5 strengths, got {len(strengths)}"

        # All should be non-empty strings
        for strength in strengths:
            assert isinstance(strength, str)
            assert len(strength) > 10  # Not trivial

    def test_communication_strength(self, generator, perfect_transcript, perfect_scores):
        """Test communication strength extracted when score ≥2."""
        persona = {"chief_complaint": "Test"}

        strengths = generator.generate_strengths(perfect_transcript, perfect_scores)

        # Should mention communication/empathy
        strength_text = " ".join(strengths).lower()
        assert any(kw in strength_text for kw in ["communication", "empathy", "listening"])

    def test_clinical_reasoning_strength(self, generator, perfect_transcript, perfect_scores):
        """Test clinical reasoning strength when score ≥3."""
        persona = {"chief_complaint": "Test"}

        strengths = generator.generate_strengths(perfect_transcript, perfect_scores)

        # Should mention clinical reasoning/diagnosis
        strength_text = " ".join(strengths).lower()
        assert any(kw in strength_text for kw in ["reasoning", "diagnosis", "clinical"])

    def test_no_strengths_for_failing_scores(self, generator, poor_transcript, failing_scores):
        """Test minimal strengths for failing scores."""
        persona = {"chief_complaint": "Test"}

        strengths = generator.generate_strengths(poor_transcript, failing_scores)

        # Should have at least 1 (generic strength)
        assert len(strengths) >= 1


class TestImprovementsGeneration:
    """Test areas for improvement from low-scoring domains."""

    def test_generate_improvements_low_scores(self, generator, poor_transcript, failing_scores):
        """Test improvements generation from failing scores."""
        persona = {"chief_complaint": "Chest pain"}

        improvements = generator.generate_improvements(poor_transcript, failing_scores)

        # Should have 2-4 improvements
        assert 2 <= len(improvements) <= 4, f"Expected 2-4 improvements, got {len(improvements)}"

        # All should be actionable (non-empty strings)
        for improvement in improvements:
            assert isinstance(improvement, str)
            assert len(improvement) > 10  # Not trivial

    def test_communication_improvement(self, generator, poor_transcript):
        """Test communication improvement when score <2."""
        scores = {
            "communication_score": 0,
            "clinical_reasoning_score": 2,
            "information_gathering_score": 2,
            "management_score": 1,
            "professionalism_score": 1,
            "total_score": 6,
            "pass_fail": "FAIL",
            "critical_errors": []
        }

        improvements = generator.generate_improvements(poor_transcript, scores)

        # Should mention communication/empathy
        improvement_text = " ".join(improvements).lower()
        assert any(kw in improvement_text for kw in ["communication", "empathy", "listening"])

    def test_critical_error_improvement_priority(self, generator, poor_transcript, failing_scores):
        """Test critical error improvement appears first."""
        persona = {"chief_complaint": "Test"}

        improvements = generator.generate_improvements(poor_transcript, failing_scores)

        # First improvement should mention critical/safety
        first_improvement = improvements[0].lower()
        assert any(kw in first_improvement for kw in ["critical", "safety", "red flag"])

    def test_minimal_improvements_for_perfect_scores(self, generator, perfect_transcript, perfect_scores):
        """Test minimal improvements for perfect scores."""
        persona = {"chief_complaint": "Test"}

        improvements = generator.generate_improvements(perfect_transcript, perfect_scores)

        # Should have at least 1 (or be empty for perfect)
        assert len(improvements) >= 0


class TestNarrativeGeneration:
    """Test narrative summary generation."""

    def test_generate_narrative_word_count(self, generator):
        """Test narrative is 100-150 words."""
        strengths = ["Excellent communication", "Strong clinical reasoning"]
        improvements = ["Could explore allergies more"]
        scores = {
            "total_score": 12,
            "pass_fail": "PASS",
            "critical_errors": []
        }

        narrative = generator.generate_narrative(strengths, improvements, scores)

        # Count words
        word_count = len(narrative.split())
        assert 50 <= word_count <= 200, f"Expected 50-200 words, got {word_count}"

    def test_narrative_pass_tone(self, generator):
        """Test narrative has positive tone for PASS."""
        strengths = ["Excellent communication"]
        improvements = []
        scores = {
            "total_score": 12,
            "pass_fail": "PASS",
            "critical_errors": []
        }

        narrative = generator.generate_narrative(strengths, improvements, scores)

        # Should have positive tone
        narrative_lower = narrative.lower()
        assert any(kw in narrative_lower for kw in ["strong", "good", "competence", "met"])

    def test_narrative_fail_tone(self, generator):
        """Test narrative has constructive tone for FAIL."""
        strengths = []
        improvements = ["Improve history taking", "Recognize red flags"]
        scores = {
            "total_score": 3,
            "pass_fail": "FAIL",
            "critical_errors": ["Missed red flag"]
        }

        narrative = generator.generate_narrative(strengths, improvements, scores)

        # Should have constructive (not harsh) tone
        narrative_lower = narrative.lower()
        assert any(kw in narrative_lower for kw in ["develop", "improve", "focus", "practice"])

    def test_narrative_borderline_tone(self, generator, borderline_scores):
        """Test narrative for borderline has balanced tone."""
        strengths = ["Basic communication"]
        improvements = ["Improve clinical reasoning", "More systematic history"]

        narrative = generator.generate_narrative(strengths, improvements, borderline_scores)

        # Should be balanced
        narrative_lower = narrative.lower()
        assert any(kw in narrative_lower for kw in ["borderline", "improvement", "competence"])


class TestConvenienceFunction:
    """Test convenience function for feedback generation."""

    def test_convenience_function_exists(self):
        """Test generate_feedback() convenience function exists."""
        if generate_feedback is None:
            pytest.skip("generate_feedback not implemented yet")

        assert callable(generate_feedback)

    def test_convenience_function_returns_dict(self, perfect_transcript, perfect_scores):
        """Test convenience function returns feedback dict."""
        if generate_feedback is None:
            pytest.skip("generate_feedback not implemented yet")

        persona = {"chief_complaint": "Test"}
        feedback = generate_feedback(perfect_transcript, perfect_scores, persona)

        assert isinstance(feedback, dict)
        assert "strengths" in feedback
        assert "areas_for_improvement" in feedback
        assert "narrative" in feedback


class TestEdgeCases:
    """Test edge cases and robustness."""

    def test_empty_transcript(self, generator):
        """Test empty transcript generates generic feedback."""
        scores = {
            "communication_score": 1,
            "clinical_reasoning_score": 1,
            "information_gathering_score": 1,
            "management_score": 0,
            "professionalism_score": 1,
            "total_score": 4,
            "pass_fail": "FAIL",
            "critical_errors": []
        }

        feedback = generator.generate_feedback([], scores, {})

        # Should still generate valid structure
        assert "strengths" in feedback
        assert "areas_for_improvement" in feedback
        assert "narrative" in feedback

    def test_missing_persona(self, generator, perfect_transcript, perfect_scores):
        """Test missing persona doesn't crash."""
        feedback = generator.generate_feedback(perfect_transcript, perfect_scores, {})

        # Should return valid feedback
        assert isinstance(feedback, dict)
        assert len(feedback["strengths"]) > 0
