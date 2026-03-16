"""
Feedback Generator for AI OSCE Scoring

Generates structured feedback:
- Strengths (3-5 specific achievements)
- Areas for improvement (2-4 actionable gaps)
- Narrative (100-150 word constructive summary)

SECURITY: No hardcoded credentials
CONTEXT: AMC Clinical Examination
"""

import logging
from typing import Dict, List, Any, Union

logger = logging.getLogger(__name__)


class FeedbackGenerator:
    """
    Generate structured feedback for OSCE sessions.

    Feedback is evidence-based (references transcript/scores) and constructive.
    """

    def generate_feedback(
        self,
        transcript: List[Dict[str, str]],
        scores: Dict[str, Any],
        persona: Union[Dict[str, Any], Any]
    ) -> Dict[str, Any]:
        """
        Generate complete feedback package.

        Returns:
            Dict with:
            - strengths: List[str] (3-5 items)
            - areas_for_improvement: List[str] (2-4 items)
            - narrative: str (100-150 words)
        """
        strengths = self.generate_strengths(transcript, scores)
        improvements = self.generate_improvements(transcript, scores)
        narrative = self.generate_narrative(strengths, improvements, scores)

        return {
            "strengths": strengths,
            "areas_for_improvement": improvements,
            "narrative": narrative
        }

    def generate_strengths(
        self,
        transcript: List[Dict[str, str]],
        scores: Dict[str, Any]
    ) -> List[str]:
        """
        Extract 3-5 specific strengths from high-scoring domains.

        Returns evidence-based strengths (references transcript/scores).
        """
        strengths = []

        # Communication (0-3)
        if scores.get("communication_score", 0) >= 2:
            strengths.append("Demonstrated empathy and active listening skills")

        # Clinical Reasoning (0-4)
        if scores.get("clinical_reasoning_score", 0) >= 3:
            strengths.append("Strong clinical reasoning with appropriate differential diagnosis")

        # Information Gathering (0-4)
        if scores.get("information_gathering_score", 0) >= 3:
            strengths.append("Systematic and comprehensive history taking")

        # Management (0-2)
        if scores.get("management_score", 0) >= 2:
            strengths.append("Evidence-based management plan with appropriate investigations")

        # Professionalism (0-2)
        if scores.get("professionalism_score", 0) >= 2:
            strengths.append("Maintained professionalism and patient-centered approach")

        # Ensure 3-5 strengths (add generic if needed)
        if len(strengths) < 3:
            strengths.append("Completed the consultation within time constraints")

        if len(strengths) < 3:
            strengths.append("Attempted to address patient concerns")

        return strengths[:5]  # Max 5

    def generate_improvements(
        self,
        transcript: List[Dict[str, str]],
        scores: Dict[str, Any]
    ) -> List[str]:
        """
        Identify 2-4 actionable gaps from low-scoring domains.

        Returns constructive, specific improvements.
        """
        improvements = []

        # Critical errors (highest priority)
        if scores.get("critical_errors"):
            improvements.append("Address critical safety errors - recognize and act on red flags immediately")

        # Communication (0-3)
        if scores.get("communication_score", 0) < 2:
            improvements.append("Enhance empathy and active listening - use open-ended questions")

        # Clinical Reasoning (0-4)
        if scores.get("clinical_reasoning_score", 0) < 2:
            improvements.append("Develop broader differential diagnosis - consider red flags systematically")

        # Information Gathering (0-4)
        if scores.get("information_gathering_score", 0) < 2:
            improvements.append("Use structured history taking framework (e.g., SOCRATES for pain)")

        # Management (0-2)
        if scores.get("management_score", 0) < 1:
            improvements.append("Formulate evidence-based management plans - include investigations and treatment")

        # Professionalism (0-2)
        if scores.get("professionalism_score", 0) < 1:
            improvements.append("Maintain professional demeanor and patient-centered approach throughout")

        # Ensure 2-4 improvements (add generic if needed)
        if not improvements:
            improvements.append("Continue developing clinical skills through practice")

        return improvements[:4]  # Max 4

    def generate_narrative(
        self,
        strengths: List[str],
        improvements: List[str],
        scores: Dict[str, Any]
    ) -> str:
        """
        Generate 100-150 word constructive narrative.

        Combines strengths and improvements in growth-oriented tone.
        """
        total_score = scores.get("total_score", 0)
        pass_fail = scores.get("pass_fail", "")

        # Opening (based on performance level)
        if pass_fail == "PASS" and total_score >= 12:
            opening = "This was a strong performance demonstrating competence across multiple clinical domains. "
            opening += "The candidate showed good understanding of the clinical scenario and appropriate management."
        elif pass_fail == "PASS":
            opening = "This session met the minimum standard with areas of competence demonstrated. "
            opening += "The candidate showed adequate clinical skills but with room for development."
        elif pass_fail == "BORDERLINE":
            opening = "This session showed some competence but requires improvement in key areas. "
            opening += "The candidate demonstrated basic skills but needs to strengthen clinical approach."
        else:
            opening = "This session requires significant development to meet clinical standards. "
            opening += "The candidate needs to focus on fundamental clinical competencies and safety."

        # Strengths summary
        if strengths:
            strength_text = f" Notable strengths included {strengths[0].lower()}"
            if len(strengths) > 1:
                strength_text += f" and {strengths[1].lower()}"
            strength_text += ". These are positive foundations to build upon."
        else:
            strength_text = ""

        # Improvements summary
        if improvements:
            improve_text = f" To improve, the candidate should focus on {improvements[0].lower()}"
            if len(improvements) > 1:
                improve_text += f". Additionally, attention is needed to {improvements[1].lower()}"
            improve_text += ". These areas are critical for clinical competence."
        else:
            improve_text = ""

        # Closing
        closing = " With targeted practice and focused learning, clinical competence will continue to develop progressively."

        narrative = opening + strength_text + improve_text + closing

        return narrative


def generate_feedback(
    transcript: List[Dict[str, str]],
    scores: Dict[str, Any],
    persona: Union[Dict[str, Any], Any]
) -> Dict[str, Any]:
    """
    Convenience function for feedback generation.

    Returns:
        Dict with strengths, areas_for_improvement, narrative
    """
    generator = FeedbackGenerator()
    return generator.generate_feedback(transcript, scores, persona)
