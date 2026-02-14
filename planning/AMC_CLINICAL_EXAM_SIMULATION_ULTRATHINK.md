# AMC Clinical Exam Simulation - Comprehensive Ultrathink Plan

**Document Type:** Master Implementation Plan (Ultrathink)
**Focus:** AI Patient + AI Examiner + WebRTC Interface + Agent Architecture
**Created:** 2026-02-06
**Status:** Ready for Mid-term Implementation (1-3 months)
**Owner:** PM + AI/ML Engineer + Full-Stack Developer

---

## 📋 Executive Summary

This document consolidates all planning for the **AMC Clinical Examination Simulator** - an AI-powered clinical exam preparation system with conversational AI patients, real-time examiner scoring, and browser-based video/audio interface.

**What Makes This "Ultrathink":**
- Integrates existing Phase 3 plan (1,320 lines of specifications)
- Adds comprehensive agent architecture (6 new SIM-* agents)
- Leverages existing 46-agent medical education infrastructure
- Provides high-level architecture decisions for mid-term timeline
- Includes integration points with EMR Practice System and RAG

**Key Components:**
1. **AI Patient Agent (SIM-001)** - Conversational roleplay with emotional states
2. **AI Examiner Agent (SIM-002)** - 15-mark AMC rubric scoring
3. **OSCE Session Orchestrator (SIM-003)** - WebSocket manager, timer, state machine
4. **Conversation Context Manager (SIM-004)** - History tracking, information graph
5. **Physical Exam Simulator (SIM-005)** - Future enhancement
6. **OSCE Performance Analytics (SIM-006)** - Pattern analysis, recommendations

**Success Metrics:**
- AI patient realism: 90%+ user satisfaction
- Examiner scoring accuracy: ±2 marks vs. human examiners
- WebRTC uptime: 99%+
- End-to-end latency: <3 seconds
- Pass mark calibration: 9/15 validated against AMC standards

---

## 🎯 Goals & Objectives

### Primary Goals

1. **Create Realistic Clinical Exam Experience**
   - AI patient that stays in character with emotional states
   - Real-time scoring using validated AMC rubrics
   - 8-minute timed stations matching actual AMC format
   - Browser-based interface (no downloads required)

2. **Leverage Existing Infrastructure**
   - Use existing 140 OSCE scenarios (cardiology: 50, respiratory: 50, psychiatry: 40)
   - Integrate with 46-agent medical education system
   - Reuse LangGraph orchestration patterns
   - Utilize FastAPI + Redis + PostgreSQL stack

3. **Ensure Australian Medical Standards**
   - Australian terminology enforcement (QA-001 validation)
   - AMC Clinical Examination rubric compliance
   - PBS/MBS context where relevant
   - eTG guidelines integration

### Secondary Goals

1. **Multi-modal Communication** (Future)
   - Voice synthesis (ElevenLabs - Australian accents)
   - Speech-to-text (OpenAI Whisper)
   - Video avatars for patient display

2. **Advanced Analytics**
   - Performance tracking across attempts
   - Pattern recognition (common mistakes)
   - Personalized improvement recommendations
   - Peer comparison (anonymized)

3. **Scalability**
   - Support 100+ concurrent sessions
   - Session recording and replay
   - Integration with EMR Practice System

---

## 🏗️ High-Level Architecture

### Four-Layer System

```
┌─────────────────────────────────────────────────────────────┐
│              PRESENTATION LAYER (Frontend)                   │
│  React 18 + TypeScript + WebRTC + WebSocket Client         │
│  - OSCE Station UI                                          │
│  - Patient Video/Avatar Display                             │
│  - Conversation Transcript                                  │
│  - Real-time Rubric Display                                 │
│  - Timer & Session Management                               │
└─────────────────────────────────────────────────────────────┘
                            ↓ WebSocket (JSON messages)
┌─────────────────────────────────────────────────────────────┐
│           ORCHESTRATION LAYER (Backend)                      │
│  FastAPI + WebSocket Manager + LangGraph Workflows         │
│  - SIM-003: OSCE Session Orchestrator                       │
│  - SIM-004: Conversation Context Manager                    │
│  - Message Routing & State Machine                          │
│  - Timer Management (8-minute countdown)                    │
└─────────────────────────────────────────────────────────────┘
                            ↓ Agent Invocation
┌─────────────────────────────────────────────────────────────┐
│            INTELLIGENCE LAYER (AI Agents)                    │
│  Claude 3.5 Sonnet + LangChain + Medical Experts           │
│  - SIM-001: AI Patient Agent (temp 0.7, natural)            │
│  - SIM-002: AI Examiner Agent (temp 0.1, consistent)        │
│  - QA-001: Australian Compliance (validation)               │
│  - QA-002: Clinical Accuracy (validation)                   │
└─────────────────────────────────────────────────────────────┘
                            ↓ Read/Write
┌─────────────────────────────────────────────────────────────┐
│              DATA LAYER (Storage)                            │
│  Redis (session state) + PostgreSQL (persistent records)   │
│  - Patient Personas (200+ profiles)                         │
│  - OSCE Scenarios (140+ stations)                           │
│  - AMC Rubrics (15-mark scoring)                            │
│  - Session Transcripts & Scores                             │
│  - Performance Analytics Data                               │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow (Detailed)

```
1. User enters OSCE station
   ↓
2. Frontend: Load scenario, initialize WebSocket, start UI
   ↓ POST /api/ai-patient/start
3. SIM-003 (Orchestrator): Create session, load scenario
   ↓
4. SIM-001 (AI Patient): Load persona, prepare opening statement
   ↓ WebSocket connect
5. Frontend ← AI Patient: "Hello doctor, I've had chest pain for 2 days..."
   ↓
6. Candidate speaks (text or voice input)
   ↓ WebSocket message {type: "candidate_message", content: "..."}
7. SIM-004 (Context Manager): Store message, update info graph
   ↓
8. SIM-001 (AI Patient): Generate contextual response (emotion-aware)
   ↓ Parallel scoring
9. SIM-002 (AI Examiner): Analyze interaction, update rubric marks
   ↓ Loop for 8 minutes
10. [Conversation continues with message routing]
    ↓
11. Timer reaches 0 or candidate clicks "End Station"
    ↓
12. SIM-003: Finalize session, trigger final scoring
    ↓
13. SIM-002: Generate comprehensive feedback report
    ↓
14. SIM-006 (Analytics): Save performance, identify patterns
    ↓
15. Frontend: Display results (score, feedback, recommendations)
```

---

## 🤖 Agent Architecture & Specifications

### Overview of New Agents

| Agent ID | Name | Purpose | Base Class | Priority |
|----------|------|---------|------------|----------|
| SIM-001 | AI Patient Agent | Conversational roleplay | BaseMedicalExpert | P0 (CRITICAL) |
| SIM-002 | Clinical Examiner Agent | AMC rubric scoring | BaseAgent | P0 (CRITICAL) |
| SIM-003 | OSCE Session Orchestrator | WebSocket + state machine | BaseAgent | P0 (CRITICAL) |
| SIM-004 | Conversation Context Manager | History + info tracking | BaseAgent | P1 (High) |
| SIM-005 | Physical Exam Simulator | Exam findings | BaseAgent | P2 (Medium - Future) |
| SIM-006 | OSCE Performance Analytics | Pattern analysis | BaseAgent | P1 (High) |

---

### SIM-001: AI Patient Agent

**File Location:** `src/agents/simulation/sim_001_ai_patient.py`

**Purpose:**
Simulate realistic patient responses during OSCE stations with emotional states, progressive information disclosure, and natural conversation flow.

**Key Features:**
- **Conversational AI:** Claude 3.5 Sonnet (temperature 0.7) for natural, human-like responses
- **Emotional States:** 6 states (neutral, anxious, tearful, angry, confused, defensive)
- **Memory Management:** LangChain ConversationBufferMemory tracking conversation history
- **Information Gating:** Reveals key information progressively (not all at once)
- **Empathy Response:** Responds warmly to student's empathy and good communication
- **Australian Context:** Uses Australian medical terminology, Medicare, GP referrals

**Architecture:**
```python
class AIPatientAgent(BaseMedicalExpert):
    def __init__(self, patient_script: Dict, emotional_state: str):
        - patient_script: {name, age, gender, presenting_complaint, history,
                          key_information, concerns, background_context}
        - emotional_state: Current emotional state
        - memory: ConversationBufferMemory (LangChain)
        - llm: ChatAnthropic (claude-3-5-sonnet, temp 0.7, max_tokens 500)
        - system_prompt: Built dynamically based on patient script

    async def respond(self, student_message: str) -> str:
        - Add student message to memory
        - Build conversation history with system prompt
        - Get AI response from Claude
        - Add AI response to memory
        - Return patient's response (1-3 sentences typically)

    def update_emotional_state(self, new_state: str):
        - Update emotional state (affects future responses)

    def get_conversation_history(self) -> List[Dict[str, str]]:
        - Return full conversation (for scoring, analytics)

    def reset(self):
        - Clear conversation memory (for new attempts)
```

**System Prompt Structure:**
```
You are a patient in a medical consultation for AMC Clinical Examination.

PATIENT DETAILS:
- Name, age, gender
- Presenting complaint
- Background context

EMOTIONAL STATE:
[Specific instructions based on state: tearful, anxious, angry, etc.]

KEY INFORMATION TO DISCLOSE:
[List of information to reveal when asked appropriate questions]

PATIENT CONCERNS:
[What the patient is worried about]

ROLEPLAY INSTRUCTIONS:
1. Stay in character (not an AI)
2. Respond naturally (1-3 sentences)
3. Don't volunteer all information immediately
4. Show appropriate emotions
5. Be realistic (forget details sometimes, need clarification)
6. Respond positively to empathy
7. Use Australian English
```

**Integration Points:**
- **QA-001 (Australian Compliance):** Validates all AI patient responses for Australian terminology
- **SIM-003 (Orchestrator):** Receives candidate messages, sends patient responses
- **SIM-004 (Context Manager):** Provides conversation history for context
- **OSCE Loader Utility:** Loads patient script from OSCE JSON files

**Data Requirements:**
- **Patient Personas:** 200+ JSON profiles in `data/patient_personas/`
  - Demographics (name, age, gender, occupation)
  - Medical history (current illness, past medical history, medications)
  - Social history (smoking, alcohol, family)
  - Personality traits (cooperative, defensive, anxious, etc.)
  - Emotional baseline (what makes them tearful, angry, etc.)
  - Conversation style (verbose, concise, evasive, open)

**Validation Checklist:**
- [ ] Stays in character (no "As an AI..." responses)
- [ ] Emotional states reflected in responses
- [ ] Information disclosed progressively
- [ ] Responds positively to empathy
- [ ] Conversation flows naturally
- [ ] Australian terminology enforced
- [ ] Response length appropriate (1-3 sentences)
- [ ] No medical jargon unless patient script specifies

**Estimated Effort:** 15-20 hours

---

### SIM-002: Clinical Examiner Agent

**File Location:** `src/agents/simulation/sim_002_examiner.py`

**Purpose:**
Analyze candidate performance in real-time and generate scoring based on AMC 15-mark rubric with detailed feedback.

**Key Features:**
- **Rubric-Based Scoring:** 15-mark AMC system (5 categories × 3 marks each)
- **Real-Time Analysis:** Can score during conversation (practice mode) or at end (timed mode)
- **Structured Feedback:** Strengths, areas for improvement, specific examples
- **Critical Error Detection:** Patient safety violations, unprofessional behavior
- **Pass/Fail Determination:** 9/15 threshold (60%)
- **Consistency:** Low temperature (0.1) for reproducible scoring

**Architecture:**
```python
class AIExaminerAgent(BaseAgent):
    def __init__(self, rubric: Dict):
        - rubric: {total_marks, pass_mark, criteria, key_skills}
        - llm: ChatAnthropic (claude-3-5-sonnet, temp 0.1, max_tokens 2000)

    async def score_conversation(
        self,
        conversation_history: List[Dict],
        patient_script: Dict
    ) -> Dict:
        - Analyze full conversation transcript
        - Apply rubric criteria
        - Detect critical errors
        - Generate structured feedback
        - Return JSON scoring result

    async def score_in_real_time(
        self,
        conversation_history: List[Dict]
    ) -> Dict:
        - Provide interim scoring (every 2-3 minutes)
        - Used for practice mode feedback

    def _build_scoring_prompt(self, patient_script: Dict) -> str:
        - Construct system prompt with rubric + scenario context
```

**AMC 15-Mark Rubric Structure:**
```
1. History Taking / Examination Technique (0-3 marks)
   - 0: Did not perform, or major errors
   - 1: Performed with significant gaps
   - 2: Performed adequately, minor gaps
   - 3: Thorough, systematic, appropriate

2. Clinical Reasoning (0-3 marks)
   - 0: No differential, inappropriate questions
   - 1: Limited differential, basic questions
   - 2: Reasonable differential, appropriate questions
   - 3: Comprehensive differential, excellent questions

3. Communication Skills (0-3 marks)
   - 0: Poor rapport, interrupts, dismissive
   - 1: Basic communication, limited empathy
   - 2: Good communication, shows empathy
   - 3: Excellent communication, builds strong rapport

4. Patient Safety (0-3 marks)
   - 0: Significant safety concerns
   - 1: Some safety issues
   - 2: Safe approach, minor concerns
   - 3: Prioritizes safety, appropriate red flag identification

5. Professionalism (0-3 marks)
   - 0: Unprofessional behavior
   - 1: Minimal professionalism
   - 2: Professional, appropriate boundaries
   - 3: Exemplary professionalism

PASS MARK: 9/15 (60%)
```

**Scoring Output Format (JSON):**
```json
{
  "total_score": 12,
  "total_marks_possible": 15,
  "pass_mark": 9,
  "pass_fail": "PASS",
  "passed": true,
  "criteria_scores": [
    {
      "criterion": "History Taking",
      "marks_awarded": 2,
      "marks_possible": 3,
      "justification": "Systematic approach but missed social history"
    },
    ...
  ],
  "strengths": [
    "Excellent rapport building and empathy",
    "Systematic questioning using open to closed funnel",
    "Appropriate red flag identification"
  ],
  "areas_for_improvement": [
    "Expand social history (smoking, alcohol, occupation)",
    "Summarize findings back to patient",
    "Provide clearer safety-netting advice"
  ],
  "overall_feedback": "Strong performance with good communication skills. Focus on comprehensive history including social factors. Continue excellent empathy and rapport building.",
  "critical_errors": [],
  "timestamp": "2026-02-06T14:30:00Z"
}
```

**Integration Points:**
- **SIM-003 (Orchestrator):** Called at end of session or periodically (practice mode)
- **SIM-004 (Context Manager):** Receives full conversation history for analysis
- **QA-002 (Clinical Accuracy):** Validates scoring against medical guidelines
- **SIM-006 (Analytics):** Provides scoring data for pattern analysis

**Data Requirements:**
- **AMC Rubric Database:** `data/amc_rubrics/` directory
  - Station-specific rubrics (history taking, physical exam, communication, etc.)
  - Detailed scoring descriptors for each mark (0, 1, 2, 3)
  - Common mistakes database (what students often do wrong)
  - Red flags (automatic deductions for critical errors)

**Validation Checklist:**
- [ ] Scoring is consistent (same conversation ≈ same score, ±1 mark)
- [ ] Marks align with rubric criteria
- [ ] Feedback is constructive and specific (not generic)
- [ ] Pass/fail threshold correct (9/15)
- [ ] Edge cases handled (very short conversation, silent student)
- [ ] Critical errors detected (safety violations, unprofessional behavior)
- [ ] JSON output format valid

**Estimated Effort:** 15-20 hours

---

### SIM-003: OSCE Session Orchestrator

**File Location:** `src/agents/simulation/sim_003_orchestrator.py`

**Purpose:**
Manage entire 8-minute OSCE station lifecycle including WebSocket connections, message routing, timer management, and session state.

**Key Features:**
- **WebSocket Manager:** Handle real-time bidirectional communication
- **State Machine:** 4 phases (setup → active → warning@7min → complete@8min)
- **Message Routing:** Candidate ↔ AI Patient, with Examiner observing
- **Timer Management:** Server-side countdown with client synchronization
- **Session Persistence:** Save to Redis (active) + PostgreSQL (final)
- **Pause/Resume:** Support for technical issues
- **Emergency Stop:** Graceful shutdown on errors

**Architecture:**
```python
class OSCESessionOrchestrator(BaseAgent):
    def __init__(self):
        - active_sessions: Dict[str, SessionState]  # In-memory or Redis
        - websocket_manager: WebSocketConnectionManager
        - timer_tasks: Dict[str, asyncio.Task]
        - redis_client: Redis connection for session state
        - db: PostgreSQL connection for final records

    async def initialize_session(
        self,
        user_id: str,
        osce_id: str,
        mode: str  # 'practice' or 'timed'
    ) -> str:
        - Load OSCE scenario
        - Create patient persona (SIM-001)
        - Initialize examiner (SIM-002)
        - Create context manager (SIM-004)
        - Generate session_id
        - Store in Redis with TTL (2 hours)
        - Return session_id

    async def handle_websocket_connection(
        self,
        websocket: WebSocket,
        session_id: str
    ):
        - Accept WebSocket connection
        - Load session from Redis
        - Start timer (if timed mode)
        - Enter message routing loop
        - Handle disconnects gracefully

    async def route_message(
        self,
        session_id: str,
        message: Dict
    ):
        - Parse message type (candidate_message, pause, resume, end)
        - Store in context manager (SIM-004)
        - Route to AI patient (SIM-001)
        - Get patient response
        - Send to candidate via WebSocket
        - Optionally trigger scoring (SIM-002) if practice mode

    async def manage_timer(self, session_id: str, duration: int = 480):
        - Count down from 8 minutes (480 seconds)
        - Send time updates every 10 seconds
        - Send warning at 7 minutes (60 seconds remaining)
        - Auto-end at 0 seconds
        - Trigger final scoring

    async def finalize_session(self, session_id: str):
        - Stop timer
        - Get final conversation history from SIM-004
        - Trigger comprehensive scoring (SIM-002)
        - Save to PostgreSQL (osce_sessions table)
        - Clean up Redis session
        - Send final results to client

    async def pause_session(self, session_id: str):
        - Pause timer
        - Update session state

    async def resume_session(self, session_id: str):
        - Resume timer
        - Update session state
```

**Session State Structure (Redis):**
```json
{
  "session_id": "osce_abc123",
  "user_id": "user_456",
  "osce_id": "respiratory_001",
  "mode": "timed",
  "status": "active",
  "start_time": "2026-02-06T14:00:00Z",
  "elapsed_time": 120,
  "time_remaining": 360,
  "patient_agent_id": "sim001_abc",
  "examiner_agent_id": "sim002_abc",
  "context_manager_id": "sim004_abc",
  "conversation_turns": 15,
  "websocket_connected": true,
  "last_activity": "2026-02-06T14:02:00Z"
}
```

**WebSocket Message Protocol:**
```json
// Client → Server (Candidate message)
{
  "type": "candidate_message",
  "content": "How long have you had this cough?",
  "timestamp": 1707230400000,
  "audio_data": null  // Optional: for voice input
}

// Server → Client (Patient response)
{
  "type": "patient_response",
  "content": "It's been about 3 weeks now, doctor.",
  "timestamp": 1707230402000,
  "emotional_state": "anxious",
  "audio_url": "/api/audio/abc123.mp3"  // Optional: for voice output
}

// Server → Client (Timer update)
{
  "type": "timer_update",
  "time_remaining": 360,
  "is_warning": false
}

// Server → Client (Session ended)
{
  "type": "session_complete",
  "scoring_result": {...},
  "transcript": [...]
}
```

**Integration Points:**
- **FastAPI:** WebSocket endpoint at `/ws/osce/{session_id}`
- **Redis:** Session state storage with 2-hour TTL
- **PostgreSQL:** Final session records in `osce_sessions` table
- **SIM-001, SIM-002, SIM-004:** Coordinates all other simulation agents
- **Frontend:** WebSocket client connection

**Validation Checklist:**
- [ ] WebSocket connections stable (no unexpected disconnects)
- [ ] Timer accurate (±1 second over 8 minutes)
- [ ] Message routing correct (candidate → patient → examiner)
- [ ] Session state persists across server restarts (Redis backup)
- [ ] Pause/resume works correctly
- [ ] Emergency stop graceful (no data loss)
- [ ] Concurrent sessions supported (100+ simultaneous)

**Estimated Effort:** 20-25 hours

---

### SIM-004: Conversation Context Manager

**File Location:** `src/agents/simulation/sim_004_context.py`

**Purpose:**
Maintain conversation context across multiple turns including message history, information disclosed, and conversation flow analysis.

**Key Features:**
- **Conversation Buffer:** Store all messages with timestamps
- **Information Graph:** Track what candidate knows vs. doesn't know yet
- **Repetition Detection:** Identify when candidate asks same question twice
- **Context Summarization:** Keep LLM prompts under token limits
- **Session Persistence:** Redis-backed storage for durability

**Architecture:**
```python
class ConversationContextManager(BaseAgent):
    def __init__(self, session_id: str):
        - session_id: Unique session identifier
        - redis_client: Redis connection
        - message_buffer: List of messages (max 100 turns)
        - information_graph: Dict tracking disclosed info
        - repetition_tracker: Dict tracking question patterns

    async def store_message(
        self,
        role: str,  # 'candidate' or 'patient'
        content: str,
        metadata: Dict = None
    ):
        - Add message to buffer
        - Update information graph (if patient disclosed new info)
        - Check for repetition (candidate asking same thing)
        - Store in Redis
        - Return message_id

    async def get_context(
        self,
        max_tokens: int = 2000
    ) -> str:
        - Retrieve recent messages (last 10 turns or max_tokens)
        - Format for LLM injection
        - Include information graph summary
        - Return context string

    async def get_full_history(self) -> List[Dict]:
        - Retrieve all messages from session start
        - Include timestamps, metadata
        - Return for scoring or analytics

    async def track_information(self, info_key: str, disclosed: bool):
        - Update information graph
        - Mark key information as disclosed/not disclosed
        - Used to ensure AI patient reveals info progressively

    async def summarize_conversation(self) -> str:
        - Generate compressed summary of older messages
        - Keep recent messages verbatim
        - Used when conversation exceeds token limits

    async def analyze_flow(self) -> Dict:
        - Analyze conversation flow (smooth vs. choppy)
        - Detect interruptions (candidate cutting off patient)
        - Identify empathy moments
        - Return analytics for scoring
```

**Information Graph Structure:**
```json
{
  "presenting_complaint_discussed": true,
  "onset_duration_asked": true,
  "aggravating_factors_explored": false,
  "past_medical_history_covered": true,
  "medications_discussed": true,
  "social_history_asked": false,
  "patient_concerns_addressed": false,
  "red_flags_identified": ["chest_pain", "shortness_of_breath"],
  "empathy_moments": 3,
  "interruptions": 0,
  "repetitive_questions": ["duration of cough"],
  "total_turns": 18
}
```

**Integration Points:**
- **SIM-001 (AI Patient):** Provides context for generating appropriate responses
- **SIM-002 (Examiner):** Provides full history for scoring
- **SIM-003 (Orchestrator):** Stores every message routed
- **Redis:** Persistent storage with session TTL

**Validation Checklist:**
- [ ] All messages stored correctly (no loss)
- [ ] Information graph updated accurately
- [ ] Repetition detection works (catches same question twice)
- [ ] Context summarization maintains key information
- [ ] Redis persistence works (survives server restart)

**Estimated Effort:** 10-15 hours

---

### SIM-005: Physical Exam Simulator (Future)

**File Location:** `src/agents/simulation/sim_005_physical_exam.py`

**Purpose:**
Simulate physical examination findings when candidate performs examination maneuvers.

**Status:** P2 (Medium Priority - Future Enhancement)

**Key Features:**
- Respond to examination maneuvers ("Auscultate chest", "Palpate abdomen")
- Provide realistic findings based on scenario (normal vs. abnormal)
- Detect incorrect technique ("You didn't wash hands first", "No consent obtained")
- Image generation for visual findings (rashes, ECGs, X-rays)

**Architecture (Planned):**
```python
class PhysicalExamSimulator(BaseAgent):
    def __init__(self, exam_findings: Dict):
        - exam_findings: Expected findings for this scenario
        - technique_checker: Validates proper exam technique

    async def respond_to_maneuver(
        self,
        maneuver: str,
        technique: Dict
    ) -> Dict:
        - Parse examination maneuver
        - Check technique (proper positioning, consent, etc.)
        - Return findings (inspection, palpation, auscultation, etc.)
        - Optionally return image URL for visual findings
```

**Estimated Effort:** 15-20 hours (Future)

---

### SIM-006: OSCE Performance Analytics

**File Location:** `src/agents/analytics/study_001_osce_analytics.py` (Enhance Existing)

**Purpose:**
Analyze OSCE performance across multiple attempts, identify patterns, generate personalized recommendations.

**Key Features:**
- **Performance Tracking:** Store scores, feedback, timestamps for all attempts
- **Pattern Recognition:** Identify recurring mistakes (e.g., always misses social history)
- **Personalized Recommendations:** "Focus on empathy - 3/5 attempts scored <2 in communication"
- **Peer Comparison:** Anonymized benchmarks ("You're in top 30% for history taking")
- **Progress Visualization:** Score trends over time

**Architecture:**
```python
class OSCEPerformanceAnalytics(BaseAgent):
    def __init__(self, user_id: str):
        - user_id: User identifier
        - db: PostgreSQL connection

    async def analyze_performance(
        self,
        user_id: str,
        time_period: str = '30_days'
    ) -> Dict:
        - Query all OSCE attempts in time period
        - Calculate average scores by category
        - Identify improvement/decline trends
        - Compare to peer averages (anonymized)
        - Generate insights

    async def identify_patterns(self, user_id: str) -> List[Dict]:
        - Analyze common mistakes across attempts
        - Identify categories with consistently low scores
        - Return pattern insights with recommendations

    async def generate_recommendations(self, analysis: Dict) -> List[str]:
        - Based on performance patterns
        - Personalized study suggestions
        - Specific OSCE stations to retry

    async def get_progress_chart(self, user_id: str) -> Dict:
        - Time series data for visualization
        - Scores by date, category, OSCE type
```

**Integration Points:**
- **SIM-002 (Examiner):** Receives scoring results to analyze
- **PostgreSQL:** Queries `osce_sessions` table for historical data
- **Frontend:** Provides data for analytics dashboard

**Estimated Effort:** 10-15 hours

---

## 🔧 Technology Stack Decisions

### Backend Technologies

| Component | Technology | Rationale |
|-----------|------------|-----------|
| **Web Framework** | FastAPI 0.109.0 | Async support, WebSocket built-in, OpenAPI docs, already used |
| **LLM Client** | Anthropic Claude 3.5 Sonnet | Best conversational AI, long context (200K), existing infrastructure |
| **LLM Framework** | LangChain 0.1.0 | Conversation memory, prompt templates, already used |
| **Orchestration** | LangGraph | Workflow orchestration, already used for MCQ generation |
| **Real-time** | WebSocket (FastAPI) | Bidirectional, low-latency, standard protocol |
| **Session State** | Redis 7.x | In-memory, fast, pub/sub, TTL support, already configured |
| **Persistent Storage** | PostgreSQL 15.x | Relational, ACID, already configured |
| **Background Tasks** | Celery | Async tasks (scoring, analytics), already configured |
| **Voice Synthesis** | ElevenLabs API (Future) | Australian accents, emotional voices |
| **Speech-to-Text** | OpenAI Whisper (Future) | Medical terminology accuracy, multi-language |

### Frontend Technologies

| Component | Technology | Rationale |
|-----------|------------|-----------|
| **Framework** | React 18 + TypeScript | Existing stack, type safety, large ecosystem |
| **Build Tool** | Vite | Fast HMR, existing setup |
| **State Management** | Zustand | Simple, existing pattern |
| **API State** | TanStack Query | Caching, existing setup |
| **Styling** | Tailwind CSS 3.4+ | Utility-first, existing design system |
| **WebSocket Client** | react-use-websocket | React hooks for WebSocket, easy integration |
| **WebRTC** | SimpleWebRTC or native | Browser-based video/audio (future enhancement) |
| **Charts** | Recharts | Performance visualization |

### Infrastructure

| Component | Technology | Rationale |
|-----------|------------|-----------|
| **Container** | Docker + docker-compose | Existing setup (11 services) |
| **Web Server** | Nginx | Reverse proxy, already configured |
| **Monitoring** | Prometheus + Grafana | Metrics, dashboards, already configured |
| **CI/CD** | GitHub Actions | Existing workflows |

---

## 📦 Data Requirements

### 1. Patient Persona Database

**Location:** `data/patient_personas/`

**Format:** JSON files (one per persona)

**Structure:**
```json
{
  "persona_id": "persona_001",
  "demographics": {
    "name": "Sarah Mitchell",
    "age": 45,
    "gender": "Female",
    "occupation": "Primary school teacher"
  },
  "medical_history": {
    "current_illness": "3-week productive cough with fever",
    "past_medical_history": ["Type 2 diabetes", "Hypertension"],
    "medications": ["Metformin 500mg BD", "Perindopril 4mg daily"],
    "allergies": ["Penicillin (rash)"]
  },
  "social_history": {
    "smoking": "Never smoker",
    "alcohol": "Social drinker (2-3 standard drinks/week)",
    "occupation_exposure": "High exposure to children (potential infections)",
    "family_history": "Father had lung cancer (smoker)"
  },
  "personality_traits": {
    "baseline_emotion": "anxious",
    "communication_style": "open but worried",
    "health_literacy": "medium",
    "cooperation_level": "high",
    "emotional_triggers": ["mention of cancer", "invasive tests"]
  },
  "conversation_patterns": {
    "response_length": "medium (2-4 sentences)",
    "uses_medical_jargon": false,
    "interrupts": false,
    "asks_questions": true
  },
  "australian_context": {
    "medicare_number": "2123 45678 9",
    "has_gp": true,
    "gp_name": "Dr. Emma Thompson",
    "healthcare_card": false,
    "private_insurance": true
  }
}
```

**Quantity:** 200+ personas covering diverse demographics, medical conditions, and personality types

**Generation Method:**
- Use MED-* expert agents (Cardiology, Respiratory, etc.) to generate realistic personas
- QA-001 (Australian Compliance) validates terminology and context
- Manual curation for personality traits and conversation patterns

**Estimated Effort:** 40-50 hours

---

### 2. AMC Rubric Database

**Location:** `data/amc_rubrics/`

**Format:** JSON files per station type

**Structure:**
```json
{
  "rubric_id": "history_taking_respiratory",
  "station_type": "history_taking",
  "specialty": "respiratory",
  "total_marks": 15,
  "pass_mark": 9,
  "criteria": [
    {
      "category": "History Taking Technique",
      "marks_possible": 3,
      "descriptors": {
        "0": "Did not take history OR major errors compromising safety",
        "1": "Disorganized, many key areas missed, poor technique",
        "2": "Systematic approach with minor gaps (e.g., missed ICE)",
        "3": "Comprehensive, systematic, appropriate open/closed questions"
      },
      "key_elements": [
        "Appropriate greeting and introduction",
        "Open question to start",
        "OPQRST for presenting complaint",
        "Review of systems",
        "Past medical history",
        "Medications and allergies",
        "Social history (smoking, alcohol, occupation)",
        "ICE (Ideas, Concerns, Expectations)"
      ],
      "common_mistakes": [
        "Starts with closed questions only",
        "Interrupts patient before they finish speaking",
        "Misses social history entirely",
        "Doesn't address patient's concerns"
      ]
    },
    {
      "category": "Clinical Reasoning",
      "marks_possible": 3,
      "descriptors": {
        "0": "No differential diagnosis evident, inappropriate questions",
        "1": "Limited differential (1-2 diagnoses), basic questions only",
        "2": "Reasonable differential (3-4 diagnoses), appropriate questions",
        "3": "Comprehensive differential, excellent discriminating questions"
      },
      "key_elements": [
        "Questions targeted to differentiate causes",
        "Appropriate red flag questions",
        "Risk factor identification",
        "Severity assessment"
      ]
    },
    {
      "category": "Communication Skills",
      "marks_possible": 3,
      "descriptors": {
        "0": "Poor rapport, dismissive, interrupts frequently",
        "1": "Basic communication, limited empathy, medical jargon",
        "2": "Good rapport, shows empathy, mostly clear language",
        "3": "Excellent rapport, empathetic, patient-centered, clear language"
      },
      "key_elements": [
        "Appropriate eye contact and body language",
        "Active listening (not interrupting)",
        "Empathetic statements",
        "Checks understanding",
        "Avoids medical jargon or explains terms"
      ]
    },
    {
      "category": "Patient Safety",
      "marks_possible": 3,
      "descriptors": {
        "0": "Significant safety concerns (missed critical red flags)",
        "1": "Some safety issues (incomplete red flag assessment)",
        "2": "Safe approach with minor concerns",
        "3": "Prioritizes safety, comprehensive red flag identification"
      },
      "red_flags": [
        "Chest pain with exertion (cardiac)",
        "Hemoptysis (malignancy, TB, PE)",
        "Weight loss (malignancy)",
        "Night sweats (TB, lymphoma)",
        "Sudden onset dyspnea (PE, pneumothorax)"
      ]
    },
    {
      "category": "Professionalism",
      "marks_possible": 3,
      "descriptors": {
        "0": "Unprofessional behavior (e.g., judgmental, dismissive)",
        "1": "Minimal professionalism, some inappropriate comments",
        "2": "Professional, maintains appropriate boundaries",
        "3": "Exemplary professionalism, respectful, non-judgmental"
      }
    }
  ],
  "automatic_deductions": [
    {
      "violation": "Did not introduce self",
      "deduction": -1
    },
    {
      "violation": "Breached confidentiality",
      "deduction": -3
    },
    {
      "violation": "Unsafe advice given",
      "deduction": -5
    }
  ]
}
```

**Quantity:** 20-30 rubrics covering different station types and specialties

**Source:** AMC Clinical Examination guidelines + existing OSCE marking criteria

**Estimated Effort:** 10-15 hours (manual curation)

---

### 3. OSCE Scenario Enhancement

**Current State:** 140 scenarios in `data/osces/*.json`

**Enhancement Needed:** Map each scenario to patient persona and add conversation flow

**New Fields to Add:**
```json
{
  "id": "respiratory_001",
  "title": "Chronic Cough - Community Acquired Pneumonia",
  "persona_id": "persona_045",  // NEW: Link to patient persona
  "expected_flow": {  // NEW: Expected conversation progression
    "opening": "Patient describes 3-week cough",
    "early_phase": ["Duration", "Productive/dry", "Fever"],
    "middle_phase": ["Associated symptoms", "Past history", "Medications"],
    "late_phase": ["Social history", "ICE", "Summary"],
    "key_turning_points": [
      "If asked about hemoptysis, patient becomes worried",
      "If empathy shown, patient opens up about cancer fear"
    ]
  },
  "scoring_checkpoints": [  // NEW: Key moments for examiner scoring
    {
      "checkpoint": "Introduced self and explained purpose",
      "timing": "First 30 seconds",
      "category": "Professionalism"
    },
    {
      "checkpoint": "Asked open question first",
      "timing": "First minute",
      "category": "Communication Skills"
    },
    {
      "checkpoint": "Explored red flags (hemoptysis, weight loss)",
      "timing": "3-5 minutes",
      "category": "Patient Safety"
    }
  ]
  // ... (existing fields: candidate_instructions, actor_instructions, etc.)
}
```

**Estimated Effort:** 30-40 hours (content enrichment for 140 scenarios)

---

## 🗓️ Implementation Timeline (Mid-term: 12 weeks)

### Phase 1: Infrastructure Setup (Weeks 1-2)

**Goals:**
- WebSocket connection manager operational
- Redis session state structure defined
- Database schema for osce_sessions table
- Basic React OSCE UI wireframes

**Deliverables:**
- [ ] FastAPI WebSocket endpoint `/ws/osce/{session_id}` working
- [ ] Redis session state CRUD operations
- [ ] PostgreSQL `osce_sessions` table created (schema defined)
- [ ] React component skeletons (OSCEStation, PatientVideo, Transcript)
- [ ] WebSocket client connection established

**Agent Work:**
- Begin SIM-003 (Orchestrator) skeleton - WebSocket handling only

**Time:** 20-30 hours

---

### Phase 2: Core Agents - AI Patient (Weeks 3-4)

**Goals:**
- SIM-001 (AI Patient Agent) fully functional
- Patient persona system operational
- Conversation memory working
- Australian compliance validation integrated

**Deliverables:**
- [ ] SIM-001 agent code complete (`src/agents/simulation/sim_001_ai_patient.py`)
- [ ] 50 patient personas generated and validated
- [ ] OSCE loader utility functional (loads patient scripts from JSON)
- [ ] API endpoint `/api/ai-patient/start` and `/api/ai-patient/chat`
- [ ] Integration with QA-001 (Australian Compliance) for response validation
- [ ] Unit tests for AI patient (10+ test cases)

**Validation:**
- Test with 10 different OSCE scenarios
- Verify AI patient stays in character
- Confirm emotional states reflected in responses
- Check Australian terminology enforcement

**Time:** 30-40 hours

---

### Phase 3: Core Agents - AI Examiner (Weeks 5-6)

**Goals:**
- SIM-002 (AI Examiner Agent) fully functional
- AMC rubric scoring operational
- Structured feedback generation working
- Scoring accuracy validated

**Deliverables:**
- [ ] SIM-002 agent code complete (`src/agents/simulation/sim_002_examiner.py`)
- [ ] 10 AMC rubrics created and validated
- [ ] API endpoint `/api/ai-examiner/score`
- [ ] Integration with QA-002 (Clinical Accuracy) for scoring validation
- [ ] Scoring accuracy tests (compare to human examiner gold standard)
- [ ] Unit tests for AI examiner (10+ test cases)

**Validation:**
- Test with 20 mock conversations (good, average, poor performance)
- Compare AI scores to 2 human examiners (target: ±2 marks)
- Verify feedback is constructive and specific
- Check pass/fail threshold (9/15)

**Time:** 30-40 hours

---

### Phase 4: Context Manager (Week 6)

**Goals:**
- SIM-004 (Conversation Context Manager) operational
- Redis-backed conversation history
- Information graph tracking working

**Deliverables:**
- [ ] SIM-004 agent code complete (`src/agents/simulation/sim_004_context.py`)
- [ ] Redis storage for conversation history
- [ ] Information graph implementation
- [ ] Repetition detection working

**Time:** 15-20 hours

---

### Phase 5: Orchestration Integration (Weeks 7-8)

**Goals:**
- SIM-003 (Orchestrator) complete with all agents integrated
- End-to-end OSCE flow working
- Timer management operational
- Session persistence working

**Deliverables:**
- [ ] SIM-003 fully integrated with SIM-001, SIM-002, SIM-004
- [ ] Timer management (8-minute countdown, 1-minute warning)
- [ ] Message routing working (candidate → patient → examiner)
- [ ] Session finalization and scoring
- [ ] Redis + PostgreSQL persistence
- [ ] End-to-end integration tests (5+ full OSCE simulations)

**Time:** 30-40 hours

---

### Phase 6: Frontend Development (Weeks 7-8, Parallel with Phase 5)

**Goals:**
- React OSCE Station UI complete
- WebSocket client integrated
- Real-time conversation display
- Timer and session controls

**Deliverables:**
- [ ] OSCEStation component complete
- [ ] PatientVideo component (avatar display)
- [ ] ConversationTranscript component (real-time updates)
- [ ] RubricDisplay component (optional real-time scoring)
- [ ] Timer display with warning state
- [ ] Session controls (end station, pause, resume)
- [ ] Results page with scoring display

**Time:** 40-50 hours

---

### Phase 7: Content Generation (Weeks 9-10)

**Goals:**
- 200+ patient personas generated
- 140 OSCE scenarios enhanced with personas
- 20+ AMC rubrics curated

**Deliverables:**
- [ ] 200 patient personas in `data/patient_personas/`
- [ ] All 140 OSCEs mapped to personas
- [ ] All 140 OSCEs enhanced with expected_flow and scoring_checkpoints
- [ ] 20 AMC rubrics in `data/amc_rubrics/`
- [ ] Content validation (QA-001, QA-002)

**Agent Work:**
- Use MED-001 (Cardiology), MED-002 (Respiratory) to generate personas
- Use PM-001 to coordinate content generation workflow
- Use QA agents for validation

**Time:** 40-50 hours

---

### Phase 8: Testing & Refinement (Weeks 11-12)

**Goals:**
- End-to-end OSCE simulation tested
- User acceptance testing with medical students
- Performance optimization
- Documentation complete

**Deliverables:**
- [ ] 50 full OSCE simulations tested (10 users × 5 stations each)
- [ ] User satisfaction survey (target: 4.5/5 stars)
- [ ] Performance optimization (<3 second latency)
- [ ] API documentation (OpenAPI)
- [ ] User guide for students
- [ ] Admin documentation for adding OSCEs
- [ ] Deployment guide

**Testing Focus:**
- AI patient realism (Turing test: 70%+ think it's human)
- Scoring accuracy (±2 marks vs. human examiners)
- WebSocket stability (99%+ uptime)
- Concurrent sessions (100+ simultaneous)

**Time:** 40-50 hours

---

### Total Effort Summary

| Phase | Duration | Effort (hours) |
|-------|----------|----------------|
| Phase 1: Infrastructure | Weeks 1-2 | 20-30 |
| Phase 2: AI Patient | Weeks 3-4 | 30-40 |
| Phase 3: AI Examiner | Weeks 5-6 | 30-40 |
| Phase 4: Context Manager | Week 6 | 15-20 |
| Phase 5: Orchestration | Weeks 7-8 | 30-40 |
| Phase 6: Frontend | Weeks 7-8 | 40-50 |
| Phase 7: Content | Weeks 9-10 | 40-50 |
| Phase 8: Testing | Weeks 11-12 | 40-50 |
| **TOTAL** | **12 weeks** | **245-320 hours** |

**Full-time (40 hrs/week):** 12 weeks
**Part-time (20 hrs/week):** 24 weeks (6 months)

---

## 🔗 Integration with Existing Systems

### 1. Integration with 46-Agent Medical Education Infrastructure

**Leverage Existing Agents:**
- **QA-001 (Australian Compliance):** Validate all AI patient responses
- **QA-002 (Clinical Accuracy):** Validate examiner scoring
- **QA-003 (Citation Validator):** Future: cite sources for exam findings
- **MED-001 (Cardiology):** Generate cardiology-specific personas and OSCEs
- **MED-002 (Respiratory):** Generate respiratory-specific personas and OSCEs
- **PM-001 (Project Manager):** Coordinate content generation workflows

**Reuse Existing Patterns:**
- **BaseAgent:** All SIM-* agents inherit from BaseAgent class
- **LangGraph Workflows:** Orchestration follows existing workflow patterns
- **AgentState TypedDict:** State management for session orchestration
- **Skills Registry:** Register new simulation skills

**Integration Points:**
```python
# Example: SIM-001 uses QA-001 for validation
from agents.qa_001_australian_compliance import AustralianComplianceValidator

class AIPatientAgent(BaseMedicalExpert):
    def __init__(self, ...):
        super().__init__(...)
        self.compliance_validator = AustralianComplianceValidator()

    async def respond(self, student_message: str) -> str:
        response = await self.llm.ainvoke(messages)

        # Validate Australian compliance
        is_compliant, issues = await self.compliance_validator.validate(response)
        if not is_compliant:
            # Regenerate response if compliance issues
            response = await self._regenerate_compliant_response(issues)

        return response
```

---

### 2. Integration with EMR Practice System (Phase 2)

**Relationship:** Parallel development, separate modules but shared infrastructure

**Shared Components:**
- **Authentication:** JWT tokens, user accounts
- **Database:** User profiles, progress tracking
- **Frontend:** Shared React components (navigation, auth, dashboard)
- **Analytics:** Combined performance dashboard

**Independent Components:**
- **Backend APIs:** Separate routes (`/api/osce/` vs. `/api/emr/`)
- **Agent Systems:** OSCE uses SIM-* agents, EMR uses validation agents
- **Data Models:** Different PostgreSQL tables

**Navigation Integration:**
```typescript
// Main navigation menu
const MainNav = () => (
  <nav>
    <NavLink to="/dashboard">Dashboard</NavLink>
    <NavLink to="/mcqs">MCQ Practice</NavLink>
    <NavLink to="/osces">OSCE Simulation</NavLink>  {/* AMC Sim */}
    <NavLink to="/emr">EMR Practice</NavLink>        {/* EMR Sim */}
    <NavLink to="/analytics">Performance</NavLink>
  </nav>
);
```

**User Progress Integration:**
```typescript
// Combined progress dashboard
interface UserProgress {
  mcqs: { attempted: number; correct: number; average_score: number };
  osces: { attempted: number; passed: number; average_score: number };
  emr: { sessions: number; validation_rate: number };
  overall_rank: number;  // Percentile across all activities
}
```

---

### 3. Integration with RAG System (Qdrant)

**Use Cases:**
1. **AI Patient Knowledge Queries:** If candidate asks complex medical question, AI patient can query RAG
2. **Examiner Validation:** AI examiner can verify clinical accuracy against RAG knowledge
3. **Content Generation:** Use RAG to generate realistic patient personas and scenarios

**Example Integration:**
```python
from services.rag_query_service import RAGQueryService

class AIPatientAgent(BaseMedicalExpert):
    def __init__(self, ...):
        super().__init__(...)
        self.rag = RAGQueryService()

    async def respond(self, student_message: str) -> str:
        # If student asks complex question, check RAG
        if self._is_complex_medical_query(student_message):
            rag_context = await self.rag.query(student_message, top_k=3)
            # Inject RAG context into LLM prompt
            prompt = f"Context: {rag_context}\n\n{student_message}"
        else:
            prompt = student_message

        response = await self.llm.ainvoke(prompt)
        return response
```

**Benefits:**
- Ensures AI patient responses are medically accurate
- Enables AI patient to answer unexpected complex questions
- Validates examiner scoring against authoritative sources

---

### 4. Content Architecture Integration

**OSCE Content Tiers (from Content Architecture Plan):**
- **FREE Tier (20%):** 30 OSCEs (10 cardiology, 10 respiratory, 10 psychiatry)
- **FREE Sample (10%):** 15 OSCEs (taster for premium)
- **Premium (70%):** 95 OSCEs (full library)

**Monetization Integration:**
```typescript
interface UserSubscription {
  tier: 'free' | 'basic' | 'premium';
  osce_access: string[];  // List of accessible OSCE IDs
  monthly_limit: number;  // Attempts per month (free: 10, basic: 50, premium: unlimited)
}

// Frontend: Check access before starting OSCE
const startOSCE = async (osceId: string) => {
  const canAccess = await checkSubscriptionAccess(osceId);
  if (!canAccess) {
    showUpgradeModal();
    return;
  }
  // Proceed with OSCE
};
```

**Content Distribution:**
- Free users: History taking and communication skills only
- Premium users: Full range (history, physical exam, breaking bad news, procedures)

---

## 🔐 Security & Compliance

### Australian Medical Compliance

**Enforcement Mechanisms:**
1. **QA-001 Agent:** Validates every AI patient response
   - Australian terminology (paracetamol not acetaminophen)
   - Emergency numbers (000 not 911)
   - Healthcare system context (Medicare, PBS, GP referrals)

2. **System Prompts:** Explicitly instruct LLMs to use Australian English

3. **Content Validation:** All patient personas, rubrics, and scenarios reviewed by QA agents

**Validation Checklist:**
- [ ] Australian terminology enforced (100% compliance)
- [ ] Medicare/PBS context accurate
- [ ] AMC rubric standards followed
- [ ] eTG guidelines cited where relevant
- [ ] No American medical terms (ER → ED, ZIP → postcode, PCP → GP)

---

### Data Privacy & Security

**Patient Data:**
- All patient personas are **fictional** (no real patient data)
- Randomly generated names, Medicare numbers, demographics
- No PHI (Protected Health Information) stored

**Candidate Data:**
- Session transcripts stored encrypted (PostgreSQL encrypted columns)
- PII (name, email) separated from performance data
- Right to deletion (GDPR/Privacy Act compliant)
- Anonymized analytics (no identifying information in peer comparisons)

**API Security:**
- JWT authentication for all endpoints
- WebSocket connections require valid session token
- Rate limiting (prevent abuse)
- HTTPS only (TLS 1.3)

**Redis Security:**
- Session TTL (2 hours) - auto-expire unused sessions
- No sensitive data in Redis (only session state, not transcripts)
- Redis AUTH enabled

---

### Quality Gates

**Pre-Production Checklist:**
- [ ] All AI patient responses validated by QA-001 (Australian compliance)
- [ ] All examiner scoring validated by QA-002 (clinical accuracy)
- [ ] 50+ full OSCE simulations tested successfully
- [ ] User acceptance testing (10+ medical students, 4.5/5 satisfaction)
- [ ] Performance testing (<3 second latency, 99% uptime)
- [ ] Security audit (no vulnerabilities, encrypted data)
- [ ] Documentation complete (API docs, user guide, admin guide)

**PM-001 Approval Required:**
- Session transcripts reviewed (sample 10 random sessions)
- Scoring accuracy verified (±2 marks vs. human gold standard)
- Australian compliance verified (100% pass rate)

---

## 📊 Success Metrics & KPIs

### Technical Metrics

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| **AI Patient Realism** | 90%+ satisfaction | User survey: "How realistic was the AI patient?" (1-5 stars) |
| **Turing Test** | 70%+ think it's human | Blind test: users rate if they think it's AI or human actor |
| **Examiner Scoring Accuracy** | ±2 marks | Compare AI scores to 2 human examiners (gold standard) |
| **Scoring Consistency** | <10% variance | Same conversation scored multiple times, variance <1.5 marks |
| **WebSocket Uptime** | 99%+ | Prometheus monitoring of connection uptime |
| **End-to-end Latency** | <3 seconds | Candidate message → AI patient response |
| **Session Stability** | <1% disconnects | % of sessions with unexpected WebSocket disconnection |
| **Concurrent Sessions** | 100+ | Load testing with 100 simultaneous OSCEs |

### Clinical Metrics

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| **Pass Mark Calibration** | 9/15 validated | Clinical educators review 20 sample scorings, confirm pass/fail |
| **Rubric Alignment** | 95%+ agreement | Human examiners agree with AI's mark allocation (±1 mark per category) |
| **Critical Error Detection** | 100% caught | AI must detect all patient safety violations in test scenarios |
| **Red Flag Identification** | 95%+ recognition | AI patient appropriately reveals red flags when asked |

### User Experience Metrics

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| **Setup Time** | <2 minutes | Time from login to OSCE start |
| **Conversation Naturalness** | 4.5/5 stars | User survey: "How natural was the conversation?" |
| **Feedback Usefulness** | 4/5 stars | User survey: "How useful was the feedback?" |
| **Re-practice Rate** | 70%+ | % of users who repeat the same station |
| **Completion Rate** | 85%+ | % of sessions completed (not abandoned mid-session) |
| **Technical Issues** | <5% | % of sessions with technical problems reported |

### Business Metrics

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| **User Engagement** | 5 OSCE attempts/week | Average attempts per active user |
| **Conversion Rate** | 30%+ | Free users upgrading to premium |
| **Retention Rate** | 80%+ | Users active after 30 days |
| **NPS Score** | 50+ | Net Promoter Score from user surveys |

---

## 🚀 Next Steps (Post-Approval)

### Immediate Actions (Week 1)

1. **Create Agent Skeleton Files**
   ```bash
   mkdir -p src/agents/simulation
   touch src/agents/simulation/sim_001_ai_patient.py
   touch src/agents/simulation/sim_002_examiner.py
   touch src/agents/simulation/sim_003_orchestrator.py
   touch src/agents/simulation/sim_004_context.py
   touch src/agents/simulation/sim_005_physical_exam.py  # Future
   touch src/agents/analytics/study_001_osce_analytics.py
   ```

2. **Setup WebSocket Infrastructure**
   - Create FastAPI WebSocket endpoint
   - Implement WebSocketConnectionManager class
   - Test basic WebSocket connection (echo server)

3. **Design Redis Session State Schema**
   - Define session state structure (JSON)
   - Implement CRUD operations
   - Test with Redis CLI

4. **Create PostgreSQL Schema**
   ```sql
   CREATE TABLE osce_sessions (
     session_id UUID PRIMARY KEY,
     user_id UUID NOT NULL,
     osce_id VARCHAR(100) NOT NULL,
     mode VARCHAR(20) NOT NULL,  -- 'practice' or 'timed'
     status VARCHAR(20) NOT NULL,  -- 'active', 'completed', 'abandoned'
     start_time TIMESTAMP NOT NULL,
     end_time TIMESTAMP,
     elapsed_time INTEGER,
     conversation_history JSONB,  -- Full transcript
     scoring_result JSONB,  -- AI examiner output
     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
     updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
   );

   CREATE INDEX idx_osce_sessions_user ON osce_sessions(user_id);
   CREATE INDEX idx_osce_sessions_status ON osce_sessions(status);
   ```

5. **Update Skills Registry**
   ```json
   {
     "skills": [
       {
         "id": "simulate_patient_conversation",
         "name": "AI Patient Simulation",
         "agent": "SIM-001",
         "description": "Simulate realistic patient roleplay for OSCE practice",
         "category": "clinical_simulation"
       },
       {
         "id": "score_clinical_performance",
         "name": "AMC OSCE Scoring",
         "agent": "SIM-002",
         "description": "Score candidate performance using 15-mark AMC rubric",
         "category": "clinical_assessment"
       },
       {
         "id": "orchestrate_osce_session",
         "name": "OSCE Session Management",
         "agent": "SIM-003",
         "description": "Manage 8-minute timed OSCE stations with WebSocket coordination",
         "category": "clinical_simulation"
       }
     ]
   }
   ```

---

### Week 2-4: AI Patient Development

Follow Phase 2 plan (see Implementation Timeline)

**Key Milestones:**
- [ ] Week 2: SIM-001 skeleton + OSCE loader working
- [ ] Week 3: 50 patient personas generated
- [ ] Week 4: End-to-end testing (AI patient responds to 10 scenarios)

---

### Week 5-8: AI Examiner + Orchestration

Follow Phases 3-5 (see Implementation Timeline)

**Key Milestones:**
- [ ] Week 5: SIM-002 scoring working with 10 rubrics
- [ ] Week 6: SIM-004 context manager operational
- [ ] Week 7: SIM-003 orchestration integrating all agents
- [ ] Week 8: End-to-end OSCE flow working

---

### Week 9-12: Content + Testing

Follow Phases 7-8 (see Implementation Timeline)

**Key Milestones:**
- [ ] Week 9: 200 patient personas complete
- [ ] Week 10: All 140 OSCEs enhanced
- [ ] Week 11: User acceptance testing (10 medical students)
- [ ] Week 12: Production deployment

---

## 📚 Related Documents

### Existing Plans (Consolidate From)
- **[03_PHASE3_AMC_SIMULATION.md](./feature-modules-2026-02-01/03_PHASE3_AMC_SIMULATION.md)** - Original Phase 3 plan (1,320 lines)
- **[README.md](./feature-modules-2026-02-01/README.md)** - Overall feature modules roadmap
- **[02_PHASE2_EMR_PRACTICE.md](./feature-modules-2026-02-01/02_PHASE2_EMR_PRACTICE.md)** - EMR Practice System (parallel development)

### Architecture Documents
- **[SYSTEM_ARCHITECTURE_OVERVIEW.md](../SYSTEM_ARCHITECTURE_OVERVIEW.md)** - Overall system architecture
- **[ARCHITECTURE_DECISION_RECORD.md](../ARCHITECTURE_DECISION_RECORD.md)** - ADRs for technology choices

### Agent Documentation
- **[src/agents/README.md](../src/agents/README.md)** - Agent system overview
- **[pm_001_project_manager.py](../src/agents/pm_001_project_manager.py)** - Project manager agent
- **[qa_001_australian_compliance.py](../src/agents/qa_001_australian_compliance.py)** - Australian compliance validator

### Data & Content
- **[CONTENT_ARCHITECTURE_PLAN.md](./CONTENT_ARCHITECTURE_PLAN.md)** - Content organization and monetization
- **[data/osces/](../data/osces/)** - 140 existing OSCE scenarios

---

## 🎓 Appendix

### A. Glossary

- **AMC:** Australian Medical Council
- **OSCE:** Objective Structured Clinical Examination (8-minute clinical stations)
- **SIM-*:** Simulation agent (new agents for clinical exam simulation)
- **MED-*:** Medical expert agent (existing agents for content generation)
- **QA-*:** Quality assurance agent (existing agents for validation)
- **LangChain:** Python framework for LLM applications (conversation memory, prompts)
- **LangGraph:** Workflow orchestration framework (agent coordination)
- **WebSocket:** Bidirectional real-time communication protocol
- **Redis:** In-memory data store (session state, caching)
- **Rubric:** Scoring criteria (AMC uses 15-mark rubric: 5 categories × 3 marks)

### B. AMC Clinical Examination Format

**Station Types:**
1. **History Taking** (8 minutes) - Take focused history from patient
2. **Physical Examination** (6 minutes) - Perform systematic examination
3. **Communication Skills** (8 minutes) - Breaking bad news, informed consent, etc.
4. **Integrated Stations** (10 minutes) - History + examination + management plan

**Marking:**
- **15-mark rubric:** 5 categories × 3 marks each
- **Pass mark:** 9/15 (60%)
- **Global rating:** Overall impression (satisfactory / borderline / unsatisfactory)

**Emotional States in OSCEs:**
- Patients may be anxious, tearful, angry, defensive, or confused
- Candidates must adapt communication style to patient's emotional state
- Empathy and rapport-building are explicitly scored

### C. Australian Medical Context

**Terminology:**
- GP (not PCP - Primary Care Physician)
- ED (not ER - Emergency Room)
- Theatre (not OR - Operating Room)
- Paracetamol (not acetaminophen)
- Postcode (not ZIP code)
- 000 (not 911 - emergency number)

**Healthcare System:**
- **Medicare:** Universal healthcare (all Australians have Medicare number)
- **PBS:** Pharmaceutical Benefits Scheme (subsidized medications)
- **MBS:** Medicare Benefits Schedule (subsidized medical services)
- **Bulk billing:** Doctor bills Medicare directly (no out-of-pocket for patient)

**Clinical Guidelines:**
- **eTG:** Therapeutic Guidelines (evidence-based treatment protocols)
- **AMH:** Australian Medicines Handbook
- **RACGP Red Book:** Preventive health guidelines

---

**Document Status:** ✅ COMPLETE - Ready for Implementation
**Last Updated:** 2026-02-06
**Version:** 1.0 (Ultrathink Master Plan)
**Prepared By:** PM + Claude (Sonnet 4.5)
**Next Review:** After Phase 1 completion (Week 2)

---

*This ultrathink document consolidates all planning, architecture, and implementation details for the AMC Clinical Exam Simulation system. It is designed to be a single source of truth for mid-term (1-3 months) implementation with comprehensive agent architecture and integration points.*
