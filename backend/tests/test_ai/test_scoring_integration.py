"""
Test Scoring Integration (End-to-End)

Tests complete scoring flow:
- Session → AI Examiner → Confidence → Feedback → Results
"""

import pytest
from unittest.mock import Mock, patch
from typing import Dict, Any

try:
    from src.ai.ai_examiner import AIExaminerService
    from src.ai.scoring.critical_errors import CriticalErrorDetector
    from src.ai.scoring.confidence import calculate_confidence
    from src.ai.scoring.feedback_generator import generate_feedback
except ImportError:
    AIExaminerService = None
    CriticalErrorDetector = None
    calculate_confidence = None
    generate_feedback = None


# Fixtures

@pytest.fixture
def mock_ai_examiner():
    """Mock AI Examiner with Vault integration."""
    if AIExaminerService is None:
        pytest.skip("AIExaminerService not implemented yet")

    with patch('src.ai.ai_examiner.get_vault_secret') as mock_vault:
        mock_vault.return_value = "test-api-key"

        with patch('src.ai.ai_examiner.Anthropic') as mock_anthropic:
            mock_client = Mock()
            mock_anthropic.return_value = mock_client

            service = AIExaminerService()
            service.client = mock_client

            yield service


@pytest.fixture
def critical_detector():
    """Critical error detector instance."""
    if CriticalErrorDetector is None:
        pytest.skip("CriticalErrorDetector not implemented yet")

    return CriticalErrorDetector()


@pytest.fixture
def perfect_session_data():
    """Perfect OSCE session data."""
    return {
        "persona": {
            "name": "Robert Chen",
            "age": 52,
            "chief_complaint": "Chest pain for 2 hours",
            "key_differentials": ["STEMI", "Unstable angina"],
            "critical_actions": ["ECG within 10 minutes", "Aspirin 300mg"]
        },
        "transcript": [
            {"role": "student", "message": "Good morning Mr. Chen. What brings you in today?"},
            {"role": "patient", "message": "I have chest pain for 2 hours."},
            {"role": "student", "message": "That sounds concerning. When did it start exactly?"},
            {"role": "patient", "message": "About 2 hours ago while climbing stairs."},
            {"role": "student", "message": "On a scale of 1-10, how severe is the pain?"},
            {"role": "patient", "message": "It's an 8 out of 10. Very painful."},
            {"role": "student", "message": "Do you have any medical history?"},
            {"role": "patient", "message": "Yes, diabetes and high cholesterol."},
            {"role": "student", "message": "I'm ordering an ECG immediately and giving you aspirin 300mg."},
            {"role": "patient", "message": "Thank you doctor."},
            {"role": "student", "message": "I'm also calling cardiology for urgent assessment."}
        ]
    }


@pytest.fixture
def failing_session_data():
    """Failing OSCE session data."""
    return {
        "persona": {
            "chief_complaint": "Chest pain",
            "critical_actions": ["ECG"]
        },
        "transcript": [
            {"role": "student", "message": "Hi."},
            {"role": "patient", "message": "Chest pain for 2 hours."},
            {"role": "student", "message": "Take paracetamol and rest."}
        ]
    }


# Test Classes

class TestEndToEndScoringFlow:
    """Test complete end-to-end scoring workflow."""

    def test_perfect_session_scoring_flow(self, mock_ai_examiner, critical_detector, perfect_session_data):
        """Test E2E flow for perfect session (15/15, PASS, high confidence)."""
        # Mock Claude API response
        mock_response = Mock()
        mock_response.content = [Mock(text='''{
            "communication_score": 3,
            "communication_feedback": "Excellent communication",
            "clinical_reasoning_score": 4,
            "clinical_reasoning_feedback": "Outstanding reasoning",
            "information_gathering_score": 4,
            "information_gathering_feedback": "Comprehensive history",
            "management_score": 2,
            "management_feedback": "Appropriate management",
            "professionalism_score": 2,
            "professionalism_feedback": "Professional demeanor",
            "total_score": 15,
            "pass_fail": "PASS",
            "critical_errors": [],
            "strengths": ["Recognized ACS", "Excellent communication"],
            "areas_for_improvement": [],
            "overall_feedback": "Excellent performance."
        }''')]
        mock_ai_examiner.client.messages.create = Mock(return_value=mock_response)

        # Step 1: AI Examiner scores session
        scores = mock_ai_examiner.score_session(
            perfect_session_data["persona"],
            perfect_session_data["transcript"]
        )

        # Step 2: Critical error detection
        errors = critical_detector.detect_errors(
            perfect_session_data["transcript"],
            perfect_session_data["persona"],
            scores
        )

        # Step 3: Apply auto-fail if critical errors
        scores = critical_detector.apply_auto_fail(scores, errors)

        # Step 4: Calculate confidence
        confidence = calculate_confidence(
            perfect_session_data["transcript"],
            scores,
            perfect_session_data["persona"]
        )

        # Step 5: Generate feedback
        feedback = generate_feedback(
            perfect_session_data["transcript"],
            scores,
            perfect_session_data["persona"]
        )

        # Assertions: Perfect session should have high scores and confidence
        assert scores["total_score"] == 15
        assert scores["pass_fail"] == "PASS"
        assert len(errors) == 0  # No critical errors
        assert confidence >= 0.9, f"Expected confidence ≥0.9, got {confidence}"
        assert len(feedback["strengths"]) >= 3
        assert "narrative" in feedback

    def test_failing_session_scoring_flow(self, mock_ai_examiner, critical_detector, failing_session_data):
        """Test E2E flow for failing session (missed red flag → FAIL)."""
        # Mock Claude API response
        mock_response = Mock()
        mock_response.content = [Mock(text='''{
            "communication_score": 1,
            "communication_feedback": "Poor communication",
            "clinical_reasoning_score": 0,
            "clinical_reasoning_feedback": "No differential diagnosis",
            "information_gathering_score": 1,
            "information_gathering_feedback": "Inadequate history",
            "management_score": 0,
            "management_feedback": "Unsafe management",
            "professionalism_score": 1,
            "professionalism_feedback": "Basic courtesy",
            "total_score": 3,
            "pass_fail": "FAIL",
            "critical_errors": [],
            "strengths": [],
            "areas_for_improvement": ["Recognize red flags", "Improve history taking"],
            "overall_feedback": "Significant deficiencies."
        }''')]
        mock_ai_examiner.client.messages.create = Mock(return_value=mock_response)

        # Step 1: AI Examiner scores
        scores = mock_ai_examiner.score_session(
            failing_session_data["persona"],
            failing_session_data["transcript"]
        )

        # Step 2: Critical error detection (should detect missed ECG)
        errors = critical_detector.detect_errors(
            failing_session_data["transcript"],
            failing_session_data["persona"],
            scores
        )

        # Step 3: Apply auto-fail
        scores = critical_detector.apply_auto_fail(scores, errors)

        # Step 4: Calculate confidence
        confidence = calculate_confidence(
            failing_session_data["transcript"],
            scores,
            failing_session_data["persona"]
        )

        # Step 5: Generate feedback
        feedback = generate_feedback(
            failing_session_data["transcript"],
            scores,
            failing_session_data["persona"]
        )

        # Assertions: Failing session should have critical errors and low confidence
        assert scores["pass_fail"] == "FAIL"
        assert len(errors) > 0, "Should detect critical error (missed ECG)"
        assert confidence < 0.7, f"Failing session should have low confidence, got {confidence}"
        assert len(feedback["areas_for_improvement"]) >= 2

    def test_critical_error_overrides_high_score(self, mock_ai_examiner, critical_detector):
        """Test critical error causes FAIL even with 15/15 score."""
        # Scenario: Perfect score but missed critical action
        persona = {"chief_complaint": "Chest pain", "critical_actions": ["ECG"]}
        transcript = [
            {"role": "student", "message": "Good communication"},
            {"role": "patient", "message": "Chest pain."},
            {"role": "student", "message": "I'll give you paracetamol."}  # Missed ECG!
        ]

        # Mock perfect scores
        mock_response = Mock()
        mock_response.content = [Mock(text='''{
            "communication_score": 3,
            "communication_feedback": "Excellent",
            "clinical_reasoning_score": 4,
            "clinical_reasoning_feedback": "Outstanding",
            "information_gathering_score": 4,
            "information_gathering_feedback": "Comprehensive",
            "management_score": 2,
            "management_feedback": "Appropriate",
            "professionalism_score": 2,
            "professionalism_feedback": "Professional",
            "total_score": 15,
            "pass_fail": "PASS",
            "critical_errors": [],
            "strengths": ["Great"],
            "areas_for_improvement": [],
            "overall_feedback": "Excellent."
        }''')]
        mock_ai_examiner.client.messages.create = Mock(return_value=mock_response)

        # Score
        scores = mock_ai_examiner.score_session(persona, transcript)

        # Detect critical errors
        errors = critical_detector.detect_errors(transcript, persona, scores)

        # Apply auto-fail
        scores = critical_detector.apply_auto_fail(scores, errors)

        # Assertions: 15/15 but critical error → FAIL
        assert scores["total_score"] == 15  # Score unchanged
        assert scores["pass_fail"] == "FAIL"  # But auto-failed
        assert len(scores["critical_errors"]) > 0


class TestPerformanceTargets:
    """Test performance targets (<5s scoring)."""

    def test_scoring_performance_target(self, mock_ai_examiner, perfect_session_data):
        """Test scoring completes in <5 seconds (p95 target)."""
        import time

        # Mock fast API response
        mock_response = Mock()
        mock_response.content = [Mock(text='{"communication_score": 3, "clinical_reasoning_score": 4, "information_gathering_score": 4, "management_score": 2, "professionalism_score": 2, "total_score": 15, "pass_fail": "PASS", "critical_errors": [], "strengths": [], "areas_for_improvement": [], "overall_feedback": "Good.", "communication_feedback": "Good", "clinical_reasoning_feedback": "Good", "information_gathering_feedback": "Good", "management_feedback": "Good", "professionalism_feedback": "Good"}')]
        mock_ai_examiner.client.messages.create = Mock(return_value=mock_response)

        start_time = time.time()

        # AI Examiner scoring
        scores = mock_ai_examiner.score_session(
            perfect_session_data["persona"],
            perfect_session_data["transcript"]
        )

        # Critical error detection
        detector = CriticalErrorDetector()
        errors = detector.detect_errors(
            perfect_session_data["transcript"],
            perfect_session_data["persona"],
            scores
        )

        # Confidence calculation
        confidence = calculate_confidence(
            perfect_session_data["transcript"],
            scores,
            perfect_session_data["persona"]
        )

        # Feedback generation
        feedback = generate_feedback(
            perfect_session_data["transcript"],
            scores,
            perfect_session_data["persona"]
        )

        elapsed = time.time() - start_time

        # Should complete <1s (mocked API is fast)
        assert elapsed < 1.0, f"Scoring took {elapsed:.2f}s (target <5s, mocked should be <1s)"


class TestDataValidation:
    """Test all data properly validated throughout pipeline."""

    def test_scores_validated_throughout_pipeline(self, mock_ai_examiner, perfect_session_data):
        """Test scores validated at each pipeline stage."""
        # Mock response
        mock_response = Mock()
        mock_response.content = [Mock(text='{"communication_score": 3, "clinical_reasoning_score": 4, "information_gathering_score": 4, "management_score": 2, "professionalism_score": 2, "total_score": 15, "pass_fail": "PASS", "critical_errors": [], "strengths": [], "areas_for_improvement": [], "overall_feedback": "Good", "communication_feedback": "Good", "clinical_reasoning_feedback": "Good", "information_gathering_feedback": "Good", "management_feedback": "Good", "professionalism_feedback": "Good"}')]
        mock_ai_examiner.client.messages.create = Mock(return_value=mock_response)

        # Score
        scores = mock_ai_examiner.score_session(
            perfect_session_data["persona"],
            perfect_session_data["transcript"]
        )

        # Validate structure
        assert "total_score" in scores
        assert "pass_fail" in scores
        assert "critical_errors" in scores

        # Validate ranges
        assert 0 <= scores["communication_score"] <= 3
        assert 0 <= scores["clinical_reasoning_score"] <= 4
        assert 0 <= scores["information_gathering_score"] <= 4
        assert 0 <= scores["management_score"] <= 2
        assert 0 <= scores["professionalism_score"] <= 2
        assert 0 <= scores["total_score"] <= 15

        # Validate pass/fail
        assert scores["pass_fail"] in ["PASS", "BORDERLINE", "FAIL"]
