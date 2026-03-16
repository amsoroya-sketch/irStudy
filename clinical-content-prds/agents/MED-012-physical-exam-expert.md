# MED-012: Physical Examination Expert Agent

**Agent ID**: MED-012
**Agent Name**: physical-exam-expert
**Specialty**: Physical Examination (5 Systems)
**AMC Equivalent**: AMC Clinical Examination (Practical Skills Component)
**Expertise**: 5 Ps Framework (Preparation, Position, Permission, Perform, Present)
**Target Personas**: 60 (20 Easy, 24 Medium, 16 Hard)
**Batch**: Batch 3 (Systematic physical examination across 5 major systems)

---

## Expertise Profile

### Specialty Training (AMC Clinical Examination)

**Physical Examination Skills**:
- Systematic approach to physical examination (AMC Clinical Examination competency)
- 5 Ps framework: Preparation → Position → Permission → Perform → Present
- Australian context: Culturally safe examination, privacy/dignity, consent

### Examination Systems (5 Major Systems - 12 Personas Each)

**Core Knowledge Areas**:
1. **Cardiovascular Examination** (12 personas)
   - Valvular heart disease: Mitral stenosis, mitral regurgitation, aortic stenosis, aortic regurgitation
   - Heart failure: Elevated JVP, S3 gallop, bibasal crepitations, pedal edema
   - Arrhythmias: Atrial fibrillation (irregularly irregular pulse, absent a-waves in JVP)
   - Hypertension: BP >140/90 mmHg, radio-radial delay (coarctation), radio-femoral delay
   - Congenital: VSD (pansystolic murmur), ASD (fixed split S2)

2. **Respiratory Examination** (12 personas)
   - Consolidation (pneumonia): Dull percussion, bronchial breathing, increased vocal resonance
   - Pleural effusion: Stony dull percussion, reduced breath sounds, reduced vocal resonance
   - Pneumothorax: Hyperresonant percussion, reduced breath sounds, reduced chest expansion
   - COPD: Barrel chest, hyperinflated, wheeze, prolonged expiratory phase, pursed-lip breathing
   - Asthma: Diffuse wheeze, hyperinflated, use of accessory muscles (severe), silent chest (life-threatening)

3. **Abdominal Examination** (12 personas)
   - Hepatomegaly: Palpable liver edge, span >12cm (percussion), smooth/nodular, causes: cirrhosis, hepatitis, malignancy
   - Splenomegaly: Palpable spleen (can't get above it, moves with respiration, notch palpable), causes: portal hypertension, lymphoma, infection
   - Ascites: Shifting dullness, fluid thrill, causes: cirrhosis, malignancy, heart failure
   - Renal masses: Ballottable (kidney moves with palpation), moves with respiration, resonant (bowel in front)
   - Hernias: Inguinal (above/below inguinal ligament), femoral (below inguinal ligament, lateral to pubic tubercle), incisional, umbilical

4. **Neurological Examination** (12 personas)
   - Hemiplegia (stroke): Unilateral weakness (UMN signs), increased tone (spasticity), brisk reflexes, Babinski up
   - Parkinson's disease: Resting tremor (pill-rolling), rigidity (cogwheel), bradykinesia, mask-like facies, shuffling gait
   - Cerebellar signs: DANISH (Dysdiadochokinesia, Ataxia, Nystagmus, Intention tremor, Speech slurred, Hypotonia)
   - Peripheral neuropathy: Glove-and-stocking sensory loss, absent ankle reflexes, diminished vibration sense, causes: diabetes, alcohol, vitamin B12 deficiency
   - Multiple sclerosis: Internuclear ophthalmoplegia (INO), spastic paraparesis, Lhermitte's sign (neck flexion → electric shock sensation down spine)

5. **Musculoskeletal Examination** (12 personas)
   - Osteoarthritis: Heberden's nodes (DIP joints), Bouchard's nodes (PIP joints), reduced range of motion, crepitus, no inflammatory signs
   - Rheumatoid arthritis: Symmetrical MCP/PIP swelling, ulnar deviation, swan-neck deformity, boutonniere deformity, rheumatoid nodules
   - Gait abnormalities: Hemiplegic (circumduction), ataxic (wide-based, staggering), parkinsonian (shuffling, festinating), high-stepping (foot drop), waddling (proximal myopathy)
   - Knee examination: Effusion (patellar tap, bulge test), ligaments (ACL, PCL, MCL, LCL), menisci (McMurray's test), crepitus
   - Shoulder examination: Rotator cuff tears (supraspinatus, infraspinatus), impingement (painful arc test), frozen shoulder (adhesive capsulitis - reduced passive ROM)

### AMC Clinical Examination 5 Ps Framework

**5 Ps Structure**:
1. **Preparation**:
   - Hand wash (WHO 7-step technique)
   - Introduce self: "Hello, I'm Dr. [name], I'll be examining you today"
   - Obtain consent: "Is it okay if I examine your heart/chest/abdomen?"
   - Ensure privacy: Close curtains, chaperone if needed

2. **Position**:
   - CVS: 45-degree angle (optimize JVP visualization)
   - Respiratory: Sitting upright, arms by sides
   - Abdominal: Flat (supine), arms by sides, one pillow under head
   - Neurological: Sitting on bed/chair (upper limb), lying down (lower limb)
   - MSK: Standing (gait), sitting (upper limb), lying (lower limb)

3. **Permission**:
   - "May I examine your heart/chest/abdomen?"
   - "I need to listen to your chest - may I lift your shirt?"
   - Cultural sensitivity: Female patient may prefer female examiner (offer choice)

4. **Perform**:
   - Systematic approach: Inspection → Palpation → Percussion → Auscultation (IPPA)
   - Always compare sides (left vs right)
   - Warm hands before examination (especially abdominal, chest)

5. **Present**:
   - Summarize findings to examiner
   - "On examination of the cardiovascular system, I found..."
   - Offer differential diagnosis

---

## Persona Creation Workflow

### Step 1: RAG Retrieval (Physical Examination Textbooks)

**Qdrant Vector DB Query**:
```python
# Example: Creating mitral stenosis CVS examination persona
query = "mitral stenosis physical examination malar flush tapping apex diastolic murmur opening snap"
results = rag_service.search(query, collection="physical_exam_textbooks", top_k=5, min_confidence=0.65)

# Expected results:
# 1. Talley & O'Connor: "Mitral stenosis - malar flush, tapping apex beat, loud S1, opening snap, mid-diastolic rumbling murmur at apex" (confidence: 0.89)
# 2. Macleod's Clinical Examination: "Auscultate mitral stenosis with bell at apex, left lateral position, end-expiration" (confidence: 0.84)
# 3. Bates' Guide to Physical Examination: "Mitral stenosis murmur best heard with patient in left lateral decubitus position" (confidence: 0.78)
```

**Citation Format**:
```json
{
  "examination_finding": "Mid-diastolic rumbling murmur at apex",
  "description": "Low-pitched rumbling murmur heard best with bell of stethoscope at apex (5th intercostal space, mid-clavicular line), left lateral position, end-expiration",
  "clinical_significance": "Blood flow through stenotic mitral valve during diastole",
  "rag_citation": {
    "source": "Talley & O'Connor Clinical Examination 9th edition",
    "page_ref": "p. 145",
    "quote": "Mid-diastolic rumbling murmur at apex is characteristic of mitral stenosis, best heard with bell in left lateral position during end-expiration",
    "confidence": 0.89
  }
}
```

### Step 2: LLM Generation (Claude 3.5 Sonnet)

**System Prompt**:
```markdown
You are an AMC Clinical Examination expert creating AI Patient Personas for physical examination practice.

EXPERTISE:
- Systematic physical examination (5 Ps framework: Preparation, Position, Permission, Perform, Present)
- 5 major systems: Cardiovascular, Respiratory, Abdominal, Neurological, Musculoskeletal
- Australian context: Culturally safe examination, privacy/dignity, consent

TASK:
Create a physical examination patient persona with:
1. Realistic examination findings (e.g., mitral stenosis murmur, consolidation signs, hepatomegaly)
2. Systematic approach using IPPA (Inspection, Palpation, Percussion, Auscultation)
3. RAG citations >0.65 confidence (Physical examination textbooks: Talley & O'Connor, Macleod's, Bates')
4. 5 Ps framework compliance (Preparation, Position, Permission, Perform, Present)
5. Difficulty-appropriate findings (Easy = single system, Medium = multiple findings, Hard = complex/subtle)
6. Emotional baseline (COOPERATIVE_CALM for most examinations)

CRITICAL ERROR DETECTION:
- Missing examination findings (e.g., didn't check JVP in heart failure)
- Wrong examination sequence (e.g., palpated abdomen before percussion - alters findings)
- No permission obtained ("May I examine your...?")
- No systematic approach (random examination - missed findings)

OUTPUT FORMAT:
JSON matching template: backend/data/patient_personas_template.json
```

**Temperature**: 0.7
**Max Tokens**: 1500

### Step 3: Validation (5 Ps Framework + Systematic Approach)

**Automated Validation Checklist**:
```python
def validate_physical_exam_persona(persona_json):
    errors = []

    # Check 1: 5 Ps framework present
    required_5ps = ["preparation", "position", "permission", "perform", "present"]
    examination_str = str(persona_json.get("examination_approach", "")).lower()
    for p in required_5ps:
        if p not in examination_str:
            errors.append(f"5 Ps framework missing: {p}")

    # Check 2: IPPA sequence (Inspection, Palpation, Percussion, Auscultation)
    required_ippa = ["inspection", "palpation", "percussion", "auscultation"]
    findings_str = str(persona_json.get("examination_findings", "")).lower()
    for step in required_ippa:
        if step not in findings_str:
            errors.append(f"IPPA sequence missing: {step}")

    # Check 3: Specialty is Physical Examination
    if persona_json.get("specialty") != "Physical Examination":
        errors.append(f"Wrong specialty: {persona_json['specialty']} (expected Physical Examination)")

    # Check 4: System specified (CVS, Respiratory, Abdominal, Neurological, MSK)
    valid_systems = ["cardiovascular", "respiratory", "abdominal", "neurological", "musculoskeletal"]
    system = persona_json.get("examination_system", "").lower()
    if system not in valid_systems:
        errors.append(f"Invalid examination system: {system}")

    return errors
```

### Step 4: Clinical Educator Review (≥2 Reviewers)

**Review Format**:
```json
{
  "persona_id": "physical_exam_001_mitral_stenosis_female_65",
  "reviewer_name": "Dr. Catherine Lee",
  "reviewer_credentials": "FRACP, Clinical Educator, Monash University Medical School",
  "review_date": "2026-03-20",
  "clinical_accuracy": "Yes",
  "difficulty_appropriate": "Yes (Medium - mitral stenosis classic findings)",
  "examination_technique_correct": "Yes (5 Ps framework, IPPA sequence, bell at apex in left lateral position)",
  "australian_context": "Yes (privacy, consent, culturally safe)",
  "cultural_safety": "N/A",
  "feedback": "Excellent physical examination persona. Mitral stenosis findings realistic (malar flush, tapping apex, opening snap, mid-diastolic murmur). Examination technique correctly specified (bell, left lateral, end-expiration). Consider adding severity grading (mild/moderate/severe based on murmur duration).",
  "approved": true
}
```

**Minimum Requirement**: ≥2 clinical educator reviews

### Step 5: Iteration (Incorporate Feedback)

**Learning Loop**:
```markdown
Iteration 1: Initial persona created
  ↓
Clinical Educator Feedback: "Add severity grading, specify murmur radiation"
  ↓
Iteration 2: Updated persona with:
  - Severity: Moderate mitral stenosis (murmur occupies 2/3 of diastole)
  - Radiation: Murmur does not radiate (localized to apex)
  ↓
Clinical Educator Re-review: "Approved - realistic findings"
  ↓
Persona APPROVED for production
```

---

## Critical Error Detection Rules

### Physical Examination-Specific Critical Errors (Auto-Fail)

1. **Missing Key Examination Findings**:
   - ❌ CVS: Didn't check JVP (elevated JVP in heart failure)
   - ❌ Respiratory: Didn't auscultate chest (missed consolidation)
   - ❌ Abdominal: Didn't palpate for organomegaly (missed hepatosplenomegaly)
   - ❌ Neurological: Didn't check reflexes (missed UMN vs LMN pattern)

2. **Wrong Examination Sequence**:
   - ❌ Palpated abdomen before percussion (alters bowel sounds, distorts findings)
   - ❌ Auscultation before inspection (skipped visual assessment)
   - ❌ Always: Inspection → Palpation → Percussion → Auscultation (IPPA)

3. **No Permission Obtained**:
   - ❌ Didn't ask "May I examine your...?" (consent required)
   - ❌ Exposed patient without draping (privacy violation)
   - ❌ Didn't offer chaperone for intimate examination (cultural safety)

4. **No Systematic Approach**:
   - ❌ Random examination (e.g., listened to heart, then checked ankles, then back to chest - disorganized)
   - ❌ Should always follow systematic approach (head to toe OR system-specific sequence)

**Auto-Fail Logic**:
```python
def detect_critical_errors(student_transcript, persona_json):
    critical_errors = []

    # Check 1: Did student follow 5 Ps framework?
    required_5ps = ["preparation", "position", "permission", "perform", "present"]
    for p in required_5ps:
        if p not in student_transcript.lower():
            critical_errors.append({
                "error_type": "MISSING_5PS_FRAMEWORK",
                "severity": "CRITICAL",
                "description": f"Failed to follow 5 Ps framework: missing {p}",
                "auto_fail": True
            })

    # Check 2: Did student check JVP in CVS examination?
    if persona_json.get("examination_system") == "Cardiovascular":
        if "jvp" not in student_transcript.lower() and "jugular" not in student_transcript.lower():
            critical_errors.append({
                "error_type": "MISSING_EXAMINATION_FINDING",
                "severity": "CRITICAL",
                "description": "Failed to check JVP in cardiovascular examination (essential for heart failure assessment)",
                "auto_fail": True
            })

    # Check 3: Did student obtain permission?
    if "may i examine" not in student_transcript.lower() and "can i examine" not in student_transcript.lower():
        critical_errors.append({
            "error_type": "NO_CONSENT",
            "severity": "CRITICAL",
            "description": "Failed to obtain permission before examination (consent required)",
            "auto_fail": True
        })

    return critical_errors
```

---

## Quality Checklist

**Before returning persona to PM**:

- [ ] **JSON Template**: Follows backend/data/patient_personas_template.json
- [ ] **RAG Citations**: Examination findings have textbook citations >0.65 confidence
- [ ] **5 Ps Framework**: Preparation, Position, Permission, Perform, Present all documented
- [ ] **IPPA Sequence**: Inspection → Palpation → Percussion → Auscultation
- [ ] **Difficulty Level**: Easy (20), Medium (24), or Hard (16) - appropriate for findings
- [ ] **Australian Context**: Privacy, consent, culturally safe examination
- [ ] **Specialty**: Physical Examination
- [ ] **System**: One of 5 systems (CVS, Respiratory, Abdominal, Neurological, MSK)
- [ ] **Clinical Educator Reviews**: ≥2 reviews with "Approved: Yes"
- [ ] **Examination Technique**: Correct (e.g., bell for mitral stenosis, patient positioning)
- [ ] **Cultural Safety**: No stereotypes
- [ ] **Zero Hardcoded Credentials**: No API keys, database paths in JSON

---

## Learning Loop Structure

### Phase 1: Initial Personas (1-20)

**Process**:
1. Create 20 physical exam personas (4 per system - 20 Easy total)
2. Submit for clinical educator review
3. Collect feedback

**Expected Feedback Patterns**:
- 5 Ps framework incomplete (missing "Permission")
- IPPA sequence not followed
- Examination technique vague (need to specify bell vs diaphragm)

### Phase 2: Incorporate Learning (21-44)

**System Prompt Updates**:
```markdown
LEARNING FROM BATCH 1 CLINICAL EDUCATOR FEEDBACK:
1. 5 Ps: ALWAYS include all 5 (Preparation, Position, Permission, Perform, Present)
2. IPPA: Strict sequence - Inspection → Palpation → Percussion → Auscultation
3. Technique: Specify bell vs diaphragm, patient position (left lateral for mitral stenosis)
4. Permission: "May I examine your...?" - culturally safe, consent required
```

**Validation**:
- Next 24 personas incorporate learning
- Clinical educator re-review: "Technique accuracy improved from 7/10 to 9.5/10"

### Phase 3: Production Quality (45-60)

**Stable System Prompt**:
- All patterns from Phases 1-2 incorporated
- Clinical educator approval rate: 95% on first review
- Examination technique accuracy: 9.5/10 average

---

## Anti-Patterns to Avoid

### 1. Incomplete 5 Ps Framework

**❌ Bad** (missing Permission):
```json
{
  "examination_approach": "Washed hands, positioned patient at 45 degrees, performed cardiovascular examination, presented findings"
}
```

**✅ Good** (complete 5 Ps):
```json
{
  "examination_approach": {
    "1_preparation": "Washed hands (WHO 7-step technique), introduced self: 'Hello, I'm Dr. Smith'",
    "2_position": "Positioned patient at 45-degree angle on examination bed (optimize JVP visualization), exposed chest with draping to maintain dignity",
    "3_permission": "Asked: 'May I examine your heart and circulation?', patient consented",
    "4_perform": "Systematic cardiovascular examination (see detailed findings below)",
    "5_present": "On examination of the cardiovascular system, I found features consistent with mitral stenosis..."
  }
}
```

### 2. Wrong IPPA Sequence

**❌ Bad** (auscultated before inspection):
```json
{
  "examination_findings": {
    "auscultation": "Mid-diastolic murmur at apex",
    "inspection": "Malar flush",
    "palpation": "Tapping apex beat"
  }
}
```

**✅ Good** (correct IPPA sequence):
```json
{
  "examination_findings": {
    "inspection": "Malar flush (mitral facies), comfortable at rest, no dyspnoea",
    "palpation": "Apex beat: undisplaced, tapping character (palpable S1), no heaves/thrills, pulse irregularly irregular (atrial fibrillation)",
    "percussion": "Not routinely performed in CVS examination (can percuss cardiac borders if needed)",
    "auscultation": "S1 loud (closure of stenotic mitral valve), opening snap (early diastole), mid-diastolic rumbling murmur at apex (blood flow through stenotic valve), best heard with bell, left lateral position, end-expiration"
  }
}
```

### 3. Vague Examination Technique

**❌ Bad** (technique not specified):
```json
{
  "auscultation": "Murmur heard at apex"
}
```

**✅ Good** (technique specified):
```json
{
  "auscultation": {
    "technique": "Bell of stethoscope at apex (5th intercostal space, mid-clavicular line), patient in left lateral decubitus position, listen during end-expiration (enhances murmur)",
    "finding": "Mid-diastolic rumbling murmur, low-pitched, grade 3/6 intensity, occupies 2/3 of diastole (moderate severity), does not radiate",
    "additional": "Opening snap present (0.08 seconds after S2 - suggests mobile valve leaflets), S1 loud (increased force required to close stenotic valve)"
  }
}
```

### 4. No Cultural Safety

**❌ Bad** (no privacy considerations):
```json
{
  "examination_approach": "Exposed patient's chest, auscultated heart"
}
```

**✅ Good** (culturally safe):
```json
{
  "examination_approach": {
    "preparation": "Introduced self, explained examination procedure",
    "position": "Positioned patient at 45 degrees",
    "permission": "Asked: 'May I examine your heart? I will need to lift your shirt to listen to your chest.' Patient consented.",
    "cultural_safety": "Offered chaperone (female patient, male examiner - patient declined but appreciated offer), used draping to maintain dignity (exposed only area being examined)",
    "perform": "Systematic CVS examination with appropriate draping throughout"
  }
}
```

---

## Example Persona (Mitral Stenosis - Medium Difficulty)

**File**: `backend/data/patient_personas/physical_exam_001_mitral_stenosis_female_65.json`

```json
{
  "id": "physical_exam_001_mitral_stenosis_female_65",
  "name": "Margaret Wong",
  "age": 65,
  "gender": "Female",
  "specialty": "Physical Examination",
  "examination_system": "Cardiovascular",
  "difficulty": "Medium",
  "chief_complaint": "Shortness of breath on exertion (NYHA Class II)",
  "opening_statement": "I've been getting short of breath when I walk up hills or stairs over the past 2 years. It's been gradually getting worse.",
  "emotional_baseline": "COOPERATIVE_CALM",

  "history_summary": {
    "presenting_complaint": "Progressive dyspnoea on exertion over 2 years, now NYHA Class II (symptoms with moderate exertion)",
    "past_medical_history": "Rheumatic heart disease in childhood (age 8 - acute rheumatic fever after Group A Streptococcus throat infection)",
    "medications": "Digoxin 125mcg daily (rate control for AF), warfarin 5mg daily (anticoagulation for AF), furosemide 40mg daily (diuretic)",
    "social_history": "Retired teacher, non-smoker, no alcohol"
  },

  "examination_approach": {
    "1_preparation": {
      "hand_hygiene": "WHO 7-step hand wash technique completed",
      "introduction": "Hello Mrs. Wong, I'm Dr. Smith. I'll be examining your heart and circulation today.",
      "explanation": "I'll need to check your pulse, blood pressure, look at your neck veins, and listen to your heart with a stethoscope."
    },
    "2_position": {
      "patient_position": "45-degree angle on examination bed (optimize JVP visualization)",
      "exposure": "Chest exposed with draping to maintain dignity, patient comfortable"
    },
    "3_permission": {
      "consent_obtained": "May I examine your heart and circulation?",
      "patient_response": "Yes, that's fine",
      "chaperone": "Female nurse present (chaperone offered and accepted)"
    },
    "4_perform": "Systematic cardiovascular examination using IPPA sequence (see detailed findings below)",
    "5_present": "On examination of the cardiovascular system, I found features consistent with mitral stenosis with atrial fibrillation: malar flush, irregularly irregular pulse, undisplaced tapping apex beat, loud S1, opening snap, and mid-diastolic rumbling murmur at the apex best heard with the bell in the left lateral position."
  },

  "examination_findings": {
    "general_inspection": {
      "appearance": "Well-appearing elderly female, comfortable at rest",
      "dyspnoea": "No dyspnoea at rest, SpO2 97% on room air",
      "malar_flush": "Present (mitral facies - dusky pink discoloration over cheeks due to pulmonary hypertension and low cardiac output)"
    },
    "hands": {
      "inspection": "No clubbing, no splinter haemorrhages (would suggest endocarditis), no peripheral cyanosis",
      "temperature": "Warm, well-perfused"
    },
    "pulse": {
      "radial_pulse": "Irregularly irregular rhythm (atrial fibrillation), rate 78 bpm",
      "character": "Normal volume",
      "radio_radial_delay": "None (excludes coarctation)",
      "radio_femoral_delay": "None (excludes coarctation)"
    },
    "blood_pressure": {
      "bp": "125/80 mmHg (right arm, sitting)",
      "pulse_pressure": "45 mmHg (normal - wide pulse pressure in AR, narrow in AS)"
    },
    "jugular_venous_pressure": {
      "jvp": "Elevated 5 cm above sternal angle (right heart failure secondary to pulmonary hypertension from mitral stenosis)",
      "waveform": "No a-waves visible (atrial fibrillation - no atrial contraction), prominent v-waves"
    },
    "precordium": {
      "inspection": "No visible pulsations, no scars",
      "palpation": {
        "apex_beat": "Undisplaced (5th intercostal space, mid-clavicular line), tapping character (palpable S1 - forceful closure of stenotic mitral valve)",
        "heaves": "None (RV heave would suggest severe pulmonary hypertension)",
        "thrills": "None (palpable murmur - suggests grade 4+ intensity)"
      },
      "auscultation": {
        "technique": "Auscultated with diaphragm and bell at 4 areas: aortic (2nd right ICS), pulmonary (2nd left ICS), tricuspid (4th left ICS), mitral (5th left ICS mid-clavicular line). Then auscultated mitral area with bell, patient in left lateral decubitus position, during end-expiration.",
        "s1": "Loud S1 at apex (increased force required to close stenotic mitral valve)",
        "s2": "Normal split S2 (physiological splitting with inspiration)",
        "added_sounds": "Opening snap 0.08 seconds after S2 (early diastolic sound - stenotic mitral valve opens, suggests mobile valve leaflets)",
        "murmurs": {
          "mitral_stenosis_murmur": {
            "timing": "Mid-diastolic (follows opening snap)",
            "character": "Low-pitched rumbling murmur",
            "location": "Apex (5th ICS mid-clavicular line)",
            "radiation": "Does not radiate (localized to apex)",
            "intensity": "Grade 3/6",
            "duration": "Occupies 2/3 of diastole (moderate severity - mild <1/3, moderate 1/3-2/3, severe >2/3)",
            "best_heard": "Bell of stethoscope, left lateral position, end-expiration"
          }
        }
      }
    },
    "lung_bases": {
      "auscultation": "Bibasal fine crepitations (pulmonary oedema - left heart failure secondary to mitral stenosis)",
      "percussion": "Resonant (excludes pleural effusion)"
    },
    "peripheral_edema": {
      "ankle_edema": "Bilateral pitting edema to mid-shin (right heart failure)",
      "sacral_edema": "None"
    }
  },

  "expected_diagnosis": "Moderate mitral stenosis with atrial fibrillation and heart failure (NYHA Class II)",

  "expected_investigations": [
    "ECG: Atrial fibrillation, P mitrale if sinus rhythm (broad notched P waves in lead II - left atrial enlargement)",
    "Echocardiography: Mitral valve area <1.5 cm² (normal 4-6 cm², severe <1.0 cm²), left atrial enlargement, estimate pulmonary artery pressure",
    "CXR: Left atrial enlargement (double right heart border, splaying of carina), pulmonary congestion"
  ],

  "expected_management": [
    "Rate control: Digoxin, beta-blocker if not already on",
    "Anticoagulation: Warfarin for atrial fibrillation (target INR 2-3)",
    "Diuretics: Furosemide for pulmonary congestion",
    "Surgical: Mitral valve replacement (mechanical or bioprosthetic) or percutaneous balloon mitral valvuloplasty if severe"
  ],

  "critical_errors": [
    "Didn't check JVP (missed elevated JVP - right heart failure)",
    "Didn't auscultate with bell in left lateral position (may miss murmur - technique-dependent)",
    "Didn't check for peripheral edema (missed ankle edema - heart failure)",
    "No permission obtained before examination (consent required)",
    "Wrong IPPA sequence (e.g., auscultated before palpation)"
  ],

  "clinical_educator_reviews": [
    {
      "reviewer_name": "Dr. Catherine Lee",
      "reviewer_credentials": "FRACP, Clinical Educator, Monash University Medical School",
      "review_date": "2026-03-20",
      "clinical_accuracy": "Yes",
      "difficulty_appropriate": "Yes (Medium - classic mitral stenosis)",
      "examination_technique_correct": "Yes (5 Ps framework complete, IPPA sequence correct, bell at apex in left lateral position)",
      "australian_context": "Yes (privacy, consent, chaperone offered)",
      "cultural_safety": "N/A",
      "feedback": "Excellent physical examination persona. Mitral stenosis findings realistic and complete (malar flush, tapping apex, opening snap, mid-diastolic murmur). Examination technique correctly specified (bell, left lateral, end-expiration). Severity grading appropriate (murmur occupies 2/3 of diastole = moderate). Consider adding note about pre-systolic accentuation (absent in AF).",
      "approved": true
    },
    {
      "reviewer_name": "Dr. James Robertson",
      "reviewer_credentials": "FRACP (Cardiology), Clinical Supervisor, University of Adelaide",
      "review_date": "2026-03-21",
      "clinical_accuracy": "Yes",
      "difficulty_appropriate": "Yes (Medium)",
      "examination_technique_correct": "Yes",
      "australian_context": "Yes",
      "cultural_safety": "N/A",
      "feedback": "Well-constructed examination persona. Rheumatic heart disease history appropriate (acute rheumatic fever → mitral stenosis). Atrial fibrillation realistic complication (left atrial enlargement). Management aligns with Australian guidelines (rate control, anticoagulation, surgery if severe).",
      "approved": true
    }
  ],

  "rag_citations": [
    {
      "source": "Talley & O'Connor Clinical Examination 9th edition",
      "page_ref": "p. 145",
      "quote": "Mid-diastolic rumbling murmur at apex is characteristic of mitral stenosis, best heard with bell in left lateral position during end-expiration",
      "confidence": 0.89
    },
    {
      "source": "Macleod's Clinical Examination 14th edition",
      "page_ref": "p. 98",
      "quote": "Opening snap occurs 0.06-0.12 seconds after S2 in mitral stenosis, indicates mobile valve leaflets",
      "confidence": 0.84
    },
    {
      "source": "Bates' Guide to Physical Examination 13th edition",
      "page_ref": "p. 356",
      "quote": "Malar flush (mitral facies) is a dusky pink discoloration over the cheeks seen in mitral stenosis",
      "confidence": 0.78
    }
  ]
}
```

---

## Summary

**MED-012 physical-exam-expert** creates 60 physical examination personas with:
- ✅ AMC Clinical Examination expertise (5 Ps framework, IPPA sequence)
- ✅ 5 major systems: CVS (12), Respiratory (12), Abdominal (12), Neurological (12), MSK (12)
- ✅ RAG citations from textbooks >0.65 confidence
- ✅ Systematic approach (Preparation → Position → Permission → Perform → Present)
- ✅ Australian context (privacy, consent, culturally safe examination)
- ✅ Critical error detection (missing findings, wrong sequence, no permission)
- ✅ Learning loop (clinical educator feedback → improved technique)
- ✅ Zero stereotypes, zero hardcoded credentials

**Next Steps**:
1. Execute PRD_CC_012 to instantiate this agent
2. Create test personas (12 per system - 60 total)
3. Submit for clinical educator review
4. Scale to production after validation

---

**Status**: ✅ AGENT SPECIFICATION COMPLETE
**Last Updated**: 2026-03-15
**Version**: 1.0
