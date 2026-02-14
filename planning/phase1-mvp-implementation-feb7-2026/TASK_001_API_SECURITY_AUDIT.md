# TASK_001: API Security Audit
## Comprehensive Security Audit with OWASP Top 10 Verification

**Metadata:**
- **Week:** 1
- **Day:** 1-2 (Feb 7-8, 2026)
- **Duration:** 6-8 hours
- **Priority:** P0-Critical
- **Dependencies:** None
- **Owner:** security-compliance-expert + rust-ffi-expert
- **Status:** 🟡 Not Started

---

## 🎯 Objectives

1. **Comprehensive security audit** of all backend API endpoints
2. **Identify and fix** all P0/P1 security vulnerabilities (target: zero)
3. **Implement automated security scanning** in CI/CD pipeline
4. **Harden JWT authentication** with best practices
5. **Verify OWASP Top 10 compliance**
6. **Document security posture** in audit report

---

## 🤖 Agent OS Delegation Template

### Agent: security-compliance-expert + rust-ffi-expert

**Context:**
You are performing a comprehensive security audit of the irStudy Medical Education Platform backend API. The platform handles medical education content (MCQs, OSCEs, Study Cards) and must meet HIPAA compliance standards for PHI protection, even though current data is non-PHI (educational content only).

**Current State:**
- Backend: FastAPI + Python 3.11+ + PostgreSQL
- Authentication: JWT-based (NOT Clerk)
- Database: `irstudy_medical` @ localhost:5433
- Infrastructure: PostgreSQL + Redis Cluster (6 nodes) + Qdrant + Vault
- Content: 1,208 MCQs, 210 OSCEs, 140 Study Cards

**Read FIRST:**
1. `/home/dev/Development/irStudy/constraints/README.md` - Project constraints
2. `/home/dev/Development/irStudy/backend/src/api/v1/` - All API route files
3. `/home/dev/Development/irStudy/backend/src/auth/` - Authentication logic
4. `/home/dev/Development/irStudy/COMPREHENSIVE_PLATFORM_PLAN_EXTENDED_SECURITY.md` - Security framework

---

### Constraints (READ THESE FIRST)

**From PROJECT_CONSTRAINTS.md:**

❌ **NEVER:**
- Hardcode database credentials or API keys
- Use mock user IDs or test credentials in production code
- Skip HTTPS/TLS for API endpoints
- Store passwords in plaintext
- Use weak JWT secrets (<32 characters)
- Disable security middleware (CORS, CSP, rate limiting)
- Allow SQL injection vectors (use parameterized queries ONLY)
- Expose sensitive data in error messages
- Skip input validation (always validate + sanitize)

✅ **ALWAYS:**
- Use environment variables for secrets (loaded from Vault in production)
- Implement rate limiting on ALL endpoints (see RATE_LIMIT settings in .env)
- Validate Australian medical context (drug names, citations)
- Use parameterized queries (SQLAlchemy ORM)
- Hash passwords with bcrypt (cost factor ≥12)
- Sign JWTs with HS256 or RS256
- Implement CORS with explicit allowed origins
- Log security events to audit log
- Validate all user inputs (Pydantic schemas)
- Use HTTPS in production (enforce with redirects)

**Australian Medical Context:**
- ❌ NEVER allow American drug names: "acetaminophen" → reject, require "paracetamol"
- ✅ ALWAYS validate citations reference Australian guidelines: eTG, PBS, AHPRA, AMH

**Security Specifications:**
- JWT token expiration: 30 minutes (access), 7 days (refresh)
- Password policy: ≥12 chars, uppercase, lowercase, digit, special char
- Account lockout: 5 failed attempts = 30 min lockout
- Rate limiting: 20 req/min (anonymous), 60 req/min (authenticated)

---

### Validation Checklist

**Before returning results, verify ALL of the following:**

#### Security Scan Results
- [ ] Bandit scan completed with 0 HIGH/CRITICAL issues
- [ ] Safety check completed with 0 CRITICAL vulnerabilities
- [ ] No hardcoded credentials found (grep scan)
- [ ] No SQL injection vectors identified
- [ ] No XSS vulnerabilities in responses

#### OWASP Top 10 Verification
- [ ] A01:2021 – Broken Access Control: JWT enforced on protected routes
- [ ] A02:2021 – Cryptographic Failures: Passwords hashed with bcrypt
- [ ] A03:2021 – Injection: Parameterized queries only (SQLAlchemy ORM)
- [ ] A04:2021 – Insecure Design: Rate limiting implemented
- [ ] A05:2021 – Security Misconfiguration: CORS configured correctly
- [ ] A06:2021 – Vulnerable Components: All dependencies up-to-date
- [ ] A07:2021 – Authentication Failures: Account lockout implemented
- [ ] A08:2021 – Data Integrity Failures: Input validation (Pydantic)
- [ ] A09:2021 – Logging Failures: Audit logging operational
- [ ] A10:2021 – Server-Side Request Forgery: No SSRF vectors

#### JWT Hardening
- [ ] JWT secret: ≥32 characters (from environment variable)
- [ ] Token expiration: 30 min (access), 7 days (refresh)
- [ ] Signature algorithm: HS256 or RS256 (not "none")
- [ ] Token validation on every request
- [ ] Refresh token rotation implemented

#### Automated Security Integration
- [ ] Bandit integrated into GitHub Actions workflow
- [ ] Safety check integrated into GitHub Actions workflow
- [ ] Pre-commit hook for security scan
- [ ] Security scan fails CI/CD if vulnerabilities found

#### Documentation
- [ ] Security audit report generated (Markdown format)
- [ ] All P0/P1 vulnerabilities listed with fixes
- [ ] Security recommendations documented
- [ ] Compliance checklist (OWASP Top 10, HIPAA considerations)

---

### Expected Output

**Deliverables:**

1. **Security Audit Report** (`backend/docs/security_audit_report_2026-02-07.md`):
   - Executive summary
   - Methodology (tools used: Bandit, Safety, manual review)
   - Findings: P0/P1/P2/P3 vulnerabilities
   - Fixes applied
   - OWASP Top 10 compliance matrix
   - Recommendations

2. **Fixed Code** (if vulnerabilities found):
   - Updated files with security fixes
   - Git commit with message: "security: Fix [vulnerability type] in [component]"

3. **CI/CD Integration** (`.github/workflows/security-scan.yml`):
   ```yaml
   name: Security Scan
   on: [push, pull_request]
   jobs:
     security:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v3
         - name: Run Bandit
           run: bandit -r backend/src/ -f json -o bandit_report.json
         - name: Run Safety
           run: safety check --json
         - name: Fail on HIGH/CRITICAL
           run: |
             CRITICAL=$(jq '.results[] | select(.issue_severity == "HIGH" or .issue_severity == "CRITICAL")' bandit_report.json | wc -l)
             if [ "$CRITICAL" -gt 0 ]; then exit 1; fi
   ```

4. **Test Results**:
   - Bandit report (JSON): `backend/security_reports/bandit_report.json`
   - Safety report (JSON): `backend/security_reports/safety_report.json`
   - Zero P0/P1 vulnerabilities confirmed

---

## 📋 Implementation Guide

### Step 1: Setup Security Tools (30 minutes)

**Install security scanning tools:**

```bash
cd /home/dev/Development/irStudy/backend

# Install Bandit (Python security linter)
pip install bandit

# Install Safety (dependency vulnerability scanner)
pip install safety

# Verify installations
bandit --version
safety --version
```

---

### Step 2: Run Initial Security Scans (1 hour)

**Run Bandit scan:**

```bash
# Scan all backend code
bandit -r src/ -f json -o security_reports/bandit_report_initial.json

# Also generate human-readable report
bandit -r src/ -f txt -o security_reports/bandit_report_initial.txt

# Review HIGH/CRITICAL issues
cat security_reports/bandit_report_initial.json | jq '.results[] | select(.issue_severity == "HIGH" or .issue_severity == "CRITICAL")'
```

**Run Safety scan:**

```bash
# Scan dependencies
safety check --json > security_reports/safety_report_initial.json

# Review CRITICAL vulnerabilities
cat security_reports/safety_report_initial.json | jq '.[] | select(.severity == "CRITICAL")'
```

**Manual code review targets:**

```bash
# Check for hardcoded credentials
grep -r "password\s*=\s*['\"]" src/
grep -r "api_key\s*=\s*['\"]" src/
grep -r "secret\s*=\s*['\"]" src/
grep -r "dbPath:" src/  # Rust FFI pattern
grep -r "dbKey:" src/   # Rust FFI pattern

# Check for SQL injection vectors (should find NONE - we use ORM)
grep -r "execute.*format" src/
grep -r "execute.*%" src/

# Check for insecure random
grep -r "random\." src/ | grep -v "secrets\."
```

---

### Step 3: Fix P0/P1 Vulnerabilities (2-3 hours)

**Priority 1: Hardcoded Credentials**

If found, replace with environment variables:

```python
# BEFORE (WRONG):
DATABASE_URL = "postgresql://amc_user:password123@localhost:5433/irstudy_medical"

# AFTER (CORRECT):
import os
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set")
```

**Priority 2: Weak JWT Configuration**

Verify JWT settings in `src/auth/security.py`:

```python
# Check JWT secret strength
import os
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY or len(SECRET_KEY) < 32:
    raise ValueError("SECRET_KEY must be ≥32 characters")

# Verify token expiration
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Not 24 hours!
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Verify signature algorithm
ALGORITHM = "HS256"  # Not "none"!
```

**Priority 3: Missing Rate Limiting**

Add rate limiting middleware if missing:

```python
# src/main.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Apply to routes
@app.get("/api/v1/mcqs/random")
@limiter.limit("60/minute")  # Authenticated users
async def get_random_mcq():
    ...
```

**Priority 4: CORS Misconfiguration**

Verify CORS settings in `src/main.py`:

```python
from fastapi.middleware.cors import CORSMiddleware

# CORRECT (explicit origins):
origins = os.getenv("CORS_ORIGINS", "").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # NOT ["*"]!
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

---

### Step 4: OWASP Top 10 Verification (1 hour)

**Create verification checklist:**

```bash
# Create OWASP compliance document
cat > docs/owasp_top10_compliance.md <<'EOF'
# OWASP Top 10 2021 - Compliance Checklist

## A01:2021 – Broken Access Control
- [x] JWT authentication enforced on all protected routes
- [x] Role-based access control implemented
- [x] No direct object reference vulnerabilities

## A02:2021 – Cryptographic Failures
- [x] Passwords hashed with bcrypt (cost factor 12)
- [x] JWT tokens signed with HS256
- [x] HTTPS enforced in production

## A03:2021 – Injection
- [x] Parameterized queries (SQLAlchemy ORM)
- [x] Input validation (Pydantic schemas)
- [x] No command injection vectors

## A04:2021 – Insecure Design
- [x] Rate limiting: 20/min (anonymous), 60/min (authenticated)
- [x] Account lockout: 5 attempts = 30 min
- [x] Session timeout: 30 minutes

## A05:2021 – Security Misconfiguration
- [x] CORS configured with explicit origins
- [x] Debug mode disabled in production
- [x] Security headers implemented (CSP, X-Frame-Options)

## A06:2021 – Vulnerable and Outdated Components
- [x] All dependencies up-to-date (Safety scan passing)
- [x] Automated dependency scanning in CI/CD

## A07:2021 – Identification and Authentication Failures
- [x] Password policy enforced (≥12 chars)
- [x] Account lockout implemented
- [x] Refresh token rotation

## A08:2021 – Software and Data Integrity Failures
- [x] Input validation (Pydantic)
- [x] Data integrity checks (database constraints)
- [x] Audit logging operational

## A09:2021 – Security Logging and Monitoring Failures
- [x] Audit logging for all security events
- [x] Failed login attempts logged
- [x] Log retention: 365 days

## A10:2021 – Server-Side Request Forgery (SSRF)
- [x] No SSRF vectors identified
- [x] URL validation for external requests
- [x] Allowlist for external APIs

EOF
```

---

### Step 5: Harden JWT Authentication (1 hour)

**Review and harden JWT implementation:**

```python
# src/auth/security.py

from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import os

# Strong secret key (from environment)
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY or len(SECRET_KEY) < 32:
    raise ValueError("SECRET_KEY must be ≥32 characters")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str, token_type: str = "access") -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != token_type:
            raise JWTError("Invalid token type")
        return payload
    except JWTError:
        return None

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
```

---

### Step 6: Integrate Security Scans into CI/CD (30 minutes)

**Create GitHub Actions workflow:**

```yaml
# .github/workflows/security-scan.yml
name: Security Scan

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  security:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          cd backend
          pip install bandit safety

      - name: Run Bandit
        run: |
          cd backend
          mkdir -p security_reports
          bandit -r src/ -f json -o security_reports/bandit_report.json
          bandit -r src/ -f txt

      - name: Run Safety
        run: |
          cd backend
          safety check --json > security_reports/safety_report.json || true
          safety check

      - name: Check for HIGH/CRITICAL issues
        run: |
          cd backend
          CRITICAL=$(jq '.results[] | select(.issue_severity == "HIGH" or .issue_severity == "CRITICAL")' security_reports/bandit_report.json | wc -l)
          echo "Found $CRITICAL HIGH/CRITICAL issues"
          if [ "$CRITICAL" -gt 0 ]; then
            echo "❌ Security scan failed: HIGH/CRITICAL vulnerabilities found"
            exit 1
          fi
          echo "✅ Security scan passed: No HIGH/CRITICAL vulnerabilities"

      - name: Upload security reports
        uses: actions/upload-artifact@v3
        with:
          name: security-reports
          path: backend/security_reports/
```

---

### Step 7: Generate Security Audit Report (30 minutes)

**Template for audit report:**

```markdown
# Security Audit Report - irStudy Medical Education Platform
**Date:** 2026-02-07
**Auditor:** security-compliance-expert + rust-ffi-expert
**Scope:** Backend API (FastAPI + Python 3.11)

---

## Executive Summary

**Audit Duration:** [X] hours
**Findings:** [X] total ([X] P0, [X] P1, [X] P2, [X] P3)
**Status:** ✅ All P0/P1 vulnerabilities fixed

---

## Methodology

**Tools Used:**
- Bandit v1.7+ (Python security linter)
- Safety v2.0+ (dependency vulnerability scanner)
- Manual code review (authentication, authorization, input validation)

**Scope:**
- All API endpoints in `backend/src/api/v1/`
- Authentication logic in `backend/src/auth/`
- Database models in `backend/src/db/`
- Environment configuration in `backend/.env`

---

## Findings

### P0 - Critical (Must Fix Immediately)

[List any P0 vulnerabilities found and fixes applied]

### P1 - High (Fix Before Production)

[List any P1 vulnerabilities found and fixes applied]

### P2 - Medium (Fix in Next Sprint)

[List any P2 vulnerabilities found and remediation plan]

### P3 - Low (Document and Monitor)

[List any P3 vulnerabilities found and recommendations]

---

## OWASP Top 10 2021 - Compliance Matrix

| Category | Status | Notes |
|----------|--------|-------|
| A01: Broken Access Control | ✅ Compliant | JWT enforced on all protected routes |
| A02: Cryptographic Failures | ✅ Compliant | Bcrypt (cost 12), HTTPS enforced |
| A03: Injection | ✅ Compliant | SQLAlchemy ORM, Pydantic validation |
| A04: Insecure Design | ✅ Compliant | Rate limiting, account lockout |
| A05: Security Misconfiguration | ✅ Compliant | CORS configured, debug disabled |
| A06: Vulnerable Components | ✅ Compliant | All dependencies up-to-date |
| A07: Auth Failures | ✅ Compliant | Strong password policy, lockout |
| A08: Data Integrity Failures | ✅ Compliant | Input validation, audit logs |
| A09: Logging Failures | ✅ Compliant | Comprehensive audit logging |
| A10: SSRF | ✅ Compliant | No SSRF vectors identified |

---

## Recommendations

1. [Recommendation 1]
2. [Recommendation 2]
3. [Recommendation 3]

---

## Sign-Off

**Auditor:** security-compliance-expert
**Date:** 2026-02-07
**Status:** ✅ Approved for Production
```

---

## 🚦 Quality Gates

| Gate | Criteria | Status |
|------|----------|--------|
| **Gate 1: Initial Scan** | Bandit + Safety scans completed | ⏳ Pending |
| **Gate 2: Zero P0/P1** | All HIGH/CRITICAL vulnerabilities fixed | ⏳ Pending |
| **Gate 3: OWASP Compliance** | All 10 categories verified | ⏳ Pending |
| **Gate 4: JWT Hardening** | Token expiration, signature, secret verified | ⏳ Pending |
| **Gate 5: CI/CD Integration** | Security scans in GitHub Actions | ⏳ Pending |
| **Gate 6: Documentation** | Audit report generated | ⏳ Pending |

**All gates must be ✅ before proceeding to TASK_002.**

---

## ✅ Success Criteria

**This task is complete when ALL of the following are true:**

1. ✅ Bandit scan: 0 HIGH/CRITICAL issues
2. ✅ Safety scan: 0 CRITICAL vulnerabilities
3. ✅ OWASP Top 10: All 10 categories compliant
4. ✅ JWT authentication: Hardened (secret ≥32 chars, expiration set, HS256)
5. ✅ No hardcoded credentials found (grep scan passes)
6. ✅ GitHub Actions workflow: Security scan operational
7. ✅ Security audit report: Generated and reviewed
8. ✅ All P0/P1 vulnerabilities: Fixed and verified

---

## ⚠️ Risks & Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **Undiscovered vulnerabilities** | Low | High | Manual code review + automated scans |
| **Dependency vulnerabilities** | Medium | Medium | Safety scan + automated updates |
| **Weak JWT secrets in .env** | Medium | High | Enforce ≥32 char requirement in code |
| **CORS misconfiguration** | Low | Medium | Explicit origins, no wildcard |

---

## 📚 Resources Required

**Tools:**
- Bandit (Python security linter)
- Safety (dependency vulnerability scanner)
- jq (JSON processing)

**Documentation:**
- [OWASP Top 10 2021](https://owasp.org/Top10/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [JWT Best Practices](https://datatracker.ietf.org/doc/html/rfc8725)

**Access:**
- Backend codebase read/write
- GitHub Actions workflow creation
- Environment variable configuration

---

**Last Updated:** 2026-02-07
**Status:** 🟡 Not Started
**Next Review:** 2026-02-08 (after completion)
**Blocking:** TASK_002, TASK_003 (all backend tasks wait for security audit)
