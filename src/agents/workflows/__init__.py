"""
LangGraph Workflows for Multi-Agent Orchestration

Provides pre-built workflows for common multi-agent tasks:
    - MCQ Generation Workflow
    - Deployment Workflow
    - Data Processing Workflow

Usage:
    from src.agents.workflows import MCQGenerationWorkflow

    workflow = MCQGenerationWorkflow(pm, rag, medical_agents, qa, db)
    result = workflow.run(
        task_description="Generate 10 cardiology MCQs about ACS",
        specialty="cardiology",
        topic="acute_coronary_syndrome"
    )
"""

from .orchestration import (
    MCQGenerationWorkflow,
    DeploymentWorkflow,
    DataProcessingWorkflow,
    AgentState,
    WorkflowStatus
)

__all__ = [
    'MCQGenerationWorkflow',
    'DeploymentWorkflow',
    'DataProcessingWorkflow',
    'AgentState',
    'WorkflowStatus',
]
