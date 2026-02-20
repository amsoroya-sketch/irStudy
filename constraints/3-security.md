# Security & Configuration Constraints

**Constraint Module**: 3 - Security
**Status**: MANDATORY
**Last Updated**: 2026-02-16
**Version**: 2.0.0

---

## Overview

This module defines security requirements for the irStudy Medical Education Platform. **ZERO-TOLERANCE** policy for security violations.

**Compliance Frameworks**:
- HIPAA (Health Insurance Portability and Accountability Act)
- Australian Privacy Principles (APPs)
- AHPRA clinical documentation standards

---

## Critical Rules Summary

| Rule | Description | Violation |
|------|-------------|-----------|
| **NO hardcoded credentials** | Use Vault or environment variables | CRITICAL |
| **NO PHI in logs** | Sanitize all patient identifiers | CRITICAL |
| **HTTPS enforced** | All production traffic encrypted | CRITICAL |
| **Strong encryption** | Argon2id for passwords, AES-256 for data | CRITICAL |
| **Audit logging** | All PHI access logged | HIGH |
| **Australian compliance** | Use Australian medical terminology | MEDIUM |

---

## 1. Credential Management

### 1.1 Zero Hardcoded Credentials

**RULE**: NEVER hardcode credentials in code or configuration files.

**❌ VIOLATIONS**:
```python
# NEVER DO THIS
ANTHROPIC_API_KEY = "sk-ant-api03-1234567890..."  # VIOLATION!
DATABASE_URL = "postgresql://user:password@localhost/db"  # VIOLATION!
JWT_SECRET = "super-secret-key-123"  # VIOLATION!
```

**✅ CORRECT PATTERNS**:
```python
# ALWAYS DO THIS
from src.core.vault import get_vault_secret

# Get from Vault
api_key = get_vault_secret("irStudy/claude", "api_key")

# Or fallback to environment (development only)
api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    raise RuntimeError("ANTHROPIC_API_KEY not set")
```

**Validation**:
```bash
# Run security audit
./scripts/security-audit.sh

# Expected output: "✅ No hardcoded credentials"
```

### 1.2 Vault Integration

**RULE**: Use HashiCorp Vault for all production secrets.

**Setup**:
```bash
# Install Vault
brew install vault  # macOS
apt install vault   # Linux

# Start dev server
vault server -dev

# Set environment
export VAULT_ADDR='http://127.0.0.1:8200'
export VAULT_TOKEN='<token>'

# Store secrets
vault kv put secret/irStudy/claude api_key="sk-ant-..."
vault kv put secret/irStudy/database password="..."
```

**Usage**:
```python
from src.core.vault import get_vault_secret

# Get entire secret
config = get_vault_secret("irStudy/claude")

# Get specific key
api_key = get_vault_secret("irStudy/claude", "api_key")
```

**Reference**: `docs/VAULT_INTEGRATION.md`

### 1.3 Environment Variables

**RULE**: `.env` files for non-secrets only. NEVER commit secrets.

**✅ Safe to commit**:
```bash
# .env
ENV=production
LOG_LEVEL=INFO
VAULT_ADDR=https://vault.irstudy.com:8200
```

**❌ NEVER commit**:
```bash
# .env.example (template only)
VAULT_TOKEN=<your-token>
ANTHROPIC_API_KEY=<your-key>
DATABASE_PASSWORD=<your-password>
```

**Gitignore**:
```bash
# .gitignore
.env
.env.local
*.key
*.pem
```

---

## 2. PHI (Protected Health Information) Protection

### 2.1 18 HIPAA Identifiers

**Protected Health Information** includes:
1. Names
2. Geographic subdivisions smaller than state
3. Dates (except year)
4. Telephone numbers
5. Fax numbers
6. Email addresses
7. Social Security numbers
8. Medical record numbers (MRN)
9. Health plan beneficiary numbers
10. Account numbers
11. Certificate/license numbers
12. Vehicle identifiers
13. Device identifiers
14. URLs
15. IP addresses
16. Biometric identifiers
17. Full-face photos
18. Any unique identifying number/characteristic

**irStudy PHI Examples**:
- Patient names
- Parent email addresses
- Session notes (clinical details)
- Goal descriptions
- Diagnosis information

### 2.2 Anonymization Before External APIs

**RULE**: Sanitize ALL PHI before sending to Claude AI or external services.

**❌ VIOLATION**:
```python
# Sending PHI to Claude API
response = claude_client.messages.create(
    model="claude-3-5-sonnet-20241022",
    messages=[{
        "role": "user",
        "content": f"Validate this SOAP note for {patient.full_name}: {soap_note.subjective}"
    }]
)
```

**✅ CORRECT**:
```python
from src.security.phi_anonymizer import anonymize_for_claude

# Anonymize PHI
anonymized_soap = anonymize_for_claude(soap_note, patient)
# patient.full_name → [PATIENT]
# patient.email → [EMAIL]
# patient.mrn → [MRN]

# Safe to send to Claude
response = claude_client.messages.create(
    model="claude-3-5-sonnet-20241022",
    messages=[{
        "role": "user",
        "content": f"Validate this SOAP note: {anonymized_soap['subjective']}"
    }]
)
```

**Implementation**:
```python
# src/security/phi_anonymizer.py
def anonymize_for_claude(data: dict, patient: Patient) -> dict:
    """Replace PHI with placeholders"""
    anonymized = data.copy()
    
    # Replace patient name
    for field in ["subjective", "objective", "assessment", "plan"]:
        if field in anonymized:
            anonymized[field] = anonymized[field].replace(patient.full_name, "[PATIENT]")
    
    return anonymized
```

### 2.3 No PHI in Logs

**RULE**: NEVER log PHI. Hash or truncate identifiers.

**❌ VIOLATIONS**:
```python
# NEVER log full identifiers
logger.info(f"Patient {patient.full_name} logged in")  # VIOLATION!
logger.info(f"Email: {user.email}")  # VIOLATION!
logger.info(f"MRN: {patient.mrn}")  # VIOLATION!
```

**✅ CORRECT**:
```python
import hashlib

# Hash identifiers
email_hash = hashlib.sha256(user.email.encode()).hexdigest()[:8]
logger.info(f"User logged in: {email_hash}")

# Truncate MRN
mrn_truncated = patient.mrn[:4] + "****"
logger.info(f"Patient session started: {mrn_truncated}")

# Use user ID (non-PHI)
logger.info(f"User {user.id} accessed EMR session {session.id}")
```

**Safe Logging Pattern**:
```python
def sanitize_log(message: str, patient: Optional[Patient] = None) -> str:
    """Remove PHI from log messages"""
    if patient:
        message = message.replace(patient.full_name, "[PATIENT]")
        message = message.replace(patient.email, "[EMAIL]")
    return message

# Usage
logger.info(sanitize_log(f"Session for {patient.full_name}", patient))
# Output: "Session for [PATIENT]"
```

---

## 3. Encryption Standards

### 3.1 Password Hashing - Argon2id

**RULE**: Use Argon2id for password hashing (NOT MD5, SHA1, or bcrypt).

**Parameters**:
- Memory: 64 MiB
- Iterations: 3
- Parallelism: 4
- Output: 32 bytes

**Implementation**:
```python
from argon2 import PasswordHasher

ph = PasswordHasher(
    time_cost=3,
    memory_cost=65536,  # 64 MiB
    parallelism=4,
    hash_len=32,
    salt_len=16
)

# Hash password
hashed = ph.hash("user_password_here")

# Verify password
try:
    ph.verify(hashed, "user_password_here")
    print("Password correct")
except:
    print("Password incorrect")
```

**❌ NEVER USE**:
- MD5 (broken)
- SHA1 (broken)
- Plain SHA256 (too fast, vulnerable to rainbow tables)
- bcrypt with default cost (too low)

### 3.2 Data Encryption - AES-256

**RULE**: Use AES-256-GCM for encrypting data at rest.

**Implementation**:
```python
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os

# Generate key (store in Vault)
key = AESGCM.generate_key(bit_length=256)

# Encrypt
aesgcm = AESGCM(key)
nonce = os.urandom(12)
ciphertext = aesgcm.encrypt(nonce, plaintext.encode(), None)

# Decrypt
plaintext = aesgcm.decrypt(nonce, ciphertext, None)
```

**Database Encryption**:
```sql
-- PostgreSQL pgcrypto
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Encrypt column
UPDATE patients
SET email_encrypted = pgp_sym_encrypt(email, 'encryption_key_from_vault');

-- Decrypt column
SELECT pgp_sym_decrypt(email_encrypted, 'encryption_key_from_vault') AS email
FROM patients;
```

### 3.3 HTTPS Enforcement

**RULE**: Redirect all HTTP to HTTPS in production.

**Middleware**:
```python
# backend/src/middleware/https_redirect.py
from fastapi import Request
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware

class HTTPSRedirectMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.scheme == "http":
            # Redirect to HTTPS
            https_url = request.url.replace(scheme="https")
            return RedirectResponse(url=str(https_url), status_code=301)
        
        response = await call_next(request)
        
        # Add security headers
        response.headers["Strict-Transport-Security"] = "max-age=31536000"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        
        return response
```

**Registration**:
```python
# backend/src/main.py
from middleware.https_redirect import add_https_middleware

app = FastAPI()
add_https_middleware(app)  # Auto-detects production
```

---

## 4. Audit Logging

### 4.1 Security Events

**RULE**: Log all PHI access and security events.

**Required Events**:
- User login/logout
- Failed login attempts
- PHI access (read, update, delete)
- Permission changes
- Password resets
- API key usage

**Implementation**:
```python
from src.security.events import log_security_event

# Log PHI access
log_security_event(
    event_type="PHI_ACCESS",
    user_id=current_user.id,
    resource_id=patient.id,
    action="READ",
    ip_address=request.client.host,
    details={"resource_type": "patient", "fields_accessed": ["name", "email"]}
)

# Log failed login
log_security_event(
    event_type="LOGIN_FAILED",
    user_id=None,
    email=form_data.username,
    ip_address=request.client.host,
    details={"reason": "invalid_password"}
)
```

**Database Schema**:
```sql
CREATE TABLE security_events (
    id SERIAL PRIMARY KEY,
    event_type VARCHAR(50) NOT NULL,
    user_id INTEGER,
    timestamp TIMESTAMP DEFAULT NOW(),
    ip_address INET,
    action VARCHAR(20),
    resource_id INTEGER,
    resource_type VARCHAR(50),
    details JSONB
);

CREATE INDEX idx_security_events_user ON security_events(user_id);
CREATE INDEX idx_security_events_timestamp ON security_events(timestamp);
```

### 4.2 Log Retention

**RULE**: Retain audit logs for 7 years (HIPAA requirement).

**Configuration**:
```python
# Log rotation
import logging.handlers

handler = logging.handlers.RotatingFileHandler(
    "/var/log/irstudy/audit.log",
    maxBytes=100_000_000,  # 100 MB
    backupCount=70  # 7 years worth
)
```

---

## 5. Australian Medical Compliance

### 5.1 Terminology

**RULE**: Use Australian medical terminology (not American).

**Correct Australian Terms**:
| Australian | American (WRONG) |
|------------|------------------|
| Paracetamol | Acetaminophen |
| Salbutamol | Albuterol |
| Adrenaline | Epinephrine |
| 000 | 911 |
| Casualty | Emergency Room (ER) |
| Theatre | Operating Room (OR) |

**Validation**:
```python
# Validator
def validate_australian_terminology(text: str) -> List[str]:
    """Check for American medical terms"""
    american_terms = {
        "acetaminophen": "paracetamol",
        "albuterol": "salbutamol",
        "epinephrine": "adrenaline",
        "911": "000",
    }
    
    violations = []
    for american, australian in american_terms.items():
        if re.search(rf'\b{american}\b', text, re.IGNORECASE):
            violations.append(f"Use '{australian}' not '{american}'")
    
    return violations
```

### 5.2 Regulatory References

**RULE**: Reference Australian guidelines (not American).

**Correct Sources**:
- eTG (Therapeutic Guidelines) - NOT UpToDate
- AMH (Australian Medicines Handbook) - NOT Lexicomp
- AHPRA standards - NOT JCAHO
- AMC Clinical Examination - NOT USMLE
- PBS (Pharmaceutical Benefits Scheme)
- MBS (Medicare Benefits Schedule)

---

## 6. Testing Requirements

### 6.1 Security Test Suite

**RULE**: Run security tests before every commit.

**Test Coverage**:
```bash
# Run all security tests
pytest backend/tests/test_security/ -v

# Expected tests
test_no_hardcoded_credentials PASSED
test_no_hardcoded_api_keys PASSED
test_no_phi_in_logs PASSED
test_phi_anonymization PASSED
test_https_redirect PASSED
test_security_headers PASSED
test_no_weak_encryption PASSED
test_australian_terminology PASSED
```

### 6.2 Pre-Commit Hook

**RULE**: Security audit blocks commits with violations.

**Hook**: `.git/hooks/pre-commit` (auto-runs `security-audit.sh`)

**Manual Run**:
```bash
./scripts/security-audit.sh
# Expected: "✅ SECURITY AUDIT PASSED"
```

---

## 7. Checklist for Developers

Before committing code:

- [ ] No hardcoded credentials (`./scripts/security-audit.sh`)
- [ ] No PHI in logs (grep `logger.*email`, `print.*patient`)
- [ ] All secrets in Vault or environment variables
- [ ] HTTPS middleware enabled in production
- [ ] Australian terminology used (not American)
- [ ] PHI anonymized before external APIs
- [ ] Security tests passing (`pytest test_security/`)
- [ ] Encryption standards met (Argon2id, AES-256)

---

## 8. References

- [HIPAA Security Rule](https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- [Australian Privacy Principles](https://www.oaic.gov.au/privacy/australian-privacy-principles)
- [Vault Documentation](https://developer.hashicorp.com/vault/docs)
- Project: `docs/VAULT_INTEGRATION.md`
- Project: `docs/SECURITY_COMPLIANCE_CHECKLIST.md`
- Project: `scripts/security-audit.sh`

---

**Status**: ✅ ACTIVE
**Next Review**: 2026-05-16 (Quarterly)
