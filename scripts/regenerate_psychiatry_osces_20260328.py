#!/usr/bin/env python3
"""
Regenerate Psychiatry OSCEs with Complete Clinical Content
==========================================================

This script regenerates psychiatry OSCEs that contain placeholder content,
replacing them with clinically accurate, Australian AMC-aligned content.

CRITICAL REQUIREMENTS:
- SAFE-T protocol in ALL psychiatry OSCEs
- Australian crisis contacts (Lifeline 13 11 14, Beyond Blue 1300 224 636)
- Mental Health Act NSW 2007 criteria if high risk
- NO placeholder phrases ("A patient presents...", "According to guidelines...")
- Specific medications with doses + PBS codes

Author: Mental Health Crisis Expert Agent
Date: 2026-03-28
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, List
import time

# SAFE-T Protocol Template
SAFET_TEMPLATE = """
SAFE-T SUICIDE RISK ASSESSMENT (MANDATORY):
- S (Specific plan): Does patient have concrete method?
- A (Access to means): Access to lethal means (medications, firearms, height)?
- F (Feelings): Hopelessness, worthlessness, feeling like a burden?
- E (Earlier attempts): History of previous suicide attempts?
- T (Threat): Explicit or implicit threat of self-harm?

Risk categorization: LOW / MODERATE / HIGH with specific clinical justification
"""

# Australian Crisis Contacts
AUSTRALIAN_CONTACTS = """
AUSTRALIAN CRISIS CONTACTS (MUST INCLUDE):
- Lifeline 13 11 14 (24/7 crisis support)
- Beyond Blue 1300 224 636 (depression/anxiety)
- Suicide Call Back Service 1300 659 467
"""

# Mental Health Act NSW 2007
MHA_CRITERIA = """
MENTAL HEALTH ACT NSW 2007 (if high risk):
Involuntary admission criteria:
1. Person has mental illness
2. Risk of serious harm to self or others
3. Requires immediate treatment
4. No less restrictive alternative
Document: Section 19 (Emergency) or Section 27 (Involuntary)
"""

def generate_osce_prompt(topic: str, osce_id: str) -> str:
    """Generate detailed prompt for Claude CLI to create psychiatry OSCE."""

    prompt = f"""You are a **Senior Consultation-Liaison Psychiatrist** with 10+ years of teaching hospital experience in mental health crisis management, emergency psychiatry, and acute inpatient care across Australian healthcare settings.

CREATE A COMPLETE PSYCHIATRY OSCE FOR AMC CLINICAL EXAMINATION

**TOPIC:** {topic}
**OSCE ID:** {osce_id}

## CRITICAL REQUIREMENTS (ZERO-TOLERANCE)

### 1. SAFE-T PROTOCOL (MANDATORY FOR ALL PSYCHIATRY OSCEs)
{SAFET_TEMPLATE}

### 2. AUSTRALIAN CRISIS CONTACTS (MANDATORY)
{AUSTRALIAN_CONTACTS}

### 3. MENTAL HEALTH ACT NSW 2007
{MHA_CRITERIA}

### 4. NO PLACEHOLDER CONTENT

**❌ NEVER use these phrases:**
- "A patient presents for psychiatric assessment"
- "Clinical history relevant to..."
- "Mental status examination findings for..."
- "According to Australian guidelines for..."
- "Systematic assessment findings for..."
- "As per protocol..."

**✅ ALWAYS use specific content:**
- Exact age, occupation, relationship status
- Specific duration (3 months, 2 weeks, 5 days)
- Named medications with doses + PBS codes (Sertraline 50mg, PBS 2062B)
- Concrete symptoms (early morning waking, anhedonia, racing thoughts)
- Specific triggers (redundancy, relationship breakdown, bereavement)

### 5. COMPLETE CLINICAL SCENARIOS

**Patient Role Instructions must include:**
- Demographics: "You are a 42-year-old accountant, married with 2 children"
- Timeline: "3 months ago you were made redundant from your job"
- Symptoms: "You wake at 3am every morning unable to get back to sleep"
- Opening statement: First thing patient says when doctor enters
- Hidden information: Revealed only if doctor asks specific questions
- Emotional state: How patient presents (tearful, agitated, flat affect)

**Candidate Instructions must include:**
- Clear role: "You are a junior doctor in ED/GP/psychiatry clinic"
- Patient demographics: "42-year-old woman"
- Presenting complaint: Exact words patient used
- Task: "Take focused history", "Assess suicide risk", "Conduct MSE"
- Time limit: "You have 8 minutes"

**Sample Answer - Immediate Management must include:**
- SAFE-T risk assessment with specific justification
- Safety plan if ANY risk present
- Specific medications: "Sertraline 50mg daily, increase to 100mg after 2 weeks, PBS 2062B"
- NOT: "Consider antidepressant as per guidelines"
- Australian crisis contacts
- Mental Health Act documentation if high risk
- Follow-up plan with specific timeframes

**Marking Criteria must include:**
- 10-15 specific items
- Each item worth points (e.g., "Asks about suicidal ideation - 2 points")
- NOT generic: "Completes history" ❌
- Instead: "Asks about biological symptoms of depression (sleep, appetite, energy, concentration) - 2 points" ✅

## OSCE STRUCTURE (JSON FORMAT)

Return a valid JSON object with this structure:

{{
  "osce_id": "{osce_id}",
  "title": "[Specific clinical scenario, e.g., 'Major Depressive Disorder - Suicide Risk Assessment']",
  "specialty": "Psychiatry",
  "difficulty": "intermediate",
  "duration_minutes": 8,
  "topics": [
    "Mental Health Crisis Management",
    "Suicide Risk Assessment (SAFE-T)",
    "[Specific diagnosis from DSM-5/ICD-11]",
    "[Specific skill, e.g., 'Mental State Examination']"
  ],
  "candidate_instructions": "[Complete detailed scenario - 150-200 words, NO generic phrases]",
  "patient_role_instructions": "[Complete patient backstory - 200-300 words with specific symptoms, timeline, emotions]",
  "sample_answer": {{
    "history_taking_structure": [
      "[10-12 specific questions with expected findings]",
      "Example: 'PRESENTING COMPLAINT: How long have you been feeling down? (Expected: 3 months since redundancy)'",
      "Example: 'BIOLOGICAL SYMPTOMS: Sleep changes? (Expected: Early morning waking at 3am, unable to return to sleep)'"
    ],
    "mental_state_examination": [
      "[Specific MSE findings across all domains]",
      "Appearance: Self-care, grooming, eye contact",
      "Behavior: Psychomotor retardation, fidgeting",
      "Speech: Rate, volume, tone",
      "Mood: Subjective ('How do you feel?' → 'Hopeless')",
      "Affect: Objective (depressed, congruent, reactive)",
      "Thought form: Linear, circumstantial",
      "Thought content: Suicidal ideation (SAFE-T assessment), delusions if psychotic",
      "Perceptions: Auditory hallucinations if psychotic",
      "Cognition: Orientation, concentration",
      "Insight: Awareness of illness",
      "Judgment: Decision-making capacity"
    ],
    "immediate_management": [
      "[12-15 specific management steps]",
      "SAFE-T RISK ASSESSMENT: [LOW/MODERATE/HIGH] - [Specific justification]",
      "Example: 'SAFE-T MODERATE RISK: Passive ideation present ('better off dead'), no specific plan, no access to means, protective factors (children), but severe hopelessness'",
      "Safety plan: [Specific steps]",
      "[Specific medication with dose + PBS code]",
      "Example: 'Sertraline 50mg mane, increase to 100mg after 2 weeks if tolerated, PBS 2062B'",
      "[Australian crisis contacts]",
      "Lifeline 13 11 14 (24/7 crisis support)",
      "Beyond Blue 1300 224 636",
      "[Mental Health Act criteria if high risk]",
      "[Follow-up plan with timeframes]"
    ]
  }},
  "marking_criteria": [
    {{
      "criterion": "[Specific observable behavior]",
      "points": 2,
      "category": "History Taking"
    }},
    "[10-15 items total, each with specific criterion and points]",
    "Example: {{'criterion': 'Asks about suicidal ideation using SAFE-T framework (plan, means, feelings, attempts, threat)', 'points': 3, 'category': 'Risk Assessment'}}"
  ],
  "learning_points": [
    "[8-10 specific clinical pearls]",
    "SAFE-T protocol for suicide risk assessment (Specific, Access, Feelings, Earlier, Threat)",
    "Mental Health Act NSW 2007 criteria for involuntary admission (if relevant)",
    "[Specific medication management with doses]",
    "Australian crisis contacts: Lifeline 13 11 14, Beyond Blue 1300 224 636",
    "[Specific clinical guidelines, e.g., 'eTG: Sertraline first-line SSRI for depression']"
  ],
  "references": [
    "RANZCP Clinical Practice Guidelines - [Specific guideline]",
    "Mental Health Act NSW 2007",
    "Australian Therapeutic Guidelines (eTG) - Psychiatry",
    "[Other specific Australian references]"
  ]
}}

## CLINICAL SCENARIOS BY TOPIC TYPE

Tailor content to the specific psychiatric condition:

**DEPRESSION/SUICIDE:**
- SAFE-T assessment mandatory
- PHQ-9 screening
- Biological symptoms (sleep, appetite, energy, concentration)
- Suicidal ideation (passive vs active, plan, intent)
- Protective factors (employment, children, religious beliefs)
- Medications: SSRIs (Sertraline, Escitalopram), SNRIs (Venlafaxine)

**PSYCHOSIS/SCHIZOPHRENIA:**
- Delusions (paranoid, grandiose, somatic)
- Hallucinations (auditory "voices" - content, frequency, command)
- Disorganized speech/behavior
- Negative symptoms (flat affect, alogia, avolition)
- Substance use screen (cannabis, amphetamines)
- Medications: Olanzapine 5-10mg, Risperidone 1-2mg, Quetiapine 50-100mg
- Mental Health Act likely needed if acute psychosis

**MANIA/BIPOLAR:**
- Elevated mood, grandiosity, reduced need for sleep
- Pressured speech, flight of ideas, distractibility
- Risky behavior (spending, hypersexuality, substance use)
- Mood stabilizers: Lithium (check levels), Valproate, Lamotrigine
- Antipsychotics: Olanzapine, Quetiapine
- Mental Health Act if manic with poor insight

**ANXIETY/PANIC:**
- Physical symptoms (palpitations, sweating, tremor, breathlessness)
- Cognitive symptoms (fear of dying, losing control, going crazy)
- Avoidance behaviors
- Differential diagnosis: Medical causes (thyroid, cardiac, resp)
- Management: CBT first-line, SSRIs if severe (Sertraline, Escitalopram)

**SUBSTANCE USE:**
- CAGE/AUDIT screening
- Withdrawal symptoms (alcohol: tremor, sweating, seizures; opioids: lacrimation, piloerection)
- Motivation to change (Stages of Change model)
- Medications: Naltrexone, Acamprosate, Buprenorphine
- Dual diagnosis common (depression + alcohol)

**DELIRIUM/ORGANIC:**
- Acute confusion, fluctuating consciousness
- Inattention, disorientation
- Medical causes: Infection, metabolic, medication, withdrawal
- MUST rule out before psychiatric diagnosis
- Management: Treat underlying cause, minimize sedation, haloperidol PRN if agitated

NOW CREATE THE OSCE FOR TOPIC: {topic}

**CRITICAL REMINDERS:**
- NO placeholder phrases ("A patient presents...", "According to guidelines...")
- SAFE-T protocol MANDATORY
- Australian crisis contacts MANDATORY
- Specific medications with doses + PBS codes
- Complete patient backstory (200-300 words)
- Complete sample answer (12-15 management steps)
- Marking criteria: 10-15 specific items with points

Return ONLY the JSON object (no markdown formatting, no explanations).
"""

    return prompt


def call_claude_cli(prompt: str) -> str:
    """Call Claude CLI with prompt and return response."""
    try:
        # Call Claude CLI with stdin (modern syntax)
        result = subprocess.run(
            ["claude", "-p"],
            input=prompt,
            capture_output=True,
            text=True,
            timeout=180  # 3 minute timeout per OSCE
        )

        if result.returncode != 0:
            print(f"    ❌ Claude CLI error: {result.stderr}", file=sys.stderr)
            return None

        response = result.stdout.strip()

        # Clean response (remove markdown code blocks if present)
        if response.startswith("```json"):
            response = response[7:]  # Remove ```json
        if response.startswith("```"):
            response = response[3:]  # Remove ```
        if response.endswith("```"):
            response = response[:-3]  # Remove trailing ```

        return response.strip()

    except subprocess.TimeoutExpired:
        print(f"    ❌ Timeout calling Claude CLI (180s)", file=sys.stderr)
        return None
    except Exception as e:
        print(f"    ❌ Error calling Claude CLI: {e}", file=sys.stderr)
        return None


def validate_osce_content(osce: Dict[str, Any]) -> List[str]:
    """Validate OSCE has no placeholder content and meets requirements."""
    issues = []

    # Placeholder phrases (ZERO TOLERANCE)
    placeholder_phrases = [
        "a patient presents",
        "clinical history relevant to",
        "mental status examination findings for",
        "according to australian guidelines for",
        "systematic assessment findings for",
        "as per protocol",
        "as per guidelines",
        "appropriate management",
        "relevant investigation",
    ]

    # Check all text fields for placeholders
    text_fields = [
        osce.get("candidate_instructions", ""),
        osce.get("patient_role_instructions", ""),
        json.dumps(osce.get("sample_answer", {})),
    ]

    for field in text_fields:
        field_lower = field.lower()
        for phrase in placeholder_phrases:
            if phrase in field_lower:
                issues.append(f"Placeholder phrase: '{phrase}'")

    # Check SAFE-T protocol present
    sample_answer_text = json.dumps(osce.get("sample_answer", {})).lower()
    if "safe-t" not in sample_answer_text and "safet" not in sample_answer_text:
        issues.append("SAFE-T protocol not found")

    # Check Australian crisis contacts
    if "13 11 14" not in sample_answer_text and "lifeline" not in sample_answer_text:
        issues.append("Lifeline 13 11 14 not found")

    # Check specific medications (not generic)
    if "as per guidelines" in sample_answer_text or "appropriate medication" in sample_answer_text:
        issues.append("Generic medication references (need specific meds + doses)")

    # Check marking criteria count
    marking_criteria = osce.get("marking_criteria", [])
    if len(marking_criteria) < 10:
        issues.append(f"Only {len(marking_criteria)} marking criteria (need 10-15)")

    # Check learning points count
    learning_points = osce.get("learning_points", [])
    if len(learning_points) < 8:
        issues.append(f"Only {len(learning_points)} learning points (need 8-10)")

    return issues


def regenerate_psychiatry_osces(input_file: str, output_file: str):
    """Main function to regenerate psychiatry OSCEs."""

    print("=" * 80)
    print("PSYCHIATRY OSCE REGENERATION")
    print("=" * 80)
    print()

    # Load input file
    input_path = Path(input_file)
    if not input_path.exists():
        print(f"❌ Input file not found: {input_file}")
        sys.exit(1)

    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Extract osces array from structure {metadata: {...}, osces: [...]}
    if isinstance(data, dict) and 'osces' in data:
        osces = data['osces']
        metadata = data.get('metadata', {})
    else:
        osces = data  # Fallback if data is already a list

    total = len(osces)
    print(f"📋 Loaded {total} OSCEs from {input_file}")
    print()

    # Create backup
    backup_path = input_path.parent / "backups" / f"{input_path.stem}_backup_{int(time.time())}.json"
    backup_path.parent.mkdir(parents=True, exist_ok=True)
    with open(backup_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)  # Backup original structure
    print(f"💾 Backup created: {backup_path}")
    print()

    # Track results
    success_count = 0
    failure_count = 0
    validation_failures = []

    # Regenerate each OSCE
    for i, osce in enumerate(osces, 1):
        osce_id = osce.get("osce_id", f"OSCE-{i:03d}")
        title = osce.get("title", "Unknown topic")

        print(f"[{i}/{total}] Regenerating {osce_id}: {title}")

        # Generate prompt
        prompt = generate_osce_prompt(title, osce_id)

        # Call Claude CLI
        print(f"    ⏳ Calling Claude CLI...")
        response = call_claude_cli(prompt)

        if not response:
            print(f"    ❌ FAILED: Claude CLI returned no response")
            failure_count += 1
            continue

        # Parse JSON
        try:
            new_osce = json.loads(response)
        except json.JSONDecodeError as e:
            print(f"    ❌ FAILED: Invalid JSON response: {e}")
            failure_count += 1
            continue

        # Validate content
        issues = validate_osce_content(new_osce)
        if issues:
            print(f"    ⚠️  VALIDATION WARNINGS: {len(issues)} issues")
            for issue in issues[:3]:  # Show first 3 issues
                print(f"        - {issue}")
            validation_failures.append({
                "osce_id": osce_id,
                "issues": issues
            })
            # Still count as success but flag for review

        # Update OSCE
        osces[i-1] = new_osce
        success_count += 1
        print(f"    ✅ SUCCESS")
        print()

        # Rate limiting (avoid overwhelming API)
        if i < total:
            time.sleep(2)  # 2 second delay between requests

    # Save output
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(osces, f, indent=2, ensure_ascii=False)

    # Print summary
    print()
    print("=" * 80)
    print("REGENERATION COMPLETE")
    print("=" * 80)
    print()
    print(f"✅ Success: {success_count}/{total} OSCEs")
    print(f"❌ Failures: {failure_count}/{total} OSCEs")
    print(f"⚠️  Validation warnings: {len(validation_failures)} OSCEs")
    print()
    print(f"📁 Output saved to: {output_file}")
    print()

    if validation_failures:
        print("⚠️  OSCEs with validation warnings:")
        for item in validation_failures[:10]:  # Show first 10
            print(f"    - {item['osce_id']}: {len(item['issues'])} issues")
        if len(validation_failures) > 10:
            print(f"    ... and {len(validation_failures) - 10} more")
        print()

    # Exit code
    if failure_count > 0:
        sys.exit(1)
    elif len(validation_failures) > 0:
        sys.exit(2)  # Success but with warnings
    else:
        sys.exit(0)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 regenerate_psychiatry_osces_20260328.py <input_file> <output_file>")
        print("Example: python3 regenerate_psychiatry_osces_20260328.py data/osces/psychiatry_40_osces.json data/osces/psychiatry_40_osces_regenerated.json")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    regenerate_psychiatry_osces(input_file, output_file)
