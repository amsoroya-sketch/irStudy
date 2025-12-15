# Expert Agent System
## Multi-Agent Architecture for Medical Education AI

**Version:** 1.0.0
**Total Agents:** 46
**Orchestration:** LangGraph

---

## Overview

This system provides 46 expert agents organized into 6 categories, all coordinated by a central Project Manager agent (PM-001). Each agent has 10+ years equivalent experience in their domain and follows professional SDLC practices.

### Agent Categories

1. **Project Management (1):** PM-001 Chief Project Manager & Architect
2. **Software Development (12):** DEV-001 to DEV-012
3. **Data & AI Engineering (8):** AI-001 to AI-008
4. **DevOps & Infrastructure (6):** DEVOPS-001 to DEVOPS-006
5. **Quality Assurance (4):** QA-001 to QA-004
6. **Medical Experts (15):** MED-001 to MED-015

---

## Quick Start

### 1. Initialize Project Manager

```python
from src.agents import ProjectManagerAgent

# Create PM-001 (Chief coordinator)
pm = ProjectManagerAgent()

# Check PM status
status = pm.get_project_status()
print(status)
```

### 2. Register Expert Agents

```python
from src.agents.base_agent import BaseAgent, AgentMetadata, AgentRole

# Example: Create a backend developer agent
class BackendAgent(BaseAgent):
    def __init__(self):
        metadata = AgentMetadata(
            agent_id="DEV-001",
            name="Senior Backend Architect",
            role=AgentRole.BACKEND_DEV,
            experience_years=10,
            technologies=["FastAPI", "SQLAlchemy", "PostgreSQL"],
            specializations=["API design", "Database architecture"],
            pros=["Async-first", "High performance"],
            cons=["No built-in admin"]
        )
        super().__init__(metadata)

    def execute_task(self, task):
        # Implementation
        return {"status": "success", "output": {...}}

    def validate_output(self, task, output):
        # Validation logic
        return True, []

# Register with PM
backend_dev = BackendAgent()
pm.register_agent(backend_dev)
```

### 3. Use Pre-built Workflows

```python
from src.agents.workflows import MCQGenerationWorkflow

# Initialize agents (simplified)
rag_agent = ...  # AI-001 RAG System
medical_agents = {"cardiology": ...}  # MED-001 Cardiology Expert
qa_agent = ...  # QA-001 Medical QA
db_agent = ...  # DEV-004 Database

# Create workflow
mcq_workflow = MCQGenerationWorkflow(
    pm_agent=pm,
    rag_agent=rag_agent,
    medical_agents=medical_agents,
    qa_agent=qa_agent,
    db_agent=db_agent
)

# Run workflow
result = mcq_workflow.run(
    task_description="Generate 10 cardiology MCQs about acute coronary syndrome",
    specialty="cardiology",
    topic="acute_coronary_syndrome"
)

print(result['final_output'])
# {
#     'question': {...},
#     'validation': {...},
#     'storage': {...}
# }
```

---

## Architecture

### Agent Hierarchy

```
User
  ↓
PM-001 (Project Manager) ← Central Coordinator
  ├─> DEV-001 to DEV-012 (Software Development)
  ├─> AI-001 to AI-008 (Data & AI)
  ├─> DEVOPS-001 to DEVOPS-006 (DevOps)
  ├─> QA-001 to QA-004 (Quality Assurance)
  └─> MED-001 to MED-015 (Medical Experts)
```

### Agent Communication

Agents communicate through:
1. **Shared State:** LangGraph `AgentState` (see `workflows/orchestration.py`)
2. **Message Passing:** Structured messages between agents
3. **Task Queue:** PM-001 manages task queue and delegation
4. **Results Aggregation:** PM-001 collects and aggregates results

### Workflow Patterns

#### 1. Sequential Workflow
```
Agent A → Agent B → Agent C → Result
```
Example: PDF Extract → Chunk → Embed → Index

#### 2. Parallel Workflow
```
      ├─> Agent A ─>┤
PM ─> ├─> Agent B ─>├─> Aggregate → Result
      └─> Agent C ─>┘
```
Example: Backend + Frontend + Database (parallel development)

#### 3. Conditional Workflow
```
Agent A → Decision → [Pass: Agent B] or [Fail: Agent C or Retry]
```
Example: QA Review → Pass: Store, Fail: Retry Generation

#### 4. Hierarchical Workflow
```
PM → Domain Expert → Specialist Agents → Aggregate → PM
```
Example: PM → Medical Expert → RAG + QA + Database → PM

---

## Agent Base Class

All agents inherit from `BaseAgent`:

```python
from src.agents import BaseAgent, AgentMetadata, AgentTask

class MyCustomAgent(BaseAgent):
    def __init__(self):
        metadata = AgentMetadata(
            agent_id="CUSTOM-001",
            name="My Custom Agent",
            role=AgentRole.BACKEND_DEV,  # Choose appropriate role
            experience_years=10,
            technologies=["Tech1", "Tech2"],
            specializations=["Spec1", "Spec2"],
            pros=["Pro1", "Pro2"],
            cons=["Con1", "Con2"],
            max_concurrent_tasks=3,  # How many tasks this agent can handle
            quality_gate_required=True  # Enforce validation
        )
        super().__init__(metadata)

        # Register custom tools
        self.register_tool(
            name="my_tool",
            func=self.my_tool_function,
            description="What this tool does"
        )

    def execute_task(self, task: AgentTask) -> Dict[str, Any]:
        """
        Execute the assigned task.

        Args:
            task: AgentTask with description, metadata, etc.

        Returns:
            Dictionary with results:
            {
                'status': 'success',
                'output': {...},
                'artifacts': ['file1.py', 'file2.py'],
                'validation_passed': True
            }
        """
        # Your implementation here
        result = {
            'status': 'success',
            'output': {'key': 'value'},
            'artifacts': [],
            'validation_passed': True
        }
        return result

    def validate_output(self, task: AgentTask, output: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate the output before returning.

        Args:
            task: The original task
            output: The output from execute_task()

        Returns:
            (validation_passed: bool, errors: List[str])

        Example:
            if output['status'] != 'success':
                return False, ['Task execution failed']

            if 'output' not in output:
                return False, ['Missing output key']

            return True, []
        """
        errors = []

        # Your validation logic here
        if output.get('status') != 'success':
            errors.append('Task failed')

        return len(errors) == 0, errors

    def my_tool_function(self, arg1: str, arg2: int) -> Dict[str, Any]:
        """Custom tool implementation"""
        return {'result': f'{arg1}-{arg2}'}
```

---

## LangGraph Workflows

### Creating Custom Workflows

```python
from langgraph.graph import StateGraph, END
from src.agents.workflows import AgentState, WorkflowStatus

class MyCustomWorkflow:
    def __init__(self, pm_agent, agent_a, agent_b):
        self.pm_agent = pm_agent
        self.agent_a = agent_a
        self.agent_b = agent_b

        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build LangGraph workflow"""
        workflow = StateGraph(AgentState)

        # Define nodes (steps in workflow)
        workflow.add_node("step_1", self.step_1_function)
        workflow.add_node("step_2", self.step_2_function)
        workflow.add_node("step_3", self.step_3_function)

        # Define edges (flow)
        workflow.set_entry_point("step_1")
        workflow.add_edge("step_1", "step_2")
        workflow.add_edge("step_2", "step_3")
        workflow.add_edge("step_3", END)

        return workflow.compile()

    def step_1_function(self, state: AgentState) -> AgentState:
        """First step in workflow"""
        print("Executing step 1...")

        # Update state
        state['results']['step_1'] = {'data': 'from step 1'}
        state['current_agent'] = 'agent_a'

        return state

    def step_2_function(self, state: AgentState) -> AgentState:
        """Second step in workflow"""
        print("Executing step 2...")

        # Use results from step 1
        step_1_data = state['results']['step_1']

        state['results']['step_2'] = {'data': 'from step 2'}

        return state

    def step_3_function(self, state: AgentState) -> AgentState:
        """Final step in workflow"""
        print("Executing step 3...")

        state['status'] = WorkflowStatus.COMPLETED
        state['final_output'] = {
            'step_1': state['results']['step_1'],
            'step_2': state['results']['step_2'],
            'step_3': {'data': 'final result'}
        }

        return state

    def run(self, task_description: str) -> Dict[str, Any]:
        """Execute the workflow"""
        initial_state: AgentState = {
            'task_id': 'CUSTOM-001',
            'task_description': task_description,
            'task_type': 'custom',
            'messages': [],
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
```

### Conditional Edges

```python
from langgraph.graph import StateGraph, END

workflow = StateGraph(AgentState)

workflow.add_node("step_1", step_1_func)
workflow.add_node("step_2_success", step_2_success_func)
workflow.add_node("step_2_failure", step_2_failure_func)

workflow.set_entry_point("step_1")

# Conditional edge: go to different nodes based on state
workflow.add_conditional_edges(
    "step_1",
    lambda state: "success" if state['results']['step_1']['passed'] else "failure",
    {
        "success": "step_2_success",
        "failure": "step_2_failure"
    }
)

workflow.add_edge("step_2_success", END)
workflow.add_edge("step_2_failure", END)
```

---

## Quality Gates

PM-001 enforces the following quality gates (configurable):

```python
pm = ProjectManagerAgent()

# Default quality gates
pm.quality_gates = {
    'code_review': True,          # At least 1 peer approval
    'unit_tests': True,            # 80%+ coverage
    'integration_tests': True,     # All critical paths tested
    'security_scan': True,         # No high/critical vulnerabilities
    'performance_test': False,     # Optional (set True for critical services)
    'documentation': True          # All public APIs documented
}

# Run quality gates on deliverable
deliverable = {
    'code_review_approved': True,
    'test_coverage': 85,
    'integration_tests_passed': True,
    'security_vulnerabilities': [],
    'documentation_complete': True
}

passed, failed_gates = pm.run_quality_gates(deliverable)

if passed:
    print("✓ All quality gates passed!")
else:
    print(f"✗ Failed gates: {failed_gates}")
```

---

## Sprint Management

```python
from src.agents import ProjectManagerAgent

pm = ProjectManagerAgent()

# Create a 2-week sprint
sprint = pm.create_sprint(
    goal="Build real-time quiz feature",
    duration_weeks=2,
    tasks=[
        {
            'title': 'Implement WebSocket backend',
            'description': 'Create WebSocket endpoints for real-time quiz'
        },
        {
            'title': 'Build real-time frontend',
            'description': 'React components with WebSocket client'
        },
        {
            'title': 'E2E testing',
            'description': 'Playwright tests for real-time features'
        }
    ]
)

print(f"Created: {sprint.sprint_id}")
print(f"Goal: {sprint.goal}")
print(f"Tasks: {len(sprint.tasks)}")

# Assign tasks to agents
for task in sprint.tasks:
    if 'backend' in task.title.lower():
        pm.assign_task_to_agent(task, agent_id='DEV-001')
    elif 'frontend' in task.title.lower():
        pm.assign_task_to_agent(task, agent_id='DEV-002')
    elif 'testing' in task.title.lower():
        pm.assign_task_to_agent(task, agent_id='QA-002')

# Generate sprint report
report = pm.generate_sprint_report(sprint)
print(f"Completion: {report['completion_rate']:.1f}%")
```

---

## Architecture Decision Records (ADR)

```python
from src.agents import ProjectManagerAgent

pm = ProjectManagerAgent()

# Document architecture decision
adr = pm.create_architecture_decision(
    title="Use FastAPI for Backend",
    context="Need high-performance async API for medical platform with auto-generated OpenAPI documentation",
    decision="Selected FastAPI over Django and Flask",
    pros=[
        "3,000+ RPS (vs Django 500 RPS)",
        "Async-first architecture",
        "Automatic OpenAPI documentation",
        "Type-safe with Pydantic models",
        "Lightweight and fast"
    ],
    cons=[
        "No built-in admin interface (unlike Django)",
        "Smaller ecosystem than Django",
        "Requires understanding of async/await"
    ],
    alternatives=[
        {
            "name": "Django",
            "reason": "Rejected due to slow performance (500 RPS) and synchronous architecture"
        },
        {
            "name": "Flask",
            "reason": "Rejected due to lack of async-first design and manual OpenAPI setup"
        }
    ]
)

print(f"Created: {adr.adr_id}")
print(f"Title: {adr.title}")
print(f"Decision: {adr.decision}")

# Accept the ADR
adr.status = "accepted"
```

---

## Agent Examples

### Example 1: Generate Medical MCQ

```python
from src.agents.workflows import MCQGenerationWorkflow

# Initialize agents
pm = ProjectManagerAgent()
rag_agent = RAGSystemAgent()
cardiology_expert = CardiologyExpertAgent()
qa_agent = MedicalQAAgent()
db_agent = DatabaseAgent()

# Register agents with PM
pm.register_agent(rag_agent)
pm.register_agent(cardiology_expert)
pm.register_agent(qa_agent)
pm.register_agent(db_agent)

# Create workflow
workflow = MCQGenerationWorkflow(
    pm_agent=pm,
    rag_agent=rag_agent,
    medical_agents={'cardiology': cardiology_expert},
    qa_agent=qa_agent,
    db_agent=db_agent
)

# Generate question
result = workflow.run(
    task_description="Generate AMC-style MCQ about acute coronary syndrome management",
    specialty="cardiology",
    topic="acute_coronary_syndrome"
)

# Access result
question = result['final_output']['question']
print(f"Question ID: {question['question_id']}")
print(f"Stem: {question['stem']}")
print(f"Correct Answer: {question['correct_answer']}")
print(f"Validation Passed: {result['final_output']['validation']['overall_pass']}")
```

### Example 2: Deploy New Feature

```python
from src.agents.workflows import DeploymentWorkflow

# Initialize agents
pm = ProjectManagerAgent()
backend_dev = BackendArchitectAgent()
frontend_dev = FrontendArchitectAgent()
e2e_tester = E2ETestingAgent()
devops = CICDEngineerAgent()

# Create workflow
workflow = DeploymentWorkflow(
    pm_agent=pm,
    dev_agents={
        'backend': backend_dev,
        'frontend': frontend_dev
    },
    qa_agents={
        'e2e': e2e_tester
    },
    devops_agent=devops
)

# Deploy
result = workflow.run(
    feature_description="Real-time quiz feature with WebSocket support"
)

# Check deployment
deployment = result['final_output']['deployment']
print(f"Status: {deployment['status']}")
print(f"Environment: {deployment['environment']}")
print(f"Health Check: {deployment['health_check']}")
```

### Example 3: Process Medical Textbooks

```python
from src.agents.workflows import DataProcessingWorkflow

# Initialize agents
pm = ProjectManagerAgent()
etl_agent = ETLEngineerAgent()
rag_agent = RAGSystemAgent()
db_agent = DatabaseAgent()
monitoring = MonitoringAgent()

# Create workflow
workflow = DataProcessingWorkflow(
    pm_agent=pm,
    etl_agent=etl_agent,
    rag_agent=rag_agent,
    db_agent=db_agent,
    monitoring_agent=monitoring
)

# Process PDFs
result = workflow.run(
    pdf_directory="data/pdfs/australian/"
)

# Check results
print(f"Pages Extracted: {result['final_output']['extracted']['pages']:,}")
print(f"Chunks Created: {result['final_output']['chunks']:,}")
print(f"Embeddings: {result['final_output']['embeddings']['chunks']:,}")
print(f"Qdrant Points: {result['final_output']['qdrant']['points']:,}")
print(f"Search Quality: {result['final_output']['validation']['search_quality']:.2%}")
```

---

## Testing Agents

```python
import pytest
from src.agents import BaseAgent, AgentMetadata, AgentTask, AgentRole, TaskStatus

def test_agent_task_execution():
    """Test agent can execute and validate tasks"""

    class TestAgent(BaseAgent):
        def __init__(self):
            metadata = AgentMetadata(
                agent_id="TEST-001",
                name="Test Agent",
                role=AgentRole.BACKEND_DEV,
                experience_years=10,
                technologies=["Python"],
                specializations=["Testing"],
                pros=["Fast"],
                cons=["Limited"]
            )
            super().__init__(metadata)

        def execute_task(self, task):
            return {'status': 'success', 'output': {'result': 42}}

        def validate_output(self, task, output):
            if output['status'] == 'success':
                return True, []
            return False, ['Task failed']

    agent = TestAgent()

    task = AgentTask(
        title="Test Task",
        description="A test task"
    )

    # Assign task
    assert agent.assign_task(task) == True

    # Run task
    completed_task = agent.run_task(task)

    # Verify
    assert completed_task.status == TaskStatus.COMPLETED
    assert completed_task.result['status'] == 'success'
    assert completed_task.result['output']['result'] == 42
```

---

## Monitoring & Logging

All agents log to their own logger:

```python
from src.agents import BaseAgent

class MyAgent(BaseAgent):
    def execute_task(self, task):
        self.logger.info(f"Starting task: {task.title}")

        try:
            # Do work
            result = {'status': 'success'}

            self.logger.info("Task completed successfully")
            return result

        except Exception as e:
            self.logger.error(f"Task failed: {e}", exc_info=True)
            raise
```

Logs format:
```
[AGENT-ID] 2025-12-14 10:30:00 - INFO - Starting task: Generate MCQ
[AGENT-ID] 2025-12-14 10:30:08 - INFO - Task completed successfully
```

---

## Best Practices

### 1. Agent Design
- ✅ **Single Responsibility:** Each agent should have one clear domain of expertise
- ✅ **10+ Years Experience:** Agents should have senior-level knowledge
- ✅ **Validation Required:** Always implement `validate_output()` for quality gates
- ✅ **Tool Registration:** Register all tools the agent can use

### 2. Workflow Design
- ✅ **Clear Steps:** Each node in workflow should have clear responsibility
- ✅ **State Management:** Use `AgentState` for passing data between agents
- ✅ **Error Handling:** Handle failures gracefully (retry, fallback, fail fast)
- ✅ **Quality Gates:** Enforce quality checks at critical points

### 3. PM Coordination
- ✅ **Central Coordinator:** PM-001 should orchestrate all workflows
- ✅ **Sprint Planning:** Use sprints for organizing work (2-week cycles)
- ✅ **ADRs:** Document architecture decisions
- ✅ **Quality Enforcement:** PM runs quality gates before approval

### 4. Testing
- ✅ **Unit Tests:** Test each agent independently
- ✅ **Integration Tests:** Test workflows end-to-end
- ✅ **Mock Agents:** Use mock agents for testing workflows
- ✅ **Quality Metrics:** Track quality gate pass rates

---

## Troubleshooting

### Agent Not Accepting Tasks

```python
agent = MyAgent()

if not agent.can_accept_task():
    print(f"Agent at capacity: {len(agent.current_tasks)}/{agent.metadata.max_concurrent_tasks}")

    # Option 1: Wait for tasks to complete
    # Option 2: Increase max_concurrent_tasks
    agent.metadata.max_concurrent_tasks = 5

    # Option 3: Assign to different agent
```

### Workflow Failing

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Run workflow
result = workflow.run(...)

# Check state
print(f"Status: {result['status']}")
print(f"Failed Quality Gates: {result['quality_checks_failed']}")
print(f"Messages: {result['messages']}")
```

### Quality Gate Failures

```python
deliverable = {...}

passed, failed_gates = pm.run_quality_gates(deliverable)

if not passed:
    for gate in failed_gates:
        print(f"Failed: {gate}")

        # Fix specific issues
        if gate == "Test coverage 75% < 80%":
            # Write more tests
            pass

        if gate.startswith("Found"):
            # Fix security vulnerabilities
            pass
```

---

## Contributing

To add new agents:

1. **Create Agent Class:** Inherit from `BaseAgent`
2. **Implement Methods:** `execute_task()` and `validate_output()`
3. **Register Tools:** Use `self.register_tool()`
4. **Document:** Add to `docs/AGENT_SPECIFICATIONS.md`
5. **Test:** Write unit and integration tests
6. **Register with PM:** `pm.register_agent(new_agent)`

See `base_agent.py` for complete interface definition.

---

## References

- **Agent Specifications:** `docs/AGENT_SPECIFICATIONS.md` (complete 46-agent catalog)
- **Base Agent:** `src/agents/base_agent.py`
- **PM-001:** `src/agents/pm_001_project_manager.py`
- **Workflows:** `src/agents/workflows/orchestration.py`
- **LangGraph Docs:** https://python.langchain.com/docs/langgraph

---

**Last Updated:** December 14, 2025
**Version:** 1.0.0
**Status:** Ready for Implementation
