#!/usr/bin/env python3
"""
Cardiology OSCE Regeneration Script - Complete Clinical Content Generation
Regenerates 50 cardiology OSCEs with ZERO placeholders, full Australian clinical accuracy

CRITICAL MEDICAL CONSTRAINTS (EMBEDDED IN ALL PROMPTS):
1. ECG findings: SPECIFIC measurements (NOT "ECG findings for STEMI")
2. Medications: Doses + PBS codes (NOT "as per guidelines")
3. STEMI protocol: Door-to-balloon <90 min (explicit timelines)
4. Australian guidelines: Heart Foundation, CSANZ, eTG (NOT US guidelines)
5. NO generic phrases: "A patient presents...", "According to guidelines..."

Usage:
    python3 scripts/regenerate_cardiology_osces_complete.py \\
        data/osces/cardiology_50_osces.json \\
        data/osces/cardiology_50_osces_regenerated.json
"""

import json
import os
import sys
import time
from typing import Dict, List, Any, Optional
from anthropic import Anthropic

# Initialize Claude client
client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

# Model configuration
CLAUDE_MODEL = "claude-sonnet-4-20250514"
MAX_TOKENS = 4096
TEMPERATURE = 0.7  # Balance between clinical accuracy and natural variation

def load_gold_standard_template() -> Dict[str, Any]:
    """Load psychiatry OSCE as gold standard structure template"""
    template_path = "data/osces/psychiatry_week1_osces.json"

    try:
        with open(template_path, 'r') as f:
            psych_osces = json.load(f)

        if psych_osces and len(psych_osces) > 0:
            print(f"✅ Loaded gold standard template from {template_path}")
            return psych_osces[0]
        else:
            print(f"⚠️  Gold standard template empty, using default structure")
            return {}

    except FileNotFoundError:
        print(f"⚠️  Gold standard template not found at {template_path}")
        return {}
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing gold standard template: {e}")
        return {}

def create_cardiology_prompt(osce_topic: str, osce_title: str) -> str:
    """
    Create comprehensive prompt for Claude to generate complete cardiology OSCE

    CRITICAL: This prompt embeds ALL medical constraints to ensure ZERO placeholders
    """

    return f"""You are a Senior Consultant Cardiologist with 15+ years of experience at a major Australian teaching hospital and an AMC Clinical Examination expert examiner.

Your task: Generate a COMPLETE, CLINICALLY ACCURATE cardiology OSCE station for Australian medical students preparing for AMC Clinical Examination.

TOPIC: {osce_topic}
TITLE: {osce_title}

═══════════════════════════════════════════════════════════════════
CRITICAL REQUIREMENTS (ZERO-TOLERANCE - MUST FOLLOW EXACTLY)
═══════════════════════════════════════════════════════════════════

1. ECG INTERPRETATION (if applicable to this topic):

   ✅ CORRECT EXAMPLES:
   - "ST elevation 3mm in leads II, III, aVF with reciprocal ST depression V1-V3 (inferior STEMI, likely RCA occlusion)"
   - "Atrial fibrillation with rapid ventricular response 145bpm, irregularly irregular rhythm, no discrete P waves"
   - "Sinus bradycardia 48bpm, 1st degree AV block (PR 240ms), left axis deviation, Q waves V1-V3 (old anteroseptal MI)"

   ❌ FORBIDDEN (NEVER USE):
   - "ECG findings for STEMI"
   - "ECG changes consistent with myocardial infarction"
   - "Typical ECG pattern"

2. MEDICATIONS (MANDATORY FOR ALL MANAGEMENT):

   ✅ CORRECT FORMAT:
   - "Aspirin 300mg PO stat (chewed), then 100mg daily - PBS 8053K"
   - "Ticagrelor 180mg PO stat, then 90mg BD for 12 months - PBS 8721K (preferred over clopidogrel per eTG)"
   - "Metoprolol 25mg BD, titrate to 100mg BD (target HR 50-60) - PBS 2933K"
   - "Atorvastatin 80mg nocte (high-intensity statin, target LDL <1.8) - PBS 8086M"
   - "Ramipril 2.5mg daily, titrate to 10mg (mortality benefit post-MI) - PBS 8624K"

   ❌ FORBIDDEN (NEVER USE):
   - "Dual antiplatelet therapy as per guidelines"
   - "Beta-blocker as appropriate"
   - "Statin therapy"
   - "ACEI or ARB"

3. STEMI/ACS PROTOCOLS (if applicable):

   MUST INCLUDE:
   - Door-to-balloon time: "<90 minutes" (specific target, not "as soon as possible")
   - Reperfusion strategy: "Primary PCI preferred. If PCI unavailable >120 minutes, consider thrombolysis (tenecteplase weight-based: 30-50mg IV bolus based on weight, contraindications: recent surgery <3 weeks, bleeding disorder, previous hemorrhagic stroke, ischemic stroke <6 months)"
   - Risk stratification: "GRACE score >140 = high risk" or "TIMI score ≥3 = consider early invasive strategy"
   - For AF: "CHA2DS2-VASc score: CHF(1), Hypertension(1), Age≥75(2), Diabetes(1), Stroke/TIA(2), Vascular disease(1), Age 65-74(1), Sex female(1). Score ≥2 men or ≥3 women = anticoagulation indicated"
   - Bleeding risk: "HASBLED score: Hypertension, Abnormal renal/liver, Stroke, Bleeding, Labile INR, Elderly, Drugs/alcohol. Score ≥3 = high bleeding risk"

4. AUSTRALIAN GUIDELINES (MANDATORY REFERENCES):

   MUST CITE:
   - "National Heart Foundation of Australia - Acute Coronary Syndromes Guidelines 2016"
   - "Cardiac Society of Australia and New Zealand (CSANZ) - [specific guideline]"
   - "eTG: Cardiovascular - [specific chapter, e.g., 'Acute coronary syndromes']"
   - PBS restrictions: "NOACs require CHA2DS2-VASc ≥2 for PBS subsidy" or "High-intensity statin PBS restricted to CVD secondary prevention"
   - MBS items: "Echocardiogram - MBS 55111", "Cardiac rehabilitation - MBS 81110", "Coronary angiogram - MBS 38200"

5. NO GENERIC PATIENT DESCRIPTIONS (MUST BE SPECIFIC):

   ❌ FORBIDDEN:
   - "A patient presents with chest pain"
   - "A 60-year-old man with cardiac risk factors"
   - "According to Australian guidelines for management"
   - "Treatment as per protocol"

   ✅ REQUIRED SPECIFICITY:
   - Age, occupation, specific presenting complaint with duration/severity/radiation
   - Exact cardiovascular risk factors (e.g., "35 pack-year smoker, known hypertension for 8 years, father died of MI at age 58")
   - Timeline (e.g., "Symptoms started at 5:47am while shoveling snow in driveway")
   - Severity scale (e.g., "9/10 crushing central chest pain")
   - Associated symptoms (e.g., "sweaty (diaphoresis), nauseous, short of breath")

6. COMPLETE CLINICAL SCENARIOS (ALL SECTIONS REQUIRED):

   - Candidate instructions: 200-400 words, specific scenario
   - Actor instructions: 150-300 words, first-person perspective with emotional state
   - Sample answer with ALL subsections:
     * History: 8-12 specific history questions with expected answers
     * Examination: Specific vital signs (numbers), inspection, palpation, auscultation findings
     * ECG findings: Detailed interpretation (if applicable)
     * Diagnosis: Primary + 2-3 differentials
     * Immediate management: 8-12 specific actions with doses/PBS codes
     * Ongoing management: 6-10 specific actions with doses/PBS codes/MBS items
   - Marking criteria: 10-15 specific assessment items
   - Learning points: 6-8 clinical pearls with Australian guideline references
   - References: 4-6 Australian guidelines/resources

═══════════════════════════════════════════════════════════════════
JSON STRUCTURE (RETURN THIS EXACT FORMAT)
═══════════════════════════════════════════════════════════════════

{{
  "osce_id": "{osce_title.lower().replace(' ', '_').replace('-', '_').replace('/', '_').replace('(', '').replace(')', '').replace(',', '').replace("'", '')}",
  "title": "{osce_title}",
  "topic": "{osce_topic}",
  "category": "cardiology",
  "difficulty": "intermediate",
  "duration_minutes": 8,
  "specialty": "cardiology",

  "candidate_instructions": "Write 200-400 words with: patient age, occupation, presenting complaint (duration, severity, character, radiation), associated symptoms (sweating, nausea, SOB), relevant PMHx (known conditions, medications), cardiovascular risk factors (smoking pack-years, family history, diabetes, hypertension, hyperlipidemia), social history. Task: Assess and manage this patient. Time: 8 minutes. Example: 'You are a junior doctor in ED. A 58-year-old taxi driver presents at 7:30am with 2 hours of severe crushing central chest pain (9/10) radiating to left arm and jaw. He woke at 5:30am with the pain while getting ready for work. He is pale, sweaty, and nauseous. Known hypertension (takes amlodipine 5mg daily but often forgets), 35 pack-year smoker (20 cigarettes daily for 35 years), father died of heart attack at age 58. He has never had chest pain like this before. Please assess this patient and initiate appropriate management. You have 8 minutes.'",

  "actor_instructions": "Write 150-300 words in first-person perspective. Include: emotional state (anxious, frightened), pain character in patient's own words, specific triggers, why you came now, concerns about dying/family, answers to typical history questions. Example: 'You are terrified you are having a heart attack like your father. You woke at 5:30am with crushing pain in the middle of your chest - it feels like an elephant sitting on your chest. The pain goes down your left arm to your fingers and up into your jaw. 9/10 pain, worst pain you've ever felt. You are very sweaty and feel sick. You tried to ignore it for 2 hours but your wife insisted you come to hospital. You smoke 20 cigarettes every day for 35 years - you know you should quit. You take a blood pressure pill (amlodipine) but you forget it about half the time. Your father died of a massive heart attack at age 58 when you were 20 years old - you're now 58 and terrified the same thing is happening to you. You have a wife and two teenage children and you're scared you'll die and leave them.'",

  "examiner_brief": "Context for examiner: This is an [acute STEMI / ACS / heart failure / etc.] scenario. Key findings to observe: [specific examination findings]. Critical actions required: [activate cath lab, specific medications, timelines]. Common candidate mistakes: [list 3-4 common errors]. Candidates should complete: [history, examination, ECG interpretation, immediate management plan] within 8 minutes.",

  "sample_answer": {{
    "history": [
      "Specific history questions with expected answers - 8-12 items covering SOCRATES (Site, Onset, Character, Radiation, Associated symptoms, Timing, Exacerbating/relieving factors, Severity), cardiovascular risk factors (smoking, diabetes, hypertension, hyperlipidemia, family history), past medical history, medications, functional capacity"
    ],

    "examination": [
      "Vital signs: BP 145/92, HR 98 regular, RR 22, SpO2 95% room air, T 36.8°C",
      "General: Pale, diaphoretic, distressed, clutching chest",
      "Cardiovascular: JVP not elevated, carotids normal volume, apex beat not displaced, HS I + II + nil murmurs, no peripheral edema",
      "Respiratory: Equal chest expansion, resonant percussion, bibasal crackles (mild pulmonary edema)",
      "ECG: [SPECIFIC FINDINGS with measurements - see requirement #1 above]",
      "Specific physical examination findings relevant to this cardiology presentation"
    ],

    "ecg_findings": "MANDATORY if applicable to topic: Write 100-200 words with SPECIFIC measurements. Example: 'Sinus rhythm 98bpm. ST elevation 3mm in leads II, III, aVF (inferior STEMI). Reciprocal ST depression 2mm in leads V1, V2, V3. Pathological Q waves in lead III. ST elevation in III > II suggests right coronary artery (RCA) occlusion. Check right-sided leads: ST elevation in V4R confirms RV infarct. Inferior STEMI with RV involvement - avoid nitrates, give IV fluids if hypotensive.' If not applicable to this topic, write brief ECG findings or omit.",

    "diagnosis": "Primary diagnosis: [Specific diagnosis]. Differential diagnoses: [2-3 alternatives with brief reasoning]",

    "immediate_management": [
      "Call for help, activate cath lab (target door-to-balloon <90 minutes from first medical contact)",
      "High-flow oxygen 15L via non-rebreather mask if SpO2 <94% (target 94-98%, avoid hyperoxia)",
      "Aspirin 300mg PO stat (chewed for faster absorption) - antiplatelet, mortality benefit - PBS 8053K",
      "Ticagrelor 180mg PO stat (preferred over clopidogrel per eTG - faster onset, no genetic variation, no loading) - PBS 8721K",
      "Morphine 2.5-5mg IV slow push + metoclopramide 10mg IV (pain relief + antiemetic, cautious if RV infarct)",
      "GTN 300mcg sublingual (if systolic BP >90mmHg, avoid if RV infarct or inferior STEMI with ST elevation V4R)",
      "Fondaparinux 2.5mg SC stat (anticoagulation for STEMI, preferred over enoxaparin if early PCI planned) - PBS 8858P",
      "IV access x2 (large bore), bloods: troponin (will be elevated), FBC, UEC, coags, lipids, glucose, CXR (portable)",
      "Transfer to cath lab for primary PCI within 90 minutes (door-to-balloon time)",
      "If PCI unavailable or delayed >120 minutes: Consider thrombolysis (tenecteplase 30-50mg IV bolus weight-based, contraindications: recent surgery <3 weeks, active bleeding, previous hemorrhagic stroke, ischemic stroke <6 months, known bleeding disorder)",
      "8-12 specific immediate actions with doses, PBS codes, timelines"
    ],

    "ongoing_management": [
      "Post-PCI: Dual antiplatelet therapy - aspirin 100mg daily + ticagrelor 90mg BD for 12 months minimum (reduce to aspirin alone after 12 months) - PBS 8053K + 8721K",
      "High-intensity statin: Atorvastatin 80mg nocte (reduces recurrent events, target LDL <1.8 mmol/L or 50% reduction) - PBS 8086M",
      "ACE inhibitor: Ramipril 2.5mg daily, titrate to 10mg over 4-6 weeks (mortality benefit post-MI, improves LV remodeling) - PBS 8624K. Monitor UEC, K+ at 1-2 weeks",
      "Beta-blocker: Metoprolol 25mg BD, titrate to 100mg BD (target HR 50-60bpm, mortality benefit post-MI) - PBS 2933K",
      "Cardiac rehabilitation referral: 6-week program, improves mortality 25%, quality of life, risk factor modification - MBS 81110",
      "Smoking cessation: Nicotine replacement therapy (patches 21mg daily, taper over 8-12 weeks) + behavioral counseling - PBS 4220K. Varenicline alternative if NRT fails",
      "Mediterranean diet counseling: Increase oily fish, olive oil, nuts, vegetables. Sodium restriction <2g/day (=5g salt)",
      "Exercise prescription: Cardiac rehab supervised initially, then 150min/week moderate aerobic + 2x/week resistance",
      "Echocardiogram: Assess LV systolic function (LVEF), regional wall motion abnormalities, valves - MBS 55111. If LVEF <40%, consider ICD.",
      "Follow-up: 2 weeks post-discharge (GP + cardiologist), then monthly for 3 months, then 3-monthly for 12 months",
      "6-10 specific ongoing management actions with doses, PBS codes, MBS items, follow-up timelines"
    ]
  }},

  "marking_criteria": [
    "Introduction: Introduces self, confirms patient identity, explains role (1 mark)",
    "Consent: Obtains consent to take history and examine (1 mark)",
    "History of presenting complaint: SOCRATES (site, onset, character, radiation, associated symptoms, timing, exacerbating/relieving factors, severity) - 7 components (2 marks)",
    "Cardiovascular risk factors: Asks about smoking, diabetes, hypertension, hyperlipidemia, family history (1 mark)",
    "Examination: Performs focused cardiovascular examination (vital signs, JVP, apex, heart sounds) or requests findings (1 mark)",
    "ECG interpretation: Correctly identifies [specific ECG abnormality] (1 mark)",
    "Diagnosis: States primary diagnosis ([specific diagnosis]) (1 mark)",
    "Immediate management: Initiates appropriate immediate treatment (aspirin, P2Y12 inhibitor, anticoagulation, activate cath lab) - at least 4/5 key actions (2 marks)",
    "Ongoing management: Describes secondary prevention (DAPT duration, statin, ACEI, beta-blocker, cardiac rehab) - at least 4/5 key actions (1 mark)",
    "Communication: Explains diagnosis and plan to patient in clear, empathetic manner (1 mark)",
    "Follow-up: Arranges appropriate follow-up (2 weeks, then monthly) (1 mark)",
    "Professionalism: Maintains professional demeanor, shows empathy, addresses patient concerns (1 mark)",
    "10-15 specific marking criteria items"
  ],

  "learning_points": [
    "STEMI diagnosis: ST elevation ≥2mm in ≥2 contiguous chest leads (V1-V6) OR ≥1mm in ≥2 contiguous limb leads (I, II, III, aVL, aVF). Reciprocal ST depression increases diagnostic accuracy.",
    "Door-to-balloon time <90 minutes improves mortality: Each 30-minute delay increases mortality by 7.5%. If PCI unavailable or delayed >120 minutes, consider thrombolysis.",
    "Ticagrelor preferred over clopidogrel (eTG 2024): Faster onset (30 min vs 2-6 hours), no genetic variation (clopidogrel affected by CYP2C19 polymorphism), superior outcomes in PLATO trial. No loading dose required (start 180mg, then 90mg BD).",
    "RV infarct complicates inferior STEMI: Check right-sided leads (V4R). ST elevation V4R = RV infarct. Avoid nitrates/diuretics (preload-dependent), give IV fluids if hypotensive. Higher mortality than isolated inferior STEMI.",
    "Post-MI medications (ABCD): Aspirin (antiplatelet), Beta-blocker (mortality benefit), ACEI (LV remodeling), Dual antiplatelet (aspirin + ticagrelor 12 months), Statin (high-intensity). All have Level 1A evidence for mortality reduction.",
    "Cardiac rehabilitation: 6-week supervised program, reduces 1-year mortality by 25%, improves quality of life, risk factor modification. Medicare rebate available (MBS 81110). Strongly recommend to all post-MI patients.",
    "Australian PBS restrictions: Ticagrelor PBS-listed for ACS (PBS 8721K), requires Authority approval for >12 months use. High-intensity statins (atorvastatin 80mg) PBS-listed for secondary prevention post-ACS. NOACs require CHA2DS2-VASc ≥2 for PBS subsidy.",
    "6-8 clinical pearls with Australian guideline references, PBS codes, MBS items, specific timelines, evidence levels"
  ],

  "references": [
    "National Heart Foundation of Australia - Acute Coronary Syndromes Guidelines 2016: https://www.heartfoundation.org.au/",
    "Cardiac Society of Australia and New Zealand (CSANZ) - Guidelines for the Management of Acute Coronary Syndromes 2016",
    "eTG: Cardiovascular - Acute coronary syndromes: https://tg.org.au/",
    "PBS Schedule - Cardiovascular medications: https://www.pbs.gov.au/ (PBS 8721K ticagrelor, PBS 8086M atorvastatin, PBS 8624K ramipril)",
    "MBS - Cardiac procedures: https://www.mbsonline.gov.au/ (MBS 55111 echocardiogram, MBS 81110 cardiac rehabilitation, MBS 38200 coronary angiogram)",
    "4-6 Australian guidelines and resources with URLs where possible"
  ]
}}

═══════════════════════════════════════════════════════════════════
EXAMPLES OF EXCELLENT OSCE CONTENT
═══════════════════════════════════════════════════════════════════

EXAMPLE 1: ACUTE STEMI (GOLD STANDARD)

Candidate instructions (EXCELLENT):
"You are a junior doctor working a night shift in the Emergency Department. At 2:15am, a 58-year-old taxi driver presents with severe chest pain. He was woken from sleep at midnight with crushing central chest pain (9/10 severity) radiating to his left arm and jaw. The pain is constant and has not relieved. He is visibly distressed, pale, and sweating profusely. He tried taking his wife's angina spray (GTN) without relief. He has never experienced chest pain like this before. Past medical history: Hypertension (diagnosed 8 years ago, takes amlodipine 5mg daily but admits he often forgets doses). Cardiovascular risk factors: 35 pack-year smoker (20 cigarettes daily for 35 years, multiple failed quit attempts), no known diabetes or high cholesterol. Strong family history: father died suddenly of 'massive heart attack' at age 58 when patient was in his 20s - he is now 58 himself and terrified he's suffering the same fate. Social: Married with two teenage children (16 and 14), works 60-hour weeks driving taxi to support family. Please assess this patient and initiate appropriate management. You have 8 minutes."

ECG findings (EXCELLENT):
"Sinus rhythm 98bpm. ST elevation 3mm in leads II, III, aVF (inferior STEMI). Reciprocal ST depression 2mm in leads V1, V2, V3. ST elevation in lead III > lead II suggests right coronary artery (RCA) occlusion rather than left circumflex. Pathological Q waves present in lead III (indicating some myocardial necrosis has already occurred). Right-sided leads (V4R) show ST elevation 2mm confirming right ventricular (RV) infarct involvement. Inferior STEMI with RV involvement: This is a high-risk presentation. RV involvement means patient is preload-dependent - avoid nitrates and diuretics as they will drop preload and cause cardiogenic shock. If hypotensive, give IV fluids NOT inotropes initially."

Immediate management (EXCELLENT):
[
  "Call for senior ED doctor and cardiology registrar immediately, activate cath lab (target door-to-balloon time <90 minutes from first medical contact, currently 2:15am + 30min = 2:45am target)",
  "High-flow oxygen 15L/min via non-rebreather mask ONLY if SpO2 <94% (current evidence shows no benefit if already normoxic, target 94-98% to avoid hyperoxia which may worsen myocardial injury)",
  "Aspirin 300mg PO stat - MUST BE CHEWED for faster buccal absorption (onset 15min chewed vs 60min swallowed) - irreversible COX-1 inhibitor, antiplatelet effect, mortality benefit proven - PBS 8053K",
  "Ticagrelor 180mg PO stat (preferred over clopidogrel per eTG 2024) - P2Y12 inhibitor, faster onset than clopidogrel (30min vs 2-6 hours), no genetic variation affecting efficacy (clopidogrel affected by CYP2C19 polymorphism in 30% Caucasians, 50% Asians), PLATO trial showed 16% relative risk reduction in CV death vs clopidogrel - PBS 8721K",
  "Morphine 2.5mg IV slow push (can repeat 2.5-5mg every 5-10min to max 10mg) PLUS metoclopramide 10mg IV (antiemetic, also prokinetic aids drug absorption). CAUTION: In RV infarct, morphine can cause hypotension - use small doses, have IV fluids ready",
  "GTN 300mcg (0.3mg) sublingual spray - CONTRAINDICATED in this case due to RV infarct (would drop preload causing cardiogenic shock). If this were lateral or anterior STEMI without RV involvement: GTN 300mcg sublingual, can repeat every 5min x3 if systolic BP >90mmHg, then start GTN infusion 10-200mcg/min titrated to pain/BP",
  "Fondaparinux 2.5mg SC stat (factor Xa inhibitor, anticoagulation for STEMI, preferred over enoxaparin if early PCI planned as lower bleeding risk, OASIS-6 trial) - PBS 8858P. Alternative: Enoxaparin 1mg/kg SC BD if PCI >24 hours or if thrombolysis planned",
  "IV access x2 large bore (16G or 18G), send urgent bloods: Troponin I or T (will be elevated in STEMI, peak at 12-24 hours but positive from 3 hours), FBC (baseline Hb, platelets for antiplatelet therapy, WCC may be elevated inflammatory response), UEC (baseline renal function for contrast PCI, K+ important as hypokalemia increases arrhythmia risk), LFT, coagulation studies (INR, APTT baseline), fasting lipids (for statin therapy, cholesterol typically drops after MI so measure on admission), glucose (stress hyperglycemia common, also check for undiagnosed diabetes)",
  "CXR portable (check mediastinal width for aortic dissection differential, look for pulmonary edema suggesting LV failure)",
  "IMMEDIATE transfer to cath lab for primary PCI (percutaneous coronary intervention) within 90 minutes door-to-balloon time. This is gold standard for STEMI - reduces mortality vs thrombolysis, opens artery mechanically, allows assessment of coronary anatomy",
  "IF PCI UNAVAILABLE or will be delayed >120 minutes: Consider thrombolysis (fibrinolytic therapy). Agent: Tenecteplase (TNK-tPA) weight-based IV bolus: <60kg=30mg, 60-70kg=35mg, 70-80kg=40mg, 80-90kg=45mg, >90kg=50mg. Check contraindications FIRST: Recent surgery (<3 weeks), active bleeding, previous hemorrhagic stroke (absolute contraindication), ischemic stroke or TIA <6 months, known bleeding disorder, suspected aortic dissection, severe uncontrolled hypertension (>180/110). After thrombolysis: Transfer for angiography within 3-24 hours (pharmaco-invasive strategy)",
  "Continuous cardiac monitoring: Watch for reperfusion arrhythmias (VT, VF - have defibrillator ready), complete heart block (inferior MI can affect AV node via RCA), bradycardia (treat with atropine 600mcg IV if symptomatic)"
]

═══════════════════════════════════════════════════════════════════

Now generate your COMPLETE, CLINICALLY ACCURATE cardiology OSCE for:

TOPIC: {osce_topic}
TITLE: {osce_title}

IMPORTANT: Return ONLY the JSON (no markdown code blocks, no extra text). Ensure all sections are complete with specific clinical details as demonstrated in the examples above."""

def regenerate_single_osce(
    osce: Dict[str, Any],
    template: Dict[str, Any],
    index: int,
    total: int
) -> Dict[str, Any]:
    """
    Regenerate a single OSCE with complete clinical content using Claude API

    Args:
        osce: Original OSCE dict (may contain placeholders)
        template: Gold standard structure template
        index: Current OSCE number (1-indexed)
        total: Total number of OSCEs

    Returns:
        Regenerated OSCE dict with complete clinical content
    """

    topic = osce.get("topic", "cardiology")
    title = osce.get("title", f"Cardiology OSCE {index}")

    print(f"[{index}/{total}] Regenerating: {title}")
    print(f"    Topic: {topic}")

    # Create comprehensive prompt
    prompt = create_cardiology_prompt(topic, title)

    try:
        # Call Claude API
        print(f"    Calling Claude API (model: {CLAUDE_MODEL})...")
        start_time = time.time()

        response = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        elapsed = time.time() - start_time
        print(f"    API call completed in {elapsed:.1f}s")

        # Extract JSON from response
        content = response.content[0].text

        # Remove markdown code blocks if present
        if content.strip().startswith("```json"):
            content = content.replace("```json", "").replace("```", "").strip()
        elif content.strip().startswith("```"):
            content = content.replace("```", "").strip()

        # Parse JSON
        regenerated_osce = json.loads(content)

        # Preserve original osce_id if it exists
        if "osce_id" in osce:
            regenerated_osce["osce_id"] = osce["osce_id"]

        # Validate basic structure
        required_fields = [
            "title", "topic", "category", "candidate_instructions",
            "actor_instructions", "sample_answer", "marking_criteria",
            "learning_points"
        ]

        missing_fields = [f for f in required_fields if f not in regenerated_osce]

        if missing_fields:
            print(f"    ⚠️  WARNING: Missing fields: {missing_fields}")

        # Check candidate instructions length
        cand_instr_len = len(regenerated_osce.get("candidate_instructions", ""))
        if cand_instr_len < 200:
            print(f"    ⚠️  WARNING: Candidate instructions too short ({cand_instr_len} chars, should be >200)")
        else:
            print(f"    ✅ Candidate instructions: {cand_instr_len} chars")

        # Check for placeholder phrases
        placeholders = [
            "A patient presents with",
            "According to Australian guidelines",
            "ECG findings for",
            "Management as per protocol",
            "as per guidelines"
        ]

        full_content = json.dumps(regenerated_osce).lower()
        found_placeholders = [p for p in placeholders if p.lower() in full_content]

        if found_placeholders:
            print(f"    ⚠️  WARNING: Placeholder phrases detected: {found_placeholders}")
        else:
            print(f"    ✅ No placeholder phrases detected")

        print(f"    ✅ SUCCESS: OSCE regenerated")
        return regenerated_osce

    except json.JSONDecodeError as e:
        print(f"    ❌ ERROR: Invalid JSON response from Claude")
        print(f"       Error: {e}")
        print(f"       Response (first 500 chars): {content[:500] if 'content' in locals() else 'No content'}")
        print(f"    Returning original OSCE (placeholder content)")
        return osce

    except Exception as e:
        print(f"    ❌ ERROR: {type(e).__name__}: {e}")
        print(f"    Returning original OSCE (placeholder content)")
        return osce

def main():
    """Main regeneration function"""

    print("=" * 80)
    print("CARDIOLOGY OSCE REGENERATION")
    print("=" * 80)
    print()

    # Parse command line arguments
    if len(sys.argv) != 3:
        print("❌ ERROR: Invalid arguments")
        print()
        print("Usage:")
        print("    python3 regenerate_cardiology_osces_complete.py <input_file> <output_file>")
        print()
        print("Example:")
        print("    python3 scripts/regenerate_cardiology_osces_complete.py \\")
        print("        data/osces/cardiology_50_osces.json \\")
        print("        data/osces/cardiology_50_osces_regenerated.json")
        print()
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    # Check API key
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("❌ ERROR: ANTHROPIC_API_KEY environment variable not set")
        print()
        print("Please set it with:")
        print("    export ANTHROPIC_API_KEY='your-api-key-here'")
        print()
        print("Or if using CLAUDE_API_KEY:")
        print("    export ANTHROPIC_API_KEY=\"$CLAUDE_API_KEY\"")
        print()
        sys.exit(1)

    print("✅ API key configured")
    print(f"✅ Using Claude model: {CLAUDE_MODEL}")
    print()

    # Load input OSCEs
    print(f"Loading OSCEs from: {input_file}")

    try:
        with open(input_file, 'r') as f:
            osces = json.load(f)
    except FileNotFoundError:
        print(f"❌ ERROR: Input file not found: {input_file}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ ERROR: Invalid JSON in input file: {e}")
        sys.exit(1)

    print(f"✅ Loaded {len(osces)} OSCEs")
    print()

    # Load gold standard template
    template = load_gold_standard_template()
    print()

    # Estimate time
    estimated_minutes = len(osces) * 2.5  # ~2.5 min per OSCE average
    print(f"⏱️  Estimated time: {estimated_minutes:.0f} minutes ({estimated_minutes/60:.1f} hours)")
    print()

    # Regenerate each OSCE
    print("=" * 80)
    print("STARTING REGENERATION")
    print("=" * 80)
    print()

    start_time = time.time()
    regenerated_osces = []
    success_count = 0
    warning_count = 0
    failure_count = 0

    for i, osce in enumerate(osces, 1):
        regenerated = regenerate_single_osce(osce, template, i, len(osces))
        regenerated_osces.append(regenerated)

        # Assess quality
        cand_instr_len = len(str(regenerated.get("candidate_instructions", "")))
        has_sample_answer = bool(regenerated.get("sample_answer"))

        if cand_instr_len > 200 and has_sample_answer:
            success_count += 1
        elif cand_instr_len > 100:
            warning_count += 1
        else:
            failure_count += 1

        print()

        # Small delay to avoid rate limiting (if needed)
        # time.sleep(0.5)

    elapsed_minutes = (time.time() - start_time) / 60

    # Save regenerated OSCEs
    print("=" * 80)
    print("SAVING RESULTS")
    print("=" * 80)
    print()

    print(f"Writing {len(regenerated_osces)} OSCEs to: {output_file}")

    try:
        with open(output_file, 'w') as f:
            json.dump(regenerated_osces, f, indent=2, ensure_ascii=False)
        print(f"✅ Successfully saved to {output_file}")
    except Exception as e:
        print(f"❌ ERROR saving output file: {e}")
        sys.exit(1)

    # Final summary
    print()
    print("=" * 80)
    print("REGENERATION COMPLETE")
    print("=" * 80)
    print()
    print(f"Total OSCEs processed: {len(osces)}")
    print(f"  ✅ Success (high quality): {success_count}")
    print(f"  ⚠️  Warning (may need review): {warning_count}")
    print(f"  ❌ Failed (placeholder content): {failure_count}")
    print()
    print(f"Time elapsed: {elapsed_minutes:.1f} minutes")
    print(f"Average per OSCE: {elapsed_minutes/len(osces):.1f} minutes")
    print()
    print(f"Output file: {output_file}")
    print()
    print("=" * 80)
    print("NEXT STEPS")
    print("=" * 80)
    print()
    print("1. Run placeholder detection:")
    print(f"   python3 scripts/detect_placeholder_content.py {output_file}")
    print()
    print("2. Spot check 3-5 random OSCEs for clinical accuracy")
    print()
    print("3. If all quality gates pass, replace original file:")
    print(f"   cp {output_file} {input_file}")
    print()

if __name__ == "__main__":
    main()
