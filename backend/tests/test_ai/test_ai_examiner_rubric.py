"""
Test AI Examiner AMC 15-Mark Rubric Implementation
Tests enhanced scoring validation and feedback generation
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any

# Import with try/except for TDD pattern
try:
    from src.ai.ai_examiner import AIExaminerService
except ImportError:
    AIExaminerService = None


# Fixtures

@pytest.fixture
def mock_persona():
    """Mock patient persona for testing."""
    return {
        "name": "Robert Chen",
        "age": 52,
        "chief_complaint": "Chest pain for 2 hours",
        "key_differentials": ["STEMI", "Unstable angina", "PE"],
        "critical_actions": [
            "ECG within 10 minutes",
            "Aspirin 300mg immediately",
            "Urgent cardiology involvement"
        ]
    }


@pytest.fixture
def perfect_transcript():
    """Transcript of a perfect OSCE session (15/15)."""
    return [
        {"role": "student", "message": "Good morning Mr. Chen. I understand you're having chest pain. Can you tell me what happened?"},
        {"role": "patient", "message": "Doctor, I've had this terrible crushing chest pain for 2 hours. It's radiating to my left arm."},
        {"role": "student", "message": "That sounds very concerning. I'm here to help. On a scale of 1-10, how severe is the pain?"},
        {"role": "patient", "message": "It's an 8 out of 10. Really bad."},
        {"role": "student", "message": "I understand this must be frightening. When did it start exactly?"},
        {"role": "patient", "message": "About 2 hours ago at work, after climbing stairs."},
        {"role": "student", "message": "Have you had anything like this before? Any medical history?"},
        {"role": "patient", "message": "I have diabetes and high cholesterol. My father had a heart attack at 50."},
        {"role": "student", "message": "Thank you for sharing that. I'm ordering an ECG right now to check your heart. I'm also giving you aspirin to prevent blood clots, and I'm calling cardiology for urgent assessment. Do you have any allergies?"},
        {"role": "patient", "message": "No allergies. Thank you for explaining everything doctor."}
    ]


@pytest.fixture
def passing_transcript():
    """Transcript of a passing session (9-14/15)."""
    return [
        {"role": "student", "message": "Hello, what brings you in today?"},
        {"role": "patient", "message": "I have chest pain."},
        {"role": "student", "message": "When did it start?"},
        {"role": "patient", "message": "2 hours ago."},
        {"role": "student", "message": "Is it severe?"},
        {"role": "patient", "message": "Yes, very painful."},
        {"role": "student", "message": "I'll order an ECG and give you aspirin."},
        {"role": "patient", "message": "Okay."}
    ]


@pytest.fixture
def borderline_transcript():
    """Transcript of a borderline session (8/15)."""
    return [
        {"role": "student", "message": "What's wrong?"},
        {"role": "patient", "message": "Chest pain."},
        {"role": "student", "message": "How long?"},
        {"role": "patient", "message": "2 hours."},
        {"role": "student", "message": "I'll get some tests."},
        {"role": "patient", "message": "Okay."}
    ]


@pytest.fixture
def failing_transcript():
    """Transcript of a failing session (0-7/15)."""
    return [
        {"role": "student", "message": "Hi."},
        {"role": "patient", "message": "I have chest pain for 2 hours."},
        {"role": "student", "message": "Take some paracetamol and rest."},
        {"role": "patient", "message": "That's it?"}
    ]


@pytest.fixture
def ai_examiner_service():
    """AI Examiner service with mocked Claude API."""
    # Import the module first to ensure it's available for patching
    import src.ai.ai_examiner

    with patch('src.ai.ai_examiner.get_vault_secret') as mock_vault:
        mock_vault.return_value = "test-api-key-from-vault"

        with patch('src.ai.ai_examiner.Anthropic') as mock_anthropic:
            mock_client = Mock()
            mock_anthropic.return_value = mock_client

            from src.ai.ai_examiner import AIExaminerService
            service = AIExaminerService()
            service.client = mock_client

            yield service


# Test Classes

class TestAIExaminerRubric:
    """Test AMC 15-mark rubric implementation."""

    def test_score_perfect_session(self, ai_examiner_service, mock_persona, perfect_transcript):
        """Test scoring of a perfect OSCE session (15/15, PASS)."""
        # Mock Claude API response
        mock_response = Mock()
        mock_response.content = [Mock(text='''{
            "communication_score": 3,
            "communication_feedback": "Outstanding empathy and communication",
            "clinical_reasoning_score": 4,
            "clinical_reasoning_feedback": "Excellent differential diagnosis",
            "information_gathering_score": 4,
            "information_gathering_feedback": "Comprehensive systematic history",
            "management_score": 2,
            "management_feedback": "Appropriate evidence-based management",
            "professionalism_score": 2,
            "professionalism_feedback": "Exemplary professionalism",
            "total_score": 15,
            "pass_fail": "PASS",
            "critical_errors": [],
            "strengths": ["Recognized ACS immediately", "Outstanding communication"],
            "areas_for_improvement": [],
            "overall_feedback": "Excellent performance meeting AMC standards."
        }''')]

        ai_examiner_service.client.messages.create = Mock(return_value=mock_response)

        # Score session
        result = ai_examiner_service.score_session(mock_persona, perfect_transcript)

        # Assertions
        assert result["total_score"] == 15
        assert result["pass_fail"] == "PASS"
        assert result["communication_score"] == 3
        assert result["clinical_reasoning_score"] == 4
        assert result["information_gathering_score"] == 4
        assert result["management_score"] == 2
        assert result["professionalism_score"] == 2
        assert len(result["critical_errors"]) == 0
        assert len(result["strengths"]) > 0

    def test_score_passing_session(self, ai_examiner_service, mock_persona, passing_transcript):
        """Test scoring of a passing session (9-14/15, PASS)."""
        # Mock Claude API response
        mock_response = Mock()
        mock_response.content = [Mock(text='''{
            "communication_score": 2,
            "communication_feedback": "Adequate communication",
            "clinical_reasoning_score": 3,
            "clinical_reasoning_feedback": "Good differential diagnosis",
            "information_gathering_score": 2,
            "information_gathering_feedback": "Basic history obtained",
            "management_score": 2,
            "management_feedback": "Appropriate management",
            "professionalism_score": 2,
            "professionalism_feedback": "Professional demeanor",
            "total_score": 11,
            "pass_fail": "PASS",
            "critical_errors": [],
            "strengths": ["Ordered ECG", "Gave aspirin"],
            "areas_for_improvement": ["Could have been more empathetic"],
            "overall_feedback": "Satisfactory performance with room for improvement."
        }''')]

        ai_examiner_service.client.messages.create = Mock(return_value=mock_response)

        # Score session
        result = ai_examiner_service.score_session(mock_persona, passing_transcript)

        # Assertions
        assert 9 <= result["total_score"] <= 14
        assert result["pass_fail"] == "PASS"
        assert len(result["areas_for_improvement"]) > 0

    def test_score_borderline_session(self, ai_examiner_service, mock_persona, borderline_transcript):
        """Test scoring of a borderline session (8/15, BORDERLINE)."""
        # Mock Claude API response
        mock_response = Mock()
        mock_response.content = [Mock(text='''{
            "communication_score": 1,
            "communication_feedback": "Minimal communication",
            "clinical_reasoning_score": 2,
            "clinical_reasoning_feedback": "Limited clinical reasoning",
            "information_gathering_score": 2,
            "information_gathering_feedback": "Incomplete history",
            "management_score": 2,
            "management_feedback": "Basic management",
            "professionalism_score": 1,
            "professionalism_feedback": "Adequate professionalism",
            "total_score": 8,
            "pass_fail": "BORDERLINE",
            "critical_errors": [],
            "strengths": ["Mentioned tests"],
            "areas_for_improvement": ["Needs more detailed history", "Improve communication"],
            "overall_feedback": "Borderline performance requiring improvement."
        }''')]

        ai_examiner_service.client.messages.create = Mock(return_value=mock_response)

        # Score session
        result = ai_examiner_service.score_session(mock_persona, borderline_transcript)

        # Assertions
        assert result["total_score"] == 8
        assert result["pass_fail"] == "BORDERLINE"
        assert len(result["areas_for_improvement"]) >= 2

    def test_score_failing_session(self, ai_examiner_service, mock_persona, failing_transcript):
        """Test scoring of a failing session (0-7/15, FAIL)."""
        # Mock Claude API response
        mock_response = Mock()
        mock_response.content = [Mock(text='''{
            "communication_score": 0,
            "communication_feedback": "Poor communication",
            "clinical_reasoning_score": 0,
            "clinical_reasoning_feedback": "No differential diagnosis",
            "information_gathering_score": 0,
            "information_gathering_feedback": "No systematic history",
            "management_score": 0,
            "management_feedback": "Unsafe management",
            "professionalism_score": 1,
            "professionalism_feedback": "Basic courtesy only",
            "total_score": 1,
            "pass_fail": "FAIL",
            "critical_errors": ["Missed acute red flag - chest pain with no ECG"],
            "strengths": [],
            "areas_for_improvement": ["Must recognize red flags", "Improve history taking", "Learn appropriate management"],
            "overall_feedback": "Significant deficiencies requiring remediation."
        }''')]

        ai_examiner_service.client.messages.create = Mock(return_value=mock_response)

        # Score session
        result = ai_examiner_service.score_session(mock_persona, failing_transcript)

        # Assertions
        assert result["total_score"] <= 7
        assert result["pass_fail"] == "FAIL"
        assert len(result["critical_errors"]) > 0 or result["total_score"] <= 7


class TestPassFailLogic:
    """Test pass/fail determination logic."""

    def test_pass_fail_logic(self, ai_examiner_service):
        """Test pass/fail logic (≥9 = PASS, 8 = BORDERLINE, ≤7 = FAIL)."""
        # Test PASS (≥9)
        scores = {"communication_score": 2, "clinical_reasoning_score": 2, "information_gathering_score": 2, "management_score": 2, "professionalism_score": 1, "critical_errors": []}
        validated = ai_examiner_service._validate_scores(scores)
        assert validated["total_score"] == 9
        assert validated["pass_fail"] == "PASS"

        # Test BORDERLINE (8)
        scores = {"communication_score": 2, "clinical_reasoning_score": 2, "information_gathering_score": 2, "management_score": 1, "professionalism_score": 1, "critical_errors": []}
        validated = ai_examiner_service._validate_scores(scores)
        assert validated["total_score"] == 8
        assert validated["pass_fail"] == "BORDERLINE"

        # Test FAIL (≤7)
        scores = {"communication_score": 1, "clinical_reasoning_score": 1, "information_gathering_score": 2, "management_score": 1, "professionalism_score": 1, "critical_errors": []}
        validated = ai_examiner_service._validate_scores(scores)
        assert validated["total_score"] == 6
        assert validated["pass_fail"] == "FAIL"

    def test_critical_error_override(self, ai_examiner_service):
        """Test critical error overrides score (15/15 but CE → FAIL)."""
        scores = {
            "communication_score": 3,
            "clinical_reasoning_score": 4,
            "information_gathering_score": 4,
            "management_score": 2,
            "professionalism_score": 2,
            "critical_errors": ["Missed acute red flag"]
        }

        validated = ai_examiner_service._validate_scores(scores)

        assert validated["total_score"] == 15
        assert validated["pass_fail"] == "FAIL"  # Critical error overrides
        assert len(validated["critical_errors"]) > 0

    def test_json_output_validation(self, ai_examiner_service):
        """Test all required JSON fields are present."""
        scores = {
            "communication_score": 2,
            "clinical_reasoning_score": 3,
            "information_gathering_score": 3,
            "management_score": 2,
            "professionalism_score": 2
        }

        validated = ai_examiner_service._validate_scores(scores)

        # Check all required fields exist
        required_fields = [
            "communication_score", "communication_feedback",
            "clinical_reasoning_score", "clinical_reasoning_feedback",
            "information_gathering_score", "information_gathering_feedback",
            "management_score", "management_feedback",
            "professionalism_score", "professionalism_feedback",
            "total_score", "pass_fail",
            "critical_errors", "strengths", "areas_for_improvement", "overall_feedback"
        ]

        for field in required_fields:
            assert field in validated, f"Missing required field: {field}"

    def test_feedback_fields_validated(self, ai_examiner_service):
        """Test all feedback fields are validated as strings."""
        scores = {
            "communication_score": 2,
            "clinical_reasoning_score": 3,
            "information_gathering_score": 3,
            "management_score": 2,
            "professionalism_score": 2,
            # Deliberately missing feedback fields
        }

        validated = ai_examiner_service._validate_scores(scores)

        # All feedback fields should be strings (with fallback values)
        feedback_fields = [
            "communication_feedback",
            "clinical_reasoning_feedback",
            "information_gathering_feedback",
            "management_feedback",
            "professionalism_feedback",
            "overall_feedback"
        ]

        for field in feedback_fields:
            assert isinstance(validated[field], str), f"{field} should be a string"
            assert len(validated[field]) > 0, f"{field} should not be empty"

    def test_arrays_validated(self, ai_examiner_service):
        """Test all arrays are validated as lists."""
        scores = {
            "communication_score": 2,
            "clinical_reasoning_score": 3,
            "information_gathering_score": 3,
            "management_score": 2,
            "professionalism_score": 2,
            # Deliberately missing arrays
        }

        validated = ai_examiner_service._validate_scores(scores)

        # All array fields should be lists
        array_fields = ["critical_errors", "strengths", "areas_for_improvement"]

        for field in array_fields:
            assert isinstance(validated[field], list), f"{field} should be a list"

    def test_temperature_consistency(self, ai_examiner_service):
        """Test temperature = 0.1 for consistent scoring."""
        assert ai_examiner_service.temperature == 0.1, "Temperature should be 0.1 for deterministic scoring"
        assert ai_examiner_service.model == "claude-3-5-sonnet-20250219", "Should use Claude 3.5 Sonnet"
