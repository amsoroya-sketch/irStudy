# Testing Requirements

[← Back to Index](README.md) | [Quick Start](QUICK_START.md)

---

## Testing Requirements

### 6.1 Unit Test Standards (MANDATORY)

**ALL agent methods MUST have unit tests with 80%+ coverage:**

```python
import pytest
from src.agents.med_001_cardiology import CardiologyExpert
from src.agents.base_agent import AgentTask, TaskStatus, AgentRole

class TestCardiologyExpert:
    """
    Test suite for Cardiology Expert (MED-001).

    Tests cover:
    - Agent initialization
    - Task execution
    - Output validation
    - Medical accuracy checks
    - Australian terminology validation
    """

    @pytest.fixture
    def agent(self):
        """Create agent instance for testing"""
        return CardiologyExpert()

    @pytest.fixture
    def sample_task(self):
        """Create sample task for testing"""
        return AgentTask(
            title="Generate ACS MCQ",
            description="Generate MCQ about acute coronary syndrome",
            metadata={
                'type': 'generate_mcq',
                'topic': 'acute_coronary_syndrome',
                'difficulty': 'medium'
            }
        )

    # Test 1: Agent Initialization
    def test_agent_initialization(self, agent):
        """Test agent initializes with correct metadata"""
        assert agent.metadata.agent_id == "MED-001"
        assert agent.metadata.name == "Cardiology Clinical Expert"
        assert agent.metadata.role == AgentRole.MEDICAL_EXPERT
        assert agent.metadata.experience_years == 15
        assert "Cardiology" in agent.metadata.specializations
        assert "Acute Coronary Syndrome" in agent.metadata.specializations
        assert len(agent.metadata.pros) > 0
        assert len(agent.metadata.cons) > 0

    # Test 2: Successful Task Execution
    def test_execute_task_success(self, agent, sample_task):
        """Test successful task execution returns expected format"""
        result = agent.execute_task(sample_task)

        assert result['status'] == 'success'
        assert 'output' in result
        assert result['validation_passed'] is True

        # Check output structure
        output = result['output']
        assert 'question_id' in output
        assert 'stem' in output
        assert 'options' in output
        assert 'correct_answer' in output
        assert 'explanation' in output
        assert 'citation' in output

    # Test 3: Validation Requires Citation
    def test_validate_output_requires_citation(self, agent, sample_task):
        """Test validation fails when citation is missing"""
        output = {
            'output': {
                'question': 'What is first-line for ACS?',
                'answer': 'Aspirin',
                # Missing citation!
            }
        }

        passed, errors = agent.validate_output(sample_task, output)

        assert not passed
        assert any('citation' in error.lower() for error in errors)

    # Test 4: Australian Spelling Validation
    def test_australian_spelling_validation(self, agent, sample_task):
        """Test validation catches American spelling"""
        output = {
            'output': {
                'stem': 'A pediatric patient presents...',  # American spelling
                'citation': 'Some source'
            }
        }

        passed, errors = agent.validate_output(sample_task, output)

        assert not passed
        assert any(
            'american' in error.lower() or 'spelling' in error.lower() or 'terminology' in error.lower()
            for error in errors
        )

    # Test 5: American Drug Names Validation
    def test_american_drug_names_rejected(self, agent, sample_task):
        """Test validation catches American drug names"""
        output = {
            'output': {
                'explanation': 'Give acetaminophen for pain',  # Should be paracetamol
                'citation': 'Therapeutic Guidelines'
            }
        }

        passed, errors = agent.validate_output(sample_task, output)

        assert not passed
        assert any('drug' in error.lower() or 'american' in error.lower() for error in errors)

    # Test 6: Dosage Units Required
    def test_dosage_requires_units(self, agent, sample_task):
        """Test validation requires dosage units"""
        output = {
            'output': {
                'dosage': '500',  # Missing units!
                'citation': 'Therapeutic Guidelines'
            }
        }

        passed, errors = agent.validate_output(sample_task, output)

        assert not passed
        assert any('unit' in error.lower() or 'dosage' in error.lower() for error in errors)

    # Test 7: Red Flag Detection
    def test_red_flag_detection(self, agent):
        """Test red flag conditions are properly identified"""
        emergency_task = AgentTask(
            title="Emergency case",
            description="Patient with chest pain radiating to arm with diaphoresis",
            metadata={'type': 'assessment'}
        )

        result = agent.execute_task(emergency_task)
        output = result['output']

        assert output.get('red_flag') is True
        assert 'acute coronary syndrome' in output.get('suspected_condition', '').lower()
        assert '000' in output.get('action', '')  # Australian emergency number

    # Test 8: Task Capacity Management
    def test_agent_capacity_management(self, agent):
        """Test agent respects max_concurrent_tasks limit"""
        # Agent max_concurrent_tasks = 5 (from metadata)

        # Assign 5 tasks (should succeed)
        for i in range(5):
            task = AgentTask(title=f"Task {i}")
            success = agent.assign_task(task)
            assert success is True

        # Try to assign 6th task (should fail)
        extra_task = AgentTask(title="Extra task")
        success = agent.assign_task(extra_task)
        assert success is False

    # Test 9: Error Handling
    def test_error_handling(self, agent):
        """Test agent handles errors gracefully"""
        invalid_task = AgentTask(
            title="Invalid task",
            description="",  # Empty description should cause error
            metadata={}  # Missing required metadata
        )

        result = agent.execute_task(invalid_task)

        assert result['status'] == 'error'
        assert 'error' in result
        assert 'error_type' in result

    # Test 10: Run Task Workflow
    def test_run_task_workflow(self, agent, sample_task):
        """Test complete task workflow via run_task()"""
        # Initial state
        assert sample_task.status == TaskStatus.PENDING

        # Run task (uses BaseAgent.run_task)
        result_task = agent.run_task(sample_task)

        # Check final state
        assert result_task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]

        if result_task.status == TaskStatus.COMPLETED:
            assert result_task.result is not None
            assert result_task.completed_at is not None
        else:
            assert result_task.error is not None
```

### 6.2 Integration Test Requirements

**Test multi-agent workflows:**

```python
import pytest
from src.agents.pm_001_project_manager import ProjectManagerAgent
from src.agents.med_001_cardiology import CardiologyExpert
from src.agents.qa_001_medical_qa import MedicalQAAgent
from src.agents.ai_001_rag_system import RAGSystemAgent

class TestMCQGenerationWorkflow:
    """Integration tests for MCQ generation workflow"""

    @pytest.fixture
    def setup_agents(self):
        """Setup all agents for workflow"""
        pm = ProjectManagerAgent()
        rag = RAGSystemAgent()
        medical = CardiologyExpert()
        qa = MedicalQAAgent()

        # Register agents with PM
        pm.register_agent(rag)
        pm.register_agent(medical)
        pm.register_agent(qa)

        return pm, rag, medical, qa

    def test_complete_mcq_workflow(self, setup_agents):
        """Test complete MCQ generation workflow end-to-end"""
        pm, rag, medical, qa = setup_agents

        # Create workflow task
        task = AgentTask(
            title="Generate Cardiology MCQ",
            description="Generate MCQ about acute coronary syndrome for ICRP preparation",
            metadata={
                'type': 'coordinate_agents',
                'workflow': [
                    {
                        'agent_id': 'AI-001',
                        'task_title': 'Retrieve ACS context from medical texts',
                        'task_description': 'Retrieve relevant context about acute coronary syndrome'
                    },
                    {
                        'agent_id': 'MED-001',
                        'task_title': 'Generate ACS MCQ',
                        'task_description': 'Generate MCQ based on retrieved context'
                    },
                    {
                        'agent_id': 'QA-001',
                        'task_title': 'Validate MCQ accuracy',
                        'task_description': 'Validate clinical accuracy and Australian context'
                    }
                ]
            }
        )

        # Execute workflow
        result = pm.execute_task(task)

        # Verify workflow succeeded
        assert result['status'] == 'success'
        assert len(result['workflow_results']) == 3

        # Verify each step
        for step_result in result['workflow_results']:
            assert step_result['assigned'] is True

        # Verify final MCQ quality
        # (In real test, would retrieve MCQ from medical agent's completed tasks)

    def test_workflow_with_qa_failure(self, setup_agents):
        """Test workflow handles QA rejection correctly"""
        # Test that workflow retries if QA fails validation
        # Maximum 3 attempts before failing completely
        pass

    def test_parallel_agent_execution(self, setup_agents):
        """Test multiple agents can work simultaneously"""
        pm, rag, medical, qa = setup_agents

        # Create multiple independent tasks
        tasks = [
            AgentTask(title=f"Task {i}", metadata={'type': 'independent'})
            for i in range(3)
        ]

        # Assign to different agents
        pm.assign_task_to_agent(tasks[0], 'AI-001')
        pm.assign_task_to_agent(tasks[1], 'MED-001')
        pm.assign_task_to_agent(tasks[2], 'QA-001')

        # Verify all accepted
        assert len(rag.current_tasks) == 1
        assert len(medical.current_tasks) == 1
        assert len(qa.current_tasks) == 1
```

### 6.3 Medical Accuracy Validation Tests

**Automated medical accuracy checks:**

```python
import pytest

class TestMedicalAccuracy:
    """Tests for medical accuracy validation"""

    def test_drug_dosage_validation(self):
        """Test drug dosage includes all required information"""
        from src.validators.medical_validator import MedicalContentValidator

        # Valid dosage info
        dosage_info = {
            'drug': 'amoxicillin',
            'dose': '500 mg',  # ✓ Has units
            'frequency': 'TDS',  # ✓ Has frequency
            'duration': '5 days',  # ✓ Has duration
            'indication': 'Community-acquired pneumonia',
            'citation': 'Therapeutic Guidelines: Antibiotic, Section 2.3'  # ✓ Has citation
        }

        validator = MedicalContentValidator()
        is_valid, errors = validator.validate_drug_info(dosage_info)

        assert is_valid
        assert len(errors) == 0

        # Invalid dosage info - missing units
        invalid_dosage = {
            'drug': 'amoxicillin',
            'dose': '500',  # ❌ Missing units
            'frequency': 'TDS',
            'citation': 'Therapeutic Guidelines'
        }

        is_valid, errors = validator.validate_drug_info(invalid_dosage)
        assert not is_valid
        assert any('unit' in error.lower() for error in errors)

    def test_red_flag_detection(self):
        """Test red flag conditions are properly detected"""
        from src.validators.red_flag_detector import RedFlagDetector

        # Critical presentation
        symptoms = {
            'chest_pain': True,
            'radiation': 'left arm',
            'diaphoresis': True,
            'nausea': True
        }

        detector = RedFlagDetector()
        result = detector.check_symptoms(symptoms)

        assert result['is_red_flag'] is True
        assert 'acute coronary syndrome' in result['suspected_condition'].lower()
        assert 'immediate' in result['recommended_action'].lower()
        assert '000' in result['recommended_action']  # Australian emergency number

        # Non-critical presentation
        symptoms = {
            'chest_pain': True,
            'worse_with_deep_breath': True,
            'pleuritic': True
        }

        result = detector.check_symptoms(symptoms)

        # May still be concerning but not immediately life-threatening
        assert 'pulmonary embolism' in result['differential_diagnoses']

    def test_australian_terminology_validation(self):
        """Test Australian medical terminology is enforced"""
        from src.validators.terminology_validator import TerminologyValidator

        validator = TerminologyValidator(region='australia')

        # Test spelling
        assert validator.is_valid_term('paediatric') is True
        assert validator.is_valid_term('pediatric') is False

        # Test drug names
        assert validator.is_valid_drug_name('paracetamol') is True
        assert validator.is_valid_drug_name('acetaminophen') is False

        # Test healthcare terms
        assert validator.is_valid_term('GP') is True
        assert validator.is_valid_term('PCP') is False
```

### 6.4 Performance Benchmarks

**Set and test performance targets:**

```python
import pytest
import time
from src.agents.ai_001_rag_system import RAGSystemAgent

class TestPerformance:
    """Performance benchmark tests"""

    def test_rag_retrieval_performance(self):
        """Test RAG retrieval meets <500ms target"""
        rag = RAGSystemAgent()
        query = "What is the treatment for acute coronary syndrome in Australia?"

        start_time = time.time()
        results = rag.semantic_search(query, top_k=5)
        elapsed_ms = (time.time() - start_time) * 1000

        # Performance target: < 500ms
        assert elapsed_ms < 500, f"RAG retrieval took {elapsed_ms:.1f}ms (target: <500ms)"
        assert len(results) == 5

        # Verify result quality
        for result in results:
            assert 'text' in result
            assert 'source' in result
            assert 'score' in result
            assert result['score'] > 0.5  # Relevance threshold

    def test_mcq_generation_performance(self):
        """Test MCQ generation completes in reasonable time"""
        from src.agents.med_001_cardiology import CardiologyExpert

        agent = CardiologyExpert()
        task = AgentTask(
            title="Generate MCQ",
            metadata={'type': 'generate_mcq', 'topic': 'ACS'}
        )

        start_time = time.time()
        result = agent.execute_task(task)
        elapsed_sec = time.time() - start_time

        # Performance target: < 15 seconds
        assert elapsed_sec < 15, f"MCQ generation took {elapsed_sec:.1f}s (target: <15s)"
        assert result['status'] == 'success'

    def test_batch_processing_efficiency(self):
        """Test batch processing scales efficiently"""
        from src.processors.medical_text_processor import MedicalTextProcessor

        processor = MedicalTextProcessor()

        # Test with increasing batch sizes
        for num_items in [10, 50, 100, 500]:
            items = [f"item_{i}" for i in range(num_items)]

            start_time = time.time()
            results = processor.process_batch(items, batch_size=100)
            elapsed = time.time() - start_time

            items_per_second = num_items / elapsed

            # Should process at least 50 items/second
            assert items_per_second > 50, f"Only {items_per_second:.1f} items/sec (target: >50)"
```

---

---

[← Back to Index](README.md) | [Quick Start](QUICK_START.md)
