# AMC Clinical Exam Simulation - Security Implementation Checklist

**Quick Reference for Developers**  
**Last Updated:** 2026-02-06

---

## Pre-Deployment Blockers (MUST COMPLETE)

### CRITICAL Issues (Do NOT deploy without fixing):

- [ ] **Remove hardcoded secret key**
  - File: `backend/src/config.py:21`
  - Action: Remove `secret_key: str = "your-secret-key-change-in-production"`
  - Fix: Make SECRET_KEY required from environment, fail fast if missing

- [ ] **Configure Redis AUTH**
  - File: `docker-compose.yml`
  - Action: Add `command: redis-server --requirepass ${REDIS_PASSWORD}`
  - Fix: Mount Redis password from Docker secret

- [ ] **Remove database credentials from default**
  - File: `backend/src/config.py:18`
  - Action: Remove `emr_user:emr_pass` from default connection string
  - Fix: Require DATABASE_URL from environment in production

### HIGH Priority (Complete before deployment):

- [ ] **Implement WebSocket authentication**
  - Validate JWT token on WebSocket connection
  - Tie session_id to user_id in Redis
  - Test unauthorized WebSocket access (should reject)

- [ ] **Implement rate limiting**
  - Install `slowapi` package
  - Add rate limits to all endpoints:
    - Login: 5/min
    - OSCE creation: 10/min
    - General API: 60/min
  - Test with automated requests

- [ ] **Add session ID validation**
  - Validate session_id is UUID format
  - Prevent Redis injection attacks
  - Test with malicious input

- [ ] **Add WebSocket message validation**
  - Limit message length (2000 chars)
  - Limit messages per session (100 max)
  - Implement per-connection rate limiting (5 msg/sec)

- [ ] **Fix testing auth bypass**
  - Only allow in development/test environments
  - Add environment check
  - Log prominent warning when enabled

---

## Week 1: Authentication & Authorization

### Tasks:

- [ ] Generate strong SECRET_KEY: `openssl rand -hex 32`
- [ ] Store SECRET_KEY in Docker secret: `/run/secrets/jwt_secret`
- [ ] Update config.py to fail fast if SECRET_KEY missing
- [ ] Test JWT token generation and validation
- [ ] Test account lockout (5 failed attempts)
- [ ] Test token expiration (30 min access, 7 day refresh)
- [ ] Document secret key rotation procedure

### Testing:

```bash
# Test missing SECRET_KEY (should fail)
unset SECRET_KEY && python -m backend.src.main

# Test invalid JWT token
curl -H "Authorization: Bearer invalid-token" http://localhost:8000/api/v1/users/me

# Test expired token
# (create token with 1-second expiry, wait 2 seconds, use it)

# Test account lockout
for i in {1..6}; do
  curl -X POST http://localhost:8000/api/v1/auth/login \
    -d '{"email":"test@example.com","password":"wrong"}'
done
```

---

## Week 2: Data Encryption

### Tasks:

- [ ] Install `sqlalchemy-utils[cryptography]`
- [ ] Generate encryption key: `openssl rand -hex 32`
- [ ] Store in Docker secret: `/run/secrets/db_encryption_key`
- [ ] Implement encrypted columns for User.email and User.full_name
- [ ] Test encrypted column read/write
- [ ] Create migration to encrypt existing data
- [ ] Implement conversation history encryption (AES-256-GCM)
- [ ] Test conversation encryption/decryption
- [ ] Update deployment docs with encryption setup

### Implementation:

```python
# Encrypted columns (User model)
from sqlalchemy_utils import EncryptedType
from sqlalchemy_utils.types.encrypted.encrypted_type import AesEngine

ENCRYPTION_KEY = os.getenv("DB_ENCRYPTION_KEY")

class User(Base):
    email = Column(
        EncryptedType(String(255), ENCRYPTION_KEY, AesEngine, 'pkcs5'),
        unique=True, index=True, nullable=False
    )
```

```python
# Conversation encryption
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

CONVERSATION_KEY = os.getenv("CONVERSATION_ENCRYPTION_KEY")
aesgcm = AESGCM(bytes.fromhex(CONVERSATION_KEY))

def encrypt_conversation(conversation: dict) -> dict:
    plaintext = json.dumps(conversation).encode('utf-8')
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, plaintext, None)
    return {"encrypted_data": ciphertext.hex(), "nonce": nonce.hex()}
```

### Testing:

```bash
# Test encrypted field storage
python -c "
from backend.src.db.models import User
user = User(email='test@example.com', full_name='Test User')
# Verify database contains encrypted bytes, not plaintext
"

# Test conversation encryption
python -c "
from backend.src.encryption import encrypt_conversation, decrypt_conversation
original = {'messages': [{'role': 'student', 'content': 'Hello'}]}
encrypted = encrypt_conversation(original)
decrypted = decrypt_conversation(encrypted)
assert original == decrypted
"
```

---

## Week 3: Audit Logging

### Tasks:

- [ ] Create AuditLog model (immutable, partitioned by month)
- [ ] Implement audit logging middleware
- [ ] Log all authenticated requests
- [ ] Log sensitive actions:
  - VIEW_SESSION (user views conversation transcript)
  - EDIT_MCQ (educator edits question)
  - DELETE_USER (admin deletes account)
  - EXPORT_DATA (user requests GDPR export)
- [ ] Implement log retention (365 days)
- [ ] Set up log archival to immutable storage (S3 Glacier)
- [ ] Create admin dashboard to query audit logs

### Implementation:

```python
class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String(100), nullable=False)
    resource_type = Column(String(50), nullable=False)
    resource_id = Column(String(100), nullable=False)
    ip_address = Column(String(45), nullable=False)
    details = Column(JSONB)
```

```python
# Audit logging middleware
@app.middleware("http")
async def audit_log_requests(request: Request, call_next):
    if request.user:  # Authenticated request
        audit_log = AuditLog(
            user_id=request.user.id,
            action=f"{request.method}_{request.url.path}",
            resource_type="api",
            resource_id=str(request.url),
            ip_address=request.client.host
        )
        db.add(audit_log)
        db.commit()
    
    response = await call_next(request)
    return response
```

### Testing:

```bash
# Test audit log creation
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/users/me
# Verify audit log entry created in database

# Test audit log retention
python -c "
from backend.src.db.models import AuditLog
from datetime import datetime, timedelta
old_log = AuditLog(timestamp=datetime.now() - timedelta(days=400))
# Run retention job, verify old_log archived
"
```

---

## Week 4: Data Retention & Privacy

### Tasks:

- [ ] Document data retention policy:
  - Active users: Indefinite
  - Inactive users (2 years no login): Archive or delete
  - Audit logs: 7 years
  - Session transcripts: 1 year
- [ ] Implement automated data deletion for inactive accounts
- [ ] Create background task for session archival
- [ ] Implement user notification before deletion (30-day notice)
- [ ] Create privacy policy page (frontend)
- [ ] Test GDPR data export (user can download all their data)
- [ ] Test GDPR data deletion (user can request account deletion)

### Implementation:

```python
# Background task for inactive account cleanup
from celery import Celery

@celery.task
def cleanup_inactive_accounts():
    two_years_ago = datetime.now() - timedelta(days=730)
    inactive_users = db.query(User).filter(
        User.last_login_at < two_years_ago,
        User.deleted_at == None
    ).all()
    
    for user in inactive_users:
        # Send notification email
        send_email(user.email, "Account deletion notice", 
                   "Your account will be deleted in 30 days")
        
        # Schedule deletion
        schedule_deletion(user.id, days=30)
```

### Testing:

```bash
# Test data export
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/users/me/export \
  -o my_data.json

# Verify JSON contains all user data

# Test data deletion
curl -X DELETE -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/users/me

# Verify user.deleted_at set, data not accessible
```

---

## Security Testing Matrix

### Authentication Tests:

| Test Case | Expected Result | Status |
|-----------|----------------|--------|
| Login with valid credentials | 200 OK, JWT tokens returned | [ ] |
| Login with invalid password | 401 Unauthorized | [ ] |
| Login after 5 failed attempts | 403 Forbidden (account locked) | [ ] |
| Access protected route without token | 401 Unauthorized | [ ] |
| Access protected route with expired token | 401 Unauthorized | [ ] |
| Access protected route with invalid token | 401 Unauthorized | [ ] |
| Refresh token with valid refresh token | 200 OK, new access token | [ ] |
| Refresh token with expired refresh token | 401 Unauthorized | [ ] |

### Authorization Tests:

| Test Case | Expected Result | Status |
|-----------|----------------|--------|
| Student accesses student endpoint | 200 OK | [ ] |
| Student accesses admin endpoint | 403 Forbidden | [ ] |
| Educator accesses educator endpoint | 200 OK | [ ] |
| Educator accesses admin endpoint | 403 Forbidden | [ ] |
| Admin accesses all endpoints | 200 OK | [ ] |

### WebSocket Tests:

| Test Case | Expected Result | Status |
|-----------|----------------|--------|
| Connect with valid JWT token | Connection accepted | [ ] |
| Connect with invalid JWT token | Connection rejected (1008) | [ ] |
| Connect with valid token but wrong session | Connection rejected (1008) | [ ] |
| Send message longer than 2000 chars | Error message returned | [ ] |
| Send 6 messages in 1 second | 6th message rate limited | [ ] |
| Send 101st message in session | Error message returned | [ ] |

### Encryption Tests:

| Test Case | Expected Result | Status |
|-----------|----------------|--------|
| Store user with email "test@example.com" | Database contains encrypted bytes | [ ] |
| Retrieve user by email | Decrypts to "test@example.com" | [ ] |
| Store conversation history | Database contains encrypted JSON | [ ] |
| Retrieve conversation | Decrypts to original JSON | [ ] |
| Backup database | Backup contains encrypted data | [ ] |

### Rate Limiting Tests:

| Test Case | Expected Result | Status |
|-----------|----------------|--------|
| 6 login attempts in 1 minute | 6th request = 429 Too Many Requests | [ ] |
| 11 OSCE creations in 1 minute | 11th request = 429 | [ ] |
| 61 API calls in 1 minute | 61st request = 429 | [ ] |

### Audit Logging Tests:

| Test Case | Expected Result | Status |
|-----------|----------------|--------|
| User views session transcript | Audit log created with VIEW_SESSION | [ ] |
| User edits MCQ | Audit log created with EDIT_MCQ | [ ] |
| User deletes account | Audit log created with DELETE_USER | [ ] |
| Query audit logs older than 365 days | Returns archived logs | [ ] |

---

## Security Scanning Commands

### Run before every commit:

```bash
# Check for hardcoded secrets
grep -r "password.*=" backend/src --include="*.py" | grep -v "password_hash\|def \|class "
grep -r "secret.*=" backend/src --include="*.py" | grep -v "def get_secret\|SECRET_KEY.*os"
grep -r "api_key.*=" backend/src --include="*.py" | grep -v "def \|class \|os.getenv"

# Check for SQL injection vulnerabilities
grep -r "execute.*%" backend/src --include="*.py"
grep -r "execute.*\+" backend/src --include="*.py"
grep -r "execute.*f\"" backend/src --include="*.py"

# Check for missing input validation
grep -r "@router" backend/src --include="*.py" | xargs grep -L "Depends\|BaseModel"

# Run static analysis
bandit -r backend/src -f json -o security-report.json

# Run dependency vulnerability scan
safety check --json
```

---

## Deployment Security Checklist

### Before deploying to production:

- [ ] All environment variables set (no defaults used)
- [ ] SECRET_KEY generated with `openssl rand -hex 32`
- [ ] DB_ENCRYPTION_KEY generated and stored in Docker secret
- [ ] CONVERSATION_ENCRYPTION_KEY generated and stored in Docker secret
- [ ] Redis AUTH enabled and password set
- [ ] PostgreSQL password changed from default
- [ ] TLS 1.3 enabled in Nginx
- [ ] HTTPS redirect enabled
- [ ] Rate limiting enabled
- [ ] Audit logging enabled
- [ ] CORS origins restricted to production domains
- [ ] Debug mode disabled (DEBUG=False)
- [ ] Testing auth bypass disabled (DISABLE_AUTH_FOR_TESTING=false)
- [ ] All dependencies up to date (no known vulnerabilities)
- [ ] Firewall configured (only ports 80, 443 exposed)
- [ ] Database backups configured
- [ ] Monitoring and alerting set up

---

## Incident Response Plan

### If security breach detected:

1. **Immediate Actions (within 1 hour):**
   - Rotate all secrets (JWT, DB encryption, Redis password)
   - Force logout all users (invalidate all tokens)
   - Take affected systems offline if necessary
   - Preserve logs for forensic analysis

2. **Investigation (within 24 hours):**
   - Review audit logs for unauthorized access
   - Identify compromised accounts
   - Determine scope of data breach
   - Notify affected users

3. **Remediation (within 1 week):**
   - Patch vulnerability
   - Deploy security updates
   - Enhanced monitoring for similar attacks
   - Post-incident review and documentation

4. **Compliance (as required):**
   - Notify authorities if required by GDPR/Privacy Act
   - Document breach in security incident log
   - Update security procedures to prevent recurrence

---

**Document Version:** 1.0  
**Last Updated:** 2026-02-06  
**Next Review:** After Phase 1 completion (Week 1)
