"""
EMR Validation System - 3-Layer Architecture

LAYERS:
1. Rule-Based Validator (<1s) - Python rules, Australian terminology
2. Claude AI Validator (3-5s) - AMC 15-mark rubric scoring
3. Fallback Validator (when Claude down) - 70% accuracy baseline

AUSTRALIAN MEDICAL COMPLIANCE:
- All validators check Australian terminology
- PBS/MBS code validation
- AHPRA standards compliance
"""

from .rule_based_validator import RuleBasedValidator
from .claude_validator import ClaudeValidator
from .fallback_validator import FallbackValidator

__all__ = ["RuleBasedValidator", "ClaudeValidator", "FallbackValidator"]
