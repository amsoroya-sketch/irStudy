# Week 2 Task Delegation Plan

**Sprint**: Week 2 (2026-02-07 to 2026-02-17)  
**PM**: Project Manager Agent  
**Sprint Goal**: Enhanced WebSocket Authentication with Zero-Trust Security

---

## Delegation Strategy

### Sequential Validation Approach
We will use **sequential validation** (not parallel) to prevent systematic errors:

1. Delegate Task 2.1 → Validate → Proceed
2. Delegate Task 2.2 → Validate → Proceed
3. Delegate Task 2.3 → Validate → Proceed
4. Delegate Task 2.4 → Validate → Complete

**Rationale**: Each task depends on previous task's correctness. Parallel execution could compound errors.

---

## Task 2.1 Delegation: WebSocket Authenticator

### Agent: security-compliance-expert
### Estimated Time: 6 hours
### Priority: P0 (Critical Path)

### Pre-Delegation Checklist
- [ ] Read WEEK2_WEBSOCKET_AUTH_SPRINT_PLAN.md
- [ ] Verify Redis cluster running (6 nodes, 7379-7384)
- [ ] Verify Vault accessible (http://localhost:8200)
- [ ] Review existing JWT infrastructure (backend/src/auth/)

### Delegation Prompt

```markdown
You are the security-compliance-expert agent for the irStudy AMC Clinical Exam Platform.

## Task: Implement WebSocket Authenticator Core (Task 2.1)

## Background
Week 1 completed JWT authentication infrastructure. Week 2 focuses on WebSocket security with zero-trust architecture.

## Critical Constraints (READ FIRST)

### Security Requirements
1. **NO hardcoded credentials** (ZERO TOLERANCE)
   - All Redis URLs from environment: os.getenv("REDIS_URL")
   - All Vault secrets from environment
   - No mock user IDs, even for testing

2. **Read existing patterns**:
   - JWT validation: /home/dev/Development/irStudy/backend/src/auth/security.py
   - Redis async: Use redis.asyncio library
   - Database patterns: /home/dev/Development/irStudy/backend/src/db/models.py

3. **Project constraints**:
   - Read: /home/dev/Development/irStudy/constraints/03-security-configuration.md
   - Follow all security patterns documented there

### Performance Requirements
- Authentication latency <50ms (p95)
- Support 100+ concurrent connections
- Rate limit: 10 connections/minute per user
- Max 3 concurrent connections per user

## Implementation Tasks

### Step 1: Create Directory Structure
```bash
mkdir -p /home/dev/Development/irStudy/backend/src/websocket
touch /home/dev/Development/irStudy/backend/src/websocket/__init__.py
```

### Step 2: Implement WebSocketAuthenticator
**File**: /home/dev/Development/irStudy/backend/src/websocket/authenticator.py

**Requirements**:
1. JWT token validation (reuse backend/src/auth/security.py)
2. Session correlation (verify session in Redis: session:{user_id})
3. Token fingerprinting (SHA-256 hash of IP + User-Agent + screen resolution)
4. Rate limiting integration (RateLimiter class)
5. Connection tracking integration (ConnectionTracker class)
6. Security event logging (all authentication attempts)

**Code Skeleton**: See WEEK2_WEBSOCKET_AUTH_SPRINT_PLAN.md section 2.1.2

### Step 3: Implement RateLimiter
**File**: /home/dev/Development/irStudy/backend/src/websocket/rate_limiter.py

**Algorithm**: Redis sorted sets (sliding window)
**Requirements**:
- Sliding window algorithm (not fixed window)
- Redis sorted sets for time-based operations
- Automatic cleanup of old entries
- Max 10 requests per 60 seconds per user

**Code Skeleton**: See WEEK2_WEBSOCKET_AUTH_SPRINT_PLAN.md section 2.1.3

### Step 4: Implement ConnectionTracker
**File**: /home/dev/Development/irStudy/backend/src/websocket/connection_tracker.py

**Requirements**:
- Track active connections per user (Redis hash)
- Enforce max 3 concurrent connections
- Store connection metadata (IP, User-Agent, timestamp)
- Heartbeat mechanism (prevent stale connections)
- Automatic cleanup

**Code Skeleton**: See WEEK2_WEBSOCKET_AUTH_SPRINT_PLAN.md section 2.1.4

### Step 5: Write Unit Tests
**File**: /home/dev/Development/irStudy/backend/tests/test_websocket_auth.py

**Test Cases**:
- JWT validation (valid, expired, invalid signature)
- Session correlation (exists, not found)
- Token fingerprinting (match, mismatch)
- Rate limiting (under limit, exceeded)
- Connection tracking (under limit, max connections)
- Performance (latency <50ms target)

**Code Skeleton**: See WEEK2_WEBSOCKET_AUTH_SPRINT_PLAN.md section 2.3.1

## Validation Checklist (COMPLETE BEFORE RETURNING)

### 1. Code Quality
- [ ] All files created in correct locations
- [ ] All functions have docstrings and type hints
- [ ] No hardcoded credentials (verified with grep)
- [ ] All Redis operations async (redis.asyncio)
- [ ] Error handling for all external calls

### 2. Security Scan
Run this command and verify 0 matches:
```bash
grep -r "redis://.*:.*@" /home/dev/Development/irStudy/backend/src/websocket/
grep -r "REDIS_URL\s*=\s*\"" /home/dev/Development/irStudy/backend/src/websocket/
```

Expected output: No matches (all secrets from environment)

### 3. Unit Tests
Run tests and verify 100% pass rate:
```bash
cd /home/dev/Development/irStudy
pytest backend/tests/test_websocket_auth.py -v --tb=short
```

Expected output:
```
======================== test session starts =========================
collected 15 tests

test_websocket_auth.py::test_authenticate_valid_token PASSED
test_websocket_auth.py::test_authenticate_expired_token PASSED
test_websocket_auth.py::test_authenticate_invalid_signature PASSED
test_websocket_auth.py::test_authenticate_session_not_found PASSED
test_websocket_auth.py::test_rate_limiter_under_limit PASSED
test_websocket_auth.py::test_rate_limiter_exceeded PASSED
test_websocket_auth.py::test_connection_tracker_under_limit PASSED
test_websocket_auth.py::test_connection_tracker_max_connections PASSED
test_websocket_auth.py::test_connection_tracker_add_remove PASSED
test_websocket_auth.py::test_fingerprint_generation PASSED
test_websocket_auth.py::test_authentication_latency_target PASSED
test_websocket_auth.py::test_security_event_logging PASSED

======================== 12 passed in 2.45s ==========================
```

### 4. Performance Validation
Run latency test specifically:
```bash
pytest backend/tests/test_websocket_auth.py::test_authentication_latency_target -v
```

Expected: p95 latency <50ms

### 5. Code Review
- [ ] Reused existing JWT functions (no duplication)
- [ ] Followed existing code patterns (see backend/src/auth/)
- [ ] Security events logged for all auth attempts
- [ ] Prometheus metrics emitted (websocket_auth_success, websocket_auth_latency_ms)

## Example Code Patterns

### Pattern 1: JWT Token Validation
```python
from auth.security import verify_access_token

# ✅ CORRECT: Reuse existing function
payload = verify_access_token(token)
if payload is None:
    return AuthenticationResult(success=False, error="Invalid token")

# ❌ INCORRECT: Don't reimplement JWT validation
try:
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
except:
    ...
```

### Pattern 2: Redis Async Operations
```python
import redis.asyncio as redis

# ✅ CORRECT: Use environment variable
redis_client = redis.from_url(
    os.getenv("REDIS_URL", "redis://localhost:7379"),
    encoding="utf-8",
    decode_responses=True
)

# ❌ INCORRECT: Hardcoded URL
redis_client = redis.from_url("redis://localhost:7379")
```

### Pattern 3: Security Event Logging
```python
# ✅ CORRECT: Log with structured data
await self._log_security_event(
    event_type="ws_auth_failed",
    user_id=user_id,
    ip_address=ip_address,
    metadata={"reason": "invalid_token"},
    severity="high"
)

# ❌ INCORRECT: Generic logging
self.logger.error(f"Auth failed for user {user_id}")
```

## Success Criteria

Task 2.1 is complete when:
- ✅ All 4 files created (authenticator.py, rate_limiter.py, connection_tracker.py, test_websocket_auth.py)
- ✅ 100% test pass rate (pytest)
- ✅ 0 hardcoded credentials (security scan)
- ✅ <50ms authentication latency (p95)
- ✅ All validation checklist items checked

## Deliverables

1. **Code Files**:
   - backend/src/websocket/__init__.py
   - backend/src/websocket/authenticator.py
   - backend/src/websocket/rate_limiter.py
   - backend/src/websocket/connection_tracker.py

2. **Test Files**:
   - backend/tests/test_websocket_auth.py

3. **Validation Output**:
   - pytest output (100% pass rate)
   - Security scan output (0 violations)
   - Performance test output (latency metrics)

## Next Steps After Completion

After Task 2.1 is validated:
1. PM will review code and test results
2. PM will run final security scan
3. PM will delegate Task 2.2 (Security Event Logging)

---

**Estimated Completion**: 6 hours  
**Status**: Ready to start  
**Dependencies**: None (all Week 1 infrastructure available)
```

### Post-Delegation Validation (PM Responsibility)

After agent completes Task 2.1, PM MUST validate:

#### 1. Run Full Test Suite
```bash
cd /home/dev/Development/irStudy
pytest backend/tests/test_websocket_auth.py -v --tb=short --cov=backend/src/websocket --cov-report=term
```

**Expected**:
- 100% test pass rate
- >80% code coverage
- No failures or errors

#### 2. Security Scan
```bash
cd /home/dev/Development/irStudy

# Check for hardcoded credentials
grep -r "redis://.*:.*@" backend/src/websocket/
grep -r "REDIS_URL\s*=\s*\"redis://" backend/src/websocket/
grep -r "VAULT_.*=\s*\"" backend/src/websocket/

# Expected: No matches
```

#### 3. Code Review
- [ ] All functions have docstrings
- [ ] Type hints present on all function signatures
- [ ] Error handling for all Redis operations
- [ ] Security events logged for all auth attempts
- [ ] No code duplication (JWT validation reused)

#### 4. Performance Validation
```bash
# Run performance-specific tests
pytest backend/tests/test_websocket_auth.py::test_authentication_latency_target -v -s
```

**Expected**:
- p95 latency <50ms
- Test passes

#### 5. Integration Check
```bash
# Verify Redis connection works
python -c "
import asyncio
import redis.asyncio as redis
import os

async def test():
    client = redis.from_url(os.getenv('REDIS_URL', 'redis://localhost:7379'))
    await client.set('test_key', 'test_value')
    value = await client.get('test_key')
    await client.delete('test_key')
    await client.close()
    print(f'Redis test: {value}')

asyncio.run(test())
"
```

**Expected**: Redis test: test_value

### Decision Gate: Proceed to Task 2.2?

**Criteria**:
- ✅ All validation steps passed
- ✅ 100% test pass rate
- ✅ 0 security violations
- ✅ Performance target met (<50ms)
- ✅ Code review passed

**If ANY criterion fails**:
1. Document failures in WEEK2_ISSUES.md
2. Create fix task and delegate back to security-compliance-expert
3. DO NOT proceed to Task 2.2 until resolved

**If all criteria pass**:
- Mark Task 2.1 as COMPLETE
- Proceed to Task 2.2 delegation

---

## Task 2.2 Delegation: Security Event Logging

### Agent: security-compliance-expert
### Estimated Time: 4 hours
### Priority: P1
### Dependencies: Task 2.1 complete

### Pre-Delegation Checklist
- [ ] Task 2.1 validated and approved
- [ ] WebSocketAuthenticator working
- [ ] Vault accessible and credentials available

### Delegation Prompt

```markdown
You are the security-compliance-expert agent for the irStudy AMC Clinical Exam Platform.

## Task: Implement Security Event Logging System (Task 2.2)

## Background
Task 2.1 completed WebSocket authentication. Now we need to implement a robust security event logging system with Vault integration for long-term SIEM analysis.

## Critical Constraints

### Security Requirements
1. **NO hardcoded Vault credentials**
   - Vault address: os.getenv("VAULT_ADDR", "http://localhost:8200")
   - Vault token: os.getenv("VAULT_TOKEN")

2. **Read existing patterns**:
   - Review: /home/dev/Development/irStudy/backend/tests/test_vault.py
   - Follow Vault client patterns there

3. **Event retention**:
   - Redis: Max 1000 events (most recent)
   - Vault: Permanent storage (audit log)
   - Batch flush every 60 seconds

## Implementation Tasks

### Step 1: Create Security Events Module
**File**: /home/dev/Development/irStudy/backend/src/security/events.py

**Requirements**:
1. SecurityEvent dataclass with schema
2. SecurityEventLogger class
3. Batch processor (background task, flush every 60s)
4. Prometheus metrics export
5. Vault audit log integration

**Code Skeleton**: See WEEK2_WEBSOCKET_AUTH_SPRINT_PLAN.md section 2.2.1

### Step 2: Integrate with WebSocketAuthenticator
Update authenticator.py to use SecurityEventLogger instead of inline logging.

**Changes Required**:
```python
# In WebSocketAuthenticator.__init__
self.event_logger = SecurityEventLogger(redis_client, vault_client)

# Replace all _log_security_event calls
await self.event_logger.log_event(
    event_type="ws_auth_failed",
    user_id=user_id,
    ip_address=ip_address,
    metadata={"reason": "invalid_token"},
    severity="high"
)
```

### Step 3: Write Unit Tests
**File**: /home/dev/Development/irStudy/backend/tests/test_security_events.py

**Test Cases**:
- Event logging to Redis
- Batch flush to Vault (60s interval)
- Prometheus metrics export
- Event retention (max 1000)
- Background task lifecycle (start/stop)

## Validation Checklist

### 1. Code Quality
- [ ] SecurityEvent dataclass defined with all fields
- [ ] SecurityEventLogger implements batch processing
- [ ] Background task properly handled (start/stop)
- [ ] Error handling for Vault failures
- [ ] No hardcoded credentials

### 2. Security Scan
```bash
grep -r "VAULT_.*=\s*\"" /home/dev/Development/irStudy/backend/src/security/
```

Expected: No matches

### 3. Unit Tests
```bash
pytest backend/tests/test_security_events.py -v
```

Expected: 100% pass rate

### 4. Integration Test
```bash
# Test full event flow (Redis → Vault)
python -c "
import asyncio
from security.events import SecurityEventLogger
import redis.asyncio as redis
import hvac

async def test():
    redis_client = redis.from_url('redis://localhost:7379')
    vault_client = hvac.Client(url='http://localhost:8200')
    
    logger = SecurityEventLogger(redis_client, vault_client)
    
    # Log event
    await logger.log_event(
        event_type='test_event',
        user_id=123,
        severity='info'
    )
    
    # Verify in Redis
    events = await logger.get_recent_events(limit=10)
    print(f'Events in Redis: {len(events)}')
    
    await redis_client.close()

asyncio.run(test())
"
```

Expected: Events in Redis: 1

## Success Criteria

- ✅ SecurityEventLogger implemented
- ✅ Batch processor working (60s interval)
- ✅ Vault integration working
- ✅ Prometheus metrics exported
- ✅ 100% test pass rate
- ✅ 0 hardcoded credentials

## Deliverables

1. backend/src/security/__init__.py
2. backend/src/security/events.py
3. backend/tests/test_security_events.py
4. Updated backend/src/websocket/authenticator.py
```

### Post-Delegation Validation (PM)

Same validation steps as Task 2.1:
1. Run tests (100% pass rate)
2. Security scan (0 violations)
3. Code review
4. Integration test (Vault write successful)

---

## Task 2.3 Delegation: Load Testing

### Agent: testing-qa-expert
### Estimated Time: 6 hours
### Priority: P1
### Dependencies: Tasks 2.1 and 2.2 complete

### Delegation Prompt

```markdown
You are the testing-qa-expert agent for the irStudy AMC Clinical Exam Platform.

## Task: Create Load Test for WebSocket Authentication (Task 2.3)

## Background
WebSocket authentication system complete (Tasks 2.1 and 2.2). Need comprehensive load testing to validate performance under stress.

## Test Requirements

### 1. Unit Tests (Enhancement)
**File**: /home/dev/Development/irStudy/backend/tests/test_websocket_auth.py

Review existing tests and add:
- Edge case tests (empty token, malformed token)
- Concurrent connection tests (race conditions)
- Cleanup tests (disconnection handling)

### 2. Integration Tests
**File**: /home/dev/Development/irStudy/backend/tests/test_websocket_integration.py

**Requirements**:
- Real Redis integration (no mocks)
- Real Vault integration (read secrets)
- Full authentication flow (end-to-end)

### 3. Load Test Script
**File**: /home/dev/Development/irStudy/backend/tests/load_test_websocket.py

**Requirements**:
- Simulate 100 concurrent connections
- Distribute across 10 users (10 connections per user)
- Measure latency distribution (p50, p95, p99)
- Verify rate limiting enforcement
- Verify connection tracking accuracy
- Generate detailed report

**Code Skeleton**: See WEEK2_WEBSOCKET_AUTH_SPRINT_PLAN.md section 2.3.3

### 4. Test Report
**File**: /home/dev/Development/irStudy/WEEK2_LOAD_TEST_REPORT.md

**Contents**:
- Test configuration (100 connections, 10 users)
- Results summary (success rate, latencies)
- Performance metrics (p50, p95, p99)
- Rate limiting effectiveness
- Connection tracking accuracy
- Pass/fail against targets
- Recommendations for optimization

## Validation Checklist

### 1. Unit Tests
```bash
pytest backend/tests/test_websocket_auth.py -v --cov=backend/src/websocket
```

Expected: >80% coverage, 100% pass rate

### 2. Integration Tests
```bash
pytest backend/tests/test_websocket_integration.py -v
```

Expected: 100% pass rate

### 3. Load Test
```bash
python backend/tests/load_test_websocket.py
```

Expected Output:
```
LOAD TEST RESULTS
================================================================================
Total connections:     100
Unique users:          10
Total time:            5.23s
Connections/second:    19.12

Successful:            85 (85.0%)
Failed:                15
Errors:                0

LATENCY METRICS:
  Average:             32.45ms
  p50:                 28.12ms
  p95:                 47.89ms ✅
  p99:                 52.34ms

✅ PASS: p95 latency < 50ms

FAILURE REASONS:
  Too many connection attempts: 10 (rate limiting working)
  Maximum concurrent connections: 5 (connection tracking working)
================================================================================
```

## Success Criteria

- ✅ Load test handles 100 concurrent connections
- ✅ p95 latency <50ms
- ✅ Rate limiting prevents >10 connections/min
- ✅ Connection tracking enforces max 3 concurrent
- ✅ Test report generated with analysis
- ✅ All tests pass (unit + integration + load)

## Deliverables

1. Enhanced unit tests (test_websocket_auth.py)
2. Integration tests (test_websocket_integration.py)
3. Load test script (load_test_websocket.py)
4. Test report (WEEK2_LOAD_TEST_REPORT.md)
```

### Post-Delegation Validation (PM)

1. Review load test report
2. Verify p95 latency <50ms
3. Confirm rate limiting working
4. Confirm connection tracking working
5. Validate test coverage >80%

---

## Task 2.4 Delegation: Documentation

### Agent: security-compliance-expert
### Estimated Time: 2 hours
### Priority: P2
### Dependencies: All implementation tasks complete

### Delegation Prompt

```markdown
## Task: Create Security Documentation (Task 2.4)

## Documents to Create

### 1. WebSocket Security Runbook
**File**: /home/dev/Development/irStudy/backend/docs/WEBSOCKET_SECURITY_RUNBOOK.md

**Contents**:
- Architecture overview (diagram)
- Authentication flow (step-by-step)
- Rate limiting configuration
- Connection tracking limits
- Security event types
- Troubleshooting guide
- Monitoring setup (Prometheus + Grafana)

### 2. API Documentation
**File**: /home/dev/Development/irStudy/backend/docs/WEBSOCKET_API.md

**Contents**:
- WebSocket connection endpoint
- Authentication handshake protocol
- Message format schemas
- Error codes and meanings
- Client examples (JavaScript, Python)

## Success Criteria

- ✅ Runbook covers all security features
- ✅ API docs complete with examples
- ✅ Troubleshooting guide tested
- ✅ Diagrams created (Mermaid format)
```

---

## Summary

### Delegation Order
1. Task 2.1: security-compliance-expert (6 hours)
2. Task 2.2: security-compliance-expert (4 hours)
3. Task 2.3: testing-qa-expert (6 hours)
4. Task 2.4: security-compliance-expert (2 hours)

### Total Estimated Time
18 hours over 10 days = ~2 hours per day (sustainable pace)

### Success Metrics
- 100% test pass rate
- 0 hardcoded credentials
- <50ms p95 authentication latency
- 100 concurrent connections supported
- Complete documentation

---

**Status**: Ready to delegate Task 2.1  
**Next Action**: Copy Task 2.1 delegation prompt and send to security-compliance-expert
