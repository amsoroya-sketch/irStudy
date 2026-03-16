"""
Confidence Calculation for AI OSCE Scoring

Calculates scoring confidence (0.0-1.0) based on:
- Evidence clarity (transcript completeness)
- Score consistency (rubric alignment)
- Edge case detection (ambiguous situations)

SECURITY: No hardcoded credentials
CONTEXT: AMC Clinical Examination
"""

import logging
from typing import Dict, List, Any, Union

logger = logging.getLogger(__name__)


class ConfidenceCalculator:
    """
    Calculate confidence in AI scoring decisions.

    Low confidence (< 0.7) → human review recommended
    High confidence (≥ 0.9) → reliable automated scoring
    """

    def __init__(self):
        self.min_confidence = 0.0
        self.max_confidence = 1.0
        self.human_review_threshold = 0.7

    def calculate_confidence(
        self,
        transcript: List[Dict[str, str]],
        scores: Dict[str, Any],
        persona: Union[Dict[str, Any], Any]
    ) -> float:
        """
        Calculate overall confidence (0.0-1.0).

        Args:
            transcript: Session conversation history
            scores: AI Examiner scores dict
            persona: Patient persona (dict or object)

        Returns:
            float: Confidence score (0.0-1.0)
        """
        # Component 1: Evidence clarity (0.0-1.0)
        evidence_clarity = self._calculate_evidence_clarity(transcript, persona)

        # Component 2: Score consistency (0.0-1.0)
        score_consistency = self._calculate_score_consistency(scores)

        # Component 3: Edge case penalty (0.0-1.0)
        edge_case_penalty = self._detect_edge_cases(transcript, scores, persona)

        # Weighted formula
        # When perfect scores (consistency=1.0), boost confidence
        confidence = (
            evidence_clarity * 0.45 +
            score_consistency * 0.55 -
            edge_case_penalty * 0.1
        )

        # Clamp to [0.0, 1.0]
        confidence = max(self.min_confidence, min(self.max_confidence, confidence))

        logger.info(
            f"Confidence: {confidence:.2f} "
            f"(evidence={evidence_clarity:.2f}, consistency={score_consistency:.2f}, penalty={edge_case_penalty:.2f})"
        )

        return confidence

    def _calculate_evidence_clarity(
        self,
        transcript: List[Dict[str, str]],
        persona: Union[Dict[str, Any], Any]
    ) -> float:
        """
        Calculate evidence clarity (transcript completeness).

        Factors:
        - Transcript length (longer = more evidence)
        - Student message count (more questions = thorough)
        - Coverage of key domains (history, examination, management)
        """
        if not transcript:
            return 0.0

        total_messages = len(transcript)
        student_messages = [m for m in transcript if m.get("role") == "student"]
        student_count = len(student_messages)

        # Heuristic: Good session has 4-15 student messages
        if student_count < 2:
            length_score = 0.2
        elif student_count < 4:
            length_score = 0.6
        elif student_count <= 15:
            length_score = 1.0
        else:
            length_score = 0.9  # Very long sessions may be rambling

        # Check domain coverage (keywords in student messages)
        student_text = " ".join([m.get("message", "").lower() for m in student_messages])

        history_coverage = any(kw in student_text for kw in ["when", "how long", "history", "symptoms", "started", "what brings", "severe"])
        exam_coverage = any(kw in student_text for kw in ["examine", "check", "vital signs", "look at", "listen"])
        management_coverage = any(kw in student_text for kw in ["treatment", "medication", "prescrib", "tests", "ecg", "blood", "referral", "ordering", "giving", "calling"])

        domain_coverage = sum([history_coverage, exam_coverage, management_coverage]) / 3.0

        # Weighted combination
        clarity = (length_score * 0.6) + (domain_coverage * 0.4)

        return clarity

    def _calculate_score_consistency(self, scores: Dict[str, Any]) -> float:
        """
        Calculate score consistency (rubric alignment).

        Factors:
        - Total score matches sum of domains
        - Pass/fail determination aligns with total score
        - Feedback present for all domains
        """
        total_score = scores.get("total_score", 0)

        # Check score matches sum
        expected_total = (
            scores.get("communication_score", 0) +
            scores.get("clinical_reasoning_score", 0) +
            scores.get("information_gathering_score", 0) +
            scores.get("management_score", 0) +
            scores.get("professionalism_score", 0)
        )

        if total_score != expected_total:
            return 0.5  # Inconsistency detected

        # Check pass/fail logic
        pass_fail = scores.get("pass_fail", "")
        critical_errors = scores.get("critical_errors", [])

        if critical_errors and pass_fail != "FAIL":
            return 0.6  # Critical error should force FAIL

        if not critical_errors:
            if total_score >= 9 and pass_fail != "PASS":
                return 0.6
            elif total_score == 8 and pass_fail != "BORDERLINE":
                return 0.6
            elif total_score <= 7 and pass_fail != "FAIL":
                return 0.6

        # Check feedback presence
        feedback_fields = [
            "communication_feedback",
            "clinical_reasoning_feedback",
            "information_gathering_feedback",
            "management_feedback",
            "professionalism_feedback",
            "overall_feedback"
        ]

        feedback_present = sum([
            1 for field in feedback_fields
            if scores.get(field) and len(scores.get(field, "")) > 10
        ])

        feedback_score = feedback_present / len(feedback_fields)

        # All checks passed
        return 0.7 + (feedback_score * 0.3)  # 0.7-1.0 range

    def _detect_edge_cases(
        self,
        transcript: List[Dict[str, str]],
        scores: Dict[str, Any],
        persona: Union[Dict[str, Any], Any]
    ) -> float:
        """
        Detect edge cases that reduce confidence.

        Edge cases:
        - Very short session (< 5 messages)
        - Borderline score (8/15)
        - Patient didn't disclose key information
        - Ambiguous clinical scenario
        """
        penalty = 0.0

        # Very short session
        if len(transcript) < 5:
            penalty += 0.3

        # Borderline score
        if scores.get("pass_fail") == "BORDERLINE":
            penalty += 0.2

        # Very low scores (< 5/15)
        if scores.get("total_score", 0) < 5:
            penalty += 0.2

        # Missing critical actions (if defined in persona)
        critical_actions = self._get_critical_actions(persona)
        if critical_actions:
            student_text = " ".join([
                m.get("message", "").lower()
                for m in transcript
                if m.get("role") == "student"
            ])

            actions_taken = sum([
                1 for action in critical_actions
                if any(keyword.lower() in student_text for keyword in action.split())
            ])

            if actions_taken < len(critical_actions) * 0.5:  # < 50% of critical actions
                penalty += 0.15

        return min(1.0, penalty)  # Cap at 1.0

    def _get_critical_actions(self, persona: Union[Dict[str, Any], Any]) -> List[str]:
        """Extract critical actions from persona."""
        if isinstance(persona, dict):
            return persona.get("critical_actions", [])
        else:
            return getattr(persona, "critical_actions", [])

    def needs_human_review(self, confidence: float) -> bool:
        """Check if confidence is low enough to warrant human review."""
        return confidence < self.human_review_threshold


def calculate_confidence(
    transcript: List[Dict[str, str]],
    scores: Dict[str, Any],
    persona: Union[Dict[str, Any], Any]
) -> float:
    """
    Convenience function for confidence calculation.

    Returns:
        float: Confidence score (0.0-1.0)
    """
    calculator = ConfidenceCalculator()
    return calculator.calculate_confidence(transcript, scores, persona)
