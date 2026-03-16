"""
AI Examiner SYSTEM_PROMPT Template Generator
AMC 15-Mark Rubric Implementation
"""
from typing import Dict, Any, List, Union


def build_examiner_system_prompt(
    persona: Union[Dict[str, Any], Any],
    transcript: List[Dict[str, str]]
) -> str:
    """
    Build dynamic SYSTEM_PROMPT for AI Examiner.
    
    Args:
        persona: PatientPersona data (dict or object)
        transcript: Conversation history [{"role": "student"/"patient", "message": "..."}]
    
    Returns:
        SYSTEM_PROMPT for AMC 15-mark rubric scoring
    """
    # Extract persona details
    if isinstance(persona, dict):
        name = persona.get("name", "Patient")
        chief_complaint = persona.get("chief_complaint", "")
        key_differentials = persona.get("key_differentials", [])
        critical_actions = persona.get("critical_actions", [])
    else:
        name = getattr(persona, "name", "Patient")
        chief_complaint = getattr(persona, "chief_complaint", "")
        key_differentials = getattr(persona, "key_differentials", [])
        critical_actions = getattr(persona, "critical_actions", [])
    
    # Format transcript
    transcript_text = _format_transcript(transcript)
    
    # Format expected differentials
    differentials_text = "\n".join(f"- {d}" for d in key_differentials) if key_differentials else "- Not specified"
    
    # Format critical actions
    actions_text = "\n".join(f"- {a}" for a in critical_actions) if critical_actions else "- Not specified"
    
    prompt = f"""You are an experienced clinical examiner trained in AMC (Australian Medical Council) standards.

Your task is to score an OSCE (Objective Structured Clinical Examination) station using the AMC 15-mark rubric.

**PATIENT SCENARIO**
================
Patient: {name}
Chief Complaint: {chief_complaint}

**EXPECTED CLINICAL APPROACH**
==========================
Key Differentials:
{differentials_text}

Critical Actions:
{actions_text}

**CONVERSATION TRANSCRIPT**
===========================
{transcript_text}

**SCORING RUBRIC (AMC 15-MARK SCALE)**
================================

1. **COMMUNICATION (0-3 marks)**
   - 0: Poor - Minimal eye contact, frequent interruptions, no rapport
   - 1: Below standard - Limited empathy, some interruptions, rushed
   - 2: Satisfactory - Maintains rapport, mostly listens, clear explanations
   - 3: Excellent - Outstanding empathy, active listening, culturally sensitive, patient feels heard

2. **CLINICAL REASONING (0-4 marks)**
   - 0: No differential diagnosis formed; missed obvious diagnosis
   - 1: Incomplete/incorrect differential; major gaps in thinking
   - 2: Reasonable differential with some gaps; logical approach
   - 3: Comprehensive differential, prioritized appropriately
   - 4: Excellent - Differential with clear prioritization and justification

3. **INFORMATION GATHERING (0-4 marks)**
   - 0: Missed critical information; systematic approach absent
   - 1: Incomplete history; significant gaps in data collection
   - 2: Adequate history with minor gaps; mostly systematic
   - 3: Thorough systematic history; all relevant information obtained
   - 4: Excellent - Systematic, comprehensive, no gaps; efficient use of time

4. **MANAGEMENT (0-2 marks)**
   - 0: Unsafe/inappropriate management; potential harm to patient
   - 1: Partially appropriate management; some gaps in safety/evidence-base
   - 2: Safe, appropriate, evidence-based management

5. **PROFESSIONALISM (0-2 marks)**
   - 0: Unprofessional behavior; dismissive, disrespectful, or inappropriate
   - 1: Mostly professional; minor lapses in demeanor or respect
   - 2: Exemplary professionalism; respectful, appropriate, maintains dignity

**PASS/FAIL DETERMINATION**
========================
- PASS: Total ≥ 9/15 (60%) AND no critical errors
- BORDERLINE: Total = 8/15
- FAIL: Total ≤ 7/15 OR critical errors detected

**CRITICAL ERRORS (Auto-fail)**
============================
- Missed critical red flag (e.g., chest pain + crushing + radiation → no ECG ordered)
- Unsafe/dangerous intervention
- Severe cultural insensitivity or discriminatory behavior
- Patient safety compromised

**YOUR TASK**
===========
Score this OSCE session using the rubric above.

**OUTPUT FORMAT** (JSON ONLY):
{{
  "communication_score": 0-3,
  "communication_feedback": "specific feedback",
  "clinical_reasoning_score": 0-4,
  "clinical_reasoning_feedback": "specific feedback",
  "information_gathering_score": 0-4,
  "information_gathering_feedback": "specific feedback",
  "management_score": 0-2,
  "management_feedback": "specific feedback",
  "professionalism_score": 0-2,
  "professionalism_feedback": "specific feedback",
  "total_score": 0-15,
  "pass_fail": "PASS|BORDERLINE|FAIL",
  "critical_errors": ["error1", "error2"] or [],
  "strengths": ["strength1", "strength2"],
  "areas_for_improvement": ["area1", "area2"],
  "overall_feedback": "narrative summary"
}}

Be strict but fair. Provide specific, actionable feedback based on the transcript.
"""
    
    return prompt


def _format_transcript(transcript: List[Dict[str, str]]) -> str:
    """Format conversation transcript for examiner prompt."""
    if not transcript:
        return "[No conversation recorded]"
    
    formatted = []
    for turn in transcript:
        role = turn.get("role", "unknown")
        message = turn.get("message", "")
        
        if role == "student":
            formatted.append(f"Student: {message}")
        elif role == "patient":
            formatted.append(f"Patient: {message}")
        else:
            formatted.append(f"{role.capitalize()}: {message}")
    
    return "\n\n".join(formatted)
