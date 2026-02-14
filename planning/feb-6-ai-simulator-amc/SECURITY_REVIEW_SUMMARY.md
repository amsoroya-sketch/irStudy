# AMC Clinical Exam Simulation - Security Review Summary

**Review Date:** 2026-02-06  
**Status:** ARCHITECTURE REVIEW (Pre-Implementation)  
**Overall Risk:** MEDIUM (3 CRITICAL issues found)

---

## Executive Summary

The AMC Clinical Exam Simulation architecture demonstrates strong security foundations with JWT authentication, bcrypt password hashing, and comprehensive input validation. However, **3 critical security gaps must be resolved before deployment**.

### Risk Rating: MEDIUM → LOW (after fixes)

**Critical Issues (BLOCKING DEPLOYMENT):**
1. Hardcoded default secret key in `config.py`
2. Redis AUTH not configured in `docker-compose.yml`
3. Database credentials in default connection string

**Timeline to Production-Ready:** 2-3 days (18 hours of security fixes)

---

## Critical Issues (Must Fix Before Deployment)

### 1. Hardcoded Secret Key - CRITICAL

**File:** `/home/dev/Development/irStudy/backend/src/config.py:21`

**Problem:**
```python
secret_key: str = "your-secret-key-change-in-production"
```

**Impact:** JWT token forgery, complete authentication bypass

**Fix:**
```python
# Remove default, fail fast if missing
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable required")
```

**Effort:** 1 hour  
**Priority:** P0 (BLOCKING)

---

### 2. Redis AUTH Not Configured - CRITICAL

**File:** Architecture documentation shows Redis with no authentication

**Problem:**
```yaml
redis:
  image: redis:7-alpine
  # NO AUTH CONFIGURED - anyone can read session data!
```

**Impact:** Session hijacking, conversation history exposure

**Fix:**
```yaml
redis:
  image: redis:7-alpine
  command: redis-server --requirepass ${REDIS_PASSWORD}
  secrets:
    - redis_password
```

**Effort:** 2 hours  
**Priority:** P0 (BLOCKING)

---

### 3. Database Credentials Hardcoded - HIGH

**File:** `/home/dev/Development/irStudy/backend/src/config.py:18`

**Problem:**
```python
database_url: str = "postgresql://emr_user:emr_pass@localhost:5432/emr_practice"
```

**Impact:** Default credentials discoverable by attackers

**Fix:**
```python
# No credentials in default
database_url: str = os.getenv(
    "DATABASE_URL", 
    "postgresql://localhost:5432/emr_practice"
)
```

**Effort:** 1 hour  
**Priority:** P0 (BLOCKING)

---

## High Priority Issues (Complete Week 1)

### 4. WebSocket Authentication Underspecified - HIGH

**Problem:** Architecture mentions authentication but doesn't specify HOW

**Missing:**
- How is JWT validated on WebSocket connection?
- How is session_id tied to user_id?
- What happens if JWT expires during OSCE?

**Fix:** Implement JWT validation in WebSocket handler:

```python
@router.websocket("/ws/osce/{session_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    session_id: str,
    token: str = Query(...),  # JWT in query param
    db: Session = Depends(get_db)
):
    # Validate JWT
    payload = verify_access_token(token)
    if not payload:
        await websocket.close(code=1008, reason="Invalid token")
        return
    
    # Verify session belongs to user
    session = await redis.hgetall(f"session:{session_id}")
    if session["user_id"] != str(payload["user_id"]):
        await websocket.close(code=1008, reason="Unauthorized")
        return
    
    await websocket.accept()
```

**Effort:** 4 hours  
**Priority:** P1 (HIGH)

---

### 5. Rate Limiting Not Implemented - HIGH

**Problem:** Architecture specifies rate limits but no implementation found

**Missing:**
- Login: 5/min (brute force protection)
- OSCE creation: 10/min (AI cost control)
- General API: 60/min

**Fix:** Install `slowapi` and apply decorators:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/auth/login")
@limiter.limit("5/minute")
async def login(request: Request, credentials: UserLogin):
    pass
```

**Effort:** 4 hours  
**Priority:** P1 (HIGH)

---

### 6. Session ID Validation Missing - HIGH

**Problem:** No validation of session_id format (Redis injection risk)

**Fix:**

```python
import uuid

def validate_session_id(session_id: str) -> bool:
    try:
        uuid.UUID(session_id)
        return True
    except ValueError:
        return False
```

**Effort:** 2 hours  
**Priority:** P1 (HIGH)

---

## Medium Priority Issues (Complete Week 2)

### 7. Encrypted Columns Not Implemented - MEDIUM

**Problem:** Architecture states "encrypted columns for sensitive data" but User model has plaintext email and full_name

**Fix:** Use `sqlalchemy-utils` EncryptedType:

```python
from sqlalchemy_utils import EncryptedType
from sqlalchemy_utils.types.encrypted.encrypted_type import AesEngine

ENCRYPTION_KEY = os.getenv("DB_ENCRYPTION_KEY")

class User(Base):
    email = Column(
        EncryptedType(String(255), ENCRYPTION_KEY, AesEngine, 'pkcs5'),
        unique=True, nullable=False
    )
```

**Effort:** 6 hours  
**Priority:** P2 (MEDIUM)

---

### 8. Conversation Encryption Missing - MEDIUM

**Problem:** Session transcripts stored as plaintext JSONB

**Fix:** Encrypt with AES-256-GCM before storage:

```python
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def encrypt_conversation(conversation: dict) -> dict:
    plaintext = json.dumps(conversation).encode('utf-8')
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, plaintext, None)
    return {
        "encrypted_data": ciphertext.hex(),
        "nonce": nonce.hex()
    }
```

**Effort:** 4 hours  
**Priority:** P2 (MEDIUM)

---

### 9. Audit Logging Incomplete - MEDIUM

**Problem:** Request logging exists but no logging of data access/modifications

**Fix:** Create AuditLog model and log sensitive actions:

```python
class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, server_default=func.now())
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String(100))  # "VIEW_SESSION", "DELETE_USER"
    resource_type = Column(String(50))
    resource_id = Column(String(100))
```

**Effort:** 8 hours  
**Priority:** P2 (MEDIUM)

---

## Compliance Assessment

### GDPR / Privacy Act: COMPLIANT

- Right to deletion: Implemented (soft delete)
- Right to access: Implemented (/api/v1/users/me)
- Data minimization: Only necessary data collected
- No real patient data: Fictional personas only

### Australian Medical Compliance: COMPLIANT

- QA-001 validator enforces Australian terminology
- Emergency number: 000 (not 911)
- Drug names: Australian (paracetamol not acetaminophen)
- Guidelines: eTG, AMH, AHPRA

### HIPAA Compliance: NEEDS WORK

- Encryption at rest: NOT IMPLEMENTED (Week 2 priority)
- Audit logging: PARTIAL (Week 3 priority)
- Access controls: IMPLEMENTED

---

## Security Testing Summary

### Tests Required Before Deployment:

**Authentication (10 tests):**
- [ ] Login with valid credentials
- [ ] Login with invalid password
- [ ] Account lockout after 5 failed attempts
- [ ] Access protected route without token
- [ ] Access protected route with expired token
- [ ] Access protected route with invalid token
- [ ] Refresh token with valid refresh token
- [ ] Refresh token with expired refresh token
- [ ] WebSocket connection with invalid JWT
- [ ] WebSocket connection with wrong session_id

**Authorization (5 tests):**
- [ ] Student accesses student endpoint (200 OK)
- [ ] Student accesses admin endpoint (403 Forbidden)
- [ ] Educator accesses educator endpoint (200 OK)
- [ ] Educator accesses admin endpoint (403 Forbidden)
- [ ] Admin accesses all endpoints (200 OK)

**Rate Limiting (3 tests):**
- [ ] 6 login attempts in 1 minute (6th = 429)
- [ ] 11 OSCE creations in 1 minute (11th = 429)
- [ ] 61 API calls in 1 minute (61st = 429)

**Encryption (4 tests):**
- [ ] Email stored as encrypted bytes in database
- [ ] Email retrieved and decrypted correctly
- [ ] Conversation stored as encrypted JSON
- [ ] Conversation retrieved and decrypted correctly

---

## Remediation Timeline

### Phase 1: Pre-Deployment (Days 1-3) - BLOCKING

| Task | Effort | Status |
|------|--------|--------|
| Remove hardcoded secret key | 1 hour | [ ] |
| Configure Redis AUTH | 2 hours | [ ] |
| Remove database credentials | 1 hour | [ ] |
| Implement WebSocket auth | 4 hours | [ ] |
| Implement rate limiting | 4 hours | [ ] |
| Add session ID validation | 2 hours | [ ] |
| Add WebSocket message validation | 3 hours | [ ] |
| Fix testing auth bypass check | 1 hour | [ ] |

**Total: 18 hours (~2-3 days)**

---

### Phase 2: Data Security (Days 4-7)

| Task | Effort | Status |
|------|--------|--------|
| Implement encrypted columns | 6 hours | [ ] |
| Implement conversation encryption | 4 hours | [ ] |
| Generate encryption keys | 2 hours | [ ] |
| Create migration for existing data | 4 hours | [ ] |
| Test QA-001 validator | 4 hours | [ ] |
| Update deployment docs | 2 hours | [ ] |

**Total: 22 hours (~3-4 days)**

---

### Phase 3: Audit & Compliance (Days 8-11)

| Task | Effort | Status |
|------|--------|--------|
| Create AuditLog model | 4 hours | [ ] |
| Implement audit middleware | 4 hours | [ ] |
| Log sensitive actions | 4 hours | [ ] |
| Implement log retention | 3 hours | [ ] |
| Set up log archival | 4 hours | [ ] |

**Total: 19 hours (~3 days)**

---

## Quick Security Scan Commands

### Run before every commit:

```bash
# Check for hardcoded secrets
grep -rn "password.*=" backend/src --include="*.py" | grep -v "def \|class \|password_hash"
grep -rn "secret.*=" backend/src --include="*.py" | grep -v "def \|os.getenv"

# Check for SQL injection
grep -rn "execute.*%" backend/src --include="*.py"
grep -rn "execute.*f\"" backend/src --include="*.py"

# Run static analysis
bandit -r backend/src

# Check dependencies
safety check
```

---

## Decision Matrix

### Should we deploy now?

**NO - 3 CRITICAL ISSUES BLOCKING**

### When can we deploy?

**After Phase 1 completion (2-3 days)**

### What's the minimum viable security?

**Phase 1 (all CRITICAL + HIGH issues fixed)**

### When are we fully compliant?

**After Phase 3 completion (~2 weeks total)**

---

## Recommendations

### Immediate Actions (Today):

1. Fix hardcoded secret key (1 hour)
2. Configure Redis AUTH (2 hours)
3. Remove database credentials (1 hour)

**Total: 4 hours to unblock deployment preparation**

### Week 1 Actions:

1. Complete all Phase 1 tasks (18 hours total)
2. Run all authentication tests (10 tests)
3. Run all authorization tests (5 tests)
4. Deploy to staging environment

### Week 2 Actions:

1. Complete all Phase 2 tasks (22 hours total)
2. Run all encryption tests (4 tests)
3. Test QA-001 Australian compliance validator
4. Deploy to production

---

## Contact Information

**Security Lead:** (to be assigned)  
**Compliance Officer:** (to be assigned)  
**Incident Response:** security@irstudy.com (to be set up)

---

## Document Control

**Version:** 1.0  
**Created:** 2026-02-06  
**Last Updated:** 2026-02-06  
**Next Review:** After Phase 1 completion  
**Classification:** Internal Use Only

---

## Related Documents

- [Full Security Assessment](SECURITY_COMPLIANCE_ASSESSMENT.md) - Detailed findings
- [Security Checklist](SECURITY_CHECKLIST.md) - Implementation tasks
- [System Architecture](01_SYSTEM_ARCHITECTURE.md) - Architecture overview
- [Project Constraints](../../constraints/03-security-configuration.md) - Security constraints
