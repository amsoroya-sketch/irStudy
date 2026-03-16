# Completion Guide: Creating Remaining 7 Medical Expert Agent Specifications

**Created**: 2026-03-15
**Purpose**: Step-by-step guide to complete MED-005 through QA-001
**Status**: 6/13 agents complete, 7 remaining
**Estimated Time**: 7-10 hours (1-1.5 hours per agent)

---

## 📋 Quick Reference: What's Complete vs Remaining

### ✅ Complete (6 agents - 4,589 lines)
- MED-001: Cardiology (659 lines)
- MED-002: Emergency Medicine (750 lines)
- MED-003: General Practice (720 lines)
- MED-004: Pediatrics (876 lines)
- MED-008: Respiratory Medicine (728 lines)
- MED-009: Neurology (756 lines)

### ⏳ Remaining (7 agents - ~5,700 lines estimated)
- **Batch 2**: MED-005 (ObGyn), 006 (Surgery), 007 (Psychiatry), 010 (Infectious Diseases)
- **Batch 3**: MED-012 (Physical Examination)
- **Batch 4**: MED-011 (Cultural Safety)
- **Final**: QA-001 (Medical QA Validator)

---

## 🎯 Step-by-Step Creation Process

### For Each Remaining Agent

**Step 1: Choose Template Base**
- Use `MED-001-cardiology-expert.md` for specialty medical agents (MED-005, 006, 007, 010)
- Use `MED-004-pediatrics-expert.md` for age/population-specific agents (MED-011, MED-012)
- Use `MED-001` for QA-001 (validator role)

**Step 2: Copy Template**
```bash
# Example for MED-005
cd /home/dev/Development/irStudy/clinical-content-prds/agents/
cp MED-001-cardiology-expert.md MED-005-obgyn-expert.md
```

**Step 3: Global Find-Replace (Agent Metadata)**
Replace these throughout the file:
- `MED-001` → `MED-005`
- `cardiology-expert` → `obgyn-expert`
- `Cardiology` → `Obstetrics & Gynaecology`
- `Cardiovascular Medicine` → `Obstetrics & Gynaecology`
- `45 (15 Easy, 18 Medium, 12 Hard)` → `27 (9 Easy, 11 Medium, 7 Hard)`
- `Batch 1` → `Batch 2`

**Step 4: Update Expertise Profile**
Use the detailed specifications below for each agent

**Step 5: Update Critical Errors**
Replace cardiology-specific errors with specialty-specific errors

**Step 6: Update Example Persona**
Replace STEMI example with specialty-specific example (details below)

**Step 7: Verify**
- Check file is 600-900 lines
- All 10 sections present
- RAG citations included
- FRACP reviews included
- No cardiology references remaining

---

## 📝 Detailed Specifications for Each Agent

### MED-005: Obstetrics & Gynaecology Expert

**File**: `MED-005-obgyn-expert.md`

**Metadata**:
- Agent ID: MED-005
- Agent Name: obgyn-expert
- Specialty: Obstetrics & Gynaecology
- FRACP Equivalent: O&G Advanced Trainee (FRANZCOG)
- eTG Expertise: Section 15.1-15.5
- Target Personas: 27 (9 Easy, 11 Medium, 7 Hard)
- Batch: Batch 2

**eTG Sections** (replace 2.1-2.8):
1. **Pregnancy Care** - eTG 15.1
   - Antenatal care schedule (visits at 12, 20, 28, 32, 36, 38, 40 weeks)
   - NIPT (non-invasive prenatal testing) at 10-12 weeks
   - NT scan (nuchal translucency) at 11-13 weeks
   - Anomaly scan at 18-22 weeks
   - GDM screening (Glucose Challenge Test) at 24-28 weeks

2. **Ectopic Pregnancy** - eTG 15.2
   - βhCG levels (should double every 48 hours in normal pregnancy)
   - Discriminatory zone: βhCG >1500 IU/L should see IUP on TVUS
   - Transvaginal ultrasound (TVUS): No intrauterine pregnancy (IUP) + βhCG >1500 = ectopic
   - Management: Methotrexate 50mg/m² IM (if unruptured, βhCG <1500, no cardiac activity) OR laparoscopic salpingectomy
   - Ruptured ectopic: Emergency laparoscopy, resuscitation (IV fluids, blood products)

3. **Contraception** - eTG 15.3
   - COCP (combined oral contraceptive pill): Estrogen + progesterone
   - POP (progesterone-only pill): Desogestrel, no estrogen
   - LARC (long-acting reversible contraception): IUD (Mirena), implant (Implanon)
   - Emergency contraception: Levonorgestrel 1.5mg PO within 72 hours OR copper IUD within 5 days

4. **Menopause** - eTG 15.4
   - Definition: 12 months amenorrhoea (average age 51 years)
   - Symptoms: Hot flashes, night sweats, vaginal dryness, mood changes
   - HRT (hormone replacement therapy): Estrogen + progesterone (if uterus intact)
   - Contraindications: Breast cancer, VTE, CVD

5. **Gynecological Cancers** - eTG 15.5
   - Cervical cancer screening: Pap smear every 5 years (25-74 years)
   - Ovarian cancer: CA-125, transvaginal ultrasound, referral if suspicious
   - Endometrial cancer: Postmenopausal bleeding (PMB) = cancer until proven otherwise
   - Vulvar cancer: Persistent itch, ulcer, lump → biopsy

**Critical Errors** (replace cardiology errors):
1. **Missed Ectopic Pregnancy**:
   - ❌ Abdominal pain + positive pregnancy test + no IUP on TVUS = ectopic until proven otherwise
   - ❌ Discharged without βhCG follow-up (ruptured ectopic can be fatal)

2. **Contraindicated Medications in Pregnancy**:
   - ❌ ACE inhibitors (perindopril, ramipril) = teratogenic (renal agenesis)
   - ❌ Warfarin = fetal bleeding, chondrodysplasia punctata
   - ❌ Isotretinoin (Roaccutane) = severe craniofacial/cardiac defects

3. **Missed Postmenopausal Bleeding (PMB)**:
   - ❌ PMB = endometrial cancer until proven otherwise (transvaginal ultrasound + biopsy)

4. **Wrong Thrombo-prophylaxis in Pregnancy**:
   - ❌ Warfarin in pregnancy (teratogenic) - use LMWH (enoxaparin) instead

**Example Persona** (replace STEMI):
**28yo F with ruptured ectopic pregnancy**:
- Chief complaint: Right lower abdominal pain, 6 weeks amenorrhoea
- Symptoms: Sudden-onset severe RIF pain, shoulder tip pain (diaphragmatic irritation from blood), dizziness (hypovolemia)
- Examination: Tachycardia 110 bpm, BP 90/60 mmHg (shock), RIF tenderness, cervical excitation
- Investigations: βhCG 2500 IU/L, TVUS no IUP, free fluid in pouch of Douglas (blood)
- Diagnosis: Ruptured ectopic pregnancy (surgical emergency)
- Management: Resuscitation (2 large-bore IV cannulas, crystalloid 1-2L, cross-match 4 units), emergency laparoscopy (salpingectomy), post-op anti-D if Rh negative

**FRACP Equivalent**: FRANZCOG (Fellow Royal Australian and New Zealand College of Obstetricians and Gynaecologists)

---

### MED-006: Surgery Expert

**File**: `MED-006-surgery-expert.md`

**Metadata**:
- Agent ID: MED-006
- Agent Name: surgery-expert
- Specialty: Surgery
- FRACP Equivalent: General Surgery Advanced Trainee (FRACS)
- eTG Expertise: Multiple sections (Acute abdomen, Pre/post-op care)
- Target Personas: 27 (9 Easy, 11 Medium, 7 Hard)
- Batch: Batch 2

**eTG Sections**:
1. **Acute Appendicitis** - eTG 9.5
   - Clinical features: RIF pain (McBurney's point), rebound tenderness, guarding, Rovsing's sign
   - Imaging: CT abdomen/pelvis (dilated appendix >6mm, fat stranding)
   - Alvarado score: Migration of pain, Anorexia, Nausea/vomiting, RIF tenderness, Rebound, Elevated temperature, Leukocytosis, Shift to left (neutrophils)
   - Management: Laparoscopic appendicectomy, antibiotics (cefazolin + metronidazole)

2. **Acute Cholecystitis** - eTG 9.6
   - Murphy's sign: Inspiratory arrest on palpation RUQ
   - Imaging: Ultrasound (thickened gallbladder wall, stones, pericholecystic fluid)
   - Management: Nil by mouth, IV fluids, antibiotics (cefazolin + metronidazole), cholecystectomy (within 72 hours)

3. **Bowel Obstruction** - eTG 9.7
   - Small bowel obstruction (SBO): Colicky pain, vomiting, absolute constipation
   - Large bowel obstruction (LBO): Abdominal distension, constipation, late vomiting
   - Imaging: AXR (dilated loops, air-fluid levels), CT (transition point)
   - Management: NBM, NG tube, IV fluids, surgical consultation

4. **Pre-operative Assessment** - eTG 7.2
   - ASA classification (I-VI): Fitness for surgery
   - Cardiac risk: Revised Cardiac Risk Index (RCRI)
   - VTE prophylaxis: LMWH (enoxaparin 40mg SC daily) + TED stockings
   - Antibiotic prophylaxis: Cefazolin 2g IV 30 minutes pre-incision

5. **Post-operative Complications** - eTG 7.3
   - Wound infection: Redness, discharge, fever (cellulitis vs abscess)
   - DVT/PE: Unilateral leg swelling, chest pain, dyspnoea
   - Anastomotic leak: Fever, tachycardia, peritonitis (day 5-7 post-op)
   - Ileus: No bowel sounds, no flatus, abdominal distension

**Critical Errors**:
1. **Missed Acute Appendicitis**:
   - ❌ RIF pain + rebound + fever = appendicitis (surgical emergency)
   - ❌ Delayed surgery → perforation → peritonitis

2. **Wrong Antibiotic Prophylaxis**:
   - ❌ No antibiotics before clean surgery (increased SSI risk)
   - ❌ Cefazolin >2 hours pre-incision (ineffective prophylaxis)

3. **Missed Compartment Syndrome** (post-trauma):
   - ❌ 5 Ps: Pain (out of proportion), Pallor, Pulselessness, Paraesthesia, Paralysis
   - ❌ Delayed fasciotomy → permanent nerve/muscle damage

4. **No VTE Prophylaxis**:
   - ❌ Post-op patients at high risk (immobility, surgery, cancer)
   - ❌ No LMWH + TED stockings → DVT/PE

**Example Persona**:
**35yo M with acute appendicitis**:
- Chief complaint: RIF pain for 24 hours
- Symptoms: Pain started periumbilical, migrated to RIF, anorexia, nausea, vomited twice
- Examination: Fever 38.2°C, McBurney's point tenderness, rebound, guarding, Rovsing's sign positive, psoas sign positive
- Investigations: WCC 16 × 10⁹/L (neutrophilia), CRP 80 mg/L, CT abdomen (dilated appendix 9mm, fat stranding)
- Diagnosis: Acute appendicitis (Alvarado score 9/10 - high probability)
- Management: NBM, IV fluids, analgesia, antibiotics (cefazolin 2g IV + metronidazole 500mg IV), laparoscopic appendicectomy

**WHO Surgical Safety Checklist**: Sign In → Time Out → Sign Out

---

### MED-007: Psychiatry Expert

**File**: `MED-007-psychiatry-expert.md`

**Metadata**:
- Agent ID: MED-007
- Agent Name: psychiatry-expert
- Specialty: Psychiatry
- FRACP Equivalent: Psychiatry Advanced Trainee (FRANZCP)
- eTG Expertise: Section 16.1-16.9
- Target Personas: 36 (12 Easy, 14 Medium, 10 Hard)
- Batch: Batch 2

**eTG Sections**:
1. **Major Depressive Disorder (MDD)** - eTG 16.2
   - DSM-5 criteria: ≥5 symptoms for ≥2 weeks (depressed mood, anhedonia, sleep, appetite, energy, concentration, guilt, psychomotor, suicide)
   - PHQ-9 screening: Score 0-27 (0-4 minimal, 5-9 mild, 10-14 moderate, 15-19 moderately severe, 20-27 severe)
   - SSRIs: Sertraline 50mg daily, escitalopram 10mg daily (first-line)
   - Psychotherapy: CBT (Cognitive Behavioral Therapy) equally effective
   - Suicide risk assessment: PHQ-9 item 9 (SI), ask direct questions

2. **Generalized Anxiety Disorder (GAD)** - eTG 16.3
   - Excessive worry for ≥6 months, difficult to control
   - GAD-7 screening: Score 0-21 (0-4 minimal, 5-9 mild, 10-14 moderate, 15-21 severe)
   - SSRIs: Sertraline, escitalopram (first-line)
   - Benzodiazepines: SHORT-TERM only (lorazepam 0.5-1mg PRN) - dependence risk

3. **Psychosis/Schizophrenia** - eTG 16.5
   - Positive symptoms: Hallucinations, delusions, disorganized speech
   - Negative symptoms: Flat affect, alogia, avolition, anhedonia
   - Antipsychotics: Olanzapine 10mg nocte, risperidone 2mg BD (atypical first-line)
   - Side effects: Extrapyramidal (parkinsonism, akathisia), metabolic (weight gain, diabetes), QTc prolongation

4. **Bipolar Disorder** - eTG 16.4
   - Manic episode: Elevated mood, decreased sleep, grandiosity, pressured speech, risk-taking
   - Mood stabilizers: Lithium 400mg BD (target level 0.6-1.0 mmol/L), sodium valproate
   - Lithium monitoring: TFTs (hypothyroidism), UEC (renal), lithium levels

5. **Suicide Risk Assessment** - eTG 16.1
   - SAD PERSONS scale: Sex (M), Age (>45 or <25), Depression, Previous attempt, Ethanol, Rational thinking loss, Social support lacking, Organized plan, No spouse, Sickness
   - Direct questions: "Are you having thoughts of harming yourself? Do you have a plan?"
   - Safety planning: Remove means (medications, firearms), crisis contacts, emergency services
   - Mental Health Act: Involuntary treatment if imminent risk

**Critical Errors**:
1. **Missed Suicide Risk**:
   - ❌ PHQ-9 item 9 positive (SI) + no safety plan = high risk
   - ❌ Direct question not asked: "Are you thinking about ending your life?"

2. **Wrong Antipsychotic (QTc Prolongation)**:
   - ❌ Haloperidol in elderly (parkinsonism, falls)
   - ❌ No ECG before starting antipsychotics (QTc >500ms = TdP risk)

3. **No Mental Health Act Assessment**:
   - ❌ Acute psychosis + risk to self/others + refuses treatment = involuntary treatment needed

4. **Benzodiazepine Long-Term**:
   - ❌ Lorazepam for >4 weeks (dependence, tolerance, withdrawal seizures)

**Example Persona**:
**25yo F with major depressive disorder + suicidal ideation**:
- Chief complaint: "I feel hopeless, like I'm better off dead"
- PHQ-9 score: 22/27 (severe depression)
- Symptoms: Depressed mood daily for 6 weeks, anhedonia, insomnia, poor appetite (5kg weight loss), fatigue, poor concentration, guilt, psychomotor retardation
- Suicide risk: Passive SI ("better off dead"), no active plan YET, no previous attempts, protective factors (family, wants to get better)
- MSE (Mental State Examination):
  - Appearance: Unkempt, poor eye contact
  - Behavior: Psychomotor retardation
  - Speech: Slow, monotone
  - Mood: "Hopeless"
  - Affect: Flat, congruent
  - Thought content: Passive suicidal ideation, no plan, no intent
  - Perception: No hallucinations
  - Cognition: Alert, oriented, poor concentration
  - Insight: Fair (recognizes depression, wants help)
  - Judgment: Fair
- Management:
  - Safety planning: Remove means (medications locked away), crisis contacts (Lifeline 13 11 14), family aware, daily check-ins
  - Escitalopram 10mg daily (SSRI - first-line for MDD)
  - CBT referral (psychologist - Medicare rebate via Mental Health Care Plan)
  - Review in 2 weeks (assess suicide risk, medication side effects)
  - Consider admission if deteriorates (Mental Health Act if refuses)

**FRACP Equivalent**: FRANZCP (Fellow Royal Australian and New Zealand College of Psychiatrists)

---

### MED-010: Infectious Diseases Expert

**File**: `MED-010-infectious-diseases-expert.md`

**Metadata**:
- Agent ID: MED-010
- Agent Name: infectious-diseases-expert
- Specialty: Infectious Diseases
- FRACP Equivalent: Infectious Diseases Advanced Trainee
- eTG Expertise: Section 5.1-5.12
- Target Personas: 27 (9 Easy, 11 Medium, 7 Hard)
- Batch: Batch 2

**eTG Sections**:
1. **Sepsis and Septic Shock** - eTG 5.8
   - qSOFA criteria (Quick Sequential Organ Failure Assessment): RR ≥22, altered GCS, SBP ≤100
   - Sepsis 6 bundle (within 1 hour): Blood cultures, Lactate, Antibiotics, Fluids (20-30mL/kg), Urine output, Oxygen
   - Empirical antibiotics: Piperacillin-tazobactam 4.5g IV TDS OR meropenem 1g IV TDS
   - Fluid resuscitation: 20-30mL/kg crystalloid (0.9% NaCl) within 3 hours

2. **Bacterial Meningitis** - eTG 5.3
   - Classic triad: Headache, fever, neck stiffness (only 44% have all three)
   - LP contraindications: Raised ICP, coagulopathy, infection at LP site
   - CSF analysis:
     - Bacterial: Cloudy, WCC >1000, protein ↑, glucose ↓, Gram stain positive
     - Viral: Clear, WCC 100-1000 (lymphocytes), protein ↑, glucose normal
   - Empirical antibiotics: Ceftriaxone 2g IV BD + vancomycin 1g IV BD + dexamethasone 10mg IV QID

3. **HIV/AIDS** - eTG 5.9
   - CD4 count: <200 = AIDS, opportunistic infections (PCP, CMV, toxoplasma)
   - ART (antiretroviral therapy): 2 NRTIs + NNRTI OR integrase inhibitor
   - PCP prophylaxis: Trimethoprim-sulfamethoxazole 160/800mg PO daily (if CD4 <200)
   - PrEP (pre-exposure prophylaxis): TDF/FTC for high-risk individuals

4. **Tuberculosis (TB)** - eTG 5.10
   - Risk factors: Immigrant from high-prevalence country, HIV, homelessness
   - Clinical features: Night sweats, weight loss, chronic cough >3 weeks, hemoptysis
   - CXR: Apical consolidation, cavitation
   - Diagnosis: Sputum AFB smear + culture, GeneXpert (rapid PCR)
   - Treatment: RIPE (Rifampicin, Isoniazid, Pyrazinamide, Ethambutol) for 2 months → RI for 4 months

5. **Infective Endocarditis (IE)** - eTG 5.4
   - Duke criteria: Major (blood cultures positive, vegetation on echo) + Minor (fever, predisposing heart condition, vascular phenomena, immunologic phenomena)
   - Blood cultures: 3 sets from different sites before antibiotics
   - Empirical antibiotics: Benzylpenicillin 2.4g IV Q4H + gentamicin 1.5mg/kg IV Q8H
   - Complications: Heart failure (valve destruction), emboli (stroke, splenic infarct), mycotic aneurysm

**Critical Errors**:
1. **Delayed Antibiotics in Sepsis**:
   - ❌ Mortality increases 7% per hour delay after sepsis recognition
   - ❌ Antibiotics should be given within 1 hour (Sepsis 6 bundle)

2. **Wrong Empirical Therapy**:
   - ❌ Missed Pseudomonas coverage in neutropenic patient (use piperacillin-tazobactam)
   - ❌ No MRSA coverage in suspected meningitis (add vancomycin)

3. **Missed Tuberculosis in Immigrant**:
   - ❌ Night sweats + weight loss + chronic cough + apical CXR changes = TB (notify public health)

4. **LP in Raised ICP**:
   - ❌ LP with papilloedema or focal neurology (risk of coning → death)
   - ❌ Always do CT brain first if concern for raised ICP

**Example Persona**:
**40yo M with bacterial meningitis**:
- Chief complaint: Severe headache, fever, photophobia
- Symptoms: Headache (worst ever, 10/10), fever 39.5°C for 12 hours, neck stiffness, photophobia, nausea/vomiting
- Examination: GCS 14/15 (E4 V4 M6), temperature 39.5°C, neck stiffness (Kernig's sign positive, Brudzinski's sign positive), photophobia, no rash, no focal neurology
- Investigations:
  - Blood cultures: Positive (Streptococcus pneumoniae)
  - Lumbar puncture: CSF cloudy, WCC 2000 (neutrophils 95%), protein 2.5 g/L (elevated), glucose 1.5 mmol/L (low, serum glucose 5.0), Gram stain: Gram-positive diplococci
- Diagnosis: Bacterial meningitis (Streptococcus pneumoniae)
- Management:
  - Empirical antibiotics: Ceftriaxone 2g IV BD + vancomycin 1g IV BD (started immediately, before LP if delay)
  - Dexamethasone 10mg IV QID for 4 days (reduces mortality/neurological sequelae)
  - Isolation (droplet precautions for first 24 hours of antibiotics)
  - Notify public health
  - Contact tracing (prophylaxis for close contacts: rifampicin or ciprofloxacin)

**Sepsis 6 Bundle**: Blood cultures → Lactate → Antibiotics → Fluids → Urine output → Oxygen

---

### MED-012: Physical Examination Expert

**File**: `MED-012-physical-exam-expert.md`

**Metadata**:
- Agent ID: MED-012
- Agent Name: physical-exam-expert
- Specialty: Physical Examination (5 Systems)
- AMC Equivalent: AMC Clinical Examination (Practical Skills)
- Expertise: 5 Ps Framework (Preparation, Position, Permission, Perform, Present)
- Target Personas: 60 (20 Easy, 24 Medium, 16 Hard)
- Batch: Batch 3

**Systems** (12 personas each):
1. **Cardiovascular Examination** (12 personas):
   - Mitral stenosis: Pansystolic murmur at apex radiating to axilla, opening snap, AF
   - Aortic stenosis: Ejection systolic murmur radiating to carotids, slow-rising pulse, narrow pulse pressure
   - Heart failure: Elevated JVP, S3 gallop, bibasal crepitations, pedal edema
   - Atrial fibrillation: Irregularly irregular pulse, absent a-waves in JVP
   - Hypertension: BP >140/90 mmHg, radio-radial delay (coarctation), radio-femoral delay

2. **Respiratory Examination** (12 personas):
   - Consolidation (pneumonia): Dull percussion, bronchial breathing, increased vocal resonance
   - Pleural effusion: Stony dull percussion, reduced breath sounds, reduced vocal resonance
   - Pneumothorax: Hyperresonant percussion, reduced breath sounds, reduced chest expansion
   - COPD: Barrel chest, hyperinflated, wheeze, prolonged expiratory phase
   - Asthma: Diffuse wheeze, hyperinflated, use of accessory muscles (severe)

3. **Abdominal Examination** (12 personas):
   - Hepatomegaly: Palpable liver edge, span >12cm (percussion), causes: cirrhosis, hepatitis, malignancy
   - Splenomegaly: Palpable spleen (can't get above it, moves with respiration, notch), causes: portal hypertension, lymphoma, infection
   - Ascites: Shifting dullness, fluid thrill
   - Renal masses: Ballottable, moves with respiration, resonant (bowel in front)
   - Hernias: Inguinal (above/below inguinal ligament), femoral (below), incisional

4. **Neurological Examination** (12 personas):
   - Hemiplegia (stroke): Unilateral weakness (UMN signs), increased tone, brisk reflexes, Babinski up
   - Parkinson's disease: Resting tremor, rigidity (cogwheel), bradykinesia, mask-like facies
   - Cerebellar signs: DANISH (Dysdiadochokinesia, Ataxia, Nystagmus, Intention tremor, Speech slurred, Hypotonia)
   - Peripheral neuropathy: Glove-and-stocking sensory loss, absent ankle reflexes, diminished vibration sense
   - Multiple sclerosis: Internuclear ophthalmoplegia, spastic paraparesis, Lhermitte's sign

5. **Musculoskeletal Examination** (12 personas):
   - Osteoarthritis: Heberden's nodes (DIP), Bouchard's nodes (PIP), reduced range of motion, crepitus
   - Rheumatoid arthritis: Symmetrical MCP/PIP swelling, ulnar deviation, swan-neck deformity, boutonniere deformity
   - Gait abnormalities: Hemiplegic, ataxic, parkinsonian, high-stepping, waddling
   - Knee examination: Effusion (patellar tap), ligaments (ACL, PCL, MCL, LCL), menisci (McMurray's test)
   - Shoulder examination: Rotator cuff tears (supraspinatus, infraspinatus), impingement, frozen shoulder

**5 Ps Framework**:
1. **Preparation**: Hand wash, introduce self, obtain consent
2. **Position**: Patient at 45-degree angle (CVS), sitting upright (respiratory)
3. **Permission**: "May I examine your heart/chest/abdomen?"
4. **Perform**: Systematic examination (inspection → palpation → percussion → auscultation)
5. **Present**: Summarize findings to examiner

**Critical Errors**:
1. **Missing Examination Findings**:
   - ❌ Didn't auscultate heart → missed murmur (mitral stenosis)
   - ❌ Didn't check JVP → missed heart failure

2. **Wrong Examination Sequence**:
   - ❌ Palpated abdomen before percussion (altered findings)
   - ❌ Didn't warm hands before chest exam (uncomfortable)

3. **No Permission Obtained**:
   - ❌ Didn't ask "May I examine...?" (consent required)
   - ❌ Exposed patient without draping (privacy)

4. **No Systematic Approach**:
   - ❌ Random examination (missed findings)
   - ❌ Should always: Inspection → Palpation → Percussion → Auscultation

**Example Persona**:
**65yo F with mitral stenosis**:
- Chief complaint: Shortness of breath on exertion (NYHA Class II)
- History: Rheumatic heart disease in childhood (age 8), progressive dyspnoea over 2 years
- Examination:
  - **Inspection**: Comfortable at rest, malar flush (mitral facies)
  - **Palpation**: Apex beat undisplaced, tapping character (palpable S1), no heaves/thrills
  - **Auscultation**:
    - S1 loud (closure of stenotic mitral valve)
    - Opening snap (early diastole - mitral valve opens)
    - Mid-diastolic rumbling murmur at apex (blood flow through stenotic valve)
    - Best heard with bell, left lateral position, end-expiration
  - **Pulse**: Irregularly irregular (atrial fibrillation)
  - **JVP**: Elevated (right heart failure secondary to MS)
- Investigations: ECG (AF, P mitrale if sinus rhythm), Echo (mitral valve area <1.5cm², LA enlargement)
- Management: Rate control (beta-blocker, digoxin), anticoagulation (warfarin for AF), diuretics (furosemide), surgical (mitral valve replacement if severe)

**AMC Clinical Examination Marking**:
- Systematic approach (5 Ps) ✓
- All findings identified ✓
- Correct interpretation ✓
- Professional manner ✓

---

### MED-011: Cultural Safety Expert

**File**: `MED-011-cultural-safety-expert.md`

**Metadata**:
- Agent ID: MED-011
- Agent Name: cultural-safety-expert
- Specialty: Cultural Safety (Aboriginal/TSI, LGBTQIA+, CALD)
- Guidelines: NACCHO Aboriginal Health, Rainbow Health Victoria, CALD Competency
- Target Personas: 92 (integrated into 360 total)
- Distribution: 12 Aboriginal/TSI (3.3%), 40 LGBTQIA+ (11%), 40 CALD (11%)
- Batch: Batch 4

**Cultural Groups**:
1. **Aboriginal and Torres Strait Islander** (12 personas):
   - Nations: Noongar (WA), Wurundjeri (VIC), Eora (NSW), Kaurna (SA), Palawa (TAS)
   - Cultural considerations: Family involvement (Elders, community), traditional healing alongside Western medicine, historical trauma (Stolen Generations), mistrust of healthcare system
   - Health disparities: 3× higher CVD, 4× higher diabetes, 2× higher CKD, lower life expectancy (8-10 years gap)
   - NACCHO protocols: Cultural safety training, Aboriginal liaison officers, flexible appointment times
   - Language: Use "Aboriginal and Torres Strait Islander" (not "indigenous"), respectful titles (Uncle, Aunty for Elders)

2. **LGBTQIA+** (40 personas):
   - Identities: Lesbian, Gay, Bisexual, Transgender, Queer, Intersex, Asexual, Non-binary, Gender diverse
   - Clinical considerations:
     - Transgender health: HRT (hormone replacement therapy - estrogen or testosterone), gender-affirming surgery
     - Sexual health: PrEP (pre-exposure prophylaxis for HIV), STI screening
     - Mental health: Higher rates depression, anxiety, suicide (minority stress)
   - Inclusive language: Pronouns (they/them), chosen name (not deadname), partner (not boyfriend/girlfriend)
   - Rainbow Health Victoria guidelines: Inclusive forms (gender options beyond M/F), same-sex partner recognition

3. **CALD (Culturally and Linguistically Diverse)** (40 personas):
   - Backgrounds: Chinese, Indian, Vietnamese, Lebanese, Italian, Greek, Sudanese, Afghan
   - Language barriers: Interpreter services (free via TIS National 131 450)
   - Cultural considerations:
     - Family decision-making (collectivist cultures)
     - Gender preferences (female doctor for female patient in some cultures)
     - Religious considerations (prayer times, fasting during Ramadan, halal/kosher food)
   - Health literacy: Explain medical terms in plain language, pictorial aids

**Critical Errors**:
1. **Stereotypical Personas**:
   - ❌ Aboriginal patient always has diabetes, alcohol issues
   - ❌ LGBTQIA+ patient always has HIV
   - ❌ CALD patient always has poor English, non-compliant

2. **Missing Cultural Context**:
   - ❌ Aboriginal patient with no family/community connection (isolated)
   - ❌ Transgender patient with no HRT history (if on HRT)
   - ❌ CALD patient with no cultural background mentioned

3. **Offensive Language**:
   - ❌ "Indigenous" (use "Aboriginal and Torres Strait Islander")
   - ❌ Deadnaming transgender patients (use chosen name)
   - ❌ Assumptions based on appearance ("Where are you really from?")

4. **No Cultural Liaison Review**:
   - ❌ Aboriginal/TSI personas deployed without Aboriginal liaison review
   - ❌ LGBTQIA+ personas deployed without LGBTQIA+ educator review

**Example Persona (Aboriginal)**:
**35yo Aboriginal F with chronic kidney disease**:
- Name: Aunty Lisa Williams (Noongar people, Western Australia)
- Chief complaint: Ankle swelling, fatigue
- Cultural background:
  - Strong connection to Country (Noongar land, southwest WA)
  - Family: Lives with extended family (mother, sisters, nieces/nephews)
  - Community: Active in local Aboriginal community health service
  - Traditional healing: Uses bush medicine for minor ailments, seeks Western medicine for serious conditions
- History:
  - Rheumatic heart disease in childhood (age 10) - common in Aboriginal Australians
  - Type 2 diabetes (diagnosed 5 years ago, HbA1c 8.5% - suboptimal control)
  - Hypertension (BP 155/95 mmHg)
- Cultural considerations:
  - Prefers Aboriginal liaison officer present for consultations
  - Family involvement important (wants sisters to know diagnosis/treatment)
  - Has experienced discrimination in healthcare previously (dismissed concerns as "just diabetes")
  - Appointment flexibility needed (caring responsibilities for nieces/nephews)
- Examination: BP 155/95, bilateral ankle edema (pitting), creatinine 180 μmol/L (eGFR 35 - CKD stage 3b)
- Management:
  - Cultural safety: Aboriginal liaison officer involved, family meeting arranged
  - CKD management: ACE inhibitor (perindopril), optimize diabetes control, nephrology referral
  - NACCHO protocol: Flexible appointments, transport assistance, culturally safe communication
- Anti-stereotyping: Employed (community health worker), non-smoker, moderate alcohol use (2 standard drinks/week), excellent medication compliance

**Cultural Liaison Review**: MANDATORY before deployment (Aboriginal health worker reviews all 12 Aboriginal personas)

**Example Persona (LGBTQIA+)**:
**28yo transgender M (FTM) with depression**:
- Name: Alex Chen (he/him pronouns)
- Gender identity: Transgender male (assigned female at birth, transitioned age 24)
- Chief complaint: Low mood, anxiety about gender-affirming surgery
- Cultural considerations:
  - Pronouns: he/him (use consistently, never "she" or deadname)
  - Preferred name: Alex (never use birth name)
  - Partner: Boyfriend James (use "partner" or specific term, not assumptions)
- HRT history:
  - Testosterone cypionate 100mg IM fortnightly for 4 years
  - Effects: Deepened voice, facial hair, increased muscle mass, cessation of menses
  - Monitoring: TFTs (normal), lipids (normal), hematocrit (slightly elevated - normal for testosterone)
- Mental health:
  - Depression (PHQ-9 score 15 - moderately severe)
  - Anxiety about upcoming top surgery (bilateral mastectomy + chest reconstruction)
  - Minority stress: Discrimination, family rejection (parents not accepting), workplace microaggressions
- Management:
  - Affirming care: Use correct name/pronouns, normalize transgender identity
  - Depression: Sertraline 50mg daily, CBT referral, peer support groups (TransFolk)
  - Gender-affirming surgery: Referral to surgeon, pre-op assessment, mental health support
  - Family therapy: Offer to family (if willing) to improve acceptance
- Anti-stereotyping: University-educated (software engineer), stable relationship, no substance abuse, excellent health literacy

**LGBTQIA+ Educator Review**: MANDATORY before deployment

---

### QA-001: Medical QA Validator

**File**: `QA-001-medical-qa-validator.md`

**Metadata**:
- Agent ID: QA-001
- Agent Name: medical-qa-validator
- Role: Quality Assurance Validator (NOT persona creator)
- Reviews: ALL 360 personas across all 12 specialties
- Quality Gates: JSON compliance, RAG citations, clinical accuracy, cultural safety
- Output: QA report JSON with pass/fail recommendations
- Batch: Final Validation

**Validation Domains**:
1. **Technical Compliance** (JSON, RAG, Structure)
2. **Clinical Accuracy** (Diagnosis, Management, Safety)
3. **Cultural Safety** (Stereotypes, Representation, Liaison Review)
4. **Educational Quality** (Difficulty, AMC Alignment, Learning Objectives)
5. **Security** (No Hardcoded Credentials, PHI Protection)

**Validation Checklist** (13 items):
1. [ ] **JSON Template Compliance**: All 360 personas follow `backend/data/patient_personas_template.json`
2. [ ] **RAG Citations >0.65**: All symptoms have eTG/AMH citations with confidence >0.65
3. [ ] **FRACP Reviews ≥2**: Each persona has ≥2 specialist clinician reviews with "Approved: Yes"
4. [ ] **Clinical Accuracy**: Zero wrong diagnoses, dangerous advice, contraindicated medications
5. [ ] **Australian Medical Context**: eTG/AMH guidelines, PBS restrictions, Medicare billing, AHPRA standards
6. [ ] **Difficulty Distribution**: 125 Easy (35%), 148 Medium (41%), 87 Hard (24%)
7. [ ] **Specialty Distribution**: Correct allocation (45 cardiology, 45 emergency, 54 GP, 36 pediatrics, etc.)
8. [ ] **Cultural Safety - Aboriginal/TSI**: 12 personas (3.3%), NO stereotypes, cultural liaison review ✓
9. [ ] **Cultural Safety - LGBTQIA+**: 40 personas (11%), NO stereotypes, educator review ✓
10. [ ] **Cultural Safety - CALD**: 40 personas (11%), NO stereotypes, diverse backgrounds
11. [ ] **Zero Hardcoded Credentials**: No API keys, database passwords, file paths in JSON
12. [ ] **Zero Security Violations**: PHI properly anonymized, no real patient data
13. [ ] **Educational Alignment**: AMC competencies covered, learning objectives clear

**QA Report Output Format**:
```json
{
  "qa_report_version": "1.0",
  "validation_date": "2026-03-25",
  "total_personas_reviewed": 360,
  "total_personas_passed": 360,
  "total_personas_failed": 0,
  "pass_rate": "100%",

  "quality_metrics": {
    "avg_rag_citation_confidence": 0.73,
    "avg_fracp_reviews_per_persona": 2.1,
    "avg_clinical_accuracy_score": 9.4,
    "cultural_safety_score": 9.8
  },

  "distribution_validation": {
    "difficulty": {
      "easy": 125,
      "medium": 148,
      "hard": 87,
      "status": "PASS (matches target distribution)"
    },
    "specialty": {
      "cardiology": 45,
      "emergency": 45,
      "general_practice": 54,
      "pediatrics": 36,
      "respiratory": 36,
      "neurology": 27,
      "obgyn": 27,
      "surgery": 27,
      "psychiatry": 36,
      "infectious_diseases": 27,
      "physical_exam": 60,
      "status": "PASS (all specialties correct)"
    },
    "cultural_diversity": {
      "aboriginal_tsi": 12,
      "lgbtqia": 40,
      "cald": 40,
      "status": "PASS (cultural liaison review complete)"
    }
  },

  "quality_issues": [],
  "clinical_inaccuracies": [],
  "cultural_safety_violations": [],
  "security_violations": [],

  "recommendation": "APPROVED FOR DEPLOYMENT",
  "deployment_readiness": "100%",
  "next_steps": [
    "Deploy to production database",
    "Integrate with AI Patient Service",
    "Begin pilot testing with 20 AMC candidates"
  ]
}
```

**Critical Errors** (Auto-Fail):
1. **Clinical Inaccuracy**: Wrong diagnosis, dangerous advice, contraindicated medication → persona FAILED
2. **Cultural Stereotype**: Offensive/stereotypical content → persona FAILED, liaison review required
3. **Security Violation**: Hardcoded credentials, real patient data → persona FAILED, immediate removal
4. **Missing FRACP Reviews**: <2 reviews → persona FAILED, requires additional reviews

**Example Validation** (single persona):
```json
{
  "persona_id": "cardiology_001_stemi_male_65",
  "validation_status": "PASS",
  "validations_performed": 13,
  "validations_passed": 13,
  "validations_failed": 0,
  "issues": [],
  "clinical_accuracy": {
    "diagnosis": "STEMI - Correct ✓",
    "management": "Aspirin 300mg STAT, clopidogrel, thrombolysis - Correct ✓",
    "critical_errors_defined": "Yes (missed STEMI, delayed aspirin) ✓",
    "status": "PASS"
  },
  "rag_citations": {
    "total_citations": 8,
    "avg_confidence": 0.76,
    "min_confidence": 0.67,
    "all_above_threshold": true,
    "status": "PASS"
  },
  "fracp_reviews": {
    "total_reviews": 2,
    "reviewers": ["Dr. Sarah Chen (FRACP Cardiology)", "Dr. Michael O'Brien (FRACP Cardiology)"],
    "all_approved": true,
    "status": "PASS"
  },
  "recommendation": "APPROVED FOR DEPLOYMENT"
}
```

---

## 🎯 Quick Creation Workflow (Per Agent)

### Step-by-Step (30-45 minutes per agent)

1. **Copy Template** (2 minutes)
   ```bash
   cd /home/dev/Development/irStudy/clinical-content-prds/agents/
   cp MED-001-cardiology-expert.md MED-XXX-SPECIALTY-expert.md
   ```

2. **Find-Replace Metadata** (5 minutes)
   - Agent ID, name, specialty, eTG sections, personas count, batch

3. **Update Expertise Profile** (10 minutes)
   - Copy eTG sections from this guide
   - Update AMC competencies

4. **Update Critical Errors** (5 minutes)
   - Replace cardiology errors with specialty errors

5. **Update Example Persona** (15 minutes)
   - Replace STEMI with specialty example
   - Ensure 300-500 lines, RAG citations, FRACP reviews

6. **Verify & Save** (3 minutes)
   - Check 600-900 lines
   - All 10 sections present
   - Save file

**Total Time**: ~40 minutes × 7 agents = **4-5 hours**

---

## ✅ Completion Checklist

After creating all 7 agents:

- [ ] All 7 files created in `/clinical-content-prds/agents/`
- [ ] Each file 600-900 lines (verify with `wc -l`)
- [ ] All follow 10-section structure
- [ ] RAG citations >0.65 in all examples
- [ ] FRACP reviews ≥2 in all examples
- [ ] Australian medical context throughout
- [ ] No cardiology references in non-cardiology agents
- [ ] Update `README.md` to show all 13 agents complete
- [ ] Run final count: `ls -1 MED-*.md | wc -l` should be 13

---

## 📊 Final Metrics (When Complete)

**Target**:
- 13 agent specification files
- ~10,300 total lines
- 360 personas specified
- 100% template compliance
- Ready for Claude Skills conversion

**Quality Gates**:
- ✅ All 10 sections present (every agent)
- ✅ 600-900 lines (every agent)
- ✅ RAG citations >0.65 (all examples)
- ✅ FRACP reviews ≥2 (all examples)
- ✅ Australian context (all agents)
- ✅ Critical errors defined (all agents)
- ✅ Learning loops (all agents)
- ✅ Cultural safety (all agents)

---

**Next Phase**: Convert to Claude Skills format → Test with pilot personas → Full generation

**Status**: This guide provides everything needed to complete the remaining 7 agent specification files
**Estimated Time**: 4-7 hours (depending on typing speed and attention to detail)

Good luck with the completion! All specifications are detailed above.
