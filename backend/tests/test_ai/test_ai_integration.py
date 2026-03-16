"""
Phase 5: Integration Tests - End-to-End AI OSCE Workflow
Tests complete workflow: AI Patient → Emotional State → RAG → AI Examiner
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import json


class TestFullOSCESessionFlow:
    """Test complete AI OSCE session workflow"""
    
    @pytest.fixture
    def mock_vault(self):
        """Mock Vault for API keys"""
        with patch('src.ai.ai_patient.get_vault_secret') as mock_vault_patient, \
             patch('src.ai.ai_examiner.get_vault_secret') as mock_vault_examiner:
            mock_vault_patient.return_value = "test-api-key"
            mock_vault_examiner.return_value = "test-api-key"
            yield
    
    @pytest.fixture
    def mock_persona(self):
        """Mock patient persona"""
        persona = Mock()
        persona.name = "Test Patient"
        persona.age = 50
        persona.gender = "Male"
        persona.occupation = "Teacher"
        persona.cultural_background = "Australian"
        persona.chief_complaint = "Chest pain"
        persona.opening_statement = "I have chest pain"
        persona.symptoms = {
            "immediate": ["chest pain"],
            "when_asked_onset": "Started 2 hours ago",
            "when_asked_severity": "8 out of 10"
        }
        persona.key_differentials = ["STEMI", "Unstable angina"]
        persona.critical_actions = ["ECG", "Aspirin"]
        return persona
    
    @patch('src.ai.ai_patient.Anthropic')
    @patch('src.ai.ai_examiner.Anthropic')
    @patch('src.ai.rag_service.QdrantClient')
    @patch('src.ai.emotional_state.get_redis_client')
    def test_complete_osce_workflow(
        self,
        mock_redis,
        mock_qdrant,
        mock_examiner_anthropic,
        mock_patient_anthropic,
        mock_vault,
        mock_persona
    ):
        """Test complete AI OSCE session from start to finish"""
        from src.ai.ai_patient import AIPatientService
        from src.ai.emotional_state import EmotionalStateMachine
        from src.ai.rag_service import RAGService
        from src.ai.ai_examiner import AIExaminerService
        
        # Setup mocks
        # Mock Redis
        mock_redis_client = Mock()
        mock_redis.return_value = mock_redis_client
        
        # Mock Qdrant
        mock_qdrant_client = Mock()
        mock_qdrant.return_value = mock_qdrant_client
        mock_qdrant_result = Mock()
        mock_qdrant_result.payload = {
            "text": "Chest pain clinical guidelines",
            "source": "eTG",
            "page_ref": "p.100"
        }
        mock_qdrant_client.search.return_value = [mock_qdrant_result]
        
        # Mock AI Patient
        mock_patient_client = MagicMock()
        mock_patient_anthropic.return_value = mock_patient_client
        mock_patient_response = Mock()
        mock_patient_response.content = [Mock(text="I have severe chest pain.")]
        mock_patient_response.usage = Mock(input_tokens=100, output_tokens=50)
        mock_patient_client.messages.create.return_value = mock_patient_response
        
        # Mock AI Examiner
        mock_examiner_client = MagicMock()
        mock_examiner_anthropic.return_value = mock_examiner_client
        mock_examiner_response = Mock()
        mock_examiner_response.content = [Mock(text=json.dumps({
            "communication_score": 3,
            "communication_feedback": "Good",
            "clinical_reasoning_score": 3,
            "clinical_reasoning_feedback": "Good",
            "information_gathering_score": 3,
            "information_gathering_feedback": "Good",
            "management_score": 2,
            "management_feedback": "Good",
            "professionalism_score": 2,
            "professionalism_feedback": "Good",
            "total_score": 13,
            "pass_fail": "PASS",
            "critical_errors": [],
            "strengths": ["Good communication"],
            "areas_for_improvement": [],
            "overall_feedback": "Well done"
        }))]
        mock_examiner_response.usage = Mock(input_tokens=500, output_tokens=200)
        mock_examiner_client.messages.create.return_value = mock_examiner_response
        
        # Initialize services
        ai_patient = AIPatientService()
        ai_patient.client = mock_patient_client
        
        rag_service = RAGService()
        ai_examiner = AIExaminerService()
        ai_examiner.client = mock_examiner_client
        
        # Simulate 8-minute OSCE session
        transcript = []
        emotional_state = "ANXIOUS_GUARDED"
        
        # Turn 1: Student greeting
        student_msg_1 = "Hello, I'm Dr. Smith. How can I help you today?"
        transcript.append({"role": "student", "message": student_msg_1})
        
        # AI Patient response
        patient_response_1 = ai_patient.generate_response(
            persona=mock_persona,
            student_message=student_msg_1,
            emotional_state=emotional_state
        )
        transcript.append({"role": "patient", "message": patient_response_1})
        assert len(patient_response_1) > 0
        
        # Turn 2: Student shows empathy
        student_msg_2 = "I understand this must be very concerning for you."
        transcript.append({"role": "student", "message": student_msg_2})
        
        # Update emotional state
        state_machine = EmotionalStateMachine()
        emotional_state = state_machine.process_student_message(student_msg_2)
        
        # AI Patient response with new emotional state
        patient_response_2 = ai_patient.generate_response(
            persona=mock_persona,
            student_message=student_msg_2,
            emotional_state=emotional_state
        )
        transcript.append({"role": "patient", "message": patient_response_2})
        
        # Turn 3: RAG-augmented response
        student_msg_3 = "Can you describe the pain?"
        transcript.append({"role": "student", "message": student_msg_3})
        
        # RAG retrieval
        rag_context = rag_service.retrieve_context(student_msg_3, top_k=5)
        assert len(rag_context) > 0
        
        patient_response_3 = ai_patient.generate_response(
            persona=mock_persona,
            student_message=student_msg_3,
            emotional_state=emotional_state
        )
        transcript.append({"role": "patient", "message": patient_response_3})
        
        # Session ends - AI Examiner scores
        scores = ai_examiner.score_session(mock_persona, transcript)
        
        # Verify complete workflow
        assert len(transcript) == 6  # 3 student + 3 patient
        assert scores["total_score"] == 13
        assert scores["pass_fail"] == "PASS"
        assert "communication_score" in scores
        assert "clinical_reasoning_score" in scores


class TestAIPatientEmotionalProgression:
    """Test AI Patient emotional state progression"""
    
    @patch('src.ai.emotional_state.get_redis_client')
    def test_emotional_state_progresses_with_empathy(self, mock_redis):
        """Test patient becomes more trusting with empathy"""
        from src.ai.emotional_state import EmotionalStateMachine
        
        mock_redis_client = Mock()
        mock_redis.return_value = mock_redis_client
        
        state_machine = EmotionalStateMachine()
        
        # Start: ANXIOUS_GUARDED
        assert state_machine.current_state == "ANXIOUS_GUARDED"
        
        # Show empathy 3 times
        state_machine.process_student_message("I understand your concern")
        state_machine.process_student_message("That sounds very difficult")
        state_machine.process_student_message("I can imagine how worried you are")
        
        # Should progress to CAUTIOUSLY_OPEN
        assert state_machine.current_state == "CAUTIOUSLY_OPEN"
        assert state_machine.empathy_points >= 3


class TestRAGAccuracy:
    """Test RAG retrieval accuracy"""
    
    @patch('src.ai.rag_service.QdrantClient')
    def test_rag_returns_relevant_context(self, mock_qdrant):
        """Test RAG retrieves relevant clinical guidelines"""
        from src.ai.rag_service import RAGService
        
        # Mock Qdrant with relevant results
        mock_client = Mock()
        mock_result = Mock()
        mock_result.payload = {
            "text": "Chest pain assessment requires systematic approach",
            "source": "AMC Handbook",
            "page_ref": "p.50"
        }
        mock_client.search.return_value = [mock_result]
        mock_qdrant.return_value = mock_client
        
        rag = RAGService()
        results = rag.retrieve_context("chest pain assessment")
        
        assert len(results) > 0
        assert "text" in results[0]
        assert "source" in results[0]
        assert "chest pain" in results[0]["text"].lower()


class TestPerformanceTargets:
    """Test performance requirements"""
    
    @patch('src.ai.ai_patient.Anthropic')
    @patch('src.ai.ai_patient.get_vault_secret')
    def test_ai_patient_response_time(self, mock_vault, mock_anthropic):
        """Test AI Patient responds within 3s"""
        from src.ai.ai_patient import AIPatientService
        import time
        
        mock_vault.return_value = "test-key"
        
        mock_client = MagicMock()
        mock_response = Mock()
        mock_response.content = [Mock(text="Response")]
        mock_response.usage = Mock(input_tokens=50, output_tokens=25)
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client
        
        service = AIPatientService()
        service.client = mock_client
        
        mock_persona = Mock()
        mock_persona.name = "Test"
        mock_persona.age = 50
        mock_persona.symptoms = {"immediate": ["pain"]}
        
        start = time.time()
        service.generate_response(mock_persona, "Hello", "ANXIOUS_GUARDED")
        elapsed = time.time() - start
        
        assert elapsed < 3.0
    
    @patch('src.ai.rag_service.QdrantClient')
    def test_rag_retrieval_time(self, mock_qdrant):
        """Test RAG retrieves within 500ms"""
        from src.ai.rag_service import RAGService
        import time
        
        mock_client = Mock()
        mock_client.search.return_value = []
        mock_qdrant.return_value = mock_client
        
        service = RAGService()
        
        start = time.time()
        service.retrieve_context("test query")
        elapsed = time.time() - start
        
        assert elapsed < 0.5


class TestSecurityCompliance:
    """Test security requirements"""
    
    def test_no_hardcoded_credentials_in_ai_patient(self):
        """Verify no hardcoded API keys in AI Patient code"""
        import inspect
        from src.ai import ai_patient
        
        source = inspect.getsource(ai_patient)
        
        # Check for hardcoded API keys
        assert "sk-ant-" not in source
        assert 'ANTHROPIC_API_KEY = "' not in source
    
    def test_no_hardcoded_credentials_in_ai_examiner(self):
        """Verify no hardcoded API keys in AI Examiner code"""
        import inspect
        from src.ai import ai_examiner
        
        source = inspect.getsource(ai_examiner)
        
        # Check for hardcoded API keys
        assert "sk-ant-" not in source
        assert 'ANTHROPIC_API_KEY = "' not in source
