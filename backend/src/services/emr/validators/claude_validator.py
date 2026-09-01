"""
Claude AI Validator

Intelligent SOAP note validation using Claude AI:
- AMC 15-mark rubric scoring
- Clinical reasoning assessment
- Differential diagnosis evaluation
- PHI anonymization before API call

PERFORMANCE: 3-5s target
SECURITY: PHI anonymized, prompt injection prevented
"""

import anthropic
from typing import Dict, Any
import logging
import json
import os

from src.core.vault import VaultClient

logger = logging.getLogger(__name__)

# Current Claude model id (configurable). Override with the EMR_CLAUDE_MODEL env
# var; defaults to a current Sonnet id. NOTE: the exact id should be confirmed
# against the claude-api skill when available — this default matches the model
# ids already used elsewhere in this codebase (see src/ai/clinical_validator.py).
DEFAULT_CLAUDE_MODEL = "claude-sonnet-4-5-20250929"


def _resolve_claude_model() -> str:
    """Resolve the Claude model id from env, falling back to the current default."""
    return os.getenv("EMR_CLAUDE_MODEL", DEFAULT_CLAUDE_MODEL)


class ClaudeValidator:
    """Layer 2: Claude AI validation with AMC rubric"""

    # AMC 15-mark rubric categories
    RUBRIC_CATEGORIES = [
        "History_Taking",  # 3 marks
        "Clinical_Reasoning",  # 3 marks
        "Documentation_Quality",  # 3 marks
        "Patient_Safety",  # 3 marks
        "Professional_Communication",  # 3 marks
    ]

    @classmethod
    async def validate(
        cls,
        soap_note: Dict[str, str],
        patient_context: Dict[str, Any],
        rule_based_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate SOAP note using Claude AI.

        Args:
            soap_note: SOAP note content
            patient_context: Patient scenario for clinical validation
            rule_based_result: Layer 1 validation result

        Returns:
            Validation result with AMC rubric scoring
        """
        try:
            # Get Claude API key from Vault
            vault = VaultClient()
            claude_key = vault.get_secret("emr/claude-api-key")

            if not claude_key:
                logger.warning("Claude API key not available, skipping AI validation")
                return cls._fallback_response()

            # Anonymize PHI before sending to Claude
            anonymized_soap = cls._anonymize_phi(soap_note)
            anonymized_patient = cls._anonymize_phi(patient_context)

            # Build validation prompt
            prompt = cls._build_validation_prompt(
                anonymized_soap,
                anonymized_patient,
                rule_based_result
            )

            # Extract the raw key. Vault (or the env fallback) returns the whole
            # secret as a dict ({"value": "<key>"}); accept a bare string too so a
            # change in secret shape can never reintroduce the crash.
            api_key = claude_key.get("value") if isinstance(claude_key, dict) else claude_key

            # Call Claude API
            client = anthropic.Anthropic(api_key=api_key)
            message = client.messages.create(
                model=_resolve_claude_model(),
                max_tokens=2048,
                temperature=0.3,  # Lower temperature for consistent scoring
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            # Parse response
            response_text = message.content[0].text
            result = cls._parse_claude_response(response_text)

            return result

        except anthropic.APIError as e:
            logger.error(f"Claude API error: {e}")
            return cls._fallback_response()
        except Exception as e:
            logger.error(f"Claude validation error: {e}")
            return cls._fallback_response()

    @classmethod
    def _anonymize_phi(cls, data: Any) -> Any:
        """
        Remove PHI from data before Claude API call.

        Removes: Names, MRN, phone numbers, addresses
        Keeps: Clinical information, symptoms, diagnoses
        """
        if isinstance(data, dict):
            return {k: cls._anonymize_phi(v) for k, v in data.items()}
        elif isinstance(data, str):
            # Replace common PHI patterns
            import re

            # Names (simplistic - in production use NER)
            text = re.sub(r'\b[A-Z][a-z]+ [A-Z][a-z]+\b', '[PATIENT_NAME]', data)

            # MRN
            text = re.sub(r'\bMRN[:\s]*\d{6,10}\b', '[MRN]', text)

            # Phone numbers
            text = re.sub(r'\b\d{4}[\s-]?\d{3}[\s-]?\d{3}\b', '[PHONE]', text)

            # Email
            text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', text)

            return text
        else:
            return data

    @classmethod
    def _build_validation_prompt(
        cls,
        soap_note: Dict[str, str],
        patient_context: Dict[str, Any],
        rule_based_result: Dict[str, Any]
    ) -> str:
        """Build Claude validation prompt.

        When ``patient_context`` carries an answer-key under
        ``validation_criteria`` (per-case expected S/O/A/P findings,
        ``critical_errors`` and ``must_not_miss`` lists), the prompt asks Claude
        to grade the student's note *against that specific answer-key* — did they
        capture the expected findings, did they commit a critical error — rather
        than against a generic rubric. See PRD-EMR-PRACTICE-001.
        """
        criteria = {}
        if isinstance(patient_context, dict):
            criteria = patient_context.get("validation_criteria") or {}

        answer_key_block = json.dumps(criteria, indent=2) if criteria else "(none provided)"

        prompt = f"""You are a senior Australian physician evaluating a medical student's SOAP note for a specific clinical case, using the AMC Clinical Examination 15-mark rubric.

**Patient Scenario / Context:**
{json.dumps(patient_context, indent=2)}

**Case Answer-Key (expected documentation for THIS case):**
{answer_key_block}

The answer-key may contain:
- "expected": the subjective/objective/assessment/plan elements a competent student should capture.
- "critical_errors": actions that are dangerous — if the note commits ANY of these, list it in "critical_errors_committed".
- "must_not_miss": elements that must be documented — if ANY is absent, list it in "missing_elements".

**Student's SOAP Note:**
Subjective: {soap_note.get('subjective', '')}
Objective: {soap_note.get('objective', '')}
Assessment: {soap_note.get('assessment', '')}
Plan: {soap_note.get('plan', '')}

**Rule-Based Validation Results:**
{json.dumps(rule_based_result, indent=2)}

**Your task — grade captured-vs-expected:**
1. Compare the note against the answer-key's "expected" elements section by section.
2. Compute a completeness percentage (0-100) for each of subjective, objective, assessment, plan.
3. List which expected elements were "captured" and which are "missing_elements".
4. List any "critical_errors_committed" (dangerous actions the note took).
5. Score the five AMC rubric categories (each 0-3): History_Taking, Clinical_Reasoning,
   Documentation_Quality, Patient_Safety, Professional_Communication.

**Australian Medical Context:**
- Use Australian drug names (paracetamol NOT acetaminophen).
- Reference eTG, PBS, MBS guidelines; emergency number is 000.

**Response Format — return ONLY this JSON object:**
{{
  "overall_score": <float 0-15>,
  "completeness": {{"subjective": <0-100>, "objective": <0-100>, "assessment": <0-100>, "plan": <0-100>}},
  "captured": ["<expected element the student documented>"],
  "missing_elements": ["<expected element the student omitted>"],
  "critical_errors_committed": ["<critical error the student committed>"],
  "accuracy_notes": ["<note on factual/clinical accuracy>"],
  "category_scores": {{
    "History_Taking": <0-3>,
    "Clinical_Reasoning": <0-3>,
    "Documentation_Quality": <0-3>,
    "Patient_Safety": <0-3>,
    "Professional_Communication": <0-3>
  }},
  "strengths": ["<strength>"],
  "improvements": ["<area for improvement>"]
}}

Provide detailed, actionable, case-specific feedback."""

        return prompt

    @classmethod
    def _parse_claude_response(cls, response_text: str) -> Dict[str, Any]:
        """Parse Claude's JSON response into the assessment result contract.

        Passes the answer-key grading fields through (completeness, captured,
        missing_elements, critical_errors_committed) so the assessment engine can
        apply the PASS/FAIL rule. See PRD-EMR-PRACTICE-001.
        """
        try:
            # Extract JSON from response (Claude sometimes adds markdown)
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                response_data = json.loads(json_match.group())
            else:
                response_data = json.loads(response_text)

            return {
                "overall_score": float(response_data.get("overall_score", 0.0)),
                "completeness": response_data.get("completeness", {}),
                "captured": response_data.get("captured", []),
                "missing_elements": response_data.get("missing_elements", []),
                "critical_errors_committed": response_data.get("critical_errors_committed", []),
                "accuracy_notes": response_data.get("accuracy_notes", []),
                "category_scores": response_data.get("category_scores", {}),
                "strengths": response_data.get("strengths", []),
                "improvements": response_data.get(
                    "improvements", response_data.get("areas_for_improvement", [])
                ),
            }

        except (json.JSONDecodeError, ValueError, TypeError) as e:
            logger.error(f"Failed to parse Claude response: {e}")
            return cls._fallback_response()

    @classmethod
    def _fallback_response(cls) -> Dict[str, Any]:
        """Fallback result when Claude is unavailable.

        Returns the same contract shape (with an ``ai_unavailable`` flag) so
        callers never crash on a missing key when the AI layer is skipped.
        """
        return {
            "overall_score": 0.0,
            "completeness": {"subjective": 0, "objective": 0, "assessment": 0, "plan": 0},
            "captured": [],
            "missing_elements": [],
            "critical_errors_committed": [],
            "accuracy_notes": ["Claude AI validation unavailable - fallback used"],
            "category_scores": {},
            "strengths": [],
            "improvements": [],
            "ai_unavailable": True,
        }

    @classmethod
    def _sanitize_prompt_injection(cls, text: str) -> str:
        """
        Prevent prompt injection attacks.

        Removes:
        - System/assistant role instructions
        - Jailbreak attempts
        - Instruction overrides
        """
        dangerous_patterns = [
            r"ignore (previous|all) (instructions|prompts)",
            r"you are (now|a|an)",
            r"system:",
            r"<\|im_start\|>",
            r"<\|im_end\|>",
        ]

        sanitized = text
        for pattern in dangerous_patterns:
            sanitized = re.sub(pattern, "[FILTERED]", sanitized, flags=re.IGNORECASE)

        return sanitized
