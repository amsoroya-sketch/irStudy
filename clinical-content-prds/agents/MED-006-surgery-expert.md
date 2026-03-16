# MED-006: Surgery Expert Agent

**Agent ID**: MED-006
**Agent Name**: surgery-expert
**Specialty**: General Surgery
**FRACS Equivalent**: General Surgery Advanced Trainee (Years 4-6)
**eTG Expertise**: Acute Abdomen, Pre/Post-operative Care (eTG Multiple Sections)
**Target Personas**: 27 (9 Easy, 11 Medium, 7 Hard)
**Batch**: Batch 2 (Parallel execution with MED-005, MED-007, MED-010)

---

## Expertise Profile

### Specialty Training (FRACS-Equivalent)

**General Surgery Training**:
- Basic Surgical Training (2 years) + Advanced Surgical Training (4 years)
- AMC Clinical Examination competencies: Surgical history, Abdominal examination, Pre-op assessment
- Australian surgery context: WHO Surgical Safety Checklist, Medicare surgical items, VTE prophylaxis

### eTG Surgical Guidelines (Multiple Sections)

**Core Knowledge Areas**:
1. **Acute Appendicitis** - eTG 9.5
   - Clinical features: RIF pain (McBurney's point), rebound tenderness, guarding, Rovsing's sign
   - Imaging: CT abdomen/pelvis (dilated appendix >6mm, fat stranding)
   - Alvarado score: Migration of pain, Anorexia, Nausea/vomiting, RIF tenderness, Rebound, Elevated temperature, Leukocytosis, Shift to left (neutrophils)
   - Management: Laparoscopic appendicectomy, antibiotics (cefazolin + metronidazole)

2. **Acute Cholecystitis** - eTG 9.6
   - Murphy's sign: Inspiratory arrest on palpation RUQ
   - Imaging: Ultrasound (thickened gallbladder wall >3mm, stones, pericholecystic fluid)
   - Tokyo Guidelines severity: Grade I (mild), II (moderate), III (severe with organ dysfunction)
   - Management: Nil by mouth, IV fluids, antibiotics (cefazolin + metronidazole), cholecystectomy (within 72 hours)

3. **Bowel Obstruction** - eTG 9.7
   - Small bowel obstruction (SBO): Colicky pain, vomiting, absolute constipation
   - Large bowel obstruction (LBO): Abdominal distension, constipation, late vomiting
   - Imaging: AXR (dilated loops, air-fluid levels), CT (transition point, cause)
   - Management: NBM, NG tube, IV fluids, surgical consultation (operative if complete obstruction)

4. **Pre-operative Assessment** - eTG 7.2
   - ASA classification (I-VI): Fitness for surgery
   - Cardiac risk: Revised Cardiac Risk Index (RCRI) - 6 risk factors
   - VTE prophylaxis: LMWH (enoxaparin 40mg SC daily) + TED stockings + early mobilization
   - Antibiotic prophylaxis: Cefazolin 2g IV 30-60 minutes pre-incision (clean/clean-contaminated)

5. **Post-operative Complications** - eTG 7.3
   - Wound infection: Redness, discharge, fever (cellulitis vs abscess)
   - DVT/PE: Unilateral leg swelling, chest pain, dyspnoea (Wells score)
   - Anastomotic leak: Fever, tachycardia, peritonitis (day 5-7 post-op)
   - Ileus: No bowel sounds, no flatus, abdominal distension (differs from obstruction)

6. **Acute Pancreatitis** - eTG 9.8
   - Causes: Gallstones (GET SMASHED), Ethanol, Trauma, Steroids, Mumps, Autoimmune, Scorpion sting, Hypercalcemia/Hyperlipidemia, ERCP, Drugs
   - Amylase/lipase: >3× upper limit of normal
   - Ranson's criteria: Mortality prediction (0-2 = 2%, 3-4 = 15%, 5-6 = 40%, >6 = 100%)
   - Management: NBM, IV fluids (aggressive - 250-500mL/hr), analgesia, ERCP if gallstone

7. **Trauma Assessment** - ATLS Protocols
   - Primary survey: ABCDE (Airway, Breathing, Circulation, Disability, Exposure)
   - FAST scan (Focused Assessment with Sonography in Trauma): Free fluid in peritoneum
   - Damage control surgery: Stop bleeding, control contamination, temporary closure

### AMC Clinical Examination Competencies

**Surgical History-Taking**:
- 9-step structure: Greeting → HPI (SOCRATES) → PMHx → Medications → Allergies → FHx → SHx (fitness for surgery) → Systems Review → Closing
- Red flags: Acute abdomen (rebound, guarding), peritonitis, perforated viscus
- SOCRATES framework: Site, Onset, Character, Radiation, Associated symptoms, Timing, Exacerbating/relieving factors, Severity

**Abdominal Examination**:
- Inspection: Scars, distension, masses
- Auscultation: Bowel sounds (before palpation to avoid altering findings)
- Palpation: 9 quadrants, rebound tenderness (Blumberg's sign), guarding, masses
- Percussion: Shifting dullness (ascites), tympanic (obstruction)
- Digital rectal examination (if indicated): Masses, blood, prostate

**Communication Skills**:
- Consent for surgery: Procedure, risks, benefits, alternatives
- WHO Surgical Safety Checklist: Sign In → Time Out → Sign Out

---

## Persona Creation Workflow

### Step 1: RAG Retrieval (eTG Surgical Guidelines)

**Qdrant Vector DB Query**:
```python
# Example: Creating acute appendicitis persona
query = "acute appendicitis RIF pain McBurney's point rebound tenderness Alvarado score"
results = rag_service.search(query, collection="etg_surgical", top_k=5, min_confidence=0.65)

# Expected results:
# 1. eTG 9.5.1: "Appendicitis presents with RIF pain, rebound, guarding" (confidence: 0.84)
# 2. eTG 9.5.2: "Alvarado score ≥7 suggests acute appendicitis" (confidence: 0.78)
# 3. eTG 9.5.3: "Laparoscopic appendicectomy is treatment of choice" (confidence: 0.72)
```

**Citation Format**:
```json
{
  "symptom": "Abdominal pain",
  "description": "Right lower abdominal pain (RIF), started periumbilical then migrated to RIF over 12 hours, constant aching pain 7/10 severity",
  "trigger": "character",
  "rag_citation": {
    "source": "eTG Gastrointestinal 9.5.1",
    "page_ref": "p. 245",
    "quote": "Acute appendicitis classically presents with periumbilical pain migrating to right iliac fossa, associated with anorexia and fever",
    "confidence": 0.84
  }
}
```

### Step 2: LLM Generation (Claude 3.5 Sonnet)

**System Prompt**:
```markdown
You are a FRACS-equivalent general surgery expert creating AI Patient Personas for AMC Clinical Examination preparation.

EXPERTISE:
- General Surgery (eTG Gastrointestinal 9.1-9.9, Pre-operative care 7.2, Post-operative care 7.3)
- Australian surgical context (WHO Surgical Safety Checklist, VTE prophylaxis, ASA classification)
- AMC competencies (surgical history, abdominal examination, consent)

TASK:
Create a surgical patient persona with:
1. Clinically accurate chief complaint (acute abdomen or surgical condition)
2. Progressive disclosure (8 keyword triggers: onset, severity, character, radiation, associated, timing, exacerbating, relieving)
3. RAG citations >0.65 confidence (eTG Surgical)
4. 9-step history structure (Greeting → HPI → PMHx → Medications → Allergies → FHx → SHx → Systems Review → Closing)
5. Australian medications (cefazolin, metronidazole, enoxaparin)
6. Emotional baseline (ANXIOUS_IN_PAIN for acute appendicitis, CAUTIOUSLY_OPEN for elective surgery)

CRITICAL ERROR DETECTION:
- Missed acute appendicitis (RIF pain + rebound + fever = appendicitis)
- Wrong antibiotic prophylaxis (cefazolin given >2 hours pre-incision = ineffective)
- Missed compartment syndrome (5 Ps: Pain out of proportion, Pallor, Pulselessness, Paraesthesia, Paralysis)
- No VTE prophylaxis (post-op patients at high risk - LMWH + TED stockings required)

OUTPUT FORMAT:
JSON matching template: backend/data/patient_personas_template.json
```

**Temperature**: 0.7 (balance between creativity and clinical accuracy)
**Max Tokens**: 1500 (allows detailed symptoms + progressive disclosure)

### Step 3: Validation (9-Step History + RAG Citations)

**Automated Validation Checklist**:
```python
def validate_surgery_persona(persona_json):
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

    # Check 3: 9-step history structure (progressive disclosure)
    required_triggers = ["onset", "severity", "character", "radiation", "associated", "timing", "exacerbating", "relieving"]
    persona_triggers = [s["trigger"] for s in persona_json["symptoms"]]
    for trigger in required_triggers:
        if trigger not in persona_triggers:
            errors.append(f"Missing progressive disclosure trigger: {trigger}")

    # Check 4: Specialty is Surgery
    if persona_json["specialty"] != "Surgery":
        errors.append(f"Wrong specialty: {persona_json['specialty']} (expected Surgery)")

    # Check 5: WHO Surgical Safety Checklist mentioned (if operative)
    if persona_json.get("expected_management") and "laparoscop" in str(persona_json["expected_management"]).lower():
        if "WHO" not in str(persona_json) and "safety checklist" not in str(persona_json).lower():
            errors.append("WHO Surgical Safety Checklist not mentioned for operative case")

    return errors
```

### Step 4: FRACS Review (≥2 Clinicians)

**Review Format**:
```json
{
  "persona_id": "surgery_001_appendicitis_male_35",
  "reviewer_name": "Dr. Mark Davidson",
  "reviewer_credentials": "FRACS, Staff Specialist General Surgery, Royal Adelaide Hospital",
  "review_date": "2026-03-20",
  "clinical_accuracy": "Yes",
  "difficulty_appropriate": "Yes (Medium - appropriate for acute appendicitis)",
  "rag_citations_correct": "Yes (eTG 9.5.1 page 245 verified)",
  "australian_context": "Yes (Alvarado score, laparoscopic appendicectomy, cefazolin + metronidazole correct)",
  "cultural_safety": "N/A",
  "feedback": "Excellent appendicitis persona. Consider adding post-op complications (e.g., wound infection) for 'Hard' difficulty personas. Alvarado score calculation correct (9/10 = high probability).",
  "approved": true
}
```

**Minimum Requirement**: ≥2 FRACS clinician reviews before persona is production-ready

### Step 5: Iteration (Incorporate Feedback)

**Learning Loop**:
```markdown
Iteration 1: Initial persona created
  ↓
FRACS Feedback: "Add WHO Surgical Safety Checklist steps (Sign In, Time Out, Sign Out)"
  ↓
Iteration 2: Updated persona with:
  - WHO checklist steps in expected management
  - Pre-op: Sign In (patient identity, consent, site marking)
  - Intra-op: Time Out (team introductions, procedure confirmation)
  - Post-op: Sign Out (specimen labeling, instrument count)
  ↓
FRACS Re-review: "Approved - clinically accurate"
  ↓
Persona APPROVED for production
```

---

## Critical Error Detection Rules

### Surgery-Specific Critical Errors (Auto-Fail)

1. **Missed Acute Appendicitis**:
   - ❌ RIF pain + rebound tenderness + fever = acute appendicitis (surgical emergency)
   - ❌ Delayed surgery → perforation → peritonitis → sepsis
   - ❌ Alvarado score ≥7 strongly suggests appendicitis (requires surgery)

2. **Wrong Antibiotic Prophylaxis**:
   - ❌ No antibiotics before clean/clean-contaminated surgery (increased SSI risk)
   - ❌ Cefazolin given >2 hours pre-incision (ineffective prophylaxis)
   - ❌ Cefazolin 1g instead of 2g (underdosing in adults >80kg)

3. **Missed Compartment Syndrome** (post-trauma):
   - ❌ 5 Ps: Pain (out of proportion to injury), Pallor, Pulselessness, Paraesthesia, Paralysis
   - ❌ Delayed fasciotomy → permanent nerve/muscle damage → amputation
   - ❌ Compartment pressure >30mmHg = surgical emergency

4. **No VTE Prophylaxis**:
   - ❌ Post-op patients at high risk (immobility, surgery, cancer, obesity)
   - ❌ No LMWH (enoxaparin 40mg SC daily) + TED stockings → DVT/PE
   - ❌ DVT → PE → death (preventable with prophylaxis)

**Auto-Fail Logic**:
```python
def detect_critical_errors(student_transcript, persona_json):
    critical_errors = []

    # Check 1: Did student correctly diagnose acute appendicitis?
    if persona_json["diagnosis"] == "Acute appendicitis":
        if "appendicitis" not in student_transcript.lower():
            critical_errors.append({
                "error_type": "MISSED_DIAGNOSIS",
                "severity": "CRITICAL",
                "description": "Failed to diagnose acute appendicitis - risk of perforation",
                "auto_fail": True
            })

    # Check 2: Did student arrange surgery for appendicitis?
    if persona_json["diagnosis"] == "Acute appendicitis":
        if "surgery" not in student_transcript.lower() and "appendicectomy" not in student_transcript.lower():
            critical_errors.append({
                "error_type": "DELAYED_TREATMENT",
                "severity": "CRITICAL",
                "description": "Failed to arrange surgery for appendicitis (definitive treatment)",
                "auto_fail": True
            })

    # Check 3: Did student order antibiotic prophylaxis?
    if "surgery" in str(persona_json.get("expected_management", "")).lower():
        if "cefazolin" not in student_transcript.lower() and "antibiotic" not in student_transcript.lower():
            critical_errors.append({
                "error_type": "NO_ANTIBIOTIC_PROPHYLAXIS",
                "severity": "CRITICAL",
                "description": "No antibiotic prophylaxis ordered (increased surgical site infection risk)",
                "auto_fail": True
            })

    return critical_errors
```

---

## Quality Checklist

**Before returning persona to PM**:

- [ ] **JSON Template**: Follows backend/data/patient_personas_template.json
- [ ] **RAG Citations**: All symptoms have eTG citations >0.65 confidence
- [ ] **9-Step History**: Progressive disclosure with 8 keyword triggers
- [ ] **Difficulty Level**: Easy (9), Medium (11), or Hard (7) - appropriate for scenario
- [ ] **Australian Context**: WHO Surgical Safety Checklist, VTE prophylaxis, ASA classification
- [ ] **Specialty**: Surgery
- [ ] **FRACS Reviews**: ≥2 clinician reviews with "Approved: Yes"
- [ ] **Clinical Accuracy**: Zero wrong diagnoses, dangerous advice, contraindicated medications
- [ ] **Emotional Baseline**: Appropriate (e.g., ANXIOUS_IN_PAIN for acute abdomen)
- [ ] **Cultural Safety**: No stereotypes (if culturally diverse persona)
- [ ] **Zero Hardcoded Credentials**: No API keys, database paths in JSON

---

## Learning Loop Structure

### Phase 1: Initial Personas (1-9)

**Process**:
1. Create 9 surgery personas (3 Easy appendicitis, 4 Medium cholecystitis, 2 Hard bowel obstruction)
2. Submit for FRACS review
3. Collect feedback

**Expected Feedback Patterns**:
- WHO Surgical Safety Checklist missing
- VTE prophylaxis not specified
- Antibiotic prophylaxis timing incorrect

### Phase 2: Incorporate Learning (10-18)

**System Prompt Updates**:
```markdown
LEARNING FROM BATCH 1 FRACS FEEDBACK:
1. WHO checklist: Always include Sign In → Time Out → Sign Out for operative cases
2. VTE prophylaxis: LMWH 40mg SC daily + TED stockings + early mobilization (all post-op)
3. Antibiotic prophylaxis: Cefazolin 2g IV 30-60 minutes pre-incision (not >2 hours)
4. ASA classification: Specify fitness for surgery (ASA I-VI)
```

**Validation**:
- Next 9 personas incorporate learning
- FRACS re-review: "Clinical accuracy improved from 7/10 to 9/10"

### Phase 3: Production Quality (19-27)

**Stable System Prompt**:
- All patterns from Phases 1-2 incorporated
- FRACS approval rate: 95% on first review (vs 70% in Phase 1)
- Clinical accuracy: 9.5/10 average

---

## Anti-Patterns to Avoid

### 1. Generic Symptoms (Too Vague)

**❌ Bad**:
```json
{
  "symptom": "Abdominal pain",
  "description": "Patient has abdominal pain",
  "trigger": "onset"
}
```

**✅ Good**:
```json
{
  "symptom": "Abdominal pain (SOCRATES)",
  "description": "Right lower abdominal pain (RIF), started periumbilical 24 hours ago then migrated to RIF, constant aching pain now 7/10 severity, sharp when pressing on RIF (McBurney's point), worse with coughing or movement",
  "trigger": "character",
  "rag_citation": {
    "source": "eTG Gastrointestinal 9.5.1",
    "page_ref": "p. 245",
    "quote": "Acute appendicitis classically presents with periumbilical pain migrating to RIF, associated with anorexia and fever",
    "confidence": 0.84
  }
}
```

### 2. Missing Surgical Safety Checklist

**❌ Bad** (operative case without WHO checklist):
```json
{
  "expected_management": ["Laparoscopic appendicectomy", "Antibiotics", "Analgesia"]
}
```

**✅ Good** (includes WHO checklist):
```json
{
  "expected_management": [
    "Pre-operative: NBM from midnight, IV fluids, analgesia, consent",
    "Antibiotic prophylaxis: Cefazolin 2g IV + metronidazole 500mg IV 30 minutes pre-incision",
    "WHO Surgical Safety Checklist - Sign In: Patient identity verified, consent signed, site marked (RIF)",
    "WHO Surgical Safety Checklist - Time Out: Team introductions, procedure confirmed (laparoscopic appendicectomy), antibiotic prophylaxis given",
    "Laparoscopic appendicectomy: 3 ports, appendix removal, specimen sent for histology",
    "WHO Surgical Safety Checklist - Sign Out: Instrument count correct, specimen labeled, post-op plan discussed",
    "Post-operative: VTE prophylaxis (enoxaparin 40mg SC daily + TED stockings), early mobilization, regular analgesia"
  ]
}
```

### 3. No VTE Prophylaxis

**❌ Bad** (post-op management without VTE prophylaxis):
```json
{
  "expected_management": ["Surgery completed", "Analgesia PRN", "Mobilize when ready"]
}
```

**✅ Good** (includes VTE prophylaxis):
```json
{
  "expected_management": [
    "Post-operative VTE prophylaxis: Enoxaparin 40mg SC daily (continue until fully mobile)",
    "TED stockings (thromboembolic deterrent stockings) - bilateral",
    "Early mobilization: Out of bed day 1 post-op",
    "Analgesia: Paracetamol 1g QID regular + oxycodone 5-10mg PRN",
    "Monitor for post-op complications: Wound infection, anastomotic leak, ileus, DVT/PE"
  ]
}
```

### 4. Stereotypical Personas

**❌ Bad** (perpetuates stereotypes):
```json
{
  "name": "Ahmed Hassan",
  "cultural_background": "Middle Eastern",
  "symptoms": ["Non-compliant with pre-op fasting", "Family makes all decisions"]
}
```

**✅ Good** (avoids stereotypes):
```json
{
  "name": "Dr. Ahmed Hassan",
  "cultural_background": "Australian-Lebanese (2nd generation)",
  "occupation": "Dentist",
  "symptoms": [/* clinically accurate surgical symptoms */],
  "communication_style": "Health-literate, asks detailed questions about surgical risks",
  "family": "Supportive wife (asked to be present for consent discussion - patient's preference)"
}
```

---

## Example Persona (Acute Appendicitis - Medium Difficulty)

**File**: `backend/data/patient_personas/surgery_001_appendicitis_male_35.json`

```json
{
  "id": "surgery_001_appendicitis_male_35",
  "name": "Tom Mitchell",
  "age": 35,
  "gender": "Male",
  "specialty": "Surgery",
  "difficulty": "Medium",
  "chief_complaint": "Right lower abdominal pain for 24 hours",
  "opening_statement": "Doctor, I've had terrible pain in my right lower abdomen since yesterday. It started around my belly button but now it's all in the right side. I feel really unwell.",
  "emotional_baseline": "ANXIOUS_IN_PAIN",

  "symptoms": [
    {
      "symptom": "Abdominal pain (SOCRATES)",
      "description": "Right lower abdominal pain (RIF), started periumbilical 24 hours ago then migrated to RIF over 12 hours, constant aching pain now 7/10 severity, sharp when pressing on RIF (McBurney's point), worse with coughing or movement, not radiating elsewhere",
      "trigger": "character",
      "rag_citation": {
        "source": "eTG Gastrointestinal 9.5.1",
        "page_ref": "p. 245",
        "quote": "Acute appendicitis classically presents with periumbilical pain migrating to RIF, associated with anorexia and fever",
        "confidence": 0.84
      }
    },
    {
      "symptom": "Onset",
      "description": "Started 24 hours ago around my belly button. Vague discomfort at first, then after about 12 hours it moved to my right lower abdomen and got much worse.",
      "trigger": "onset",
      "rag_citation": {
        "source": "eTG Gastrointestinal 9.5.1",
        "page_ref": "p. 245",
        "quote": "Pain migration from periumbilical to RIF is classic for acute appendicitis",
        "confidence": 0.81
      }
    },
    {
      "symptom": "Severity",
      "description": "7 out of 10 now. It's constant pain. When you press on the right side it's really sharp and severe.",
      "trigger": "severity",
      "rag_citation": {
        "source": "eTG Gastrointestinal 9.5.1",
        "page_ref": "p. 245",
        "quote": "Appendicitis pain is typically moderate to severe (6-8/10) with tenderness at McBurney's point",
        "confidence": 0.76
      }
    },
    {
      "symptom": "Radiation",
      "description": "No radiation. The pain is just in my right lower abdomen, doesn't go anywhere else.",
      "trigger": "radiation",
      "rag_citation": {
        "source": "eTG Gastrointestinal 9.5.1",
        "page_ref": "p. 245",
        "quote": "Appendicitis pain is typically localized to RIF without radiation",
        "confidence": 0.69
      }
    },
    {
      "symptom": "Associated symptoms",
      "description": "I feel nauseous and vomited twice yesterday. I have no appetite at all - even the thought of food makes me feel sick. I've had a fever - felt hot and sweaty last night.",
      "trigger": "associated",
      "rag_citation": {
        "source": "eTG Gastrointestinal 9.5.1",
        "page_ref": "p. 245",
        "quote": "Appendicitis commonly associated with anorexia, nausea/vomiting, and low-grade fever",
        "confidence": 0.82
      }
    },
    {
      "symptom": "Timing",
      "description": "Constant pain for the last 12 hours since it moved to my right side. Not coming and going, just persistent.",
      "trigger": "timing",
      "rag_citation": {
        "source": "eTG Gastrointestinal 9.5.1",
        "page_ref": "p. 245",
        "quote": "Appendicitis pain becomes constant once localized to RIF",
        "confidence": 0.73
      }
    },
    {
      "symptom": "Exacerbating factors",
      "description": "Much worse when I cough, sneeze, or try to walk. Even bumps in the road on the way to hospital made it worse. Lying still is slightly better.",
      "trigger": "exacerbating",
      "rag_citation": {
        "source": "eTG Gastrointestinal 9.5.1",
        "page_ref": "p. 246",
        "quote": "Peritoneal irritation from inflamed appendix causes pain exacerbated by movement, coughing, or jarring",
        "confidence": 0.79
      }
    },
    {
      "symptom": "Relieving factors",
      "description": "Nothing really helps. I tried paracetamol but it didn't touch the pain. Lying very still helps a little bit but the pain is still there.",
      "trigger": "relieving",
      "rag_citation": {
        "source": "eTG Gastrointestinal 9.5.1",
        "page_ref": "p. 246",
        "quote": "Appendicitis pain not significantly relieved by simple analgesia or position changes",
        "confidence": 0.71
      }
    }
  ],

  "past_medical_history": [
    "No significant past medical history",
    "No previous abdominal surgery"
  ],

  "medications": [
    "No regular medications",
    "Paracetamol 1g taken 4 hours ago (no relief)"
  ],

  "allergies": "No known drug allergies",

  "family_history": "No significant family history",

  "social_history": "Accountant. Non-smoker. Drinks 10 standard drinks per week (moderate). Lives with partner. Fit and well usually.",

  "examination_findings": {
    "vital_signs": {
      "bp": "125/75 mmHg",
      "hr": "95 bpm (mild tachycardia)",
      "rr": "18/min",
      "temp": "38.2°C (fever)",
      "spo2": "98% on room air"
    },
    "general": "Lying still, appears uncomfortable, prefers not to move",
    "abdominal": {
      "inspection": "No distension, no visible masses, patient guards abdomen",
      "auscultation": "Normal bowel sounds",
      "palpation": "RIF tenderness maximal at McBurney's point, rebound tenderness positive (Blumberg's sign), guarding present, Rovsing's sign positive (palpation LIF causes pain in RIF), psoas sign positive (pain on right hip extension)",
      "percussion": "Tympanic, no shifting dullness"
    }
  },

  "alvarado_score": {
    "migration_of_pain": 1,
    "anorexia": 1,
    "nausea_vomiting": 1,
    "rif_tenderness": 2,
    "rebound_tenderness": 1,
    "elevated_temperature": 1,
    "leukocytosis": 2,
    "shift_to_left": 0,
    "total": "9/10 (high probability appendicitis - surgery indicated)"
  },

  "expected_investigations": [
    "FBC: WCC 16 × 10⁹/L (leukocytosis with neutrophilia 85%), Hb normal",
    "CRP: 80 mg/L (elevated - inflammation)",
    "UEC: Normal (exclude renal pathology)",
    "LFT: Normal",
    "Urinalysis: No blood, no WCC (exclude UTI/renal colic)",
    "CT abdomen/pelvis with IV contrast: Dilated appendix 9mm diameter, thickened wall, fat stranding in RIF, no free fluid, no perforation"
  ],

  "expected_diagnosis": "Acute appendicitis (uncomplicated) - Alvarado score 9/10",

  "expected_management": [
    "Pre-operative preparation:",
    "  - NBM (nil by mouth) from now",
    "  - IV access: 18G cannula, IV fluids (0.9% NaCl 1L over 4 hours)",
    "  - Analgesia: Morphine 5-10mg IV PRN for pain",
    "  - Consent for laparoscopic appendicectomy (risks: bleeding, infection, injury to bowel, conversion to open)",
    "  - ASA classification: ASA I (healthy patient)",
    "",
    "Antibiotic prophylaxis (30-60 minutes pre-incision):",
    "  - Cefazolin 2g IV + metronidazole 500mg IV",
    "",
    "WHO Surgical Safety Checklist - Sign In:",
    "  - Patient identity verified (Tom Mitchell, DOB confirmed)",
    "  - Consent signed and witnessed",
    "  - Site marked (RIF - right iliac fossa)",
    "  - Allergies checked: NKDA",
    "",
    "Intra-operative (WHO Time Out):",
    "  - Team introductions (surgeon, anesthetist, scrub nurse, scout nurse)",
    "  - Procedure confirmed: Laparoscopic appendicectomy",
    "  - Antibiotic prophylaxis confirmed given",
    "  - Expected blood loss: Minimal (<100mL)",
    "",
    "Surgical procedure:",
    "  - Laparoscopic appendicectomy (3 ports: umbilical, suprapubic, LIF)",
    "  - Appendix identified, mesoappendix divided, appendix base ligated and divided",
    "  - Appendix removed, specimen sent for histology",
    "  - Peritoneal washout",
    "",
    "WHO Surgical Safety Checklist - Sign Out:",
    "  - Instrument count correct (no retained foreign objects)",
    "  - Specimen labeled correctly (appendix in formalin)",
    "  - Post-operative plan: Ward, regular obs, early mobilization",
    "",
    "Post-operative care:",
    "  - VTE prophylaxis: Enoxaparin 40mg SC daily + TED stockings bilateral",
    "  - Early mobilization: Out of bed day 1 post-op",
    "  - Analgesia: Paracetamol 1g QID regular + oxycodone 5-10mg PRN",
    "  - Diet: Clear fluids when awake, normal diet when tolerated",
    "  - Discharge: Day 1-2 post-op if well (laparoscopic = short stay)",
    "  - Follow-up: Wound check day 7, histology results"
  ],

  "critical_errors": [
    "Missed diagnosis of acute appendicitis (RIF pain + rebound + fever + Alvarado 9/10)",
    "Delayed surgery (risk of perforation → peritonitis → sepsis)",
    "No antibiotic prophylaxis (increased surgical site infection risk)",
    "Antibiotic prophylaxis >2 hours pre-incision (ineffective)",
    "No VTE prophylaxis post-operatively (risk of DVT/PE)",
    "No WHO Surgical Safety Checklist (increased adverse events)"
  ],

  "fracs_reviews": [
    {
      "reviewer_name": "Dr. Mark Davidson",
      "reviewer_credentials": "FRACS, Staff Specialist General Surgery, Royal Adelaide Hospital",
      "review_date": "2026-03-20",
      "clinical_accuracy": "Yes",
      "difficulty_appropriate": "Yes (Medium)",
      "rag_citations_correct": "Yes (eTG 9.5.1 verified)",
      "australian_context": "Yes (Alvarado score, WHO checklist, VTE prophylaxis all correct)",
      "cultural_safety": "N/A",
      "feedback": "Excellent appendicitis persona. Clinical presentation textbook (pain migration, Rovsing's sign, psoas sign). Alvarado score correctly calculated. WHO Surgical Safety Checklist well-integrated. Consider adding post-op complication (e.g., wound infection) for 'Hard' variant.",
      "approved": true
    },
    {
      "reviewer_name": "Dr. Lisa Chen",
      "reviewer_credentials": "FRACS, Consultant General Surgeon, Flinders Medical Centre",
      "review_date": "2026-03-21",
      "clinical_accuracy": "Yes",
      "difficulty_appropriate": "Yes (Medium - uncomplicated appendicitis)",
      "rag_citations_correct": "Yes",
      "australian_context": "Yes",
      "cultural_safety": "N/A",
      "feedback": "Well-constructed surgical persona. VTE prophylaxis appropriately included (enoxaparin + TED stockings). CT findings realistic (dilated appendix 9mm, fat stranding). Management aligns with RACS guidelines.",
      "approved": true
    }
  ]
}
```

---

## Summary

**MED-006 surgery-expert** creates 27 surgical personas with:
- ✅ FRACS-equivalent expertise (eTG Gastrointestinal 9.1-9.9, Pre/post-op care 7.2-7.3)
- ✅ RAG citations >0.65 confidence
- ✅ 9-step history structure (surgical history)
- ✅ Australian surgical context (WHO Surgical Safety Checklist, VTE prophylaxis, ASA classification)
- ✅ Critical error detection (missed appendicitis, no antibiotic prophylaxis, no VTE prophylaxis)
- ✅ Learning loop (FRACS feedback → improved personas)
- ✅ Zero stereotypes, zero hardcoded credentials

**Next Steps**:
1. Execute PRD_CC_006 to instantiate this agent
2. Create test persona (surgery_001_appendicitis_male_35.json)
3. Submit for FRACS review
4. Scale to 27 personas after validation

---

**Status**: ✅ AGENT SPECIFICATION COMPLETE
**Last Updated**: 2026-03-15
**Version**: 1.0
