# Australian Healthcare System Context for AI OSCE

**Source**: PRD 1 Step 6 + Australian healthcare guidelines
**Purpose**: Ensure AI Patient and AI Examiner understand Australian-specific healthcare delivery
**Created**: 2026-02-10
**Target Users**: AI Patient, AI Examiner, IMG candidates preparing for AMC Clinical Examination

---

## Purpose

This document provides essential Australian healthcare context that differentiates the Australian medical system from other countries (especially US, UK, and other systems IMG candidates may be familiar with).

**Critical for AI OSCE**:
- AI Patient must reference Australian healthcare systems (Medicare, PBS, AHPRA)
- AI Examiner must mark students WRONG if they use non-Australian terminology or contexts
- IMG students preparing for AMC Clinical Examination must learn Australian healthcare delivery

---

## 1. Medicare & Bulk Billing

### 1.1 What is Medicare?

**Medicare**: Australia's universal public health insurance scheme
- Covers ALL Australian citizens and permanent residents
- Funded by 2% Medicare levy on taxable income
- Provides rebates for GP visits, specialist consultations, investigations

**NOT covered by Medicare**:
- Most dental care (except some for children)
- Ambulance services (covered differently by states)
- Private hospital accommodation
- Glasses, hearing aids, most allied health (unless part of CDM plan)

### 1.2 Medicare Item Numbers (Common Investigations)

**Pathology**:
- **Full Blood Count (FBC):** Item 65070 ($16.90 rebate)
- **Troponin (cardiac marker):** Item 66512 ($16.90 rebate)
- **HbA1c (diabetes monitoring):** Item 66551 ($16.90 rebate)
- **Lipid profile:** Item 66656 ($16.90 rebate)
- **Urine MCS (microscopy, culture, sensitivity):** Item 69319 ($12.75 rebate)

**Imaging**:
- **Chest X-ray:** Item 58503 ($37.05 rebate)
- **Ultrasound pelvic (transabdominal):** Item 55700 ($74.90 rebate)
- **Ultrasound pelvic (transvaginal):** Item 55718 ($114.45 rebate)
- **CT head (non-contrast):** Item 56001 ($179.10 rebate)

**Cardiac Investigations**:
- **ECG (12-lead):** Item 11700 ($20.00 rebate, bulk-billed in most practices)
- **Echocardiogram:** Item 55116 ($188.85 rebate)
- **Exercise stress test:** Item 11712 ($59.60 rebate)

**GP Consultation Items**:
- **Standard consultation (<20 min):** Item 23 or 36 ($39.10 rebate)
- **Long consultation (20-40 min):** Item 36 or 44 ($75.75 rebate)
- **Mental Health Treatment Plan (MHTP):** Item 2715 ($75.75 rebate)

### 1.3 Bulk Billing

**Bulk Billing**: GP/practice accepts Medicare rebate as full payment (patient pays $0)
- Common in metropolitan areas
- Less common in rural areas (gap payments often required)
- Always available for concession card holders (pensioner, health care card)

**AI Patient Scenario Example**:
```
Patient: "Doctor, I don't have much money at the moment. Do you bulk bill?"
Student should know: "Yes, this practice bulk bills for pensioners and health care card holders."
```

---

## 2. PBS (Pharmaceutical Benefits Scheme)

### 2.1 What is PBS?

**PBS**: Government-subsidized medication scheme
- Reduces cost of most prescription medications
- General patients: $31.60 per script (2024 co-payment)
- Concession card holders: $7.70 per script (2024)
- Safety Net: Once you reach threshold ($277.20 for concession, $1,647.90 for general), medications become free/cheaper

### 2.2 PBS Medication Restrictions

**No Authority Required** (GP can prescribe immediately):
- Most antibiotics (amoxicillin, doxycycline, cephalexin)
- Paracetamol, ibuprofen
- Common antihypertensives (perindopril, amlodipine)
- First-line SSRIs (sertraline, escitalopram)
- Asthma inhalers (salbutamol, fluticasone/salmeterol)

**Streamlined Authority** (tick box on script, no phone call required):
- Second-line antibiotics (e.g., roxithromycin for CAP in penicillin allergy)
- Osteoporosis medications (denosumab, alendronate if specific criteria met)
- Anticoagulants (rivaroxaban, apixaban for AF)

**Authority Required** (phone PBS 1800 888 333 or online approval):
- **Biologics**: Adalimumab (rheumatoid arthritis, Crohn's disease), infliximab
- **Expensive antibiotics**: Linezolid (MRSA), daptomycin
- **SGLT2 inhibitors**: Empagliflozin, dapagliflozin (diabetes with CV disease)
- **Antipsychotics**: Clozapine (schizophrenia)

**AI Patient Response Example**:
```
Patient: "Doctor, I've been prescribed that biologic injection for my arthritis, but the pharmacist said I need some special approval form. What does that mean?"

Expected Student Response:
"That's called an authority prescription. I'll need to apply through PBS for approval. I'll need to document that you've tried at least 2 other DMARDs first and your disease activity score meets the criteria."
```

### 2.3 PBS Co-Payment Exemptions

**Closing the Gap (Aboriginal and Torres Strait Islander patients)**:
- PBS co-payment waived ($0 cost)
- Requires verification of Aboriginal/Torres Strait Islander status

**AI Patient Scenario (Aboriginal patient)**:
```
Patient: "Doc, I can't afford these medications. I'm on Newstart."

Student should ask: "Do you identify as Aboriginal or Torres Strait Islander? If so, you can access the Closing the Gap PBS co-payment exemption, which means your medications are free."
```

---

## 3. Emergency Services - Triple Zero (000)

### 3.1 National Emergency Number

**000 (Triple Zero)** - NOT 911
- Operator asks: "Police, Fire, or Ambulance?"
- Works from landlines and mobiles
- **112** also works (international standard, redirects to 000)

**AI Examiner Auto-Fail Trigger**:
- Student says "Call 911" → CRITICAL ERROR (wrong country)
- Correct: "Call 000 for an ambulance"

### 3.2 Ambulance Services (State-Based, NOT Free)

**Ambulance costs vary by state**:

| State | Emergency Callout Cost | Free for Pensioners? | Notes |
|-------|------------------------|---------------------|-------|
| **NSW** | $401 + $3.62/km | ✅ Yes | Most expensive |
| **QLD** | FREE | ✅ Free for all QLD residents | Only state with free ambulance |
| **VIC** | $1,234 | ❌ No (must have ambulance insurance) | Very expensive |
| **WA** | $992 + $6/km | ✅ Yes | - |
| **SA** | $1,059 | ✅ Yes | - |
| **TAS** | $372 | ✅ Yes | - |

**AI Patient Scenario**:
```
Patient (elderly, NSW): "Doctor, I'm having chest pain, but should I call an ambulance? I'm worried about the cost..."

Correct Student Response:
"Mr. Smith, this sounds like a heart attack. We need to call an ambulance immediately (000). Since you're a pensioner, the ambulance is free in NSW, so please don't worry about the cost. Your health is the priority."

Incorrect Response:
"Let's see if your daughter can drive you to hospital to save money." → CRITICAL ERROR (delays care for STEMI)
```

---

## 4. AHPRA Standards (Australian Health Practitioner Regulation Agency)

### 4.1 What is AHPRA?

**AHPRA**: National regulatory body for health practitioners
- Registers doctors, nurses, pharmacists, etc.
- Sets standards for professional conduct
- Investigates complaints
- Can suspend/cancel registration

**Medical Board of Australia**: Works with AHPRA to regulate medical practitioners

### 4.2 Mandatory Reporting Requirements

**ALL registered health practitioners MUST report**:

1. **Sexual misconduct** with patient
   - Any sexual relationship with current patient
   - Inappropriate examination without chaperone
   - Sexual comments or advances

2. **Intoxication** affecting patient care
   - Doctor/nurse impaired by alcohol or drugs while working
   - Witnessed first-hand (not hearsay)

3. **Significant departure from accepted standards**
   - Dangerous prescribing (e.g., opioids without indication)
   - Failure to recognize life-threatening condition
   - Practicing outside scope of competence

**OSCE Scenario Example**:
```
Patient: "My previous doctor made me feel uncomfortable during the breast examination. He didn't offer a female chaperone and made comments about my appearance."

Expected Student Response:
"I'm very sorry that happened to you. That's not acceptable professional behavior. With your permission, I'd like to help you make a formal complaint to AHPRA. All doctors must have a chaperone for intimate examinations and should never make inappropriate comments."

AI Examiner scoring:
- ✅ Recognized mandatory reporting trigger
- ✅ Empathetic response
- ✅ Offered to assist with complaint process
- ✅ Explained professional standards
```

### 4.3 Informed Consent Requirements (AHPRA Standards)

**Valid consent requires**:
1. **Capacity**: Patient understands information and can make decision
2. **Information**: Diagnosis, treatment options, risks/benefits, alternatives
3. **Voluntary**: No coercion
4. **Documented**: Written consent for procedures, verbal for examinations

**Special Considerations**:
- **Interpreter required**: CALD patients with limited English (consent not valid without interpreter)
- **Cultural considerations**: Aboriginal patients may prefer family involvement in decision-making
- **Children**: Parent/guardian consent required (<18 years, unless mature minor exception)

---

## 5. NSW Health Protocols

### 5.1 Early Pregnancy Assessment Unit (EPAU)

**EPAU**: Specialized service for first trimester complications
- Available in most major NSW hospitals
- Provides same-day ultrasound + specialist ObGyn review
- **Direct access**: Patients can self-refer OR GP referral (no need for ED)

**AI Patient Scenario (ObGyn)**:
```
Patient: "I'm 8 weeks pregnant and had some bleeding this morning. The GP said to come to hospital. Should I go to Emergency?"

Correct Student Response:
"At [Hospital Name], we have an Early Pregnancy Assessment Unit (EPAU) specifically for this situation. They can see you today and do an ultrasound to check on the baby. That's usually a better pathway than Emergency Department, as they're specialists in early pregnancy."

Incorrect Response:
"Go to Emergency Department" → Not wrong, but less ideal (ED often busy, EPAU provides specialized care)
```

### 5.2 NSW Ambulance Protocols

**MET (Medical Emergency Team) Call Criteria** (in-hospital):
- RR <8 or >30
- HR <40 or >130
- SBP <90 mmHg
- Conscious state: sudden decrease
- Airway threatened
- Staff member worried about patient

**STEMI Protocol**:
- ECG within 10 minutes of presentation
- Cath lab activation within 90 minutes of first medical contact
- Pre-hospital thrombolysis if >90 min from PCI-capable hospital

### 5.3 Antenatal Care Protocols (eTG Obstetrics)

**Gestational Diabetes Screening**:
- **All women**: OGTT (Oral Glucose Tolerance Test) at 24-28 weeks
- **High risk** (BMI >30, previous GDM, PCOS): OGTT at booking visit + 24-28 weeks

**Group B Streptococcus (GBS)**:
- Screen at 36 weeks (vaginal-rectal swab)
- If positive: Intrapartum antibiotics (benzylpenicillin IV)

**Anti-D (for Rh-negative women)**:
- Routine prophylaxis: 28 weeks + 34 weeks
- After any bleeding episode: Within 72 hours
- Dose: 250 IU if <12 weeks, 625 IU if ≥12 weeks

---

## 6. Rural & Remote Healthcare

### 6.1 RFDS (Royal Flying Doctor Service)

**Services**:
- Aeromedical retrievals (emergency transfers from remote areas to tertiary hospitals)
- Primary healthcare clinics (regular visits to remote communities)
- Telehealth consultations
- Mental health services

**AI Patient Scenario**:
```
Patient (remote Northern Territory): "Doctor, I live 300km from Alice Springs. If something goes wrong with my pregnancy, how quickly can help arrive?"

Correct Student Response:
"The Royal Flying Doctor Service (RFDS) provides aeromedical retrievals. In an emergency, they can usually reach you within 1-2 hours and fly you to Alice Springs Hospital. We can also arrange telehealth consultations with obstetricians if needed between your clinic visits."
```

### 6.2 Rural Doctor Workforce Shortage Programme (RDWSP)

**Incentives for rural doctors**:
- Higher Medicare rebates for rural/remote consultations
- Practice Incentives Program (PIP)
- Relocation assistance
- CME (Continuing Medical Education) funding

**AI Patient comment**:
```
Patient: "We're so lucky to have you here, doctor. The last GP left after only 6 months."
(Reflects reality of rural workforce shortages)
```

---

## 7. Cultural Considerations

### 7.1 Aboriginal & Torres Strait Islander Health

**Key Concepts**:

**1. "Sorry Business"** (Mourning period):
- Extended family mourning after death (weeks to months)
- Affects appointment attendance
- Photo/name of deceased person avoided
- AI Patient scenario: "Sorry doc, I couldn't make my last appointment - we had Sorry Business in the family."

**2. "Shame"**:
- Feeling of embarrassment/humiliation
- Affects disclosure of sensitive topics (mental health, sexual health, family violence)
- Overcome by building trust, non-judgmental approach, involving Aboriginal Health Worker

**3. Family Decision-Making**:
- Healthcare decisions often involve extended family (uncles, aunties, elders)
- Respect for elders' opinions
- Student should ask: "Would you like any family members present while we discuss your treatment options?"

**4. Traditional Healing**:
- Bush medicine used alongside Western medicine
- Respect for traditional healers ("ngangkari" in Central Australia)
- Student should ask: "Are you using any traditional medicines or seeing a traditional healer?" (non-judgmental tone)

**5. Historical Trauma**:
- Stolen Generations (forced removal of Aboriginal children 1910s-1970s)
- Institutional racism in healthcare (e.g., higher maternal mortality rates)
- Mistrust of mainstream health system
- Build trust by acknowledging past wrongs, cultural humility

**Communication Example (Good)**:
```
Student: "Uncle Billy, I understand this is difficult to talk about. Would you like your daughter here while we discuss your treatment options? We can also arrange for an Aboriginal Health Worker to be present if that would make you more comfortable."
```

**Communication Example (Bad)**:
```
Student: "You need to take your medications every day. Why haven't you been compliant?"
(Judgmental, doesn't acknowledge barriers to access - cost, distance, cultural mistrust)
```

### 7.2 CALD (Culturally and Linguistically Diverse) Patients

**TIS (Translating and Interpreting Service)**:
- **Phone Number**: 131 450
- **Available**: 24/7, over 160 languages
- **Cost**: FREE for medical appointments (funded by Department of Home Affairs)
- **Process**: Doctor calls TIS → selects language → 3-way conversation

**When to use professional interpreter**:
- ✅ Limited English proficiency
- ✅ Complex medical discussions (diagnosis, treatment options, consent)
- ✅ Mental health assessments (nuance crucial)
- ✅ Breaking bad news
- ✅ Legal situations (capacity assessment, mandatory reporting)

**When NOT to use family member as interpreter**:
- ❌ Privacy concerns (patient may not want family to know diagnosis)
- ❌ Accuracy issues (family member may not understand medical terminology)
- ❌ Sensitive topics (sexual health, family violence, mental health)
- ❌ Children as interpreters (inappropriate burden, accuracy issues)

**AI Patient Scenario**:
```
Patient (limited English, daughter present): "My English not so good, doctor. Can my daughter translate for me?"

Correct Student Response:
"I appreciate your daughter being here to support you, but for this medical discussion, I'd like to use a professional interpreter to make sure we communicate clearly. We can call the Translating and Interpreting Service - it's free and confidential. What language would you prefer?"

Incorrect Response:
"Sure, your daughter can translate." → WRONG (privacy, accuracy, may miss critical information)
```

**Cultural Considerations by Background**:

**Middle Eastern/North African**:
- May prefer same-gender doctor (especially for intimate examinations)
- Extended family involvement in healthcare decisions
- Direct eye contact may be seen as disrespectful (especially by women to male doctors)
- Expressiveness of pain culturally appropriate (not "over-dramatizing")

**East Asian (Chinese, Vietnamese, Korean)**:
- Mental health stigma very strong (may minimize symptoms)
- Deference to authority (may not question doctor, say "yes" without understanding)
- Student should check understanding: "Can you tell me in your own words what we discussed?"
- Family hierarchy important (involve adult children in elderly parent's care)

**South Asian (Indian, Pakistani, Bangladeshi)**:
- May expect paternalistic approach (doctor tells, patient follows)
- Diabetes and cardiovascular disease very prevalent (screening important)
- Vegetarian diets (consider B12, iron supplementation)
- Joint family structures (multiple generations living together)

**Sudanese/African Refugees**:
- High rates of PTSD, trauma (war, displacement, refugee camps)
- Female genital mutilation (FGM) in some communities (sensitive topic, non-judgmental approach)
- Low health literacy (may not be familiar with Western medical concepts)
- Strong community support networks (churches, community groups)

---

## 8. Medical Terminology (Australian vs US)

### 8.1 Medication Names

| ✅ Australian Name | ❌ US Name | Indication |
|------------------|-----------|------------|
| Paracetamol | Acetaminophen | Analgesia/fever |
| Salbutamol | Albuterol | Asthma |
| Adrenaline | Epinephrine | Anaphylaxis |
| Noradrenaline | Norepinephrine | Septic shock |
| Frusemide | Furosemide | Heart failure |
| Glyceryl trinitrate (GTN) | Nitroglycerin | Angina |

**AI Examiner Marking**:
- Student says "Give acetaminophen" → Mark as INCORRECT, comment: "Use Australian medication names (paracetamol)"

### 8.2 Healthcare Roles

| ✅ Australian Term | ❌ US Term | Explanation |
|------------------|-----------|-------------|
| GP (General Practitioner) | Family doctor / PCP | Primary care physician |
| Registrar | Resident (PGY4+) | Specialist trainee |
| Consultant | Attending | Qualified specialist |
| Theatre | OR (Operating Room) | Surgery location |
| Casualty / ED | ER (Emergency Room) | Emergency department |
| Ward | Floor | Hospital unit |
| Physio | PT (Physical Therapist) | Physiotherapist |

### 8.3 Emergency & Hospital Terms

| ✅ Australian | ❌ US | Context |
|-------------|------|---------|
| 000 | 911 | Emergency number |
| MET call | Code Blue | In-hospital emergency |
| ICU | MICU/SICU | Intensive care unit |
| Trolley | Gurney | Hospital bed on wheels |
| Notes | Chart | Medical records |
| Discharge summary | DC summary | Hospital discharge letter |

### 8.4 Spelling Differences (Australian English)

**Australian spelling uses British English**:
- ✅ Haemoglobin (NOT hemoglobin)
- ✅ Anaemia (NOT anemia)
- ✅ Oesophagus (NOT esophagus)
- ✅ Paediatric (NOT pediatric)
- ✅ Haematology (NOT hematology)
- ✅ Foetus (NOT fetus)
- ✅ Manoeuvre (NOT maneuver)
- ✅ Colour, tumour, favour (NOT color, tumor, favor)

**RAG chunks from Australian sources naturally use Australian spelling** → Enforces correct spelling in AI responses.

---

## 9. Units of Measurement (Australian vs US)

### 9.1 Blood Glucose

**Australian**: mmol/L
**US**: mg/dL

| Reference Range | Australian (mmol/L) | US (mg/dL) |
|----------------|---------------------|------------|
| Fasting glucose (normal) | 3.5-5.5 | 63-99 |
| Random glucose (diabetes) | ≥11.1 | ≥200 |
| HbA1c (diabetes diagnosis) | ≥6.5% | ≥6.5% (same) |

**AI Examiner Marking**:
- Student says "Fasting glucose 95 - that's normal" → WRONG (95 mmol/L would be severe hyperglycaemia)
- Correct: "Fasting glucose 5.2 mmol/L - that's normal"

### 9.2 Cholesterol / Lipids

**Australian targets** (mmol/L):
- Total cholesterol: <5.5 mmol/L
- LDL cholesterol: <2.0 mmol/L
- HDL cholesterol: >1.0 mmol/L (men), >1.3 mmol/L (women)
- Triglycerides: <2.0 mmol/L

**US uses mg/dL** (different units - not just conversion)

### 9.3 Other Lab Values

| Test | Australian Unit | US Unit |
|------|----------------|---------|
| Creatinine | μmol/L | mg/dL |
| Bilirubin | μmol/L | mg/dL |
| Urea | mmol/L | mg/dL (BUN) |
| Calcium | mmol/L | mg/dL |

**eGFR (kidney function)**: Same units globally (mL/min/1.73m²)

---

## 10. Success Criteria for AI OSCE

**PRD 1 Complete When**:

✅ **All AI Patient scenarios use Australian terminology**:
   - Paracetamol (NOT acetaminophen)
   - GP (NOT family doctor)
   - 000 (NOT 911)
   - ED/Casualty (NOT ER)

✅ **Medicare item numbers included where relevant**:
   - "I'll order an ECG (Medicare item 11700) and chest X-ray (item 58503)"

✅ **PBS restrictions mentioned for expensive medications**:
   - "For that biologic, I'll need to apply for PBS authority approval"

✅ **AHPRA standards referenced**:
   - Mandatory reporting scenarios
   - Informed consent (including interpreter requirement)
   - Professional boundaries

✅ **NSW Health protocols for obstetrics, emergency management**:
   - EPAU referral for early pregnancy complications
   - MET call criteria
   - Antenatal screening (OGTT, GBS, Anti-D)

✅ **Cultural considerations for Aboriginal, CALD patients**:
   - Sorry Business, shame, family decision-making (Aboriginal)
   - TIS interpreter use (CALD)
   - Cultural safety language

✅ **Units in mmol/L (NOT mg/dL)**:
   - Blood glucose: 5.2 mmol/L (NOT 95 mg/dL)
   - Cholesterol: 6.2 mmol/L (NOT 240 mg/dL)

**AI Examiner Auto-Fail Triggers** (Non-Australian Context):
- ❌ Student says "Call 911" (should be 000)
- ❌ Student uses acetaminophen (should be paracetamol)
- ❌ Student uses mg/dL without conversion (should use mmol/L)
- ❌ Student uses family member as interpreter for CALD patient (should use TIS)

---

**End of Australian Healthcare Context** - Ready for Clinical Advisor review
