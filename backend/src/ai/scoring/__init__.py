"""
AI OSCE Scoring System

This module provides critical error detection, confidence calculation,
and feedback generation for AI OSCE sessions.

Submodules:
- critical_errors: Detects safety-critical errors that auto-fail sessions
- error_rules: Defines 20+ critical error rules with patterns
- confidence: Calculates scoring confidence (0.0-1.0)
- feedback_generator: Generates structured feedback (strengths, improvements, narrative)
"""

from src.ai.scoring.critical_errors import CriticalErrorDetector

__all__ = ["CriticalErrorDetector"]
