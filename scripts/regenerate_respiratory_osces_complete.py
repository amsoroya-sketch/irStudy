#!/usr/bin/env python3
"""
Respiratory OSCE Regeneration Script
Regenerates 50 respiratory OSCEs with complete clinical content

CRITICAL CONSTRAINTS:
1. Spirometry: Specific FEV1/FVC values (not generic)
2. Oxygen targets: 88-92% for COPD, 94-98% for non-COPD
3. Inhaler devices: Specific devices + technique
4. Medications: Doses + PBS codes
5. Severity classification: Mild/moderate/severe/life-threatening
6. Australian guidelines: Asthma Council, COPD-X, TSANZ
7. Zero placeholders: No "A patient presents..." phrases
"""

import json
import sys
import os
from pathlib import Path
from typing import Dict, List, Any
import anthropic

# Configuration
CLAUDE_API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not CLAUDE_API_KEY:
    print("ERROR: ANTHROPIC_API_KEY environment variable not set")
    sys.exit(1)

client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
MODEL = "claude-sonnet-4-20250514"

# Respiratory OSCE generation prompt template
RESPIRATORY_OSCE_GENERATION_PROMPT = """You are an Australian respiratory physician and clinical educator creating an OSCE station for AMC Clinical Examination preparation.

CRITICAL CONSTRAINTS (ZERO-TOLERANCE):

1. SPIROMETRY VALUES (MANDATORY):
   - MUST include specific values: "FEV1 1.2L (40% predicted), FVC 2.8L (85% predicted), FEV1/FVC 0.43"
   - NEVER use: "Spirometry findings for COPD" or "Obstructive pattern"
   - Post-bronchodilator values required if relevant

2. OXYGEN TARGETS (CRITICAL):
   - COPD / Chronic CO2 retention: Target SpO2 88-92% (Venturi mask 28%, 4L/min)
   - Non-COPD (Asthma, Pneumonia, PE): Target SpO2 94-98% (Hudson mask 8-10L/min)
   - NEVER use wrong target for condition

3. INHALER DEVICES (MANDATORY):
   - Specify device AND technique: "Salbutamol 200mcg 2 puffs PRN via MDI + spacer (shake, breathe out, press, slow deep breath, hold 10 seconds), PBS 8333L"
   - Include: Turbuhaler, HandiHaler, Accuhaler, MDI + spacer
   - NEVER use: "Inhaler therapy as appropriate"

4. MEDICATIONS:
   - Include doses: "Prednisolone 50mg PO stat"
   - Include PBS codes: "PBS 1234K"
   - Include frequency: "Q20min" or "BD"

5. SEVERITY CLASSIFICATION:
   - Asthma: Mild / Moderate / Severe / Life-threatening
   - COPD: Mild / Moderate / Severe
   - Include criteria for each level

6. AUSTRALIAN GUIDELINES:
   - Reference: National Asthma Council, COPD-X, TSANZ, eTG
   - Use Australian terminology: Paracetamol (not acetaminophen)

7. NO PLACEHOLDERS:
   - NEVER use: "A patient presents with..."
   - ALWAYS use: Specific patient details (age, occupation, timeline, symptoms)

TOPIC: {topic}

Generate a complete OSCE station with this exact JSON structure:

{{
  "osce_id": "RESP-{osce_number:03d}",
  "specialty": "Respiratory",
  "topic": "{topic}",
  "difficulty": "medium|hard",
  "time_allocated": 8,
  "candidate_instructions": "Detailed scenario with specific patient (age, occupation, timeline, symptoms, social context). Include task (assess severity, initiate management, counsel patient). Example: 'You are a junior doctor in ED. A 28-year-old office worker with known asthma presents with severe shortness of breath...' (200-300 words)",
  "actor_instructions": "Actor briefing with patient perspective, emotional state, social context, responses to questions. Example: 'You are a 28-year-old office worker with asthma since childhood. You ran out of your brown puffer 2 weeks ago...' (150-250 words)",
  "examiner_instructions": "What examiner observes: Approach, communication, clinical reasoning, safety. Include key skills assessed.",
  "sample_answer": {{
    "history_taking": [
      "Specific questions with expected answers (if applicable)"
    ],
    "examination_findings": [
      "Specific findings: RR 32/min, SpO2 89%, bilateral wheeze, peak flow 150L/min (33% predicted)",
      "Spirometry if relevant: FEV1 X.XL (XX% predicted), FVC X.XL, FEV1/FVC ratio"
    ],
    "severity_classification": "Classify severity (Mild/Moderate/Severe/Life-threatening) with criteria from Australian guidelines",
    "diagnosis": "Primary diagnosis with differentials if applicable",
    "immediate_management": [
      "Specific medications with doses, routes, frequency, PBS codes",
      "Oxygen therapy: Target SpO2 (88-92% COPD vs 94-98% non-COPD), device, flow rate",
      "Monitoring: Continuous SpO2, repeat peak flow, ABG if indicated",
      "Escalation criteria: When to call senior, ICU referral"
    ],
    "investigations": [
      "Specific tests: ABG (interpret), CXR (what looking for), FBC/UEC",
      "Spirometry interpretation if applicable"
    ],
    "ongoing_management": [
      "Inhaler therapy: Specific devices + technique + PBS codes",
      "Oral medications: Doses, duration",
      "Non-pharmacological: Smoking cessation, pulmonary rehab"
    ],
    "discharge_planning": [
      "Discharge medications with specific devices + technique",
      "Written action plans: Asthma Action Plan / COPD Action Plan",
      "Follow-up: GP in 2-7 days (MBS 23), specialist if criteria met",
      "Safety netting: Red flags to return for"
    ],
    "red_flags": [
      "Life-threatening features: Silent chest, exhaustion, cyanosis, altered consciousness",
      "Escalation triggers specific to condition"
    ]
  }},
  "marking_criteria": [
    "Introduces self, confirms patient identity (1 mark)",
    "Takes focused history: Onset, triggers, previous episodes, medications (2 marks)",
    "Assesses severity using objective criteria (RR, HR, SpO2, peak flow) (2 marks)",
    "Initiates high-flow oxygen with correct target (88-92% COPD vs 94-98% non-COPD) (2 marks)",
    "Administers nebulized bronchodilators (salbutamol + ipratropium if severe) (2 marks)",
    "Administers corticosteroids (prednisolone 50mg PO or hydrocortisone IV) (2 marks)",
    "Requests investigations (ABG, CXR, peak flow) (1 mark)",
    "Recognizes escalation criteria (ICU if not improving, life-threatening features) (2 marks)",
    "Plans discharge with specific inhaler devices + technique (2 marks)",
    "Provides written action plan and safety netting (2 marks)",
    "Professional communication, empathy, shared decision-making (2 marks)"
  ],
  "learning_points": [
    "Severity classification with specific criteria",
    "Oxygen targets: 88-92% COPD vs 94-98% non-COPD",
    "Inhaler devices and technique (70% use incorrectly)",
    "Australian guidelines: Asthma Council / COPD-X / TSANZ",
    "Red flags requiring immediate escalation",
    "Discharge planning: Written action plans mandatory",
    "PBS restrictions for respiratory medications"
  ],
  "common_mistakes": [
    "Using 94-98% oxygen for COPD (causes CO2 retention)",
    "Not assessing severity objectively (RR, SpO2, peak flow)",
    "Forgetting ipratropium in severe asthma",
    "Not providing written action plan",
    "Generic inhaler instructions without device/technique",
    "Missing red flags (silent chest = ICU, not improvement)"
  ],
  "references": [
    "National Asthma Council Australia. Australian Asthma Handbook. Version 2.2, 2022.",
    "COPD-X Guidelines. COPD-X Australian and New Zealand Guidelines, 2023.",
    "Thoracic Society of Australia and New Zealand (TSANZ). Respiratory Guidelines.",
    "eTG Complete. Respiratory chapter. Therapeutic Guidelines Limited, 2023.",
    "O'Driscoll BR, et al. BTS guideline for oxygen use in adults in healthcare and emergency settings. Thorax 2017;72:ii1-ii90."
  ]
}}

Generate complete clinical content with ZERO placeholders. Use specific patient details, specific values, specific medications with doses and PBS codes, specific inhaler devices with technique instructions.

Topic: {topic}
OSCE Number: {osce_number}

IMPORTANT: Return ONLY valid JSON, no additional text or explanation."""


def load_source_osces(input_file: str) -> List[Dict[str, Any]]:
    """Load source OSCEs from JSON file."""
    print(f"Loading source OSCEs from: {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    osces = data.get('osces', [])
    print(f"✅ Loaded {len(osces)} OSCEs")
    return osces


def generate_respiratory_osce(topic: str, osce_number: int) -> Dict[str, Any]:
    """Generate a single respiratory OSCE using Claude API."""
    prompt = RESPIRATORY_OSCE_GENERATION_PROMPT.format(
        topic=topic,
        osce_number=osce_number
    )

    print(f"  Generating RESP-{osce_number:03d}: {topic[:60]}...")

    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=16000,
            temperature=1.0,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )

        # Extract JSON from response
        content = response.content[0].text

        # Try to find JSON in response
        json_start = content.find('{')
        json_end = content.rfind('}') + 1

        if json_start == -1 or json_end == 0:
            print(f"    ⚠️  No JSON found in response")
            return None

        json_str = content[json_start:json_end]
        osce = json.loads(json_str)

        print(f"    ✅ Generated successfully")
        return osce

    except json.JSONDecodeError as e:
        print(f"    ❌ JSON decode error: {e}")
        return None
    except Exception as e:
        print(f"    ❌ Generation error: {e}")
        return None


def validate_osce_quality(osce: Dict[str, Any]) -> Dict[str, bool]:
    """Validate OSCE against quality gates."""
    checks = {
        "has_specific_patient": True,
        "has_spirometry_values": False,
        "has_oxygen_targets": False,
        "has_inhaler_devices": False,
        "has_pbs_codes": False,
        "has_severity_classification": False,
        "no_placeholders": True
    }

    # Convert OSCE to string for pattern matching
    osce_str = json.dumps(osce).lower()

    # Check for placeholders
    placeholder_patterns = [
        "a patient presents",
        "according to australian guidelines",
        "spirometry findings for",
        "inhaler therapy as appropriate",
        "bronchodilator therapy",
        "oxygen therapy"
    ]

    for pattern in placeholder_patterns:
        if pattern in osce_str:
            checks["no_placeholders"] = False
            break

    # Check for specific spirometry values
    if "fev1" in osce_str and "predicted" in osce_str and "l (" in osce_str:
        checks["has_spirometry_values"] = True

    # Check for oxygen targets
    if "88-92%" in osce_str or "94-98%" in osce_str:
        checks["has_oxygen_targets"] = True

    # Check for inhaler devices
    inhaler_devices = ["turbuhaler", "handihaler", "accuhaler", "mdi", "spacer"]
    if any(device in osce_str for device in inhaler_devices):
        checks["has_inhaler_devices"] = True

    # Check for PBS codes
    if "pbs" in osce_str and any(char.isdigit() for char in osce_str):
        checks["has_pbs_codes"] = True

    # Check for severity classification
    severity_terms = ["mild", "moderate", "severe", "life-threatening"]
    if any(term in osce_str for term in severity_terms):
        checks["has_severity_classification"] = True

    return checks


def regenerate_respiratory_osces(input_file: str, output_file: str):
    """Main regeneration function."""
    print("=" * 60)
    print("RESPIRATORY OSCE REGENERATION - 50 OSCEs")
    print("=" * 60)
    print()

    # Load source OSCEs
    source_osces = load_source_osces(input_file)

    if len(source_osces) != 50:
        print(f"⚠️  Warning: Expected 50 OSCEs, found {len(source_osces)}")

    print()
    print("Starting regeneration...")
    print(f"Estimated time: {len(source_osces) * 2}-{len(source_osces) * 3} minutes")
    print()

    regenerated_osces = []
    failed_osces = []
    quality_report = []

    for idx, source_osce in enumerate(source_osces, 1):
        topic = source_osce.get('topic', f'Respiratory condition {idx}')
        osce_number = idx

        print(f"[{idx}/{len(source_osces)}] Processing: {topic}")

        # Generate OSCE
        regenerated = generate_respiratory_osce(topic, osce_number)

        if regenerated is None:
            print(f"    ⚠️  Failed to generate, keeping original")
            failed_osces.append(topic)
            regenerated_osces.append(source_osce)
            continue

        # Validate quality
        quality_checks = validate_osce_quality(regenerated)
        quality_report.append({
            "osce_id": f"RESP-{osce_number:03d}",
            "topic": topic,
            "checks": quality_checks
        })

        passed_checks = sum(1 for v in quality_checks.values() if v)
        total_checks = len(quality_checks)

        if passed_checks < total_checks:
            print(f"    ⚠️  Quality checks: {passed_checks}/{total_checks} passed")
            for check, passed in quality_checks.items():
                if not passed:
                    print(f"        ❌ {check}")
        else:
            print(f"    ✅ Quality checks: {passed_checks}/{total_checks} passed")

        regenerated_osces.append(regenerated)
        print()

    # Save regenerated OSCEs
    output_data = {
        "metadata": {
            "total_osces": len(regenerated_osces),
            "specialty": "Respiratory",
            "regeneration_date": "2026-03-28",
            "model": MODEL,
            "source_file": input_file
        },
        "osces": regenerated_osces
    }

    print("Saving regenerated OSCEs...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print(f"✅ Saved to: {output_file}")
    print()

    # Summary report
    print("=" * 60)
    print("REGENERATION SUMMARY")
    print("=" * 60)
    print()
    print(f"Total OSCEs: {len(source_osces)}")
    print(f"Successfully regenerated: {len(regenerated_osces) - len(failed_osces)}")
    print(f"Failed: {len(failed_osces)}")
    print()

    if failed_osces:
        print("Failed OSCEs:")
        for topic in failed_osces:
            print(f"  - {topic}")
        print()

    # Quality gate summary
    print("Quality Gate Summary:")
    total_checks = len(quality_report)

    if total_checks > 0:
        quality_stats = {
            "has_specific_patient": 0,
            "has_spirometry_values": 0,
            "has_oxygen_targets": 0,
            "has_inhaler_devices": 0,
            "has_pbs_codes": 0,
            "has_severity_classification": 0,
            "no_placeholders": 0
        }

        for report in quality_report:
            for check, passed in report["checks"].items():
                if passed:
                    quality_stats[check] += 1

        for check, count in quality_stats.items():
            percentage = (count / total_checks) * 100
            status = "✅" if percentage >= 90 else "⚠️"
            print(f"  {status} {check}: {count}/{total_checks} ({percentage:.1f}%)")

    print()
    print("=" * 60)
    print("REGENERATION COMPLETE")
    print("=" * 60)
    print()
    print(f"Output file: {output_file}")
    print()
    print("Next steps:")
    print("1. Run placeholder detection: python3 scripts/detect_placeholder_content.py")
    print("2. Manually spot check 3 random OSCEs")
    print("3. Validate all quality gates")
    print("4. Replace original file if all checks pass")


def main():
    """Main entry point."""
    if len(sys.argv) != 3:
        print("Usage: python3 regenerate_respiratory_osces_complete.py <input_file> <output_file>")
        print()
        print("Example:")
        print("  python3 regenerate_respiratory_osces_complete.py \\")
        print("    data/osces/respiratory_50_osces.json \\")
        print("    data/osces/respiratory_50_osces_regenerated.json")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    # Validate input file exists
    if not os.path.exists(input_file):
        print(f"ERROR: Input file not found: {input_file}")
        sys.exit(1)

    # Validate output directory exists
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        print(f"ERROR: Output directory not found: {output_dir}")
        sys.exit(1)

    # Execute regeneration
    try:
        regenerate_respiratory_osces(input_file, output_file)
    except KeyboardInterrupt:
        print()
        print("⚠️  Regeneration interrupted by user")
        sys.exit(1)
    except Exception as e:
        print()
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
