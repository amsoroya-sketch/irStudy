#!/usr/bin/env python3
"""
LangGraph Workflows for Agent Orchestration
Defines workflows for multi-agent task execution
"""

from typing import Dict, List, Any, Optional, Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolExecutor
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
import operator
from enum import Enum


class WorkflowStatus(Enum):
    """Workflow execution status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentState(TypedDict):
    """
    State shared across all agents in workflow.

    This is the central state that gets passed between agents.
    Each agent can read from and write to this state.
    """
    # Task information
    task_id: str
    task_description: str
    task_type: str  # "mcq_generation", "deployment", "data_processing", etc.

    # Messages (conversation history)
    messages: Annotated[List[BaseMessage], operator.add]

    # Current status
    status: WorkflowStatus
    current_agent: Optional[str]

    # Intermediate results from agents
    results: Dict[str, Any]

    # Context and metadata
    context: Dict[str, Any]
    metadata: Dict[str, Any]

    # Quality gates
    quality_checks_passed: List[str]
    quality_checks_failed: List[str]

    # Final output
    final_output: Optional[Dict[str, Any]]


class MCQGenerationWorkflow:
    """
    Workflow for generating medical MCQ questions.

    Agents involved:
    1. PM-001: Coordinates workflow
    2. AI-001: RAG System - Retrieves relevant medical content
    3. MED-XXX: Medical Expert - Generates question
    4. QA-001: Medical QA - Validates clinical accuracy
    5. DEV-004: Database - Stores approved question

    Flow:
    User Request → PM → RAG → Medical Expert → QA Review → Database → User
    """

    def __init__(self, pm_agent, rag_agent, medical_agents: Dict, qa_agent, db_agent):
        self.pm_agent = pm_agent
        self.rag_agent = rag_agent
        self.medical_agents = medical_agents  # {specialty: agent}
        self.qa_agent = qa_agent
        self.db_agent = db_agent

        # Build graph
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build LangGraph workflow"""
        workflow = StateGraph(AgentState)

        # Define nodes (each node is an agent)
        workflow.add_node("pm_coordinator", self.pm_coordinate)
        workflow.add_node("rag_retrieval", self.rag_retrieve)
        workflow.add_node("medical_expert", self.medical_generate)
        workflow.add_node("qa_review", self.qa_validate)
        workflow.add_node("database_store", self.database_store)

        # Define edges (workflow flow)
        workflow.set_entry_point("pm_coordinator")

        workflow.add_edge("pm_coordinator", "rag_retrieval")
        workflow.add_edge("rag_retrieval", "medical_expert")
        workflow.add_edge("medical_expert", "qa_review")

        # Conditional edge: QA passes → database, QA fails → retry or end
        workflow.add_conditional_edges(
            "qa_review",
            self.should_retry_or_store,
            {
                "store": "database_store",
                "retry": "medical_expert",
                "fail": END
            }
        )

        workflow.add_edge("database_store", END)

        return workflow.compile()

    def pm_coordinate(self, state: AgentState) -> AgentState:
        """PM-001 coordinates the workflow"""
        print(f"[PM-001] Coordinating MCQ generation: {state['task_description']}")

        # Extract specialty from task
        specialty = state['metadata'].get('specialty', 'general_practice')

        # Update state
        state['status'] = WorkflowStatus.IN_PROGRESS
        state['current_agent'] = 'PM-001'
        state['messages'].append(
            AIMessage(content=f"PM-001: Starting MCQ generation for {specialty}")
        )

        return state

    def rag_retrieve(self, state: AgentState) -> AgentState:
        """AI-001 RAG System retrieves relevant medical content"""
        print("[AI-001] Retrieving medical content from vector database...")

        topic = state['metadata'].get('topic', 'general')

        # Simulate RAG retrieval (in real implementation, call Qdrant)
        retrieved_context = {
            'chunks': [
                {
                    'text': 'Acute coronary syndrome includes unstable angina, NSTEMI, and STEMI...',
                    'source': 'Harrison\'s Internal Medicine',
                    'page': 1523
                },
                {
                    'text': 'Initial management includes MONA (Morphine, Oxygen, Nitrates, Aspirin)...',
                    'source': 'Therapeutic Guidelines',
                    'page': 342
                }
            ],
            'retrieval_time_ms': 450
        }

        state['results']['rag_context'] = retrieved_context
        state['messages'].append(
            AIMessage(content=f"AI-001: Retrieved {len(retrieved_context['chunks'])} relevant chunks")
        )

        return state

    def medical_generate(self, state: AgentState) -> AgentState:
        """MED-XXX Medical Expert generates MCQ question"""
        specialty = state['metadata'].get('specialty', 'general_practice')
        print(f"[MED-{specialty.upper()}] Generating MCQ question...")

        # Get context from RAG
        rag_context = state['results'].get('rag_context', {})

        # Simulate question generation (in real implementation, call LLM)
        generated_question = {
            'question_id': 'MCQ-CARD-001',
            'specialty': specialty,
            'topic': state['metadata'].get('topic', 'general'),
            'difficulty': 'medium',
            'stem': 'A 55-year-old man presents with 30 minutes of crushing chest pain radiating to left arm. ECG shows ST elevation in V2-V4. What is the most appropriate immediate management?',
            'options': {
                'A': 'Aspirin 300mg PO + IV morphine',
                'B': 'Immediate PCI (primary coronary intervention)',
                'C': 'Thrombolysis with alteplase',
                'D': 'Observation and serial troponins',
                'E': 'Oral beta-blocker and statin'
            },
            'correct_answer': 'B',
            'explanation': 'This patient presents with STEMI (ST-elevation myocardial infarction). The most appropriate immediate management is primary PCI within 90 minutes of first medical contact. This is superior to thrombolysis when available promptly. Aspirin and morphine should also be given, but PCI is the definitive treatment.',
            'citations': [
                'Therapeutic Guidelines: Cardiovascular, Section 3.2',
                'Harrison\'s Internal Medicine, Chapter 295'
            ],
            'generation_time_sec': 8.3
        }

        state['results']['generated_question'] = generated_question
        state['messages'].append(
            AIMessage(content=f"MED-{specialty.upper()}: Generated MCQ question")
        )

        return state

    def qa_validate(self, state: AgentState) -> AgentState:
        """QA-001 Medical QA validates clinical accuracy"""
        print("[QA-001] Validating medical accuracy...")

        question = state['results'].get('generated_question', {})

        # Simulate QA validation (in real implementation, run validation checks)
        validation_result = {
            'clinical_accuracy': True,
            'guideline_compliance': True,
            'format_correct': True,
            'clarity_score': 0.92,
            'distractor_quality': 0.88,
            'explanation_quality': 0.95,
            'overall_pass': True,
            'feedback': [
                'Excellent question, clinically accurate',
                'Citations properly referenced',
                'Distractors are plausible'
            ],
            'warnings': []
        }

        state['results']['validation'] = validation_result

        if validation_result['overall_pass']:
            state['quality_checks_passed'].append('medical_accuracy')
            state['messages'].append(
                AIMessage(content="QA-001: Validation PASSED - Question approved")
            )
        else:
            state['quality_checks_failed'].append('medical_accuracy')
            state['messages'].append(
                AIMessage(content="QA-001: Validation FAILED - Needs revision")
            )

        return state

    def should_retry_or_store(self, state: AgentState) -> str:
        """
        Decision function: Should we retry generation or store the question?

        Returns:
            - "store": QA passed, store in database
            - "retry": QA failed, retry generation (max 3 attempts)
            - "fail": Max retries exceeded, fail workflow
        """
        validation = state['results'].get('validation', {})

        if validation.get('overall_pass', False):
            return "store"

        # Check retry count
        retry_count = state['metadata'].get('retry_count', 0)
        if retry_count < 3:
            state['metadata']['retry_count'] = retry_count + 1
            print(f"[PM-001] QA failed, retrying... (attempt {retry_count + 1}/3)")
            return "retry"
        else:
            print("[PM-001] Max retries exceeded, failing workflow")
            return "fail"

    def database_store(self, state: AgentState) -> AgentState:
        """DEV-004 Database stores approved question"""
        print("[DEV-004] Storing question in PostgreSQL...")

        question = state['results'].get('generated_question', {})
        validation = state['results'].get('validation', {})

        # Simulate database storage
        storage_result = {
            'question_id': question['question_id'],
            'stored': True,
            'database': 'postgresql',
            'collection': 'mcq_questions',
            'timestamp': '2025-12-14T10:30:00Z'
        }

        state['results']['storage'] = storage_result
        state['status'] = WorkflowStatus.COMPLETED
        state['final_output'] = {
            'question': question,
            'validation': validation,
            'storage': storage_result
        }

        state['messages'].append(
            AIMessage(content=f"DEV-004: Question {question['question_id']} stored successfully")
        )

        return state

    def run(self, task_description: str, specialty: str, topic: str) -> Dict[str, Any]:
        """
        Execute the MCQ generation workflow.

        Args:
            task_description: High-level task description
            specialty: Medical specialty (cardiology, pediatrics, etc.)
            topic: Specific topic within specialty

        Returns:
            Final output with generated question
        """
        # Initialize state
        initial_state: AgentState = {
            'task_id': f'MCQ-{specialty.upper()}-{topic.upper()}',
            'task_description': task_description,
            'task_type': 'mcq_generation',
            'messages': [HumanMessage(content=task_description)],
            'status': WorkflowStatus.PENDING,
            'current_agent': None,
            'results': {},
            'context': {},
            'metadata': {
                'specialty': specialty,
                'topic': topic,
                'retry_count': 0
            },
            'quality_checks_passed': [],
            'quality_checks_failed': [],
            'final_output': None
        }

        # Run workflow
        final_state = self.graph.invoke(initial_state)

        return final_state


class DeploymentWorkflow:
    """
    Workflow for deploying new features.

    Agents involved:
    1. PM-001: Coordinates deployment
    2. DEV-XXX: Development agents (Backend, Frontend, etc.)
    3. QA-002: E2E Testing
    4. QA-003: Performance Testing
    5. QA-004: Security Testing
    6. DEVOPS-002: CI/CD Engineer

    Flow:
    PM → Dev Agents (parallel) → Testing (parallel) → Quality Gates → Deploy
    """

    def __init__(self, pm_agent, dev_agents: Dict, qa_agents: Dict, devops_agent):
        self.pm_agent = pm_agent
        self.dev_agents = dev_agents
        self.qa_agents = qa_agents
        self.devops_agent = devops_agent

        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build deployment workflow graph"""
        workflow = StateGraph(AgentState)

        # Nodes
        workflow.add_node("pm_plan", self.pm_plan_deployment)
        workflow.add_node("dev_implement", self.dev_implement_features)
        workflow.add_node("qa_test", self.qa_run_tests)
        workflow.add_node("pm_quality_gates", self.pm_run_quality_gates)
        workflow.add_node("devops_deploy", self.devops_deploy)

        # Edges
        workflow.set_entry_point("pm_plan")
        workflow.add_edge("pm_plan", "dev_implement")
        workflow.add_edge("dev_implement", "qa_test")
        workflow.add_edge("qa_test", "pm_quality_gates")

        # Conditional: Quality gates pass → deploy, fail → end
        workflow.add_conditional_edges(
            "pm_quality_gates",
            lambda state: "deploy" if all([
                'code_review' in state['quality_checks_passed'],
                'unit_tests' in state['quality_checks_passed'],
                'security_scan' in state['quality_checks_passed']
            ]) else "fail",
            {
                "deploy": "devops_deploy",
                "fail": END
            }
        )

        workflow.add_edge("devops_deploy", END)

        return workflow.compile()

    def pm_plan_deployment(self, state: AgentState) -> AgentState:
        """PM-001 plans deployment"""
        print("[PM-001] Planning deployment...")
        state['status'] = WorkflowStatus.IN_PROGRESS
        state['current_agent'] = 'PM-001'
        return state

    def dev_implement_features(self, state: AgentState) -> AgentState:
        """Development agents implement features (parallel)"""
        print("[DEV-AGENTS] Implementing features in parallel...")

        # Simulate parallel development
        state['results']['dev_artifacts'] = {
            'backend': {'files': ['api/endpoints.py', 'models/quiz.py'], 'tests': 'passed'},
            'frontend': {'files': ['pages/quiz.tsx', 'components/Timer.tsx'], 'tests': 'passed'}
        }

        return state

    def qa_run_tests(self, state: AgentState) -> AgentState:
        """QA agents run tests (parallel)"""
        print("[QA-AGENTS] Running tests in parallel...")

        # Simulate parallel testing
        state['results']['qa_results'] = {
            'e2e': {'passed': 45, 'failed': 0, 'coverage': 85},
            'performance': {'rps': 3200, 'p95_latency': 95, 'passed': True},
            'security': {'vulnerabilities': 0, 'passed': True}
        }

        return state

    def pm_run_quality_gates(self, state: AgentState) -> AgentState:
        """PM-001 enforces quality gates"""
        print("[PM-001] Running quality gates...")

        qa_results = state['results'].get('qa_results', {})

        # Check quality gates
        if qa_results['e2e']['coverage'] >= 80:
            state['quality_checks_passed'].append('unit_tests')

        if qa_results['security']['passed']:
            state['quality_checks_passed'].append('security_scan')

        # Assume code review passed (manual in real scenario)
        state['quality_checks_passed'].append('code_review')

        return state

    def devops_deploy(self, state: AgentState) -> AgentState:
        """DEVOPS-002 deploys to production"""
        print("[DEVOPS-002] Deploying to Kubernetes...")

        state['results']['deployment'] = {
            'environment': 'production',
            'status': 'success',
            'deployed_at': '2025-12-14T11:00:00Z',
            'health_check': 'passed'
        }

        state['status'] = WorkflowStatus.COMPLETED
        state['final_output'] = state['results']

        return state

    def run(self, feature_description: str) -> Dict[str, Any]:
        """Execute deployment workflow"""
        initial_state: AgentState = {
            'task_id': 'DEPLOY-001',
            'task_description': feature_description,
            'task_type': 'deployment',
            'messages': [HumanMessage(content=feature_description)],
            'status': WorkflowStatus.PENDING,
            'current_agent': None,
            'results': {},
            'context': {},
            'metadata': {},
            'quality_checks_passed': [],
            'quality_checks_failed': [],
            'final_output': None
        }

        final_state = self.graph.invoke(initial_state)
        return final_state


class DataProcessingWorkflow:
    """
    Workflow for processing medical textbooks (PDF → Embeddings → Qdrant).

    Agents involved:
    1. PM-001: Coordinates pipeline
    2. AI-004: ETL Engineer - Runs processing scripts
    3. AI-001: RAG System - Validates embeddings
    4. DEV-004: Database - Manages Qdrant
    5. DEVOPS-003: Monitoring - Tracks progress

    Flow:
    PM → ETL (PDF Extract) → ETL (Chunk) → ETL (Embed) → Database (Index) → Validation
    """

    def __init__(self, pm_agent, etl_agent, rag_agent, db_agent, monitoring_agent):
        self.pm_agent = pm_agent
        self.etl_agent = etl_agent
        self.rag_agent = rag_agent
        self.db_agent = db_agent
        self.monitoring_agent = monitoring_agent

        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build data processing workflow"""
        workflow = StateGraph(AgentState)

        workflow.add_node("pm_coordinate", self.pm_coordinate)
        workflow.add_node("etl_extract", self.etl_extract_pdfs)
        workflow.add_node("etl_chunk", self.etl_chunk_texts)
        workflow.add_node("etl_embed", self.etl_generate_embeddings)
        workflow.add_node("db_index", self.db_index_qdrant)
        workflow.add_node("rag_validate", self.rag_validate_search)

        workflow.set_entry_point("pm_coordinate")
        workflow.add_edge("pm_coordinate", "etl_extract")
        workflow.add_edge("etl_extract", "etl_chunk")
        workflow.add_edge("etl_chunk", "etl_embed")
        workflow.add_edge("etl_embed", "db_index")
        workflow.add_edge("db_index", "rag_validate")
        workflow.add_edge("rag_validate", END)

        return workflow.compile()

    def pm_coordinate(self, state: AgentState) -> AgentState:
        print("[PM-001] Coordinating data processing pipeline...")
        state['status'] = WorkflowStatus.IN_PROGRESS
        return state

    def etl_extract_pdfs(self, state: AgentState) -> AgentState:
        print("[AI-004] Extracting text from PDFs...")
        state['results']['extracted'] = {'pages': 35000, 'words': 12000000}
        return state

    def etl_chunk_texts(self, state: AgentState) -> AgentState:
        print("[AI-004] Chunking medical texts...")
        state['results']['chunks'] = 40000
        return state

    def etl_generate_embeddings(self, state: AgentState) -> AgentState:
        print("[AI-004] Generating PubMedBERT embeddings...")
        state['results']['embeddings'] = {'chunks': 40000, 'dimension': 768}
        return state

    def db_index_qdrant(self, state: AgentState) -> AgentState:
        print("[DEV-004] Indexing in Qdrant...")
        state['results']['qdrant'] = {'collection': 'medical_knowledge', 'points': 40000}
        return state

    def rag_validate_search(self, state: AgentState) -> AgentState:
        print("[AI-001] Validating semantic search...")
        state['results']['validation'] = {'search_quality': 0.93, 'passed': True}
        state['status'] = WorkflowStatus.COMPLETED
        state['final_output'] = state['results']
        return state

    def run(self, pdf_directory: str) -> Dict[str, Any]:
        """Execute data processing workflow"""
        initial_state: AgentState = {
            'task_id': 'DATA-PROC-001',
            'task_description': f'Process PDFs from {pdf_directory}',
            'task_type': 'data_processing',
            'messages': [HumanMessage(content='Process medical textbooks')],
            'status': WorkflowStatus.PENDING,
            'current_agent': None,
            'results': {},
            'context': {'pdf_directory': pdf_directory},
            'metadata': {},
            'quality_checks_passed': [],
            'quality_checks_failed': [],
            'final_output': None
        }

        final_state = self.graph.invoke(initial_state)
        return final_state


# Example usage
if __name__ == "__main__":
    print("LangGraph Agent Orchestration Workflows")
    print("=" * 60)
    print("\n1. MCQ Generation Workflow")
    print("2. Deployment Workflow")
    print("3. Data Processing Workflow")
    print("\nThese workflows coordinate multiple expert agents to complete complex tasks.")
    print("\nTo use:")
    print("  from src.agents.workflows.orchestration import MCQGenerationWorkflow")
    print("  workflow = MCQGenerationWorkflow(pm, rag, medical_agents, qa, db)")
    print("  result = workflow.run('Generate cardiology MCQ', 'cardiology', 'ACS')")
