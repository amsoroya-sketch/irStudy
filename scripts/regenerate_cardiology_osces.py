#!/usr/bin/env python3
"""
Regenerate cardiology OSCEs with full clinical content.
Uses Claude CLI for generation.

Usage:
    python3 regenerate_cardiology_osces.py data/osces/cardiology_50_osces.json output.json

Requirements:
    - Claude CLI installed and configured
    - Focus: STEMI/NSTEMI, heart failure, arrhythmias, ECG interpretation
"""

import json
import sys
import subprocess
from pathlib import Path
from typing import Dict
from datetime import datetime

# Cardiology OSCE generation prompt
CARDIOLOGY_OSCE_PROMPT = """You are a medical education expert creating cardiology OSCEs for Australian AMC Clinical Examination preparation.

Generate a complete OSCE station with full clinical content (NOT placeholder templates).

**MANDATORY REQUIREMENTS:**

1. **Complete Clinical Scenario**:
   - Specific patient demographics (age, gender, risk factors)
   - Detailed presenting complaint with timeline
   - Specific examination findings (NOT "examination findings for...")
   - ECG findings if applicable (specific changes, not generic)

2. **Cardiology-Specific Content**:
   - **ECG interpretation**: Specific findings (e.g., "ST elevation 2mm in leads II, III, aVF indicating inferior STEMI")
   - **Medications**: Specific doses + PBS codes
     - Example: "Aspirin 300mg PO stat, Ticagrelor 180mg PO stat, PBS 8721K"
     - Example: "Metoprolol 25mg BD, Ramipril 2.5mg daily, PBS 2933K"
   - **STEMI/NSTEMI**: Door-to-balloon time <90min, dual antiplatelet, PCI vs thrombolysis criteria
   - **Heart Failure**: NYHA class, BNP levels, fluid restriction (1-1.5L/day), medication titration
   - **Arrhythmias**: Specific rhythms (AF with RVR 140bpm), CHA2DS2-VASc score, HASBLED score
   - **Risk stratification**: Framingham score, GRACE score, TIMI score

3. **Australian Context (MANDATORY)**:
   - National Heart Foundation guidelines
   - Cardiac Society of Australia and New Zealand (CSANZ) recommendations
   - eTG: Cardiovascular chapter
   - PBS restrictions (e.g., "NOACs require CHA2DS2-VASc ≥2 for PBS")
   - MBS items for procedures (e.g., "Echocardiogram - MBS 55111")

4. **Complete Management Plans**:
   - Acute management: Specific medications with doses and timing
   - Investigations: Specific tests (troponin, BNP, echocardiogram, angiography)
   - Long-term management: Cardiac rehabilitation, lifestyle modifications, medication titration
   - Safety netting: Warning signs, when to call ambulance

**TOPIC FOR THIS OSCE:**
{topic}

**SUBTOPIC:**
{subtopic}

**DIFFICULTY:**
{difficulty}

**EXAMPLE STRUCTURE:**

```json
{{
  "id": "CARD-OSCE-{topic_code}-{timestamp}",
  "station_number": "CARD-{number}",
  "station_type": "Clinical Assessment / Emergency Management",
  "specialty": "Cardiology",
  "topic": "{topic}",
  "time_limit": 8,
  "difficulty": "{difficulty}",
  "candidate_instructions": "[SPECIFIC: '58-year-old man presents with 2 hours of central crushing chest pain radiating to left arm. Pain 8/10, not relieved by GTN. Known hypertension, smoker.' NOT 'A patient presents with chest pain']",
  "actor_instructions": "[COMPLETE: 'You are a 58-year-old taxi driver. You woke at 5am with severe crushing central chest pain radiating to your left arm and jaw. You are sweaty and nauseous. Your father died of heart attack at age 62. You smoke 20 cigarettes daily for 35 years. You take amlodipine for high blood pressure but often forget doses. You are scared you are having a heart attack.']",
  "examiner_instructions": "[What to observe: Rapid STEMI recognition, appropriate initial management (MONA + dual antiplatelet), timely activation of cath lab, door-to-balloon <90min discussion]",
  "marking_criteria": {{
    "introduction_assessment": {{"marks": 1, "criteria": "Rapid introduction, recognizes emergency, calls for help"}},
    "focused_history": {{"marks": 2, "criteria": "SOCRATES pain assessment, cardiac risk factors, medications"}},
    "examination": {{"marks": 1, "criteria": "Brief focused exam: vitals, cardiac auscultation, signs of heart failure"}},
    "ecg_interpretation": {{"marks": 2, "criteria": "Correctly identifies STEMI (ST elevation >2mm in contiguous leads)"}},
    "immediate_management": {{"marks": 3, "criteria": "MONA protocol (Morphine, Oxygen if SpO2<94%, Nitrates, Aspirin), dual antiplatelet (ticagrelor/clopidogrel), anticoagulation (fondaparinux/enoxaparin)"}},
    "reperfusion_strategy": {{"marks": 2, "criteria": "Activates cath lab for primary PCI (door-to-balloon <90min target) OR discusses thrombolysis if PCI unavailable"}},
    "investigations": {{"marks": 1, "criteria": "Troponin, FBC, UEC, coagulation, lipids, CXR, echocardiogram"}},
    "secondary_prevention": {{"marks": 2, "criteria": "Discusses long-term: dual antiplatelet 12 months, high-intensity statin, ACE inhibitor, beta-blocker, cardiac rehab, smoking cessation"}},
    "communication": {{"marks": 1, "criteria": "Explains diagnosis clearly, reassures patient, addresses concerns"}},
    "total": 15
  }},
  "sample_answer": {{
    "history_summary": "58-year-old man with 2-hour history of crushing central chest pain (8/10) radiating to left arm and jaw. Pain started at rest, not relieved by GTN. Associated sweating, nausea. Risk factors: 35 pack-year smoker, hypertension (poorly controlled), family history (father MI at 62). Known medications: amlodipine 5mg daily (poor adherence).",
    "examination_findings": "Distressed, sweaty, pale. BP 155/95, HR 98 regular, SpO2 96% room air. JVP not elevated. Heart sounds: dual, no murmurs. Chest clear. No peripheral edema.",
    "ecg_findings": "Sinus rhythm 98bpm. ST elevation 3mm in leads II, III, aVF (inferior STEMI). Reciprocal ST depression in V1-V3. Q waves in III.",
    "provisional_diagnosis": "Acute inferior STEMI (likely RCA occlusion)",
    "differential_diagnosis": [
      "NSTEMI (but ST elevation makes STEMI more likely)",
      "Aortic dissection (consider if pain maximal at onset, tearing quality)",
      "Pulmonary embolism (but ST elevation pattern not typical)"
    ],
    "immediate_management": [
      "Call for help, activate cath lab (target door-to-balloon <90 minutes)",
      "IV access x2, oxygen if SpO2 <94% (target 94-98%)",
      "Aspirin 300mg PO stat (chewed)",
      "Ticagrelor 180mg PO stat (preferred over clopidogrel per eTG) PBS 8721K",
      "Morphine 2.5-5mg IV + metoclopramide 10mg IV (pain + nausea)",
      "GTN 300-600mcg sublingual (if BP >90 systolic, no RV infarct)",
      "Fondaparinux 2.5mg SC stat (anticoagulation) PBS 8858P",
      "Continuous ECG monitoring, repeat ECG if pain recurs",
      "Troponin (will be elevated), FBC, UEC, coagulation, lipids",
      "Transfer to cath lab for primary PCI (target <90min from first medical contact)"
    ],
    "ongoing_management": [
      "Post-PCI: Dual antiplatelet therapy (aspirin 100mg daily + ticagrelor 90mg BD) for 12 months",
      "High-intensity statin: Atorvastatin 80mg nocte, PBS 8086M",
      "ACE inhibitor: Ramipril 2.5mg daily, titrate to 10mg (improves mortality post-MI), PBS 8624K",
      "Beta-blocker: Metoprolol 25mg BD, titrate to 100mg BD (improves mortality), PBS 2933K",
      "Cardiac rehabilitation referral (MBS 81110)",
      "Smoking cessation counseling + nicotine replacement therapy (PBS 4220K)",
      "Dietary advice: Mediterranean diet, sodium restriction <2g/day",
      "Monitor: Echocardiogram (assess LV function), repeat lipids in 6 weeks (target LDL <1.8)",
      "Review in 2 weeks, then ongoing cardiology follow-up"
    ]
  }},
  "learning_points": [
    "STEMI diagnosis: ST elevation ≥2mm in contiguous chest leads OR ≥1mm in limb leads",
    "Immediate management: Aspirin 300mg + ticagrelor 180mg (NOT clopidogrel per Australian guidelines)",
    "Door-to-balloon time <90 minutes (or <60 min if <3 hours from symptom onset)",
    "RV infarct (inferior STEMI): Avoid nitrates/morphine (preload-dependent), give IV fluids",
    "Post-MI medications: DAPT 12 months, high-intensity statin, ACE inhibitor, beta-blocker (ABCD)",
    "National Heart Foundation: Secondary prevention guidelines, cardiac rehab improves outcomes by 25%"
  ],
  "australian_context": true,
  "australian_guidelines": [
    "National Heart Foundation: Acute Coronary Syndromes Guidelines",
    "CSANZ: STEMI Management Guidelines",
    "Therapeutic Guidelines: Cardiovascular - Acute coronary syndrome"
  ]
}}
```

**CRITICAL - NO PLACEHOLDERS:**
- ❌ NO "A patient presents with chest pain"
- ❌ NO "ECG findings for STEMI"
- ❌ NO "According to Australian guidelines..."
- ✅ YES "58-year-old taxi driver with 2-hour crushing chest pain radiating to left arm, 35 pack-year smoker"
- ✅ YES "ST elevation 3mm in leads II, III, aVF (inferior STEMI)"
- ✅ YES "Aspirin 300mg PO stat, Ticagrelor 180mg PO stat, PBS 8721K"

**OUTPUT INSTRUCTIONS:**
Return ONLY valid JSON. No markdown, no explanations. Just the JSON object.

Generate the complete cardiology OSCE now:"""


def generate_cardiology_osce(topic: str, subtopic: str, difficulty: str, number: int) -> Dict:
    """Generate a single cardiology OSCE using Claude CLI."""

    topic_code = topic.replace(" ", "-").replace("/", "-").upper()[:10]
    timestamp = datetime.now().strftime("%Y%m%d")

    prompt = CARDIOLOGY_OSCE_PROMPT.format(
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
            "generator": "regenerate_cardiology_osces.py + Claude CLI",
            "constraint_applied": "Cardiology OSCE Requirements"
        }

        print(f"  ✅ Generated successfully")
        return osce

    except Exception as e:
        print(f"  ❌ Generation failed: {str(e)}")
        return None


def regenerate_osces_file(input_path: Path, output_path: Path):
    """Regenerate all cardiology OSCEs in a file."""

    print(f"\n{'='*80}")
    print(f"Cardiology OSCE Regeneration: {input_path.name}")
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

        new_osce = generate_cardiology_osce(topic, subtopic, difficulty, idx)

        if new_osce:
            regenerated_osces.append(new_osce)
            success_count += 1
        else:
            print(f"  ⚠️ Skipping due to generation failure")

    output_data = {
        "metadata": {
            "specialty": "Cardiology",
            "generation_date": datetime.now().isoformat(),
            "generator": "regenerate_cardiology_osces.py + Claude CLI",
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
        print("Usage: python3 regenerate_cardiology_osces.py <input.json> <output.json>")
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
