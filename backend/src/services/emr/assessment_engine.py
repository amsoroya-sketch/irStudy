"""
EMR Documentation Assessment Engine (PRD-EMR-PRACTICE-001)

Turns a student's submitted SOAP note into a real, case-specific assessment by
grading it against the case answer-key (``MockPatient.validation_criteria``):
- did the student capture the expected S/O/A/P elements,
- did they commit a critical error,
- did they omit a "must-not-miss" element.

This module is thin wiring on top of the existing ``ClaudeValidator`` (which
owns PHI anonymisation, the Vault-key lookup and the Anthropic call). It does not
fork the validator or add a third validation path.

SECURITY: PHI is anonymised inside ``ClaudeValidator.validate`` before any
Anthropic call; the Claude API key is read from HashiCorp Vault.
"""

from __future__ import annotations

import asyncio
import concurrent.futures
from typing import Any, Dict, Optional

from src.services.emr.validators.claude_validator import ClaudeValidator

# Overall-score threshold (out of 15) for a PASS, absent any critical/must-miss
# failure. Documented as the AMC ~60% competency line.
PASS_THRESHOLD = 9.0


def decide_pass_fail(result: Dict[str, Any], criteria: Optional[Dict[str, Any]]) -> bool:
    """Apply the PASS/FAIL rule.

    Returns ``False`` if the note committed ANY critical error, OR omitted ANY
    "must_not_miss" element from the answer-key. Otherwise the result is a PASS
    only when ``overall_score >= PASS_THRESHOLD``.
    """
    # Any committed critical error is an automatic fail.
    if result.get("critical_errors_committed"):
        return False

    criteria = criteria or {}
    must_not_miss = criteria.get("must_not_miss") or []
    missing = set(result.get("missing_elements") or [])
    for required in must_not_miss:
        if required in missing:
            return False

    return float(result.get("overall_score", 0.0)) >= PASS_THRESHOLD


async def assess_submission(
    soap_note: Dict[str, str],
    validation_criteria: Optional[Dict[str, Any]],
    layers_1_2: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Assess a submitted SOAP note against the case answer-key.

    Args:
        soap_note: the student's final SOAP note (subjective/objective/assessment/plan).
        validation_criteria: the case answer-key from ``MockPatient.validation_criteria``.
        layers_1_2: the rule-based (Layer 1) + Australian-terminology (Layer 2) results,
            threaded to Claude as context and echoed back in the result.

    Returns:
        The assessment result contract (see PRD), including ``pass_fail``.
    """
    criteria = validation_criteria or {}
    layers_1_2 = layers_1_2 or {}

    # ClaudeValidator.validate anonymises PHI, reads the Vault key and calls
    # Claude; on any failure (incl. missing key) it returns the fallback contract.
    claude_result = await ClaudeValidator.validate(
        soap_note,
        {"validation_criteria": criteria},
        layers_1_2,
    )

    result: Dict[str, Any] = {
        "overall_score": float(claude_result.get("overall_score", 0.0)),
        "completeness": claude_result.get("completeness", {}),
        "captured": claude_result.get("captured", []),
        "missing_elements": claude_result.get("missing_elements", []),
        "critical_errors_committed": claude_result.get("critical_errors_committed", []),
        "accuracy_notes": claude_result.get("accuracy_notes", []),
        "category_scores": claude_result.get("category_scores", {}),
        "strengths": claude_result.get("strengths", []),
        "improvements": claude_result.get("improvements", []),
        "layers_1_2": layers_1_2,
    }
    result["pass_fail"] = decide_pass_fail(result, criteria)
    if claude_result.get("ai_unavailable"):
        result["ai_unavailable"] = True
    return result


def assess_submission_sync(
    soap_note: Dict[str, str],
    validation_criteria: Optional[Dict[str, Any]],
    layers_1_2: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Synchronous wrapper around :func:`assess_submission`.

    Safe to call from either a synchronous context or from inside a running
    event loop (e.g. a FastAPI async endpoint): when a loop is already running
    the coroutine is executed on a dedicated worker thread so we never call
    ``asyncio.run`` re-entrantly.
    """
    coro_factory = lambda: assess_submission(soap_note, validation_criteria, layers_1_2)

    try:
        running_loop = asyncio.get_running_loop()
    except RuntimeError:
        running_loop = None

    if running_loop is not None and running_loop.is_running():
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            return pool.submit(lambda: asyncio.run(coro_factory())).result()

    return asyncio.run(coro_factory())
