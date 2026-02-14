# Week 2 Deployment Guide - WebSocket Authentication

**Version**: 1.0  
**Last Updated**: 2026-02-07  
**Project**: AMC Clinical Exam Simulation v2.0  
**Sprint**: Week 2 - Enhanced WebSocket Authentication

---

## Overview

This guide provides step-by-step instructions for deploying Week 2 WebSocket authentication system to production. Follow these procedures to ensure secure, compliant, and performant deployment.

### Prerequisites Checklist

Before deployment, ensure:

- [ ] **Infrastructure**: Redis Cluster, Vault, PostgreSQL provisioned
- [ ] **Secrets**: JWT secrets, Vault tokens configured
- [ ] **TLS Certificates**: Valid SSL/TLS certificates for `wss://`
- [ ] **Monitoring**: Prometheus, Grafana deployed
- [ ] **Backups**: Vault backup strategy in place
- [ ] **Testing**: All tests passing (35/35 unit tests, load tests)
- [ ] **Security Review**: Security runbook reviewed, incident response plan ready

---

## Prerequisites

### Infrastructure Requirements

**Required Services**:

| Service | Version | Purpose | High Availability |
|---------|---------|---------|-------------------|
| **Redis** | 7.0+ | Session storage, rate limiting, connection tracking | Yes (cluster mode) |
| **Vault** | 1.14+ | Secrets management, audit logs | Yes (HA mode) |
| **PostgreSQL** | 15+ | User database, session metadata | Yes (replication) |
| **Load Balancer** | Any | WebSocket connection distribution | Yes (active-active) |

**Resource Requirements** (per instance):

| Component | CPU | Memory | Storage | Network |
|-----------|-----|--------|---------|---------|
| Backend API | 4 vCPU | 8 GB | 50 GB | 1 Gbps |
| Redis | 2 vCPU | 4 GB | 20 GB (persistent) | 1 Gbps |
| Vault | 2 vCPU | 4 GB | 100 GB (audit logs) | 1 Gbps |
| PostgreSQL | 4 vCPU | 16 GB | 500 GB | 1 Gbps |

**Scaling**:
- Start with 3 backend instances (load balanced)
- Redis: 3-node cluster (1 primary, 2 replicas)
- Vault: 3-node HA cluster
- PostgreSQL: 1 primary + 2 read replicas

---

### Environment Variables

**Required Environment Variables**:

```bash
# Application
APP_ENV=production
DEBUG=false
LOG_LEVEL=INFO

# Security
SECRET_KEY=<fetch-from-vault>  # JWT signing key
CORS_ORIGINS=https://app.example.com

# Database
DATABASE_URL=postgresql://user:pass@postgres:5432/amc_simulation
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10

# Redis
REDIS_URL=redis://redis-cluster:7379
REDIS_MAX_CONNECTIONS=100
REDIS_SOCKET_TIMEOUT=5

# Vault
VAULT_ADDR=https://vault.example.com:8200
VAULT_TOKEN=<root-token-or-approle>
VAULT_KV_PATH=amc-simulation

# WebSocket
WS_MAX_CONNECTIONS_PER_USER=3
WS_RATE_LIMIT=10
WS_RATE_LIMIT_WINDOW=60
WS_HEARTBEAT_INTERVAL=30
WS_HEARTBEAT_TIMEOUT=300

# Monitoring
PROMETHEUS_ENABLED=true
PROMETHEUS_PORT=9090
GRAFANA_URL=https://grafana.example.com

# Logging
SENTRY_DSN=https://...@sentry.io/...  # Error tracking
LOG_FORMAT=json  # Production format
```

**Environment Variable Sources**:
- **Development**: `.env` file (not committed)
- **Staging/Production**: Kubernetes Secrets, AWS Secrets Manager, or Vault

---

## Secrets Management

### Vault Setup

**1. Initialize Vault** (if not already done):
```bash
# Initialize Vault cluster
vault operator init -key-shares=5 -key-threshold=3

# Unseal Vault (on all nodes)
vault operator unseal <unseal-key-1>
vault operator unseal <unseal-key-2>
vault operator unseal <unseal-key-3>

# Login
vault login <root-token>
```

**2. Enable KV Secrets Engine**:
```bash
# Enable KV v2 secrets engine
vault secrets enable -path=amc-simulation kv-v2

# Enable audit logs
vault secrets enable -path=audit kv-v2
```

**3. Store JWT Secret**:
```bash
# Generate secure JWT secret (256-bit)
JWT_SECRET=$(openssl rand -hex 32)

# Store in Vault
vault kv put amc-simulation/api-keys \
  jwt_secret=$JWT_SECRET \
  created_at=$(date -u +"%Y-%m-%dT%H:%M:%SZ") \
  rotation_policy="90 days"

# Verify
vault kv get amc-simulation/api-keys
```

**4. Store Database Credentials**:
```bash
vault kv put amc-simulation/database \
  username="amc_user" \
  password="$(openssl rand -base64 32)" \
  host="postgres.example.com" \
  port="5432" \
  database="amc_simulation"
```

**5. Create Vault Policies**:
```bash
# Create policy for application
cat > amc-app-policy.hcl <<'POLICY'
# Read application secrets
path "amc-simulation/data/api-keys" {
  capabilities = ["read"]
}

path "amc-simulation/data/database" {
  capabilities = ["read"]
}

# Write audit logs
path "audit/data/security_events/*" {
  capabilities = ["create", "update", "read"]
}
POLICY

# Apply policy
vault policy write amc-app amc-app-policy.hcl

# Create token with policy (for application)
vault token create -policy=amc-app -ttl=720h
```

---

### Secret Rotation

**JWT Secret Rotation** (every 90 days):

```bash
# 1. Generate new secret
NEW_SECRET=$(openssl rand -hex 32)

# 2. Store in Vault with version
vault kv put amc-simulation/api-keys \
  jwt_secret=$NEW_SECRET \
  previous_secret=$(vault kv get -field=jwt_secret amc-simulation/api-keys) \
  rotated_at=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# 3. Rolling restart application (supports both old and new secrets for 24h)
kubectl rollout restart deployment/amc-backend

# 4. After 24h, remove support for old secret
# (Update application to only use new secret)
```

**Database Password Rotation**:

```bash
# 1. Create new database user
psql -c "CREATE USER amc_user_new WITH PASSWORD 'new-password';"
psql -c "GRANT ALL PRIVILEGES ON DATABASE amc_simulation TO amc_user_new;"

# 2. Update Vault
vault kv put amc-simulation/database \
  username="amc_user_new" \
  password="new-password" \
  host="postgres.example.com" \
  port="5432" \
  database="amc_simulation"

# 3. Rolling restart application
kubectl rollout restart deployment/amc-backend

# 4. After verification, drop old user
psql -c "DROP USER amc_user;"
```

---

## Redis Configuration

### Redis Cluster Setup

**Cluster Configuration** (`redis.conf`):

```conf
# Cluster mode
cluster-enabled yes
cluster-config-file nodes.conf
cluster-node-timeout 5000

# Persistence
save 900 1
save 300 10
save 60 10000
appendonly yes
appendfilename "appendonly.aof"

# Memory
maxmemory 4gb
maxmemory-policy allkeys-lru

# Security
requirepass <redis-password>
protected-mode yes
bind 0.0.0.0

# Performance
tcp-backlog 511
timeout 300
tcp-keepalive 300
```

**Create Redis Cluster**:

```bash
# Create 3-node cluster (1 primary, 2 replicas)
redis-cli --cluster create \
  redis-1:7379 \
  redis-2:7379 \
  redis-3:7379 \
  --cluster-replicas 1 \
  --cluster-yes

# Verify cluster
redis-cli -c -h redis-1 -p 7379 cluster info
redis-cli -c -h redis-1 -p 7379 cluster nodes
```

**Redis Persistence Strategy**:

1. **RDB Snapshots**: Every 15 minutes (if ≥1 key changed)
2. **AOF (Append-Only File)**: Enabled (fsync every second)
3. **Backup**: Daily snapshots to S3/GCS

**Backup Script**:
```bash
#!/bin/bash
# redis-backup.sh

DATE=$(date +%Y-%m-%d)
BACKUP_DIR=/backups/redis

# Save RDB snapshot
redis-cli -h redis-1 -p 7379 BGSAVE

# Wait for save to complete
while [ $(redis-cli -h redis-1 -p 7379 LASTSAVE) -eq $(redis-cli -h redis-1 -p 7379 LASTSAVE) ]; do
  sleep 1
done

# Copy to backup location
cp /var/lib/redis/dump.rdb $BACKUP_DIR/dump-$DATE.rdb

# Upload to cloud storage
aws s3 cp $BACKUP_DIR/dump-$DATE.rdb s3://backups/redis/

# Clean old backups (keep 30 days)
find $BACKUP_DIR -name "dump-*.rdb" -mtime +30 -delete
```

---

## Database Migration

### Alembic Migrations for Week 2

**Migration Files**:
```
backend/alembic/versions/
├── 20260201_1430_001_initial_schema.py  (Week 1)
└── 20260207_1000_002_websocket_auth.py  (Week 2 - NEW)
```

**Week 2 Migration** (`20260207_1000_002_websocket_auth.py`):

```python
"""Week 2: WebSocket authentication tables

Revision ID: 20260207_1000_002
Revises: 20260201_1430_001
Create Date: 2026-02-07 10:00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

# revision identifiers
revision = '20260207_1000_002'
down_revision = '20260201_1430_001'
branch_labels = None
depends_on = None

def upgrade():
    # WebSocket sessions table
    op.create_table(
        'websocket_sessions',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', UUID(as_uuid=True), nullable=False),
        sa.Column('connection_id', sa.String(64), nullable=False, unique=True),
        sa.Column('ip_address', sa.String(45), nullable=False),
        sa.Column('user_agent', sa.Text, nullable=True),
        sa.Column('fingerprint', sa.String(64), nullable=False),
        sa.Column('connected_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('last_heartbeat', sa.DateTime(timezone=True), nullable=False),
        sa.Column('disconnected_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('metadata', JSONB, nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
    )
    
    # Indexes
    op.create_index('idx_websocket_sessions_user_id', 'websocket_sessions', ['user_id'])
    op.create_index('idx_websocket_sessions_connection_id', 'websocket_sessions', ['connection_id'])
    op.create_index('idx_websocket_sessions_connected_at', 'websocket_sessions', ['connected_at'])

def downgrade():
    op.drop_index('idx_websocket_sessions_connected_at')
    op.drop_index('idx_websocket_sessions_connection_id')
    op.drop_index('idx_websocket_sessions_user_id')
    op.drop_table('websocket_sessions')
```

**Run Migration**:

```bash
# Development
cd backend
source venv/bin/activate
alembic upgrade head

# Production (via deployment pipeline)
kubectl exec -it deployment/amc-backend -- \
  alembic upgrade head

# Verify
alembic current
alembic history
```

**Rollback** (if needed):
```bash
# Rollback to previous version
alembic downgrade -1

# Rollback to specific version
alembic downgrade 20260201_1430_001
```

---

## Service Deployment

### Docker Compose (Development/Staging)

**docker-compose.yml**:

```yaml
version: '3.8'

services:
  # Backend API
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - APP_ENV=production
      - DATABASE_URL=postgresql://user:pass@postgres:5432/amc_simulation
      - REDIS_URL=redis://redis:7379
      - VAULT_ADDR=http://vault:8200
      - VAULT_TOKEN=${VAULT_TOKEN}
      - SECRET_KEY=${SECRET_KEY}
    depends_on:
      - postgres
      - redis
      - vault
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped
  
  # Redis Cluster
  redis:
    image: redis:7-alpine
    ports:
      - "7379:7379"
    command: >
      redis-server
      --port 7379
      --requirepass ${REDIS_PASSWORD}
      --appendonly yes
      --maxmemory 4gb
      --maxmemory-policy allkeys-lru
    volumes:
      - redis-data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "-p", "7379", "ping"]
      interval: 10s
      timeout: 3s
      retries: 3
    restart: unless-stopped
  
  # HashiCorp Vault
  vault:
    image: vault:1.14
    ports:
      - "8200:8200"
    environment:
      - VAULT_DEV_ROOT_TOKEN_ID=${VAULT_ROOT_TOKEN}
      - VAULT_DEV_LISTEN_ADDRESS=0.0.0.0:8200
    cap_add:
      - IPC_LOCK
    volumes:
      - vault-data:/vault/data
    healthcheck:
      test: ["CMD", "vault", "status"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped
  
  # PostgreSQL
  postgres:
    image: postgres:15-alpine
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_USER=amc_user
      - POSTGRES_PASSWORD=${DB_PASSWORD}
      - POSTGRES_DB=amc_simulation
    volumes:
      - postgres-data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U amc_user"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped
  
  # Prometheus
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
    restart: unless-stopped
  
  # Grafana
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
    volumes:
      - grafana-data:/var/lib/grafana
      - ./monitoring/grafana-dashboards:/etc/grafana/provisioning/dashboards
    restart: unless-stopped

volumes:
  redis-data:
  vault-data:
  postgres-data:
  prometheus-data:
  grafana-data:
```

**Deploy**:
```bash
# Set environment variables
export VAULT_TOKEN=$(openssl rand -hex 32)
export SECRET_KEY=$(openssl rand -hex 32)
export REDIS_PASSWORD=$(openssl rand -hex 16)
export DB_PASSWORD=$(openssl rand -base64 32)
export GRAFANA_PASSWORD=$(openssl rand -base64 16)

# Deploy
docker-compose up -d

# Verify
docker-compose ps
docker-compose logs -f backend
```

---

### Kubernetes Deployment (Production)

**Namespace**:
```yaml
# namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: amc-simulation
```

**Secrets**:
```yaml
# secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: amc-secrets
  namespace: amc-simulation
type: Opaque
stringData:
  jwt-secret: <base64-encoded>
  db-password: <base64-encoded>
  redis-password: <base64-encoded>
  vault-token: <base64-encoded>
```

**Backend Deployment**:
```yaml
# backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: amc-backend
  namespace: amc-simulation
spec:
  replicas: 3
  selector:
    matchLabels:
      app: amc-backend
  template:
    metadata:
      labels:
        app: amc-backend
    spec:
      containers:
      - name: backend
        image: amc-simulation/backend:week2-latest
        ports:
        - containerPort: 8000
          name: http
        env:
        - name: APP_ENV
          value: "production"
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: amc-secrets
              key: database-url
        - name: REDIS_URL
          value: "redis://redis-cluster:7379"
        - name: VAULT_ADDR
          value: "https://vault.amc-simulation.svc.cluster.local:8200"
        - name: VAULT_TOKEN
          valueFrom:
            secretKeyRef:
              name: amc-secrets
              key: vault-token
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: amc-secrets
              key: jwt-secret
        resources:
          requests:
            memory: "4Gi"
            cpu: "2000m"
          limits:
            memory: "8Gi"
            cpu: "4000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
```

**Backend Service**:
```yaml
# backend-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: amc-backend
  namespace: amc-simulation
spec:
  selector:
    app: amc-backend
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

**Deploy to Kubernetes**:
```bash
# Create namespace
kubectl apply -f namespace.yaml

# Create secrets (use sealed-secrets or external-secrets in production)
kubectl apply -f secrets.yaml

# Deploy application
kubectl apply -f backend-deployment.yaml
kubectl apply -f backend-service.yaml

# Verify deployment
kubectl get pods -n amc-simulation
kubectl logs -f deployment/amc-backend -n amc-simulation

# Check service
kubectl get svc -n amc-simulation
```

---

## Health Checks

### Health Check Endpoints

**1. Application Health**:
```bash
curl http://localhost:8000/health

# Response
{
  "status": "healthy",
  "timestamp": "2026-02-07T10:30:45Z",
  "version": "2.0.0",
  "checks": {
    "database": "healthy",
    "redis": "healthy",
    "vault": "healthy"
  }
}
```

**2. Redis Health**:
```bash
redis-cli -h redis-cluster -p 7379 PING
# Response: PONG
```

**3. Vault Health**:
```bash
curl -s https://vault.example.com:8200/v1/sys/health | jq
# Response: {"initialized": true, "sealed": false, ...}
```

**4. Database Health**:
```bash
psql -h postgres -U amc_user -d amc_simulation -c "SELECT 1;"
# Response: 1
```

---

## Performance Tuning

### Redis Optimization

**Connection Pooling**:
```python
# backend/src/config.py
REDIS_MAX_CONNECTIONS = 100  # Per instance
REDIS_SOCKET_TIMEOUT = 5     # Seconds
REDIS_SOCKET_CONNECT_TIMEOUT = 2
```

**Memory Optimization**:
```conf
# redis.conf
maxmemory 4gb
maxmemory-policy allkeys-lru  # Evict least recently used keys
```

**Persistence Tuning**:
```conf
# RDB snapshots (less frequent for performance)
save 900 1      # 15 minutes if ≥1 key changed
save 300 100    # 5 minutes if ≥100 keys changed

# AOF (append-only file)
appendonly yes
appendfsync everysec  # Balance between safety and performance
```

### Database Optimization

**Connection Pooling**:
```python
# backend/src/db/base.py
DATABASE_POOL_SIZE = 20           # Connections per instance
DATABASE_MAX_OVERFLOW = 10        # Extra connections if pool exhausted
DATABASE_POOL_RECYCLE = 3600      # Recycle connections every hour
```

**Indexes** (from migration):
```sql
CREATE INDEX idx_websocket_sessions_user_id ON websocket_sessions(user_id);
CREATE INDEX idx_websocket_sessions_connection_id ON websocket_sessions(connection_id);
CREATE INDEX idx_websocket_sessions_connected_at ON websocket_sessions(connected_at);
```

---

## Security Hardening

### TLS Configuration

**Generate TLS Certificates** (Let's Encrypt):
```bash
# Install certbot
apt-get install certbot

# Generate certificate
certbot certonly --standalone -d api.example.com

# Certificate location
/etc/letsencrypt/live/api.example.com/fullchain.pem
/etc/letsencrypt/live/api.example.com/privkey.pem
```

**NGINX Configuration** (TLS termination):
```nginx
server {
    listen 443 ssl http2;
    server_name api.example.com;
    
    # TLS certificates
    ssl_certificate /etc/letsencrypt/live/api.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.example.com/privkey.pem;
    
    # TLS settings (Mozilla Modern)
    ssl_protocols TLSv1.3;
    ssl_prefer_server_ciphers off;
    
    # WebSocket proxy
    location /ws {
        proxy_pass http://backend:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_read_timeout 3600s;
        proxy_send_timeout 3600s;
    }
    
    # API proxy
    location / {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Firewall Rules

**Allow only necessary ports**:
```bash
# Application
ufw allow 443/tcp  # HTTPS
ufw allow 8000/tcp # Backend (internal only)

# Redis (internal only)
ufw allow from 10.0.0.0/8 to any port 7379

# Vault (internal only)
ufw allow from 10.0.0.0/8 to any port 8200

# PostgreSQL (internal only)
ufw allow from 10.0.0.0/8 to any port 5432

# Enable firewall
ufw enable
```

### Rate Limit Tuning

**Adjust WebSocket rate limits**:
```python
# backend/src/websocket/rate_limiter.py
class RateLimiter:
    def __init__(
        self,
        redis_client: redis.Redis,
        max_connections: int = 20,  # Increased from 10 (if needed)
        window_seconds: int = 60
    ):
```

**NGINX rate limiting** (DDoS protection):
```nginx
http {
    # Define rate limit zone
    limit_req_zone $binary_remote_addr zone=websocket:10m rate=10r/s;
    
    server {
        location /ws {
            # Apply rate limit
            limit_req zone=websocket burst=20 nodelay;
            
            proxy_pass http://backend:8000;
            # ... (rest of config)
        }
    }
}
```

---

## Rollback Procedures

### Rollback to Week 1

**Scenario**: Critical issue in Week 2, need to revert

**Procedure**:

```bash
# 1. Rollback database migration
alembic downgrade 20260201_1430_001

# 2. Deploy Week 1 backend
kubectl set image deployment/amc-backend \
  backend=amc-simulation/backend:week1-stable \
  -n amc-simulation

# 3. Verify rollback
kubectl rollout status deployment/amc-backend -n amc-simulation

# 4. Clear Redis (Week 2 data structures)
redis-cli -h redis-cluster -p 7379 FLUSHDB

# 5. Restart backend
kubectl rollout restart deployment/amc-backend -n amc-simulation

# 6. Verify health
curl https://api.example.com/health

# 7. Monitor logs
kubectl logs -f deployment/amc-backend -n amc-simulation
```

**Post-Rollback**:
1. Investigate root cause of issue
2. Fix issue in Week 2 code
3. Re-test in staging environment
4. Re-deploy Week 2 when ready

---

## Post-Deployment Validation

### Smoke Tests

**1. Application Health**:
```bash
curl -f https://api.example.com/health || echo "FAIL: Health check failed"
```

**2. WebSocket Connection**:
```bash
# Install wscat: npm install -g wscat

# Get JWT token
TOKEN=$(curl -X POST https://api.example.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password"}' | \
  jq -r '.access_token')

# Test WebSocket connection
wscat -c wss://api.example.com/ws \
  --header "Authorization: Bearer $TOKEN" \
  --header "X-Session-ID: $(uuidgen)" \
  --header "X-Fingerprint: $(echo -n 'test' | sha256sum | cut -d' ' -f1)"

# Expected: Connection established
```

**3. Rate Limiting**:
```bash
# Attempt 11 connections rapidly (should be rate limited)
for i in {1..11}; do
  wscat -c wss://api.example.com/ws \
    --header "Authorization: Bearer $TOKEN" \
    --header "X-Session-ID: $(uuidgen)" \
    --header "X-Fingerprint: $(echo -n 'test' | sha256sum | cut -d' ' -f1)" &
done

# Expected: 10 succeed, 11th gets 429 Too Many Requests
```

**4. Security Event Logging**:
```bash
# Check events in Vault
vault kv get audit/security_events/$(date +%Y-%m-%d) | jq

# Expected: Recent authentication events visible
```

**5. Prometheus Metrics**:
```bash
curl -s http://prometheus.example.com/api/v1/query?query=security_events_total | jq

# Expected: Metrics available
```

### Load Tests

**Run load tests post-deployment**:
```bash
# SSH to backend instance
ssh backend-1.example.com

# Run load tests
cd /app
source venv/bin/activate
bash run_load_tests.sh

# Review report
cat TASK_2.3_LOAD_TEST_REPORT.md
```

**Expected Results**:
- P95 latency <50ms
- 100 concurrent connections successful
- Rate limiting enforced
- Connection tracking working
- 0 errors

---

## Monitoring Setup

### Prometheus Configuration

**prometheus.yml**:
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'amc-backend'
    static_configs:
      - targets: ['backend-1:8000', 'backend-2:8000', 'backend-3:8000']
    metrics_path: '/metrics'

  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']

alerting:
  alertmanagers:
    - static_configs:
        - targets: ['alertmanager:9093']

rule_files:
  - 'alerts.yml'
```

**alerts.yml** (copy from WEEK2_SECURITY_RUNBOOK.md):
```yaml
groups:
  - name: websocket_auth
    interval: 30s
    rules:
      - alert: HighAuthFailureRate
        expr: rate(security_events_total{event_type="ws_auth_failed"}[5m]) > 10
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High WebSocket authentication failure rate"
          description: "{{ $value }} failed auth attempts/sec (threshold: 10/sec)"
```

### Grafana Dashboards

**Import Week 2 Dashboard**:
1. Login to Grafana: https://grafana.example.com
2. Import dashboard from `monitoring/grafana-dashboards/week2-websocket-auth.json`
3. Configure data source: Prometheus

**Dashboard Panels**:
- Authentication success rate (%)
- Failed authentication attempts/sec
- Rate limit rejections/sec
- Active WebSocket connections
- P50/P95/P99 authentication latency
- Vault flush latency
- Redis memory usage
- Database connection pool

---

## Conclusion

Week 2 WebSocket authentication system is now deployed to production. For operational procedures, see:

- **Security Runbook**: `WEEK2_SECURITY_RUNBOOK.md`
- **API Documentation**: `WEEK2_API_DOCUMENTATION.md`
- **Operations Guide**: `WEEK2_OPERATIONS_GUIDE.md`

**For Production Support**: Contact DevOps team at `devops@example.com`

---

**Revision History**:

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2026-02-07 | Initial release | DevOps Team |

---

**Status**: ✅ PRODUCTION-READY
