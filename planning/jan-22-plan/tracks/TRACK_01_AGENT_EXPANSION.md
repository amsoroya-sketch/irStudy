# Track 1: Agent Expansion
**Duration:** Weeks 1-10
**Goal:** Expand 8 medical expert agents from 115 LOC to 850+ LOC each
**Total Code Increase:** ~5,880 LOC (735 LOC × 8 agents)
**Status:** 🟡 WEEK 1 IN PROGRESS

---

## Overview

This track focuses on transforming basic medical expert agents into comprehensive, production-ready specialists capable of:
- Generating AMC-level MCQs with RAG citations
- Creating 8-minute OSCE stations with marking rubrics
- Providing specialty-specific clinical tools
- Ensuring 100% Australian guideline compliance

---

## Agent Expansion Schedule

### Weeks 1-2: MED-009 Psychiatry (First Agent)
**Status:** 🟢 ACTIVE
**Progress:** 0% → 100%
**Timeline:** 2026-01-24 to 2026-02-07

#### Week 1 Deliverables (50% - 400 LOC)
- [x] Mental State Examination framework (120 LOC)
- [x] Risk assessment tools (100 LOC)
- [x] Australian Mental Health Act compliance (80 LOC)

#### Week 2 Deliverables (100% - 850 LOC)
- [ ] Psychiatric medication side effects (180 LOC)
- [ ] ECT counseling framework (120 LOC)
- [ ] 17 psychiatry topics coverage (150 LOC)

**Why Psychiatry First:**
- High complexity (MSE, risk assessment, Mental Health Act)
- Establishes template for other agents
- Critical for AMC exam (common topic)
- Lessons learned apply to all agents

**Related Document:** [MED-009 Psychiatry Expansion Plan](../agents/MED_009_PSYCHIATRY_EXPANSION.md)

---

### Weeks 3-4: MED-003 Gastroenterology + MED-004 Endocrinology
**Status:** ⏳ PENDING
**Progress:** 0% → 100% each
**Timeline:** 2026-02-08 to 2026-02-21

#### MED-003 Gastroenterology (850 LOC)

**Week 3: 50% Complete (400 LOC)**
- [ ] GI scoring tools (120 LOC)
  - Glasgow-Blatchford score (upper GI bleeding)
  - Rockall score (rebleeding risk)
  - MELD score (liver disease severity)
  - Child-Pugh classification
  - NAFLD fibrosis score

- [ ] Liver disease assessment (140 LOC)
  - Cirrhosis diagnosis and complications
  - Hepatic encephalopathy grading
  - Ascites management
  - Varices screening and management
  - Hepatorenal syndrome

- [ ] Inflammatory bowel disease (140 LOC)
  - Crohn's disease vs. ulcerative colitis
  - Disease activity scores (Harvey-Bradshaw, Mayo)
  - Medication management (5-ASA, biologics)
  - Surgery indications

**Week 4: 100% Complete (850 LOC)**
- [ ] Upper GI disorders (150 LOC)
  - GERD, peptic ulcer disease
  - H. pylori testing and treatment
  - Barrett's esophagus surveillance

- [ ] Lower GI disorders (150 LOC)
  - IBS, diverticular disease
  - Colorectal cancer screening
  - Hemorrhoids, anal fissures

- [ ] Pancreatic and biliary (150 LOC)
  - Acute and chronic pancreatitis
  - Gallstones and cholecystitis
  - Pancreatic cancer red flags

#### MED-004 Endocrinology (850 LOC)

**Week 3: 50% Complete (400 LOC)**
- [ ] Diabetes management tools (140 LOC)
  - Type 1 vs. Type 2 diabetes
  - HbA1c targets (individualized)
  - Medication algorithms (metformin → SGLT2i → GLP-1)
  - Insulin initiation and titration
  - Diabetic complications screening

- [ ] Thyroid disease (130 LOC)
  - Hypothyroidism vs. hyperthyroidism
  - Thyroid function test interpretation
  - Levothyroxine dosing
  - Graves' disease, thyroid nodules

- [ ] Lipid management (130 LOC)
  - Cardiovascular risk assessment
  - Statin therapy (primary and secondary prevention)
  - Non-statin therapies (ezetimibe, PCSK9 inhibitors)
  - Familial hypercholesterolemia

**Week 4: 100% Complete (850 LOC)**
- [ ] Adrenal disorders (150 LOC)
  - Addison's disease, Cushing's syndrome
  - Primary aldosteronism
  - Pheochromocytoma

- [ ] Pituitary disorders (150 LOC)
  - Hypopituitarism, hyperprolactinemia
  - Acromegaly
  - Diabetes insipidus

- [ ] Bone and mineral (150 LOC)
  - Osteoporosis screening and treatment
  - Hypercalcemia, hypocalcemia
  - Vitamin D deficiency

**Progress Target (End of Week 4):**
- ✅ 3 agents complete: MED-009, MED-003, MED-004
- ✅ 2,550 LOC added (850 × 3)
- ✅ 30% of total agent expansion complete

---

### Weeks 5-6: MED-005 Neurology + MED-006 Emergency Medicine
**Status:** ⏳ PENDING
**Progress:** 0% → 100% each
**Timeline:** 2026-02-22 to 2026-03-07

#### MED-005 Neurology (850 LOC)

**Week 5: 50% Complete (400 LOC)**
- [ ] Stroke assessment tools (140 LOC)
  - NIHSS (National Institutes of Health Stroke Scale)
  - FAST/BEFAST screening
  - Thrombolysis criteria (tPA window)
  - Stroke mimics

- [ ] Seizure and epilepsy (130 LOC)
  - Seizure types and classification
  - Status epilepticus management
  - Antiepileptic drugs (Australian PBS)
  - Driving restrictions (Australian guidelines)

- [ ] Headache disorders (130 LOC)
  - Migraine, tension-type, cluster headaches
  - Red flags (thunderclap, new onset >50 years)
  - Prophylaxis and acute treatment

**Week 6: 100% Complete (850 LOC)**
- [ ] Movement disorders (150 LOC)
  - Parkinson's disease
  - Essential tremor
  - Restless legs syndrome

- [ ] Demyelinating diseases (150 LOC)
  - Multiple sclerosis
  - Guillain-Barré syndrome
  - Myasthenia gravis

- [ ] Peripheral neuropathy (150 LOC)
  - Diabetic neuropathy
  - Carpal tunnel syndrome
  - Radiculopathy

#### MED-006 Emergency Medicine (850 LOC)

**Week 5: 50% Complete (400 LOC)**
- [ ] Resuscitation tools (140 LOC)
  - ACLS algorithms (Australian ANZCOR)
  - Sepsis management (Surviving Sepsis Campaign)
  - Trauma primary survey (ATLS)
  - Massive transfusion protocol

- [ ] Shock assessment (130 LOC)
  - Hypovolemic, cardiogenic, distributive, obstructive
  - Fluid resuscitation strategies
  - Vasopressor selection

- [ ] Anaphylaxis (130 LOC)
  - Recognition criteria
  - Adrenaline dosing (IM 0.5mg)
  - Biphasic reaction monitoring
  - Discharge criteria

**Week 6: 100% Complete (850 LOC)**
- [ ] Toxicology (150 LOC)
  - Paracetamol overdose (Rumack-Matthew nomogram)
  - Salicylate, opioid, benzodiazepine overdose
  - Antidote administration

- [ ] Environmental emergencies (150 LOC)
  - Heatstroke, hypothermia
  - Envenomation (Australian snakes, spiders)
  - Drowning

- [ ] Procedural sedation (150 LOC)
  - Sedation scale (Ramsay, RASS)
  - Medication selection
  - Monitoring and reversal

**Progress Target (End of Week 6):**
- ✅ 5 agents complete: MED-009, MED-003, MED-004, MED-005, MED-006
- ✅ 4,250 LOC added (850 × 5)
- ✅ 50% of total agent expansion complete

---

### Weeks 7-8: MED-007 ObGyn + MED-008 Paediatrics
**Status:** ⏳ PENDING
**Progress:** 0% → 100% each
**Timeline:** 2026-03-08 to 2026-03-21

#### MED-007 Obstetrics & Gynaecology (850 LOC)

**Week 7: 50% Complete (400 LOC)**
- [ ] Antenatal care tools (140 LOC)
  - Routine screening (OGTT, GBS, anomaly scan)
  - Antenatal risk assessment (VBAC, preterm birth)
  - Prenatal diagnosis (NIPT, amniocentesis)
  - Immunization in pregnancy (whooping cough, flu)

- [ ] Pregnancy complications (130 LOC)
  - Preeclampsia, gestational diabetes
  - Antepartum hemorrhage (placenta previa, abruption)
  - Preterm labor management
  - Multiple pregnancy

- [ ] Contraception (130 LOC)
  - UKMEC contraceptive eligibility
  - LARC (IUD, implant)
  - Emergency contraception
  - Contraception counseling

**Week 8: 100% Complete (850 LOC)**
- [ ] Labor and delivery (150 LOC)
  - Stages of labor, partogram
  - Induction of labor
  - Augmentation, instrumental delivery
  - Cesarean section indications

- [ ] Gynecological conditions (150 LOC)
  - Abnormal uterine bleeding
  - Pelvic pain (endometriosis, ovarian cyst)
  - PCOS, infertility
  - Menopause management

- [ ] Gynecological oncology (150 LOC)
  - Cervical, ovarian, endometrial cancer
  - Screening programs (cervical screening)
  - Red flags and referral

#### MED-008 Paediatrics (850 LOC)

**Week 7: 50% Complete (400 LOC)**
- [ ] Developmental assessment (140 LOC)
  - Developmental milestones (6mo, 12mo, 18mo, 2yr, 4yr)
  - Red flags for developmental delay
  - Autism spectrum disorder screening
  - ADHD assessment (Conners scale)

- [ ] Immunization schedule (130 LOC)
  - Australian National Immunisation Program
  - Vaccine-preventable diseases
  - Catch-up schedules
  - Vaccine hesitancy counseling

- [ ] Growth monitoring (130 LOC)
  - Growth charts (WHO, CDC)
  - Failure to thrive
  - Obesity assessment
  - Constitutional delay

**Week 8: 100% Complete (850 LOC)**
- [ ] Common pediatric conditions (150 LOC)
  - Fever without source
  - Bronchiolitis, croup, pneumonia
  - Gastroenteritis, dehydration
  - Rashes (viral exanthems, eczema)

- [ ] Neonatal care (150 LOC)
  - Neonatal jaundice (phototherapy criteria)
  - Neonatal resuscitation
  - Congenital abnormalities screening

- [ ] Pediatric emergencies (150 LOC)
  - Sepsis, meningitis
  - Diabetic ketoacidosis
  - Status epilepticus
  - Safeguarding (non-accidental injury)

**Progress Target (End of Week 8):**
- ✅ 7 agents complete (+ MED-007, MED-008)
- ✅ 5,950 LOC added (850 × 7)
- ✅ 70% of total agent expansion complete

---

### Weeks 9-10: MED-010 General Practice (Final Agent)
**Status:** ⏳ PENDING
**Progress:** 0% → 100%
**Timeline:** 2026-03-22 to 2026-04-04

#### MED-010 General Practice (850 LOC)

**Week 9: 50% Complete (400 LOC)**
- [ ] Preventive health tools (140 LOC)
  - Health assessment (45-49 years, 75+ years)
  - Cancer screening (breast, cervical, colorectal)
  - Cardiovascular risk assessment (Framingham, QRISK)
  - Immunization (influenza, pneumococcal, zoster)

- [ ] Chronic disease management (130 LOC)
  - Diabetes annual review
  - Asthma action plan
  - COPD management
  - Hypertension management

- [ ] Mental health in primary care (130 LOC)
  - Depression screening (PHQ-9, K10)
  - Mental Health Treatment Plan
  - GP Mental Health Care Plan (MHCP)
  - Referral to psychology, psychiatry

**Week 10: 100% Complete (850 LOC)**
- [ ] Geriatric assessment (150 LOC)
  - Comprehensive geriatric assessment
  - Falls risk assessment (FRAT)
  - Polypharmacy review
  - Advance care planning

- [ ] Musculoskeletal (150 LOC)
  - Back pain (red flags)
  - Osteoarthritis
  - Gout, rheumatoid arthritis screening
  - Sports injuries

- [ ] Common presentations (150 LOC)
  - Upper respiratory tract infections
  - Urinary tract infections
  - Skin infections (cellulitis, abscesses)
  - Minor injuries

**Progress Target (End of Week 10):**
- ✅ **ALL 8 agents complete** (MED-001, MED-002, MED-003, MED-004, MED-005, MED-006, MED-007, MED-008, MED-009, MED-010)
- ✅ 6,800 LOC added (850 × 8)
- ✅ **100% of total agent expansion complete** ✅

---

## Agent Expansion Template (Used for All Agents)

### Standard Components (Every Agent)
1. **Clinical Tools** (200-300 LOC)
   - Scoring systems, calculators, assessment tools
   - Example: NIHSS for neurology, MELD for gastroenterology

2. **Diagnosis Frameworks** (150-200 LOC)
   - Diagnostic criteria (DSM-5, WHO, Australian guidelines)
   - Differential diagnosis generators

3. **Management Algorithms** (150-200 LOC)
   - Step-wise treatment protocols
   - Australian guideline compliance (eTG, AMH)

4. **Medication Tools** (100-150 LOC)
   - Drug selection, dosing, interactions
   - PBS restrictions, authority scripts

5. **MCQ Generation** (100-150 LOC)
   - Topic-specific MCQ templates
   - RAG citation integration
   - Difficulty calibration

6. **OSCE Station Generation** (100-150 LOC)
   - History, examination, communication stations
   - Marking rubrics
   - 8-minute timing

7. **Topic Coverage Validation** (50 LOC)
   - Ensure all specialty topics covered
   - Gap analysis

**Total per Agent:** 850-1,100 LOC

---

## Quality Standards (All Agents)

### Code Quality
- **Test Coverage:** >80% per agent
- **Documentation:** Complete docstrings
- **Linting:** Pass flake8, mypy
- **Code Review:** PM-001 approval required

### Clinical Quality
- **Guideline Compliance:** 100% Australian guidelines
- **Citation Accuracy:** 100% RAG-verified
- **Expert Review:** 10% sample reviewed by specialist

### Performance
- **MCQ Generation:** <10 seconds per question
- **OSCE Generation:** <30 seconds per station
- **RAG Query Latency:** <500ms

---

## Success Metrics

| Metric | Target | Week 4 | Week 6 | Week 8 | Week 10 | Status |
|--------|--------|--------|--------|--------|---------|--------|
| **Agents Complete** | 8 | 3 | 5 | 7 | 8 | 🟡 0/8 |
| **Total LOC Added** | 6,800 | 2,550 | 4,250 | 5,950 | 6,800 | 🟡 0 |
| **Test Coverage** | >80% | 75% | 80% | 82% | 85% | 🟡 - |
| **MCQs Generated** | 5,000 | 1,500 | 2,800 | 4,200 | 5,000 | 🟡 0 |
| **OSCE Modules** | 100 | 30 | 60 | 85 | 100 | 🟡 0 |

---

## Risk Management

### Risk 1: Agent Complexity Variance (MEDIUM)
**Issue:** Some specialties more complex than others
**Mitigation:**
- MED-009 Psychiatry first (most complex, sets template)
- Simpler agents later (MED-010 GP)
**Contingency:** Adjust LOC targets based on complexity

### Risk 2: Timeline Compression (MEDIUM)
**Issue:** 8 agents in 10 weeks = aggressive pace
**Mitigation:**
- 2 agents in parallel (Weeks 3-8)
- Template reuse from MED-009
**Contingency:** Extend to Week 12 if needed

### Risk 3: Clinical Accuracy (HIGH)
**Issue:** Agents must be 100% clinically accurate
**Mitigation:**
- RAG citation for all claims
- Expert review of 10% sample
- QA-001 validation
**Contingency:** Increase expert review to 20% if issues found

---

## Related Documents
- [MED-009 Psychiatry Expansion](../agents/MED_009_PSYCHIATRY_EXPANSION.md)
- [Week 1 Execution Plan](../weekly/WEEK_01_EXECUTION.md)
- [Expansion Roadmap](../EXPANSION_ROADMAP.md)

---

**Last Updated:** 2026-01-24
**Status:** 🟡 WEEK 1 IN PROGRESS (MED-009 Psychiatry)
**Owner:** Agent Expansion Team
**Next Milestone:** Week 2 - MED-009 100% complete
**Final Milestone:** Week 10 - All 8 agents complete
