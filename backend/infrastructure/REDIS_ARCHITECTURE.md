# Redis Architecture
## irStudy Platform - EMR Practice + AI OSCE Simulation

**Date**: 2026-02-16
**Version**: 1.0
**Purpose**: Redis configuration, namespace strategy, and operational procedures
**Status**: Ready for Deployment

---

## 📋 OVERVIEW

Redis serves as the **in-memory data store** for the irStudy platform, supporting:
- **EMR System**: Dashboard caching, rate limiting, auto-save buffering
- **AI OSCE System**: Active session state, real-time transcripts, emotional state tracking

**Total Allocation**: 2.5 GB (512 MB EMR + 2 GB OSCE)

---

## 🗂️ NAMESPACE STRATEGY

### EMR Namespaces (512 MB)

| Namespace | Purpose | TTL | Eviction | Size Est. |
|-----------|---------|-----|----------|-----------|
| `emr:dashboard:user:{user_id}` | Cached analytics (sessions, scores, trends) | 5 min | Allowed | ~50 KB/user |
| `emr:ratelimit:{ip_address}` | API rate limiting counters | 1 min | Allowed | ~1 KB/IP |
| `emr:session:{session_id}:autosave` | Auto-save buffer for SOAP notes | 1 hour | Allowed | ~10 KB/session |
| `emr:template:cache:{template_id}` | Cached SOAP templates | 24 hours | Allowed | ~5 KB/template |
| `emr:validation:queue:{user_id}` | Claude API validation queue (FIFO) | None | Not allowed | ~20 KB/user |

**Estimated Usage**:
- 1000 active users × 50 KB dashboard = 50 MB
- 100 concurrent sessions × 10 KB autosave = 1 MB
- 500 templates × 5 KB = 2.5 MB
- 200 validation queues × 20 KB = 4 MB
- **Total**: ~60 MB active + 450 MB buffer

### AI OSCE Namespaces (2 GB)

| Namespace | Purpose | TTL | Eviction | Size Est. |
|-----------|---------|-----|----------|-----------|
| `osce:session:{session_id}:state` | Active session state (user, persona, timer) | None* | NOT allowed | ~5 KB/session |
| `osce:session:{session_id}:transcript` | Real-time conversation transcript | None* | NOT allowed | ~100 KB/session |
| `osce:session:{session_id}:emotional` | Emotional state machine (6 states) | None* | NOT allowed | ~2 KB/session |
| `osce:session:{session_id}:timer` | 8-minute countdown timer | 480s | Allowed | ~500 bytes/session |
| `osce:ratelimit:claude:{user_id}` | Claude API rate limiting | 1 min | Allowed | ~1 KB/user |
| `osce:persona:cache:{persona_id}` | Cached patient personas | 1 hour | Allowed | ~50 KB/persona |

**\*TTL is None until session completes** (8 min max), then deleted or moved to PostgreSQL.

**Estimated Usage**:
- 100 concurrent sessions × 107 KB (state + transcript + emotional) = 10.7 MB
- 360 cached personas × 50 KB = 18 MB
- 1000 users × 1 KB rate limit = 1 MB
- **Total**: ~30 MB active + 1.97 GB buffer for peak load (1000 concurrent sessions)

### Shared Namespaces

| Namespace | Purpose | TTL | Size Est. |
|-----------|---------|-----|----------|
| `shared:ratelimit:global:claude` | Global Claude API rate limit (90 req/min) | 1 min | 10 KB |
| `shared:session:{session_id}:lock` | Distributed locks for concurrency | 30s | 1 KB/lock |

---

## ⚙️ REDIS CONFIGURATION

### redis.conf

```conf
# ==============================================================================
# MEMORY CONFIGURATION
# ==============================================================================

# Total memory allocation
maxmemory 2560mb                       # 2.5 GB (512 MB EMR + 2 GB OSCE)

# Eviction policy
maxmemory-policy allkeys-lru           # Evict least recently used keys

# Sample size for LRU algorithm
maxmemory-samples 5                    # Default, good balance

# ==============================================================================
# PERSISTENCE
# ==============================================================================

# RDB Snapshots (for disaster recovery)
save 900 1                             # Save after 15 min if ≥1 key changed
save 300 10                            # Save after 5 min if ≥10 keys changed
save 60 10000                          # Save after 1 min if ≥10,000 keys changed

stop-writes-on-bgsave-error yes        # Stop writes if snapshot fails
rdbcompression yes                     # Compress RDB files
rdbchecksum yes                        # Checksum for corruption detection
dbfilename dump.rdb
dir /var/lib/redis

# AOF (Append-Only File) for session safety
appendonly yes
appendfilename "appendonly.aof"
appendfsync everysec                   # Sync to disk every second (balance)
no-appendfsync-on-rewrite no           # Don't skip fsync during rewrite
auto-aof-rewrite-percentage 100        # Rewrite when 2x original size
auto-aof-rewrite-min-size 64mb         # Minimum size before rewrite

# ==============================================================================
# NETWORKING
# ==============================================================================

bind 0.0.0.0                           # Listen on all interfaces (Docker)
port 6380                              # Custom port (avoid conflict with other Redis)
protected-mode no                      # Disable (using password auth)
requirepass VAULT_MANAGED              # Read from Vault: secret/ai-osce/redis-password

# Connection limits
maxclients 10000                       # Max concurrent connections
timeout 0                              # Keep connections alive (no timeout)
tcp-keepalive 300                      # TCP keepalive (5 min)

# ==============================================================================
# LOGGING
# ==============================================================================

loglevel notice                        # Production: notice, Debug: verbose
logfile /var/log/redis/redis-server.log
syslog-enabled no

# ==============================================================================
# PERFORMANCE TUNING
# ==============================================================================

# Disable slow operations in production
slowlog-log-slower-than 10000          # Log queries slower than 10ms
slowlog-max-len 128                    # Keep last 128 slow queries

# ==============================================================================
# SECURITY
# ==============================================================================

# Disable dangerous commands in production
rename-command FLUSHDB ""
rename-command FLUSHALL ""
rename-command CONFIG ""
rename-command SHUTDOWN SHUTDOWN_VAULT_MANAGED  # Rename, require password

# ==============================================================================
# ADVANCED CONFIG
# ==============================================================================

# Hash optimization (small hashes use less memory)
hash-max-ziplist-entries 512
hash-max-ziplist-value 64

# List optimization
list-max-ziplist-size -2

# Set optimization
set-max-intset-entries 512

# Sorted set optimization
zset-max-ziplist-entries 128
zset-max-ziplist-value 64
```

---

## 🐳 DOCKER DEPLOYMENT

### Docker Compose

```yaml
# docker-compose.yml (irstudy-redis service)
services:
  irstudy-redis:
    image: redis:7.2-alpine
    container_name: irstudy-redis
    restart: unless-stopped
    ports:
      - "6380:6379"
    volumes:
      - ./backend/infrastructure/redis.conf:/usr/local/etc/redis/redis.conf
      - irstudy-redis-data:/data
      - irstudy-redis-logs:/var/log/redis
    command: redis-server /usr/local/etc/redis/redis.conf
    healthcheck:
      test: ["CMD", "redis-cli", "-p", "6379", "ping"]
      interval: 10s
      timeout: 3s
      retries: 3
      start_period: 10s
    networks:
      - irstudy-network
    environment:
      - TZ=Australia/Sydney

volumes:
  irstudy-redis-data:
    driver: local
  irstudy-redis-logs:
    driver: local

networks:
  irstudy-network:
    driver: bridge
```

### Kubernetes Deployment (Production)

```yaml
# k8s/redis-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: irstudy-redis
  namespace: irstudy
spec:
  replicas: 1                          # Single instance (no clustering for now)
  selector:
    matchLabels:
      app: irstudy-redis
  template:
    metadata:
      labels:
        app: irstudy-redis
    spec:
      containers:
      - name: redis
        image: redis:7.2-alpine
        ports:
        - containerPort: 6379
        resources:
          requests:
            memory: "3Gi"              # 2.5 GB + 500 MB overhead
            cpu: "500m"
          limits:
            memory: "4Gi"
            cpu: "1000m"
        volumeMounts:
        - name: redis-config
          mountPath: /usr/local/etc/redis
        - name: redis-data
          mountPath: /data
        livenessProbe:
          exec:
            command:
            - redis-cli
            - ping
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          exec:
            command:
            - redis-cli
            - ping
          initialDelaySeconds: 5
          periodSeconds: 5
      volumes:
      - name: redis-config
        configMap:
          name: redis-config
      - name: redis-data
        persistentVolumeClaim:
          claimName: redis-data-pvc

---
apiVersion: v1
kind: Service
metadata:
  name: irstudy-redis
  namespace: irstudy
spec:
  selector:
    app: irstudy-redis
  ports:
  - port: 6379
    targetPort: 6379
  type: ClusterIP
```

---

## 📊 MONITORING & ALERTING

### Key Metrics to Monitor

```python
# backend/src/core/redis_monitor.py
import redis
from prometheus_client import Gauge

# Memory metrics
redis_memory_used = Gauge('redis_memory_used_bytes', 'Redis memory used', ['namespace'])
redis_memory_peak = Gauge('redis_memory_peak_bytes', 'Redis peak memory')
redis_memory_fragmentation = Gauge('redis_memory_fragmentation_ratio', 'Memory fragmentation')

# Key metrics
redis_keys_total = Gauge('redis_keys_total', 'Total keys', ['namespace'])
redis_keys_expired = Gauge('redis_keys_expired_total', 'Expired keys')

# Performance metrics
redis_ops_per_sec = Gauge('redis_ops_per_sec', 'Operations per second')
redis_hit_rate = Gauge('redis_hit_rate', 'Cache hit rate percentage')

# Connection metrics
redis_connected_clients = Gauge('redis_connected_clients', 'Connected clients')
redis_blocked_clients = Gauge('redis_blocked_clients', 'Blocked clients')

def update_redis_metrics(redis_client: redis.Redis):
    """Update Prometheus metrics from Redis INFO"""
    info = redis_client.info()

    # Memory
    redis_memory_used.labels(namespace='total').set(info['used_memory'])
    redis_memory_peak.set(info['used_memory_peak'])
    redis_memory_fragmentation.set(info['mem_fragmentation_ratio'])

    # Keys (per namespace)
    for namespace in ['emr', 'osce', 'shared']:
        keys = redis_client.keys(f"{namespace}:*")
        redis_keys_total.labels(namespace=namespace).set(len(keys))

    # Performance
    redis_ops_per_sec.set(info['instantaneous_ops_per_sec'])

    # Hit rate calculation
    hits = info['keyspace_hits']
    misses = info['keyspace_misses']
    hit_rate = (hits / (hits + misses) * 100) if (hits + misses) > 0 else 0
    redis_hit_rate.set(hit_rate)

    # Connections
    redis_connected_clients.set(info['connected_clients'])
    redis_blocked_clients.set(info['blocked_clients'])
```

### Alert Rules (Prometheus)

```yaml
# prometheus/alerts/redis.yaml
groups:
  - name: redis_alerts
    interval: 30s
    rules:
      # Memory alerts
      - alert: RedisMemoryHigh
        expr: redis_memory_used_bytes / (2.5 * 1024^3) > 0.8
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Redis memory usage above 80%"
          description: "Redis is using {{ $value | humanizePercentage }} of allocated 2.5 GB"

      - alert: RedisMemoryCritical
        expr: redis_memory_used_bytes / (2.5 * 1024^3) > 0.9
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Redis memory usage above 90%"
          description: "Redis is using {{ $value | humanizePercentage }} of allocated 2.5 GB - risk of eviction"

      # Fragmentation alerts
      - alert: RedisHighFragmentation
        expr: redis_memory_fragmentation_ratio > 1.5
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Redis memory fragmentation high"
          description: "Fragmentation ratio is {{ $value }} - consider restart"

      # Performance alerts
      - alert: RedisSlowQueries
        expr: rate(redis_slowlog_length[5m]) > 10
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High rate of slow Redis queries"
          description: "{{ $value }} slow queries per minute"

      # Connection alerts
      - alert: RedisConnectionSaturation
        expr: redis_connected_clients > 9000
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Redis connection pool near limit"
          description: "{{ $value }} connected clients (limit: 10000)"
```

---

## 🔧 OPERATIONAL PROCEDURES

### Daily Operations

```bash
#!/bin/bash
# /scripts/redis_ops.sh

# 1. Check memory usage
redis-cli -p 6380 INFO memory | grep used_memory_human

# 2. Check key count by namespace
echo "EMR keys:"
redis-cli -p 6380 --scan --pattern "emr:*" | wc -l

echo "OSCE keys:"
redis-cli -p 6380 --scan --pattern "osce:*" | wc -l

# 3. Check slow queries
redis-cli -p 6380 SLOWLOG GET 10

# 4. Check connected clients
redis-cli -p 6380 CLIENT LIST | wc -l
```

### Backup Procedure

```bash
#!/bin/bash
# /scripts/redis_backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/redis"

# 1. Create RDB snapshot
redis-cli -p 6380 BGSAVE

# Wait for background save to complete
while [ $(redis-cli -p 6380 INFO persistence | grep rdb_bgsave_in_progress:1 | wc -l) -eq 1 ]; do
    echo "Waiting for BGSAVE to complete..."
    sleep 5
done

# 2. Copy RDB file
cp /var/lib/redis/dump.rdb ${BACKUP_DIR}/dump_${DATE}.rdb

# 3. Copy AOF file
cp /var/lib/redis/appendonly.aof ${BACKUP_DIR}/appendonly_${DATE}.aof

# 4. Upload to S3
aws s3 cp ${BACKUP_DIR}/dump_${DATE}.rdb s3://irstudy-backups/redis/
aws s3 cp ${BACKUP_DIR}/appendonly_${DATE}.aof s3://irstudy-backups/redis/

# 5. Clean up old backups (keep 7 days)
find ${BACKUP_DIR} -name "dump_*.rdb" -mtime +7 -delete
find ${BACKUP_DIR} -name "appendonly_*.aof" -mtime +7 -delete

echo "Backup completed: ${DATE}"
```

### Restore Procedure

```bash
#!/bin/bash
# /scripts/redis_restore.sh

BACKUP_FILE=$1  # e.g., dump_20260216_120000.rdb

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: ./redis_restore.sh <backup_file>"
    exit 1
fi

# 1. Stop Redis
redis-cli -p 6380 SHUTDOWN NOSAVE

# 2. Restore RDB file
cp ${BACKUP_FILE} /var/lib/redis/dump.rdb

# 3. Restart Redis
systemctl start redis

# 4. Verify
redis-cli -p 6380 PING
echo "Restore completed from ${BACKUP_FILE}"
```

### Emergency Flush (Use with Caution)

```bash
#!/bin/bash
# /scripts/redis_emergency_flush.sh

# Flush specific namespace (e.g., emr:* or osce:*)
NAMESPACE=$1

if [ -z "$NAMESPACE" ]; then
    echo "Usage: ./redis_emergency_flush.sh <namespace>"
    echo "Example: ./redis_emergency_flush.sh emr"
    exit 1
fi

echo "WARNING: This will delete all keys matching ${NAMESPACE}:*"
read -p "Are you sure? (yes/no): " CONFIRM

if [ "$CONFIRM" == "yes" ]; then
    redis-cli -p 6380 --scan --pattern "${NAMESPACE}:*" | xargs redis-cli -p 6380 DEL
    echo "Flushed ${NAMESPACE} namespace"
else
    echo "Aborted"
fi
```

---

## 🚨 TROUBLESHOOTING

### Common Issues

**Issue 1: Memory Exhausted**
```bash
# Symptoms
redis-cli -p 6380 INFO memory | grep maxmemory_policy
# Shows: maxmemory_policy:allkeys-lru

# Diagnosis
redis-cli -p 6380 INFO stats | grep evicted_keys
# If evicted_keys > 0, memory limit reached

# Solutions
# 1. Increase maxmemory (if infrastructure allows)
# 2. Reduce TTLs (free memory faster)
# 3. Delete old sessions manually
redis-cli -p 6380 --scan --pattern "osce:session:*" | xargs redis-cli -p 6380 TTL
# Delete sessions older than 1 hour
```

**Issue 2: High Latency**
```bash
# Symptoms
redis-cli -p 6380 --latency

# Diagnosis
redis-cli -p 6380 SLOWLOG GET 20
# Check for slow queries (>10ms)

# Solutions
# 1. Avoid KEYS command (use SCAN instead)
# 2. Optimize data structures (use hashes for small objects)
# 3. Enable pipelining for bulk operations
```

**Issue 3: Connection Limit Reached**
```bash
# Symptoms
redis-cli -p 6380 INFO clients | grep connected_clients
# If connected_clients > 9000 (warning), >10000 (critical)

# Diagnosis
redis-cli -p 6380 CLIENT LIST | head -20
# Check for stuck connections

# Solutions
# 1. Kill idle connections
redis-cli -p 6380 CLIENT LIST | grep idle | awk '{print $2}' | xargs -I {} redis-cli -p 6380 CLIENT KILL ID {}

# 2. Increase maxclients (if infrastructure allows)
```

**Issue 4: AOF File Corruption**
```bash
# Symptoms
# Redis fails to start with error: "Bad file format reading the append only file"

# Diagnosis
redis-check-aof /var/lib/redis/appendonly.aof

# Solutions
# 1. Repair AOF file
redis-check-aof --fix /var/lib/redis/appendonly.aof

# 2. If repair fails, restore from RDB snapshot
cp /backups/redis/dump_latest.rdb /var/lib/redis/dump.rdb
# Note: Will lose data since last RDB snapshot
```

---

## 📈 SCALING STRATEGY

### Current: Single Instance (2.5 GB)
- **Capacity**: 1000 concurrent OSCE sessions
- **Limitations**: No HA, single point of failure

### Future: Redis Sentinel (HA)
- **When**: >2000 active users, >500 concurrent sessions
- **Architecture**: 1 master + 2 replicas + 3 sentinels
- **Failover**: Automatic (< 30 seconds)

### Future: Redis Cluster (Sharding)
- **When**: >5000 active users, >10 GB data
- **Architecture**: 6 nodes (3 masters + 3 replicas)
- **Sharding**: By namespace (emr:* → shard 1, osce:* → shard 2)

---

## ✅ DEPLOYMENT CHECKLIST

### Pre-Deployment
- [ ] `redis.conf` created with maxmemory=2560mb
- [ ] Vault secret `ai-osce/redis-password` set
- [ ] Docker volume `irstudy-redis-data` created
- [ ] Backup script scheduled (cron: daily at 2 AM)

### Deployment
- [ ] Redis container started: `docker-compose up -d irstudy-redis`
- [ ] Health check passes: `docker exec irstudy-redis redis-cli ping`
- [ ] Password authentication works: `redis-cli -p 6380 -a <password> PING`
- [ ] Persistence verified: `redis-cli -p 6380 CONFIG GET save`

### Post-Deployment
- [ ] Prometheus metrics endpoint working (`/metrics`)
- [ ] Alerts configured (memory >80%, high fragmentation)
- [ ] Backup restored successfully (test disaster recovery)
- [ ] Load testing: 100 concurrent connections, <5ms latency

---

**Document Status**: ✅ Ready for Deployment
**Created**: 2026-02-16
**Last Updated**: 2026-02-16
**Version**: 1.0
**Owner**: DevOps + Backend Team
