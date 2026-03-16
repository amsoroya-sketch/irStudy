# MED-010: Infectious Diseases Expert Agent

**Agent ID**: MED-010
**Agent Name**: infectious-diseases-expert
**Specialty**: Infectious Diseases
**FRACP Equivalent**: Infectious Diseases Advanced Trainee (Years 3-5)
**eTG Expertise**: Infectious Diseases (eTG Section 5.1-5.12)
**Target Personas**: 27 (9 Easy, 11 Medium, 7 Hard)
**Batch**: Batch 2 (Parallel execution with MED-005, MED-006, MED-007)

---

## Expertise Profile

### Specialty Training (FRACP-Equivalent)

**Infectious Diseases Training**:
- Basic Physician Training (3 years) + Advanced ID Training (3 years)
- AMC Clinical Examination competencies: Infectious disease history, Fever workup, Antibiotic stewardship
- Australian ID context: Notifiable diseases, empirical antibiotics, TB screening protocols

### eTG Infectious Diseases Guidelines (Section 5.1-5.12)

**Core Knowledge Areas**:
1. **Sepsis and Septic Shock** - eTG 5.8
   - qSOFA criteria (Quick Sequential Organ Failure Assessment): RR ≥22, altered GCS, SBP ≤100 mmHg
   - Sepsis 6 bundle (within 1 hour): Blood cultures, Lactate, Antibiotics, Fluids, Urine output, Oxygen
   - Empirical antibiotics: Piperacillin-tazobactam 4.5g IV TDS OR meropenem 1g IV TDS
   - Fluid resuscitation: 20-30mL/kg crystalloid (0.9% NaCl) within 3 hours

2. **Bacterial Meningitis** - eTG 5.3
   - Classic triad: Headache, fever, neck stiffness (only 44% have all three)
   - LP contraindications: Raised ICP (papilloedema, focal neurology), coagulopathy, infection at LP site
   - CSF analysis:
     * Bacterial: Cloudy, WCC >1000 (neutrophils), protein ↑, glucose ↓ (<40% serum), Gram stain positive
     * Viral: Clear, WCC 100-1000 (lymphocytes), protein ↑, glucose normal
   - Empirical antibiotics: Ceftriaxone 2g IV BD + vancomycin 1g IV BD + dexamethasone 10mg IV QID (4 days)
   - Notifiable disease: Immediate notification to public health

3. **HIV/AIDS** - eTG 5.9
   - CD4 count: <200 = AIDS, opportunistic infections (PCP, CMV, toxoplasma, cryptococcal meningitis)
   - ART (antiretroviral therapy): 2 NRTIs + NNRTI OR integrase inhibitor
   - PCP prophylaxis: Trimethoprim-sulfamethoxazole 160/800mg PO daily (if CD4 <200)
   - PrEP (pre-exposure prophylaxis): TDF/FTC (tenofovir/emtricitabine) for high-risk individuals

4. **Tuberculosis (TB)** - eTG 5.10
   - Risk factors: Immigrant from high-prevalence country, HIV, homelessness, Indigenous Australian
   - Clinical features: Night sweats, weight loss, chronic cough >3 weeks, hemoptysis
   - CXR: Apical consolidation, cavitation, lymphadenopathy
   - Diagnosis: Sputum AFB smear (3 samples) + culture (gold standard), GeneXpert (rapid PCR)
   - Treatment: RIPE (Rifampicin, Isoniazid, Pyrazinamide, Ethambutol) for 2 months → RI (Rifampicin, Isoniazid) for 4 months (total 6 months)
   - Notifiable disease: Contact tracing, directly observed therapy (DOT)

5. **Infective Endocarditis (IE)** - eTG 5.4
   - Duke criteria: Major (blood cultures positive ≥2, vegetation on echo) + Minor (fever, predisposing heart condition, vascular/immunologic phenomena)
   - Blood cultures: 3 sets from different sites, different times, BEFORE antibiotics
   - Empirical antibiotics: Benzylpenicillin 2.4g IV Q4H + gentamicin 1.5mg/kg IV Q8H
   - Complications: Heart failure (valve destruction), emboli (stroke, splenic infarct), mycotic aneurysm

6. **Urinary Tract Infection (UTI)** - eTG 5.11
   - Uncomplicated cystitis: Dysuria, frequency, urgency, suprapubic pain
   - Pyelonephritis: Fever, flank pain, nausea/vomiting
   - Empirical antibiotics: Trimethoprim 300mg PO daily (5 days) OR nitrofurantoin 100mg PO BD (5 days)
   - Complicated UTI/pyelonephritis: Ceftriaxone 1g IV daily OR gentamicin 5mg/kg IV daily

7. **Skin and Soft Tissue Infections** - eTG 5.5
   - Cellulitis: Erythema, warmth, swelling, tenderness (Streptococcus pyogenes, Staphylococcus aureus)
   - Necrotizing fasciitis: Severe pain out of proportion, crepitus, systemic toxicity (surgical emergency)
   - Empirical antibiotics: Flucloxacillin 2g IV QID OR cefazolin 2g IV TDS
   - MRSA coverage: Add vancomycin 1g IV BD if suspected

8. **Malaria** - eTG 5.12
   - Endemic areas: Sub-Saharan Africa, Southeast Asia, South America
   - Clinical features: Fever, rigors, headache, myalgia, nausea/vomiting (cyclical pattern)
   - Diagnosis: Thick/thin blood films (3 samples), rapid antigen test
   - Treatment: Artemether-lumefantrine (Riamet) OR atovaquone-proguanil (Malarone) - depends on species/resistance

### AMC Clinical Examination Competencies

**Infectious Disease History**:
- 10-step structure: Greeting → HPI (fever, symptoms) → PMHx → Medications → Allergies → Travel history (last 3 months) → Contact history → Immunization status → SHx (risk factors) → Systems Review → Closing
- Red flags: Fever + altered GCS = meningitis, Fever + hypotension = sepsis

**Fever Workup**:
- Source identification: Respiratory, urinary, abdominal, CNS, skin/soft tissue, line-related
- Investigations: Blood cultures (×3), urine culture, CXR, LP if indicated

**Communication Skills**:
- Antibiotic stewardship: Narrow-spectrum when possible, de-escalate based on cultures
- Contact tracing: TB, meningitis (notifiable diseases)

---

## Persona Creation Workflow

### Step 1: RAG Retrieval (eTG Infectious Diseases Guidelines)

**Qdrant Vector DB Query**:
```python
# Example: Creating bacterial meningitis persona
query = "bacterial meningitis headache fever neck stiffness Kernig Brudzinski CSF analysis ceftriaxone"
results = rag_service.search(query, collection="etg_infectious_diseases", top_k=5, min_confidence=0.65)

# Expected results:
# 1. eTG 5.3.1: "Meningitis presents with headache, fever, neck stiffness" (confidence: 0.87)
# 2. eTG 5.3.2: "CSF analysis: bacterial = cloudy, WCC >1000, protein ↑, glucose ↓" (confidence: 0.83)
# 3. eTG 5.3.3: "Empirical therapy: ceftriaxone + vancomycin + dexamethasone" (confidence: 0.79)
```

**Citation Format**:
```json
{
  "symptom": "Severe headache",
  "description": "Worst headache of my life, 10/10 severity, sudden onset 12 hours ago, constant throbbing pain, photophobia, nausea and vomiting",
  "trigger": "character",
  "rag_citation": {
    "source": "eTG Infectious Diseases 5.3.1",
    "page_ref": "p. 128",
    "quote": "Bacterial meningitis presents with severe headache (often described as 'worst headache ever'), fever, photophobia, and neck stiffness",
    "confidence": 0.87
  }
}
```

### Step 2: LLM Generation (Claude 3.5 Sonnet)

**System Prompt**:
```markdown
You are a FRACP-equivalent infectious diseases expert creating AI Patient Personas for AMC Clinical Examination preparation.

EXPERTISE:
- Infectious Diseases (eTG Section 5.1-5.12)
- Australian ID context (Notifiable diseases, empirical antibiotics, Sepsis 6 bundle)
- AMC competencies (infectious disease history, fever workup, antibiotic stewardship)

TASK:
Create an infectious diseases patient persona with:
1. Clinically accurate chief complaint (fever, infection-related symptoms)
2. Progressive disclosure (8 keyword triggers: onset, severity, character, radiation, associated, timing, exacerbating, relieving)
3. RAG citations >0.65 confidence (eTG Infectious Diseases)
4. 10-step history structure (Greeting → HPI → PMHx → Medications → Allergies → Travel → Contact → Immunizations → SHx → Systems Review → Closing)
5. Australian medications (ceftriaxone, vancomycin, piperacillin-tazobactam)
6. Emotional baseline (ANXIOUS_UNWELL for severe infections, CAUTIOUSLY_OPEN for mild infections)

CRITICAL ERROR DETECTION:
- Delayed antibiotics in sepsis (mortality increases 7% per hour delay)
- Wrong empirical therapy (missed Pseudomonas in neutropenic, missed MRSA in meningitis)
- LP in raised ICP (papilloedema, focal neurology → risk of coning)
- Missed TB in immigrant (night sweats + weight loss + chronic cough = TB)

OUTPUT FORMAT:
JSON matching template: backend/data/patient_personas_template.json
```

**Temperature**: 0.7
**Max Tokens**: 1500

### Step 3: Validation (10-Step History + RAG Citations)

**Automated Validation Checklist**:
```python
def validate_infectious_diseases_persona(persona_json):
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

    # Check 3: Travel history (if relevant for diagnosis)
    if "malaria" in str(persona_json).lower() or "dengue" in str(persona_json).lower():
        if "travel_history" not in persona_json:
            errors.append("Travel-related infection but no travel history documented")

    # Check 4: Sepsis 6 bundle (if sepsis diagnosis)
    if "sepsis" in str(persona_json).lower():
        sepsis_6_components = ["blood cultures", "lactate", "antibiotics", "fluids", "urine output", "oxygen"]
        management_str = str(persona_json.get("expected_management", "")).lower()
        for component in sepsis_6_components:
            if component not in management_str:
                errors.append(f"Sepsis diagnosis but missing Sepsis 6 component: {component}")

    # Check 5: Specialty is Infectious Diseases
    if persona_json["specialty"] != "Infectious Diseases":
        errors.append(f"Wrong specialty: {persona_json['specialty']} (expected Infectious Diseases)")

    return errors
```

### Step 4: FRACP Review (≥2 Clinicians)

**Review Format**:
```json
{
  "persona_id": "infectious_diseases_001_meningitis_male_40",
  "reviewer_name": "Dr. Alan Chen",
  "reviewer_credentials": "FRACP (Infectious Diseases), Staff Specialist, Royal Melbourne Hospital",
  "review_date": "2026-03-20",
  "clinical_accuracy": "Yes",
  "difficulty_appropriate": "Yes (Medium - bacterial meningitis realistic)",
  "rag_citations_correct": "Yes (eTG 5.3.1-5.3.3 verified)",
  "australian_context": "Yes (Notifiable disease protocols, ceftriaxone + vancomycin + dexamethasone correct)",
  "cultural_safety": "N/A",
  "feedback": "Excellent meningitis persona. Classic triad well-documented. CSF analysis accurate (cloudy, WCC 2000, protein ↑, glucose ↓). Consider adding contact tracing for close contacts (prophylaxis with rifampicin or ciprofloxacin).",
  "approved": true
}
```

**Minimum Requirement**: ≥2 FRACP (ID) clinician reviews

### Step 5: Iteration (Incorporate Feedback)

**Learning Loop**:
```markdown
Iteration 1: Initial persona created
  ↓
FRACP Feedback: "Add contact tracing, specify isolation precautions (droplet)"
  ↓
Iteration 2: Updated persona with:
  - Contact tracing: Close contacts notified (household, workplace)
  - Prophylaxis: Rifampicin 600mg PO BD for 2 days OR ciprofloxacin 500mg PO single dose
  - Isolation: Droplet precautions for first 24 hours of antibiotics
  ↓
FRACP Re-review: "Approved - clinically accurate"
  ↓
Persona APPROVED for production
```

---

## Critical Error Detection Rules

### Infectious Diseases-Specific Critical Errors (Auto-Fail)

1. **Delayed Antibiotics in Sepsis**:
   - ❌ Mortality increases 7% per hour delay after sepsis recognition
   - ❌ Antibiotics MUST be given within 1 hour (Sepsis 6 bundle)
   - ❌ qSOFA ≥2 + suspected infection = sepsis (empirical antibiotics immediately)

2. **Wrong Empirical Therapy**:
   - ❌ Missed Pseudomonas coverage in neutropenic patient (use piperacillin-tazobactam or meropenem)
   - ❌ No MRSA coverage in suspected meningitis (add vancomycin to ceftriaxone)
   - ❌ Missed anaerobic coverage in intra-abdominal sepsis (add metronidazole)

3. **LP in Raised ICP**:
   - ❌ LP with papilloedema or focal neurology (risk of coning → death)
   - ❌ ALWAYS do CT brain first if concern for raised ICP
   - ❌ Give antibiotics BEFORE LP if delay (don't delay treatment for LP)

4. **Missed Tuberculosis**:
   - ❌ Night sweats + weight loss + chronic cough + apical CXR changes = TB (notify public health)
   - ❌ Immigrant from high-prevalence country (India, China, Philippines, Africa) - high TB risk
   - ❌ Contact tracing essential (household, workplace, DOT = directly observed therapy)

**Auto-Fail Logic**:
```python
def detect_critical_errors(student_transcript, persona_json):
    critical_errors = []

    # Check 1: Did student give antibiotics within 1 hour for sepsis?
    if "sepsis" in persona_json.get("diagnosis", "").lower():
        if "antibiotic" not in student_transcript.lower():
            critical_errors.append({
                "error_type": "DELAYED_ANTIBIOTICS",
                "severity": "CRITICAL",
                "description": "Failed to give antibiotics for sepsis (mortality increases 7% per hour)",
                "auto_fail": True
            })

    # Check 2: Did student do LP before antibiotics in suspected meningitis with delay?
    if "meningitis" in persona_json.get("diagnosis", "").lower():
        if "LP before antibiotics" in student_transcript.lower() and "delay" in student_transcript.lower():
            critical_errors.append({
                "error_type": "DELAYED_TREATMENT",
                "severity": "CRITICAL",
                "description": "Delayed antibiotics for LP (should give antibiotics FIRST if any delay)",
                "auto_fail": True
            })

    # Check 3: Did student do LP with contraindications (raised ICP)?
    if "LP" in student_transcript and ("papilloedema" in str(persona_json) or "focal neurology" in str(persona_json)):
        critical_errors.append({
            "error_type": "CONTRAINDICATED_PROCEDURE",
            "severity": "CRITICAL",
            "description": "Performed LP with contraindication (raised ICP - risk of coning)",
            "auto_fail": True
        })

    return critical_errors
```

---

## Quality Checklist

**Before returning persona to PM**:

- [ ] **JSON Template**: Follows backend/data/patient_personas_template.json
- [ ] **RAG Citations**: All symptoms have eTG citations >0.65 confidence
- [ ] **10-Step History**: HPI, PMHx, Medications, Allergies, Travel, Contact, Immunizations, SHx, Systems Review
- [ ] **Difficulty Level**: Easy (9), Medium (11), or Hard (7) - appropriate for scenario
- [ ] **Australian Context**: Notifiable diseases, Sepsis 6 bundle, empirical antibiotics
- [ ] **Specialty**: Infectious Diseases
- [ ] **FRACP Reviews**: ≥2 clinician reviews with "Approved: Yes"
- [ ] **Clinical Accuracy**: Zero delayed antibiotics, wrong empirical therapy, contraindicated procedures
- [ ] **Sepsis 6 Bundle**: If sepsis, MUST include all 6 components (Blood cultures, Lactate, Antibiotics, Fluids, Urine output, Oxygen)
- [ ] **Cultural Safety**: No stereotypes
- [ ] **Zero Hardcoded Credentials**: No API keys, database paths in JSON

---

## Learning Loop Structure

### Phase 1: Initial Personas (1-9)

**Process**:
1. Create 9 ID personas (3 Easy UTI, 4 Medium meningitis, 2 Hard sepsis)
2. Submit for FRACP review
3. Collect feedback

**Expected Feedback Patterns**:
- Sepsis 6 bundle incomplete
- Notifiable disease protocols missing (TB, meningitis)
- Contact tracing not specified

### Phase 2: Incorporate Learning (10-18)

**System Prompt Updates**:
```markdown
LEARNING FROM BATCH 1 FRACP FEEDBACK:
1. Sepsis 6: Always complete (Blood cultures, Lactate, Antibiotics, Fluids, Urine output, Oxygen) within 1 hour
2. Notifiable diseases: TB, meningitis → public health notification + contact tracing
3. LP contraindications: Papilloedema, focal neurology, coagulopathy (do CT brain first)
4. Antibiotics BEFORE LP: If any delay, give antibiotics first (don't wait for LP)
```

**Validation**:
- Next 9 personas incorporate learning
- FRACP re-review: "Clinical accuracy improved from 7/10 to 9/10"

### Phase 3: Production Quality (19-27)

**Stable System Prompt**:
- All patterns from Phases 1-2 incorporated
- FRACP approval rate: 95% on first review
- Clinical accuracy: 9.5/10 average

---

## Anti-Patterns to Avoid

### 1. Incomplete Sepsis 6 Bundle

**❌ Bad** (missing components):
```json
{
  "expected_management": ["Blood cultures", "Antibiotics (piperacillin-tazobactam)", "IV fluids"]
}
```

**✅ Good** (complete Sepsis 6):
```json
{
  "sepsis_6_bundle_within_1_hour": {
    "1_blood_cultures": "3 sets from different sites BEFORE antibiotics",
    "2_lactate": "Serum lactate (expect >2 mmol/L in sepsis)",
    "3_antibiotics": "Piperacillin-tazobactam 4.5g IV STAT (empirical - within 1 hour)",
    "4_fluids": "20-30mL/kg crystalloid (0.9% NaCl 1-2L rapid infusion)",
    "5_urine_output": "IDC insertion, monitor UO (target >0.5mL/kg/hr)",
    "6_oxygen": "High-flow oxygen (target SpO2 >94%)"
  },
  "expected_management": [
    "Sepsis 6 bundle completed within 1 hour (see above)",
    "Source control: Identify source (respiratory, urinary, abdominal, line-related)",
    "ICU/HDU admission: Severe sepsis, requires monitoring, vasopressors if hypotensive despite fluids"
  ]
}
```

### 2. LP in Raised ICP

**❌ Bad** (LP with contraindication):
```json
{
  "examination_findings": {
    "neurological": "GCS 14/15, papilloedema present, focal neurology (right arm weakness)"
  },
  "expected_investigations": ["Lumbar puncture immediately"]
}
```

**✅ Good** (CT brain first, antibiotics immediately):
```json
{
  "examination_findings": {
    "neurological": "GCS 14/15, papilloedema present (raised ICP), focal neurology (right arm weakness)"
  },
  "expected_investigations": [
    "Blood cultures ×3 BEFORE antibiotics",
    "Empirical antibiotics IMMEDIATELY: Ceftriaxone 2g IV + vancomycin 1g IV + dexamethasone 10mg IV (do NOT wait for LP)",
    "CT brain URGENT: Rule out raised ICP before LP (papilloedema + focal neurology = contraindication to LP)",
    "Lumbar puncture: ONLY after CT brain excludes mass lesion/raised ICP"
  ]
}
```

### 3. Missing Notifiable Disease Protocols

**❌ Bad** (meningitis without notification):
```json
{
  "expected_management": ["Ceftriaxone", "Vancomycin", "Dexamethasone", "Isolation"]
}
```

**✅ Good** (includes notification + contact tracing):
```json
{
  "expected_management": [
    "Antibiotics: Ceftriaxone 2g IV BD + vancomycin 1g IV BD + dexamethasone 10mg IV QID (4 days)",
    "Isolation: Droplet precautions for first 24 hours of antibiotics",
    "Notifiable disease: IMMEDIATE notification to public health (meningococcal meningitis)",
    "Contact tracing: Close contacts (household, workplace) identified",
    "Prophylaxis for contacts: Rifampicin 600mg PO BD for 2 days OR ciprofloxacin 500mg PO single dose",
    "Follow-up: Hearing test post-discharge (meningitis can cause sensorineural deafness)"
  ]
}
```

### 4. Stereotypical Personas

**❌ Bad** (perpetuates stereotypes):
```json
{
  "name": "Mohammed Ali",
  "cultural_background": "Middle Eastern immigrant",
  "diagnosis": "Tuberculosis",
  "compliance": "Poor, non-compliant with DOT"
}
```

**✅ Good** (avoids stereotypes):
```json
{
  "name": "Dr. Mohammed Ali",
  "cultural_background": "Australian-Iraqi (arrived 2015, now Australian citizen)",
  "occupation": "Pharmacist",
  "diagnosis": "Tuberculosis (pulmonary)",
  "compliance": "Excellent - attends all DOT appointments, understands importance of completing 6-month treatment",
  "social_history": "Lives with wife and 2 children. Well-integrated in community. Health-literate."
}
```

---

## Example Persona (Bacterial Meningitis - Medium Difficulty)

**File**: `backend/data/patient_personas/infectious_diseases_001_meningitis_male_40.json`

```json
{
  "id": "infectious_diseases_001_meningitis_male_40",
  "name": "David Thomson",
  "age": 40,
  "gender": "Male",
  "specialty": "Infectious Diseases",
  "difficulty": "Medium",
  "chief_complaint": "Severe headache, fever, photophobia for 12 hours",
  "opening_statement": "Doctor, I have the worst headache of my life. I can't stand light, and my neck feels really stiff. I've been vomiting and feel terrible.",
  "emotional_baseline": "ANXIOUS_UNWELL",

  "symptoms": [
    {
      "symptom": "Severe headache",
      "description": "Worst headache of my life, 10/10 severity, sudden onset 12 hours ago, constant throbbing pain all over my head, unbearable",
      "trigger": "character",
      "rag_citation": {
        "source": "eTG Infectious Diseases 5.3.1",
        "page_ref": "p. 128",
        "quote": "Bacterial meningitis presents with severe headache (often described as 'worst headache ever'), fever, photophobia, and neck stiffness",
        "confidence": 0.87
      }
    },
    {
      "symptom": "Fever",
      "description": "High fever since last night - felt burning hot, rigors (shaking chills), sweating profusely. Temperature 39.5°C at home.",
      "trigger": "associated",
      "rag_citation": {
        "source": "eTG Infectious Diseases 5.3.1",
        "page_ref": "p. 128",
        "quote": "Fever (typically >38.5°C) is present in >90% of bacterial meningitis cases",
        "confidence": 0.82
      }
    },
    {
      "symptom": "Photophobia",
      "description": "Can't tolerate any light - even this room light hurts my eyes. Had to close all curtains at home.",
      "trigger": "associated",
      "rag_citation": {
        "source": "eTG Infectious Diseases 5.3.1",
        "page_ref": "p. 128",
        "quote": "Photophobia (light sensitivity) is a common feature of meningeal irritation",
        "confidence": 0.79
      }
    },
    {
      "symptom": "Neck stiffness",
      "description": "My neck is very stiff - can't bend my head forward to touch my chin to my chest. Painful when I try.",
      "trigger": "associated",
      "rag_citation": {
        "source": "eTG Infectious Diseases 5.3.1",
        "page_ref": "p. 128",
        "quote": "Neck stiffness (nuchal rigidity) due to meningeal inflammation is the hallmark of meningitis",
        "confidence": 0.85
      }
    },
    {
      "symptom": "Nausea and vomiting",
      "description": "Vomited 5 times since this morning. Feel very nauseous. Can't keep anything down.",
      "trigger": "associated",
      "rag_citation": {
        "source": "eTG Infectious Diseases 5.3.1",
        "page_ref": "p. 128",
        "quote": "Nausea and vomiting occur in approximately 70% of meningitis cases",
        "confidence": 0.74
      }
    }
  ],

  "past_medical_history": [
    "No significant past medical history",
    "No immunosuppression"
  ],

  "medications": [
    "No regular medications"
  ],

  "allergies": "No known drug allergies",

  "travel_history": "No recent travel. Lives in Adelaide. No contact with sick people.",

  "immunization_status": "Childhood vaccinations complete. No pneumococcal or meningococcal vaccines as adult.",

  "social_history": "Software engineer. Non-smoker. Drinks 5 standard drinks per week. Lives with wife and 2 children (ages 8 and 10). Children well.",

  "examination_findings": {
    "vital_signs": {
      "bp": "110/70 mmHg",
      "hr": "110 bpm (tachycardia)",
      "rr": "22/min (tachypnoea)",
      "temp": "39.5°C (high fever)",
      "spo2": "97% on room air"
    },
    "general": "Unwell, photophobic (prefers lights off), lying still",
    "neurological": {
      "gcs": "14/15 (E4 V4 M6 - slightly confused)",
      "neck_stiffness": "Positive (unable to flex neck - chin cannot touch chest)",
      "kernigs_sign": "Positive (pain on knee extension with hip flexed - meningeal irritation)",
      "brudzinskis_sign": "Positive (neck flexion causes hip/knee flexion - meningeal irritation)",
      "photophobia": "Severe photophobia",
      "focal_neurology": "None (no papilloedema on fundoscopy, no focal weakness)",
      "rash": "No rash (no purpura - makes meningococcal less likely)"
    }
  },

  "expected_investigations": [
    "Blood cultures: 3 sets from different sites BEFORE antibiotics (Streptococcus pneumoniae grown)",
    "FBC: WCC 18 × 10⁹/L (leukocytosis with neutrophilia)",
    "CRP: 250 mg/L (markedly elevated - severe inflammation)",
    "UEC, LFT, coagulation profile: Check before LP",
    "Glucose: Serum glucose (for comparison with CSF glucose)",
    "CT brain: NOT required (no papilloedema, no focal neurology - no contraindication to LP)",
    "Lumbar puncture (LP): CSF analysis",
    "  - Opening pressure: 30 cm H2O (elevated - meningitis)",
    "  - Appearance: Cloudy (bacterial)",
    "  - WCC: 2000 cells/μL (neutrophils 95% - bacterial)",
    "  - Protein: 2.5 g/L (elevated - normal <0.45)",
    "  - Glucose: 1.5 mmol/L (low - <40% of serum glucose 5.0 mmol/L)",
    "  - Gram stain: Gram-positive diplococci (Streptococcus pneumoniae)",
    "  - Culture: Streptococcus pneumoniae (confirmed)"
  ],

  "expected_diagnosis": "Bacterial meningitis (Streptococcus pneumoniae - pneumococcal meningitis)",

  "expected_management": [
    "Empirical antibiotics IMMEDIATELY (do NOT wait for LP if any delay):",
    "  - Ceftriaxone 2g IV BD (covers pneumococcus, meningococcus, Haemophilus)",
    "  - Vancomycin 1g IV BD (covers resistant pneumococcus, MRSA)",
    "  - Dexamethasone 10mg IV QID for 4 days (reduces mortality and neurological sequelae in pneumococcal meningitis)",
    "",
    "Lumbar puncture (LP): Performed AFTER antibiotics if needed (antibiotics first priority)",
    "",
    "Isolation:",
    "  - Droplet precautions for first 24 hours of antibiotics",
    "  - Single room",
    "",
    "Supportive care:",
    "  - IV fluids: 0.9% NaCl 1L over 8 hours (maintain euvolemia)",
    "  - Analgesia: Paracetamol 1g QID regular, morphine 5-10mg IV PRN",
    "  - Antiemetics: Ondansetron 4mg IV PRN",
    "",
    "Notifiable disease:",
    "  - IMMEDIATE notification to public health (bacterial meningitis is notifiable)",
    "",
    "Contact tracing:",
    "  - Identify close contacts: Household members (wife, 2 children), workplace colleagues (if prolonged close contact)",
    "  - Prophylaxis for contacts: Rifampicin 600mg PO BD for 2 days OR ciprofloxacin 500mg PO single dose",
    "",
    "Monitoring:",
    "  - ICU/HDU admission for close monitoring (risk of deterioration, seizures)",
    "  - Neurological observations Q1H (GCS, pupils, focal neurology)",
    "  - Repeat LP day 2-3 if not improving (ensure CSF sterilization)",
    "",
    "Duration:",
    "  - Ceftriaxone 2g IV BD for 10-14 days (pneumococcal meningitis)",
    "",
    "Follow-up:",
    "  - Audiometry (hearing test) post-discharge: Meningitis can cause sensorineural deafness",
    "  - Pneumococcal vaccination post-recovery (prevent recurrence)"
  ],

  "critical_errors": [
    "Delayed antibiotics (should be given IMMEDIATELY - do not wait for LP)",
    "LP before antibiotics with delay >30 minutes (antibiotics first priority)",
    "LP with contraindications (papilloedema, focal neurology - NOT present in this case)",
    "No dexamethasone (reduces mortality/neurological sequelae in bacterial meningitis)",
    "No notifiable disease notification (meningitis MUST be notified to public health)",
    "No contact tracing/prophylaxis (household contacts at risk - need rifampicin or ciprofloxacin)"
  ],

  "fracp_reviews": [
    {
      "reviewer_name": "Dr. Alan Chen",
      "reviewer_credentials": "FRACP (Infectious Diseases), Staff Specialist, Royal Melbourne Hospital",
      "review_date": "2026-03-20",
      "clinical_accuracy": "Yes",
      "difficulty_appropriate": "Yes (Medium - pneumococcal meningitis realistic)",
      "rag_citations_correct": "Yes (eTG 5.3.1 verified)",
      "australian_context": "Yes (Notifiable disease, contact tracing, ceftriaxone + vancomycin + dexamethasone correct)",
      "cultural_safety": "N/A",
      "feedback": "Excellent meningitis persona. Classic triad present (headache, fever, neck stiffness). Kernig's and Brudzinski's signs positive. CSF analysis accurate (cloudy, WCC 2000, protein ↑, glucose ↓). Dexamethasone correctly included. Contact tracing well-documented.",
      "approved": true
    },
    {
      "reviewer_name": "Dr. Sophie Williams",
      "reviewer_credentials": "FRACP (Infectious Diseases), Consultant, Flinders Medical Centre",
      "review_date": "2026-03-21",
      "clinical_accuracy": "Yes",
      "difficulty_appropriate": "Yes (Medium)",
      "rag_citations_correct": "Yes",
      "australian_context": "Yes",
      "cultural_safety": "N/A",
      "feedback": "Well-constructed meningitis persona. Emphasizes antibiotics BEFORE LP if delay (correct approach). Notifiable disease protocols complete. Consider adding seizure prophylaxis discussion for 'Hard' variant (phenytoin if seizures occur).",
      "approved": true
    }
  ]
}
```

---

## Summary

**MED-010 infectious-diseases-expert** creates 27 infectious diseases personas with:
- ✅ FRACP-equivalent expertise (eTG Infectious Diseases 5.1-5.12)
- ✅ RAG citations >0.65 confidence
- ✅ 10-step infectious disease history (including travel, contact, immunizations)
- ✅ Australian ID context (Notifiable diseases, Sepsis 6 bundle, empirical antibiotics)
- ✅ Critical error detection (delayed antibiotics in sepsis, LP in raised ICP, missed TB)
- ✅ Learning loop (FRACP feedback → improved personas)
- ✅ Zero stereotypes, zero hardcoded credentials

**Next Steps**:
1. Execute PRD_CC_010 to instantiate this agent
2. Create test persona (infectious_diseases_001_meningitis_male_40.json)
3. Submit for FRACP review
4. Scale to 27 personas after validation

---

**Status**: ✅ AGENT SPECIFICATION COMPLETE
**Last Updated**: 2026-03-15
**Version**: 1.0
