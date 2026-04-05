"""
Mock Exam Orchestration Service

Handles 16-station AMC OSCE mock exam logic:
- Auto-persona selection (balanced distribution)
- Station progression state machine
- Score aggregation and pass/fail calculation
"""

from src.services.mock_exam.orchestrator import MockExamOrchestrator

__all__ = ["MockExamOrchestrator"]
