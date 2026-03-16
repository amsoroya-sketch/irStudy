# PRD_CC_001: Medical Expert Agent Creation

**PRD ID**: CC_001
**Phase**: Phase 1 (Foundation)
**Priority**: P0 (BLOCKS Phase 2)
**Effort Estimate**: 12-16 hours
**Dependencies**: None
**Status**: NOT STARTED

---

## 1. Request

### User Story

**As a** Project Manager
**I want** 13 medical expert agent specifications created using Agent OS framework
**So that** I can delegate 360 persona creation tasks to specialty-specific agents with FRACP-equivalent expertise

### Business Context

The irStudy AI OSCE Simulation System needs **360 AI Patient Personas** across 10 medical specialties. Creating these personas manually would take 240-300 hours sequentially. By creating **13 specialist agents** using Agent OS framework, we can:
- **Parallelize** persona creation (5 agents simultaneously)
- **Ensure quality** (each agent has FRACP-equivalent expertise + validation checklists)
- **Enable learning** (agents improve based on FRACP clinician feedback)
- **Reduce timeline** from 240-300 hours to 48-60 hours (80% reduction)

**Clinical Evaluation Report Finding**:
> "0 of 360 AI Patient Personas created (production blocker). Estimated effort: 80-100 hours content creation + 40-60 hours expert validation."

**Solution**: Use Agent OS to automate content creation with medical expert agents, then validate with FRACP clinicians.

### Problem Statement

**Current State**:
- No agent specifications exist for medical content creation
- Each specialty requires different eTG guidelines (Cardiology: Section 2.1-2.8, Respiratory: Section 3.1-3.7, etc.)
- No standardized quality checklists for persona creation
- No learning loops (agents can't improve based on feedback)

**Target State**:
- 13 agent specification files created (agents/MED-001 through QA-001)
- Each agent has FRACP-equivalent expertise (eTG sections documented)
- Standardized persona creation workflow (RAG → LLM → Validate → FRACP Review → Iterate)
- Learning loops defined (feedback → system prompt updates)
- Quality checklists automated (RAG citations >0.65, zero hardcoded credentials)

### Success Metrics

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| Agent specification files created | 13 | 0 | NOT STARTED |
| eTG sections documented per agent | 5-12 sections | 0 | NOT STARTED |
| Critical error detection rules per agent | 4-6 rules | 0 | NOT STARTED |
| Quality checklist items per agent | 10+ items | 0 | NOT STARTED |
| Learning loop examples per agent | 3+ examples | 0 | NOT STARTED |
| Test persona created and validated | 1 (cardiology) | 0 | NOT STARTED |

---

## 2. Architecture

### Agent OS Workflow Diagram

```
┌────────────────────────────────────────────────────────────┐
│              13 Medical Expert Agents                       │
│  (MED-001 through MED-010, MED-011, MED-012, QA-001)       │
└────────────────────────────────────────────────────────────┘
                            │
                            ▼
         ┌──────────────────────────────────────┐
         │  Persona Creation Workflow            │
         │  (Same for all agents)                │
         └──────────────────────────────────────┘
                            │
            ┌───────────────┼───────────────┐
            ▼               ▼               ▼
    ┌────────────┐  ┌────────────┐  ┌────────────┐
    │ RAG        │  │ LLM        │  │ Validate   │
    │ Retrieval  │→ │ Generation │→ │ (Checklist)│
    │ (eTG/AMH)  │  │ (Claude)   │  │            │
    └────────────┘  └────────────┘  └────────────┘
                            │
                            ▼
                    ┌────────────┐
                    │ FRACP      │
                    │ Review     │
                    │ (≥2 clinicians)
                    └────────────┘
                            │
                            ▼
                    ┌────────────┐
                    │ Learning   │
                    │ Loop       │
                    │ (Update    │
                    │  prompt)   │
                    └────────────┘
```

### Agent Specification Template

**Each agent file** (`agents/MED-XXX-specialty-expert.md`) contains:

1. **Expertise Profile**
   - FRACP-equivalent training (years, specialty)
   - eTG sections with page numbers (e.g., "eTG Cardiovascular 2.1-2.8, pages 40-65")
   - AMC competency domains (history-taking, physical examination, communication)
   - Australian medical context (PBS medications, MBS billing codes)

2. **Persona Creation Workflow**
   - Step 1: RAG Retrieval (Qdrant query, min_confidence=0.65)
   - Step 2: LLM Generation (Claude 3.5 Sonnet, temp=0.7, max_tokens=1500)
   - Step 3: Validation (automated checklist)
   - Step 4: FRACP Review (≥2 clinicians)
   - Step 5: Iteration (incorporate feedback)

3. **Critical Error Detection Rules** (4-6 rules per specialty)
   - Wrong diagnosis (e.g., STEMI as heartburn)
   - Dangerous advice (e.g., NSAIDs in acute kidney injury)
   - Contraindicated medications (e.g., beta-blockers in severe asthma)
   - Missed red flags (e.g., chest pain + diaphoresis = ACS)

4. **Quality Checklist** (10+ items)
   - [ ] Follows JSON template
   - [ ] RAG citations >0.65 confidence
   - [ ] 9-step history structure present
   - [ ] Difficulty level appropriate (Easy/Medium/Hard)
   - [ ] Australian medications (paracetamol, salbutamol, adrenaline)
   - [ ] ≥2 FRACP clinician reviews
   - [ ] Zero hardcoded credentials
   - [ ] Zero clinical inaccuracies
   - [ ] Cultural safety validated (if applicable)
   - [ ] Specialty correct

5. **Learning Loop Structure**
   - Phase 1: Initial personas (1-10) → Collect FRACP feedback
   - Phase 2: Incorporate learning (11-25) → System prompt updates
   - Phase 3: Production quality (26-45) → 95% approval rate

6. **Anti-Patterns to Avoid**
   - ❌ Generic symptoms (too vague)
   - ❌ US medical context (acetaminophen instead of paracetamol)
   - ❌ Missing cultural context (Aboriginal health without NACCHO protocols)
   - ❌ Stereotypical personas (Aboriginal patients only with diabetes)

### Persona JSON Template (Complete Example)

**File**: `backend/data/patient_personas_template.json`

```json
{
  "id": "specialty_###_condition_gender_age",
  "name": "Full Name",
  "age": 65,
  "gender": "Male/Female/Non-binary",
  "specialty": "Cardiology",
  "difficulty": "Easy/Medium/Hard",
  "chief_complaint": "Chief complaint in patient's words",
  "opening_statement": "Patient's opening statement verbatim",
  "emotional_baseline": "ANXIOUS_GUARDED/CAUTIOUSLY_OPEN/TRUSTING/DEFENSIVE/WITHDRAWN",
  
  "symptoms": [
    {
      "symptom": "Symptom name (SOCRATES)",
      "description": "Detailed description with SOCRATES framework",
      "trigger": "onset/severity/character/radiation/associated/timing/exacerbating/relieving",
      "rag_citation": {
        "source": "eTG Section X.Y.Z",
        "page_ref": "p. XX",
        "quote": "Exact quote from eTG",
        "confidence": 0.78
      }
    }
  ],
  
  "past_medical_history": ["Condition 1", "Condition 2"],
  "medications": ["Medication 1 (dose, frequency)", "Medication 2"],
  "allergies": "No known drug allergies / Allergies listed",
  "family_history": "Relevant family history",
  "social_history": "Smoking, alcohol, occupation, living situation",
  
  "systems_review": {
    "cardiovascular": "CVS review",
    "respiratory": "Resp review",
    "other": "All other systems reviewed and negative"
  },
  
  "expected_diagnosis": "Primary diagnosis",
  "expected_investigations": ["Investigation 1", "Investigation 2"],
  "expected_management": ["Management step 1", "Management step 2"],
  
  "critical_errors": [
    "Error 1: Wrong diagnosis",
    "Error 2: Dangerous advice"
  ],
  
  "fracp_reviews": [
    {
      "reviewer_name": "Dr. Name",
      "reviewer_credentials": "FRACP (Specialty)",
      "review_date": "YYYY-MM-DD",
      "clinical_accuracy": "Yes/No",
      "difficulty_appropriate": "Yes/No",
      "rag_citations_correct": "Yes/No",
      "australian_context": "Yes/No",
      "cultural_safety": "Yes/No/N/A",
      "feedback": "Detailed feedback",
      "approved": true/false
    }
  ]
}
```

### RAG Citation Requirements

**All symptoms MUST have RAG citations** with:
- **Source**: eTG section (e.g., "eTG Cardiovascular 2.1.2")
- **Page reference**: Specific page (e.g., "p. 42")
- **Quote**: Exact text from eTG (proves citation accuracy)
- **Confidence**: ≥0.65 (Qdrant retrieval confidence score)

**Example RAG query**:
```python
results = rag_service.search(
    query="ST-elevation myocardial infarction acute management aspirin",
    collection="etg_cardiovascular",
    top_k=5,
    min_confidence=0.65
)

# Expected result:
# {
#   "source": "eTG Cardiovascular 2.1.2",
#   "page_ref": "p. 42",
#   "quote": "Aspirin 300mg loading dose STAT in STEMI",
#   "confidence": 0.78
# }
```

---

## 3. Implementation Tasks

### Task 1: Create Agent Directory Structure

**Effort**: 30 minutes

**Steps**:
```bash
cd /home/dev/Development/irStudy/clinical-content-prds/agents

# Create placeholder files
touch MED-001-cardiology-expert.md
touch MED-002-emergency-expert.md
touch MED-003-gp-expert.md
touch MED-004-pediatrics-expert.md
touch MED-005-obgyn-expert.md
touch MED-006-surgery-expert.md
touch MED-007-psychiatry-expert.md
touch MED-008-respiratory-expert.md
touch MED-009-neurology-expert.md
touch MED-010-infectious-diseases-expert.md
touch MED-011-cultural-safety-expert.md
touch MED-012-physical-exam-expert.md
touch QA-001-medical-qa-validator.md

# Verify
ls -la
# Expected: 13 agent files + README.md = 14 files total
```

**Validation**:
- [ ] 13 agent files created
- [ ] Naming convention correct (MED-###-specialty-expert.md)

---

### Task 2: Delegate Agent Specification Creation to Specialist

**Effort**: 10-14 hours (distributed across multiple agents)

**Delegation Strategy**: Since this is creating agent specifications (meta-work), PM should create the specifications directly using the template pattern established in MED-001-cardiology-expert.md.

**Agent Specifications to Create**:

#### 2.1: MED-001 Cardiology Expert (DONE - Sample Created)

**Already created**: `agents/MED-001-cardiology-expert.md` (659 lines)
**Status**: ✅ COMPLETE (serves as template for others)

#### 2.2: MED-002 Emergency Medicine Expert

**Expertise**:
- eTG Sections: Multiple (ACS 2.1, Stroke 12.3, Trauma, Sepsis 5.4, Anaphylaxis 4.2)
- Critical conditions: STEMI, stroke, trauma, sepsis, anaphylaxis
- Time-critical management (door-to-needle <60min for stroke)

**Critical Error Rules**:
- Missed stroke (no FAST assessment)
- Delayed sepsis recognition (no qSOFA score)
- Missed anaphylaxis (no IM adrenaline within 5 minutes)

**Personas**: 45 (15 Easy, 18 Medium, 12 Hard)

#### 2.3: MED-003 GP (General Practice) Expert

**Expertise**:
- eTG Sections: Multiple (Chronic disease management, Preventive health)
- Common conditions: Type 2 diabetes, hypertension, hyperlipidaemia, depression, osteoarthritis
- Preventive health: Cancer screening, immunizations, cardiovascular risk assessment

**Critical Error Rules**:
- Missed red flags (red flag back pain = spinal cord compression)
- Inappropriate antibiotic prescribing (viral URTI)
- Missed depression screening (PHQ-9)

**Personas**: 54 (20 Easy, 22 Medium, 12 Hard)

#### 2.4: MED-004 Pediatrics Expert

**Expertise**:
- eTG Sections: 14.1-14.6 (Child health)
- Common conditions: Asthma, croup, gastroenteritis, febrile seizures
- Developmental milestones, growth charts, immunization schedule

**Critical Error Rules**:
- Missed meningococcal sepsis (non-blanching rash)
- Wrong medication doses (pediatric dosing errors)
- Missed non-accidental injury (bruising patterns)

**Personas**: 36 (15 Easy, 15 Medium, 6 Hard)

#### 2.5: MED-005 ObGyn Expert

**Expertise**:
- eTG Sections: 15.1-15.5 (Women's health)
- Common conditions: Pregnancy complications, menstrual disorders, menopause, contraception
- Antenatal care, pre-eclampsia, gestational diabetes

**Critical Error Rules**:
- Missed ectopic pregnancy (abdo pain + vaginal bleeding in pregnancy)
- Missed ovarian torsion (sudden-onset severe abdo pain)
- Missed pre-eclampsia (headache + visual changes + HTN in pregnancy)

**Personas**: 27 (12 Easy, 9 Medium, 6 Hard)

#### 2.6: MED-006 Surgery Expert

**Expertise**:
- eTG Sections: Multiple (Acute surgical conditions)
- Common conditions: Appendicitis, cholecystitis, bowel obstruction, AAA
- Pre-operative assessment, post-operative complications

**Critical Error Rules**:
- Missed acute abdomen (peritonism, guarding, rebound tenderness)
- Missed AAA (pulsatile abdominal mass + hypotension)
- Missed bowel obstruction (absolute constipation + vomiting)

**Personas**: 27 (9 Easy, 12 Medium, 6 Hard)

#### 2.7: MED-007 Psychiatry Expert

**Expertise**:
- eTG Sections: 16.1-16.9 (Mental health)
- Common conditions: Depression, anxiety, bipolar disorder, schizophrenia
- Suicide risk assessment, involuntary treatment, medication management

**Critical Error Rules**:
- Missed suicide risk (passive ideation vs active plan)
- Missed serotonin syndrome (tremor, confusion, hyperthermia on SSRIs)
- Missed lithium toxicity (tremor, confusion, renal impairment)

**Personas**: 36 (12 Easy, 15 Medium, 9 Hard)

#### 2.8: MED-008 Respiratory Expert

**Expertise**:
- eTG Sections: 3.1-3.7 (Respiratory)
- Common conditions: Asthma, COPD, pneumonia, pulmonary embolism
- Spirometry interpretation, oxygen therapy, NIV

**Critical Error Rules**:
- Missed PE (breathlessness + pleuritic pain + leg swelling)
- Inappropriate oxygen in COPD (target SpO2 88-92% not 94-98%)
- Missed pneumothorax (sudden breathlessness + reduced breath sounds)

**Personas**: 36 (12 Easy, 15 Medium, 9 Hard)

#### 2.9: MED-009 Neurology Expert

**Expertise**:
- eTG Sections: 12.1-12.5 (Neurology)
- Common conditions: Stroke, seizures, headache, Parkinson's disease, multiple sclerosis
- Neurological examination (cranial nerves, power, sensation, reflexes, coordination)

**Critical Error Rules**:
- Missed stroke (no FAST assessment within 10 minutes)
- Missed meningitis (headache + photophobia + neck stiffness)
- Missed SAH (thunderclap headache)

**Personas**: 27 (9 Easy, 12 Medium, 6 Hard)

#### 2.10: MED-010 Infectious Diseases Expert

**Expertise**:
- eTG Sections: 5.1-5.12 (Infections)
- Common conditions: Sepsis, pneumonia, UTI, cellulitis, TB, HIV
- Antibiotic stewardship, empiric therapy, culture-directed therapy

**Critical Error Rules**:
- Missed sepsis (qSOFA ≥2 = sepsis until proven otherwise)
- Inappropriate antibiotics (narrow-spectrum preferred over broad-spectrum)
- Missed TB (persistent cough >2 weeks + night sweats + weight loss)

**Personas**: 27 (9 Easy, 12 Medium, 6 Hard)

#### 2.11: MED-011 Cultural Safety Expert

**Expertise**:
- Aboriginal and Torres Strait Islander health (NACCHO guidelines)
- LGBTQIA+ health (Rainbow Health guidelines)
- CALD (Culturally and Linguistically Diverse) health (interpreter protocols)
- Cultural humility, trauma-informed care

**Critical Error Rules**:
- Stereotypical personas (Aboriginal patients only with diabetes)
- Missing cultural context (Aboriginal health without NACCHO protocols)
- Inappropriate pronoun use (misgendering LGBTQIA+ patients)
- Interpreter not offered (CALD patient with limited English)

**Personas**: 92 (integrated into 360 total - 12 Aboriginal/TSI, 40 LGBTQIA+, 40 CALD)

#### 2.12: MED-012 Physical Examination Expert

**Expertise**:
- AMC Clinical Examination (physical examination stations)
- 5 Ps framework (Preparation, Position, Permission, Perform, Present)
- Examination systems: CVS, Respiratory, Abdominal, Neurological, MSK

**Critical Error Rules**:
- No hand hygiene (infection control failure)
- No permission obtained (professionalism failure)
- Wrong position (e.g., CVS examination flat instead of 45-degree angle)
- Missed key examination findings (e.g., pansystolic murmur in MR)

**Personas**: 60 (CVS 15, Resp 15, Abdo 12, Neuro 12, MSK 6)

#### 2.13: QA-001 Medical QA Validator

**Expertise**:
- Quality assurance across all specialties
- All eTG sections (Cardiovascular, Respiratory, Neurology, etc.)
- Clinical accuracy validation, cultural safety validation
- Final quality gate before deployment

**Quality Checks** (runs after all 360 personas created):
- [ ] All 360 personas follow JSON template
- [ ] All RAG citations >0.65 confidence
- [ ] All have ≥2 FRACP clinician reviews
- [ ] Zero hardcoded credentials
- [ ] Zero clinical inaccuracies
- [ ] Cultural safety validated (12 Aboriginal/TSI, 40 LGBTQIA+, 40 CALD)
- [ ] Difficulty distribution correct (125 Easy, 148 Medium, 87 Hard)
- [ ] Specialty distribution correct (10 specialties as per MASTER_PLAN.md)

---

### Task 3: Create Persona JSON Template

**Effort**: 1 hour

**Steps**:
```bash
cd /home/dev/Development/irStudy/backend/data

# Create template file
cat > patient_personas_template.json << 'EOF'
{
  "id": "specialty_###_condition_gender_age",
  "name": "Full Name",
  "age": 65,
  "gender": "Male/Female/Non-binary",
  "specialty": "Cardiology",
  "difficulty": "Easy/Medium/Hard",
  "chief_complaint": "Chief complaint in patient's words",
  "opening_statement": "Patient's opening statement verbatim",
  "emotional_baseline": "ANXIOUS_GUARDED",
  "symptoms": [
    {
      "symptom": "Symptom name (SOCRATES)",
      "description": "Detailed description with SOCRATES framework",
      "trigger": "onset/severity/character/radiation/associated/timing/exacerbating/relieving",
      "rag_citation": {
        "source": "eTG Section X.Y.Z",
        "page_ref": "p. XX",
        "quote": "Exact quote from eTG",
        "confidence": 0.78
      }
    }
  ],
  "past_medical_history": ["Condition 1", "Condition 2"],
  "medications": ["Medication 1 (dose, frequency)", "Medication 2"],
  "allergies": "No known drug allergies",
  "family_history": "Relevant family history",
  "social_history": "Smoking, alcohol, occupation, living situation",
  "systems_review": {
    "cardiovascular": "CVS review",
    "respiratory": "Resp review",
    "other": "All other systems reviewed and negative"
  },
  "expected_diagnosis": "Primary diagnosis",
  "expected_investigations": ["Investigation 1", "Investigation 2"],
  "expected_management": ["Management step 1", "Management step 2"],
  "critical_errors": ["Error 1", "Error 2"],
  "fracp_reviews": [
    {
      "reviewer_name": "Dr. Name",
      "reviewer_credentials": "FRACP (Specialty)",
      "review_date": "YYYY-MM-DD",
      "clinical_accuracy": "Yes/No",
      "difficulty_appropriate": "Yes/No",
      "rag_citations_correct": "Yes/No",
      "australian_context": "Yes/No",
      "cultural_safety": "Yes/No/N/A",
      "feedback": "Detailed feedback",
      "approved": true
    }
  ]
}
EOF

# Verify
cat patient_personas_template.json | jq .
```

**Validation**:
- [ ] Template file created
- [ ] JSON valid (jq parses successfully)
- [ ] All required fields present

---

### Task 4: Create Test Persona (Cardiology STEMI)

**Effort**: 2 hours

**Purpose**: Validate entire persona creation workflow before scaling to 360 personas

**Steps**:
1. Use MED-001 cardiology-expert specification
2. Create 1 STEMI persona (cardiology_001_stemi_male_65.json)
3. Submit for FRACP review (≥2 clinicians)
4. Incorporate feedback
5. Validate quality gates pass

**Expected Output**: `backend/data/patient_personas/cardiology_001_stemi_male_65.json` (see MED-001 specification for example)

**Validation**:
- [ ] Persona follows JSON template
- [ ] RAG citations >0.65 confidence
- [ ] 9-step history structure present
- [ ] ≥2 FRACP clinician reviews with "Approved: Yes"
- [ ] Zero hardcoded credentials
- [ ] Clinical accuracy validated

---

## 4. Testing Requirements

### QA Checklist (After All 13 Agent Specs Created)

- [ ] **Agent Count**: 13 agent specification files created
- [ ] **Naming Convention**: All files follow MED-###-specialty-expert.md or QA-###-role.md
- [ ] **eTG Sections**: Each specialty agent has 5-12 eTG sections documented with page numbers
- [ ] **Critical Error Rules**: Each specialty agent has 4-6 critical error detection rules
- [ ] **Quality Checklist**: Each agent has 10+ quality checklist items
- [ ] **Learning Loop**: Each agent has 3+ learning loop examples (Phase 1 → Phase 2 → Phase 3)
- [ ] **Anti-Patterns**: Each agent has 4-6 anti-patterns documented
- [ ] **Example Persona**: Each specialty agent has 1 complete persona example (JSON format)
- [ ] **Template Compliance**: Persona JSON template created and validated

### Validation Commands

```bash
# Check agent file count
ls -la clinical-content-prds/agents/*.md | wc -l
# Expected: 14 files (13 agents + README.md)

# Check eTG sections documented (grep for "eTG Section")
grep -r "eTG Section" clinical-content-prds/agents/*.md | wc -l
# Expected: ≥50 (5+ sections per specialty agent × 10 agents)

# Check critical error rules
grep -r "Critical Error" clinical-content-prds/agents/*.md | wc -l
# Expected: ≥40 (4+ rules per specialty agent × 10 agents)

# Validate JSON template
jq . backend/data/patient_personas_template.json
# Expected: Parsed successfully (exit code 0)

# Check test persona
ls -la backend/data/patient_personas/cardiology_001_stemi_male_65.json
# Expected: File exists (1 test persona created)
```

---

## 5. Acceptance Criteria

### Definition of Done

- [✅] **13 Agent Specification Files Created**
  - MED-001 through MED-010 (10 specialty experts)
  - MED-011 (cultural safety expert)
  - MED-012 (physical examination expert)
  - QA-001 (medical QA validator)

- [✅] **Each Agent Has FRACP-Equivalent Expertise**
  - eTG sections documented with page numbers (5-12 sections per agent)
  - AMC competency domains covered
  - Australian medical context (PBS medications, MBS billing)

- [✅] **Standardized Persona Creation Workflow**
  - RAG → LLM → Validate → FRACP Review → Iterate (same for all agents)
  - Automated validation checklist (10+ items)
  - Critical error detection rules (4-6 per specialty)

- [✅] **Learning Loops Defined**
  - Phase 1 → Phase 2 → Phase 3 progression documented
  - FRACP feedback → system prompt updates
  - Target 95% approval rate by Phase 3

- [✅] **Persona JSON Template Created**
  - Template file: backend/data/patient_personas_template.json
  - All required fields documented
  - RAG citation structure defined

- [✅] **Test Persona Validated**
  - 1 cardiology STEMI persona created
  - ≥2 FRACP clinician reviews with "Approved: Yes"
  - Quality gates passed (RAG citations >0.65, zero hardcoded credentials)

### Success Criteria

**Quantitative**:
- 13/13 agent files created (100%)
- ≥50 eTG sections documented (avg 5 per specialty agent)
- ≥40 critical error rules (avg 4 per specialty agent)
- 1 test persona with ≥2 FRACP approvals

**Qualitative**:
- FRACP clinicians confirm: "Agent specifications are clinically accurate and appropriate for AMC preparation"
- PM confirms: "Agents are ready to create 360 personas in Phase 2"
- Security scan: 0 hardcoded credentials in template or test persona

---

## 6. Dependencies

**Upstream Dependencies** (BLOCKS this PRD):
- None (Phase 1 can start immediately)

**Downstream Dependencies** (this PRD BLOCKS):
- **PRD_CC_002**: RAG Enhancement (agents need eTG citations)
- **PRD_CC_003**: History-Taking Personas (agents create personas)
- **PRD_CC_004**: Physical Examination Personas (MED-012 agent creates these)
- **PRD_CC_006**: Cultural Safety Personas (MED-011 agent creates these)

**Parallel Work**:
- PRD_CC_002 (RAG Enhancement) can run in parallel with Task 2 (agent specification creation)

---

## 7. Timeline

**Total Effort**: 12-16 hours
**Calendar Time**: 3-5 days (if 2-4 hours/day)
**Target Completion**: Week 2 (Phase 1)

| Task | Effort | Calendar Days | Status |
|------|--------|---------------|--------|
| Task 1: Create agent directory structure | 30 min | Day 1 | NOT STARTED |
| Task 2: Delegate agent specification creation | 10-14 hours | Days 1-4 | NOT STARTED |
| Task 3: Create persona JSON template | 1 hour | Day 4 | NOT STARTED |
| Task 4: Create test persona | 2 hours | Day 5 | NOT STARTED |
| **TOTAL** | **12-16 hours** | **5 days** | **NOT STARTED** |

---

## 8. Next Steps (After PRD_CC_001 Complete)

1. **Execute PRD_CC_002**: RAG Enhancement (eTG citations with page numbers)
2. **Execute PRD_CC_003**: History-Taking Personas (240 personas using MED-001 through MED-010 agents)
3. **Execute PRD_CC_004**: Physical Examination Personas (60 personas using MED-012 agent)
4. **Execute PRD_CC_006**: Cultural Safety Personas (92 personas using MED-011 agent)

---

**Status**: ✅ PRD COMPLETE - READY FOR EXECUTION
**Priority**: P0 (BLOCKS Phase 2)
**Estimated Effort**: 12-16 hours
**Target Completion**: Week 2
**Last Updated**: 2026-03-15
**Version**: 1.0
