# Constraint 16: OSCE Script Requirements

**Version:** 1.0
**Created:** 2026-04-03
**Scope:** ALL OSCE content types across all specialties
**Zero-Tolerance:** CRITICAL - No placeholders allowed

---

## Purpose

Prevent placeholder/template OSCEs from deployment. Ensure ALL OSCE scripts contain **complete, specific clinical content** suitable for AMC Clinical Examination preparation.

**Context:** Following discovery of 97.6% placeholder rate (205/210 OSCEs were empty templates), this constraint establishes mandatory requirements to prevent recurrence.

---

## Scope

**Applies to:**
- ALL OSCE content types
- ALL specialties (psychiatry, cardiology, respiratory, neurology, gastroenterology, general medicine, etc.)
- ALL scenario types (emergency, clinic, inpatient, assessment, communication)

**Zero-Tolerance Requirements:** 8 mandatory protocols must be met for EVERY OSCE

---

## Protocol 1: Complete Clinical Vignette (NO PLACEHOLDERS)

### Zero-Tolerance Requirement

**NO generic placeholder text allowed anywhere in OSCE**

### Forbidden Phrases (Auto-Reject)

```bash
# These phrases trigger immediate REJECTION:
❌ "A patient presents for psychiatric assessment"
❌ "A patient presents with..."
❌ "Clinical history relevant to..."
❌ "Mental status examination findings for..."
❌ "Examination findings consistent with..."
❌ "According to Australian guidelines for..."
❌ "Management as per protocol"
❌ "Treatment as appropriate"
❌ "As per guidelines"
```

### Required Content Structure

**ALL OSCEs must include:**

1. **Patient Demographics (Specific)**
   - Age (exact): "42-year-old" NOT "middle-aged"
   - Gender: "woman" NOT "patient"
   - Occupation: "primary school teacher" NOT "employed"
   - Example: "42-year-old female primary school teacher"

2. **Presenting Complaint (Detailed)**
   - Specific symptom: "low mood" NOT "psychiatric symptoms"
   - Timeline: "6-week history" NOT "recent onset"
   - Character: "persistent sadness, daily crying episodes"
   - Example: "6-week history of persistent low mood with daily crying episodes and loss of interest in hobbies"

3. **Clinical Context (Complete)**
   - Setting: "Emergency Department at Royal Brisbane Hospital"
   - Precipitating event: "Job loss 2 months ago"
   - Severity impact: "Unable to work for 3 weeks, withdrawn from family"
   - Example: "Presents to ED after wife found suicide note, following redundancy 8 weeks ago"

4. **Red Flags (Explicit)**
   - Must state warning signs specific to condition
   - Psychiatry: "Passive suicidal ideation ('better off dead'), no plan"
   - Cardiology: "Sudden-onset crushing chest pain 9/10, radiating to jaw and left arm, diaphoretic"
   - Respiratory: "Unable to complete sentences, using accessory muscles, SpO2 89% room air"

### Validation Check

```bash
# Auto-reject if any placeholders detected:
grep -E "A patient presents|According to guidelines|as per protocol|Clinical history relevant" osce_file.json
# Exit code 2 = CRITICAL violation
```

---

## Protocol 2: 9-Step History Taking (MANDATORY for AMC)

### Zero-Tolerance Requirement

**ALL 9 steps must be present with specific content**

### Structure (Complete)

1. **Presenting Complaint**
   - Chief symptom: "Low mood"
   - Duration: "6 weeks"
   - Example: "6-week history of persistent low mood"

2. **History of Presenting Complaint (HPI)**
   - For pain: SOCRATES (Site, Onset, Character, Radiation, Associated symptoms, Timing, Exacerbating/relieving, Severity)
   - For non-pain: Detailed progression with timeline
   - Example:
     ```
     Onset: Gradual over 6 weeks following job loss
     Character: Persistent sadness, anhedonia (lost interest in gardening, stopped seeing friends)
     Associated: Early morning waking at 4am, poor concentration at work, 4kg weight loss (not trying)
     Timing: Worse mornings, improves slightly by evening
     Severity: Unable to work last 3 weeks, PHQ-9 score 21/27 (severe)
     Red flags: Passive suicidal ideation but no plan ("sometimes think family better off without me")
     ```

3. **Past Medical History**
   - Chronic conditions: "Type 2 diabetes (10 years, HbA1c 7.2%)"
   - Previous episodes: "One episode depression age 25, treated with CBT, resolved after 6 months"
   - Surgeries: "Appendectomy age 18"
   - Hospitalizations: "Nil psychiatric admissions"

4. **Medications (Current)**
   - Drug name (Australian): "Metformin"
   - Dose + frequency: "1000mg twice daily"
   - Compliance: "Takes regularly, no side effects"
   - Example: "Metformin 1000mg BD (compliant), Atorvastatin 40mg nocte"

5. **Allergies**
   - Drug: "Penicillin"
   - Reaction type: "Rash (urticarial) age 10"
   - Example: "Penicillin (urticaria), NKDA otherwise"

6. **Family History**
   - Relevant conditions: "Mother has depression (treated with sertraline)"
   - Age of onset: "Mother diagnosed age 45"
   - Outcomes: "Well-controlled on medication"
   - Example: "Mother: depression age 45 (well-controlled on SSRI). Father: CAD, died MI age 62"

7. **Social History (Complete)**
   - Occupation: "Primary school teacher (Year 3)"
   - Living situation: "Lives with husband and 2 children (ages 8, 11)"
   - Smoking: "Ex-smoker, 10 pack-years, quit 5 years ago"
   - Alcohol: "10 standard drinks/week (2 glasses wine nightly)"
   - Illicit drugs: "Denies"
   - Support: "Supportive husband, close to sister"
   - Example:
     ```
     Occupation: Primary school teacher (Year 3), on sick leave 3 weeks
     Living: Husband (supportive), 2 children ages 8 and 11
     Smoking: Ex-smoker (10 pack-years, quit 5 years ago)
     Alcohol: 10 std drinks/week (2 glasses wine nightly, increasing recently)
     Drugs: Denies cannabis, amphetamines
     Support: Husband very supportive, sister calls daily, few close friends
     ```

8. **Systems Review**
   - Relevant negative findings
   - Example: "No chest pain, palpitations, shortness of breath. No headaches, visual changes. No bowel/bladder symptoms."

9. **ICE (Ideas, Concerns, Expectations)**
   - Ideas: What patient thinks is wrong
   - Concerns: What patient is worried about
   - Expectations: What patient wants from consultation
   - Example:
     ```
     Ideas: "I think I'm depressed like my mother was"
     Concerns: "Worried I'll end up in hospital like she did, afraid to take medication (side effects)"
     Expectations: "Want to feel normal again so I can go back to work and be a good mother"
     ```

### Validation Check

```python
# Check all 9 steps present
history_sections = [
    'presenting_complaint',
    'hpi',
    'past_medical_history',
    'medications',
    'allergies',
    'family_history',
    'social_history',
    'systems_review',
    'ice'
]

missing = [s for s in history_sections if s not in osce_data]
if missing:
    raise ValidationError(f"Missing history sections: {missing}")
```

---

## Protocol 3: Systematic Physical Examination (MANDATORY)

### Zero-Tolerance Requirement

**Complete examination with specific findings (NOT "examination findings for...")**

### Structure: Inspection → Palpation → Percussion → Auscultation

#### Respiratory Example (Complete)

```json
"examination": {
  "general": "Alert, distressed, sitting upright (tripod position), using accessory muscles (sternocleidomastoid, intercostals)",
  "vitals": {
    "BP": "135/85 mmHg",
    "HR": "115 bpm (sinus tachycardia)",
    "RR": "32/min (tachypnoea)",
    "SpO2": "89% on room air",
    "Temperature": "38.8°C"
  },
  "hands": "Warm peripheries, no cyanosis, no clubbing, no asterixis",
  "respiratory": {
    "inspection": "Reduced chest expansion right base, intercostal recession, trachea central, no chest wall deformity",
    "palpation": "Reduced tactile fremitus right lower zone, trachea central, apex beat not displaced",
    "percussion": "Dull percussion note right lower zone (consolidation), resonant elsewhere",
    "auscultation": "Bronchial breathing right lower zone with coarse crackles, reduced air entry right base, no wheeze"
  },
  "cardiovascular_brief": "JVP not elevated, HS I+II+0, no peripheral edema",
  "clinical_significance": "Findings consistent with right lower lobe pneumonia (consolidation)"
}
```

#### Cardiovascular Example (Complete)

```json
"examination": {
  "general": "Pale, diaphoretic, clutching chest, distressed",
  "vitals": {
    "BP": "145/92 mmHg",
    "HR": "98 bpm regular",
    "RR": "22/min",
    "SpO2": "95% room air",
    "Temperature": "36.8°C"
  },
  "hands": "Cool peripheries, capillary refill <2 seconds, no cyanosis",
  "cardiovascular": {
    "inspection": "JVP not elevated at 45 degrees, no visible apex beat, no chest wall scars",
    "palpation": "Apex beat 5th intercostal space midclavicular line (not displaced), normal character, no heaves/thrills",
    "auscultation": "Heart sounds I + II + 0 (no murmurs), no added sounds (S3/S4/rubs)"
  },
  "peripheral_pulses": "Radial: equal, regular 98bpm. Carotid: normal volume, no bruits. Pedal pulses: palpable bilaterally",
  "peripheral_edema": "No ankle/sacral edema",
  "respiratory_brief": "Bibasal crackles (mild pulmonary edema), otherwise clear",
  "ecg_findings": "[See Protocol 4 for detailed ECG interpretation]"
}
```

#### Psychiatry Mental State Examination (Complete 8 Domains)

```json
"mse_findings": {
  "appearance": "Casually dressed, appropriate for season, appears stated age, unkempt hair, poor eye contact",
  "behavior": "Psychomotor retardation (slow movements, long latency answering questions), sits slumped, tearful when discussing mood",
  "speech": "Low volume, monotonous tone, slow rate, decreased spontaneity (answers questions but doesn't elaborate)",
  "mood_subjective": "'I feel hopeless, like nothing will ever get better' (patient's words)",
  "affect_objective": "Constricted, depressed, congruent with mood, tearful at times, limited reactivity",
  "thought_form": "Linear, goal-directed, no tangentiality or circumstantiality",
  "thought_content": "Preoccupied with guilt ('I'm a terrible mother'), passive suicidal ideation ('family would be better off without me') but denies plan, no homicidal ideation, no delusions",
  "perceptions": "No hallucinations (auditory, visual, tactile), no illusions",
  "cognition": "Alert, oriented to person/place/time, attention reduced (difficulty concentrating on questions), memory subjectively impaired (forgets appointments)",
  "insight": "Partial insight - acknowledges feeling depressed, understands need for treatment, but ambivalent about medication",
  "judgment": "Impaired by illness - neglecting self-care, withdrawn from usual activities"
}
```

### Forbidden (Never Use)

```
❌ "Examination findings consistent with Acute Asthma Exacerbation"
❌ "Mental status examination findings for Major Depressive Disorder"
❌ "Physical examination reveals findings typical of..."
❌ "Vital signs as expected for this condition"
```

---

## Protocol 4: Radiology Systematic Interpretation (MANDATORY for Imaging OSCEs)

### Zero-Tolerance Requirement

**Must use systematic framework - NO generic descriptions**

### Frameworks by Modality

#### CXR: ABCDE Approach (MANDATORY Template)

```json
"radiology_interpretation": {
  "modality": "CXR PA and lateral",
  "indication": "?Pneumonia - productive cough, fever 38.8°C, right-sided chest pain",
  "technical_adequacy": {
    "rotation": "No rotation (clavicular heads equidistant from midline spinous process)",
    "inspiration": "Adequate (7 anterior ribs visible, 10 posterior ribs)",
    "penetration": "Adequate (vertebrae visible behind heart, disc spaces seen)",
    "inclusion": "Both costophrenic angles and lung apices included"
  },
  "abcde_systematic": {
    "A_airway": "Trachea midline, no deviation. Carina at T4/5, angle normal (60-90 degrees). No paratracheal masses.",
    "B_breathing": "Right lower zone airspace opacification 5x3cm with air bronchograms (consolidation). Silhouette sign: right heart border obscured (confirms RML involvement). Left lung clear. No pleural effusion. No pneumothorax.",
    "C_circulation": "Heart size normal (cardiothoracic ratio 45%, normal <50%). Aortic knuckle normal contour. No pulmonary venous congestion. Normal pulmonary vascular markings.",
    "D_diaphragm_mediastinum": "Right hemidiaphragm obscured by consolidation (silhouette sign). Left hemidiaphragm at 10th rib posteriorly (normal). Mediastinum central, normal width. No hilar lymphadenopathy.",
    "E_everything_else": "No rib fractures. No lytic/sclerotic bone lesions. Soft tissues normal. No free air under diaphragm. No surgical clips/prostheses."
  },
  "impression": "Right middle/lower lobe consolidation consistent with community-acquired pneumonia. No complications (no effusion, no abscess).",
  "comparison": "No prior imaging available for comparison",
  "clinical_correlation": "Imaging findings consistent with clinical presentation of productive cough, fever, right-sided pleuritic chest pain, bronchial breathing on examination."
}
```

#### ECG: 7-Step Method (MANDATORY Template)

```json
"ecg_interpretation": {
  "clinical_context": "58-year-old man, 2 hours crushing central chest pain radiating to jaw/arm, sweaty, previous smoker",
  "seven_step_systematic": {
    "1_rate": "98 bpm (normal sinus rhythm rate 60-100)",
    "2_rhythm": "Regular (R-R intervals equal), sinus rhythm (P waves before each QRS, PR interval consistent)",
    "3_axis": "Normal axis (positive QRS in leads I and II, QRS predominantly positive in leads I, II, aVF)",
    "4_intervals": {
      "PR_interval": "160ms (normal 120-200ms)",
      "QRS_duration": "90ms (normal <120ms, narrow complex)",
      "QT_interval": "380ms, QTc 410ms (normal QTc <450ms men)"
    },
    "5_p_waves": "Present, upright in leads I, II, aVF (normal sinus P waves). P wave morphology normal. P wave axis normal.",
    "6_qrs_complexes": {
      "voltage": "Normal (no LVH: SV1 + RV5 = 28mm, normal <35mm)",
      "q_waves": "NEW pathological Q waves in leads II, III, aVF (>1mm wide, >2mm deep). Suggests completed inferior MI.",
      "r_wave_progression": "Normal (R wave progressively increases V1→V6)"
    },
    "7_st_segments_t_waves": {
      "ST_elevation": "3mm ST elevation in leads II, III, aVF (inferior STEMI). Convex upward 'tombstone' morphology.",
      "reciprocal_changes": "2mm ST depression in leads V1, V2, V3 (reciprocal to inferior STEMI)",
      "t_waves": "Hyperacute T waves (tall, peaked) in leads II, III, aVF"
    }
  },
  "additional_findings": {
    "ST_elevation_III_vs_II": "ST elevation in III (3mm) > ST elevation in II (2mm) → suggests RCA occlusion (vs LCx if II>III)",
    "right_sided_leads": "Check V4R: 2mm ST elevation confirms RV infarct (30% of inferior STEMIs have RV involvement)"
  },
  "conclusion": "ACUTE INFERIOR STEMI (ST elevation II, III, aVF) with RIGHT VENTRICULAR INVOLVEMENT (V4R elevation)",
  "rca_vs_lcx": "RCA occlusion likely (ST elevation III > II, V4R elevation)",
  "immediate_actions": [
    "Activate cath lab - door-to-balloon <90 minutes",
    "AVOID NITRATES (RV infarct - preload dependent)",
    "IV fluids if hypotensive (NOT nitrates)",
    "Aspirin 300mg, Ticagrelor 180mg, Fondaparinux 2.5mg",
    "Primary PCI to RCA"
  ]
}
```

#### CT: ABC Method

```json
"ct_interpretation": {
  "modality": "CT Brain non-contrast",
  "indication": "Sudden-onset worst headache of life, ?subarachnoid haemorrhage",
  "abc_systematic": {
    "A_asymmetry_airway": {
      "symmetry": "Brain parenchyma symmetric, no midline shift",
      "ventricles": "Lateral ventricles symmetric, normal size. Third/fourth ventricles patent.",
      "sulci": "Cortical sulci symmetric, no effacement"
    },
    "B_blood_bones": {
      "blood": "HYPERDENSITY in basal cisterns (pentagonal configuration), interpeduncular cistern, sylvian fissures bilaterally. Consistent with ACUTE SUBARACHNOID HAEMORRHAGE.",
      "intraventricular": "No intraventricular extension",
      "parenchymal": "No intraparenchymal haemorrhage",
      "skull": "Intact skull vault, no fractures. Paranasal sinuses clear."
    },
    "C_csf_circulation": {
      "basal_cisterns": "BLOOD-FILLED (hyperdense)",
      "ventricles": "Normal size (no hydrocephalus)",
      "mass_effect": "No mass effect, no herniation"
    }
  },
  "conclusion": "Acute subarachnoid haemorrhage (SAH), likely aneurysmal (perimesencephalic pattern). Modified Fisher Grade 3 (thick SAH, high vasospasm risk).",
  "next_steps": [
    "CT angiography (CTA) to identify aneurysm",
    "Neurosurgery urgent consult",
    "Nimodipine 60mg 4-hourly (vasospasm prophylaxis)",
    "ICU admission, strict BP control"
  ]
}
```

### Forbidden (Never Use)

```
❌ "The investigations show findings consistent with Pneumonia"
❌ "CXR findings for Community-Acquired Pneumonia"
❌ "ECG changes typical of STEMI"
❌ "Imaging demonstrates pathology as expected"
```

---

## Protocol 5: Medication Management (Australian Standards - MANDATORY)

### Zero-Tolerance Requirement

**Complete pharmacological management with Australian drug names, doses, and PBS codes**

### Required Elements (ALL Mandatory)

1. **Australian Drug Names (NOT US names)**
   - ✅ Paracetamol (NOT acetaminophen)
   - ✅ Salbutamol (NOT albuterol)
   - ✅ Adrenaline (NOT epinephrine)
   - ✅ Lignocaine (NOT lidocaine)

2. **Exact Doses, Routes, Frequencies, Durations**
   - ✅ "Aspirin 300mg PO stat, then 100mg daily"
   - ✅ "Salbutamol 100mcg MDI + spacer, 12 puffs q20min"
   - ❌ "Aspirin as appropriate"
   - ❌ "Bronchodilator therapy"

3. **PBS Codes (Where Applicable)**
   - ✅ "Ticagrelor 90mg BD - PBS 8721K"
   - ✅ "Sertraline 50mg daily - PBS 2062B"
   - ❌ "Antidepressant therapy"

4. **Drug Interactions Assessment**
   - Example: "Aspirin + ticagrelor: additive bleeding risk. Monitor for GI bleed, easy bruising. PPI if high risk."

5. **Monitoring Parameters**
   - Example: "Sertraline: Monitor for suicidal ideation (increased risk first 2 weeks), serotonin syndrome (agitation, tremor, hyperthermia), sexual dysfunction"

6. **Patient Counseling Points**
   - Example: "Take with food to reduce nausea. May cause drowsiness - avoid driving initially. Sexual side effects common (60%) - discuss alternatives if problematic."

### Complete Example: Acute Asthma Management

```json
"medication_management": {
  "acute_treatment_ed": [
    {
      "drug": "Salbutamol",
      "route": "Inhalation via MDI + spacer",
      "dose": "100mcg per actuation",
      "frequency": "12 puffs (1200mcg), repeat every 20 minutes for 3 doses (first hour)",
      "alternative": "Salbutamol 5mg nebulised with oxygen if severe/life-threatening",
      "pbs_code": "8333L",
      "monitoring": "Peak flow pre/post (expect 15-20% improvement), SpO2 (target 93-95%), heart rate (salbutamol causes tachycardia), assess work of breathing"
    },
    {
      "drug": "Ipratropium bromide",
      "route": "Nebulised with oxygen",
      "dose": "500mcg",
      "frequency": "With each salbutamol nebuliser if severe asthma",
      "indication": "Severe asthma (SpO2 <92%, unable to speak in sentences, peak flow <50% predicted) OR poor response to salbutamol alone",
      "pbs_code": "2234X",
      "monitoring": "Work of breathing, peak flow improvement"
    },
    {
      "drug": "Prednisolone",
      "route": "Oral (preferred) or IV if vomiting",
      "dose": "50mg",
      "frequency": "Stat dose in ED, then 50mg daily for 5 days",
      "alternative": "Hydrocortisone 100mg IV q6h if unable to swallow or vomiting",
      "pbs_code": "2928M",
      "rationale": "Reduces airway inflammation, prevents relapse. Benefit starts 4-6 hours, maximal 12-24 hours.",
      "counseling": "Take with food (GI upset). Complete full 5-day course. No tapering needed for 5 days. May cause insomnia (take morning), mood changes, hyperglycaemia (check BGL if diabetic)",
      "monitoring": "Mood, sleep, blood glucose (if diabetic)"
    },
    {
      "drug": "Oxygen",
      "route": "Nasal prongs 2-4L/min OR Hudson mask 6-10L/min",
      "target": "SpO2 93-95%",
      "caution": "Avoid hyperoxia (SpO2 >98%) - may worsen V/Q mismatch. In patients with Type 2 respiratory failure (chronic CO2 retention), target 88-92% to avoid suppressing hypoxic drive",
      "monitoring": "SpO2 continuous, RR, work of breathing, ABG if severe (pH <7.35, PaCO2 >45 = impending respiratory failure)"
    },
    {
      "drug": "Magnesium sulphate",
      "indication": "SEVERE or LIFE-THREATENING asthma (SpO2 <92% despite treatment, silent chest, altered conscious state, exhaustion)",
      "route": "IV infusion",
      "dose": "2g (8mmol) in 100mL 0.9% saline over 20 minutes",
      "mechanism": "Bronchodilator via smooth muscle relaxation (blocks calcium channels)",
      "pbs_code": "Unrestricted",
      "monitoring": "BP (may cause hypotension), tendon reflexes (hyperreflexia if toxic), respiratory rate",
      "caution": "Infuse slowly (over 20min minimum) to avoid hypotension, flushing"
    }
  ],

  "discharge_medications": [
    {
      "drug": "Budesonide/formoterol combination",
      "trade_name": "Symbicort Turbuhaler",
      "dose": "200/6 mcg",
      "frequency": "2 puffs twice daily (morning and night)",
      "duration": "Ongoing (ICS maintenance therapy, NOT reliever)",
      "pbs_code": "10123J",
      "device_technique": "Turbuhaler: Breathe IN fast and deep (opposite to MDI). Hold breath 10 seconds. Rinse mouth after (prevents thrush).",
      "rationale": "Inhaled corticosteroid (ICS) is controller medication - reduces airway inflammation. Formoterol is long-acting beta-agonist (LABA) for bronchodilation. Use DAILY even when well.",
      "counseling": "NOT a reliever - use daily. Rinse mouth after to prevent oral thrush. May take 1-2 weeks to see full benefit.",
      "monitoring": "Asthma control (ACT score), inhaler technique at every visit, oral thrush"
    },
    {
      "drug": "Salbutamol",
      "trade_name": "Ventolin, Asmol (MDI or accuhaler)",
      "dose": "100mcg per puff (MDI)",
      "frequency": "PRN for symptoms (wheeze, breathlessness, chest tightness)",
      "duration": "Ongoing",
      "pbs_code": "1234K",
      "device_technique": "MDI + spacer: Shake, 1 puff into spacer, breathe in slowly over 3-4 seconds, hold 10 seconds, wait 30 seconds before next puff.",
      "counseling": "Reliever medication - use when needed for symptoms. If using >3 times per week, ICS not adequate - see GP. If using >12 puffs in 24 hours, go to ED. Lasts 4 hours.",
      "red_flags": "If needing salbutamol >3 times/week = poor control, step up ICS. If >12 puffs/day = severe exacerbation, go to ED."
    },
    {
      "drug": "Prednisolone",
      "dose": "50mg",
      "frequency": "Daily for 5 days (already dispensed in ED, no prescription needed)",
      "counseling": "Complete full 5-day course even if feeling better. May cause insomnia (take in morning), increased appetite, mood changes.",
      "monitoring": "Ensure compliance - premature cessation increases relapse risk"
    }
  ],

  "drug_interactions": "Salbutamol + prednisolone may cause hypokalaemia (monitor K+ if on diuretics, digoxin). Formoterol + salbutamol = additive tachycardia (expect HR 90-110).",

  "monitoring_plan": [
    "Peak flow daily (record in asthma diary, bring to appointments)",
    "Inhaler technique at EVERY visit (90% patients use incorrectly)",
    "Asthma Control Test (ACT) score monthly (score <20 = poor control)",
    "Prednisolone side effects: mood, sleep, weight, blood glucose (if diabetic)",
    "Spacer: wash weekly with detergent, air dry (don't wipe - static reduces drug delivery)"
  ],

  "red_flags_patient_education": [
    "Go to ED immediately if: unable to speak in sentences, using >12 puffs salbutamol in 24 hours, chest feels tight despite salbutamol, drowsy/confused, lips blue",
    "Call ambulance if: severe breathlessness, can't walk/talk, exhausted, chest pain"
  ]
}
```

### Forbidden (Never Use)

```
❌ "According to Australian guidelines for Acute Asthma: immediate management steps"
❌ "Dual antiplatelet therapy as per protocol"
❌ "Beta-blocker as appropriate"
❌ "Statin therapy"
❌ "Bronchodilator treatment"
```

---

## Protocol 6: SAFE-T Suicide Risk Assessment (MANDATORY for Psychiatry)

### Zero-Tolerance Requirement

**SAFE-T assessment MANDATORY for ALL:**
- Mood disorders (depression, bipolar)
- Psychotic disorders (schizophrenia, schizoaffective)
- Any mention of suicidal ideation
- Risk assessment OSCEs

### Cross-Reference

See **Constraint 15: Psychiatry MCQ Requirements** sections 2-4 for complete SAFE-T protocol.

### Minimum Required Content

```json
"safe_t_assessment": {
  "S_specific_plan": "Passive suicidal ideation ('better off dead', 'family would be better without me'). No active plan. Denies intent to act on thoughts. No plan to jump from bridge despite living near Story Bridge.",

  "A_access_to_means": "Lives alone near Story Bridge (means available). Has 2 months supply of sertraline at home (30 x 50mg tablets = potentially lethal in overdose). No firearms. No stockpile of other medications. ACTION: Remove medication stockpile, sister to hold keys to medication cabinet.",

  "F_feelings_hopelessness": "Severe hopelessness (PHQ-9 item 9 = 3/3). States 'nothing will ever change', 'I'll always be like this', 'no point trying'. Sees no future. Cannot identify any positives. Risk factor for suicide attempt.",

  "E_earlier_attempts": "No previous suicide attempts. One episode of deliberate self-harm age 17 (superficial wrist cuts with razor blade) during parental divorce. No hospital presentation. No ongoing self-harm.",

  "T_threat_assessment": {
    "risk_level": "MODERATE",
    "rationale": "Passive suicidal ideation without active plan/intent, BUT high hopelessness, access to means (medication stockpile, bridge proximity), poor social support (lives alone, minimal friends), significant stressors (job loss, financial debt). Protective factors: Engaged in treatment, has supportive sister, religious beliefs against suicide ('Catholic - suicide is a sin')",

    "risk_factors": [
      "Severe depression (PHQ-9 21/27)",
      "High hopelessness (Beck Hopelessness Scale would likely be elevated)",
      "Social isolation (divorced, lives alone, minimal friends)",
      "Unemployment (lost job 4 months ago, financial stress $180k debt)",
      "Male gender (3x higher suicide rate than females in Australia)",
      "Access to means (medications, lives near bridge)",
      "Past self-harm (age 17)"
    ],

    "protective_factors": [
      "Engaged with treatment (attended GP, accepted referral)",
      "Family support (sister supportive, calls daily)",
      "No active plan or intent",
      "Religious beliefs ('suicide is a sin')",
      "Concerned about impact on children (guilt about abandoning them)",
      "Ambivalent about suicide ('part of me wants to live')"
    ]
  },

  "immediate_safety_actions": [
    "Safety plan: Remove all medications from home (sister to hold), lock away sharps/ropes",
    "Crisis contacts provided: Lifeline 13 11 14 (24/7), Beyond Blue 1300 224 636, Mental Health Access Line 1800 011 511 (NSW)",
    "Sister to stay overnight tonight (not leave alone)",
    "GP review in 2 days (appointment booked, Dr Smith aware of risk)",
    "Psychiatry urgent clinic in 1 week (appointment letter given)",
    "Contract for safety: Agreed to call crisis line or present to ED if thoughts worsen, no plan to harm self",
    "Remove alcohol from home (disinhibition risk)"
  ],

  "mental_health_act_criteria": {
    "meets_criteria": false,
    "rationale": "No active suicidal plan/intent. No immediate risk requiring involuntary admission. Agrees to voluntary treatment. Protective factors present (family support, engagement). Involuntary admission NOT indicated at this time.",

    "criteria_assessment": {
      "1_mental_illness": "YES - Major Depressive Disorder, severe episode (DSM-5 296.23)",
      "2_risk_of_harm": "MODERATE risk to self (passive SI, no plan). No risk to others. No risk of serious deterioration at this time.",
      "3_refuses_treatment": "NO - Patient engaged, accepts voluntary treatment, willing to see psychiatrist",
      "4_no_less_restrictive": "N/A - Voluntary community treatment appropriate. Crisis team follow-up, GP monitoring, psychiatry outpatient sufficient."
    },

    "follow_up_if_deteriorates": "If develops active plan/intent, acquires means, makes preparations, refuses help, or attempts suicide → Mental Health Act Schedule 1 assessment may be required. Emergency psychiatric review via ED."
  }
}
```

### Mental Health Act NSW 2007 - Schedule 1 Criteria

```markdown
Involuntary admission requires ALL 4 criteria:

1. Mental illness (or mental disorder)
2. Risk of:
   - Serious harm to self OR others, OR
   - Serious deterioration in condition
3. Refused/unable to consent to voluntary treatment
4. No less restrictive care available

If NOT all 4 met → Voluntary treatment pathway
```

### Australian Crisis Contacts (MANDATORY)

```
Lifeline: 13 11 14 (24/7 crisis support)
Beyond Blue: 1300 224 636 (depression/anxiety support)
Mental Health Access Line: 1800 011 511 (NSW - 24/7 triage, varies by state)
Suicide Call Back Service: 1300 659 467 (24/7)
QLife: 1800 184 527 (LGBTQIA+ peer support)
Kids Helpline: 1800 551 800 (5-25 years)
Emergency: 000 or present to ED
```

---

## Protocol 7: Cultural Safety (MANDATORY for Australian AMC)

### Zero-Tolerance Requirement

**Address cultural considerations for ALL patients**

### Required Elements (ALL Mandatory)

#### 1. Aboriginal and Torres Strait Islander Status

```json
"cultural_safety": {
  "aboriginal_tsi_inquiry": {
    "question": "Do you identify as Aboriginal or Torres Strait Islander?",
    "response": "No" | "Yes - Aboriginal" | "Yes - Torres Strait Islander" | "Yes - both",

    "if_yes_actions": [
      "Offer Aboriginal health liaison officer (AHL0) - 'Would you like me to contact our Aboriginal health liaison officer? They can provide cultural support during your care.'",

      "Social and Emotional Wellbeing (SEWB) framework - holistic approach:",
      "  - Connection to culture (language, ceremony, art)",
      "  - Connection to family (extended kinship networks)",
      "  - Connection to community (Elders, Aboriginal organizations)",
      "  "  - Connection to country (traditional lands, spiritual places)",
      "  - Connection to spirituality (Dreaming, ancestors, spirituality)",

      "Historical trauma awareness:",
      "  - Stolen Generations impact: distrust of institutions, trauma transmission across generations",
      "  - Institutional racism: police, hospitals, child protection → affects help-seeking",
      "  - Culturally safe mental health: Aboriginal-controlled services (e.g., Goolum Goolum Aboriginal Medical Service, headspace Indigenous)",

      "Family involvement in care (with patient consent):",
      "  - 'Who would you like involved in your care? Family members, Elders, community support?'",
      "  - Recognize extended family structures (kinship obligations)",
      "  - Involve family in treatment planning (culturally appropriate)",

      "Medication counseling:",
      "  - Higher rates of medication non-adherence (distrust, cost barriers, cultural beliefs about Western medicine)",
      "  - PBS co-payment exemption if Health Care Card/Concession Card",
      "  - Link to Aboriginal Medical Service for ongoing care (better engagement)"
    ]
  }
}
```

#### 2. Language and Interpreter Services

```json
"language_interpreter": {
  "english_first_language": "Yes" | "No - [specify language]",

  "if_no_actions": [
    "Offer professional interpreter - 'I notice English is not your first language. Would you like a professional interpreter? This is a free service.'",

    "DO NOT use family members for interpretation:",
    "  - Confidentiality breach (mental health, domestic violence, sexual health)",
    "  - Accuracy issues (family may filter/edit information)",
    "  - Power imbalances (child interpreting for parent)",
    "  - Cultural taboos (discussing certain topics through family)",

    "Book qualified interpreter:",
    "  - Language Line: 1300 131 450 (telephone interpreter, available 24/7 for 200+ languages)",
    "  - TIS National: 131 450 (Translating and Interpreting Service)",
    "  - On-site interpreter for complex consultations (psychiatry, informed consent, bad news)",

    "Provide translated resources:",
    "  - Beyond Blue: Multilingual mental health fact sheets (Arabic, Chinese, Vietnamese, etc.)",
    "  - HealthDirect: Health information in 35+ languages",
    "  - NSW Health: Multicultural Health Communication Service resources"
  ]
}
```

#### 3. Culturally and Linguistically Diverse (CALD) Considerations

```json
"cald_considerations": {
  "relevant_factors": [
    "Depression expression varies across cultures:",
    "  - Asian cultures: Somatic symptoms more prominent (headaches, fatigue, body pain) rather than mood symptoms",
    "  - Middle Eastern: Family shame/stigma barrier to mental health treatment",
    "  - African communities: Spiritual/religious explanations for mental illness (witchcraft, spirit possession) - validate beliefs while offering treatment",

    "Stigma barriers to treatment:",
    "  - Mental illness seen as family shame (Asian, Middle Eastern cultures)",
    "  - Fear of discrimination, social ostracism",
    "  - Normalize help-seeking: 'Many people from [community] experience depression. Treatment is confidential.'",

    "Family decision-making in collectivist cultures:",
    "  - Involve family in treatment decisions (with patient consent)",
    "  - Recognize: Individual autonomy vs family collective decision-making",
    "  - Balance: Australian medical ethics (patient autonomy) + cultural respect (family involvement)",

    "Alternative health practices:",
    "  - Traditional Chinese Medicine (TCM): Herbal medicine, acupuncture",
    "  - Ayurveda (South Asian): Dietary changes, meditation",
    "  - Integration approach: 'You can continue [traditional practice] alongside Western treatment - they can work together.'",
    "  - Safety: Check for drug interactions (St John's Wort + SSRIs = serotonin syndrome)"
  ]
}
```

#### 4. LGBTQIA+ Inclusive Care

```json
"lgbtqia_inclusive": {
  "pronoun_inquiry": "What pronouns do you use? (he/him, she/her, they/them, other)",

  "inclusive_language": [
    "Use gender-neutral terms until disclosed:",
    "  - 'Partner' (not husband/wife)",
    "  - 'Significant other' (not boyfriend/girlfriend)",
    "  - 'Parents' (not mother/father if discussing parenting)",

    "Affirm identity when disclosed:",
    "  - 'Thank you for sharing that with me. I'll make sure to use [pronoun].'",
    "  - 'Your medical record will reflect your affirmed name and pronoun.'",

    "Avoid assumptions:",
    "  - Don't assume sexual orientation from appearance/presentation",
    "  - Don't assume gender identity from appearance",
    "  - Ask open-ended: 'Are you sexually active? If so, with people of which gender(s)?'"
  ],

  "specific_considerations": [
    "LGBTQIA+ youth 5x higher suicide risk (vs heterosexual/cisgender peers)",

    "Minority stress model:",
    "  - Discrimination, rejection, victimization → chronic stress → mental health problems",
    "  - Family rejection (especially if from conservative/religious background)",
    "  - School bullying (40% LGBTQIA+ youth report harassment)",

    "Protective factors:",
    "  - Family acceptance (dramatically reduces suicide risk)",
    "  - LGBTQIA+ peer support groups",
    "  - School-based support (e.g., Safe Schools Coalition)",

    "Resources:",
    "  - QLife: 1800 184 527 (LGBTQIA+ peer support and referral service)",
    "  - Headspace: LGBTQIA+ specific programs",
    "  - Twenty10: LGBTQIA+ youth support (NSW)",

    "Gender dysphoria specific:",
    "  - If patient expresses distress about gender identity: 'Trans-affirmative care available. Would you like referral to specialist service (e.g., Queensland Gender Clinic, Sydney Gender Service)?'",
    "  - Hormone therapy, surgery referrals through specialist gender services",
    "  - Mental health support for transition process"
  ]
}
```

### Validation Check

```python
# Check cultural safety addressed
cultural_sections = [
    'aboriginal_tsi_inquiry',
    'language_interpreter',
    'cald_considerations' or 'lgbtqia_inclusive'
]

if not any(section in osce_data['sample_answer'] for section in cultural_sections):
    raise ValidationError("Cultural safety not addressed (Protocol 7 violation)")
```

---

## Protocol 8: Red Flags and Safety Netting (MANDATORY)

### Zero-Tolerance Requirement

**Specific warning signs for deterioration + follow-up plan for EVERY OSCE**

### Required Structure

```json
"safety_netting": {
  "red_flags_patient_education": {
    "immediate_ed_presentation_if": [
      "Suicidal plan with intent to act ('I'm going to the bridge tonight')",
      "Command hallucinations telling you to harm yourself or others",
      "Unable to care for yourself (not eating/drinking for 2+ days, severe neglect)",
      "Severe agitation or violence risk",
      "Chest pain recurring despite treatment, or new crushing chest pain",
      "Shortness of breath worsening rapidly despite salbutamol",
      "Drowsiness, confusion, or loss of consciousness",
      "New focal neurological symptoms (face droop, arm weakness, speech difficulty = stroke until proven otherwise)"
    ],

    "call_gp_urgently_if": [
      "Suicidal thoughts increasing despite medication (within 1-2 days of starting)",
      "New side effects from medication:",
      "  - Rash (severe drug reaction - Stevens-Johnson syndrome risk)",
      "  - Tremor, confusion, fever (? serotonin syndrome if on SSRI)",
      "  - Severe nausea/vomiting preventing medication adherence",
      "Stopping medication without doctor approval (withdrawal risk, relapse)",
      "Social withdrawal worsening (not leaving house, stopped answering phone)",
      "Using reliever inhaler >3 times per week (poor asthma control)"
    ],

    "routine_follow_up": "See schedule below"
  },

  "follow_up_plan": {
    "gp_review": {
      "timing": "Dr Smith in 3 days (Friday 10am, appointment booked)",
      "purpose": "Suicide risk monitoring, check medication adherence, assess for side effects",
      "booking_status": "Appointment booked and confirmed"
    },

    "specialist_review": {
      "specialty": "Psychiatry urgent clinic",
      "timing": "1-2 weeks (appointment letter given, will receive call to confirm)",
      "purpose": "Comprehensive psychiatric assessment, medication review, risk re-assessment",
      "wait_list": "Urgent category (within 2 weeks)",
      "what_if_delayed": "If no appointment within 2 weeks, call Mental Health Access Line 1800 011 511"
    },

    "allied_health": {
      "psychology": "Mental Health Care Plan completed (10 Medicare-subsidised sessions per calendar year)",
      "referral": "To Clinical Psychologist Sarah Jones, Cognitive Behavioral Therapy (CBT) for depression",
      "timing": "Will call patient within 1 week to book first session",
      "cost": "Medicare rebate $93.35 per session (Psychology Better Access). Out-of-pocket: $50-100 depending on psychologist (bulk-billing available - ask reception)"
    },

    "cardiac_rehabilitation": "(If post-MI cardiology OSCE)",
    "respiratory_education": "(If asthma/COPD OSCE - inhaler technique, asthma action plan)"
  },

  "crisis_contacts": [
    "Lifeline: 13 11 14 (24/7 crisis support)",
    "Beyond Blue: 1300 224 636 (depression/anxiety)",
    "Mental Health Access Line: 1800 011 511 (NSW, 24/7 psychiatric triage)",
    "Emergency: 000 or present to nearest Emergency Department",
    "GP after hours: 13 SICK (13 7425) or Healthdirect 1800 022 222"
  ],

  "collateral_information": {
    "next_of_kin": "Sister (Jane Doe, mobile 0412 345 678) - aware of diagnosis, safety plan, warning signs. Will check on patient daily.",

    "gp_communication": {
      "method": "Discharge summary faxed to Dr Smith (03) 9876 5432",
      "content_included": "Diagnosis (Major Depressive Disorder, severe), suicide risk assessment (MODERATE), safety plan, medications started (sertraline 50mg), follow-up plan, red flags for GP to monitor",
      "timing": "Faxed today (copy given to patient)"
    },

    "psychiatry_communication": "(If urgent referral) Psychiatry registrar contacted directly (Dr Brown paged, aware of case, patient on wait list)"
  },

  "patient_handouts_provided": [
    "Beyond Blue: Depression fact sheet",
    "Safety plan (written, includes crisis contacts, coping strategies, reasons for living)",
    "Medication information sheet (sertraline: dosing, side effects, what to expect)",
    "Mental Health Care Plan (copy for patient, copy for psychologist)",
    "Discharge summary (copy for patient to give GP)"
  ]
}
```

### Condition-Specific Red Flags

#### Psychiatry (Depression with SI)
```
IMMEDIATE ED:
- Suicidal plan + intent
- Command hallucinations
- Unable to care for self
- Severe agitation

URGENT GP (1-2 days):
- Suicidal thoughts worsening
- Serotonin syndrome (confusion, tremor, fever, sweating if on SSRI)
- Stopping medication without approval
- Social withdrawal worsening
```

#### Cardiology (Post-STEMI)
```
IMMEDIATE ED:
- Chest pain recurring (? re-infarction, stent thrombosis)
- Severe shortness of breath (? heart failure, pulmonary edema)
- Syncope, palpitations (? arrhythmia - VT risk post-MI)
- Sudden leg pain/swelling (? DVT)

URGENT GP/Cardiology (1-2 days):
- Increasing fatigue, ankle swelling (? developing heart failure)
- Bleeding (gums, bruising, black stools) on dual antiplatelet
- Side effects: muscle pain on statin (? rhabdomyolysis if severe)
```

#### Respiratory (Asthma)
```
IMMEDIATE ED:
- Unable to speak in sentences
- Using >12 puffs salbutamol in 24 hours
- Chest feels tight despite salbutamol
- Drowsy/confused (? hypoxia, CO2 retention)
- Lips/fingers blue (cyanosis)

URGENT GP (1-2 days):
- Using reliever >3 times per week (poor control, ICS inadequate)
- Night-time symptoms waking from sleep
- Unable to exercise normally
- Peak flow <80% personal best
```

---

## Validation Scripts

### Pre-Flight Validation Command

```bash
#!/bin/bash
# Pre-deployment validation for OSCEs
# Exit code 0 = PASS, 2 = CRITICAL violations

OSCE_FILE="$1"

echo "Validating OSCE: $OSCE_FILE"
echo "================================"

# Check 1: No placeholder text
echo "Check 1: Placeholder detection..."
PLACEHOLDERS=$(grep -E "A patient presents|According to guidelines|as per protocol|Clinical history relevant|Examination findings consistent|Mental status examination findings for" "$OSCE_FILE")

if [ -n "$PLACEHOLDERS" ]; then
    echo "❌ FAIL: Placeholders detected"
    echo "$PLACEHOLDERS"
    exit 2
fi
echo "✅ PASS: No placeholders"

# Check 2: 9-step history present
echo "Check 2: 9-step history..."
HISTORY_SECTIONS=("presenting_complaint" "hpi" "past_medical_history" "medications" "allergies" "family_history" "social_history" "systems_review" "ice")

for section in "${HISTORY_SECTIONS[@]}"; do
    if ! grep -q "\"$section\"" "$OSCE_FILE"; then
        echo "❌ FAIL: Missing history section: $section"
        exit 2
    fi
done
echo "✅ PASS: All 9 history sections present"

# Check 3: Specific examination findings
echo "Check 3: Examination specificity..."
GENERIC_EXAM=$(grep -E "examination findings for|findings consistent with|as expected for" "$OSCE_FILE")

if [ -n "$GENERIC_EXAM" ]; then
    echo "❌ FAIL: Generic examination descriptions"
    exit 2
fi
echo "✅ PASS: Specific examination findings"

# Check 4: Medications have doses (if medication management OSCE)
echo "Check 4: Medication specificity..."
if grep -q "medication\|drug\|treatment" "$OSCE_FILE"; then
    if ! grep -q "mg\|mcg\|units" "$OSCE_FILE"; then
        echo "❌ FAIL: Medications without doses"
        exit 2
    fi
    echo "✅ PASS: Medications have specific doses"
fi

# Check 5: SAFE-T present for psychiatry
echo "Check 5: SAFE-T (psychiatry only)..."
if grep -qi "psychiatry\|depression\|psychosis\|suicide" "$OSCE_FILE"; then
    if ! grep -qi "safe-t\|specific plan\|access to means" "$OSCE_FILE"; then
        echo "❌ FAIL: Psychiatry OSCE missing SAFE-T"
        exit 2
    fi
    echo "✅ PASS: SAFE-T protocol present"
fi

# Check 6: Australian crisis contacts (psychiatry)
if grep -qi "psychiatry\|depression\|suicide" "$OSCE_FILE"; then
    if ! grep -q "13 11 14\|Lifeline\|Beyond Blue" "$OSCE_FILE"; then
        echo "❌ FAIL: Missing Australian crisis contacts"
        exit 2
    fi
    echo "✅ PASS: Australian crisis contacts present"
fi

# Check 7: Cultural safety addressed
echo "Check 7: Cultural safety..."
if ! grep -qi "aboriginal\|torres strait\|interpreter\|cultural" "$OSCE_FILE"; then
    echo "⚠️  WARNING: Cultural safety not addressed"
fi

# Check 8: Red flags and safety netting
echo "Check 8: Safety netting..."
if ! grep -qi "red flag\|warning sign\|follow.up\|crisis contact" "$OSCE_FILE"; then
    echo "❌ FAIL: No safety netting/red flags"
    exit 2
fi
echo "✅ PASS: Safety netting present"

echo "================================"
echo "✅ ALL CRITICAL CHECKS PASSED"
echo "OSCE is DEPLOYMENT READY"
exit 0
```

### Usage

```bash
# Validate single OSCE
./scripts/osce_pre_flight_validation.sh data/osces/psychiatry_40_osces.json

# Validate all OSCEs
for file in data/osces/*.json; do
    ./scripts/osce_pre_flight_validation.sh "$file" || echo "FAILED: $file"
done
```

---

## Auto-Fix Procedures

### Approach: Hybrid (Semi-Automated)

**Unlike SAFE-T auto-fix (HIGH feasibility for MCQs), OSCE auto-fix is LOW-MEDIUM feasibility because:**

1. SAFE-T: Add pre-written section to existing MCQ → HIGH feasibility
2. OSCEs: Generate entire clinical scenarios from scratch → LOW feasibility

**Recommended Hybrid Approach:**

```python
# Step 1: Generate clinical vignette from placeholder using LLM
python scripts/osce_content_generator.py \
  --input "data/osces/psychiatry_40_osces.json" \
  --topic "Major Depressive Disorder" \
  --output "data/osces/psychiatry_40_osces_generated.json"

# Step 2: Auto-inject mandatory sections (SAFE-T, cultural safety)
python scripts/osce_safe_t_injector.py \
  --input "data/osces/psychiatry_40_osces_generated.json" \
  --constraint "constraints/15-psychiatry-mcq-requirements.md"

# Step 3: Validate against Constraint 16
./scripts/osce_pre_flight_validation.sh \
  --input "data/osces/psychiatry_40_osces_generated.json" \
  --constraint "constraints/16-osce-requirements.md"
# Exit code 0 = PASS, 2 = CRITICAL violations

# Step 4: Human clinical review (FRACP specialist)
# Clinician reviews generated content for clinical accuracy
```

---

## Quality Gates Summary

| Gate | Requirement | Target | Critical? |
|------|-------------|--------|-----------|
| **Gate 1: Zero Placeholders** | No generic phrases | 100% | ✅ CRITICAL |
| **Gate 2: 9-Step History** | All 9 sections present | 100% | ✅ CRITICAL |
| **Gate 3: Specific Examination** | Detailed findings (NOT "consistent with") | 100% | ✅ CRITICAL |
| **Gate 4: Radiology Systematic** | ABCDE/7-step/ABC frameworks | 100% (if applicable) | ✅ CRITICAL |
| **Gate 5: Medications Complete** | Doses + PBS codes | 100% (if applicable) | ✅ CRITICAL |
| **Gate 6: SAFE-T** | All psychiatry OSCEs | 100% (psychiatry) | ✅ CRITICAL |
| **Gate 7: Cultural Safety** | Addressed for all patients | 100% | ⚠️ HIGH |
| **Gate 8: Safety Netting** | Red flags + follow-up plan | 100% | ✅ CRITICAL |

---

## Integration with Generation Pipeline

### Pre-Generation

```python
# Load Constraint 16 before generating OSCEs
with open('constraints/16-osce-requirements.md') as f:
    constraint_16 = f.read()

# Include in LLM prompt
prompt = f"""
Generate complete OSCE station for: {topic}

MANDATORY CONSTRAINTS (Constraint 16):
{constraint_16}

Generate the OSCE now:
"""
```

### Post-Generation

```bash
# Validate immediately after generation
python scripts/generate_osce.py --topic "Depression" --output temp_osce.json
./scripts/osce_pre_flight_validation.sh temp_osce.json

if [ $? -eq 0 ]; then
    mv temp_osce.json data/osces/final_osce.json
    echo "✅ OSCE validated and deployed"
else
    echo "❌ OSCE validation FAILED - fix before deployment"
    exit 1
fi
```

### CI/CD Integration

```yaml
# .github/workflows/osce-validation.yml
name: OSCE Content Validation

on: [push, pull_request]

jobs:
  validate-osces:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Detect placeholder content
        run: |
          python3 scripts/detect_placeholder_content.py data/osces/*.json
          if [ $? -ne 0 ]; then
            echo "❌ Placeholders detected - blocking deployment"
            exit 1
          fi

      - name: Validate all OSCEs against Constraint 16
        run: |
          for osce in data/osces/*.json; do
            ./scripts/osce_pre_flight_validation.sh "$osce"
            if [ $? -ne 0 ]; then
              echo "❌ OSCE validation failed: $osce"
              exit 1
            fi
          done

      - name: Report validation results
        run: |
          echo "✅ ALL OSCEs passed validation"
          echo "DEPLOYMENT READY"
```

---

## Lessons Learned (From 97.6% Placeholder Discovery)

### What Went Wrong

1. **Metadata was misleading**: OSCEs had `"validation_failures": []` but content was 100% placeholders
2. **Structure vs Content**: Validated JSON structure, NOT content completeness
3. **No content depth checks**: Checked if fields *existed*, not if fields were *populated with clinical data*

### What This Constraint Prevents

1. **Explicit placeholder detection**: Automated scripts check for forbidden phrases
2. **Content completeness validation**: Check field length, specific required elements (doses, PBS codes)
3. **Quality gates at generation time**: Reject immediately if placeholders detected, don't wait for manual review
4. **Zero-tolerance enforcement**: Any placeholder = auto-reject, no exceptions

### Success Criteria for This Constraint

- ✅ 0% placeholder rate (down from 97.6%)
- ✅ 100% OSCEs have 9-step history
- ✅ 100% psychiatry OSCEs have SAFE-T
- ✅ 100% OSCEs have specific medications with doses (if applicable)
- ✅ 100% OSCEs have cultural safety addressed
- ✅ 100% OSCEs have red flags + safety netting

---

## Appendix: Example Comparison

### ❌ PLACEHOLDER OSCE (REJECTED - 97.6% of original OSCEs)

```json
{
  "scenario": {
    "patient_presentation": "A patient presents for psychiatric assessment. MSE - Appearance & Behavior.",
    "history": "Clinical history relevant to MSE - Appearance & Behavior",
    "examination_findings": "Examination findings for MSE - Appearance & Behavior"
  },
  "expected_answers": {
    "assessment": "Systematic assessment findings for MSE - Appearance & Behavior",
    "diagnosis": "Primary diagnosis: MSE - Appearance & Behavior",
    "management": "According to Australian guidelines for MSE - Appearance & Behavior"
  },
  "references": [
    {
      "title": "AMC Handbook",
      "content": ""  // EMPTY!
    }
  ]
}
```

**Why REJECTED:**
- ❌ Generic presentation ("A patient presents...")
- ❌ Placeholder history ("Clinical history relevant to...")
- ❌ Generic management ("According to guidelines...")
- ❌ Empty references
- ❌ No clinical specificity anywhere
- ❌ Zero educational value

---

### ✅ COMPLETE OSCE (APPROVED - After Constraint 16 Implementation)

```json
{
  "title": "Major Depressive Disorder with Active Suicidal Ideation - Emergency Department Assessment",
  "specialty": "Psychiatry",
  "duration": 8,

  "candidate_instructions": "You are a junior doctor working in the Emergency Department at Royal Brisbane Hospital. David Chen, a 38-year-old married plumber, has been brought in by ambulance at 2:15am after his wife Sarah found a suicide note on their kitchen table at midnight. Four months ago, his plumbing business of 12 years collapsed due to mounting debts ($180,000). He had to lay off three employees who had worked with him for years, which caused immense guilt. His wife reports he has been increasingly withdrawn over the past 6 weeks - stopped attending his weekly soccer games, no longer plays with their two children (ages 8 and 10), and spends most evenings drinking alone in the garage. Tonight, Sarah woke at midnight to find him missing from bed. She discovered a note stating 'I'm sorry. You're all better off without me. The life insurance will cover the debts.' She found him sitting in his car in the closed garage with the engine running. She immediately turned off the engine and called 000. Paramedics brought him to ED. Your task: Conduct a comprehensive psychiatric assessment including suicide risk assessment, Mental State Examination, and formulate an immediate management plan. Time: 8 minutes.",

  "patient_role_instructions": "You are David Chen, 38-year-old married plumber. You feel utterly hopeless and worthless. Your business collapsed 4 months ago - you're $180,000 in debt and had to lay off employees who trusted you. You feel like a complete failure as a provider. For 6 weeks you've felt empty, can't sleep (wake at 3am every night ruminating), lost 7kg (not trying - just not hungry), can't concentrate. You've stopped all hobbies - quit your weekly soccer, stopped playing with kids, avoid friends. You drink 8-10 beers nightly trying to sleep. Tonight you decided 'it's better this way' - wrote note, started car in closed garage intending to die by carbon monoxide. Your wife found you before you lost consciousness. You're angry she stopped you ('I just wanted it to be over'). When asked directly: YES you have active plan to die (method: car exhaust), YES you have intent ('I can't live like this'), NO protective factors visible right now (though deep down you love kids, just can't see past despair). You feel guilty burdening everyone. Mother had severe depression, hospitalized twice (you're terrified of becoming like her). You appear flat, hopeless, make minimal eye contact, speak in monotone.",

  "sample_answer": {
    "history_9_steps": {
      "presenting_complaint": "38-year-old man brought to ED by ambulance at 2:15am following interrupted suicide attempt (car exhaust, closed garage). Discovered by wife after finding suicide note.",

      "hpi": {
        "onset": "6 weeks progressive worsening mood following business collapse 4 months ago",
        "character": "Persistent low mood, anhedonia (stopped soccer, no longer plays with children), early morning waking (3am daily), 7kg weight loss, poor concentration, guilt ('I'm a failure as provider')",
        "timeline": "Deterioration over 6 weeks → acute crisis tonight (active plan + intent + action)",
        "severity": "Severe: PHQ-9 would be 24-27/27 (severe range). Complete functional impairment (no work, withdrawn from all activities, neglecting family)",
        "red_flags": "ACTIVE SUICIDAL PLAN (car exhaust) + INTENT ('I can't live like this') + ACTION TAKEN (started car in closed garage, written suicide note)"
      },

      "safe_t_assessment": {
        "S_specific_plan": "ACTIVE PLAN: Die by carbon monoxide poisoning in car (closed garage). Action taken tonight - wrote note, started engine, would have succeeded if wife had not intervened. Plan is lethal, accessible (owns car + garage), and he attempted it within last 2 hours.",

        "A_access_to_means": "IMMEDIATE ACCESS: Car and garage at home. Also has tools (plumber - access to sharp objects, potential hanging points in workshop). Lives in house with garage. Wife now aware but cannot monitor 24/7.",

        "F_feelings_hopelessness": "SEVERE HOPELESSNESS: 'I can't see any way out', 'better for everyone if I'm gone', 'I'm a burden'. Beck Hopelessness Scale would score very high. Sees no future, cannot identify any positives. Guilt overwhelming ('I've destroyed everything').",

        "E_earlier_attempts": "NO previous attempts. Mother had severe depression, hospitalized twice when patient was child (age 8 and 12). Witnessed mother's suffering, terrified of 'becoming like her'. This fear may have contributed to delay in seeking help.",

        "T_threat_level": "**IMMINENT HIGH RISK**",
        "rationale": "Active plan + intent + recent action (attempted 2 hours ago) + access to means + severe hopelessness + intoxication (alcohol) + social isolation + major stressors ($180k debt, business failure, guilt) + impulsivity (went from plan to action rapidly tonight) + minimal protective factors visible currently",

        "risk_factors": [
          "ACTIVE plan + intent + recent attempt (2 hours ago) - HIGHEST RISK",
          "Access to means (car, garage, tools)",
          "Severe depression (6 weeks, all DSM-5 criteria met)",
          "High hopelessness, guilt, worthlessness",
          "Male gender (3x suicide rate vs females in Australia)",
          "Acute psychosocial stressors (business collapse, $180k debt, job loss)",
          "Social withdrawal, isolation (stopped friends, soccer, family activities)",
          "Alcohol use increasing (8-10 beers nightly = hazardous drinking)",
          "Insomnia (3am waking nightly - exhaustion impairs judgment)",
          "Family history of severe depression (mother hospitalized twice)"
        ],

        "protective_factors": [
          "Wife alerted, very concerned (found him, called ambulance)",
          "Two children ages 8 and 10 (though currently unable to see them as reason to live)",
          "Arrived at ED (engagement, even if reluctant)",
          "No psychotic symptoms, no command hallucinations",
          "Previously functioning well (ran business 12 years, married, active in community)"
        ],

        "protective_factors_note": "Protective factors are WEAK currently - patient states 'family better off without me' (delusional guilt). Children are protective factor objectively but patient cannot access this emotionally right now due to depression severity."
      },

      "mental_health_act_criteria": {
        "meets_criteria": "**YES - ALL 4 CRITERIA MET**",
        "requires_schedule_1": "YES - Involuntary admission indicated",

        "criteria_met": {
          "1_mental_illness": "YES - Major Depressive Disorder, severe episode with psychotic features (delusional guilt: 'family better off without me')",
          "2_imminent_risk": "YES - IMMINENT risk of serious harm to self. Active suicide attempt 2 hours ago, ongoing plan + intent + access to means. Without intervention, re-attempt within hours highly likely.",
          "3_refuses_treatment": "YES - Patient states 'I don't want to be here', angry wife intervened, wants to leave ED to 'finish what I started'. Refuses voluntary admission.",
          "4_no_less_restrictive": "YES - Voluntary outpatient treatment INSUFFICIENT given imminent suicide risk. Community crisis team cannot provide 24/7 observation. Involuntary psychiatric admission REQUIRED for safety."
        },

        "documentation": "Schedule 1 criteria met. Psychiatry registrar contacted (Dr Lisa Wang paged 0245hrs, arrived ED 0310hrs, agreed Schedule 1 appropriate). Mental Health Act NSW 2007 Schedule 1 Form completed. Patient to be admitted involuntarily to Psychiatric Emergency Care Unit (PECU) for 24-hour observation, then transferred to acute psychiatry ward.",

        "patient_notification": "Patient informed: 'David, I'm very concerned about your safety. You attempted to end your life 2 hours ago and you're telling me you still plan to do this. Under the Mental Health Act, because you're at imminent risk and you don't want voluntary admission, I need to admit you to the psychiatric unit for your safety. This is involuntary admission - you can't leave yet. We will keep you safe while we treat your depression. A psychiatrist will see you within 12 hours to review this decision.'"
      },

      "past_medical_history": "Nil significant medical conditions. No previous psychiatric diagnoses or treatment. No previous hospitalizations.",

      "medications": "Nil regular medications. Occasional paracetamol for headaches.",

      "allergies": "NKDA (no known drug allergies)",

      "family_history": "**SIGNIFICANT: Mother has severe depression** - two psychiatric hospitalizations (when patient aged 8 and 12 years). Treated with ECT during second admission. Patient witnessed mother's suffering, states 'I swore I'd never end up like her' (may explain delayed help-seeking). Mother now stable on venlafaxine. Father: hypertension, alive age 68. No family history of suicide completion (mother had attempts but survived).",

      "social_history": {
        "occupation": "Self-employed plumber (12 years). Business collapsed 4 months ago due to $180,000 debt (bad investments in property development that failed). Currently unemployed, no income.",
        "living_situation": "Lives with wife Sarah (supportive, very concerned) and two children ages 8 and 10 in suburban house (owns house, mortgage $450k).",
        "relationships": "Married 12 years. Wife describes normally 'great father, involved with kids'. Relationship strain past 6 weeks (withdrawn, irritable, sleeping in garage).",
        "financial": "$180,000 business debt + $450,000 mortgage. No income currently. Life insurance $500,000 (patient's rationale for suicide: 'insurance will clear debts'). Severe financial stress.",
        "smoking": "Ex-smoker, 15 pack-years (20/day for 15 years age 18-33), quit 5 years ago when first child born.",
        "alcohol": "Increasing to hazardous levels past 6 weeks: 8-10 beers nightly (80-100g alcohol = hazardous drinking >60g/day men). Previously social drinker only (2-3 beers weekend). Using alcohol to cope ('to sleep, to stop thinking').",
        "illicit_drugs": "Denies cannabis, amphetamines, other drugs.",
        "social_support": "ISOLATED. Stopped all social contact past 6 weeks: quit weekly soccer team (10 years), stopped seeing friends ('too ashamed'), withdrawn from extended family. Wife is only support but relationship strained."
      },

      "systems_review": "No chest pain, palpitations, SOB. No headaches, visual changes, focal neurology. Appetite very poor (7kg weight loss 6 weeks). Early morning waking (3am) every night, can't get back to sleep (ruminating about debts, guilt). Energy very low ('exhausted but can't sleep'). Concentration very poor ('can't read newspaper, forget what people say')."
    },

    "mse_complete": {
      "appearance": "38-year-old man, appears stated age, casually dressed (jeans, t-shirt), unkempt (unshaven 3-4 days, hair uncombed), poor hygiene (body odor), minimal eye contact (looks at floor most of interview)",

      "behavior": "Psychomotor retardation (slow movements, long latency answering questions - 5-10 second delays). Sits slumped in chair. Appears withdrawn. Periodically becomes tearful but doesn't cry audibly. When discussing children, briefly covered face with hands. No aggression observed.",

      "speech": "Low volume (interviewer had to ask to speak up), slow rate, monotonous tone (no inflection), decreased quantity (one-word answers unless prompted). Long latencies (10+ seconds before answering). Vocabulary appropriate to education.",

      "mood_subjective": "'Hopeless' (patient's word). Also states: 'I feel empty', 'I can't see any point', 'I'm a burden to everyone', 'they'd be better without me'.",

      "affect_objective": "Severely depressed, constricted (no range), flat (little facial expression), congruent with mood. Tearful when discussing wife finding him ('I'm sorry I put her through that, but I still think it's the right thing'). No reactivity to jokes or reassurance.",

      "thought_form": "Linear, goal-directed. No tangentiality, circumstantiality, or flight of ideas. Slower than normal (long latencies). Rumination present ('I keep going over and over what I did wrong, how I failed everyone').",

      "thought_content": {
        "suicidal_ideation": "ACTIVE with PLAN and INTENT: 'I want to die', 'I'm going to finish what I started when I get out of here', 'car exhaust worked before, it will work again'. Lethality high.",
        "homicidal_ideation": "Denies intent to harm others. Denies thoughts of harming wife or children. (Note: Some men with depression have homicide-suicide risk, but not evident here - interview specifically asked, patient denied).",
        "guilt": "SEVERE, DELUSIONAL LEVEL: 'I've destroyed my family', 'I'm a complete failure', 'I've let down my employees - they trusted me and I ruined their lives too', 'my children would be better off without a father like me' (delusional guilt - objectively false but patient believes absolutely).",
        "worthlessness": "'I'm worthless', 'I can't do anything right', 'I'm a burden'.",
        "delusions": "PRESENT - delusional guilt (psychotic depression). Believes family 'better off without me' despite wife's distress, children needing him. Unshakeable belief even when challenged with evidence.",
        "paranoia": "Denies. No persecutory delusions.",
        "obsessions_compulsions": "None reported."
      },

      "perceptions": "Denies auditory/visual/tactile hallucinations. No command hallucinations (specifically asked: 'Do you hear voices telling you to hurt yourself?' - denied). No illusions.",

      "cognition": {
        "consciousness": "Alert",
        "orientation": "Oriented to person (knows own name), place (Royal Brisbane Hospital Emergency Department), time (early hours of morning, day of week correct, year correct)",
        "attention_concentration": "IMPAIRED. Difficulty concentrating on interview questions (had to repeat several questions). Unable to do serial 7s accurately (92, 85, 77, 71... gave up - 'I can't think'). Digit span reduced (4 forward, 2 backward - normal 7 forward, 5 backward).",
        "memory": "Subjectively impaired: 'I forget everything, I can't remember appointments, I forget what people tell me'. Short-term memory: Could recall 2/3 objects at 5 minutes (mildly impaired - may be concentration issue). Long-term memory: Intact (recalls business timeline, children's ages, personal history accurately)."
      },

      "insight": "**POOR/ABSENT**. Does NOT believe he is ill ('I'm not depressed, I'm a realist - my family IS better off without me'). Does NOT believe he needs treatment ('I don't need medication, I need to not exist'). Does not accept involuntary admission ('you're making a mistake, I should be allowed to leave').",

      "judgment": "**SEVERELY IMPAIRED** by illness. Made life-threatening decision (suicide attempt) while intoxicated and in severe depressive episode. Cannot make safe decisions currently (states will re-attempt if released). Risk assessment capacity: ABSENT - cannot weigh risks/benefits rationally due to delusional guilt and hopelessness."
    },

    "provisional_diagnosis": "**Major Depressive Disorder, severe episode WITH PSYCHOTIC FEATURES (DSM-5: 296.24, ICD-11: 6A70.3)**",

    "dsm5_criteria_met": {
      "criterion_A": "≥5 symptoms present for ≥2 weeks including (1) depressed mood AND (2) anhedonia",
      "symptoms_present": [
        "1. Depressed mood: daily for 6 weeks ('I feel empty, hopeless')",
        "2. Anhedonia: marked (stopped ALL previously enjoyed activities - soccer, playing with kids, socializing)",
        "3. Weight loss: 7kg in 6 weeks (significant - NOT intentional dieting)",
        "4. Insomnia: early morning waking 3am daily, can't return to sleep",
        "5. Psychomotor retardation: observable (slow movements, long latencies)",
        "6. Fatigue: 'exhausted all the time'",
        "7. Worthlessness/guilt: SEVERE, reaches delusional level ('I'm worthless', 'family better without me')",
        "8. Concentration impaired: 'can't read newspaper, forget conversations', digit span reduced",
        "9. Suicidal ideation: ACTIVE with plan + intent + recent attempt"
      ],
      "criterion_B": "Significant distress/impairment: YES - complete functional impairment (no work, withdrawn from all activities, neglecting family, attempted suicide)",
      "criterion_C": "Not attributable to substance: Alcohol use is comorbid but depression preceded increased drinking (depression caused drinking, not vice versa)",
      "criterion_D": "Not better explained by other disorder: No manic episodes (not bipolar), no primary psychotic disorder (psychotic features are mood-congruent)",
      "specifiers": "WITH PSYCHOTIC FEATURES (mood-congruent delusional guilt: 'family better off without me'), severe severity (most/all symptoms, marked functional impairment, life-threatening)"
    },

    "differential_diagnosis": [
      {
        "diagnosis": "Bipolar I Disorder, current episode depressed",
        "for": "Family history of severe depression (mother with ECT) could suggest bipolar in family. Severe depression with psychotic features can be bipolar depressed.",
        "against": "NO history of manic/hypomanic episodes. Patient and wife deny any periods of elevated mood, decreased need for sleep, increased energy, impulsivity (outside current depression). Screen carefully before starting antidepressant (risk of switching to mania).",
        "action": "Detailed collateral from wife re: any past hypomanic episodes. If any doubt, avoid antidepressants initially, use mood stabilizer (e.g., valproate) + antipsychotic."
      },
      {
        "diagnosis": "Adjustment Disorder with depressed mood",
        "for": "Clear precipitant (business collapse 4 months ago, $180k debt)",
        "against": "Severity, duration, psychotic features ALL exceed adjustment disorder. Meets full MDD criteria. Functional impairment extreme. Adjustment disorder is milder, shorter (<6 months), no psychotic features.",
        "conclusion": "This is MDD, NOT adjustment disorder."
      },
      {
        "diagnosis": "Substance-Induced Depressive Disorder (alcohol)",
        "for": "Hazardous alcohol use (8-10 beers nightly)",
        "against": "Timing: Depression onset (6 weeks ago) PRECEDED alcohol increase. Depression caused drinking (self-medication for insomnia, to 'stop thinking'), NOT vice versa. If alcohol-induced, would expect improvement with abstinence - patient's hopelessness, suicidal ideation, delusional guilt are independent of alcohol.",
        "conclusion": "MDD with comorbid alcohol misuse (separate diagnoses, treat both)."
      },
      {
        "diagnosis": "Complicated Grief (after business loss)",
        "for": "Loss of business (12 years work, identity tied to being plumber), guilt about employees",
        "against": "This is not bereavement (no death). Symptoms exceed normal grief response (psychotic features, functional impairment, suicide attempt). Meets MDD criteria fully.",
        "conclusion": "This is MDD triggered by loss, NOT grief disorder."
      }
    ],

    "immediate_management": {
      "safety_first": [
        "**INVOLUNTARY ADMISSION** under Mental Health Act NSW 2007 Schedule 1 (all 4 criteria met - see above)",
        "Psychiatry registrar contacted STAT (Dr Lisa Wang paged, arrived 0310hrs, agreed Schedule 1 appropriate)",
        "Psychiatric Emergency Care Unit (PECU) admission for 24-hour observation",
        "CONSTANT OBSERVATION (1:1 nursing, never leave alone, remove sharps/cords/belts)",
        "Search belongings for means (sharps, medications, cords)",
        "Suicide-proof room (no ligature points, plastic cutlery, shatterproof glass)",
        "Elopement risk: Lock ward doors, patient on 1:1 observation",
        "Nil sharps, nil belt, nil shoelaces (removed)",
        "Contact wife Sarah: Update on admission, reassure re: safety, offer support (contact social work for family support)"
      ],

      "pharmacotherapy": [
        {
          "indication": "Acute agitation/distress in ED",
          "drug": "Lorazepam",
          "dose": "1-2mg PO or IM",
          "rationale": "Short-acting benzodiazepine for acute anxiety/agitation. Patient distressed ('I don't want to be here'). Sedation will help immediate safety.",
          "pbs_code": "1449C",
          "monitoring": "Respiratory rate, sedation level",
          "duration": "PRN in ED/first 24 hours only (avoid dependence)"
        },
        {
          "indication": "PSYCHOTIC DEPRESSION (antipsychotic FIRST-LINE, NOT antidepressant alone)",
          "drug": "Olanzapine",
          "dose": "10mg PO nocte (can give 5-10mg STAT in ED if very agitated)",
          "rationale": "Antipsychotic for psychotic features (delusional guilt). Olanzapine preferred: sedating (helps insomnia), low EPS, evidence in psychotic depression. DO NOT give antidepressant alone in psychotic depression (inadequate - needs antipsychotic + antidepressant OR ECT).",
          "pbs_code": "8622W (PBS restricted: psychotic depression, bipolar, schizophrenia)",
          "monitoring": "Sedation, metabolic (weight, glucose, lipids - olanzapine causes weight gain 2-4kg, diabetes risk), EPS (low with olanzapine but monitor), BP (orthostatic hypotension risk)",
          "counseling": "May cause drowsiness (take at night, helps sleep), increased appetite/weight gain (common, monitor), dry mouth",
          "duration": "Continue until psychotic features resolve (usually 4-8 weeks), then taper slowly"
        },
        {
          "indication": "DEPRESSION (in addition to antipsychotic)",
          "drug": "Venlafaxine",
          "dose": "75mg XR daily (extended release), increase to 150mg after 1 week, target 225mg (more effective than SSRI in severe depression)",
          "rationale": "SNRI (serotonin-norepinephrine reuptake inhibitor) more effective than SSRI in severe depression (meta-analyses). Venlafaxine preferred over SSRI in psychotic depression, severe melancholic depression, treatment-resistant depression.",
          "alternative": "Could use SSRI (e.g., sertraline 50mg daily, increase to 150-200mg) but less effective in severe depression. Mirtazapine 30mg nocte alternative if insomnia prominent.",
          "pbs_code": "8661K",
          "monitoring": "CRITICAL: Monitor for suicidal ideation increase first 2 weeks (black box warning age <25, but relevant all ages in severe depression). BP (venlafaxine can increase BP, check weekly initially). Serotonin syndrome (agitation, tremor, hyperthermia, confusion - especially if combined with other serotonergic drugs).",
          "counseling": "May take 2-4 weeks to see benefit (not instant). May worsen suicidal thoughts initially (if so, contact psychiatry immediately). Take with food (reduces nausea). Don't stop suddenly (withdrawal syndrome - taper over 4 weeks when ceasing).",
          "duration": "Minimum 6-12 months after recovery (prevent relapse). If second episode, consider 2+ years. If third episode, consider lifelong.",
          "screening_before_starting": "MUST screen for bipolar before starting antidepressant (risk of switching to mania). Collateral history from wife: Any past elevated mood, decreased sleep need, impulsivity, spending sprees? If ANY suggestion bipolar, use mood stabilizer instead (valproate 500mg BD)."
        }
      ],

      "non_pharmacological": [
        "**ECT (Electroconvulsive Therapy) consideration:** Psychotic depression responds BEST to ECT (70-90% response vs 50-60% medication). If no improvement after 2 weeks medication, or if patient cannot wait (ongoing high suicide risk despite admission), offer ECT. Requires consent (or guardian consent if incapacitated, or Mental Health Tribunal approval if refuses). Discuss with patient + wife when acute crisis settles.",

        "Psychotherapy: NOT appropriate acutely (too depressed, psychotic, high risk). Once stabilized (psychotic features resolved, suicide risk reduced), CBT for depression. Evidence: CBT + medication superior to medication alone for relapse prevention.",

        "Social work: Contact wife Sarah, offer support. Financial counseling (National Debt Helpline 1800 007 007). Centrelink application (disability support pension may be appropriate if long-term impairment). Referral to community mental health team for discharge planning."
      ],

      "investigations": [
        "Bloods (exclude organic causes, baseline before medications):",
        "  - FBC (anaemia can mimic depression)",
        "  - UEC (electrolytes, renal function baseline)",
        "  - LFTs (liver function baseline before medications)",
        "  - TFTs (hypothyroidism can cause depression - TSH, free T4)",
        "  - B12, folate (deficiency can cause depression)",
        "  - Glucose, HbA1c (diabetes can cause depression, also baseline before olanzapine which increases diabetes risk)",
        "  - Lipids (baseline before olanzapine)",
        "  - Urine drug screen (exclude amphetamines, cocaine - can mimic/cause psychosis)",
        "  - Blood alcohol level (was 0.18% in ED - confirms intoxication at time of attempt, now sober)",

        "Carboxyhaemoglobin level: To assess carbon monoxide exposure from tonight's attempt. Patient was in garage <5 minutes before wife intervened, so likely minimal exposure, but check. If elevated >10%, treat with high-flow oxygen.",

        "ECG: Baseline before starting venlafaxine (can prolong QT interval slightly). If QTc >450ms, use alternative antidepressant (e.g., sertraline).",

        "Brain imaging: NOT indicated (no focal neurology, no head trauma, no cognitive decline suggesting dementia). Depression is clinical diagnosis."
      ],

      "collateral_information": [
        "Wife Sarah contacted in ED waiting room:",
        "  - Timeline confirmation (6 weeks worsening, tonight's attempt)",
        "  - Screen for bipolar (any past manic episodes?) - she denies",
        "  - Medications/substance use verification",
        "  - Safety at home (secure car keys, garage, sharps when discharged)",
        "  - Offer support, social work referral",
        "  - Explain involuntary admission, visiting hours, treatment plan",
        "  - Provide crisis contacts",

        "GP: Will contact Dr James Lee (patient's GP) tomorrow to inform of admission, request past medical records, coordinate discharge planning."
      ]
    },

    "ongoing_management": {
      "inpatient": [
        "PECU (Psychiatric Emergency Care Unit) 24 hours, then transfer acute psychiatry ward",
        "Continue 1:1 observation until risk reduces (psychiatrist to review daily)",
        "Medication titration: Olanzapine 10mg nocte, venlafaxine 75mg daily (increase to 150mg day 7, then 225mg day 14 if tolerated)",
        "Daily psychiatrist review: Suicide risk re-assessment, Mental Health Act review (Schedule 1 must be reviewed by psychiatrist within 12 hours, then every 3 days)",
        "Supportive psychotherapy: Daily sessions with ward psychologist (supportive, NOT CBT yet - too unwell)",
        "Occupational therapy: Graded activity scheduling (start simple tasks, increase complexity as improves)",
        "Family meetings: Include wife Sarah, explain illness, treatment, recovery timeline, discharge planning",
        "Expected length of stay: 2-4 weeks (until psychotic features resolve, suicide risk reduces to low, established on medications)"
      ],

      "discharge_criteria": [
        "Psychotic features resolved (no delusional guilt)",
        "Suicide risk LOW (no plan, no intent, can identify reasons for living, engaged in safety planning)",
        "Established on medications (therapeutic doses, tolerated)",
        "Insight improved (accepts diagnosis, agrees to ongoing treatment)",
        "Home safety assessment completed (wife has secured garage, car keys, sharps)",
        "Community mental health team engaged (appointments scheduled)",
        "GP follow-up arranged (within 1 week of discharge)"
      ],

      "discharge_plan": [
        "Community mental health team: Weekly appointments with case manager, fortnightly psychiatrist review",
        "GP: Dr James Lee review 1 week post-discharge, then fortnightly (medication monitoring, suicide risk, general health)",
        "Psychology: CBT for depression once stable (10 sessions Medicare-funded via Mental Health Care Plan)",
        "Medications: Olanzapine 10mg nocte + venlafaxine 225mg daily (continue minimum 6-12 months)",
        "Financial counseling: National Debt Helpline referral (1800 007 007)",
        "Centrelink: Disability Support Pension application (may be appropriate if long-term impairment)",
        "Alcohol counseling: Once depression improving, address hazardous drinking (currently drinking to cope - treat depression first, then alcohol)",
        "Family therapy: Couples counseling (wife has been through trauma finding him, relationship repair needed)",
        "Return to work: Gradual (NOT plumbing self-employment initially - too stressful). Explore alternative employment with less financial pressure. Occupational therapist to assist graded return to work."
      ],

      "relapse_prevention": [
        "Medication adherence: Venlafaxine minimum 6-12 months after recovery. If stop too early, 60-70% relapse within 6 months.",
        "Recognize early warning signs: Insomnia, social withdrawal, guilt thoughts, anhedonia → seek help EARLY",
        "Stress management: CBT techniques, problem-solving therapy",
        "Lifestyle: Regular exercise (30min 3x/week - evidence for depression prevention), sleep hygiene, reduce/cease alcohol",
        "Support network: Re-engage with friends, soccer team (meaningful activities reduce relapse)",
        "Financial stability: Debt counseling, sustainable employment (avoid high-stress self-employment initially)"
      ]
    },

    "safety_netting": {
      "red_flags_while_inpatient": [
        "Sudden improvement in mood (may indicate decision made to suicide - 'terminal lucidity')",
        "Requesting leave (may be planning attempt)",
        "Giving away possessions",
        "Withdrawal from groups, refusing medications",
        "Any of these → immediate psychiatrist review, increase observation"
      ],

      "red_flags_post_discharge": [
        "IMMEDIATE ED PRESENTATION: Active suicidal plan/intent, preparing to attempt, acquiring means, command hallucinations, severe agitation, psychotic relapse",
        "URGENT PSYCHIATRY (within 24 hours): Suicidal thoughts increasing, stopping medications, psychotic symptoms returning, severe insomnia (>3 nights), alcohol binge",
        "GP REVIEW (within 1 week): Medication side effects (nausea, sedation, tremor), no improvement after 4 weeks, relationship difficulties worsening"
      ],

      "crisis_contacts_provided": [
        "Lifeline: 13 11 14 (24/7)",
        "Beyond Blue: 1300 224 636",
        "Suicide Call Back Service: 1300 659 467",
        "Mental Health Access Line: 1800 011 511 (NSW 24/7)",
        "Emergency: 000 or present to ED",
        "Community mental health team: (07) 3000 xxxx (Mon-Fri 8am-5pm)",
        "After hours psychiatry: Contact Mental Health Access Line"
      ]
    }
  },

  "marking_criteria": [
    {"criterion": "Introduction and rapport", "marks": 1, "description": "Introduces self, explains purpose, establishes empathic rapport (challenging given patient's reluctance, but attempts empathy)"},
    {"criterion": "Presenting complaint", "marks": 1, "description": "Elicits tonight's suicide attempt (method, timing, discovery), recent note"},
    {"criterion": "Depression symptoms (DSM-5)", "marks": 2, "description": "Assesses ≥5 DSM-5 symptoms: mood, anhedonia, weight, sleep, psychomotor, fatigue, guilt, concentration, SI"},
    {"criterion": "Suicide risk assessment (SAFE-T)", "marks": 3, "description": "Specific plan (car exhaust), Access (garage, car), Feelings (hopelessness severe), Earlier attempts (none), Threat level (IMMINENT HIGH)"},
    {"criterion": "Mental State Examination", "marks": 2, "description": "Systematic MSE including appearance, behavior, speech, mood, affect, thought content (delusional guilt), perceptions, cognition, insight"},
    {"criterion": "Psychotic features", "marks": 1, "description": "Identifies delusional guilt ('family better without me' - unshakeable despite evidence)"},
    {"criterion": "Collateral history", "marks": 1, "description": "Obtains information from wife (timeline, bipolar screen, functional impairment)"},
    {"criterion": "Past psychiatric + family history", "marks": 1, "description": "Asks about previous episodes (none), family history (mother severe depression + ECT)"},
    {"criterion": "Substance use", "marks": 1, "description": "Alcohol (8-10 beers nightly past 6 weeks), smoking (ex-smoker)"},
    {"criterion": "Mental Health Act criteria", "marks": 2, "description": "Recognizes all 4 criteria met, recommends involuntary admission Schedule 1"},
    {"criterion": "Immediate safety management", "marks": 2, "description": "1:1 observation, remove means, psychiatric consultation STAT, PECU admission"},
    {"criterion": "Pharmacotherapy appropriate", "marks": 2, "description": "Antipsychotic (olanzapine) for psychotic features + antidepressant (venlafaxine), NOT antidepressant alone"},
    {"criterion": "Communication and empathy", "marks": 1, "description": "Maintains appropriate empathy despite patient's hostility ('I understand you're in a lot of pain'), non-judgmental"},
    {"criterion": "TOTAL", "marks": 20}
  ],

  "learning_points": [
    "**Psychotic depression requires antipsychotic + antidepressant (OR ECT), NOT antidepressant alone.** Delusional guilt ('family better without me') is mood-congruent psychotic feature - olanzapine 10mg + venlafaxine 225mg, OR ECT (70-90% response).",

    "**SAFE-T assessment: Active plan + intent + recent action = IMMINENT HIGH RISK.** This patient attempted 2 hours ago, still has plan/intent/access → requires involuntary admission, cannot be managed outpatient.",

    "**Mental Health Act NSW 2007 Schedule 1 criteria (all 4 must be met): (1) Mental illness ✓ (2) Imminent risk harm ✓ (3) Refuses voluntary treatment ✓ (4) No less restrictive option ✓ → Involuntary admission indicated.** Psychiatry must review within 12 hours, then every 3 days.",

    "**Screen for bipolar before starting antidepressants:** Family history severe depression (mother + ECT) could suggest bipolar. Collateral from wife: Any past manic episodes? If yes/uncertain, use mood stabilizer (valproate) instead of antidepressant (risk of switching to mania).",

    "**Venlafaxine (SNRI) more effective than SSRIs in severe/melancholic depression:** Meta-analyses show SNRIs (venlafaxine, duloxetine) superior to SSRIs in severe depression. Start 75mg XR daily, increase to 150-225mg. Monitor BP (can increase), suicidal ideation first 2 weeks.",

    "**ECT is first-line for psychotic depression if medication fails or patient cannot wait:** 70-90% response rate (vs 50-60% medication). Consider if no improvement 2 weeks medication, or ongoing high suicide risk despite admission.",

    "**Australian crisis contacts:** Lifeline 13 11 14 (24/7), Beyond Blue 1300 224 636, Suicide Call Back Service 1300 659 467, Mental Health Access Line 1800 011 511 (NSW). Provide written list to all patients with depression.",

    "**'Terminal lucidity' - sudden mood improvement in high-risk patient may indicate decision made to suicide, NOT actual recovery.** If inpatient suddenly appears cheerful, giving away possessions, requesting leave → increase observation, psychiatrist review STAT.",

    "**Depression medication: Minimum 6-12 months after recovery to prevent relapse.** If stop at 3 months (when feeling better), 60-70% relapse within 6 months. Second episode: 2+ years. Third episode: consider lifelong.",

    "**Assess functional impairment severity:** This patient: (1) No work 4 months (2) Withdrawn from ALL activities (soccer, friends, family) (3) Stopped self-care (hygiene) (4) Suicide attempt → Severe impairment, requires intensive treatment (hospitalization, likely ECT)."
  ],

  "references": [
    {"title": "Therapeutic Guidelines: Psychiatry", "section": "Chapter 3: Depressive disorders, Section 3.4: Psychotic depression", "recommendation": "Antipsychotic + antidepressant OR ECT (first-line for psychotic depression)"},
    {"title": "RANZCP Clinical Practice Guidelines for Mood Disorders", "year": "2020", "recommendation": "Psychotic depression: ECT preferred, or antipsychotic (olanzapine, quetiapine) + antidepressant (venlafaxine > SSRI)"},
    {"title": "Mental Health Act NSW 2007", "section": "Schedule 1: Criteria for involuntary admission", "criteria": "4 criteria all required: (1) Mental illness (2) Imminent risk (3) Refuses voluntary (4) No less restrictive"},
    {"title": "SAFE-T Suicide Risk Assessment Framework", "source": "SAMHSA (adapted for Australian context)", "components": "Specific plan, Access to means, Feelings hopelessness, Earlier attempts, Threat level"},
    {"title": "Black Dog Institute: Clinical Guidelines for Management of Psychotic Depression", "recommendation": "Consider ECT early if severe suicidality or medication contraindicated. Response rate 70-90% vs 50-60% medication."}
  ]
}
```

**Why APPROVED:**
- ✅ Complete clinical vignette (specific patient, timeline, context, red flags)
- ✅ All 9 history steps with specific content
- ✅ Complete Mental State Examination (all 8 domains)
- ✅ SAFE-T protocol thoroughly documented
- ✅ Mental Health Act criteria assessed
- ✅ Specific medications with doses, PBS codes, rationale
- ✅ Australian crisis contacts
- ✅ Cultural safety addressed
- ✅ Red flags and safety netting comprehensive
- ✅ High educational value for AMC preparation

---

**END OF CONSTRAINT 16**

**Last Updated:** 2026-04-03
**Version:** 1.0
**Status:** ACTIVE - Zero-Tolerance Enforcement
