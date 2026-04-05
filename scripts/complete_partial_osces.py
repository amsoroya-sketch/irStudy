#!/usr/bin/env python3
"""
Complete Partial OSCE Regenerations - Smart Completion Script

This script:
1. Loads partially regenerated OSCE files
2. Identifies NULL/incomplete OSCEs
3. Regenerates ONLY the missing OSCEs
4. Preserves existing high-quality OSCEs
5. Updates the file in-place

Usage:
    python3 scripts/complete_partial_osces.py \\
        data/osces/psychiatry_40_osces_regenerated.json \\
        data/osces/psychiatry_40_osces.json \\
        psychiatry

Arguments:
    - regenerated_file: Partially complete file (with NULL OSCEs)
    - original_file: Original file (has topic metadata)
    - specialty: psychiatry, cardiology, or respiratory
"""

import json
import os
import sys
import time
import subprocess
from pathlib import Path
from datetime import datetime

# Claude CLI configuration
CLAUDE_MODEL = "claude-sonnet-4-20250514"


def is_osce_complete(osce: dict) -> bool:
    """Check if an OSCE has all required fields populated."""
    if not osce:
        return False

    # Check essential fields
    has_title = osce.get('title') not in [None, '', 'Unknown']
    has_candidate = osce.get('candidate_instructions') not in [None, '']
    has_sample = osce.get('sample_answer') not in [None, {}, '']

    # For object structure
    if 'scenario' in osce:
        has_scenario = osce.get('scenario') not in [None, {}]
        return has_title and has_candidate and has_sample and has_scenario

    return has_title and has_candidate and has_sample


def get_psychiatry_prompt(topic: str, subtopic: str, difficulty: str) -> str:
    """Get prompt for psychiatry OSCE generation."""
    return f"""You are an expert psychiatrist and AMC Clinical Examination examiner.

Generate a COMPLETE psychiatry OSCE station for: {topic}
Subtopic: {subtopic}
Difficulty: {difficulty}

MANDATORY REQUIREMENTS:

1. SAFE-T Protocol (CRITICAL - ALWAYS INCLUDE):
   - Specific plan assessment
   - Access to means
   - Feelings of hopelessness
   - Earlier suicide attempts
   - Threat level (low/medium/high risk)
   - Risk factors vs protective factors

2. Australian Crisis Contacts (CRITICAL):
   - Lifeline 13 11 14
   - Beyond Blue 1300 224 636
   - Mental Health Access Line (state-specific)

3. Specific Clinical Content:
   - Patient demographics: age, gender, occupation
   - Presenting complaint: specific symptoms with timeline
   - Complete psychiatric history (9-step)
   - Mental State Examination: All 8 domains
   - Risk assessment: Suicide, homicide, self-harm, vulnerability

4. Management Plan:
   - Immediate: Safety plan, crisis contacts, emergency protocols
   - Medication: Specific drugs with doses + PBS codes
     Example: "Sertraline 50mg daily (PBS 2062B)" NOT "SSRI as appropriate"
   - Therapy: CBT/DBT/IPT with specific referrals
   - Follow-up: GP in 3 days, psychiatry in 1-2 weeks
   - Mental Health Act criteria if applicable

5. Marking Criteria: 10-15 items, 15 marks total

6. Learning Points: 5-7 Australian-specific clinical pearls

Return valid JSON with this structure:
{{
  "title": "Specific clinical title",
  "osce_id": "PSYCH-{topic[:4].upper()}-XXX",
  "specialty": "Psychiatry",
  "difficulty": "{difficulty}",
  "duration_minutes": 8,
  "topics": ["{topic}"],
  "candidate_instructions": "Complete scenario with context...",
  "patient_role_instructions": "Complete patient backstory...",
  "examiner_instructions": "What to observe and assess...",
  "marking_criteria": [
    {{"criterion": "...", "marks": 1, "description": "..."}},
    ...
  ],
  "sample_answer": {{
    "history_summary": "Specific findings...",
    "mse_findings": "Complete MSE all 8 domains...",
    "diagnosis": "Primary diagnosis with ICD-11/DSM-5 code",
    "differentials": ["...", "...", "..."],
    "safe_t_assessment": {{
      "specific_plan": "...",
      "access_to_means": "...",
      "feelings_hopelessness": "...",
      "earlier_attempts": "...",
      "threat_level": "low/medium/high",
      "risk_factors": ["...", "..."],
      "protective_factors": ["...", "..."]
    }},
    "management": {{
      "immediate": "Safety plan, remove means, crisis contacts...",
      "medications": "Specific drugs with doses + PBS codes",
      "therapy": "CBT/DBT referral specifics",
      "follow_up": "GP in 3 days, psychiatry in 1-2 weeks",
      "crisis_contacts": "Lifeline 13 11 14, Beyond Blue 1300 224 636"
    }},
    "mental_health_act": "Criteria assessment if applicable..."
  }},
  "learning_points": [
    "SAFE-T: Always assess suicide risk explicitly...",
    "Australian crisis contacts: Lifeline 13 11 14...",
    "..."
  ],
  "references": [
    {{"title": "RANZCP Clinical Guidelines", "section": "..."}},
    {{"title": "Mental Health Act NSW 2007", "section": "..."}},
    {{"title": "Therapeutic Guidelines: Psychiatry", "section": "..."}}
  ]
}}

NO PLACEHOLDERS - every field must have specific clinical content.
Return ONLY the JSON, no markdown, no explanations."""


def get_cardiology_prompt(topic: str, difficulty: str) -> str:
    """Get prompt for cardiology OSCE generation."""
    return f"""You are a senior cardiologist and AMC Clinical Examination examiner.

Generate a COMPLETE cardiology OSCE for: {topic}
Difficulty: {difficulty}

MANDATORY REQUIREMENTS:

1. ECG Interpretation (if applicable):
   - Specific measurements: "ST elevation 3mm in leads II, III, aVF"
   - NOT generic: "ECG findings for STEMI"

2. Medications with Doses + PBS Codes:
   - "Aspirin 300mg PO stat - PBS 8053K"
   - "Ticagrelor 180mg PO stat, then 90mg BD - PBS 8721K"
   - NOT: "Dual antiplatelet therapy as per guidelines"

3. STEMI Protocol (if applicable):
   - Door-to-balloon time: <90 minutes
   - Primary PCI vs thrombolysis criteria
   - Anticoagulation specifics

4. Australian Guidelines:
   - National Heart Foundation
   - CSANZ (Cardiac Society of Australia and New Zealand)
   - eTG: Cardiovascular

Return valid JSON with complete clinical scenario, specific medications, PBS codes, and Australian context.
NO PLACEHOLDERS. Return ONLY JSON."""


def get_respiratory_prompt(topic: str, difficulty: str) -> str:
    """Get prompt for respiratory OSCE generation."""
    return f"""You are a respiratory physician and AMC Clinical Examination examiner.

Generate a COMPLETE respiratory OSCE for: {topic}
Difficulty: {difficulty}

MANDATORY REQUIREMENTS:

1. Spirometry Interpretation (if applicable):
   - Specific values: "FEV1 1.8L (45% predicted), FVC 3.2L (65% predicted), FEV1/FVC 0.56"
   - Pattern: "Obstructive pattern" with severity
   - NOT: "Spirometry findings for COPD"

2. Oxygen Targets:
   - COPD: 88-92% SpO2
   - Non-COPD: 94-98% SpO2
   - Specific reasoning

3. Inhalers with Devices:
   - "Salbutamol 100mcg MDI + spacer, 2 puffs PRN - PBS 8333L"
   - "Tiotropium 18mcg HandiHaler, 1 cap daily - PBS 8723K"
   - Device technique demonstration

4. Australian Guidelines:
   - National Asthma Council Australia
   - COPD-X Guidelines
   - TSANZ (Thoracic Society of Australia and New Zealand)

Return valid JSON with complete clinical scenario, spirometry values, specific medications with devices and PBS codes.
NO PLACEHOLDERS. Return ONLY JSON."""


def generate_osce_with_claude(topic: str, subtopic: str, difficulty: str, specialty: str, index: int) -> dict:
    """Generate OSCE using Claude CLI."""

    # Select prompt based on specialty
    if specialty == "psychiatry":
        prompt = get_psychiatry_prompt(topic, subtopic, difficulty)
    elif specialty == "cardiology":
        prompt = get_cardiology_prompt(topic, difficulty)
    elif specialty == "respiratory":
        prompt = get_respiratory_prompt(topic, difficulty)
    else:
        raise ValueError(f"Unknown specialty: {specialty}")

    print(f"    Calling Claude CLI...")

    try:
        # Call Claude CLI
        result = subprocess.run(
            ['claude', '--model', CLAUDE_MODEL],
            input=prompt,
            capture_output=True,
            text=True,
            timeout=180
        )

        if result.returncode != 0:
            print(f"    ❌ Claude CLI error: {result.stderr[:200]}")
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
                print(f"    ❌ Could not find JSON in response")
                return None

        osce = json.loads(json_str)
        print(f"    ✅ Generated successfully")
        return osce

    except subprocess.TimeoutExpired:
        print(f"    ❌ Timeout (180s exceeded)")
        return None
    except json.JSONDecodeError as e:
        print(f"    ❌ JSON parse error: {e}")
        return None
    except Exception as e:
        print(f"    ❌ Generation failed: {str(e)}")
        return None


def complete_partial_osces(regenerated_path: Path, original_path: Path, specialty: str):
    """Complete a partially regenerated OSCE file."""

    print(f"\n{'='*80}")
    print(f"COMPLETING PARTIAL {specialty.upper()} OSCES")
    print(f"{'='*80}\n")

    # Load files
    print(f"Loading files...")
    with open(regenerated_path, 'r') as f:
        data = json.load(f)

    with open(original_path, 'r') as f:
        original_data = json.load(f)

    # Handle different file structures
    if isinstance(data, dict) and 'osces' in data:
        osces = data['osces']
        metadata = data.get('metadata', {})
        structure = 'object'
    elif isinstance(data, list):
        osces = data
        metadata = {}
        structure = 'array'
    else:
        print(f"❌ Unknown file structure")
        return

    # Get original OSCEs for topic metadata
    if isinstance(original_data, dict) and 'osces' in original_data:
        original_osces = original_data['osces']
    elif isinstance(original_data, list):
        original_osces = original_data
    else:
        print(f"❌ Cannot read original file")
        return

    print(f"  Structure: {structure}")
    print(f"  Current OSCEs: {len(osces)}")
    print(f"  Original OSCEs: {len(original_osces)}")

    # Find incomplete OSCEs
    incomplete_indices = []
    for i, osce in enumerate(osces):
        if not is_osce_complete(osce):
            incomplete_indices.append(i)

    print(f"\n  Complete OSCEs: {len(osces) - len(incomplete_indices)}")
    print(f"  Incomplete OSCEs: {len(incomplete_indices)}")

    if not incomplete_indices:
        print(f"\n✅ All OSCEs already complete!")
        return

    print(f"\n  Incomplete indices: {[i+1 for i in incomplete_indices[:20]]}")
    if len(incomplete_indices) > 20:
        print(f"    ... and {len(incomplete_indices)-20} more")

    # Regenerate incomplete OSCEs
    print(f"\nRegenerating {len(incomplete_indices)} OSCEs...")
    success_count = 0

    for idx in incomplete_indices:
        # Get topic from original
        if idx < len(original_osces):
            original = original_osces[idx]
            topic = original.get('topic', 'Unknown Topic')
            subtopic = original.get('subtopic', '')
            difficulty = original.get('difficulty', 'medium')
        else:
            topic = f"OSCE {idx+1}"
            subtopic = ""
            difficulty = "medium"

        print(f"\n  [{idx+1}/{len(osces)}] {topic}")

        new_osce = generate_osce_with_claude(topic, subtopic, difficulty, specialty, idx+1)

        if new_osce:
            osces[idx] = new_osce
            success_count += 1
            print(f"    ✅ Replaced NULL OSCE")
        else:
            print(f"    ❌ Generation failed - keeping NULL")

        # Rate limiting - increased to 10s to avoid API exhaustion
        time.sleep(10)  # 10 seconds between calls = max 6 calls/min

    # Update metadata
    if structure == 'object':
        metadata['last_completion_date'] = datetime.now().isoformat()
        metadata['total_osces'] = len(osces)
        metadata['regeneration_status'] = 'COMPLETE' if all(is_osce_complete(o) for o in osces) else 'PARTIAL'

        output_data = {
            'metadata': metadata,
            'osces': osces
        }
    else:
        output_data = osces

    # Save updated file
    print(f"\nSaving to {regenerated_path}...")
    with open(regenerated_path, 'w') as f:
        json.dump(output_data, f, indent=2)

    # Final summary
    final_complete = sum(1 for o in osces if is_osce_complete(o))
    print(f"\n{'='*80}")
    print(f"COMPLETION SUMMARY")
    print(f"{'='*80}")
    print(f"  Total OSCEs: {len(osces)}")
    print(f"  Complete: {final_complete}/{len(osces)} ({final_complete/len(osces)*100:.0f}%)")
    print(f"  Newly generated: {success_count}")
    print(f"  Status: {'✅ COMPLETE' if final_complete == len(osces) else '⚠️  STILL PARTIAL'}")
    print()


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(__doc__)
        sys.exit(1)

    regenerated_file = Path(sys.argv[1])
    original_file = Path(sys.argv[2])
    specialty = sys.argv[3].lower()

    if not regenerated_file.exists():
        print(f"❌ Regenerated file not found: {regenerated_file}")
        sys.exit(1)

    if not original_file.exists():
        print(f"❌ Original file not found: {original_file}")
        sys.exit(1)

    if specialty not in ['psychiatry', 'cardiology', 'respiratory']:
        print(f"❌ Invalid specialty: {specialty}")
        print(f"   Must be: psychiatry, cardiology, or respiratory")
        sys.exit(1)

    complete_partial_osces(regenerated_file, original_file, specialty)
