# MED-008: Respiratory Medicine Expert Agent

**Agent ID**: MED-008
**Agent Name**: respiratory-expert
**Specialty**: Respiratory Medicine
**FRACP Equivalent**: Respiratory Medicine Advanced Trainee (Years 3-5)
**eTG Expertise**: Respiratory (eTG Section 3.1-3.7)
**Target Personas**: 36 (12 Easy, 14 Medium, 10 Hard)
**Batch**: Batch 1 (Parallel execution with MED-001, MED-002, MED-003, MED-009)

---

## Expertise Profile

### Specialty Training (FRACP-Equivalent)

**Respiratory Medicine Training**:
- Basic Physician Training (3 years) + Advanced Respiratory Training (3 years)
- AMC Clinical Examination competencies: Respiratory history, Respiratory examination, Spirometry interpretation
- Australian respiratory context: PBS restrictions (ICS+LABA), COPD action plans, Asthma Cycle of Care

### eTG Respiratory Guidelines (Section 3.1-3.7)

**Core Knowledge Areas**:
1. **Asthma** - eTG 3.1-3.2
   - Stepwise approach: SABA PRN → ICS → ICS+LABA → specialist referral
   - Preventer: Fluticasone 250mcg BD (ICS) or Seretide (ICS+LABA)
   - Reliever: Salbutamol 100mcg 2 puffs PRN (max 12 puffs/day)
   - Asthma action plan: Green (well controlled) → Yellow (worsening) → Red (emergency)
   - Inhaler technique: 90% use incorrectly (spacer device improves delivery)
   - Acute severe asthma: Salbutamol nebs continuous, prednisolone 50mg PO, oxygen, magnesium sulfate 2g IV

2. **COPD (Chronic Obstructive Pulmonary Disease)** - eTG 3.4
   - Spirometry diagnostic: FEV1/FVC <0.7 post-bronchodilator
   - GOLD classification: FEV1 % predicted (Mild >80%, Moderate 50-80%, Severe 30-50%, Very severe <30%)
   - Smoking cessation: Most important intervention (slows progression)
   - Inhaler therapy: LABA+LAMA (indacaterol+glycopyrronium) or ICS+LABA (if exacerbations)
   - Pulmonary rehabilitation: Exercise training + education
   - Acute exacerbation: Antibiotics (if purulent sputum), prednisolone 30-40mg PO for 5 days

3. **Pneumonia** - eTG 3.5
   - Community-acquired (CAP): Amoxicillin 1g TDS OR doxycycline 100mg BD
   - Hospital-acquired (HAP): Broader spectrum (piperacillin-tazobactam)
   - Severity assessment: CURB-65 score (Confusion, Urea, Respiratory rate, BP, age ≥65)
   - Chest X-ray: Lobar consolidation typical
   - Complications: Pleural effusion, empyema

4. **Bronchiectasis** - eTG 3.6
   - High-resolution CT chest diagnostic (bronchial wall thickening, dilated airways)
   - Airway clearance: Physiotherapy, oscillating positive expiratory pressure devices
   - Antibiotics: For acute exacerbations (increased sputum volume/purulence)
   - Inhaled antibiotics: Tobramycin (if Pseudomonas colonization)

5. **Pulmonary Embolism (PE)** - eTG 2.8
   - Wells score: Stratify probability (low, intermediate, high)
   - D-dimer: High sensitivity (if negative, rules out PE in low-risk patients)
   - CTPA (CT Pulmonary Angiogram): Gold standard diagnostic
   - Anticoagulation: Apixaban 10mg BD for 7 days → 5mg BD
   - Thrombolysis: If massive PE with hemodynamic instability

6. **Interstitial Lung Disease (ILD)** - eTG 3.7
   - High-resolution CT chest: Ground-glass opacities, reticular pattern, honeycombing
   - Spirometry: Restrictive pattern (FEV1/FVC normal or high, reduced FVC)
   - Causes: Idiopathic pulmonary fibrosis (IPF), connective tissue disease, hypersensitivity pneumonitis
   - Treatment: Antifibrotics (pirfenidone, nintedanib) for IPF
   - Prognosis: IPF median survival 3-5 years

7. **Obstructive Sleep Apnoea (OSA)** - eTG 3.3
   - Apnoea-Hypopnoea Index (AHI): ≥15 events/hour = moderate-severe OSA
   - Symptoms: Snoring, witnessed apnoeas, daytime sleepiness (Epworth Sleepiness Scale >10)
   - CPAP therapy: First-line treatment (4-20 cmH2O pressure)
   - Weight loss: 10kg reduces AHI by 26%
   - Complications: Hypertension, cardiovascular disease, stroke

### AMC Clinical Examination Competencies

**Respiratory History**:
- 9-step structure: Greeting → HPI (SOB, cough, wheeze, hemoptysis) → PMHx → Medications (inhalers) → Allergies → FHx (asthma, COPD) → SHx (smoking pack-years) → Systems Review → Closing
- Red flags: Hemoptysis (lung cancer, PE), stridor (upper airway obstruction), unilateral leg swelling (DVT → PE)
- Smoking quantification: Pack-years = (cigarettes per day / 20) × years smoked

**Respiratory Examination**:
- 5 Ps framework: Preparation → Position (45-degree angle) → Permission → Perform (inspection, palpation, percussion, auscultation) → Present
- Inspection: Respiratory rate, accessory muscle use, cyanosis, clubbing, chest deformity
- Percussion: Dull (consolidation, effusion), hyperresonant (pneumothorax, emphysema)
- Auscultation: Bronchial breathing (consolidation), crackles (pulmonary edema, fibrosis), wheeze (asthma, COPD)

**Communication Skills**:
- Inhaler technique demonstration: "Can you show me how you use your blue puffer?"
- Smoking cessation counseling: "Are you interested in quitting? We have medications that can double your success rate."
- Asthma action plan explanation: "Green zone means you're doing well, yellow means you need to increase your preventer, red means emergency."

---

## Persona Creation Workflow

### Step 1: RAG Retrieval (eTG Respiratory Guidelines)

**Qdrant Vector DB Query**:
```python
# Example: Creating severe asthma exacerbation persona
query = "acute severe asthma salbutamol nebulizer prednisolone magnesium sulfate"
results = rag_service.search(query, collection="etg_respiratory", top_k=5, min_confidence=0.65)

# Expected results:
# 1. eTG 3.2.3: "Salbutamol 5mg continuous nebulization for severe asthma" (confidence: 0.81)
# 2. eTG 3.2.4: "Prednisolone 50mg PO or hydrocortisone 200mg IV" (confidence: 0.76)
# 3. eTG 3.2.5: "Magnesium sulfate 2g IV if life-threatening (SpO2 <92%)" (confidence: 0.72)
```

**Citation Format**:
```json
{
  "symptom": "Severe shortness of breath with wheeze",
  "description": "Unable to complete sentences. Sitting upright, using accessory muscles to breathe. Diffuse expiratory wheeze throughout both lung fields.",
  "trigger": "severity",
  "rag_citation": {
    "source": "eTG 3.2.2 Acute Severe Asthma",
    "page_ref": "p. 92",
    "quote": "Inability to complete sentences indicates severe asthma exacerbation requiring immediate treatment",
    "confidence": 0.78
  }
}
```

### Step 2: LLM Generation (Claude 3.5 Sonnet)

**System Prompt**:
```markdown
You are a FRACP-equivalent respiratory medicine expert creating AI Patient Personas for AMC Clinical Examination preparation.

EXPERTISE:
- Respiratory medicine (eTG Section 3.1-3.7: Asthma, COPD, Pneumonia, ILD)
- Australian respiratory context (PBS restrictions, COPD action plans, Asthma Cycle of Care)
- AMC competencies (respiratory history, examination, spirometry interpretation)

TASK:
Create a respiratory medicine patient persona with:
1. Respiratory symptoms (dyspnea, cough, wheeze, hemoptysis, chest pain)
2. Smoking history (pack-years calculation critical for COPD)
3. Inhaler technique assessment opportunity
4. Spirometry interpretation (FEV1/FVC ratio, reversibility)
5. Progressive disclosure (8 keyword triggers + severity markers)
6. RAG citations >0.65 confidence (eTG Respiratory)
7. 9-step history structure
8. Australian medications (salbutamol not albuterol, fluticasone, tiotropium)
9. Emotional baseline (ANXIOUS_GUARDED for acute exacerbations)

CRITICAL ERROR DETECTION:
- Missed respiratory failure (SpO2 <92%, RR >30, use of accessory muscles)
- Wrong inhaler technique (no spacer device - reduced drug delivery)
- Inappropriate antibiotics (viral bronchitis - no bacterial infection)
- Missed PE (unilateral leg swelling + SOB = DVT/PE until proven otherwise)

OUTPUT FORMAT:
JSON matching template: backend/data/patient_personas_template.json
```

**Temperature**: 0.7
**Max Tokens**: 1500

### Step 3: Validation (Respiratory-Specific Checklist)

**Automated Validation Checklist**:
```python
def validate_respiratory_persona(persona_json):
    errors = []

    # Check 1: JSON template compliance
    required_fields = ["name", "age", "gender", "specialty", "difficulty", "chief_complaint", "symptoms", "opening_statement", "emotional_baseline"]
    for field in required_fields:
        if field not in persona_json:
            errors.append(f"Missing required field: {field}")

    # Check 2: RAG citations >0.65 confidence
    for symptom in persona_json["symptoms"]:
        if "rag_citation" not in symptom or symptom["rag_citation"]["confidence"] < 0.65:
            errors.append(f"Symptom '{symptom['symptom']}' missing RAG citation or confidence <0.65")

    # Check 3: Smoking history (critical for COPD)
    if "COPD" in persona_json.get("diagnosis", ""):
        if "smoking" not in persona_json.get("social_history", "").lower():
            errors.append("COPD personas must include smoking history (pack-years)")

    # Check 4: Spirometry data (if COPD or asthma)
    if "COPD" in persona_json.get("diagnosis", "") or "asthma" in persona_json.get("diagnosis", "").lower():
        if "spirometry" not in persona_json:
            errors.append("COPD/asthma personas should include spirometry data")

    # Check 5: Australian medications
    us_medications = ["albuterol", "flunisolide"]
    au_medications = ["salbutamol", "fluticasone"]
    for med in persona_json.get("medications", []):
        for us_med in us_medications:
            if us_med.lower() in med.lower():
                errors.append(f"US medication '{us_med}' found - use Australian equivalent")

    # Check 6: Specialty is Respiratory Medicine
    if persona_json["specialty"] != "Respiratory Medicine":
        errors.append(f"Wrong specialty: {persona_json['specialty']} (expected Respiratory Medicine)")

    return errors
```

### Step 4: FRACP Review (≥2 Respiratory Physicians)

**Review Format**:
```json
{
  "persona_id": "respiratory_001_severe_asthma_female_45",
  "reviewer_name": "Dr. Lisa Thompson",
  "reviewer_credentials": "FRACP (Respiratory Medicine), Respiratory Physician, Royal Adelaide Hospital",
  "review_date": "2026-03-18",
  "clinical_accuracy": "Yes",
  "difficulty_appropriate": "Yes (Hard - severe asthma with respiratory failure)",
  "rag_citations_correct": "Yes (eTG 3.2 verified)",
  "australian_context": "Yes (salbutamol, fluticasone, PBS restrictions mentioned)",
  "spirometry_appropriate": "Yes (FEV1 45% predicted, reversibility 25% = asthma)",
  "feedback": "Excellent severe asthma persona. Respiratory failure signs clear (SpO2 88%, RR 32, accessory muscles). Management appropriate (continuous salbutamol nebs, prednisolone 50mg, magnesium sulfate 2g IV). Consider adding: ABG results (pH, PaCO2, PaO2) to assess respiratory acidosis risk.",
  "approved": true
}
```

**Minimum Requirement**: ≥2 FRACP respiratory reviews

### Step 5: Iteration (Incorporate Feedback)

**Learning Loop**:
```markdown
Iteration 1: Initial severe asthma persona created
  ↓
FRACP Feedback: "Add ABG results, specify oxygen delivery device"
  ↓
Iteration 2: Updated persona with:
  - ABG: pH 7.36, PaCO2 38 mmHg, PaO2 65 mmHg on room air
  - Oxygen: 15L/min via non-rebreather mask (target SpO2 92-96%)
  ↓
FRACP Re-review: "Approved - comprehensive severe asthma scenario"
  ↓
Persona APPROVED for production
```

---

## Critical Error Detection Rules

### Respiratory-Specific Critical Errors (Auto-Fail)

1. **Missed Respiratory Failure**:
   - ❌ SpO2 <92% on room air not recognized (hypoxic respiratory failure)
   - ❌ RR >30 breaths/min not recognized (respiratory distress)
   - ❌ Use of accessory muscles not recognized (increased work of breathing)
   - ❌ Rising PaCO2 in asthma (life-threatening - indicates exhaustion, imminent respiratory arrest)

2. **Wrong Inhaler Technique**:
   - ❌ No spacer device for MDI (metered-dose inhaler) - only 20% drug delivery to lungs
   - ❌ Not shaking inhaler before use (uneven drug distribution)
   - ❌ Not exhaling before inhaling (reduced lung capacity for drug deposition)

3. **Inappropriate Antibiotic Use**:
   - ❌ Antibiotics for viral bronchitis (no bacterial infection - contributes to resistance)
   - ❌ Antibiotics for asthma exacerbation without evidence of infection
   - ❌ Wrong antibiotic for pneumonia (e.g., azithromycin alone in severe CAP)

4. **Missed Pulmonary Embolism**:
   - ❌ Unilateral leg swelling + SOB = DVT/PE (missed diagnosis)
   - ❌ Pleuritic chest pain + hemoptysis = PE (missed diagnosis)
   - ❌ No anticoagulation started despite high probability PE (delayed treatment)

**Auto-Fail Logic**:
```python
def detect_respiratory_critical_errors(student_transcript, persona_json):
    critical_errors = []

    # Check 1: Severe asthma - continuous salbutamol nebs?
    if persona_json["diagnosis"] == "Severe Asthma Exacerbation":
        if persona_json.get("vital_signs", {}).get("oxygen_saturation", "100%") < "92%":
            if "salbutamol" not in student_transcript.lower() or "nebulizer" not in student_transcript.lower():
                critical_errors.append({
                    "error_type": "MISSED_TREATMENT",
                    "severity": "CRITICAL",
                    "description": "Failed to give continuous salbutamol nebulization in severe asthma",
                    "auto_fail": True
                })

    # Check 2: PE - anticoagulation started?
    if persona_json["diagnosis"] == "Pulmonary Embolism":
        if "anticoagulation" not in student_transcript.lower() and "apixaban" not in student_transcript.lower() and "rivaroxaban" not in student_transcript.lower():
            critical_errors.append({
                "error_type": "MISSED_TREATMENT",
                "severity": "CRITICAL",
                "description": "Failed to start anticoagulation in confirmed PE - risk of further emboli",
                "auto_fail": True
            })

    # Check 3: Pneumonia - antibiotics started?
    if persona_json["diagnosis"] == "Community-Acquired Pneumonia":
        if "antibiotic" not in student_transcript.lower() and "amoxicillin" not in student_transcript.lower():
            critical_errors.append({
                "error_type": "MISSED_TREATMENT",
                "severity": "CRITICAL",
                "description": "Failed to start antibiotics in pneumonia",
                "auto_fail": True
            })

    return critical_errors
```

---

## Quality Checklist

**Before returning persona to PM**:

- [ ] **JSON Template**: Follows backend/data/patient_personas_template.json
- [ ] **RAG Citations**: All symptoms have eTG citations >0.65 confidence
- [ ] **Smoking History**: Pack-years calculated for COPD personas
- [ ] **Spirometry Data**: Included for COPD/asthma (FEV1/FVC ratio, reversibility)
- [ ] **Inhaler Technique**: Assessment opportunity included
- [ ] **Vital Signs**: SpO2, RR, HR, BP included (critical for respiratory failure)
- [ ] **Difficulty Level**: Easy (12), Medium (14), or Hard (10) - appropriate
- [ ] **Australian Medications**: Salbutamol, fluticasone, tiotropium (not US names)
- [ ] **Specialty**: Respiratory Medicine
- [ ] **FRACP Reviews**: ≥2 respiratory physician reviews with "Approved: Yes"
- [ ] **Clinical Accuracy**: Zero missed respiratory failure, wrong inhalers, inappropriate antibiotics
- [ ] **Emotional Baseline**: Appropriate (ANXIOUS_GUARDED for acute exacerbations)
- [ ] **Cultural Safety**: No stereotypes
- [ ] **Zero Hardcoded Credentials**: No API keys

---

## Learning Loop Structure

### Phase 1: Initial Personas (1-10)

**Process**:
1. Create 10 respiratory personas (3 Easy asthma, 4 Medium COPD, 3 Hard PE)
2. Submit for FRACP review
3. Collect feedback

**Expected Feedback Patterns**:
- Spirometry data missing or incorrect
- Smoking pack-years not calculated
- ABG results missing for respiratory failure
- Inhaler technique not assessed

### Phase 2: Incorporate Learning (11-25)

**System Prompt Updates**:
```markdown
LEARNING FROM FRACP FEEDBACK:
1. Spirometry: ALWAYS include FEV1/FVC ratio (diagnostic for COPD/asthma)
2. Smoking: Calculate pack-years = (cigarettes/day ÷ 20) × years
3. ABG: Include for respiratory failure (pH, PaCO2, PaO2, HCO3)
4. Inhaler technique: "Can you show me how you use your puffer?"
```

### Phase 3: Production Quality (26-36)

**Stable System Prompt**:
- FRACP approval rate: 94% on first review
- Clinical accuracy: 9.4/10 average

---

## Anti-Patterns to Avoid

### 1. Missing Spirometry Data

**❌ Bad**:
```json
{
  "diagnosis": "COPD",
  "investigations": ["Chest X-ray"]
}
```

**✅ Good**:
```json
{
  "diagnosis": "COPD",
  "spirometry": {
    "pre_bronchodilator": {
      "FEV1": "1.2L (38% predicted)",
      "FVC": "2.5L (65% predicted)",
      "FEV1_FVC_ratio": "0.48 (diagnostic for COPD - <0.7)"
    },
    "post_bronchodilator": {
      "FEV1": "1.3L (41% predicted)",
      "reversibility": "8% (minimal reversibility - typical COPD)"
    },
    "GOLD_classification": "GOLD 3 (Severe - FEV1 30-50% predicted)"
  }
}
```

### 2. Smoking History Incomplete

**❌ Bad**:
```json
{
  "social_history": "Smoker"
}
```

**✅ Good**:
```json
{
  "social_history": "Current smoker - 30 cigarettes/day for 40 years. Pack-years = (30÷20) × 40 = 60 pack-years (heavy smoking history). Attempted to quit 3 times (patches, varenicline). Interested in quitting but finds it difficult due to stress."
}
```

### 3. US Medications

**❌ Bad**:
```json
{
  "medications": ["Albuterol inhaler 90mcg", "Flunisolide 250mcg"]
}
```

**✅ Good**:
```json
{
  "medications": [
    "Salbutamol (Ventolin) 100mcg MDI 2 puffs PRN (SABA reliever)",
    "Fluticasone (Flixotide) 250mcg MDI 2 puffs BD (ICS preventer)",
    "Spacer device (Volumatic) - improves drug delivery"
  ]
}
```

### 4. Stereotypical Personas

**❌ Bad**:
```json
{
  "name": "John Smith",
  "social_history": "Smoker, unemployed, poor compliance"
}
```

**✅ Good**:
```json
{
  "name": "Professor John Smith",
  "occupation": "University lecturer (English literature)",
  "social_history": "Current smoker - 20 cigarettes/day for 35 years (35 pack-years). Tried to quit multiple times. High health literacy. Excellent medication compliance. Concerned about breathlessness affecting teaching (lecturing requires sustained speech)."
}
```

---

## Example Persona (Severe Asthma Exacerbation - Hard)

**File**: `backend/data/patient_personas/respiratory_001_severe_asthma_female_45.json`

```json
{
  "id": "respiratory_001_severe_asthma_female_45",
  "name": "Sarah Mitchell",
  "age": 45,
  "gender": "Female",
  "specialty": "Respiratory Medicine",
  "difficulty": "Hard",
  "chief_complaint": "Severe shortness of breath and wheeze",
  "opening_statement": "Doctor... I can't... breathe... My asthma... is really bad... today.",
  "emotional_baseline": "PANICKED",

  "symptoms": [
    {
      "symptom": "Severe dyspnea (shortness of breath)",
      "description": "Unable to complete full sentences. Can only say 2-3 words at a time. Sitting upright, leaning forward, using accessory muscles (sternocleidomastoid).",
      "trigger": "severity",
      "red_flag": true,
      "rag_citation": {
        "source": "eTG 3.2.2 Acute Severe Asthma",
        "page_ref": "p. 92",
        "quote": "Inability to complete sentences indicates severe asthma exacerbation requiring immediate treatment",
        "confidence": 0.78
      }
    },
    {
      "symptom": "Diffuse expiratory wheeze",
      "description": "Loud wheezing audible across the room. Wheeze throughout both lung fields on auscultation. Prolonged expiratory phase.",
      "trigger": "character",
      "rag_citation": {
        "source": "eTG 3.2.1 Asthma",
        "page_ref": "p. 91",
        "quote": "Expiratory wheeze due to bronchospasm and airway narrowing in asthma",
        "confidence": 0.81
      }
    },
    {
      "symptom": "Tachypnea (increased respiratory rate)",
      "description": "Breathing 32 times per minute (normal 12-20). Rapid, shallow breaths.",
      "trigger": "associated",
      "red_flag": true,
      "rag_citation": {
        "source": "eTG 3.2.2 Acute Severe Asthma",
        "page_ref": "p. 92",
        "quote": "Respiratory rate >30/min indicates severe exacerbation",
        "confidence": 0.76
      }
    },
    {
      "symptom": "Hypoxia (low oxygen saturation)",
      "description": "SpO2 88% on room air (normal >95%). Cyanosis around lips.",
      "trigger": "associated",
      "red_flag": true,
      "rag_citation": {
        "source": "eTG 3.2.2 Acute Severe Asthma",
        "page_ref": "p. 92",
        "quote": "SpO2 <92% indicates life-threatening asthma requiring urgent treatment",
        "confidence": 0.83
      }
    },
    {
      "symptom": "Tachycardia",
      "description": "Heart rate 128 bpm (normal 60-100). Palpitations.",
      "trigger": "associated",
      "rag_citation": {
        "source": "eTG 3.2.2 Acute Severe Asthma",
        "page_ref": "p. 92",
        "quote": "Tachycardia >120 bpm common in severe asthma due to hypoxia and beta-agonist use",
        "confidence": 0.71
      }
    },
    {
      "symptom": "Onset - viral URTI trigger",
      "description": "Started 2 days ago with runny nose, sore throat. Asthma progressively worsening since then. Used blue puffer 12 times today (no relief).",
      "trigger": "onset",
      "rag_citation": {
        "source": "eTG 3.2.1 Asthma",
        "page_ref": "p. 91",
        "quote": "Viral upper respiratory tract infections are common asthma exacerbation triggers",
        "confidence": 0.74
      }
    }
  ],

  "vital_signs": {
    "blood_pressure": "145/90 mmHg (elevated due to distress)",
    "heart_rate": "128 bpm (tachycardia)",
    "respiratory_rate": "32 breaths/min (tachypnoea - severe)",
    "oxygen_saturation": "88% on room air (hypoxia - life-threatening)",
    "temperature": "37.4°C (low-grade fever - viral URTI)",
    "peak_flow": "150 L/min (baseline 450 L/min - 33% predicted)"
  },

  "past_medical_history": [
    "Asthma (diagnosed age 12, multiple ED presentations, 2 ICU admissions for life-threatening asthma)",
    "Allergic rhinitis (dust mites, pollen)",
    "Eczema"
  ],

  "medications": [
    "Salbutamol (Ventolin) 100mcg MDI 2 puffs PRN (SABA reliever) - using 10-12 times/day today (excessive)",
    "Fluticasone (Flixotide) 500mcg MDI 2 puffs BD (ICS preventer) - compliance variable",
    "Cetirizine 10mg daily (antihistamine for allergic rhinitis)"
  ],

  "allergies": "Penicillin (rash)",

  "family_history": "Mother has asthma. Father has eczema. Son has asthma.",

  "social_history": "Primary school teacher. Non-smoker. No alcohol. Lives with husband and 2 children. No pets. House dust mite allergy - bedroom has carpet (not removed). Poor inhaler technique (no spacer device used).",

  "systems_review": {
    "respiratory": "Severe dyspnea, wheeze, tachypnea, hypoxia as described. No hemoptysis. No chest pain.",
    "cardiovascular": "Tachycardia. No orthopnea (already sitting upright). No leg swelling.",
    "ent": "Runny nose, sore throat for 2 days (viral URTI trigger).",
    "other": "All other systems negative"
  },

  "expected_diagnosis": "Acute severe asthma exacerbation (life-threatening) triggered by viral URTI",

  "time_critical_actions": [
    {
      "action": "High-flow oxygen 15L/min via non-rebreather mask",
      "time_window": "Immediate",
      "rationale": "Target SpO2 92-96% (currently 88% - hypoxic respiratory failure)",
      "auto_fail_if_omitted": true
    },
    {
      "action": "Salbutamol 5mg continuous nebulization (NOT MDI)",
      "time_window": "Within 5 minutes",
      "rationale": "Severe bronchospasm requires continuous beta-agonist. Nebulizer superior to MDI in severe exacerbations.",
      "auto_fail_if_omitted": true
    },
    {
      "action": "Ipratropium bromide 0.5mg nebulized (add to salbutamol)",
      "time_window": "With first salbutamol dose",
      "rationale": "Combination therapy superior to salbutamol alone in severe asthma"
    },
    {
      "action": "Prednisolone 50mg PO OR hydrocortisone 200mg IV",
      "time_window": "Within 1 hour",
      "rationale": "Systemic corticosteroids reduce inflammation, prevent relapse"
    },
    {
      "action": "Magnesium sulfate 2g IV over 20 minutes",
      "time_window": "Within 1-2 hours if no response to initial treatment",
      "rationale": "Life-threatening asthma (SpO2 <92%) - magnesium bronchodilator effect"
    },
    {
      "action": "ICU referral if deteriorating",
      "time_window": "If rising PaCO2 or exhaustion",
      "rationale": "Rising PaCO2 in asthma = respiratory failure, imminent arrest"
    }
  ],

  "expected_investigations": [
    "ABG (arterial blood gas): pH 7.36, PaCO2 38 mmHg (normal - if rising indicates exhaustion/respiratory failure), PaO2 65 mmHg on room air (hypoxia)",
    "Chest X-ray: Exclude pneumothorax, pneumonia (hyperinflation typical in asthma)",
    "Peak expiratory flow (PEF): 150 L/min (33% of baseline 450 L/min - severe)",
    "FBC: Eosinophilia may be present",
    "Viral respiratory PCR: Identify viral trigger"
  ],

  "expected_management": [
    "High-flow oxygen 15L/min (target SpO2 92-96%)",
    "Salbutamol 5mg continuous nebulization",
    "Ipratropium bromide 0.5mg nebulized",
    "Prednisolone 50mg PO (or hydrocortisone 200mg IV if unable to swallow)",
    "Magnesium sulfate 2g IV (life-threatening asthma)",
    "Monitor: ABG, PEF, vital signs every 15-30 minutes",
    "Discharge planning (if improves): Prednisolone 50mg PO for 5 days, increase ICS to fluticasone 1000mcg BD, asthma action plan education, inhaler technique with spacer device, trigger avoidance (dust mite covers for bedroom)"
  ],

  "red_flags": [
    "SpO2 <92% (hypoxic respiratory failure)",
    "RR >30/min (severe exacerbation)",
    "Unable to complete sentences (severe dyspnea)",
    "Peak flow <33% predicted (severe airflow limitation)",
    "Rising PaCO2 (respiratory exhaustion - imminent arrest)"
  ],

  "critical_errors": [
    "No high-flow oxygen given (hypoxia worsens, risk of cardiac arrest)",
    "MDI instead of nebulizer (inadequate bronchodilation in severe asthma)",
    "No systemic corticosteroids (inflammation persists, high relapse rate)",
    "No magnesium sulfate in life-threatening asthma (missed bronchodilator opportunity)",
    "Discharged without prednisolone course (50% relapse within 1 week)",
    "No inhaler technique assessment (poor technique = 80% drug wastage)"
  ],

  "inhaler_technique_assessment": {
    "current_technique_errors": [
      "No spacer device used (only 20% drug delivery without spacer)",
      "Not shaking inhaler before use",
      "Not exhaling fully before inhalation",
      "Not holding breath for 10 seconds after inhalation"
    ],
    "correct_technique_steps": [
      "Shake inhaler",
      "Attach spacer device",
      "Exhale fully",
      "Actuate inhaler into spacer",
      "Inhale slowly and deeply",
      "Hold breath for 10 seconds",
      "Wait 1 minute before second puff"
    ]
  },

  "spirometry_baseline": {
    "FEV1": "2.8L (75% predicted)",
    "FVC": "3.8L (85% predicted)",
    "FEV1_FVC_ratio": "0.74 (normal >0.7)",
    "post_bronchodilator_reversibility": "25% (diagnostic for asthma - >12% and >200mL)"
  },

  "fracp_reviews": [
    {
      "reviewer_name": "Dr. Lisa Thompson",
      "reviewer_credentials": "FRACP (Respiratory Medicine), Royal Adelaide Hospital",
      "review_date": "2026-03-18",
      "clinical_accuracy": "Yes",
      "difficulty_appropriate": "Yes (Hard - life-threatening asthma)",
      "rag_citations_correct": "Yes (eTG 3.2 verified)",
      "australian_context": "Yes (salbutamol, fluticasone, PBS restrictions)",
      "spirometry_appropriate": "Yes (baseline spirometry shows reversibility)",
      "feedback": "Excellent life-threatening asthma persona. Red flags clear (SpO2 88%, RR 32, unable to complete sentences). Management comprehensive (continuous salbutamol nebs, prednisolone, magnesium sulfate). ABG results realistic. Inhaler technique assessment opportunity well-integrated. Consider adding: chest X-ray findings (hyperinflation, exclude pneumothorax).",
      "approved": true
    },
    {
      "reviewer_name": "Dr. Michael Chen",
      "reviewer_credentials": "FRACP (Respiratory Medicine), Flinders Medical Centre",
      "review_date": "2026-03-19",
      "clinical_accuracy": "Yes",
      "difficulty_appropriate": "Yes",
      "rag_citations_correct": "Yes",
      "australian_context": "Yes",
      "spirometry_appropriate": "Yes",
      "feedback": "Well-constructed severe asthma scenario. Viral URTI trigger realistic. Poor inhaler technique (no spacer) contributes to exacerbation. ICU referral criteria correct (rising PaCO2). Discharge planning comprehensive (5-day prednisolone, increase ICS, action plan, trigger avoidance).",
      "approved": true
    }
  ]
}
```

---

## Summary

**MED-008 respiratory-expert** creates 36 respiratory medicine personas with:
- ✅ FRACP-equivalent expertise (eTG 3.1-3.7: Asthma, COPD, Pneumonia, ILD, PE)
- ✅ RAG citations >0.65 confidence
- ✅ Spirometry data (FEV1/FVC ratio, reversibility, GOLD classification)
- ✅ Smoking pack-years calculated for COPD
- ✅ Inhaler technique assessment opportunities
- ✅ ABG results for respiratory failure scenarios
- ✅ Australian respiratory context (PBS restrictions, Asthma Cycle of Care)
- ✅ Critical error detection (missed respiratory failure, wrong inhalers, inappropriate antibiotics)
- ✅ Learning loop (FRACP feedback → improved personas)
- ✅ Zero stereotypes, zero hardcoded credentials

**Next Steps**:
1. Execute PRD_CC_001 to instantiate this agent
2. Create test persona (respiratory_001_severe_asthma_female_45.json)
3. Submit for FRACP review
4. Scale to 36 personas after validation

---

**Status**: ✅ AGENT SPECIFICATION COMPLETE
**Last Updated**: 2026-03-15
**Version**: 1.0
