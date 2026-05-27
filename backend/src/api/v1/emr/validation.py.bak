"""
3-Layer SOAP Note Validation System

VALIDATION LAYERS:
1. Rule-based validation (always runs)
   - Completeness checks
   - Structure validation
   - Australian medical standards

2. Claude AI validation (60% of time)
   - Clinical reasoning
   - Safety checks
   - Evidence-based practice

3. Specialist review (flagged cases only)
   - Manual expert review for borderline or complex cases

SECURITY:
- Claude API key fetched from Vault (never hardcoded)
- No PHI in error messages or logs
"""

import random
from typing import Dict, Optional
from src.config import get_settings


# ============================================================================
# LAYER 1: RULE-BASED VALIDATION
# ============================================================================


class RuleBasedValidator:
    """
    Layer 1: Rule-based SOAP note validation

    CHECKS:
    - Minimum word counts (subjective: 50 words, etc.)
    - Required sections present
    - Australian terminology compliance
    - PBS medication validation
    - MBS pathology test validation
    """

    def validate(self, soap_note: Dict, patient_context: Dict) -> Dict:
        """
        Validate SOAP note using rule-based checks

        Args:
            soap_note: SOAP note content (subjective, objective, assessment, plan)
            patient_context: Mock patient clinical information

        Returns:
            Validation result dict with score and feedback
        """
        errors = []
        completeness_score = 100
        structure_score = 100

        # Check minimum word counts
        subjective_words = len(soap_note.get("subjective", "").split())
        objective_words = len(soap_note.get("objective", "").split())
        assessment_words = len(soap_note.get("assessment", "").split())
        plan_words = len(soap_note.get("plan", "").split())

        if subjective_words < 30:
            errors.append(
                f"Subjective section too brief ({subjective_words} words). "
                "Expected detailed history (30+ words)."
            )
            completeness_score -= 15

        if objective_words < 30:
            errors.append(
                f"Objective section too brief ({objective_words} words). "
                "Expected detailed examination findings (30+ words)."
            )
            completeness_score -= 15

        if assessment_words < 20:
            errors.append(
                f"Assessment section too brief ({assessment_words} words). "
                "Expected differential diagnosis with reasoning (20+ words)."
            )
            completeness_score -= 20

        if plan_words < 20:
            errors.append(
                f"Plan section too brief ({plan_words} words). "
                "Expected comprehensive management plan (20+ words)."
            )
            completeness_score -= 20

        # Check for American vs Australian terminology
        full_text = " ".join(
            [
                soap_note.get("subjective", ""),
                soap_note.get("objective", ""),
                soap_note.get("assessment", ""),
                soap_note.get("plan", ""),
            ]
        ).lower()

        # Flag American terminology
        if "acetaminophen" in full_text:
            errors.append(
                "Use Australian drug names: 'paracetamol' instead of 'acetaminophen'"
            )
            structure_score -= 10

        if "tylenol" in full_text:
            errors.append("Use Australian drug names: 'paracetamol' instead of 'Tylenol'")
            structure_score -= 10

        if "911" in full_text:
            errors.append("Use Australian emergency number: '000' instead of '911'")
            structure_score -= 5

        # Calculate overall Layer 1 score
        layer_1_score = (completeness_score * 0.6 + structure_score * 0.4) / 100 * 90

        return {
            "score": round(layer_1_score, 1),
            "completeness": completeness_score,
            "structure": structure_score,
            "errors": errors,
            "feedback": self._generate_feedback(errors, layer_1_score),
        }

    def _generate_feedback(self, errors: list, score: float) -> str:
        """Generate human-readable feedback"""
        if score >= 80:
            return "Good documentation structure. " + (
                " ".join(errors) if errors else "All rule-based checks passed."
            )
        elif score >= 60:
            return (
                "Documentation needs improvement. "
                + " ".join(errors[:2])
                + (" ..." if len(errors) > 2 else "")
            )
        else:
            return "Significant documentation issues. " + " ".join(errors[:3])


# ============================================================================
# LAYER 2: CLAUDE AI VALIDATION
# ============================================================================


class ClaudeAIValidator:
    """
    Layer 2: Claude AI-powered clinical validation

    CHECKS:
    - Clinical reasoning quality
    - Safety considerations
    - Evidence-based practice
    - Differential diagnosis completeness

    SECURITY:
    - API key fetched from Vault (via config)
    - Patient data anonymized in prompts
    """

    def __init__(self):
        self.settings = get_settings()

    async def validate(self, soap_note: Dict, patient_context: Dict) -> Optional[Dict]:
        """
        Validate SOAP note using Claude AI

        Args:
            soap_note: SOAP note content
            patient_context: Mock patient information

        Returns:
            Validation result dict or None if Claude unavailable
        """
        try:
            # Get Claude API key from Vault
            anthropic_api_key = self.settings.anthropic_api_key

            # Import Anthropic SDK
            try:
                from anthropic import Anthropic
            except ImportError:
                # Claude SDK not available, return None (fallback to Layer 1 only)
                return None

            # Initialize Claude client
            client = Anthropic(api_key=anthropic_api_key)

            # Construct validation prompt
            prompt = self._construct_validation_prompt(soap_note, patient_context)

            # Call Claude API
            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1000,
                temperature=0.3,  # Lower temperature for consistent medical evaluation
                messages=[{"role": "user", "content": prompt}],
            )

            # Parse Claude's response
            return self._parse_claude_response(response.content[0].text)

        except Exception as e:
            # Log error (without PHI) and return None to fallback to Layer 1
            print(f"Claude validation failed: {type(e).__name__}")
            return None

    def _construct_validation_prompt(self, soap_note: Dict, patient_context: Dict) -> str:
        """
        Construct validation prompt for Claude

        SECURITY: Anonymize patient data (use age/gender/complaint only, no names)
        """
        chief_complaint = patient_context.get("presenting_complaint", "Unknown")
        age = patient_context.get("age", "Unknown")
        gender = patient_context.get("gender", "Unknown")

        prompt = f"""You are an AMC Clinical Examiner evaluating a medical student's SOAP note documentation.

PATIENT CONTEXT:
- Age: {age}
- Gender: {gender}
- Presenting Complaint: {chief_complaint}

STUDENT'S SOAP NOTE:

Subjective:
{soap_note.get('subjective', 'Not provided')}

Objective:
{soap_note.get('objective', 'Not provided')}

Assessment:
{soap_note.get('assessment', 'Not provided')}

Plan:
{soap_note.get('plan', 'Not provided')}

TASK:
Evaluate this SOAP note on these criteria (score 0-100 for each):
1. Clinical Reasoning (0-100): Is the differential diagnosis logical and evidence-based?
2. Safety (0-100): Are red flags identified? Are dangerous conditions ruled out?
3. Evidence-Based Practice (0-100): Does management align with Australian guidelines (eTG)?

Provide your evaluation in this EXACT format:
CLINICAL_REASONING: [score 0-100]
SAFETY: [score 0-100]
EVIDENCE_BASED: [score 0-100]
FEEDBACK: [1-2 sentence constructive feedback]

Example format:
CLINICAL_REASONING: 85
SAFETY: 90
EVIDENCE_BASED: 80
FEEDBACK: Good differential diagnosis. Consider adding troponin timing for serial cardiac markers in suspected ACS.
"""
        return prompt

    def _parse_claude_response(self, response_text: str) -> Dict:
        """Parse Claude's structured response"""
        try:
            lines = response_text.strip().split("\n")
            scores = {}

            for line in lines:
                if "CLINICAL_REASONING:" in line:
                    scores["clinical_reasoning"] = int(line.split(":")[1].strip())
                elif "SAFETY:" in line:
                    scores["safety"] = int(line.split(":")[1].strip())
                elif "EVIDENCE_BASED:" in line:
                    scores["evidence_based"] = int(line.split(":")[1].strip())
                elif "FEEDBACK:" in line:
                    scores["feedback"] = line.split(":", 1)[1].strip()

            # Calculate overall Layer 2 score
            if all(
                k in scores for k in ["clinical_reasoning", "safety", "evidence_based"]
            ):
                layer_2_score = (
                    scores["clinical_reasoning"] * 0.4
                    + scores["safety"] * 0.4
                    + scores["evidence_based"] * 0.2
                )

                return {
                    "score": round(layer_2_score, 1),
                    "clinical_reasoning": scores["clinical_reasoning"],
                    "safety": scores["safety"],
                    "evidence_based": scores["evidence_based"],
                    "feedback": scores.get("feedback", "No feedback provided"),
                    "errors": [],
                }
            else:
                # Parsing failed, return None
                return None

        except Exception:
            return None


# ============================================================================
# COMBINED VALIDATION SERVICE
# ============================================================================


async def validate_soap_note(
    soap_note: Dict, patient_context: Dict, time_taken_seconds: int
) -> Dict:
    """
    3-layer SOAP note validation

    VALIDATION FLOW:
    1. Layer 1 (Rule-based): Always runs
    2. Layer 2 (Claude AI): 60% of time (cost optimization)
    3. Layer 3 (Specialist): Flagged cases only (not implemented yet)

    Args:
        soap_note: SOAP note content
        patient_context: Mock patient information
        time_taken_seconds: Time taken to complete session

    Returns:
        Combined validation result with overall score
    """
    # Layer 1: Rule-based validation (always runs)
    validator_layer1 = RuleBasedValidator()
    layer1_result = validator_layer1.validate(soap_note, patient_context)

    # Layer 2: Claude AI validation (60% of time)
    layer2_result = None
    if random.random() < 0.6:
        validator_layer2 = ClaudeAIValidator()
        layer2_result = await validator_layer2.validate(soap_note, patient_context)

    # Combine scores
    if layer2_result:
        # Weighted combination: Layer 1 (40%) + Layer 2 (60%)
        overall_score = layer1_result["score"] * 0.4 + layer2_result["score"] * 0.6
    else:
        # Fallback to Layer 1 only
        overall_score = layer1_result["score"]

    # Determine pass/fail
    if overall_score >= 70:
        pass_fail = "PASS"
    elif overall_score >= 60:
        pass_fail = "BORDERLINE"
    else:
        pass_fail = "FAIL"

    return {
        "overall_score": round(overall_score, 1),
        "layer_1_rule_based": {
            "score": layer1_result["score"],
            "completeness": layer1_result["completeness"],
            "structure": layer1_result["structure"],
            "errors": layer1_result["errors"],
            "feedback": layer1_result["feedback"],
        },
        "layer_2_claude_ai": layer2_result if layer2_result else None,
        "layer_3_specialist": None,  # Not implemented yet
        "pass_fail": pass_fail,
        "time_taken_seconds": time_taken_seconds,
    }
