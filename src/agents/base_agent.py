#!/usr/bin/env python3
"""
Base Agent Class - Foundation for All Expert Agents
Provides common interfaces, tool management, and state handling
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging
from datetime import datetime
import uuid


class AgentRole(Enum):
    """Agent role categories"""

    PROJECT_MANAGEMENT = "project_management"
    MEDICAL_EXPERT = "medical_expert"
    BACKEND_DEV = "backend_dev"
    FRONTEND_DEV = "frontend_dev"
    DATA_AI = "data_ai"
    DEVOPS = "devops"
    QA_TESTING = "qa_testing"
    SECURITY = "security"


class TaskStatus(Enum):
    """Task execution status"""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


@dataclass
class AgentTask:
    """Represents a task assigned to an agent"""

    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    status: TaskStatus = TaskStatus.PENDING
    assigned_to: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentMetadata:
    """Agent metadata and capabilities"""

    agent_id: str
    name: str
    role: AgentRole
    experience_years: int
    technologies: List[str]
    specializations: List[str]
    pros: List[str]
    cons: List[str]
    max_concurrent_tasks: int = 3
    quality_gate_required: bool = True
    version: str = "1.0.0"


class BaseAgent(ABC):
    """
    Base class for all expert agents in the system.

    All agents must:
    1. Define their metadata (expertise, technologies, pros/cons)
    2. Implement execute_task() for task execution
    3. Implement validate_output() for self-validation
    4. Use standard logging and error handling
    """

    def __init__(self, metadata: AgentMetadata):
        self.metadata = metadata
        self.logger = self._setup_logger()
        self.current_tasks: List[AgentTask] = []
        self.completed_tasks: List[AgentTask] = []
        self.tools: Dict[str, Callable] = {}
        self.state: Dict[str, Any] = {}

    def _setup_logger(self) -> logging.Logger:
        """Setup agent-specific logger"""
        logger = logging.getLogger(f"agent.{self.metadata.agent_id}")
        logger.setLevel(logging.INFO)

        # Console handler
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            f"[{self.metadata.agent_id}] %(asctime)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        return logger

    def register_tool(self, name: str, func: Callable, description: str = ""):
        """Register a tool that this agent can use"""
        self.tools[name] = {"function": func, "description": description}
        self.logger.info(f"Registered tool: {name}")

    def can_accept_task(self) -> bool:
        """Check if agent can accept more tasks"""
        active_tasks = [t for t in self.current_tasks if t.status == TaskStatus.IN_PROGRESS]
        return len(active_tasks) < self.metadata.max_concurrent_tasks

    def assign_task(self, task: AgentTask) -> bool:
        """Assign a task to this agent"""
        if not self.can_accept_task():
            self.logger.warning(f"Cannot accept task {task.task_id} - at capacity")
            return False

        task.assigned_to = self.metadata.agent_id
        task.status = TaskStatus.PENDING
        self.current_tasks.append(task)
        self.logger.info(f"Accepted task: {task.title} ({task.task_id})")
        return True

    @abstractmethod
    def execute_task(self, task: AgentTask) -> Dict[str, Any]:
        """
        Execute the assigned task.

        Must be implemented by each agent with their specific logic.
        Should return a dictionary with results.

        Example:
        {
            'status': 'success',
            'output': {...},
            'artifacts': ['path/to/file1.py', 'path/to/file2.py'],
            'validation_passed': True
        }
        """
        pass

    @abstractmethod
    def validate_output(self, task: AgentTask, output: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate the output before returning.

        Returns:
            (validation_passed: bool, errors: List[str])

        Example checks:
        - Code compiles (no syntax errors)
        - Tests pass
        - Security scan clean
        - Meets quality standards
        """
        pass

    def run_task(self, task: AgentTask) -> AgentTask:
        """
        Main task execution workflow with validation.

        1. Mark task as in-progress
        2. Execute task
        3. Validate output
        4. Mark as completed or failed
        5. Return updated task
        """
        try:
            # Update status
            task.status = TaskStatus.IN_PROGRESS
            self.logger.info(f"Starting task: {task.title}")

            # Execute
            output = self.execute_task(task)

            # Validate
            if self.metadata.quality_gate_required:
                validation_passed, errors = self.validate_output(task, output)

                if not validation_passed:
                    task.status = TaskStatus.FAILED
                    task.error = f"Validation failed: {', '.join(errors)}"
                    self.logger.error(f"Task validation failed: {errors}")
                    return task

            # Success
            task.status = TaskStatus.COMPLETED
            task.result = output
            task.completed_at = datetime.now()
            self.logger.info(f"Task completed: {task.title}")

            # Move to completed
            self.current_tasks.remove(task)
            self.completed_tasks.append(task)

        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            self.logger.error(f"Task execution failed: {e}", exc_info=True)

        return task

    def get_status_report(self) -> Dict[str, Any]:
        """Generate status report for this agent"""
        return {
            "agent_id": self.metadata.agent_id,
            "name": self.metadata.name,
            "role": self.metadata.role.value,
            "current_tasks": len(self.current_tasks),
            "completed_tasks": len(self.completed_tasks),
            "can_accept_tasks": self.can_accept_task(),
            "active_tasks": [
                {"task_id": t.task_id, "title": t.title, "status": t.status.value}
                for t in self.current_tasks
            ],
        }

    def get_expertise_summary(self) -> Dict[str, Any]:
        """Get agent expertise and capabilities"""
        return {
            "agent_id": self.metadata.agent_id,
            "name": self.metadata.name,
            "role": self.metadata.role.value,
            "experience_years": self.metadata.experience_years,
            "technologies": self.metadata.technologies,
            "specializations": self.metadata.specializations,
            "pros": self.metadata.pros,
            "cons": self.metadata.cons,
            "tools_available": list(self.tools.keys()),
        }

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.metadata.agent_id} name={self.metadata.name}>"

    # ============================================================================
    # SKILL METHODS (Task 018 - Agent OS Integration)
    # ============================================================================

    def generate_mcq(
        self,
        topic: str,
        difficulty: str = "medium",
        count: int = 10,
        specialty: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate multiple choice questions for a given medical topic.

        Args:
            topic: Medical topic (e.g., "acute coronary syndrome", "asthma management")
            difficulty: Question difficulty level ("easy", "medium", "hard")
            count: Number of MCQs to generate (default: 10)
            specialty: Medical specialty ("cardiology", "respiratory", "psychiatry")

        Returns:
            Dict containing:
            - mcqs: List of generated MCQ objects
            - citations: RAG citations (>0.70 confidence)
            - metadata: Generation stats (time, model, quality score)

        Raises:
            ValueError: If difficulty not in ['easy', 'medium', 'hard']
            RuntimeError: If RAG system unavailable

        Example:
            >>> agent.generate_mcq("atrial fibrillation", "medium", 5, "cardiology")
            {
                'mcqs': [...],
                'citations': [...],
                'metadata': {'generation_time_ms': 2340, 'quality_score': 0.92}
            }
        """
        if difficulty not in ["easy", "medium", "hard"]:
            raise ValueError(f"Invalid difficulty: {difficulty}. Must be easy, medium, or hard.")

        self.logger.info(f"Generating {count} {difficulty} MCQs for topic: {topic}")

        # Check if MCQ generation tool is registered
        if "generate_mcq" not in self.tools:
            raise RuntimeError("MCQ generation tool not registered. Register with register_tool().")

        # Call the registered tool
        result = self.tools["generate_mcq"]["function"](
            topic=topic, difficulty=difficulty, count=count, specialty=specialty
        )

        self.logger.info(f"Generated {len(result.get('mcqs', []))} MCQs successfully")
        return result

    def validate_citation(self, citation: Dict[str, Any], source: str = "qdrant") -> Dict[str, Any]:
        """
        Validate a RAG citation meets quality standards.

        Args:
            citation: Citation object with keys:
                - source_title: Title of source document
                - page_number: Page reference
                - confidence_score: RAG confidence (0.0-1.0)
                - chunk_text: Excerpt from source
            source: Citation source system ("qdrant", "neo4j", "statpearls")

        Returns:
            Dict containing:
            - valid: Boolean indicating if citation passes validation
            - errors: List of validation errors (if any)
            - warnings: List of warnings (e.g., low confidence)
            - metadata: Validation details

        Validation Rules:
            - confidence_score >= 0.70 (CRITICAL)
            - page_number present and valid
            - source_title matches Australian guidelines (eTG, AMH, PBS)
            - chunk_text not empty
            - No placeholder content

        Example:
            >>> agent.validate_citation({
            ...     'source_title': 'eTG: Cardiovascular',
            ...     'page_number': 42,
            ...     'confidence_score': 0.85,
            ...     'chunk_text': 'Aspirin 300mg loading dose...'
            ... })
            {
                'valid': True,
                'errors': [],
                'warnings': [],
                'metadata': {'validation_time_ms': 15}
            }
        """
        self.logger.info(f"Validating citation from source: {source}")

        errors = []
        warnings = []

        # Rule 1: Confidence threshold
        confidence = citation.get("confidence_score", 0.0)
        if confidence < 0.70:
            errors.append(f"Confidence score {confidence:.2f} below minimum threshold 0.70")

        # Rule 2: Page number
        if "page_number" not in citation or not citation["page_number"]:
            errors.append("Missing page_number (required for citations)")

        # Rule 3: Source title validation
        source_title = citation.get("source_title", "")
        australian_sources = ["etg", "amh", "pbs", "therapeutic guidelines", "ahpra"]
        if not any(src in source_title.lower() for src in australian_sources):
            warnings.append(f"Source '{source_title}' may not be Australian-specific")

        # Rule 4: Chunk text not empty
        chunk_text = citation.get("chunk_text", "").strip()
        if not chunk_text:
            errors.append("chunk_text is empty")
        elif len(chunk_text) < 50:
            warnings.append(f"chunk_text very short ({len(chunk_text)} chars) - may lack context")

        # Rule 5: No placeholder content
        placeholders = ["[PLACEHOLDER]", "Option A", "Option B", "Clinical scenario for"]
        if any(ph in chunk_text for ph in placeholders):
            errors.append(f"Placeholder content detected in chunk_text")

        valid = len(errors) == 0

        result = {
            "valid": valid,
            "errors": errors,
            "warnings": warnings,
            "metadata": {
                "confidence_score": confidence,
                "source": source,
                "validation_rules_checked": 5,
            },
        }

        if valid:
            self.logger.info("Citation validation passed")
        else:
            self.logger.warning(f"Citation validation failed: {errors}")

        return result

    def analyze_performance(self, user_id: str, time_period: str = "month") -> Dict[str, Any]:
        """
        Analyze user performance and identify weak areas.

        Args:
            user_id: User's unique identifier
            time_period: Analysis period ("week", "month", "all_time")

        Returns:
            Dict containing:
            - overall_accuracy: Percentage (0.0-100.0)
            - weak_areas: List of topics with <60% accuracy
            - strong_areas: List of topics with >80% accuracy
            - specialty_breakdown: Performance by specialty
            - time_series: Daily/weekly performance trend
            - recommendations: Personalized study recommendations

        Example:
            >>> agent.analyze_performance("user_123", "month")
            {
                'overall_accuracy': 72.5,
                'weak_areas': [
                    {'topic': 'ECG interpretation', 'accuracy': 45.0, 'attempts': 20},
                    {'topic': 'Arrhythmia management', 'accuracy': 58.0, 'attempts': 12}
                ],
                'strong_areas': [
                    {'topic': 'Heart failure', 'accuracy': 92.0, 'attempts': 25}
                ],
                'recommendations': [
                    'Focus on ECG interpretation (20 MCQs recommended)',
                    'Review arrhythmia protocols (eTG Cardiovascular Ch 3)'
                ]
            }
        """
        if time_period not in ["week", "month", "all_time"]:
            raise ValueError(
                f"Invalid time_period: {time_period}. Must be week, month, or all_time."
            )

        self.logger.info(f"Analyzing performance for user {user_id} (period: {time_period})")

        # Check if performance analysis tool is registered
        if "analyze_performance" not in self.tools:
            raise RuntimeError("Performance analysis tool not registered.")

        result = self.tools["analyze_performance"]["function"](
            user_id=user_id, time_period=time_period
        )

        self.logger.info(
            f"Performance analysis complete: {result.get('overall_accuracy', 0):.1f}% accuracy"
        )
        return result

    def create_study_plan(self, user_id: str, target_exam: str, weeks: int = 8) -> Dict[str, Any]:
        """
        Create personalized study plan based on user's weak areas.

        Args:
            user_id: User's unique identifier
            target_exam: Target exam ("icrp_2026", "amc_clinical", "usmle_step_3")
            weeks: Study plan duration in weeks (default: 8)

        Returns:
            Dict containing:
            - plan_id: Unique plan identifier
            - weekly_goals: List of weekly objectives
            - daily_schedule: Recommended daily study activities
            - mcq_targets: Daily MCQ practice targets
            - osce_targets: Weekly OSCE practice targets
            - resources: Recommended readings (eTG chapters, etc.)
            - milestones: Progress checkpoints

        Algorithm:
            1. Analyze current performance (weak areas)
            2. Prioritize topics by exam weight and weakness
            3. Allocate time using spaced repetition
            4. Balance MCQs, OSCEs, revision

        Example:
            >>> agent.create_study_plan("user_123", "amc_clinical", 8)
            {
                'plan_id': 'plan_abc123',
                'weekly_goals': [
                    {
                        'week': 1,
                        'focus_areas': ['Cardiology basics', 'ECG interpretation'],
                        'mcq_count': 70,
                        'osce_count': 3
                    },
                    ...
                ],
                'daily_schedule': {
                    'monday': ['MCQs: 10 cardiology', 'Review: eTG Ch 2'],
                    ...
                }
            }
        """
        self.logger.info(f"Creating {weeks}-week study plan for {target_exam}")

        if "create_study_plan" not in self.tools:
            raise RuntimeError("Study plan tool not registered.")

        result = self.tools["create_study_plan"]["function"](
            user_id=user_id, target_exam=target_exam, weeks=weeks
        )

        self.logger.info(f"Study plan created: {result.get('plan_id', 'unknown')}")
        return result

    def query_knowledge_graph(self, query: str, max_depth: int = 3) -> Dict[str, Any]:
        """
        Query Neo4j knowledge graph for medical knowledge relationships.

        Args:
            query: Natural language query or Cypher query
            max_depth: Maximum relationship traversal depth (1-5)

        Returns:
            Dict containing:
            - nodes: List of matching nodes (diseases, drugs, symptoms)
            - relationships: List of edges (CAUSES, TREATS, CONTRAINDICATES)
            - paths: Shortest paths between concepts
            - confidence: Result confidence score

        Example:
            >>> agent.query_knowledge_graph("What causes atrial fibrillation?", 2)
            {
                'nodes': [
                    {'id': 'disease_af', 'name': 'Atrial Fibrillation', 'type': 'disease'},
                    {'id': 'risk_htn', 'name': 'Hypertension', 'type': 'risk_factor'},
                    {'id': 'risk_chf', 'name': 'Heart Failure', 'type': 'risk_factor'}
                ],
                'relationships': [
                    {'from': 'risk_htn', 'to': 'disease_af', 'type': 'CAUSES', 'weight': 0.85},
                    {'from': 'risk_chf', 'to': 'disease_af', 'type': 'CAUSES', 'weight': 0.78}
                ],
                'confidence': 0.92
            }
        """
        if max_depth < 1 or max_depth > 5:
            raise ValueError("max_depth must be between 1 and 5")

        self.logger.info(f"Querying knowledge graph: '{query}' (depth: {max_depth})")

        if "query_knowledge_graph" not in self.tools:
            raise RuntimeError("Knowledge graph tool not registered.")

        result = self.tools["query_knowledge_graph"]["function"](query=query, max_depth=max_depth)

        self.logger.info(f"Knowledge graph query returned {len(result.get('nodes', []))} nodes")
        return result

    def semantic_search(
        self, query: str, collection: str = "medical_knowledge", top_k: int = 5
    ) -> Dict[str, Any]:
        """
        Perform semantic search on Qdrant vector database.

        Args:
            query: Natural language search query
            collection: Qdrant collection name (default: "medical_knowledge")
            top_k: Number of results to return (1-50)

        Returns:
            Dict containing:
            - results: List of matching chunks with scores
            - query_embedding: Query vector (for debugging)
            - search_time_ms: Query latency
            - cache_hit: Boolean indicating if result was cached

        Vector Search Pipeline:
            1. Generate query embedding (sentence-transformers)
            2. Search Qdrant HNSW index
            3. Filter by confidence threshold (>0.70)
            4. Return top-k results with metadata

        Example:
            >>> agent.semantic_search("management of acute MI", "medical_knowledge", 3)
            {
                'results': [
                    {
                        'chunk_id': 'chunk_12345',
                        'text': 'Acute MI management: Aspirin 300mg, clopidogrel...',
                        'source': 'eTG: Cardiovascular',
                        'page': 156,
                        'confidence': 0.92
                    },
                    {
                        'chunk_id': 'chunk_12346',
                        'text': 'STEMI protocol: Primary PCI within 90 minutes...',
                        'source': 'NHFA Guidelines',
                        'page': 23,
                        'confidence': 0.88
                    }
                ],
                'search_time_ms': 42,
                'cache_hit': False
            }
        """
        if top_k < 1 or top_k > 50:
            raise ValueError("top_k must be between 1 and 50")

        self.logger.info(f"Semantic search: '{query}' (top_k: {top_k}, collection: {collection})")

        if "semantic_search" not in self.tools:
            raise RuntimeError("Semantic search tool not registered.")

        result = self.tools["semantic_search"]["function"](
            query=query, collection=collection, top_k=top_k
        )

        results_count = len(result.get("results", []))
        search_time = result.get("search_time_ms", 0)
        self.logger.info(f"Semantic search returned {results_count} results in {search_time}ms")

        return result
