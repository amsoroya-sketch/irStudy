# Medical Expert Agents Specification (MED-001 to MED-010)
## Australian Clinical Knowledge Experts for AMC Preparation

**Version:** 1.0.0
**Created:** January 17, 2026
**Status:** 📋 SPECIFICATION - Awaiting Approval
**Owner:** PM-001 (Project Manager)

---

## Executive Summary

Implement 10 Medical Expert Agents (MED-001 to MED-010) to provide specialized Australian clinical knowledge for AMC (Australian Medical Council) exam preparation. Each agent is a domain expert capable of:

1. **Generating MCQ questions** with Australian guideline compliance
2. **Creating OSCE scenarios** for AMC Clinical Exam preparation
3. **Developing clinical cases** with differential diagnoses
4. **Validating medical content** against Therapeutic Guidelines (eTG)
5. **Providing RAG-integrated responses** with exact citations (page/section numbers)

---

## Objectives

### Primary Goals
1. ✅ Implement 10 specialty-specific medical expert agents
2. ✅ Integrate with RAG system for citation-backed responses
3. ✅ Generate 500+ validated MCQs (50 per specialty)
4. ✅ Generate 20+ OSCE scenarios
5. ✅ Achieve 100% Australian guideline compliance
6. ✅ Achieve 100% citation accuracy (RAG-verified page/section numbers)

### Success Criteria
- [ ] All 10 agents extend BaseAgent correctly
- [ ] All agents integrate with RAG system (Qdrant + S-PubMedBert)
- [ ] All generated content has exact citations (book: page, eTG: section)
- [ ] 90%+ pass rate on QA-001 validation
- [ ] 80%+ manual review quality score (4.0/5.0)
- [ ] 0 American terminology/drug names
- [ ] Response time <5 seconds for content generation

---

## Agent Specifications

### MED-001: Cardiology Expert

**Specialty:** Cardiovascular Medicine
**Coverage:** Acute Coronary Syndrome, Heart Failure, Arrhythmias, Valvular Disease
**Primary Sources:**
- Therapeutic Guidelines: Cardiovascular (eTG Section 5.x)
- Talley & O'Connor's Clinical Examination (8th ed, Cardiovascular chapter)
- AMC Handbook of Clinical Assessment (Cardiovascular stations)

**Key Competencies:**
- ECG interpretation (STEMI, NSTEMI, arrhythmias)
- Cardiac risk scoring (GRACE, TIMI, CHA2DS2-VASc)
- Heart failure management (Australian guidelines)
- Antiplatelet/anticoagulation therapy (PBS restrictions)

**Content Generation Targets:**
- 50 MCQs (40% easy, 40% medium, 20% hard)
- 3 OSCE stations (chest pain history, CVS examination, ECG interpretation)
- 5 clinical cases (ACS, HF, AF, valvular disease, HTN)

---

### MED-002: Respiratory Expert

**Specialty:** Respiratory Medicine
**Coverage:** Asthma, COPD, Pneumonia, PE, Pleural Effusion, Respiratory Failure
**Primary Sources:**
- Therapeutic Guidelines: Respiratory (eTG Section 3.x)
- Talley & O'Connor's Clinical Examination (Respiratory chapter)
- Australian Asthma Handbook

**Key Competencies:**
- Spirometry interpretation
- Asthma/COPD management (Australian stepwise approach)
- Community-acquired pneumonia (CAP) treatment
- PE risk stratification (Wells score)

**Content Generation Targets:**
- 50 MCQs
- 3 OSCE stations (SOB history, RS examination, spirometry interpretation)
- 5 clinical cases (asthma exacerbation, COPD, CAP, PE, pleural effusion)

---

### MED-003: Gastroenterology Expert

**Specialty:** Gastroenterology & Hepatology
**Coverage:** IBD, GORD, PUD, GI Bleeding, Hepatitis, Cirrhosis
**Primary Sources:**
- Therapeutic Guidelines: Gastrointestinal (eTG Section 4.x)
- Talley & O'Connor's Clinical Examination (Abdominal chapter)
- Australian Immunisation Handbook (Hepatitis A/B)

**Key Competencies:**
- Upper GI bleeding management (risk stratification)
- IBD management (Crohn's, UC)
- Hepatitis screening and management
- Coeliac disease diagnosis

**Content Generation Targets:**
- 50 MCQs
- 2 OSCE stations (abdominal pain history, abdominal examination)
- 5 clinical cases (UGIB, IBD flare, hepatitis, cirrhosis, coeliac)

---

### MED-004: Endocrinology Expert

**Specialty:** Endocrinology & Metabolism
**Coverage:** Diabetes, Thyroid, Osteoporosis, Hyperlipidaemia, Obesity
**Primary Sources:**
- Therapeutic Guidelines: Endocrinology & Diabetes (eTG Section 6.x)
- Australian Diabetes Society guidelines
- RACGP Red Book (diabetes screening)

**Key Competencies:**
- Type 2 diabetes management (stepwise approach)
- Thyroid function test interpretation
- Osteoporosis screening and management
- Lipid management (PBS restrictions for statins)

**Content Generation Targets:**
- 50 MCQs
- 2 OSCE stations (diabetes counseling, thyroid examination)
- 5 clinical cases (T2DM, DKA, thyrotoxicosis, hypothyroid, osteoporosis)

---

### MED-005: Neurology Expert

**Specialty:** Neurology
**Coverage:** Stroke, Seizure, Headache, MS, Parkinson's, Neuropathy
**Primary Sources:**
- Therapeutic Guidelines: Neurology (eTG Section 7.x)
- Talley & O'Connor's Clinical Examination (Neurological chapter)
- Australian Stroke Guidelines

**Key Competencies:**
- Stroke management (thrombolysis criteria)
- Seizure management (first-line AEDs in Australia)
- Headache red flags
- Neurological examination

**Content Generation Targets:**
- 50 MCQs
- 3 OSCE stations (headache history, neuro examination, stroke management)
- 5 clinical cases (stroke, seizure, MS, migraine, Parkinson's)

---

### MED-006: Emergency Medicine Expert

**Specialty:** Emergency Medicine
**Coverage:** Trauma, Resuscitation, Toxicology, Acute Presentations
**Primary Sources:**
- Therapeutic Guidelines: Emergency (eTG Section 8.x)
- Oxford Handbook of Emergency Medicine (5th ed)
- NSW Health Emergency Protocols

**Key Competencies:**
- ATLS principles
- Anaphylaxis management (Australian dosing)
- Toxicology (paracetamol, salicylate overdose)
- Sepsis management

**Content Generation Targets:**
- 50 MCQs
- 3 OSCE stations (trauma assessment, anaphylaxis, resuscitation)
- 5 clinical cases (trauma, anaphylaxis, sepsis, overdose, DKA)

---

### MED-007: Obstetrics & Gynaecology Expert

**Specialty:** Obstetrics & Gynaecology
**Coverage:** Pregnancy, Labour, Contraception, Menopause, Gynaecological Oncology
**Primary Sources:**
- Therapeutic Guidelines: Women's Health (eTG Section 9.x)
- RANZCOG guidelines
- RACGP Red Book (antenatal care)

**Key Competencies:**
- Antenatal screening (Australian schedule)
- Labour management
- Contraception counseling (PBS restrictions)
- Menopause management (HRT guidelines)

**Content Generation Targets:**
- 50 MCQs
- 2 OSCE stations (antenatal counseling, contraception counseling)
- 5 clinical cases (pre-eclampsia, PPH, PCOS, menopause, cervical cancer screening)

---

### MED-008: Paediatrics Expert

**Specialty:** Paediatrics
**Coverage:** Developmental Milestones, Childhood Infections, Asthma, Seizures, Failure to Thrive
**Primary Sources:**
- Therapeutic Guidelines: Paediatric (eTG Section 10.x)
- Australian Immunisation Handbook
- RACGP Red Book (well-child checks)

**Key Competencies:**
- Developmental assessment (ages 0-5)
- Immunisation schedule (Australian)
- Paediatric drug dosing (weight-based)
- Fever without source management

**Content Generation Targets:**
- 50 MCQs
- 2 OSCE stations (developmental assessment, paediatric history)
- 5 clinical cases (bronchiolitis, febrile seizure, asthma, FTT, meningitis)

---

### MED-009: Psychiatry Expert

**Specialty:** Psychiatry & Mental Health
**Coverage:** Depression, Anxiety, Psychosis, Bipolar, Substance Use
**Primary Sources:**
- Therapeutic Guidelines: Psychiatry (eTG Section 11.x)
- Mental Health Act (NSW)
- RANZCP guidelines

**Key Competencies:**
- Mental state examination
- Depression management (stepwise approach)
- Psychosis management (first-line antipsychotics)
- Mental Health Act criteria

**Content Generation Targets:**
- 50 MCQs
- 2 OSCE stations (MSE, depression screening, suicide risk assessment)
- 5 clinical cases (depression, anxiety, schizophrenia, bipolar, substance use)

---

### MED-010: General Practice Expert

**Specialty:** General Practice / Family Medicine
**Coverage:** Preventive Health, Common Presentations, Chronic Disease, Screening
**Primary Sources:**
- Murtagh's General Practice (8th ed)
- RACGP Red Book (screening guidelines)
- PBS (common prescriptions)

**Key Competencies:**
- Health screening (Australian schedule)
- Chronic disease management (care plans, Team Care Arrangements)
- Common presentations (URTI, UTI, back pain)
- Medicare items (GP Management Plan, Team Care Arrangement)

**Content Generation Targets:**
- 50 MCQs
- 2 OSCE stations (health screening counseling, chronic disease review)
- 5 clinical cases (UTI, back pain, health check, depression, T2DM)

---

## Technical Architecture

### Class Structure

All agents follow this pattern (extends BaseAgent):

```python
from src.agents.base_agent import BaseAgent, AgentMetadata, AgentRole, AgentTask, TaskStatus
from src.rag.query_engine import MedicalRAGSystem
from typing import Dict, List, Any

class SpecialtyExpert(BaseAgent):
    """MED-XXX: Specialty Expert"""

    def __init__(self, rag_system: MedicalRAGSystem):
        metadata = AgentMetadata(
            agent_id="MED-XXX",
            name="Specialty Expert",
            role=AgentRole.MEDICAL_EXPERT,
            experience_years=15,
            technologies=["Therapeutic Guidelines", "Specialty"],
            specializations=["Topic1", "Topic2", "AMC Prep"],
            pros=["Expert in Australian guidelines", "15+ years experience"],
            cons=["Limited to specialty domain"],
            max_concurrent_tasks=5,
            quality_gate_required=True
        )
        super().__init__(metadata)
        self.rag = rag_system
        self._register_specialty_tools()

    def execute_task(self, task: AgentTask) -> Dict[str, Any]:
        """Execute specialty-specific task"""
        # Implementation
        pass

    def validate_output(self, task: AgentTask, output: Dict[str, Any]) -> tuple[bool, List[str]]:
        """Validate medical accuracy"""
        # Check citations, Australian context, drug names, units
        pass
```

### RAG Integration Pattern

```python
def _generate_mcq_with_rag(self, topic: str, difficulty: str) -> Dict:
    """Generate MCQ using RAG for citations"""

    # 1. Query RAG for relevant content
    rag_results = self.rag.query(
        question=f"What are the key clinical features and management of {topic}?",
        specialty=self.metadata.specializations[0],
        context_limit=10
    )

    # 2. Extract citations (page/section numbers)
    citations = rag_results['sources']  # Must have page/section numbers

    # 3. Generate question using LLM with context
    mcq = self._llm_generate_mcq(
        topic=topic,
        context=rag_results['answer'],
        citations=citations,
        difficulty=difficulty
    )

    # 4. Validate citation accuracy (RAG confidence > 0.65)
    mcq['rag_confidence'] = rag_results['confidence']
    mcq['rag_verified'] = rag_results['confidence'] > 0.65

    return mcq
```

### Citation Format (MANDATORY)

**Book citations:**
```
(Talley & O'Connor's Clinical Examination, 8th ed, p.145)
(Murtagh's General Practice, 8th ed, p.892)
(Oxford Handbook of Emergency Medicine, 5th ed, p.234)
```

**eTG citations:**
```
(Therapeutic Guidelines: Cardiovascular, Section 5.2.1, 2024)
(Therapeutic Guidelines: Paediatric, Section 2.3, 2024)
```

**NEVER use generic citations:**
```
❌ (eTG 2024)
❌ (Talley)
❌ (Australian guidelines)
```

---

## Content Generation Workflow

### MCQ Generation Pipeline

```
1. Topic Selection → Agent receives topic (e.g., "acute coronary syndrome")
2. RAG Query → Retrieve relevant Australian guideline content
3. LLM Generation → Generate question stem, options, explanation
4. Citation Extraction → Add exact page/section numbers from RAG
5. Self-Validation → Check Australian terminology, units, red flags
6. QA-001 Validation → External quality check
7. Storage → Save to database if passes validation
```

### OSCE Scenario Generation Pipeline

```
1. Station Type → History taking / Examination / Communication
2. RAG Query → Retrieve relevant clinical scenarios
3. LLM Generation → Generate candidate/actor/examiner instructions
4. Marking Criteria → Create structured rubric
5. Self-Validation → Check AMC format compliance
6. QA-001 Validation → External quality check
7. Storage → Save if passes validation
```

---

## Quality Gates

### Agent Self-Validation (MANDATORY)

Each agent's `validate_output()` checks:

1. **Citation Requirements:**
   - [ ] All citations have page numbers (books) OR section numbers (eTG)
   - [ ] RAG confidence > 0.65 for auto-citations
   - [ ] Minimum 2 references per MCQ

2. **Australian Context:**
   - [ ] Australian drug names (paracetamol NOT acetaminophen)
   - [ ] Australian spelling (paediatric NOT pediatric)
   - [ ] Australian units (mmol/L NOT mg/dL)
   - [ ] Australian emergency number (000 NOT 911)

3. **Medical Accuracy:**
   - [ ] Drug dosages include units
   - [ ] Red flags identified for emergencies
   - [ ] Evidence-based recommendations
   - [ ] Guideline-compliant management

4. **Format Compliance:**
   - [ ] MCQ: 5 options, 1 correct answer
   - [ ] OSCE: 8-minute station format
   - [ ] Appropriate difficulty level

### External Validation (QA-001)

After agent self-validation, content goes to QA-001 for:
- Clinical accuracy verification
- Citation page/section number checking
- Australian context audit
- Educational value assessment

**Target Pass Rate:** 90%+ on first submission

---

## Implementation Plan

### Phase 1: Core Infrastructure (Week 1)
- [ ] Create `/src/agents/medical/` directory structure
- [ ] Implement base medical agent template
- [ ] Integrate RAG system for citation extraction
- [ ] Setup logging and error handling

### Phase 2: Agent Implementation (Week 2-3)
- [ ] Implement MED-001 (Cardiology) - Test/validate template
- [ ] Implement MED-002 to MED-010 (parallel development)
- [ ] Create unit tests for each agent
- [ ] Document agent APIs

### Phase 3: Content Generation (Week 4)
- [ ] Generate 50 MCQs per specialty (500 total)
- [ ] Generate 2-3 OSCE scenarios per specialty (20-30 total)
- [ ] Run through QA-001 validation
- [ ] Manual expert review (sample 10%)

### Phase 4: Integration & Testing (Week 5)
- [ ] Integration tests with RAG system
- [ ] End-to-end content generation workflow
- [ ] Performance optimization (<5s response time)
- [ ] Documentation and examples

---

## Dependencies

### Required Systems
1. **RAG System (Qdrant + S-PubMedBert):**
   - Medical knowledge collection indexed (9,672+ chunks)
   - Query engine operational (<3s response time)
   - Citation extraction working (confidence scoring)

2. **LLM System (Ollama):**
   - Meditron 7B for fast generation
   - Llama 3.1 70B for complex reasoning
   - Model router functional

3. **QA Agents:**
   - QA-001 (Australian compliance) operational
   - QA-002 (Clinical accuracy) operational
   - QA-003 (Citation validator) operational

### Required Data
1. **Medical Textbooks (PDF processed and indexed):**
   - Therapeutic Guidelines (eTG) - All specialties
   - Talley & O'Connor's Clinical Examination (8th ed)
   - Murtagh's General Practice (8th ed)
   - Oxford Handbook of Emergency Medicine (5th ed)
   - AMC Handbook of Clinical Assessment

2. **Australian Guidelines:**
   - PBS medication listings
   - AHPRA standards
   - Australian Immunisation Handbook
   - RACGP Red Book

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Agents implemented | 10/10 | File count |
| MCQs generated | 500+ | Database count |
| OSCE scenarios | 20+ | Database count |
| QA-001 pass rate | 90%+ | Validation logs |
| Manual review score | 4.0/5.0 | Expert review |
| Citation accuracy | 100% | RAG verification |
| Australian compliance | 100% | QA-001 audit |
| Response time | <5s | Performance logs |
| Test coverage | 80%+ | pytest coverage |

---

## Risks & Mitigation

### Risk 1: RAG citation confidence too low
**Impact:** Cannot auto-generate page/section numbers
**Mitigation:** Manual citation review for low-confidence matches (<0.65)

### Risk 2: LLM generates American terminology
**Impact:** Fails Australian compliance validation
**Mitigation:** Strong system prompts + post-generation validation

### Risk 3: Content quality below target (4.0/5.0)
**Impact:** Not suitable for AMC exam preparation
**Mitigation:** Iterative prompt engineering + expert review loop

### Risk 4: Performance >5s response time
**Impact:** Poor user experience
**Mitigation:** Use Meditron 7B for simple queries, optimize RAG search

---

## Next Steps

### Immediate Actions (This Week)
1. **Review & Approve Specification** (1 hour)
   - User reviews this document
   - Approve or request changes

2. **Create Agent Templates** (8 hours)
   - Base medical expert class
   - MCQ generation template
   - OSCE generation template

3. **Implement MED-001** (16 hours)
   - Cardiology expert as prototype
   - Full integration with RAG
   - Complete test suite
   - Validate template works

4. **Parallel Implementation** (40 hours)
   - MED-002 to MED-010 using validated template
   - Customize for each specialty
   - Test suite for each

### Approval Required

**⚠️ User Decision Point:**

Should I proceed with implementation of the Medical Expert Agents (MED-001 to MED-010) as specified?

Options:
1. ✅ **Approve & Proceed** - Start implementation immediately
2. 🔄 **Request Changes** - Modify specification first
3. ❌ **Reject** - Different approach needed

---

**Last Updated:** January 17, 2026
**Status:** 📋 AWAITING APPROVAL
**Next:** Architect Review → ADR → Implementation
