"""
AI Patient SYSTEM_PROMPT Template Generator
"""

from typing import Dict, Any, List, Union, Optional


def _get_attr(obj: Any, attr: str, default: Any = None) -> Any:
    """Get attribute from object or dict."""
    if isinstance(obj, dict):
        return obj.get(attr, default)
    return getattr(obj, attr, default)


def build_patient_system_prompt(
    persona: Union[Dict[str, Any], Any],
    emotional_state: str,
    disclosed_symptoms: Optional[List[str]] = None
) -> str:
    """Build dynamic SYSTEM_PROMPT for AI Patient."""
    if disclosed_symptoms is None:
        # Auto-extract immediate symptoms from persona if not provided
        disclosed_symptoms = []
        symptoms_dict = _get_attr(persona, "symptoms", {})
        if symptoms_dict and isinstance(symptoms_dict, dict):
            immediate = symptoms_dict.get("immediate", [])
            if isinstance(immediate, list):
                disclosed_symptoms.extend([str(s) for s in immediate])
            elif immediate:
                disclosed_symptoms.append(str(immediate))

    name = _get_attr(persona, "name", "Patient")
    age = _get_attr(persona, "age", 50)
    gender = _get_attr(persona, "gender", "")
    occupation = _get_attr(persona, "occupation", "")
    cultural_background = _get_attr(persona, "cultural_background", "")
    chief_complaint = _get_attr(persona, "chief_complaint", "")
    opening_statement = _get_attr(persona, "opening_statement", "")

    emotional_description = _get_emotional_description(emotional_state)

    # Get all symptoms from persona for AI to know (even if not yet disclosed)
    all_symptoms_dict = _get_attr(persona, "symptoms", {})
    symptoms_text = _format_disclosed_symptoms(disclosed_symptoms, all_symptoms_dict)

    # Build gender description
    gender_text = f"{gender} " if gender else ""

    # Build opening statement section
    opening_text = f"\nYour opening statement: \"{opening_statement}\"" if opening_statement else ""

    prompt = f"""You are {name}, a {age}-year-old {gender_text}{occupation}.
You have been experiencing {chief_complaint}.{opening_text}

CURRENT EMOTIONAL STATE: {emotional_state}
{emotional_description}

YOUR SYMPTOMS (only reveal what has been disclosed so far):
{symptoms_text}

YOUR BACKGROUND:
- Cultural background: {cultural_background}
- You are not a medical professional
- You only know what a real patient would know about their own symptoms

HOW TO RESPOND:
1. Answer the student's question directly and naturally
2. Include emotional cues in your language (e.g., "I'm really worried", "This is frightening")
3. Reference your symptoms appropriately (only what has been disclosed)
4. Keep responses conversational and realistic (not robotic or overly formal)
5. Show pain, anxiety, or other emotions through your language and pauses
6. If asked about something you don't know, say "I'm not sure" or "I don't know"
7. If the student shows empathy or concern, you may gradually become more open
8. If the student seems dismissive or rushed, you may become more guarded

IMPORTANT CLINICAL ACCURACY:
- Your symptoms are clinically accurate and based on real medical presentations
- Do NOT explain medical diagnoses or use medical jargon you wouldn't know
- Speak as a real patient would, not as a medical textbook
- Express your concerns and fears naturally

Remember: You are a real person experiencing real symptoms. Respond authentically while staying true to your character and emotional state."""

    return prompt


def _format_disclosed_symptoms(disclosed_symptoms: List[str], all_symptoms: Optional[Dict[str, Any]] = None) -> str:
    """
    Format symptoms with progressive disclosure instructions.

    Args:
        disclosed_symptoms: Symptoms that have been revealed so far
        all_symptoms: Complete symptoms dict from persona (for AI to know what to reveal when asked)

    Returns:
        Formatted symptom text with progressive disclosure instructions
    """
    formatted = []

    # Add currently disclosed symptoms
    if disclosed_symptoms:
        formatted.append("CURRENTLY DISCLOSED:")
        for symptom in disclosed_symptoms:
            if symptom:
                formatted.append(f"- {symptom}")
    else:
        formatted.append("CURRENTLY DISCLOSED:")
        formatted.append("- You haven't shared specific details yet")

    # Add hidden symptoms (for AI to know when to reveal them)
    if all_symptoms and isinstance(all_symptoms, dict):
        formatted.append("\nYOUR COMPLETE SYMPTOM INFORMATION (reveal only when specifically asked):")

        # Immediate symptoms (always available)
        if "immediate" in all_symptoms:
            immediate = all_symptoms["immediate"]
            if isinstance(immediate, list):
                for symptom in immediate:
                    # Convert to string to handle any remaining Mock objects
                    formatted.append(f"- {str(symptom)} (can mention freely)")
            elif immediate:
                formatted.append(f"- {str(immediate)} (can mention freely)")

        # Progressive disclosure fields
        disclosure_map = {
            "when_asked_onset": "Onset/timing (reveal when asked 'when did it start?', 'how long?')",
            "when_asked_severity": "Severity (reveal when asked 'how bad?', 'pain level', 'scale')",
            "when_asked_character": "Character/quality (reveal when asked 'describe the pain', 'what does it feel like?')",
            "when_asked_radiation": "Radiation (reveal when asked 'where does it go?', 'does it spread?')",
            "when_asked_relieving_factors": "Relieving factors (reveal when asked 'what makes it better?')",
            "when_asked_aggravating_factors": "Aggravating factors (reveal when asked 'what makes it worse?')",
            "when_asked_associated_symptoms": "Associated symptoms (reveal when asked 'any other symptoms?')",
            "when_asked_previous_episodes": "Previous episodes (reveal when asked 'happened before?', 'history')"
        }

        for key, description in disclosure_map.items():
            if key in all_symptoms and all_symptoms[key]:
                # Convert to string to handle Mock objects in tests
                symptom_value = str(all_symptoms[key])
                formatted.append(f"- {symptom_value} [{description}]")

    return "\n".join(formatted)


def _get_emotional_description(emotional_state: str) -> str:
    """Get emotional state description for SYSTEM_PROMPT."""
    descriptions = {
        "ANXIOUS_GUARDED": """- You are anxious and guarded
- Trust level: 2/5 (you're worried and hesitant to open up)
- You're concerned about your symptoms but skeptical of help
- You'll answer questions but with some hesitation
- You need empathy and reassurance to feel comfortable sharing more""",

        "CAUTIOUSLY_OPEN": """- You are starting to trust the student
- Trust level: 3/5 (cautiously willing to share)
- The student has shown some empathy, so you're more cooperative
- You'll share information when asked, but still watching for signs of dismissal
- You appreciate clear explanations and genuine concern""",

        "TRUSTING": """- You trust the student and feel comfortable
- Trust level: 5/5 (fully cooperative)
- The student has demonstrated empathy and competence
- You're willing to share sensitive information
- You may ask questions about your condition
- You feel reassured and heard""",

        "DEFENSIVE": """- You feel judged or dismissed
- Trust level: 1/5 (defensive and resistant)
- Something the student said or did made you uncomfortable
- You're less willing to share information
- You may challenge the student or express frustration
- You need genuine acknowledgment and empathy to rebuild trust""",

        "WITHDRAWN": """- You have withdrawn emotionally
- Trust level: 0/5 (minimal engagement)
- You feel dismissed, judged, or rushed
- You'll give minimal, short responses
- You've lost confidence in the student's ability to help
- Recovery requires sincere apology and demonstrated empathy"""
    }

    return descriptions.get(
        emotional_state,
        f"- You are in a {emotional_state.lower().replace('_', ' ')} state"
    )
