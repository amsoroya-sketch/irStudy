# PRD: AI OSCE Scoring System with AMC 15-Mark Rubric

**PRD ID**: PRD_AI_OSCE_004_SCORING_SYSTEM
**Category**: Backend + AI Scoring Engine
**Priority**: P0-Critical (DEPENDS on PRD_001 & PRD_002, BLOCKS exam completion flow)
**Estimated Effort**: 24-28 hours
**Dependencies**: PRD_AI_OSCE_001_DATABASE_AND_APIS (MUST be complete), PRD_AI_OSCE_002_AI_INTEGRATION (MUST be complete)
**Status**: Not Started

---

## R - REQUEST (What & Why)

### User Story

**As a** medical student
**I want** automated, immediate scoring of my OSCE practice sessions using the AMC 15-mark rubric
**So that** I receive consistent, clinically-validated feedback aligned to Australian medical examination standards within seconds of completing a session

**As a** system architect
**I want** an AI Examiner scoring system that detects critical errors (20+ rules), validates scores against 200+ golden dataset scenarios, and generates personalized feedback
**So that** scoring is reliable, auditable, and trustworthy for progression decisions

### Business Context

The AI OSCE Simulation System requires an automated scoring engine that delivers:

1. **AMC 15-Mark Rubric Implementation** (Claude 3.5 Sonnet, temp=0.1)
   - Communication (0-3): Empathy, rapport, listening
   - Clinical Reasoning (0-4): Differential diagnosis, prioritization
   - Information Gathering (0-4): Systematic history, completeness
   - Management (0-2): Safety, evidence-base, appropriateness
   - Professionalism (0-2): Respect, dignity, cultural sensitivity
   - Pass Threshold: ≥9/15 AND no critical errors
   - Fail Threshold: ≤7/15 OR critical error detected

2. **Critical Error Detection** (Rules-Based Engine)
   - 20+ hallmark error rules (missed red flags, unsafe actions, cultural insensitivity)
   - Auto-fail logic: One critical error → FAIL regardless of total score
   - Examples: Chest pain + no ECG, severe hypertension + inappropriate medication, patient dignity violations

3. **Golden Dataset Validation** (200 Scenarios)
   - AI vs. Human examiner score variance ≤2 marks on 15-mark scale
   - Pass/fail agreement ≥99%
   - Confidence metrics (0.0-1.0) for edge cases
   - Continuous improvement through dataset expansion

4. **Feedback Generation** (Narrative + Structured)
   - Strengths (3-5 specific achievements)
   - Areas for improvement (2-4 actionable gaps)
   - Transcript annotations (evidence references)
   - Constructive, growth-oriented tone

**Business Value**:
- Scaling from 10 human examiners to unlimited AI capacity
- Consistent scoring across 360+ patient personas
- Immediate feedback loop (minutes vs. days)
- Cost: $0.004-0.006 per scoring session (vs. $50-100 human examiner time)
- Audit trail: Every score versioned, traceable, defensible

### Success Metrics

- **Scoring Accuracy**: AI scores ≥95% aligned with expert human validation (golden dataset)
- **Critical Error Detection**: Catches 100% of obvious red flags, ≤5% false positives
- **Feedback Quality**: 90% of students find feedback "specific and actionable"
- **Response Time**: Scoring complete <5 seconds (p95) after session ends
- **Pass/Fail Reliability**: ≥99% agreement between AI and human examiners on pass/fail decisions
- **Golden Dataset Coverage**: 200 scenarios representing 10+ clinical areas
- **Prompt Versioning**: Track all 3+ scoring prompt versions (v1.0, v2.0, v2.1) with accuracy metrics
- **System Uptime**: 99.9% scoring availability
- **AMC Alignment**: 100% compliance with AMC Clinical Examination standards

### Scope

**In Scope**:
- AI Examiner scoring service (Claude 3.5 Sonnet, temp=0.1 for consistency)
- AMC 15-mark rubric implementation (5 domains, weighted scoring)
- Critical error detection engine (20+ rules, auto-fail logic)
- Scoring confidence calculation (0.0-1.0 range)
- Feedback generation (strengths, improvements, narrative)
- Scoring prompt version control (v1.0, v2.0, v2.1)
- Golden dataset creation (200 scenarios with expert scores)
- Golden dataset validation (AI vs. human alignment ≥95%)
- Transcript annotation system (evidence references)
- Cost tracking (scoring tokens, model usage)
- Scoring data persistence (PostgreSQL osce_scores table)
- User progress updates (trigger-based from scores)

**Out of Scope** (Future):
- Real-time score adjustments by human examiners (PRD_005)
- Machine learning-based confidence prediction (Phase 2)
- Multi-language feedback generation (Phase 2)
- Peer comparison analytics (Phase 3)
- Spaced repetition based on scores (Phase 3)

---

## A - ARCHITECTURE (How)

### Technical Approach

**AI Examiner System**: Implement Claude 3.5 Sonnet scorer with:
1. Versioned SYSTEM_PROMPT templates (AMC rubric, scoring criteria, 5 domains)
2. Dynamic USER_PROMPT construction (scenario + transcript + expected approach)
3. Structured JSON output validation (5 scores + feedback + critical errors)
4. Critical error detection rules (20+ conditions)
5. Scoring confidence calculation (evidence-based)

**Golden Dataset Validation**: Establish 200-scenario dataset with:
1. Expert human-scored reference sessions
2. AI scoring vs. human comparison
3. Variance tracking (mark difference, pass/fail alignment)
4. Continuous expansion process

**Key Design Decisions**:
1. **Temperature = 0.1**: Deterministic scoring (same transcript → same score)
2. **Versioned prompts**: Database-stored, versioned, auditable for regulatory compliance
3. **Critical errors**: Predefined rules (not AI judgment alone) + AI-detected subtleties
4. **Confidence scoring**: Evidence clarity + score consistency + edge case detection
5. **Golden dataset**: 10% of sessions reserved for human expert review (low confidence)
6. **Transcript annotations**: Evidence snippets highlighted for feedback
7. **Audit trail**: Every score logged with prompt version, model, timestamp

### System Design

#### Component Diagram
```
┌──────────────────────────────────────────────────────┐
│         FRONTEND (React)                              │
│  - Results page (score breakdown, feedback)           │
│  - PASS/FAIL badge (green/red)                        │
│  - Detailed feedback per rubric category              │
└────────────────────┬─────────────────────────────────┘
                     │ WebSocket (scoring_complete)
                     ↓
┌──────────────────────────────────────────────────────┐
│         BACKEND (FastAPI, Python 3.11)                │
│                                                       │
│  ┌─────────────────────────────────────────────────┐ │
│  │  Session End Trigger                            │ │
│  │  - Timer expires at 8:00 mark                   │ │
│  │  - Update session_state = 'scoring'             │ │
│  │  - Fetch conversation_history from Redis/PG    │ │
│  └─────────────────────────────────────────────────┘ │
│                     ↓                                  │
│  ┌─────────────────────────────────────────────────┐ │
│  │  AI Examiner Scoring Service                    │ │
│  │  - Load SYSTEM_PROMPT (versioned, temp=0.1)    │ │
│  │  - Build USER_PROMPT (scenario + transcript)   │ │
│  │  - Call Claude 3.5 Sonnet                       │ │
│  │  - Validate JSON (5 scores, feedback)           │ │
│  │  - Detect critical errors (rules engine)        │ │
│  │  - Calculate confidence (0.0-1.0)               │ │
│  └─────────────────────────────────────────────────┘ │
│                     ↓                                  │
│  ┌─────────────────────────────────────────────────┐ │
│  │  Critical Error Detection (Rules Engine)        │ │
│  │  - Rule 1: Red flag missed → auto-fail         │ │
│  │  - Rule 2: Unsafe action → auto-fail           │ │
│  │  - Rule 3: Cultural insensitivity → auto-fail  │ │
│  │  - Rule 4-20: Domain-specific violations       │ │
│  │  - Returns: error_list[], auto_fail boolean     │ │
│  └─────────────────────────────────────────────────┘ │
│                     ↓                                  │
│  ┌─────────────────────────────────────────────────┐ │
│  │  Feedback Generation Service                    │ │
│  │  - Extract strengths (3-5 from transcript)     │ │
│  │  - Identify improvements (2-4 gaps)             │ │
│  │  - Generate narrative (constructive tone)       │ │
│  │  - Annotate transcript (evidence references)    │ │
│  └─────────────────────────────────────────────────┘ │
│                     ↓                                  │
│  ┌─────────────────────────────────────────────────┐ │
│  │  Score Persistence & Validation                 │ │
│  │  - INSERT osce_scores (PostgreSQL)              │ │
│  │  - Calculate total_score = sum(5 domains)      │ │
│  │  - Validate: 0-15 range, correct math           │ │
│  │  - Determine pass_fail logic                    │ │
│  │  - Store confidence, tokens, cost               │ │
│  │  - Save scored_at, scoring_model, prompt_ver   │ │
│  └─────────────────────────────────────────────────┘ │
│                     ↓                                  │
│  ┌─────────────────────────────────────────────────┐ │
│  │  Trigger: user_progress Update                  │ │
│  │  - Function: update_ai_osce_progress()          │ │
│  │  - ai_osces_attempted ← +1                      │ │
│  │  - ai_osces_passed ← +1 (if PASS)               │ │
│  │  - ai_osce_avg_score ← recalculate              │ │
│  └─────────────────────────────────────────────────┘ │
│                     ↓                                  │
│  ┌─────────────────────────────────────────────────┐ │
│  │  WebSocket Broadcast (Results)                  │ │
│  │  - Send: {total_score, pass_fail, feedback}    │ │
│  │  - Send: {breakdown, strengths, improvements}  │ │
│  │  - Update session_state = 'complete'            │ │
│  └─────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────┘
                     ↓ SQLAlchemy ORM
┌──────────────────────────────────────────────────────┐
│           POSTGRESQL 15 DATABASE                      │
│  - osce_scores (5 domains, feedback, critical_errors)│
│  - scoring_prompt_versions (v1.0, v2.0, v2.1)       │
│  - golden_dataset_results (200 sessions)             │
│  - user_progress (updated via trigger)               │
└──────────────────────────────────────────────────────┘
```

#### AI Examiner Scoring Flow (Detailed)

```
PHASE 1: PREPARE SCORING CONTEXT
═════════════════════════════════

Session ends at 8:00 mark (WebSocket timer expires)
  ↓
Backend: UPDATE osce_attempts SET session_state = 'scoring'
  ↓
Backend: Fetch from PostgreSQL:
  - conversation_history (full 8-min transcript)
  - emotional_state_transitions (state progression)
  - student_actions (categorized communications)
  - persona details (expected differentials, critical actions)
  ↓
Backend: Fetch scoring prompt version:
  - SELECT * FROM scoring_prompt_versions WHERE active = TRUE
  - Current: v2.1 (98.5% accuracy on golden dataset)


PHASE 2: BUILD AI EXAMINER PROMPT
═════════════════════════════════

SYSTEM_PROMPT (from scoring_prompt_versions.prompt_template):
───────────────────────────────────────────────────────────
You are an experienced AMC Clinical Examiner. Your task: score this
OSCE station using the AMC 15-mark rubric.

SCORING DOMAINS (Total 15 marks):

1. COMMUNICATION (0-3 marks)
   0: Poor - Minimal eye contact, frequent interruptions, no rapport
   1: Below standard - Limited empathy, some interruptions, rushed
   2: Satisfactory - Maintains rapport, mostly listens, clear explanations
   3: Excellent - Outstanding empathy, active listening, culturally sensitive

2. CLINICAL REASONING (0-4 marks)
   0: No differential diagnosis; missed obvious diagnosis
   1: Incomplete/incorrect DDx; major gaps in thinking
   2: Reasonable DDx with some gaps; logical approach
   3: Comprehensive DDx, prioritized appropriately
   4: Excellent - DDx with clear prioritization + justification

3. INFORMATION GATHERING (0-4 marks)
   0: Missed critical information; systematic approach absent
   1: Incomplete history; significant gaps in data collection
   2: Adequate history with minor gaps; mostly systematic
   3: Thorough systematic history; all relevant information obtained
   4: Excellent - Systematic, comprehensive, no gaps; efficient time use

4. MANAGEMENT (0-2 marks)
   0: Unsafe/inappropriate management; potential patient harm
   1: Partially appropriate management; some gaps in safety/evidence
   2: Safe, appropriate, evidence-based management

5. PROFESSIONALISM (0-2 marks)
   0: Unprofessional; dismissive, disrespectful, inappropriate
   1: Mostly professional; minor lapses in demeanor or respect
   2: Exemplary professionalism; respectful, appropriate, maintains dignity

PASS/FAIL RULES:
- PASS: Total ≥9/15 (60%) AND no critical errors
- BORDERLINE: Total = 8/15
- FAIL: Total ≤7/15 OR critical error detected

CRITICAL ERRORS (Auto-fail, regardless of score):
1. Missed acute red flag (e.g., chest pain + no ECG)
2. Unsafe intervention (contraindicated medication, wrong dose)
3. Severe cultural insensitivity or discriminatory behavior
4. Patient safety compromised (abandoned, ignored distress)
5. Missed anaphylaxis signs
6. Incorrect vital sign interpretation
7. Failed to escalate appropriate emergency
8. Inadequate pain management
9. Medication allergy not checked
10. Infection control violations
11. No resuscitation in cardiac arrest
12. Dismissive of serious symptoms
13. Inappropriate intimate examination
14. Failed to obtain informed consent
15. Severe communication breakdown
[15+ more domain-specific rules...]

OUTPUT FORMAT (Valid JSON required):
{
  "communication_score": 0-3,
  "communication_feedback": "specific evidence-based feedback",
  "clinical_reasoning_score": 0-4,
  "clinical_reasoning_feedback": "...",
  "information_gathering_score": 0-4,
  "information_gathering_feedback": "...",
  "management_score": 0-2,
  "management_feedback": "...",
  "professionalism_score": 0-2,
  "professionalism_feedback": "...",
  "total_score": 0-15,
  "pass_fail": "PASS|BORDERLINE|FAIL",
  "critical_errors": ["error1", ...] or [],
  "strengths": ["strength1", "strength2"],
  "areas_for_improvement": ["area1", "area2"],
  "overall_feedback": "narrative summary"
}


USER_PROMPT (Specific Station):
──────────────────────────────

PATIENT SCENARIO
════════════════
Name: Robert Chen, 52M, Chinese Australian accountant
Chief Complaint: Chest pain for 2 hours (crushing, radiating to left arm)
Context: Diaphoretic, anxious, family history of early MI

EXPECTED CLINICAL APPROACH
════════════════════════════
Key differentials: STEMI (most likely), Unstable angina, PE
Critical actions:
- ECG within 10 minutes (red flag assessment)
- Aspirin 300mg immediately (if not contraindicated)
- IV access, bloods (troponin, FBC, lipids)
- Continuous cardiac monitoring
- Urgent cardiology/emergency team involvement
- Pain relief (morphine if severe)

ACTUAL STUDENT CONVERSATION (8-min transcript)
═════════════════════════════════════════════════
[Full transcript with 8-10 student/patient exchanges]

Student: "Good morning Mr. Chen. I understand you're having chest pain
         today. I'm here to help. Can you tell me what happened?"

Patient: "Doctor, I've been having this terrible chest pain for the past
         2 hours. It started at work and hasn't gone away. I'm really
         worried."

[... 8 more exchanges ...]

Student: "I'm ordering an ECG right now to check your heart's electrical
         activity. I'm also giving you aspirin to prevent blood clots.
         And I'm calling our cardiology team to get you to hospital
         for more tests. Do you have any questions?"

Patient: "I understand. Thank you for explaining everything. I feel a bit
         better knowing what's going on."

Now score this OSCE performance using the AMC 15-mark rubric above.
Focus on evidence from the transcript. Be specific, not generic.


PHASE 3: CALL CLAUDE 3.5 SONNET (AI EXAMINER)
═════════════════════════════════════════════

LLM Call Parameters:
  model: "claude-3-5-sonnet-20250219"
  temperature: 0.1  # Deterministic scoring (consistency critical)
  max_tokens: 1000
  system: [SYSTEM_PROMPT from scoring_prompt_versions]
  user: [USER_PROMPT constructed above]

Claude Response (JSON):
{
  "communication_score": 3,
  "communication_feedback": "Excellent communication throughout. Student opened
                            with empathy and clear introduction. Used open-ended
                            questions to understand concerns. Patient progressed from
                            anxious to trusting, indicating outstanding rapport.",

  "clinical_reasoning_score": 4,
  "clinical_reasoning_feedback": "Outstanding clinical reasoning. Student recognized
                                 ACS immediately from red flags (crushing pain,
                                 radiation, diaphoresis). Differential diagnosis
                                 appropriate with STEMI prioritized. Clinical
                                 decision-making evidence-based.",

  "information_gathering_score": 4,
  "information_gathering_feedback": "Systematic, comprehensive history. Covered pain
                                    characteristics, associated symptoms (dyspnea,
                                    diaphoresis), medical history (diabetes,
                                    cholesterol), medications, smoking, family history.
                                    No gaps. Efficient time use.",

  "management_score": 2,
  "management_feedback": "Safe, appropriate, evidence-based management. ECG ordered
                        immediately (critical action). Aspirin 300mg given (correct
                        dose). Cardiology involvement arranged. Monitoring implied.",

  "professionalism_score": 2,
  "professionalism_feedback": "Exemplary professionalism. Respectful tone, clear
                             explanations. Procedures explained to alleviate anxiety.
                             Patient dignity and autonomy maintained.",

  "total_score": 15,
  "pass_fail": "PASS",
  "critical_errors": [],

  "strengths": [
    "Recognized acute coronary syndrome immediately",
    "Outstanding empathy and communication",
    "Systematic history taking",
    "Evidence-based emergency management"
  ],

  "areas_for_improvement": [
    "Could have explored allergies explicitly",
    "Minor: Could have offered analgesia proactively"
  ],

  "overall_feedback": "Excellent performance. Student demonstrated clinical acumen,
                     communication skills, and appropriate emergency management.
                     Meets AMC Clinical Examination pass standard."
}

Tokens used: 1,245 (input) + 156 (output) = 1,401 total
Cost: 1,401 × $0.003/1K = $0.004203


PHASE 4: VALIDATE & PROCESS SCORE
══════════════════════════════════

1. JSON Validation (Pydantic):
   ✓ 5 scores present (0-3, 0-4, 0-4, 0-2, 0-2)
   ✓ total_score = 3+4+4+2+2 = 15 ✓
   ✓ pass_fail in ['PASS', 'BORDERLINE', 'FAIL']
   ✓ critical_errors is array
   ✓ Feedback fields non-empty

2. Critical Error Detection (Rules Engine):
   ✓ All 20+ rules executed against transcript
   ✓ Results: [] (no critical errors)

3. Confidence Calculation:
   evidence_clarity = 0.95  (transcript very clear)
   score_consistency = 0.98  (scores match performance)
   edge_case_penalty = 0.0   (no ambiguous situations)
   confidence = (0.95×0.5 + 0.98×0.4 - 0.0×0.1) = 0.97 (97% confidence)

4. Save to PostgreSQL:
   INSERT INTO osce_scores (
     score_id, attempt_id,
     communication_score, communication_feedback,
     clinical_reasoning_score, clinical_reasoning_feedback,
     information_gathering_score, information_gathering_feedback,
     management_score, management_feedback,
     professionalism_score, professionalism_feedback,
     total_score, pass_fail, critical_errors,
     strengths, areas_for_improvement, overall_feedback,
     scored_by, scoring_model, scoring_prompt_version,
     scoring_confidence,
     scored_at
   ) VALUES (
     uuid, attempt_id,
     3, "Excellent communication...",
     4, "Outstanding clinical reasoning...",
     4, "Systematic and thorough...",
     2, "Safe, appropriate, evidence-based...",
     2, "Exemplary professionalism...",
     15, "PASS", [],
     ["Recognized ACS...", ...],
     ["Could have explored...", ...],
     "Excellent performance...",
     "ai_examiner",
     "claude-3-5-sonnet-20250219",
     "v2.1",
     0.97,  # Confidence 97%
     NOW()
   )

5. Update Session State:
   UPDATE osce_attempts
   SET session_state = 'complete',
       total_messages = 13,
       total_tokens_used = 1566,
       llm_cost_usd = 0.0048,
       updated_at = NOW()
   WHERE attempt_id = {attempt_id}

6. Trigger user_progress Update:
   Function: update_ai_osce_progress()
   Updates:
   - ai_osces_attempted ← +1
   - ai_osces_passed ← +1 (since pass_fail = PASS)
   - ai_osce_avg_score ← (15+prev_avg)/count
   - last_ai_osce_at ← NOW()


PHASE 5: BROADCAST RESULTS
═════════════════════════════════

WebSocket: Send to student
{
  "type": "scoring_complete",
  "total_score": 15,
  "max_score": 15,
  "percentage": 100,
  "pass_fail": "PASS",
  "breakdown": {
    "communication": {"score": 3, "max": 3, "feedback": "..."},
    "clinical_reasoning": {"score": 4, "max": 4, "feedback": "..."},
    "information_gathering": {"score": 4, "max": 4, "feedback": "..."},
    "management": {"score": 2, "max": 2, "feedback": "..."},
    "professionalism": {"score": 2, "max": 2, "feedback": "..."}
  },
  "strengths": [
    "Recognized acute coronary syndrome immediately",
    ...
  ],
  "areas_for_improvement": [
    "Could have explored allergies explicitly",
    ...
  ],
  "overall_feedback": "Excellent performance...",
  "timestamp": "2026-02-16T10:14:30Z"
}

Frontend: Display results page
  - Large PASS badge (green)
  - Score: 15/15 (100%) with progress bar
  - Breakdown table (5 domains with scores)
  - Detailed feedback per domain
  - Conversation transcript (annotations for evidence)
  - Strengths & improvements highlighted
  - Options: Review, Save PDF, Retry, Next Station
```

#### Database Extensions

**Table: osce_scores** (Stores All Scoring Results)
```sql
CREATE TABLE osce_scores (
    score_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    attempt_id UUID NOT NULL REFERENCES osce_attempts(attempt_id),

    -- AMC 15-Mark Rubric Scores
    communication_score SMALLINT CHECK (communication_score >= 0 AND communication_score <= 3),
    communication_feedback TEXT NOT NULL,

    clinical_reasoning_score SMALLINT CHECK (clinical_reasoning_score >= 0 AND clinical_reasoning_score <= 4),
    clinical_reasoning_feedback TEXT NOT NULL,

    information_gathering_score SMALLINT CHECK (information_gathering_score >= 0 AND information_gathering_score <= 4),
    information_gathering_feedback TEXT NOT NULL,

    management_score SMALLINT CHECK (management_score >= 0 AND management_score <= 2),
    management_feedback TEXT NOT NULL,

    professionalism_score SMALLINT CHECK (professionalism_score >= 0 AND professionalism_score <= 2),
    professionalism_feedback TEXT NOT NULL,

    -- Total & Status
    total_score SMALLINT GENERATED ALWAYS AS (
        communication_score + clinical_reasoning_score +
        information_gathering_score + management_score + professionalism_score
    ) STORED,
    pass_fail VARCHAR(10) CHECK (pass_fail IN ('PASS', 'BORDERLINE', 'FAIL')),

    -- Critical Errors & Feedback
    critical_errors JSONB DEFAULT '[]'::jsonb,
    strengths TEXT[],
    areas_for_improvement TEXT[],
    overall_feedback TEXT NOT NULL,

    -- Scoring Metadata
    scored_by VARCHAR(50) DEFAULT 'ai_examiner',  -- 'ai_examiner' or 'human_reviewer'
    scoring_model VARCHAR(100) DEFAULT 'claude-3-5-sonnet-20250219',
    scoring_prompt_version VARCHAR(20) DEFAULT 'v2.1',
    scoring_confidence DECIMAL(3,2) CHECK (scoring_confidence >= 0.0 AND scoring_confidence <= 1.0),

    -- Cost Tracking
    scoring_tokens_used INTEGER,
    scoring_cost_usd DECIMAL(10,6),

    -- Timestamps
    scored_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(attempt_id)  -- One score per attempt
);

-- Indexes
CREATE INDEX idx_osce_scores_pass_fail ON osce_scores(pass_fail);
CREATE INDEX idx_osce_scores_user_id ON osce_scores USING (
    SELECT user_id FROM osce_attempts WHERE attempt_id = osce_scores.attempt_id
);
```

**Table: scoring_prompt_versions** (Version Control for Scoring Prompts)
```sql
CREATE TABLE scoring_prompt_versions (
    version_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    version VARCHAR(20) UNIQUE NOT NULL,  -- e.g., "v1.0", "v2.0", "v2.1"
    prompt_template TEXT NOT NULL,  -- Full SYSTEM_PROMPT for AI Examiner
    rubric_definition JSONB NOT NULL,  -- Structured rubric (domains, ranges, criteria)
    active BOOLEAN DEFAULT FALSE,  -- Only one active version at a time

    -- Accuracy Metrics
    test_dataset_size INTEGER,  -- Number of golden dataset sessions tested
    test_dataset_accuracy DECIMAL(3,2),  -- 0.95 = 95% accuracy
    test_pass_fail_agreement DECIMAL(3,2),  -- 1.0 = 100% agreement
    test_variance_mean DECIMAL(3,2),  -- Avg variance from human scores

    -- Metadata
    release_notes TEXT,  -- Changes from previous version
    created_by UUID REFERENCES users(user_id),
    created_at TIMESTAMP DEFAULT NOW(),
    archived_at TIMESTAMP NULL,

    CONSTRAINT valid_version_format CHECK (version ~ '^v\d+\.\d+$')
);

-- Example data:
-- v1.0: Initial baseline (90% accuracy)
-- v2.0: Improved critical error detection (95% accuracy)
-- v2.1: Enhanced feedback generation (98.5% accuracy, current)
```

**Table: golden_dataset_results** (Validation of AI vs. Human Scoring)
```sql
CREATE TABLE golden_dataset_results (
    result_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL,  -- Reference to actual session (or mock scenario)

    -- Human Expert Scores
    human_communication_score SMALLINT,
    human_clinical_reasoning_score SMALLINT,
    human_information_gathering_score SMALLINT,
    human_management_score SMALLINT,
    human_professionalism_score SMALLINT,
    human_total_score SMALLINT,
    human_pass_fail VARCHAR(10),

    -- AI Examiner Scores
    ai_score_id UUID REFERENCES osce_scores(score_id),

    -- Variance Analysis
    communication_variance SMALLINT GENERATED ALWAYS AS (
        ABS(human_communication_score - (SELECT communication_score FROM osce_scores WHERE score_id = ai_score_id))
    ) STORED,
    total_variance SMALLINT GENERATED ALWAYS AS (
        ABS(human_total_score - (SELECT total_score FROM osce_scores WHERE score_id = ai_score_id))
    ) STORED,
    pass_fail_agreement BOOLEAN GENERATED ALWAYS AS (
        human_pass_fail = (SELECT pass_fail FROM osce_scores WHERE score_id = ai_score_id)
    ) STORED,

    -- Metadata
    human_examiner_name VARCHAR(255),
    notes TEXT,
    validated_at TIMESTAMP DEFAULT NOW(),

    CHECK (total_variance <= 2)  -- Max acceptable variance
);

-- Example: 200 sessions representing 10+ clinical areas
-- - Cardiovascular (chest pain, arrhythmia, heart failure): 40 sessions
-- - Respiratory (dyspnea, chest pain, hemoptysis): 30 sessions
-- - GI (abdominal pain, bleeding): 30 sessions
-- - Neurology (headache, seizure, stroke): 30 sessions
-- - Infectious (fever, sepsis): 20 sessions
-- - Other (endocrine, renal, psychiatric): 50 sessions
```

#### Integration Points

**Critical Error Rules Engine**
```python
# backend/services/critical_error_detector.py

CRITICAL_ERROR_RULES = {
    "rule_001_chest_pain_no_ecg": {
        "description": "Chest pain with red flags but ECG not ordered",
        "conditions": [
            "symptom contains 'chest pain'",
            "symptom contains 'crushing' OR 'pressure' OR 'radiating'",
            "NO action contains 'ECG' OR 'electrocardiogram'",
            "family_history contains 'heart attack' OR 'MI'"
        ],
        "error_text": "Missed critical red flag: Did not order ECG for acute coronary syndrome",
        "severity": "CRITICAL"
    },

    "rule_002_anaphylaxis_no_epinephrine": {
        "description": "Anaphylaxis signs present but epinephrine not given",
        "conditions": [
            "symptoms contain 'itching' OR 'swelling' OR 'breathing difficulty'",
            "vital_signs show 'hypotension' OR 'tachycardia'",
            "NO action contains 'epinephrine' OR 'adrenaline' OR 'epipen'",
            "timeline shows rapid progression"
        ],
        "error_text": "Critical safety issue: Anaphylaxis not managed with immediate epinephrine",
        "severity": "CRITICAL"
    },

    "rule_003_cultural_insensitivity": {
        "description": "Disrespect for cultural background or dismissal of family preferences",
        "conditions": [
            "student dismisses family involvement request",
            "student makes cultural stereotype comments",
            "student ignores expressed cultural preferences"
        ],
        "error_text": "Severe cultural insensitivity: Patient dignity and preferences not respected",
        "severity": "CRITICAL"
    },

    # 17+ more rules covering:
    # - Medication errors (unsafe doses, contraindications)
    # - Missed vital sign abnormalities
    # - Failure to escalate emergencies
    # - Inadequate pain management
    # - Infection control violations
    # - Consent violations
    # - Communication breakdown
    # etc.
}

def detect_critical_errors(transcript, persona, scores):
    """Run all critical error rules against transcript."""
    errors = []

    for rule_id, rule in CRITICAL_ERROR_RULES.items():
        if evaluate_rule_conditions(rule, transcript, persona):
            errors.append({
                "rule_id": rule_id,
                "error_text": rule["error_text"],
                "severity": rule["severity"]
            })

    return errors

# Usage:
critical_errors = detect_critical_errors(transcript, persona, scores)
if critical_errors:
    pass_fail = "FAIL"  # Auto-fail regardless of score
```

**Confidence Scoring Algorithm**
```python
# backend/services/scoring_confidence.py

def calculate_confidence(transcript, ai_scores, critical_errors):
    """
    Calculate confidence in scoring (0.0-1.0).

    Factors:
    - Evidence clarity: How clear is performance from transcript?
    - Score consistency: Do scores match obvious performance?
    - Edge case penalty: Ambiguous situations reduce confidence
    - Critical error clarity: Clear vs. subtle errors
    """

    # 1. Evidence Clarity (0.0-1.0)
    # How clear/obvious is the performance from transcript?
    # - Excellent/Poor performance → 0.95+
    # - Borderline/ambiguous → 0.75-0.85
    evidence_clarity = analyze_transcript_clarity(transcript)

    # 2. Score Consistency (0.0-1.0)
    # Do the 5 domain scores align logically?
    # - Consistent profile → 0.95+
    # - Some misalignment → 0.80-0.90
    score_consistency = check_score_consistency(ai_scores)

    # 3. Edge Case Penalty (0.0-0.3)
    # Reduce confidence for ambiguous scenarios
    # - No edge cases → 0.0
    # - Multiple ambiguities → 0.3
    edge_case_penalty = detect_edge_cases(transcript)

    # 4. Critical Error Clarity (0.0-0.1)
    # If critical error detected, how clear was it?
    # - Very obvious error → 0.0 penalty
    # - Subtle/debatable error → 0.1 penalty
    error_clarity_penalty = 0.0
    if critical_errors:
        error_clarity_penalty = assess_error_clarity(critical_errors)

    # Combined confidence
    confidence = (
        evidence_clarity * 0.5 +
        score_consistency * 0.4 -
        edge_case_penalty * 0.1 -
        error_clarity_penalty * 0.1
    )

    return min(1.0, max(0.0, confidence))

# Examples:
# - Excellent performance (clear transcript) → confidence = 0.97
# - Poor performance (obvious failures) → confidence = 0.96
# - Borderline performance (ambiguous) → confidence = 0.78
# - Mixed performance (some scores don't align) → confidence = 0.80
```

### Technology Stack
- **AI Model**: Claude 3.5 Sonnet (Anthropic)
- **Scoring Logic**: Python 3.11+ with Pydantic (validation)
- **Database**: PostgreSQL 15 (osce_scores, scoring_prompt_versions, golden_dataset_results)
- **Cache**: Redis (session state during scoring process)
- **Backend**: FastAPI + uvicorn
- **Python SDK**: anthropic v0.25+
- **Testing**: pytest, hypothesis (property-based testing)

---

## L - LOOP (Iterative Development)

### Phase 1: AI Examiner Foundation (35% effort, 9-10 hours)
**Goal**: Build AI Examiner scoring with AMC 15-mark rubric

**Tasks**:
1. Design AMC rubric SYSTEM_PROMPT template (1 hour)
2. Implement JSON output validation (Pydantic model) (1 hour)
3. Build AI Examiner service (LLM call + response parsing) (1.5 hours)
4. Implement scoring logic (total calculation, pass/fail rules) (1 hour)
5. Design & build critical error detection rules engine (1.5 hours)
6. Implement scoring confidence calculation (1 hour)
7. Create scoring_prompt_versions table + version management (1 hour)
8. Design feedback generation system (concept + examples) (1 hour)

**Validation Gate**:
- [ ] AI Examiner produces valid JSON (5 scores + feedback)
- [ ] total_score matches sum of 5 domains (constraint validated)
- [ ] pass_fail logic correct (PASS ≥9, FAIL ≤7, BORDERLINE = 8)
- [ ] Critical error detection catches 5+ obvious errors
- [ ] Confidence scores in 0.0-1.0 range (realistic distribution)
- [ ] 10 mock transcripts scored, all reasonable

---

### Phase 2: Critical Error Rules & Validation (30% effort, 8-9 hours)
**Goal**: Complete 20+ critical error rules, golden dataset validation

**Tasks**:
1. Specify 20+ critical error rules (with examples) (1.5 hours)
2. Implement critical error detection logic in rules engine (1.5 hours)
3. Test critical error detection on mock scenarios (1 hour)
4. Create golden dataset structure (5 initial sessions) (1.5 hours)
5. Expand golden dataset (200 sessions total, 10+ clinical areas) (2 hours)
6. Validate AI scoring vs. human (golden dataset comparison) (1 hour)

**Validation Gate**:
- [ ] 20 critical error rules implemented
- [ ] Rules catch 100% of obvious errors
- [ ] False positive rate <5%
- [ ] 5 golden dataset sessions created with expert scores
- [ ] AI vs. human variance ≤2 marks (on 15-mark scale)
- [ ] Pass/fail agreement ≥99%

---

### Phase 3: Feedback Generation & Session Integration (25% effort, 6-7 hours)
**Goal**: Actionable feedback, session end-to-end flow, testing

**Tasks**:
1. Design feedback generation algorithm (strengths + improvements) (1 hour)
2. Implement feedback generation service (1.5 hours)
3. Implement transcript annotation system (evidence references) (1 hour)
4. Build scoring session end-to-end flow (trigger → score → broadcast) (1.5 hours)
5. Write unit tests (AI Examiner, confidence, feedback) (1 hour)
6. Write integration tests (session end-to-end scoring) (1.5 hours)

**Validation Gate**:
- [ ] Feedback is specific, not generic (references transcript)
- [ ] 10 sample transcripts have manually-reviewed feedback
- [ ] Session end-to-end flow: Session end → Score → Broadcast <5 seconds
- [ ] Unit test coverage ≥85%
- [ ] Integration test: Full session with 5+ messages scores correctly

---

### Phase 4: Documentation & Production Validation (10% effort, 2-3 hours)
**Goal**: Documentation, final golden dataset validation, production readiness

**Tasks**:
1. Document AI Examiner rubric (with examples) (1 hour)
2. Document critical error rules (all 20+) (1 hour)
3. Final golden dataset validation (200 sessions, ≥95% accuracy) (30 min)
4. Create production deployment checklist (30 min)

**Validation Gate**:
- [ ] All prompt templates documented
- [ ] Critical error rules documented with examples
- [ ] 200 golden dataset sessions validated (≥95% AI alignment)
- [ ] Production readiness confirmed

---

## P - PLAN (Detailed Implementation)

### Phase 1: AI Examiner Foundation

**Task 1.1**: Design AMC 15-Mark Rubric SYSTEM_PROMPT
- **Effort**: 1 hour
- **Owner**: Backend Engineer (with Medical Advisor review)
- **Deliverable**: SYSTEM_PROMPT template for scoring_prompt_versions v2.1
- **Acceptance Criteria**:
  - [ ] 5 domains defined with 0-15 total range (Communication 0-3, Clinical Reasoning 0-4, etc.)
  - [ ] Scoring criteria clear for each level (0, 1, 2, 3 marks)
  - [ ] Critical error definitions included (20+ rules)
  - [ ] Pass/fail logic explicit (PASS ≥9, FAIL ≤7)
  - [ ] JSON output format specified
  - [ ] Reviewed by medical advisor for AMC alignment

**Task 1.2**: Implement JSON Output Validation (Pydantic)
- **Effort**: 1 hour
- **Owner**: Backend Engineer
- **Deliverable**: `backend/models/scoring_output.py` with ScoreOutput model
- **Acceptance Criteria**:
  - [ ] Pydantic model: communication_score (0-3), clinical_reasoning_score (0-4), etc.
  - [ ] Validates: all fields present, types correct, ranges valid
  - [ ] Calculates total_score = sum of 5 domains
  - [ ] Validates: total_score matches sum (constraint)
  - [ ] Determines pass_fail (PASS/BORDERLINE/FAIL)
  - [ ] Parses critical_errors array
  - [ ] Unit tests: Valid + invalid JSON payloads

**Task 1.3**: Build AI Examiner Service
- **Effort**: 1.5 hours
- **Owner**: Backend Engineer
- **Deliverable**: `backend/services/ai_examiner.py`
- **Acceptance Criteria**:
  - [ ] Service loads transcript + persona + expected approach from PostgreSQL
  - [ ] Constructs SYSTEM_PROMPT (from scoring_prompt_versions active version)
  - [ ] Constructs USER_PROMPT (scenario + transcript + context)
  - [ ] Calls Claude 3.5 Sonnet (temp=0.1 for deterministic scoring)
  - [ ] Parses JSON response, validates with Pydantic
  - [ ] Token counting: accurate (input + output)
  - [ ] Cost calculation: token × $0.003/1K
  - [ ] Error handling: Validation errors + LLM retry logic

**Task 1.4**: Implement Scoring Logic & Pass/Fail Rules
- **Effort**: 1 hour
- **Owner**: Backend Engineer
- **Deliverable**: Scoring logic functions
- **Acceptance Criteria**:
  - [ ] total_score = sum(5 domain scores)
  - [ ] pass_fail = "PASS" if total_score ≥9 AND no critical_errors
  - [ ] pass_fail = "FAIL" if total_score ≤7 OR critical_errors present
  - [ ] pass_fail = "BORDERLINE" if total_score = 8
  - [ ] Logic tested on 15 mock scores

**Task 1.5**: Design & Build Critical Error Detection Rules Engine
- **Effort**: 1.5 hours
- **Owner**: Backend Engineer
- **Deliverable**: `backend/services/critical_error_detector.py`
- **Acceptance Criteria**:
  - [ ] 20 critical error rules specified (with conditions + error text)
  - [ ] Rules engine evaluates rules against transcript + persona
  - [ ] Returns error_list[] and auto_fail boolean
  - [ ] Examples: Chest pain no ECG, Anaphylaxis no epi, Cultural insensitivity
  - [ ] Tested on 10 mock transcripts (catches obvious errors)

**Task 1.6**: Implement Scoring Confidence Calculation
- **Effort**: 1 hour
- **Owner**: Backend Engineer
- **Deliverable**: `backend/services/confidence_scorer.py`
- **Acceptance Criteria**:
  - [ ] Confidence formula: evidence_clarity * 0.5 + score_consistency * 0.4 - edge_cases * 0.1
  - [ ] Returns 0.0-1.0 confidence score
  - [ ] High confidence (0.95+): Clear performance
  - [ ] Low confidence (0.70-0.85): Ambiguous/borderline cases
  - [ ] Tested on 10 mock transcripts (realistic distribution)

**Task 1.7**: Create scoring_prompt_versions Table & Version Management
- **Effort**: 1 hour
- **Owner**: Backend Engineer
- **Deliverable**: Alembic migration + version control logic
- **Acceptance Criteria**:
  - [ ] scoring_prompt_versions table created (version, template, active, accuracy)
  - [ ] v1.0 loaded (baseline prompt)
  - [ ] v2.0 loaded (improved critical error detection)
  - [ ] v2.1 loaded (current version, 98.5% accuracy)
  - [ ] Query: Get active version for AI Examiner
  - [ ] Only ONE version active at a time (constraint)

**Task 1.8**: Design Feedback Generation System (Concept)
- **Effort**: 1 hour
- **Owner**: Backend Engineer
- **Deliverable**: Feedback generation algorithm specification
- **Acceptance Criteria**:
  - [ ] Algorithm design: Extract strengths (3-5 from transcript)
  - [ ] Algorithm design: Identify improvements (2-4 gaps)
  - [ ] Algorithm design: Generate narrative (constructive tone)
  - [ ] Algorithm design: Annotate transcript (evidence references)
  - [ ] Examples: 5 sample transcripts with proposed feedback

---

### Phase 2: Critical Error Rules & Validation

**Task 2.1**: Specify 20+ Critical Error Rules
- **Effort**: 1.5 hours
- **Owner**: Backend Engineer (with Medical Advisor)
- **Deliverable**: `backend/config/critical_error_rules.yaml`
- **Acceptance Criteria**:
  - [ ] Rule 1: Chest pain + red flags → No ECG
  - [ ] Rule 2: Anaphylaxis signs → No epinephrine
  - [ ] Rule 3: Severe cultural insensitivity
  - [ ] Rules 4-20: Domain-specific violations (medication, vital signs, escalation, etc.)
  - [ ] Each rule has: conditions, error_text, severity level
  - [ ] Medical advisor approval for clinical accuracy

**Task 2.2**: Implement Critical Error Detection Logic
- **Effort**: 1.5 hours
- **Owner**: Backend Engineer
- **Deliverable**: Rules engine implementation in `critical_error_detector.py`
- **Acceptance Criteria**:
  - [ ] Rules engine evaluates all 20+ rules
  - [ ] Returns errors[] and auto_fail flag
  - [ ] Handles transcript analysis (student actions, patient info)
  - [ ] Tested on 10 mock transcripts
  - [ ] False positive rate <5%

**Task 2.3**: Test Critical Error Detection on Mock Scenarios
- **Effort**: 1 hour
- **Owner**: Backend Engineer / Testing QA
- **Deliverable**: Test cases for critical error detection
- **Acceptance Criteria**:
  - [ ] 10 mock transcripts created (5 with obvious errors, 5 clean)
  - [ ] Critical error detector catches all 5 error transcripts
  - [ ] No false positives on clean transcripts
  - [ ] Error messages are clear and specific

**Task 2.4**: Create Golden Dataset Structure (Initial 5 Sessions)
- **Effort**: 1.5 hours
- **Owner**: Backend Engineer (with Medical Advisor)
- **Deliverable**: 5 golden dataset sessions with expert human scores
- **Acceptance Criteria**:
  - [ ] Session 1: Excellent (14-15/15, PASS)
  - [ ] Session 2: Good (11-12/15, PASS)
  - [ ] Session 3: Borderline (8/15, BORDERLINE)
  - [ ] Session 4: Poor (5-7/15, FAIL)
  - [ ] Session 5: Critical error (7/15, FAIL)
  - Each includes: Full transcript, expert scores, expert feedback

**Task 2.5**: Expand Golden Dataset (200 Sessions Total)
- **Effort**: 2 hours
- **Owner**: Backend Engineer (with Medical Advisor)
- **Deliverable**: 200 golden dataset sessions covering 10+ clinical areas
- **Acceptance Criteria**:
  - [ ] Cardiovascular (chest pain, arrhythmia): 40 sessions
  - [ ] Respiratory (dyspnea, hemoptysis): 30 sessions
  - [ ] GI (abdominal pain, bleeding): 30 sessions
  - [ ] Neurology (headache, stroke): 30 sessions
  - [ ] Infectious (fever, sepsis): 20 sessions
  - [ ] Other (endocrine, renal): 50 sessions
  - [ ] Each session: Full transcript, expert scores, feedback

**Task 2.6**: Validate AI Scoring vs. Human (Golden Dataset Comparison)
- **Effort**: 1 hour
- **Owner**: Backend Engineer
- **Deliverable**: Accuracy report + alignment metrics
- **Acceptance Criteria**:
  - [ ] Run 200 golden dataset sessions through AI Examiner
  - [ ] Calculate variance per session (AI score vs. human score)
  - [ ] Calculate pass_fail agreement rate
  - [ ] Report: "AI Examiner ≥95% aligned with expert scoring"
  - [ ] Variance: Mean ≤0.8 marks, Max ≤2 marks
  - [ ] Pass/fail agreement ≥99%

---

### Phase 3: Feedback Generation & Session Integration

**Task 3.1**: Implement Feedback Generation Service
- **Effort**: 1.5 hours
- **Owner**: Backend Engineer
- **Deliverable**: `backend/services/feedback_generator.py`
- **Acceptance Criteria**:
  - [ ] Extract strengths (3-5 from transcript)
  - [ ] Identify improvements (2-4 gaps)
  - [ ] Generate overall narrative (2-3 sentences, constructive)
  - [ ] Feedback references transcript evidence (not generic)
  - [ ] Tested on 10 mock transcripts

**Task 3.2**: Implement Transcript Annotation System
- **Effort**: 1 hour
- **Owner**: Backend Engineer
- **Deliverable**: `backend/services/transcript_annotator.py`
- **Acceptance Criteria**:
  - [ ] Annotate transcript with evidence snippets
  - [ ] Mark good communication examples
  - [ ] Mark clinical reasoning moments
  - [ ] Mark information gathering points
  - [ ] Mark management decisions
  - [ ] Generate annotated transcript for frontend

**Task 3.3**: Build Session End-to-End Scoring Flow
- **Effort**: 1.5 hours
- **Owner**: Backend Engineer
- **Deliverable**: Complete flow: Session end → Score → Broadcast
- **Acceptance Criteria**:
  - [ ] Trigger: WebSocket timer expires at 8:00
  - [ ] Fetch: conversation_history, emotional_state_transitions from PostgreSQL
  - [ ] Call: AI Examiner service
  - [ ] Process: Validate JSON, detect critical errors, calculate confidence
  - [ ] Save: osce_scores with all fields
  - [ ] Update: user_progress via trigger
  - [ ] Broadcast: Results via WebSocket to student
  - [ ] Total time: <5 seconds (p95)

**Task 3.4**: Write Unit Tests (AI Examiner, Confidence, Feedback)
- **Effort**: 1 hour
- **Owner**: Backend Engineer / Testing QA
- **Deliverable**: `backend/tests/test_services/test_ai_examiner.py`
- **Test Cases**:
  - [ ] test_json_output_validation (valid + invalid)
  - [ ] test_score_calculation (total_score = sum)
  - [ ] test_pass_fail_logic (PASS ≥9, FAIL ≤7)
  - [ ] test_critical_error_detection
  - [ ] test_confidence_calculation (0.0-1.0 range)
  - [ ] test_feedback_generation (specific, not generic)
  - [ ] Coverage ≥85%

**Task 3.5**: Write Integration Tests (End-to-End Session Scoring)
- **Effort**: 1.5 hours
- **Owner**: Backend Engineer / Testing QA
- **Deliverable**: `backend/tests/test_integration/test_scoring_session.py`
- **Test Cases**:
  - [ ] Full session: 8 minutes of conversation → Scoring triggered
  - [ ] AI Examiner called with correct context
  - [ ] JSON validated, critical errors detected
  - [ ] Score saved to PostgreSQL (osce_scores)
  - [ ] user_progress updated (attempt count, pass count, avg score)
  - [ ] WebSocket broadcasts results to student
  - [ ] Session state = 'complete'
  - [ ] Coverage ≥85%

---

### Phase 4: Documentation & Production Validation

**Task 4.1**: Document AI Examiner Rubric
- **Effort**: 1 hour
- **Owner**: Backend Engineer
- **Deliverable**: `backend/docs/AI_EXAMINER_RUBRIC.md`
- **Contents**:
  - Overview of AI Examiner system
  - AMC 15-mark rubric breakdown (5 domains, scoring criteria)
  - Critical error definitions (all 20+, with examples)
  - Pass/fail logic (PASS ≥9, FAIL ≤7, BORDERLINE = 8)
  - Feedback generation guidelines
  - Prompt version history (v1.0, v2.0, v2.1 with accuracy metrics)
  - Golden dataset summary (200 sessions, 10+ clinical areas)

**Task 4.2**: Document Critical Error Rules
- **Effort**: 1 hour
- **Owner**: Backend Engineer
- **Deliverable**: `backend/docs/CRITICAL_ERROR_RULES.md`
- **Contents**:
  - All 20+ critical error rules listed
  - Each rule: Conditions, error text, clinical rationale
  - Examples: Transcript snippets showing detection
  - False positive cases (rules NOT triggered)
  - Integration with AI Examiner scoring

**Task 4.3**: Final Golden Dataset Validation (200 Sessions)
- **Effort**: 30 min
- **Owner**: Backend Engineer
- **Deliverable**: Final accuracy report
- **Acceptance Criteria**:
  - [ ] 200 golden dataset sessions scored by AI Examiner
  - [ ] Compare AI scores vs. expert human scores
  - [ ] Calculate variance (should be <2 marks average)
  - [ ] Calculate pass_fail agreement (should be ≥99%)
  - [ ] Report: "AI Examiner ≥95% aligned with expert scoring"

**Task 4.4**: Create Production Deployment Checklist
- **Effort**: 30 min
- **Owner**: Backend Engineer
- **Deliverable**: Deployment checklist + validation script
- **Acceptance Criteria**:
  - [ ] scoring_prompt_versions v2.1 active
  - [ ] osce_scores table created with constraints
  - [ ] golden_dataset_results table created
  - [ ] Critical error rules engine tested
  - [ ] Confidence calculation validated
  - [ ] WebSocket scoring flow tested
  - [ ] Performance targets met (<5 seconds)
  - [ ] Database indexes created

---

## H - HANDOFF (Delivery & Validation)

### Acceptance Criteria (MUST ALL PASS)

#### Functional Requirements
- [ ] AI Examiner produces valid JSON with 5 scores (0-15 total)
- [ ] AMC 15-Mark Rubric: All 5 domains (Communication 0-3, Clinical Reasoning 0-4, etc.)
- [ ] Scoring logic: total_score = sum of 5 domains (validated)
- [ ] Pass/fail rules: PASS ≥9 AND no critical errors, FAIL ≤7 OR critical error
- [ ] Critical error detection: 20+ rules implemented, catches obvious errors
- [ ] Critical error detection: <5% false positive rate
- [ ] Scoring confidence: 0.0-1.0 range, realistic distribution
- [ ] Feedback generation: Specific, actionable, references transcript evidence
- [ ] Session end-to-end flow: Session end → Score → Broadcast <5 seconds
- [ ] Scoring prompt versioning: Database-stored (v1.0, v2.0, v2.1)
- [ ] Cost tracking: Accurate token counting, LLM cost calculated

#### Quality Requirements
- [ ] **Test Coverage**: ≥85% (unit + integration)
- [ ] **Test Pass Rate**: 100% (zero tolerance for flaky tests)
- [ ] **Code Quality**: No linting errors, follows FastAPI best practices
- [ ] **Documentation**: Rubric, critical error rules, golden dataset documented

#### Performance Requirements
- [ ] **Scoring Response**: <5 seconds (p95) from session end to broadcast
- [ ] **AI Examiner call**: <3 seconds (p95) for LLM response
- [ ] **JSON validation**: <100ms
- [ ] **Critical error detection**: <500ms (all 20+ rules)
- [ ] **Database inserts**: <200ms (score + progress update)

#### Validation Requirements (Golden Dataset)
- [ ] **200 scenarios** representing 10+ clinical areas
- [ ] **AI vs. human variance**: ≤2 marks average (on 15-mark scale)
- [ ] **Pass/fail agreement**: ≥99%
- [ ] **Accuracy report**: "AI Examiner ≥95% aligned with expert scoring"

#### AMC Medical Compliance
- [ ] **15-Mark Rubric**: Exactly matches AMC Clinical Examination standards
- [ ] **Rubric accuracy**: Expert review confirms alignment
- [ ] **Critical actions**: Match clinical guidelines (e.g., ECG <10min for STEMI)
- [ ] **Differential diagnosis**: Expected DDx matches evidence
- [ ] **Red flag detection**: Catches hallmark findings

#### Security & Compliance
- [ ] **No hardcoded LLM keys**: API key from environment variable
- [ ] **Input validation**: Transcripts validated before scoring
- [ ] **Audit trail**: Every score logged (model, prompt version, timestamp)
- [ ] **Data encryption**: Scores encrypted at rest (if required)

---

### Testing Requirements

#### Unit Tests (≥85% coverage target)
```python
# backend/tests/test_services/test_ai_examiner.py

def test_json_output_validation():
    """Valid score output passes validation."""

def test_json_invalid_ranges():
    """Invalid score ranges rejected."""

def test_total_score_calculation():
    """total_score = sum of 5 domains."""

def test_pass_fail_logic():
    """PASS ≥9, FAIL ≤7, BORDERLINE = 8."""

def test_critical_error_detection():
    """Critical errors caught and flagged."""

def test_confidence_calculation():
    """Confidence in 0.0-1.0 range."""

def test_feedback_generation():
    """Feedback is specific, not generic."""
```

#### Integration Tests (End-to-End)
```python
# backend/tests/test_integration/test_scoring_session.py

def test_full_scoring_session_flow():
    """Complete session end-to-end with scoring."""
    # 1. Create session
    # 2. Simulate 8-minute conversation
    # 3. Session end triggered
    # 4. AI Examiner called
    # 5. Score saved to PostgreSQL
    # 6. user_progress updated
    # 7. Results broadcast via WebSocket
    # 8. Assertions: All data correct
```

#### Golden Dataset Validation
```
AI Examiner Accuracy on 200 Golden Dataset Sessions:

Variance Analysis:
  Communication score variance: mean 0.3, max 1
  Clinical reasoning variance: mean 0.5, max 2
  Information gathering variance: mean 0.4, max 1
  Management variance: mean 0.2, max 1
  Professionalism variance: mean 0.1, max 1
  Total score variance: mean 0.8, max 2

Pass/Fail Agreement:
  AI PASS, Human PASS: 120 sessions (98%)
  AI FAIL, Human FAIL: 75 sessions (100%)
  AI BORDERLINE: 5 sessions (100% agreement)
  Discrepancies: 0 sessions (0%)

OVERALL ACCURACY: ≥95% (Requirement met)
```

---

### Documentation Deliverables

1. **AI Examiner Rubric** (`backend/docs/AI_EXAMINER_RUBRIC.md`)
   - 5-domain rubric breakdown
   - Scoring criteria per domain
   - Critical error definitions
   - Pass/fail logic

2. **Critical Error Rules** (`backend/docs/CRITICAL_ERROR_RULES.md`)
   - All 20+ rules listed
   - Conditions + error text
   - Clinical rationale

3. **Integration Guide** (`backend/docs/SCORING_INTEGRATION.md`)
   - Architecture overview
   - Scoring flow diagram
   - API endpoints + WebSocket messages

4. **Golden Dataset Report** (`backend/docs/GOLDEN_DATASET_VALIDATION.md`)
   - 200 scenarios summary
   - Clinical area breakdown
   - Accuracy metrics
   - AI vs. human comparison

---

## 📊 Project Statistics

**Total File Size**: 45-50 KB
**Estimated Lines of Code**: 2000+ (including documentation)
**Total Effort**: 24-28 hours
**Team Composition**:
- 1x Backend Engineer (primary implementation)
- 1x Medical Advisor (rubric validation, clinical accuracy)
- 1x Testing QA (unit + integration tests)
- 1x PM Coordinator (oversight, deliverables)

**Success Criteria**:
- ✅ All 12 tasks complete and validated
- ✅ ≥85% test coverage, 100% pass rate
- ✅ AI scoring ≥95% accurate vs. human (golden dataset)
- ✅ Scoring response <5 seconds (p95)
- ✅ All documentation complete

---

**Document Status**: Ready for Implementation
**Created**: 2026-02-16
**Version**: 1.0
**File Size**: ~48 KB (final)
