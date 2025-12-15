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
            f'[{self.metadata.agent_id}] %(asctime)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        return logger

    def register_tool(self, name: str, func: Callable, description: str = ""):
        """Register a tool that this agent can use"""
        self.tools[name] = {
            'function': func,
            'description': description
        }
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
            'agent_id': self.metadata.agent_id,
            'name': self.metadata.name,
            'role': self.metadata.role.value,
            'current_tasks': len(self.current_tasks),
            'completed_tasks': len(self.completed_tasks),
            'can_accept_tasks': self.can_accept_task(),
            'active_tasks': [
                {
                    'task_id': t.task_id,
                    'title': t.title,
                    'status': t.status.value
                }
                for t in self.current_tasks
            ]
        }

    def get_expertise_summary(self) -> Dict[str, Any]:
        """Get agent expertise and capabilities"""
        return {
            'agent_id': self.metadata.agent_id,
            'name': self.metadata.name,
            'role': self.metadata.role.value,
            'experience_years': self.metadata.experience_years,
            'technologies': self.metadata.technologies,
            'specializations': self.metadata.specializations,
            'pros': self.metadata.pros,
            'cons': self.metadata.cons,
            'tools_available': list(self.tools.keys())
        }

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.metadata.agent_id} name={self.metadata.name}>"
