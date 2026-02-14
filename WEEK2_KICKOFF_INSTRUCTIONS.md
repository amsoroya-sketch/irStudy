# Week 2 Kickoff Instructions - AMC Simulation v2.0

**Sprint:** Phase 1, Week 2 - Enhanced WebSocket Authentication
**Dates:** February 6-13, 2026
**Status:** Ready to Start
**Prerequisites:** Week 1 Complete ✅

---

## Pre-Development Checklist

Before starting Week 2 implementation, validate Week 1 deliverables:

### Step 1: Verify Infrastructure Services (15 minutes)

```bash
# Navigate to project directory
cd /home/dev/Development/irStudy

# Check if services are already running
docker ps | grep amc

# If not running, start them
docker-compose -f docker-compose.dev.yml up -d

# Wait 30-60 seconds for health checks
sleep 60

# Verify all services are healthy
docker-compose -f docker-compose.dev.yml ps

# Expected: All services show "healthy" status
# - amc-vault-dev (port 8200)
# - amc-postgres-dev (port 5432)
# - amc-redis-master-1 (port 6379)
# - amc-redis-master-2 (port 6380)
# - amc-redis-master-3 (port 6381)
# - amc-redis-replica-1 (port 6382)
# - amc-redis-replica-2 (port 6383)
# - amc-redis-replica-3 (port 6384)
# - amc-redis-sentinel-1 (port 26379)
```

**Troubleshooting:**
```bash
# If any service is unhealthy, check logs
docker logs amc-vault-dev
docker logs amc-postgres-dev

# If Redis cluster fails, manually initialize
docker exec amc-redis-master-1 redis-cli --cluster create \
  redis-master-1:6379 redis-master-2:6380 redis-master-3:6381 \
  redis-replica-1:6382 redis-replica-2:6383 redis-replica-3:6384 \
  --cluster-replicas 1 --cluster-yes -a $REDIS_PASSWORD
```

---

### Step 2: Validate Vault Integration (10 minutes)

```bash
# Activate Python virtual environment
source venv/bin/activate

# Set Vault environment variables
export VAULT_ADDR=http://localhost:8200
export VAULT_ROOT_TOKEN=dev-only-token-change-in-prod

# Verify Vault is accessible
curl -H "X-Vault-Token: $VAULT_ROOT_TOKEN" \
  $VAULT_ADDR/v1/sys/health

# Expected: HTTP 200 OK with JSON response

# Check if secrets are already stored
curl -H "X-Vault-Token: $VAULT_ROOT_TOKEN" \
  $VAULT_ADDR/v1/amc-simulation/data/database

# If secrets not found, run setup script
python backend/scripts/setup_vault.py

# Expected output:
# ✅ Connected to Vault successfully
# ✅ Database secrets stored successfully
# ✅ API keys stored successfully
# ✅ Vault setup complete!
```

---

### Step 3: Validate Database Schema (10 minutes)

```bash
# Check if schema already exists
docker exec amc-postgres-dev psql -U amc_user -d amc_simulation -c "\dt"

# If tables don't exist, apply migration
docker exec -i amc-postgres-dev psql -U amc_user -d amc_simulation \
  < backend/db/migrations/001_initial_schema_encrypted.sql

# Verify tables created
docker exec amc-postgres-dev psql -U amc_user -d amc_simulation -c "\dt"

# Expected output: List of 4 tables
# - users
# - patient_personas
# - osce_scenarios
# - osce_sessions

# Verify encryption functions created
docker exec amc-postgres-dev psql -U amc_user -d amc_simulation -c "\df encrypt_data"

# Expected: encrypt_data function exists
```

---

### Step 4: Run Week 1 Tests (5 minutes)

```bash
# Ensure pytest is installed
pip install pytest hvac cryptography pydantic-settings

# Run Vault integration tests
pytest backend/tests/test_vault.py -v

# Expected: All tests pass (15+ tests)
# - test_vault_connection
# - test_get_database_secrets
# - test_get_encryption_key
# - test_database_url
# - test_settings_singleton
```

**Quality Gate:** All Week 1 tests must pass before proceeding to Week 2.

---

## Week 2 Overview

**Focus:** Enhanced WebSocket Authentication with Zero-Trust Security

**Goals:**
1. Implement multi-factor WebSocket authentication (JWT + session correlation + fingerprinting)
2. Add rate limiting (max 10 connections/minute per user)
3. Create security event logging for SIEM integration
4. Test with 100 concurrent connections

**Deliverables:**
- `backend/src/websocket/authenticator.py` (WebSocketAuthenticator class)
- `backend/src/websocket/rate_limiter.py` (Redis-backed rate limiting)
- `backend/src/security/events.py` (Security event logger)
- `backend/tests/test_websocket_auth.py` (Comprehensive test suite)
- Load test script for 100 concurrent connections

---

## Week 2 Task Breakdown

### Task 2.1: WebSocketAuthenticator Implementation (3 days)

**Complexity:** High
**Estimated Effort:** 18 hours
**Agent:** security-compliance-expert

**Sub-tasks:**
1. **JWT Token Validation** (4 hours)
   - Parse JWT from WebSocket connection query parameters
   - Validate signature using Vault-stored JWT secret
   - Verify token expiration and claims
   - Extract user_id from token

2. **Session Correlation** (4 hours)
   - Fetch session data from Redis
   - Verify session belongs to authenticated user
   - Log security event if user_id mismatch detected
   - Implement session refresh mechanism

3. **Token Fingerprinting** (3 hours)
   - Generate fingerprint from (IP + User-Agent + screen resolution)
   - Store fingerprint in Redis during initial authentication
   - Compare fingerprint on WebSocket connection
   - Flag suspicious connections (different fingerprint)

4. **Rate Limiting** (4 hours)
   - Implement sliding window rate limiter using Redis
   - Max 10 connections per minute per user
   - Track connection attempts in Redis sorted set
   - Return HTTP 429 if limit exceeded

5. **Connection Tracking** (3 hours)
   - Track active WebSocket connections per user
   - Store connection metadata (IP, timestamp, fingerprint)
   - Implement max 3 concurrent connections per user
   - Gracefully close oldest connection if limit exceeded

**Code Pattern:**
```python
# backend/src/websocket/authenticator.py
from datetime import datetime, timedelta
import jwt
import redis
from fastapi import WebSocket, HTTPException
from src.config import get_settings

class WebSocketAuthenticator:
    """Zero-trust WebSocket authentication with multi-factor validation"""

    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.settings = get_settings()

    async def authenticate(
        self,
        websocket: WebSocket,
        token: str,
        session_id: str,
        fingerprint: str
    ) -> dict:
        """
        Multi-factor authentication for WebSocket connections

        Returns:
            dict: {user_id, email, role, session_id}

        Raises:
            HTTPException: 403 if authentication fails
        """
        # Step 1: Validate JWT token
        try:
            jwt_secret = self.settings.jwt_secret
            payload = jwt.decode(token, jwt_secret, algorithms=["HS256"])
            user_id = payload.get("sub")
            email = payload.get("email")
            role = payload.get("role", "student")

            if not user_id:
                raise HTTPException(status_code=403, detail="Invalid token")
        except jwt.ExpiredSignatureError:
            self._log_security_event("TOKEN_EXPIRED", {"session_id": session_id})
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.InvalidTokenError:
            self._log_security_event("INVALID_TOKEN", {"session_id": session_id})
            raise HTTPException(status_code=403, detail="Invalid token")

        # Step 2: Verify session belongs to user (CRITICAL)
        session_key = f"session:{session_id}"
        session_data = self.redis.hgetall(session_key)

        if not session_data or session_data.get("user_id") != user_id:
            self._log_security_event("SESSION_HIJACK_ATTEMPT", {
                "session_id": session_id,
                "token_user_id": user_id,
                "session_user_id": session_data.get("user_id"),
                "ip": websocket.client.host
            })
            raise HTTPException(status_code=403, detail="Session mismatch")

        # Step 3: Token fingerprinting
        stored_fingerprint = self.redis.get(f"fingerprint:{user_id}")
        if stored_fingerprint and stored_fingerprint != fingerprint:
            self._log_security_event("FINGERPRINT_MISMATCH", {
                "user_id": user_id,
                "stored": stored_fingerprint,
                "received": fingerprint
            })
            # Don't block yet, just log for monitoring

        # Step 4: Rate limiting
        if not await self._check_rate_limit(user_id):
            self._log_security_event("RATE_LIMIT_EXCEEDED", {"user_id": user_id})
            raise HTTPException(status_code=429, detail="Too many connections")

        # Step 5: Connection tracking
        await self._track_connection(user_id, websocket, fingerprint)

        return {
            "user_id": user_id,
            "email": email,
            "role": role,
            "session_id": session_id
        }

    async def _check_rate_limit(self, user_id: str) -> bool:
        """Check if user is within rate limit (10 connections/minute)"""
        key = f"rate_limit:{user_id}"
        now = datetime.now().timestamp()
        minute_ago = now - 60

        # Remove old entries
        self.redis.zremrangebyscore(key, 0, minute_ago)

        # Count recent connections
        count = self.redis.zcard(key)

        if count >= 10:
            return False

        # Add current connection attempt
        self.redis.zadd(key, {str(now): now})
        self.redis.expire(key, 60)

        return True

    async def _track_connection(self, user_id: str, websocket: WebSocket, fingerprint: str):
        """Track active connection with metadata"""
        connection_id = f"{user_id}:{datetime.now().timestamp()}"
        connection_key = f"active_connections:{user_id}"

        connection_data = {
            "connection_id": connection_id,
            "ip": websocket.client.host,
            "fingerprint": fingerprint,
            "connected_at": datetime.now().isoformat()
        }

        # Add to set of active connections
        self.redis.hset(connection_key, connection_id, str(connection_data))

        # Check concurrent connection limit (max 3)
        active_count = self.redis.hlen(connection_key)
        if active_count > 3:
            # Close oldest connection
            oldest = sorted(self.redis.hgetall(connection_key).keys())[0]
            self.redis.hdel(connection_key, oldest)
            self._log_security_event("CONNECTION_LIMIT_EXCEEDED", {
                "user_id": user_id,
                "closed_connection": oldest
            })

    def _log_security_event(self, event_type: str, metadata: dict):
        """Log security event for SIEM integration"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "metadata": metadata
        }
        # Store in Redis list for batch processing
        self.redis.lpush("security_events", str(event))
        self.redis.ltrim("security_events", 0, 999)  # Keep last 1000 events
```

**Quality Gates:**
- [ ] JWT validation works with valid tokens
- [ ] JWT validation rejects expired/invalid tokens
- [ ] Session correlation detects hijack attempts
- [ ] Rate limiter blocks after 10 connections/minute
- [ ] Connection tracking enforces max 3 concurrent connections
- [ ] Security events logged to Redis
- [ ] All tests pass (pytest backend/tests/test_websocket_auth.py -v)

---

### Task 2.2: Security Event Logging (1 day)

**Complexity:** Medium
**Estimated Effort:** 6 hours
**Agent:** security-compliance-expert

**Sub-tasks:**
1. Create security event schema
2. Implement batch event processor
3. Add Prometheus metrics export
4. Create dashboard visualization

**Deliverable:** `backend/src/security/events.py`

**Quality Gates:**
- [ ] Events stored in structured format
- [ ] Batch processor flushes every 60 seconds
- [ ] Prometheus metrics exported
- [ ] Dashboard shows real-time security events

---

### Task 2.3: Load Testing (1 day)

**Complexity:** Medium
**Estimated Effort:** 6 hours
**Agent:** testing-qa-expert

**Sub-tasks:**
1. Create load test script with 100 concurrent connections
2. Verify rate limiting under load
3. Measure latency (target: <50ms authentication)
4. Generate load test report

**Deliverable:** `backend/tests/load_test_websocket.py`

**Quality Gates:**
- [ ] 100 concurrent connections established successfully
- [ ] Rate limiting works under load
- [ ] Authentication latency <50ms (p95)
- [ ] No memory leaks after 10-minute test
- [ ] Load test report generated

---

## Week 2 Success Criteria

**Security:**
- [ ] Zero-trust authentication implemented (JWT + session + fingerprint)
- [ ] Rate limiting prevents abuse (max 10 connections/minute)
- [ ] Security events logged for all suspicious activity
- [ ] No hardcoded secrets (all from Vault)

**Performance:**
- [ ] Authentication latency <50ms (p95)
- [ ] Handles 100 concurrent connections
- [ ] Redis memory usage <100MB for connection tracking

**Testing:**
- [ ] All unit tests pass (100% pass rate)
- [ ] Load test passes with 100 connections
- [ ] Security event logging validated

**Documentation:**
- [ ] WebSocket authentication flow diagram created
- [ ] Security event types documented
- [ ] Week 2 completion summary written

---

## Starting Week 2 Development

Once Week 1 validation is complete, use Agent OS to coordinate Week 2 implementation:

```bash
# In Claude Code, delegate to project-manager-coordinator
"Start Week 2 implementation: Enhanced WebSocket Authentication

Use agent-os project-manager-coordinator to coordinate:

Task 2.1: security-compliance-expert → Implement WebSocketAuthenticator
Task 2.2: security-compliance-expert → Create security event logging
Task 2.3: testing-qa-expert → Create load test script

Per PROJECT_CONSTRAINTS.md:
- All secrets from Vault (no hardcoded credentials)
- Follow zero-trust architecture pattern
- Test-driven development (tests first, then implementation)
- 100% test pass rate before task completion

Constraints:
- Use Redis for rate limiting and connection tracking
- Log all security events for SIEM integration
- Target <50ms authentication latency
- Support 100 concurrent connections

Quality Gates:
- pytest backend/tests/test_websocket_auth.py -v (all pass)
- Load test with 100 connections succeeds
- Security scan shows 0 hardcoded credentials
"
```

---

## Week 2 Timeline

| Day | Focus | Deliverable |
|-----|-------|-------------|
| **Day 1** | JWT + Session Validation | WebSocketAuthenticator class (partial) |
| **Day 2** | Rate Limiting + Fingerprinting | WebSocketAuthenticator class (complete) |
| **Day 3** | Connection Tracking + Tests | Test suite passing |
| **Day 4** | Security Event Logging | Security event system |
| **Day 5** | Load Testing + Documentation | Week 2 complete |

---

## Expected Completion Date

**Week 2 End Date:** February 13, 2026
**Production Readiness:** 40% (Week 2 of 12 weeks)

---

## Next: Week 3 Preview

**Week 3 Focus:** Prompt Injection Defense & Input Validation

**Tasks:**
- Task 3.1: Implement prompt injection detector
- Task 3.2: Create input sanitization pipeline
- Task 3.3: Add conversation transcript monitoring

---

## Contact & Support

**Questions?** Review the following documents:
- ENHANCED_IMPLEMENTATION_PLAN.md (v2.0 architecture)
- PHASED_IMPLEMENTATION_ROADMAP.md (12-week plan)
- PROJECT_CONSTRAINTS.md (security requirements)

**Status:** Ready to start Week 2 development after Week 1 validation complete ✅
