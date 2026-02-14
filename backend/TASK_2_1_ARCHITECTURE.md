# Task 2.1: WebSocket Authenticator Core - Architecture Diagram

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    WebSocket Client (Browser)                    │
│  Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...                 │
│  IP: 192.168.1.100                                               │
│  User-Agent: Mozilla/5.0                                         │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ WebSocket Connection Request
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              WebSocketAuthenticator (authenticator.py)           │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ authenticate(token, connection_id, ip, user_agent)        │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                   │
│  Step 1: JWT Validation                                          │
│  ┌─────────────────────────────────────────┐                    │
│  │ verify_access_token(token)              │◄─────────────┐     │
│  │ ↓                                        │              │     │
│  │ - Check signature (HS256)                │              │     │
│  │ - Check expiration                       │              │     │
│  │ - Extract user_id from "sub"             │              │     │
│  └─────────────────────────────────────────┘              │     │
│                                                             │     │
│  Step 2: Session Correlation                               │     │
│  ┌─────────────────────────────────────────┐              │     │
│  │ Redis: exists("session:{user_id}")      │──────────┐   │     │
│  │ ↓                                        │          │   │     │
│  │ - Verify session exists                 │          │   │     │
│  │ - Check not expired                      │          │   │     │
│  └─────────────────────────────────────────┘          │   │     │
│                                                         │   │     │
│  Step 3: Token Fingerprinting                          │   │     │
│  ┌─────────────────────────────────────────┐          │   │     │
│  │ fingerprint = sha256(ip + ua + screen)  │          │   │     │
│  │ ↓                                        │          │   │     │
│  │ - Compare with stored fingerprint        │          │   │     │
│  │ - Detect session hijacking               │          │   │     │
│  └─────────────────────────────────────────┘          │   │     │
│                                                         │   │     │
│  Step 4: Rate Limiting                                 │   │     │
│  ┌─────────────────────────────────────────┐          │   │     │
│  │ RateLimiter.check_rate_limit(user_id)   │──────┐   │   │     │
│  │ ↓                                        │      │   │   │     │
│  │ - Check 10 requests per 60 seconds      │      │   │   │     │
│  │ - Sliding window algorithm               │      │   │   │     │
│  └─────────────────────────────────────────┘      │   │   │     │
│                                                     │   │   │     │
│  Step 5: Connection Tracking                       │   │   │     │
│  ┌─────────────────────────────────────────┐      │   │   │     │
│  │ ConnectionTracker.add_connection()      │──┐   │   │   │     │
│  │ ↓                                        │  │   │   │   │     │
│  │ - Check max 3 concurrent connections    │  │   │   │   │     │
│  │ - Store connection metadata              │  │   │   │   │     │
│  └─────────────────────────────────────────┘  │   │   │   │     │
│                                                 │   │   │   │     │
│  Step 6: Security Event Logging                │   │   │   │     │
│  ┌─────────────────────────────────────────┐  │   │   │   │     │
│  │ _log_security_event()                   │──┼───┼───┼───┼──┐  │
│  │ ↓                                        │  │   │   │   │  │  │
│  │ - Log to Redis (30-day retention)       │  │   │   │   │  │  │
│  │ - Anonymize PHI (IP, user_id)           │  │   │   │   │  │  │
│  └─────────────────────────────────────────┘  │   │   │   │  │  │
│                                                 │   │   │   │  │  │
│  Return: AuthenticationResult                  │   │   │   │  │  │
│  ┌─────────────────────────────────────────┐  │   │   │   │  │  │
│  │ success: true                           │  │   │   │   │  │  │
│  │ user_id: "test-user-12345"              │  │   │   │   │  │  │
│  │ message: "Authentication successful"    │  │   │   │   │  │  │
│  │ metadata: {latency_ms: 18.42}           │  │   │   │   │  │  │
│  └─────────────────────────────────────────┘  │   │   │   │  │  │
└────────────────────────────────────────────────┼───┼───┼───┼──┼──┘
                                                  │   │   │   │  │
                                                  ▼   ▼   ▼   ▼  ▼
┌─────────────────────────────────────────────────────────────────┐
│                       Redis (Data Store)                         │
│  ┌──────────────────┬──────────────────┬──────────────────────┐ │
│  │ RateLimiter      │ ConnectionTracker│ Security Events      │ │
│  ├──────────────────┼──────────────────┼──────────────────────┤ │
│  │ Data Structure:  │ Data Structure:  │ Data Structure:      │ │
│  │ Sorted Sets      │ Hashes           │ Strings (JSON)       │ │
│  │                  │                  │                      │ │
│  │ Key Pattern:     │ Key Pattern:     │ Key Pattern:         │ │
│  │ ratelimit:ws:    │ connections:     │ audit:ws:            │ │
│  │   {user_id}      │   {user_id}      │   {event_type}:      │ │
│  │                  │                  │   {timestamp}        │ │
│  │ Operations:      │ Operations:      │ Operations:          │ │
│  │ - ZADD           │ - HSET           │ - SETEX (30 days)    │ │
│  │ - ZCOUNT         │ - HGET           │ - GET                │ │
│  │ - ZREMRANGE      │ - HDEL           │                      │ │
│  │                  │ - HGETALL        │                      │ │
│  │ Performance:     │ Performance:     │ Performance:         │ │
│  │ O(log N)         │ O(1)             │ O(1)                 │ │
│  └──────────────────┴──────────────────┴──────────────────────┘ │
│                                                                   │
│  Session Data (from Week 1):                                     │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ Key: session:{user_id}                                  │    │
│  │ Value: {                                                │    │
│  │   "user_id": "test-user-12345",                         │    │
│  │   "email": "test@example.com",                          │    │
│  │   "fingerprint": "8a3f2b1c..."  (SHA-256 hash)          │    │
│  │ }                                                        │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                         ▲
                         │
                         │ Uses Vault-backed URL
                         │ (no hardcoded credentials)
                         │
┌─────────────────────────────────────────────────────────────────┐
│                  Configuration (config.py)                       │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ settings.redis_url → Vault: amc-simulation/database     │   │
│  │   redis_host: localhost                                 │   │
│  │   redis_port: 7379                                      │   │
│  │   redis_password: *** (from Vault, not hardcoded)       │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## Component Interaction Flow

### 1. RateLimiter (rate_limiter.py)

```
User makes connection attempt
         │
         ▼
check_rate_limit(user_id)
         │
         ├─► Redis Pipeline:
         │   ├─ ZREMRANGEBYSCORE: Remove old entries (>60s ago)
         │   ├─ ZCOUNT: Count requests in window
         │   ├─ ZADD: Add current timestamp
         │   └─ EXPIRE: Set TTL for cleanup
         │
         ▼
Return (allowed, current_count, remaining)
```

### 2. ConnectionTracker (connection_tracker.py)

```
User establishes connection
         │
         ▼
add_connection(user_id, connection_id, ip, ua)
         │
         ├─► Cleanup stale connections
         │   └─ Check last_heartbeat > 5 minutes
         │
         ├─► Check connection limit
         │   └─ HLEN connections:{user_id} < 3?
         │
         ├─► Store connection metadata
         │   └─ HSET connections:{user_id}
         │       {connection_id: {ip, ua, timestamp}}
         │
         ▼
Return (success, message)

Heartbeat (every 30s)
         │
         ▼
update_heartbeat(user_id, connection_id)
         │
         └─► Update last_heartbeat timestamp
```

### 3. WebSocketAuthenticator (authenticator.py)

```
Authentication Request
         │
         ▼
JWT Validation ───► Session Correlation ───► Fingerprinting
         │                   │                      │
         │                   │                      │
         ▼                   ▼                      ▼
Rate Limiting ───► Connection Tracking ───► Security Logging
         │                   │                      │
         │                   │                      │
         ▼                   ▼                      ▼
Return AuthenticationResult (success/failure + metadata)
```

## Security Architecture

### Zero-Trust Principles

1. **JWT Validation**: Never trust client tokens without verification
2. **Session Correlation**: Token valid ≠ session valid (double-check)
3. **Fingerprinting**: Detect session hijacking (IP/UA change)
4. **Rate Limiting**: Prevent brute-force and DoS attacks
5. **Connection Tracking**: Limit resources per user
6. **Audit Logging**: Full security event trail

### PHI Protection

```python
# Input:
user_id = "test-user-12345678"
ip_address = "192.168.1.100"

# Logged (anonymized):
anonymized_user_id = "test-use***"     # First 8 chars only
anonymized_ip = "192.168.1.***"         # First 3 octets only

# Audit event:
{
  "user_id": "test-use***",
  "ip_address": "192.168.1.***",
  "event_type": "ws_auth_success"
}
```

### Performance Optimizations

1. **Redis Pipeline**: Atomic operations (reduce round-trips)
2. **Sorted Sets**: O(log N) for rate limiting
3. **Hash Operations**: O(1) for connection tracking
4. **Lazy Cleanup**: Only clean stale connections when needed

## Error Handling

```
Authentication Flow
         │
         ├─► JWT Invalid?
         │   └─ Return: "Invalid or expired token" (400)
         │
         ├─► Session Not Found?
         │   └─ Return: "Session not found or expired" (401)
         │
         ├─► Fingerprint Mismatch?
         │   └─ Return: "Token fingerprint mismatch" (403)
         │       Log: CRITICAL security event
         │
         ├─► Rate Limit Exceeded?
         │   └─ Return: "Rate limit exceeded" (429)
         │
         ├─► Max Connections?
         │   └─ Return: "Maximum 3 concurrent connections" (403)
         │
         └─► Success
             └─ Return: AuthenticationResult (200)
                Metadata: {latency_ms, rate_limit_remaining}
```

## Integration Points

### Existing Systems (Week 1)

- **JWT Validation**: `backend/src/auth/security.py::verify_access_token()`
- **Configuration**: `backend/src/config.py::get_settings()`
- **User Model**: `backend/src/db/models.py::User`

### Future Systems (Week 2+)

- **WebSocket Endpoint**: `backend/src/api/v1/websocket.py` (Task 2.2)
- **Real-time Events**: `backend/src/websocket/events.py` (Task 2.3)
- **Frontend Client**: `frontend/src/websocket/client.ts` (Task 2.4)

---

**Prepared by**: security-compliance-expert agent  
**Date**: 2026-02-07  
**Version**: 1.0
