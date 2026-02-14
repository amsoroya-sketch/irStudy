# AMC Clinical Exam Simulation - Security & Compliance Assessment

**Assessment Date:** 2026-02-06  
**Assessor:** Security & HIPAA Compliance Expert  
**Architecture Version:** 1.0  
**Status:** ARCHITECTURE REVIEW (Pre-Implementation)

---

## Executive Summary

### Overall Security Rating: MEDIUM RISK

**Rating Breakdown:**
- Authentication & Authorization: LOW RISK
- Data Security: MEDIUM RISK (3 critical issues)
- Medical Data Compliance: LOW RISK
- Australian Medical Compliance: LOW RISK
- Attack Surface: MEDIUM RISK (2 high-priority issues)

### Compliance Assessment: NEEDS WORK

**Key Findings:**
- No real patient data (fictional personas): COMPLIANT
- GDPR/Privacy Act right to deletion: COMPLIANT
- Audit logging: PARTIALLY COMPLIANT (gaps identified)
- Encryption: NEEDS WORK (TLS configured, at-rest encryption incomplete)

### Critical Issues Requiring Immediate Action: 3

1. **CRITICAL:** Hardcoded default secret key in production config
2. **CRITICAL:** Incomplete Redis AUTH configuration in architecture
3. **HIGH:** Missing WebSocket authentication specification

---

## 1. Authentication & Authorization Assessment

### Overall Rating: LOW RISK

### Strengths:

**JWT Token Implementation:**
- Bcrypt password hashing (work factor 12) - SECURE
- HS256 algorithm for JWT signing - ACCEPTABLE
- Secret key loaded from environment/Docker secret - GOOD PRACTICE
- Token expiration enforced (30 min access, 7 day refresh) - COMPLIANT
- Token type validation (access vs. refresh) - SECURE

**Account Security:**
- Account lockout after 5 failed attempts (30 min) - COMPLIANT
- Failed login attempt tracking - IMPLEMENTED
- Email verification required - IMPLEMENTED
- Active account checks - IMPLEMENTED

**Role-Based Access Control:**
- Three roles defined (Student, Educator, Admin) - SUFFICIENT
- Permission checks via FastAPI dependencies - SECURE
- Role validation in JWT payload - IMPLEMENTED

### Issues Identified:

#### CRITICAL: Hardcoded Default Secret Key

**Location:** `/home/dev/Development/irStudy/backend/src/config.py:21`

```python
# JWT
secret_key: str = "your-secret-key-change-in-production"
```

**Risk:** If deployed to production without overriding via environment variable, this allows JWT token forgery.

**Impact:** Complete authentication bypass, unauthorized access to all user accounts.

**Remediation:**
```python
# CORRECT PATTERN (from auth/security.py):
def get_secret_key() -> str:
    secret_key = os.getenv("SECRET_KEY")
    if not secret_key:
        raise ValueError("JWT secret key not found. Set SECRET_KEY env var")
    return secret_key

SECRET_KEY = get_secret_key()
```

**Action Required:**
1. Remove hardcoded default from `config.py`
2. Make `SECRET_KEY` a required environment variable
3. Fail fast on startup if not provided
4. Update deployment docs to enforce secret generation

**Timeline:** BEFORE DEPLOYMENT (blocking issue)

---

#### HIGH: Database Connection String with Hardcoded Credentials

**Location:** `/home/dev/Development/irStudy/backend/src/config.py:18`

```python
database_url: str = "postgresql://emr_user:emr_pass@localhost:5432/emr_practice"
```

**Risk:** Default credentials in codebase, easily discovered by attackers.

**Remediation:**
```python
database_url: str = os.getenv(
    "DATABASE_URL", 
    "postgresql://localhost:5432/emr_practice"  # No credentials in default
)
```

**Action Required:**
1. Remove credentials from default connection string
2. Require `DATABASE_URL` from environment in production
3. Add validation in `lifespan` startup to check DB connectivity

**Timeline:** BEFORE DEPLOYMENT

---

#### MEDIUM: Testing Auth Bypass Flag

**Location:** `/home/dev/Development/irStudy/backend/src/auth/dependencies.py:29`

```python
DISABLE_AUTH_FOR_TESTING = os.getenv("DISABLE_AUTH_FOR_TESTING", "false").lower() == "true"
```

**Risk:** If accidentally enabled in production, bypasses all authentication.

**Remediation:**
```python
# Only allow bypass in development/test environments
ENV = os.getenv("ENV", "production")
DISABLE_AUTH_FOR_TESTING = (
    ENV in ["development", "test"] and 
    os.getenv("DISABLE_AUTH_FOR_TESTING", "false").lower() == "true"
)

if DISABLE_AUTH_FOR_TESTING:
    logger.warning("⚠️  AUTH BYPASS ENABLED - DEVELOPMENT/TEST ONLY!")
```

**Action Required:**
1. Add environment check (only allow in dev/test)
2. Log prominent warning when enabled
3. Add startup check to fail if enabled in production

**Timeline:** WEEK 1 (before testing)

---

### WebSocket Authentication Specification: INCOMPLETE

**Architecture Documentation:**
- Section 8.1 mentions "WebSocket connection requires valid session_id"
- Section 8.1 mentions "session_id validated against Redis"
- NO specification for how session_id is obtained securely

**Missing Details:**
1. How is initial WebSocket connection authenticated? (JWT token in query param? Header?)
2. How is session_id generated? (server-side on POST /api/osce/start?)
3. Is session_id tied to user_id to prevent session hijacking?
4. What happens if JWT expires during an 8-minute OSCE session?

**Recommended Specification:**

```python
# WebSocket authentication flow:
# 1. Client calls POST /api/osce/start with JWT in Authorization header
# 2. Server validates JWT, creates session, stores in Redis with user_id
# 3. Server returns session_id
# 4. Client connects to WebSocket with session_id in query param
# 5. Server validates session_id exists in Redis AND user_id matches JWT

@router.websocket("/ws/osce/{session_id}")
async def websocket_endpoint(
    websocket: WebSocket, 
    session_id: str,
    token: str = Query(...),  # JWT token as query param
    db: Session = Depends(get_db)
):
    # Validate JWT token
    payload = verify_access_token(token)
    if not payload:
        await websocket.close(code=1008, reason="Invalid token")
        return
    
    user_id = payload["user_id"]
    
    # Validate session belongs to user
    session = await redis.hgetall(f"session:{session_id}")
    if not session or session["user_id"] != str(user_id):
        await websocket.close(code=1008, reason="Session not found or unauthorized")
        return
    
    await websocket.accept()
    # ... handle messages
```

**Action Required:**
1. Document WebSocket authentication flow in API specification
2. Implement JWT validation on WebSocket connection
3. Tie session_id to user_id in Redis
4. Add test cases for unauthorized WebSocket access attempts

**Timeline:** WEEK 1 (before WebSocket implementation)

---

## 2. Data Security Assessment

### Overall Rating: MEDIUM RISK

### Encryption Strategy:

**In Transit:**
- TLS 1.3 specified in architecture - COMPLIANT
- WSS (WebSocket Secure) mentioned - GOOD PRACTICE
- HTTPS redirect in production (main.py) - IMPLEMENTED

**At Rest:**
- PostgreSQL encrypted columns mentioned but NOT IMPLEMENTED
- Redis AUTH password mentioned but NOT CONFIGURED in architecture
- Session transcripts encryption mentioned but NO CODE

**Ratings:**
- In-transit encryption: LOW RISK (properly specified)
- At-rest encryption: HIGH RISK (not implemented)

---

#### CRITICAL: Redis Security Not Configured

**Architecture Documentation:**
- Section 8.2 states "Redis: AUTH password for Redis connections"
- `.env.template` line 49 states "REDIS_PASSWORD loaded from Docker secret"
- `docker-compose.yml` in ARCHITECTURE_SUMMARY.md shows NO Redis password configuration

**Missing Configuration:**

```yaml
# CURRENT (from ARCHITECTURE_SUMMARY.md):
redis:
  image: redis:7-alpine
  ports:
    - "6379:6379"
  volumes:
    - redis_data:/data
  # NO AUTH CONFIGURED!
```

**CORRECT Configuration:**

```yaml
redis:
  image: redis:7-alpine
  command: redis-server --requirepass ${REDIS_PASSWORD}
  ports:
    - "6379:6379"
  volumes:
    - redis_data:/data
  secrets:
    - redis_password
  environment:
    - REDIS_PASSWORD_FILE=/run/secrets/redis_password
```

**Impact:** 
- Session state accessible without authentication
- Conversation history readable by unauthorized parties
- Session hijacking via direct Redis access

**Action Required:**
1. Add Redis AUTH to docker-compose.yml
2. Update application code to use REDIS_PASSWORD
3. Test Redis connectivity with AUTH enabled
4. Document in deployment guide

**Timeline:** BEFORE DEPLOYMENT (blocking issue)

---

#### HIGH: PostgreSQL Encrypted Columns Not Implemented

**Architecture Documentation:**
- Section 8.2 states "PostgreSQL encrypted columns for sensitive data"
- Database models show PHI fields (email, full_name) with NO encryption

**Current Implementation (db/models.py):**

```python
class User(Base):
    # Profile (PHI - should be encrypted at application layer)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    # NO ENCRYPTION IMPLEMENTED
```

**Risk:**
- If database backup is compromised, PII is exposed in plaintext
- Does not meet HIPAA "encryption at rest" requirement

**Recommended Implementation:**

```python
from sqlalchemy_utils import EncryptedType
from sqlalchemy_utils.types.encrypted.encrypted_type import AesEngine

ENCRYPTION_KEY = os.getenv("DB_ENCRYPTION_KEY")  # From Docker secret

class User(Base):
    email = Column(
        EncryptedType(String(255), ENCRYPTION_KEY, AesEngine, 'pkcs5'),
        unique=True, index=True, nullable=False
    )
    full_name = Column(
        EncryptedType(String(255), ENCRYPTION_KEY, AesEngine, 'pkcs5'),
        nullable=False
    )
```

**Action Required:**
1. Install `sqlalchemy-utils` with cryptography extras
2. Generate encryption key: `openssl rand -hex 32`
3. Store in Docker secret `/run/secrets/db_encryption_key`
4. Implement encrypted columns for PII fields
5. Create migration to encrypt existing data

**Timeline:** WEEK 2 (before storing real user data)

---

#### MEDIUM: Session Transcript Encryption Missing

**Architecture Documentation:**
- Section 8.2 states "Session Transcripts: Encrypted before storage"
- Database schema shows `conversation_history` as JSONB with NO encryption

**Current Schema:**

```sql
CREATE TABLE osce_sessions (
    conversation_history JSONB,  -- NO ENCRYPTION
    scoring_result JSONB
);
```

**Recommendation:**
- Encrypt full `conversation_history` field before inserting into PostgreSQL
- Use application-layer encryption (AES-256-GCM)
- Store encryption metadata (IV, tag) alongside encrypted data

**Implementation:**

```python
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os
import json

CONVERSATION_ENCRYPTION_KEY = os.getenv("CONVERSATION_ENCRYPTION_KEY")  # 32 bytes
aesgcm = AESGCM(bytes.fromhex(CONVERSATION_ENCRYPTION_KEY))

def encrypt_conversation(conversation: dict) -> dict:
    """Encrypt conversation history before storage"""
    plaintext = json.dumps(conversation).encode('utf-8')
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, plaintext, None)
    
    return {
        "encrypted_data": ciphertext.hex(),
        "nonce": nonce.hex(),
        "algorithm": "AES-256-GCM"
    }

def decrypt_conversation(encrypted: dict) -> dict:
    """Decrypt conversation history on retrieval"""
    ciphertext = bytes.fromhex(encrypted["encrypted_data"])
    nonce = bytes.fromhex(encrypted["nonce"])
    plaintext = aesgcm.decrypt(nonce, ciphertext, None)
    
    return json.loads(plaintext.decode('utf-8'))
```

**Action Required:**
1. Implement conversation encryption functions
2. Generate and store encryption key in Docker secret
3. Encrypt conversations before saving to PostgreSQL
4. Update retrieval logic to decrypt automatically

**Timeline:** WEEK 2 (before storing OSCE sessions)

---

### API Key Management:

**Current Approach:**
- Anthropic API key: Environment variable - GOOD
- ElevenLabs API key: Not yet implemented - N/A
- OpenAI API key: Environment variable - GOOD

**Best Practice Met:**
- No API keys in code - COMPLIANT
- Docker secrets supported - GOOD
- `.env.template` provides guidance - GOOD

**Rating:** LOW RISK

---

## 3. Medical Data Compliance Assessment

### Overall Rating: LOW RISK

### Fictional Patient Data:

**Architecture states:**
- "Patient Personas: All fictional (no real patient data)"
- 200+ fictional profiles planned

**Verification:**
- Database schema shows `patient_personas` table with fictional attributes
- No mechanism to import real patient data
- No PHI fields from real patients

**Rating:** COMPLIANT

---

### GDPR / Privacy Act Compliance:

**Right to Deletion:**
- User model includes `deleted_at` field (soft delete) - IMPLEMENTED
- Architecture mentions "Right to deletion implemented" - DOCUMENTED

**Right to Access:**
- Users can retrieve their own performance data - IMPLEMENTED
- `/api/v1/users/me` endpoint exists - IMPLEMENTED

**Data Minimization:**
- Only collects necessary data (email, name, performance) - COMPLIANT
- No excessive tracking - GOOD

**Rating:** COMPLIANT

---

### Audit Logging:

**Current Implementation:**
- Request logging middleware in `main.py` - IMPLEMENTED
- Logs all API requests with request ID - GOOD
- Database has `created_at`, `updated_at` timestamps - IMPLEMENTED

**Gaps:**
- No logging of data access (who viewed what conversation transcript)
- No logging of data modifications (who edited what)
- No immutable audit log (logs could be deleted)

**Recommendation:**

```python
class AuditLog(Base):
    """Immutable audit trail for HIPAA compliance"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False)  # "VIEW_SESSION", "EDIT_MCQ", "DELETE_USER"
    resource_type = Column(String(50), nullable=False)  # "osce_session", "mcq", "user"
    resource_id = Column(String(100), nullable=False)
    ip_address = Column(String(45), nullable=False)
    user_agent = Column(Text, nullable=True)
    details = Column(JSONB, nullable=True)  # Additional context
    
    # NO UPDATE OR DELETE - Immutable audit trail
    __table_args__ = (
        {'postgresql_partition_by': 'RANGE (timestamp)'},  # Partition by month
    )
```

**Action Required:**
1. Create `AuditLog` model with immutable design
2. Add middleware to log all authenticated requests
3. Log sensitive actions (view session, delete user, export data)
4. Implement log retention policy (365 days as per .env.template)
5. Set up log archival to immutable storage

**Timeline:** WEEK 3 (HIPAA requirement)

---

### Data Retention:

**Current Policy:**
- Redis session TTL: 2 hours - GOOD (auto-cleanup)
- PostgreSQL data: No retention policy specified - NEEDS WORK

**Recommendation:**
- Define retention periods:
  - Active user data: Indefinite (until user requests deletion)
  - Inactive users (no login for 2 years): Archive or delete with notification
  - Audit logs: 7 years (HIPAA requirement)
  - Session transcripts: 1 year (educational record)

**Action Required:**
1. Document data retention policy in privacy policy
2. Implement automated data deletion for inactive accounts
3. Create background task to archive old sessions
4. Notify users before data deletion (30-day notice)

**Timeline:** WEEK 4

---

## 4. Australian Medical Compliance Assessment

### Overall Rating: LOW RISK

### QA-001 Australian Compliance Validator:

**Documented Checks:**
- Australian terminology (paracetamol not acetaminophen) - SPECIFIED
- Emergency number (000 not 911) - SPECIFIED
- Healthcare context (Medicare, PBS, GP) - SPECIFIED
- Medical guidelines (eTG, AMH) - SPECIFIED

**Architecture Integration:**
- AI patient responses validated before sending to candidate - GOOD
- Examiner scoring validated against clinical guidelines - GOOD
- Content generation validated before database storage - GOOD

**Rating:** COMPLIANT (assuming QA-001 is implemented correctly)

**Verification Needed:**
- Test QA-001 agent with US terminology to confirm rejection
- Test emergency number validation (911 should be flagged)
- Test drug name validation (acetaminophen should be flagged)

**Action Required:**
1. Create test suite for QA-001 validation
2. Document validation rules in QA-001 agent implementation
3. Add metrics to track validation failures

**Timeline:** WEEK 2 (with agent implementation)

---

## 5. Attack Surface Analysis

### Overall Rating: MEDIUM RISK

### Injection Attacks:

**SQL Injection:**
- SQLAlchemy ORM used throughout - SAFE
- No raw SQL execution with user input found - GOOD
- Pydantic validation on all inputs - GOOD

**Rating:** LOW RISK

---

**NoSQL Injection (Redis):**
- Session IDs validated before Redis queries - IMPLEMENTATION NEEDED
- Conversation history stored as JSON (not executed) - SAFE

**Recommendation:**
```python
import uuid

def validate_session_id(session_id: str) -> bool:
    """Validate session ID format to prevent Redis injection"""
    try:
        # Session ID should be UUID format
        uuid.UUID(session_id)
        return True
    except ValueError:
        return False

# In WebSocket handler:
if not validate_session_id(session_id):
    await websocket.close(code=1008, reason="Invalid session ID")
    return
```

**Action Required:**
1. Implement session ID validation
2. Test Redis queries with malicious input
3. Add rate limiting on session creation

**Timeline:** WEEK 1

---

### Cross-Site Scripting (XSS):

**Frontend (React):**
- React escapes HTML by default - SAFE
- No `dangerouslySetInnerHTML` usage expected - GOOD

**Backend (API):**
- Pydantic validates and sanitizes inputs - GOOD
- No direct HTML rendering in API - SAFE

**Rating:** LOW RISK

---

### Cross-Site Request Forgery (CSRF):

**Current Protection:**
- JWT tokens in Authorization header (not cookies) - CSRF-RESISTANT
- SameSite cookies configured in .env.template - GOOD

**Rating:** LOW RISK

---

### Rate Limiting:

**Architecture Documentation:**
- Section 8.2 mentions "Rate limiting on all endpoints"
- `.env.template` specifies rate limits:
  - Anonymous: 20/min, 100/hour
  - Authenticated: 60/min, 1000/hour
  - AI endpoints: 10/min, 100/hour

**Implementation Status:**
- `main.py` shows import of rate limiter - MENTIONED
- No actual rate limiting middleware found in code - NOT IMPLEMENTED

**Missing Implementation:**

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@router.post("/auth/login")
@limiter.limit("5/minute")  # Prevent brute force
async def login(request: Request, credentials: UserLogin, db: Session = Depends(get_db)):
    pass

@router.post("/osce/start")
@limiter.limit("10/minute")  # Prevent AI abuse
async def start_osce(request: Request, user: User = Depends(get_current_user)):
    pass
```

**Action Required:**
1. Install `slowapi` package
2. Configure limiter with Redis backend (for distributed rate limiting)
3. Apply rate limits to all endpoints:
   - Auth endpoints: 5/min (brute force prevention)
   - OSCE creation: 10/min (AI cost control)
   - General API: 60/min
4. Test rate limiting with automated requests

**Timeline:** WEEK 1 (before deployment)

---

### Input Validation:

**Current Approach:**
- Pydantic schemas validate all inputs - GOOD
- Type validation, length limits, regex patterns - IMPLEMENTED

**Example (from schemas/user.py):**

```python
class UserCreate(BaseModel):
    email: EmailStr  # Validates email format
    password: str = Field(..., min_length=12)  # Enforces min length
    full_name: str = Field(..., min_length=2, max_length=255)
```

**Gaps:**
- No validation for WebSocket message content length
- No validation for conversation history size (could fill Redis)

**Recommendation:**

```python
class CandidateMessage(BaseModel):
    type: Literal["candidate_message", "pause", "end"]
    content: str = Field(..., max_length=2000)  # Limit message length
    timestamp: int

# In WebSocket handler:
try:
    message = CandidateMessage.parse_obj(json.loads(data))
except ValidationError as e:
    await websocket.send_json({"type": "error", "message": "Invalid message format"})
    return
```

**Action Required:**
1. Add Pydantic validation for WebSocket messages
2. Enforce message length limits (2000 chars)
3. Limit conversation history size in Redis (e.g., max 100 messages)

**Timeline:** WEEK 1

---

### WebSocket Security:

**Current Specification:**
- Connection authentication mentioned but NOT DETAILED
- No mention of message validation
- No mention of DoS prevention (message flood)

**Recommendations:**

1. **Authentication:** (already covered in Section 1)

2. **Message Validation:**
```python
MAX_MESSAGE_LENGTH = 2000
MAX_MESSAGES_PER_SESSION = 100

async def handle_message(websocket: WebSocket, data: str):
    # Validate message size
    if len(data) > MAX_MESSAGE_LENGTH:
        await websocket.send_json({"type": "error", "message": "Message too long"})
        return
    
    # Validate message count
    message_count = await redis.hget(f"session:{session_id}", "message_count")
    if int(message_count or 0) >= MAX_MESSAGES_PER_SESSION:
        await websocket.send_json({"type": "error", "message": "Message limit reached"})
        return
```

3. **DoS Prevention:**
```python
from collections import deque
import time

class WebSocketRateLimiter:
    def __init__(self, max_per_second=5):
        self.timestamps = deque(maxlen=max_per_second)
        self.max_per_second = max_per_second
    
    def allow_message(self) -> bool:
        now = time.time()
        # Remove timestamps older than 1 second
        while self.timestamps and self.timestamps[0] < now - 1:
            self.timestamps.popleft()
        
        if len(self.timestamps) >= self.max_per_second:
            return False  # Rate limit exceeded
        
        self.timestamps.append(now)
        return True
```

**Action Required:**
1. Implement WebSocket authentication (covered in Section 1)
2. Add message validation and size limits
3. Implement per-connection rate limiting (5 messages/second)
4. Test WebSocket DoS scenarios

**Timeline:** WEEK 1

---

## 6. Prioritized Remediation Plan

### Phase 1: Pre-Deployment (Blocking Issues) - WEEK 1

**Priority: CRITICAL**

| Issue | Severity | Effort | Timeline |
|-------|----------|--------|----------|
| Remove hardcoded secret key in config.py | CRITICAL | 1 hour | Day 1 |
| Configure Redis AUTH in docker-compose | CRITICAL | 2 hours | Day 1 |
| Implement WebSocket authentication | HIGH | 4 hours | Day 2 |
| Implement rate limiting (slowapi) | HIGH | 4 hours | Day 2 |
| Add session ID validation (Redis injection) | HIGH | 2 hours | Day 3 |
| Add WebSocket message validation | MEDIUM | 3 hours | Day 3 |
| Remove database credentials from config.py | HIGH | 1 hour | Day 4 |
| Add testing auth bypass environment check | MEDIUM | 1 hour | Day 4 |

**Total Effort:** ~18 hours (~2-3 days)

---

### Phase 2: Data Security - WEEK 2

**Priority: HIGH**

| Issue | Severity | Effort | Timeline |
|-------|----------|--------|----------|
| Implement encrypted columns (SQLAlchemy) | HIGH | 6 hours | Day 1-2 |
| Implement conversation encryption (AES-GCM) | MEDIUM | 4 hours | Day 2 |
| Generate and store encryption keys | HIGH | 2 hours | Day 3 |
| Create migration to encrypt existing data | MEDIUM | 4 hours | Day 3-4 |
| Test QA-001 Australian compliance validator | MEDIUM | 4 hours | Day 4 |
| Update deployment docs with encryption setup | LOW | 2 hours | Day 5 |

**Total Effort:** ~22 hours (~3-4 days)

---

### Phase 3: Audit & Compliance - WEEK 3

**Priority: MEDIUM**

| Issue | Severity | Effort | Timeline |
|-------|----------|--------|----------|
| Create AuditLog model with immutable design | MEDIUM | 4 hours | Day 1 |
| Implement audit logging middleware | MEDIUM | 4 hours | Day 2 |
| Log sensitive actions (view, edit, delete) | MEDIUM | 4 hours | Day 3 |
| Implement log retention policy | LOW | 3 hours | Day 4 |
| Set up log archival to immutable storage | MEDIUM | 4 hours | Day 5 |
| Create audit log query dashboard (admin) | LOW | 6 hours | Week 4 |

**Total Effort:** ~25 hours (~4 days)

---

### Phase 4: Data Retention & Privacy - WEEK 4

**Priority: LOW**

| Issue | Severity | Effort | Timeline |
|-------|----------|--------|----------|
| Document data retention policy | LOW | 2 hours | Day 1 |
| Implement automated data deletion (inactive) | MEDIUM | 6 hours | Day 2-3 |
| Create background task for session archival | LOW | 4 hours | Day 3 |
| Implement user notification before deletion | LOW | 3 hours | Day 4 |
| Create privacy policy page (frontend) | LOW | 4 hours | Day 5 |

**Total Effort:** ~19 hours (~3 days)

---

## 7. Security Testing Checklist

### Pre-Deployment Testing (Week 1):

- [ ] Confirm SECRET_KEY cannot be deployed with default value
- [ ] Test Redis connection with AUTH enabled
- [ ] Test WebSocket connection with invalid JWT token (should reject)
- [ ] Test WebSocket connection with valid JWT but wrong session_id (should reject)
- [ ] Test rate limiting on login endpoint (5 failed attempts = 403)
- [ ] Test rate limiting on OSCE creation (10 requests/min = 429)
- [ ] Test session ID validation with malicious input (should reject)
- [ ] Test WebSocket message length limit (2001 chars = error)
- [ ] Test account lockout after 5 failed logins (30-min lockout)
- [ ] Confirm TLS 1.3 enabled in production Nginx config

---

### Data Security Testing (Week 2):

- [ ] Verify email and full_name fields are encrypted in PostgreSQL
- [ ] Verify conversation history is encrypted before storage
- [ ] Test decryption of stored conversations (should work)
- [ ] Test database backup contains encrypted data (not plaintext)
- [ ] Confirm encryption keys are loaded from Docker secrets (not env vars)
- [ ] Test QA-001 rejects US terminology (acetaminophen = error)
- [ ] Test QA-001 rejects US emergency number (911 = error)
- [ ] Test QA-001 accepts Australian terminology (paracetamol = pass)

---

### Audit & Compliance Testing (Week 3):

- [ ] Verify audit log records all authenticated requests
- [ ] Verify sensitive actions logged (VIEW_SESSION, DELETE_USER)
- [ ] Confirm audit logs cannot be deleted (immutable)
- [ ] Test audit log retention (logs older than 365 days archived)
- [ ] Verify user can request data export (GDPR compliance)
- [ ] Verify user can request data deletion (GDPR compliance)
- [ ] Test soft delete (deleted_at field set, data not removed)

---

## 8. Ongoing Security Maintenance

### Weekly Tasks:

- Review audit logs for suspicious activity
- Check rate limiting metrics (blocked requests)
- Monitor failed login attempts
- Review Redis memory usage (session cleanup)

### Monthly Tasks:

- Rotate JWT secret key (with grace period for active tokens)
- Review and update dependency versions (security patches)
- Scan codebase for hardcoded secrets (automated CI/CD check)
- Review user account lockouts (legitimate vs. attacks)

### Quarterly Tasks:

- External penetration testing
- Security audit of new features
- Update threat model
- Review and update data retention policy

---

## 9. Conclusion

### Summary:

The AMC Clinical Exam Simulation architecture demonstrates **strong security foundations** with JWT authentication, bcrypt password hashing, and comprehensive input validation. However, **critical gaps in data encryption and Redis security** must be addressed before deployment.

### Key Strengths:

1. No real patient data (fictional personas only)
2. Strong authentication with account lockout
3. Proper use of environment variables for secrets (mostly)
4. GDPR-compliant user data deletion
5. Australian medical compliance enforced via QA-001

### Key Weaknesses:

1. Hardcoded default secret key (CRITICAL)
2. Redis AUTH not configured (CRITICAL)
3. WebSocket authentication underspecified (HIGH)
4. Encrypted columns not implemented (HIGH)
5. Audit logging incomplete (MEDIUM)

### Recommendations:

**BLOCK DEPLOYMENT until:**
- [ ] Hardcoded secret key removed
- [ ] Redis AUTH configured and tested
- [ ] WebSocket authentication implemented and tested
- [ ] Rate limiting implemented and tested

**Complete within 2 weeks:**
- [ ] Encrypted columns for PII fields
- [ ] Conversation history encryption
- [ ] Comprehensive audit logging

**Complete within 4 weeks:**
- [ ] Data retention policy documented and implemented
- [ ] Automated data deletion for inactive accounts
- [ ] Privacy policy page created

### Final Rating: MEDIUM RISK (Pre-Implementation)

**With critical issues resolved, rating will improve to LOW RISK.**

---

**Assessment Completed:** 2026-02-06  
**Next Review:** After Phase 1 implementation (Week 1 completion)  
**Document Version:** 1.0
