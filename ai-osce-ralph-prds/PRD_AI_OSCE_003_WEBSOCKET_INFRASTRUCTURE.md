# PRD: WebSocket Real-Time Conversation Infrastructure

**PRD ID**: PRD_AI_OSCE_003_WEBSOCKET_INFRASTRUCTURE
**Category**: Backend Infrastructure
**Priority**: P0-Critical (DEPENDS on PRD_001 & PRD_002, ENABLES frontend integration)
**Estimated Effort**: 18-22 hours
**Dependencies**: PRD_AI_OSCE_001_DATABASE_AND_APIS (MUST be complete), PRD_AI_OSCE_002_AI_INTEGRATION (MUST be complete)
**Status**: Not Started

---

## R - REQUEST (What & Why)

### User Story

**As a** medical student
**I want** real-time conversational interaction with an AI Patient for 8 minutes with live timer and emotional state indicators
**So that** I can practice clinical communication in a realistic, low-latency simulation that matches actual OSCE timing constraints

**As a** system architect
**I want** a robust WebSocket infrastructure that handles 100+ concurrent sessions, maintains session state in Redis, syncs to PostgreSQL every 30 seconds, and auto-finalizes sessions at 8:00 with 1-minute warning
**So that** students experience fast (<3s) conversational flow without dropped connections or data loss

### Business Context

The AI OSCE Simulation System requires production-grade WebSocket infrastructure to enable:

1. **Real-Time 8-Minute Sessions**
   - Live student ↔ AI Patient conversation
   - Immediate feedback on emotional state
   - Strict 8-minute timer (hard stop, no override)
   - 1-minute warning at 7:00 elapsed

2. **Session State Management**
   - Redis cache: Active conversation buffer, emotional state, empathy points
   - PostgreSQL: Permanent archive every 30 seconds
   - Zero message loss (syncback on disconnect)

3. **JWT WebSocket Authentication**
   - Token validation on connection
   - User authorization (can only join own sessions)
   - Rate limiting (max 3 concurrent WebSocket connections per user)

4. **Message Queuing & Flow Control**
   - Student messages → AI Patient service
   - Patient response → WebSocket broadcast
   - Timeout handling (if AI takes >5s, send "thinking..." indicator)

5. **Connection Resilience**
   - Automatic reconnect (client-side exponential backoff)
   - Session recovery from last sync point
   - Graceful degradation (if Redis down, use PostgreSQL cache)

**Business Value**:
- <3s conversation latency (student feels interactive, not robotic)
- 100+ concurrent sessions (scale to 1000s with load balancing)
- Zero data loss (dual storage: Redis + PostgreSQL)
- Exam-safe (strict timer prevents cheating)

### Success Metrics

- **Latency**: Student message → AI response <3 seconds (p95)
- **Concurrency**: 100 simultaneous WebSocket connections
- **Availability**: 99.9% uptime (zero dropped conversations mid-session)
- **Data Integrity**: 100% message sync (zero loss)
- **Message Delivery**: 100% of messages reach PostgreSQL
- **Timer Accuracy**: ±0.5 seconds (8:00 auto-finalize precise)
- **User Experience**: Session recovery <2 seconds on reconnect

### Scope

**In Scope**:
- WebSocket endpoint with JWT authentication
- Real-time message routing (student → AI Patient service → client)
- Emotional state broadcast (real-time indicators)
- 8-minute timer with 1-minute warning
- Redis session cache (persona, state, messages, actions)
- PostgreSQL sync job (every 30 seconds + on session end)
- Rate limiting (max 3 concurrent per user)
- Message validation (length, content)
- Error handling & recovery
- Connection state tracking
- Session finalization & cleanup

**Out of Scope** (Future Iterations):
- Multiple simultaneous sessions per user (Phase 2)
- Voice/video streaming (Phase 3)
- Message encryption (Phase 2, security hardening)
- Load balancer (Phase 2, multi-instance deployment)
- Prometheus metrics (Phase 2, observability)

---

## A - ARCHITECTURE (How)

### Technical Approach

Implement FastAPI WebSocket handler with JWT authentication, Redis-backed session state, and PostgreSQL persistence. Use async/await for non-blocking I/O, implement message queue to prevent blocking, and use Celery beat for periodic sync jobs.

**Key Design Decisions**:
1. **Redis-first, PostgreSQL-backup**: Active sessions in Redis (fast), synced to PostgreSQL (reliable)
2. **Async message processing**: Student message → background task (don't block WebSocket)
3. **Strict timer implementation**: Server-side timer (client can't manipulate)
4. **Progressive state tracking**: Emotional transitions logged in real-time
5. **Rate limiting**: Per-user connection limit (prevent abuse)
6. **Connection recovery**: UUID-based session identification (survives network hiccups)

### System Design

#### Component Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                      FRONTEND (React)                            │
│  - WebSocket connection (wss://)                                 │
│  - Send student message                                          │
│  - Receive patient response + timer update + emotional state     │
└────────────────────┬─────────────────────────────────────────────┘
                     │ WebSocket (wss://api.example.com/ws/osce/{attempt_id})
                     ↓
┌──────────────────────────────────────────────────────────────────┐
│               FASTAPI BACKEND (Python 3.11)                      │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  WebSocket Handler: /ws/osce/{attempt_id}              │   │
│  │  - JWT authentication (extract user_id from token)     │   │
│  │  - Rate limiting check (max 3 concurrent)              │   │
│  │  - Load session from Redis                             │   │
│  │  - Event loop: Monitor timer, route messages            │   │
│  │  - On disconnect: Sync Redis → PostgreSQL             │   │
│  └─────────────────────────────────────────────────────────┘   │
│                     ↓                                            │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Message Router                                         │   │
│  │  - Validate student message (length, content)          │   │
│  │  - Queue to background task (AI Patient service)       │   │
│  │  - Send "thinking..." indicator if delay >1s           │   │
│  │  - Update message_count in Redis                       │   │
│  │  - Update last_message_at timestamp                    │   │
│  └─────────────────────────────────────────────────────────┘   │
│                     ↓                                            │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Timer Service                                          │   │
│  │  - Server-side countdown (8:00)                        │   │
│  │  - Broadcast timer_update every 1 second               │   │
│  │  - Send warning at 7:00 (1-min remaining)             │   │
│  │  - Auto-finalize at 8:00 (hard stop)                  │   │
│  └─────────────────────────────────────────────────────────┘   │
│                     ↓                                            │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Session State Manager (Redis)                          │   │
│  │  - osce:session:{attempt_id}:persona (TTL 1800s)      │   │
│  │  - osce:session:{attempt_id}:state (HASH)             │   │
│  │  - osce:session:{attempt_id}:messages (LIST)          │   │
│  │  - osce:session:{attempt_id}:actions (LIST)           │   │
│  │  - osce:session:{attempt_id}:rag_cache (optional)    │   │
│  └─────────────────────────────────────────────────────────┘   │
│                     ↓                                            │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Periodic Sync Job (Celery Beat, every 30s)           │   │
│  │  - Read from Redis                                     │   │
│  │  - Write to PostgreSQL osce_attempts                   │   │
│  │  - Accumulate tokens_used, llm_cost_usd               │   │
│  │  - No data loss on Redis failure                       │   │
│  └─────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────┘
                     ↓ SQLAlchemy ORM
┌──────────────────────────────────────────────────────────────────┐
│                    POSTGRESQL 15 DATABASE                        │
│  - osce_attempts (conversation_history, emotional_transitions)  │
│  - osce_scores (scoring after session end)                      │
│  - user_progress (updated via trigger)                          │
└──────────────────────────────────────────────────────────────────┘
                     ↓
┌──────────────────────────────────────────────────────────────────┐
│                    REDIS CACHE LAYER                            │
│  - Active session state (1800s TTL)                             │
│  - Emotional state + empathy tracking                           │
│  - Message buffer (synced every 30s)                            │
│  - Rate limit counters                                          │
└──────────────────────────────────────────────────────────────────┘
```

#### Data Flow: 8-Minute WebSocket Session

```
┌─────────────────────────────────────────────────────────────────┐
│ STEP 1: WEBSOCKET CONNECTION                                    │
└─────────────────────────────────────────────────────────────────┘

Frontend: User clicks "Start OSCE"
    ↓
Frontend: Receives POST /api/v1/osce-sessions response
    {
      "attempt_id": "uuid-123",
      "websocket_url": "wss://api.example.com/ws/osce/uuid-123",
      "session_token": "eyJ..."
    }
    ↓
Frontend: Initiates WebSocket connection
    ws = new WebSocket("wss://api.example.com/ws/osce/uuid-123?token=eyJ...")
    ↓
Backend: WebSocket handler receives connection request
    - Path: /ws/osce/{attempt_id}
    - Query: token=session_token
    ↓
Backend: Authenticate JWT token
    - Extract: user_id, attempt_id
    - Validate: Token signature, expiry, user_id matches attempt owner
    - If invalid: Close connection (403 Unauthorized)
    ↓
Backend: Check rate limits
    - Query Redis: GET user:{user_id}:websocket_connections
    - Current: 0
    - Limit: 3 concurrent per user
    - Increment: SET user:{user_id}:websocket_connections 1 (TTL 1800)
    - If exceeds: Close connection (429 Too Many Requests)
    ↓
Backend: Load session state
    REDIS GET osce:session:{attempt_id}:state
    REDIS GET osce:session:{attempt_id}:persona
    REDIS GET osce:session:{attempt_id}:messages
    ↓
Backend: Initialize timer
    started_at = NOW()
    timer_elapsed = 0
    max_duration = 480 seconds (8 minutes)
    ↓
Backend: Send opening patient statement
    AI_PATIENT_RESPONSE = Load from persona.opening_statement
    WebSocket SEND: {
      "type": "patient_message",
      "speaker": "patient",
      "message": "Doctor, I've been having...",
      "emotional_state": "ANXIOUS_GUARDED",
      "timestamp": "2026-02-16T10:05:23Z"
    }
    ↓
Backend: Start timer task (async)
    asyncio.create_task(timer_loop(attempt_id))
    ↓
Frontend: Display patient message + timer
    "8:00" ← Timer starts counting down

┌─────────────────────────────────────────────────────────────────┐
│ STEP 2: MESSAGE EXCHANGE LOOP (0:00 - 8:00)                     │
└─────────────────────────────────────────────────────────────────┘

Frontend: Student types message
    "I understand that must be very concerning. Can you tell me more?"
    ↓
Frontend: Send via WebSocket
    ws.send(JSON.stringify({
      "type": "student_message",
      "message": "I understand that must be..."
    }))
    ↓
Backend: Receive message
    - Timestamp: 0:23 elapsed
    - Message: "I understand that must be..."
    ↓
Backend: Validate message
    - Not empty: ✓
    - Length <5000 chars: ✓
    - Not spam/abuse: ✓
    ↓
Backend: Log to Redis (immediate)
    REDIS LPUSH osce:session:{attempt_id}:messages {
      "timestamp": "2026-02-16T10:05:45Z",
      "speaker": "student",
      "message": "I understand that must be..."
    }
    REDIS HSET osce:session:{attempt_id}:state message_count 2
    ↓
Backend: Queue AI Patient response (background task)
    asyncio.create_task(generate_ai_response(attempt_id, message))
    ↓
Backend: Detect empathy markers
    - Found: "I understand", "concerning"
    - Empathy delta: +1
    - REDIS HINCRBY osce:session:{attempt_id}:state empathy_points 1
    - New empathy: 1 (not at threshold 3 yet)
    - State: remains ANXIOUS_GUARDED
    ↓
Backend: Send "thinking..." indicator
    WebSocket SEND: {
      "type": "thinking",
      "message": "Patient is thinking..."
    }
    ↓
[Background task: AI Patient service generates response]
    - Load persona + emotional state
    - Perform RAG query
    - Call Claude 3.5 Sonnet (temp=0.7)
    - Response: "Well, it started about 2 hours ago..."
    - Tokens: 78 input + 54 output = 132
    ↓
Backend: Receive AI response
    - Log to Redis: LPUSH osce:session:{attempt_id}:messages
    - Update tokens: HSET osce:session:{attempt_id}:state tokens_used 366
    ↓
Backend: Send AI Patient response
    WebSocket SEND: {
      "type": "patient_message",
      "speaker": "patient",
      "message": "Well, it started about 2 hours ago...",
      "emotional_state": "ANXIOUS_GUARDED",
      "timestamp": "2026-02-16T10:06:15Z"
    }
    ↓
Frontend: Display patient response
    Message appears in chat
    Emotional indicator shows: ANXIOUS_GUARDED (icon/color)
    ↓
[REPEAT: Student sends message → AI responds (0:23 to 7:00)]

┌─────────────────────────────────────────────────────────────────┐
│ STEP 3: TIMER WARNING AT 7:00 ELAPSED                           │
└─────────────────────────────────────────────────────────────────┘

Backend: Timer service detects 420 seconds elapsed
    - max_duration = 480
    - remaining = 60
    - At 60s remaining: Send warning
    ↓
Backend: Send 1-minute warning
    WebSocket SEND: {
      "type": "timer_warning",
      "message": "1 minute remaining",
      "timestamp": "2026-02-16T10:13:43Z"
    }
    ↓
PostgreSQL: Log warning sent
    UPDATE osce_attempts
    SET warning_1min_shown = TRUE
    WHERE attempt_id = {attempt_id}
    ↓
Frontend: Display warning
    "TIME'S UP IN 1 MINUTE!" badge/alert
    Visual indication (red timer)

┌─────────────────────────────────────────────────────────────────┐
│ STEP 4: SESSION AUTO-FINALIZATION AT 8:00                       │
└─────────────────────────────────────────────────────────────────┘

Backend: Timer service detects 480 seconds elapsed
    - timer_expired = TRUE
    - Stop accepting new student messages
    ↓
Backend: Finalize session
    PostgreSQL: UPDATE osce_attempts
        SET ended_at = NOW(),
            duration_seconds = 480,
            timer_expired = TRUE,
            session_state = 'finalized'
        WHERE attempt_id = {attempt_id}
    ↓
Backend: Final Redis → PostgreSQL sync
    Read all from Redis:
    - conversation_history
    - emotional_state_transitions
    - student_actions
    - rag_queries_executed
    - tokens_used, llm_cost_usd

    Write to PostgreSQL:
    UPDATE osce_attempts
        SET conversation_history = ...,
            emotional_state_transitions = ...,
            student_actions = ...,
            rag_queries_executed = ...,
            total_messages = 13,
            total_tokens_used = 3456,
            llm_cost_usd = 0.01038,
            updated_at = NOW()
    ↓
Backend: Send session end message
    WebSocket SEND: {
      "type": "session_ended",
      "message": "Time's up! Your session is being scored.",
      "attempt_id": "uuid-123",
      "timestamp": "2026-02-16T10:13:45Z"
    }
    ↓
Backend: Trigger AI Examiner scoring (background task)
    asyncio.create_task(score_session(attempt_id))
    - Service loads conversation_history from PostgreSQL
    - Calls Claude 3.5 Sonnet with AMC rubric
    - Returns {scores, feedback, critical_errors}
    - Inserts into osce_scores table
    - Fires user_progress trigger
    ↓
Backend: Cleanup Redis
    REDIS DEL osce:session:{attempt_id}:persona
    REDIS DEL osce:session:{attempt_id}:state
    REDIS DEL osce:session:{attempt_id}:messages
    REDIS DEL osce:session:{attempt_id}:actions
    REDIS DEL osce:session:{attempt_id}:rag_cache
    REDIS DECR user:{user_id}:websocket_connections
    ↓
Backend: Send scoring results (when complete)
    WebSocket SEND: {
      "type": "scoring_complete",
      "total_score": 14,
      "pass_fail": "PASS",
      "breakdown": {...},
      "overall_feedback": "..."
    }
    ↓
Backend: Close WebSocket connection
    Graceful close (1000 Normal Closure)
    ↓
Frontend: Display results page
    Score breakdown, feedback, strengths, areas for improvement
    Option to retry with different persona

┌─────────────────────────────────────────────────────────────────┐
│ STEP 5: CONNECTION RECOVERY (IF NETWORK DISCONNECTS)            │
└─────────────────────────────────────────────────────────────────┘

[Network hiccup: Student's WebSocket disconnects at 3:45]
    ↓
Backend: Detect disconnect
    - Handler exception: WebSocket.disconnect
    - Log: "Attempt uuid-123 disconnected at 225s elapsed"
    ↓
Backend: Immediate PostgreSQL sync
    READ: osce:session:{attempt_id}:messages
    WRITE: osce_attempts.conversation_history (don't lose data)
    ↓
Backend: Keep session alive (don't finalize)
    - session_state remains 'conversation'
    - timer continues running server-side
    - PostgreSQL keeps attempt record (not ended)
    ↓
Frontend: Detect WebSocket close
    - Attempt to reconnect (exponential backoff: 1s, 2s, 4s, 8s)
    - Re-authenticate with same session_token
    ↓
Backend: Reconnect attempt (within 30 seconds)
    - Load session from Redis (still valid: TTL 1800s)
    - Verify: user_id, attempt_id match
    - Load: conversation_history, emotional_state, timer_elapsed
    ↓
Backend: Send "reconnected" message
    WebSocket SEND: {
      "type": "session_resumed",
      "message": "Connection restored. Session continues from where you left off.",
      "timer_remaining": 254  # 480 - 226 elapsed
    }
    ↓
Backend: Send conversation history since disconnect
    WebSocket SEND: {
      "type": "conversation_history_sync",
      "messages": [
        {all messages from since disconnect or from last received},
      ]
    }
    ↓
Frontend: Resume conversation
    Chat displays synced messages
    Timer updates to remaining seconds
    Student can continue sending messages
    ↓
[Continue normal flow until 8:00]

┌─────────────────────────────────────────────────────────────────┐
│ STEP 6: NO RECONNECT WITHIN 30 SECONDS (TIMEOUT)                │
└─────────────────────────────────────────────────────────────────┘

[Student reconnects after 45 seconds: Session expired]
    ↓
Backend: Reconnect attempt
    - Check session in Redis
    - If expired or not found: Session is closed
    ↓
Backend: Check PostgreSQL for active attempt
    SELECT * FROM osce_attempts
    WHERE attempt_id = {attempt_id} AND session_state IN ('conversation', 'finalized')
    ↓
Result: Session already finalized (after 8:00 or earlier timeout)
    - If still in PostgreSQL: Load from cache
    - If finalized: Display results from osce_scores
    ↓
Frontend: Display recovery option
    "Your session was ended due to inactivity. View results or start a new session."
```

### Database & Cache Integration

#### Redis Keys (Session-specific)

```
osce:session:{attempt_id}:persona
- Type: Hash (or JSON string)
- TTL: 1800 seconds (30 minutes, extends on activity)
- Fields: persona_id, name, age, symptoms, medical_history, emotional_profile, rag_hints
- Purpose: Avoid repeated PostgreSQL loads

osce:session:{attempt_id}:state
- Type: Hash
- TTL: 1800 seconds
- Fields:
  - session_state: "conversation" | "warning_1min" | "finalized"
  - emotional_state: "ANXIOUS_GUARDED" | "CAUTIOUSLY_OPEN" | "TRUSTING" | "WITHDRAWN" | "UPSET"
  - empathy_points: 0-10 (integer)
  - pain_level: 1-10
  - anxiety_level: 1-10
  - message_count: integer
  - tokens_used: integer
  - last_message_at: ISO timestamp
  - timer_started_at: ISO timestamp
  - warning_1min_sent: boolean
- Purpose: Real-time state tracking

osce:session:{attempt_id}:messages
- Type: List (LIFO - newest first)
- TTL: 1800 seconds
- Content: [{timestamp, speaker, message, emotional_state, tokens_used}, ...]
- Purpose: Conversation buffer (periodically synced to PostgreSQL)

osce:session:{attempt_id}:actions
- Type: List (LIFO)
- TTL: 1800 seconds
- Content: [{timestamp, action, category}, ...]
- Purpose: Student action log (communication, info_gathering, management)

osce:session:{attempt_id}:rag_cache (optional)
- Type: Hash
- TTL: 1800 seconds
- Content: {last_query, chunks, timestamp}
- Purpose: Avoid repeated RAG queries for same topic

# Rate limiting
user:{user_id}:websocket_connections
- Type: Integer (counter)
- TTL: 1800 seconds (expires with session)
- Purpose: Track concurrent WebSocket connections (max 3)
- Increment on connect, decrement on disconnect
```

#### PostgreSQL Sync Job (Every 30 seconds)

```python
@celery_beat.periodic_task(run_every=30.0)
async def sync_redis_to_postgres():
    """Sync active Redis sessions to PostgreSQL"""

    # Find all active sessions
    pattern = "osce:session:*:state"
    active_sessions = redis.keys(pattern)

    for session_key in active_sessions:
        attempt_id = session_key.split(":")[2]

        # Load from Redis
        messages = redis.lrange(f"osce:session:{attempt_id}:messages", 0, -1)
        state = redis.hgetall(f"osce:session:{attempt_id}:state")
        actions = redis.lrange(f"osce:session:{attempt_id}:actions", 0, -1)
        rag_queries = redis.lrange(f"osce:session:{attempt_id}:rag_queries", 0, -1)

        # Parse JSON
        messages_json = [json.loads(msg) for msg in messages]
        actions_json = [json.loads(action) for action in actions]
        rag_queries_json = [json.loads(q) for q in rag_queries]

        # Calculate emotional state transitions
        transitions = extract_state_transitions(messages_json, state)

        # Update PostgreSQL
        db.execute("""
            UPDATE osce_attempts
            SET conversation_history = :messages,
                student_actions = :actions,
                emotional_state_transitions = :transitions,
                rag_queries_executed = :rag_queries,
                total_messages = :msg_count,
                total_tokens_used = :tokens,
                llm_cost_usd = :cost,
                updated_at = NOW()
            WHERE attempt_id = :attempt_id
        """, {
            "messages": json.dumps(messages_json),
            "actions": json.dumps(actions_json),
            "transitions": json.dumps(transitions),
            "rag_queries": json.dumps(rag_queries_json),
            "msg_count": len(messages_json),
            "tokens": int(state.get('tokens_used', 0)),
            "cost": calculate_cost(int(state.get('tokens_used', 0))),
            "attempt_id": attempt_id
        })
        db.commit()

    logger.info(f"Synced {len(active_sessions)} sessions to PostgreSQL")
```

### Message Types (WebSocket Protocol)

#### Client → Server

```json
{
  "type": "student_message",
  "message": "Can you tell me more about when the pain started?"
}
```

#### Server → Client

```json
{
  "type": "patient_message",
  "speaker": "patient",
  "message": "It was around 11 o'clock this morning...",
  "emotional_state": "CAUTIOUSLY_OPEN",
  "emotional_state_changed": false,
  "pain_level": 8,
  "anxiety_level": 6,
  "timestamp": "2026-02-16T10:06:15Z"
}
```

```json
{
  "type": "timer_update",
  "elapsed_seconds": 45,
  "remaining_seconds": 435
}
```

```json
{
  "type": "timer_warning",
  "message": "1 minute remaining",
  "timestamp": "2026-02-16T10:13:43Z"
}
```

```json
{
  "type": "session_ended",
  "message": "Time's up! Your session is being scored.",
  "attempt_id": "uuid-123",
  "timestamp": "2026-02-16T10:13:45Z"
}
```

```json
{
  "type": "scoring_complete",
  "total_score": 14,
  "max_score": 15,
  "pass_fail": "PASS",
  "breakdown": {
    "communication": {"score": 3, "max": 3, "feedback": "..."},
    "clinical_reasoning": {"score": 4, "max": 4, "feedback": "..."}
  },
  "strengths": ["Excellent empathy", "..."],
  "areas_for_improvement": ["Could explore...", "..."],
  "overall_feedback": "Strong performance..."
}
```

```json
{
  "type": "error",
  "code": "SESSION_TIMEOUT",
  "message": "Session timed out due to inactivity"
}
```

---

## L - LOOP (Iterative Development)

### Phase 1: WebSocket Foundation (35% of effort, 6-7 hours)
**Goal**: Implement WebSocket handler with authentication, timer, and message routing

**Tasks**:
1. Create WebSocket endpoint with JWT auth - 1.5 hours
2. Implement 8-minute timer with 1-minute warning - 1.5 hours
3. Implement message validation & routing - 1.5 hours
4. Add rate limiting (max 3 concurrent) - 1 hour
5. Implement connection state tracking - 1 hour

**Validation Gate**:
- [ ] WebSocket connects successfully with valid JWT
- [ ] Connection rejected with invalid/expired token (401)
- [ ] Rate limit enforced (4th connection rejected)
- [ ] Timer counts down accurately (±0.5s)
- [ ] 1-minute warning sent at 7:00
- [ ] Session auto-finalizes at 8:00
- [ ] Messages validated (length, content)
- [ ] Student messages logged to Redis

---

### Phase 2: Session State Management (35% of effort, 6-7 hours)
**Goal**: Redis cache integration with PostgreSQL sync

**Tasks**:
1. Implement Redis session cache (persona, state, messages) - 1.5 hours
2. Build periodic sync job (Celery Beat, every 30s) - 1.5 hours
3. Implement session recovery on reconnect - 1.5 hours
4. Add graceful disconnect handling - 1 hour
5. Implement Redis key expiration & cleanup - 1 hour

**Validation Gate**:
- [ ] All session data cached in Redis
- [ ] PostgreSQL synced every 30 seconds (no data loss)
- [ ] Message count accurate before/after sync
- [ ] Session recovered on reconnect within 30s
- [ ] Redis keys expire after 1800s
- [ ] No stale data from previous sessions

---

### Phase 3: AI Integration & Testing (30% of effort, 5-6 hours)
**Goal**: Integrate AI Patient service, test end-to-end flow

**Tasks**:
1. Connect AI Patient service to WebSocket - 1 hour
2. Implement message queuing (background tasks) - 1 hour
3. Add emotional state tracking & broadcast - 1 hour
4. Write integration tests (end-to-end sessions) - 1.5 hours
5. Load test (100 concurrent WebSockets) - 1.5 hours

**Validation Gate**:
- [ ] AI Patient responses received via WebSocket
- [ ] Response time <3 seconds (p95)
- [ ] Emotional state updated in real-time
- [ ] 100 concurrent sessions stable
- [ ] No dropped connections
- [ ] Test coverage ≥80%

---

## P - PLAN (Detailed Implementation)

### Phase 1 Tasks

**Task 1.1**: Create WebSocket Endpoint with JWT Auth
- **Effort**: 1.5 hours
- **Owner**: Backend Engineer
- **Deliverable**: WebSocket handler at `/ws/osce/{attempt_id}`
- **Dependencies**: PRD_001, PRD_002 must be complete
- **Acceptance Criteria**:
  - [ ] Endpoint created: `async def websocket_osce(websocket: WebSocket, attempt_id: str)`
  - [ ] JWT token extracted from query parameter: `?token=...`
  - [ ] Token validated (signature, expiry, user_id)
  - [ ] User authorization (user_id matches attempt owner)
  - [ ] Connection accepted: `await websocket.accept()`
  - [ ] Invalid token: Connection rejected (close code 4001)
  - [ ] Test with valid and invalid tokens

**Task 1.2**: Implement 8-Minute Timer
- **Effort**: 1.5 hours
- **Owner**: Backend Engineer
- **Deliverable**: Timer service with 1-min warning and auto-finalize
- **Dependencies**: Task 1.1
- **Acceptance Criteria**:
  - [ ] Timer starts on WebSocket connect
  - [ ] Timer updates broadcast every 1 second (JSON message)
  - [ ] 1-minute warning sent at 7:00 elapsed (420 seconds)
  - [ ] Session auto-finalizes at 8:00 (480 seconds)
  - [ ] Timer accurate ±0.5 seconds
  - [ ] No client-side override possible (server authoritative)
  - [ ] Test timer precision with mocked time

**Task 1.3**: Implement Message Validation & Routing
- **Effort**: 1.5 hours
- **Owner**: Backend Engineer
- **Deliverable**: Message handler with validation
- **Dependencies**: Task 1.1
- **Acceptance Criteria**:
  - [ ] Accept `{"type": "student_message", "message": "..."}`
  - [ ] Validate: message not empty, length <5000 chars
  - [ ] Reject: spam/offensive content (simple regex)
  - [ ] Reject: messages after 8:00 (session ended)
  - [ ] Log to Redis: `LPUSH osce:session:{attempt_id}:messages`
  - [ ] Queue to AI Patient service (background task)
  - [ ] Send "thinking..." indicator if delay >1s
  - [ ] Error handling: If AI service down, send error message

**Task 1.4**: Add Rate Limiting
- **Effort**: 1 hour
- **Owner**: Backend Engineer
- **Deliverable**: Rate limiter (max 3 concurrent WebSocket per user)
- **Dependencies**: Task 1.1
- **Acceptance Criteria**:
  - [ ] On connect: Check `user:{user_id}:websocket_connections`
  - [ ] Count <3: Increment and proceed
  - [ ] Count ≥3: Close connection (code 4029, too many requests)
  - [ ] On disconnect: Decrement counter
  - [ ] Counter expires after 1800s (session TTL)
  - [ ] Test: Create 4 connections, verify 4th rejected

**Task 1.5**: Implement Connection State Tracking
- **Effort**: 1 hour
- **Owner**: Backend Engineer
- **Deliverable**: Track connection status and cleanup
- **Dependencies**: Task 1.1
- **Acceptance Criteria**:
  - [ ] Track: Connected, Disconnected, Reconnecting states
  - [ ] Log: Connection timestamp, disconnection timestamp
  - [ ] On normal close: Session_state = finalized
  - [ ] On abnormal close: Session_state = conversation (not ended)
  - [ ] Cleanup: Redis key increments/decrements
  - [ ] Test: Normal close, network error, timeout scenarios

---

### Phase 2 Tasks

**Task 2.1**: Implement Redis Session Cache
- **Effort**: 1.5 hours
- **Owner**: Backend Engineer
- **Deliverable**: Redis cache for session state
- **Dependencies**: Task 1.1
- **Acceptance Criteria**:
  - [ ] Load persona: `REDIS GET osce:session:{attempt_id}:persona`
  - [ ] Load state: `REDIS GET osce:session:{attempt_id}:state` (HASH)
  - [ ] Create/update all Redis keys with correct TTL (1800s)
  - [ ] Messages list: LIFO order (newest first)
  - [ ] Actions list: LIFO order
  - [ ] Test cache hit rate (>95%)
  - [ ] Test no stale data (TTL expires correctly)

**Task 2.2**: Build Periodic Sync Job
- **Effort**: 1.5 hours
- **Owner**: Backend Engineer
- **Deliverable**: Celery Beat task syncing every 30 seconds
- **Dependencies**: Task 2.1
- **Acceptance Criteria**:
  - [ ] Celery Beat configured (beat -A backend.celery_app)
  - [ ] Task registered: `sync_redis_to_postgres` (30s interval)
  - [ ] Reads all from Redis: messages, actions, state, rag_queries
  - [ ] Writes to PostgreSQL: conversation_history, emotional_state_transitions, student_actions
  - [ ] Accumulates: total_messages, total_tokens_used, llm_cost_usd
  - [ ] No data loss: Final sync at session end
  - [ ] Test: Create session, wait 35s, verify PostgreSQL updated

**Task 2.3**: Implement Session Recovery on Reconnect
- **Effort**: 1.5 hours
- **Owner**: Backend Engineer
- **Deliverable**: Recovery flow for disconnected sessions
- **Dependencies**: Tasks 1.1, 2.1
- **Acceptance Criteria**:
  - [ ] Client disconnects (network hiccup)
  - [ ] Server: Immediately syncs Redis → PostgreSQL
  - [ ] Client: Detects disconnect, attempts reconnect (exponential backoff)
  - [ ] Reconnect within 30s: Session found in Redis
  - [ ] Backend: Loads conversation_history, emotional_state, timer_elapsed
  - [ ] Backend: Sends `session_resumed` message
  - [ ] Backend: Syncs conversation history since disconnect
  - [ ] Frontend: Chat resumes, timer updates
  - [ ] Test: Simulate disconnect, reconnect, verify no message loss

**Task 2.4**: Add Graceful Disconnect Handling
- **Effort**: 1 hour
- **Owner**: Backend Engineer
- **Deliverable**: Cleanup logic on disconnect
- **Dependencies**: Task 2.1
- **Acceptance Criteria**:
  - [ ] On disconnect (normal or error): Catch exception
  - [ ] Immediate PostgreSQL sync (don't lose data)
  - [ ] Check: Is session still active (timer not expired)?
  - [ ] If active: Keep session alive in Redis (TTL 1800)
  - [ ] If expired: Clean up Redis keys
  - [ ] Decrement rate limit counter
  - [ ] Log disconnect reason
  - [ ] Test: Normal close, error close, timeout scenarios

**Task 2.5**: Implement Redis Key Expiration & Cleanup
- **Effort**: 1 hour
- **Owner**: Backend Engineer
- **Deliverable**: Background cleanup of expired sessions
- **Dependencies**: Task 2.1
- **Acceptance Criteria**:
  - [ ] All session keys have TTL 1800 seconds
  - [ ] Rate limit keys expire with session
  - [ ] Background job cleans up expired keys (optional, Redis does this)
  - [ ] Test: Create session, wait 1800s, verify keys expired
  - [ ] Verify no orphaned data in Redis

---

### Phase 3 Tasks

**Task 3.1**: Connect AI Patient Service to WebSocket
- **Effort**: 1 hour
- **Owner**: Backend Engineer
- **Deliverable**: Integration with AI Patient service
- **Dependencies**: Tasks 1.1, 2.1, PRD_002
- **Acceptance Criteria**:
  - [ ] Student message → AI Patient service (async)
  - [ ] AI Patient returns response + tokens_used
  - [ ] Response broadcast to WebSocket
  - [ ] Tokens accumulated in Redis state
  - [ ] Cost calculated and accumulated
  - [ ] Test: Full message exchange

**Task 3.2**: Implement Message Queuing (Background Tasks)
- **Effort**: 1 hour
- **Owner**: Backend Engineer
- **Deliverable**: Background task queue for AI responses
- **Dependencies**: Task 3.1
- **Acceptance Criteria**:
  - [ ] Student message → Background task (don't block WebSocket)
  - [ ] "thinking..." indicator sent immediately
  - [ ] AI response ready → Broadcast to client
  - [ ] If delay >5s: Send "still thinking..." update
  - [ ] Timeout after 30s: Send error message
  - [ ] Test: AI slowdown doesn't block other sessions

**Task 3.3**: Add Emotional State Tracking & Broadcast
- **Effort**: 1 hour
- **Owner**: Backend Engineer
- **Deliverable**: Real-time emotional state updates
- **Dependencies**: Task 2.1, PRD_002
- **Acceptance Criteria**:
  - [ ] Emotional state updated in Redis on each response
  - [ ] State transitions broadcast to client
  - [ ] Empathy points tracked and displayed
  - [ ] Message includes: emotional_state, emotional_state_changed, pain_level, anxiety_level
  - [ ] Frontend: Emotional indicator updates in real-time
  - [ ] Test: Verify state transitions match expected rules

**Task 3.4**: Write Integration Tests (End-to-End)
- **Effort**: 1.5 hours
- **Owner**: Backend Engineer / Testing QA
- **Deliverable**: `backend/tests/test_integration/test_websocket_session.py`
- **Dependencies**: Tasks 3.1-3.3
- **Test Cases**:
  - [ ] Test full 8-minute session (5 messages exchanges)
  - [ ] Test timer accuracy (message at 0s, 1s, 7:00, 8:00)
  - [ ] Test 1-minute warning at 7:00
  - [ ] Test auto-finalize at 8:00
  - [ ] Test message validation (reject empty, too long, spam)
  - [ ] Test JWT auth (valid, invalid, expired tokens)
  - [ ] Test rate limiting (4th connection rejected)
  - [ ] Test session recovery (disconnect/reconnect)
  - [ ] Test PostgreSQL sync (messages persisted)
  - [ ] Coverage ≥80%

**Task 3.5**: Load Test (100 Concurrent WebSockets)
- **Effort**: 1.5 hours
- **Owner**: Backend Engineer / Testing QA
- **Deliverable**: Load test with 100 concurrent sessions
- **Dependencies**: Tasks 3.1-3.3
- **Test Procedure**:
  - [ ] Spawn 100 WebSocket clients
  - [ ] Each sends 5 messages over 8 minutes
  - [ ] Measure: Latency, memory, CPU, error rate
  - [ ] Verify: No dropped connections
  - [ ] Verify: <3s response time (p95)
  - [ ] Verify: Database consistency
  - [ ] Report: Performance metrics

---

## H - HANDOFF (Delivery & Validation)

### Acceptance Criteria (MUST ALL PASS)

#### Functional Requirements
- [ ] WebSocket connects with JWT authentication
- [ ] Connection rejected with invalid/expired token (401)
- [ ] Rate limiting enforced (max 3 concurrent per user)
- [ ] Timer counts down accurately (±0.5 seconds)
- [ ] 1-minute warning sent at 7:00
- [ ] Session auto-finalizes at 8:00
- [ ] Messages validated (length, content, spam)
- [ ] Messages routed to AI Patient service
- [ ] AI responses broadcast to WebSocket
- [ ] Emotional state tracked and broadcast
- [ ] Session state cached in Redis (TTL 1800s)
- [ ] PostgreSQL synced every 30 seconds (no data loss)
- [ ] Session recovered on reconnect (within 30s)
- [ ] Graceful disconnect handling
- [ ] Redis keys expire correctly
- [ ] AI Examiner triggered at session end
- [ ] Score saved to PostgreSQL
- [ ] user_progress updated (trigger fires)

#### Quality Requirements
- [ ] **Test Coverage**: ≥80% (unit + integration)
- [ ] **Test Pass Rate**: 100% (zero tolerance)
- [ ] **Code Quality**: No linting errors
- [ ] **Documentation**: WebSocket protocol documented

#### Performance Requirements
- [ ] **Latency**: <3 seconds (p95) for AI response
- [ ] **Concurrency**: 100 simultaneous WebSocket connections
- [ ] **Availability**: 99.9% uptime
- [ ] **Timer Accuracy**: ±0.5 seconds
- [ ] **Data Integrity**: 100% of messages reach PostgreSQL

#### Security Requirements
- [ ] **JWT Authentication**: Valid token required
- [ ] **User Authorization**: Users can only access own sessions
- [ ] **Rate Limiting**: Max 3 concurrent connections per user
- [ ] **Message Validation**: Length <5000 chars, content sanitized

---

### Documentation Deliverables

#### WebSocket Protocol Documentation (`backend/docs/WEBSOCKET_PROTOCOL.md`)
- Overview of WebSocket flow
- Message types and examples
- Authentication flow
- Timer behavior
- Error handling
- Recovery scenarios

#### Testing Requirements

```python
# backend/tests/test_integration/test_websocket_session.py

async def test_full_8_minute_session():
    """Test complete WebSocket session flow"""
    # 1. Connect WebSocket with valid JWT
    # 2. Receive opening patient statement
    # 3. Send 5 messages (0:30, 1:30, 2:30, 3:30, 4:30)
    # 4. Receive 5 AI responses
    # 5. At 7:00: Receive 1-minute warning
    # 6. At 8:00: Receive session_ended
    # 7. Receive scoring_complete
    # 8. Verify PostgreSQL has all messages

async def test_rate_limiting():
    """Test max 3 concurrent WebSocket per user"""
    # Connect 3 WebSockets as same user
    # All succeed
    # Connect 4th: Should fail (429 Too Many Requests)

async def test_session_recovery():
    """Test reconnect within 30 seconds"""
    # Connect, send 2 messages
    # Disconnect (network error)
    # Reconnect with same attempt_id
    # Load conversation history, continue session
    # Verify no message loss
```

---

### Success Validation

**This PRD is considered COMPLETE when**:
1. ✅ WebSocket endpoint created with JWT auth
2. ✅ 8-minute timer implemented with 1-min warning
3. ✅ Message routing to AI Patient service working
4. ✅ Redis session cache operational (TTL 1800s)
5. ✅ PostgreSQL sync job running (every 30s)
6. ✅ Session recovery on reconnect working
7. ✅ Rate limiting enforced (max 3 concurrent)
8. ✅ Graceful disconnect handling
9. ✅ 100 concurrent WebSocket connections stable
10. ✅ <3s response time (p95)
11. ✅ Test coverage ≥80%, 100% pass rate
12. ✅ WebSocket protocol documented

---

**Document Status**: Complete
**Created**: 2026-02-16
**Last Updated**: 2026-02-16
**Version**: 1.0
**File Size**: ~47 KB
**Target Reader**: Backend Engineers, DevOps, QA

---

## Related Documents

- **Depends On**: PRD_AI_OSCE_001_DATABASE_AND_APIS, PRD_AI_OSCE_002_AI_INTEGRATION
- **Enables**: Frontend WebSocket integration, Mock exam orchestration
- **Architecture Ref**: AI_OSCE_SIMULATION_INTEGRATION_ARCHITECTURE.md (Section 3.1, lines 515-770)
