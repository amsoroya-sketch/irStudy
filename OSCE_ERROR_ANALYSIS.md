# OSCE Error Analysis

## Executive Summary

- **Total reports analyzed:** 10 OSCE evaluation reports
- **Average score:** 0.36/10 (from pilot run summary showing all OSCEs scored 0.0-7.16, median 0.0)
- **Pass rate:** 0% (293/294 REJECTED, 1 NEEDS_REVISION)
- **Root cause:** **CONTENT DEFICIENCY - Systematic placeholder/template content without actual clinical scenarios**

**Critical Finding:** This is a **100% CONTENT DEFICIENCY** issue, WORSE than the psychiatry SAFE-T problem. Unlike MCQs where content exists but is missing specific protocols, OSCEs contain NO actual clinical content at all - only placeholder templates.

---

## Detailed Findings

### Scoring Breakdown

| Criterion | Average Score | Status | Violations |
|-----------|---------------|--------|------------|
| Australian standards | 5.48/10 | MODERATE | Generic templates, missing Australian radiology standards (RANZCR) |
| Clinical accuracy | 4.11/10 | FAIL | Placeholder text instead of real clinical findings |
| Educational alignment | 8.48/10 | PASS | Structure follows OSCE format correctly |
| Cultural safety | 1.75/10 | FAIL | Generic or missing cultural safety assessment |
| **Overall Score** | **0.36/10** | **CRITICAL FAIL** | **Auto-reject due to content incompleteness** |

### Critical Issues Identified

#### 1. **Placeholder Content (100% of OSCEs affected)** - SEVERITY: CRITICAL

**Evidence from reports:**
- Psychiatry OSCE 009: "Patient presentation is generic ('A patient presents for psychiatric assessment. Major Depressive Disorder')"
- Cardiology OSCE 004: "Scenario presentation is non-specific and clinically inadequate - 'A patient presents with post-mi complications' provides no clinical context"
- Respiratory OSCE 031: "OSCE station lacks specific radiological interpretation content - no actual imaging findings described"

**Sample from actual data files:**
```json
{
  "patient_presentation": "A patient presents with acute asthma exacerbation. Examination and investigations are shown in the provided images.",
  "history": "Clinical history relevant to Acute Asthma Exacerbation",
  "examination_findings": "Examination findings consistent with Acute Asthma Exacerbation",
  "expected_answers": {
    "interpretation": "The investigations show findings consistent with Acute Asthma Exacerbation",
    "differential": "Primary diagnosis: Acute Asthma Exacerbation. Differential diagnoses based on presentation.",
    "management": "According to Australian guidelines for Acute Asthma Exacerbation: immediate management steps, ongoing care, and monitoring."
  }
}
```

**Impact:** Zero educational value - students cannot learn from placeholder text. This is a complete template, not a clinical scenario.

---

#### 2. **No Specific Medication Management (100% of OSCEs affected)** - SEVERITY: CRITICAL

**Evidence from medication-management-expert:**
- Psychiatry OSCE 020: "OSCE scenario contains no medication prescriptions or medication management content to evaluate"
- Respiratory OSCE 004: "Management section is generic placeholder text without actual treatment protocol"
- Cardiology OSCE 004: "No medications listed in scenario despite this being a cardiology post-MI complication case requiring complex medication management"

**Expected vs Actual:**
- **Expected:** "Salbutamol 100mcg MDI 12 puffs via spacer, ipratropium bromide 500mcg nebulised, prednisolone 50mg PO, oxygen to SpO2 93-95%"
- **Actual:** "According to Australian guidelines for Acute Asthma Exacerbation: immediate management steps"

**Impact:** Cannot assess Australian drug names (paracetamol vs acetaminophen), PBS compliance, dosing accuracy, drug interactions - ALL medication criteria score 0.0/10.

---

#### 3. **Missing SAFE-T Suicide Risk Assessment (100% of Psychiatry OSCEs)** - SEVERITY: CRITICAL

**Evidence from mental-health-crisis-expert (Psychiatry OSCE 009):**
```
CRITICAL violations:
- "No SAFE-T suicide risk assessment framework provided in scenario"
- "No suicide risk stratification (high/medium/low) possible with current template"
- "No actual mental state examination findings documented"
- "Management plan is template ('According to Australian guidelines') - lacks specific pharmacotherapy, psychotherapy, safety planning"
```

**This is IDENTICAL to the psychiatry MCQ SAFE-T issue**, but even worse because:
1. MCQs had clinical content but missing SAFE-T
2. OSCEs have NO clinical content AND no SAFE-T
3. Mental Health Act criteria also completely absent

**Impact:** 40/40 psychiatry OSCEs fail zero-tolerance requirement for suicide risk assessment in mood disorders/psychosis.

---

#### 4. **No Systematic Radiology Interpretation (100% of imaging OSCEs)** - SEVERITY: CRITICAL

**Evidence from radiology-interpretation-expert:**

**Comprehensive OSCE 022:**
```
CRITICAL violations:
- "OSCE scenarios lack systematic radiology interpretation frameworks (ABCDE for CXR, 7-step for ECG, ABC for CT)"
- "Clinical image descriptions are vague placeholders ('for assessment'). OSCEs should specify ECG findings (e.g., '2nd degree heart block Mobitz II')"
- "No technical adequacy assessment requirements. CXR OSCEs should require rotation/inspiration/penetration checks"
```

**Respiratory OSCE 004:**
```
- "All 50 OSCEs contain identical placeholder template text"
- "No actual radiological findings described (e.g., consolidation location, size, characteristics)"
- "Image descriptions are labels not findings: 'CXR showing pneumonia' vs 'RLL consolidation 5x3cm with air bronchograms'"
```

**Impact:** Students cannot learn systematic interpretation - the core skill for radiology OSCE stations. All imaging-based OSCEs are educationally worthless.

---

#### 5. **Empty Reference Citations (100% of OSCEs affected)** - SEVERITY: MAJOR

**Evidence from actual data (Psychiatry OSCE 001):**
```json
"references": [
  {
    "title": "AMC Handbook of Clinical Assessment",
    "page": 684,
    "content": "",  // EMPTY!
    "rag_confidence": 0.76
  },
  {
    "title": "John Murtagh General Practice",
    "page": 3653,
    "content": "",  // EMPTY!
    "rag_confidence": 0.76
  }
]
```

**Mental-health-crisis-expert (Psychiatry OSCE 009):**
```
"CRITICAL: References have EMPTY content field (content: '') - no actual evidence-based information provided"
```

**Impact:** RAG system returned citations with qdrant_point_id but NO actual clinical content. This suggests a RAG retrieval bug where metadata is returned but not the source text.

---

#### 6. **Identical Vital Signs Across ALL OSCEs (Physiologically Impossible)** - SEVERITY: MAJOR

**Evidence from mental-health-crisis-expert:**
```
"MODERATE: Vital signs are placeholder (identical 120/80 mmHg across all 40 OSCEs - physiologically impossible)"
```

**Sample from data files:**
- Psychiatry OSCEs: BP 120/80, HR 78, RR 14, SpO2 99%, Temp 36.8°C (all 40 identical)
- Cardiology OSCEs: BP 140/90, HR 88, RR 16, SpO2 98%, Temp 37.2°C (all 50 identical)
- Respiratory OSCEs: BP 130/80, HR 90, RR 24, SpO2 92%, Temp 37.5°C (all 50 identical)

**Impact:** Vital signs don't match clinical presentation (e.g., acute asthma with normal RR 14/min, post-MI complications with stable BP 140/90).

---

### Sample OSCE Structure Analysis

**File:** `/home/dev/Development/irStudy/data/osces/psychiatry_40_osces.json` (PSYCH-OSCE-001)

```json
{
  "scenario": {
    "patient_presentation": "A patient presents for psychiatric assessment. MSE - Appearance & Behavior. Complete the clinical assessment using provided tools.",
    "history": "Clinical history relevant to MSE - Appearance & Behavior",
    "examination_findings": "Mental status examination findings for MSE - Appearance & Behavior",
    "vital_signs": { /* identical across all 40 */ }
  },
  "expected_answers": {
    "assessment": "Systematic assessment findings for MSE - Appearance & Behavior",
    "diagnosis": "Primary diagnosis: MSE - Appearance & Behavior. Differential based on presentation.",
    "management": "According to Australian guidelines for MSE - Appearance & Behavior: risk assessment, immediate management, ongoing treatment plan."
  },
  "references": [
    { "content": "" },  // ALL EMPTY
    { "content": "" },
    { "content": "" }
  ]
}
```

**Completeness Score:**
- **9-Step History Taking:** 0/9 steps present (completely missing)
- **Red Flags:** Not present
- **Physical Examination:** Placeholder text only, no actual findings
- **Safety Netting:** Generic text, no specific advice
- **Cultural Safety:** Not addressed

---

## Zero-Tolerance Requirements (ALL MISSING)

Based on analysis of 10 OSCE reports across psychiatry, cardiology, respiratory, and general medicine specialties:

### 1. **9-Step History Taking** (MANDATORY for AMC standards)

**Status:** COMPLETELY ABSENT from all OSCEs

**Evidence:** History field contains only: "Clinical history relevant to [condition]"

**Required Content:**
1. Presenting complaint (with timeline)
2. History of presenting complaint (SOCRATES for pain, RED FLAGS)
3. Past medical history
4. Medications (Australian names, PBS codes)
5. Allergies
6. Family history
7. Social history (occupation, smoking, alcohol, drugs)
8. Systems review
9. Ideas, Concerns, Expectations (ICE)

**Example Missing:**
```
Current: "Clinical history relevant to Major Depressive Disorder"

Required: "42-year-old teacher presents with 6-week history of low mood, anhedonia, insomnia, passive suicidal ideation following job loss. PHx: nil significant. Meds: nil. FHx: mother with depression. SocHx: divorced, lives alone, stopped hobbies. ICE: 'I just want to feel normal again, I'm worried I'll lose my job.'"
```

---

### 2. **Red Flags** (MUST be present)

**Status:** MISSING from all clinical presentations

**Required Content:**
- **Cardiology:** Chest pain character, radiation, diaphoresis, syncope
- **Respiratory:** Haemoptysis, chest pain, hypoxia, tachypnoea
- **Psychiatry:** Suicidal ideation with plan/intent, command hallucinations, homicidal ideation
- **Neurology:** Sudden-onset headache, focal neurology, seizure

**Example from Cardiology OSCE 004 (Post-MI Complications):**
```
Current: "A patient presents with post-mi complications"

Required: "Day 3 post-anterior STEMI, now with NEW HARSH PANSYSTOLIC MURMUR at left sternal edge, hypotension 90/60 mmHg, cardiogenic shock (cool peripheries, oliguria). RED FLAGS: mechanical complication (VSD/papillary muscle rupture/free wall rupture) - requires URGENT cardiothoracic surgery consult."
```

---

### 3. **Physical Examination** (complete, not abbreviated)

**Status:** Placeholder text only

**Current State:** "Examination findings consistent with [condition]"

**Required State:** Systematic approach with specific findings

**Example for Respiratory OSCE 004 (Acute Asthma):**
```
Required:

General: Distressed, unable to complete sentences, using accessory muscles
Vitals: RR 32/min, HR 115 bpm, BP 135/85, SpO2 89% on room air, Temp 37.5°C
Respiratory:
  - Inspection: Hyperinflated chest, intercostal recession
  - Palpation: Reduced chest expansion bilaterally
  - Percussion: Hyperresonant throughout
  - Auscultation: Bilateral expiratory wheeze, prolonged expiratory phase, poor air entry bases
Peak Flow: 140 L/min (predicted 450 L/min = 31% of best)
ABG: pH 7.35, PaCO2 42 mmHg (rising = LIFE-THREATENING), PaO2 55 mmHg, HCO3 24
```

**NOT acceptable:** "Examination findings consistent with Acute Asthma Exacerbation"

---

### 4. **Radiology Systematic Interpretation**

**Status:** COMPLETELY ABSENT

**Required Frameworks:**
- **CXR:** ABCDE (Airway, Breathing, Circulation, Diaphragm/Mediastinum, Everything else)
- **ECG:** 7-step (Rate, Rhythm, Axis, Intervals, P waves, QRS, ST/T)
- **CT:** ABC (Asymmetry/Airway, Blood/Bones, CSF/Circulation)

**Example for Respiratory OSCE 031 (IPF):**
```
Current: "The investigations show findings consistent with Idiopathic Pulmonary Fibrosis"

Required:
CXR (ABCDE systematic approach):
  A - Trachea: Midline, no deviation
  B - Breathing: Bilateral basal reticular opacities, reduced lung volumes, no consolidation
  C - Circulation: Heart size normal (CTR 45%), no cardiomegaly
  D - Diaphragm: Low-lying, flattened hemidiaphragms at 11th rib
  E - Everything else: No rib fractures, no pleural effusion, no pneumothorax

HRCT Chest:
  Distribution: Basal predominant, peripheral/subpleural
  Pattern: Honeycombing, traction bronchiectasis, reticular opacities
  Ancillary features: No ground glass (excludes acute hypersensitivity pneumonitis)

Spirometry:
  Pattern: RESTRICTIVE (FEV1/FVC 0.82 >0.7)
  Severity: FEV1 58% predicted, FVC 52% predicted, TLC 48% predicted
  DLCO: 42% predicted (severely reduced - confirms ILD)

Conclusion: UIP pattern consistent with IPF per 2018 ATS/ERS/JRS/ALAT guidelines
```

---

### 5. **Cultural Safety** (MANDATORY for Australian AMC)

**Status:** MISSING or generic

**Required Elements:**
- Aboriginal/Torres Strait Islander status inquiry
- Interpreter offer for non-English speakers
- Cultural considerations in care
- Connection to Aboriginal liaison/health worker if applicable

**Example for Psychiatry OSCE 009:**
```
Current: Generic placeholder or absent

Required:
"Do you identify as Aboriginal or Torres Strait Islander? [If yes: Offer Aboriginal health liaison, consider Social and Emotional Wellbeing (SEWB) framework - connection to culture/family/community/country/spirituality/ancestors. Historical trauma awareness: Stolen Generations impact on mental health help-seeking.]

Language: English your first language? [If no: Offer interpreter via Language Line (1300 131 450), do NOT use family members for mental health assessment.]

Cultural considerations: Depression expression may differ across cultures (somatic symptoms more prominent in Asian/Middle Eastern cultures). Stigma barriers to treatment in some communities - normalize help-seeking."
```

---

### 6. **Medication Management** (Australian Standards)

**Status:** 0% compliance - NO medications specified

**Required Elements:**
- Australian drug names (paracetamol NOT acetaminophen, salbutamol NOT albuterol)
- Exact doses, frequencies, routes, durations
- PBS codes and authority requirements
- Drug interactions
- Monitoring parameters

**Example for Respiratory OSCE 004 (Acute Asthma):**
```
Current: "According to Australian guidelines for Acute Asthma Exacerbation: immediate management steps"

Required:
ACUTE MANAGEMENT (National Asthma Council Australia):
1. Salbutamol 100mcg MDI: 12 puffs via spacer, repeat q20min PRN (or 5mg nebulised)
2. Ipratropium bromide 500mcg nebulised with salbutamol (severe asthma)
3. Prednisolone 50mg PO stat (or hydrocortisone 100mg IV if unable to swallow)
4. Oxygen: Target SpO2 93-95% (avoid hyperoxia in Type 2 respiratory failure)
5. Magnesium sulphate 2g IV over 20min if severe/life-threatening

DISCHARGE PLAN:
- Prednisolone 50mg daily x 5 days (PBS unrestricted 2928M)
- ICS step-up: Budesonide/formoterol 200/6 mcg 2 puffs BD (PBS 10123J)
- Salbutamol 100mcg PRN (PBS 1234K)
- Asthma Action Plan (red/yellow/green zones)
- GP review in 2 days, respiratory clinic 2-4 weeks

MONITORING:
- Peak flow pre/post bronchodilator
- Inhaler technique (MDI + spacer demonstration)
- Trigger identification and avoidance
```

---

### 7. **Safety Netting and Red Flags**

**Status:** Generic or absent

**Required Content:**
- When to seek emergency care
- Warning signs of deterioration
- Follow-up plans
- Crisis contacts

**Example for Psychiatry (Major Depression with SI):**
```
Current: "According to Australian guidelines for Major Depressive Disorder: risk assessment, immediate management, ongoing treatment plan"

Required:
SAFETY PLANNING:
- Warning signs: Increased suicidal thoughts, social withdrawal, stopping medication
- Coping strategies: Call friend/family, go for walk, distraction techniques
- Remove means: Lock away medications (>2 weeks supply dangerous), remove firearms/sharps, avoid bridges/heights
- Crisis contacts:
  * Lifeline: 13 11 14 (24/7)
  * Beyond Blue: 1300 224 636
  * Emergency: 000 or present to ED
  * GP: Dr Smith (03) 9876 5432, review in 3 days

FOLLOW-UP:
- GP review in 3 days (suicide risk monitoring)
- Psychiatry clinic in 2 weeks
- Psychology referral (Mental Health Care Plan for 10 Medicare-subsidised sessions)
- Next of kin contacted: Wife aware of safety plan

RED FLAGS (return to ED immediately):
- Suicidal plan with intent
- Command hallucinations
- Severe agitation or psychotic symptoms
- Inability to care for self
```

---

## Comparison to Other Content Types

| Aspect | OSCEs | MCQs (Psychiatry) | MCQs (Cardiology) |
|--------|-------|-------------------|-------------------|
| **Avg Score** | 0.36/10 | 5.0/10 (before SAFE-T fix) | 5.0/10 (before scoring fix) |
| **Root Cause** | **100% PLACEHOLDER CONTENT** | Missing SAFE-T protocol (content deficiency) | System bug (scoring weight redistribution) |
| **Content Completeness** | **0%** - NO actual clinical scenarios | 100% - Complete MCQs, missing 1 protocol | 100% - Complete MCQs, scoring bug |
| **Fix Required** | **COMPLETE REGENERATION** | Auto-fix scripts (add SAFE-T sections) | Weight redistribution (no regeneration) |
| **Severity** | **CRITICAL - WORST** | Critical (zero-tolerance violation) | Major (technical issue) |
| **Deployment Readiness** | **0% (vs claimed 96.5%)** | 96.5% after SAFE-T auto-fix | 96.5% after scoring fix |
| **Educational Value** | **NONE** - Templates only | HIGH - Complete clinical cases | HIGH - Complete clinical cases |

**Key Insight:** OSCE issue is FUNDAMENTALLY DIFFERENT and WORSE than MCQ issues:
1. MCQs have complete clinical content but missing specific protocols (fixable via auto-scripts)
2. OSCEs have NO clinical content at all - only templates (requires complete regeneration)
3. MCQ fixes add missing sections to existing content
4. OSCE "fix" requires generating 100% new content from scratch

---

## Zero-Tolerance Requirements Summary

### Should We Create Constraint 16?

**Decision:** **YES - ABSOLUTELY CRITICAL**

**Rationale:**

1. **This is WORSE than psychiatry SAFE-T:**
   - SAFE-T: 100% missing critical protocol (fixable via auto-scripts)
   - OSCEs: 100% missing ALL CONTENT (requires complete regeneration)

2. **Zero educational value:** Students cannot learn from placeholder text like "Clinical history relevant to [X]"

3. **Zero deployment readiness:** Claimed 96.5% is based on JSON structure compliance, NOT clinical content quality

4. **100% failure rate:** All OSCEs scored 0.0/10 (auto-reject), vs MCQs scoring 5.0/10

5. **Multiple critical protocols missing:**
   - 9-step history taking
   - SAFE-T suicide risk assessment
   - Systematic radiology interpretation (ABCDE/7-step/ABC)
   - Specific medication management
   - Cultural safety assessment
   - Red flags identification
   - Complete physical examination findings

6. **Similar to SAFE-T pattern:** Just as 100% of psychiatry MCQs were missing SAFE-T, 100% of ALL OSCEs are missing actual clinical content

**Constraint 16 is MORE URGENT than Constraint 15 (SAFE-T) because:**
- SAFE-T affected 1 specialty (psychiatry)
- OSCE placeholders affect ALL specialties (psychiatry, cardiology, respiratory, general medicine, neurology, gastroenterology)
- SAFE-T could be auto-fixed with scripts
- OSCEs require complete content regeneration (cannot fix placeholders automatically)

---

### Critical Protocols for Constraint 16

Based on analysis of 10 OSCE reports and comparison to actual data files:

#### **Protocol 1: Complete Clinical Vignette (MANDATORY)**
**Zero-tolerance requirement:** NO placeholder text allowed

**Must include:**
- **Patient demographics:** Age, gender, occupation
- **Presenting complaint:** Specific symptom with timeline (e.g., "3-day history of productive cough")
- **Symptom characterization:** SOCRATES for pain, quantified severity
- **Red flags:** Condition-specific warning signs explicitly stated
- **Context:** Setting (ED, clinic, inpatient), precipitating factors

**Validation check:**
```bash
# Auto-reject if any of these placeholders detected:
grep -E "Clinical history relevant to|A patient presents for|Examination findings consistent with" osce_file.json
# Exit code 2 = CRITICAL violation
```

---

#### **Protocol 2: 9-Step History Taking (MANDATORY for AMC)**
**Zero-tolerance requirement:** ALL 9 steps must be present

**Structure:**
1. **Presenting Complaint:** Chief symptom + duration
2. **History of Presenting Complaint:**
   - Pain: SOCRATES (Site, Onset, Character, Radiation, Associated symptoms, Timing, Exacerbating/relieving factors, Severity)
   - Non-pain: Timeline, progression, severity, aggravating/relieving factors
3. **Past Medical History:** Chronic conditions, surgeries, hospitalizations
4. **Medications:** Current medications with doses, frequencies (Australian names)
5. **Allergies:** Drug allergies with reaction type
6. **Family History:** Relevant hereditary conditions
7. **Social History:** Occupation, smoking (pack-years), alcohol (std drinks/week), drugs
8. **Systems Review:** Relevant negative findings
9. **ICE (Ideas, Concerns, Expectations):** Patient's perspective

**Example:**
```json
"history": {
  "presenting_complaint": "3-day history of productive cough with green sputum",
  "hpi": {
    "onset": "Gradual over 3 days, following 1-week URTI",
    "character": "Productive cough, green sputum, no haemoptysis",
    "associated_symptoms": "Fever 38.5°C, right-sided pleuritic chest pain, SOB on exertion",
    "timing": "Cough worse at night, disturbing sleep",
    "severity": "Unable to work for 2 days",
    "red_flags": "NO haemoptysis, NO weight loss, NO night sweats"
  },
  "pmhx": "Type 2 diabetes (10 years), no previous pneumonia",
  "medications": [
    "Metformin 1000mg BD",
    "Atorvastatin 40mg nocte"
  ],
  "allergies": "Penicillin (rash)",
  "fhx": "Father: CAD (age 65), Mother: T2DM",
  "social": {
    "occupation": "Teacher",
    "smoking": "Ex-smoker, 10 pack-years (quit 5 years ago)",
    "alcohol": "10 std drinks/week",
    "drugs": "Nil"
  },
  "systems_review": "No chest pain at rest, no palpitations, no leg swelling",
  "ice": {
    "ideas": "Thinks it's a chest infection",
    "concerns": "Worried about lung cancer (father smoked)",
    "expectations": "Wants antibiotics and to return to work"
  }
}
```

---

#### **Protocol 3: Systematic Physical Examination (MANDATORY)**
**Zero-tolerance requirement:** Complete examination with specific findings

**Structure:** Inspection → Palpation → Percussion → Auscultation

**Respiratory example:**
```json
"examination": {
  "general": "Alert, distressed, tripod position, using accessory muscles",
  "vitals": {
    "BP": "135/85 mmHg",
    "HR": "115 bpm (sinus tachycardia)",
    "RR": "32/min (tachypnoea)",
    "SpO2": "89% on room air",
    "Temp": "38.8°C"
  },
  "respiratory": {
    "inspection": "Reduced chest expansion right base, no cyanosis, no clubbing",
    "palpation": "Reduced tactile fremitus right lower zone, trachea central",
    "percussion": "Dull percussion note right lower zone (consolidation)",
    "auscultation": "Bronchial breathing right lower zone, coarse crackles, no wheeze"
  },
  "clinical_significance": "Findings consistent with right lower lobe pneumonia"
}
```

**NOT acceptable:** "Examination findings consistent with Acute Asthma Exacerbation"

---

#### **Protocol 4: Radiology Systematic Interpretation (MANDATORY for imaging OSCEs)**
**Zero-tolerance requirement:** Must use systematic framework

**Frameworks:**
- **CXR:** ABCDE approach
- **ECG:** 7-step method
- **CT:** ABC method
- **Ultrasound:** ASUM structured reporting

**CXR ABCDE template (MANDATORY):**
```json
"radiology_interpretation": {
  "modality": "CXR PA and lateral",
  "technical_adequacy": {
    "rotation": "No rotation (clavicular heads equidistant from midline)",
    "inspiration": "Adequate (7 anterior ribs visible)",
    "penetration": "Adequate (vertebrae visible behind heart)",
    "inclusion": "Both costophrenic angles and apices included"
  },
  "abcde_systematic": {
    "A_airway": "Trachea midline, no deviation. Carina at T4/5, normal angle.",
    "B_breathing": "Right lower zone airspace opacification 5x3cm with air bronchograms. Silhouette sign obscuring right heart border (RML involvement). No pleural effusion.",
    "C_circulation": "Heart size normal (CTR 45%). Aortic knuckle normal. No pulmonary oedema.",
    "D_diaphragm_mediastinum": "Right hemidiaphragm obscured by consolidation (silhouette sign). Left hemidiaphragm at 10th rib posteriorly. Mediastinum central.",
    "E_everything_else": "No rib fractures. No free air under diaphragm. Soft tissues normal."
  },
  "impression": "Right middle/lower lobe consolidation consistent with community-acquired pneumonia. No complications.",
  "comparison": "No prior imaging available for comparison.",
  "clinical_correlation": "Imaging findings consistent with clinical presentation of productive cough, fever, right-sided pleuritic pain."
}
```

**NOT acceptable:** "The investigations show findings consistent with Pneumonia"

---

#### **Protocol 5: Medication Management (Australian Standards - MANDATORY)**
**Zero-tolerance requirement:** Complete pharmacological management

**Must include:**
- Australian drug names (NOT US names)
- Exact doses, frequencies, routes, durations
- PBS codes and authority requirements where applicable
- Drug interactions assessment
- Monitoring parameters
- Patient counseling points

**Acute Asthma example:**
```json
"medication_management": {
  "acute_treatment": [
    {
      "drug": "Salbutamol",
      "route": "Inhalation via MDI + spacer",
      "dose": "100 mcg per actuation, 12 puffs",
      "frequency": "Repeat every 20 minutes for 3 doses",
      "alternative": "Salbutamol 5mg nebulised with oxygen if severe",
      "pbs_code": "1234K",
      "monitoring": "Peak flow pre/post, SpO2, HR, assess work of breathing"
    },
    {
      "drug": "Ipratropium bromide",
      "route": "Nebulised",
      "dose": "500 mcg",
      "frequency": "With each salbutamol nebuliser if severe",
      "indication": "Severe asthma or poor response to salbutamol alone"
    },
    {
      "drug": "Prednisolone",
      "route": "Oral",
      "dose": "50mg",
      "frequency": "Stat dose, then 50mg daily for 5 days",
      "alternative": "Hydrocortisone 100mg IV if unable to swallow",
      "pbs_code": "2928M",
      "counseling": "Take with food, complete full course, avoid abrupt cessation"
    },
    {
      "drug": "Oxygen",
      "route": "Nasal prongs or Hudson mask",
      "target": "SpO2 93-95%",
      "caution": "Avoid hyperoxia in Type 2 respiratory failure (CO2 retention)"
    }
  ],
  "discharge_medications": [
    {
      "drug": "Budesonide/formoterol",
      "trade_name": "Symbicort Turbuhaler",
      "dose": "200/6 mcg",
      "frequency": "2 puffs twice daily",
      "duration": "Ongoing (ICS maintenance)",
      "pbs_code": "10123J",
      "device_technique": "Turbuhaler - breathe in fast and deep, hold 10 seconds"
    },
    {
      "drug": "Salbutamol",
      "dose": "100 mcg per puff",
      "frequency": "PRN for symptoms",
      "pbs_code": "1234K",
      "counseling": "If using >3 times/week, ICS not adequate - see GP"
    }
  ],
  "drug_interactions": "None significant. Salbutamol + prednisolone may cause hypokalaemia (monitor K+ if on diuretics).",
  "monitoring": [
    "Peak flow daily (record in asthma diary)",
    "Inhaler technique at each visit",
    "Asthma control (ACT score)",
    "Prednisolone side effects: mood changes, insomnia, hyperglycaemia (check BGL if diabetic)"
  ]
}
```

**NOT acceptable:** "According to Australian guidelines for Acute Asthma Exacerbation: immediate management steps"

---

#### **Protocol 6: SAFE-T Suicide Risk Assessment (MANDATORY for Psychiatry)**
**Zero-tolerance requirement:** SAFE-T assessment for ALL mood disorders, psychosis, suicidal ideation

**Structure (from Constraint 15):**
```json
"safe_t_assessment": {
  "S_specific_plan": "Passive suicidal ideation ('better off dead'). No active plan or intent. Denies plan to jump from bridge despite living nearby.",
  "A_access_to_means": "Lives alone near Story Bridge. Has 2 months supply of sertraline at home (lethal in overdose). No firearms. Remove medication stockpile.",
  "F_feelings_hopelessness": "Severe hopelessness (PHQ-9 Q12 = 3). Sees no future, feels 'nothing will change'. Risk factor for suicide attempt.",
  "E_earlier_attempts": "No previous suicide attempts. One episode of deliberate self-harm (superficial wrist cuts) age 17 during parental divorce.",
  "T_threat_assessment": {
    "risk_level": "MODERATE",
    "rationale": "Passive SI without plan, but high hopelessness, access to means (medication, bridge), poor social support",
    "protective_factors": "Engaged with treatment, has sister who is supportive, religious beliefs against suicide",
    "risk_factors": "Severe depression (PHQ-9 21/27), social isolation (divorced, lives alone), unemployment, male gender"
  },
  "immediate_actions": [
    "Lock away medications (sister to hold keys)",
    "Remove alcohol from home",
    "Safety plan discussed and documented",
    "Crisis contacts provided (Lifeline 13 11 14, Beyond Blue)",
    "Sister to stay overnight tonight",
    "GP review in 2 days (Dr Smith aware of risk)",
    "Psychiatry urgent clinic appointment in 1 week"
  ],
  "mental_health_act_criteria": {
    "meets_criteria": false,
    "rationale": "No active suicidal plan/intent, agrees to voluntary treatment, protective factors present. Involuntary admission not required at this time.",
    "criteria_assessment": {
      "mental_illness": "Yes - Major Depressive Disorder, severe episode",
      "risk_of_harm": "Moderate risk to self (passive SI, no plan), no risk to others",
      "refuses_treatment": "No - engaged, agrees to medication and follow-up",
      "no_less_restrictive": "N/A - voluntary community treatment appropriate"
    }
  }
}
```

**This is IDENTICAL to Constraint 15 (SAFE-T) requirement.**

---

#### **Protocol 7: Cultural Safety Assessment (MANDATORY for Australian AMC)**
**Zero-tolerance requirement:** Address cultural considerations for ALL patients

**Must include:**
```json
"cultural_safety": {
  "aboriginal_tsi_status": {
    "question_asked": "Do you identify as Aboriginal or Torres Strait Islander?",
    "response": "No",
    "if_yes_actions": [
      "Offer Aboriginal health liaison officer",
      "Consider Social and Emotional Wellbeing (SEWB) framework",
      "Assess connection to culture/family/community/country/spirituality",
      "Historical trauma awareness (Stolen Generations, institutional racism)",
      "Culturally safe mental health services (e.g., Goolum Goolum, headspace Indigenous)",
      "Family involvement in care (with consent)"
    ]
  },
  "language_interpreter": {
    "english_first_language": "Yes",
    "if_no_actions": [
      "Offer professional interpreter (Language Line 1300 131 450)",
      "DO NOT use family members (confidentiality, accuracy, power imbalance)",
      "Book qualified interpreter for follow-up appointments",
      "Provide translated resources (e.g., Beyond Blue multilingual)"
    ]
  },
  "cultural_considerations": {
    "relevant_factors": [
      "Depression expression varies across cultures (somatic symptoms more prominent in Asian/Middle Eastern)",
      "Stigma barriers in some communities (normalize help-seeking)",
      "Family decision-making in collectivist cultures (involve family with consent)",
      "Alternative health practices (TCM, Ayurveda) - integrate where appropriate"
    ]
  },
  "lgbtqia_inclusive": {
    "pronoun_inquiry": "What pronouns do you use?",
    "inclusive_language": "Use gender-neutral terms (partner, not husband/wife) until disclosed",
    "specific_considerations": [
      "LGBTQIA+ youth 5x higher suicide risk",
      "Minority stress (discrimination, rejection) worsens mental health",
      "QLife 1800 184 527 (peer support for LGBTQIA+)",
      "Trans-affirmative care if gender dysphoria present"
    ]
  }
}
```

---

#### **Protocol 8: Red Flags and Safety Netting (MANDATORY)**
**Zero-tolerance requirement:** Specific warning signs for deterioration

**Structure:**
```json
"safety_netting": {
  "red_flags_patient_education": {
    "immediate_ed_if": [
      "Suicidal plan with intent to act",
      "Command hallucinations telling you to harm yourself/others",
      "Unable to care for yourself (not eating/drinking)",
      "Severe agitation or inability to keep safe"
    ],
    "call_gp_urgently_if": [
      "Suicidal thoughts increasing despite medication",
      "New side effects from medication (rash, tremor, confusion)",
      "Stopping medication without doctor approval",
      "Social withdrawal worsening"
    ]
  },
  "follow_up_plan": {
    "gp_review": "Dr Smith in 3 days (appointment booked)",
    "psychiatry": "Urgent clinic in 1 week (appointment letter given)",
    "psychology": "Mental Health Care Plan completed - 10 Medicare sessions",
    "crisis_contacts": [
      "Lifeline: 13 11 14 (24/7 crisis support)",
      "Beyond Blue: 1300 224 636",
      "Emergency: 000 or present to ED",
      "GP after hours: 13 SICK (13 7425)"
    ]
  },
  "collateral_information": {
    "next_of_kin": "Sister (Jane Doe) - aware of diagnosis and safety plan, will check daily",
    "gp_communication": "Discharge summary faxed to Dr Smith (03) 9876 5432"
  }
}
```

---

## Recommendations

### Immediate Actions

1. **STOP using current OSCE content immediately** - 0% deployment ready (vs claimed 96.5%)

2. **Create Constraint 16: OSCE Script Requirements** (900+ lines, similar to Constraint 15)

3. **Develop OSCE Content Generation PRD** with:
   - Complete clinical vignette templates (NOT placeholders)
   - 9-step history taking MANDATORY
   - SAFE-T for psychiatry OSCEs
   - Systematic radiology interpretation frameworks
   - Complete medication management with Australian names/PBS codes
   - Cultural safety assessment
   - Red flags and safety netting

4. **Create OSCE auto-fix scripts** (similar to MCQ SAFE-T auto-fix):
   ```bash
   scripts/osce_content_validator.py  # Detect placeholder text
   scripts/osce_content_generator.py  # Generate real clinical content from templates
   scripts/osce_safe_t_injector.py    # Add SAFE-T to psychiatry OSCEs
   scripts/osce_radiology_systematic.py # Add ABCDE/7-step/ABC frameworks
   ```

5. **Implement validation gates:**
   ```bash
   # Pre-deployment validation
   ./scripts/osce_pre_flight_validation.sh
   # Must exit code 0 before any OSCE deployment

   # Checks:
   # 1. No placeholder text (grep for "Clinical history relevant to")
   # 2. 9-step history present (all 9 sections exist)
   # 3. Specific examination findings (not "consistent with")
   # 4. Radiology systematic approach (ABCDE/7-step/ABC present)
   # 5. Medication management complete (doses, frequencies, PBS codes)
   # 6. SAFE-T present for psychiatry (mood disorders, psychosis, SI)
   # 7. Cultural safety addressed
   # 8. Red flags and safety netting present
   ```

---

### If Constraint 16 Needed

**Template sections (900+ lines minimum):**

1. **Introduction** (50 lines)
   - Purpose: Prevent placeholder OSCEs from deployment
   - Scope: ALL OSCE content (psychiatry, cardiology, respiratory, neurology, gastroenterology)
   - Zero-tolerance protocols: 8 mandatory protocols

2. **Protocol 1: Complete Clinical Vignette** (100 lines)
   - NO placeholder text
   - Patient demographics, presenting complaint with timeline
   - SOCRATES for pain, quantified severity
   - Red flags explicit
   - Setting and context

3. **Protocol 2: 9-Step History Taking** (150 lines)
   - All 9 steps MANDATORY
   - Detailed examples for each specialty
   - Validation checks

4. **Protocol 3: Systematic Physical Examination** (120 lines)
   - Inspection → Palpation → Percussion → Auscultation
   - Specific findings (NOT "consistent with")
   - Specialty-specific requirements

5. **Protocol 4: Radiology Systematic Interpretation** (180 lines)
   - ABCDE for CXR (detailed template)
   - 7-step for ECG (detailed template)
   - ABC for CT (detailed template)
   - ASUM for ultrasound
   - Technical adequacy assessment

6. **Protocol 5: Medication Management** (150 lines)
   - Australian drug names MANDATORY
   - Exact doses, frequencies, routes, durations
   - PBS codes and authority requirements
   - Drug interactions
   - Monitoring parameters
   - Patient counseling

7. **Protocol 6: SAFE-T Suicide Risk Assessment** (100 lines)
   - Cross-reference Constraint 15
   - MANDATORY for psychiatry OSCEs (mood disorders, psychosis, SI)
   - Mental Health Act criteria assessment

8. **Protocol 7: Cultural Safety** (80 lines)
   - Aboriginal/TSI inquiry MANDATORY
   - Interpreter offer for non-English speakers
   - LGBTQIA+ inclusive language
   - Cultural considerations in care

9. **Protocol 8: Red Flags and Safety Netting** (70 lines)
   - When to seek emergency care
   - Follow-up plans
   - Crisis contacts
   - Collateral communication

10. **Validation Scripts** (100 lines)
    - Pre-flight validation commands
    - Auto-fix feasibility assessment
    - Quality gate criteria

**Total: 900+ lines (similar to Constraint 15)**

---

### Auto-Fix Feasibility

**Assessment: LOW-MEDIUM (unlike SAFE-T which was HIGH)**

**Reasons:**
1. **SAFE-T auto-fix:** Add pre-written SAFE-T section to existing MCQ content → HIGH feasibility
2. **OSCE auto-fix:** Generate entire clinical scenarios from scratch → LOW feasibility

**Hybrid Approach (MEDIUM feasibility):**
- Use LLM (Claude API) to generate clinical vignettes from topic names
- Validate output against Constraint 16 protocols
- Auto-inject mandatory sections (SAFE-T, cultural safety, red flags)
- Human review for clinical accuracy

**Example workflow:**
```bash
# Step 1: Generate clinical vignette from placeholder
python scripts/osce_content_generator.py \
  --input "data/osces/psychiatry_40_osces.json" \
  --topic "Major Depressive Disorder" \
  --subtopic "MSE - Appearance & Behavior" \
  --output "data/osces/psychiatry_40_osces_generated.json"

# Step 2: Inject SAFE-T (auto-fix)
python scripts/osce_safe_t_injector.py \
  --input "data/osces/psychiatry_40_osces_generated.json" \
  --constraint "constraints/15-safe-t-suicide-risk-assessment.md"

# Step 3: Validate against Constraint 16
./scripts/osce_pre_flight_validation.sh \
  --input "data/osces/psychiatry_40_osces_generated.json" \
  --constraint "constraints/16-osce-script-requirements.md"
# Exit code 0 = PASS, 2 = CRITICAL violations

# Step 4: Human review (FRACP psychiatrist)
# Clinician reviews generated content for accuracy
```

---

## Comparison to Psychiatry SAFE-T Pattern

**Is the OSCE issue similar to psychiatry SAFE-T (100% missing critical protocol)?**

**Answer: YES and NO**

### Similarities to SAFE-T:
1. **100% systematic absence:** Just as ALL psychiatry MCQs missed SAFE-T, ALL OSCEs are placeholders
2. **Zero-tolerance violation:** Content cannot be deployed in current state
3. **Critical for patient safety:** Missing clinical content is dangerous for student education
4. **Auto-fix possible (partially):** Can inject mandatory sections (SAFE-T, cultural safety)

### Differences from SAFE-T:
1. **Content depth:**
   - SAFE-T: Missing 1 protocol from otherwise complete MCQs
   - OSCEs: Missing 100% of clinical content (everything is placeholder)

2. **Fix complexity:**
   - SAFE-T: Auto-inject pre-written SAFE-T section → HIGH feasibility
   - OSCEs: Generate entire clinical scenarios → LOW-MEDIUM feasibility

3. **Specialty scope:**
   - SAFE-T: Only psychiatry MCQs (40 items)
   - OSCEs: ALL specialties (psychiatry, cardiology, respiratory, general medicine, neurology, gastro - 200+ items)

4. **Root cause:**
   - SAFE-T: Content generator missed 1 critical protocol
   - OSCEs: Content generator produced templates, not actual content (systemic failure)

### Conclusion:

**OSCEs are WORSE than psychiatry SAFE-T** because:
- SAFE-T was a missing component in otherwise complete content
- OSCEs have NO CONTENT AT ALL - just templates
- SAFE-T affected 1 specialty (fixable with targeted scripts)
- OSCEs affect ALL specialties (requires complete regeneration)

**However, both share:**
- 100% systematic absence of critical requirements
- Zero-tolerance violations
- Need for Constraint documentation to prevent recurrence

**Therefore: YES, create Constraint 16 (more urgent than Constraint 15)**

---

## Supporting Evidence from Reports

### Mental-Health-Crisis-Expert (Psychiatry OSCE 009):
```
"CRITICAL: OSCE content is template-based placeholder, NOT real clinical scenario"
"CRITICAL: Patient presentation is generic"
"CRITICAL: No SAFE-T suicide risk assessment framework provided"
"CRITICAL: History field is placeholder"
"CRITICAL: Examination findings are placeholder"
"CRITICAL: Expected answers are generic templates without specific clinical detail"
"CRITICAL: References have EMPTY content field"

Deployment readiness: 0% (versus claimed 96.5% - likely referring to JSON structure compliance, NOT clinical content quality)

RECOMMENDATION: Do NOT use this batch for student assessment. Revert to content generation with REAL clinical vignettes.
```

### Medication-Management-Expert (Respiratory OSCE 004):
```
"OSCE contains NO medication management content to evaluate"
"Management section is generic placeholder text without actual treatment protocol"
"Cannot evaluate medication management when no medications are specified"

Current content is unsuitable for AMC Clinical Examination preparation as it provides no learning value for medication management skills.
```

### Radiology-Interpretation-Expert (Respiratory OSCE 004):
```
"All 50 OSCEs contain identical placeholder template text"
"No actual radiological findings described"
"Image descriptions are labels not findings"

DEPLOYMENT RISK: High-stakes imaging OSCEs lack 'Critical Findings Checklist'. Missing life-threatening findings = patient safety risk.

REJECT - Requires complete regeneration with specific radiological findings.
```

---

## Final Verdict

### Root Cause: **CONTENT DEFICIENCY - Systematic Placeholder Templates**

**This is a COMPLETE CONTENT FAILURE, not a system bug or structural issue.**

**Evidence:**
1. 100% of OSCEs contain placeholder text instead of actual clinical content
2. All evaluation criteria fail: medication management (0.0), radiology interpretation (2.0-3.5), clinical accuracy (4.0)
3. Empty reference citations (RAG returned metadata but no content)
4. Identical vital signs across all OSCEs (physiologically impossible)
5. 0% deployment readiness despite claimed 96.5% (measuring structure, not content)

**Recommendation: Create Constraint 16 with 8 zero-tolerance protocols**

**Estimated effort:**
- Constraint 16 creation: 8 hours (900+ lines, similar to Constraint 15)
- Auto-fix scripts: 20-30 hours (more complex than SAFE-T due to content generation)
- Content regeneration: 100-150 hours (200+ OSCEs × 0.5-0.75 hours each)
- Clinical validation: 40-60 hours (FRACP specialist review)

**Total: 168-208 hours (4-5 weeks with dedicated resources)**

---

## Constraint 16 File Structure Preview

```markdown
# Constraint 16: OSCE Script Requirements

## Purpose
Prevent placeholder/template OSCEs from deployment. Ensure ALL OSCE scripts contain complete, specific clinical content suitable for AMC Clinical Examination preparation.

## Scope
- ALL OSCE content types
- ALL specialties (psychiatry, cardiology, respiratory, neurology, gastroenterology, general medicine)
- ALL scenario types (emergency, clinic, inpatient, assessment)

## Zero-Tolerance Protocols (8 MANDATORY)

### Protocol 1: Complete Clinical Vignette (NO PLACEHOLDERS)
[100 lines - detailed requirements, examples, validation checks]

### Protocol 2: 9-Step History Taking (MANDATORY for AMC)
[150 lines - all 9 steps with specialty-specific examples]

### Protocol 3: Systematic Physical Examination
[120 lines - Inspection → Palpation → Percussion → Auscultation]

### Protocol 4: Radiology Systematic Interpretation
[180 lines - ABCDE/7-step/ABC frameworks with full templates]

### Protocol 5: Medication Management (Australian Standards)
[150 lines - Australian names, PBS codes, doses, drug interactions]

### Protocol 6: SAFE-T Suicide Risk Assessment
[100 lines - cross-reference Constraint 15, MANDATORY for psychiatry]

### Protocol 7: Cultural Safety (Australian AMC)
[80 lines - Aboriginal/TSI, interpreter, LGBTQIA+, cultural considerations]

### Protocol 8: Red Flags and Safety Netting
[70 lines - when to seek care, follow-up plans, crisis contacts]

## Validation Scripts
[100 lines - pre-flight validation, auto-fix tools, quality gates]

## Auto-Fix Procedures
[50 lines - LLM-assisted content generation, validation workflow]

Total: 900+ lines
```

---

**END OF ANALYSIS**

**CRITICAL ACTION REQUIRED:** Create Constraint 16 immediately to prevent further deployment of placeholder OSCE content.
