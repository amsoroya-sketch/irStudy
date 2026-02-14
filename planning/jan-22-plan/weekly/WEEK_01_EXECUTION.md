# Week 1 Execution Plan: Psychiatry Agent + Initial Content
**Date Range:** 2026-01-24 to 2026-01-31
**Phase:** Phase A - Foundation
**Status:** 🟢 READY TO START

---

## Week Overview

**Primary Goals:**
1. Start MED-009 Psychiatry agent expansion (115 → 400 LOC, 50% complete)
2. Generate first 100 psychiatry MCQs with RAG citations
3. Begin 17 psychiatry OSCE modules (complete 5)
4. Start QA-003 upgrade design (RAG integration)

**Dependencies:**
- ✅ RAG system complete (42,647 vectors)
- ✅ Embedding pipeline operational
- ✅ Qdrant vector database indexed
- ✅ Citation extraction working

---

## Track 1: Agent Expansion (MED-009 Psychiatry)

### Current State
- **File:** `src/agents/medical/med_009_psychiatry.py`
- **Current LOC:** 115 lines
- **Target LOC (Week 1):** 400 lines (50% of 850 total)
- **Status:** 🟡 IN PROGRESS

### Tasks

#### Day 1-2: Mental State Examination Framework (8 hours)
- [ ] **Add MSE structured assessment tool**
  - Appearance and behavior
  - Speech (rate, volume, content)
  - Mood and affect
  - Thought form and content
  - Perception (hallucinations, illusions)
  - Cognition (orientation, memory, attention)
  - Insight and judgment

- [ ] **Create MSE scoring rubric**
  - OSCE marking criteria
  - Common findings interpretation
  - Red flags identification

**Deliverables:**
- `mental_state_examination.py` (120 LOC)
- MSE template for OSCE stations
- MCQ generation prompts for MSE

**Success Criteria:**
- ✅ MSE framework generates valid OSCE stations
- ✅ Can produce 20 MSE-related MCQs
- ✅ All components map to Australian psychiatry guidelines

---

#### Day 3-4: Risk Assessment Tools (8 hours)
- [ ] **Suicide risk assessment**
  - SAD PERSONS scale
  - Columbia Suicide Severity Rating Scale
  - Immediate vs. ongoing risk
  - Safety planning
  - Mental Health Act involuntary admission criteria (NSW/VIC/QLD)

- [ ] **Risk of harm to others**
  - Violence risk assessment
  - Duty to warn considerations
  - Forensic psychiatry principles

- [ ] **Self-harm assessment**
  - Non-suicidal self-injury (NSSI)
  - Protective factors
  - Referral pathways

**Deliverables:**
- `risk_assessment_tools.py` (100 LOC)
- Risk stratification algorithms
- Australian Mental Health Act compliance checks

**Success Criteria:**
- ✅ Risk assessment tools validated against RANZCP guidelines
- ✅ Can generate 15 risk assessment MCQs
- ✅ Mental Health Act criteria correctly applied

---

#### Day 5: Australian Mental Health Act Compliance (4 hours)
- [ ] **State-specific Mental Health Act provisions**
  - NSW Mental Health Act 2007
  - Victorian Mental Health Act 2014
  - Queensland Mental Health Act 2016
  - Common elements across states

- [ ] **Involuntary treatment criteria**
  - Schedule criteria (mental illness, risk, treatment available)
  - Community Treatment Orders (CTOs)
  - Emergency detention powers
  - Tribunal processes

**Deliverables:**
- `mental_health_act_compliance.py` (80 LOC)
- State-specific criteria lookup
- MCQ generation for legal/ethical scenarios

**Success Criteria:**
- ✅ All 3 state acts represented
- ✅ Can generate 10 Mental Health Act MCQs
- ✅ Correct legal terminology used

---

### Week 1 Agent Progress Target
**Current:** 115 LOC
**New Code:** ~300 LOC (MSE 120 + Risk 100 + MHA 80)
**Total End of Week:** ~415 LOC ✅ (Exceeds 400 LOC target)

**Completion Status:** 50% of final 850 LOC target

---

## Track 2: Content Generation

### Psychiatry MCQs (100 questions)

#### Breakdown by Topic
- **Depression (25 MCQs)**
  - Major depressive disorder diagnosis (DSM-5 criteria)
  - Antidepressant selection (SSRIs, SNRIs, TCAs, MAOIs)
  - Treatment-resistant depression
  - ECT indications
  - Postpartum depression

- **Anxiety Disorders (20 MCQs)**
  - Generalized anxiety disorder
  - Panic disorder
  - Social anxiety disorder
  - PTSD
  - Pharmacotherapy (SSRIs, benzodiazepines)

- **Psychotic Disorders (25 MCQs)**
  - Schizophrenia diagnosis and treatment
  - First-episode psychosis
  - Antipsychotic medications (typical vs. atypical)
  - Clozapine monitoring (TGA requirements)
  - Medication side effects (EPS, metabolic syndrome, QTc prolongation)

- **Bipolar Disorder (15 MCQs)**
  - Manic episode criteria
  - Mood stabilizers (lithium, valproate, lamotrigine)
  - Acute mania management
  - Lithium monitoring and toxicity

- **Suicide Risk & Mental Health Act (15 MCQs)**
  - Suicide risk assessment
  - Involuntary admission criteria
  - Community Treatment Orders
  - Emergency detention powers

#### Generation Process
1. **Use RAG system to retrieve citations**
   - Query: "Depression diagnosis criteria DSM-5"
   - Extract: RANZCP Clinical Practice Guidelines, eTG Psychotropic
   - Verify: Page numbers, edition, year

2. **Generate MCQ with template**
   - Clinical scenario (age, presentation, duration)
   - Question stem (diagnosis, investigation, management)
   - 5 options (1 correct, 4 plausible distractors)
   - Explanation (why correct, why distractors wrong)
   - References (minimum 2, page numbers)

3. **Automated QA validation**
   - Clinical accuracy check
   - Australian context check (medication names, units)
   - Citation verification (page numbers exist)
   - Difficulty calibration

**Daily Targets:**
- Day 1: 20 MCQs (depression)
- Day 2: 20 MCQs (anxiety + bipolar)
- Day 3: 25 MCQs (psychotic disorders)
- Day 4: 20 MCQs (suicide risk + MHA)
- Day 5: 15 MCQs (review + additional topics)

**Success Criteria:**
- ✅ 100 MCQs generated with RAG citations
- ✅ 90%+ pass automated QA-001 validation
- ✅ 100% have minimum 2 Australian guideline references
- ✅ Difficulty distribution: 40% easy, 40% medium, 20% hard

---

### Psychiatry OSCE Modules (5 of 17 complete)

#### Week 1 Target: 5 OSCE Stations

**Station 1: Major Depressive Disorder History**
- Duration: 8 minutes
- Task: Take focused psychiatric history from patient with low mood
- Assessment: MSE components, risk assessment, differential diagnosis
- Marking criteria: 20 points (empathy, safety, diagnosis)

**Station 2: Mental State Examination**
- Duration: 8 minutes
- Task: Perform and document MSE on patient with psychosis
- Assessment: Systematic approach, documentation, interpretation
- Marking criteria: 20 points (completeness, accuracy, professionalism)

**Station 3: Suicide Risk Assessment**
- Duration: 8 minutes
- Task: Assess suicide risk in patient presenting with suicidal ideation
- Assessment: Risk factors, protective factors, safety planning
- Marking criteria: 20 points (risk stratification, safety, disposition)

**Station 4: Explain Antidepressant Therapy**
- Duration: 8 minutes
- Task: Counsel patient starting SSRI (sertraline)
- Assessment: Communication, side effects, expectations, monitoring
- Marking criteria: 20 points (information delivery, empathy, consent)

**Station 5: Mental Health Act Scenario**
- Duration: 8 minutes
- Task: Determine if patient meets criteria for involuntary admission
- Assessment: Legal criteria, documentation, communication with family
- Marking criteria: 20 points (legal knowledge, communication, documentation)

**Generation Process:**
1. Create patient scenario (backstory, presentation)
2. Define candidate task (clear instructions)
3. Create examiner marking sheet (criteria + rubric)
4. Add model answer (what excellent candidate would do)
5. Include learning points (common mistakes, key concepts)

**Success Criteria:**
- ✅ All 5 stations have complete marking rubrics
- ✅ 8-minute timing validated
- ✅ Australian context (Mental Health Act, PBS medications)
- ✅ Aligned with AMC clinical exam format

---

## Track 3: Quality Assurance - QA-003 Upgrade

### Current State
- **Agent:** QA-003 (Performance Testing Agent)
- **Current Focus:** Manual testing, performance metrics
- **Target:** Automated RAG citation validation

### Week 1 Tasks

#### Day 1-2: Design QA-003 RAG Integration (4 hours)
- [ ] **Define RAG validation workflow**
  - Input: Generated MCQ with references
  - Process: Query RAG for each citation
  - Validation: Verify page numbers, extract content
  - Output: Confidence score (0.0-1.0)

- [ ] **Design confidence scoring system**
  - >0.90: Auto-approve (high confidence match)
  - 0.75-0.90: LLM verification required
  - <0.75: Reject (citation not found or inaccurate)

**Deliverables:**
- `qa_003_rag_integration_design.md` (design document)
- Workflow diagram (input → process → output)
- Test cases (10 sample MCQs with expected scores)

---

#### Day 3-5: Implement Initial RAG Integration (6 hours)
- [ ] **Create RAG query module**
  - Interface with Qdrant vector database
  - Accept citation text as input
  - Return top 5 matches with similarity scores
  - Extract page numbers from metadata

- [ ] **Implement confidence scoring**
  - Cosine similarity threshold mapping
  - Page number verification logic
  - Edge case handling (missing pages, multi-page citations)

**Deliverables:**
- `rag_citation_validator.py` (50 LOC)
- Unit tests (test_rag_validator.py)
- 20 sample MCQs tested

**Success Criteria:**
- ✅ Can validate 20 MCQs with citations
- ✅ Confidence scores align with manual review
- ✅ <5 seconds per MCQ validation
- ✅ 100% accuracy on page number extraction

---

## Track 4: Content Enhancement

### Week 1 Tasks

#### Day 1-2: Plan Existing Content Audit (4 hours)
- [ ] **Inventory existing OSCE modules**
  - Count total modules: 46
  - Categorize by specialty
  - Identify modules without citations
  - Prioritize high-yield topics (cardiology, respiratory, emergency)

- [ ] **Document current citation status**
  - Modules with citations: 0/46 (0%)
  - Target end of week: 0/46 (audit only, no enhancements yet)

**Deliverables:**
- `existing_osce_audit.csv` (module list with metadata)
- `citation_gap_analysis.md` (which modules need citations)
- Prioritization matrix (P0, P1, P2)

---

#### Day 3-5: Document 46 OSCE Modules Structure (6 hours)
- [ ] **Analyze OSCE module format**
  - Scenario structure
  - Marking rubric format
  - Learning objectives
  - Current reference format (if any)

- [ ] **Identify citation integration points**
  - Clinical claims requiring evidence
  - Management recommendations
  - Diagnostic criteria
  - Medication dosing

- [ ] **Create citation template**
  - Format: "Reference: [Title], [Author], [Page numbers], [Year]"
  - Placement: After each clinical claim
  - Validation: RAG confidence score required

**Deliverables:**
- `osce_module_structure_analysis.md`
- `citation_template.md`
- Sample enhanced module (1 module with citations added)

**Success Criteria:**
- ✅ All 46 modules catalogued
- ✅ Citation gaps identified
- ✅ Enhancement template validated on 1 module
- ✅ Ready for Week 2 enhancement work

---

## Week 1 Milestones

### Critical Success Metrics

| Metric | Target | Status | Notes |
|--------|--------|--------|-------|
| **MED-009 Psychiatry LOC** | 400 (50%) | 🟡 IN PROGRESS | 115 → 415 LOC |
| **Psychiatry MCQs** | 100 | 🟡 IN PROGRESS | 0 → 100 |
| **Psychiatry OSCE Modules** | 5 | 🟡 IN PROGRESS | 0 → 5 |
| **QA-003 Upgrade Started** | Design + 50 LOC | 🟡 IN PROGRESS | RAG integration |
| **OSCE Audit Complete** | 46 modules | 🟡 IN PROGRESS | Catalogued + gaps |

### Deliverables Checklist
- [ ] MED-009 agent code: 415 LOC (mental_state_examination.py, risk_assessment_tools.py, mental_health_act_compliance.py)
- [ ] 100 psychiatry MCQs (JSON format with citations)
- [ ] 5 psychiatry OSCE modules (PDF + marking rubrics)
- [ ] QA-003 design document
- [ ] QA-003 RAG integration (50 LOC, tested on 20 MCQs)
- [ ] OSCE audit (existing_osce_audit.csv, citation_gap_analysis.md)
- [ ] Citation template (citation_template.md)

---

## Risk Management

### Identified Risks

**Risk 1: Psychiatry agent complexity** (MEDIUM)
- **Issue:** Mental Health Act has state-specific variations
- **Mitigation:** Focus on common elements across NSW/VIC/QLD
- **Contingency:** Defer state-specific nuances to Week 2

**Risk 2: MCQ generation speed** (LOW)
- **Issue:** 100 MCQs in 5 days = 20/day
- **Mitigation:** Template-based generation, RAG citation automation
- **Contingency:** Reduce to 80 MCQs if quality issues arise

**Risk 3: QA-003 RAG integration** (MEDIUM)
- **Issue:** First time integrating RAG into QA workflow
- **Mitigation:** Start with design document, test on small sample
- **Contingency:** Extend to Week 2 if implementation issues

---

## Daily Schedule

### Day 1 (Monday)
- **AM:** MED-009 - Mental State Examination framework (4 hours)
- **PM:** Generate 20 depression MCQs (4 hours)

### Day 2 (Tuesday)
- **AM:** MED-009 - Complete MSE, start risk assessment (4 hours)
- **PM:** Generate 20 anxiety + bipolar MCQs (4 hours)

### Day 3 (Wednesday)
- **AM:** MED-009 - Risk assessment tools (4 hours)
- **PM:** Generate 25 psychotic disorder MCQs, QA-003 design (4 hours)

### Day 4 (Thursday)
- **AM:** MED-009 - Mental Health Act compliance (4 hours)
- **PM:** Generate 20 suicide risk MCQs, QA-003 implementation (4 hours)

### Day 5 (Friday)
- **AM:** Generate 5 OSCE modules, final 15 MCQs (4 hours)
- **PM:** OSCE audit, QA-003 testing, week review (4 hours)

**Total Hours:** 40 hours (8 hours/day × 5 days)

---

## Handoff to Week 2

### Completed by End of Week 1
- ✅ MED-009 Psychiatry: 50% complete (400 LOC)
- ✅ 100 psychiatry MCQs generated
- ✅ 5 psychiatry OSCE modules complete
- ✅ QA-003 upgrade: Design + initial implementation
- ✅ OSCE audit: 46 modules catalogued

### Ready for Week 2
- MED-009 Psychiatry: Expand to 850 LOC (add medication tools, ECT counseling)
- Generate 300 more psychiatry MCQs (reach 400 total)
- Complete remaining 12 psychiatry OSCE modules (reach 17 total)
- QA-003: Complete RAG integration (300+ LOC)
- Start OSCE enhancement (add citations to first 10 modules)

---

## Related Documents
- [Expansion Roadmap](../EXPANSION_ROADMAP.md)
- [Week 2 Execution Plan](WEEK_02_EXECUTION.md)
- [MED-009 Agent Plan](../../04_AGENT_PLANS/medical_specialists/MED_009_PSYCHIATRY_PLAN.md)
- [QA-003 Upgrade Plan](../QA_003_UPGRADE_PLAN.md)

---

**Last Updated:** 2026-01-24
**Status:** 🟢 READY TO START
**Owner:** Project Manager (PM-001)
**Next Review:** 2026-01-31 (End of Week 1)
