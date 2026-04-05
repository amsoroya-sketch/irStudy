#!/usr/bin/env python3
"""
Regenerate respiratory OSCEs with full clinical content.
Uses Claude CLI for generation.

Usage:
    python3 regenerate_respiratory_osces.py data/osces/respiratory_50_osces.json output.json

Requirements:
    - Claude CLI installed and configured
    - Focus: Asthma, COPD, pneumonia, PE, spirometry interpretation
"""

import json
import sys
import subprocess
from pathlib import Path
from typing import Dict
from datetime import datetime

# Respiratory OSCE generation prompt
RESPIRATORY_OSCE_PROMPT = """You are a medical education expert creating respiratory OSCEs for Australian AMC Clinical Examination preparation.

Generate a complete OSCE station with full clinical content (NOT placeholder templates).

**MANDATORY REQUIREMENTS:**

1. **Complete Clinical Scenario**:
   - Specific patient demographics (age, gender, smoking history)
   - Detailed presenting complaint with timeline
   - Specific examination findings (NOT "examination findings for...")
   - Spirometry values if applicable (specific FEV1/FVC values)

2. **Respiratory-Specific Content**:
   - **Spirometry interpretation**: Specific values with pattern
     - Example: "FEV1 1.2L (40% predicted), FVC 2.8L (85% predicted), FEV1/FVC 0.43 (obstruction pattern)"
   - **Oxygen targets**:
     - COPD: 88-92% SpO2 (avoid hyperoxia → CO2 retention)
     - Non-COPD: 94-98% SpO2
   - **Inhaler devices**: Specific devices with technique
     - MDI + spacer (salbutamol)
     - Turbuhaler (budesonide/formoterol)
     - HandiHaler (tiotropium)
     - Accuhaler (fluticasone/salmeterol)
   - **Medications**: Specific doses + PBS codes
     - Example: "Salbutamol 200mcg 2 puffs PRN via MDI + spacer, PBS 8333L"
     - Example: "Budesonide/formoterol 200/6 Turbuhaler 2 puffs BD, PBS 8097K"
   - **Exacerbation severity**: Mild/moderate/severe criteria, hospital vs home treatment

3. **Australian Context (MANDATORY)**:
   - National Asthma Council guidelines
   - COPD-X Guidelines (Australian and New Zealand)
   - Thoracic Society of Australia and New Zealand (TSANZ)
   - eTG: Respiratory chapter
   - PBS restrictions (e.g., "ICS/LABA requires documented asthma for PBS")
   - MBS items (e.g., "Spirometry - MBS 11506")

4. **Complete Management Plans**:
   - Acute management: Specific medications with doses, oxygen therapy, monitoring
   - Investigations: Spirometry, CXR, ABG, sputum culture, CTPA if PE suspected
   - Long-term management: Inhaler technique, action plans, pulmonary rehabilitation
   - Safety netting: Warning signs for deterioration, when to call ambulance

**TOPIC FOR THIS OSCE:**
{topic}

**SUBTOPIC:**
{subtopic}

**DIFFICULTY:**
{difficulty}

**EXAMPLE STRUCTURE:**

```json
{{
  "id": "RESP-OSCE-{topic_code}-{timestamp}",
  "station_number": "RESP-{number}",
  "station_type": "Clinical Assessment / Emergency Management",
  "specialty": "Respiratory",
  "topic": "{topic}",
  "time_limit": 8,
  "difficulty": "{difficulty}",
  "candidate_instructions": "[SPECIFIC: '28-year-old woman presents to ED with severe shortness of breath and wheeze. Known asthma, ran out of preventer 2 weeks ago. Unable to speak full sentences.' NOT 'A patient presents with asthma exacerbation']",
  "actor_instructions": "[COMPLETE: 'You are a 28-year-old office worker with asthma since childhood. You ran out of your brown puffer (Symbicort) 2 weeks ago and haven't had time to get prescription refilled. Over last 2 days, increasing wheeze and breathlessness. Today woke at 3am unable to breathe, blue puffer (salbutamol) not helping (used 20 puffs in last 4 hours). You can only speak 3-4 words between breaths. You are scared and anxious. No fever, no chest pain, no cough.']",
  "examiner_instructions": "[What to observe: Rapid severity assessment (severe exacerbation), appropriate oxygen therapy (target 94-98%), nebulized bronchodilators + ipratropium, steroids (prednisolone 50mg or hydrocortisone 100mg IV), reassessment after 20 minutes]",
  "marking_criteria": {{
    "introduction_assessment": {{"marks": 1, "criteria": "Rapid introduction, recognizes emergency, positions patient upright"}},
    "severity_assessment": {{"marks": 2, "criteria": "Correctly identifies SEVERE: unable to speak sentences, tachypnea >25, tachycardia >110, SpO2 <90%"}},
    "oxygen_therapy": {{"marks": 1, "criteria": "High-flow oxygen to maintain SpO2 94-98% (NOT 88-92%, this is non-COPD)"}},
    "bronchodilator_therapy": {{"marks": 3, "criteria": "Salbutamol 5mg nebulized (continuous if life-threatening) + Ipratropium 500mcg nebulized"}},
    "corticosteroids": {{"marks": 2, "criteria": "Prednisolone 50mg PO OR Hydrocortisone 100mg IV (if cannot swallow)"}},
    "monitoring": {{"marks": 1, "criteria": "Continuous SpO2, repeat peak flow, clinical reassessment at 20 minutes"}},
    "escalation_criteria": {{"marks": 2, "criteria": "Discusses ICU criteria: exhaustion, silent chest, falling SpO2 despite treatment, pCO2 rising"}},
    "discharge_planning": {{"marks": 2, "criteria": "If improves: 5-7 days prednisolone, restart preventers (ICS/LABA), written asthma action plan, GP follow-up"}},
    "communication": {{"marks": 1, "criteria": "Reassures patient, clear instructions, checks understanding"}},
    "total": 15
  }},
  "sample_answer": {{
    "history_summary": "28-year-old woman with known asthma presenting with acute severe exacerbation. Stopped preventer (budesonide/formoterol) 2 weeks ago due to running out. Progressive dyspnea over 2 days, woke at 3am unable to breathe. Salbutamol ineffective (20 puffs in 4 hours). Unable to speak full sentences. No triggers identified (no URTI, no allergen exposure). No previous ICU admissions.",
    "examination_findings": "Distressed, sitting forward, unable to complete sentences. RR 32/min, HR 125 regular, BP 135/85, SpO2 89% room air. Using accessory muscles. Trachea central. Chest: bilateral expiratory wheeze throughout, prolonged expiratory phase. Peak flow 150 L/min (personal best 450 L/min = 33% predicted).",
    "severity_classification": "ACUTE SEVERE ASTHMA (per National Asthma Council):\n- Unable to speak sentences (can only speak 3-4 words)\n- RR >25/min (32/min)\n- HR >110/min (125/min)\n- SpO2 <90% (89% room air)\n- Peak flow 33% predicted (<50% = severe)\n\nNOT life-threatening (no silent chest, no exhaustion, no altered consciousness, no bradycardia)",
    "provisional_diagnosis": "Acute severe asthma exacerbation",
    "differential_diagnosis": [
      "Life-threatening asthma (if deteriorates: silent chest, exhaustion, SpO2 <85%)",
      "Pneumonia (but no fever, no productive cough)",
      "Pneumothorax (but trachea central, bilateral wheeze)",
      "Pulmonary embolism (but no risk factors, no chest pain, bilateral wheeze)"
    ],
    "immediate_management": [
      "Sit patient upright, call for help",
      "High-flow oxygen via Hudson mask 8-10L/min to maintain SpO2 94-98% (monitor closely)",
      "Salbutamol 5mg nebulized with oxygen (NOT air), repeat every 20 minutes. If life-threatening: continuous nebulization",
      "Ipratropium 500mcg nebulized (combine with salbutamol), repeat every 20 minutes for first hour",
      "Prednisolone 50mg PO stat OR Hydrocortisone 100mg IV if cannot swallow (PBS 1234K)",
      "IV access, FBC, UEC (check K+ - salbutamol causes hypokalemia)",
      "ABG if SpO2 not improving or concerns about CO2 retention (normal pCO2 = good, rising pCO2 = exhaustion)",
      "CXR (exclude pneumothorax, pneumonia)",
      "Continuous SpO2 monitoring, repeat peak flow at 20 minutes",
      "Reassess at 20 minutes: If improving → continue treatment. If not improving or deteriorating → senior review, consider ICU"
    ],
    "icu_criteria": [
      "Exhaustion (unable to maintain effort of breathing)",
      "Altered consciousness or confusion",
      "Silent chest (no wheeze despite respiratory effort = critical)",
      "SpO2 <85% despite high-flow oxygen",
      "pCO2 >45 mmHg (rising CO2 = respiratory failure)",
      "Bradycardia (indicates imminent arrest)"
    ],
    "discharge_planning": [
      "If improves: Prednisolone 50mg daily for 5-7 days (no tapering needed for short course)",
      "Restart preventer: Budesonide/formoterol 200/6 Turbuhaler 2 puffs twice daily, PBS 8097K",
      "Reliever: Salbutamol 100mcg MDI + spacer 2-4 puffs PRN (max 8 puffs/day), PBS 8333L",
      "Written Asthma Action Plan (National Asthma Council template)",
      "Inhaler technique review (spacer for MDI, Turbuhaler technique)",
      "Trigger avoidance education",
      "GP follow-up in 2-7 days (MBS 23, 36, or 44)",
      "Consider referral to respiratory physician if frequent exacerbations (>2/year)",
      "Safety netting: Return if worsening breathlessness, chest pain, fever, or if salbutamol needed >8 puffs/day"
    ]
  }},
  "learning_points": [
    "Asthma severity: Severe if unable to speak sentences, RR >25, HR >110, SpO2 <90%, peak flow <50% predicted",
    "Oxygen targets: 94-98% for asthma (NOT 88-92%, that's for COPD with chronic CO2 retention)",
    "Combination therapy: Salbutamol + ipratropium more effective than salbutamol alone in severe asthma",
    "Steroids: Prednisolone 50mg for 5-7 days (no tapering needed for short courses <2 weeks)",
    "Peak flow: Personal best more useful than predicted values (varies by height, age, gender)",
    "National Asthma Council: All adults with asthma should have written Asthma Action Plan",
    "ICU transfer: Silent chest is CRITICAL (indicates exhaustion, not improvement)"
  ],
  "australian_context": true,
  "australian_guidelines": [
    "National Asthma Council: Australian Asthma Handbook",
    "Therapeutic Guidelines: Respiratory - Acute asthma",
    "TSANZ: Guidelines for acute asthma management"
  ]
}}
```

**CRITICAL - NO PLACEHOLDERS:**
- ❌ NO "A patient presents with shortness of breath"
- ❌ NO "Spirometry findings for COPD"
- ❌ NO "According to Australian guidelines..."
- ✅ YES "28-year-old office worker with asthma, ran out of Symbicort 2 weeks ago, unable to speak full sentences"
- ✅ YES "FEV1 1.2L (40% predicted), FEV1/FVC 0.43 (obstruction), no reversibility"
- ✅ YES "Salbutamol 5mg nebulized Q20min, Ipratropium 500mcg nebulized, Prednisolone 50mg PO, PBS 8097K"

**OUTPUT INSTRUCTIONS:**
Return ONLY valid JSON. No markdown, no explanations. Just the JSON object.

Generate the complete respiratory OSCE now:"""


def generate_respiratory_osce(topic: str, subtopic: str, difficulty: str, number: int) -> Dict:
    """Generate a single respiratory OSCE using Claude CLI."""

    topic_code = topic.replace(" ", "-").replace("/", "-").upper()[:10]
    timestamp = datetime.now().strftime("%Y%m%d")

    prompt = RESPIRATORY_OSCE_PROMPT.format(
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

        # Extract JSON
        if "```json" in response_text:
            json_start = response_text.find("```json") + 7
            json_end = response_text.find("```", json_start)
            json_str = response_text[json_start:json_end].strip()
        elif response_text.startswith("{"):
            json_str = response_text
        else:
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
            else:
                print(f"  ❌ Could not find JSON in response")
                return None

        osce = json.loads(json_str)

        osce["metadata"] = {
            "generated_date": datetime.now().isoformat(),
            "generator": "regenerate_respiratory_osces.py + Claude CLI",
            "constraint_applied": "Respiratory OSCE Requirements"
        }

        print(f"  ✅ Generated successfully")
        return osce

    except Exception as e:
        print(f"  ❌ Generation failed: {str(e)}")
        return None


def regenerate_osces_file(input_path: Path, output_path: Path):
    """Regenerate all respiratory OSCEs in a file."""

    print(f"\n{'='*80}")
    print(f"Respiratory OSCE Regeneration: {input_path.name}")
    print(f"{'='*80}\n")

    with open(input_path, 'r') as f:
        original_data = json.load(f)

    original_osces = original_data.get("osces", [])
    total = len(original_osces)

    print(f"Total OSCEs to regenerate: {total}")

    regenerated_osces = []
    success_count = 0

    for idx, original_osce in enumerate(original_osces, 1):
        topic = original_osce.get("topic", "Unknown Topic")
        subtopic = original_osce.get("subtopic", "")
        difficulty = original_osce.get("difficulty", "medium")

        print(f"\n[{idx}/{total}] Topic: {topic}")

        new_osce = generate_respiratory_osce(topic, subtopic, difficulty, idx)

        if new_osce:
            regenerated_osces.append(new_osce)
            success_count += 1
        else:
            print(f"  ⚠️ Skipping due to generation failure")

    output_data = {
        "metadata": {
            "specialty": "Respiratory",
            "generation_date": datetime.now().isoformat(),
            "generator": "regenerate_respiratory_osces.py + Claude CLI",
            "total_osces": success_count,
            "source_file": str(input_path),
            "regeneration_status": "COMPLETE" if success_count == total else "PARTIAL"
        },
        "osces": regenerated_osces
    }

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

    if success_count > 0:
        print("Running placeholder detection...")
        subprocess.run(
            ['python3', 'scripts/detect_placeholder_content.py', str(output_path)],
            cwd=Path.cwd()
        )

    return success_count == total


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 regenerate_respiratory_osces.py <input.json> <output.json>")
        sys.exit(1)

    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2])

    if not input_file.exists():
        print(f"ERROR: Input file not found: {input_file}")
        sys.exit(1)

    # Create backup
    backup_dir = Path("data/osces/backups") / datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup_path = backup_dir / input_file.name

    import shutil
    shutil.copy2(input_file, backup_path)
    print(f"✅ Backup created: {backup_path}")

    success = regenerate_osces_file(input_file, output_file)
    sys.exit(0 if success else 1)
