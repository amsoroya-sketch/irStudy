# AI OSCE Simulation - Operations & Deployment Review

**Date:** 2026-02-09
**Reviewer:** DevOps Engineer
**Architecture Reference:** AI_OSCE_SIMULATION_INTEGRATION_ARCHITECTURE.md
**Status:** Production Readiness Assessment

---

## 1. Deployment Architecture

```ascii
┌─────────────────────────────────────────────────────────────────────┐
│                          PRODUCTION DEPLOYMENT                       │
└─────────────────────────────────────────────────────────────────────┘

                            ┌──────────────┐
                            │   Cloudflare │ (DDoS, WAF, Rate Limiting)
                            │   DNS + CDN  │
                            └──────┬───────┘
                                   │ HTTPS
                   ┌───────────────┴───────────────┐
                   │    Nginx Load Balancer        │
                   │    - SSL Termination          │
                   │    - Rate Limiting (backup)   │
                   │    - Request Routing          │
                   └───────────────┬───────────────┘
                                   │
        ┌──────────────────────────┼──────────────────────────┐
        │                          │                          │
┌───────▼───────┐         ┌────────▼────────┐       ┌────────▼────────┐
│  FastAPI      │         │  FastAPI        │       │  FastAPI        │
│  Backend 1    │         │  Backend 2      │       │  Backend 3      │
│  (8000)       │         │  (8000)         │       │  (8000)         │
│               │         │                 │       │                 │
│ - REST API    │         │ - REST API      │       │ - REST API      │
│ - WebSocket   │         │ - WebSocket     │       │ - WebSocket     │
└───────┬───────┘         └────────┬────────┘       └────────┬────────┘
        │                          │                          │
        └──────────────────────────┼──────────────────────────┘
                                   │
                   ┌───────────────┴───────────────┐
                   │                               │
        ┌──────────▼──────────┐         ┌─────────▼─────────┐
        │  Redis Cluster      │         │  PostgreSQL 16    │
        │  (Session State)    │         │  (Primary)        │
        │  - Master: 6379     │         │  Port: 5432       │
        │  - Replica: 6380    │         │                   │
        │  - Sentinel: 26379  │         │  Hot Standby      │
        └──────────┬──────────┘         │  (Read Replica)   │
                   │                    └─────────┬─────────┘
                   │                              │
        ┌──────────┴──────────┐         ┌────────▼─────────┐
        │  Celery Workers     │         │  Qdrant Vector   │
        │  - Count: 4         │         │  Database        │
        │  - Queues:          │         │  Port: 6333      │
        │    • osce_sessions  │         │  (42,647 chunks) │
        │    • scoring        │         └──────────────────┘
        │    • sync_jobs      │
        └─────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                      MONITORING & OBSERVABILITY                      │
└─────────────────────────────────────────────────────────────────────┘

    ┌──────────────┐      ┌──────────────┐      ┌──────────────┐
    │  Prometheus  │─────►│   Grafana    │      │  Sentry.io   │
    │  (Metrics)   │      │  (Dashboard) │      │  (Errors)    │
    │  Port: 9090  │      │  Port: 3000  │      │              │
    └──────┬───────┘      └──────────────┘      └──────────────┘
           │
           │ Scrape targets every 15s
           │
    ┌──────▼───────────────────────────────────────────────────┐
    │ - backend:8000/metrics (FastAPI)                         │
    │ - redis_exporter:9121                                    │
    │ - postgres_exporter:9187                                 │
    │ - node_exporter:9100 (system metrics)                    │
    └──────────────────────────────────────────────────────────┘
```

### Infrastructure Requirements

| Component | Minimum Spec | Recommended Spec | Notes |
|-----------|--------------|------------------|-------|
| **FastAPI Backend** | 2 vCPU, 4GB RAM | 4 vCPU, 8GB RAM | 3 instances (HA) |
| **PostgreSQL** | 4 vCPU, 8GB RAM | 8 vCPU, 16GB RAM | SSD storage required |
| **Redis** | 2 vCPU, 4GB RAM | 4 vCPU, 8GB RAM | Master + Replica |
| **Qdrant** | 4 vCPU, 6GB RAM | 8 vCPU, 12GB RAM | Vector similarity searches |
| **Celery Workers** | 2 vCPU, 4GB RAM | 4 vCPU, 8GB RAM | 4 workers recommended |
| **Load Balancer** | 1 vCPU, 2GB RAM | 2 vCPU, 4GB RAM | Nginx |

**Total Minimum:** 15 vCPU, 28GB RAM
**Total Recommended:** 30 vCPU, 56GB RAM

### Docker Compose Compatibility

Based on PROJECT_CONSTRAINTS.md (lines 225-237), all services use **Python 3.11** (not 3.12) for ML package compatibility:
- PyTorch 2.10.0 (Python 3.12 compatible)
- sentence-transformers 3.3.1
- transformers 4.48.0

Existing `docker-compose.yml` security features:
- Docker secrets for credentials
- Read-only root filesystems
- Capability dropping (no-new-privileges)
- Resource limits per service
- Health checks for all services

---

## 2. Top 5 Monitoring Metrics

### Metric 1: AI Response Latency (CRITICAL)

**Target:** <3s at p95, <5s at p99

```yaml
# Prometheus Configuration
# monitoring/prometheus.yml

scrape_configs:
  - job_name: 'irstudy_backend'
    scrape_interval: 15s
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'

# Alert Rule
groups:
  - name: ai_osce_latency
    interval: 30s
    rules:
      - alert: HighAIResponseLatency
        expr: histogram_quantile(0.95, rate(ai_response_duration_seconds_bucket[5m])) > 3
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "AI response latency p95 > 3s"
          description: "95th percentile AI response time is {{ $value }}s (target: <3s)"

      - alert: CriticalAIResponseLatency
        expr: histogram_quantile(0.99, rate(ai_response_duration_seconds_bucket[5m])) > 5
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "AI response latency p99 > 5s"
          description: "99th percentile AI response time is {{ $value }}s (target: <5s)"
```

**FastAPI Instrumentation:**

```python
# backend/src/main.py
from prometheus_client import Histogram, Counter
import time

ai_response_duration = Histogram(
    'ai_response_duration_seconds',
    'Time to generate AI Patient/Examiner response',
    ['model', 'session_type'],
    buckets=[0.5, 1.0, 1.5, 2.0, 3.0, 5.0, 10.0]
)

@app.websocket("/ws/osce/{attempt_id}")
async def osce_websocket(websocket: WebSocket, attempt_id: str):
    # ... authentication ...

    async for message in websocket.iter_text():
        start_time = time.time()

        # Generate AI response
        ai_response = await generate_ai_patient_response(message)

        # Record latency
        duration = time.time() - start_time
        ai_response_duration.labels(
            model='claude-3.5-sonnet',
            session_type='individual'
        ).observe(duration)

        await websocket.send_json(ai_response)
```

---

### Metric 2: Session Completion Rate

**Target:** >90% completion rate

```yaml
# Prometheus Alert
- alert: LowSessionCompletionRate
  expr: |
    (
      sum(rate(osce_sessions_completed_total[1h]))
      /
      sum(rate(osce_sessions_started_total[1h]))
    ) < 0.9
  for: 10m
  labels:
    severity: warning
  annotations:
    summary: "OSCE session completion rate below 90%"
    description: "Only {{ $value | humanizePercentage }} of sessions are being completed"
```

**Instrumentation:**

```python
from prometheus_client import Counter

osce_sessions_started = Counter(
    'osce_sessions_started_total',
    'Total OSCE sessions started',
    ['specialty', 'difficulty']
)

osce_sessions_completed = Counter(
    'osce_sessions_completed_total',
    'Total OSCE sessions completed (8 minutes)',
    ['specialty', 'difficulty', 'outcome']
)

osce_sessions_abandoned = Counter(
    'osce_sessions_abandoned_total',
    'Total OSCE sessions abandoned before completion',
    ['specialty', 'difficulty', 'abandonment_reason']
)
```

---

### Metric 3: AI Cost Per Session

**Target:** <$0.30 per session (with prompt caching: $0.045)

```yaml
# Prometheus Alert
- alert: HighAICostPerSession
  expr: |
    (
      sum(rate(ai_tokens_used_total{direction="output"}[1h])) * 15 / 1000000
      +
      sum(rate(ai_tokens_used_total{direction="input"}[1h])) * 3 / 1000000
    )
    /
    sum(rate(osce_sessions_completed_total[1h])) > 0.30
  for: 15m
  labels:
    severity: warning
  annotations:
    summary: "AI cost per session exceeds $0.30 target"
    description: "Current cost: ${{ $value | humanize }} per session"

- alert: DailyAIBudgetExceeded
  expr: |
    sum(increase(ai_cost_usd_total[24h])) > 50
  labels:
    severity: critical
  annotations:
    summary: "Daily AI budget exceeded $50"
    description: "Total AI spend in last 24h: ${{ $value }}"
```

**Instrumentation:**

```python
from prometheus_client import Counter

ai_tokens_used = Counter(
    'ai_tokens_used_total',
    'Total AI tokens consumed',
    ['model', 'direction', 'task']  # direction: input/output, task: patient/examiner
)

ai_cost_usd = Counter(
    'ai_cost_usd_total',
    'Total AI cost in USD',
    ['model', 'task']
)

# Track per session
async def generate_ai_patient_response(message: str):
    response = await claude_client.generate(...)

    # Record metrics
    ai_tokens_used.labels(
        model='claude-3.5-sonnet',
        direction='input',
        task='patient'
    ).inc(response.input_tokens)

    ai_tokens_used.labels(
        model='claude-3.5-sonnet',
        direction='output',
        task='patient'
    ).inc(response.output_tokens)

    # Calculate cost (Claude 3.5 Sonnet pricing)
    cost = (response.input_tokens * 3 / 1_000_000) + (response.output_tokens * 15 / 1_000_000)
    ai_cost_usd.labels(model='claude-3.5-sonnet', task='patient').inc(cost)
```

---

### Metric 4: Redis Replication Lag

**Target:** <100ms lag, <1s max

```yaml
# Prometheus Alert
- alert: HighRedisReplicationLag
  expr: redis_replication_lag_seconds > 1
  for: 2m
  labels:
    severity: critical
  annotations:
    summary: "Redis replication lag > 1 second"
    description: "Replica is {{ $value }}s behind master (risk of data loss)"

- alert: RedisReplicaDown
  expr: redis_connected_slaves < 1
  for: 1m
  labels:
    severity: critical
  annotations:
    summary: "Redis replica down - no failover capability"
```

**Redis Exporter Setup:**

```bash
# docker-compose.yml addition
  redis_exporter:
    image: oliver006/redis_exporter:latest
    container_name: irstudy-redis-exporter
    restart: unless-stopped
    environment:
      REDIS_ADDR: redis:6379
      REDIS_PASSWORD_FILE: /run/secrets/redis_password
    ports:
      - "9121:9121"
    networks:
      - irstudy-network
    secrets:
      - redis_password
```

---

### Metric 5: Concurrent WebSocket Connections

**Target:** <100 concurrent (system capacity), alert at >80

```yaml
# Prometheus Alert
- alert: HighConcurrentOSCESessions
  expr: websocket_connections_active{endpoint="/ws/osce"} > 80
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "High concurrent OSCE sessions (>80)"
    description: "Current: {{ $value }} concurrent sessions (capacity: 100)"

- alert: WebSocketConnectionCapacityReached
  expr: websocket_connections_active{endpoint="/ws/osce"} >= 100
  labels:
    severity: critical
  annotations:
    summary: "WebSocket capacity reached - scaling required"
```

**Instrumentation:**

```python
from prometheus_client import Gauge

websocket_connections_active = Gauge(
    'websocket_connections_active',
    'Active WebSocket connections',
    ['endpoint', 'user_type']
)

@app.websocket("/ws/osce/{attempt_id}")
async def osce_websocket(websocket: WebSocket, attempt_id: str):
    websocket_connections_active.labels(
        endpoint='/ws/osce',
        user_type='student'
    ).inc()

    try:
        # ... session logic ...
    finally:
        websocket_connections_active.labels(
            endpoint='/ws/osce',
            user_type='student'
        ).dec()
```

---

## 3. Critical Incident Runbooks

### Runbook 1: AI Response Latency Spike (>5s)

**Trigger:** Prometheus alert `CriticalAIResponseLatency`

**Severity:** P1 (Critical - Impacts all users)

**Step-by-Step Response:**

```bash
# STEP 1: Verify the issue (2 minutes)
# Check Grafana dashboard: http://grafana:3000/d/ai-osce-overview
# Verify p99 latency is actually >5s (not false alarm)

# STEP 2: Check Claude API status (1 minute)
curl -X GET https://status.anthropic.com/api/v2/status.json
# If Claude is degraded, proceed to STEP 3 (failover)
# If Claude is operational, proceed to STEP 4 (internal bottleneck)

# STEP 3: Failover to Kimi 2.5 (FREE fallback) (3 minutes)
# Check circuit breaker status
docker exec irstudy-backend python -c "
from src.ai_router import check_circuit_breaker_status
print(check_circuit_breaker_status())
"

# Manual override to force Kimi fallback
docker exec irstudy-backend python -c "
from src.ai_router import force_fallback_provider
force_fallback_provider('kimi')
print('✅ Forced fallback to Kimi 2.5')
"

# Verify failover working
curl http://localhost:8001/health/ai-router
# Expected: {"primary": "claude", "active": "kimi", "status": "circuit_open"}

# STEP 4: Check RAG query latency (if Claude is operational) (2 minutes)
docker exec irstudy-backend python -c "
import time
from qdrant_client import QdrantClient
client = QdrantClient(url='http://qdrant:6333')

start = time.time()
results = client.search(
    collection_name='medical_knowledge',
    query_vector=[0.1] * 384,  # Dummy query
    limit=5
)
duration = time.time() - start
print(f'Qdrant latency: {duration:.2f}s')
if duration > 1.0:
    print('⚠️ Qdrant is slow - restart required')
"

# If Qdrant is slow (>1s), restart it
docker restart irstudy-qdrant
# Wait 30s for health check
sleep 30
docker ps | grep irstudy-qdrant  # Should show "healthy"

# STEP 5: Check Redis session state cache (2 minutes)
docker exec irstudy-redis redis-cli --no-auth-warning \
    -a $(cat secrets/redis_password.txt) \
    --latency-history

# If latency >50ms, investigate Redis memory usage
docker exec irstudy-redis redis-cli --no-auth-warning \
    -a $(cat secrets/redis_password.txt) \
    INFO memory

# If memory usage >90%, clear expired sessions manually
docker exec irstudy-backend python -c "
from src.tasks.session_cleanup import cleanup_expired_osce_sessions
cleanup_expired_osce_sessions()
print('✅ Expired sessions cleaned up')
"

# STEP 6: Scale backend horizontally (if all else fails) (5 minutes)
# Increase backend replicas from 3 to 5
docker-compose up -d --scale backend=5

# Verify all instances are healthy
for i in {1..5}; do
    curl -f http://backend-$i:8000/health || echo "Backend-$i unhealthy"
done

# STEP 7: Monitor recovery (10 minutes)
# Watch Grafana dashboard for latency returning to <3s
# Check Sentry for any new error spikes
# Verify session completion rate remains >90%

# STEP 8: Post-incident (30 minutes)
# Document root cause in incident log
# If Claude API was degraded, check if we need to increase rate limits
# If Qdrant was slow, schedule reindexing during off-peak hours
# If Redis was OOM, increase memory allocation or eviction policy
```

**Escalation:**
- If issue persists >15 minutes: Page on-call engineer
- If Claude API is down >1 hour: Email users about degraded service

---

### Runbook 2: Redis Master Down (Session State Loss)

**Trigger:** Prometheus alert `RedisReplicaDown` or `RedisMasterDown`

**Severity:** P0 (Critical - Data loss risk)

**Step-by-Step Response:**

```bash
# STEP 1: Verify Redis master is down (1 minute)
docker ps | grep irstudy-redis
# If container is stopped, proceed to STEP 2
# If container is running but unhealthy, proceed to STEP 3

# STEP 2: Promote replica to master (IMMEDIATE - 2 minutes)
# Check replication status
docker exec irstudy-redis-replica redis-cli --no-auth-warning \
    -a $(cat secrets/redis_password.txt) \
    INFO replication

# Output should show: role:slave, master_link_status:down

# Promote replica to master
docker exec irstudy-redis-replica redis-cli --no-auth-warning \
    -a $(cat secrets/redis_password.txt) \
    REPLICAOF NO ONE

# Verify promotion
docker exec irstudy-redis-replica redis-cli --no-auth-warning \
    -a $(cat secrets/redis_password.txt) \
    INFO replication
# Output should show: role:master

# Update backend to use new master IP
# Edit docker-compose.yml temporarily (or use DNS update)
# Restart backend services
docker-compose restart backend celery-worker

# STEP 3: Restart old master as replica (5 minutes)
docker-compose restart redis

# Wait for health check
sleep 30

# Configure old master as replica of new master
docker exec irstudy-redis redis-cli --no-auth-warning \
    -a $(cat secrets/redis_password.txt) \
    REPLICAOF redis-replica 6379

# Verify replication established
docker exec irstudy-redis redis-cli --no-auth-warning \
    -a $(cat secrets/redis_password.txt) \
    INFO replication
# Output should show: role:slave, master_link_status:up

# STEP 4: Assess data loss (10 minutes)
# Check PostgreSQL for last sync timestamp
docker exec irstudy-postgres psql -U postgres -d irstudy_medical -c "
SELECT
    COUNT(*) as active_sessions,
    MAX(updated_at) as last_sync
FROM osce_attempts
WHERE session_state IN ('conversation', 'warning_1min')
AND ended_at IS NULL;
"

# If last_sync was >30s ago, some session data may be lost
# Identify affected users
docker exec irstudy-postgres psql -U postgres -d irstudy_medical -c "
SELECT
    user_id,
    attempt_id,
    started_at,
    EXTRACT(EPOCH FROM (NOW() - updated_at)) as seconds_since_last_sync
FROM osce_attempts
WHERE session_state IN ('conversation', 'warning_1min')
AND ended_at IS NULL
AND updated_at < NOW() - INTERVAL '30 seconds'
ORDER BY seconds_since_last_sync DESC;
"

# STEP 5: Notify affected users (15 minutes)
# Create incident report for users who lost >2 minutes of session data
docker exec irstudy-backend python -c "
from src.services.incident_notification import notify_affected_users

affected_user_ids = [...]  # From STEP 4 query

notify_affected_users(
    user_ids=affected_user_ids,
    incident_type='redis_master_failure',
    message='Your OSCE session was interrupted due to a technical issue. You have been granted 1 free retry.',
    compensation='free_osce_session'
)
print(f'✅ Notified {len(affected_user_ids)} affected users')
"

# STEP 6: Enable Redis Sentinel (permanent fix) (30 minutes)
# Update docker-compose.yml to add Redis Sentinel
cat >> docker-compose.yml << 'EOF'
  redis-sentinel:
    image: redis:7-alpine
    container_name: irstudy-redis-sentinel
    restart: unless-stopped
    command: redis-sentinel /etc/redis/sentinel.conf
    volumes:
      - ./monitoring/redis-sentinel.conf:/etc/redis/sentinel.conf
    networks:
      - irstudy-network
EOF

# Create sentinel configuration
cat > monitoring/redis-sentinel.conf << 'EOF'
port 26379
sentinel monitor irstudy-master redis 6379 2
sentinel down-after-milliseconds irstudy-master 5000
sentinel parallel-syncs irstudy-master 1
sentinel failover-timeout irstudy-master 10000
sentinel auth-pass irstudy-master $(cat /run/secrets/redis_password)
EOF

# Deploy sentinel
docker-compose up -d redis-sentinel

# Verify sentinel is monitoring
docker exec irstudy-redis-sentinel redis-cli -p 26379 sentinel masters

# STEP 7: Post-incident review (1 hour)
# Calculate exact data loss window
# Review backup strategy (Redis AOF persistence)
# Update runbook with lessons learned
# Schedule Redis cluster upgrade planning session
```

**Prevention:**
- Implement Redis Sentinel for automatic failover
- Enable Redis AOF (Append-Only File) persistence
- Increase sync_active_osce_sessions() frequency from 30s to 15s

---

### Runbook 3: AI Cost Budget Exceeded ($50/day)

**Trigger:** Prometheus alert `DailyAIBudgetExceeded`

**Severity:** P2 (High - Financial impact)

**Step-by-Step Response:**

```bash
# STEP 1: Verify budget exceeded (2 minutes)
# Check Grafana cost dashboard
curl -s http://localhost:9090/api/v1/query?query='sum(increase(ai_cost_usd_total[24h]))' | jq

# If cost is genuinely >$50, proceed immediately

# STEP 2: IMMEDIATE - Switch to free Kimi fallback (1 minute)
docker exec irstudy-backend python -c "
from src.ai_router import force_fallback_provider
force_fallback_provider('kimi', reason='budget_exceeded')
print('✅ Switched to Kimi 2.5 (FREE) - Claude spending stopped')
"

# Verify fallback active
curl http://localhost:8001/health/ai-router
# Expected: {"active": "kimi", "reason": "budget_exceeded"}

# STEP 3: Analyze cost breakdown (10 minutes)
docker exec irstudy-postgres psql -U postgres -d irstudy_medical << 'EOF'
-- Find sessions with abnormal token usage
SELECT
    attempt_id,
    user_id,
    persona_id,
    total_tokens_used,
    llm_cost_usd,
    total_messages,
    duration_seconds,
    (total_tokens_used::float / NULLIF(total_messages, 0)) as tokens_per_message
FROM osce_attempts
WHERE started_at >= NOW() - INTERVAL '24 hours'
AND total_tokens_used > 50000  -- Abnormal: >50K tokens per session
ORDER BY total_tokens_used DESC
LIMIT 20;
EOF

# Identify outliers:
# - Normal session: ~7K tokens, $0.045
# - Outlier: >50K tokens, >$0.30

# STEP 4: Investigate outlier sessions (15 minutes)
# Check conversation transcripts for abuse patterns
docker exec irstudy-postgres psql -U postgres -d irstudy_medical -c "
SELECT
    conversation_history,
    student_actions
FROM osce_attempts
WHERE attempt_id = 'OUTLIER_ATTEMPT_ID';
" | less

# Red flags to look for:
# - Student spamming very long messages
# - Looping conversation (same questions repeated)
# - Attempt to manipulate AI (prompt injection)

# STEP 5: Block abusive users (immediate)
# If abuse detected, suspend user accounts
docker exec irstudy-backend python -c "
from src.services.user_management import suspend_user

abusive_user_ids = [...]  # From STEP 3 analysis

for user_id in abusive_user_ids:
    suspend_user(
        user_id=user_id,
        reason='excessive_ai_usage',
        duration_days=7
    )
    print(f'✅ Suspended user {user_id} for 7 days')
"

# STEP 6: Implement stricter rate limits (30 minutes)
# Add per-user daily token cap
docker exec irstudy-backend python -c "
from src.api.v1.osces import update_rate_limits

update_rate_limits({
    'max_tokens_per_session': 30000,  # Hard cap (down from 50K)
    'max_sessions_per_user_per_day': 10,  # Daily limit
    'max_messages_per_session': 30,  # Prevent spam
})
print('✅ Stricter rate limits applied')
"

# Restart backend to apply limits
docker-compose restart backend

# STEP 7: Optimize prompt caching (if not enabled) (1 hour)
# Verify Claude prompt caching is enabled
docker exec irstudy-backend python -c "
from src.ai_router.claude_client import check_prompt_caching_status
status = check_prompt_caching_status()
print(f'Prompt caching: {status}')
"

# If not enabled, enable it (saves 40% on input tokens)
# Edit backend/src/ai_router/claude_client.py
# Add: cache_control={"type": "ephemeral"} to system prompts

# STEP 8: Project remaining budget (10 minutes)
# Calculate burn rate with new limits
docker exec irstudy-postgres psql -U postgres -d irstudy_medical << 'EOF'
SELECT
    DATE_TRUNC('hour', started_at) as hour,
    COUNT(*) as sessions,
    SUM(llm_cost_usd) as hourly_cost,
    AVG(llm_cost_usd) as avg_cost_per_session
FROM osce_attempts
WHERE started_at >= NOW() - INTERVAL '24 hours'
GROUP BY hour
ORDER BY hour DESC;
EOF

# Project daily cost with new limits: ~$30/day (safe)

# STEP 9: Communication (30 minutes)
# Notify stakeholders about cost incident
# Email to product owner:
cat > /tmp/cost_incident_report.txt << 'EOF'
Subject: AI OSCE Cost Budget Exceeded - Mitigation Applied

Incident Summary:
- Daily AI cost exceeded $50 threshold at 14:35 UTC
- Root cause: 5 users with abnormal token usage (>50K tokens/session)
- Immediate action: Switched to free Kimi fallback provider
- Permanent fix: Stricter rate limits (30K tokens/session, 10 sessions/day)

Financial Impact:
- Estimated overspend: $15 (total $65 for the day)
- Projected daily cost with new limits: $30/day
- Monthly projection: $900/month (within $1,335 budget)

User Impact:
- All active sessions switched to Kimi (slightly lower quality)
- 5 abusive users suspended for 7 days
- 95% of users unaffected (normal usage patterns)

Next Steps:
- Monitor cost for 48 hours
- Switch back to Claude primary when budget resets (midnight UTC)
- Schedule prompt optimization review

Incident Owner: DevOps Team
EOF

# STEP 10: Schedule Claude re-enablement (next day)
# Set cron job to switch back to Claude at midnight UTC
crontab -e
# Add: 0 0 * * * docker exec irstudy-backend python -c "from src.ai_router import reset_to_primary_provider; reset_to_primary_provider()"
```

**Prevention:**
- Implement per-user token quotas
- Enable prompt caching (40% savings)
- Add client-side message length limits (max 500 chars)
- Monitor daily spend in real-time (alert at $40)

---

## 4. CI/CD Pipeline

### GitHub Actions Workflow

**File:** `.github/workflows/deploy-production.yml`

```yaml
name: Deploy AI OSCE to Production

on:
  push:
    branches:
      - main
    paths:
      - 'backend/**'
      - 'docker-compose.yml'
      - '.github/workflows/deploy-production.yml'
  workflow_dispatch:  # Manual trigger

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}/backend

jobs:
  # ============================================================================
  # JOB 1: Security Scan & Test
  # ============================================================================
  security-and-test:
    runs-on: ubuntu-latest
    timeout-minutes: 30

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python 3.11
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install pytest pytest-cov pytest-asyncio

      - name: Run unit tests
        run: |
          cd backend
          pytest tests/ -v --cov=src --cov-report=xml --cov-report=term

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          file: backend/coverage.xml
          fail_ci_if_error: false

      - name: Security scan - Bandit (Python)
        run: |
          pip install bandit
          bandit -r backend/src -ll -f json -o bandit-report.json || true
          cat bandit-report.json

      - name: Security scan - Safety (Dependencies)
        run: |
          pip install safety
          safety check --json || true

      - name: Build Docker image
        run: |
          docker build -t irstudy-backend:test -f backend/Dockerfile backend/

      - name: Container security scan - Trivy
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: 'irstudy-backend:test'
          format: 'sarif'
          output: 'trivy-results.sarif'
          severity: 'CRITICAL,HIGH'

      - name: Upload Trivy results to GitHub Security
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'

  # ============================================================================
  # JOB 2: Build & Push Docker Image
  # ============================================================================
  build-and-push:
    runs-on: ubuntu-latest
    needs: security-and-test
    timeout-minutes: 20

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Log in to GitHub Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata (tags, labels)
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=sha,prefix={{branch}}-
            type=ref,event=branch
            type=semver,pattern={{version}}

      - name: Build and push Docker image
        uses: docker/build-push-action@v5
        with:
          context: ./backend
          file: ./backend/Dockerfile
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  # ============================================================================
  # JOB 3: Database Migration (Staging)
  # ============================================================================
  migrate-staging:
    runs-on: ubuntu-latest
    needs: build-and-push
    environment: staging
    timeout-minutes: 10

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python 3.11
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install alembic psycopg2-binary

      - name: Run Alembic migrations (staging)
        env:
          DATABASE_URL: ${{ secrets.STAGING_DATABASE_URL }}
        run: |
          cd backend
          alembic upgrade head

      - name: Verify migration success
        env:
          DATABASE_URL: ${{ secrets.STAGING_DATABASE_URL }}
        run: |
          python -c "
          import psycopg2
          conn = psycopg2.connect('${{ secrets.STAGING_DATABASE_URL }}')
          cur = conn.cursor()
          cur.execute('SELECT version_num FROM alembic_version')
          version = cur.fetchone()[0]
          print(f'✅ Staging database at version: {version}')
          "

  # ============================================================================
  # JOB 4: Deploy to Staging
  # ============================================================================
  deploy-staging:
    runs-on: ubuntu-latest
    needs: migrate-staging
    environment: staging
    timeout-minutes: 15

    steps:
      - name: Deploy to staging server via SSH
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.STAGING_HOST }}
          username: ${{ secrets.STAGING_USER }}
          key: ${{ secrets.STAGING_SSH_KEY }}
          script: |
            cd /opt/irstudy

            # Pull latest docker-compose configuration
            git pull origin main

            # Pull new Docker images
            docker-compose pull backend celery-worker celery-beat

            # Restart services with zero-downtime (rolling restart)
            docker-compose up -d --no-deps --scale backend=3 backend
            sleep 30  # Wait for health checks

            # Restart Celery workers
            docker-compose restart celery-worker celery-beat

            # Verify deployment
            curl -f http://localhost:8001/health || exit 1

            echo "✅ Staging deployment successful"

      - name: Smoke test staging API
        run: |
          sleep 10
          curl -f https://staging-api.irstudy.com/health
          curl -f https://staging-api.irstudy.com/metrics

  # ============================================================================
  # JOB 5: Production Approval Gate
  # ============================================================================
  approval-gate:
    runs-on: ubuntu-latest
    needs: deploy-staging
    environment: production-approval
    timeout-minutes: 1440  # 24 hours max wait

    steps:
      - name: Wait for manual approval
        run: |
          echo "⏳ Waiting for manual approval to deploy to production..."
          echo "Staging deployment successful: https://staging.irstudy.com"

  # ============================================================================
  # JOB 6: Deploy to Production
  # ============================================================================
  deploy-production:
    runs-on: ubuntu-latest
    needs: approval-gate
    environment: production
    timeout-minutes: 30

    steps:
      - name: Database Migration (Production)
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.PRODUCTION_HOST }}
          username: ${{ secrets.PRODUCTION_USER }}
          key: ${{ secrets.PRODUCTION_SSH_KEY }}
          script: |
            cd /opt/irstudy/backend

            # Backup database before migration
            docker exec irstudy-postgres pg_dump -U postgres irstudy_medical > \
                /backup/pre-migration-$(date +%Y%m%d-%H%M%S).sql

            # Run migrations
            alembic upgrade head

            echo "✅ Production database migrated"

      - name: Deploy to Production (Blue-Green)
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.PRODUCTION_HOST }}
          username: ${{ secrets.PRODUCTION_USER }}
          key: ${{ secrets.PRODUCTION_SSH_KEY }}
          script: |
            cd /opt/irstudy

            # Pull latest images
            docker-compose pull backend celery-worker celery-beat flower

            # Scale up new instances (green deployment)
            docker-compose up -d --no-deps --scale backend=6 backend

            # Wait for health checks (60s)
            sleep 60

            # Verify new instances are healthy
            for i in {4..6}; do
              docker exec irstudy-backend-$i curl -f http://localhost:8000/health || exit 1
            done

            # Traffic is now split 50/50 between old (3) and new (3) instances
            echo "✅ New instances deployed and healthy"

            # Monitor for 5 minutes
            echo "⏳ Monitoring new instances for 5 minutes..."
            sleep 300

            # Check error rate via Prometheus
            curl -s http://localhost:9090/api/v1/query?query='rate(http_requests_total{status=~"5.."}[5m])' | jq

            # If error rate is acceptable, scale down old instances
            docker-compose up -d --no-deps --scale backend=3 backend

            # Restart Celery workers
            docker-compose restart celery-worker celery-beat flower

            echo "✅ Production deployment complete (blue-green)"

      - name: Smoke test production API
        run: |
          sleep 15
          curl -f https://api.irstudy.com/health
          curl -f https://api.irstudy.com/metrics

      - name: Notify Slack
        uses: slackapi/slack-github-action@v1
        with:
          webhook-url: ${{ secrets.SLACK_WEBHOOK_URL }}
          payload: |
            {
              "text": "🚀 AI OSCE Production Deployment Successful",
              "blocks": [
                {
                  "type": "section",
                  "text": {
                    "type": "mrkdwn",
                    "text": "*AI OSCE Production Deployment*\n✅ Deployment successful\n*Commit:* ${{ github.sha }}\n*Author:* ${{ github.actor }}"
                  }
                }
              ]
            }

  # ============================================================================
  # JOB 7: Rollback (if production fails)
  # ============================================================================
  rollback-production:
    runs-on: ubuntu-latest
    needs: deploy-production
    if: failure()
    environment: production

    steps:
      - name: Emergency Rollback
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.PRODUCTION_HOST }}
          username: ${{ secrets.PRODUCTION_USER }}
          key: ${{ secrets.PRODUCTION_SSH_KEY }}
          script: |
            cd /opt/irstudy

            # Rollback Docker images to previous version
            docker-compose pull backend:previous-stable

            # Restart all backend services
            docker-compose up -d --force-recreate backend celery-worker

            # Rollback database migration (if needed)
            cd backend
            alembic downgrade -1

            echo "✅ Emergency rollback complete"

      - name: Notify Slack - Rollback
        uses: slackapi/slack-github-action@v1
        with:
          webhook-url: ${{ secrets.SLACK_WEBHOOK_URL }}
          payload: |
            {
              "text": "🚨 AI OSCE Production Rollback Executed",
              "blocks": [
                {
                  "type": "section",
                  "text": {
                    "type": "mrkdwn",
                    "text": "*AI OSCE Production Rollback*\n🚨 Deployment failed - rolled back to previous version\n*Commit:* ${{ github.sha }}\n*Investigation required*"
                  }
                }
              ]
            }
```

---

## 5. Cost Monitoring Dashboard

### Grafana Dashboard Configuration

**File:** `monitoring/grafana/dashboards/ai-osce-cost-monitoring.json`

```json
{
  "dashboard": {
    "title": "AI OSCE Cost Monitoring",
    "uid": "ai-osce-cost",
    "timezone": "browser",
    "refresh": "1m",
    "panels": [
      {
        "id": 1,
        "title": "Current Daily AI Spend",
        "type": "stat",
        "targets": [
          {
            "expr": "sum(increase(ai_cost_usd_total[24h]))",
            "legendFormat": "Daily Spend"
          }
        ],
        "thresholds": {
          "mode": "absolute",
          "steps": [
            {"value": 0, "color": "green"},
            {"value": 40, "color": "yellow"},
            {"value": 50, "color": "red"}
          ]
        },
        "options": {
          "displayMode": "lcd",
          "unit": "currencyUSD"
        },
        "gridPos": {"x": 0, "y": 0, "w": 6, "h": 4}
      },
      {
        "id": 2,
        "title": "Cost Per Session (Target: $0.045)",
        "type": "timeseries",
        "targets": [
          {
            "expr": "rate(ai_cost_usd_total[5m]) / rate(osce_sessions_completed_total[5m])",
            "legendFormat": "Cost Per Session"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "currencyUSD",
            "thresholds": {
              "steps": [
                {"value": 0, "color": "green"},
                {"value": 0.10, "color": "yellow"},
                {"value": 0.30, "color": "red"}
              ]
            }
          }
        },
        "gridPos": {"x": 6, "y": 0, "w": 12, "h": 4}
      },
      {
        "id": 3,
        "title": "Token Usage Breakdown",
        "type": "piechart",
        "targets": [
          {
            "expr": "sum by (direction) (increase(ai_tokens_used_total[1h]))",
            "legendFormat": "{{ direction }}"
          }
        ],
        "options": {
          "legend": {"displayMode": "table", "placement": "right"},
          "pieType": "donut"
        },
        "gridPos": {"x": 18, "y": 0, "w": 6, "h": 4}
      },
      {
        "id": 4,
        "title": "Hourly Cost Trend (Last 24h)",
        "type": "timeseries",
        "targets": [
          {
            "expr": "rate(ai_cost_usd_total[1h])",
            "legendFormat": "Hourly Cost"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "currencyUSD",
            "color": {"mode": "palette-classic"}
          }
        },
        "gridPos": {"x": 0, "y": 4, "w": 12, "h": 6}
      },
      {
        "id": 5,
        "title": "Cost by Model",
        "type": "table",
        "targets": [
          {
            "expr": "sum by (model) (increase(ai_cost_usd_total[24h]))",
            "format": "table",
            "instant": true
          }
        ],
        "transformations": [
          {
            "id": "organize",
            "options": {
              "renameByName": {"Value": "Cost (24h)", "model": "Model"}
            }
          }
        ],
        "gridPos": {"x": 12, "y": 4, "w": 6, "h": 6}
      },
      {
        "id": 6,
        "title": "Top 10 Highest Cost Sessions",
        "type": "table",
        "targets": [
          {
            "expr": "topk(10, max_over_time(ai_cost_usd_per_session[24h]))",
            "format": "table",
            "instant": true
          }
        ],
        "gridPos": {"x": 18, "y": 4, "w": 6, "h": 6}
      },
      {
        "id": 7,
        "title": "Monthly Projection",
        "type": "stat",
        "targets": [
          {
            "expr": "sum(increase(ai_cost_usd_total[24h])) * 30",
            "legendFormat": "Monthly Projection"
          }
        ],
        "thresholds": {
          "mode": "absolute",
          "steps": [
            {"value": 0, "color": "green"},
            {"value": 1200, "color": "yellow"},
            {"value": 1500, "color": "red"}
          ]
        },
        "options": {
          "unit": "currencyUSD",
          "displayMode": "gradient"
        },
        "gridPos": {"x": 0, "y": 10, "w": 8, "h": 3}
      },
      {
        "id": 8,
        "title": "Budget Remaining (Daily: $50)",
        "type": "gauge",
        "targets": [
          {
            "expr": "50 - sum(increase(ai_cost_usd_total[24h]))",
            "legendFormat": "Remaining Budget"
          }
        ],
        "options": {
          "unit": "currencyUSD",
          "min": 0,
          "max": 50,
          "thresholds": {
            "steps": [
              {"value": 0, "color": "red"},
              {"value": 10, "color": "yellow"},
              {"value": 20, "color": "green"}
            ]
          }
        },
        "gridPos": {"x": 8, "y": 10, "w": 8, "h": 3}
      },
      {
        "id": 9,
        "title": "Provider Distribution (Claude vs Kimi)",
        "type": "piechart",
        "targets": [
          {
            "expr": "sum by (model) (increase(ai_tokens_used_total[1h]))",
            "legendFormat": "{{ model }}"
          }
        ],
        "gridPos": {"x": 16, "y": 10, "w": 8, "h": 3}
      }
    ],
    "annotations": {
      "list": [
        {
          "name": "Deployments",
          "datasource": "Prometheus",
          "expr": "changes(process_start_time_seconds[1m]) > 0",
          "iconColor": "blue",
          "textFormat": "Deployment"
        },
        {
          "name": "Budget Alerts",
          "datasource": "Prometheus",
          "expr": "ALERTS{alertname=\"DailyAIBudgetExceeded\"}",
          "iconColor": "red",
          "textFormat": "Budget Exceeded"
        }
      ]
    }
  }
}
```

### Prometheus Alertmanager Configuration

**File:** `monitoring/alertmanager.yml`

```yaml
global:
  smtp_smarthost: 'smtp.gmail.com:587'
  smtp_from: 'alerts@irstudy.com'
  smtp_auth_username: 'alerts@irstudy.com'
  smtp_auth_password: '${SMTP_PASSWORD}'

route:
  group_by: ['alertname', 'severity']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 12h
  receiver: 'team-notifications'

  routes:
    - match:
        severity: critical
      receiver: 'pagerduty-critical'
      continue: true

    - match:
        severity: warning
      receiver: 'slack-warnings'
      continue: true

    - match:
        alertname: DailyAIBudgetExceeded
      receiver: 'cost-alerts'
      repeat_interval: 1h

receivers:
  - name: 'team-notifications'
    email_configs:
      - to: 'devops@irstudy.com'
        headers:
          Subject: '[AI OSCE] {{ .GroupLabels.alertname }}'

  - name: 'pagerduty-critical'
    pagerduty_configs:
      - service_key: '${PAGERDUTY_SERVICE_KEY}'
        description: '{{ .GroupLabels.alertname }}: {{ .CommonAnnotations.summary }}'

  - name: 'slack-warnings'
    slack_configs:
      - api_url: '${SLACK_WEBHOOK_URL}'
        channel: '#ai-osce-alerts'
        title: 'AI OSCE Warning: {{ .GroupLabels.alertname }}'
        text: '{{ .CommonAnnotations.description }}'
        color: 'warning'

  - name: 'cost-alerts'
    slack_configs:
      - api_url: '${SLACK_WEBHOOK_URL}'
        channel: '#ai-osce-cost-alerts'
        title: '💰 AI Cost Alert: Budget Exceeded'
        text: |
          Daily AI spend has exceeded $50 threshold.
          Current spend: ${{ .CommonAnnotations.value }}
          Action: Switched to free Kimi fallback
        color: 'danger'
    email_configs:
      - to: 'finance@irstudy.com,devops@irstudy.com'
        headers:
          Subject: '[URGENT] AI OSCE Daily Budget Exceeded'

inhibit_rules:
  - source_match:
      severity: 'critical'
    target_match:
      severity: 'warning'
    equal: ['alertname']
```

---

## Production Readiness Checklist

### Infrastructure
- [ ] All Docker secrets configured (`./secrets/*.txt` files created)
- [ ] PostgreSQL 16 deployed with hot standby replica
- [ ] Redis Sentinel configured for automatic failover
- [ ] Qdrant vector database indexed with 42,647 medical chunks
- [ ] Nginx load balancer configured with SSL termination
- [ ] Cloudflare CDN configured with DDoS protection

### Monitoring
- [ ] Prometheus scraping all services (15s interval)
- [ ] Grafana dashboards created (AI OSCE Overview, Cost Monitoring)
- [ ] Alertmanager configured with PagerDuty + Slack
- [ ] Sentry.io error tracking enabled
- [ ] Log aggregation (ELK stack or Datadog)

### Security
- [ ] All containers run as non-root users
- [ ] Docker secrets used (no hardcoded credentials)
- [ ] Rate limiting enabled (3 concurrent WebSocket per user)
- [ ] HTTPS enforced (TLS 1.3)
- [ ] Security scanning in CI/CD (Trivy, Bandit, Safety)

### Performance
- [ ] Load testing completed (100 concurrent sessions)
- [ ] AI response latency <3s at p95
- [ ] Redis replication lag <100ms
- [ ] Database connection pooling (max 20 connections per backend)

### Cost Control
- [ ] Daily AI budget alert ($50/day)
- [ ] Per-session token cap (30,000 tokens)
- [ ] Per-user daily limit (10 OSCE sessions)
- [ ] Prompt caching enabled (40% savings)
- [ ] Circuit breaker to free Kimi fallback configured

### Disaster Recovery
- [ ] PostgreSQL daily backups (pg_dump to S3)
- [ ] Redis AOF persistence enabled
- [ ] Database migration rollback tested
- [ ] Incident runbooks documented (3 critical scenarios)
- [ ] RTO: 15 minutes, RPO: 30 seconds

### Documentation
- [ ] Operations runbooks complete (3 critical incidents)
- [ ] CI/CD pipeline documented
- [ ] Cost monitoring dashboard configured
- [ ] On-call rotation established
- [ ] Post-incident review template created

---

## Next Steps

1. **Immediate (Week 1):**
   - Deploy monitoring stack (Prometheus + Grafana)
   - Create Docker secrets for all services
   - Set up CI/CD pipeline in GitHub Actions
   - Configure cost alerts (Slack + Email)

2. **Short-term (Week 2-3):**
   - Load testing with 100 concurrent sessions
   - Optimize Qdrant vector search performance
   - Enable Redis Sentinel for automatic failover
   - Create incident response runbooks

3. **Medium-term (Month 1-2):**
   - Implement auto-scaling for backend services
   - Set up database read replicas for load distribution
   - Create comprehensive backup/restore procedures
   - Conduct disaster recovery drills

4. **Long-term (Month 3+):**
   - Multi-region deployment for global latency reduction
   - AI cost optimization (prompt engineering, model selection)
   - Advanced monitoring (APM, distributed tracing)
   - Capacity planning for 1000+ concurrent users

---

**Document Version:** 1.0
**Last Updated:** 2026-02-09
**Review Cycle:** Monthly (or after major incidents)
**Owner:** DevOps Team
**Approved By:** [Pending Technical Lead Approval]

---

**END OF OPERATIONS REVIEW**
