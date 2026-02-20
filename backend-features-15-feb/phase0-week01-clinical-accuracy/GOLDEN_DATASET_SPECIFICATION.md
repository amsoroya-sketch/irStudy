# Golden Dataset Specification - Clinical Validation Benchmark

**Document Version**: 1.0
**Purpose**: Define structure and creation process for Golden Dataset used to validate automated OSCE scoring and clinical content generation
**Created**: 2026-02-15
**Target Users**: Clinical Advisor, Backend developers, QA engineers

---

## Executive Summary

The Golden Dataset is a curated collection of 200 expertly-reviewed clinical scenarios with gold-standard scoring that serves as the benchmark for validating our automated scoring system and RAG-generated content.

**Purpose**:
1. Validate automated OSCE scoring accuracy (target: ≥85% agreement with human experts)
2. Train and test RAG content generation system
3. Establish clinical quality benchmarks
4. Provide exemplar responses for student learning

**Composition**:
- **200 clinical scenarios** (150 passing responses, 50 failing responses)
- **3 diversity categories**: Aboriginal/Torres Strait Islander, CALD, Mainstream
- **5 clinical domains**: Communication, Clinical Reasoning, Information Gathering, Management, Professionalism
- **Expert review**: All scored by FRACGP-qualified reviewer using AMC 15-mark rubric

**Quality Gates**:
- ✅ 100% expert review (no AI-only scoring)
- ✅ Inter-rater reliability: κ ≥ 0.80 (substantial agreement)
- ✅ Australian guideline alignment: 100%
- ✅ Cultural safety validation: 100%

---

## 1. Dataset Structure

### 1.1 Overall Composition

| Category | Count | Pass Rate | Purpose |
|----------|-------|-----------|---------|
| **Excellent (14-15/15)** | 30 | 100% | Exemplar responses for student learning |
| **Good (11-13/15)** | 60 | 100% | Strong pass responses |
| **Borderline Pass (9-10/15)** | 60 | 100% | Minimum competency threshold |
| **Borderline Fail (7-8/15)** | 25 | 0% | Just below threshold |
| **Clear Fail (0-6/15)** | 20 | 0% | Multiple major deficiencies |
| **Auto-Fail (Critical Error)** | 5 | 0% | Safety violations regardless of score |
| **TOTAL** | **200** | **75%** | Realistic pass rate for AMC exam |

### 1.2 Clinical Scenario Distribution

**By Clinical Domain Focus**:

| Domain | Scenario Count | Examples |
|--------|---------------|----------|
| Communication-Heavy | 40 | Breaking bad news, mental health, CALD patients |
| Clinical Reasoning-Heavy | 50 | Diagnostic challenges, complex presentations |
| Information Gathering-Heavy | 30 | History-taking stations |
| Management-Heavy | 50 | Acute emergencies, chronic disease management |
| Professionalism-Heavy | 30 | Ethics, confidentiality, cultural safety |

**By Clinical Context**:

| Context | Scenario Count | Examples |
|---------|---------------|----------|
| Acute Emergency | 40 | STEMI, anaphylaxis, pre-eclampsia, stroke |
| Chronic Disease Management | 50 | COPD, diabetes, hypertension, asthma |
| Mental Health | 30 | Depression, anxiety, psychosis |
| Preventive Care | 20 | Health checks, screening, immunization |
| Cultural Safety | 30 | Aboriginal patients, CALD patients, interpreter use |
| Obstetrics/Pediatrics | 30 | Pre-eclampsia, developmental assessment, immunization |

**By Patient Demographics** (Diversity Requirements):

| Demographic | Scenario Count | Cultural Competence Focus |
|-------------|---------------|---------------------------|
| Aboriginal/Torres Strait Islander | 30 | Social determinants, AHW involvement, Closing the Gap |
| CALD (Non-English Speaking) | 30 | Interpreter use, cultural beliefs |
| CALD (English Speaking) | 20 | Cultural beliefs, family-centered care |
| Mainstream Australian | 80 | General clinical competence |
| Elderly (>65 years) | 40 | Polypharmacy, geriatric syndromes |

---

## 2. Scenario Template Structure

Each scenario in the Golden Dataset follows this structure:

### 2.1 Metadata

```json
{
  "scenario_id": "GD-001",
  "title": "Acute Coronary Syndrome - STEMI Presentation",
  "clinical_context": "acute_emergency",
  "primary_domain_focus": "clinical_reasoning",
  "difficulty": "moderate",
  "patient_demographics": {
    "age": 58,
    "gender": "male",
    "ethnicity": "mainstream_australian",
    "cultural_considerations": []
  },
  "learning_objectives": [
    "Recognize STEMI presentation",
    "Formulate appropriate differential diagnosis",
    "Initiate time-critical emergency management",
    "Demonstrate empathy and clear communication"
  ],
  "estimated_time": "8_minutes",
  "station_type": "history_and_management"
}
```

### 2.2 Clinical Context Card (Student View)

What the student receives at the start of the station:

```markdown
**Patient**: Mr. John Anderson
**Age**: 58 years
**Setting**: Emergency Department

**Presenting Complaint**: "I have severe chest pain"

**Vital Signs**:
- BP: 145/88 mmHg
- HR: 105 bpm
- RR: 20/min
- SpO2: 96% on room air
- Temp: 37.1°C

**Task**: Take a focused history and formulate an initial management plan (8 minutes)
```

### 2.3 Complete Scenario Details (Examiner/Developer View)

Full clinical information including:
- History of presenting complaint (detailed)
- Past medical history
- Medications
- Family history
- Social history
- Examination findings (if examination station)
- Investigation results (if provided to student)
- Expected student actions

### 2.4 Student Response (Transcript)

**For Each Response Level** (Excellent, Good, Borderline Pass, Borderline Fail, Fail, Auto-Fail):

```json
{
  "response_id": "GD-001-EXCELLENT",
  "scenario_id": "GD-001",
  "response_level": "excellent",
  "transcript": "Full verbatim transcript of student-patient interaction...",
  "word_count": 650,
  "duration_seconds": 480
}
```

### 2.5 Expert Scoring (Gold Standard)

```json
{
  "scoring_id": "GD-001-EXCELLENT-SCORE",
  "response_id": "GD-001-EXCELLENT",
  "expert_reviewer": {
    "name": "Dr. Sarah Chen",
    "qualification": "FRACGP",
    "years_experience": 15,
    "amc_examiner": true
  },
  "scores": {
    "communication": {
      "score": 3,
      "max": 3,
      "justification": "Excellent rapport building with clear introduction. Used open-ended questions predominantly (75%). Demonstrated active listening with empathy phrases. Checked understanding regularly. No medical jargon without explanation.",
      "behavioral_anchors_met": [
        "Introduction within first 30 seconds",
        "Open-ended questions ≥60%",
        "Empathy phrases ≥3 instances",
        "Understanding checks present",
        "No unexplained jargon"
      ],
      "evidence_quotes": [
        "That must be very concerning for you",
        "Can you tell me more about the pain?",
        "Does that make sense?"
      ]
    },
    "clinical_reasoning": {
      "score": 4,
      "max": 4,
      "justification": "Comprehensive differential diagnosis with 4 relevant differentials (ACS, unstable angina, PE, aortic dissection). Clear logical reasoning linking symptoms to pathophysiology. Identified all red flags. Appropriate urgency assigned.",
      "differentials_identified": [
        "Acute Coronary Syndrome (STEMI) - most likely",
        "Unstable Angina",
        "Pulmonary Embolism",
        "Aortic Dissection"
      ],
      "red_flags_identified": [
        "2-hour duration",
        "Radiation to arm and jaw",
        "Multiple CV risk factors",
        "Associated sweating"
      ]
    },
    "information_gathering": {
      "score": 3,
      "max": 3,
      "justification": "Systematic SOCRATES approach. Covered all 8 components. Comprehensive history including PMHx, medications with allergy check, FHx, SHx. Appropriate red flag screening.",
      "socrates_coverage": "8/8",
      "history_components": [
        "HPC", "PMHx", "Medications", "Allergies", "FHx", "SHx", "Red flags"
      ]
    },
    "management": {
      "score": 3,
      "max": 3,
      "justification": "Appropriate immediate management (ECG, aspirin 300mg, cardiology referral). Checked allergies before prescribing. Explained next steps clearly. Specific safety-netting advice provided.",
      "critical_actions": [
        "ECG ordered immediately",
        "Aspirin 300mg (correct dose)",
        "Allergy check performed",
        "Cardiology consultation",
        "Safety-netting with 000 mention"
      ],
      "australian_guidelines": [
        "eTG Cardiovascular: ACS Management (2024)"
      ]
    },
    "professionalism": {
      "score": 2,
      "max": 2,
      "justification": "Exemplary professionalism. Asked permission throughout. Maintained patient dignity. Clear explanations. Checked understanding. Confidentiality respected.",
      "ahpra_standards_met": true,
      "cultural_safety": "not_applicable"
    }
  },
  "total_score": 15,
  "max_score": 15,
  "percentage": 100,
  "overall_result": "PASS",
  "meets_minimum_thresholds": true,
  "critical_errors": [],
  "australian_compliance": {
    "terminology_correct": true,
    "guidelines_followed": true,
    "emergency_number_correct": true,
    "drug_names_australian": true
  },
  "examiner_comments": "Exceptional performance demonstrating all competencies at highest level. Clear communication, comprehensive history, systematic clinical reasoning, appropriate management. Suitable for AMC pass with distinction."
}
```

### 2.6 Citations (RAG Validation)

```json
{
  "citations": [
    {
      "domain": "clinical_reasoning",
      "source": "Therapeutic Guidelines: Cardiovascular",
      "section": "5.2.1",
      "title": "Acute Coronary Syndrome Management",
      "publication_date": "2024",
      "edition": "2024",
      "page": null,
      "url": "https://www.tg.org.au",
      "confidence": 0.92,
      "relevance": "Confirms ACS as primary differential for crushing chest pain with radiation"
    },
    {
      "domain": "management",
      "source": "Australian Medicines Handbook",
      "section": "Chapter 8",
      "title": "Cardiovascular Drugs - Aspirin",
      "publication_date": "2024",
      "page": "245",
      "confidence": 0.89,
      "relevance": "Confirms aspirin 300mg loading dose for ACS"
    }
  ]
}
```

---

## 3. Seven-Step Validation Process

Each scenario undergoes rigorous 7-step validation before inclusion in Golden Dataset:

### Step 1: Clinical Accuracy Review
**Reviewer**: FRACGP-qualified GP or AMC examiner
**Checklist**:
- [ ] Scenario is clinically realistic
- [ ] Presentation matches cited guidelines
- [ ] Red flags appropriate for condition
- [ ] Differential diagnoses complete

### Step 2: Australian Guideline Alignment
**Reviewer**: Clinical documentation expert
**Checklist**:
- [ ] All management recommendations from eTG/AMH/RACGP
- [ ] Australian medication names used (paracetamol, salbutamol)
- [ ] Australian emergency protocols (000, not 911)
- [ ] PBS/Medicare considerations mentioned where relevant

### Step 3: Cultural Safety Validation
**Reviewer**: Cultural safety expert + Aboriginal Health Worker (for Aboriginal scenarios)
**Checklist**:
- [ ] No stereotyping in patient portrayal
- [ ] Social determinants acknowledged appropriately
- [ ] Communication strategies culturally appropriate
- [ ] Interpreter use mandatory for CALD scenarios with language barrier
- [ ] Aboriginal Health Worker offered for Aboriginal scenarios

### Step 4: Response Transcript Generation
**Process**:
- Simulate 6 different student responses per scenario (excellent, good, borderline pass, borderline fail, fail, auto-fail)
- Ensure responses demonstrate range of competency levels
- Include specific examples of behavioral anchors being met/not met

### Step 5: Expert Scoring (Gold Standard)
**Reviewer**: FRACGP-qualified GP with AMC examiner experience
**Process**:
- Score each response using AMC 15-mark rubric
- Provide detailed justification for each domain score
- Quote specific examples from transcript as evidence
- Cite Australian guidelines where applicable

### Step 6: Inter-Rater Reliability Testing
**Process**:
- Second expert reviews 20% of scenarios (40 responses)
- Calculate Cohen's kappa (κ) for inter-rater agreement
- Target: κ ≥ 0.80 (substantial agreement)
- If κ < 0.80, review and refine scoring rubric

**Interpretation of κ**:
| κ Value | Agreement Level | Action |
|---------|----------------|---------|
| 0.81 - 1.00 | Almost perfect | APPROVED |
| 0.61 - 0.80 | Substantial | Review edge cases, refine rubric |
| 0.41 - 0.60 | Moderate | REJECT - Major rubric refinement needed |
| 0.00 - 0.40 | Poor | REJECT - Complete rubric overhaul required |

### Step 7: Final Clinical Advisor Approval
**Reviewer**: Clinical Advisor (final authority)
**Checklist**:
- [ ] All 200 scenarios reviewed
- [ ] Inter-rater reliability ≥0.80
- [ ] Australian standards compliance 100%
- [ ] Cultural safety validated 100%
- [ ] Ready for production use

**Estimated Timeline**: 15-20 business days for full dataset validation

---

## 4. Dataset Creation Workflow

### 4.1 Phase 1: Scenario Selection (Week 1)

**Goal**: Identify 200 diverse clinical scenarios

**Process**:
1. Review AMC Clinical Exam blueprint
2. Identify common presentations:
   - Chest pain (ACS, PE, pneumonia, GORD)
   - Shortness of breath (asthma, COPD, pneumonia, cardiac failure)
   - Abdominal pain (appendicitis, cholecystitis, renal colic, ectopic pregnancy)
   - Headache (migraine, SAH, meningitis, temporal arteritis)
   - Mental health (depression, anxiety, psychosis, suicidal ideation)
3. Ensure diversity:
   - 30 Aboriginal/Torres Strait Islander scenarios
   - 50 CALD scenarios (30 non-English speaking, 20 English speaking)
   - 40 elderly patients (>65 years)
   - 30 obstetric/pediatric scenarios
4. Map to AMC rubric domains (ensure even distribution)

**Deliverable**: List of 200 scenario titles with metadata

### 4.2 Phase 2: Scenario Writing (Weeks 2-4)

**Goal**: Create full scenarios with clinical context cards

**Process**:
1. Clinical documentation expert writes scenario details:
   - Patient demographics
   - Presenting complaint
   - Full history (HPC, PMHx, FHx, SHx, Medications)
   - Examination findings
   - Investigation results
   - Learning objectives
2. Review for clinical accuracy (FRACGP reviewer)
3. Add Australian guideline citations
4. Validate cultural safety (for Aboriginal/CALD scenarios)

**Deliverable**: 200 complete scenario documents

### 4.3 Phase 3: Response Transcript Generation (Weeks 5-7)

**Goal**: Create 6 student responses per scenario (1200 transcripts total)

**Process**:
1. For each scenario, write 6 responses:
   - **Excellent (14-15/15)**: Demonstrates all behavioral anchors
   - **Good (11-13/15)**: Strong performance, minor gaps
   - **Borderline Pass (9-10/15)**: Minimum competency
   - **Borderline Fail (7-8/15)**: Below threshold
   - **Fail (0-6/15)**: Multiple deficiencies
   - **Auto-Fail**: Critical error despite other competencies

2. Ensure realistic responses (not overly artificial)
3. Include cultural competence variations for Aboriginal/CALD scenarios
4. Vary response length and communication styles

**Deliverable**: 1200 student response transcripts

### 4.4 Phase 4: Expert Scoring (Weeks 8-10)

**Goal**: Gold-standard scoring by FRACGP-qualified expert

**Process**:
1. Expert reviewer scores all 1200 responses using AMC 15-mark rubric
2. Provide detailed domain-by-domain justification
3. Quote specific transcript examples as evidence
4. Cite Australian guidelines
5. Flag critical errors

**Deliverable**: 1200 expert-scored responses with justifications

### 4.5 Phase 5: Inter-Rater Reliability Testing (Week 11)

**Goal**: Validate scoring consistency (κ ≥ 0.80)

**Process**:
1. Second expert scores 240 responses (20% sample)
2. Calculate Cohen's kappa for each domain
3. Analyze discrepancies
4. Refine rubric if needed
5. Re-score discrepant cases until agreement reached

**Deliverable**: Inter-rater reliability report

### 4.6 Phase 6: Final Review & Approval (Week 12)

**Goal**: Clinical Advisor sign-off

**Process**:
1. Clinical Advisor reviews complete dataset
2. Spot-checks 10% of scenarios (20 scenarios, 120 responses)
3. Validates Australian compliance
4. Approves for production use

**Deliverable**: Approved Golden Dataset v1.0

---

## 5. Data Storage & Access

### 5.1 Database Schema

```sql
-- Golden Dataset Scenarios
CREATE TABLE golden_scenarios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scenario_id VARCHAR(20) UNIQUE NOT NULL,  -- e.g., "GD-001"
    title TEXT NOT NULL,
    clinical_context VARCHAR(50),  -- acute_emergency, chronic_disease, etc.
    primary_domain_focus VARCHAR(50),  -- communication, clinical_reasoning, etc.
    difficulty VARCHAR(20),  -- easy, moderate, hard
    patient_age INTEGER,
    patient_gender VARCHAR(20),
    patient_ethnicity VARCHAR(50),
    cultural_considerations JSONB DEFAULT '[]',
    learning_objectives JSONB,
    estimated_time_minutes INTEGER DEFAULT 8,
    station_type VARCHAR(50),  -- history, examination, history_and_management
    clinical_context_card TEXT,  -- What student sees
    full_scenario_details JSONB,  -- Complete scenario information
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Golden Dataset Responses
CREATE TABLE golden_responses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    response_id VARCHAR(30) UNIQUE NOT NULL,  -- e.g., "GD-001-EXCELLENT"
    scenario_id VARCHAR(20) REFERENCES golden_scenarios(scenario_id),
    response_level VARCHAR(20),  -- excellent, good, borderline_pass, borderline_fail, fail, auto_fail
    transcript TEXT NOT NULL,
    word_count INTEGER,
    duration_seconds INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Golden Dataset Expert Scores (Gold Standard)
CREATE TABLE golden_scores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scoring_id VARCHAR(50) UNIQUE NOT NULL,
    response_id VARCHAR(30) REFERENCES golden_responses(response_id),

    -- Expert reviewer details
    expert_name VARCHAR(100),
    expert_qualification VARCHAR(50),  -- FRACGP, FRACS, etc.
    expert_years_experience INTEGER,
    expert_amc_examiner BOOLEAN,

    -- Domain scores
    communication_score INTEGER CHECK (communication_score BETWEEN 0 AND 3),
    communication_justification TEXT,
    communication_evidence JSONB,  -- Quotes from transcript

    clinical_reasoning_score INTEGER CHECK (clinical_reasoning_score BETWEEN 0 AND 4),
    clinical_reasoning_justification TEXT,
    clinical_reasoning_evidence JSONB,

    information_gathering_score INTEGER CHECK (information_gathering_score BETWEEN 0 AND 3),
    information_gathering_justification TEXT,
    information_gathering_evidence JSONB,

    management_score INTEGER CHECK (management_score BETWEEN 0 AND 3),
    management_justification TEXT,
    management_evidence JSONB,

    professionalism_score INTEGER CHECK (professionalism_score BETWEEN 0 AND 2),
    professionalism_justification TEXT,
    professionalism_evidence JSONB,

    -- Total score (calculated)
    total_score INTEGER GENERATED ALWAYS AS (
        communication_score +
        clinical_reasoning_score +
        information_gathering_score +
        management_score +
        professionalism_score
    ) STORED,

    -- Pass/Fail
    overall_result VARCHAR(20),  -- PASS, BORDERLINE, FAIL
    meets_minimum_thresholds BOOLEAN,
    critical_errors JSONB DEFAULT '[]',

    -- Australian compliance
    australian_terminology_correct BOOLEAN,
    australian_guidelines_followed BOOLEAN,
    emergency_number_correct BOOLEAN,
    drug_names_australian BOOLEAN,

    -- Examiner comments
    examiner_comments TEXT,

    -- Citations
    citations JSONB,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Inter-Rater Reliability Tracking
CREATE TABLE inter_rater_reliability (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    test_date DATE NOT NULL,
    expert_1_name VARCHAR(100),
    expert_2_name VARCHAR(100),
    sample_size INTEGER,  -- Number of responses both scored

    -- Cohen's kappa by domain
    communication_kappa DECIMAL(4,3),
    clinical_reasoning_kappa DECIMAL(4,3),
    information_gathering_kappa DECIMAL(4,3),
    management_kappa DECIMAL(4,3),
    professionalism_kappa DECIMAL(4,3),
    overall_kappa DECIMAL(4,3),

    -- Agreement level
    agreement_level VARCHAR(20),  -- poor, moderate, substantial, almost_perfect

    -- Discrepancies
    discrepant_cases JSONB,  -- List of response_ids with disagreement

    notes TEXT,
    approved_for_production BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 5.2 Access Control

**Who Can Access**:
- ✅ Backend automated scoring system (read-only)
- ✅ QA engineers for testing (read-only)
- ✅ Clinical Advisor for review (read/write)
- ✅ Expert reviewers for scoring (write scores only)
- ❌ Students (no access - to prevent memorization)

**API Endpoints**:
```python
# Get random sample for automated scoring validation
GET /api/v1/golden-dataset/sample?size=50&difficulty=moderate

# Get specific scenario for testing
GET /api/v1/golden-dataset/scenarios/{scenario_id}

# Get all responses for a scenario
GET /api/v1/golden-dataset/scenarios/{scenario_id}/responses

# Get gold-standard score for a response
GET /api/v1/golden-dataset/responses/{response_id}/score
```

---

## 6. Use Cases

### 6.1 Automated Scoring Validation

**Purpose**: Test that automated NLP scoring matches expert human scoring

**Process**:
1. Select random sample from Golden Dataset (e.g., 50 responses)
2. Run automated scoring algorithm on all 50
3. Compare automated scores to gold-standard expert scores
4. Calculate accuracy metrics:
   - **Domain-level accuracy**: % of responses where automated score matches expert score (±1 mark tolerance)
   - **Pass/Fail accuracy**: % of responses where automated pass/fail matches expert
   - **Critical error detection**: % of auto-fail cases correctly identified

**Success Criteria**:
- Domain accuracy ≥75%
- Pass/Fail accuracy ≥85%
- Critical error detection: 100% (zero tolerance for missing safety violations)

### 6.2 RAG Content Generation Testing

**Purpose**: Validate that RAG-generated content meets quality standards

**Process**:
1. Use Golden Dataset scenarios as prompts for RAG system
2. Generate new responses using RAG
3. Expert reviewer compares RAG-generated content to gold-standard
4. Validate:
   - Clinical accuracy
   - Australian guideline alignment
   - Citation completeness
   - Terminology correctness

**Success Criteria**:
- Clinical accuracy ≥90%
- Guideline alignment: 100%
- Citation completeness: 100%
- Australian terminology: 100%

### 6.3 Student Learning Examples

**Purpose**: Provide exemplar responses for students to study

**Process**:
1. Select "Excellent" responses from Golden Dataset
2. Present to students with expert annotations:
   - Highlighting behavioral anchors met
   - Explaining why specific phrases earned marks
   - Showing application of AMC rubric
3. Compare to "Fail" responses to demonstrate contrasts

**Visibility**:
- Show ONLY "Excellent" and "Good" responses to students
- Don't show "Fail" responses (avoid teaching bad habits)

### 6.4 Continuous Improvement

**Purpose**: Refine automated scoring over time

**Process**:
1. Monthly: Review discrepancies between automated and expert scores
2. Analyze patterns in errors
3. Refine NLP algorithms or rubric interpretation
4. Re-test on Golden Dataset
5. Update system when accuracy improves

---

## 7. Quality Assurance Metrics

### 7.1 Dataset Quality Metrics

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Clinical accuracy | 100% | Expert review, no factual errors |
| Australian guideline alignment | 100% | All citations from approved sources |
| Cultural safety compliance | 100% | No stereotyping, appropriate communication strategies |
| Inter-rater reliability (κ) | ≥0.80 | Cohen's kappa calculation |
| Response diversity | 75% pass, 25% fail | Realistic AMC exam pass rate |

### 7.2 Validation Testing Metrics

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Automated scoring accuracy | ≥85% pass/fail | Compare to gold standard |
| Domain-level accuracy | ≥75% (±1 mark) | Compare each domain score |
| Critical error detection | 100% | All auto-fail cases identified |
| False positive rate (incorrect fail) | <5% | Students incorrectly failed |
| False negative rate (incorrect pass) | <2% | Unsafe students incorrectly passed (more dangerous) |

---

## 8. Maintenance & Updates

### 8.1 Annual Review Cycle

**Every 12 months**:
1. Review all 200 scenarios for clinical accuracy
2. Update for new Australian guidelines (eTG, AMH updates)
3. Replace outdated scenarios (medications changed, protocols updated)
4. Add new scenarios for emerging conditions
5. Re-validate inter-rater reliability (new expert scores 20% sample)

### 8.2 Continuous Additions

**Ongoing**:
- Add new scenarios when students encounter edge cases
- Incorporate feedback from Clinical Advisor
- Expand diversity (new cultural groups, rare conditions)
- Target goal: 500 scenarios within 3 years

---

## 9. Deliverables & Timeline

### Phase 0.1 Week 1 Deliverable (This Document)

**Status**: ✅ COMPLETE
- Golden Dataset specification documented
- Structure defined
- Validation process outlined
- Ready for Clinical Advisor review

### Week 2-12 Implementation

| Week | Deliverable | Owner | Approval Gate |
|------|------------|-------|---------------|
| 1 | Scenario selection list (200 titles) | Clinical Documentation Expert | Clinical Advisor |
| 2-4 | 200 complete scenarios written | Clinical Documentation Expert | FRACGP Reviewer |
| 5-7 | 1200 student responses written | Clinical Team | FRACGP Reviewer |
| 8-10 | 1200 expert scores (gold standard) | FRACGP Reviewer | - |
| 11 | Inter-rater reliability testing | 2x FRACGP Reviewers | κ ≥ 0.80 |
| 12 | Final Clinical Advisor approval | Clinical Advisor | APPROVED for production |

**Total Timeline**: 12 weeks (3 months)

**Total Effort**: 200-250 hours (expert review is time-intensive)

---

## 10. Example Golden Dataset Entry

See full example in Appendix A below.

**Scenario ID**: GD-001
**Title**: Acute Coronary Syndrome - STEMI Presentation
**Responses**: 6 levels (Excellent, Good, Borderline Pass, Borderline Fail, Fail, Auto-Fail)
**Expert Scores**: Complete AMC 15-mark rubric breakdown
**Citations**: eTG Cardiovascular, AMH

---

**Document Status**: ✅ Ready for Clinical Advisor Review
**Created**: 2026-02-15
**Next Steps**: Begin scenario selection (Week 1) → Clinical Advisor approval → Full dataset creation
**Estimated Completion**: 2026-05-15 (12 weeks from start)

---

**END OF DOCUMENT**
