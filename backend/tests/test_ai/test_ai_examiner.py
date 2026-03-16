"""
TDD Tests for AI Examiner Service
Phase 4: AI Examiner

CRITICAL: Tests written FIRST following TDD methodology.
Expected initial result: ALL TESTS FAIL (RED phase)
After implementation: ALL TESTS PASS (GREEN phase)
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import json

# Import will fail initially (TDD RED phase)
try:
    from src.ai.ai_examiner import AIExaminerService
    from src.ai.prompts.examiner_system_prompt import build_examiner_system_prompt
except ImportError:
    AIExaminerService = None
    build_examiner_system_prompt = None


@pytest.fixture
def mock_persona():
    """Mock patient persona for testing"""
    persona = Mock()
    persona.name = "Robert Chen"
    persona.chief_complaint = "Chest pain for 2 hours"
    persona.key_differentials = ["STEMI", "Unstable angina", "PE"]
    persona.critical_actions = ["ECG <10 min", "Aspirin 300mg", "Cardiology consult"]
    return persona


@pytest.fixture
def mock_transcript():
    """Mock conversation transcript"""
    return [
        {"role": "student", "message": "Hello, I'm Dr. Smith. How can I help you today?"},
        {"role": "patient", "message": "I've been having terrible chest pain for 2 hours."},
        {"role": "student", "message": "I understand this must be frightening. Can you describe the pain?"},
        {"role": "patient", "message": "It's crushing, like someone standing on my chest. Goes down my left arm."},
        {"role": "student", "message": "When did it start?"},
        {"role": "patient", "message": "Started after climbing stairs at work."}
    ]


@pytest.fixture
def mock_vault():
    """Mock Vault client that returns test API key"""
    with patch('src.ai.ai_examiner.get_vault_secret') as mock_get_secret:
        mock_get_secret.return_value = "test-api-key-from-vault"
        yield mock_get_secret


class TestAIExaminerInitialization:
    """Test suite for AI Examiner service initialization"""
    
    def test_ai_examiner_service_exists(self):
        """Test that AIExaminerService class exists"""
        if AIExaminerService is None:
            pytest.fail("AIExaminerService not implemented yet (TDD RED)")
        assert AIExaminerService is not None
    
    def test_ai_examiner_initializes_with_vault_key(self, mock_vault):
        """Test AI Examiner service initializes with Vault API key"""
        if AIExaminerService is None:
            pytest.skip("AIExaminerService not implemented yet")
        
        service = AIExaminerService()
        
        # Verify Vault was called for API key
        mock_vault.assert_called()
        
        # Verify service initialized correctly
        assert service.client is not None
        assert service.model == "claude-3-5-sonnet-20250219"
        assert service.temperature == 0.1  # Consistent scoring
        assert service.max_tokens == 2000
    
    def test_no_hardcoded_api_key(self, mock_vault):
        """Test that no hardcoded API keys exist"""
        if AIExaminerService is None:
            pytest.skip("AIExaminerService not implemented yet")
        
        service = AIExaminerService()
        assert service.api_key == "test-api-key-from-vault"


class TestScoring:
    """Test suite for OSCE session scoring"""
    
    @patch('src.ai.ai_examiner.Anthropic')
    def test_score_session_basic(self, mock_anthropic_class, mock_vault, mock_persona, mock_transcript):
        """Test AI Examiner scores session successfully"""
        if AIExaminerService is None:
            pytest.skip("AIExaminerService not implemented yet")
        
        # Mock Claude API response
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client
        
        mock_response = Mock()
        mock_response.content = [Mock(text=json.dumps({
            "communication_score": 3,
            "communication_feedback": "Excellent empathy and rapport",
            "clinical_reasoning_score": 4,
            "clinical_reasoning_feedback": "Recognized ACS immediately",
            "information_gathering_score": 4,
            "information_gathering_feedback": "Systematic history",
            "management_score": 2,
            "management_feedback": "Appropriate management",
            "professionalism_score": 2,
            "professionalism_feedback": "Exemplary professionalism",
            "total_score": 15,
            "pass_fail": "PASS",
            "critical_errors": [],
            "strengths": ["Excellent communication", "Rapid recognition"],
            "areas_for_improvement": [],
            "overall_feedback": "Outstanding performance"
        }))]
        mock_client.messages.create.return_value = mock_response
        
        service = AIExaminerService()
        service.client = mock_client
        
        # Score session
        scores = service.score_session(mock_persona, mock_transcript)
        
        # Verify scoring structure
        assert "communication_score" in scores
        assert "clinical_reasoning_score" in scores
        assert "information_gathering_score" in scores
        assert "management_score" in scores
        assert "professionalism_score" in scores
        assert "total_score" in scores
        assert "pass_fail" in scores
        
        # Verify scores in valid ranges
        assert 0 <= scores["communication_score"] <= 3
        assert 0 <= scores["clinical_reasoning_score"] <= 4
        assert 0 <= scores["information_gathering_score"] <= 4
        assert 0 <= scores["management_score"] <= 2
        assert 0 <= scores["professionalism_score"] <= 2
        assert 0 <= scores["total_score"] <= 15
        assert scores["pass_fail"] in ["PASS", "BORDERLINE", "FAIL"]
    
    @patch('src.ai.ai_examiner.Anthropic')
    def test_total_score_calculation(self, mock_anthropic_class, mock_vault, mock_persona, mock_transcript):
        """Test total_score equals sum of domain scores"""
        if AIExaminerService is None:
            pytest.skip("AIExaminerService not implemented yet")
        
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client
        
        mock_response = Mock()
        mock_response.content = [Mock(text=json.dumps({
            "communication_score": 2,
            "communication_feedback": "Good",
            "clinical_reasoning_score": 3,
            "clinical_reasoning_feedback": "Good",
            "information_gathering_score": 3,
            "information_gathering_feedback": "Good",
            "management_score": 1,
            "management_feedback": "Adequate",
            "professionalism_score": 2,
            "professionalism_feedback": "Good",
            "total_score": 11,
            "pass_fail": "PASS",
            "critical_errors": [],
            "strengths": [],
            "areas_for_improvement": [],
            "overall_feedback": "Good performance"
        }))]
        mock_client.messages.create.return_value = mock_response
        
        service = AIExaminerService()
        service.client = mock_client
        
        scores = service.score_session(mock_persona, mock_transcript)
        
        # Verify total_score = sum of domains
        expected_total = (
            scores["communication_score"] +
            scores["clinical_reasoning_score"] +
            scores["information_gathering_score"] +
            scores["management_score"] +
            scores["professionalism_score"]
        )
        assert scores["total_score"] == expected_total
    
    @patch('src.ai.ai_examiner.Anthropic')
    def test_pass_fail_logic(self, mock_anthropic_class, mock_vault, mock_persona, mock_transcript):
        """Test pass/fail determination logic"""
        if AIExaminerService is None:
            pytest.skip("AIExaminerService not implemented yet")
        
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client
        
        service = AIExaminerService()
        service.client = mock_client
        
        # Test PASS (≥9 points, no critical errors)
        mock_response = Mock()
        mock_response.content = [Mock(text=json.dumps({
            "communication_score": 2, "communication_feedback": "",
            "clinical_reasoning_score": 2, "clinical_reasoning_feedback": "",
            "information_gathering_score": 3, "information_gathering_feedback": "",
            "management_score": 1, "management_feedback": "",
            "professionalism_score": 1, "professionalism_feedback": "",
            "total_score": 9, "pass_fail": "PASS", "critical_errors": [],
            "strengths": [], "areas_for_improvement": [], "overall_feedback": ""
        }))]
        mock_client.messages.create.return_value = mock_response
        scores = service.score_session(mock_persona, mock_transcript)
        assert scores["pass_fail"] == "PASS"
        assert scores["total_score"] >= 9
        
        # Test FAIL (≤7 points)
        mock_response.content = [Mock(text=json.dumps({
            "communication_score": 1, "communication_feedback": "",
            "clinical_reasoning_score": 1, "clinical_reasoning_feedback": "",
            "information_gathering_score": 2, "information_gathering_feedback": "",
            "management_score": 1, "management_feedback": "",
            "professionalism_score": 1, "professionalism_feedback": "",
            "total_score": 6, "pass_fail": "FAIL", "critical_errors": [],
            "strengths": [], "areas_for_improvement": [], "overall_feedback": ""
        }))]
        scores = service.score_session(mock_persona, mock_transcript)
        assert scores["pass_fail"] == "FAIL"
        assert scores["total_score"] <= 7


class TestCriticalErrors:
    """Test suite for critical error detection"""
    
    @patch('src.ai.ai_examiner.Anthropic')
    def test_critical_error_auto_fail(self, mock_anthropic_class, mock_vault, mock_persona, mock_transcript):
        """Test critical errors cause auto-fail regardless of score"""
        if AIExaminerService is None:
            pytest.skip("AIExaminerService not implemented yet")
        
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client
        
        # High score but critical error
        mock_response = Mock()
        mock_response.content = [Mock(text=json.dumps({
            "communication_score": 3, "communication_feedback": "",
            "clinical_reasoning_score": 3, "clinical_reasoning_feedback": "",
            "information_gathering_score": 3, "information_gathering_feedback": "",
            "management_score": 2, "management_feedback": "",
            "professionalism_score": 2, "professionalism_feedback": "",
            "total_score": 13,
            "pass_fail": "FAIL",
            "critical_errors": ["Missed critical red flag: no ECG ordered"],
            "strengths": [], "areas_for_improvement": [], "overall_feedback": ""
        }))]
        mock_client.messages.create.return_value = mock_response
        
        service = AIExaminerService()
        service.client = mock_client
        
        scores = service.score_session(mock_persona, mock_transcript)
        
        # Should be FAIL despite high score
        assert scores["pass_fail"] == "FAIL"
        assert len(scores["critical_errors"]) > 0


class TestSystemPromptBuilder:
    """Test suite for examiner SYSTEM_PROMPT builder"""
    
    def test_build_examiner_system_prompt_exists(self):
        """Test that build_examiner_system_prompt function exists"""
        if build_examiner_system_prompt is None:
            pytest.fail("build_examiner_system_prompt not implemented yet")
        assert build_examiner_system_prompt is not None
    
    def test_system_prompt_includes_persona(self, mock_persona, mock_transcript):
        """Test SYSTEM_PROMPT includes persona details"""
        if build_examiner_system_prompt is None:
            pytest.skip("build_examiner_system_prompt not implemented yet")
        
        prompt = build_examiner_system_prompt(mock_persona, mock_transcript)
        
        # Verify persona details included
        assert mock_persona.name in prompt
        assert mock_persona.chief_complaint in prompt
        assert "STEMI" in prompt  # Key differential
        assert "ECG" in prompt  # Critical action
    
    def test_system_prompt_includes_transcript(self, mock_persona, mock_transcript):
        """Test SYSTEM_PROMPT includes conversation transcript"""
        if build_examiner_system_prompt is None:
            pytest.skip("build_examiner_system_prompt not implemented yet")
        
        prompt = build_examiner_system_prompt(mock_persona, mock_transcript)
        
        # Verify transcript included
        assert "Hello, I'm Dr. Smith" in prompt
        assert "chest pain" in prompt.lower()
    
    def test_system_prompt_includes_rubric(self, mock_persona, mock_transcript):
        """Test SYSTEM_PROMPT includes AMC 15-mark rubric"""
        if build_examiner_system_prompt is None:
            pytest.skip("build_examiner_system_prompt not implemented yet")
        
        prompt = build_examiner_system_prompt(mock_persona, mock_transcript)
        
        # Verify rubric included
        assert "COMMUNICATION" in prompt.upper()
        assert "CLINICAL REASONING" in prompt.upper()
        assert "INFORMATION GATHERING" in prompt.upper()
        assert "MANAGEMENT" in prompt.upper()
        assert "PROFESSIONALISM" in prompt.upper()
        assert "0-3" in prompt  # Communication range
        assert "0-4" in prompt  # Clinical reasoning range


class TestErrorHandling:
    """Test suite for error handling"""
    
    @patch('src.ai.ai_examiner.Anthropic')
    def test_handles_api_error(self, mock_anthropic_class, mock_vault, mock_persona, mock_transcript):
        """Test graceful handling of Claude API errors"""
        if AIExaminerService is None:
            pytest.skip("AIExaminerService not implemented yet")
        
        mock_client = MagicMock()
        mock_client.messages.create.side_effect = Exception("API error")
        mock_anthropic_class.return_value = mock_client
        
        service = AIExaminerService()
        service.client = mock_client
        
        # Should not crash, return fallback scores
        scores = service.score_session(mock_persona, mock_transcript)
        
        assert isinstance(scores, dict)
        assert "total_score" in scores
        assert scores["pass_fail"] == "FAIL"  # Fallback is FAIL
    
    @patch('src.ai.ai_examiner.Anthropic')
    def test_handles_malformed_json(self, mock_anthropic_class, mock_vault, mock_persona, mock_transcript):
        """Test handling of malformed JSON responses"""
        if AIExaminerService is None:
            pytest.skip("AIExaminerService not implemented yet")
        
        mock_client = MagicMock()
        mock_response = Mock()
        mock_response.content = [Mock(text="This is not JSON")]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic_class.return_value = mock_client
        
        service = AIExaminerService()
        service.client = mock_client
        
        # Should handle gracefully
        scores = service.score_session(mock_persona, mock_transcript)
        assert isinstance(scores, dict)
