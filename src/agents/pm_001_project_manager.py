#!/usr/bin/env python3
"""
PM-001: Chief Project Manager & Architect
Orchestrates all agents with professional SDLC practices
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import json

from .base_agent import (
    BaseAgent,
    AgentMetadata,
    AgentRole,
    AgentTask,
    TaskStatus
)


@dataclass
class Sprint:
    """Represents a development sprint"""
    sprint_id: str
    sprint_number: int
    start_date: datetime
    end_date: datetime
    goal: str
    tasks: List[AgentTask] = field(default_factory=list)
    status: str = "planned"  # planned, active, completed
    retrospective: Optional[Dict[str, Any]] = None


@dataclass
class ArchitectureDecision:
    """Architecture Decision Record (ADR)"""
    adr_id: str
    title: str
    status: str  # proposed, accepted, rejected, superseded
    context: str
    decision: str
    consequences: Dict[str, List[str]]  # pros, cons
    alternatives: List[Dict[str, str]]
    created_at: datetime
    created_by: str


class ProjectManagerAgent(BaseAgent):
    """
    PM-001: Chief Project Manager & Architect

    Experience: 10+ years in medical software, 5+ years as architect

    Technologies:
    - Project Management: Jira, Linear, Asana, GitHub Projects
    - Architecture: C4 Model, UML, Event Storming, Domain-Driven Design
    - SDLC: Agile/Scrum, Kanban, CI/CD
    - Documentation: Confluence, Notion, ADR, RFC
    - Risk Management: SWOT, FMEA, Dependency Analysis

    Responsibilities:
    1. Sprint Planning & Execution
    2. Architecture Decision Making
    3. Agent Coordination & Task Delegation
    4. Quality Gate Enforcement
    5. Risk Management
    6. SDLC Process Enforcement
    7. Code Review Coordination
    8. Documentation Standards
    9. Stakeholder Communication
    10. Technical Debt Management

    Pros:
    - Ensures system consistency across all components
    - Prevents technical debt through proactive architecture
    - Coordinates complex multi-agent workflows
    - Enforces quality standards (80%+ test coverage, security scans)
    - Long-term vision with short-term execution
    - Risk identification and mitigation

    Cons:
    - Can slow down rapid prototyping phases
    - Documentation overhead in early stages
    - May over-engineer simple features
    - Requires balance between process and agility
    """

    def __init__(self):
        metadata = AgentMetadata(
            agent_id="PM-001",
            name="Chief Project Manager & Architect",
            role=AgentRole.PROJECT_MANAGEMENT,
            experience_years=10,
            technologies=[
                "Jira", "Linear", "GitHub Projects",
                "C4 Model", "UML", "DDD",
                "Agile/Scrum", "Kanban",
                "Confluence", "ADR", "RFC"
            ],
            specializations=[
                "Medical software architecture",
                "HIPAA compliance",
                "Multi-agent system coordination",
                "SDLC process design",
                "Risk management",
                "Technical debt prevention"
            ],
            pros=[
                "Ensures system consistency across components",
                "Prevents technical debt through proactive architecture",
                "Coordinates complex multi-agent workflows",
                "Enforces quality standards (80%+ coverage)",
                "Long-term vision with short-term execution",
                "Risk identification and mitigation"
            ],
            cons=[
                "Can slow down rapid prototyping",
                "Documentation overhead in early stages",
                "May over-engineer simple features",
                "Requires balance between process and agility"
            ],
            max_concurrent_tasks=10,
            quality_gate_required=True
        )
        super().__init__(metadata)

        # PM-specific state
        self.sprints: List[Sprint] = []
        self.current_sprint: Optional[Sprint] = None
        self.architecture_decisions: List[ArchitectureDecision] = []
        self.registered_agents: Dict[str, BaseAgent] = {}
        self.quality_gates: Dict[str, bool] = {
            'code_review': True,
            'unit_tests': True,
            'integration_tests': True,
            'security_scan': True,
            'performance_test': False,  # Optional for now
            'documentation': True
        }

        # Register PM tools
        self._register_pm_tools()

    def _register_pm_tools(self):
        """Register project management tools"""
        self.register_tool(
            "create_sprint",
            self.create_sprint,
            "Create a new 2-week development sprint"
        )
        self.register_tool(
            "assign_task_to_agent",
            self.assign_task_to_agent,
            "Assign a task to a specific expert agent"
        )
        self.register_tool(
            "create_architecture_decision",
            self.create_architecture_decision,
            "Document an architecture decision (ADR)"
        )
        self.register_tool(
            "run_quality_gates",
            self.run_quality_gates,
            "Run all quality gates for a deliverable"
        )
        self.register_tool(
            "generate_sprint_report",
            self.generate_sprint_report,
            "Generate sprint completion report"
        )

    def register_agent(self, agent: BaseAgent):
        """Register an expert agent for task delegation"""
        self.registered_agents[agent.metadata.agent_id] = agent
        self.logger.info(f"Registered agent: {agent.metadata.name} ({agent.metadata.agent_id})")

    def create_sprint(
        self,
        goal: str,
        duration_weeks: int = 2,
        tasks: Optional[List[Dict[str, Any]]] = None
    ) -> Sprint:
        """Create a new development sprint"""
        sprint_number = len(self.sprints) + 1
        start_date = datetime.now()
        end_date = start_date + timedelta(weeks=duration_weeks)

        sprint = Sprint(
            sprint_id=f"SPRINT-{sprint_number:03d}",
            sprint_number=sprint_number,
            start_date=start_date,
            end_date=end_date,
            goal=goal,
            tasks=[]
        )

        # Create tasks if provided
        if tasks:
            for task_data in tasks:
                task = AgentTask(
                    title=task_data['title'],
                    description=task_data['description'],
                    metadata={'sprint_id': sprint.sprint_id}
                )
                sprint.tasks.append(task)

        self.sprints.append(sprint)
        self.current_sprint = sprint
        sprint.status = "active"

        self.logger.info(f"Created {sprint.sprint_id}: {goal}")
        return sprint

    def assign_task_to_agent(
        self,
        task: AgentTask,
        agent_id: str,
        force: bool = False
    ) -> bool:
        """
        Assign a task to a specific agent.

        Args:
            task: The task to assign
            agent_id: Target agent ID
            force: Override capacity checks (use with caution)

        Returns:
            True if assignment successful
        """
        if agent_id not in self.registered_agents:
            self.logger.error(f"Agent {agent_id} not found")
            return False

        agent = self.registered_agents[agent_id]

        # Check capacity
        if not force and not agent.can_accept_task():
            self.logger.warning(f"Agent {agent_id} at capacity")
            return False

        # Assign
        success = agent.assign_task(task)
        if success:
            self.logger.info(f"Assigned task '{task.title}' to {agent.metadata.name}")

        return success

    def create_architecture_decision(
        self,
        title: str,
        context: str,
        decision: str,
        pros: List[str],
        cons: List[str],
        alternatives: List[Dict[str, str]]
    ) -> ArchitectureDecision:
        """
        Create an Architecture Decision Record (ADR).

        Example:
            pm.create_architecture_decision(
                title="Use FastAPI for Backend",
                context="Need high-performance async API for medical platform",
                decision="Selected FastAPI over Django and Flask",
                pros=["3,000+ RPS", "Async-first", "Auto OpenAPI docs"],
                cons=["No built-in admin", "Smaller ecosystem"],
                alternatives=[
                    {"name": "Django", "reason": "Too slow (500 RPS)"},
                    {"name": "Flask", "reason": "Not async-first"}
                ]
            )
        """
        adr = ArchitectureDecision(
            adr_id=f"ADR-{len(self.architecture_decisions) + 1:03d}",
            title=title,
            status="proposed",
            context=context,
            decision=decision,
            consequences={"pros": pros, "cons": cons},
            alternatives=alternatives,
            created_at=datetime.now(),
            created_by=self.metadata.agent_id
        )

        self.architecture_decisions.append(adr)
        self.logger.info(f"Created {adr.adr_id}: {title}")
        return adr

    def run_quality_gates(self, deliverable: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Run all quality gates for a deliverable.

        Quality Gates:
        1. Code Review: At least 1 peer approval
        2. Unit Tests: 80%+ coverage
        3. Integration Tests: All critical paths tested
        4. Security Scan: No high/critical vulnerabilities
        5. Performance Test: Meets SLA targets (optional)
        6. Documentation: All public APIs documented

        Returns:
            (passed: bool, failed_gates: List[str])
        """
        failed_gates = []

        # Code Review
        if self.quality_gates['code_review']:
            if not deliverable.get('code_review_approved', False):
                failed_gates.append("Code review not approved")

        # Unit Tests
        if self.quality_gates['unit_tests']:
            coverage = deliverable.get('test_coverage', 0)
            if coverage < 80:
                failed_gates.append(f"Test coverage {coverage}% < 80%")

        # Integration Tests
        if self.quality_gates['integration_tests']:
            if not deliverable.get('integration_tests_passed', False):
                failed_gates.append("Integration tests failed")

        # Security Scan
        if self.quality_gates['security_scan']:
            vulnerabilities = deliverable.get('security_vulnerabilities', [])
            high_critical = [v for v in vulnerabilities if v['severity'] in ['high', 'critical']]
            if high_critical:
                failed_gates.append(f"Found {len(high_critical)} high/critical vulnerabilities")

        # Documentation
        if self.quality_gates['documentation']:
            if not deliverable.get('documentation_complete', False):
                failed_gates.append("Documentation incomplete")

        passed = len(failed_gates) == 0
        return passed, failed_gates

    def generate_sprint_report(self, sprint: Optional[Sprint] = None) -> Dict[str, Any]:
        """Generate sprint completion report"""
        if sprint is None:
            sprint = self.current_sprint

        if not sprint:
            return {"error": "No sprint to report on"}

        total_tasks = len(sprint.tasks)
        completed_tasks = [t for t in sprint.tasks if t.status == TaskStatus.COMPLETED]
        failed_tasks = [t for t in sprint.tasks if t.status == TaskStatus.FAILED]
        in_progress_tasks = [t for t in sprint.tasks if t.status == TaskStatus.IN_PROGRESS]

        report = {
            'sprint_id': sprint.sprint_id,
            'goal': sprint.goal,
            'start_date': sprint.start_date.isoformat(),
            'end_date': sprint.end_date.isoformat(),
            'total_tasks': total_tasks,
            'completed': len(completed_tasks),
            'failed': len(failed_tasks),
            'in_progress': len(in_progress_tasks),
            'completion_rate': len(completed_tasks) / total_tasks * 100 if total_tasks > 0 else 0,
            'tasks_by_status': {
                'completed': [t.title for t in completed_tasks],
                'failed': [t.title for t in failed_tasks],
                'in_progress': [t.title for t in in_progress_tasks]
            }
        }

        return report

    def execute_task(self, task: AgentTask) -> Dict[str, Any]:
        """
        Execute PM-specific tasks like sprint planning, coordination, etc.

        PM Tasks:
        - Sprint planning
        - Architecture decisions
        - Agent coordination
        - Quality gate enforcement
        - Risk management
        """
        task_type = task.metadata.get('type', 'unknown')

        if task_type == 'sprint_planning':
            sprint = self.create_sprint(
                goal=task.metadata['goal'],
                tasks=task.metadata.get('tasks', [])
            )
            return {
                'status': 'success',
                'sprint': sprint,
                'message': f"Created {sprint.sprint_id}"
            }

        elif task_type == 'architecture_decision':
            adr = self.create_architecture_decision(
                title=task.metadata['title'],
                context=task.metadata['context'],
                decision=task.metadata['decision'],
                pros=task.metadata['pros'],
                cons=task.metadata['cons'],
                alternatives=task.metadata.get('alternatives', [])
            )
            return {
                'status': 'success',
                'adr': adr,
                'message': f"Created {adr.adr_id}"
            }

        elif task_type == 'coordinate_agents':
            # Coordinate multiple agents for complex workflow
            workflow = task.metadata['workflow']
            results = []

            for step in workflow:
                agent_id = step['agent_id']
                agent_task = AgentTask(
                    title=step['task_title'],
                    description=step['task_description']
                )

                success = self.assign_task_to_agent(agent_task, agent_id)
                results.append({
                    'agent_id': agent_id,
                    'task_id': agent_task.task_id,
                    'assigned': success
                })

            return {
                'status': 'success',
                'workflow_results': results
            }

        else:
            return {
                'status': 'error',
                'message': f"Unknown PM task type: {task_type}"
            }

    def validate_output(self, task: AgentTask, output: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate PM task output.

        PM validation ensures:
        - Sprint plans are realistic
        - Architecture decisions are well-documented
        - Task assignments are balanced
        """
        errors = []

        task_type = task.metadata.get('type', 'unknown')

        if task_type == 'sprint_planning':
            sprint = output.get('sprint')
            if not sprint:
                errors.append("No sprint created")
            elif len(sprint.tasks) == 0:
                errors.append("Sprint has no tasks")

        elif task_type == 'architecture_decision':
            adr = output.get('adr')
            if not adr:
                errors.append("No ADR created")
            elif len(adr.consequences['pros']) == 0:
                errors.append("ADR has no pros listed")
            elif len(adr.alternatives) == 0:
                errors.append("ADR has no alternatives considered")

        return len(errors) == 0, errors

    def get_project_status(self) -> Dict[str, Any]:
        """Get comprehensive project status"""
        return {
            'current_sprint': self.current_sprint.sprint_id if self.current_sprint else None,
            'total_sprints': len(self.sprints),
            'registered_agents': len(self.registered_agents),
            'architecture_decisions': len(self.architecture_decisions),
            'quality_gates': self.quality_gates,
            'agent_status': {
                agent_id: agent.get_status_report()
                for agent_id, agent in self.registered_agents.items()
            }
        }
