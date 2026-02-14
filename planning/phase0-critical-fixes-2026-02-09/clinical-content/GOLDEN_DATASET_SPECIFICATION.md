# Golden Dataset Specification - 200 Expert-Validated OSCE Scenarios

**Source**: AI_OSCE_CLINICAL_REVIEW_REPORT.md Section 6 + PRD 1
**Purpose**: Ensure AI Examiner scoring accuracy matches human AMC examiners
**Created**: 2026-02-10
**Australian Context**: All scenarios validated by Australian-trained specialists (FRACGP, FACEM, FRANZCOG, RACP)

---

## Purpose

The Golden Dataset is a collection of 200 expert-validated OSCE scenarios used to:
1. **Calibrate AI Examiner scoring** against human AMC examiners
2. **Validate AI Patient clinical accuracy** (all responses must be medically correct)
3. **Test RAG system performance** (confidence >0.65, Australian sources only)
4. **Establish baseline pass rates** by difficulty level
5. **Ensure cultural diversity** in patient presentations

**Quality Standard**: AI Examiner scores must be within ±2 marks of human AMC examiner scores for ALL 200 scenarios.

---

## 1. Dataset Composition

### 1.1 By Specialty (25 scenarios × 8 specialties = 200 total)

**Specialty Distribution**:
1. **Cardiology**: 25 scenarios
   - Examples: ACS, heart failure, arrhythmias, hypertension, valvular disease
2. **Respiratory**: 25 scenarios
   - Examples: Asthma, COPD, pneumonia, PE, lung cancer, pleural effusion
3. **Gastroenterology**: 25 scenarios
   - Examples: Abdominal pain (appendicitis, cholecystitis), GI bleeding, IBD, hepatitis
4. **Neurology**: 25 scenarios
   - Examples: Stroke, headache, seizures, weakness, dizziness, neuropathy
5. **Endocrinology**: 25 scenarios
   - Examples: Diabetes, thyroid disorders, Addison's, Cushing's, osteoporosis
6. **Psychiatry**: 25 scenarios
   - Examples: Depression, anxiety, psychosis, bipolar, suicide risk, capacity assessment
7. **Surgery**: 25 scenarios
   - Examples: Acute abdomen, hernias, lumps, trauma, pre-op assessment, post-op complications
8. **Obstetrics & Gynaecology**: 25 scenarios
   - Examples: Early pregnancy bleeding, antenatal care, contraception, abnormal vaginal bleeding, menopause

**Rationale**: Mirrors AMC Clinical Examination specialty distribution.

### 1.2 By Difficulty Level

**Foundation (Easy)**: 40% (80 scenarios)
- **Target Pass Rate**: 75-85%
- **Characteristics**: Common presentations, straightforward diagnosis, standard management
- **Examples**:
  - Uncomplicated asthma exacerbation
  - Simple UTI in young woman
  - Ankle sprain assessment
  - Routine antenatal booking visit

**Intermediate (Moderate)**: 40% (80 scenarios)
- **Target Pass Rate**: 60-70%
- **Characteristics**: Multiple differentials, some red flags, requires systematic approach
- **Examples**:
  - Chest pain (differentiate ACS vs PE vs musculoskeletal)
  - Headache (differentiate migraine vs tension vs red flag causes)
  - Abdominal pain (multiple differentials, need to exclude surgical emergency)
  - Postnatal depression with suicide risk assessment

**Advanced (Difficult)**: 20% (40 scenarios)
- **Target Pass Rate**: 40-50%
- **Characteristics**: Complex presentations, cultural competence required, high-stakes communication
- **Examples**:
  - Aboriginal patient with bronchiectasis + CAP (social determinants, cultural safety)
  - CALD patient with interpreter-required mental health assessment
  - Breaking bad news (miscarriage, cancer diagnosis, HIV positive)
  - Capacity assessment in elderly patient with cognitive impairment

**Rationale**: Difficulty distribution reflects AMC exam mix (most scenarios intermediate, with tail of difficult scenarios to discriminate excellent candidates).

### 1.3 By Cultural Diversity

**Aboriginal and Torres Strait Islander Patients**: 20% (40 scenarios)
- **Rationale**: Reflects Australian demographics; tests cultural competence
- **Must include**: Cultural safety, social determinants, higher disease burden (diabetes, CKD, bronchiectasis), interpreter/Aboriginal Health Worker involvement
- **Examples**:
  - 48M Aboriginal man, Alice Springs, CAP + bronchiectasis
  - 32F Aboriginal woman, rural NSW, gestational diabetes
  - 65M Aboriginal elder, Arnhem Land, CKD + diabetes

**CALD Patients** (Culturally and Linguistically Diverse): 30% (60 scenarios)
- **Top backgrounds**: Sudanese, Syrian, Afghan, Vietnamese, Chinese, Indian
- **Must include**: Interpreter use (MANDATORY), cultural beliefs about illness, migration trauma (refugees), mental health stigma
- **Examples**:
  - 29F Sudanese refugee, postnatal depression, Arabic interpreter required
  - 55M Chinese migrant, chest pain, reluctant to discuss mental health
  - 18F Afghan refugee, contraception counseling, cultural sensitivities

**Mainstream Australian Patients**: 50% (100 scenarios)
- **Backgrounds**: Anglo-Australian, diverse socioeconomic status, urban + rural
- **Must include**: Range of ages (pediatric to elderly), rural health barriers, LGBTIQ+ presentations
- **Examples**:
  - 32F Anglo-Australian teacher, IVF pregnancy, first trimester bleeding
  - 68M retired farmer, rural Victoria, COPD exacerbation
  - 25M gay man, Melbourne, STI screening + mental health

**Rationale**: IMG students often struggle with Aboriginal health context and interpreter use. Golden Dataset must test these competencies.

---

## 2. Seven-Step Validation Process

Each of the 200 scenarios undergoes rigorous validation before inclusion in Golden Dataset.

### Step 1: Clinical Expert Creation (2 hours per scenario)

**Who Creates Scenarios**: Australian-trained specialists with OSCE examiner experience
- FRACGP (Fellows of RACGP) for GP scenarios
- FACEM (Fellows of ACEM) for ED scenarios
- FRANZCOG (Fellows of RANZCOG) for ObGyn scenarios
- FRACP (Fellows of RACP) for medical specialty scenarios

**Deliverables** (per scenario):
1. **Patient Demographics**:
   - Name, age, gender, occupation
   - Cultural background (Aboriginal, CALD, mainstream Australian)
   - Interpreter requirement (yes/no, language)
   - Location (urban/rural, state)

2. **Chief Complaint & Opening Statement**:
   - Exact words patient says when student enters
   - Example: "G'day doc, I've had this cough for nearly a week now and I'm feeling pretty crook."

3. **Progressive Disclosure JSONB Structure**:
   - Layered information (basic → intermediate → advanced)
   - Triggered by appropriate student questions
   - Example:
   ```json
   {
     "basic": {
       "trigger": "Can you tell me about the pain?",
       "response": "It's in my chest, started this morning while I was climbing stairs"
     },
     "intermediate": {
       "trigger": "Where exactly? Can you show me?",
       "response": "Here [points to central chest]. It's crushing, like an elephant sitting on my chest. Goes down my left arm."
     },
     "advanced": {
       "trigger": "Have you ever had this before?",
       "response": "My dad died of a heart attack at 53. I'm 52 now. I've been worried about this for years."
     }
   }
   ```

4. **Emotional Profile with State Transitions**:
   - Baseline state (ANXIOUS_GUARDED, STOIC_MINIMIZING, etc.)
   - Transition triggers (empathy shown → CAUTIOUSLY_OPEN)
   - Cultural emotional style (Western_expressive, Aboriginal_stoic, CALD_reserved)
   - Pain/anxiety levels (0-10)
   - Trust threshold (how easily patient opens up)

5. **Expected Differentials** (ranked by likelihood):
   - Primary diagnosis (most likely)
   - 2-3 key differentials student should consider
   - Red flags that distinguish between them
   - Example:
   ```
   1. STEMI (most likely - crushing pain, radiation, risk factors)
   2. Unstable angina (less likely - usually <10 min, resolves with rest)
   3. PE (consider - can present similarly, check risk factors)
   4. Aortic dissection (must exclude - tearing pain, radiation to back)
   ```

6. **Critical Actions with Timeframes**:
   - What student MUST do (with time limits)
   - Auto-fail if missed
   - Example:
   ```json
   [
     {
       "action": "Call MET/000",
       "timeframe": "Immediately (within 30 seconds)",
       "auto_fail_if_missed": true
     },
     {
       "action": "Order 12-lead ECG",
       "timeframe": "Within 10 minutes",
       "auto_fail_if_missed": true
     },
     {
       "action": "Give aspirin 300mg PO",
       "timeframe": "Immediately after checking allergies",
       "auto_fail_if_wrong_dose": true
     }
   ]
   ```

7. **RAG Query Hints**:
   - Suggested queries AI Patient should make to retrieve accurate information
   - Expected confidence scores (>0.65)
   - Expected sources (eTG Cardiovascular, Talley & O'Connor, etc.)
   - Example:
   ```json
   {
     "query": "acute coronary syndrome immediate management",
     "expected_confidence": ">0.80",
     "expected_sources": ["eTG Cardiovascular", "NSW Health ACS Protocol"]
   }
   ```

**Quality Check**: Senior examiner reviews scenario for clinical accuracy, cultural appropriateness, Australian context.

---

### Step 2: AI Patient Simulation Test (30 minutes per scenario)

**Who Tests**: Medical student actor (PGY1-3 level) OR IMG candidate in ICRP preparation

**Process**:
1. Student enters simulated OSCE with AI Patient
2. **8-minute station** (standard AMC OSCE duration)
3. AI Patient responds based on progressive disclosure + emotional state machine
4. **Full conversation transcript recorded** (every question, every response)
5. **Emotional state transitions logged**:
   ```json
   {
     "0:00": "ANXIOUS_GUARDED",
     "2:15": "CAUTIOUSLY_OPEN (student showed empathy)",
     "5:30": "TRUSTING (student systematic, competent)",
     "7:00": "DISTRESSED (student explained diagnosis sensitively)"
   }
   ```
6. **RAG citations logged** for every AI Patient medical claim:
   ```json
   {
     "timestamp": "3:45",
     "ai_claim": "I have crushing central chest pain radiating to my left arm",
     "rag_confidence": 0.87,
     "citations": [
       "(Talley & O'Connor 8th ed, p.145: Chest pain characteristics)",
       "(eTG Cardiovascular 5.1, 2024: ACS presentation)"
     ]
   }
   ```

**Output**: Complete OSCE transcript ready for scoring.

---

### Step 3: AI Examiner Scoring (5 minutes per scenario)

**Process**:
1. AI Examiner receives full transcript
2. Scores using AMC 15-mark rubric (see AMC_15_MARK_RUBRIC_EXPANDED.md)
3. **Structured JSON output**:
   ```json
   {
     "communication_score": 2,
     "communication_feedback": "Adequate rapport; mostly patient-centered with occasional interruptions",
     "communication_citation": "(AMC Handbook, p.23-25: Communication criteria)",

     "clinical_reasoning_score": 3,
     "clinical_reasoning_feedback": "Identified ACS and PE as differentials; logical reasoning but missed aortic dissection",
     "clinical_reasoning_citation": "(Talley & O'Connor 8th ed, p.145-147: Chest pain differentials)",

     "information_gathering_score": 3,
     "information_gathering_feedback": "Systematic SOCRATES approach; covered risk factors well; forgot to ask about previous episodes",
     "information_gathering_citation": "(AMC Handbook, p.45-47: Systematic history taking)",

     "management_score": 2,
     "management_feedback": "Ordered ECG and called cardiology; appropriate investigations; forgot to give aspirin 300mg immediately",
     "management_citation": "(eTG Cardiovascular 5.2.1, 2024: ACS immediate management)",

     "professionalism_score": 2,
     "professionalism_feedback": "Professional throughout; asked permission before examination; maintained patient dignity",
     "professionalism_citation": "(AMC Handbook, p.12: Professionalism standards)",

     "total_score": 12,
     "pass_fail": "PASS",
     "critical_errors": []
   }
   ```

**Quality Check**: AI response logged for comparison with human examiners.

---

### Step 4: Human Examiner Scoring (15 minutes per scenario)

**Who Scores**: 3 independent AMC-trained examiners (blinded to AI score and each other's scores)

**Process**:
1. Each examiner receives same transcript (anonymized)
2. Uses official AMC 15-mark rubric
3. Scores independently:
   - Communication (0-3)
   - Clinical Reasoning (0-4)
   - Information Gathering (0-4)
   - Management (0-2)
   - Professionalism (0-2)
   - Total (/15)
   - Pass/Fail decision
   - Critical errors noted

4. **Record score breakdown**:
   ```
   Examiner 1: 12/15 (Pass)
   Examiner 2: 11/15 (Pass)
   Examiner 3: 13/15 (Pass)
   ```

**Rationale**: 3 examiners provides inter-rater reliability check. If human examiners disagree significantly (>3 marks variance), scenario may be ambiguous and needs revision.

---

### Step 5: Inter-Rater Reliability Testing

**Acceptance Criteria**:

**AI vs Human Variance** (MANDATORY for scenario inclusion):
- AI vs Human Examiner 1: ≤±2 marks variance ✅
- AI vs Human Examiner 2: ≤±2 marks variance ✅
- AI vs Human Examiner 3: ≤±2 marks variance ✅

**Human Examiner Agreement** (validates scenario quality):
- Cohen's kappa >0.70 (substantial agreement)
- If kappa <0.70 → Scenario ambiguous, needs revision

**Example Calculation**:
```
AI Examiner: 12/15
Human Examiner 1: 11/15 (variance = -1, ✅ PASS)
Human Examiner 2: 13/15 (variance = +1, ✅ PASS)
Human Examiner 3: 10/15 (variance = -2, ✅ PASS)

Result: ✅ Scenario APPROVED for Golden Dataset
```

**Example FAILURE**:
```
AI Examiner: 12/15
Human Examiner 1: 9/15 (variance = -3, ❌ FAIL - exceeds ±2)
Human Examiner 2: 14/15 (variance = +2, ✅ PASS)
Human Examiner 3: 8/15 (variance = -4, ❌ FAIL - exceeds ±2)

Result: ❌ Scenario REJECTED - proceed to Step 6 (Iteration)
```

---

### Step 6: Iteration (if variance >±2 marks)

**Process when AI Examiner fails validation**:

1. **Analyze Discrepancy**:
   - Is AI too harsh? (scoring lower than humans)
   - Is AI too lenient? (scoring higher than humans)
   - Did AI miss critical error that humans caught?
   - Did AI penalize something humans didn't?

2. **Review Specific Domain Variances**:
   ```
   Example:
   AI Communication: 1/3
   Human avg Communication: 2.3/3
   → AI being too harsh on communication (likely over-penalizing minor interruptions)
   ```

3. **Adjust AI Examiner Rubric Interpretation**:
   - Update AMC_15_MARK_RUBRIC_EXPANDED.md with clearer criteria
   - Add examples of what constitutes 1 vs 2 vs 3 marks
   - Emphasize "IMG students often speak quickly due to anxiety - minor interruptions acceptable if overall empathy shown"

4. **Re-score Scenario with Updated Prompt**:
   - Run AI Examiner again with refined rubric
   - Compare new AI score to human scores
   - Check if variance now ≤±2 marks

5. **Repeat Until Validated**:
   - Maximum 3 iterations
   - If still failing after 3 iterations → Flag for senior clinical reviewer (may be scenario issue, not AI issue)

**Common Iteration Patterns**:
- **Week 1-2**: AI often too harsh on communication (learns to be more forgiving)
- **Week 3-4**: AI learns to catch critical errors humans catch
- **Week 5-6**: Fine-tuning professionalism and management scoring

---

### Step 7: Final Approval

**Approval Authority**:
- Clinical Advisor (senior AMC examiner with 5+ years experience)
- Quality Assurance Lead

**Final Approval Criteria**:
✅ **AI vs human variance ≤±2 marks** (all 3 human examiners)
✅ **Critical error detection 100% accurate** (AI catches all critical errors humans catch, no false positives)
✅ **Feedback clinically appropriate** (reviewed by clinical advisor)
✅ **Australian medical context correct throughout** (terminology, guidelines, emergency numbers)
✅ **RAG citations valid** (all confidence >0.65, Australian sources only)
✅ **Cultural appropriateness confirmed** (if Aboriginal/CALD scenario, reviewed by cultural consultant)

**Approval Documentation**:
```json
{
  "scenario_id": "GOLDEN_CARDIO_001",
  "specialty": "Cardiology",
  "difficulty": "Advanced",
  "approved_by": "Dr. Sarah Chen, FRACP",
  "approval_date": "2026-02-15",
  "ai_human_variance": [-1, +1, -2],
  "human_inter_rater_kappa": 0.78,
  "critical_errors_detected_correctly": true,
  "cultural_review_completed": true,
  "rag_validation_passed": true,
  "approved_for_production": true
}
```

**Rejection Criteria** (scenario NOT approved):
- ❌ AI variance >±2 marks after 3 iterations
- ❌ Human examiners disagree significantly (kappa <0.60)
- ❌ Critical error detection failed
- ❌ Cultural insensitivity detected
- ❌ RAG citations invalid (<0.65 confidence or non-Australian sources)

**If Rejected**: Scenario returned to clinical expert for revision (Step 1).

---

## 3. Dataset Structure

### 3.1 File Organization

**Directory**: `data/golden_dataset/`

**Structure**:
```
data/golden_dataset/
├── README.md (this file)
├── cardiology/
│   ├── GOLDEN_CARDIO_001_ACS_STEMI.json
│   ├── GOLDEN_CARDIO_002_Heart_Failure.json
│   └── ... (25 files)
├── respiratory/
│   ├── GOLDEN_RESP_001_Asthma_Exacerbation.json
│   └── ... (25 files)
├── gastro/
│   └── ... (25 files)
├── neuro/
│   └── ... (25 files)
├── endocrine/
│   └── ... (25 files)
├── psychiatry/
│   └── ... (25 files)
├── surgery/
│   └── ... (25 files)
├── obgyn/
│   └── ... (25 files)
└── validation_reports/
    ├── inter_rater_reliability.csv
    ├── ai_human_variance_summary.json
    └── quarterly_recalibration_2026_Q1.json
```

### 3.2 Scenario JSON Schema

**File**: `GOLDEN_CARDIO_001_ACS_STEMI.json`

```json
{
  "scenario_metadata": {
    "scenario_id": "GOLDEN_CARDIO_001",
    "specialty": "Cardiology",
    "diagnosis": "STEMI (ST-Elevation Myocardial Infarction)",
    "difficulty": "Intermediate",
    "target_pass_rate": "60-70%",
    "created_by": "Dr. Michael Wong, FRACP",
    "created_date": "2026-02-10",
    "approved_date": "2026-02-15",
    "cultural_background": "Mainstream Australian"
  },

  "patient_demographics": {
    "name": "Robert Chen",
    "age": 52,
    "gender": "Male",
    "occupation": "Accountant",
    "cultural_background": "Anglo-Australian",
    "aboriginal_torres_strait_islander": false,
    "cald_background": false,
    "interpreter_required": false,
    "location": "Sydney, NSW",
    "remote_area": false
  },

  "chief_complaint": "Doctor, I've had this terrible chest pain since this morning. It won't go away.",

  "progressive_disclosure": {
    "basic": { ... },
    "intermediate": { ... },
    "advanced": { ... }
  },

  "emotional_profile": {
    "baseline_state": "ANXIOUS_GUARDED",
    "pain_level": 8,
    "anxiety_level": 7,
    "cultural_emotional_style": "Western_expressive",
    "state_transitions": { ... }
  },

  "expected_differentials": [
    {
      "rank": 1,
      "diagnosis": "STEMI",
      "likelihood": "Most likely",
      "rationale": "Crushing central chest pain >20 min, radiation to left arm, diaphoresis, risk factors"
    },
    {
      "rank": 2,
      "diagnosis": "Unstable angina",
      "likelihood": "Possible",
      "rationale": "Similar presentation but usually shorter duration, resolves with GTN"
    },
    {
      "rank": 3,
      "diagnosis": "Pulmonary embolism",
      "likelihood": "Must exclude",
      "rationale": "Can present with chest pain, check for PE risk factors"
    },
    {
      "rank": 4,
      "diagnosis": "Aortic dissection",
      "likelihood": "Must exclude",
      "rationale": "Tearing chest pain radiating to back, requires urgent imaging"
    }
  ],

  "critical_actions": [ ... ],

  "rag_query_hints": [ ... ],

  "validation_results": {
    "ai_examiner_score": 12,
    "human_examiner_scores": [11, 13, 10],
    "ai_human_variance": [-1, +1, -2],
    "human_inter_rater_kappa": 0.78,
    "critical_errors_detected": true,
    "rag_validation_passed": true,
    "approved": true
  }
}
```

---

## 4. Quarterly Recalibration

**Purpose**: Ensure AI Examiner scoring remains accurate over time (no drift).

**Frequency**: Every 3 months (Q1, Q2, Q3, Q4)

**Process**:

### Step 1: Random Sampling
- Select 20 scenarios randomly from Golden Dataset (10%)
- Stratify by specialty (2-3 per specialty)
- Include mix of difficulty levels

### Step 2: New Medical Student Actors
- Recruit 10 different medical students (PGY1-3 level)
- Each student completes 2 random OSCE scenarios
- Generate 20 new transcripts

### Step 3: AI Examiner Re-Scoring
- Run current AI Examiner on all 20 transcripts
- Record scores

### Step 4: New Human Examiner Panel
- Recruit 3 NEW human AMC examiners (not the original validators)
- Each examiner scores all 20 transcripts (blinded)
- Record scores

### Step 5: Compare Variance
- Calculate AI vs human variance for each scenario
- **Acceptance**: All 20 scenarios still have ≤±2 marks variance
- **Warning**: 1-3 scenarios exceed ±2 marks → Minor drift, adjust AI prompts
- **Failure**: >3 scenarios exceed ±2 marks → Major drift, full re-calibration required

### Step 6: Analyze Drift Patterns
**Common drift patterns**:
- **AI becoming harsher over time**: Updated rubric examples making AI more critical
- **AI becoming more lenient**: AI learning to excuse mistakes
- **Domain-specific drift**: AI communication scoring drifting but clinical reasoning stable

### Step 7: Corrective Action
- Update AMC_15_MARK_RUBRIC_EXPANDED.md with additional examples
- Re-run validation on failed scenarios
- Document changes in quarterly recalibration report

**Example Report**:
```json
{
  "recalibration_date": "2026-05-01",
  "quarter": "Q2 2026",
  "scenarios_tested": 20,
  "scenarios_passed": 18,
  "scenarios_failed": 2,
  "drift_detected": "Minor - AI communication scoring 0.5 marks harsher",
  "corrective_action": "Updated rubric with 'minor interruptions acceptable if overall empathy shown'",
  "re_validation_passed": true
}
```

---

## 5. Success Criteria

**Golden Dataset Complete When**:

✅ **200 scenarios created** (25 per specialty × 8)
✅ **All 200 scenarios validated** (AI vs human variance ≤±2 marks)
✅ **Diversity targets met**:
   - 40 Aboriginal/Torres Strait Islander scenarios (20%)
   - 60 CALD scenarios (30%)
   - 100 mainstream Australian scenarios (50%)
✅ **Difficulty distribution achieved**:
   - 80 Foundation scenarios (target pass rate 75-85%)
   - 80 Intermediate scenarios (target pass rate 60-70%)
   - 40 Advanced scenarios (target pass rate 40-50%)
✅ **Cultural reviews completed** (all Aboriginal/CALD scenarios reviewed by cultural consultants)
✅ **RAG validation passed** (all AI Patient responses have citations >0.65, Australian sources only)
✅ **Documentation complete** (all scenarios have JSON files + validation reports)
✅ **Quarterly recalibration schedule established** (Q1, Q2, Q3, Q4)

---

## 6. Timeline and Resources

### 6.1 Timeline

**Scenario Creation**: 2 hours × 200 scenarios = **400 hours** (50 days @ 8 hours/day)
- Can be parallelized: 5 clinical experts working simultaneously = 10 days

**AI Patient Testing**: 30 min × 200 scenarios = **100 hours** (12.5 days @ 8 hours/day)
- Can be parallelized: 5 medical students testing simultaneously = 2.5 days

**AI Examiner Scoring**: 5 min × 200 scenarios = **16.7 hours** (automated, <1 day)

**Human Examiner Scoring**: 15 min × 200 scenarios × 3 examiners = **150 hours** (18.75 days @ 8 hours/day)
- Can be parallelized: 3 examiners working simultaneously = 6.25 days

**Iteration & Approval**: Estimate 30% of scenarios need 1 iteration = 60 scenarios × 1 hour = **60 hours** (7.5 days)

**Total Timeline**: ~30-40 working days (6-8 weeks) with parallelization

### 6.2 Resources Required

**Clinical Experts**: 5 specialists (FRACGP, FACEM, FRANZCOG, RACP)
- $200/hour × 400 hours = $80,000

**Medical Student Actors**: 5 students (PGY1-3)
- $50/hour × 100 hours = $5,000

**Human Examiner Panel**: 3 AMC-trained examiners
- $150/hour × 150 hours = $22,500

**Cultural Consultants**: Aboriginal health consultant + CALD health consultant
- $150/hour × 40 hours = $6,000

**Total Budget**: ~$113,500 for Golden Dataset creation

**Quarterly Recalibration Budget**: ~$8,000/quarter (20 scenarios × shorter process)

---

## 7. Use Cases

### 7.1 Calibrating AI Examiner Before Production

**Process**:
1. Create initial AI Examiner prompt with AMC rubric
2. Test on 10 Golden Dataset scenarios
3. Calculate variance vs human examiners
4. Iterate on prompt until variance ≤±2 marks
5. Test on remaining 190 scenarios
6. If all pass → Deploy to production
7. If >5% fail → Continue iteration

### 7.2 Testing RAG System Accuracy

**Process**:
1. Run AI Patient on all 200 scenarios
2. Log all RAG citations
3. Verify:
   - All confidence scores >0.65 ✅
   - All sources Australian ✅
   - No hallucinations detected ✅
4. If validation fails → Improve RAG embeddings, re-test

### 7.3 Establishing Pass Rate Benchmarks

**Process**:
1. Have 50 IMG students (real ICRP candidates) complete 4 random Golden Dataset OSCEs each
2. AI Examiner scores all attempts
3. Calculate pass rates by difficulty:
   - Foundation scenarios: 78% pass rate ✅ (target 75-85%)
   - Intermediate scenarios: 64% pass rate ✅ (target 60-70%)
   - Advanced scenarios: 42% pass rate ✅ (target 40-50%)
4. Use these benchmarks to grade production OSCEs

### 7.4 Quality Assurance Spot Checks

**Monthly QA Process**:
1. Select 5 random scenarios from Golden Dataset
2. Have 5 new medical students complete them
3. AI Examiner scores
4. Compare to original human examiner scores
5. If variance increases → Trigger recalibration

---

**End of Golden Dataset Specification** - Ready for Clinical Advisor review and resourcing approval
