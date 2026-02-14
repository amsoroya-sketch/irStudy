# Week 2 Operations Guide - WebSocket Authentication

**Version**: 1.0  
**Last Updated**: 2026-02-07  
**Project**: AMC Clinical Exam Simulation v2.0  
**Sprint**: Week 2 - Enhanced WebSocket Authentication

---

## Overview

This operations guide provides day-to-day procedures for maintaining and operating the Week 2 WebSocket authentication system. Use this guide for routine tasks, monitoring, and maintenance procedures.

### Operational Responsibilities

**Security Operations Team**:
- Monitor security events and alerts
- Investigate authentication failures
- Respond to security incidents
- Manage rate limits and connection tracking

**DevOps/SRE Team**:
- Monitor system health and performance
- Scale infrastructure as needed
- Manage backups and disaster recovery
- Deploy updates and patches

**On-Call Engineer**:
- Respond to alerts 24/7
- Perform emergency procedures
- Escalate critical issues

---

## Daily Operations

### Morning Checklist (Start of Day)

**Duration**: 15 minutes  
**Frequency**: Every business day at 9:00 AM

**Tasks**:

- [ ] **1. Check System Health**
  ```bash
  # Application health
  curl https://api.example.com/health
  
  # Expected: {"status": "healthy", ...}
  ```

- [ ] **2. Review Overnight Alerts**
  ```bash
  # Check Grafana alerts dashboard
  open https://grafana.example.com/alerts
  
  # Expected: No critical alerts
  ```

- [ ] **3. Monitor Authentication Metrics**
  ```promql
  # Check authentication success rate (should be >99%)
  rate(security_events_total{event_type="ws_auth_success"}[24h])
    /
  rate(security_events_total{event_type=~"ws_auth_.*"}[24h])
  
  # Expected: >0.99 (99%+)
  ```

- [ ] **4. Review Security Events**
  ```bash
  # Get yesterday's security events
  YESTERDAY=$(date -d "yesterday" +%Y-%m-%d)
  vault kv get -format=json audit/security_events/$YESTERDAY | \
    jq '.data.data | {count, high_severity: [.events[] | select(.severity=="high")] | length}'
  
  # Expected: Few or no high-severity events
  ```

- [ ] **5. Check Connection Pool Health**
  ```bash
  # Active WebSocket connections
  redis-cli -h redis-cluster -p 7379 KEYS "ws:connections:*" | wc -l
  
  # Expected: <500 (normal load)
  ```

- [ ] **6. Verify Backup Success**
  ```bash
  # Check last Redis backup
  ls -lh /backups/redis/ | tail -1
  
  # Expected: Backup from last night present
  
  # Check last Vault backup
  vault operator raft snapshot save /tmp/vault-snapshot.snap
  ls -lh /tmp/vault-snapshot.snap
  
  # Expected: Recent snapshot saved successfully
  ```

- [ ] **7. Document Issues**
  - Log any issues found in operations log
  - Create tickets for non-urgent issues
  - Escalate critical issues immediately

---

### Evening Checklist (End of Day)

**Duration**: 10 minutes  
**Frequency**: Every business day at 5:00 PM

**Tasks**:

- [ ] **1. Review Day's Activity**
  ```promql
  # Total authentication attempts today
  increase(security_events_total{event_type=~"ws_auth_.*"}[24h])
  ```

- [ ] **2. Check for Anomalies**
  ```bash
  # Failed authentication attempts (should be <100/day)
  vault kv get -format=json audit/security_events/$(date +%Y-%m-%d) | \
    jq '[.data.data.events[] | select(.event_type=="ws_auth_failed")] | length'
  ```

- [ ] **3. Verify Vault Flush Working**
  ```promql
  # Vault flush errors (should be 0)
  increase(security_events_vault_errors_total[24h])
  ```

- [ ] **4. Update Operations Log**
  ```bash
  echo "$(date): Daily operations completed. Status: OK" >> /var/log/operations.log
  ```

---

## Weekly Operations

### Monday: System Review

**Duration**: 1 hour  
**Frequency**: Every Monday at 10:00 AM

**Tasks**:

1. **Review Last Week's Metrics**
   ```promql
   # Authentication success rate (last 7 days)
   rate(security_events_total{event_type="ws_auth_success"}[7d])
     /
   rate(security_events_total{event_type=~"ws_auth_.*"}[7d])
   
   # P95 latency (last 7 days)
   histogram_quantile(0.95, 
     rate(security_events_flush_latency_ms_bucket[7d]))
   ```

2. **Analyze Security Events**
   ```bash
   # Get last week's events
   for day in {1..7}; do
     DATE=$(date -d "$day days ago" +%Y-%m-%d)
     vault kv get -format=json audit/security_events/$DATE | \
       jq -r '.data.data | "\(.count) events on '$DATE'"'
   done
   ```

3. **Review Rate Limit Effectiveness**
   ```bash
   # Rate limit rejections last week
   vault kv get -format=json audit/security_events/$(date -d "7 days ago" +%Y-%m-%d) | \
     jq '[.data.data.events[] | select(.event_type=="ws_rate_limit_exceeded")] | length'
   ```

4. **Check for Performance Degradation**
   ```promql
   # Compare current week vs previous week
   # P95 latency change
   histogram_quantile(0.95, rate(security_events_flush_latency_ms_bucket[7d]))
     -
   histogram_quantile(0.95, rate(security_events_flush_latency_ms_bucket[7d] offset 7d))
   ```

5. **Document Findings**
   - Create weekly operations report
   - Share with team in Slack/email
   - Create improvement tickets if needed

---

### Wednesday: Capacity Planning

**Duration**: 30 minutes  
**Frequency**: Every Wednesday at 2:00 PM

**Tasks**:

1. **Check Redis Memory Usage**
   ```bash
   redis-cli -h redis-cluster -p 7379 INFO memory | grep used_memory_human
   
   # Alert if >80% of maxmemory (4GB)
   ```

2. **Check Vault Storage**
   ```bash
   du -sh /vault/data
   
   # Alert if >80% of allocated storage
   ```

3. **Check Database Size**
   ```sql
   SELECT pg_size_pretty(pg_database_size('amc_simulation'));
   ```

4. **Check Connection Pool Utilization**
   ```python
   # Query via API or database
   SELECT COUNT(*) as active_connections 
   FROM pg_stat_activity 
   WHERE datname = 'amc_simulation';
   
   # Alert if >80% of pool size (20 connections)
   ```

5. **Forecast Capacity Needs**
   - Trend analysis (growth rate)
   - Estimate when scaling needed
   - Plan infrastructure upgrades

---

### Friday: Security Review

**Duration**: 1 hour  
**Frequency**: Every Friday at 3:00 PM

**Tasks**:

1. **Review High-Severity Security Events**
   ```bash
   # Get all high-severity events this week
   for day in {0..6}; do
     DATE=$(date -d "$day days ago" +%Y-%m-%d)
     vault kv get -format=json audit/security_events/$DATE | \
       jq -r '.data.data.events[] | select(.severity=="high" or .severity=="critical")'
   done
   ```

2. **Check for Suspicious Patterns**
   - Multiple failed auth attempts from same IP
   - Fingerprint mismatches
   - Unusual connection patterns
   - Rate limit abuse

3. **Verify Security Controls**
   ```bash
   # Test rate limiting still working
   for i in {1..11}; do
     curl -X POST https://api.example.com/ws &
   done
   # Expected: 11th request gets 429
   
   # Test connection tracking
   # (Manual test: Open 4 WebSocket connections, 4th should be rejected)
   ```

4. **Review Access Logs**
   ```bash
   # Check for unauthorized access attempts
   grep "401\|403" /var/log/nginx/access.log | tail -50
   ```

5. **Update Security Documentation**
   - Document new threats discovered
   - Update incident response procedures
   - Share security tips with team

---

## Monthly Operations

### First Monday: Compliance Audit

**Duration**: 2-3 hours  
**Frequency**: First Monday of each month

**Tasks**:

1. **HIPAA Compliance Review**
   - [ ] Audit logs present and complete (Vault)
   - [ ] Access controls functioning (authentication tests)
   - [ ] Data integrity verified (Vault KV v2 versioning)
   - [ ] PHI protection confirmed (PII anonymization)

2. **Security Event Audit**
   ```bash
   # Export last month's security events
   YEAR=$(date +%Y)
   MONTH=$(date +%m)
   
   for day in {01..31}; do
     vault kv get -format=json audit/security_events/$YEAR-$MONTH-$day \
       2>/dev/null >> audit_$YEAR-$MONTH.json
   done
   
   # Analyze:
   jq -s '[.[].data.data.events[]] | group_by(.event_type) | map({event: .[0].event_type, count: length})' \
     audit_$YEAR-$MONTH.json
   ```

3. **Generate Compliance Report**
   - Total authentication attempts
   - Failed authentication rate
   - Security incidents responded to
   - Uptime/availability metrics
   - Backup verification

4. **Review and Update Policies**
   - Update security runbook if needed
   - Review and update rate limits
   - Adjust monitoring thresholds

5. **Certification**
   - Sign off on compliance report
   - Submit to compliance officer
   - Archive report

---

### Second Monday: Performance Review

**Duration**: 2 hours  
**Frequency**: Second Monday of each month

**Tasks**:

1. **Analyze Last Month's Performance**
   ```promql
   # P50, P95, P99 latency trends (last 30 days)
   histogram_quantile(0.50, rate(security_events_flush_latency_ms_bucket[30d]))
   histogram_quantile(0.95, rate(security_events_flush_latency_ms_bucket[30d]))
   histogram_quantile(0.99, rate(security_events_flush_latency_ms_bucket[30d]))
   ```

2. **Identify Bottlenecks**
   - Slow database queries
   - Redis latency spikes
   - Network issues
   - CPU/memory constraints

3. **Optimization Opportunities**
   - Query optimization
   - Cache tuning
   - Connection pool sizing
   - Resource allocation

4. **Capacity Planning Update**
   - Current utilization vs capacity
   - Growth trends
   - Scaling timeline
   - Budget estimate

5. **Performance Improvement Plan**
   - Create tickets for optimizations
   - Prioritize improvements
   - Schedule implementation

---

### Third Monday: Disaster Recovery Drill

**Duration**: 1 hour  
**Frequency**: Third Monday of each month

**Tasks**:

1. **Backup Verification**
   ```bash
   # Test Redis backup restore
   redis-cli -h redis-test -p 7379 FLUSHDB
   redis-cli -h redis-test -p 7379 --rdb /backups/redis/dump-latest.rdb
   redis-cli -h redis-test -p 7379 DBSIZE
   # Expected: Same number of keys as production
   
   # Test Vault backup restore
   vault operator raft snapshot restore /backups/vault/vault-snapshot-latest.snap
   ```

2. **Failover Test**
   ```bash
   # Redis failover (manual trigger)
   redis-cli -h redis-primary -p 7379 DEBUG SLEEP 30
   # Verify: Replica promoted to primary automatically
   
   # Database failover (if using replication)
   # Promote read replica to primary (test in staging)
   ```

3. **Recovery Time Objective (RTO) Measurement**
   - Time to detect failure: <5 minutes
   - Time to restore from backup: <30 minutes
   - Time to full service restoration: <1 hour

4. **Document Lessons Learned**
   - What went well
   - What could be improved
   - Update DR procedures

---

## Scaling Procedures

### Scale Up Redis (Add Memory)

**Scenario**: Redis memory usage >80%

**Procedure**:
```bash
# 1. Check current memory
redis-cli -h redis-cluster -p 7379 INFO memory | grep used_memory_human

# 2. Update Redis configuration
# Edit redis.conf:
# maxmemory 8gb  (increase from 4gb)

# 3. Apply configuration (no downtime)
redis-cli -h redis-1 -p 7379 CONFIG SET maxmemory 8gb
redis-cli -h redis-2 -p 7379 CONFIG SET maxmemory 8gb
redis-cli -h redis-3 -p 7379 CONFIG SET maxmemory 8gb

# 4. Verify
redis-cli -h redis-cluster -p 7379 CONFIG GET maxmemory

# 5. Update monitoring thresholds (80% of 8GB = 6.4GB)
```

---

### Scale Out Backend (Add Instances)

**Scenario**: CPU usage >80% or latency increasing

**Kubernetes**:
```bash
# 1. Increase replicas
kubectl scale deployment/amc-backend --replicas=5 -n amc-simulation

# 2. Verify
kubectl get pods -n amc-simulation

# 3. Monitor load distribution
kubectl top pods -n amc-simulation

# 4. Update HPA (Horizontal Pod Autoscaler)
kubectl autoscale deployment/amc-backend \
  --min=3 --max=10 --cpu-percent=70 \
  -n amc-simulation
```

**Docker Swarm**:
```bash
docker service scale amc-backend=5
docker service ps amc-backend
```

---

### Scale Rate Limits (Increase Limits)

**Scenario**: Many legitimate users hitting rate limits

**Procedure**:
```python
# 1. Edit rate limiter configuration
# backend/src/websocket/rate_limiter.py

class RateLimiter:
    def __init__(
        self,
        redis_client: redis.Redis,
        max_connections: int = 20,  # Increased from 10
        window_seconds: int = 60
    ):

# 2. Deploy updated code
kubectl set image deployment/amc-backend \
  backend=amc-simulation/backend:new-rate-limits \
  -n amc-simulation

# 3. Verify
# Test with load test: bash run_load_tests.sh

# 4. Monitor impact
# Check rate_limit_exceeded events decrease
```

---

## Backup and Recovery

### Daily Backup Procedures

**Redis Backup** (automated cron job):
```bash
#!/bin/bash
# /etc/cron.daily/redis-backup.sh

DATE=$(date +%Y-%m-%d-%H%M)
BACKUP_DIR=/backups/redis
S3_BUCKET=s3://backups-amc/redis

# Trigger background save
redis-cli -h redis-1 -p 7379 BGSAVE

# Wait for save to complete
while [ $(redis-cli -h redis-1 -p 7379 LASTSAVE) -eq $(redis-cli -h redis-1 -p 7379 LASTSAVE) ]; do
  sleep 5
done

# Copy RDB file
cp /var/lib/redis/dump.rdb $BACKUP_DIR/dump-$DATE.rdb

# Upload to S3
aws s3 cp $BACKUP_DIR/dump-$DATE.rdb $S3_BUCKET/

# Clean old backups (keep 30 days)
find $BACKUP_DIR -name "dump-*.rdb" -mtime +30 -delete

# Log success
echo "$(date): Redis backup completed: dump-$DATE.rdb" >> /var/log/backup.log
```

**Vault Backup** (automated cron job):
```bash
#!/bin/bash
# /etc/cron.daily/vault-backup.sh

DATE=$(date +%Y-%m-%d-%H%M)
BACKUP_DIR=/backups/vault
S3_BUCKET=s3://backups-amc/vault

# Create snapshot
vault operator raft snapshot save $BACKUP_DIR/vault-$DATE.snap

# Upload to S3
aws s3 cp $BACKUP_DIR/vault-$DATE.snap $S3_BUCKET/

# Clean old backups (keep 90 days for compliance)
find $BACKUP_DIR -name "vault-*.snap" -mtime +90 -delete

# Log success
echo "$(date): Vault backup completed: vault-$DATE.snap" >> /var/log/backup.log
```

**Database Backup** (PostgreSQL automated):
```bash
#!/bin/bash
# /etc/cron.daily/postgres-backup.sh

DATE=$(date +%Y-%m-%d-%H%M)
BACKUP_DIR=/backups/postgres
S3_BUCKET=s3://backups-amc/postgres

# Create backup
pg_dump -h postgres -U amc_user -d amc_simulation -F c -f $BACKUP_DIR/amc-$DATE.dump

# Upload to S3
aws s3 cp $BACKUP_DIR/amc-$DATE.dump $S3_BUCKET/

# Clean old backups (keep 30 days)
find $BACKUP_DIR -name "amc-*.dump" -mtime +30 -delete

# Log success
echo "$(date): PostgreSQL backup completed: amc-$DATE.dump" >> /var/log/backup.log
```

---

### Recovery Procedures

**Redis Recovery**:
```bash
# 1. Stop Redis
systemctl stop redis

# 2. Replace RDB file
cp /backups/redis/dump-2026-02-07.rdb /var/lib/redis/dump.rdb
chown redis:redis /var/lib/redis/dump.rdb

# 3. Start Redis
systemctl start redis

# 4. Verify data
redis-cli -p 7379 DBSIZE
redis-cli -p 7379 KEYS "session:*" | wc -l

# 5. Monitor
tail -f /var/log/redis/redis.log
```

**Vault Recovery**:
```bash
# 1. Stop Vault (all nodes)
systemctl stop vault

# 2. Restore snapshot (on primary node)
vault operator raft snapshot restore /backups/vault/vault-2026-02-07.snap

# 3. Start Vault
systemctl start vault

# 4. Unseal Vault
vault operator unseal <key-1>
vault operator unseal <key-2>
vault operator unseal <key-3>

# 5. Verify data
vault kv list amc-simulation
vault kv get amc-simulation/api-keys

# 6. Monitor
tail -f /var/log/vault/vault.log
```

**Database Recovery**:
```bash
# 1. Stop application (prevent writes)
kubectl scale deployment/amc-backend --replicas=0 -n amc-simulation

# 2. Drop and recreate database
psql -h postgres -U postgres -c "DROP DATABASE amc_simulation;"
psql -h postgres -U postgres -c "CREATE DATABASE amc_simulation OWNER amc_user;"

# 3. Restore backup
pg_restore -h postgres -U amc_user -d amc_simulation /backups/postgres/amc-2026-02-07.dump

# 4. Verify data
psql -h postgres -U amc_user -d amc_simulation -c "SELECT COUNT(*) FROM users;"

# 5. Restart application
kubectl scale deployment/amc-backend --replicas=3 -n amc-simulation

# 6. Monitor
kubectl logs -f deployment/amc-backend -n amc-simulation
```

---

## Performance Monitoring

### Key Performance Indicators (KPIs)

**Availability**:
- Target: 99.9% uptime
- Measurement: `(total_time - downtime) / total_time`

**Authentication Latency**:
- Target: P95 <50ms
- Query: `histogram_quantile(0.95, rate(security_events_flush_latency_ms_bucket[5m]))`

**Success Rate**:
- Target: >99%
- Query: `rate(security_events_total{event_type="ws_auth_success"}[5m]) / rate(security_events_total{event_type=~"ws_auth_.*"}[5m])`

**Error Rate**:
- Target: <1%
- Query: `rate(security_events_total{event_type="ws_auth_failed"}[5m]) / rate(security_events_total{event_type=~"ws_auth_.*"}[5m])`

---

### Latency Dashboards

**Grafana Query Examples**:

```promql
# P50, P95, P99 latency
histogram_quantile(0.50, rate(security_events_flush_latency_ms_bucket[5m]))
histogram_quantile(0.95, rate(security_events_flush_latency_ms_bucket[5m]))
histogram_quantile(0.99, rate(security_events_flush_latency_ms_bucket[5m]))

# Average latency
rate(security_events_flush_latency_ms_sum[5m]) / rate(security_events_flush_latency_ms_count[5m])

# Latency by instance (multi-instance)
histogram_quantile(0.95, 
  rate(security_events_flush_latency_ms_bucket[5m])) by (instance)
```

---

## Cost Optimization

### Redis Memory Optimization

**Current Usage**:
```bash
redis-cli -h redis-cluster -p 7379 INFO memory | grep used_memory_human
```

**Optimization Techniques**:

1. **Eviction Policy**: Already set to `allkeys-lru`
2. **Key Expiration**: Set TTL on temporary keys
   ```bash
   # Rate limit keys expire after 60 seconds
   redis-cli -h redis-cluster -p 7379 TTL "ws:ratelimit:user-12345678"
   ```
3. **Data Compression**: Use Redis serialization for large values

**Cost Reduction**:
- 4GB Redis: ~$50/month
- Optimized to 2GB: ~$25/month (50% savings)

---

### Vault Storage Optimization

**Current Usage**:
```bash
du -sh /vault/data
```

**Optimization Techniques**:

1. **Audit Log Retention**: Archive old logs to S3
   ```bash
   # Move logs >90 days old to cold storage
   find /vault/data/audit -name "*.json" -mtime +90 -exec aws s3 cp {} s3://archives/vault/ \; -delete
   ```

2. **KV Versioning**: Limit versions (currently unlimited)
   ```bash
   vault kv metadata put -max-versions=10 amc-simulation/api-keys
   ```

**Cost Reduction**:
- 100GB Vault: ~$100/month
- Optimized to 50GB: ~$50/month (50% savings)

---

## Alerts and Notifications

### Alert Definitions

**Critical Alerts** (page on-call engineer):

| Alert | Threshold | Action |
|-------|-----------|--------|
| High auth failure rate | >10 failures/sec for 5 min | Investigate immediately |
| Fingerprint mismatch | Any occurrence | Security investigation |
| Vault flush failures | >0.1 errors/sec for 5 min | Check Vault health |
| Redis down | Down for 1 min | Failover to replica |
| Database down | Down for 1 min | Failover to replica |

**Warning Alerts** (notify team Slack channel):

| Alert | Threshold | Action |
|-------|-----------|--------|
| High rate limit rejections | >5/sec for 10 min | Review rate limits |
| Slow Vault flush | P95 >1000ms for 10 min | Optimize Vault |
| Memory usage high | >80% for 15 min | Plan scaling |
| Disk space low | <20% free | Clean old data |

---

### Escalation Procedures

**Level 1: Warning Alert**
1. Notify team in Slack #ops channel
2. On-call engineer reviews (no immediate action required)
3. Create ticket if recurring

**Level 2: Critical Alert**
1. Page on-call engineer immediately
2. On-call investigates and mitigates
3. Escalate to senior engineer if needed
4. Post-mortem required

**Level 3: Outage**
1. Page entire on-call rotation
2. Activate incident response plan
3. Create war room (Zoom/Slack)
4. Executive notification
5. Post-incident review required

---

## Common Tasks

### Add User to Whitelist (Bypass Rate Limit)

**Scenario**: VIP user needs higher rate limit

**Procedure**:
```bash
# 1. Clear current rate limit
redis-cli -h redis-cluster -p 7379 DEL "ws:ratelimit:user-12345678"

# 2. Add to whitelist (code change required)
# Edit backend/src/websocket/rate_limiter.py
WHITELISTED_USERS = ["user-12345678", "user-87654321"]

# 3. Deploy updated code
kubectl set image deployment/amc-backend backend=amc-simulation/backend:latest -n amc-simulation

# 4. Verify
# User should no longer be rate limited
```

---

### Reset Rate Limit for User

**Scenario**: User legitimately hit rate limit, needs reset

**Procedure**:
```bash
# Clear rate limit
redis-cli -h redis-cluster -p 7379 DEL "ws:ratelimit:user-12345678"

# Verify
redis-cli -h redis-cluster -p 7379 EXISTS "ws:ratelimit:user-12345678"
# Expected: 0 (key deleted)

# Notify user
echo "Rate limit reset for user-12345678 at $(date)" >> /var/log/operations.log
```

---

### Force Disconnect User

**Scenario**: User account compromised, need to disconnect all sessions

**Procedure**:
```bash
# 1. Disconnect all WebSocket connections
redis-cli -h redis-cluster -p 7379 DEL "ws:connections:user-12345678"

# 2. Invalidate session
redis-cli -h redis-cluster -p 7379 DEL "session:user-12345678"

# 3. Log security event
vault kv put audit/manual_disconnect/user-12345678 \
  timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ") \
  reason="account_compromised" \
  operator=$(whoami)

# 4. Notify security team
echo "SECURITY: Forcibly disconnected user-12345678 at $(date)" | \
  mail -s "Security Event" security@example.com
```

---

## Conclusion

This operations guide provides comprehensive procedures for maintaining Week 2 WebSocket authentication system. For additional information, see:

- **Security Runbook**: `WEEK2_SECURITY_RUNBOOK.md`
- **API Documentation**: `WEEK2_API_DOCUMENTATION.md`
- **Deployment Guide**: `WEEK2_DEPLOYMENT_GUIDE.md`

**For Operational Support**: Contact operations team at `ops@example.com`

---

**Revision History**:

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2026-02-07 | Initial release | Operations Team |

---

**Status**: ✅ OPERATIONAL
