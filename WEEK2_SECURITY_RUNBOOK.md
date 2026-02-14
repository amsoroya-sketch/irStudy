# Week 2 Security Runbook - WebSocket Authentication

**Version**: 1.0  
**Last Updated**: 2026-02-07  
**Maintainer**: Security Operations Team  
**Project**: AMC Clinical Exam Simulation v2.0  
**Sprint**: Week 2 - Enhanced WebSocket Authentication

---

## Overview

Week 2 implements a comprehensive zero-trust WebSocket authentication system with 6-step validation, security event logging, and real-time monitoring. This runbook provides operational procedures for security incidents, monitoring, and emergency response.

### Security Features Summary

- **Zero-Trust Authentication**: 6-step validation (JWT, session, fingerprint, rate limits, connection tracking, logging)
- **Security Event Logging**: Dual storage (Redis + Vault) with 60-second batch processing
- **Rate Limiting**: 10 connections/60 seconds per user (sliding window)
- **Connection Tracking**: Maximum 3 concurrent connections per user
- **Prometheus Metrics**: Real-time monitoring and alerting
- **PII Anonymization**: User IDs and IP addresses anonymized in logs

---

## Authentication Flow

### 6-Step Zero-Trust Authentication

**Step 1: JWT Token Validation**

**Purpose**: Verify token signature, expiration, and claims

**Implementation**:
```python
# Reuses backend/src/auth/security.py verify_access_token()
payload = jwt.decode(token, jwt_secret, algorithms=["HS256"])
# Validates: signature, expiration, token_type="access"
```

**Error Handling**:
- Invalid signature → 401 Unauthorized: "Invalid token signature"
- Expired token → 401 Unauthorized: "Token has expired"
- Wrong token type → 401 Unauthorized: "Invalid token type"
- Missing claims → 401 Unauthorized: "Invalid token format"

**Recovery**:
1. Client requests new token via `/api/v1/auth/login`
2. Client retries WebSocket connection with new token

---

**Step 2: Session Correlation**

**Purpose**: Verify session exists in Redis and belongs to authenticated user

**Implementation**:
```python
# Check session exists: session:{user_id}
session_data = await redis.get(f"session:{user_id}")
if not session_data:
    return AuthenticationResult(success=False, message="Session not found")
```

**Error Handling**:
- Session not found → 403 Forbidden: "Session not found or expired"
- Session user mismatch → 403 Forbidden: "Session does not belong to user"

**Recovery**:
1. Client logs out and logs back in to create new session
2. Client retries WebSocket connection

---

**Step 3: Token Fingerprinting**

**Purpose**: Detect token theft/replay attacks via device fingerprint

**Implementation**:
```python
# Generate fingerprint: SHA-256(IP + User-Agent + screen resolution)
fingerprint_data = f"{ip_address}{user_agent}{screen_resolution}"
current_fingerprint = hashlib.sha256(fingerprint_data.encode()).hexdigest()

# Compare with stored fingerprint
if current_fingerprint != stored_fingerprint:
    await log_security_event("ws_fingerprint_mismatch", severity="critical")
    # Allow connection but log for investigation
```

**Error Handling**:
- Fingerprint mismatch → **WARNING** logged (connection allowed, investigation triggered)

**Investigation Procedure**:
1. Check security events for `ws_fingerprint_mismatch` from user
2. Verify if user changed device/browser/network
3. If suspicious: Force logout user, require re-authentication
4. If legitimate: Update fingerprint in session

---

**Step 4: Rate Limiting**

**Purpose**: Prevent DoS attacks and connection abuse

**Implementation**:
```python
# Sliding window: 10 connections/60 seconds per user
# Redis sorted set: ws:ratelimit:{user_id}
allowed = await rate_limiter.check_rate_limit(user_id)
if not allowed:
    return AuthenticationResult(
        success=False,
        message="Rate limit exceeded",
        metadata={"retry_after": retry_after_seconds}
    )
```

**Error Handling**:
- Rate limit exceeded → 429 Too Many Requests
- Retry-After header returned with seconds to wait

**Recovery**:
1. Client waits `retry_after` seconds
2. Client retries connection
3. If persistent: Investigate potential DoS attack

**Admin Override**:
```bash
# Reset rate limit for user (emergency)
redis-cli -p 7379 DEL "ws:ratelimit:user-12345678"
```

---

**Step 5: Connection Tracking**

**Purpose**: Enforce maximum concurrent connections per user

**Implementation**:
```python
# Max 3 concurrent connections per user
# Redis hash: ws:connections:{user_id}
active_count = await connection_tracker.get_connection_count(user_id)
if active_count >= 3:
    return AuthenticationResult(
        success=False,
        message="Maximum concurrent connections exceeded"
    )
```

**Error Handling**:
- Max connections exceeded → 403 Forbidden: "Maximum concurrent connections (3) exceeded"

**Recovery**:
1. Client closes unused WebSocket connections
2. Client retries new connection
3. If stale connections present: Wait 5 minutes for heartbeat timeout

**Admin Override**:
```bash
# Force disconnect all user connections (emergency)
redis-cli -p 7379 DEL "ws:connections:user-12345678"
```

---

**Step 6: Security Event Logging**

**Purpose**: Audit trail for compliance and incident investigation

**Implementation**:
```python
# Log all authentication attempts (success/failure)
await event_logger.log_event(
    event_type="ws_auth_success",  # or "ws_auth_failed"
    user_id=user_id,
    ip_address=ip_address,
    metadata={"connection_id": conn_id, "latency_ms": 25.5},
    severity="info"  # or "high" for failures
)
```

**Storage**:
- **Redis**: 1000 most recent events (real-time queries)
- **Vault**: Permanent storage at `audit/security_events/{YYYY-MM-DD}`

**Retention**:
- Redis: 1000 events (rolling, ~1-2 days typical)
- Vault: Permanent (HIPAA compliance)

---

## Security Events

### Event Types

| Event Type | Description | Severity | Action Required |
|------------|-------------|----------|-----------------|
| `ws_auth_success` | Successful WebSocket authentication | info | None (routine) |
| `ws_auth_failed` | Failed authentication attempt | high | Monitor for patterns |
| `ws_fingerprint_mismatch` | Token fingerprint mismatch detected | critical | Investigate immediately |
| `ws_rate_limit_exceeded` | User exceeded rate limit | medium | Monitor for DoS |
| `ws_max_connections` | Max concurrent connections exceeded | low | Normal (user has 3+ tabs) |
| `ws_disconnect` | WebSocket disconnection | info | None (routine) |
| `ws_session_not_found` | Session missing in Redis | high | Possible session hijacking |

### Severity Levels

- **info**: Routine events (successful auth, normal disconnect)
- **low**: Minor security events (max connections, expected failures)
- **medium**: Potential abuse (rate limit, repeated failures)
- **high**: Security concerns (session not found, invalid tokens)
- **critical**: Serious threats (fingerprint mismatch, session hijacking)

### Event Retention

**Redis** (real-time queries):
- Capacity: 1000 most recent events
- TTL: Rolling window (oldest evicted when 1001st event added)
- Query latency: <5ms

**Vault** (permanent audit log):
- Storage path: `audit/security_events/{YYYY-MM-DD}`
- Batch interval: 60 seconds
- Retention: Permanent (HIPAA requirement)
- Format: JSON with event array

---

## Monitoring

### Prometheus Metrics

#### Security Events Metrics

**1. security_events_total**
```
Type: Counter
Labels: event_type, severity
Description: Total security events logged
```

**Example Queries**:
```promql
# Total failed authentication attempts (last 1 hour)
increase(security_events_total{event_type="ws_auth_failed"}[1h])

# Critical security events (last 5 minutes)
increase(security_events_total{severity="critical"}[5m])

# Authentication success rate
rate(security_events_total{event_type="ws_auth_success"}[5m]) 
  / 
rate(security_events_total{event_type=~"ws_auth_.*"}[5m])
```

**2. security_events_flush_latency_ms**
```
Type: Histogram
Buckets: [10, 50, 100, 200, 500, 1000, 2000, 5000]
Description: Vault batch flush latency
```

**Example Queries**:
```promql
# P95 flush latency (should be <500ms)
histogram_quantile(0.95, 
  rate(security_events_flush_latency_ms_bucket[5m]))

# Average flush latency
rate(security_events_flush_latency_ms_sum[5m]) 
  / 
rate(security_events_flush_latency_ms_count[5m])
```

**3. security_events_vault_errors_total**
```
Type: Counter
Labels: error_type
Description: Vault errors during event flush
```

**Example Queries**:
```promql
# Vault connection errors (last 5 minutes)
increase(security_events_vault_errors_total{error_type="connection"}[5m])

# Total Vault errors rate
rate(security_events_vault_errors_total[5m])
```

### Alerting Rules

**Critical Alerts** (page security team immediately):

```yaml
# Alert: High rate of authentication failures
- alert: HighAuthFailureRate
  expr: rate(security_events_total{event_type="ws_auth_failed"}[5m]) > 10
  for: 5m
  labels:
    severity: critical
  annotations:
    summary: "High WebSocket authentication failure rate"
    description: "{{ $value }} failed auth attempts/sec (threshold: 10/sec)"

# Alert: Fingerprint mismatch detected
- alert: FingerprintMismatch
  expr: increase(security_events_total{event_type="ws_fingerprint_mismatch"}[5m]) > 0
  for: 1m
  labels:
    severity: critical
  annotations:
    summary: "Token fingerprint mismatch detected"
    description: "Possible token theft - investigate immediately"

# Alert: Vault flush failures
- alert: VaultFlushFailures
  expr: rate(security_events_vault_errors_total[5m]) > 0.1
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "Vault audit log flush failing"
    description: "Events not being persisted to Vault"
```

**Warning Alerts** (monitor closely):

```yaml
# Alert: High rate limit rejections
- alert: HighRateLimitRejections
  expr: rate(security_events_total{event_type="ws_rate_limit_exceeded"}[5m]) > 5
  for: 10m
  labels:
    severity: warning
  annotations:
    summary: "High rate limit rejections"
    description: "Possible DoS attack or misconfigured client"

# Alert: Slow Vault flush
- alert: SlowVaultFlush
  expr: histogram_quantile(0.95, rate(security_events_flush_latency_ms_bucket[5m])) > 1000
  for: 10m
  labels:
    severity: warning
  annotations:
    summary: "Slow Vault flush operations"
    description: "P95 flush latency {{ $value }}ms (threshold: 1000ms)"
```

---

## Incident Response

### Common Security Incidents

#### 1. High Failed Authentication Rate

**Symptoms**:
- Alert: `HighAuthFailureRate` triggered
- Prometheus shows spike in `ws_auth_failed` events

**Investigation**:
```bash
# 1. Query recent failed authentication events
redis-cli -p 7379 LRANGE "security:events" 0 100 | grep ws_auth_failed

# 2. Check event distribution by user
vault kv get -format=json audit/security_events/$(date +%Y-%m-%d) | \
  jq '.data.data.events[] | select(.event_type=="ws_auth_failed") | .user_id' | \
  sort | uniq -c | sort -rn

# 3. Check for IP-based attack
vault kv get -format=json audit/security_events/$(date +%Y-%m-%d) | \
  jq '.data.data.events[] | select(.event_type=="ws_auth_failed") | .ip_address' | \
  sort | uniq -c | sort -rn
```

**Remediation**:
- **Single user**: Password reset, force logout
- **Multiple users**: Check for expired tokens, JWT secret rotation
- **Single IP**: Block IP at firewall level
- **Distributed**: Possible DDoS, enable Cloudflare rate limiting

---

#### 2. Token Fingerprint Mismatch

**Symptoms**:
- Alert: `FingerprintMismatch` triggered
- Critical severity security event logged

**Investigation**:
```bash
# 1. Get fingerprint mismatch events
vault kv get -format=json audit/security_events/$(date +%Y-%m-%d) | \
  jq '.data.data.events[] | select(.event_type=="ws_fingerprint_mismatch")'

# 2. Check user's recent activity
redis-cli -p 7379 LRANGE "security:events" 0 1000 | \
  grep "user-12345678" | tail -50

# 3. Verify user's session
redis-cli -p 7379 GET "session:user-12345678"
```

**Remediation**:
- **Legitimate**: User changed device/network/browser - update fingerprint
- **Suspicious**: Force logout user, require password reset
- **Confirmed theft**: Invalidate all user sessions, notify user, incident report

**Force Logout**:
```bash
# Invalidate user session
redis-cli -p 7379 DEL "session:user-12345678"

# Disconnect all WebSocket connections
redis-cli -p 7379 DEL "ws:connections:user-12345678"
```

---

#### 3. Rate Limit Abuse

**Symptoms**:
- Alert: `HighRateLimitRejections` triggered
- Many `ws_rate_limit_exceeded` events

**Investigation**:
```bash
# 1. Identify users hitting rate limits
redis-cli -p 7379 KEYS "ws:ratelimit:*" | wc -l

# 2. Check specific user's rate limit data
redis-cli -p 7379 ZRANGE "ws:ratelimit:user-12345678" 0 -1 WITHSCORES

# 3. Check if legitimate (mobile app reconnecting) or attack
vault kv get -format=json audit/security_events/$(date +%Y-%m-%d) | \
  jq '.data.data.events[] | select(.event_type=="ws_rate_limit_exceeded") | .metadata'
```

**Remediation**:
- **Legitimate**: Increase rate limit for specific user temporarily
- **Bug**: Fix client code (reconnection logic)
- **Attack**: Block user/IP, investigate further

**Temporary Rate Limit Increase**:
```bash
# Clear rate limit for user (allows reconnection)
redis-cli -p 7379 DEL "ws:ratelimit:user-12345678"

# Note: Implement proper solution (e.g., exponential backoff in client)
```

---

#### 4. Vault Flush Failures

**Symptoms**:
- Alert: `VaultFlushFailures` triggered
- Events not being persisted to Vault

**Investigation**:
```bash
# 1. Check Vault availability
curl -s http://localhost:8200/v1/sys/health | jq

# 2. Check Vault token validity
vault token lookup

# 3. Check disk space (Vault storage)
df -h /vault/data

# 4. Check background task status
# (Check application logs for SecurityEventLogger errors)
```

**Remediation**:
- **Vault unavailable**: Restart Vault, check network
- **Token expired**: Rotate Vault token, update environment variable
- **Disk full**: Clear old Vault data, increase storage
- **Background task crashed**: Restart application (background task auto-restarts)

**Manual Flush** (if needed):
```python
# Connect to application container
# Execute Python:
from src.security.events import SecurityEventLogger
import redis.asyncio as redis

redis_client = redis.Redis.from_url("redis://localhost:7379")
logger = SecurityEventLogger(redis_client)
await logger.batch_flush()  # Manual flush
```

---

#### 5. Session Hijacking Attempt

**Symptoms**:
- Multiple `ws_session_not_found` events for same user
- User reports unexpected logouts

**Investigation**:
```bash
# 1. Check user's session status
redis-cli -p 7379 GET "session:user-12345678"

# 2. Check authentication events timeline
vault kv get -format=json audit/security_events/$(date +%Y-%m-%d) | \
  jq '.data.data.events[] | select(.user_id=="user-123***") | {timestamp, event_type, metadata}' | \
  less

# 3. Check for fingerprint mismatches
vault kv get -format=json audit/security_events/$(date +%Y-%m-%d) | \
  jq '.data.data.events[] | select(.user_id=="user-123***" and .event_type=="ws_fingerprint_mismatch")'
```

**Remediation**:
1. Force logout user immediately
2. Invalidate all user sessions
3. Require password reset
4. Contact user to verify recent activity
5. File incident report
6. Review logs for other affected users

---

## Rate Limiting

### Configuration

**Current Limits**:
- **Connections per user**: 10 per 60 seconds (sliding window)
- **Algorithm**: Redis sorted sets (ZADD, ZREMRANGEBYSCORE)
- **Enforcement**: Before connection establishment

**Data Structure**:
```
Key: ws:ratelimit:{user_id}
Type: Sorted Set
Members: Connection timestamp (Unix epoch)
Score: Connection timestamp (for sorting)
TTL: 60 seconds after last connection
```

### Adjusting Rate Limits

**Temporary Adjustment** (single user):
```bash
# Clear rate limit (allows immediate reconnection)
redis-cli -p 7379 DEL "ws:ratelimit:user-12345678"
```

**Permanent Adjustment** (code change):
```python
# backend/src/websocket/rate_limiter.py
class RateLimiter:
    def __init__(
        self,
        redis_client: redis.Redis,
        max_connections: int = 10,  # Change this
        window_seconds: int = 60    # Or this
    ):
```

**Recommended Limits by User Type**:
- Standard user: 10 connections/60s
- Premium user: 20 connections/60s
- Admin user: 50 connections/60s
- Service account: 100 connections/60s

### Troubleshooting Rate Limit Issues

**Problem**: Legitimate users being blocked

**Investigation**:
```bash
# Check user's connection pattern
redis-cli -p 7379 ZRANGE "ws:ratelimit:user-12345678" 0 -1 WITHSCORES

# Output: List of Unix timestamps
# If timestamps clustered: Legitimate burst
# If evenly distributed: Client reconnecting too frequently
```

**Solutions**:
- Client needs exponential backoff
- Increase rate limit temporarily
- Fix client reconnection logic
- Whitelist specific user (code change)

---

## Connection Tracking

### Configuration

**Current Limits**:
- **Max concurrent connections**: 3 per user
- **Heartbeat interval**: 30 seconds
- **Stale connection timeout**: 5 minutes (10 missed heartbeats)

**Data Structure**:
```
Key: ws:connections:{user_id}
Type: Hash
Fields: {connection_id} -> {JSON metadata}
Metadata: {
  "ip_address": "192.168.1.100",
  "user_agent": "Mozilla/5.0...",
  "connected_at": "2026-02-07T10:30:00Z",
  "last_heartbeat": "2026-02-07T10:35:00Z"
}
```

### Debugging Stale Connections

**Problem**: User cannot connect (3 stale connections present)

**Investigation**:
```bash
# 1. List user's active connections
redis-cli -p 7379 HGETALL "ws:connections:user-12345678"

# 2. Check last heartbeat timestamps
# If last_heartbeat >5 minutes old: Stale connection
```

**Manual Cleanup**:
```bash
# Remove specific stale connection
redis-cli -p 7379 HDEL "ws:connections:user-12345678" "conn-abc123"

# Remove all connections for user (emergency)
redis-cli -p 7379 DEL "ws:connections:user-12345678"
```

**Automated Cleanup** (application handles this):
```python
# ConnectionTracker.cleanup_stale_connections()
# Runs every 60 seconds via background task
# Removes connections with last_heartbeat >5 minutes old
```

### Heartbeat Mechanism

**Client Responsibility**:
```javascript
// Client sends ping every 30 seconds
setInterval(() => {
  websocket.send(JSON.stringify({type: "ping"}));
}, 30000);
```

**Server Responsibility**:
```python
# Update last_heartbeat timestamp on ping
await connection_tracker.update_heartbeat(user_id, connection_id)
```

**Monitoring**:
```bash
# Check if heartbeat mechanism working
redis-cli -p 7379 HGET "ws:connections:user-12345678" "conn-abc123" | \
  jq '.last_heartbeat'

# Should update every 30 seconds
```

---

## Vault Integration

### Storage Structure

**Audit Log Path**:
```
audit/security_events/{YYYY-MM-DD}
```

**Example**:
```
audit/security_events/2026-02-07
audit/security_events/2026-02-08
```

**Data Format**:
```json
{
  "events": [
    {
      "timestamp": "2026-02-07T10:30:45.123456Z",
      "event_type": "ws_auth_success",
      "user_id": "user-123***",
      "ip_address": "192.168.1.***",
      "metadata": {
        "connection_id": "conn-abc123",
        "latency_ms": 25.5
      },
      "severity": "info"
    }
  ],
  "count": 1245,
  "last_updated": "2026-02-07T23:59:59.999999Z"
}
```

### Backup/Restore Audit Logs

**Backup** (export Vault data):
```bash
# Export single day
vault kv get -format=json audit/security_events/2026-02-07 > \
  backup_2026-02-07.json

# Export entire month
for day in {01..31}; do
  vault kv get -format=json audit/security_events/2026-02-$day > \
    backup_2026-02-$day.json 2>/dev/null
done
```

**Restore** (import Vault data):
```bash
# Restore single day
vault kv put audit/security_events/2026-02-07 @backup_2026-02-07.json
```

### Querying Audit Logs

**Get events for specific date**:
```bash
vault kv get -format=json audit/security_events/2026-02-07 | \
  jq '.data.data'
```

**Filter by event type**:
```bash
vault kv get -format=json audit/security_events/2026-02-07 | \
  jq '.data.data.events[] | select(.event_type=="ws_auth_failed")'
```

**Filter by severity**:
```bash
vault kv get -format=json audit/security_events/2026-02-07 | \
  jq '.data.data.events[] | select(.severity=="critical")'
```

**Count events by type**:
```bash
vault kv get -format=json audit/security_events/2026-02-07 | \
  jq '.data.data.events | group_by(.event_type) | map({event_type: .[0].event_type, count: length})'
```

---

## Emergency Procedures

### Disable WebSocket Authentication (Emergency Only)

**⚠️ WARNING**: This bypasses all security controls. Use only in catastrophic failure.

**Procedure**:
1. Edit `backend/src/websocket/authenticator.py`
2. Comment out authentication checks (not recommended - fix actual issue instead)
3. Restart application

**Better Alternative**: Fix actual issue (Vault down, Redis down, etc.)

---

### Force Disconnect All Users

**Scenario**: Suspected security breach, need to force all re-authentication

**Procedure**:
```bash
# 1. Clear all WebSocket connections
redis-cli -p 7379 KEYS "ws:connections:*" | xargs redis-cli -p 7379 DEL

# 2. Clear all sessions (forces logout)
redis-cli -p 7379 KEYS "session:*" | xargs redis-cli -p 7379 DEL

# 3. Clear all rate limits (allows reconnection)
redis-cli -p 7379 KEYS "ws:ratelimit:*" | xargs redis-cli -p 7379 DEL

# 4. Log security event
echo "SECURITY INCIDENT: Force disconnect all users at $(date)" >> /var/log/security_incidents.log

# 5. Notify users via email/push notification
# (Implement in application code)
```

**Post-Incident**:
1. Investigate root cause
2. File incident report
3. Review all security events from past 24 hours
4. Rotate JWT secrets if compromised

---

### Rotate JWT Secret

**Scenario**: JWT secret potentially compromised

**Procedure**:
```bash
# 1. Generate new JWT secret
NEW_SECRET=$(openssl rand -hex 32)

# 2. Store in Vault
vault kv put amc-simulation/api-keys jwt_secret=$NEW_SECRET

# 3. Update environment variable (or restart with new Vault value)
export SECRET_KEY=$NEW_SECRET

# 4. Restart application
# All existing tokens now invalid - users must re-authenticate

# 5. Log security event
vault kv put audit/jwt_rotation date=$(date) reason="suspected_compromise"
```

**Note**: Gradual rotation (support 2 keys for 24 hours) not yet implemented.

---

## Troubleshooting

### High Authentication Latency

**Symptoms**:
- P95 latency >50ms (target: <50ms)
- Users reporting slow connection establishment

**Investigation**:
```bash
# 1. Check Redis latency
redis-cli -p 7379 --latency-history

# 2. Check Vault latency
time vault kv get amc-simulation/api-keys

# 3. Check network latency
ping localhost

# 4. Check application metrics
curl -s http://localhost:8000/metrics | grep security_events
```

**Common Causes**:
- Redis overloaded (too many connections)
- Network congestion
- Background task blocking (batch flush taking >50ms)
- CPU overloaded (JWT verification slow)

**Solutions**:
- Scale Redis (add replicas)
- Optimize batch flush (reduce batch size)
- Add JWT verification caching
- Scale application horizontally

---

### Security Events Not Logged

**Symptoms**:
- No events in Redis (`security:events` empty)
- Vault audit log not updating

**Investigation**:
```bash
# 1. Check Redis connection
redis-cli -p 7379 PING

# 2. Check Vault connection
vault status

# 3. Check background task status
# (Check application logs for SecurityEventLogger errors)

# 4. Check environment variables
echo $VAULT_ADDR
echo $VAULT_ROOT_TOKEN
```

**Common Causes**:
- Background task not started
- Vault token expired
- Redis connection failed
- Application crashed

**Solutions**:
```python
# Ensure background task started:
await event_logger.start_background_task()

# Check if running:
# Background task should run every 60 seconds
```

---

### Rate Limit Not Enforcing

**Symptoms**:
- Users connecting >10 times/60s
- No `ws_rate_limit_exceeded` events

**Investigation**:
```bash
# 1. Check rate limit data structure
redis-cli -p 7379 TYPE "ws:ratelimit:user-12345678"
# Should be: zset (sorted set)

# 2. Check rate limit entries
redis-cli -p 7379 ZRANGE "ws:ratelimit:user-12345678" 0 -1 WITHSCORES

# 3. Check application code
# Ensure check_rate_limit() called before authentication
```

**Common Causes**:
- Rate limit check skipped (bug)
- Redis data corrupted
- Clock skew (Unix timestamps incorrect)

**Solutions**:
- Fix application code
- Clear corrupted data: `redis-cli DEL ws:ratelimit:*`
- Sync system clock: `ntpdate time.nist.gov`

---

## Conclusion

This security runbook provides comprehensive operational procedures for Week 2 WebSocket authentication system. For additional documentation, see:

- **API Documentation**: `WEEK2_API_DOCUMENTATION.md`
- **Deployment Guide**: `WEEK2_DEPLOYMENT_GUIDE.md`
- **Operations Guide**: `WEEK2_OPERATIONS_GUIDE.md`

**For 24/7 Security Support**: Contact security team at `security@example.com`

---

**Revision History**:

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2026-02-07 | Initial release | Security Compliance Expert |

---

**Status**: ✅ PRODUCTION-READY
