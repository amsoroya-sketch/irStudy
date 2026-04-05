#!/usr/bin/env python3
"""
Regenerate psychiatry OSCEs with full clinical content.
Uses gold standard template (psychiatry_week1_osces.json) as model.
Uses Claude CLI for generation.

Usage:
    python3 regenerate_psychiatry_osces.py data/osces/psychiatry_40_osces.json output.json

Requirements:
    - Claude CLI installed and configured
    - Constraint 15 (SAFE-T requirements)
    - Gold standard template for reference
"""

import json
import sys
import subprocess
from pathlib import Path
from typing import Dict
from datetime import datetime

# OSCE generation prompt template
OSCE_GENERATION_PROMPT = """You are a medical education expert creating OSCEs for Australian AMC Clinical Examination preparation.

Generate a complete OSCE station with full clinical content (NOT placeholder templates).

**MANDATORY REQUIREMENTS:**

1. **Complete Clinical Scenario**:
   - Specific patient demographics (age, gender, occupation)
   - Detailed presenting complaint (not "A patient presents for...")
   - Complete history with timeline
   - Specific examination findings (not "examination findings for...")

2. **Detailed Instructions (all 3 required)**:
   - Candidate instructions: Clear task, context, time limit
   - Actor instructions: Complete patient backstory, symptoms, affect, responses to questions
   - Examiner instructions: What to observe, key competencies, pass criteria

3. **Detailed Marking Criteria**:
   - 10-15 marking criteria with specific point values
   - Clear description of what earns marks
   - Total marks (typically 15)

4. **Complete Sample Answer**:
   - History summary: Specific clinical findings (not generic text)
   - Provisional diagnosis with DSM-5/ICD-11 codes
   - Differential diagnoses (at least 3)
   - Immediate management: Specific medications with doses, PBS codes, monitoring, safety netting

5. **Learning Points**:
   - 5-7 specific clinical pearls
   - Australian context (eTG, RANZCP, Mental Health Act)

6. **Psychiatry-Specific Requirements (MANDATORY)**:
   - SAFE-T protocol for ALL psychiatry OSCEs (Specific plan, Access, Feelings, Earlier attempts, Threat)
   - Mental Health Act criteria if high risk (4 criteria for involuntary admission)
   - Australian crisis contacts: Lifeline 13 11 14, Beyond Blue 1300 224 636
   - Cultural safety considerations (Aboriginal/TSI, LGBTQIA+, CALD)

7. **References**:
   - Australian sources (RANZCP, eTG, Mental Health Act)
   - Specific page numbers/sections

**TOPIC FOR THIS OSCE:**
{topic}

**SUBTOPIC:**
{subtopic}

**DIFFICULTY:**
{difficulty}

**EXAMPLE STRUCTURE (from gold standard psychiatry_week1_osces.json):**

```json
{{
  "id": "PSYCH-OSCE-{topic_code}-{timestamp}",
  "station_number": "PSYCH-{number}",
  "station_type": "Psychiatric History Taking",
  "specialty": "Psychiatry",
  "topic": "{topic}",
  "time_limit": 8,
  "difficulty": "{difficulty}",
  "candidate_instructions": "[SPECIFIC scenario: '42-year-old accountant presents with 3-month history of low mood.' NOT 'A patient presents for...']",
  "actor_instructions": "[COMPLETE backstory: 'You are a 42-year-old accountant. You feel sad most days, lost 4kg without trying, wake at 4am unable to sleep. You feel guilty about not being good enough as a mother. You deny suicidal thoughts but sometimes think everyone would be better off without you. You appear tearful when discussing mood.']",
  "examiner_instructions": "[What to observe: 'Systematic psychiatric history, DSM-5 depression criteria assessment, risk assessment (suicide/self-harm), appropriate empathy']",
  "marking_criteria": {{
    "introduction_rapport": {{"marks": 1, "criteria": "Introduces self, explains purpose, establishes empathic rapport"}},
    "presenting_complaint": {{"marks": 1, "criteria": "Elicits presenting complaint and timeline (3 months)"}},
    "dsm5_core_symptoms": {{"marks": 3, "criteria": "Assesses depressed mood, anhedonia, sleep, appetite, concentration, energy, guilt/worthlessness"}},
    "duration_severity": {{"marks": 1, "criteria": "Determines duration (>2 weeks) and functional impairment (work, family)"}},
    "suicide_risk": {{"marks": 2, "criteria": "Explicitly asks about suicidal ideation, plan, intent, protective factors"}},
    "past_psychiatric_history": {{"marks": 1, "criteria": "Previous episodes, treatments, hospitalizations"}},
    "substance_use": {{"marks": 1, "criteria": "Alcohol (increasing use as self-medication), illicit drugs, smoking"}},
    "family_history": {{"marks": 1, "criteria": "Family history of psychiatric illness"}},
    "social_history": {{"marks": 1, "criteria": "Occupation, living situation, support network, stressors"}},
    "screening_questions": {{"marks": 1, "criteria": "Screens for mania, psychosis, anxiety (differential diagnosis)"}},
    "summary_plan": {{"marks": 2, "criteria": "Summarizes findings, offers provisional diagnosis (MDD), outlines next steps"}},
    "communication_empathy": {{"marks": 1, "criteria": "Maintains appropriate empathy, responds to emotional cues"}},
    "total": 15
  }},
  "sample_answer": {{
    "history_summary": "42-year-old woman with 3-month history of low mood, anhedonia, early morning waking, 4kg weight loss, poor concentration, feelings of guilt. Meets DSM-5 criteria for Major Depressive Disorder (moderate severity). Passive suicidal ideation ('better off without me') but no active plan. Risk factors: Family history of depression, increasing alcohol use. Protective factors: Employed, has children, engaged in consultation.",
    "provisional_diagnosis": "Major Depressive Disorder, moderate severity (DSM-5: 296.32)",
    "differential_diagnosis": [
      "Adjustment disorder with depressed mood",
      "Bipolar disorder (depressive episode) - screen for previous manic episodes",
      "Hypothyroidism - check TFTs",
      "Alcohol use disorder (developing)"
    ],
    "immediate_management": [
      "Safety plan: No immediate suicide risk but requires close monitoring",
      "Psychoeducation about depression and treatment options",
      "Discuss psychological therapy (CBT first-line per eTG)",
      "Consider antidepressant (SSRI: sertraline 50mg daily or escitalopram 10mg daily, PBS 2062B)",
      "TFTs, FBC, B12, folate to exclude organic causes",
      "Alcohol reduction counseling",
      "GP Mental Health Care Plan (Medicare rebate for psychology)",
      "Review in 1-2 weeks, safety netting for suicidal thoughts",
      "SAFE-T LOW RISK: No plan, no access to means, passive ideation only, protective factors present"
    ]
  }},
  "learning_points": [
    "DSM-5 MDD criteria: ≥5 symptoms for ≥2 weeks including depressed mood OR anhedonia",
    "SAFE-T suicide risk assessment: Always assess explicitly (Specific plan, Access, Feelings, Earlier attempts, Threat)",
    "eTG first-line: Psychological therapy (CBT/IPT) ± antidepressant for moderate-severe",
    "Screen for bipolar before starting antidepressant (can trigger mania)",
    "Alcohol use often increases in depression (self-medication) - address both",
    "Australian crisis contacts: Lifeline 13 11 14 (24/7), Beyond Blue 1300 224 636"
  ],
  "australian_context": true,
  "australian_guidelines": [
    "Therapeutic Guidelines: Psychiatry - Depression chapter",
    "RANZCP Clinical Practice Guidelines for Mood Disorders",
    "Beyond Blue Clinical Practice Guidelines"
  ]
}}
```

**CRITICAL - NO PLACEHOLDERS:**
- ❌ NO "A patient presents for psychiatric assessment"
- ❌ NO "Clinical history relevant to..."
- ❌ NO "Mental status examination findings for..."
- ❌ NO "According to Australian guidelines for..."
- ✅ YES Specific demographics: "52-year-old unemployed man"
- ✅ YES Specific symptoms: "hasn't slept in 3 days, believes government monitoring via microchip"
- ✅ YES Specific management: "Olanzapine 10mg PO stat, Lorazepam 1mg PO PRN, PBS 2933K"

**OUTPUT INSTRUCTIONS:**
Return ONLY valid JSON. No markdown, no explanations, no code blocks. Just the JSON object starting with {{ and ending with }}.

Generate the complete OSCE now:"""


def generate_osce_with_claude(topic: str, subtopic: str, difficulty: str, number: int) -> Dict:
    """Generate a single OSCE using Claude CLI."""

    # Create topic code for ID
    topic_code = topic.replace(" ", "-").replace("/", "-").upper()[:10]
    timestamp = datetime.now().strftime("%Y%m%d")

    prompt = OSCE_GENERATION_PROMPT.format(
        topic=topic,
        subtopic=subtopic,
        difficulty=difficulty,
        topic_code=topic_code,
        number=str(number).zfill(3),
        timestamp=timestamp
    )

    print(f"\n  Generating OSCE #{number}: {topic}")
    if subtopic:
        print(f"  Subtopic: {subtopic}")
    print(f"  Calling Claude CLI...")

    try:
        # Call Claude CLI with prompt
        result = subprocess.run(
            ['claude', '--model', 'claude-sonnet-4-20250514', ],
            input=prompt,
            capture_output=True,
            text=True,
            timeout=120
        )

        if result.returncode != 0:
            print(f"  ❌ Claude CLI error: {result.stderr}")
            return None

        response_text = result.stdout.strip()

        # Extract JSON from response
        if "```json" in response_text:
            json_start = response_text.find("```json") + 7
            json_end = response_text.find("```", json_start)
            json_str = response_text[json_start:json_end].strip()
        elif "```" in response_text:
            json_start = response_text.find("```") + 3
            json_end = response_text.find("```", json_start)
            json_str = response_text[json_start:json_end].strip()
        elif response_text.startswith("{"):
            json_str = response_text
        else:
            # Try to find JSON object in response
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
            else:
                print(f"  ❌ Could not find JSON in response")
                print(f"  Response preview: {response_text[:200]}")
                return None

        osce = json.loads(json_str)

        # Add metadata
        osce["metadata"] = {
            "generated_date": datetime.now().isoformat(),
            "generator": "regenerate_psychiatry_osces.py + Claude CLI",
            "source_template": "psychiatry_week1_osces.json",
            "constraint_15_applied": True,
            "safe_t_mandatory": True
        }

        print(f"  ✅ Generated successfully")
        return osce

    except subprocess.TimeoutExpired:
        print(f"  ❌ Timeout (120s exceeded)")
        return None
    except json.JSONDecodeError as e:
        print(f"  ❌ JSON parse error: {e}")
        print(f"  Response preview: {json_str[:200] if 'json_str' in locals() else 'N/A'}")
        return None
    except Exception as e:
        print(f"  ❌ Generation failed: {str(e)}")
        return None


def regenerate_osces_file(input_path: Path, output_path: Path):
    """Regenerate all OSCEs in a file."""

    print(f"\n{'='*80}")
    print(f"OSCE Regeneration: {input_path.name}")
    print(f"{'='*80}\n")

    # Load original file (has metadata about topics)
    with open(input_path, 'r') as f:
        original_data = json.load(f)

    original_osces = original_data.get("osces", [])
    total = len(original_osces)

    print(f"Total OSCEs to regenerate: {total}")

    # Regenerate each OSCE
    regenerated_osces = []
    success_count = 0

    for idx, original_osce in enumerate(original_osces, 1):
        topic = original_osce.get("topic", "Unknown Topic")
        subtopic = original_osce.get("subtopic", "")
        difficulty = original_osce.get("difficulty", "medium")

        print(f"\n[{idx}/{total}] Topic: {topic}")

        # Generate new OSCE
        new_osce = generate_osce_with_claude(topic, subtopic, difficulty, idx)

        if new_osce:
            regenerated_osces.append(new_osce)
            success_count += 1
        else:
            print(f"  ⚠️ Skipping due to generation failure")

    # Create output data
    output_data = {
        "metadata": {
            "specialty": "Psychiatry",
            "generation_date": datetime.now().isoformat(),
            "generator": "regenerate_psychiatry_osces.py + Claude CLI",
            "total_osces": success_count,
            "source_file": str(input_path),
            "regeneration_status": "COMPLETE" if success_count == total else "PARTIAL",
            "constraint_15_applied": True,
            "safe_t_mandatory": True
        },
        "osces": regenerated_osces
    }

    # Save to output file
    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"\n{'='*80}")
    print(f"Regeneration Summary")
    print(f"{'='*80}")
    print(f"Total OSCEs: {total}")
    print(f"Successfully regenerated: {success_count}")
    print(f"Failed: {total - success_count}")
    print(f"Success rate: {success_count/total*100:.1f}%")
    print(f"Output file: {output_path}")
    print(f"{'='*80}\n")

    # Run placeholder detection on output
    if success_count > 0:
        print("Running placeholder detection on output...")
        subprocess.run(
            ['python3', 'scripts/detect_placeholder_content.py', str(output_path)],
            cwd=Path.cwd()
        )

    return success_count == total


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 regenerate_psychiatry_osces.py <input.json> <output.json>")
        print("\nExample:")
        print("  python3 regenerate_psychiatry_osces.py data/osces/psychiatry_40_osces.json data/osces/psychiatry_40_osces_regenerated.json")
        sys.exit(1)

    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2])

    if not input_file.exists():
        print(f"ERROR: Input file not found: {input_file}")
        sys.exit(1)

    # Create backup of original file
    backup_dir = Path("data/osces/backups") / datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup_path = backup_dir / input_file.name

    import shutil
    shutil.copy2(input_file, backup_path)
    print(f"✅ Backup created: {backup_path}")

    # Regenerate OSCEs
    success = regenerate_osces_file(input_file, output_file)

    sys.exit(0 if success else 1)
