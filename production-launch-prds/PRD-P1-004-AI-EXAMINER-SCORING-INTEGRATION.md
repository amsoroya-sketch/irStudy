# PRD: AI Examiner Scoring Integration - OSCE Session Finalization

**PRD ID**: PRD-P1-004-AI-EXAMINER-SCORING-INTEGRATION
**Category**: Backend + Frontend Integration
**Priority**: P0-Critical (BLOCKS seeing OSCE results)
**Estimated Effort**: 4-6 hours
**Dependencies**: P1-1 (WebSocket Infrastructure), P1-2 (Session Controls), P1-3 (Emotional State)
**Status**: Ready for Implementation
**Standards**: T-RALPH V2.1 (Updated 2026-03-29)
**Assigned Agent**: `python-backend-developer` + `react-frontend-developer`

---

## R - REQUEST (What & Why)

### Executive Summary

Create the **AI Examiner Scoring Integration** system that automatically scores completed 8-minute OSCE sessions using Claude 3.5 Sonnet with the AMC Clinical Examination 15-mark rubric. When a student ends an OSCE session (or when the 8-minute timer expires), the backend must:

1. **Finalize the session** - Mark session as complete, record end time
2. **Invoke AI Examiner** - Send conversation transcript to existing `src/ai/ai_examiner.py` service
3. **Process scoring** - Receive structured score (Communication 0-3, Clinical Reasoning 0-4, Information Gathering 0-4, Management 0-2, Professionalism 0-2, Total 0-15)
4. **Detect critical errors** - Check for safety violations using `src/ai/scoring/critical_errors.py` (25+ rules)
5. **Apply auto-fail logic** - Even 15/15 becomes FAIL if critical errors detected
6. **Store results** - Insert into `ai_osce_scores` table
7. **Display results** - Frontend shows score breakdown, feedback, strengths, areas for improvement

**Impact**: Students can now see instant, consistent AI-powered feedback after every OSCE practice session, replacing traditional delayed human feedback. This unlocks the core value proposition of AI OSCE practice.

**Current State**: Students can complete OSCE sessions via WebSocket chat, but sessions end without any feedback or scoring. The AI Examiner service exists (`src/ai/ai_examiner.py` ~800 lines) but is not integrated into the API workflow.

**Desired State**: Automatic scoring within 3-5 seconds of session end, with detailed feedback displayed in a Material-UI results screen showing rubric breakdown, critical errors (if any), and actionable improvement suggestions.

### User Story

**As a** medical student practicing for the AMC Clinical Examination
**I want** to receive instant AI-powered scoring and feedback after completing an 8-minute OSCE session
**So that** I can identify my strengths and weaknesses, understand where I need to improve, and track my progress toward achieving a passing score (≥9/15) without waiting for human examiner availability

### Problem Statement

**Current Pain Points**:
1. **No feedback loop** - Students complete OSCE sessions but have no way to know how they performed
2. **Manual scoring delay** - Traditional OSCE feedback requires human examiners (24-48 hour delay)
3. **Inconsistent evaluation** - Human examiners vary in strictness and focus areas
4. **No critical error detection** - Students may miss safety-critical mistakes (e.g., failing to order ECG for chest pain)
5. **Limited practice opportunities** - Cost and availability constraints limit repetition

**Solution**:
- **Instant automated scoring** using Claude 3.5 Sonnet trained on AMC rubric
- **Consistent evaluation** - Same standards applied every time
- **Critical error detection** - 25+ safety rules automatically enforced
- **Unlimited practice** - Students can repeat scenarios multiple times to improve
- **Detailed feedback** - Structured suggestions for each rubric category

**Business Value**:
- **Cost reduction**: $0.04-0.07 per AI-scored session vs. $50-100 for human examiner
- **Instant feedback**: 3-5 seconds vs. 24-48 hours
- **Consistency**: 100% adherence to AMC rubric standards
- **Safety**: Zero tolerance for critical errors (auto-fail enforcement)
- **Scalability**: Support 1000+ concurrent students without additional examiner hiring

### Success Criteria

#### Must Have (100% Required)
- [ ] **API Endpoint**: `POST /api/v1/osce-sessions/{attempt_id}/finalize` returns 200 with scores
- [ ] **AI Examiner Integration**: Calls `src/ai/ai_examiner.py` service with conversation transcript
- [ ] **15-Mark Rubric**: Returns scores for all 5 categories (Communication, Clinical Reasoning, Information Gathering, Management, Professionalism)
- [ ] **Critical Error Detection**: Checks 25+ safety rules using `src/ai/scoring/critical_errors.py`
- [ ] **Auto-Fail Logic**: Sets `pass_fail = "FAIL"` if critical errors detected, even if score is 15/15
- [ ] **Database Storage**: Inserts complete results into `ai_osce_scores` table
- [ ] **Frontend Display**: Material-UI results component shows score breakdown, feedback, critical errors
- [ ] **Performance**: Scoring completes within 5 seconds (p95)
- [ ] **Security**: No hardcoded API keys, all secrets from Vault
- [ ] **Testing**: 100% test pass rate (15+ backend tests, 10+ frontend tests)

#### Should Have (90% Priority)
- [ ] **Progress Update**: Automatically updates `user_progress` table with new avg_score
- [ ] **Error Handling**: Graceful degradation if AI Examiner service fails (retry logic)
- [ ] **Caching**: Cache persona details to reduce DB queries during scoring
- [ ] **Audit Trail**: Log all scoring requests to Redis for troubleshooting
- [ ] **Accessibility**: WCAG 2.2 AA compliance on results screen

#### Nice to Have (Optional)
- [ ] **Export Results**: Download PDF of OSCE feedback report
- [ ] **Share Results**: Generate shareable link for educators
- [ ] **Comparison View**: Compare current score with previous attempts on same persona
- [ ] **Historical Trends**: Show score progression over time (chart)

### Scope

**In Scope**:
- Backend API endpoint for session finalization
- Integration with existing AI Examiner service (`src/ai/ai_examiner.py`)
- Critical error detection using existing rules (`src/ai/scoring/critical_errors.py`)
- Database insertion into `ai_osce_scores` table
- Frontend results component with Material-UI 7
- Score breakdown display (5 categories + total)
- Critical errors display (if any)
- Feedback display (strengths, areas for improvement, overall feedback)
- Performance optimization (scoring <5s)
- Comprehensive testing (unit + integration + E2E)

**Out of Scope** (Future Iterations):
- PDF export functionality - PRD-P2-001
- Historical trends dashboard - PRD-P3-001
- Educator review interface - PRD-P4-001
- Multi-attempt comparison - PRD-P5-001
- AI Examiner model fine-tuning - Content team

---

## A - ARCHITECTURE (How)

### Technical Approach

Extend the existing OSCE session API with a finalization endpoint that:
1. Marks session as complete in `ai_osce_attempts` table
2. Retrieves conversation history from database
3. Calls existing AI Examiner service with AMC rubric prompt
4. Runs critical error detection rules
5. Applies auto-fail logic if critical errors found
6. Stores results in `ai_osce_scores` table
7. Returns structured response to frontend

**Key Design Decisions**:
1. **Reuse existing AI Examiner service** - Don't duplicate scoring logic, integrate with `src/ai/ai_examiner.py`
2. **Critical errors override score** - Even perfect 15/15 becomes FAIL if safety violations detected
3. **Synchronous scoring** - Student waits 3-5s for results (acceptable UX, simpler architecture than async job queue)
4. **Structured feedback** - AI Examiner returns JSON with specific fields (not free-form text)
5. **Idempotency** - Calling finalize twice returns same cached result (no duplicate scoring charges)

### System Design

#### Component Interaction Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                    FRONTEND (React + Material-UI 7)                 │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  OSCESession.tsx                                             │  │
│  │  - Student completes 8-min session                           │  │
│  │  - Clicks "End Session" OR timer expires                     │  │
│  │  - Calls POST /osce-sessions/{id}/finalize                   │  │
│  │  - Shows loading spinner (3-5s)                              │  │
│  └────────────────────────┬─────────────────────────────────────┘  │
│                           │                                         │
│  ┌────────────────────────▼─────────────────────────────────────┐  │
│  │  OSCEResults.tsx                                             │  │
│  │  - Receives score response                                   │  │
│  │  - Displays rubric breakdown (5 categories)                  │  │
│  │  - Shows critical errors (if any)                            │  │
│  │  - Displays feedback (strengths, improvements, overall)      │  │
│  └──────────────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────────────┘
                         │ HTTPS POST
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   FASTAPI BACKEND (Python 3.11)                     │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  /api/v1/osce-sessions/{attempt_id}/finalize                 │  │
│  │  - Validate JWT token (student owns this session)            │  │
│  │  - Check session state (must be "active" or "paused")        │  │
│  │  - Mark session as "finalized" (UPDATE ai_osce_attempts)     │  │
│  └────────────────────────┬─────────────────────────────────────┘  │
│                           │                                         │
│  ┌────────────────────────▼─────────────────────────────────────┐  │
│  │  AI Examiner Service (src/ai/ai_examiner.py)                 │  │
│  │  - Load conversation_history from DB                         │  │
│  │  - Build AMC rubric prompt (15-mark scale)                   │  │
│  │  - Call Claude 3.5 Sonnet API                                │  │
│  │  - Parse structured JSON response                            │  │
│  │  - Return {communication_score, clinical_reasoning, ...}     │  │
│  └────────────────────────┬─────────────────────────────────────┘  │
│                           │                                         │
│  ┌────────────────────────▼─────────────────────────────────────┐  │
│  │  Critical Error Detector (src/ai/scoring/critical_errors.py) │  │
│  │  - Check 25+ safety rules                                    │  │
│  │  - Pattern matching on transcript                            │  │
│  │  - Examples: Missed ECG for chest pain, no allergy check     │  │
│  │  - Return list of detected errors                            │  │
│  └────────────────────────┬─────────────────────────────────────┘  │
│                           │                                         │
│  ┌────────────────────────▼─────────────────────────────────────┐  │
│  │  Auto-Fail Logic                                             │  │
│  │  - IF critical_errors.length > 0:                            │  │
│  │      pass_fail = "FAIL"  (even if score = 15/15)             │  │
│  │  - ELSE IF total_score >= 9:                                 │  │
│  │      pass_fail = "PASS"                                      │  │
│  │  - ELSE:                                                     │  │
│  │      pass_fail = "FAIL"                                      │  │
│  └────────────────────────┬─────────────────────────────────────┘  │
│                           │                                         │
│  ┌────────────────────────▼─────────────────────────────────────┐  │
│  │  Database Storage (PostgreSQL)                               │  │
│  │  - INSERT INTO ai_osce_scores (...)                          │  │
│  │  - UPDATE user_progress (avg_score, osces_attempted)         │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

#### Data Flow: Session Finalization

```
1. SESSION END TRIGGER
   Student clicks "End Session" OR Timer reaches 00:00
   ↓
   Frontend → POST /api/v1/osce-sessions/{attempt_id}/finalize
   Headers: Authorization: Bearer {jwt_token}

2. VALIDATION
   Backend → Verify JWT (user owns this session)
   Backend → Check session_state (must be "active" or "paused", not already "finalized")
   Backend → Check if score already exists (idempotency check)

3. SESSION FINALIZATION
   Backend → UPDATE ai_osce_attempts
      SET ended_at = NOW(),
          duration_seconds = EXTRACT(EPOCH FROM (NOW() - started_at)),
          session_state = 'finalized'
      WHERE attempt_id = {attempt_id}

4. LOAD CONVERSATION
   Backend → SELECT conversation_history, emotional_state_transitions, student_actions
      FROM ai_osce_attempts WHERE attempt_id = {attempt_id}
   Backend → SELECT persona details (name, chief_complaint, critical_actions)
      FROM patient_personas WHERE persona_id = {persona_id}

5. AI EXAMINER SCORING
   Backend → Call ai_examiner.score_session(persona, transcript)
   AI Examiner → Build AMC rubric prompt:
      "You are an experienced OSCE examiner for the AMC Clinical Examination.
       Score this 8-minute consultation using the 15-mark rubric:
       - Communication (0-3)
       - Clinical Reasoning (0-4)
       - Information Gathering (0-4)
       - Management (0-2)
       - Professionalism (0-2)

       Patient: {persona.name}, {persona.age}, {persona.gender}
       Chief Complaint: {persona.chief_complaint}

       Transcript:
       {formatted_conversation_history}

       Return JSON with scores and feedback."

   AI Examiner → Call Claude 3.5 Sonnet API
   AI Examiner → Parse response:
      {
        "communication_score": 3,
        "communication_feedback": "Excellent rapport building...",
        "clinical_reasoning_score": 3,
        "clinical_reasoning_feedback": "Good differential diagnosis...",
        "information_gathering_score": 3,
        "information_gathering_feedback": "Systematic history taking...",
        "management_score": 2,
        "management_feedback": "Appropriate management plan...",
        "professionalism_score": 2,
        "professionalism_feedback": "Maintained professionalism...",
        "total_score": 13,
        "strengths": ["Good communication", "Systematic approach"],
        "areas_for_improvement": ["Could explore red flags more"],
        "overall_feedback": "Strong performance overall..."
      }

6. CRITICAL ERROR DETECTION
   Backend → Call critical_error_detector.detect_errors(transcript, persona, scores)
   Detector → Check 25+ rules:
      - CE001: Chest pain without ECG
      - CE002: Stroke symptoms without recognition
      - CE003: Anaphylaxis without adrenaline
      ... (22 more rules)
   Detector → Return: [
      {
        "rule_id": "CE001",
        "name": "Missed acute red flag - chest pain",
        "description": "Failed to order ECG for chest pain presentation",
        "category": "acute_care",
        "evidence": "Patient mentioned chest pain but student did not order ECG"
      }
   ]

7. AUTO-FAIL LOGIC
   Backend → IF critical_errors.length > 0:
                scores["pass_fail"] = "FAIL"
                scores["critical_errors"] = critical_errors
             ELSE IF scores["total_score"] >= 9:
                scores["pass_fail"] = "PASS"
             ELSE:
                scores["pass_fail"] = "FAIL"

8. DATABASE STORAGE
   Backend → INSERT INTO ai_osce_scores (
      attempt_id,
      communication_score, communication_feedback,
      clinical_reasoning_score, clinical_reasoning_feedback,
      information_gathering_score, information_gathering_feedback,
      management_score, management_feedback,
      professionalism_score, professionalism_feedback,
      total_score, pass_fail,
      strengths, areas_for_improvement, overall_feedback,
      critical_errors,
      scored_at, scored_by
   ) VALUES (...)

   Backend → UPDATE user_progress
      SET ai_osces_attempted = ai_osces_attempted + 1,
          ai_osces_passed = ai_osces_passed + (scores.pass_fail == "PASS" ? 1 : 0),
          ai_osce_avg_score = (
            SELECT AVG(total_score) FROM ai_osce_scores
            WHERE attempt_id IN (SELECT attempt_id FROM ai_osce_attempts WHERE user_id = {user_id})
          ),
          last_ai_osce_at = NOW()
      WHERE user_id = {user_id}

9. RETURN RESPONSE
   Backend → Return JSON:
   {
     "attempt_id": "9d76cd2a-5ad0-4e01-835a-3ce995023367",
     "persona_name": "Emma Wilson",
     "session_duration": 480,
     "scores": {
       "communication": {"score": 3, "max": 3, "feedback": "..."},
       "clinical_reasoning": {"score": 3, "max": 4, "feedback": "..."},
       "information_gathering": {"score": 3, "max": 4, "feedback": "..."},
       "management": {"score": 2, "max": 2, "feedback": "..."},
       "professionalism": {"score": 2, "max": 2, "feedback": "..."},
       "total": {"score": 13, "max": 15}
     },
     "result": {
       "pass_fail": "PASS",
       "pass_threshold": 9,
       "percentage": 86.7
     },
     "feedback": {
       "strengths": ["Good communication", "Systematic approach"],
       "areas_for_improvement": ["Could explore red flags more"],
       "overall": "Strong performance overall..."
     },
     "critical_errors": [],
     "scored_at": "2026-03-21T21:05:30Z"
   }

10. FRONTEND DISPLAY
    Frontend → Receives response
    Frontend → Renders OSCEResults component:
       - Header: "PASS" (green) or "FAIL" (red)
       - Total Score: 13/15 (86.7%)
       - Category Breakdown: 5 progress bars with scores
       - Critical Errors: Alert box (if any)
       - Feedback: Strengths, Improvements, Overall
       - Actions: "Try Again", "Review Transcript", "Generate Study Cards"
```

### Database Schema

#### Existing Table: ai_osce_scores

Already exists in database from PRD_AI_OSCE_001. No schema changes needed.

```sql
-- Verify table structure
\d ai_osce_scores

-- Expected columns:
-- score_id (UUID, PRIMARY KEY)
-- attempt_id (UUID, FOREIGN KEY -> ai_osce_attempts)
-- communication_score (INT 0-3)
-- communication_feedback (TEXT)
-- clinical_reasoning_score (INT 0-4)
-- clinical_reasoning_feedback (TEXT)
-- information_gathering_score (INT 0-4)
-- information_gathering_feedback (TEXT)
-- management_score (INT 0-2)
-- management_feedback (TEXT)
-- professionalism_score (INT 0-2)
-- professionalism_feedback (TEXT)
-- total_score (INT 0-15, GENERATED)
-- pass_fail (VARCHAR CHECK IN ('PASS', 'FAIL'))
-- strengths (JSONB)
-- areas_for_improvement (JSONB)
-- overall_feedback (TEXT)
-- critical_errors (JSONB)
-- scored_at (TIMESTAMP WITH TIME ZONE)
-- scored_by (VARCHAR, DEFAULT 'ai_examiner')
```

### API Endpoint Specification

#### POST /api/v1/osce-sessions/{attempt_id}/finalize

**Purpose**: Finalize OSCE session and return AI-generated scores

**Authentication**: JWT Bearer token required

**Rate Limit**: 10 requests per minute per user

**Request**:
```http
POST /api/v1/osce-sessions/9d76cd2a-5ad0-4e01-835a-3ce995023367/finalize HTTP/1.1
Host: localhost:8001
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json
```

**No request body required** (all data from database)

**Response 200 OK** (Success):
```json
{
  "attempt_id": "9d76cd2a-5ad0-4e01-835a-3ce995023367",
  "persona_name": "Emma Wilson",
  "persona_code": "general_practice_062_type_female_64",
  "session_duration": 480,
  "started_at": "2026-03-21T20:58:12.482660+00:00",
  "ended_at": "2026-03-21T21:06:12.482660+00:00",
  "scores": {
    "communication": {
      "score": 3,
      "max": 3,
      "feedback": "Excellent rapport building. Used open-ended questions effectively. Demonstrated active listening with appropriate verbal and non-verbal cues."
    },
    "clinical_reasoning": {
      "score": 3,
      "max": 4,
      "feedback": "Developed appropriate differential diagnosis for Type 2 Diabetes. Considered complications. Could have explored medication adherence more thoroughly."
    },
    "information_gathering": {
      "score": 3,
      "max": 4,
      "feedback": "Systematic history taking using structured approach. Covered social, family history. Missed opportunity to ask about dietary patterns in detail."
    },
    "management": {
      "score": 2,
      "max": 2,
      "feedback": "Appropriate management plan discussed. Explained HbA1c targets clearly. Discussed lifestyle modifications."
    },
    "professionalism": {
      "score": 2,
      "max": 2,
      "feedback": "Maintained professional boundaries throughout. Showed empathy. Ensured patient understanding."
    },
    "total": {
      "score": 13,
      "max": 15
    }
  },
  "result": {
    "pass_fail": "PASS",
    "pass_threshold": 9,
    "percentage": 86.7
  },
  "feedback": {
    "strengths": [
      "Excellent communication and rapport building",
      "Systematic approach to history taking",
      "Clear explanation of management plan"
    ],
    "areas_for_improvement": [
      "Explore dietary patterns in more detail for diabetes management",
      "Ask more specific questions about medication adherence",
      "Consider screening for diabetic complications (retinopathy, neuropathy)"
    ],
    "overall": "Strong performance overall. You demonstrated excellent communication skills and a systematic approach to gathering information. Your management plan was appropriate and well-explained. To improve further, focus on exploring lifestyle factors in greater depth and ensuring comprehensive screening for complications."
  },
  "critical_errors": [],
  "scored_at": "2026-03-21T21:06:15.123456+00:00"
}
```

**Response 400 Bad Request** (Session not active):
```json
{
  "error": {
    "code": 400,
    "message": "Cannot finalize session - session state is 'finalized'. Session has already been scored.",
    "path": "/api/v1/osce-sessions/9d76cd2a-5ad0-4e01-835a-3ce995023367/finalize"
  }
}
```

**Response 403 Forbidden** (Not your session):
```json
{
  "error": {
    "code": 403,
    "message": "You do not have permission to finalize this session. This session belongs to another user.",
    "path": "/api/v1/osce-sessions/9d76cd2a-5ad0-4e01-835a-3ce995023367/finalize"
  }
}
```

**Response 404 Not Found** (Session doesn't exist):
```json
{
  "error": {
    "code": 404,
    "message": "OSCE session not found",
    "path": "/api/v1/osce-sessions/invalid-uuid/finalize"
  }
}
```

**Response 500 Internal Server Error** (AI Examiner failure):
```json
{
  "error": {
    "code": 500,
    "message": "AI Examiner service error: API rate limit exceeded. Please try again in 60 seconds.",
    "path": "/api/v1/osce-sessions/9d76cd2a-5ad0-4e01-835a-3ce995023367/finalize"
  }
}
```

### Performance Requirements

- **Scoring Latency**: <5 seconds (p95), <3 seconds (p50)
- **Database Query**: <50ms for session retrieval
- **Claude API Call**: <3 seconds for response
- **Critical Error Detection**: <100ms for rule checking
- **Total Response Time**: <5 seconds end-to-end

### Security Requirements

- **No hardcoded API keys**: All secrets from Vault (`ANTHROPIC_API_KEY`)
- **JWT validation**: Verify user owns the session before scoring
- **SQL injection prevention**: Use parameterized queries only
- **Rate limiting**: Max 10 finalize requests per minute per user
- **Audit logging**: Log all scoring requests to Redis with user_id, attempt_id, timestamp

---

## L - LOOP (Iterative Development)

### Phase 1: Backend API Endpoint (2 hours)

**Deliverables**:
- Create `finalize_session()` function in `backend/src/api/v1/osce_sessions.py`
- Integrate with existing `ai_examiner.score_session()` from `src/ai/ai_examiner.py`
- Integrate with existing `critical_error_detector.detect_errors()` from `src/ai/scoring/critical_errors.py`
- Database insertion into `ai_osce_scores` table
- Error handling (session not found, already finalized, AI service failure)

**Validation Checkpoints**:
- [ ] Endpoint returns 200 with valid score structure
- [ ] Score inserted into `ai_osce_scores` table correctly
- [ ] Critical errors detected when applicable
- [ ] Auto-fail logic works (FAIL if critical errors, even with 15/15)
- [ ] Idempotency: Calling twice returns cached result
- [ ] Performance: <5s response time

**Rollback Strategy**:
- If AI Examiner integration fails, return mock scores for testing
- If database insertion fails, rollback session state to "active"

**Testing**:
```bash
# Unit tests
pytest backend/tests/test_api/test_osce_finalize.py -v

# Integration tests
pytest backend/tests/test_integration/test_scoring_workflow.py -v

# Expected: 10/10 tests passing
```

### Phase 2: Frontend Results Component (1.5 hours)

**Deliverables**:
- Create `frontend/src/components/osce/OSCEResults.tsx` (350 lines)
- Material-UI 7 layout with score breakdown
- Critical errors alert box (if any)
- Feedback display (strengths, improvements, overall)
- Action buttons (Try Again, Review Transcript, Generate Study Cards)

**Validation Checkpoints**:
- [ ] Component renders without TypeScript errors
- [ ] Score breakdown displays all 5 categories correctly
- [ ] Total score shows with percentage calculation
- [ ] Pass/Fail badge displays with correct color (green/red)
- [ ] Critical errors alert appears when errors exist
- [ ] Feedback sections display with proper formatting
- [ ] WCAG 2.2 AA compliance (color contrast, ARIA labels)

**Rollback Strategy**:
- If component crashes, fallback to simple JSON display

**Testing**:
```bash
# Component tests
npm test -- OSCEResults.test.tsx

# Expected: 15/15 tests passing
```

### Phase 3: Integration & E2E Testing (0.5 hours)

**Deliverables**:
- E2E test: Complete OSCE session → Finalize → View results
- Performance test: Scoring latency <5s
- Security test: Cannot finalize other users' sessions

**Validation Checkpoints**:
- [ ] E2E test passes (Playwright)
- [ ] Scoring completes within 5s
- [ ] Unauthorized access blocked (403 error)
- [ ] No hardcoded credentials in code

**Testing**:
```bash
# E2E tests
npm run test:e2e -- osce-scoring.spec.ts

# Expected: 5/5 scenarios passing
```

---

## P - PLAN (Detailed Implementation)

### File 1: `backend/src/api/v1/osce_sessions.py` (+180 lines)

**Purpose**: Add finalize endpoint to existing OSCE sessions router

**Implementation**:

```python
# backend/src/api/v1/osce_sessions.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any
from uuid import UUID
import logging

from src.db.base import get_db
from src.db.models import OSCEAttemptAI, PatientPersona, User, OSCEScoreAI
from src.auth.dependencies import get_current_active_user
from src.ai.ai_examiner import AIExaminerService
from src.ai.scoring.critical_errors import CriticalErrorDetector

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/osce-sessions", tags=["ai-osce"])


@router.post("/{attempt_id}/finalize", response_model=Dict[str, Any])
async def finalize_osce_session(
    attempt_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Finalize OSCE session and return AI-generated scores.

    This endpoint:
    1. Marks session as finalized
    2. Calls AI Examiner for scoring
    3. Detects critical errors
    4. Applies auto-fail logic
    5. Stores results in database
    6. Updates user progress

    Args:
        attempt_id: UUID of OSCE attempt
        current_user: Authenticated user
        db: Database session

    Returns:
        Structured score response with rubric breakdown, feedback, critical errors

    Raises:
        HTTPException 403: User does not own this session
        HTTPException 404: Session not found
        HTTPException 400: Session already finalized
        HTTPException 500: AI Examiner service error
    """

    # 1. RETRIEVE SESSION
    logger.info(f"Finalizing OSCE session {attempt_id} for user {current_user.id}")

    attempt = db.query(OSCEAttemptAI).filter(
        OSCEAttemptAI.attempt_id == attempt_id
    ).first()

    if not attempt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="OSCE session not found"
        )

    # 2. AUTHORIZATION CHECK
    if str(attempt.user_id) != str(current_user.id):
        logger.warning(
            f"User {current_user.id} attempted to finalize session {attempt_id} "
            f"belonging to user {attempt.user_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to finalize this session. "
                   "This session belongs to another user."
        )

    # 3. CHECK SESSION STATE (Idempotency)
    if attempt.session_state == "finalized":
        # Session already scored - return cached result
        logger.info(f"Session {attempt_id} already finalized, returning cached score")
        existing_score = db.query(OSCEScoreAI).filter(
            OSCEScoreAI.attempt_id == attempt_id
        ).first()

        if existing_score:
            return _format_score_response(attempt, existing_score, db)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Session is marked as finalized but no score found. "
                       "Please contact support."
            )

    # 4. VALIDATE SESSION STATE
    if attempt.session_state not in ["active", "paused"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot finalize session - session state is '{attempt.session_state}'. "
                   f"Only active or paused sessions can be finalized."
        )

    # 5. FINALIZE SESSION IN DATABASE
    from datetime import datetime, timezone

    attempt.ended_at = datetime.now(timezone.utc)
    attempt.duration_seconds = int(
        (attempt.ended_at - attempt.started_at).total_seconds()
    )
    attempt.session_state = "finalized"
    db.commit()

    logger.info(
        f"Session {attempt_id} finalized. Duration: {attempt.duration_seconds}s"
    )

    # 6. RETRIEVE PERSONA
    persona = db.query(PatientPersona).filter(
        PatientPersona.persona_id == attempt.persona_id
    ).first()

    if not persona:
        logger.error(f"Persona {attempt.persona_id} not found for session {attempt_id}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Patient persona not found. Cannot score session."
        )

    # 7. PREPARE TRANSCRIPT
    transcript = attempt.conversation_history or []
    if not transcript:
        logger.warning(f"Empty transcript for session {attempt_id}")

    # 8. CALL AI EXAMINER SERVICE
    try:
        logger.info(f"Calling AI Examiner for session {attempt_id}")
        examiner = AIExaminerService()
        scores = examiner.score_session(persona, transcript)

        logger.info(
            f"AI Examiner returned score: {scores.get('total_score', 0)}/15 "
            f"for session {attempt_id}"
        )
    except Exception as e:
        logger.error(f"AI Examiner service error for session {attempt_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI Examiner service error: {str(e)}"
        )

    # 9. DETECT CRITICAL ERRORS
    try:
        logger.info(f"Checking critical errors for session {attempt_id}")
        detector = CriticalErrorDetector()
        critical_errors = detector.detect_errors(transcript, persona, scores)

        if critical_errors:
            logger.warning(
                f"Critical errors detected for session {attempt_id}: "
                f"{len(critical_errors)} errors"
            )
    except Exception as e:
        logger.error(f"Critical error detection failed for session {attempt_id}: {str(e)}")
        # Don't fail the request - continue without critical error detection
        critical_errors = []

    # 10. APPLY AUTO-FAIL LOGIC
    if critical_errors:
        scores["pass_fail"] = "FAIL"
        scores["critical_errors"] = critical_errors
        logger.info(
            f"Auto-fail applied to session {attempt_id} due to "
            f"{len(critical_errors)} critical error(s)"
        )
    else:
        # Determine pass/fail based on score
        if scores.get("total_score", 0) >= 9:
            scores["pass_fail"] = "PASS"
        else:
            scores["pass_fail"] = "FAIL"
        scores["critical_errors"] = []

    # 11. STORE RESULTS IN DATABASE
    try:
        osce_score = OSCEScoreAI(
            attempt_id=attempt_id,
            communication_score=scores.get("communication_score", 0),
            communication_feedback=scores.get("communication_feedback", ""),
            clinical_reasoning_score=scores.get("clinical_reasoning_score", 0),
            clinical_reasoning_feedback=scores.get("clinical_reasoning_feedback", ""),
            information_gathering_score=scores.get("information_gathering_score", 0),
            information_gathering_feedback=scores.get("information_gathering_feedback", ""),
            management_score=scores.get("management_score", 0),
            management_feedback=scores.get("management_feedback", ""),
            professionalism_score=scores.get("professionalism_score", 0),
            professionalism_feedback=scores.get("professionalism_feedback", ""),
            pass_fail=scores.get("pass_fail", "FAIL"),
            strengths=scores.get("strengths", []),
            areas_for_improvement=scores.get("areas_for_improvement", []),
            overall_feedback=scores.get("overall_feedback", ""),
            critical_errors=scores.get("critical_errors", []),
            scored_by="ai_examiner"
        )

        db.add(osce_score)
        db.commit()
        db.refresh(osce_score)

        logger.info(f"Score stored in database for session {attempt_id}")
    except Exception as e:
        logger.error(f"Database insertion failed for session {attempt_id}: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to store score in database: {str(e)}"
        )

    # 12. UPDATE USER PROGRESS
    try:
        _update_user_progress(current_user.id, scores.get("pass_fail"), db)
    except Exception as e:
        logger.error(f"Failed to update user progress: {str(e)}")
        # Don't fail the request - progress update is non-critical

    # 13. RETURN FORMATTED RESPONSE
    return _format_score_response(attempt, osce_score, db)


def _format_score_response(
    attempt: OSCEAttemptAI,
    score: OSCEScoreAI,
    db: Session
) -> Dict[str, Any]:
    """
    Format score database record into API response structure.

    Args:
        attempt: OSCE attempt record
        score: Score record
        db: Database session

    Returns:
        Formatted response dictionary
    """
    persona = db.query(PatientPersona).filter(
        PatientPersona.persona_id == attempt.persona_id
    ).first()

    return {
        "attempt_id": str(attempt.attempt_id),
        "persona_name": persona.name if persona else "Unknown",
        "persona_code": persona.persona_code if persona else "unknown",
        "session_duration": attempt.duration_seconds,
        "started_at": attempt.started_at.isoformat(),
        "ended_at": attempt.ended_at.isoformat() if attempt.ended_at else None,
        "scores": {
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
            },
            "total": {
                "score": score.total_score,
                "max": 15
            }
        },
        "result": {
            "pass_fail": score.pass_fail,
            "pass_threshold": 9,
            "percentage": round((score.total_score / 15) * 100, 1)
        },
        "feedback": {
            "strengths": score.strengths,
            "areas_for_improvement": score.areas_for_improvement,
            "overall": score.overall_feedback
        },
        "critical_errors": score.critical_errors,
        "scored_at": score.scored_at.isoformat()
    }


def _update_user_progress(user_id: str, pass_fail: str, db: Session):
    """
    Update user_progress table with new OSCE attempt stats.

    Args:
        user_id: User ID
        pass_fail: "PASS" or "FAIL"
        db: Database session
    """
    from sqlalchemy import text

    # Calculate average score across all attempts
    avg_score_query = text("""
        SELECT AVG(s.total_score)
        FROM ai_osce_scores s
        JOIN ai_osce_attempts a ON s.attempt_id = a.attempt_id
        WHERE a.user_id = :user_id
    """)

    avg_score = db.execute(avg_score_query, {"user_id": user_id}).scalar() or 0

    # Update user_progress
    update_query = text("""
        UPDATE user_progress
        SET ai_osces_attempted = ai_osces_attempted + 1,
            ai_osces_passed = ai_osces_passed + CASE WHEN :pass_fail = 'PASS' THEN 1 ELSE 0 END,
            ai_osce_avg_score = :avg_score,
            last_ai_osce_at = NOW()
        WHERE user_id = :user_id
    """)

    db.execute(update_query, {
        "user_id": user_id,
        "pass_fail": pass_fail,
        "avg_score": avg_score
    })
    db.commit()

    logger.info(
        f"User {user_id} progress updated: avg_score={avg_score:.1f}, "
        f"latest_result={pass_fail}"
    )
```

### File 2: `frontend/src/components/osce/OSCEResults.tsx` (+350 lines)

**Purpose**: Material-UI component to display OSCE scoring results

**Implementation**:

```typescript
// frontend/src/components/osce/OSCEResults.tsx

import React from 'react';
import {
  Box,
  Paper,
  Typography,
  LinearProgress,
  Chip,
  Alert,
  AlertTitle,
  Divider,
  Button,
  Stack,
  Grid,
} from '@mui/material';
import {
  CheckCircle as CheckCircleIcon,
  Cancel as CancelIcon,
  Refresh as RefreshIcon,
  Description as DescriptionIcon,
  School as SchoolIcon,
  Warning as WarningIcon,
} from '@mui/icons-material';
import { styled } from '@mui/material/styles';

// ============================================================================
// TYPE DEFINITIONS
// ============================================================================

interface CategoryScore {
  score: number;
  max: number;
  feedback: string;
}

interface ScoreBreakdown {
  communication: CategoryScore;
  clinical_reasoning: CategoryScore;
  information_gathering: CategoryScore;
  management: CategoryScore;
  professionalism: CategoryScore;
  total: {
    score: number;
    max: number;
  };
}

interface Result {
  pass_fail: 'PASS' | 'FAIL';
  pass_threshold: number;
  percentage: number;
}

interface Feedback {
  strengths: string[];
  areas_for_improvement: string[];
  overall: string;
}

interface CriticalError {
  rule_id: string;
  name: string;
  description: string;
  category: string;
  evidence: string;
}

interface OSCEResultsProps {
  attempt_id: string;
  persona_name: string;
  persona_code: string;
  session_duration: number;
  started_at: string;
  ended_at: string;
  scores: ScoreBreakdown;
  result: Result;
  feedback: Feedback;
  critical_errors: CriticalError[];
  scored_at: string;
  onTryAgain?: () => void;
  onReviewTranscript?: () => void;
  onGenerateStudyCards?: () => void;
}

// ============================================================================
// STYLED COMPONENTS
// ============================================================================

const ResultsContainer = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(4),
  maxWidth: 1000,
  margin: '0 auto',
}));

const HeaderBox = styled(Box)(({ theme }) => ({
  textAlign: 'center',
  marginBottom: theme.spacing(4),
}));

const PassChip = styled(Chip)(({ theme }) => ({
  fontSize: '1.5rem',
  padding: theme.spacing(3, 5),
  height: 'auto',
  backgroundColor: theme.palette.success.main,
  color: theme.palette.success.contrastText,
  '& .MuiChip-icon': {
    fontSize: '2rem',
  },
}));

const FailChip = styled(Chip)(({ theme }) => ({
  fontSize: '1.5rem',
  padding: theme.spacing(3, 5),
  height: 'auto',
  backgroundColor: theme.palette.error.main,
  color: theme.palette.error.contrastText,
  '& .MuiChip-icon': {
    fontSize: '2rem',
  },
}));

const CategoryBox = styled(Box)(({ theme }) => ({
  marginBottom: theme.spacing(3),
}));

const FeedbackSection = styled(Box)(({ theme }) => ({
  marginTop: theme.spacing(4),
}));

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export function OSCEResults({
  attempt_id,
  persona_name,
  persona_code,
  session_duration,
  started_at,
  ended_at,
  scores,
  result,
  feedback,
  critical_errors,
  scored_at,
  onTryAgain,
  onReviewTranscript,
  onGenerateStudyCards,
}: OSCEResultsProps) {
  const isPassed = result.pass_fail === 'PASS';
  const hasCriticalErrors = critical_errors && critical_errors.length > 0;

  // Format duration (seconds to MM:SS)
  const formatDuration = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  // Calculate progress percentage for linear progress bars
  const getProgressPercentage = (score: number, max: number): number => {
    return (score / max) * 100;
  };

  // Get color for score based on performance
  const getScoreColor = (score: number, max: number): 'error' | 'warning' | 'success' => {
    const percentage = (score / max) * 100;
    if (percentage < 60) return 'error';
    if (percentage < 80) return 'warning';
    return 'success';
  };

  return (
    <ResultsContainer elevation={3}>
      {/* HEADER: Pass/Fail Badge */}
      <HeaderBox>
        {isPassed ? (
          <PassChip
            icon={<CheckCircleIcon />}
            label="PASS"
            aria-label="Session result: PASS"
          />
        ) : (
          <FailChip
            icon={<CancelIcon />}
            label="FAIL"
            aria-label="Session result: FAIL"
          />
        )}

        <Typography variant="h4" component="h1" sx={{ mt: 2 }}>
          OSCE Session Results
        </Typography>

        <Typography variant="body1" color="text.secondary" sx={{ mt: 1 }}>
          Patient: {persona_name} ({persona_code})
        </Typography>

        <Typography variant="body2" color="text.secondary">
          Session Duration: {formatDuration(session_duration)}
        </Typography>
      </HeaderBox>

      <Divider sx={{ mb: 4 }} />

      {/* CRITICAL ERRORS ALERT */}
      {hasCriticalErrors && (
        <Alert severity="error" icon={<WarningIcon />} sx={{ mb: 4 }}>
          <AlertTitle>Critical Safety Errors Detected</AlertTitle>
          <Typography variant="body2" sx={{ mb: 2 }}>
            Your session has been marked as <strong>FAIL</strong> due to {critical_errors.length}{' '}
            critical safety error(s), regardless of your score. These are safety-critical mistakes
            that would put patients at risk in real clinical practice.
          </Typography>

          {critical_errors.map((error, index) => (
            <Box key={index} sx={{ mb: 2 }}>
              <Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>
                {error.name} ({error.rule_id})
              </Typography>
              <Typography variant="body2">{error.description}</Typography>
              <Typography variant="body2" color="text.secondary" sx={{ fontStyle: 'italic' }}>
                Evidence: {error.evidence}
              </Typography>
            </Box>
          ))}
        </Alert>
      )}

      {/* TOTAL SCORE */}
      <Box sx={{ textAlign: 'center', mb: 4 }}>
        <Typography variant="h2" component="p" aria-label="Total score">
          {scores.total.score} / {scores.total.max}
        </Typography>
        <Typography variant="h6" color="text.secondary">
          {result.percentage}%
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
          Pass Threshold: {result.pass_threshold}/15 (60%)
        </Typography>
      </Box>

      <Divider sx={{ mb: 4 }} />

      {/* SCORE BREAKDOWN BY CATEGORY */}
      <Typography variant="h5" component="h2" sx={{ mb: 3 }}>
        Category Breakdown
      </Typography>

      <Grid container spacing={3}>
        {/* Communication */}
        <Grid item xs={12}>
          <CategoryBox>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
              <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>
                Communication
              </Typography>
              <Typography variant="subtitle1">
                {scores.communication.score} / {scores.communication.max}
              </Typography>
            </Box>
            <LinearProgress
              variant="determinate"
              value={getProgressPercentage(scores.communication.score, scores.communication.max)}
              color={getScoreColor(scores.communication.score, scores.communication.max)}
              sx={{ height: 10, borderRadius: 5, mb: 1 }}
              aria-label={`Communication score: ${scores.communication.score} out of ${scores.communication.max}`}
            />
            <Typography variant="body2" color="text.secondary">
              {scores.communication.feedback}
            </Typography>
          </CategoryBox>
        </Grid>

        {/* Clinical Reasoning */}
        <Grid item xs={12}>
          <CategoryBox>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
              <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>
                Clinical Reasoning
              </Typography>
              <Typography variant="subtitle1">
                {scores.clinical_reasoning.score} / {scores.clinical_reasoning.max}
              </Typography>
            </Box>
            <LinearProgress
              variant="determinate"
              value={getProgressPercentage(scores.clinical_reasoning.score, scores.clinical_reasoning.max)}
              color={getScoreColor(scores.clinical_reasoning.score, scores.clinical_reasoning.max)}
              sx={{ height: 10, borderRadius: 5, mb: 1 }}
              aria-label={`Clinical Reasoning score: ${scores.clinical_reasoning.score} out of ${scores.clinical_reasoning.max}`}
            />
            <Typography variant="body2" color="text.secondary">
              {scores.clinical_reasoning.feedback}
            </Typography>
          </CategoryBox>
        </Grid>

        {/* Information Gathering */}
        <Grid item xs={12}>
          <CategoryBox>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
              <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>
                Information Gathering
              </Typography>
              <Typography variant="subtitle1">
                {scores.information_gathering.score} / {scores.information_gathering.max}
              </Typography>
            </Box>
            <LinearProgress
              variant="determinate"
              value={getProgressPercentage(scores.information_gathering.score, scores.information_gathering.max)}
              color={getScoreColor(scores.information_gathering.score, scores.information_gathering.max)}
              sx={{ height: 10, borderRadius: 5, mb: 1 }}
              aria-label={`Information Gathering score: ${scores.information_gathering.score} out of ${scores.information_gathering.max}`}
            />
            <Typography variant="body2" color="text.secondary">
              {scores.information_gathering.feedback}
            </Typography>
          </CategoryBox>
        </Grid>

        {/* Management */}
        <Grid item xs={12}>
          <CategoryBox>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
              <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>
                Management
              </Typography>
              <Typography variant="subtitle1">
                {scores.management.score} / {scores.management.max}
              </Typography>
            </Box>
            <LinearProgress
              variant="determinate"
              value={getProgressPercentage(scores.management.score, scores.management.max)}
              color={getScoreColor(scores.management.score, scores.management.max)}
              sx={{ height: 10, borderRadius: 5, mb: 1 }}
              aria-label={`Management score: ${scores.management.score} out of ${scores.management.max}`}
            />
            <Typography variant="body2" color="text.secondary">
              {scores.management.feedback}
            </Typography>
          </CategoryBox>
        </Grid>

        {/* Professionalism */}
        <Grid item xs={12}>
          <CategoryBox>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
              <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>
                Professionalism
              </Typography>
              <Typography variant="subtitle1">
                {scores.professionalism.score} / {scores.professionalism.max}
              </Typography>
            </Box>
            <LinearProgress
              variant="determinate"
              value={getProgressPercentage(scores.professionalism.score, scores.professionalism.max)}
              color={getScoreColor(scores.professionalism.score, scores.professionalism.max)}
              sx={{ height: 10, borderRadius: 5, mb: 1 }}
              aria-label={`Professionalism score: ${scores.professionalism.score} out of ${scores.professionalism.max}`}
            />
            <Typography variant="body2" color="text.secondary">
              {scores.professionalism.feedback}
            </Typography>
          </CategoryBox>
        </Grid>
      </Grid>

      <Divider sx={{ my: 4 }} />

      {/* FEEDBACK SECTION */}
      <FeedbackSection>
        <Typography variant="h5" component="h2" sx={{ mb: 3 }}>
          Detailed Feedback
        </Typography>

        {/* Strengths */}
        {feedback.strengths && feedback.strengths.length > 0 && (
          <Box sx={{ mb: 3 }}>
            <Typography variant="h6" sx={{ mb: 1, color: 'success.main' }}>
              ✓ Strengths
            </Typography>
            <Box component="ul" sx={{ pl: 3 }}>
              {feedback.strengths.map((strength, index) => (
                <Typography component="li" variant="body1" key={index} sx={{ mb: 0.5 }}>
                  {strength}
                </Typography>
              ))}
            </Box>
          </Box>
        )}

        {/* Areas for Improvement */}
        {feedback.areas_for_improvement && feedback.areas_for_improvement.length > 0 && (
          <Box sx={{ mb: 3 }}>
            <Typography variant="h6" sx={{ mb: 1, color: 'warning.main' }}>
              → Areas for Improvement
            </Typography>
            <Box component="ul" sx={{ pl: 3 }}>
              {feedback.areas_for_improvement.map((area, index) => (
                <Typography component="li" variant="body1" key={index} sx={{ mb: 0.5 }}>
                  {area}
                </Typography>
              ))}
            </Box>
          </Box>
        )}

        {/* Overall Feedback */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="h6" sx={{ mb: 1 }}>
            Overall Feedback
          </Typography>
          <Typography variant="body1">{feedback.overall}</Typography>
        </Box>
      </FeedbackSection>

      <Divider sx={{ my: 4 }} />

      {/* ACTION BUTTONS */}
      <Stack direction="row" spacing={2} justifyContent="center">
        <Button
          variant="contained"
          color="primary"
          startIcon={<RefreshIcon />}
          onClick={onTryAgain}
          aria-label="Try this scenario again"
        >
          Try Again
        </Button>

        <Button
          variant="outlined"
          startIcon={<DescriptionIcon />}
          onClick={onReviewTranscript}
          aria-label="Review conversation transcript"
        >
          Review Transcript
        </Button>

        <Button
          variant="outlined"
          color="secondary"
          startIcon={<SchoolIcon />}
          onClick={onGenerateStudyCards}
          aria-label="Generate study cards from this session"
        >
          Generate Study Cards
        </Button>
      </Stack>

      {/* METADATA */}
      <Box sx={{ mt: 4, textAlign: 'center' }}>
        <Typography variant="caption" color="text.secondary">
          Scored by AI Examiner at {new Date(scored_at).toLocaleString()}
        </Typography>
      </Box>
    </ResultsContainer>
  );
}
```

### File 3: `backend/tests/test_api/test_osce_finalize.py` (+200 lines)

**Purpose**: Comprehensive unit and integration tests for scoring endpoint

**Implementation**:

```python
# backend/tests/test_api/test_osce_finalize.py

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone
import json

from src.main import app
from src.db.models import OSCEAttemptAI, PatientPersona, User, OSCEScoreAI
from src.auth.security import create_access_token

client = TestClient(app)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def test_user(db_session):
    """Create test student user"""
    user = User(
        email="student@test.com",
        password_hash="hashed_password",
        full_name="Test Student",
        role="student",
        is_active=True,
        is_verified=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_persona(db_session):
    """Create test patient persona"""
    persona = PatientPersona(
        persona_code="CARD-TEST-001",
        name="Test Patient",
        age=55,
        gender="Male",
        specialty="Cardiology",
        chief_complaint="Chest pain",
        opening_statement="I have chest pain",
        symptoms={"immediate": ["chest pain"]},
        emotional_profile={"baseline_state": "ANXIOUS_GUARDED"}
    )
    db_session.add(persona)
    db_session.commit()
    db_session.refresh(persona)
    return persona


@pytest.fixture
def test_session(db_session, test_user, test_persona):
    """Create test OSCE session"""
    attempt = OSCEAttemptAI(
        user_id=test_user.id,
        persona_id=test_persona.persona_id,
        session_type="individual",
        session_state="active",
        conversation_history=[
            {"role": "student", "message": "Hello, how are you?"},
            {"role": "patient", "message": "I have chest pain"},
            {"role": "student", "message": "Can you describe the pain?"},
            {"role": "patient", "message": "It's crushing, central"},
            {"role": "student", "message": "I'd like to order an ECG"}
        ]
    )
    db_session.add(attempt)
    db_session.commit()
    db_session.refresh(attempt)
    return attempt


@pytest.fixture
def auth_headers(test_user):
    """Generate valid JWT token"""
    token = create_access_token(data={"user_id": test_user.id, "email": test_user.email})
    return {"Authorization": f"Bearer {token}"}


# ============================================================================
# SUCCESS CASES
# ============================================================================

@patch('src.api.v1.osce_sessions.AIExaminerService')
@patch('src.api.v1.osce_sessions.CriticalErrorDetector')
def test_finalize_session_success(
    mock_detector,
    mock_examiner,
    test_session,
    auth_headers,
    db_session
):
    """Test successful session finalization with AI scoring"""
    # Mock AI Examiner response
    mock_examiner_instance = MagicMock()
    mock_examiner.return_value = mock_examiner_instance
    mock_examiner_instance.score_session.return_value = {
        "communication_score": 3,
        "communication_feedback": "Excellent rapport",
        "clinical_reasoning_score": 3,
        "clinical_reasoning_feedback": "Good differential",
        "information_gathering_score": 3,
        "information_gathering_feedback": "Systematic history",
        "management_score": 2,
        "management_feedback": "Appropriate plan",
        "professionalism_score": 2,
        "professionalism_feedback": "Professional throughout",
        "total_score": 13,
        "strengths": ["Good communication"],
        "areas_for_improvement": ["Could explore more"],
        "overall_feedback": "Strong performance"
    }

    # Mock Critical Error Detector (no errors)
    mock_detector_instance = MagicMock()
    mock_detector.return_value = mock_detector_instance
    mock_detector_instance.detect_errors.return_value = []

    # Execute
    response = client.post(
        f"/api/v1/osce-sessions/{test_session.attempt_id}/finalize",
        headers=auth_headers
    )

    # Verify response
    assert response.status_code == 200
    data = response.json()

    assert data["attempt_id"] == str(test_session.attempt_id)
    assert data["scores"]["total"]["score"] == 13
    assert data["scores"]["total"]["max"] == 15
    assert data["result"]["pass_fail"] == "PASS"
    assert data["result"]["percentage"] == 86.7
    assert data["critical_errors"] == []
    assert len(data["feedback"]["strengths"]) > 0

    # Verify database insertion
    score = db_session.query(OSCEScoreAI).filter(
        OSCEScoreAI.attempt_id == test_session.attempt_id
    ).first()

    assert score is not None
    assert score.total_score == 13
    assert score.pass_fail == "PASS"


@patch('src.api.v1.osce_sessions.AIExaminerService')
@patch('src.api.v1.osce_sessions.CriticalErrorDetector')
def test_finalize_session_with_critical_errors_auto_fail(
    mock_detector,
    mock_examiner,
    test_session,
    auth_headers,
    db_session
):
    """Test auto-fail logic when critical errors detected (even with perfect score)"""
    # Mock AI Examiner with perfect score
    mock_examiner_instance = MagicMock()
    mock_examiner.return_value = mock_examiner_instance
    mock_examiner_instance.score_session.return_value = {
        "communication_score": 3,
        "communication_feedback": "Perfect",
        "clinical_reasoning_score": 4,
        "clinical_reasoning_feedback": "Perfect",
        "information_gathering_score": 4,
        "information_gathering_feedback": "Perfect",
        "management_score": 2,
        "management_feedback": "Perfect",
        "professionalism_score": 2,
        "professionalism_feedback": "Perfect",
        "total_score": 15,
        "strengths": ["Everything perfect"],
        "areas_for_improvement": [],
        "overall_feedback": "Flawless"
    }

    # Mock Critical Error Detector with error
    mock_detector_instance = MagicMock()
    mock_detector.return_value = mock_detector_instance
    mock_detector_instance.detect_errors.return_value = [
        {
            "rule_id": "CE001",
            "name": "Missed acute red flag - chest pain",
            "description": "Failed to order ECG for chest pain",
            "category": "acute_care",
            "evidence": "Patient mentioned chest pain but no ECG ordered"
        }
    ]

    # Execute
    response = client.post(
        f"/api/v1/osce-sessions/{test_session.attempt_id}/finalize",
        headers=auth_headers
    )

    # Verify auto-fail applied despite perfect score
    assert response.status_code == 200
    data = response.json()

    assert data["scores"]["total"]["score"] == 15  # Perfect score
    assert data["result"]["pass_fail"] == "FAIL"  # But FAIL due to critical error
    assert len(data["critical_errors"]) == 1
    assert data["critical_errors"][0]["rule_id"] == "CE001"


# ============================================================================
# ERROR CASES
# ============================================================================

def test_finalize_session_not_found(auth_headers):
    """Test 404 when session doesn't exist"""
    response = client.post(
        "/api/v1/osce-sessions/invalid-uuid/finalize",
        headers=auth_headers
    )

    assert response.status_code == 404
    assert "not found" in response.json()["error"]["message"].lower()


def test_finalize_session_unauthorized(test_session, db_session):
    """Test 403 when user doesn't own session"""
    # Create different user
    other_user = User(
        email="other@test.com",
        password_hash="hashed",
        full_name="Other User",
        role="student",
        is_active=True,
        is_verified=True
    )
    db_session.add(other_user)
    db_session.commit()

    # Generate token for different user
    token = create_access_token(data={"user_id": other_user.id, "email": other_user.email})
    headers = {"Authorization": f"Bearer {token}"}

    # Execute
    response = client.post(
        f"/api/v1/osce-sessions/{test_session.attempt_id}/finalize",
        headers=headers
    )

    assert response.status_code == 403
    assert "permission" in response.json()["error"]["message"].lower()


def test_finalize_session_already_finalized(test_session, auth_headers, db_session):
    """Test idempotency - calling finalize twice returns cached result"""
    # First call - success
    with patch('src.api.v1.osce_sessions.AIExaminerService') as mock_examiner, \
         patch('src.api.v1.osce_sessions.CriticalErrorDetector') as mock_detector:

        mock_examiner_instance = MagicMock()
        mock_examiner.return_value = mock_examiner_instance
        mock_examiner_instance.score_session.return_value = {
            "communication_score": 2,
            "communication_feedback": "Good",
            "clinical_reasoning_score": 2,
            "clinical_reasoning_feedback": "Good",
            "information_gathering_score": 2,
            "information_gathering_feedback": "Good",
            "management_score": 1,
            "management_feedback": "Good",
            "professionalism_score": 1,
            "professionalism_feedback": "Good",
            "total_score": 8,
            "strengths": ["Decent"],
            "areas_for_improvement": ["Improve"],
            "overall_feedback": "Okay"
        }

        mock_detector_instance = MagicMock()
        mock_detector.return_value = mock_detector_instance
        mock_detector_instance.detect_errors.return_value = []

        response1 = client.post(
            f"/api/v1/osce-sessions/{test_session.attempt_id}/finalize",
            headers=auth_headers
        )

        assert response1.status_code == 200
        data1 = response1.json()

    # Second call - should return cached result without calling AI Examiner again
    response2 = client.post(
        f"/api/v1/osce-sessions/{test_session.attempt_id}/finalize",
        headers=auth_headers
    )

    assert response2.status_code == 200
    data2 = response2.json()

    # Verify same result returned
    assert data1["attempt_id"] == data2["attempt_id"]
    assert data1["scores"]["total"]["score"] == data2["scores"]["total"]["score"]
    assert data1["result"]["pass_fail"] == data2["result"]["pass_fail"]


def test_finalize_session_invalid_state(test_session, auth_headers, db_session):
    """Test 400 when session in invalid state"""
    # Set session state to something invalid
    test_session.session_state = "abandoned"
    db_session.commit()

    response = client.post(
        f"/api/v1/osce-sessions/{test_session.attempt_id}/finalize",
        headers=auth_headers
    )

    assert response.status_code == 400
    assert "cannot finalize" in response.json()["error"]["message"].lower()


@patch('src.api.v1.osce_sessions.AIExaminerService')
def test_finalize_session_ai_examiner_failure(mock_examiner, test_session, auth_headers):
    """Test 500 when AI Examiner service fails"""
    # Mock AI Examiner to raise exception
    mock_examiner_instance = MagicMock()
    mock_examiner.return_value = mock_examiner_instance
    mock_examiner_instance.score_session.side_effect = Exception("API rate limit exceeded")

    response = client.post(
        f"/api/v1/osce-sessions/{test_session.attempt_id}/finalize",
        headers=auth_headers
    )

    assert response.status_code == 500
    assert "ai examiner" in response.json()["error"]["message"].lower()


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

@patch('src.api.v1.osce_sessions.AIExaminerService')
@patch('src.api.v1.osce_sessions.CriticalErrorDetector')
def test_finalize_session_performance(
    mock_detector,
    mock_examiner,
    test_session,
    auth_headers
):
    """Test scoring completes within 5 seconds"""
    import time

    # Mock services
    mock_examiner_instance = MagicMock()
    mock_examiner.return_value = mock_examiner_instance
    mock_examiner_instance.score_session.return_value = {
        "communication_score": 2,
        "communication_feedback": "Good",
        "clinical_reasoning_score": 2,
        "clinical_reasoning_feedback": "Good",
        "information_gathering_score": 2,
        "information_gathering_feedback": "Good",
        "management_score": 1,
        "management_feedback": "Good",
        "professionalism_score": 1,
        "professionalism_feedback": "Good",
        "total_score": 8,
        "strengths": [],
        "areas_for_improvement": [],
        "overall_feedback": "Okay"
    }

    mock_detector_instance = MagicMock()
    mock_detector.return_value = mock_detector_instance
    mock_detector_instance.detect_errors.return_value = []

    # Execute with timing
    start = time.time()
    response = client.post(
        f"/api/v1/osce-sessions/{test_session.attempt_id}/finalize",
        headers=auth_headers
    )
    duration = time.time() - start

    assert response.status_code == 200
    assert duration < 5.0  # Must complete within 5 seconds
```

### File 4: `frontend/src/components/osce/__tests__/OSCEResults.test.tsx` (+150 lines)

**Purpose**: Component tests for OSCEResults

**Implementation**:

```typescript
// frontend/src/components/osce/__tests__/OSCEResults.test.tsx

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { OSCEResults } from '../OSCEResults';
import '@testing-library/jest-dom';

// ============================================================================
// TEST DATA
// ============================================================================

const mockPassingResult = {
  attempt_id: '9d76cd2a-5ad0-4e01-835a-3ce995023367',
  persona_name: 'Emma Wilson',
  persona_code: 'general_practice_062_type_female_64',
  session_duration: 480,
  started_at: '2026-03-21T20:58:12.482660+00:00',
  ended_at: '2026-03-21T21:06:12.482660+00:00',
  scores: {
    communication: { score: 3, max: 3, feedback: 'Excellent rapport' },
    clinical_reasoning: { score: 3, max: 4, feedback: 'Good differential' },
    information_gathering: { score: 3, max: 4, feedback: 'Systematic history' },
    management: { score: 2, max: 2, feedback: 'Appropriate plan' },
    professionalism: { score: 2, max: 2, feedback: 'Professional' },
    total: { score: 13, max: 15 },
  },
  result: {
    pass_fail: 'PASS' as const,
    pass_threshold: 9,
    percentage: 86.7,
  },
  feedback: {
    strengths: ['Good communication', 'Systematic approach'],
    areas_for_improvement: ['Could explore red flags more'],
    overall: 'Strong performance overall',
  },
  critical_errors: [],
  scored_at: '2026-03-21T21:06:15.123456+00:00',
};

const mockFailingResultWithCriticalErrors = {
  ...mockPassingResult,
  scores: {
    ...mockPassingResult.scores,
    total: { score: 15, max: 15 }, // Perfect score
  },
  result: {
    pass_fail: 'FAIL' as const,
    pass_threshold: 9,
    percentage: 100,
  },
  critical_errors: [
    {
      rule_id: 'CE001',
      name: 'Missed acute red flag - chest pain',
      description: 'Failed to order ECG for chest pain presentation',
      category: 'acute_care',
      evidence: 'Patient mentioned chest pain but student did not order ECG',
    },
  ],
};

// ============================================================================
// TESTS: RENDERING
// ============================================================================

describe('OSCEResults - Rendering', () => {
  test('renders PASS badge for passing result', () => {
    render(<OSCEResults {...mockPassingResult} />);

    const passBadge = screen.getByLabelText(/session result: pass/i);
    expect(passBadge).toBeInTheDocument();
    expect(passBadge).toHaveTextContent('PASS');
  });

  test('renders FAIL badge for failing result', () => {
    const failingResult = {
      ...mockPassingResult,
      scores: { ...mockPassingResult.scores, total: { score: 7, max: 15 } },
      result: { pass_fail: 'FAIL' as const, pass_threshold: 9, percentage: 46.7 },
    };

    render(<OSCEResults {...failingResult} />);

    const failBadge = screen.getByLabelText(/session result: fail/i);
    expect(failBadge).toBeInTheDocument();
    expect(failBadge).toHaveTextContent('FAIL');
  });

  test('displays total score correctly', () => {
    render(<OSCEResults {...mockPassingResult} />);

    const totalScore = screen.getByLabelText(/total score/i);
    expect(totalScore).toHaveTextContent('13 / 15');

    const percentage = screen.getByText('86.7%');
    expect(percentage).toBeInTheDocument();
  });

  test('displays all 5 category scores', () => {
    render(<OSCEResults {...mockPassingResult} />);

    expect(screen.getByText('Communication')).toBeInTheDocument();
    expect(screen.getByText('Clinical Reasoning')).toBeInTheDocument();
    expect(screen.getByText('Information Gathering')).toBeInTheDocument();
    expect(screen.getByText('Management')).toBeInTheDocument();
    expect(screen.getByText('Professionalism')).toBeInTheDocument();
  });

  test('displays category feedback', () => {
    render(<OSCEResults {...mockPassingResult} />);

    expect(screen.getByText('Excellent rapport')).toBeInTheDocument();
    expect(screen.getByText('Good differential')).toBeInTheDocument();
    expect(screen.getByText('Systematic history')).toBeInTheDocument();
  });
});

// ============================================================================
// TESTS: CRITICAL ERRORS
// ============================================================================

describe('OSCEResults - Critical Errors', () => {
  test('displays critical errors alert when errors exist', () => {
    render(<OSCEResults {...mockFailingResultWithCriticalErrors} />);

    const alert = screen.getByText(/critical safety errors detected/i);
    expect(alert).toBeInTheDocument();
  });

  test('shows error details for each critical error', () => {
    render(<OSCEResults {...mockFailingResultWithCriticalErrors} />);

    expect(screen.getByText(/missed acute red flag - chest pain/i)).toBeInTheDocument();
    expect(screen.getByText(/failed to order ecg/i)).toBeInTheDocument();
    expect(screen.getByText(/patient mentioned chest pain but student did not order ecg/i)).toBeInTheDocument();
  });

  test('does not show critical errors alert when no errors', () => {
    render(<OSCEResults {...mockPassingResult} />);

    const alert = screen.queryByText(/critical safety errors detected/i);
    expect(alert).not.toBeInTheDocument();
  });

  test('shows FAIL even with perfect score when critical errors present', () => {
    render(<OSCEResults {...mockFailingResultWithCriticalErrors} />);

    // Perfect score displayed
    expect(screen.getByLabelText(/total score/i)).toHaveTextContent('15 / 15');
    expect(screen.getByText('100%')).toBeInTheDocument();

    // But still FAIL
    const failBadge = screen.getByLabelText(/session result: fail/i);
    expect(failBadge).toBeInTheDocument();
  });
});

// ============================================================================
// TESTS: FEEDBACK
// ============================================================================

describe('OSCEResults - Feedback', () => {
  test('displays strengths list', () => {
    render(<OSCEResults {...mockPassingResult} />);

    expect(screen.getByText(/strengths/i)).toBeInTheDocument();
    expect(screen.getByText('Good communication')).toBeInTheDocument();
    expect(screen.getByText('Systematic approach')).toBeInTheDocument();
  });

  test('displays areas for improvement list', () => {
    render(<OSCEResults {...mockPassingResult} />);

    expect(screen.getByText(/areas for improvement/i)).toBeInTheDocument();
    expect(screen.getByText('Could explore red flags more')).toBeInTheDocument();
  });

  test('displays overall feedback', () => {
    render(<OSCEResults {...mockPassingResult} />);

    expect(screen.getByText(/overall feedback/i)).toBeInTheDocument();
    expect(screen.getByText('Strong performance overall')).toBeInTheDocument();
  });
});

// ============================================================================
// TESTS: INTERACTIONS
// ============================================================================

describe('OSCEResults - Interactions', () => {
  test('calls onTryAgain when Try Again button clicked', () => {
    const handleTryAgain = jest.fn();
    render(<OSCEResults {...mockPassingResult} onTryAgain={handleTryAgain} />);

    const tryAgainButton = screen.getByLabelText(/try this scenario again/i);
    fireEvent.click(tryAgainButton);

    expect(handleTryAgain).toHaveBeenCalledTimes(1);
  });

  test('calls onReviewTranscript when Review Transcript button clicked', () => {
    const handleReview = jest.fn();
    render(<OSCEResults {...mockPassingResult} onReviewTranscript={handleReview} />);

    const reviewButton = screen.getByLabelText(/review conversation transcript/i);
    fireEvent.click(reviewButton);

    expect(handleReview).toHaveBeenCalledTimes(1);
  });

  test('calls onGenerateStudyCards when Generate Study Cards button clicked', () => {
    const handleGenerate = jest.fn();
    render(<OSCEResults {...mockPassingResult} onGenerateStudyCards={handleGenerate} />);

    const generateButton = screen.getByLabelText(/generate study cards/i);
    fireEvent.click(generateButton);

    expect(handleGenerate).toHaveBeenCalledTimes(1);
  });
});

// ============================================================================
// TESTS: ACCESSIBILITY
// ============================================================================

describe('OSCEResults - Accessibility', () => {
  test('has proper ARIA labels for all interactive elements', () => {
    render(<OSCEResults {...mockPassingResult} />);

    expect(screen.getByLabelText(/session result/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/total score/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/communication score/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/try this scenario again/i)).toBeInTheDocument();
  });

  test('displays formatted duration', () => {
    render(<OSCEResults {...mockPassingResult} />);

    const duration = screen.getByText(/session duration: 8:00/i);
    expect(duration).toBeInTheDocument();
  });
});
```

---

## H - HANDOFF (Delivery & Validation)

### Acceptance Criteria Checklist

#### Functionality
- [ ] **API Endpoint Created**: `POST /api/v1/osce-sessions/{attempt_id}/finalize` returns 200 with scores
- [ ] **Session Finalization**: Updates `ai_osce_attempts` table with `ended_at`, `duration_seconds`, `session_state='finalized'`
- [ ] **AI Examiner Integration**: Calls `src/ai/ai_examiner.py` with conversation transcript
- [ ] **Score Structure**: Returns 5 category scores (Communication 0-3, Clinical Reasoning 0-4, Information Gathering 0-4, Management 0-2, Professionalism 0-2, Total 0-15)
- [ ] **Critical Error Detection**: Checks 25+ safety rules using `src/ai/scoring/critical_errors.py`
- [ ] **Auto-Fail Logic**: Sets `pass_fail="FAIL"` if critical errors exist, even with 15/15 score
- [ ] **Database Storage**: Inserts complete results into `ai_osce_scores` table
- [ ] **Idempotency**: Calling finalize twice returns cached result (no duplicate AI calls)
- [ ] **Authorization**: Only session owner can finalize (403 for unauthorized users)
- [ ] **Error Handling**: Graceful error messages for not found (404), invalid state (400), AI service failure (500)

#### Frontend Display
- [ ] **OSCEResults Component**: Renders without TypeScript errors
- [ ] **Pass/Fail Badge**: Green "PASS" or red "FAIL" chip displayed prominently
- [ ] **Total Score**: Displays score/max and percentage
- [ ] **Category Breakdown**: All 5 categories shown with progress bars and feedback
- [ ] **Critical Errors Alert**: Red alert box appears when critical errors exist
- [ ] **Feedback Sections**: Strengths, Areas for Improvement, Overall Feedback displayed
- [ ] **Action Buttons**: Try Again, Review Transcript, Generate Study Cards functional
- [ ] **Accessibility**: WCAG 2.2 AA compliant (ARIA labels, keyboard navigation, color contrast ≥4.5:1)

#### Performance
- [ ] **Scoring Latency**: <5 seconds (p95) end-to-end response time
- [ ] **Database Query**: <50ms for session retrieval
- [ ] **Claude API**: <3 seconds for AI Examiner response

#### Security
- [ ] **No Hardcoded Credentials**: All secrets from Vault (grep check passes)
- [ ] **JWT Validation**: User authorization verified before scoring
- [ ] **SQL Injection Prevention**: Parameterized queries only
- [ ] **Rate Limiting**: Max 10 finalize requests per minute per user enforced

#### Testing
- [ ] **Backend Unit Tests**: 10/10 tests passing in `test_osce_finalize.py`
- [ ] **Frontend Component Tests**: 15/15 tests passing in `OSCEResults.test.tsx`
- [ ] **Integration Tests**: E2E workflow test passing (create session → finalize → view results)
- [ ] **Test Coverage**: ≥80% coverage for new code

### Testing Requirements

#### Unit Tests (Backend)

```bash
# Run backend unit tests
cd /home/dev/Development/irStudy/backend
pytest tests/test_api/test_osce_finalize.py -v --tb=short

# Expected output:
# ================== test session starts ==================
# tests/test_api/test_osce_finalize.py::test_finalize_session_success PASSED
# tests/test_api/test_osce_finalize.py::test_finalize_session_with_critical_errors_auto_fail PASSED
# tests/test_api/test_osce_finalize.py::test_finalize_session_not_found PASSED
# tests/test_api/test_osce_finalize.py::test_finalize_session_unauthorized PASSED
# tests/test_api/test_osce_finalize.py::test_finalize_session_already_finalized PASSED
# tests/test_api/test_osce_finalize.py::test_finalize_session_invalid_state PASSED
# tests/test_api/test_osce_finalize.py::test_finalize_session_ai_examiner_failure PASSED
# tests/test_api/test_osce_finalize.py::test_finalize_session_performance PASSED
# ================== 10 passed in 2.34s ==================
```

#### Component Tests (Frontend)

```bash
# Run frontend component tests
cd /home/dev/Development/irStudy/frontend
npm test -- OSCEResults.test.tsx

# Expected output:
# PASS src/components/osce/__tests__/OSCEResults.test.tsx
#   OSCEResults - Rendering
#     ✓ renders PASS badge for passing result (45 ms)
#     ✓ renders FAIL badge for failing result (32 ms)
#     ✓ displays total score correctly (28 ms)
#     ✓ displays all 5 category scores (35 ms)
#     ✓ displays category feedback (30 ms)
#   OSCEResults - Critical Errors
#     ✓ displays critical errors alert when errors exist (40 ms)
#     ✓ shows error details for each critical error (35 ms)
#     ✓ does not show critical errors alert when no errors (25 ms)
#     ✓ shows FAIL even with perfect score when critical errors present (38 ms)
#   OSCEResults - Feedback
#     ✓ displays strengths list (30 ms)
#     ✓ displays areas for improvement list (28 ms)
#     ✓ displays overall feedback (25 ms)
#   OSCEResults - Interactions
#     ✓ calls onTryAgain when Try Again button clicked (35 ms)
#     ✓ calls onReviewTranscript when Review Transcript button clicked (32 ms)
#     ✓ calls onGenerateStudyCards when Generate Study Cards button clicked (30 ms)
#   OSCEResults - Accessibility
#     ✓ has proper ARIA labels for all interactive elements (40 ms)
#     ✓ displays formatted duration (20 ms)
#
# Test Suites: 1 passed, 1 total
# Tests:       15 passed, 15 total
# Time:        2.456 s
```

#### E2E Tests (Playwright)

```typescript
// frontend/e2e/osce-scoring.spec.ts

import { test, expect } from '@playwright/test';

test('Complete OSCE workflow with scoring', async ({ page }) => {
  // 1. Login
  await page.goto('http://localhost:5173/login');
  await page.fill('[name="email"]', 'student@test.com');
  await page.fill('[name="password"]', 'TestPassword123');
  await page.click('button[type="submit"]');
  await expect(page).toHaveURL(/dashboard/);

  // 2. Navigate to OSCE Practice
  await page.goto('http://localhost:5173/osce-practice');
  await expect(page.locator('h1')).toContainText('OSCE Practice');

  // 3. Select persona and start session
  await page.click('[data-testid="persona-card"]:first-child');
  await page.click('button:has-text("Start Session")');

  // Wait for WebSocket connection
  await expect(page.locator('[data-testid="chat-interface"]')).toBeVisible();

  // 4. Send 5 messages
  for (let i = 1; i <= 5; i++) {
    await page.fill('[aria-label="Chat message input"]', `Message ${i}: Tell me about your symptoms`);
    await page.click('[aria-label="Send message"]');
    await page.waitForSelector('[data-testid="ai-message"]', { timeout: 5000 });
  }

  // 5. End session
  await page.click('button:has-text("End Session")');
  await page.click('button:has-text("Confirm")');

  // 6. Wait for scoring (up to 10 seconds)
  await page.waitForSelector('[data-testid="osce-results"]', { timeout: 10000 });

  // 7. Verify results displayed
  await expect(page.locator('[data-testid="total-score"]')).toBeVisible();
  await expect(page.locator('[data-testid="total-score"]')).toContainText('/15');

  const passFailBadge = page.locator('[aria-label*="Session result"]');
  await expect(passFailBadge).toBeVisible();

  // 8. Verify all categories shown
  await expect(page.locator('text=Communication')).toBeVisible();
  await expect(page.locator('text=Clinical Reasoning')).toBeVisible();
  await expect(page.locator('text=Information Gathering')).toBeVisible();
  await expect(page.locator('text=Management')).toBeVisible();
  await expect(page.locator('text=Professionalism')).toBeVisible();

  // 9. Verify feedback sections
  await expect(page.locator('text=Strengths')).toBeVisible();
  await expect(page.locator('text=Areas for Improvement')).toBeVisible();
  await expect(page.locator('text=Overall Feedback')).toBeVisible();

  // 10. Verify action buttons
  await expect(page.locator('button:has-text("Try Again")')).toBeVisible();
  await expect(page.locator('button:has-text("Review Transcript")')).toBeVisible();
  await expect(page.locator('button:has-text("Generate Study Cards")')).toBeVisible();
});

test('Critical error auto-fail displays correctly', async ({ page }) => {
  // This test would require a persona with known critical error triggers
  // Skipped in automated CI, manual test required
});
```

### Validation Commands

```bash
# ============================================================================
# BACKEND VALIDATION
# ============================================================================

# 1. TypeScript validation (ensure no compilation errors)
cd /home/dev/Development/irStudy/backend
python -m py_compile src/api/v1/osce_sessions.py
# Expected: No output (success)

# 2. Run unit tests
pytest tests/test_api/test_osce_finalize.py -v
# Expected: 10/10 tests passed

# 3. Security scan (check for hardcoded credentials)
grep -r "ANTHROPIC_API_KEY\|sk-ant-" src/api/v1/osce_sessions.py
# Expected: 0 matches

# 4. Lint check
flake8 src/api/v1/osce_sessions.py --max-line-length=100
# Expected: 0 errors

# 5. Test coverage
pytest tests/test_api/test_osce_finalize.py --cov=src.api.v1.osce_sessions --cov-report=term
# Expected: ≥80% coverage

# ============================================================================
# FRONTEND VALIDATION
# ============================================================================

# 6. TypeScript compilation
cd /home/dev/Development/irStudy/frontend
npx tsc --noEmit
# Expected: 0 errors

# 7. Component tests
npm test -- OSCEResults.test.tsx
# Expected: 15/15 tests passed

# 8. Build test
npm run build
# Expected: Build succeeded

# 9. Lint check
npm run lint
# Expected: 0 errors

# 10. Accessibility audit (manual)
npm run storybook
# Then: Navigate to OSCEResults story
# Verify: Color contrast ≥4.5:1, keyboard navigation works, ARIA labels present

# ============================================================================
# INTEGRATION VALIDATION
# ============================================================================

# 11. Start dev servers
tmux new-session -d -s irstudy-test
tmux send-keys -t irstudy-test "cd backend && source venv/bin/activate && uvicorn src.main:app --reload" C-m
tmux split-window -t irstudy-test
tmux send-keys -t irstudy-test "cd frontend && npm run dev" C-m

# Wait for servers to start
sleep 5

# 12. E2E test
cd /home/dev/Development/irStudy/frontend
npx playwright test e2e/osce-scoring.spec.ts
# Expected: 1/1 scenarios passed

# 13. Performance test (manual)
curl -w "@curl-format.txt" -o /dev/null -s -X POST \
  "http://localhost:8001/api/v1/osce-sessions/{attempt_id}/finalize" \
  -H "Authorization: Bearer {token}"
# Expected: total_time < 5.0s

# 14. Stop test servers
tmux kill-session -t irstudy-test
```

### Security Validation

```bash
# Check for hardcoded API keys
grep -r "sk-ant-\|ANTHROPIC_API_KEY.*=" backend/src/api/v1/osce_sessions.py
# Expected: 0 matches

# Check for SQL injection vulnerabilities
grep -r "execute(.*f\"" backend/src/api/v1/osce_sessions.py
# Expected: 0 matches (should use parameterized queries)

# Check for XSS vulnerabilities (frontend)
grep -r "dangerouslySetInnerHTML" frontend/src/components/osce/OSCEResults.tsx
# Expected: 0 matches
```

### Performance Benchmarks

```bash
# API response time test (requires active session)
curl -w "total_time: %{time_total}s\n" -o /dev/null -s -X POST \
  "http://localhost:8001/api/v1/osce-sessions/9d76cd2a-5ad0-4e01-835a-3ce995023367/finalize" \
  -H "Authorization: Bearer eyJhbGciOi..."
# Expected: total_time < 5.0s (p95)

# Database query performance
psql -U postgres -d irstudy_medical -c "
  EXPLAIN ANALYZE
  SELECT * FROM ai_osce_attempts WHERE attempt_id = '9d76cd2a-5ad0-4e01-835a-3ce995023367';
"
# Expected: Execution time < 50ms
```

---

## Agent OS Expert Constraints

### Agent: python-backend-developer

**CRITICAL - Read These Files FIRST** (T-RALPH v2.1):
1. **Global Constraints (ALL projects)**: `/home/dev/Development/ralph-dashboard/docs/specifications/prd-standards/RALPH_GLOBAL_CONSTRAINTS.md`
   - Section 4: Quality Gates (compilation, tests, security - zero tolerance)
   - Section 6: Security Standards (no hardcoded credentials - zero tolerance)
2. **PROJECT_CONSTRAINTS.md**: `/home/dev/Development/irStudy/PROJECT_CONSTRAINTS.md`
   - Section 1: Medical Accuracy (Australian standards, eTG, PBS, AHPRA)
   - Section 3: Security (NEVER hardcode API keys)
   - Section 4: LLM Integration (Claude API usage)
   - Section 6: Testing (100% pass rate mandatory)
3. **Existing Code**: Search for similar implementations before creating new code

**Validation Checklist** (Complete before returning):
- [ ] Read PROJECT_CONSTRAINTS.md sections 1, 3, 4, 6
- [ ] Followed existing patterns (provide file:line references)
- [ ] `pytest tests/test_api/test_osce_finalize.py -v` → 10/10 passed (100% pass rate)
- [ ] `grep -r "sk-ant-\|ANTHROPIC_API_KEY\s*=" src/` → 0 matches (zero tolerance)
- [ ] `flake8 src/api/v1/osce_sessions.py` → 0 errors
- [ ] Performance: Scoring completes in <5s (measured with real Claude API)

**1. Existing Code Integration (MUST FOLLOW)**:
- **DO NOT recreate AI Examiner logic** - Use existing `src/ai/ai_examiner.py` service
- **DO NOT recreate Critical Error Detector** - Use existing `src/ai/scoring/critical_errors.py`
- **Follow existing API patterns** - See `src/api/v1/patient_personas.py` for router structure
- **Use existing auth dependencies** - `get_current_active_user` from `src/auth/dependencies.py`
- **Match database models** - Use `OSCEAttemptAI`, `OSCEScoreAI`, `PatientPersona` from `src/db/models.py`

**2. Australian Medical Standards (MUST ENFORCE)**:
- Use "paracetamol" (not "acetaminophen")
- Reference eTG (Therapeutic Guidelines), AHPRA, AMH in feedback
- Emergency number: 000 (not 911)
- SI units (mmol/L not mg/dL)

**3. Security Requirements (MUST MEET)** (See Global Constraints Section 6):
- NO hardcoded API keys - Use Vault secrets (zero tolerance)
- Parameterized SQL queries only (prevent injection)
- JWT validation on all endpoints
- Rate limiting: 10 requests/minute per user

**4. Performance Requirements (MUST ACHIEVE)** (See Global Constraints Section 8):
- Total response time: <5 seconds (p95)
- Database queries: <50ms
- Claude API call: <3 seconds

### Agent: react-frontend-developer

**CRITICAL - Read These Files FIRST** (T-RALPH v2.1):
1. **Global Constraints (ALL projects)**: `/home/dev/Development/ralph-dashboard/docs/specifications/prd-standards/RALPH_GLOBAL_CONSTRAINTS.md`
   - Section 4: Quality Gates (TypeScript, tests, linting - zero tolerance)
   - Section 6: Security Standards (no hardcoded API keys)
   - Section 7: Documentation Standards (code comments, JSDoc)
2. **PROJECT_CONSTRAINTS.md**: `/home/dev/Development/irStudy/PROJECT_CONSTRAINTS.md`
   - Section 2: Code Architecture (React patterns, component structure)
   - Section 6: Testing (100% pass rate mandatory)
3. **Existing Code**: See `frontend/src/components/osce/WebSocketChat.tsx` for patterns

**Validation Checklist** (Complete before returning):
- [ ] Read PROJECT_CONSTRAINTS.md sections 2, 6
- [ ] Followed existing patterns: WebSocketChat.tsx (provide line references)
- [ ] `npx tsc --noEmit` → 0 errors (zero tolerance)
- [ ] `npm test -- OSCEResults.test.tsx` → 15/15 passed (100% pass rate)
- [ ] `npm run lint` → 0 errors
- [ ] `npm run build` → Build succeeds
- [ ] Accessibility: Color contrast ≥4.5:1, keyboard navigation works

**1. Material-UI Patterns (MUST FOLLOW)**:
- Use Material-UI 7 components (`@mui/material`)
- Follow existing component structure: See `frontend/src/components/osce/WebSocketChat.tsx`
- Use `styled()` API for custom styling (not CSS files)
- Theme-aware components (support light/dark mode)

**2. TypeScript Standards (MUST ENFORCE)**:
- NO `any` types allowed
- Strict null checking enabled
- Proper interface definitions for all props
- Component file naming: PascalCase (`OSCEResults.tsx`)

**3. Accessibility Requirements (MUST MEET)** (See Global Constraints Section 7):
- WCAG 2.2 AA compliance
- All interactive elements have `aria-label`
- Color contrast ≥4.5:1
- Keyboard navigation works (Tab, Enter)
- Screen reader announces score changes

**4. Performance Requirements (MUST ACHIEVE)** (See Global Constraints Section 8):
- Component render time: <100ms
- Smooth animations: 60fps
- No layout shift when scores load

---

## Files to Create/Modify

### Created (4 files)
- `backend/src/api/v1/osce_sessions.py` (+180 lines) - Finalize endpoint implementation
- `frontend/src/components/osce/OSCEResults.tsx` (+350 lines) - Results display component
- `backend/tests/test_api/test_osce_finalize.py` (+200 lines) - Backend unit/integration tests
- `frontend/src/components/osce/__tests__/OSCEResults.test.tsx` (+150 lines) - Frontend component tests

### Modified (2 files)
- `backend/src/api/v1/router.py` (+2 lines) - Import osce_sessions router if not already imported
- `frontend/src/api/osce.ts` (+15 lines) - Add `finalizeSession()` API client function

**Total Lines**: ~900 lines of production code + tests

---

**End of PRD-P1-004-AI-EXAMINER-SCORING-INTEGRATION**
**Next PRD**: PRD-P1-005-AUTO-STUDY-CARD-GENERATION (2,400 lines)
**Estimated Total PRD Generation Time**: 2-3 hours for all 5 PRDs
