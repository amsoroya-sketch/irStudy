# AMC Clinical Exam Simulation - Complete Architecture Summary

**Document:** ARCHITECTURE_SUMMARY.md
**Version:** 1.0
**Last Updated:** 2026-02-06
**Purpose:** Consolidated architecture reference covering all aspects of the system

---

## 📋 Table of Contents

1. [Agent Architecture](#agent-architecture)
2. [State Machines](#state-machines)
3. [Data Architecture](#data-architecture)
4. [API Specifications](#api-specifications)
5. [Deployment Guide](#deployment-guide)
6. [Integration Guide](#integration-guide)

---

# Agent Architecture

## Agent Overview Diagram

![Agent Architecture Overview](images/03_agent_architecture_overview.png)

## Six New Simulation Agents (SIM-*)

### SIM-001: AI Patient Agent

![SIM-001 Detail](images/04_sim001_ai_patient_detail.png)

**Purpose:** Conversational AI patient with emotional states

**Class Structure:**
```python
class AIPatientAgent(BaseMedicalExpert):
    # Attributes
    patient_script: Dict          # Patient persona and medical history
    emotional_state: str          # Current emotion (neutral, anxious, tearful, etc.)
    memory: ConversationBufferMemory  # LangChain conversation history
    llm: ChatAnthropic            # Claude 3.5 Sonnet (temp=0.7)

    # Methods
    async def respond(self, student_message: str) -> str
    def update_emotional_state(self, new_state: str)
    def get_conversation_history(self) -> List[Dict]
    def reset(self)
    def _build_system_prompt(self) -> str
```

**Key Features:**
- Stays in character throughout conversation
- Reveals information progressively (not all at once)
- Responds positively to empathy
- 6 emotional states with transitions
- Australian medical context (Medicare, PBS, GP)

**LLM Configuration:**
- Model: Claude 3.5 Sonnet (claude-3-5-sonnet-20241022)
- Temperature: 0.7 (for natural conversation)
- Max tokens: 500 (patients don't monologue)
- Response length: 1-3 sentences typically

**Validation:**
- QA-001 (Australian Compliance) validates every response
- Checks: Australian terminology, emergency numbers, healthcare context

---

### SIM-002: AI Examiner Agent

![SIM-002 Detail](images/05_sim002_examiner_detail.png)

**Purpose:** AMC rubric-based scoring with detailed feedback

**Class Structure:**
```python
class AIExaminerAgent(BaseAgent):
    # Attributes
    rubric: Dict                  # AMC 15-mark rubric
    total_marks: int = 15
    pass_mark: int = 9
    criteria: List[Dict]          # 5 categories × 3 marks
    llm: ChatAnthropic            # Claude 3.5 Sonnet (temp=0.1)

    # Methods
    async def score_conversation(
        self,
        conversation_history: List[Dict],
        patient_script: Dict
    ) -> Dict
    async def score_in_real_time(self, conversation: List[Dict]) -> Dict
    def _build_scoring_prompt(self, patient_script: Dict) -> str
    def _parse_scoring_result(self, response: str) -> Dict
```

**AMC 15-Mark Rubric:**
1. History Taking / Examination Technique (0-3 marks)
2. Clinical Reasoning (0-3 marks)
3. Communication Skills (0-3 marks)
4. Patient Safety (0-3 marks)
5. Professionalism (0-3 marks)

**Pass Mark:** 9/15 (60%)

**Scoring Output:**
```json
{
  "total_score": 12,
  "pass_fail": "PASS",
  "criteria_scores": [
    {
      "criterion": "History Taking",
      "marks_awarded": 2,
      "marks_possible": 3,
      "justification": "Systematic approach but missed social history"
    }
  ],
  "strengths": ["Excellent rapport building", "Systematic questioning"],
  "areas_for_improvement": ["Expand social history", "Summarize findings"],
  "overall_feedback": "Strong performance with good communication skills..."
}
```

**LLM Configuration:**
- Model: Claude 3.5 Sonnet
- Temperature: 0.1 (for consistent scoring)
- Max tokens: 2000 (detailed feedback)

---

### SIM-003: OSCE Session Orchestrator

![SIM-003 Detail](images/06_sim003_orchestrator_detail.png)

**Purpose:** Manage entire OSCE session lifecycle

**Class Structure:**
```python
class OSCESessionOrchestrator(BaseAgent):
    # Attributes
    active_sessions: Dict[str, SessionState]
    timer_tasks: Dict[str, asyncio.Task]
    websocket_manager: WebSocketConnectionManager
    redis_client: Redis
    db: PostgreSQL

    # Methods
    async def initialize_session(self, user_id, osce_id, mode) -> str
    async def handle_websocket_connection(self, websocket, session_id)
    async def route_message(self, session_id, message: Dict)
    async def manage_timer(self, session_id, duration=480)
    async def finalize_session(self, session_id)
    async def pause_session(self, session_id)
    async def resume_session(self, session_id)
```

**Responsibilities:**
- Accept WebSocket connections from clients
- Route messages between frontend and AI agents
- Manage timer (8-minute countdown with 1-minute warning)
- Coordinate SIM-001 (patient), SIM-002 (examiner), SIM-004 (context)
- Persist session state to Redis
- Save final data to PostgreSQL

**Session State (Redis):**
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
  "context_manager_id": "sim004_abc"
}
```

---

### SIM-004: Conversation Context Manager

**Purpose:** Track conversation history and information disclosure

**Class Structure:**
```python
class ConversationContextManager(BaseAgent):
    # Attributes
    session_id: str
    redis_client: Redis
    message_buffer: List[Dict]
    information_graph: Dict
    repetition_tracker: Dict

    # Methods
    async def store_message(self, role: str, content: str, metadata: Dict)
    async def get_context(self, max_tokens: int = 2000) -> str
    async def get_full_history(self) -> List[Dict]
    async def track_information(self, info_key: str, disclosed: bool)
    async def summarize_conversation(self) -> str
    async def analyze_flow(self) -> Dict
```

**Information Graph:**
```json
{
  "presenting_complaint_discussed": true,
  "onset_duration_asked": true,
  "past_medical_history_covered": true,
  "social_history_asked": false,
  "patient_concerns_addressed": false,
  "red_flags_identified": ["chest_pain", "shortness_of_breath"],
  "empathy_moments": 3,
  "interruptions": 0,
  "repetitive_questions": ["duration of cough"],
  "total_turns": 18
}
```

---

### SIM-005: Physical Exam Simulator (Future)

**Purpose:** Simulate physical examination findings

**Status:** P2 (Future Enhancement)

**Planned Features:**
- Respond to examination maneuvers ("Auscultate chest", "Palpate abdomen")
- Provide realistic findings (normal vs. abnormal)
- Detect incorrect technique ("You didn't wash hands first")
- Image generation for visual findings (rashes, ECGs, X-rays)

---

### SIM-006: OSCE Performance Analytics

**Purpose:** Analyze performance and generate recommendations

**Key Features:**
- Track scores across multiple attempts
- Identify recurring mistakes
- Generate personalized recommendations
- Peer comparison (anonymized benchmarks)
- Progress visualization

**Analytics Output:**
```json
{
  "user_id": "user_456",
  "time_period": "30_days",
  "total_attempts": 15,
  "average_score": 11.2,
  "pass_rate": 0.80,
  "category_averages": {
    "history_taking": 2.5,
    "clinical_reasoning": 2.3,
    "communication": 2.8,
    "patient_safety": 2.4,
    "professionalism": 2.6
  },
  "common_mistakes": [
    "Consistently misses social history (10/15 attempts)",
    "Rarely summarizes findings (12/15 attempts)"
  ],
  "recommendations": [
    "Practice social history questions (smoking, alcohol, occupation)",
    "Implement SOAP summarization technique"
  ],
  "percentile": 72
}
```

---

# State Machines

## OSCE Session State Machine

![Session State Machine](images/07_state_machine_session.png)

### States

1. **SETUP** - Load OSCE, create agents
2. **ACTIVE** - Conversation (0-7 minutes)
3. **WARNING** - 1 minute remaining (7-8 minutes)
4. **COMPLETE** - Scoring and feedback
5. **PAUSED** - Technical issue (practice mode only)

### State Transitions

| From | To | Trigger |
|------|----|---------|
| START | SETUP | User clicks "Start OSCE" |
| SETUP | ACTIVE | Session initialized, timer starts |
| ACTIVE | WARNING | Timer reaches 7:00 |
| WARNING | COMPLETE | Timer reaches 8:00 OR user clicks "End" |
| COMPLETE | END | Results displayed |
| ACTIVE | PAUSED | User pauses (practice mode) |
| PAUSED | ACTIVE | User resumes |
| ACTIVE/WARNING | COMPLETE | Emergency stop (error) |

### Implementation

```python
class SessionState(Enum):
    SETUP = "setup"
    ACTIVE = "active"
    WARNING = "warning"
    COMPLETE = "complete"
    PAUSED = "paused"

async def manage_timer(session_id: str):
    session = get_session(session_id)

    while session.time_remaining > 0:
        await asyncio.sleep(1)
        session.time_remaining -= 1

        # State transitions
        if session.time_remaining == 60:
            session.status = SessionState.WARNING
            await send_warning_message(session_id)

        if session.time_remaining == 0:
            session.status = SessionState.COMPLETE
            await finalize_session(session_id)
```

---

## Patient Emotional State Machine

![Emotional State Machine](images/08_state_machine_emotions.png)

### Emotional States

1. **NEUTRAL** - Calm, cooperative
2. **ANXIOUS** - Worried, quick speech
3. **TEARFUL** - Emotional, pauses to cry
4. **ANGRY** - Frustrated, defensive
5. **CONFUSED** - Unclear, vague answers
6. **DEFENSIVE** - Reluctant, guarded

### Transition Triggers

**From NEUTRAL to:**
- **ANXIOUS:** Rushed questions, no empathy
- **TEARFUL:** Bad news discussed, no support
- **ANGRY:** Dismissed concerns, not listened to
- **CONFUSED:** Medical jargon, complex questions
- **DEFENSIVE:** Judgmental, invasive questions

**Back to NEUTRAL (with empathy):**
- **From ANXIOUS:** Reassurance, empathy shown
- **From TEARFUL:** Support given, time allowed
- **From ANGRY:** Apology, listening
- **From CONFUSED:** Clear explanation, check understanding
- **From DEFENSIVE:** Respect shown, trust built

### Implementation

```python
class EmotionalState(Enum):
    NEUTRAL = "neutral"
    ANXIOUS = "anxious"
    TEARFUL = "tearful"
    ANGRY = "angry"
    CONFUSED = "confused"
    DEFENSIVE = "defensive"

def update_emotional_state(
    current_state: EmotionalState,
    student_message: str,
    empathy_detected: bool
) -> EmotionalState:
    if empathy_detected and current_state != EmotionalState.NEUTRAL:
        return EmotionalState.NEUTRAL

    if "worried" in student_message.lower() or rushed_tone(student_message):
        return EmotionalState.ANXIOUS

    # ... other transition logic

    return current_state
```

---

# Data Architecture

## Database Schema Diagram

![Database Schema](images/09_database_schema_er.png)

## PostgreSQL Tables

### users
```sql
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    subscription_tier VARCHAR(50) NOT NULL,  -- 'free', 'basic', 'premium'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
```

### osces
```sql
CREATE TABLE osces (
    osce_id VARCHAR(100) PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    specialty VARCHAR(100) NOT NULL,  -- 'cardiology', 'respiratory', etc.
    station_type VARCHAR(100) NOT NULL,  -- 'history_taking', 'physical_exam', etc.
    persona_id VARCHAR(100) REFERENCES patient_personas(persona_id),
    rubric_id VARCHAR(100) REFERENCES amc_rubrics(rubric_id),
    candidate_instructions TEXT,
    actor_instructions TEXT,
    marking_criteria JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_osces_specialty ON osces(specialty);
CREATE INDEX idx_osces_station_type ON osces(station_type);
```

### patient_personas
```sql
CREATE TABLE patient_personas (
    persona_id VARCHAR(100) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    age INTEGER NOT NULL,
    gender VARCHAR(50) NOT NULL,
    occupation VARCHAR(255),
    medical_history JSONB,  -- Current illness, past history, medications
    social_history JSONB,   -- Smoking, alcohol, family
    personality_traits JSONB,  -- Baseline emotion, communication style
    australian_context JSONB,  -- Medicare number, GP details
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### amc_rubrics
```sql
CREATE TABLE amc_rubrics (
    rubric_id VARCHAR(100) PRIMARY KEY,
    rubric_name VARCHAR(255) NOT NULL,
    station_type VARCHAR(100) NOT NULL,
    specialty VARCHAR(100),
    total_marks INTEGER DEFAULT 15,
    pass_mark INTEGER DEFAULT 9,
    criteria JSONB NOT NULL,  -- 5 categories with descriptors
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### osce_sessions
```sql
CREATE TABLE osce_sessions (
    session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    osce_id VARCHAR(100) REFERENCES osces(osce_id),
    mode VARCHAR(20) NOT NULL,  -- 'practice' or 'timed'
    status VARCHAR(20) NOT NULL,  -- 'active', 'completed', 'abandoned'
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    elapsed_time INTEGER,  -- Seconds
    conversation_history JSONB,  -- Full transcript
    scoring_result JSONB,  -- AI examiner output
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_sessions_user_status ON osce_sessions(user_id, status);
CREATE INDEX idx_sessions_created ON osce_sessions(created_at DESC);
```

### user_performance
```sql
CREATE TABLE user_performance (
    performance_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    session_id UUID REFERENCES osce_sessions(session_id) ON DELETE CASCADE,
    total_score NUMERIC(4,1),  -- e.g., 12.5
    passed BOOLEAN,
    category_scores JSONB,  -- Scores by category
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_performance_user_date ON user_performance(user_id, created_at DESC);
```

---

## Redis Data Structures

### Session State
```
Key: session:{session_id}
Type: Hash
TTL: 2 hours
Fields:
  status: "active"
  time_remaining: 360
  patient_agent_id: "sim001_abc"
  examiner_agent_id: "sim002_abc"
  conversation_turns: 15
  websocket_connected: true
  last_activity: "2026-02-06T14:02:00Z"
```

### Conversation History
```
Key: conversation:{session_id}
Type: List (LPUSH for new messages)
TTL: 2 hours
Format: JSON strings
[
  '{"role": "student", "content": "...", "timestamp": 1707230400}',
  '{"role": "patient", "content": "...", "timestamp": 1707230402}'
]
```

---

# API Specifications

## WebSocket Protocol Diagram

![WebSocket Protocol](images/10_websocket_protocol.png)

## REST API Endpoints

### Authentication
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "student@example.com",
  "password": "secure_password"
}

Response: 200 OK
{
  "access_token": "eyJ0eXAi...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

### OSCE Management
```http
POST /api/osce/start
Authorization: Bearer {token}
Content-Type: application/json

{
  "osce_id": "respiratory_001",
  "mode": "timed"
}

Response: 201 Created
{
  "session_id": "abc123",
  "patient_name": "Sarah Mitchell",
  "presenting_complaint": "3-week productive cough",
  "emotional_state": "anxious",
  "websocket_url": "ws://localhost:8001/ws/osce/abc123"
}
```

```http
POST /api/osce/{session_id}/end
Authorization: Bearer {token}

Response: 200 OK
{
  "session_id": "abc123",
  "total_score": 12,
  "pass_fail": "PASS",
  "detailed_feedback": {...}
}
```

---

## WebSocket Protocol

### Connection
```javascript
const ws = new WebSocket(`ws://localhost:8001/ws/osce/${sessionId}`);

ws.onopen = () => {
  console.log('Connected to OSCE session');
};

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  handleMessage(message);
};
```

### Message Types

**Client → Server:**
```json
// Candidate message
{
  "type": "candidate_message",
  "content": "How long have you had this cough?",
  "timestamp": 1707230400000
}

// Pause session (practice mode)
{
  "type": "pause",
  "timestamp": 1707230400000
}

// End session
{
  "type": "end",
  "timestamp": 1707230400000
}
```

**Server → Client:**
```json
// Patient response
{
  "type": "patient_response",
  "content": "It's been about 3 weeks now, doctor.",
  "emotional_state": "anxious",
  "timestamp": 1707230402000
}

// Timer update (every 10 seconds)
{
  "type": "timer_update",
  "time_remaining": 360,
  "is_warning": false
}

// Session complete
{
  "type": "session_complete",
  "scoring_result": {
    "total_score": 12,
    "pass_fail": "PASS",
    ...
  },
  "transcript": [...]
}

// Error
{
  "type": "error",
  "message": "Session not found",
  "code": 404
}
```

---

# Deployment Guide

## Deployment Architecture Diagram

![Deployment Architecture](images/11_deployment_architecture.png)

## Docker Compose Configuration

```yaml
version: '3.8'

services:
  # Frontend
  frontend:
    image: amc-simulation-frontend:latest
    build: ./frontend
    ports:
      - "80:80"
    environment:
      - REACT_APP_API_URL=http://api:8001
      - REACT_APP_WS_URL=ws://api:8001

  # Backend API (3 replicas)
  api:
    image: amc-simulation-api:latest
    build: ./backend
    deploy:
      replicas: 3
    ports:
      - "8001:8001"
    environment:
      - REDIS_URL=redis://redis:6379
      - DATABASE_URL=postgresql://user:pass@postgres:5432/amc_db
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    depends_on:
      - redis
      - postgres

  # Celery Workers
  celery-worker:
    image: amc-simulation-api:latest
    command: celery -A src.tasks worker --loglevel=info
    deploy:
      replicas: 2
    environment:
      - REDIS_URL=redis://redis:6379
      - DATABASE_URL=postgresql://user:pass@postgres:5432/amc_db
    depends_on:
      - redis
      - postgres

  # Redis
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  # PostgreSQL
  postgres:
    image: postgres:15-alpine
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_USER=amc_user
      - POSTGRES_PASSWORD=secure_password
      - POSTGRES_DB=amc_db
    volumes:
      - postgres_data:/var/lib/postgresql/data

  # Nginx Load Balancer
  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - frontend
      - api

  # Monitoring
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    depends_on:
      - prometheus

volumes:
  redis_data:
  postgres_data:
```

---

# Integration Guide

## Integration Architecture Diagram

![Integration Architecture](images/12_integration_architecture.png)

## Integration Points

### 1. 46-Agent Medical Education Infrastructure

**Shared Agents:**
- **QA-001 (Australian Compliance):** Validates AI patient responses
- **QA-002 (Clinical Accuracy):** Validates examiner scoring
- **MED-001, MED-002:** Generate patient personas

**Integration:**
```python
from agents.qa_001_australian_compliance import AustralianComplianceValidator
from agents.qa_002_clinical_accuracy import ClinicalAccuracyValidator

class AIPatientAgent(BaseMedicalExpert):
    def __init__(self, ...):
        self.compliance_validator = AustralianComplianceValidator()

    async def respond(self, message: str) -> str:
        response = await self.llm.ainvoke(...)

        # Validate Australian compliance
        is_compliant, issues = await self.compliance_validator.validate(response)
        if not is_compliant:
            response = await self._regenerate_compliant_response(issues)

        return response
```

---

### 2. EMR Practice System

**Shared Infrastructure:**
- Authentication (JWT tokens)
- User database
- Performance analytics

**Separate Components:**
- Different APIs (`/api/osce/` vs. `/api/emr/`)
- Different database tables
- Different agent systems

**Navigation Integration:**
```typescript
const MainNav = () => (
  <nav>
    <NavLink to="/dashboard">Dashboard</NavLink>
    <NavLink to="/mcqs">MCQ Practice</NavLink>
    <NavLink to="/osces">OSCE Simulation</NavLink>
    <NavLink to="/emr">EMR Practice</NavLink>
    <NavLink to="/analytics">Performance</NavLink>
  </nav>
);
```

---

### 3. RAG System (Qdrant)

**Use Cases:**
- AI patient queries RAG for complex medical facts
- Examiner validates clinical accuracy against RAG
- Content generation uses RAG for realistic scenarios

**Integration:**
```python
from services.rag_query_service import RAGQueryService

class AIPatientAgent:
    def __init__(self, ...):
        self.rag = RAGQueryService()

    async def respond(self, message: str) -> str:
        if self._is_complex_medical_query(message):
            rag_context = await self.rag.query(message, top_k=3)
            prompt = f"Context: {rag_context}\n\n{message}"
        else:
            prompt = message

        response = await self.llm.ainvoke(prompt)
        return response
```

---

## Summary

This architecture documentation provides comprehensive coverage of:
- ✅ **12 Architecture Diagrams** generated with Python
- ✅ **6 New Agents** (SIM-001 to SIM-006) with detailed specifications
- ✅ **State Machines** for session and emotional states
- ✅ **Data Architecture** (PostgreSQL + Redis schemas)
- ✅ **API Specifications** (REST + WebSocket protocols)
- ✅ **Deployment Guide** (Docker + scaling)
- ✅ **Integration Guide** (existing systems + RAG)

**For detailed information, see individual markdown files in this directory.**

---

**Navigation:**
- [00_INDEX.md](00_INDEX.md) - Complete table of contents
- [01_SYSTEM_ARCHITECTURE.md](01_SYSTEM_ARCHITECTURE.md) - Four-layer architecture
- [README.md](README.md) - Quick start guide
