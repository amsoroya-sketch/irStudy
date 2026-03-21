"""
Critical Error Detector for AI OSCE Scoring

Detects safety-critical errors in OSCE sessions that trigger auto-fail.
Uses pattern matching and keyword detection across 25+ critical error rules.

SECURITY: No hardcoded credentials
CONTEXT: AMC Clinical Examination standards (Australian)
"""

import re
import logging
from typing import Dict, List, Any, Union

from src.ai.scoring.error_rules import CRITICAL_ERROR_RULES, get_all_rules

logger = logging.getLogger(__name__)


class CriticalErrorDetector:
    """
    Detects critical errors in OSCE transcripts that trigger auto-fail.

    Critical errors represent safety violations that override any score.
    Even a perfect 15/15 session becomes FAIL if a critical error is detected.
    """

    def __init__(self):
        """Initialize detector with all critical error rules."""
        self.rules = get_all_rules()
        logger.info(f"✅ CriticalErrorDetector initialized with {len(self.rules)} rules")

    def detect_errors(
        self,
        transcript: List[Dict[str, str]],
        persona: Union[Dict[str, Any], Any],
        scores: Dict[str, Any] = None
    ) -> List[Dict[str, str]]:
        """
        Detect critical errors in OSCE session transcript.

        Args:
            transcript: Conversation history [{"role": "student"/"patient", "message": "..."}]
            persona: Patient persona data (dict or object)
            scores: Optional scores dict with feedback fields

        Returns:
            List of detected critical errors:
            [
                {
                    "rule_id": "CE001",
                    "name": "Missed acute red flag - chest pain",
                    "description": "Failed to order ECG for chest pain presentation",
                    "category": "acute_care",
                    "evidence": "Patient mentioned chest pain but student did not order ECG"
                }
            ]
        """
        detected_errors = []

        # Combine transcript into single text for pattern matching
        full_transcript = self._transcript_to_text(transcript)
        student_messages = self._get_student_messages(transcript)
        patient_messages = self._get_patient_messages(transcript)

        # Extract persona info
        chief_complaint = self._get_chief_complaint(persona)

        # Check each rule
        for rule in self.rules:
            error = self._check_rule(
                rule,
                full_transcript,
                student_messages,
                patient_messages,
                chief_complaint,
                scores
            )
            if error:
                detected_errors.append(error)
                logger.warning(f"⚠️  Critical error detected: {rule.rule_id} - {rule.name}")

        return detected_errors

    def _check_rule(
        self,
        rule,
        full_transcript: str,
        student_messages: str,
        patient_messages: str,
        chief_complaint: str,
        scores: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        Check if a specific rule is violated.

        Returns error dict if violated, None otherwise.
        """
        # Custom check functions for complex rules
        if rule.check_function:
            return rule.check_function(
                full_transcript,
                student_messages,
                patient_messages,
                chief_complaint,
                scores
            )

        # For acute_care rules, ALWAYS use heuristic checking (not simple pattern matching)
        # This prevents false positives (e.g., "chest pain" mentioned but ECG ordered)
        if rule.category == "acute_care":
            if self._is_red_flag_missed(rule, patient_messages, student_messages):
                return {
                    "rule_id": rule.rule_id,
                    "name": rule.name,
                    "description": rule.description,
                    "category": rule.category,
                    "evidence": f"Red flag symptoms mentioned but no appropriate action taken"
                }
            return None  # Don't do pattern matching for acute care

        # For medication_safety rules, use heuristics
        if rule.category == "medication_safety":
            if self._is_red_flag_missed(rule, patient_messages, student_messages):
                return {
                    "rule_id": rule.rule_id,
                    "name": rule.name,
                    "description": rule.description,
                    "category": rule.category,
                    "evidence": f"Medication safety violation detected"
                }
            return None

        # For clinical_management, use heuristics
        if rule.category == "clinical_management":
            if self._is_red_flag_missed(rule, patient_messages, student_messages):
                return {
                    "rule_id": rule.rule_id,
                    "name": rule.name,
                    "description": rule.description,
                    "category": rule.category,
                    "evidence": f"Clinical management violation detected"
                }
            return None

        # Pattern-based detection (only for professionalism, safeguarding rules)
        for pattern in rule.patterns:
            if re.search(pattern, full_transcript, re.IGNORECASE):
                return {
                    "rule_id": rule.rule_id,
                    "name": rule.name,
                    "description": rule.description,
                    "category": rule.category,
                    "evidence": f"Pattern matched: {pattern}"
                }

        return None

    def _is_red_flag_missed(self, rule, patient_messages: str, student_messages: str) -> bool:
        """
        Check if red flag symptom was mentioned by patient but not acted upon by student.

        Heuristics:
        - CE001 (chest pain): Patient says "chest pain" but student doesn't mention "ECG"
        - CE002 (stroke): Patient says stroke symptoms but student doesn't mention "stroke protocol" or "CT"
        - CE003 (anaphylaxis): Patient says breathing difficulty but student doesn't mention "adrenaline" or "epinephrine"
        """
        patient_lower = patient_messages.lower()
        student_lower = student_messages.lower()

        # CE001: Chest pain without ECG
        if rule.rule_id == "CE001":
            has_chest_pain = any(kw in patient_lower for kw in ["chest pain", "crushing pain", "cardiac pain"])
            ordered_ecg = any(kw in student_lower for kw in ["ecg", "electrocardiogram", "ekg"])
            return has_chest_pain and not ordered_ecg

        # CE002: Stroke symptoms without recognition
        if rule.rule_id == "CE002":
            has_stroke_symptoms = any(kw in patient_lower for kw in ["facial droop", "arm weakness", "slurred speech", "sudden weakness"])
            recognized_stroke = any(kw in student_lower for kw in ["stroke", "tia", "fast protocol", "ct brain", "ct head"])
            return has_stroke_symptoms and not recognized_stroke

        # CE003: Anaphylaxis without treatment
        if rule.rule_id == "CE003":
            has_anaphylaxis = any(kw in patient_lower for kw in ["difficulty breathing", "throat closing", "throat swelling", "widespread rash"])
            treated_anaphylaxis = any(kw in student_lower for kw in ["adrenaline", "epipen", "anaphylaxis"])
            return has_anaphylaxis and not treated_anaphylaxis

        # CE005: Ectopic pregnancy not considered
        if rule.rule_id == "CE005":
            is_woman_with_pain = ("abdominal pain" in patient_lower or "pelvic pain" in patient_lower)
            pregnancy_mentioned = any(kw in patient_lower for kw in ["pregnant", "missed period", "positive pregnancy"])
            considered_ectopic = "ectopic" in student_lower
            return is_woman_with_pain and pregnancy_mentioned and not considered_ectopic

        # CE008: Allergy not checked before prescribing
        if rule.rule_id == "CE008":
            prescribed_medication = any(kw in student_lower for kw in ["prescrib", "amoxicillin", "penicillin", "antibiotic", "medication for", "i'm giving you"])
            asked_about_allergies = any(kw in student_lower for kw in ["allerg", "allergic", "any medications you can't take", "medication sensitivities"])
            return prescribed_medication and not asked_about_allergies

        # CE012: Cardiac arrest without resuscitation
        if rule.rule_id == "CE012":
            cardiac_arrest = any(kw in patient_lower for kw in ["not breathing", "no pulse", "collapsed", "unconscious"])
            initiated_cpr = any(kw in student_lower for kw in ["cpr", "resuscitation", "chest compressions", "call 000", "emergency"])
            return cardiac_arrest and not initiated_cpr

        return False

    def _transcript_to_text(self, transcript: List[Dict[str, str]]) -> str:
        """Convert transcript to single text block."""
        return " ".join([msg.get("message", "") for msg in transcript])

    def _get_student_messages(self, transcript: List[Dict[str, str]]) -> str:
        """Extract only student messages."""
        return " ".join([
            msg.get("message", "")
            for msg in transcript
            if msg.get("role") == "student"
        ])

    def _get_patient_messages(self, transcript: List[Dict[str, str]]) -> str:
        """Extract only patient messages."""
        return " ".join([
            msg.get("message", "")
            for msg in transcript
            if msg.get("role") == "patient"
        ])

    def _get_chief_complaint(self, persona: Union[Dict[str, Any], Any]) -> str:
        """Extract chief complaint from persona."""
        if isinstance(persona, dict):
            return persona.get("chief_complaint", "")
        else:
            return getattr(persona, "chief_complaint", "")

    def has_critical_errors(self, errors: List[Dict[str, str]]) -> bool:
        """Check if any critical errors exist."""
        return len(errors) > 0

    def apply_auto_fail(self, scores: Dict[str, Any], errors: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Apply auto-fail logic if critical errors detected.

        Even a perfect 15/15 score becomes FAIL if critical errors exist.
        """
        if self.has_critical_errors(errors):
            scores["pass_fail"] = "FAIL"
            scores["critical_errors"] = errors
            logger.warning(
                f"⚠️  AUTO-FAIL applied: {len(errors)} critical error(s) detected, "
                f"score={scores.get('total_score', 0)}/15"
            )
        return scores
