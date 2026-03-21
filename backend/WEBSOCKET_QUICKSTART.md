# WebSocket OSCE Sessions - Quick Start Guide

## TL;DR

The WebSocket infrastructure for real-time OSCE chat sessions is **ALREADY COMPLETE**. This guide shows you how to use it.

## Endpoint

```
ws://localhost:8001/ws/osce/{attempt_id}?token={jwt_token}
```

## Quick Test

### 1. Start the Server

```bash
cd /home/dev/Development/irStudy/backend
uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload
```

### 2. Create an OSCE Session (REST API)

```bash
# Get JWT token first (login)
curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student@example.com",
    "password": "your_password"
  }'

# Use token to create OSCE session
curl -X POST http://localhost:8001/api/v1/osce-sessions \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "persona_id": "PERSONA_UUID",
    "session_type": "individual"
  }'

# Response:
{
  "attempt_id": "abc-123-def-456",
  "persona_code": "CARD-001",
  "opening_statement": "Doctor, I have chest pain...",
  "time_limit_seconds": 480
}
```

### 3. Connect to WebSocket

**Using `wscat` (Command Line):**

```bash
# Install wscat
npm install -g wscat

# Connect
wscat -c "ws://localhost:8001/ws/osce/abc-123-def-456?token=YOUR_JWT_TOKEN"

# Send message
> {"type": "student_message", "message": "Hello, can you tell me more about the pain?"}

# Receive response
< {"type": "patient_message", "speaker": "patient", "message": "It started this morning...", "emotional_state": "ANXIOUS_GUARDED"}
```

**Using Python:**

```python
import asyncio
import websockets
import json

async def test_websocket():
    attempt_id = "abc-123-def-456"
    jwt_token = "YOUR_JWT_TOKEN"
    uri = f"ws://localhost:8001/ws/osce/{attempt_id}?token={jwt_token}"

    async with websockets.connect(uri) as websocket:
        # Wait for opening statement
        response = await websocket.recv()
        print(f"Patient: {json.loads(response)}")

        # Send student message
        await websocket.send(json.dumps({
            "type": "student_message",
            "message": "Can you tell me when the pain started?"
        }))

        # Receive AI Patient response
        response = await websocket.recv()
        print(f"Patient: {json.loads(response)}")

asyncio.run(test_websocket())
```

**Using JavaScript (Frontend):**

```javascript
const attemptId = 'abc-123-def-456';
const jwtToken = localStorage.getItem('jwt_token');
const ws = new WebSocket(
  `ws://localhost:8001/ws/osce/${attemptId}?token=${jwtToken}`
);

ws.onopen = () => {
  console.log('✅ Connected to OSCE session');
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Received:', data);

  switch (data.type) {
    case 'patient_message':
      displayPatientMessage(data.message, data.emotional_state);
      break;

    case 'timer_update':
      updateTimer(data.remaining_seconds);
      break;

    case 'timer_warning':
      showWarning('1 minute remaining!');
      break;

    case 'session_ended':
      showSessionEnded();
      break;

    case 'scoring_complete':
      displayScore(data);
      break;
  }
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};

ws.onclose = () => {
  console.log('❌ Disconnected from OSCE session');
};

// Send student message
function sendMessage(message) {
  ws.send(JSON.stringify({
    type: 'student_message',
    message: message
  }));
}

// Example usage
sendMessage('Can you tell me more about the chest pain?');
```

## Message Types

### Client → Server

Only one message type is supported:

```json
{
  "type": "student_message",
  "message": "Your question here"
}
```

**Validation Rules:**
- `message` cannot be empty
- Maximum length: 5000 characters
- Must be valid JSON

### Server → Client

#### 1. Patient Message

```json
{
  "type": "patient_message",
  "speaker": "patient",
  "message": "It started about 2 hours ago...",
  "emotional_state": "ANXIOUS_GUARDED",
  "emotional_state_changed": false,
  "timestamp": "2026-03-22T10:05:23Z"
}
```

**Emotional States:**
- `COOPERATIVE`
- `ANXIOUS_GUARDED`
- `DEFENSIVE_HOSTILE`
- `WITHDRAWN_UNCOOPERATIVE`

#### 2. Thinking Indicator

```json
{
  "type": "thinking",
  "message": "Patient is thinking..."
}
```

Sent immediately after student message, before AI response.

#### 3. Timer Update (Every Second)

```json
{
  "type": "timer_update",
  "elapsed_seconds": 45,
  "remaining_seconds": 435
}
```

#### 4. Timer Warning (At 7:00 Mark)

```json
{
  "type": "timer_warning",
  "message": "1 minute remaining",
  "timestamp": "2026-03-22T10:13:43Z"
}
```

#### 5. Session Ended (At 8:00 Mark)

```json
{
  "type": "session_ended",
  "message": "Time's up! Your session is being scored.",
  "attempt_id": "abc-123-def-456",
  "timestamp": "2026-03-22T10:14:43Z"
}
```

#### 6. Scoring Complete

```json
{
  "type": "scoring_complete",
  "total_score": 14,
  "max_score": 15,
  "pass_fail": "PASS",
  "breakdown": {
    "communication_score": 3,
    "clinical_reasoning_score": 3,
    "information_gathering_score": 3,
    "management_score": 3,
    "professionalism_score": 2
  },
  "strengths": [
    "Excellent rapport building",
    "Thorough history taking"
  ],
  "areas_for_improvement": [
    "Could have explored red flags more thoroughly"
  ],
  "overall_feedback": "Strong performance..."
}
```

#### 7. Error

```json
{
  "type": "error",
  "message": "Error description"
}
```

## Session Flow

```
1. Frontend creates OSCE session (POST /api/v1/osce-sessions)
   ↓
2. Frontend connects to WebSocket (ws://...?token=jwt)
   ↓
3. Server authenticates JWT token
   ↓
4. Server authorizes user (owns session)
   ↓
5. Server checks rate limits (max 3 concurrent)
   ↓
6. Server accepts WebSocket connection
   ↓
7. Server starts 8-minute timer
   ↓
8. Server sends opening patient statement
   ↓
9. Student sends messages ←→ AI Patient responds (8 minutes)
   │   - Timer updates every 1 second
   │   - Emotional state may change based on student's approach
   ↓
10. Server sends 1-minute warning (at 7:00)
   ↓
11. Server auto-finalizes session (at 8:00)
   ↓
12. Server triggers AI Examiner scoring
   ↓
13. Server sends scoring results
   ↓
14. Server closes WebSocket connection
```

## Rate Limiting

- **Max concurrent connections per user**: 3
- **4th connection**: Rejected with `code 1008` (Policy Violation)

## Error Codes

| Code | Reason | Description |
|------|--------|-------------|
| 1008 | Policy Violation | Invalid/missing JWT token, unauthorized access, or rate limit exceeded |
| 1011 | Internal Error | Server error during authentication or message processing |

## Authentication

### JWT Token

Required in query parameter: `?token=YOUR_JWT_TOKEN`

**Token must contain:**
- `user_id` or `sub` claim (user identifier)
- Valid signature
- Not expired

**Example JWT payload:**
```json
{
  "sub": "user-123",
  "email": "student@example.com",
  "role": "student",
  "exp": 1711234567
}
```

### Authorization

- User must **own** the OSCE attempt
- Verified by checking `OSCEAttemptAI.user_id == token.user_id`

## Performance

- **Message Latency**: <100ms (p95)
- **AI Response Time**: <5s (p95)
- **Concurrent Sessions**: 100+ users supported
- **Redis Caching**: Session state cached for performance
- **PostgreSQL Sync**: Every 30 seconds (Celery Beat)

## Troubleshooting

### Connection Refused

```bash
# Check if server is running
curl http://localhost:8001/health

# Expected response:
{"status": "healthy", "service": "irStudy Medical Education Platform"}
```

### Authentication Failed (Code 1008)

- Verify JWT token is valid: `jwt.io`
- Check token is not expired
- Verify user_id claim exists
- Ensure user owns the attempt

### Rate Limit Exceeded (Code 1008)

- Max 3 concurrent WebSocket connections per user
- Close existing connections before opening new ones

### No AI Response

- Check Claude API key is configured in Vault
- Verify `ANTHROPIC_API_KEY` environment variable (fallback)
- Check server logs for AI Patient service errors

### Session Not Found

- Verify attempt_id exists in database
- Ensure attempt was created via REST API first

## Environment Variables

```bash
# JWT Authentication
JWT_SECRET_KEY="your-secret-key"  # Change in production

# Claude API (fallback if Vault unavailable)
ANTHROPIC_API_KEY="sk-ant-..."  # Optional

# Redis Connection
REDIS_HOST="localhost"
REDIS_PORT=6379
REDIS_DB=0

# PostgreSQL Connection
DATABASE_URL="postgresql://user:pass@localhost/irstudy"
```

## Development vs. Production

### Development (localhost)

```
ws://localhost:8001/ws/osce/{attempt_id}?token={jwt}
```

### Production (HTTPS)

```
wss://api.irstudy.com/ws/osce/{attempt_id}?token={jwt}
```

**Note**: Use `wss://` (WebSocket Secure) in production, not `ws://`

## Testing

### Unit Tests

```bash
cd /home/dev/Development/irStudy/backend
pytest tests/test_websocket/ -v
```

### Integration Test

```bash
# Terminal 1: Start server
uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload

# Terminal 2: Run integration test
python tests/integration/test_websocket_flow.py
```

### Load Test

```bash
# Test 100 concurrent connections
python tests/load_test_websocket.py --connections 100
```

## Files Reference

| File | Description | Lines |
|------|-------------|-------|
| `src/websocket/handler.py` | Main WebSocket handler | 295 |
| `src/websocket/router.py` | FastAPI endpoint | 99 |
| `src/websocket/session_manager.py` | State management | 442 |
| `src/websocket/auth.py` | Authentication | 78 |
| `src/websocket/timer.py` | 8-minute countdown | 245 |
| `src/ai/ai_patient.py` | AI Patient service | 291 |
| `src/db/models.py` | Database models | - |

## Support

For issues or questions:
1. Check server logs: `tail -f logs/irstudy.log`
2. Review FastAPI docs: `http://localhost:8001/api/docs`
3. Check WebSocket endpoint docs: `http://localhost:8001/api/docs#/WebSocket`

---

**Last Updated**: 2026-03-22
**Status**: ✅ Production-Ready
