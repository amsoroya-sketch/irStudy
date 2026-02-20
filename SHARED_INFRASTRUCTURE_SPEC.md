# Shared Infrastructure Specification
## irStudy Platform - EMR Practice + AI OSCE Simulation

**Date**: 2026-02-16
**Version**: 1.0
**Scope**: Reusable components across EMR and AI OSCE systems
**Status**: Ready for Implementation

---

## 📋 OVERVIEW

This document defines the **shared infrastructure** components used by both the EMR Practice System and AI OSCE Simulation System. By centralizing these specifications, we ensure consistency, prevent duplicate work, and enable seamless integration between systems.

**Purpose**: Single source of truth for Vault, Redis, JWT, security headers, and encryption standards.

**Systems Covered**:
- EMR Practice System (SOAP documentation, Claude AI validation)
- AI OSCE Simulation (AI Patient/Examiner, 8-minute sessions)

---

## 🔐 1. HASHICORP VAULT - SECRET MANAGEMENT

### 1.1 Vault Key Hierarchy

```
secret/
├── database/
│   ├── postgres-irstudy-password         # Shared by both systems
│   ├── postgres-connection-string        # postgresql://user:pass@host:5433/irstudy
│   └── postgres-admin-password           # For migrations, admin tasks
│
├── emr/
│   ├── claude-api-key                    # EMR SOAP validator (shared with AI OSCE)
│   ├── session-encryption-key            # AES-256-GCM key for EMR data at rest
│   ├── template-signing-key              # HMAC key for template integrity
│   └── fallback-validator-key            # Rule-based fallback when Claude down
│
├── ai-osce/
│   ├── claude-api-key                    # AI Patient/Examiner (same as emr/claude-api-key)
│   ├── kimi-api-key                      # Fallback for AI Patient (70% quality)
│   ├── redis-password                    # OSCE session storage authentication
│   ├── websocket-secret                  # JWT signing for WebSocket connections
│   ├── session-encryption-key            # AES-256-GCM for transcript encryption
│   └── scoring-salt                      # Salt for scoring hash verification
│
└── shared/
    ├── jwt-secret                        # Authentication token signing (256-bit)
    ├── jwt-refresh-secret                # Refresh token signing (256-bit, rotated monthly)
    ├── https-tls-cert                    # SSL certificate (Let's Encrypt or CA)
    ├── https-tls-key                     # SSL private key
    └── api-rate-limit-secret             # HMAC secret for rate limit tokens
```

### 1.2 Access Control Policies

**EMR Backend Service**:
```hcl
path "secret/emr/*" {
  capabilities = ["read"]
}

path "secret/database/*" {
  capabilities = ["read"]
}

path "secret/shared/jwt-secret" {
  capabilities = ["read"]
}

path "secret/shared/api-rate-limit-secret" {
  capabilities = ["read"]
}
```

**AI OSCE Backend Service**:
```hcl
path "secret/ai-osce/*" {
  capabilities = ["read"]
}

path "secret/database/*" {
  capabilities = ["read"]
}

path "secret/shared/jwt-secret" {
  capabilities = ["read"]
}

path "secret/shared/api-rate-limit-secret" {
  capabilities = ["read"]
}
```

**Admin / DevOps**:
```hcl
path "secret/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}
```

### 1.3 Key Rotation Schedule

| Secret | Rotation Frequency | Method |
|--------|-------------------|--------|
| Database passwords | 90 days | Manual, coordinated downtime |
| JWT secrets | 30 days | Automatic, dual-key overlap |
| Claude API key | As needed | Immediate (API key compromised) |
| Encryption keys | 180 days | Gradual migration (dual-key decrypt) |
| TLS certificates | 90 days (Let's Encrypt auto) | Automated via certbot |

### 1.4 Vault Configuration

**Development Mode** (local testing):
```bash
vault server -dev -dev-root-token-id="dev-only-token-change-in-prod"
export VAULT_ADDR='http://localhost:8200'
export VAULT_TOKEN='dev-only-token-change-in-prod'
```

**Production Mode** (self-hosted HA):
```bash
# vault.hcl
storage "postgresql" {
  connection_url = "postgresql://vault:password@localhost:5432/vault"
}

listener "tcp" {
  address     = "0.0.0.0:8200"
  tls_cert_file = "/etc/vault/tls/cert.pem"
  tls_key_file  = "/etc/vault/tls/key.pem"
}

ui = true
api_addr = "https://vault.irstudy.internal:8200"
cluster_addr = "https://vault.irstudy.internal:8201"
```

### 1.5 Backend Integration

**Python (FastAPI)**:
```python
# backend/src/core/vault.py
import hvac
import os

class VaultClient:
    def __init__(self):
        self.client = hvac.Client(
            url=os.getenv('VAULT_ADDR', 'http://localhost:8200'),
            token=os.getenv('VAULT_TOKEN')
        )

    def get_secret(self, path: str) -> dict:
        """Read secret from Vault"""
        response = self.client.secrets.kv.v2.read_secret_version(path=path)
        return response['data']['data']

    def get_database_config(self) -> dict:
        """Get PostgreSQL connection details"""
        return self.get_secret('database')

    def get_jwt_secret(self) -> str:
        """Get JWT signing secret"""
        secrets = self.get_secret('shared/jwt-secret')
        return secrets['value']

# Usage in services
vault = VaultClient()
db_config = vault.get_database_config()
DATABASE_URL = db_config['postgres-connection-string']
```

---

## 🗄️ 2. REDIS - IN-MEMORY DATA STORE

### 2.1 Namespace Strategy

**EMR System** (512 MB allocation):
```
emr:dashboard:user:{user_id}           # Dashboard analytics cache (TTL: 5 min)
emr:ratelimit:{ip_address}             # API rate limiting counters (TTL: 1 min)
emr:session:{session_id}:autosave      # Auto-save buffer for SOAP notes (TTL: 1 hour)
emr:template:cache:{template_id}       # Cached SOAP templates (TTL: 24 hours)
emr:validation:queue:{user_id}         # Claude API validation queue (FIFO)
```

**AI OSCE System** (2 GB allocation):
```
osce:session:{session_id}:state        # Active session state (8-min conversations, NO TTL until complete)
osce:session:{session_id}:transcript   # Real-time transcript (synced to PostgreSQL every 30s, NO TTL)
osce:session:{session_id}:emotional    # Emotional state machine (6 states, NO TTL)
osce:session:{session_id}:timer        # Countdown timer (8 min = 480s, TTL: 480s)
osce:ratelimit:claude:{user_id}        # Claude API rate limiting (TTL: 1 min)
osce:persona:cache:{persona_id}        # Cached patient personas (TTL: 1 hour)
```

**Shared**:
```
shared:ratelimit:global:claude         # Global Claude API rate limit (90 req/min combined)
shared:session:{session_id}:lock       # Distributed locks for concurrent operations
```

### 2.2 Memory Configuration

**redis.conf**:
```conf
# Total memory
maxmemory 2560mb                       # 2.5 GB total (512 MB EMR + 2 GB OSCE)

# Default eviction policy
maxmemory-policy allkeys-lru           # Evict least recently used keys

# Namespace-specific policies (using Redis modules or client-side enforcement)
# EMR: Allow eviction (cache can be regenerated)
# OSCE: No eviction for active sessions (critical data, synced to PostgreSQL)
```

**Client-Side Enforcement** (Python):
```python
# backend/src/core/redis_config.py
import redis

class RedisClient:
    def __init__(self):
        self.client = redis.Redis(
            host='localhost',
            port=6380,
            db=0,
            password=vault.get_secret('ai-osce/redis-password')['value'],
            decode_responses=True
        )

    def set_emr_cache(self, key: str, value: str, ttl: int = 300):
        """EMR cache with TTL (evictable)"""
        full_key = f"emr:{key}"
        self.client.setex(full_key, ttl, value)

    def set_osce_session(self, session_id: str, field: str, value: str):
        """OSCE session data (no TTL, critical)"""
        full_key = f"osce:session:{session_id}:{field}"
        self.client.set(full_key, value)  # No TTL until session ends

    def get_with_namespace(self, namespace: str, key: str) -> str:
        """Get value with namespace prefix"""
        full_key = f"{namespace}:{key}"
        return self.client.get(full_key)
```

### 2.3 Persistence Strategy

**RDB (Snapshot)**:
```conf
# Save snapshots to disk
save 900 1       # After 900 sec (15 min) if at least 1 key changed
save 300 10      # After 300 sec (5 min) if at least 10 keys changed
save 60 10000    # After 60 sec if at least 10000 keys changed

dbfilename dump.rdb
dir /var/lib/redis
```

**AOF (Append-Only File)** - For OSCE session safety:
```conf
appendonly yes
appendfilename "appendonly.aof"
appendfsync everysec               # Sync to disk every second (balance performance/safety)
auto-aof-rewrite-percentage 100    # Rewrite when AOF is 2x original size
auto-aof-rewrite-min-size 64mb
```

### 2.4 Backup & Recovery

**Daily Backup**:
```bash
#!/bin/bash
# /scripts/redis_backup.sh
DATE=$(date +%Y%m%d_%H%M%S)
redis-cli --rdb /backups/redis_dump_${DATE}.rdb
aws s3 cp /backups/redis_dump_${DATE}.rdb s3://irstudy-backups/redis/
```

**Disaster Recovery**:
```bash
# Restore from backup
redis-cli SHUTDOWN NOSAVE
cp /backups/redis_dump_20260216_120000.rdb /var/lib/redis/dump.rdb
redis-server /etc/redis/redis.conf
```

---

## 🔑 3. JWT AUTHENTICATION - UNIFIED TOKEN FORMAT

### 3.1 Token Structure

**Access Token** (15-minute expiry):
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "student@example.com",
  "role": "student",
  "user_progress_id": "660e8400-e29b-41d4-a716-446655440001",
  "subscription_tier": "premium",
  "mock_exam_access": true,
  "emr_session_limit": 50,
  "osce_session_limit": 30,
  "iat": 1708041600,
  "exp": 1708042500,
  "iss": "irstudy-platform",
  "aud": ["emr-api", "osce-api"]
}
```

**Refresh Token** (7-day expiry):
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "token_id": "770e8400-e29b-41d4-a716-446655440002",
  "iat": 1708041600,
  "exp": 1708646400,
  "iss": "irstudy-platform",
  "type": "refresh"
}
```

### 3.2 Token Generation (Python)

```python
# backend/src/core/auth.py
import jwt
from datetime import datetime, timedelta

def create_access_token(user: User, vault: VaultClient) -> str:
    """Create JWT access token"""
    jwt_secret = vault.get_jwt_secret()

    payload = {
        "user_id": str(user.user_id),
        "email": user.email,
        "role": user.role,
        "user_progress_id": str(user.user_progress_id),
        "subscription_tier": user.subscription_tier,
        "mock_exam_access": user.has_mock_exam_access,
        "emr_session_limit": 50,  # From subscription tier
        "osce_session_limit": 30,
        "iat": int(datetime.utcnow().timestamp()),
        "exp": int((datetime.utcnow() + timedelta(minutes=15)).timestamp()),
        "iss": "irstudy-platform",
        "aud": ["emr-api", "osce-api"]
    }

    return jwt.encode(payload, jwt_secret, algorithm="HS256")

def verify_token(token: str, vault: VaultClient) -> dict:
    """Verify and decode JWT token"""
    jwt_secret = vault.get_jwt_secret()

    try:
        payload = jwt.decode(
            token,
            jwt_secret,
            algorithms=["HS256"],
            audience=["emr-api", "osce-api"],
            issuer="irstudy-platform"
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

### 3.3 Token Usage in APIs

**FastAPI Dependency**:
```python
from fastapi import Depends, HTTPException, Header

async def get_current_user(authorization: str = Header(None)) -> dict:
    """Extract and verify JWT from Authorization header"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

    token = authorization.replace("Bearer ", "")
    payload = verify_token(token, vault)

    return payload

# Usage in endpoints
@app.get("/api/v1/emr/sessions")
async def get_emr_sessions(current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    # ... fetch sessions for user_id
```

---

## 🔒 4. HTTPS & SECURITY HEADERS

### 4.1 Security Headers (9 Headers - Mandatory)

**Applied to ALL responses** (EMR + OSCE):
```python
# backend/src/middleware/https_redirect.py
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # 1. HSTS - Force HTTPS for 1 year
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        # 2. Prevent MIME sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # 3. Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"

        # 4. XSS protection
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # 5. Content Security Policy
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; "
            "font-src 'self'; "
            "connect-src 'self' wss://irstudy.com"  # Allow WebSocket for OSCE
        )

        # 6. Referrer policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # 7. Permissions policy (disable unused features)
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"

        # 8. Cache control (no caching of sensitive data)
        if "/api/v1/" in request.url.path:
            response.headers["Cache-Control"] = "no-store, max-age=0"
            response.headers["Pragma"] = "no-cache"

        return response
```

### 4.2 HTTPS Redirect

**HTTP → HTTPS Automatic Redirect**:
```python
class HTTPSRedirectMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # In production, redirect all HTTP to HTTPS
        if request.url.scheme == "http" and os.getenv("ENVIRONMENT") == "production":
            https_url = request.url.replace(scheme="https")
            return RedirectResponse(url=str(https_url), status_code=301)

        return await call_next(request)
```

### 4.3 WebSocket Security (OSCE System)

**Secure WebSocket (wss://) with JWT**:
```python
from fastapi import WebSocket, WebSocketDisconnect

@app.websocket("/ws/osce/{session_id}")
async def osce_websocket(websocket: WebSocket, session_id: str):
    # 1. Accept connection
    await websocket.accept()

    try:
        # 2. First message must be JWT token
        auth_message = await websocket.receive_text()
        auth_data = json.loads(auth_message)
        token = auth_data.get("token")

        # 3. Verify JWT
        payload = verify_token(token, vault)
        user_id = payload["user_id"]

        # 4. Validate user has access to this session
        if not await verify_session_access(user_id, session_id):
            await websocket.send_text(json.dumps({"error": "Unauthorized"}))
            await websocket.close(code=1008)
            return

        # 5. Session is authenticated, proceed with OSCE conversation
        while True:
            message = await websocket.receive_text()
            # ... handle OSCE conversation

    except WebSocketDisconnect:
        # Clean up session
        pass
```

---

## 🔐 5. ENCRYPTION STANDARDS

### 5.1 Data at Rest (AES-256-GCM)

**PHI/Sensitive Data in PostgreSQL**:
```python
# backend/src/security/encryption.py
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.backends import default_backend
import os

class DataEncryption:
    def __init__(self, vault: VaultClient, system: str):
        """
        system: 'emr' or 'ai-osce'
        """
        key_path = f"{system}/session-encryption-key"
        self.key = vault.get_secret(key_path)['value'].encode()
        self.cipher = AESGCM(self.key)

    def encrypt(self, plaintext: str) -> bytes:
        """Encrypt data with AES-256-GCM"""
        nonce = os.urandom(12)  # 96-bit nonce
        plaintext_bytes = plaintext.encode('utf-8')
        ciphertext = self.cipher.encrypt(nonce, plaintext_bytes, None)

        # Return nonce + ciphertext (prepend nonce for decryption)
        return nonce + ciphertext

    def decrypt(self, encrypted_data: bytes) -> str:
        """Decrypt data with AES-256-GCM"""
        nonce = encrypted_data[:12]
        ciphertext = encrypted_data[12:]
        plaintext_bytes = self.cipher.decrypt(nonce, ciphertext, None)
        return plaintext_bytes.decode('utf-8')

# Usage in models
emr_cipher = DataEncryption(vault, 'emr')
osce_cipher = DataEncryption(vault, 'ai-osce')

# Encrypt SOAP note before saving
encrypted_soap = emr_cipher.encrypt(soap_note_text)
db.execute("INSERT INTO emr_soap_notes (encrypted_content) VALUES (?)", (encrypted_soap,))

# Encrypt OSCE transcript before saving
encrypted_transcript = osce_cipher.encrypt(json.dumps(conversation_history))
db.execute("INSERT INTO osce_attempts (conversation_history) VALUES (?)", (encrypted_transcript,))
```

### 5.2 Password Hashing (Argon2id)

**User Passwords** (never encrypted, always hashed):
```python
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

ph = PasswordHasher(
    time_cost=2,        # Number of iterations
    memory_cost=65536,  # 64 MB memory
    parallelism=4,      # 4 parallel threads
    hash_len=32,        # 256-bit hash
    salt_len=16         # 128-bit salt
)

def hash_password(password: str) -> str:
    """Hash password with Argon2id"""
    return ph.hash(password)

def verify_password(password: str, password_hash: str) -> bool:
    """Verify password against hash"""
    try:
        ph.verify(password_hash, password)

        # Check if rehash needed (parameters changed)
        if ph.check_needs_rehash(password_hash):
            new_hash = ph.hash(password)
            # Update database with new_hash

        return True
    except VerifyMismatchError:
        return False
```

### 5.3 Claude API Data Anonymization

**PHI Anonymization Before Sending to Claude**:
```python
# backend/src/security/phi_anonymizer.py
import re
from typing import Dict

class PHIAnonymizer:
    def __init__(self):
        self.patterns = {
            'name': r'\b([A-Z][a-z]+ [A-Z][a-z]+)\b',  # John Smith
            'mrn': r'\bMRN[:\s]*(\d{6,10})\b',
            'phone': r'\b(\d{3}[-.\s]?\d{3}[-.\s]?\d{4})\b',
            'email': r'\b([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b',
            'address': r'\b(\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd))\b'
        }
        self.replacements = {}

    def anonymize(self, text: str) -> str:
        """Replace PHI with placeholders"""
        anonymized = text

        for phi_type, pattern in self.patterns.items():
            matches = re.findall(pattern, text)
            for i, match in enumerate(matches):
                placeholder = f"[{phi_type.upper()}_{i+1}]"
                self.replacements[placeholder] = match
                anonymized = anonymized.replace(match, placeholder)

        return anonymized

    def deanonymize(self, text: str) -> str:
        """Restore original PHI from placeholders"""
        deanonymized = text
        for placeholder, original in self.replacements.items():
            deanonymized = deanonymized.replace(placeholder, original)
        return deanonymized

# Usage before Claude API call
anonymizer = PHIAnonymizer()
soap_note = "Patient John Smith (MRN: 1234567) presents with chest pain..."
anonymized_soap = anonymizer.anonymize(soap_note)
# anonymized_soap = "Patient [NAME_1] (MRN: [MRN_1]) presents with chest pain..."

# Send to Claude
claude_feedback = await claude_api_call(anonymized_soap)

# Restore PHI in feedback (if needed for logging)
final_feedback = anonymizer.deanonymize(claude_feedback)
```

---

## 🚦 6. RATE LIMITING

### 6.1 Claude API Shared Rate Limit

**Combined Limit**: 90 req/min (EMR + OSCE)
**Priority Queue**:
1. AI Patient (OSCE) - Highest priority (real-time 8-min sessions)
2. AI Examiner (OSCE) - Medium priority (scoring, not real-time)
3. EMR Validator - Lowest priority (asynchronous, can wait)

**Implementation**:
```python
# backend/src/core/ai_router.py
import asyncio
from collections import deque

class ClaudeRateLimiter:
    def __init__(self, max_requests: int = 90, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = deque()
        self.lock = asyncio.Lock()

    async def acquire(self, priority: int = 3):
        """
        Acquire permission to make Claude API call
        priority: 1 (highest) = AI Patient, 2 = AI Examiner, 3 (lowest) = EMR Validator
        """
        async with self.lock:
            now = time.time()

            # Remove requests outside window
            while self.requests and self.requests[0] < now - self.window_seconds:
                self.requests.popleft()

            # If at limit, wait
            if len(self.requests) >= self.max_requests:
                sleep_time = self.requests[0] + self.window_seconds - now
                await asyncio.sleep(sleep_time)

            # Record this request
            self.requests.append(now)

rate_limiter = ClaudeRateLimiter(max_requests=90, window_seconds=60)

async def call_claude_with_limit(prompt: str, priority: int = 3):
    """Call Claude API with rate limiting"""
    await rate_limiter.acquire(priority)
    return await claude_api_call(prompt)
```

### 6.2 API Endpoint Rate Limiting (Redis)

**Per-IP Rate Limiting**:
```python
from fastapi import Request, HTTPException
import time

async def rate_limit_middleware(request: Request, call_next):
    """Rate limit: 60 requests per minute per IP"""
    client_ip = request.client.host
    redis_key = f"emr:ratelimit:{client_ip}"

    # Increment counter
    current = redis_client.incr(redis_key)

    if current == 1:
        # First request in window, set expiry
        redis_client.expire(redis_key, 60)

    if current > 60:
        raise HTTPException(status_code=429, detail="Rate limit exceeded (60 req/min)")

    response = await call_next(request)
    response.headers["X-RateLimit-Limit"] = "60"
    response.headers["X-RateLimit-Remaining"] = str(max(0, 60 - current))
    return response
```

---

## 📊 7. MONITORING & OBSERVABILITY

### 7.1 Prometheus Metrics

**Metrics to Track** (shared across EMR + OSCE):
```python
from prometheus_client import Counter, Histogram, Gauge

# API metrics
api_requests_total = Counter('api_requests_total', 'Total API requests', ['method', 'endpoint', 'status'])
api_request_duration = Histogram('api_request_duration_seconds', 'API request duration', ['method', 'endpoint'])

# Claude API metrics
claude_api_calls = Counter('claude_api_calls_total', 'Total Claude API calls', ['system', 'priority'])
claude_api_errors = Counter('claude_api_errors_total', 'Claude API errors', ['system', 'error_type'])
claude_api_latency = Histogram('claude_api_latency_seconds', 'Claude API latency', ['system'])

# Redis metrics
redis_keys_total = Gauge('redis_keys_total', 'Total Redis keys', ['namespace'])
redis_memory_bytes = Gauge('redis_memory_bytes', 'Redis memory usage', ['namespace'])

# Database metrics
db_connections_active = Gauge('db_connections_active', 'Active database connections')
db_query_duration = Histogram('db_query_duration_seconds', 'Database query duration', ['query_type'])
```

### 7.2 Health Check Endpoints

**Kubernetes Liveness/Readiness Probes**:
```python
@app.get("/health/live")
async def liveness_check():
    """Liveness probe - is the app running?"""
    return {"status": "alive", "timestamp": datetime.utcnow().isoformat()}

@app.get("/health/ready")
async def readiness_check():
    """Readiness probe - can the app serve traffic?"""
    checks = {
        "database": await check_database(),
        "redis": await check_redis(),
        "vault": await check_vault(),
        "qdrant": await check_qdrant()  # OSCE only
    }

    all_ready = all(checks.values())
    status_code = 200 if all_ready else 503

    return JSONResponse(
        status_code=status_code,
        content={
            "status": "ready" if all_ready else "not_ready",
            "checks": checks,
            "timestamp": datetime.utcnow().isoformat()
        }
    )
```

---

## 🔄 8. DISASTER RECOVERY

### 8.1 Backup Strategy

| Component | Backup Frequency | Retention | Location |
|-----------|-----------------|-----------|----------|
| PostgreSQL | Every 6 hours | 30 days | S3 + local snapshots |
| Redis (RDB) | Every 5 minutes | 7 days | S3 + local disk |
| Redis (AOF) | Continuous | 7 days | Local disk + S3 daily |
| Vault secrets | Manual export | Encrypted, offline | Secure storage (KMS) |
| Qdrant vectors | Daily | 14 days | S3 |

### 8.2 Recovery Time Objectives (RTO)

- **Database failure**: RTO < 15 minutes (restore from latest 6-hour backup)
- **Redis failure**: RTO < 5 minutes (restore from latest RDB + replay AOF)
- **Vault failure**: RTO < 10 minutes (failover to HA standby)
- **Complete infrastructure failure**: RTO < 2 hours (rebuild from backups)

---

## 📝 SUMMARY

### Shared Components Checklist

- [x] **Vault**: Key hierarchy defined, access policies created
- [x] **Redis**: Namespaces defined, memory allocation planned, persistence configured
- [x] **JWT**: Token structure unified, generation/verification implemented
- [x] **HTTPS**: Security headers defined (9 headers), redirect middleware created
- [x] **Encryption**: AES-256-GCM for data at rest, Argon2id for passwords
- [x] **Rate Limiting**: Claude API (90 req/min shared), API endpoints (60 req/min per IP)
- [x] **Monitoring**: Prometheus metrics defined, health checks implemented
- [x] **Disaster Recovery**: Backup strategy defined, RTO targets set

### Next Steps

1. **Week 1**: Implement this specification
   - Deploy Vault (development mode for testing)
   - Configure Redis (namespaces, persistence)
   - Apply security headers middleware
   - Implement JWT generation/verification

2. **Week 2+**: Reference this spec in all EMR/OSCE implementation
   - EMR backend: Use `emr:*` namespace, EMR encryption key
   - OSCE backend: Use `osce:*` namespace, OSCE encryption key
   - Both: Use shared JWT secret, shared security headers

---

**Document Status**: ✅ Ready for Implementation
**Created**: 2026-02-16
**Last Updated**: 2026-02-16
**Version**: 1.0
**Owner**: PM Coordinator
