# Clinical Advisor Review Package - Phase 0 PRD 1 (Clinical Accuracy)

**Purpose**: Obtain Clinical Advisor approval for all clinical content before Phase 1 implementation
**Prepared**: 2026-02-10
**Approval Deadline**: 5 business days from delivery (by 2026-02-17)
**Contact**: [Clinical Advisor Name/Email to be inserted]

---

## Executive Summary

This review package contains 5 clinical content documents created to address **Issues 1-4** identified in the AI_OSCE_CLINICAL_REVIEW_REPORT.md:

**Issues Addressed**:
1. **Simplified patient personas** lacking progressive disclosure → Fixed with DIVERSE_CLINICAL_SCENARIOS.md
2. **Generic AMC rubric** without detailed examples → Fixed with AMC_15_MARK_RUBRIC_EXPANDED.md
3. **RAG hallucinations** (no validation) → Fixed with RAG_VALIDATION_SPECIFICATION.md
4. **Lack of Golden Dataset** for AI vs human examiner calibration → Fixed with GOLDEN_DATASET_SPECIFICATION.md

**Additional Context**: AUSTRALIAN_HEALTHCARE_CONTEXT.md ensures Australian medical terminology and systems are used throughout.

---

## Documents for Review

### 1. Expanded AMC 15-Mark Rubric

**File**: `../clinical-content/AMC_15_MARK_RUBRIC_EXPANDED.md`
**Pages**: 273 lines (~10 pages)
**Review Time Estimate**: 2-3 hours

**Purpose**:
Provide AI Examiner with detailed, unambiguous scoring criteria for all 5 domains of AMC 15-mark OSCE rubric.

**Key Content**:
- **Communication Skills (0-3 marks)**: Detailed criteria for 3, 2, 1, 0 marks with examples
- **Clinical Reasoning (0-4 marks)**: Differential diagnosis quality, red flag identification, reasoning logic
- **Information Gathering (0-4 marks)**: Systematic history taking (SOCRATES, OPQRST), red flag questioning
- **Management (0-2 marks)**: Australian guideline-aligned management (eTG, NSW Health), safety-net advice
- **Professionalism (0-2 marks)**: AHPRA standards, patient dignity, informed consent
- **AMC Scoring Thresholds**: Pass ≥9/15 AND no critical errors AND minimum scores per domain
- **Critical Errors (Auto-Fail)**: Patient safety violations, professional misconduct, clinical incompetence
- **Common IMG Student Mistakes**: By domain (e.g., speaking too quickly, using medical jargon, premature closure)

**Questions for Clinical Advisor**:
1. ✅ Are scoring criteria aligned with official AMC Clinical Examination standards?
2. ✅ Are examples of "Excellent" (3/3, 4/4) vs "Satisfactory" (2/3, 2/4) vs "Poor" (0-1) realistic?
3. ✅ Are critical errors (auto-fail triggers) comprehensive and accurate?
   - Patient safety violations (failure to recognize STEMI, dangerous prescribing)
   - Professional misconduct (breach of confidentiality, discriminatory comments)
   - Clinical incompetence (complete failure to take history)
4. ✅ Are common IMG mistakes accurate based on your experience as AMC examiner?
5. ✅ Are RAG citations appropriate?
   - (AMC Handbook of Clinical Assessment, p.23-25: Communication Skills Marking Criteria)
   - (Talley & O'Connor's Clinical Examination, 8th ed, p.145-147: Chest pain differentials)

**Action Required**:
- [ ] **APPROVE** rubric as-is
- [ ] **REQUEST CHANGES** (specify which domain/criteria needs revision)

**Signature**: ________________
**Date**: ________________

---

### 2. Diverse Clinical Scenarios (3 Complete Scenarios)

**File**: `../clinical-content/DIVERSE_CLINICAL_SCENARIOS.md`
**Pages**: 348 lines (~12 pages)
**Review Time Estimate**: 1-2 hours

**Purpose**:
Provide AI Patient with diverse, culturally appropriate clinical scenarios that reflect Australian patient populations (Aboriginal, CALD, mainstream).

**Scenario 1: Aboriginal Patient - Community-Acquired Pneumonia**
- **Patient**: David Namatjira, 48M, Pitjantjatjara people, Alice Springs NT
- **Presentation**: CAP + bronchiectasis, penicillin allergy, social determinants (transport barriers, medication cost)
- **Cultural Considerations**: Stoic presentation, mistrust of mainstream health, family involvement, Aboriginal Health Worker liaison
- **Critical Actions**: Roxithromycin (penicillin allergy alternative per eTG), chest X-ray within 30 min, TB screening, PBS authority script for azithromycin prophylaxis
- **RAG Citations**: 4 citations (eTG Antibiotic 2.3.2, NSW Health Respiratory Infections Protocol 4.1, Talley & O'Connor p.267-269, AIHW Aboriginal Health Report 2023 p.45)
- **Difficulty**: Advanced (45% pass rate)

**Scenario 2: CALD Patient - Postnatal Depression**
- **Patient**: Fatima Hassan, 29F, Sudanese refugee, Arabic interpreter MANDATORY
- **Presentation**: Moderate-severe postnatal depression, passive suicidal ideation, trauma history, cultural stigma around mental illness
- **Cultural Considerations**: Interpreter use (TIS 131 450), trauma-informed care, reassurance baby won't be taken away, normalization of postnatal depression
- **Critical Actions**: EPDS scoring, suicide risk assessment, Perinatal Mental Health Service referral, social worker referral, sertraline 50mg (PBS listed, safe in breastfeeding)
- **RAG Citations**: 4 citations (eTG Psychotropic 2.3.1, Beyond Blue Clinical Practice Guidelines Section 4, NSW Health Perinatal Mental Health Protocol 2.2, RACGP Guidelines Section 3.1)
- **Difficulty**: Advanced (40% pass rate)

**Scenario 3: Obstetric Emergency - First Trimester Bleeding**
- **Patient**: Sarah Mitchell, 32F, Anglo-Australian, IVF pregnancy, previous miscarriage
- **Presentation**: 8 weeks gestation, heavy bleeding, tissue passage, high emotional distress
- **Communication Skills**: Breaking bad news, empathy phrases ("I can see this is very distressing"), avoid harmful phrases ("Don't worry, I'm sure it's fine")
- **Critical Actions**: Pelvic ultrasound URGENT (exclude ectopic), Rhesus status (Anti-D within 72 hours if Rh negative), sensitive explanation of miscarriage management options (expectant/medical/surgical), grief support (SANDS, Pink Elephants)
- **RAG Citations**: 4 citations (eTG Obstetrics Section 3.2, RANZCOG Guidelines Early Pregnancy Loss 2.1, Talley & O'Connor p.567-569, NSW Health Early Pregnancy Loss Protocol Section 4)
- **Difficulty**: Intermediate (60% pass rate)

**Questions for Clinical Advisor**:
1. ✅ Are clinical presentations medically accurate?
   - Symptoms, signs, red flags appropriate for each diagnosis?
2. ✅ Are progressive disclosure sequences realistic?
   - Does AI Patient reveal information logically (basic → intermediate → advanced)?
3. ✅ Are emotional states appropriate for each scenario?
   - GUARDED_STOIC (Aboriginal patient)
   - GUARDED_ASHAMED (CALD patient with postnatal depression)
   - ANXIOUS_DISTRESSED (first trimester bleeding)
4. ✅ Are critical actions aligned with Australian guidelines?
   - eTG Antibiotic 2.3.2 for penicillin allergy in CAP
   - eTG Psychotropic 2.3.1 for postnatal depression management
   - eTG Obstetrics Section 3.2 for first trimester bleeding
   - NSW Health protocols referenced correctly
5. ✅ Are cultural considerations authentic and appropriate?
   - Aboriginal: Social determinants, cultural mistrust, Aboriginal Health Worker involvement, Closing the Gap PBS exemption
   - CALD: Interpreter MANDATORY (TIS), trauma history, mental health stigma, refugee isolation
6. ✅ Are RAG citations valid?
   - All confidence >0.65 (to be validated during implementation)
   - Australian sources only (eTG, AMH, NSW Health, AMC Handbook, RANZCOG, RACGP)

**Action Required**:
- [ ] **APPROVE Scenario 1** (Aboriginal CAP)
- [ ] **APPROVE Scenario 2** (CALD postnatal depression)
- [ ] **APPROVE Scenario 3** (Obstetric emergency)
- [ ] **REQUEST CHANGES** (specify which scenario and what changes)

**Signature**: ________________
**Date**: ________________

---

### 3. RAG Validation Specification

**File**: `../clinical-content/RAG_VALIDATION_SPECIFICATION.md`
**Pages**: 465 lines (~17 pages)
**Review Time Estimate**: 30-45 minutes

**Purpose**:
Prevent AI Patient from providing medically incorrect or dangerous information by validating all medical claims against RAG (Retrieval Augmented Generation) chunks.

**Key Requirements**:
1. **Confidence Threshold**: >0.65 minimum (per PROJECT_CONSTRAINTS.md), >0.80 ideal for critical medical information
2. **Australian Source Filtering**: ONLY use eTG, AMH, PBS, AMC Handbook, RANZCOG, RACGP, NSW Health protocols
3. **Hallucination Detection**: Verify medication dosing, investigation timeframes, critical actions, red flags against RAG chunks
4. **Expert Validation Process**: 200 Golden Dataset scenarios validated by FRACGP/FACEM/FRANZCOG clinicians
5. **Quarterly Recalibration**: Re-validate 10% of scenarios every 3 months

**Validation Algorithm**:
```python
def validate_ai_response(response: str, rag_chunks: list) -> tuple[bool, list]:
    # Step 1: Confidence threshold filter (>0.65)
    # Step 2: Australian sources only
    # Step 3: Minimum 1 citation required
    # Step 4: Extract top 3 citations
    return (is_valid, citations_list)
```

**Questions for Clinical Advisor**:
1. ✅ Is confidence threshold >0.65 appropriate for medical accuracy?
   - Should critical information (medication dosing, red flags) require higher threshold (>0.80)?
2. ✅ Are approved Australian sources comprehensive?
   - eTG (all specialties), AMH, PBS, AMC Handbook, Talley & O'Connor, RANZCOG, RACGP, RACP, ACEM
   - Any sources missing?
3. ✅ Is hallucination detection mechanism adequate?
   - Verification of medication dosing against AMH
   - Verification of investigation timeframes against eTG/NSW Health protocols
   - Verification of red flags against evidence in RAG chunks
4. ✅ Should we reject all US-only sources (UpToDate, USMLE, ACOG, AHA)?
   - Even if confidence is high?
5. ✅ Is citation format appropriate?
   - Example: (Therapeutic Guidelines: Antibiotic, Section 2.3.2, 2024: CAP treatment in penicillin-allergic patients)

**Action Required**:
- [ ] **APPROVE** RAG validation specification
- [ ] **REQUEST CHANGES** (specify concerns with confidence threshold, source filtering, or hallucination detection)

**Signature**: ________________
**Date**: ________________

---

### 4. Golden Dataset Specification (200 Scenarios)

**File**: `../clinical-content/GOLDEN_DATASET_SPECIFICATION.md`
**Pages**: 635 lines (~23 pages)
**Review Time Estimate**: 1 hour

**Purpose**:
Ensure AI Examiner scoring accuracy matches human AMC examiners through rigorous validation of 200 expert-created OSCE scenarios.

**Dataset Composition**:
- **By Specialty**: 25 scenarios × 8 specialties = 200 total
  - Cardiology, Respiratory, Gastroenterology, Neurology, Endocrinology, Psychiatry, Surgery, ObGyn
- **By Difficulty**:
  - Foundation 40% (80 scenarios, target pass rate 75-85%)
  - Intermediate 40% (80 scenarios, target pass rate 60-70%)
  - Advanced 20% (40 scenarios, target pass rate 40-50%)
- **By Cultural Diversity**:
  - Aboriginal/Torres Strait Islander: 20% (40 scenarios)
  - CALD: 30% (60 scenarios)
  - Mainstream Australian: 50% (100 scenarios)

**7-Step Validation Process**:
1. **Clinical Expert Creation** (2 hours per scenario): FRACGP/FACEM/FRANZCOG create patient persona, progressive disclosure, critical actions
2. **AI Patient Simulation Test** (30 min per scenario): Medical student (PGY1-3) completes 8-minute OSCE
3. **AI Examiner Scoring** (5 min per scenario): AI scores using AMC 15-mark rubric
4. **Human Examiner Scoring** (15 min per scenario): 3 independent AMC-trained examiners score same transcript (blinded)
5. **Inter-Rater Reliability Testing**: AI vs Human variance ≤±2 marks (MANDATORY)
6. **Iteration** (if variance >±2): Adjust AI Examiner prompt, re-score
7. **Final Approval**: Clinical Advisor + Senior AMC Examiner sign-off

**Quarterly Recalibration**:
- Re-validate 20 random scenarios (10%) every 3 months
- Detect scoring drift (AI becoming harsher or more lenient over time)
- Correct via rubric updates

**Budget Estimate**:
- Clinical experts: $200/hr × 400 hrs = $80,000
- Medical student actors: $50/hr × 100 hrs = $5,000
- Human examiner panel: $150/hr × 150 hrs = $22,500
- Cultural consultants: $150/hr × 40 hrs = $6,000
- **Total**: ~$113,500 for Golden Dataset creation

**Questions for Clinical Advisor**:
1. ✅ Is 7-step validation process feasible and rigorous enough?
2. ✅ Is ±2 marks variance acceptable for AI vs human examiner?
   - Or should tolerance be tighter (±1 mark)?
3. ✅ Is sample size (200 scenarios) sufficient for calibration?
   - 25 per specialty seems reasonable?
4. ✅ Can you recommend FRACGP/FACEM/FRANZCOG fellows for validation panel?
   - Need 5 clinical experts with AMC examiner experience
5. ✅ Is quarterly recalibration frequency appropriate?
   - Or should we recalibrate more frequently (monthly)?
6. ✅ Is budget estimate ($113,500) realistic for your institution?
   - Do these hourly rates align with standard fees?

**Action Required**:
- [ ] **APPROVE** Golden Dataset specification
- [ ] **REQUEST CHANGES** (specify concerns with validation process, sample size, or budget)
- [ ] **PROVIDE REFERRALS** for FRACGP/FACEM/FRANZCOG validation panel (if approving)

**Signature**: ________________
**Date**: ________________

---

### 5. Australian Healthcare Context

**File**: `../clinical-content/AUSTRALIAN_HEALTHCARE_CONTEXT.md`
**Pages**: 700+ lines (~25 pages)
**Review Time Estimate**: 30-45 minutes

**Purpose**:
Ensure AI Patient and AI Examiner understand Australian-specific healthcare delivery, terminology, and cultural context.

**Key Content**:
- **Medicare & PBS**: Item numbers (ECG 11700, chest X-ray 58503), PBS authority prescriptions, co-payment exemptions (Closing the Gap)
- **Emergency Services**: 000 (NOT 911), ambulance costs by state (NSW $401, QLD free, VIC $1,234)
- **AHPRA Standards**: Mandatory reporting (sexual misconduct, intoxication, significant departure from standards), informed consent requirements
- **NSW Health Protocols**: EPAU for early pregnancy complications, MET call criteria, antenatal screening (OGTT, GBS, Anti-D)
- **Rural & Remote**: RFDS (Royal Flying Doctor Service) aeromedical retrievals, telehealth, workforce shortages
- **Cultural Considerations**:
  - Aboriginal: Sorry Business, shame, family decision-making, traditional healing, historical trauma
  - CALD: TIS interpreter (131 450), avoid family member interpreters, cultural stigma variations
- **Medical Terminology**: Paracetamol (NOT acetaminophen), salbutamol (NOT albuterol), adrenaline (NOT epinephrine), 000 (NOT 911), GP (NOT family doctor), ED (NOT ER)
- **Units of Measurement**: mmol/L for glucose (NOT mg/dL), fasting glucose 3.5-5.5 mmol/L

**Auto-Fail Triggers for Non-Australian Context**:
- ❌ Student says "Call 911" (should be 000)
- ❌ Student uses acetaminophen (should be paracetamol)
- ❌ Student uses mg/dL without conversion (should use mmol/L)
- ❌ Student uses family member as interpreter for CALD patient (should use TIS)

**Questions for Clinical Advisor**:
1. ✅ Are Medicare item numbers correct and up-to-date?
   - ECG 11700 ($20.00 rebate)
   - Chest X-ray 58503 ($37.05 rebate)
   - FBC 65070 ($16.90 rebate)
2. ✅ Are PBS restrictions accurately described?
   - Biologics require authority prescription
   - First-line SSRIs (sertraline, escitalopram) no authority required
3. ✅ Are AHPRA mandatory reporting triggers correct?
   - Sexual misconduct, intoxication, significant departure from standards
4. ✅ Are cultural considerations appropriate and non-stereotyping?
   - Aboriginal: Sorry Business, shame, family decision-making
   - CALD: TIS interpreter use, cultural stigma variations by background
5. ✅ Are Australian terminology and spelling correct throughout?
   - Paracetamol, salbutamol, adrenaline, haemoglobin, anaemia, oesophagus, paediatric
6. ✅ Are units of measurement (mmol/L) correctly specified?
   - Fasting glucose 3.5-5.5 mmol/L (NOT 63-99 mg/dL)

**Action Required**:
- [ ] **APPROVE** Australian Healthcare Context document
- [ ] **REQUEST CHANGES** (specify incorrect item numbers, PBS restrictions, AHPRA standards, or cultural considerations)

**Signature**: ________________
**Date**: ________________

---

## Approval Process

### Timeline

| Day | Activity | Responsible |
|-----|----------|-------------|
| **Day 1-2** | Prepare all documents (COMPLETE) | Development Team |
| **Day 3** | Submit to Clinical Advisor | Project Manager |
| **Day 3-7** | Clinical Advisor review (5 business days) | Clinical Advisor |
| **Day 8** | Approval received OR iteration begins | Clinical Advisor |
| **Day 9** | Proceed to Phase 0 PRD 2 (Security Hardening) | Development Team |

**Approval Deadline**: 5 business days from delivery (by **2026-02-17**)

### Approval Format

**Email Approval** OR **Written Sign-Off Document** acceptable.

**Required Statement**:
> "I, [Name], [Credentials], approve the clinical content prepared for the AI OSCE Simulation system Phase 0 PRD 1 (Clinical Accuracy). I confirm that all medical information is accurate, aligned with AMC Clinical Examination standards, and appropriate for Australian medical practice as of February 2026."
>
> **Documents Approved**:
> - [ ] AMC_15_MARK_RUBRIC_EXPANDED.md
> - [ ] DIVERSE_CLINICAL_SCENARIOS.md (all 3 scenarios)
> - [ ] RAG_VALIDATION_SPECIFICATION.md
> - [ ] GOLDEN_DATASET_SPECIFICATION.md
> - [ ] AUSTRALIAN_HEALTHCARE_CONTEXT.md
>
> **Signature**: ________________
> **Name**: ________________
> **Credentials**: ________________
> **Date**: ________________

### If Changes Requested

**Process**:
1. Clinical Advisor specifies which document and which section needs revision
2. Development team iterates on specific sections (timeline: 1-2 days)
3. Re-submit changed sections only (not entire package)
4. Clinical Advisor re-reviews (timeline: 1-2 days)
5. Approval or further iteration

**Maximum 2 iterations expected** before final approval.

---

## Next Steps After Approval

### If Approved

1. ✅ **Clinical Advisor approves** → Proceed to **Phase 0 PRD 2: Security Hardening** (5 services + 21 tests)
2. Document approval in project records
3. Begin PRD 2 implementation immediately (no gap)

### If Changes Requested

1. ❌ **Clinical Advisor requests changes** → Iterate on specific sections, re-submit
2. Timeline extends by 2-4 days per iteration
3. Block PRD 2 until approval received

---

## Critical Path Impact

**BLOCKING**: Clinical Advisor approval blocks:
- ✋ **Phase 0 PRD 2** (Security Hardening)
- ✋ **Phase 0 PRD 3** (Database Optimization)
- ✋ **ALL of Phase 1** (4-week implementation sprint)

**If approval delayed by 1 week** → Entire Phase 0 and Phase 1 delayed by 1 week

**Mitigation**:
- Start PRD 2 (Security Hardening) in parallel at risk (can rollback if clinical content rejected)
- Maintain close communication with Clinical Advisor during review period
- Offer to present documents in person if questions arise

---

## Contact Information

**Clinical Advisor**: [Name to be inserted]
**Email**: [Email to be inserted]
**Phone**: [Phone to be inserted]
**Institution**: [Institution to be inserted]
**AMC Examiner Since**: [Year to be inserted]

**Development Team Contact**:
**Project Manager**: [Name to be inserted]
**Email**: [Email to be inserted]
**Phone**: [Phone to be inserted]

---

## Summary Checklist for Clinical Advisor

**Before approving, please verify**:
- [ ] All 5 documents reviewed thoroughly
- [ ] Medical accuracy confirmed (diagnoses, management, medications, doses)
- [ ] AMC Clinical Examination standards alignment confirmed
- [ ] Australian healthcare context correct (Medicare, PBS, AHPRA, 000, terminology)
- [ ] Cultural considerations appropriate (Aboriginal, CALD)
- [ ] RAG citations valid (eTG, AMH, AMC Handbook, NSW Health)
- [ ] No American terminology detected (acetaminophen, 911, ER, mg/dL)
- [ ] Golden Dataset validation process feasible
- [ ] Budget estimate reasonable ($113,500)
- [ ] Quarterly recalibration plan acceptable
- [ ] Approval statement signed and dated

**Thank you for your expert review. Your approval is critical to ensuring clinical safety and accuracy in the AI OSCE Simulation system.**

---

**End of Clinical Advisor Review Package** - Ready for submission
