# Security Compliance Checklist

**Project**: irStudy Medical Education Platform
**Purpose**: Pre-deployment security validation
**Status**: MANDATORY before production deployment
**Last Updated**: 2026-02-16

---

## Overview

This checklist ensures the irStudy platform meets security and compliance requirements before deployment. **ALL items must be checked** before going live.

**Compliance Frameworks**:
- HIPAA (Health Insurance Portability and Accountability Act)
- Australian Privacy Principles (APPs)
- AHPRA clinical documentation standards
- SOC 2 Type II (future consideration)

---

## Pre-Deployment Security Checklist

### 1. Credential Management

- [ ] **No hardcoded credentials** - Run `./scripts/security-audit.sh`
  - Zero hardcoded passwords in codebase
  - Zero hardcoded API keys (Anthropic, OpenAI, etc.)
  - Zero database URLs with credentials
  - Zero JWT secrets in code

- [ ] **All secrets in Vault** - Not environment variables
  - Anthropic API key: `vault kv get secret/irStudy/claude`
  - Database credentials: `vault kv get secret/irStudy/database`
  - JWT secret: `vault kv get secret/irStudy/jwt`
  - Encryption key: `vault kv get secret/irStudy/encryption`
  - Redis password: `vault kv get secret/irStudy/redis`

- [ ] **Secret rotation schedule documented**
  - API keys rotated quarterly (every 90 days)
  - Database passwords rotated monthly
  - JWT secrets rotated weekly
  - Rotation procedure in `docs/SECRETS_ROTATION.md`

### 2. Encryption

- [ ] **HTTPS enforced** - `HTTPSRedirectMiddleware` enabled
  - Middleware registered in `backend/src/main.py`
  - HTTP requests redirected to HTTPS (301)
  - Localhost/127.0.0.1 exempted for development

- [ ] **Security headers present**
  - `Strict-Transport-Security: max-age=31536000; includeSubDomains`
  - `X-Content-Type-Options: nosniff`
  - `X-Frame-Options: DENY`
  - `X-XSS-Protection: 1; mode=block`
  - `Content-Security-Policy` configured
  - `Referrer-Policy: strict-origin-when-cross-origin`

- [ ] **Database encryption at rest**
  - PostgreSQL: `pgcrypto` extension enabled
  - Sensitive columns encrypted (patient names, emails, notes)
  - Encryption key stored in Vault

- [ ] **Password hashing** - Argon2id (not MD5/SHA1)
  - Algorithm: Argon2id
  - Memory: 64 MiB
  - Iterations: 3
  - Parallelism: 4
  - Output: 32 bytes

- [ ] **Data integrity** - HMAC SHA-512
  - Sensitive data includes HMAC for tampering detection

### 3. PHI (Protected Health Information) Protection

- [ ] **PHI anonymized before external APIs** - Claude API
  - Patient names replaced with `[PATIENT]`
  - Emails hashed before logging
  - Medical record numbers (MRN) truncated
  - Dates of birth removed from API requests

- [ ] **No PHI in logs** - Sanitization implemented
  - No patient names in log files
  - No email addresses (unless hashed)
  - No medical record numbers
  - No dates of birth
  - Run: `grep -r "logger.*email\|print.*patient" backend/src/`

- [ ] **PHI access audit trail** - All access logged
  - User ID logged for every PHI access
  - Timestamp recorded
  - Action logged (read, update, delete)
  - IP address captured
  - Stored in `security_events` table

### 4. Authentication & Authorization

- [ ] **JWT expiration configured**
  - Access token: 15 minutes
  - Refresh token: 7 days
  - Tokens invalidated on logout

- [ ] **CORS configured** - Only allowed origins
  - Production: `https://irstudy.com`, `https://app.irstudy.com`
  - Development: `http://localhost:3000`
  - No wildcard `*` in production

- [ ] **Rate limiting enabled** - `slowapi` configured
  - Login: 5 attempts / 15 minutes
  - API endpoints: 100 requests / minute
  - Claude API: 10 requests / minute (expensive)

- [ ] **Session management** - Secure cookies
  - `HttpOnly` flag set
  - `Secure` flag set (HTTPS only)
  - `SameSite=Strict` for CSRF protection

### 5. Input Validation & Sanitization

- [ ] **Prompt injection prevention** - Sanitization implemented
  - User input sanitized before Claude API
  - SQL injection protection (parameterized queries)
  - XSS protection (HTML escaping)
  - Run tests: `pytest backend/tests/test_security/test_prompt_injection.py`

- [ ] **Australian terminology validation**
  - American drug names rejected (acetaminophen → paracetamol)
  - American emergency number rejected (911 → 000)
  - US measurement units rejected (mg/dL → mmol/L)

- [ ] **Data validation** - Pydantic schemas
  - All API endpoints use Pydantic models
  - Type checking enforced
  - Min/max lengths validated

### 6. Australian Medical Compliance

- [ ] **Medicare numbers validated** - Luhn algorithm
  - 10-digit format enforced
  - Checksum validated
  - Invalid Medicare numbers rejected

- [ ] **Aboriginal/TSI status captured** - 4 ABS categories
  - Aboriginal but not Torres Strait Islander
  - Torres Strait Islander but not Aboriginal
  - Both Aboriginal and Torres Strait Islander
  - Neither Aboriginal nor Torres Strait Islander

- [ ] **PBS medication codes validated**
  - PBS codes checked against official list
  - Authority requirements enforced
  - Max 5 repeats validated

- [ ] **MBS pathology item numbers validated**
  - Item numbers checked against MBS schedule
  - Appropriateness validated by Claude AI

- [ ] **Australian drug names enforced**
  - Paracetamol (not acetaminophen)
  - Salbutamol (not albuterol)
  - Adrenaline (not epinephrine)
  - 000 emergency number (not 911)

- [ ] **eTG/AMH/AHPRA guidelines referenced**
  - RAG system includes eTG (Therapeutic Guidelines)
  - AMH (Australian Medicines Handbook) cited
  - AHPRA clinical documentation standards followed

- [ ] **AMC Clinical Examination rubric** - Not ICRP
  - OSCE scoring uses AMC 15-mark rubric
  - Communication: 0-3 marks
  - Clinical reasoning: 0-4 marks
  - Physical examination: 0-4 marks
  - Professionalism: 0-2 marks
  - Management: 0-2 marks

### 7. Testing & Quality Assurance

- [ ] **Security tests passing** - 100% pass rate
  - Run: `pytest backend/tests/test_security/ -v`
  - `test_no_hardcoded_credentials` PASSED
  - `test_https_redirect` PASSED
  - `test_security_headers` PASSED
  - `test_phi_anonymization` PASSED
  - `test_encryption` PASSED
  - `test_prompt_injection` PASSED

- [ ] **Test coverage ≥70%** - Unit + integration
  - Run: `pytest --cov=backend/src --cov-report=html`
  - Security module: ≥80% coverage
  - Authentication: ≥90% coverage

- [ ] **E2E tests passing** - Playwright
  - Login flow tested
  - EMR practice session tested
  - Validation API tested

### 8. Monitoring & Incident Response

- [ ] **Audit logging enabled** - All PHI access logged
  - `security_events` table created
  - Log retention: 7 years (HIPAA requirement)
  - Log shipping to SIEM configured

- [ ] **Intrusion detection** - Failed login alerts
  - >5 failed logins → Alert
  - Suspicious API usage → Alert
  - Unauthorized PHI access → Alert

- [ ] **Incident response plan documented**
  - Breach notification procedure (72 hours)
  - Contact list (CTO, Legal, Compliance)
  - Forensics preservation procedure

- [ ] **Backup & disaster recovery**
  - Daily encrypted backups
  - 30-day retention
  - Restore tested monthly

### 9. Documentation

- [ ] **Security runbook created** - `docs/SECURITY_RUNBOOK.md`
  - Incident response procedures
  - Secret rotation procedures
  - Audit log review procedures

- [ ] **Vault integration documented** - `docs/VAULT_INTEGRATION.md`
  - Setup instructions
  - Usage examples
  - Troubleshooting guide

- [ ] **Compliance checklist (this file)** - Reviewed quarterly

### 10. Production Deployment

- [ ] **Environment variables configured**
  - `ENV=production`
  - `VAULT_ADDR=https://vault.irstudy.com:8200`
  - `VAULT_TOKEN` set (not in .env file)
  - `DATABASE_URL` not set (retrieved from Vault)

- [ ] **HTTPS certificate installed** - Let's Encrypt or paid cert
  - Valid certificate chain
  - Auto-renewal configured
  - HSTS preload submitted

- [ ] **Firewall rules configured**
  - Only ports 80, 443 exposed
  - Database port not publicly accessible
  - Vault port restricted to backend servers

- [ ] **Security audit completed** - `./scripts/security-audit.sh`
  - Zero violations detected
  - Report archived
  - Sign-off by Security Lead

---

## Quick Validation Commands

```bash
# 1. Run security audit
./scripts/security-audit.sh

# 2. Run security tests
cd /home/dev/Development/irStudy/backend
source venv/bin/activate
pytest tests/test_security/ -v

# 3. Check Vault secrets
vault kv list secret/irStudy
vault kv get secret/irStudy/claude
vault kv get secret/irStudy/database

# 4. Verify HTTPS redirect
curl -I http://irstudy.com
# Expected: HTTP/1.1 301 Moved Permanently
# Location: https://irstudy.com

# 5. Check security headers
curl -I https://irstudy.com
# Expected: Strict-Transport-Security, X-Frame-Options, etc.

# 6. Test PHI anonymization
pytest backend/tests/test_security/test_phi_anonymizer.py -v

# 7. Test prompt injection prevention
pytest backend/tests/test_security/test_prompt_injection.py -v
```

---

## Sign-Off

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Security Lead | ___________ | ___________ | ______ |
| CTO | ___________ | ___________ | ______ |
| Compliance Officer | ___________ | ___________ | ______ |
| Legal Counsel | ___________ | ___________ | ______ |

---

## References

- [HIPAA Security Rule](https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- [Australian Privacy Principles](https://www.oaic.gov.au/privacy/australian-privacy-principles)
- [AHPRA Standards](https://www.ahpra.gov.au/Publications/Codes-Guidelines.aspx)
- Project: `docs/HIPAA_COMPLIANCE.md`
- Project: `docs/VAULT_INTEGRATION.md`
- Project: `docs/SECURITY_RUNBOOK.md`

---

**Last Reviewed**: 2026-02-16
**Next Review Due**: 2026-05-16 (Quarterly)
