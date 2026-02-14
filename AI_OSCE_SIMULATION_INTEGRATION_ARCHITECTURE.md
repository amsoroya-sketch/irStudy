# AI OSCE Simulation - Integration Architecture

**Last Updated:** 2026-02-09
**Status:** Design Phase
**Owner:** PM Coordinator

## Executive Summary

This document defines how the AI Patient/Examiner simulation system integrates with the existing AMC Clinical Exam platform infrastructure. Based on confirmed user requirements, this architecture creates a **separate, dedicated subsystem** for AI-powered OSCE practice while maintaining connections to core authentication, progress tracking, and content systems.

## 1. Architecture Principles

### 1.1 Separation of Concerns
- **NEW subsystem**: AI Patient personas, OSCE attempts, and scores are stored in dedicated tables
- **NOT reusing**: Existing OSCE content structure (140+ scenarios remain for reference/study)
- **Integration points**: User authentication, progress tracking, specialty taxonomy

### 1.2 Dual Storage Strategy
- **Redis**: Active session state (8-minute conversations, emotional states, RAG context)
- **PostgreSQL**: Permanent archive (full transcripts, scores, performance analytics)
- **Sync mechanism**: Background job every 30 seconds during session

### 1.3 Exam Mode Support
- **Individual Practice**: Student selects any persona, 8-minute session, immediate feedback
- **Mock Exam Mode**: 16 sequential stations, 2.5 hours total, comprehensive scoring

---

## 2. Database Schema Design

### 2.1 New Tables Overview

```
patient_personas (360 rows target)
    ↓ FK
osce_attempts (user sessions)
    ↓ FK
osce_scores (AMC 15-mark rubric)
    ↓ Integration
user_progress (existing table - updated)
```

### 2.2 patient_personas Table

**Purpose**: Rich AI patient profiles with emotional intelligence and progressive disclosure

```sql
CREATE TABLE patient_personas (
    -- Identity
    persona_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    persona_code VARCHAR(20) UNIQUE NOT NULL,  -- e.g., "CARD-001-CHEST-PAIN"

    -- Patient Demographics
    name VARCHAR(100) NOT NULL,
    age INT NOT NULL CHECK (age BETWEEN 18 AND 95),
    gender VARCHAR(20) NOT NULL,
    occupation VARCHAR(100),
    cultural_background VARCHAR(100),  -- e.g., "Vietnamese Australian"
    preferred_language VARCHAR(50) DEFAULT 'English',

    -- Clinical Presentation
    specialty VARCHAR(50) NOT NULL,  -- cardiology, respiratory, etc.
    chief_complaint TEXT NOT NULL,
    opening_statement TEXT NOT NULL,  -- What patient says first

    -- Progressive Disclosure Structure
    symptoms JSONB NOT NULL,
    /*
    {
      "immediate": ["chest pain for 2 hours", "pain radiates to left arm"],
      "when_asked_onset": "Started after climbing stairs at work",
      "when_asked_severity": "8 out of 10, feels like crushing pressure",
      "when_asked_relieving_factors": "Resting helps a bit, but pain persists",
      "when_asked_previous_episodes": "Had similar pain 6 months ago, dismissed it"
    }
    */

    medical_history JSONB NOT NULL,
    /*
    {
      "volunteer": ["Type 2 diabetes", "high cholesterol"],
      "when_asked_medications": ["Metformin 1000mg BD", "Atorvastatin 40mg nocte"],
      "when_asked_family_history": "Father died of heart attack age 55",
      "when_asked_social": "Smokes 10 cigarettes/day for 20 years",
      "red_flags": ["crushing chest pain", "family history MI"]
    }
    */

    -- Emotional Intelligence
    emotional_profile JSONB NOT NULL,
    /*
    {
      "baseline_state": "ANXIOUS_GUARDED",
      "pain_level": 8,
      "anxiety_level": 7,
      "trust_threshold": 3,  -- How many empathy points to advance state
      "triggers": {
        "empathy_phrases": ["I understand", "That must be frightening"],
        "dismissive_phrases": ["It's probably nothing", "rushed body language"],
        "cultural_sensitivity_tests": ["Do you want family present?"]
      },
      "state_transitions": {
        "ANXIOUS_GUARDED → CAUTIOUSLY_OPEN": "Student shows empathy, asks open questions",
        "CAUTIOUSLY_OPEN → TRUSTING": "Student addresses pain, explains clearly",
        "TRUSTING → WITHDRAWN": "Student interrupts, dismisses concerns"
      }
    }
    */

    -- RAG Integration
    rag_query_hints TEXT[],  -- Search terms for RAG: ["acute coronary syndrome", "STEMI management"]
    key_differentials TEXT[],  -- Expected DDx: ["STEMI", "unstable angina", "pulmonary embolism"]
    critical_actions TEXT[],  -- Must-do: ["ECG within 10 minutes", "aspirin 300mg", "call cardiology"]

    -- Difficulty Metadata
    difficulty_level VARCHAR(20) NOT NULL CHECK (difficulty_level IN ('foundation', 'intermediate', 'advanced')),
    estimated_pass_rate DECIMAL(3,1),  -- Historical: 67.5% pass rate

    -- AMC Alignment
    amc_blueprint_area VARCHAR(100),  -- "Cardiovascular - Acute Coronary Syndromes"
    amc_competencies TEXT[],  -- ["Clinical reasoning", "Emergency management"]

    -- Audit Fields
    created_by UUID REFERENCES users(user_id),
    created_at TIMESTAMP DEFAULT NOW(),
    validated_by UUID REFERENCES users(user_id),  -- Expert clinician approval
    validated_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    version INT DEFAULT 1
);

CREATE INDEX idx_personas_specialty ON patient_personas(specialty);
CREATE INDEX idx_personas_difficulty ON patient_personas(difficulty_level);
CREATE INDEX idx_personas_active ON patient_personas(is_active) WHERE is_active = TRUE;
```

### 2.3 osce_attempts Table

**Purpose**: Tracks each student's OSCE practice session (individual or mock exam)

```sql
CREATE TABLE osce_attempts (
    -- Identity
    attempt_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Relationships
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    persona_id UUID NOT NULL REFERENCES patient_personas(persona_id),
    mock_exam_id UUID REFERENCES mock_exams(exam_id),  -- NULL for individual practice

    -- Session Metadata
    session_type VARCHAR(20) NOT NULL CHECK (session_type IN ('individual', 'mock_exam')),
    station_number INT,  -- 1-16 for mock exams, NULL for individual

    -- Timing
    started_at TIMESTAMP NOT NULL DEFAULT NOW(),
    ended_at TIMESTAMP,
    duration_seconds INT,  -- Auto-calculated: ended_at - started_at
    warning_1min_shown BOOLEAN DEFAULT FALSE,
    timer_expired BOOLEAN DEFAULT FALSE,

    -- Conversation Archive
    conversation_history JSONB NOT NULL DEFAULT '[]'::jsonb,
    /*
    [
      {
        "timestamp": "2026-02-09T10:05:23Z",
        "speaker": "patient",
        "message": "I've been having this terrible chest pain for the past 2 hours",
        "emotional_state": "ANXIOUS_GUARDED",
        "pain_level": 8,
        "tokens_used": 45
      },
      {
        "timestamp": "2026-02-09T10:05:45Z",
        "speaker": "student",
        "message": "I understand that must be very concerning. Can you tell me more about when it started?",
        "empathy_detected": true,
        "tokens_used": 32
      },
      ...
    ]
    */

    -- Emotional State Tracking
    emotional_state_transitions JSONB DEFAULT '[]'::jsonb,
    /*
    [
      {"timestamp": "2026-02-09T10:05:23Z", "state": "ANXIOUS_GUARDED"},
      {"timestamp": "2026-02-09T10:06:12Z", "state": "CAUTIOUSLY_OPEN", "trigger": "empathy_shown"},
      {"timestamp": "2026-02-09T10:07:45Z", "state": "TRUSTING", "trigger": "clear_explanation"}
    ]
    */

    -- Student Actions Logged
    student_actions JSONB DEFAULT '[]'::jsonb,
    /*
    [
      {"timestamp": "2026-02-09T10:06:30Z", "action": "asked_pain_location", "category": "information_gathering"},
      {"timestamp": "2026-02-09T10:07:10Z", "action": "showed_empathy", "category": "communication"},
      {"timestamp": "2026-02-09T10:07:50Z", "action": "ordered_ecg", "category": "management"}
    ]
    */

    -- RAG Usage
    rag_queries_executed JSONB DEFAULT '[]'::jsonb,
    /*
    [
      {
        "timestamp": "2026-02-09T10:05:23Z",
        "query": "acute coronary syndrome management",
        "chunks_retrieved": 5,
        "sources": ["AMC Clinical Examination p.234", "eTG Cardiovascular"]
      }
    ]
    */

    -- Performance Metrics
    total_messages INT DEFAULT 0,
    total_tokens_used INT DEFAULT 0,
    llm_cost_usd DECIMAL(6,4) DEFAULT 0.0000,

    -- Session Status
    session_state VARCHAR(20) DEFAULT 'initialized' CHECK (
        session_state IN ('initialized', 'intro', 'conversation', 'warning_1min', 'finalized', 'scoring', 'complete')
    ),

    -- Audit
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_attempts_user ON osce_attempts(user_id);
CREATE INDEX idx_attempts_persona ON osce_attempts(persona_id);
CREATE INDEX idx_attempts_started ON osce_attempts(started_at DESC);
CREATE INDEX idx_attempts_mock_exam ON osce_attempts(mock_exam_id) WHERE mock_exam_id IS NOT NULL;
```

### 2.4 osce_scores Table

**Purpose**: AMC 15-mark rubric scoring by AI Examiner

```sql
CREATE TABLE osce_scores (
    -- Identity
    score_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    attempt_id UUID NOT NULL REFERENCES osce_attempts(attempt_id) ON DELETE CASCADE,

    -- AMC 15-Mark Rubric Breakdown
    communication_score INT NOT NULL CHECK (communication_score BETWEEN 0 AND 3),
    communication_feedback TEXT,
    /*
    Grading Criteria:
    0 = Poor: Minimal eye contact, interrupts patient, no rapport
    1 = Below standard: Limited empathy, some interruptions
    2 = Satisfactory: Good rapport, mostly patient-centered
    3 = Excellent: Outstanding empathy, active listening, culturally sensitive
    */

    clinical_reasoning_score INT NOT NULL CHECK (clinical_reasoning_score BETWEEN 0 AND 4),
    clinical_reasoning_feedback TEXT,
    /*
    0 = No differential diagnosis formed
    1 = Incomplete/incorrect DDx
    2 = Reasonable DDx, some gaps
    3 = Comprehensive DDx, logical reasoning
    4 = Excellent DDx with clear prioritization
    */

    information_gathering_score INT NOT NULL CHECK (information_gathering_score BETWEEN 0 AND 4),
    information_gathering_feedback TEXT,
    /*
    0 = Missed critical information
    1 = Incomplete history
    2 = Adequate history, minor gaps
    3 = Thorough history, systematic approach
    4 = Excellent systematic approach, no gaps
    */

    management_score INT NOT NULL CHECK (management_score BETWEEN 0 AND 2),
    management_feedback TEXT,
    /*
    0 = Unsafe/inappropriate management
    1 = Partially appropriate
    2 = Safe, appropriate, evidence-based
    */

    professionalism_score INT NOT NULL CHECK (professionalism_score BETWEEN 0 AND 2),
    professionalism_feedback TEXT,
    /*
    0 = Unprofessional behavior
    1 = Mostly professional
    2 = Exemplary professionalism
    */

    -- Overall Scoring
    total_score INT NOT NULL CHECK (total_score BETWEEN 0 AND 15),
    pass_fail VARCHAR(10) NOT NULL CHECK (pass_fail IN ('PASS', 'FAIL', 'BORDERLINE')),
    /*
    PASS: ≥9/15 (60%) AND no critical errors
    BORDERLINE: 8/15
    FAIL: ≤7/15 OR critical error detected
    */

    -- Critical Errors (Auto-Fail)
    critical_errors JSONB DEFAULT '[]'::jsonb,
    /*
    [
      {
        "timestamp": "2026-02-09T10:06:30Z",
        "error_type": "missed_red_flag",
        "description": "Did not order ECG for chest pain patient",
        "severity": "critical"
      }
    ]
    */

    -- Detailed Feedback
    strengths TEXT[],  -- ["Excellent empathy shown", "Systematic history taking"]
    areas_for_improvement TEXT[],  -- ["Consider red flags earlier", "Order investigations sooner"]

    overall_feedback TEXT,  -- Narrative summary

    -- AI Examiner Metadata
    scored_by VARCHAR(50) DEFAULT 'ai_examiner',  -- Future: Support human examiner override
    scoring_model VARCHAR(50),  -- "claude-3.5-sonnet-20250219"
    scoring_prompt_version VARCHAR(20),  -- "v2.1"
    scoring_confidence DECIMAL(3,2),  -- 0.00-1.00: AI's confidence in scoring

    -- Golden Dataset Validation
    is_golden_dataset BOOLEAN DEFAULT FALSE,
    expert_human_score INT,  -- For validation: compare AI vs human
    score_variance INT,  -- ABS(ai_score - human_score)

    -- Audit
    scored_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_scores_attempt ON osce_scores(attempt_id);
CREATE INDEX idx_scores_pass_fail ON osce_scores(pass_fail);
CREATE INDEX idx_scores_total ON osce_scores(total_score DESC);
CREATE INDEX idx_scores_golden ON osce_scores(is_golden_dataset) WHERE is_golden_dataset = TRUE;
```

### 2.5 mock_exams Table

**Purpose**: Orchestrate 16-station full mock exams

```sql
CREATE TABLE mock_exams (
    exam_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id),

    -- Exam Configuration
    exam_date DATE NOT NULL DEFAULT CURRENT_DATE,
    stations_config JSONB NOT NULL,
    /*
    [
      {"station": 1, "persona_id": "uuid-1", "specialty": "cardiology"},
      {"station": 2, "persona_id": "uuid-2", "specialty": "respiratory"},
      ...
      {"station": 16, "persona_id": "uuid-16", "specialty": "psychiatry"}
    ]
    */

    -- Progress Tracking
    current_station INT DEFAULT 1 CHECK (current_station BETWEEN 1 AND 16),
    exam_state VARCHAR(20) DEFAULT 'scheduled' CHECK (
        exam_state IN ('scheduled', 'in_progress', 'paused', 'completed', 'abandoned')
    ),

    -- Timing
    scheduled_start TIMESTAMP NOT NULL,
    actual_start TIMESTAMP,
    actual_end TIMESTAMP,
    total_duration_minutes INT,  -- Should be ~150 minutes (16 stations × 8 min + breaks)

    -- Overall Performance
    total_score INT,  -- Sum of all 16 station scores
    overall_pass_fail VARCHAR(10) CHECK (overall_pass_fail IN ('PASS', 'FAIL', 'INCOMPLETE')),

    -- Audit
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_mock_exams_user ON mock_exams(user_id);
CREATE INDEX idx_mock_exams_date ON mock_exams(exam_date DESC);
CREATE INDEX idx_mock_exams_state ON mock_exams(exam_state);
```

### 2.6 Integration with Existing user_progress Table

**Update**: Add AI OSCE tracking to existing progress system

```sql
-- Add new columns to existing user_progress table
ALTER TABLE user_progress
    ADD COLUMN ai_osces_attempted INT DEFAULT 0,
    ADD COLUMN ai_osces_passed INT DEFAULT 0,
    ADD COLUMN ai_osce_avg_score DECIMAL(4,2),  -- Average total_score across all attempts
    ADD COLUMN mock_exams_completed INT DEFAULT 0,
    ADD COLUMN last_ai_osce_at TIMESTAMP;

-- Update trigger to increment counters
CREATE OR REPLACE FUNCTION update_ai_osce_progress()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE user_progress
    SET
        ai_osces_attempted = ai_osces_attempted + 1,
        ai_osces_passed = CASE
            WHEN (SELECT pass_fail FROM osce_scores WHERE attempt_id = NEW.attempt_id) = 'PASS'
            THEN ai_osces_passed + 1
            ELSE ai_osces_passed
        END,
        last_ai_osce_at = NEW.ended_at,
        ai_osce_avg_score = (
            SELECT AVG(s.total_score)
            FROM osce_attempts a
            JOIN osce_scores s ON a.attempt_id = s.attempt_id
            WHERE a.user_id = NEW.user_id
        )
    WHERE user_id = NEW.user_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_ai_osce_progress
AFTER UPDATE OF ended_at ON osce_attempts
FOR EACH ROW
WHEN (NEW.ended_at IS NOT NULL AND OLD.ended_at IS NULL)
EXECUTE FUNCTION update_ai_osce_progress();
```

---

## 3. Data Flow Architecture

### 3.1 Individual Practice Mode - Complete Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│ PHASE 1: PERSONA SELECTION                                          │
└─────────────────────────────────────────────────────────────────────┘

Student (Frontend)
    ↓
    GET /api/v1/patient-personas?specialty=cardiology&difficulty=intermediate
    ↓
Backend (FastAPI)
    ↓
    Query: SELECT * FROM patient_personas
           WHERE specialty = 'cardiology'
           AND difficulty_level = 'intermediate'
           AND is_active = TRUE
    ↓
    Return: [
      {
        "persona_id": "uuid-123",
        "persona_code": "CARD-001-CHEST-PAIN",
        "name": "Robert Chen",
        "chief_complaint": "Chest pain for 2 hours",
        "difficulty_level": "intermediate",
        "estimated_pass_rate": 67.5
      },
      ...
    ]
    ↓
Student: Clicks "Start OSCE" on persona

┌─────────────────────────────────────────────────────────────────────┐
│ PHASE 2: SESSION INITIALIZATION                                     │
└─────────────────────────────────────────────────────────────────────┘

POST /api/v1/osce-sessions
Body: {
  "persona_id": "uuid-123",
  "session_type": "individual"
}
    ↓
Backend: Create osce_attempt record
    INSERT INTO osce_attempts (user_id, persona_id, session_type, started_at)
    VALUES ('user-uuid', 'uuid-123', 'individual', NOW())
    RETURNING attempt_id
    ↓
Backend: Load persona into Redis
    REDIS SET osce:session:{attempt_id}:persona {
      "persona_id": "uuid-123",
      "name": "Robert Chen",
      "symptoms": {...},
      "emotional_profile": {...},
      "rag_query_hints": [...]
    }
    REDIS EXPIRE osce:session:{attempt_id}:persona 1800  # 30 minutes
    ↓
Backend: Initialize conversation state
    REDIS SET osce:session:{attempt_id}:state {
      "session_state": "initialized",
      "emotional_state": "ANXIOUS_GUARDED",
      "pain_level": 8,
      "anxiety_level": 7,
      "empathy_points": 0,
      "message_count": 0,
      "tokens_used": 0
    }
    ↓
Backend: Return WebSocket connection details
    Response: {
      "attempt_id": "attempt-uuid-456",
      "websocket_url": "wss://api.example.com/ws/osce/{attempt_id}",
      "session_token": "jwt-token",
      "expires_in": 1800
    }

┌─────────────────────────────────────────────────────────────────────┐
│ PHASE 3: WEBSOCKET CONNECTION                                       │
└─────────────────────────────────────────────────────────────────────┘

Student: Connect to WebSocket
    wss://api.example.com/ws/osce/{attempt_id}?token={jwt-token}
    ↓
Backend: Authenticate WebSocket connection
    - Verify JWT token (WebSocketAuthenticator)
    - Check rate limits (ConnectionTracker: max 3 concurrent)
    - Authorize user_id matches attempt owner
    ↓
Backend: Send opening statement from AI Patient
    Load from Redis: osce:session:{attempt_id}:persona
    ↓
AI Patient (Claude 3.5 Sonnet)
    SYSTEM_PROMPT: "You are Robert Chen, a 52-year-old accountant..."
    USER_PROMPT: "Give your opening statement"
    ↓
    Response: "Doctor, I've been having this terrible chest pain for the past 2 hours.
               It started at work and hasn't gone away. I'm really worried."
    ↓
WebSocket → Student: {
  "type": "patient_message",
  "speaker": "patient",
  "message": "Doctor, I've been having this terrible chest pain...",
  "emotional_state": "ANXIOUS_GUARDED",
  "timestamp": "2026-02-09T10:05:23Z"
}
    ↓
Backend: Log to Redis + PostgreSQL
    REDIS LPUSH osce:session:{attempt_id}:messages {message_json}
    PostgreSQL: UPDATE osce_attempts
                SET conversation_history = conversation_history || {message_json}
                WHERE attempt_id = {attempt_id}

┌─────────────────────────────────────────────────────────────────────┐
│ PHASE 4: CONVERSATION LOOP (8 minutes)                              │
└─────────────────────────────────────────────────────────────────────┘

Student: Types message
    WebSocket → "I understand that must be very concerning. Can you tell me
                 more about when it started?"
    ↓
Backend: Process student message
    1. Log message to Redis
    2. Analyze for empathy markers (NLP)
       - Detected: "I understand", "concerning" → empathy_shown = TRUE
    3. Update emotional state
       REDIS HINCRBY osce:session:{attempt_id}:state empathy_points 1
       Check if threshold reached (3 points) → Advance state
       ANXIOUS_GUARDED → CAUTIOUSLY_OPEN
    4. Log student action
       REDIS LPUSH osce:session:{attempt_id}:actions {
         "action": "showed_empathy",
         "category": "communication",
         "timestamp": "2026-02-09T10:05:45Z"
       }
    ↓
Backend: Execute RAG query
    Query Qdrant: "acute coronary syndrome management"
    ↓
    Retrieve top 5 chunks:
    [
      {"text": "STEMI management: ECG within 10 minutes...", "source": "eTG Cardiology p.45"},
      {"text": "Chest pain red flags: crushing pain, radiation...", "source": "AMC Handbook p.234"},
      ...
    ]
    ↓
Backend: Generate AI Patient response
    SYSTEM_PROMPT: "You are Robert Chen. Emotional state: CAUTIOUSLY_OPEN.
                    Student showed empathy, you're willing to share more."
    USER_PROMPT: "Student asked: '{student_message}'"
    RAG_CONTEXT: "{top_5_chunks}"
    ↓
AI Patient (Claude 3.5 Sonnet, temp=0.7)
    Response: "Well, it started about 2 hours ago. I was climbing stairs at work
               when I suddenly felt this crushing pain in my chest. It's like
               someone's standing on my chest. The pain goes down my left arm too."
    ↓
WebSocket → Student: {
  "type": "patient_message",
  "speaker": "patient",
  "message": "Well, it started about 2 hours ago...",
  "emotional_state": "CAUTIOUSLY_OPEN",  # State advanced!
  "timestamp": "2026-02-09T10:06:15Z"
}
    ↓
Backend: Background sync to PostgreSQL (every 30 seconds)
    CronJob:
    FOR each active session in Redis:
        messages = REDIS LRANGE osce:session:{attempt_id}:messages 0 -1
        state = REDIS HGETALL osce:session:{attempt_id}:state
        actions = REDIS LRANGE osce:session:{attempt_id}:actions 0 -1

        PostgreSQL: UPDATE osce_attempts
                    SET conversation_history = {messages},
                        emotional_state_transitions = {state_history},
                        student_actions = {actions},
                        total_messages = {count},
                        total_tokens_used = {sum},
                        updated_at = NOW()
                    WHERE attempt_id = {attempt_id}
    ↓
[Repeat conversation loop for 8 minutes]
    ↓
Timer: 7:00 elapsed → Send 1-minute warning
    WebSocket → Student: {
      "type": "timer_warning",
      "message": "1 minute remaining"
    }
    PostgreSQL: UPDATE osce_attempts SET warning_1min_shown = TRUE
    ↓
Timer: 8:00 elapsed → Auto-finalize session
    WebSocket → Student: {
      "type": "session_ended",
      "message": "Time's up! Your session is being scored."
    }
    PostgreSQL: UPDATE osce_attempts
                SET ended_at = NOW(),
                    duration_seconds = EXTRACT(EPOCH FROM (NOW() - started_at)),
                    timer_expired = TRUE,
                    session_state = 'finalized'

┌─────────────────────────────────────────────────────────────────────┐
│ PHASE 5: AI EXAMINER SCORING                                        │
└─────────────────────────────────────────────────────────────────────┘

Backend: Trigger scoring job
    PostgreSQL: UPDATE osce_attempts SET session_state = 'scoring'
    ↓
Backend: Prepare scoring context
    Load from PostgreSQL:
    - conversation_history (full transcript)
    - emotional_state_transitions
    - student_actions
    - persona details (expected_differentials, critical_actions)
    ↓
AI Examiner (Claude 3.5 Sonnet, temp=0.1 for consistency)
    SYSTEM_PROMPT: "You are an experienced AMC examiner. Score this OSCE
                    using the AMC 15-mark rubric."
    USER_PROMPT:
    """
    SCENARIO: Robert Chen, 52M, chest pain
    EXPECTED DIFFERENTIALS: STEMI, unstable angina, PE
    CRITICAL ACTIONS: ECG within 10 min, aspirin 300mg, call cardiology

    TRANSCRIPT:
    [Student] I understand that must be concerning... (empathy shown)
    [Patient] It started 2 hours ago climbing stairs...
    [Student] Can you describe the pain? (open question, good)
    [Patient] Crushing, radiates to left arm...
    [Student] Any history of heart problems? (systematic approach)
    [Patient] Father died of heart attack age 55...
    [Student] I'm ordering an ECG right now (critical action taken ✓)
    ...

    Score using AMC rubric:
    - Communication (0-3)
    - Clinical Reasoning (0-4)
    - Information Gathering (0-4)
    - Management (0-2)
    - Professionalism (0-2)
    """
    ↓
AI Examiner: Structured output
    {
      "communication_score": 3,
      "communication_feedback": "Excellent empathy shown throughout. Used open questions.
                                 Maintained eye contact (inferred from conversational flow).
                                 Patient progressed from ANXIOUS_GUARDED to TRUSTING.",

      "clinical_reasoning_score": 4,
      "clinical_reasoning_feedback": "Comprehensive differential diagnosis formed.
                                      Correctly identified red flags (chest pain + radiation + family history).
                                      Prioritized STEMI appropriately.",

      "information_gathering_score": 3,
      "information_gathering_feedback": "Systematic history taking. Covered pain characteristics,
                                         risk factors, family history. Minor gap: didn't ask about
                                         previous similar episodes.",

      "management_score": 2,
      "management_feedback": "Appropriate immediate management. Ordered ECG correctly.
                              Mentioned aspirin and cardiology consultation.",

      "professionalism_score": 2,
      "professionalism_feedback": "Professional throughout. Explained clearly. Maintained patient dignity.",

      "total_score": 14,
      "pass_fail": "PASS",
      "critical_errors": [],

      "strengths": ["Excellent empathy", "Systematic approach", "Identified red flags early"],
      "areas_for_improvement": ["Could explore previous episodes", "Could explain ECG findings to patient"],
      "overall_feedback": "Strong performance. Demonstrated excellent communication and clinical reasoning..."
    }
    ↓
Backend: Save score to PostgreSQL
    INSERT INTO osce_scores (
      attempt_id,
      communication_score, communication_feedback,
      clinical_reasoning_score, clinical_reasoning_feedback,
      information_gathering_score, information_gathering_feedback,
      management_score, management_feedback,
      professionalism_score, professionalism_feedback,
      total_score, pass_fail, critical_errors,
      strengths, areas_for_improvement, overall_feedback,
      scored_by, scoring_model, scoring_prompt_version,
      scored_at
    ) VALUES (...)
    ↓
Backend: Update session state
    PostgreSQL: UPDATE osce_attempts SET session_state = 'complete'
    ↓
Backend: Trigger progress update
    Function: update_ai_osce_progress() (see schema section)
    Updates: user_progress.ai_osces_attempted, ai_osces_passed, ai_osce_avg_score
    ↓
Backend: Clear Redis session data
    REDIS DEL osce:session:{attempt_id}:persona
    REDIS DEL osce:session:{attempt_id}:state
    REDIS DEL osce:session:{attempt_id}:messages
    REDIS DEL osce:session:{attempt_id}:actions

┌─────────────────────────────────────────────────────────────────────┐
│ PHASE 6: RESULTS DISPLAY                                            │
└─────────────────────────────────────────────────────────────────────┘

Backend: Send results via WebSocket
    WebSocket → Student: {
      "type": "scoring_complete",
      "total_score": 14,
      "max_score": 15,
      "pass_fail": "PASS",
      "breakdown": {
        "communication": {"score": 3, "max": 3, "feedback": "..."},
        "clinical_reasoning": {"score": 4, "max": 4, "feedback": "..."},
        ...
      },
      "overall_feedback": "Strong performance...",
      "strengths": [...],
      "areas_for_improvement": [...]
    }
    ↓
Frontend: Display results page
    - Score breakdown (bar chart: 14/15, 93%)
    - PASS badge (green)
    - Detailed feedback per rubric category
    - Conversation transcript with annotations
    - Option to review, save PDF, retry

┌─────────────────────────────────────────────────────────────────────┐
│ END OF INDIVIDUAL PRACTICE FLOW                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 3.2 Mock Exam Mode - Complete Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│ MOCK EXAM MODE: 16 SEQUENTIAL STATIONS                              │
└─────────────────────────────────────────────────────────────────────┘

Student: Click "Start Mock Exam"
    ↓
POST /api/v1/mock-exams
Body: {
  "exam_date": "2026-02-09",
  "specialty_mix": "balanced"  # Auto-selects 16 personas across specialties
}
    ↓
Backend: Create mock exam
    1. Select 16 personas (2 per specialty × 8 specialties)
       Query: SELECT persona_id FROM patient_personas
              WHERE difficulty_level IN ('intermediate', 'advanced')
              ORDER BY RANDOM()
              LIMIT 2 PER specialty

    2. Create mock_exams record
       INSERT INTO mock_exams (user_id, exam_date, stations_config)
       VALUES ('user-uuid', '2026-02-09', '[
         {"station": 1, "persona_id": "card-uuid-1", "specialty": "cardiology"},
         {"station": 2, "persona_id": "resp-uuid-2", "specialty": "respiratory"},
         ...
         {"station": 16, "persona_id": "psych-uuid-16", "specialty": "psychiatry"}
       ]')

    3. Return: {
         "exam_id": "mock-exam-uuid",
         "stations": 16,
         "estimated_duration": "2 hours 40 minutes",
         "start_url": "/mock-exam/{exam_id}/station/1"
       }
    ↓
Frontend: Display mock exam instructions
    "You are about to start a full 16-station mock exam. Each station is 8 minutes.
     You cannot pause or skip stations. Are you ready?"
    ↓
Student: Click "Start Exam"
    ↓
Backend: Update exam state
    UPDATE mock_exams SET exam_state = 'in_progress', actual_start = NOW()
    ↓
[For Station 1-16, REPEAT Individual Practice Flow with modifications:]

    Station N:
    1. Create osce_attempt with mock_exam_id and station_number
    2. Run 8-minute session (same as individual practice)
    3. Score session immediately
    4. Auto-advance to next station (no pause)
    ↓
    WebSocket → Student: {
      "type": "station_complete",
      "station": 1,
      "total_stations": 16,
      "score": 12,
      "pass_fail": "PASS",
      "next_station_starts_in": 5  # 5-second break
    }
    ↓
    Wait 5 seconds → Load Station 2...
    ↓
[Repeat until Station 16 complete]
    ↓
Backend: Calculate overall exam score
    Query: SELECT SUM(s.total_score) AS total, COUNT(*) AS stations
           FROM osce_attempts a
           JOIN osce_scores s ON a.attempt_id = s.attempt_id
           WHERE a.mock_exam_id = {exam_id}

    Result: {total: 198, stations: 16}
    Average: 198 / 16 = 12.375 (rounded: 12.4/15 per station)
    Overall: 198 / 240 = 82.5% (PASS if ≥60% AND no critical errors)
    ↓
Backend: Update mock_exams record
    UPDATE mock_exams
    SET exam_state = 'completed',
        actual_end = NOW(),
        total_duration_minutes = EXTRACT(EPOCH FROM (NOW() - actual_start)) / 60,
        total_score = 198,
        overall_pass_fail = 'PASS'
    WHERE exam_id = {exam_id}
    ↓
Backend: Update user progress
    UPDATE user_progress
    SET mock_exams_completed = mock_exams_completed + 1
    WHERE user_id = {user_id}
    ↓
Frontend: Display overall mock exam results
    - Overall score: 198/240 (82.5%) - PASS
    - Station-by-station breakdown (table)
    - Strengths across all stations
    - Common weaknesses to address
    - Comparison to pass threshold
    - Option to download comprehensive PDF report

┌─────────────────────────────────────────────────────────────────────┐
│ END OF MOCK EXAM FLOW                                                │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 4. API Endpoints Specification

### 4.1 Patient Personas API

```
GET /api/v1/patient-personas
Query Params:
  - specialty: String (cardiology, respiratory, etc.)
  - difficulty: String (foundation, intermediate, advanced)
  - limit: Int (default: 20)
  - offset: Int (default: 0)
Response: {
  "total": 360,
  "personas": [
    {
      "persona_id": "uuid",
      "persona_code": "CARD-001-CHEST-PAIN",
      "name": "Robert Chen",
      "age": 52,
      "chief_complaint": "Chest pain for 2 hours",
      "specialty": "cardiology",
      "difficulty_level": "intermediate",
      "estimated_pass_rate": 67.5
    },
    ...
  ]
}
```

```
GET /api/v1/patient-personas/{persona_id}
Response: {
  "persona_id": "uuid",
  "persona_code": "CARD-001-CHEST-PAIN",
  "name": "Robert Chen",
  "age": 52,
  "gender": "Male",
  "occupation": "Accountant",
  "chief_complaint": "Chest pain for 2 hours",
  "opening_statement": "Doctor, I've been having this terrible chest pain...",
  "specialty": "cardiology",
  "difficulty_level": "intermediate",
  "estimated_pass_rate": 67.5,
  "key_differentials": ["STEMI", "Unstable angina", "PE"],
  "amc_blueprint_area": "Cardiovascular - Acute Coronary Syndromes"
}
```

### 4.2 OSCE Sessions API

```
POST /api/v1/osce-sessions
Body: {
  "persona_id": "uuid",
  "session_type": "individual"
}
Response: {
  "attempt_id": "uuid",
  "websocket_url": "wss://api.example.com/ws/osce/{attempt_id}",
  "session_token": "jwt-token",
  "expires_in": 1800,
  "persona": {
    "name": "Robert Chen",
    "opening_statement": "Doctor, I've been having..."
  }
}
```

```
GET /api/v1/osce-sessions/{attempt_id}
Response: {
  "attempt_id": "uuid",
  "user_id": "uuid",
  "persona": {...},
  "session_type": "individual",
  "started_at": "2026-02-09T10:05:23Z",
  "ended_at": "2026-02-09T10:13:45Z",
  "duration_seconds": 502,
  "session_state": "complete",
  "total_messages": 18,
  "total_tokens_used": 3456
}
```

```
GET /api/v1/osce-sessions/{attempt_id}/transcript
Response: {
  "attempt_id": "uuid",
  "conversation": [
    {
      "timestamp": "2026-02-09T10:05:23Z",
      "speaker": "patient",
      "message": "Doctor, I've been having...",
      "emotional_state": "ANXIOUS_GUARDED"
    },
    {
      "timestamp": "2026-02-09T10:05:45Z",
      "speaker": "student",
      "message": "I understand that must be concerning...",
      "empathy_detected": true
    },
    ...
  ],
  "emotional_state_transitions": [
    {"timestamp": "2026-02-09T10:05:23Z", "state": "ANXIOUS_GUARDED"},
    {"timestamp": "2026-02-09T10:06:12Z", "state": "CAUTIOUSLY_OPEN"}
  ]
}
```

```
GET /api/v1/osce-sessions/{attempt_id}/score
Response: {
  "score_id": "uuid",
  "attempt_id": "uuid",
  "total_score": 14,
  "max_score": 15,
  "pass_fail": "PASS",
  "breakdown": {
    "communication": {
      "score": 3,
      "max": 3,
      "feedback": "Excellent empathy shown..."
    },
    "clinical_reasoning": {
      "score": 4,
      "max": 4,
      "feedback": "Comprehensive DDx formed..."
    },
    "information_gathering": {
      "score": 3,
      "max": 4,
      "feedback": "Systematic history taking..."
    },
    "management": {
      "score": 2,
      "max": 2,
      "feedback": "Appropriate immediate management..."
    },
    "professionalism": {
      "score": 2,
      "max": 2,
      "feedback": "Professional throughout..."
    }
  },
  "strengths": ["Excellent empathy", "Systematic approach"],
  "areas_for_improvement": ["Could explore previous episodes"],
  "overall_feedback": "Strong performance...",
  "scored_at": "2026-02-09T10:14:30Z"
}
```

### 4.3 Mock Exams API

```
POST /api/v1/mock-exams
Body: {
  "exam_date": "2026-02-09",
  "specialty_mix": "balanced"
}
Response: {
  "exam_id": "uuid",
  "stations": 16,
  "stations_config": [
    {"station": 1, "persona_id": "uuid-1", "specialty": "cardiology"},
    ...
  ],
  "estimated_duration": "2 hours 40 minutes",
  "start_url": "/mock-exam/{exam_id}/station/1"
}
```

```
GET /api/v1/mock-exams/{exam_id}
Response: {
  "exam_id": "uuid",
  "user_id": "uuid",
  "exam_date": "2026-02-09",
  "exam_state": "completed",
  "current_station": 16,
  "actual_start": "2026-02-09T09:00:00Z",
  "actual_end": "2026-02-09T11:42:15Z",
  "total_duration_minutes": 162,
  "total_score": 198,
  "max_score": 240,
  "overall_pass_fail": "PASS"
}
```

```
GET /api/v1/mock-exams/{exam_id}/results
Response: {
  "exam_id": "uuid",
  "overall_score": 198,
  "max_score": 240,
  "percentage": 82.5,
  "overall_pass_fail": "PASS",
  "stations": [
    {
      "station": 1,
      "persona": "Robert Chen - Chest pain",
      "specialty": "cardiology",
      "score": 14,
      "pass_fail": "PASS"
    },
    ...
  ],
  "summary": {
    "stations_passed": 15,
    "stations_failed": 1,
    "average_score": 12.4,
    "strongest_area": "Communication (avg 2.8/3)",
    "weakest_area": "Management (avg 1.5/2)"
  },
  "comprehensive_feedback": "Overall strong performance..."
}
```

### 4.4 WebSocket Protocol

```
Connection: wss://api.example.com/ws/osce/{attempt_id}?token={jwt-token}

Client → Server Messages:
{
  "type": "student_message",
  "message": "Can you tell me more about when the pain started?"
}

Server → Client Messages:
{
  "type": "patient_message",
  "speaker": "patient",
  "message": "It started about 2 hours ago climbing stairs...",
  "emotional_state": "CAUTIOUSLY_OPEN",
  "timestamp": "2026-02-09T10:06:15Z"
}

{
  "type": "timer_update",
  "elapsed_seconds": 420,
  "remaining_seconds": 60
}

{
  "type": "timer_warning",
  "message": "1 minute remaining"
}

{
  "type": "session_ended",
  "message": "Time's up! Your session is being scored.",
  "attempt_id": "uuid"
}

{
  "type": "scoring_complete",
  "total_score": 14,
  "pass_fail": "PASS",
  "breakdown": {...}
}

{
  "type": "error",
  "code": "RATE_LIMIT_EXCEEDED",
  "message": "Please wait before sending another message"
}
```

---

## 5. Redis Session Management

### 5.1 Redis Key Structure

```
# Active session persona data
osce:session:{attempt_id}:persona
TTL: 1800 seconds (30 minutes)
Value: JSON {
  "persona_id": "uuid",
  "name": "Robert Chen",
  "symptoms": {...},
  "emotional_profile": {...},
  "rag_query_hints": [...]
}

# Active session state
osce:session:{attempt_id}:state
TTL: 1800 seconds
Value: Hash {
  "session_state": "conversation",
  "emotional_state": "CAUTIOUSLY_OPEN",
  "pain_level": 8,
  "anxiety_level": 5,
  "empathy_points": 2,
  "message_count": 8,
  "tokens_used": 1234
}

# Conversation history (temp buffer)
osce:session:{attempt_id}:messages
TTL: 1800 seconds
Value: List of JSON [
  {"timestamp": "...", "speaker": "patient", "message": "..."},
  {"timestamp": "...", "speaker": "student", "message": "..."},
  ...
]

# Student actions log
osce:session:{attempt_id}:actions
TTL: 1800 seconds
Value: List of JSON [
  {"timestamp": "...", "action": "showed_empathy", "category": "communication"},
  ...
]

# RAG context cache
osce:session:{attempt_id}:rag_cache
TTL: 1800 seconds
Value: JSON {
  "last_query": "acute coronary syndrome",
  "chunks": [...],
  "timestamp": "2026-02-09T10:06:00Z"
}
```

### 5.2 Background Sync Job

```python
# Runs every 30 seconds via Celery Beat

@celery.task
def sync_active_osce_sessions():
    """Sync Redis session data to PostgreSQL for disaster recovery"""

    # Find all active sessions
    pattern = "osce:session:*:state"
    active_sessions = redis_client.keys(pattern)

    for session_key in active_sessions:
        attempt_id = session_key.split(":")[2]

        # Load from Redis
        messages = redis_client.lrange(f"osce:session:{attempt_id}:messages", 0, -1)
        state = redis_client.hgetall(f"osce:session:{attempt_id}:state")
        actions = redis_client.lrange(f"osce:session:{attempt_id}:actions", 0, -1)

        # Parse JSON
        messages_json = [json.loads(msg) for msg in messages]
        actions_json = [json.loads(action) for action in actions]

        # Update PostgreSQL
        db.execute("""
            UPDATE osce_attempts
            SET conversation_history = :messages,
                student_actions = :actions,
                total_messages = :msg_count,
                total_tokens_used = :tokens,
                updated_at = NOW()
            WHERE attempt_id = :attempt_id
        """, {
            "messages": json.dumps(messages_json),
            "actions": json.dumps(actions_json),
            "msg_count": int(state.get('message_count', 0)),
            "tokens": int(state.get('tokens_used', 0)),
            "attempt_id": attempt_id
        })

    logger.info(f"Synced {len(active_sessions)} active OSCE sessions to PostgreSQL")
```

### 5.3 Session Cleanup

```python
@celery.task
def cleanup_expired_osce_sessions():
    """Clean up Redis data for completed/expired sessions"""

    # Find sessions completed > 1 hour ago
    cutoff = datetime.utcnow() - timedelta(hours=1)

    completed_attempts = db.execute("""
        SELECT attempt_id
        FROM osce_attempts
        WHERE session_state = 'complete'
        AND ended_at < :cutoff
    """, {"cutoff": cutoff}).fetchall()

    for row in completed_attempts:
        attempt_id = row[0]

        # Delete from Redis (data already in PostgreSQL)
        redis_client.delete(
            f"osce:session:{attempt_id}:persona",
            f"osce:session:{attempt_id}:state",
            f"osce:session:{attempt_id}:messages",
            f"osce:session:{attempt_id}:actions",
            f"osce:session:{attempt_id}:rag_cache"
        )

    logger.info(f"Cleaned up {len(completed_attempts)} expired Redis sessions")
```

---

## 6. Integration Points with Existing System

### 6.1 Authentication & Authorization

```
AI OSCE system inherits existing RBAC:

Permissions required:
- osce:practice:access (all authenticated students)
- osce:mock_exam:access (premium tier or paid users)
- persona:manage:create (admin only - create new personas)
- persona:manage:validate (clinical experts - approve personas)

Existing infrastructure:
- JWT authentication (backend/src/auth/security.py)
- Permission checking (backend/src/auth/permissions.py)
- WebSocket authentication (backend/src/websocket/authenticator.py)

Usage:
@require_permission("osce:practice:access")
async def create_osce_session(persona_id: UUID, user: User = Depends(get_current_user)):
    ...
```

### 6.2 Progress Tracking Integration

```
Existing user_progress table EXTENDED (see schema section 2.6):

New columns added:
- ai_osces_attempted: INT (counter)
- ai_osces_passed: INT (counter)
- ai_osce_avg_score: DECIMAL (rolling average)
- mock_exams_completed: INT (counter)
- last_ai_osce_at: TIMESTAMP

Frontend dashboard can now show:
- "You've completed 15 AI OSCEs this week (12 passed, 3 failed)"
- "Average score: 11.2/15 (75%)"
- "Strongest area: Communication (2.8/3 avg)"
- "Weakest area: Management (1.4/2 avg) - Practice more!"
```

### 6.3 Content Taxonomy Integration

```
AI personas use existing specialty taxonomy:

Existing specialties (from current system):
- Cardiology
- Respiratory
- Gastroenterology
- Neurology
- Endocrinology
- Psychiatry
- Surgery
- ObGyn
- Paediatrics

patient_personas.specialty references this taxonomy

Frontend filters:
- Browse by specialty (reuse existing filter components)
- Filter by difficulty (new: foundation/intermediate/advanced)
- Search by chief complaint
```

### 6.4 RAG System Integration

```
AI Patient/Examiner use EXISTING Qdrant RAG:

Existing infrastructure:
- Qdrant vector DB (port 6333)
- 42,647 medical chunks indexed
- Sources: eTG, AMH, AMC Clinical Examination Handbook, Cochrane
- Embeddings: sentence-transformers/all-MiniLM-L6-v2

NEW usage pattern:
- AI Patient: Query RAG for realistic symptom details
  Example: "acute coronary syndrome typical presentation"
  → Retrieve chunks about chest pain characteristics, risk factors
  → AI uses this to give medically accurate responses

- AI Examiner: Query RAG for scoring guidelines
  Example: "AMC OSCE communication skills rubric"
  → Retrieve official marking criteria
  → AI scores consistently with guidelines

No changes to existing RAG infrastructure needed
```

### 6.5 AI Router Integration

```
AI Patient/Examiner use EXISTING ai_router:

Existing infrastructure:
- backend/src/ai_router/ (dual provider system)
- Provider 1: Kimi 2.5 (FREE fallback)
- Provider 2: Claude 3.5 Sonnet (PAID primary)
- Circuit breaker: Falls back to Kimi on rate limits

NEW usage:
from src.ai_router import get_ai_client

client = await get_ai_client(
    task="osce_patient_simulation",
    max_tokens=500,
    temperature=0.7
)

response = await client.generate(
    system_prompt=PATIENT_SYSTEM_PROMPT,
    user_message=student_message,
    rag_context=chunks
)

Circuit breaker logic (existing):
- If Claude rate limited → Switch to Kimi
- If Claude error rate > 10% → Switch to Kimi
- If budget exceeded → Switch to Kimi

NEW cost tracking:
- Log tokens per OSCE attempt
- Alert if daily cost > $50 (safety threshold)
```

---

## 7. Performance & Scalability

### 7.1 Latency Targets

```
User Action → AI Response: <3 seconds (95th percentile)

Breakdown:
- Student message → Backend: <100ms (WebSocket)
- Backend processing (empathy detection, state update): <200ms
- RAG query to Qdrant: <300ms (5 chunks)
- Claude 3.5 Sonnet generation: <2000ms (avg 1200ms)
- Response → Student: <100ms (WebSocket)
Total: <2700ms (within 3s target)

Optimizations:
- RAG caching: Cache chunks per persona (30 min TTL)
- Prompt caching: Claude caches system prompts (40% token savings)
- Response streaming: Show partial responses as they generate
```

### 7.2 Concurrent Capacity

```
Target: 100 simultaneous OSCE sessions

Resource requirements:
- Redis: 100 sessions × 5 keys × 10KB avg = 5MB (negligible)
- PostgreSQL: Sync writes every 30s (100 sessions = 3.3 writes/sec, easy)
- Claude API: 100 sessions × 8 min × 6 messages/min = 4800 messages / 8 min = 10 req/sec
  - Claude 3.5 rate limit: 10,000 req/min → 166 req/sec (plenty of headroom)
- WebSocket connections: 100 concurrent (FastAPI handles 10K+ easily)

Bottleneck analysis:
- Most likely bottleneck: Claude API cost, not capacity
- Mitigation: Circuit breaker to free Kimi if budget exceeded
```

### 7.3 Cost Analysis

```
Per OSCE Session (8 minutes, ~18 messages):

AI Patient responses:
- 18 messages × 150 tokens avg = 2700 tokens output
- System prompt: 500 tokens (cached after first message)
- Student messages: 18 × 50 tokens = 900 tokens input
- RAG context: 5 chunks × 200 tokens × 3 queries = 3000 tokens input
- Total: 3900 input tokens, 2700 output tokens

AI Examiner scoring:
- System prompt: 300 tokens
- Transcript: 3000 tokens input
- Scoring output: 800 tokens output
- Total: 3300 input tokens, 800 output tokens

Overall per session:
- Input: 7200 tokens × $3/M = $0.0216
- Output: 3500 tokens × $15/M = $0.0525
- Total: $0.0741 per OSCE session

With prompt caching (40% savings):
- Cost: $0.0445 per OSCE session
- Target: <$0.30 (✓ achieved)

At scale (1000 OSCEs/day):
- Daily cost: $44.50
- Monthly cost: $1,335
- Annual cost: $16,245 (reasonable for premium feature)
```

---

## 8. Implementation Roadmap

### Phase 1: Database & Core APIs (Week 1)
- [ ] Create new tables (patient_personas, osce_attempts, osce_scores, mock_exams)
- [ ] Add columns to user_progress
- [ ] Create database migrations
- [ ] Implement CRUD APIs for patient personas
- [ ] Implement session creation API
- [ ] Test database schema with sample data

### Phase 2: AI Integration (Week 2)
- [ ] Create AI Patient system prompts (50 variations)
- [ ] Create AI Examiner scoring prompts
- [ ] Integrate with existing ai_router
- [ ] Integrate with existing RAG system
- [ ] Implement emotional state machine
- [ ] Test AI responses with sample conversations

### Phase 3: WebSocket Infrastructure (Week 3)
- [ ] Extend existing WebSocket authenticator for OSCE sessions
- [ ] Implement conversation loop (student ↔ AI Patient)
- [ ] Implement timer system (8-minute countdown, 1-min warning)
- [ ] Implement Redis session management
- [ ] Implement background sync job (Redis → PostgreSQL)
- [ ] Test concurrent sessions (10 simultaneous)

### Phase 4: Scoring System (Week 4)
- [ ] Implement AI Examiner scoring algorithm
- [ ] Create rubric templates (AMC 15-mark)
- [ ] Implement critical error detection
- [ ] Create Golden Dataset (20 validated scenarios)
- [ ] Test scoring consistency (AI vs human examiner)
- [ ] Implement feedback generation

### Phase 5: Frontend Implementation (Week 5-6)
- [ ] Persona browsing page (filter by specialty/difficulty)
- [ ] OSCE session interface (chat UI, timer, patient info)
- [ ] WebSocket integration (real-time messaging)
- [ ] Results display (score breakdown, feedback)
- [ ] Transcript viewer (annotated conversation)
- [ ] Mock exam orchestration UI

### Phase 6: Mock Exam Mode (Week 7)
- [ ] Mock exam creation logic (16 persona selection)
- [ ] Station progression system
- [ ] Overall scoring calculation
- [ ] Comprehensive report generation
- [ ] PDF export functionality
- [ ] Test full 2.5-hour mock exam flow

### Phase 7: Testing & Validation (Week 8)
- [ ] Load testing (100 concurrent sessions)
- [ ] Golden Dataset validation (200 scenarios)
- [ ] Compare AI vs human examiner scores
- [ ] Security testing (RBAC, WebSocket auth)
- [ ] Performance optimization (cache tuning)
- [ ] Cost monitoring (stay within budget)

### Phase 8: Content Creation (Week 9-12)
- [ ] Create 360 patient personas (45 per specialty × 8)
- [ ] Expert clinician validation
- [ ] Progressive disclosure script writing
- [ ] Emotional profile tuning
- [ ] RAG query hint optimization
- [ ] Estimated pass rate calibration

### Phase 9: Production Launch (Week 13)
- [ ] Deploy to production
- [ ] Monitor first 100 sessions
- [ ] Gather user feedback
- [ ] Iterate on AI prompts
- [ ] Document best practices
- [ ] Train support team

---

## 9. Success Metrics

### 9.1 Technical Metrics

```
Latency:
- Target: <3s per AI response (95th percentile)
- Measure: Prometheus histogram (ai_response_latency_seconds)

Uptime:
- Target: 99.5% (max 3.6 hours downtime/month)
- Measure: Uptime Robot monitoring

Cost:
- Target: <$0.30 per OSCE session
- Measure: Track tokens_used, calculate daily spend
- Alert: If daily cost > $50

Accuracy:
- Target: 96%+ medical accuracy (with RAG)
- Measure: Expert validation of AI Patient responses
- Golden Dataset: AI Examiner scores within ±2 marks of human

Concurrent Capacity:
- Target: 100 simultaneous sessions
- Measure: Load testing with Locust (ramp to 100 users)
```

### 9.2 User Experience Metrics

```
Session Completion Rate:
- Target: >90% (students finish 8-minute session without abandoning)
- Measure: COUNT(ended_at IS NOT NULL) / COUNT(started_at)

Pass Rate:
- Target: 60-70% (similar to real AMC OSCE)
- Measure: COUNT(pass_fail = 'PASS') / COUNT(*)

User Satisfaction:
- Target: >4.0/5.0 rating
- Measure: Post-session survey

Mock Exam Adoption:
- Target: 30% of users complete at least 1 mock exam
- Measure: COUNT(DISTINCT user_id FROM mock_exams) / COUNT(DISTINCT user_id FROM users)
```

### 9.3 Clinical Metrics

```
Scoring Consistency:
- Target: AI Examiner within ±2 marks of human examiner (200 Golden Dataset scenarios)
- Measure: Quarterly validation study

Emotional Realism:
- Target: >80% of students report "AI patient felt realistic"
- Measure: Post-session survey question

Clinical Accuracy:
- Target: 0 major clinical errors in AI Patient responses
- Measure: Expert clinician monthly audit (sample 50 transcripts)
```

---

## 10. Risk Mitigation

### 10.1 Technical Risks

**Risk 1: Claude API Rate Limits**
- Impact: Students cannot practice OSCEs
- Mitigation: Circuit breaker to free Kimi 2.5 fallback (existing infrastructure)
- Monitoring: Track API error rate, auto-switch at 10% error rate

**Risk 2: Cost Overrun**
- Impact: Monthly AI costs exceed budget ($2000/month)
- Mitigation:
  - Hard cap: Max 50K tokens per OSCE session
  - Daily budget: Alert if cost > $50/day
  - Fallback: Switch to Kimi (free) if budget exceeded
- Monitoring: Real-time token tracking, daily cost reports

**Risk 3: Redis Data Loss**
- Impact: Active session state lost (student loses progress)
- Mitigation:
  - Background sync to PostgreSQL every 30 seconds
  - Redis persistence enabled (AOF mode)
  - Students can resume from last sync point
- Recovery: 90% of session data recoverable from PostgreSQL

**Risk 4: Latency Spikes**
- Impact: AI responses take >5 seconds (poor UX)
- Mitigation:
  - RAG caching (avoid repeated Qdrant queries)
  - Prompt caching (Claude caches system prompts)
  - Response streaming (show partial responses)
- Monitoring: Alert if p95 latency > 3 seconds

### 10.2 Clinical Risks

**Risk 5: AI Medical Errors**
- Impact: AI Patient gives clinically incorrect information
- Mitigation:
  - RAG integration (96.4% accuracy vs 86.6% without)
  - Expert validation of all 360 personas
  - Monthly transcript audits by clinician
  - Disclaimer: "This is a simulation for practice only"
- Monitoring: Expert clinician reviews sample of 50 transcripts/month

**Risk 6: Inconsistent Scoring**
- Impact: AI Examiner scores unfairly vs human examiners
- Mitigation:
  - Golden Dataset validation (200 scenarios)
  - Quarterly recalibration (compare AI vs human scores)
  - Target: ±2 marks variance
  - Students can request human review
- Monitoring: Track score variance, student complaints

### 10.3 User Experience Risks

**Risk 7: Low Adoption**
- Impact: Students don't use AI OSCE feature
- Mitigation:
  - Onboarding: Guided first OSCE with tips
  - Gamification: Achievements for completing 10 OSCEs
  - Social proof: "1,245 students practiced this week"
- Monitoring: Track weekly active users, session starts

**Risk 8: Unrealistic AI Patient**
- Impact: Students report "AI felt robotic, not like real patient"
- Mitigation:
  - Emotional state machine (6 states)
  - Progressive disclosure (reveal info naturally)
  - Cultural background details
  - User testing with 10 beta students before launch
- Monitoring: Post-session survey: "How realistic was the AI patient?"

---

## 11. Security & Compliance

### 11.1 Data Privacy

```
Personal Data Stored:
- Student messages (conversation transcripts)
- Performance scores
- Session timestamps

Compliance:
- GDPR: Students can request data deletion
  - API: DELETE /api/v1/users/{user_id}/osce-data
  - Soft delete: osce_attempts.deleted_at = NOW()
- Data retention: 2 years, then auto-purge
- Anonymization: Remove user_id for research analytics

Medical Data:
- AI Patient personas: NOT real patient data (synthetic scenarios)
- No PHI (Protected Health Information) stored
- Disclaimer: "This is a simulation, not real medical advice"
```

### 11.2 Authentication & Authorization

```
Existing RBAC (reused):
- JWT authentication (backend/src/auth/security.py)
- Zero-trust WebSocket auth (backend/src/websocket/authenticator.py)
- Permission checking (backend/src/auth/permissions.py)

New permissions:
- osce:practice:access (default for all authenticated students)
- osce:mock_exam:access (premium tier only)
- persona:manage:create (admin only)
- persona:manage:validate (clinical experts only)

Rate limiting (existing):
- Max 3 concurrent WebSocket connections per user
- Redis sliding window (backend/src/websocket/rate_limiter.py)
```

### 11.3 Abuse Prevention

```
Anti-Cheating Measures:
- Session timer strictly enforced (cannot pause/extend)
- Mock exams cannot be restarted mid-exam
- Transcripts logged for audit (detect GPT-4 assistance)

Cost Abuse Prevention:
- Max 50K tokens per OSCE session (hard cap)
- Max 10 OSCE sessions per user per day
- Suspicious usage patterns flagged for review

Content Moderation:
- Student messages scanned for inappropriate content
- AI Patient will not respond to offensive/unethical questions
- Violations logged, repeat offenders suspended
```

---

## Appendix A: Sample Patient Persona

```json
{
  "persona_id": "550e8400-e29b-41d4-a716-446655440001",
  "persona_code": "CARD-001-CHEST-PAIN",
  "name": "Robert Chen",
  "age": 52,
  "gender": "Male",
  "occupation": "Accountant",
  "cultural_background": "Chinese Australian",
  "preferred_language": "English (Cantonese as second language)",

  "specialty": "cardiology",
  "chief_complaint": "Chest pain for 2 hours",
  "opening_statement": "Doctor, I've been having this terrible chest pain for the past 2 hours. It started at work and it hasn't gone away. I'm really worried.",

  "symptoms": {
    "immediate": [
      "Chest pain for 2 hours",
      "Pain radiates to left arm",
      "Feels like crushing pressure"
    ],
    "when_asked_onset": "Started suddenly while climbing stairs at work around 11am. Was carrying a box of files.",
    "when_asked_severity": "8 out of 10. It's the worst pain I've ever felt. Like someone's standing on my chest.",
    "when_asked_character": "Heavy, crushing, tight. Not sharp or stabbing.",
    "when_asked_radiation": "Goes down my left arm, sometimes into my jaw.",
    "when_asked_relieving_factors": "Sitting still helps a bit, but it doesn't go away. Paracetamol didn't help.",
    "when_asked_aggravating_factors": "Moving around makes it worse. Deep breaths hurt a bit.",
    "when_asked_associated_symptoms": "I'm sweating a lot and feel a bit nauseous. Short of breath too.",
    "when_asked_previous_episodes": "Had similar pain about 6 months ago after climbing stairs, but it went away after 5 minutes. Thought it was just indigestion."
  },

  "medical_history": {
    "volunteer": [
      "Type 2 diabetes for 10 years",
      "High cholesterol"
    ],
    "when_asked_medications": [
      "Metformin 1000mg twice daily",
      "Atorvastatin 40mg at night",
      "Baby aspirin 100mg daily"
    ],
    "when_asked_allergies": "No known allergies",
    "when_asked_family_history": "Father died of heart attack at age 55. Mother has high blood pressure.",
    "when_asked_social": {
      "smoking": "Smoked 10 cigarettes per day for 20 years. Tried to quit many times.",
      "alcohol": "Social drinker, 1-2 beers on weekends",
      "exercise": "Sedentary job. No regular exercise.",
      "diet": "Irregular meals due to work stress. Eats takeaway often."
    }
  },

  "emotional_profile": {
    "baseline_state": "ANXIOUS_GUARDED",
    "pain_level": 8,
    "anxiety_level": 7,
    "trust_threshold": 3,
    "triggers": {
      "empathy_phrases": [
        "I understand this must be frightening",
        "I can see you're in a lot of pain",
        "Thank you for telling me",
        "We're going to take good care of you"
      ],
      "dismissive_phrases": [
        "It's probably nothing serious",
        "You're overreacting",
        "Let's not worry about that",
        "Rushed body language (inferred from conversation pace)"
      ],
      "cultural_sensitivity_tests": [
        "Would you like me to call your family?",
        "Is there anyone you'd like present during examination?",
        "Do you have any cultural preferences for care?"
      ]
    },
    "state_transitions": {
      "ANXIOUS_GUARDED → CAUTIOUSLY_OPEN": "Student shows empathy, uses open-ended questions, explains what they're doing",
      "CAUTIOUSLY_OPEN → TRUSTING": "Student addresses pain management, gives clear explanations, involves patient in decision-making",
      "TRUSTING → FULLY_COOPERATIVE": "Student demonstrates cultural sensitivity, includes family, explains prognosis honestly",
      "ANY_STATE → WITHDRAWN": "Student dismisses concerns, interrupts frequently, appears rushed or distracted",
      "ANY_STATE → UPSET": "Student makes insensitive comments about lifestyle (smoking, weight), judgmental tone"
    }
  },

  "rag_query_hints": [
    "acute coronary syndrome management",
    "STEMI vs NSTEMI presentation",
    "chest pain red flags",
    "AMC cardiology emergency management",
    "cardiac risk factors assessment"
  ],

  "key_differentials": [
    "STEMI (most likely given duration, radiation, sweating)",
    "Unstable angina",
    "Pulmonary embolism",
    "Aortic dissection (less likely, no back pain)",
    "Pericarditis (less likely, not pleuritic)"
  ],

  "critical_actions": [
    "Order ECG within 10 minutes",
    "Give aspirin 300mg immediately (if not allergic)",
    "Call cardiology/emergency team",
    "IV access and bloods (troponin, FBC, lipids, glucose)",
    "Continuous cardiac monitoring",
    "Oxygen if SpO2 <94%",
    "Analgesia (morphine if severe pain)",
    "Explain diagnosis and urgent need for transfer"
  ],

  "difficulty_level": "intermediate",
  "estimated_pass_rate": 67.5,

  "amc_blueprint_area": "Cardiovascular - Acute Coronary Syndromes",
  "amc_competencies": [
    "Clinical reasoning and diagnostic skills",
    "Emergency and acute care management",
    "Communication and patient-centered care",
    "Risk assessment and prevention"
  ],

  "is_active": true,
  "version": 1,
  "validated_by": "expert-clinician-uuid",
  "validated_at": "2026-02-01T10:00:00Z"
}
```

---

## Appendix B: Sample Conversation Transcript

```
[Station: CARD-001-CHEST-PAIN | Duration: 8:00 | Score: 14/15 - PASS]

00:00 [AI Patient - ANXIOUS_GUARDED]
"Doctor, I've been having this terrible chest pain for the past 2 hours. It started at work and it hasn't gone away. I'm really worried."

00:18 [Student]
"I can see you're very concerned, and I want to help you. Thank you for coming in. Can you tell me a bit more about the pain? Where exactly do you feel it?"

[Empathy detected ✓ → Emotional state advancing]

00:35 [AI Patient - CAUTIOUSLY_OPEN]
"It's right here in the middle of my chest. It's like someone's standing on my chest... the pain is so heavy. And it goes down my left arm too."

00:52 [Student]
"That sounds very uncomfortable. When did this pain start exactly, and what were you doing at the time?"

[Open-ended question ✓, systematic approach ✓]

01:10 [AI Patient - CAUTIOUSLY_OPEN]
"It started around 11am this morning. I was climbing stairs at work, carrying a box of files. The pain just came on suddenly."

01:28 [Student]
"I see. On a scale of 0 to 10, with 10 being the worst pain imaginable, how would you rate this pain?"

[Pain assessment ✓]

01:42 [AI Patient - CAUTIOUSLY_OPEN]
"It's an 8. It's the worst pain I've ever felt, doctor. I'm really scared."

01:55 [Student]
"I understand this is frightening. We're going to take good care of you. Have you noticed any other symptoms along with the chest pain? Like shortness of breath or sweating?"

[Empathy maintained ✓, Associated symptoms checked ✓]

02:15 [AI Patient - TRUSTING]
"Yes! I'm sweating a lot, even though it's not hot. And I'm short of breath. I also feel a bit nauseous."

[Emotional state advanced: TRUSTING - student earning trust]

02:35 [Student]
"Thank you for telling me all this. I need to ask about your medical history. Do you have any existing medical conditions? High blood pressure, diabetes, anything like that?"

[Systematic history taking ✓]

02:52 [AI Patient - TRUSTING]
"Yes, I have diabetes. I've had it for about 10 years. And high cholesterol too. I take metformin and atorvastatin."

03:10 [Student]
"And does anyone in your family have heart problems?"

[Family history ✓ - relevant to cardiac risk]

03:20 [AI Patient - TRUSTING]
"My father died of a heart attack when he was 55. My mother has high blood pressure."

[RED FLAG revealed - strong family history]

03:35 [Student]
"I'm sorry to hear about your father. Do you smoke?"

[Risk factors assessment ✓]

03:42 [AI Patient - TRUSTING]
"Yes... I smoke about 10 cigarettes a day. I've been smoking for 20 years. I know I should quit."

03:58 [Student]
"That's useful information, thank you. Based on what you've told me, I'm concerned this could be your heart. I'm going to order an ECG right away - that's a heart tracing - and we need to get you to hospital urgently."

[Critical action identified ✓, Clear communication ✓]

04:20 [AI Patient - FULLY_COOPERATIVE]
"Oh God, is it a heart attack? Am I going to be okay?"

[Emotional state: FULLY_COOPERATIVE - student has built strong rapport]

04:28 [Student]
"I understand you're worried. Yes, this could be a heart attack, which is why we need to act quickly. The good news is that we've caught this early and there are very effective treatments available. I'm going to give you some aspirin to chew right now, and we're going to call the cardiology team."

[Management explained ✓, Critical medication given ✓, Appropriate urgency ✓]

04:55 [AI Patient - FULLY_COOPERATIVE]
"Okay doctor, I trust you. Should I call my wife?"

05:05 [Student]
"Absolutely, that's a good idea. Would you like me to speak with her as well to explain what's happening?"

[Patient-centered care ✓, Family involvement ✓]

05:15 [AI Patient - FULLY_COOPERATIVE]
"Yes please, that would help. She'll be very worried."

05:25 [Student]
"Of course. While we're waiting for the ambulance, I'm going to start some monitoring and get IV access so we can give you pain relief if you need it. Is your pain any better or worse right now?"

[Ongoing assessment ✓, Procedural explanation ✓]

05:45 [AI Patient - FULLY_COOPERATIVE]
"It's still about an 8. It hasn't really changed."

05:52 [Student]
"Okay, I'm going to give you some morphine for the pain. This will help make you more comfortable."

[Analgesia provided ✓]

06:05 [AI Patient - FULLY_COOPERATIVE]
"Thank you doctor. What happens next?"

06:12 [Student]
"The cardiology team will review your ECG and bloods. Depending on the results, you'll likely need a procedure called an angiogram where they look at the arteries in your heart. They might need to put in a stent to open up a blocked artery. This is a very effective treatment and you're in the best place."

[Clear prognosis ✓, Next steps explained ✓]

06:40 [AI Patient - FULLY_COOPERATIVE]
"Okay, I understand. Thank you for explaining everything so clearly."

06:50 [Student]
"You're welcome. Do you have any questions for me?"

[Opportunity for questions ✓]

07:00 [AI Patient - FULLY_COOPERATIVE]
"No, I think you've explained everything well. I'm just scared."

07:08 [Student]
"That's completely understandable. The team here is excellent and we're going to look after you. I'll stay with you until the ambulance arrives, and I'll call your wife now."

[Reassurance ✓, Continuity of care ✓]

07:30 [AI Patient - FULLY_COOPERATIVE]
"Thank you doctor, I really appreciate your help."

08:00 [SESSION ENDED - Scoring in progress...]

═══════════════════════════════════════════════════════════════════

SCORING REPORT - Generated by AI Examiner

Communication: 3/3 - EXCELLENT
✓ Established rapport immediately with empathy statement
✓ Used open-ended questions throughout
✓ Explained all procedures clearly in patient-friendly language
✓ Involved family appropriately
✓ Patient emotional state progressed from ANXIOUS_GUARDED → FULLY_COOPERATIVE

Clinical Reasoning: 4/4 - EXCELLENT
✓ Formed comprehensive differential diagnosis (ACS as primary)
✓ Identified critical red flags (chest pain + radiation + family history + diabetes)
✓ Prioritized appropriately (cardiac cause given clinical picture)
✓ Logical systematic approach to history taking

Information Gathering: 3/4 - GOOD
✓ Systematic pain assessment (SOCRATES approach)
✓ Thorough risk factor assessment (DM, smoking, FHx)
✓ Associated symptoms explored
✗ Minor gap: Did not ask about previous similar episodes (patient had episode 6 months ago)

Management: 2/2 - EXCELLENT
✓ ECG ordered urgently (critical action)
✓ Aspirin 300mg given immediately (critical action)
✓ Cardiology team called (critical action)
✓ Analgesia provided (morphine)
✓ Appropriate urgency demonstrated

Professionalism: 2/2 - EXCELLENT
✓ Professional demeanor throughout
✓ Patient dignity maintained
✓ Clear, honest communication about diagnosis
✓ Cultural sensitivity (offered to include family)

TOTAL SCORE: 14/15 (93%)
RESULT: PASS ✓

Critical Errors: NONE

Strengths:
• Excellent empathy and communication skills - patient trust built rapidly
• Systematic approach to history taking
• Identified red flags early and acted appropriately
• Clear explanations of management plan

Areas for Improvement:
• Could have explored previous similar episodes (patient mentioned 6-month-ago episode only when directly asked in simulation, but student didn't ask)
• Could have explained ECG findings to patient once available

Overall Feedback:
This was a strong performance demonstrating excellent clinical and communication skills. The student quickly identified this as a likely acute coronary syndrome and acted appropriately with urgent management. The systematic approach to history taking, combined with empathetic communication, resulted in the patient feeling reassured despite a frightening situation. The student correctly prioritized critical actions (ECG, aspirin, cardiology referral) and explained the management plan clearly. This performance meets AMC standards for safe, effective, and patient-centered care.

Recommendation: PASS - This student is ready for independent practice in this scenario.

═══════════════════════════════════════════════════════════════════
```

---

## Document Control

**Revision History:**

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-02-09 | PM Coordinator | Initial architecture document |

**Approval:**

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Product Owner | [Pending] | | |
| Technical Lead | [Pending] | | |
| Clinical Advisor | [Pending] | | |

**Next Steps:**
1. User review of architecture (confirm approach aligns with vision)
2. Technical team review (validate feasibility)
3. Clinical advisor review (validate medical accuracy approach)
4. Approval to proceed with Phase 1 implementation

**Related Documents:**
- COMPREHENSIVE_PLATFORM_PLAN.md (product roadmap)
- PROJECT_CONSTRAINTS.md (development constraints)
- backend/src/ai_router/README.md (existing AI infrastructure)
- backend/src/websocket/README.md (existing WebSocket infrastructure)

---

**END OF DOCUMENT**
