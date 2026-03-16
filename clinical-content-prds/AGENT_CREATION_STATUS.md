# Medical Expert Agent Specification Files - Creation Status

**Project**: irStudy Medical Education Platform - 360 AI Patient Personas
**Phase**: PATH B - Agent OS Medical Skills Infrastructure
**Created**: 2026-03-15
**Status**: 6/13 agents complete (46%), 243/360 personas specified (67.5%)

---

## ✅ Completed Agent Specifications (6/13 - 4,589 lines)

### Batch 1 (5/5 - 207 personas) - READY FOR PARALLEL EXECUTION

| Agent ID | Specialty | Lines | Personas | File Size | Status |
|----------|-----------|-------|----------|-----------|--------|
| **MED-001** | Cardiology | 659 | 45 (15E, 18M, 12H) | 25KB | ✅ Complete |
| **MED-002** | Emergency Medicine | 750 | 45 (15E, 18M, 12H) | 30KB | ✅ Complete |
| **MED-003** | General Practice | 720 | 54 (18E, 22M, 14H) | 30KB | ✅ Complete |
| **MED-008** | Respiratory Medicine | 728 | 36 (12E, 14M, 10H) | 30KB | ✅ Complete |
| **MED-009** | Neurology | 756 | 27 (9E, 11M, 7H) | 30KB | ✅ Complete |

**Batch 1 Total**: 3,613 lines, 207 personas across 5 specialties

### Batch 2 (1/5 started - 36 personas so far)

| Agent ID | Specialty | Lines | Personas | File Size | Status |
|----------|-----------|-------|----------|-----------|--------|
| **MED-004** | Pediatrics | 876 | 36 (12E, 14M, 10H) | 32KB | ✅ Complete |

**Batch 2 Progress**: 876 lines, 36 personas (24% of Batch 2 complete)

---

## 🔄 Remaining Agent Specifications (7/13)

### Batch 2 Remaining (4 agents - 117 personas)

| Agent ID | Specialty | Est. Lines | Personas | Priority | Template Ready |
|----------|-----------|------------|----------|----------|----------------|
| **MED-005** | Obstetrics & Gynaecology | ~700 | 27 (9E, 11M, 7H) | HIGH | ✅ |
| **MED-006** | Surgery | ~700 | 27 (9E, 11M, 7H) | HIGH | ✅ |
| **MED-007** | Psychiatry | ~750 | 36 (12E, 14M, 10H) | HIGH | ✅ |
| **MED-010** | Infectious Diseases | ~700 | 27 (9E, 11M, 7H) | MEDIUM | ✅ |

**Estimated**: 2,850 lines, 117 personas

### Batch 3 (1 agent - 60 personas)

| Agent ID | Specialty | Est. Lines | Personas | Priority | Template Ready |
|----------|-----------|------------|----------|----------|----------------|
| **MED-012** | Physical Examination | ~800 | 60 (20E, 24M, 16H) | HIGH | ✅ |

**Estimated**: 800 lines, 60 personas (12 each: CVS, Resp, Abdo, Neuro, MSK)

### Batch 4 (1 agent - 92 integrated personas)

| Agent ID | Specialty | Est. Lines | Personas | Priority | Template Ready |
|----------|-----------|------------|----------|----------|----------------|
| **MED-011** | Cultural Safety | ~850 | 92 (integrated) | CRITICAL | ✅ |

**Estimated**: 850 lines, 92 personas (12 Aboriginal/TSI, 40 LGBTQIA+, 40 CALD)

### Final Validation (1 agent)

| Agent ID | Specialty | Est. Lines | Personas | Priority | Template Ready |
|----------|-----------|------------|----------|----------|----------------|
| **QA-001** | Medical QA Validator | ~600 | Reviews 360 | CRITICAL | ✅ |

**Estimated**: 600 lines (reviews all 360 personas, not creator)

---

## 📊 Overall Progress Summary

**Completed**:
- ✅ 6/13 agents (46%)
- ✅ 4,589 lines written
- ✅ 243/360 personas specified (67.5%)
- ✅ Batch 1 COMPLETE (can execute in parallel now)
- ✅ Template pattern established (659-900 lines per agent, all 10 sections)

**Remaining**:
- ⏳ 7/13 agents (54%)
- ⏳ ~5,700 lines estimated
- ⏳ 117/360 personas remaining (32.5%)
- ⏳ Batches 2-4 + QA-001 validation

**Total Estimated**:
- **13 agents total** (6 complete, 7 remaining)
- **~10,300 lines total** (4,589 complete, 5,700 estimated)
- **360 personas specified** (243 complete, 117 remaining)

---

## 🎯 Template Structure (All 10 Sections - Consistent)

Each agent specification follows this exact structure:

1. **Agent Metadata** (ID, specialty, FRACP training, eTG sections, personas count, batch)
2. **Expertise Profile** (Specialty training, eTG guidelines, AMC competencies)
3. **Persona Creation Workflow** (RAG → LLM → Validation → FRACP Review → Iteration)
4. **Critical Error Detection Rules** (Specialty-specific auto-fail criteria with Python code)
5. **Quality Checklist** (Before returning to PM - 10-15 validation items)
6. **Learning Loop Structure** (Phase 1-3: Initial → Learning → Production quality)
7. **Anti-Patterns to Avoid** (4 examples: ❌ Bad vs ✅ Good with code/JSON)
8. **Example Persona** (Complete JSON: 300-500 lines with RAG citations, FRACP reviews)
9. **Summary** (Agent capabilities, next steps)
10. **Status/Version** (Completion status, last updated, version number)

**Average Length**: 700 lines per agent (range: 659-876 lines)

---

## 🔑 Key Specifications from Completed Agents

### MED-001: Cardiology Expert
- **eTG 2.1-2.8**: ACS, Heart failure, Arrhythmias, Hypertension, Valvular disease
- **Critical Errors**: Missed STEMI, delayed aspirin, beta-blockers in severe asthma
- **Example**: 65yo M with STEMI (chest pain, ST elevation, troponin rise)
- **RAG Citations**: eTG Cardiovascular 2.1.2 (confidence 0.78)
- **FRACP Reviews**: 2 cardiology reviews (approved)

### MED-002: Emergency Medicine Expert
- **eTG Multiple**: ACS, Stroke, Trauma, Anaphylaxis, Sepsis
- **Critical Errors**: Subcutaneous adrenaline (should be IM), thrombolysis >4.5h, missed stridor
- **Example**: 28yo F with anaphylaxis (stridor, hypotension, adrenaline 0.5mg IM)
- **Time-Critical**: Adrenaline within 5 minutes, thrombolysis <4.5 hours
- **FACEM Reviews**: 2 emergency physician reviews

### MED-003: General Practice Expert
- **eTG Multiple**: T2DM, HTN, Asthma, OA, Depression, COPD
- **Critical Errors**: Missed diabetes, NSAIDs in CKD, missed screening
- **Example**: 65yo M with T2DM (polyuria, polydipsia, HbA1c 8.2%)
- **Comorbidities**: 2-5 chronic conditions typical (metabolic syndrome)
- **Preventive Health**: Immunizations, cancer screening, CVD risk
- **FRACGP Reviews**: 2 GP reviews

### MED-004: Pediatrics Expert
- **eTG 14.1-14.6**: Febrile child, Asthma, Gastroenteritis, Development, Immunizations
- **Critical Errors**: Wrong weight-based dosing, missed developmental red flags, missed sepsis <3 months
- **Example**: 3yo M with febrile seizure (generalized, 2 minutes, benign)
- **Weight-Based Dosing**: Paracetamol 15mg/kg, amoxicillin 25mg/kg
- **Developmental Milestones**: Gross motor, fine motor, speech, social
- **NIP Schedule**: Birth to 18 months immunization compliance
- **FRACP Reviews**: 2 paediatric reviews

### MED-008: Respiratory Medicine Expert
- **eTG 3.1-3.7**: Asthma, COPD, Pneumonia, ILD, PE, Bronchiectasis
- **Critical Errors**: Missed respiratory failure (SpO2 <92%, RR >30), wrong inhaler technique, inappropriate antibiotics
- **Example**: 45yo F with severe asthma (SpO2 88%, continuous salbutamol nebs, magnesium sulfate)
- **Spirometry**: FEV1/FVC ratio, reversibility, GOLD classification
- **Smoking Pack-Years**: (cigarettes/day ÷ 20) × years smoked
- **FRACP Reviews**: 2 respiratory physician reviews

### MED-009: Neurology Expert
- **eTG 12.1-12.5**: Stroke, Epilepsy, Headache, Parkinson's, MS
- **Critical Errors**: Missed stroke (FAST negative but present), thrombolysis without CT, wrong seizure management
- **Example**: 55yo M with stroke (NIHSS 8, thrombolysis eligible at 2 hours)
- **NIHSS Scoring**: 0-42 scale (11 components)
- **FAST Assessment**: Face, Arms, Speech, Time
- **Thrombolysis**: Alteplase 0.9mg/kg IV within 4.5 hours, contraindications checked
- **FRACP Reviews**: 2 neurology reviews

---

## 📋 Remaining Agent Specifications - Key Details

### MED-005: Obstetrics & Gynaecology (27 personas)
- **eTG 15.1-15.5**: Pregnancy, Contraception, Menopause, Gynae cancers, Ectopic pregnancy
- **Critical Errors**: Missed ectopic pregnancy (abdominal pain + positive pregnancy test + no IUP), contraindicated medications in pregnancy (ACE inhibitors = teratogenic, warfarin = fetal bleeding)
- **Example Persona**: 28yo F with ectopic pregnancy (6 weeks amenorrhea, RIF pain, +ve βhCG, no IUP on TVUS, ruptured tube → emergency laparoscopy)
- **Key Investigations**: βhCG levels (doubling time), transvaginal ultrasound, discriminatory zone
- **Management**: Methotrexate (if unruptured, βhCG <1500, no cardiac activity) vs laparoscopic salpingectomy
- **Australian Context**: Pregnancy screening (NIPT, NT scan at 12 weeks), antenatal care schedule

### MED-006: Surgery (27 personas)
- **eTG Multiple**: Acute abdomen (appendicitis, cholecystitis, bowel obstruction), Pre-op assessment, Post-op complications
- **Critical Errors**: Missed acute appendicitis (RIF pain + rebound + fever = surgical emergency), wrong antibiotic prophylaxis (cefazolin for clean surgery), missed compartment syndrome (5 Ps: Pain, Pallor, Pulselessness, Paraesthesia, Paralysis)
- **Example Persona**: 35yo M with acute appendicitis (RIF pain 24 hours, McBurney's point tenderness, rebound, Rovsing's sign, fever 38.2°C, WCC 16)
- **Key Examination**: Rebound tenderness, guarding, Rovsing's sign, psoas sign
- **Management**: Laparoscopic appendicectomy, cefazolin + metronidazole prophylaxis
- **WHO Surgical Safety Checklist**: Sign In, Time Out, Sign Out

### MED-007: Psychiatry (36 personas)
- **eTG 16.1-16.9**: Depression (MDD), Anxiety (GAD, panic disorder), Psychosis (schizophrenia), Bipolar disorder, Suicide risk assessment
- **Critical Errors**: Missed suicide risk (PHQ-9 item 9 positive = SI, no safety plan), wrong antipsychotic (haloperidol in elderly = parkinsonism, QTc prolongation), no Mental Health Act assessment (involuntary treatment needed)
- **Example Persona**: 25yo F with major depressive disorder + suicidal ideation (PHQ-9 score 22 = severe, SI passive "better off dead", no plan yet, protective factors = family, treatment = escitalopram 10mg + CBT + safety planning)
- **MSE (Mental State Examination)**: Appearance, Behavior, Speech, Mood, Affect, Thought (form/content), Perception (hallucinations), Cognition, Insight, Judgment
- **Risk Assessment**: SAD PERSONS scale (Sex, Age, Depression, Previous attempt, Ethanol, Rational thinking loss, Social support, Organized plan, No spouse, Sickness)
- **Safety Planning**: Remove means (medications, firearms), crisis contacts, distraction techniques, emergency services

### MED-010: Infectious Diseases (27 personas)
- **eTG 5.1-5.12**: Sepsis, Meningitis, Endocarditis, HIV, Tuberculosis, Tropical infections
- **Critical Errors**: Delayed antibiotics in sepsis (mortality ↑7% per hour delay), wrong empirical therapy (missed Pseudomonas coverage in neutropenic patient), missed TB in immigrant (night sweats, weight loss, cough >3 weeks, apical consolidation on CXR)
- **Example Persona**: 40yo M with bacterial meningitis (headache, fever 39.5°C, neck stiffness, photophobia, Kernig's sign, LP: CSF cloudy, WCC 2000, protein ↑, glucose ↓, Gram stain: Gram-positive diplococci = Strep pneumoniae, empirical: ceftriaxone 2g IV + vancomycin 1g IV, dexamethasone 10mg IV)
- **Sepsis 6 Bundle** (within 1 hour): Blood cultures, Lactate, Antibiotics, Fluids (20-30mL/kg), Urine output monitoring, Oxygen
- **LP Contraindications**: Raised ICP (papilloedema, focal neurology), coagulopathy, thrombocytopenia, infection at LP site

### MED-012: Physical Examination (60 personas - 12 each system)
- **AMC Clinical Examination**: 5 Ps framework (Preparation, Position, Permission, Perform, Present)
- **Critical Errors**: Missing examination findings (didn't auscultate heart → missed murmur), wrong examination sequence (palpated abdomen before percussion → altered findings), no permission obtained ("May I examine your chest?")
- **Example Persona**: 65yo F with mitral stenosis (pansystolic murmur grade 3/6 at apex radiating to axilla, opening snap, low-pitched diastolic rumble, AF on ECG, dyspnoea NYHA Class II)
- **Systems**:
  - **CVS** (12): Mitral stenosis, Aortic stenosis, Heart failure, Atrial fibrillation, Hypertension
  - **Respiratory** (12): Consolidation, Pleural effusion, Pneumothorax, COPD, Asthma
  - **Abdominal** (12): Hepatomegaly, Splenomegaly, Ascites, Renal masses, Hernias
  - **Neurological** (12): Hemiplegia, Parkinson's disease, Cerebellar signs, Peripheral neuropathy
  - **Musculoskeletal** (12): Osteoarthritis, Rheumatoid arthritis, Gait abnormalities

### MED-011: Cultural Safety (92 integrated personas)
- **Guidelines**: NACCHO Aboriginal health, LGBTQIA+ health (Rainbow Health Victoria), CALD cultural competency
- **Critical Errors**: Stereotypical personas (Aboriginal patient always has diabetes/alcohol issues), missing cultural context (no family/community connection), offensive language (terms causing offense)
- **Example Persona**: 35yo Aboriginal F with chronic kidney disease (Noongar people WA, family history RHD in childhood, community support strong, prefers family present for medical discussions, experienced discrimination in healthcare previously, uses traditional healing alongside Western medicine)
- **Distribution**:
  - **Aboriginal/TSI** (12 personas): 3.3% (consistent with Australian population)
  - **LGBTQIA+** (40 personas): 11% (higher representation for inclusivity training)
  - **CALD** (40 personas): 11% (culturally and linguistically diverse backgrounds)
- **Cultural Liaison Review**: MANDATORY before deployment (prevents stereotypes, validates cultural accuracy)
- **Anti-Stereotyping Checklist**: No assumptions based on ethnicity, religion, gender identity, sexual orientation

### QA-001: Medical QA Validator (Reviews all 360)
- **Purpose**: Quality assurance for ALL 360 personas across all 12 specialties
- **Validation Checklist**:
  - [ ] All 360 personas follow JSON template
  - [ ] All RAG citations >0.65 confidence
  - [ ] All have ≥2 FRACP clinician reviews
  - [ ] Zero hardcoded credentials (API keys, database paths)
  - [ ] Zero clinical inaccuracies (wrong diagnosis, dangerous advice, contraindicated medications)
  - [ ] Cultural safety validated (12 Aboriginal/TSI, 40 LGBTQIA+, 40 CALD - no stereotypes)
  - [ ] Difficulty distribution correct (125 Easy, 148 Medium, 87 Hard)
  - [ ] Specialty distribution correct (10 specialties as per MASTER_PLAN.md)
  - [ ] Australian medical context maintained (PBS, Medicare, AHPRA, eTG/AMH)
- **QA Report Output**:
```json
{
  "total_personas_reviewed": 360,
  "total_personas_passed": 360,
  "total_personas_failed": 0,
  "quality_issues": [],
  "clinical_inaccuracies": 0,
  "cultural_safety_violations": 0,
  "avg_rag_citation_confidence": 0.73,
  "avg_fracp_reviews_per_persona": 2.1,
  "recommendation": "APPROVED FOR DEPLOYMENT"
}
```

---

## 🚀 Next Steps

### Immediate (This Session)
1. ✅ **6 agents complete** - Template pattern established
2. ⏳ **7 agents remaining** - Ready for creation (templates prepared)

### Phase 1: Complete Agent Specifications (Remaining ~5-6 hours)
1. Create **MED-005** (ObGyn) - 700 lines
2. Create **MED-006** (Surgery) - 700 lines
3. Create **MED-007** (Psychiatry) - 750 lines
4. Create **MED-010** (Infectious Diseases) - 700 lines
5. Create **MED-012** (Physical Exam) - 800 lines
6. Create **MED-011** (Cultural Safety) - 850 lines
7. Create **QA-001** (Medical QA Validator) - 600 lines

**Total Estimated**: ~5,700 lines, 7 agent files

### Phase 2: Convert to Claude Skills (Est. 10-15 hours)
1. Create `/home/dev/.claude/skills/medical/` directory structure
2. Convert agent specs to Claude Skills format (like `devops-docker-build-production-v1.md`)
3. Register in `skills-registry.json`:
   - 13 medical skills
   - Triggers, dependencies, tags
   - Estimated tokens per skill
4. Test skill invocation: `Skill: MED-001-cardiology-expert`

### Phase 3: Test with Pilot Personas (Est. 8-10 hours)
1. Create 1 pilot persona per specialty (10 total)
2. Submit to FRACP clinician panels (≥2 reviewers each)
3. Collect feedback
4. Iterate on agent specs based on feedback

### Phase 4: Full Persona Generation (Est. 100-120 hours)
1. Execute Batch 1 (5 agents in parallel) → 207 personas (Week 4-6)
2. Execute Batch 2 (5 agents in parallel) → 153 personas (Week 6-8)
3. Execute Batch 3 (1 agent) → 60 personas (Week 8-9)
4. Execute Batch 4 (1 agent + cultural liaison) → 92 personas (Week 9-10)
5. QA-001 validation → All 360 personas (Week 10)

**Total Timeline**: 24 weeks (6 months including HREC approval, FRACP reviews, iteration)

---

## 📁 File Locations

**Agent Specifications**:
- `/home/dev/Development/irStudy/clinical-content-prds/agents/`
- 6 complete files (MED-001, 002, 003, 004, 008, 009)
- 7 remaining (MED-005, 006, 007, 010, 011, 012, QA-001)

**Documentation**:
- `/home/dev/Development/irStudy/clinical-content-prds/MASTER_PLAN.md` (850 lines - 24-week roadmap)
- `/home/dev/Development/irStudy/clinical-content-prds/RALPH_EXECUTION_PLAN.md` (550 lines - parallel execution)
- `/home/dev/Development/irStudy/clinical-content-prds/QUICK_START.md` (230 lines - immediate actions)

**Future Locations**:
- `/home/dev/.claude/skills/medical/` (Claude Skills - to be created)
- `/home/dev/Development/irStudy/backend/data/patient_personas/` (360 persona JSON files - to be generated)

---

## ✅ Quality Gates

**Agent Specification Quality**:
- [x] All 10 sections present (Metadata, Expertise, Workflow, Critical Errors, Checklist, Learning Loop, Anti-Patterns, Example, Summary, Status)
- [x] 600-900 lines per agent
- [x] RAG citations >0.65 confidence in examples
- [x] FRACP reviews (≥2) in examples
- [x] Australian medical context (eTG, AMH, PBS, Medicare, AHPRA)
- [x] Critical error detection with Python code
- [x] Zero hardcoded credentials
- [x] Zero stereotypes (cultural safety)

**Persona Generation Quality** (Future):
- [ ] 100% JSON template compliance
- [ ] 100% RAG citations >0.65 confidence
- [ ] 100% FRACP reviews (≥2 per persona)
- [ ] 100% Australian medical context
- [ ] Zero clinical inaccuracies
- [ ] Zero cultural safety violations
- [ ] Difficulty distribution: 125 Easy (35%), 148 Medium (41%), 87 Hard (24%)

---

**Last Updated**: 2026-03-15 07:30
**Version**: 1.0
**Status**: Phase 1 in progress (6/13 agents complete, 7 remaining)
**Next Action**: Complete remaining 7 agent specification files
