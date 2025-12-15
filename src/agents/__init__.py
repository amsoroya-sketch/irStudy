"""
Expert Agent System for Medical Education AI

This module provides a complete multi-agent system with 46 expert agents
across project management, software development, AI/data engineering,
DevOps, QA, and medical expertise.

Quick Start:
    from src.agents import ProjectManagerAgent
    from src.agents.workflows import MCQGenerationWorkflow

    pm = ProjectManagerAgent()
    # ... initialize other agents ...

    workflow = MCQGenerationWorkflow(pm, rag, medical_agents, qa, db)
    result = workflow.run("Generate cardiology MCQ", "cardiology", "ACS")

Available Agent Categories:
    - Project Management (1): PM-001
    - Software Development (12): DEV-001 to DEV-012
    - Data & AI Engineering (8): AI-001 to AI-008
    - DevOps & Infrastructure (6): DEVOPS-001 to DEVOPS-006
    - Quality Assurance (4): QA-001 to QA-004
    - Medical Experts (15): MED-001 to MED-015
"""

from .base_agent import (
    BaseAgent,
    AgentMetadata,
    AgentRole,
    AgentTask,
    TaskStatus
)

from .pm_001_project_manager import ProjectManagerAgent

__all__ = [
    # Base classes
    'BaseAgent',
    'AgentMetadata',
    'AgentRole',
    'AgentTask',
    'TaskStatus',

    # Agents
    'ProjectManagerAgent',
]

__version__ = '1.0.0'
