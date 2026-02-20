# PRD: AI OSCE Database Schema & API Endpoints

**PRD ID**: PRD_AI_OSCE_001_DATABASE_AND_APIS
**Category**: Backend
**Priority**: P0-Critical (BLOCKS all AI OSCE work)
**Estimated Effort**: 16-20 hours
**Dependencies**: None (foundation task)
**Status**: Not Started

---

## R - REQUEST (What & Why)

### User Story
**As a** backend developer
**I want** a complete AI OSCE database schema with patient personas, session tracking, scoring, and REST API endpoints
**So that** the AI Patient/Examiner simulation system can store 360 patient personas, track 8-minute OSCE sessions, record AI-scored performance, and enable medical students to practice clinical skills for the AMC Clinical Examination

### Business Context
The AI OSCE Simulation System requires dedicated database infrastructure and API layer to support:

1. **360 AI Patient Personas** (progressive disclosure, emotional intelligence, RAG-integrated)
2. **Individual Practice Sessions** (8-minute OSCE simulations with real-time AI interaction)
3. **Mock Exam Mode** (16-station sequential exams, 2.5 hours total)
4. **AMC 15-Mark Rubric Scoring** (AI Examiner with Communication/Clinical Reasoning/Management scores)
5. **Progress Integration** (link AI OSCE performance to existing user_progress tracking)
6. **Session State Management** (Redis for active sessions, PostgreSQL for permanent archive)

This database migration and API implementation is the **foundation** for the entire AI OSCE feature and must be completed before any frontend or AI integration work can begin.

**Business Value**:
- Provides realistic clinical practice without requiring standardized patients
- Reduces examination anxiety through unlimited practice opportunities
- Delivers instant, consistent AI-powered feedback (vs. delayed human feedback)
- Enables data-driven performance analytics and progress tracking
- Cost-effective at scale ($0.04-0.07 per session vs. $50-100 for human-based OSCE)

### Success Metrics
- **Migration Speed**: Complete database setup in <5 minutes (no table locks)
- **Data Integrity**: 0 data loss, all foreign keys validated, 360 personas loaded
- **API Response Time**: <200ms for GET requests, <500ms for POST with validation
- **Query Performance**: Active session queries <50ms, persona retrieval <100ms
- **Schema Accuracy**: 100% match to specification (4 new tables + user_progress extension)
- **Rollback Safety**: Rollback script tested and functional

### Scope
**In Scope**:
- 4 new AI OSCE tables (patient_personas, osce_attempts, osce_scores, mock_exams)
- Extend existing `user_progress` table with 5 AI OSCE metrics
- Performance indexes for all common query patterns
- AMC-specific scoring fields (15-mark rubric, pass/fail thresholds)
- 6 REST API endpoints (personas list/get, sessions create/get/transcript/score)
- Pydantic DTOs for request/response validation
- FastAPI routers with JWT authentication
- Integration with existing auth, user_progress, and specialty taxonomy

**Out of Scope** (Future Iterations):
- Data population (360 patient personas) - Separate content creation sprint
- WebSocket implementation for real-time chat - PRD_AI_OSCE_002
- AI Patient/Examiner LLM integration - PRD_AI_OSCE_003
- Redis session state management - PRD_AI_OSCE_004
- Frontend UI components - Frontend PRDs
- Mock exam orchestration logic - PRD_AI_OSCE_005

---

## A - ARCHITECTURE (How)

### Technical Approach
Create Alembic migration script to extend PostgreSQL database with AI OSCE-specific schema while preserving existing tables. Implement REST API layer using FastAPI with Pydantic validation, JWT authentication, and integration with existing `users` and `user_progress` tables.

**Key Design Decisions**:
1. **Separate storage for personas vs. attempts**: Patient personas are reference data (reusable), attempts are session data (user-specific)
2. **JSONB for flexible data**: conversation_history, emotional_state_transitions, student_actions stored as JSONB for schema flexibility
3. **Generated columns for derived data**: age, total_score calculated automatically to ensure consistency
4. **Dual storage strategy**: Redis for active session state (8 min), PostgreSQL for permanent archive (later implementation)
5. **AMC 15-mark rubric**: Separate score fields for Communication (0-3), Clinical Reasoning (0-4), Information Gathering (0-4), Management (0-2), Professionalism (0-2)

### System Design

#### Component Diagram
```
┌──────────────────────────────────────────────────────────────────┐
│                      FRONTEND (React)                            │
│  - Persona browsing (filter by specialty/difficulty)            │
│  - OSCE session UI (8-min timer, chat interface)                │
│  - Results display (score breakdown, feedback, transcript)      │
└────────────────────┬─────────────────────────────────────────────┘
                     │ HTTPS REST API
                     ↓
┌──────────────────────────────────────────────────────────────────┐
│               FASTAPI BACKEND (Python 3.11)                      │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  API Router: /api/v1/patient-personas                   │   │
│  │  - GET /patient-personas (list with filters)            │   │
│  │  - GET /patient-personas/{persona_id}                   │   │
│  └─────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  API Router: /api/v1/osce-sessions                      │   │
│  │  - POST /osce-sessions (create session)                 │   │
│  │  - GET /osce-sessions/{attempt_id}                      │   │
│  │  - GET /osce-sessions/{attempt_id}/transcript           │   │
│  │  - GET /osce-sessions/{attempt_id}/score                │   │
│  └─────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Middleware: JWT Authentication, Rate Limiting          │   │
│  └─────────────────────────────────────────────────────────┘   │
└────────────────────┬─────────────────────────────────────────────┘
                     │ SQLAlchemy ORM
                     ↓
┌──────────────────────────────────────────────────────────────────┐
│                  POSTGRESQL 15 DATABASE                          │
│                                                                  │
│  ┌──────────────┐   ┌────────────────┐   ┌─────────────────┐   │
│  │   users      │   │ patient_       │   │ osce_attempts   │   │
│  │ (existing)   │   │ personas       │   │                 │   │
│  │              │   │                │   │ - user_id FK    │   │
│  │ - id         │←──┤ - persona_id   │←──┤ - persona_id FK │   │
│  │ - email      │   │ - persona_code │   │ - session_type  │   │
│  │ - role       │   │ - name, age    │   │ - started_at    │   │
│  └──────────────┘   │ - symptoms     │   │ - ended_at      │   │
│                     │ - emotional_   │   │ - conversation_ │   │
│  ┌──────────────┐   │   profile      │   │   history       │   │
│  │ user_        │   │ - rag_query_   │   └────────┬────────┘   │
│  │ progress     │   │   hints        │            │            │
│  │ (extended)   │   │ - difficulty   │            │ FK         │
│  │              │   │ - amc_         │            ↓            │
│  │ + ai_osces_  │   │   blueprint    │   ┌─────────────────┐   │
│  │   attempted  │   └────────────────┘   │ osce_scores     │   │
│  │ + ai_osces_  │                        │                 │   │
│  │   passed     │   ┌────────────────┐   │ - attempt_id FK │   │
│  │ + ai_osce_   │   │ mock_exams     │   │ - communication │   │
│  │   avg_score  │   │                │   │   _score (0-3)  │   │
│  │ + mock_exams_│   │ - user_id FK   │   │ - clinical_     │   │
│  │   completed  │   │ - stations_    │   │   reasoning (0-4│   │
│  │ + last_ai_   │   │   config       │   │ - total_score   │   │
│  │   osce_at    │   │ - exam_state   │   │ - pass_fail     │   │
│  └──────────────┘   │ - total_score  │   │ - feedback      │   │
│                     └────────────────┘   └─────────────────┘   │
└──────────────────────────────────────────────────────────────────┘
```

#### Data Flow: Individual Practice Mode
```
1. PERSONA SELECTION
   Student → GET /api/v1/patient-personas?specialty=cardiology&difficulty=intermediate
   Backend → Query patient_personas table
   Backend → Return list of 20 personas (filtered, paginated)

2. SESSION CREATION
   Student → POST /api/v1/osce-sessions {persona_id, session_type: "individual"}
   Backend → Create osce_attempts record (user_id, persona_id, started_at)
   Backend → Return {attempt_id, websocket_url, session_token}

3. CONVERSATION (WebSocket - future PRD)
   [8-minute interaction between Student and AI Patient via WebSocket]
   Backend → Update osce_attempts.conversation_history (JSONB array)
   Backend → Track emotional_state_transitions
   Backend → Log student_actions

4. SESSION FINALIZATION
   Timer expires (8:00) → Auto-finalize session
   Backend → UPDATE osce_attempts SET ended_at = NOW(), duration_seconds = 480

5. AI EXAMINER SCORING (future PRD)
   Backend → Load conversation_history from osce_attempts
   Backend → Call Claude 3.5 Sonnet with AMC rubric prompt
   AI Examiner → Return structured score (communication, clinical_reasoning, etc.)
   Backend → INSERT INTO osce_scores (attempt_id, scores, feedback)

6. RESULTS RETRIEVAL
   Student → GET /api/v1/osce-sessions/{attempt_id}/score
   Backend → JOIN osce_attempts + osce_scores
   Backend → Return {total_score: 14/15, pass_fail: "PASS", breakdown, feedback}

7. PROGRESS UPDATE
   Backend → Trigger update_ai_osce_progress() function
   Database → UPDATE user_progress SET ai_osces_attempted++, ai_osce_avg_score = AVG(...)
```

### Database Schema Details

#### Table 1: patient_personas
**Purpose**: Rich AI patient profiles with emotional intelligence, progressive disclosure, and RAG hints

```sql
CREATE TABLE patient_personas (
    -- Identity
    persona_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    persona_code VARCHAR(20) UNIQUE NOT NULL,  -- e.g., "CARD-001-CHEST-PAIN"

    -- Patient Demographics
    name VARCHAR(100) NOT NULL,
    age INTEGER NOT NULL CHECK (age BETWEEN 18 AND 95),
    gender VARCHAR(20) NOT NULL,
    occupation VARCHAR(100),
    cultural_background VARCHAR(100),  -- e.g., "Vietnamese Australian"
    preferred_language VARCHAR(50) DEFAULT 'English',

    -- Clinical Presentation
    specialty VARCHAR(50) NOT NULL,  -- cardiology, respiratory, emergency_medicine, etc.
    chief_complaint TEXT NOT NULL,
    opening_statement TEXT NOT NULL,  -- What patient says first (for AI Patient)

    -- Progressive Disclosure Structure
    symptoms JSONB NOT NULL,
    /*
    Example structure:
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
    Example:
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
    Example:
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

    -- RAG Integration (for AI Patient to query medical knowledge)
    rag_query_hints TEXT[],  -- Search terms: ["acute coronary syndrome", "STEMI management"]
    key_differentials TEXT[],  -- Expected DDx: ["STEMI", "unstable angina", "PE"]
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
    version INTEGER DEFAULT 1
);

CREATE INDEX idx_personas_specialty ON patient_personas(specialty) WHERE is_active = TRUE;
CREATE INDEX idx_personas_difficulty ON patient_personas(difficulty_level) WHERE is_active = TRUE;
CREATE INDEX idx_personas_active ON patient_personas(is_active) WHERE is_active = TRUE;
CREATE INDEX idx_personas_code ON patient_personas(persona_code);
```

#### Table 2: osce_attempts
**Purpose**: Tracks each student's OSCE practice session (individual or mock exam)

```sql
CREATE TABLE osce_attempts (
    -- Identity
    attempt_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Relationships
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    persona_id UUID NOT NULL REFERENCES patient_personas(persona_id) ON DELETE RESTRICT,
    mock_exam_id UUID REFERENCES mock_exams(exam_id) ON DELETE CASCADE,  -- NULL for individual practice

    -- Session Metadata
    session_type VARCHAR(20) NOT NULL CHECK (session_type IN ('individual', 'mock_exam')),
    station_number INTEGER,  -- 1-16 for mock exams, NULL for individual

    -- Timing
    started_at TIMESTAMP NOT NULL DEFAULT NOW(),
    ended_at TIMESTAMP,
    duration_seconds INTEGER,  -- Auto-calculated: EXTRACT(EPOCH FROM (ended_at - started_at))
    warning_1min_shown BOOLEAN DEFAULT FALSE,
    timer_expired BOOLEAN DEFAULT FALSE,

    -- Conversation Archive (PostgreSQL permanent storage)
    conversation_history JSONB NOT NULL DEFAULT '[]'::jsonb,
    /*
    Example structure:
    [
      {
        "timestamp": "2026-02-16T10:05:23Z",
        "speaker": "patient",
        "message": "I've been having this terrible chest pain for the past 2 hours",
        "emotional_state": "ANXIOUS_GUARDED",
        "pain_level": 8,
        "tokens_used": 45
      },
      {
        "timestamp": "2026-02-16T10:05:45Z",
        "speaker": "student",
        "message": "I understand that must be very concerning. Can you tell me more?",
        "empathy_detected": true,
        "tokens_used": 32
      }
    ]
    */

    -- Emotional State Tracking
    emotional_state_transitions JSONB DEFAULT '[]'::jsonb,
    /*
    [
      {"timestamp": "2026-02-16T10:05:23Z", "state": "ANXIOUS_GUARDED"},
      {"timestamp": "2026-02-16T10:06:12Z", "state": "CAUTIOUSLY_OPEN", "trigger": "empathy_shown"},
      {"timestamp": "2026-02-16T10:07:45Z", "state": "TRUSTING", "trigger": "clear_explanation"}
    ]
    */

    -- Student Actions Logged
    student_actions JSONB DEFAULT '[]'::jsonb,
    /*
    [
      {"timestamp": "2026-02-16T10:06:30Z", "action": "asked_pain_location", "category": "information_gathering"},
      {"timestamp": "2026-02-16T10:07:10Z", "action": "showed_empathy", "category": "communication"},
      {"timestamp": "2026-02-16T10:07:50Z", "action": "ordered_ecg", "category": "management"}
    ]
    */

    -- RAG Usage (for debugging/analytics)
    rag_queries_executed JSONB DEFAULT '[]'::jsonb,
    /*
    [
      {
        "timestamp": "2026-02-16T10:05:23Z",
        "query": "acute coronary syndrome management",
        "chunks_retrieved": 5,
        "sources": ["AMC Clinical Examination p.234", "eTG Cardiovascular"]
      }
    ]
    */

    -- Performance Metrics
    total_messages INTEGER DEFAULT 0,
    total_tokens_used INTEGER DEFAULT 0,
    llm_cost_usd DECIMAL(6,4) DEFAULT 0.0000,

    -- Session Status
    session_state VARCHAR(20) DEFAULT 'initialized' CHECK (
        session_state IN ('initialized', 'intro', 'conversation', 'warning_1min', 'finalized', 'scoring', 'complete')
    ),

    -- Audit
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    -- Constraints
    CONSTRAINT valid_completion CHECK (
        (session_state = 'complete' AND ended_at IS NOT NULL) OR
        (session_state != 'complete')
    )
);

CREATE INDEX idx_attempts_user ON osce_attempts(user_id, started_at DESC);
CREATE INDEX idx_attempts_persona ON osce_attempts(persona_id);
CREATE INDEX idx_attempts_started ON osce_attempts(started_at DESC);
CREATE INDEX idx_attempts_mock_exam ON osce_attempts(mock_exam_id) WHERE mock_exam_id IS NOT NULL;
CREATE INDEX idx_attempts_active ON osce_attempts(user_id, session_state) WHERE session_state IN ('conversation', 'warning_1min');
```

#### Table 3: osce_scores
**Purpose**: AMC 15-mark rubric scoring by AI Examiner

```sql
CREATE TABLE osce_scores (
    -- Identity
    score_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    attempt_id UUID NOT NULL UNIQUE REFERENCES osce_attempts(attempt_id) ON DELETE CASCADE,

    -- AMC 15-Mark Rubric Breakdown
    communication_score INTEGER NOT NULL CHECK (communication_score BETWEEN 0 AND 3),
    communication_feedback TEXT,
    /*
    Grading Criteria:
    0 = Poor: Minimal eye contact, interrupts patient, no rapport
    1 = Below standard: Limited empathy, some interruptions
    2 = Satisfactory: Good rapport, mostly patient-centered
    3 = Excellent: Outstanding empathy, active listening, culturally sensitive
    */

    clinical_reasoning_score INTEGER NOT NULL CHECK (clinical_reasoning_score BETWEEN 0 AND 4),
    clinical_reasoning_feedback TEXT,
    /*
    0 = No differential diagnosis formed
    1 = Incomplete/incorrect DDx
    2 = Reasonable DDx, some gaps
    3 = Comprehensive DDx, logical reasoning
    4 = Excellent DDx with clear prioritization
    */

    information_gathering_score INTEGER NOT NULL CHECK (information_gathering_score BETWEEN 0 AND 4),
    information_gathering_feedback TEXT,
    /*
    0 = Missed critical information
    1 = Incomplete history
    2 = Adequate history, minor gaps
    3 = Thorough history, systematic approach
    4 = Excellent systematic approach, no gaps
    */

    management_score INTEGER NOT NULL CHECK (management_score BETWEEN 0 AND 2),
    management_feedback TEXT,
    /*
    0 = Unsafe/inappropriate management
    1 = Partially appropriate
    2 = Safe, appropriate, evidence-based
    */

    professionalism_score INTEGER NOT NULL CHECK (professionalism_score BETWEEN 0 AND 2),
    professionalism_feedback TEXT,
    /*
    0 = Unprofessional behavior
    1 = Mostly professional
    2 = Exemplary professionalism
    */

    -- Overall Scoring (calculated fields)
    total_score INTEGER NOT NULL CHECK (total_score BETWEEN 0 AND 15),
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
        "timestamp": "2026-02-16T10:06:30Z",
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
    expert_human_score INTEGER,  -- For validation: compare AI vs human
    score_variance INTEGER,  -- ABS(ai_score - human_score)

    -- Audit
    scored_at TIMESTAMP NOT NULL DEFAULT NOW(),

    -- Constraints
    CONSTRAINT valid_total_score CHECK (
        total_score = communication_score + clinical_reasoning_score +
                      information_gathering_score + management_score + professionalism_score
    )
);

CREATE INDEX idx_scores_attempt ON osce_scores(attempt_id);
CREATE INDEX idx_scores_pass_fail ON osce_scores(pass_fail);
CREATE INDEX idx_scores_total ON osce_scores(total_score DESC);
CREATE INDEX idx_scores_golden ON osce_scores(is_golden_dataset) WHERE is_golden_dataset = TRUE;
```

#### Table 4: mock_exams
**Purpose**: Orchestrate 16-station full mock exams

```sql
CREATE TABLE mock_exams (
    exam_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,

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
    current_station INTEGER DEFAULT 1 CHECK (current_station BETWEEN 1 AND 16),
    exam_state VARCHAR(20) DEFAULT 'scheduled' CHECK (
        exam_state IN ('scheduled', 'in_progress', 'paused', 'completed', 'abandoned')
    ),

    -- Timing
    scheduled_start TIMESTAMP NOT NULL,
    actual_start TIMESTAMP,
    actual_end TIMESTAMP,
    total_duration_minutes INTEGER,  -- Should be ~150 minutes (16 stations × 8 min + breaks)

    -- Overall Performance
    total_score INTEGER,  -- Sum of all 16 station scores (max 240)
    overall_pass_fail VARCHAR(10) CHECK (overall_pass_fail IN ('PASS', 'FAIL', 'INCOMPLETE')),

    -- Audit
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_mock_exams_user ON mock_exams(user_id, exam_date DESC);
CREATE INDEX idx_mock_exams_date ON mock_exams(exam_date DESC);
CREATE INDEX idx_mock_exams_state ON mock_exams(exam_state);
```

#### Table 5: Extend Existing user_progress
**Purpose**: Add AI OSCE tracking to existing progress system

```sql
-- Add new columns to existing user_progress table
ALTER TABLE user_progress
    ADD COLUMN ai_osces_attempted INTEGER DEFAULT 0,
    ADD COLUMN ai_osces_passed INTEGER DEFAULT 0,
    ADD COLUMN ai_osce_avg_score DECIMAL(4,2),  -- Average total_score across all attempts
    ADD COLUMN mock_exams_completed INTEGER DEFAULT 0,
    ADD COLUMN last_ai_osce_at TIMESTAMP;

-- Create index for AI OSCE progress queries
CREATE INDEX idx_user_progress_ai_osce ON user_progress(user_id, ai_osces_attempted DESC);

-- Create trigger to auto-update progress when OSCE session completes
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

### API Endpoints Specification

#### Endpoint 1: List Patient Personas (GET /api/v1/patient-personas)
**Purpose**: Browse available patient scenarios with filtering

```python
# DTOs (Pydantic models)
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class PersonaListParams(BaseModel):
    specialty: Optional[str] = None  # Filter by specialty
    difficulty: Optional[str] = Field(None, regex="^(foundation|intermediate|advanced)$")
    limit: int = Field(20, ge=1, le=100)
    offset: int = Field(0, ge=0)

class PersonaSummary(BaseModel):
    persona_id: str
    persona_code: str
    name: str
    age: int
    chief_complaint: str
    specialty: str
    difficulty_level: str
    estimated_pass_rate: Optional[float]

class PersonaListResponse(BaseModel):
    total: int
    personas: List[PersonaSummary]
    offset: int
    limit: int

# FastAPI Router
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from ..dependencies import get_db, get_current_user
from ..models.user import User

router = APIRouter(prefix="/api/v1/patient-personas", tags=["AI OSCE Personas"])

@router.get("", response_model=PersonaListResponse)
async def list_patient_personas(
    specialty: Optional[str] = Query(None),
    difficulty: Optional[str] = Query(None, regex="^(foundation|intermediate|advanced)$"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # JWT authentication required
):
    """
    List available patient personas for AI OSCE practice.

    Filters:
    - specialty: cardiology, respiratory, emergency_medicine, etc.
    - difficulty: foundation, intermediate, advanced

    Returns paginated list of persona summaries.
    """
    query = db.query(PatientPersona).filter(PatientPersona.is_active == True)

    if specialty:
        query = query.filter(PatientPersona.specialty == specialty)
    if difficulty:
        query = query.filter(PatientPersona.difficulty_level == difficulty)

    total = query.count()
    personas = query.order_by(PatientPersona.specialty, PatientPersona.difficulty_level)\
                    .offset(offset).limit(limit).all()

    return PersonaListResponse(
        total=total,
        personas=[PersonaSummary.from_orm(p) for p in personas],
        offset=offset,
        limit=limit
    )
```

**Response Example**:
```json
{
  "total": 360,
  "offset": 0,
  "limit": 20,
  "personas": [
    {
      "persona_id": "550e8400-e29b-41d4-a716-446655440001",
      "persona_code": "CARD-001-CHEST-PAIN",
      "name": "Robert Chen",
      "age": 52,
      "chief_complaint": "Chest pain for 2 hours",
      "specialty": "cardiology",
      "difficulty_level": "intermediate",
      "estimated_pass_rate": 67.5
    }
  ]
}
```

#### Endpoint 2: Get Patient Persona Details (GET /api/v1/patient-personas/{persona_id})
**Purpose**: Retrieve full persona details (demographics, opening statement, difficulty)

```python
class PersonaDetail(BaseModel):
    persona_id: str
    persona_code: str
    name: str
    age: int
    gender: str
    occupation: Optional[str]
    cultural_background: Optional[str]
    chief_complaint: str
    opening_statement: str
    specialty: str
    difficulty_level: str
    estimated_pass_rate: Optional[float]
    key_differentials: List[str]
    amc_blueprint_area: Optional[str]
    amc_competencies: List[str]
    created_at: datetime

    class Config:
        orm_mode = True

@router.get("/{persona_id}", response_model=PersonaDetail)
async def get_patient_persona(
    persona_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get full details of a specific patient persona.

    Note: Does NOT return symptoms, medical_history, or emotional_profile
    (those are loaded server-side for AI Patient during session).
    """
    persona = db.query(PatientPersona).filter(
        PatientPersona.persona_id == persona_id,
        PatientPersona.is_active == True
    ).first()

    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")

    return PersonaDetail.from_orm(persona)
```

**Response Example**:
```json
{
  "persona_id": "550e8400-e29b-41d4-a716-446655440001",
  "persona_code": "CARD-001-CHEST-PAIN",
  "name": "Robert Chen",
  "age": 52,
  "gender": "Male",
  "occupation": "Accountant",
  "cultural_background": "Chinese Australian",
  "chief_complaint": "Chest pain for 2 hours",
  "opening_statement": "Doctor, I've been having this terrible chest pain...",
  "specialty": "cardiology",
  "difficulty_level": "intermediate",
  "estimated_pass_rate": 67.5,
  "key_differentials": ["STEMI", "Unstable angina", "Pulmonary embolism"],
  "amc_blueprint_area": "Cardiovascular - Acute Coronary Syndromes",
  "amc_competencies": ["Clinical reasoning", "Emergency management"],
  "created_at": "2026-02-01T10:00:00Z"
}
```

#### Endpoint 3: Create OSCE Session (POST /api/v1/osce-sessions)
**Purpose**: Initialize a new AI OSCE practice session

```python
class CreateSessionRequest(BaseModel):
    persona_id: str = Field(..., description="UUID of patient persona to practice with")
    session_type: str = Field("individual", regex="^(individual|mock_exam)$")

class CreateSessionResponse(BaseModel):
    attempt_id: str
    websocket_url: str  # For future WebSocket connection
    session_token: str  # JWT token for WebSocket auth
    expires_in: int  # Seconds until token expires (1800 = 30 min)
    persona: PersonaSummary

@router.post("", response_model=CreateSessionResponse, status_code=201)
async def create_osce_session(
    request: CreateSessionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new AI OSCE practice session.

    Steps:
    1. Validate persona exists and is active
    2. Create osce_attempts record
    3. Generate WebSocket session token
    4. Return session details for frontend to initiate WebSocket connection
    """
    # Validate persona
    persona = db.query(PatientPersona).filter(
        PatientPersona.persona_id == request.persona_id,
        PatientPersona.is_active == True
    ).first()

    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")

    # Create attempt record
    attempt = OSCEAttempt(
        user_id=current_user.user_id,
        persona_id=request.persona_id,
        session_type=request.session_type,
        started_at=datetime.utcnow(),
        session_state='initialized'
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)

    # Generate WebSocket session token (JWT)
    session_token = create_websocket_token(
        user_id=current_user.user_id,
        attempt_id=attempt.attempt_id,
        expires_delta=timedelta(minutes=30)
    )

    return CreateSessionResponse(
        attempt_id=str(attempt.attempt_id),
        websocket_url=f"wss://{settings.API_DOMAIN}/ws/osce/{attempt.attempt_id}",
        session_token=session_token,
        expires_in=1800,
        persona=PersonaSummary.from_orm(persona)
    )
```

**Request Example**:
```json
POST /api/v1/osce-sessions
{
  "persona_id": "550e8400-e29b-41d4-a716-446655440001",
  "session_type": "individual"
}
```

**Response Example**:
```json
{
  "attempt_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "websocket_url": "wss://api.example.com/ws/osce/a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "session_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 1800,
  "persona": {
    "persona_id": "550e8400-e29b-41d4-a716-446655440001",
    "persona_code": "CARD-001-CHEST-PAIN",
    "name": "Robert Chen",
    "age": 52,
    "chief_complaint": "Chest pain for 2 hours",
    "specialty": "cardiology",
    "difficulty_level": "intermediate",
    "estimated_pass_rate": 67.5
  }
}
```

#### Endpoint 4: Get OSCE Session (GET /api/v1/osce-sessions/{attempt_id})
**Purpose**: Retrieve session metadata (timing, state, message count)

```python
class SessionMetadata(BaseModel):
    attempt_id: str
    user_id: str
    persona: PersonaSummary
    session_type: str
    started_at: datetime
    ended_at: Optional[datetime]
    duration_seconds: Optional[int]
    session_state: str
    total_messages: int
    total_tokens_used: int
    llm_cost_usd: float

@router.get("/{attempt_id}", response_model=SessionMetadata)
async def get_osce_session(
    attempt_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get metadata for an OSCE session.

    Authorization: User can only access their own sessions.
    """
    attempt = db.query(OSCEAttempt).filter(
        OSCEAttempt.attempt_id == attempt_id
    ).first()

    if not attempt:
        raise HTTPException(status_code=404, detail="Session not found")

    # Authorization check
    if attempt.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this session")

    persona = db.query(PatientPersona).filter(
        PatientPersona.persona_id == attempt.persona_id
    ).first()

    return SessionMetadata(
        attempt_id=str(attempt.attempt_id),
        user_id=str(attempt.user_id),
        persona=PersonaSummary.from_orm(persona),
        session_type=attempt.session_type,
        started_at=attempt.started_at,
        ended_at=attempt.ended_at,
        duration_seconds=attempt.duration_seconds,
        session_state=attempt.session_state,
        total_messages=attempt.total_messages,
        total_tokens_used=attempt.total_tokens_used,
        llm_cost_usd=float(attempt.llm_cost_usd)
    )
```

#### Endpoint 5: Get Session Transcript (GET /api/v1/osce-sessions/{attempt_id}/transcript)
**Purpose**: Retrieve full conversation history with emotional state transitions

```python
class ConversationMessage(BaseModel):
    timestamp: datetime
    speaker: str  # "patient" or "student"
    message: str
    emotional_state: Optional[str]
    empathy_detected: Optional[bool]

class EmotionalStateTransition(BaseModel):
    timestamp: datetime
    state: str
    trigger: Optional[str]

class TranscriptResponse(BaseModel):
    attempt_id: str
    conversation: List[ConversationMessage]
    emotional_state_transitions: List[EmotionalStateTransition]

@router.get("/{attempt_id}/transcript", response_model=TranscriptResponse)
async def get_session_transcript(
    attempt_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get full conversation transcript and emotional state transitions.

    Only available for completed sessions.
    """
    attempt = db.query(OSCEAttempt).filter(
        OSCEAttempt.attempt_id == attempt_id
    ).first()

    if not attempt:
        raise HTTPException(status_code=404, detail="Session not found")

    if attempt.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    if attempt.session_state not in ['complete', 'scoring']:
        raise HTTPException(status_code=400, detail="Session not yet complete")

    return TranscriptResponse(
        attempt_id=str(attempt.attempt_id),
        conversation=[ConversationMessage(**msg) for msg in attempt.conversation_history],
        emotional_state_transitions=[EmotionalStateTransition(**t) for t in attempt.emotional_state_transitions]
    )
```

**Response Example**:
```json
{
  "attempt_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "conversation": [
    {
      "timestamp": "2026-02-16T10:05:23Z",
      "speaker": "patient",
      "message": "Doctor, I've been having this terrible chest pain for the past 2 hours.",
      "emotional_state": "ANXIOUS_GUARDED"
    },
    {
      "timestamp": "2026-02-16T10:05:45Z",
      "speaker": "student",
      "message": "I understand that must be very concerning. Can you tell me more?",
      "empathy_detected": true
    }
  ],
  "emotional_state_transitions": [
    {
      "timestamp": "2026-02-16T10:05:23Z",
      "state": "ANXIOUS_GUARDED"
    },
    {
      "timestamp": "2026-02-16T10:06:12Z",
      "state": "CAUTIOUSLY_OPEN",
      "trigger": "empathy_shown"
    }
  ]
}
```

#### Endpoint 6: Get Session Score (GET /api/v1/osce-sessions/{attempt_id}/score)
**Purpose**: Retrieve AI Examiner scoring results with detailed feedback

```python
class ScoreBreakdown(BaseModel):
    score: int
    max: int
    feedback: str

class SessionScore(BaseModel):
    score_id: str
    attempt_id: str
    total_score: int
    max_score: int = 15
    pass_fail: str
    breakdown: dict  # communication, clinical_reasoning, information_gathering, management, professionalism
    strengths: List[str]
    areas_for_improvement: List[str]
    overall_feedback: str
    critical_errors: List[dict]
    scored_at: datetime
    scoring_model: str

@router.get("/{attempt_id}/score", response_model=SessionScore)
async def get_session_score(
    attempt_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get AI Examiner scoring results for completed session.

    Only available after session is scored (session_state = 'complete').
    """
    attempt = db.query(OSCEAttempt).filter(
        OSCEAttempt.attempt_id == attempt_id
    ).first()

    if not attempt:
        raise HTTPException(status_code=404, detail="Session not found")

    if attempt.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    score = db.query(OSCEScore).filter(
        OSCEScore.attempt_id == attempt_id
    ).first()

    if not score:
        if attempt.session_state != 'complete':
            raise HTTPException(status_code=400, detail="Session not yet scored")
        else:
            raise HTTPException(status_code=404, detail="Score not found")

    return SessionScore(
        score_id=str(score.score_id),
        attempt_id=str(score.attempt_id),
        total_score=score.total_score,
        max_score=15,
        pass_fail=score.pass_fail,
        breakdown={
            "communication": {
                "score": score.communication_score,
                "max": 3,
                "feedback": score.communication_feedback
            },
            "clinical_reasoning": {
                "score": score.clinical_reasoning_score,
                "max": 4,
                "feedback": score.clinical_reasoning_feedback
            },
            "information_gathering": {
                "score": score.information_gathering_score,
                "max": 4,
                "feedback": score.information_gathering_feedback
            },
            "management": {
                "score": score.management_score,
                "max": 2,
                "feedback": score.management_feedback
            },
            "professionalism": {
                "score": score.professionalism_score,
                "max": 2,
                "feedback": score.professionalism_feedback
            }
        },
        strengths=score.strengths,
        areas_for_improvement=score.areas_for_improvement,
        overall_feedback=score.overall_feedback,
        critical_errors=score.critical_errors,
        scored_at=score.scored_at,
        scoring_model=score.scoring_model
    )
```

**Response Example**:
```json
{
  "score_id": "f1e2d3c4-b5a6-7890-1234-567890abcdef",
  "attempt_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "total_score": 14,
  "max_score": 15,
  "pass_fail": "PASS",
  "breakdown": {
    "communication": {
      "score": 3,
      "max": 3,
      "feedback": "Excellent empathy shown throughout. Used open questions..."
    },
    "clinical_reasoning": {
      "score": 4,
      "max": 4,
      "feedback": "Comprehensive differential diagnosis formed..."
    },
    "information_gathering": {
      "score": 3,
      "max": 4,
      "feedback": "Systematic history taking. Minor gap: didn't ask about previous episodes"
    },
    "management": {
      "score": 2,
      "max": 2,
      "feedback": "Appropriate immediate management. Ordered ECG correctly..."
    },
    "professionalism": {
      "score": 2,
      "max": 2,
      "feedback": "Professional throughout. Explained clearly..."
    }
  },
  "strengths": [
    "Excellent empathy and communication skills",
    "Systematic approach to history taking",
    "Identified red flags early"
  ],
  "areas_for_improvement": [
    "Could explore previous similar episodes",
    "Could explain ECG findings to patient"
  ],
  "overall_feedback": "Strong performance. Demonstrated excellent communication and clinical reasoning...",
  "critical_errors": [],
  "scored_at": "2026-02-16T10:14:30Z",
  "scoring_model": "claude-3.5-sonnet-20250219"
}
```

### Technology Stack
- **Database**: PostgreSQL 15 (existing instance)
- **Migration Tool**: Alembic 1.13+
- **ORM**: SQLAlchemy 2.0+
- **API Framework**: FastAPI 0.109+
- **Validation**: Pydantic 2.6+
- **Authentication**: JWT (existing auth system)
- **Python**: 3.11+
- **Testing**: pytest, httpx

### Integration Points
- **Integrates with**: Existing `users` table (JWT auth), existing `user_progress` table
- **Consumed by**: Frontend React components, future WebSocket handlers
- **Depends on**: Existing database infrastructure, existing auth middleware
- **Future Integration**: Redis (session state), Qdrant (RAG), Claude 3.5 Sonnet (AI Patient/Examiner)

### Security Considerations
- [x] JWT authentication required for all endpoints
- [x] User authorization check (users can only access their own sessions)
- [x] Input validation via Pydantic schemas
- [x] Foreign key constraints prevent orphaned records
- [x] ON DELETE CASCADE for user data (GDPR compliance)
- [x] ON DELETE RESTRICT for reference data (patient personas)
- [x] No sensitive data exposed (symptoms, medical_history kept server-side)
- [x] Rate limiting (via existing middleware)

### Performance Requirements
- **Migration Time**: <5 minutes (CONCURRENTLY for indexes)
- **API Response Times**:
  - GET /patient-personas: <200ms (p95)
  - POST /osce-sessions: <500ms (p95)
  - GET /osce-sessions/{id}/score: <300ms (p95)
- **Database Query Times**:
  - Active sessions: <50ms
  - Persona retrieval: <100ms
  - Score retrieval with JOINs: <150ms
- **Concurrent Users**: 100+ supported

---

## L - LOOP (Iterative Development)

### Phase 1: Database Foundation (35% of effort, 6-7 hours)
**Goal**: Create production-ready Alembic migration with all tables and indexes

**Tasks**:
1. Create Alembic revision file - 30 min
2. Write CREATE TABLE for patient_personas - 1.5 hours (large JSONB schema)
3. Write CREATE TABLE for osce_attempts - 1 hour
4. Write CREATE TABLE for osce_scores - 1 hour
5. Write CREATE TABLE for mock_exams - 45 min
6. Write ALTER TABLE user_progress + trigger function - 1 hour
7. Write CREATE INDEX CONCURRENTLY statements (15+ indexes) - 1 hour
8. Write rollback/downgrade script - 45 min

**Validation Gate**:
- [ ] Alembic revision file created (`alembic/versions/20260216_XXXX_add_ai_osce_schema.py`)
- [ ] All 4 tables defined with correct columns, types, constraints
- [ ] 5 columns added to user_progress
- [ ] Trigger function `update_ai_osce_progress()` created
- [ ] All indexes created with CONCURRENTLY flag
- [ ] Downgrade script written and tested
- [ ] No syntax errors (`python -m py_compile`)
- [ ] Migration tested in isolated test database

---

### Phase 2: API Implementation (40% of effort, 7-8 hours)
**Goal**: Implement 6 REST API endpoints with Pydantic validation

**Tasks**:
1. Create Pydantic DTOs (10+ models) - 1.5 hours
2. Implement GET /patient-personas (list with filters) - 1 hour
3. Implement GET /patient-personas/{persona_id} - 45 min
4. Implement POST /osce-sessions (create session) - 1.5 hours (includes JWT token generation)
5. Implement GET /osce-sessions/{attempt_id} - 45 min
6. Implement GET /osce-sessions/{attempt_id}/transcript - 1 hour
7. Implement GET /osce-sessions/{attempt_id}/score - 1 hour
8. Add JWT authentication decorators - 30 min
9. Add authorization checks (user can only access own sessions) - 30 min

**Validation Gate**:
- [ ] All 6 API endpoints implemented
- [ ] Pydantic schemas validate input/output
- [ ] JWT authentication working on all endpoints
- [ ] Authorization checks prevent cross-user access
- [ ] FastAPI OpenAPI docs auto-generated
- [ ] Unit tests for DTOs (valid/invalid inputs)
- [ ] Integration tests for each endpoint

---

### Phase 3: Testing & Documentation (25% of effort, 4-5 hours)
**Goal**: Production-ready quality with comprehensive tests and docs

**Tasks**:
1. Write unit tests for database models - 1 hour
2. Write integration tests for API endpoints - 2 hours
3. Test migration (upgrade + downgrade) - 30 min
4. Performance testing (EXPLAIN ANALYZE queries) - 1 hour
5. Write API documentation - 1 hour
6. Write database schema documentation - 30 min

**Validation Gate**:
- [ ] Test coverage ≥80% (unit + integration)
- [ ] 100% test pass rate
- [ ] Performance benchmarks met (<200ms API responses)
- [ ] Migration rollback tested successfully
- [ ] OpenAPI documentation complete
- [ ] README with setup instructions
- [ ] ER diagram generated

---

## P - PLAN (Detailed Implementation)

### Phase 1 Tasks (Database Foundation)

**Task 1.1**: Create Alembic Revision
- **Effort**: 30 min
- **Owner**: Backend Engineer
- **Deliverable**: `alembic/versions/20260216_XXXX_add_ai_osce_schema.py`
- **Dependencies**: None
- **Command**:
  ```bash
  cd /home/dev/Development/irStudy/backend
  source venv/bin/activate
  alembic revision -m "add_ai_osce_schema_4_tables_and_user_progress_extension"
  ```
- **Acceptance Criteria**:
  - [ ] Revision file created
  - [ ] File has upgrade() and downgrade() functions
  - [ ] Revision ID generated

**Task 1.2**: Write CREATE TABLE for patient_personas
- **Effort**: 1.5 hours (complex JSONB schema)
- **Owner**: Backend Engineer
- **Deliverable**: Complete patient_personas table definition
- **Dependencies**: Task 1.1
- **Acceptance Criteria**:
  - [ ] All columns defined (persona_id, persona_code, name, age, gender, etc.)
  - [ ] JSONB columns: symptoms, medical_history, emotional_profile
  - [ ] ARRAY columns: rag_query_hints, key_differentials, critical_actions, amc_competencies
  - [ ] CHECK constraint for age BETWEEN 18 AND 95
  - [ ] CHECK constraint for difficulty_level IN ('foundation', 'intermediate', 'advanced')
  - [ ] Foreign keys to users (created_by, validated_by)
  - [ ] UNIQUE constraint on persona_code
  - [ ] Timestamps (created_at, validated_at)

**Task 1.3**: Write CREATE TABLE for osce_attempts
- **Effort**: 1 hour
- **Owner**: Backend Engineer
- **Deliverable**: Complete osce_attempts table
- **Dependencies**: Task 1.1
- **Acceptance Criteria**:
  - [ ] Foreign keys to users, patient_personas, mock_exams
  - [ ] ON DELETE CASCADE for users (GDPR)
  - [ ] ON DELETE RESTRICT for patient_personas (preserve reference data)
  - [ ] CHECK constraint for session_type IN ('individual', 'mock_exam')
  - [ ] CHECK constraint for session_state (7 valid states)
  - [ ] JSONB columns: conversation_history, emotional_state_transitions, student_actions, rag_queries_executed
  - [ ] Duration calculated field
  - [ ] Timestamps (started_at, ended_at, created_at, updated_at)
  - [ ] CHECK constraint for valid_completion

**Task 1.4**: Write CREATE TABLE for osce_scores
- **Effort**: 1 hour
- **Owner**: Backend Engineer
- **Deliverable**: Complete osce_scores table with AMC rubric
- **Dependencies**: Task 1.1
- **Acceptance Criteria**:
  - [ ] Foreign key to osce_attempts (UNIQUE to enforce one score per attempt)
  - [ ] 5 score fields with CHECK constraints (communication 0-3, clinical_reasoning 0-4, etc.)
  - [ ] 5 feedback fields (TEXT)
  - [ ] CHECK constraint for total_score BETWEEN 0 AND 15
  - [ ] CHECK constraint for pass_fail IN ('PASS', 'FAIL', 'BORDERLINE')
  - [ ] CHECK constraint to validate total_score = sum of component scores
  - [ ] ARRAY columns: strengths, areas_for_improvement
  - [ ] JSONB column: critical_errors
  - [ ] Golden dataset fields (is_golden_dataset, expert_human_score, score_variance)

**Task 1.5**: Write CREATE TABLE for mock_exams
- **Effort**: 45 min
- **Owner**: Backend Engineer
- **Deliverable**: Complete mock_exams table
- **Dependencies**: Task 1.1
- **Acceptance Criteria**:
  - [ ] Foreign key to users (ON DELETE CASCADE)
  - [ ] JSONB column: stations_config (16 stations)
  - [ ] CHECK constraint for current_station BETWEEN 1 AND 16
  - [ ] CHECK constraint for exam_state (5 valid states)
  - [ ] CHECK constraint for overall_pass_fail IN ('PASS', 'FAIL', 'INCOMPLETE')
  - [ ] Timing fields (scheduled_start, actual_start, actual_end, total_duration_minutes)
  - [ ] Timestamps (created_at, updated_at)

**Task 1.6**: Write ALTER TABLE user_progress + Trigger
- **Effort**: 1 hour
- **Owner**: Backend Engineer
- **Deliverable**: 5 new columns + auto-update trigger
- **Dependencies**: Task 1.1, Task 1.3
- **Acceptance Criteria**:
  - [ ] 5 columns added: ai_osces_attempted, ai_osces_passed, ai_osce_avg_score, mock_exams_completed, last_ai_osce_at
  - [ ] Trigger function `update_ai_osce_progress()` created
  - [ ] Trigger fires AFTER UPDATE OF ended_at ON osce_attempts
  - [ ] Trigger increments ai_osces_attempted
  - [ ] Trigger increments ai_osces_passed IF pass_fail = 'PASS'
  - [ ] Trigger calculates ai_osce_avg_score from all user's scores
  - [ ] Trigger updates last_ai_osce_at timestamp

**Task 1.7**: Write CREATE INDEX Statements
- **Effort**: 1 hour
- **Owner**: Backend Engineer
- **Deliverable**: 15+ indexes created
- **Dependencies**: Tasks 1.2-1.5
- **Acceptance Criteria**:
  - [ ] All indexes use CREATE INDEX CONCURRENTLY (production-safe)
  - [ ] patient_personas: idx_specialty, idx_difficulty, idx_active, idx_code
  - [ ] osce_attempts: idx_user, idx_persona, idx_started, idx_mock_exam, idx_active
  - [ ] osce_scores: idx_attempt, idx_pass_fail, idx_total, idx_golden
  - [ ] mock_exams: idx_user, idx_date, idx_state
  - [ ] user_progress: idx_user_progress_ai_osce

**Task 1.8**: Write Rollback/Downgrade Script
- **Effort**: 45 min
- **Owner**: Backend Engineer
- **Deliverable**: Complete downgrade() function
- **Dependencies**: Tasks 1.2-1.7
- **Acceptance Criteria**:
  - [ ] DROP INDEX IF EXISTS for all indexes (reverse order)
  - [ ] DROP TRIGGER IF EXISTS trigger_update_ai_osce_progress
  - [ ] DROP FUNCTION IF EXISTS update_ai_osce_progress()
  - [ ] ALTER TABLE user_progress DROP COLUMN for all 5 columns
  - [ ] DROP TABLE IF EXISTS for all 4 tables (reverse dependency order: mock_exams, osce_scores, osce_attempts, patient_personas)
  - [ ] Downgrade tested in separate test database

---

### Phase 2 Tasks (API Implementation)

**Task 2.1**: Create Pydantic DTOs
- **Effort**: 1.5 hours
- **Owner**: Backend Engineer
- **Deliverable**: 10+ Pydantic models in `backend/src/schemas/ai_osce.py`
- **Dependencies**: None (can run parallel to Phase 1)
- **Acceptance Criteria**:
  - [ ] PersonaListParams, PersonaSummary, PersonaListResponse
  - [ ] PersonaDetail
  - [ ] CreateSessionRequest, CreateSessionResponse
  - [ ] SessionMetadata
  - [ ] ConversationMessage, EmotionalStateTransition, TranscriptResponse
  - [ ] ScoreBreakdown, SessionScore
  - [ ] All schemas have proper types, Field validators, regex patterns
  - [ ] All schemas have orm_mode = True for ORM mapping

**Task 2.2**: Implement GET /patient-personas
- **Effort**: 1 hour
- **Owner**: Backend Engineer
- **Deliverable**: Router endpoint in `backend/src/api/v1/ai_osce_personas.py`
- **Dependencies**: Task 2.1, Database migration complete
- **Acceptance Criteria**:
  - [ ] Endpoint accepts query params: specialty, difficulty, limit, offset
  - [ ] Query filters by is_active = TRUE
  - [ ] Results paginated (default limit 20, max 100)
  - [ ] Returns total count + personas array
  - [ ] JWT authentication required
  - [ ] OpenAPI docs auto-generated

**Task 2.3**: Implement GET /patient-personas/{persona_id}
- **Effort**: 45 min
- **Owner**: Backend Engineer
- **Deliverable**: Router endpoint
- **Dependencies**: Task 2.1, Task 2.2
- **Acceptance Criteria**:
  - [ ] Returns full persona details (excluding sensitive fields)
  - [ ] 404 if persona not found or not active
  - [ ] JWT authentication required
  - [ ] OpenAPI docs auto-generated

**Task 2.4**: Implement POST /osce-sessions
- **Effort**: 1.5 hours (includes JWT token generation)
- **Owner**: Backend Engineer
- **Deliverable**: Router endpoint in `backend/src/api/v1/ai_osce_sessions.py`
- **Dependencies**: Task 2.1, Database migration complete
- **Acceptance Criteria**:
  - [ ] Validates persona exists and is active
  - [ ] Creates osce_attempts record
  - [ ] Generates WebSocket JWT token (30-min expiry)
  - [ ] Returns attempt_id, websocket_url, session_token, persona
  - [ ] 201 Created status code
  - [ ] 404 if persona not found
  - [ ] JWT authentication required

**Task 2.5**: Implement GET /osce-sessions/{attempt_id}
- **Effort**: 45 min
- **Owner**: Backend Engineer
- **Deliverable**: Router endpoint
- **Dependencies**: Task 2.1, Task 2.4
- **Acceptance Criteria**:
  - [ ] Returns session metadata (timing, state, message count)
  - [ ] Authorization check: user can only access own sessions
  - [ ] 404 if session not found
  - [ ] 403 if unauthorized
  - [ ] JWT authentication required

**Task 2.6**: Implement GET /osce-sessions/{attempt_id}/transcript
- **Effort**: 1 hour
- **Owner**: Backend Engineer
- **Deliverable**: Router endpoint
- **Dependencies**: Task 2.1, Task 2.4
- **Acceptance Criteria**:
  - [ ] Returns conversation_history array
  - [ ] Returns emotional_state_transitions array
  - [ ] Only available for completed sessions (session_state = 'complete')
  - [ ] Authorization check: user can only access own sessions
  - [ ] 400 if session not complete
  - [ ] JWT authentication required

**Task 2.7**: Implement GET /osce-sessions/{attempt_id}/score
- **Effort**: 1 hour
- **Owner**: Backend Engineer
- **Deliverable**: Router endpoint
- **Dependencies**: Task 2.1, Task 2.4
- **Acceptance Criteria**:
  - [ ] Joins osce_attempts + osce_scores
  - [ ] Returns total_score, pass_fail, breakdown (5 domains), strengths, areas_for_improvement, overall_feedback
  - [ ] 404 if score not found (not yet scored)
  - [ ] Authorization check: user can only access own sessions
  - [ ] JWT authentication required

**Task 2.8**: Add JWT Authentication Decorators
- **Effort**: 30 min
- **Owner**: Backend Engineer
- **Deliverable**: All endpoints protected by `Depends(get_current_user)`
- **Dependencies**: Tasks 2.2-2.7
- **Acceptance Criteria**:
  - [ ] All endpoints require valid JWT token
  - [ ] 401 if token missing or invalid
  - [ ] get_current_user dependency retrieves user from token

**Task 2.9**: Add Authorization Checks
- **Effort**: 30 min
- **Owner**: Backend Engineer
- **Deliverable**: User authorization logic
- **Dependencies**: Tasks 2.5-2.7
- **Acceptance Criteria**:
  - [ ] GET /osce-sessions/{id} checks attempt.user_id == current_user.user_id
  - [ ] GET /osce-sessions/{id}/transcript checks ownership
  - [ ] GET /osce-sessions/{id}/score checks ownership
  - [ ] 403 Forbidden if unauthorized

---

### Phase 3 Tasks (Testing & Documentation)

**Task 3.1**: Write Unit Tests for Database Models
- **Effort**: 1 hour
- **Owner**: Backend Engineer / Testing QA
- **Deliverable**: `backend/tests/test_models/test_ai_osce_models.py`
- **Dependencies**: Phase 1 complete
- **Test Cases**:
  - [ ] Test PatientPersona model creation with valid JSONB
  - [ ] Test CHECK constraints (age 18-95, difficulty enum)
  - [ ] Test OSCEAttempt model with foreign keys
  - [ ] Test OSCEScore CHECK constraints (score ranges, total_score validation)
  - [ ] Test trigger function (update_ai_osce_progress)
  - [ ] Test CASCADE delete (delete user → delete attempts)
  - [ ] Test RESTRICT delete (cannot delete persona if attempts exist)

**Task 3.2**: Write Integration Tests for API Endpoints
- **Effort**: 2 hours
- **Owner**: Backend Engineer / Testing QA
- **Deliverable**: `backend/tests/test_api/test_ai_osce_api.py`
- **Dependencies**: Phase 2 complete
- **Test Cases**:
  - [ ] Test GET /patient-personas (200, pagination, filters)
  - [ ] Test GET /patient-personas/{id} (200 found, 404 not found)
  - [ ] Test POST /osce-sessions (201 created, 404 invalid persona)
  - [ ] Test GET /osce-sessions/{id} (200 authorized, 403 unauthorized)
  - [ ] Test GET /osce-sessions/{id}/transcript (200, 400 not complete)
  - [ ] Test GET /osce-sessions/{id}/score (200, 404 not scored)
  - [ ] Test JWT authentication (401 if missing token)

**Task 3.3**: Test Migration (Upgrade + Downgrade)
- **Effort**: 30 min
- **Owner**: Backend Engineer
- **Deliverable**: Migration validated in test database
- **Dependencies**: Phase 1 complete
- **Test Procedure**:
  ```bash
  # Upgrade
  alembic upgrade head
  # Verify 4 tables created
  psql -c "\dt patient_personas osce_attempts osce_scores mock_exams"
  # Verify 5 columns in user_progress
  psql -c "\d user_progress" | grep ai_osce
  # Downgrade
  alembic downgrade -1
  # Verify tables dropped
  psql -c "\dt patient_personas"  # Should return empty
  # Re-upgrade (idempotency)
  alembic upgrade head
  ```
- **Acceptance Criteria**:
  - [ ] Upgrade creates all tables, columns, indexes, triggers
  - [ ] Downgrade removes all AI OSCE schema
  - [ ] Re-upgrade works (idempotent)

**Task 3.4**: Performance Testing (EXPLAIN ANALYZE)
- **Effort**: 1 hour
- **Owner**: Backend Engineer
- **Deliverable**: Performance benchmarks documented
- **Dependencies**: Phase 1 complete, test data loaded
- **Test Queries**:
  ```sql
  -- Query 1: List personas by specialty (should use idx_personas_specialty)
  EXPLAIN ANALYZE
  SELECT * FROM patient_personas
  WHERE specialty = 'cardiology' AND is_active = TRUE
  LIMIT 20;
  -- Target: Index Scan, <100ms

  -- Query 2: Get user's active sessions (should use idx_attempts_active)
  EXPLAIN ANALYZE
  SELECT * FROM osce_attempts
  WHERE user_id = '...' AND session_state IN ('conversation', 'warning_1min');
  -- Target: Index Scan, <50ms

  -- Query 3: Get session with score (JOIN)
  EXPLAIN ANALYZE
  SELECT a.*, s.*
  FROM osce_attempts a
  LEFT JOIN osce_scores s ON a.attempt_id = s.attempt_id
  WHERE a.attempt_id = '...';
  -- Target: Index Scan + Nested Loop, <150ms
  ```
- **Acceptance Criteria**:
  - [ ] All queries use Index Scan (not Seq Scan)
  - [ ] Performance targets met (<100ms for persona queries, <50ms for active sessions)

**Task 3.5**: Write API Documentation
- **Effort**: 1 hour
- **Owner**: Backend Engineer
- **Deliverable**: `backend/docs/AI_OSCE_API.md`
- **Contents**:
  - Overview of AI OSCE API
  - Authentication (JWT required)
  - Endpoint reference (6 endpoints with request/response examples)
  - Error codes and handling
  - Rate limiting
- **Acceptance Criteria**:
  - [ ] All endpoints documented
  - [ ] Request/response examples provided
  - [ ] Error scenarios documented
  - [ ] OpenAPI spec auto-generated by FastAPI

**Task 3.6**: Write Database Schema Documentation
- **Effort**: 30 min
- **Owner**: Backend Engineer
- **Deliverable**: `backend/docs/AI_OSCE_DATABASE_SCHEMA.md`
- **Contents**:
  - ER diagram
  - Table descriptions (purpose, key columns, relationships)
  - Index explanations
  - Trigger documentation
  - Query examples
- **Acceptance Criteria**:
  - [ ] All 4 tables documented
  - [ ] Relationships explained
  - [ ] JSONB schema examples provided
  - [ ] ER diagram generated (dbdiagram.io or similar)

---

### Dependency Graph
```
Task 1.1 (Create Alembic revision)
    ↓
┌───┴───┬────────┬───────┬───────┐
│       │        │       │       │
1.2     1.3      1.4     1.5     1.6 (CREATE TABLE statements + ALTER TABLE)
│       │        │       │       │
└───┬───┴────────┴───────┴───────┘
    ↓
Task 1.7 (CREATE INDEX)
    ↓
Task 1.8 (Rollback script)
    ↓
Phase 1 COMPLETE → Run migration
    ↓
┌───┴───────────────────┐
│                       │
Task 2.1 (DTOs)         Task 3.1 (Unit tests)
    ↓                       ↓
Tasks 2.2-2.9 (API)     Task 3.2 (Integration tests)
    ↓                       ↓
Phase 2 COMPLETE        Task 3.3 (Migration test)
    ↓                       ↓
    └───────┬───────────────┘
            ↓
    Tasks 3.4-3.6 (Performance + Docs)
            ↓
    Phase 3 COMPLETE
```

---

### Timeline (Example)

| Day | Phase | Tasks | Hours | Deliverable |
|-----|-------|-------|-------|-------------|
| Day 1 AM | Phase 1 | 1.1-1.4 | 4h | First 3 tables + revision |
| Day 1 PM | Phase 1 | 1.5-1.8 | 4h | Last table, indexes, rollback |
| Day 2 AM | Phase 2 | 2.1-2.3 | 3h | DTOs + persona endpoints |
| Day 2 PM | Phase 2 | 2.4-2.5 | 2.5h | Session create/get endpoints |
| Day 3 AM | Phase 2 | 2.6-2.9 | 3h | Transcript/score + auth |
| Day 3 PM | Phase 3 | 3.1-3.2 | 3h | Unit + integration tests |
| Day 4 AM | Phase 3 | 3.3-3.4 | 1.5h | Migration test + performance |
| Day 4 PM | Phase 3 | 3.5-3.6 | 1.5h | Documentation |

**Total**: 3-4 days, 16-20 hours effort

---

## H - HANDOFF (Delivery & Validation)

### Acceptance Criteria (MUST ALL PASS)

#### Functional Requirements
- [ ] 4 AI OSCE tables created (patient_personas, osce_attempts, osce_scores, mock_exams)
- [ ] 5 columns added to user_progress (ai_osces_attempted, ai_osces_passed, ai_osce_avg_score, mock_exams_completed, last_ai_osce_at)
- [ ] Trigger function auto-updates user_progress when session completes
- [ ] All foreign key relationships functional (CASCADE and RESTRICT work correctly)
- [ ] All CHECK constraints enforced (age ranges, score ranges, enums)
- [ ] JSONB columns accept valid JSON structures
- [ ] ARRAY columns accept arrays
- [ ] 6 API endpoints functional (personas list/get, sessions create/get/transcript/score)
- [ ] JWT authentication working on all endpoints
- [ ] Authorization checks prevent cross-user access

#### Quality Requirements
- [ ] **Test Coverage**: ≥80% (unit + integration)
- [ ] **Test Pass Rate**: 100% (zero tolerance)
- [ ] **Code Quality**: No linting errors, follows FastAPI best practices
- [ ] **Documentation**: API docs complete, database schema documented
- [ ] **Migration Success**: Alembic upgrade executes with 0 errors
- [ ] **Rollback Safety**: Alembic downgrade works without data loss

#### Performance Requirements
- [ ] **Migration Time**: <5 minutes total
- [ ] **API Response Times**:
  - GET /patient-personas: <200ms (p95)
  - POST /osce-sessions: <500ms (p95)
  - GET /osce-sessions/{id}/score: <300ms (p95)
- [ ] **Database Query Times**:
  - Active sessions: <50ms
  - Persona retrieval: <100ms
  - Score retrieval with JOIN: <150ms
- [ ] **Index Usage**: All queries use Index Scan (verified with EXPLAIN ANALYZE)

#### Security Requirements
- [ ] **No Hardcoded Credentials**: Database password from environment variable
- [ ] **JWT Authentication**: All endpoints require valid token
- [ ] **Authorization**: Users can only access their own sessions (403 if unauthorized)
- [ ] **Input Validation**: Pydantic schemas validate all inputs
- [ ] **GDPR Compliance**: ON DELETE CASCADE for user data

#### Australian Medical Compliance
- [ ] **AMC 15-Mark Rubric**: Scoring follows official AMC breakdown (Communication 0-3, Clinical Reasoning 0-4, etc.)
- [ ] **Pass/Fail Thresholds**: PASS = ≥9/15, BORDERLINE = 8/15, FAIL = ≤7/15
- [ ] **AMC Blueprint Areas**: patient_personas references AMC curriculum areas
- [ ] **Australian Context**: Cultural background, preferred language fields for personas

---

### Testing Requirements

#### Unit Tests (≥80% coverage target)
```python
# backend/tests/test_models/test_ai_osce_models.py

def test_patient_persona_creation():
    """Test valid persona creation with JSONB fields"""
    persona = PatientPersona(
        persona_code="CARD-001",
        name="Test Patient",
        age=52,
        gender="Male",
        specialty="cardiology",
        chief_complaint="Chest pain",
        opening_statement="I have chest pain",
        symptoms={"immediate": ["chest pain"]},
        medical_history={"volunteer": ["diabetes"]},
        emotional_profile={"baseline_state": "ANXIOUS_GUARDED"},
        rag_query_hints=["acute coronary syndrome"],
        key_differentials=["STEMI", "Unstable angina"],
        critical_actions=["ECG within 10 minutes"],
        difficulty_level="intermediate"
    )
    db.add(persona)
    db.commit()
    assert persona.persona_id is not None
    assert persona.age == 52

def test_osce_score_total_validation():
    """Test CHECK constraint for total_score = sum of components"""
    # This should FAIL (total_score != sum)
    with pytest.raises(IntegrityError):
        score = OSCEScore(
            attempt_id="...",
            communication_score=3,
            clinical_reasoning_score=4,
            information_gathering_score=3,
            management_score=2,
            professionalism_score=2,
            total_score=10,  # INVALID: should be 14
            pass_fail="PASS"
        )
        db.add(score)
        db.commit()

def test_user_progress_trigger():
    """Test auto-update trigger when session completes"""
    # Create user, persona, attempt
    user = User(email="test@example.com")
    persona = PatientPersona(...valid data...)
    attempt = OSCEAttempt(user_id=user.user_id, persona_id=persona.persona_id)
    db.add_all([user, persona, attempt])
    db.commit()

    # Complete session
    attempt.ended_at = datetime.utcnow()
    db.commit()

    # Create score
    score = OSCEScore(
        attempt_id=attempt.attempt_id,
        communication_score=3,
        clinical_reasoning_score=4,
        information_gathering_score=3,
        management_score=2,
        professionalism_score=2,
        total_score=14,
        pass_fail="PASS"
    )
    db.add(score)
    db.commit()

    # Trigger should update user_progress
    progress = db.query(UserProgress).filter_by(user_id=user.user_id).first()
    assert progress.ai_osces_attempted == 1
    assert progress.ai_osces_passed == 1
    assert progress.ai_osce_avg_score == 14.0
```

#### Integration Tests (API Endpoints)
```python
# backend/tests/test_api/test_ai_osce_api.py

def test_list_personas_success(client, auth_headers):
    """Test GET /patient-personas with filters"""
    response = client.get(
        "/api/v1/patient-personas?specialty=cardiology&difficulty=intermediate&limit=10",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "personas" in data
    assert "total" in data
    assert data["limit"] == 10

def test_create_session_success(client, auth_headers, test_persona):
    """Test POST /osce-sessions"""
    response = client.post(
        "/api/v1/osce-sessions",
        json={"persona_id": str(test_persona.persona_id), "session_type": "individual"},
        headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert "attempt_id" in data
    assert "websocket_url" in data
    assert "session_token" in data
    assert data["expires_in"] == 1800

def test_get_session_unauthorized(client, auth_headers, other_user_session):
    """Test GET /osce-sessions/{id} with unauthorized access"""
    response = client.get(
        f"/api/v1/osce-sessions/{other_user_session.attempt_id}",
        headers=auth_headers
    )
    assert response.status_code == 403
    assert "Not authorized" in response.json()["detail"]

def test_get_score_not_yet_scored(client, auth_headers, incomplete_session):
    """Test GET /osce-sessions/{id}/score before scoring"""
    response = client.get(
        f"/api/v1/osce-sessions/{incomplete_session.attempt_id}/score",
        headers=auth_headers
    )
    assert response.status_code == 400
    assert "not yet scored" in response.json()["detail"]
```

#### E2E Tests (Playwright - future)
- [ ] User flow: Browse personas → Start session → View results
- [ ] User flow: Complete session → View transcript → View score breakdown

---

### Documentation Deliverables

#### 1. API Documentation (`backend/docs/AI_OSCE_API.md`)
```markdown
# AI OSCE API Documentation

## Overview
REST API for AI Patient/Examiner OSCE simulation system.

## Authentication
All endpoints require JWT token in Authorization header:
```
Authorization: Bearer <token>
```

## Endpoints

### GET /api/v1/patient-personas
List available patient scenarios with optional filters.

**Query Parameters**:
- `specialty` (optional): Filter by specialty (e.g., "cardiology")
- `difficulty` (optional): Filter by difficulty ("foundation", "intermediate", "advanced")
- `limit` (optional): Results per page (default 20, max 100)
- `offset` (optional): Pagination offset (default 0)

**Response** (200 OK):
```json
{
  "total": 360,
  "personas": [...],
  "offset": 0,
  "limit": 20
}
```

[Continue for all 6 endpoints...]
```

#### 2. Database Schema Documentation (`backend/docs/AI_OSCE_DATABASE_SCHEMA.md`)
- ER diagram (visual representation)
- Table descriptions (purpose, columns, relationships)
- JSONB schema examples
- Index explanations
- Trigger documentation

#### 3. Migration Guide (`backend/docs/AI_OSCE_MIGRATION_GUIDE.md`)
- Pre-migration checklist
- Migration steps (backup → upgrade → verify)
- Rollback procedure
- Post-migration validation

---

### Deployment Checklist

#### Pre-Deployment
- [ ] All acceptance criteria met
- [ ] All tests passing (100% pass rate)
- [ ] Migration tested in development
- [ ] Rollback script tested
- [ ] Documentation complete
- [ ] Code review approved
- [ ] Security audit complete

#### Deployment (Development)
- [ ] Backup database (`pg_dump`)
- [ ] Run `alembic upgrade head`
- [ ] Verify tables created (4 tables)
- [ ] Verify columns added to user_progress (5 columns)
- [ ] Verify indexes created (15+)
- [ ] Verify trigger created
- [ ] Run smoke tests (API endpoints respond)
- [ ] Check logs for errors

#### Post-Deployment
- [ ] Performance metrics within targets (<200ms API responses)
- [ ] Database queries use indexes (EXPLAIN ANALYZE)
- [ ] Foreign keys functional
- [ ] Trigger auto-updates user_progress
- [ ] Documentation updated in repository
- [ ] Team notified of new API endpoints

---

### Success Validation

**This PRD is considered COMPLETE when**:
1. ✅ 4 AI OSCE tables created and verified
2. ✅ 5 columns added to user_progress with auto-update trigger
3. ✅ All indexes created with CONCURRENTLY
4. ✅ 6 API endpoints implemented and functional
5. ✅ JWT authentication working on all endpoints
6. ✅ Authorization checks prevent cross-user access
7. ✅ Test coverage ≥80%, 100% pass rate
8. ✅ Performance targets met (<200ms API, <50ms DB queries)
9. ✅ Rollback script tested and functional
10. ✅ Documentation complete (API docs, schema docs, migration guide)
11. ✅ Migration executes in <5 minutes
12. ✅ Zero data loss or integrity violations

**Sign-off Required From**:
- [ ] Backend Engineer (implementation complete, tests passing)
- [ ] PM Coordinator (requirements met, quality validated)
- [ ] Security Expert (JWT auth OK, authorization checks OK, no hardcoded credentials)
- [ ] Testing QA (test coverage ≥80%, 100% pass rate, performance benchmarks met)

---

## 📎 Appendices

### Appendix A: Sample Patient Persona (Full JSONB Structure)
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

### Appendix B: Alembic Migration Skeleton
```python
"""add_ai_osce_schema_4_tables_and_user_progress_extension

Revision ID: 20260216_XXXX
Revises: [previous_revision]
Create Date: 2026-02-16 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY

# revision identifiers, used by Alembic.
revision = '20260216_XXXX'
down_revision = '[previous_revision]'
branch_labels = None
depends_on = None

def upgrade():
    # Table 1: patient_personas
    op.create_table(
        'patient_personas',
        sa.Column('persona_id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('persona_code', sa.String(20), unique=True, nullable=False),
        # ... (full schema from detailed spec)
    )

    # Table 2: osce_attempts
    # ... (full schema)

    # Table 3: osce_scores
    # ... (full schema)

    # Table 4: mock_exams
    # ... (full schema)

    # Extend user_progress
    op.add_column('user_progress', sa.Column('ai_osces_attempted', sa.Integer, server_default='0'))
    # ... (5 columns)

    # Create trigger function
    op.execute("""
    CREATE OR REPLACE FUNCTION update_ai_osce_progress()
    RETURNS TRIGGER AS $$
    BEGIN
        -- (trigger logic from spec)
    END;
    $$ LANGUAGE plpgsql;
    """)

    # Create trigger
    op.execute("""
    CREATE TRIGGER trigger_update_ai_osce_progress
    AFTER UPDATE OF ended_at ON osce_attempts
    FOR EACH ROW
    WHEN (NEW.ended_at IS NOT NULL AND OLD.ended_at IS NULL)
    EXECUTE FUNCTION update_ai_osce_progress();
    """)

    # Indexes (CONCURRENTLY)
    # ... (15+ indexes)

def downgrade():
    # Drop trigger
    op.execute("DROP TRIGGER IF EXISTS trigger_update_ai_osce_progress ON osce_attempts")
    # Drop function
    op.execute("DROP FUNCTION IF EXISTS update_ai_osce_progress()")
    # Drop indexes
    # ... (reverse order)
    # Drop tables
    # ... (reverse dependency order)
    # Remove columns from user_progress
    # ... (5 columns)
```

### Appendix C: Error Codes
| Code | Message | Description | Resolution |
|------|---------|-------------|------------|
| 400 | Session not yet complete | Attempted to get transcript for active session | Wait for session to complete (session_state = 'complete') |
| 400 | Session not yet scored | Attempted to get score before AI Examiner scored | Wait for scoring to complete |
| 401 | Invalid or missing token | JWT token missing or expired | Re-authenticate to get new token |
| 403 | Not authorized | User attempting to access another user's session | Can only access own sessions |
| 404 | Persona not found | Persona ID invalid or persona not active | Use GET /patient-personas to find valid personas |
| 404 | Session not found | Attempt ID invalid | Verify attempt_id from POST /osce-sessions response |

### Appendix D: Related PRDs
- **Blocks**:
  - PRD_AI_OSCE_002_WEBSOCKET_CHAT (needs database tables and API endpoints)
  - PRD_AI_OSCE_003_AI_PATIENT_INTEGRATION (needs persona data)
  - PRD_AI_OSCE_004_AI_EXAMINER_SCORING (needs osce_scores table)
  - PRD_AI_OSCE_005_MOCK_EXAM_ORCHESTRATION (needs mock_exams table)
  - All frontend PRDs (need API endpoints)
- **Depends On**: None (foundation task)
- **Related**:
  - Existing user authentication system (JWT)
  - Existing user_progress tracking

---

**Document Status**: Complete
**Created**: 2026-02-16
**Last Updated**: 2026-02-16
**Approved By**: Pending PM Review
**Version**: 1.0
**File Size**: ~55 KB
**Line Count**: ~1600 lines
