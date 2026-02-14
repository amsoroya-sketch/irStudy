# irStudy Medical Education Platform
## Extended Implementation Plan with Security, Compliance & Validation

**Version:** 3.0 (Extended)
**Date:** 2026-02-06
**Status:** Production-Ready Tactical Plan
**Based On:** COMPREHENSIVE_PLATFORM_PLAN.md + Security Framework Integration

---

## 📋 EXECUTIVE SUMMARY

This document extends the original comprehensive plan with:

1. **Security Framework Integration** - Leveraging existing cyberSecurity/ infrastructure
2. **Content Validation Workflow** - Phase 0 quality assurance before launch
3. **Citation UI/UX Specifications** - Detailed component designs
4. **Copyright & Legal Compliance** - Risk mitigation strategies
5. **Realistic Timeline Extensions** - 28 weeks vs original 14 weeks
6. **AI Validation Protocols** - Medical education assessment standards
7. **Agent OS Integration** - Expert agent delegation framework

### Critical Changes from Original Plan

| Aspect | Original Plan | Extended Plan |
|--------|--------------|---------------|
| **Timeline** | 14 weeks | 28 weeks (7 months) |
| **Phases** | 3 phases | 4 phases (added Phase 0) |
| **Security** | Mentioned | Fully integrated |
| **Content QA** | Assumed ready | 4-week validation process |
| **Citations** | "Show citations" | Detailed UI/UX spec |
| **Copyright** | Not addressed | Legal compliance framework |
| **Testing** | Not specified | 100% pass rate requirement |

---

## 🔒 PART 1: SECURITY FRAMEWORK INTEGRATION

### 1.1 Security Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SECURITY LAYERS (Defense in Depth)                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  LAYER 1: AUTHENTICATION & IDENTITY                                         │
│  ├── Provider: Clerk (HIPAA-compliant tier)                                │
│  ├── Features:                                                             │
│  │   ├── Email + Password (primary)                                        │
│  │   ├── Social Login (Google, Apple, Microsoft)                           │
│  │   ├── MFA (TOTP) - Required for Ultimate tier                           │
│  │   ├── Device fingerprinting                                             │
│  │   └── Session management (JWT + refresh tokens)                         │
│  ├── Session Security:                                                     │
│  │   ├── Access Token: 15 minutes expiry                                   │
│  │   ├── Refresh Token: 7 days (HTTP-only cookie)                          │
│  │   ├── Concurrent Session Limit: 3 devices (Pro), 5 (Ultimate)           │
│  │   └── Automatic logout on suspicious activity                           │
│  └── Password Policy:                                                      │
│      ├── Minimum 8 characters                                              │
│      ├── Must include: uppercase, lowercase, number                        │
│      ├── Cannot reuse last 5 passwords                                     │
│      ├── Account lockout: 5 failed attempts = 15min freeze                 │
│      └── Password reset: Email link (24h expiry)                           │
│                                                                             │
│  LAYER 2: AUTHORIZATION & ACCESS CONTROL                                    │
│  ├── Role-Based Access Control (RBAC):                                     │
│  │   ├── User Roles:                                                       │
│  │   │   ├── Free (read-only, 200 MCQs)                                    │
│  │   │   ├── Pro (full content access)                                     │
│  │   │   ├── Ultimate (+ AI features)                                      │
│  │   │   ├── Institutional Admin (cohort management)                       │
│  │   │   └── Super Admin (platform management)                             │
│  │   └── Feature Gates:                                                    │
│  │       ├── MCQ access: Role-based limits                                 │
│  │       ├── AI Tutor: Query limits (100/mo Pro, unlimited Ultimate)       │
│  │       ├── EMR Practice: Pro+ only                                       │
│  │       └── AI Simulation: Ultimate only                                  │
│  ├── API Authorization:                                                    │
│  │   ├── Bearer token validation on every request                          │
│  │   ├── Rate limiting (100 req/min per user)                              │
│  │   └── IP-based throttling (1000 req/min per IP)                         │
│  └── Content Access Control:                                               │
│      ├── Database-level row security (PostgreSQL RLS)                      │
│      ├── Content encryption at rest (AES-256)                              │
│      └── Audit trail for all content access                                │
│                                                                             │
│  LAYER 3: DATA PROTECTION & PRIVACY                                         │
│  ├── Encryption:                                                           │
│  │   ├── At Rest: AES-256 (database, file storage)                         │
│  │   ├── In Transit: TLS 1.3 (all API calls)                               │
│  │   └── Secrets: AWS Secrets Manager / HashiCorp Vault                    │
│  ├── Personal Data Handling:                                               │
│  │   ├── PII Storage: Name, email, country (encrypted)                     │
│  │   ├── Study Data: Progress, scores (anonymized for analytics)           │
│  │   ├── GDPR Compliance:                                                  │
│  │   │   ├── Right to access (export all user data)                        │
│  │   │   ├── Right to deletion (30-day retention)                          │
│  │   │   ├── Data portability (JSON export)                                │
│  │   │   └── Consent management (marketing opt-in/out)                     │
│  │   └── Australian Privacy Principles (APP):                              │
│  │       ├── Notification of collection                                    │
│  │       ├── Data minimization (only collect necessary)                    │
│  │       └── Overseas disclosure (if using US cloud)                       │
│  └── Medical Data Protection:                                              │
│      ├── User study history: Not considered PHI (no patient data)          │
│      ├── EMR practice scenarios: Fictional patients only                   │
│      └── No real patient data stored                                       │
│                                                                             │
│  LAYER 4: APPLICATION SECURITY                                              │
│  ├── Frontend Security:                                                    │
│  │   ├── Content Security Policy (CSP)                                     │
│  │   ├── XSS Protection (React auto-escaping + DOMPurify)                  │
│  │   ├── CSRF Protection (SameSite cookies)                                │
│  │   └── Subresource Integrity (SRI) for CDN assets                        │
│  ├── Backend Security:                                                     │
│  │   ├── Input Validation: Pydantic schemas (FastAPI)                      │
│  │   ├── SQL Injection Prevention: Parameterized queries (SQLAlchemy)      │
│  │   ├── Command Injection Prevention: No shell execution                  │
│  │   └── Path Traversal Prevention: Whitelist file paths                   │
│  ├── API Security:                                                         │
│  │   ├── CORS: Whitelist origins only                                      │
│  │   ├── Rate Limiting: Redis-based (100 req/min)                          │
│  │   ├── Request Size Limits: 10MB max                                     │
│  │   └── API Versioning: /api/v1/ for stability                            │
│  └── Dependency Security:                                                  │
│      ├── Automated scanning: Snyk / Dependabot                             │
│      ├── Weekly updates for critical CVEs                                  │
│      ├── Pin versions in requirements.txt / package.json                   │
│      └── Quarterly security audits                                         │
│                                                                             │
│  LAYER 5: INFRASTRUCTURE SECURITY                                           │
│  ├── Network Security:                                                     │
│  │   ├── VPC isolation (AWS / Railway)                                     │
│  │   ├── Security groups (least privilege)                                 │
│  │   ├── WAF (Web Application Firewall) - Cloudflare                       │
│  │   └── DDoS protection - Cloudflare                                      │
│  ├── Database Security:                                                    │
│  │   ├── PostgreSQL: Private subnet only                                   │
│  │   ├── No public internet access                                         │
│  │   ├── Encryption at rest (AWS RDS encryption)                           │
│  │   ├── Automated backups (daily, 30-day retention)                       │
│  │   └── Point-in-time recovery enabled                                    │
│  ├── Secrets Management:                                                   │
│  │   ├── Never commit secrets to git                                       │
│  │   ├── Environment variables via platform (Vercel, Railway)              │
│  │   ├── Rotation: 90-day password rotation                                │
│  │   └── Audit logs for secret access                                      │
│  └── Monitoring & Alerting:                                                │
│      ├── Security Logs: CloudWatch / Datadog                               │
│      ├── Failed login alerts (5+ failures)                                 │
│      ├── Unusual API patterns (Sentry)                                     │
│      └── Weekly security reports                                           │
│                                                                             │
│  LAYER 6: COMPLIANCE & AUDIT                                                │
│  ├── HIPAA Compliance (if applicable):                                     │
│  │   ├── Business Associate Agreement (BAA) with vendors                   │
│  │   ├── Clerk: HIPAA-compliant tier                                       │
│  │   ├── Stripe: HIPAA-compliant payment processing                        │
│  │   ├── AWS: BAA required for RDS/S3                                      │
│  │   └── Audit logs: 6-year retention                                      │
│  ├── Australian Privacy Act Compliance:                                    │
│  │   ├── Privacy policy published                                          │
│  │   ├── Data breach notification (72h to OAIC)                            │
│  │   └── Cross-border disclosure notices                                   │
│  ├── PCI DSS Compliance:                                                   │
│  │   ├── Stripe handles all card data (SAQ A)                              │
│  │   ├── No card data stored on our servers                                │
│  │   └── Annual PCI compliance review                                      │
│  └── Security Audits:                                                      │
│      ├── Quarterly penetration testing                                     │
│      ├── Annual third-party security audit                                 │
│      ├── Vulnerability disclosure program                                  │
│      └── Bug bounty program (post-launch)                                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Integration with Existing cyberSecurity/ Framework

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    EXISTING SECURITY ASSETS INTEGRATION                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Your Project Already Has:                                                 │
│  ├── cyberSecurity/ folder (security compliance docs)                      │
│  ├── Security scanning infrastructure                                      │
│  └── Credential scanning hooks                                             │
│                                                                             │
│  INTEGRATION PLAN:                                                          │
│                                                                             │
│  1. Pre-Commit Hooks (Git Hooks)                                           │
│     ├── Location: .git/hooks/pre-commit                                    │
│     ├── Function: Scan for hardcoded credentials                           │
│     ├── Tools:                                                             │
│     │   ├── git-secrets (AWS credentials)                                  │
│     │   ├── detect-secrets (generic secrets)                               │
│     │   └── Custom regex for API keys                                      │
│     ├── What's Blocked:                                                    │
│     │   ├── API keys (ANTHROPIC_API_KEY, OPENAI_API_KEY)                   │
│     │   ├── Database credentials (postgres://...)                          │
│     │   ├── JWT secrets                                                    │
│     │   └── Any string matching secret patterns                            │
│     └── Exit Code: 1 (blocks commit if secrets found)                      │
│                                                                             │
│  2. CI/CD Security Scanning                                                │
│     ├── GitHub Actions / GitLab CI                                         │
│     ├── Steps:                                                             │
│     │   ├── Dependency scanning (npm audit, safety)                        │
│     │   ├── SAST (Static Analysis) - Semgrep                               │
│     │   ├── Container scanning - Trivy                                     │
│     │   └── License compliance check                                       │
│     └── Failure: Block PR merge if critical CVEs                           │
│                                                                             │
│  3. Environment Variable Management                                         │
│     ├── Development: .env.local (gitignored)                               │
│     ├── Staging: Vercel/Railway env vars                                   │
│     ├── Production: AWS Secrets Manager                                    │
│     └── Template: .env.example (safe to commit)                            │
│                                                                             │
│  4. Security Documentation                                                  │
│     ├── SECURITY.md (vulnerability disclosure policy)                      │
│     ├── CONTRIBUTING.md (security guidelines)                              │
│     └── cyberSecurity/README.md (internal policies)                        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.3 Security Implementation Checklist

**Phase 0: Security Foundation (Week 1)**

- [ ] Set up Clerk authentication
  - [ ] Create Clerk account (HIPAA tier if storing medical data)
  - [ ] Configure social login providers (Google, Apple, Microsoft)
  - [ ] Set password policy
  - [ ] Enable MFA for Ultimate tier
  - [ ] Configure session management

- [ ] Set up Stripe payments
  - [ ] Create Stripe account
  - [ ] Configure products (Free, Pro, Ultimate, Institutional)
  - [ ] Set up webhooks for subscription events
  - [ ] Test payment flow in test mode
  - [ ] Enable fraud detection (Radar)

- [ ] Database security hardening
  - [ ] Enable PostgreSQL encryption at rest (AWS RDS)
  - [ ] Configure Row-Level Security (RLS) policies
  - [ ] Create database users with least privilege
  - [ ] Set up automated backups (daily)
  - [ ] Test point-in-time recovery

- [ ] Install pre-commit hooks
  - [ ] Install git-secrets: `brew install git-secrets`
  - [ ] Configure patterns: `git secrets --add 'API_KEY.*'`
  - [ ] Test: Try committing a fake secret
  - [ ] Document in CONTRIBUTING.md

- [ ] Configure security monitoring
  - [ ] Set up Sentry for error tracking
  - [ ] Configure CloudWatch logs (AWS)
  - [ ] Create alerts for failed logins (5+ failures)
  - [ ] Set up uptime monitoring (UptimeRobot)

**Phase 1-3: Ongoing Security (Weeks 2-28)**

- [ ] Weekly dependency updates
  - [ ] Run `npm audit` / `pip-audit`
  - [ ] Update critical CVEs within 48h
  - [ ] Test after updates

- [ ] Monthly security reviews
  - [ ] Review access logs for anomalies
  - [ ] Check for new user roles needed
  - [ ] Update security documentation

- [ ] Quarterly penetration testing
  - [ ] Hire external security firm (e.g., Cobalt, Bugcrowd)
  - [ ] Test authentication flows
  - [ ] Test API endpoints for injection
  - [ ] Remediate findings within 30 days

---

## 📊 PART 2: CONTENT VALIDATION & QUALITY ASSURANCE

### 2.1 Phase 0: Content Quality Assurance (NEW - 4 Weeks)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PHASE 0: CONTENT VALIDATION WORKFLOW                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  GOAL: Validate all 18,000+ MCQs + 3,000+ OSCEs before ANY user-facing     │
│        platform development. Ensure 100% citation coverage and clinical     │
│        accuracy.                                                            │
│                                                                             │
│  DURATION: 4 weeks (before Phase 1)                                         │
│  RESOURCES: 1 dev + 1 medical reviewer (part-time)                          │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  WEEK 1: AUTOMATED VALIDATION                                       │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │                                                                      │   │
│  │  Task 1.1: RAG Citation Validation (Days 1-3)                       │   │
│  │  ├── Script: scripts/validate_rag_facts.py (already exists)         │   │
│  │  ├── Process:                                                       │   │
│  │  │   ├── For each MCQ explanation:                                  │   │
│  │  │   │   ├── Extract medical facts                                  │   │
│  │  │   │   ├── Query Qdrant vector DB (42,647 chunks)                 │   │
│  │  │   │   ├── Match fact → source chunk                              │   │
│  │  │   │   └── Record: source, page, confidence score                 │   │
│  │  │   ├── Generate report: citation_validation_report.json           │   │
│  │  │   └── Flag items with <80% confidence                            │   │
│  │  ├── Expected Output:                                               │   │
│  │  │   ├── 18,000 MCQs × 3 citations = 54,000 fact validations        │   │
│  │  │   ├── ~15% flagged for manual review (~8,100 facts)              │   │
│  │  │   └── Estimated time: 3 days (automated)                         │   │
│  │  └── Acceptance Criteria:                                           │   │
│  │      ├── 100% of MCQs have attempted citation match                 │   │
│  │      ├── Confidence scores recorded for all                         │   │
│  │      └── Flagged items exported to review queue                     │   │
│  │                                                                      │   │
│  │  Task 1.2: Australian Compliance Check (Days 4-5)                   │   │
│  │  ├── Script: scripts/validate_australian_compliance.py              │   │
│  │  ├── Checks:                                                        │   │
│  │  │   ├── Drug names: Generic (not brand) unless PBS-specific        │   │
│  │  │   ├── Guidelines: eTG/AMH/RACGP citations present                │   │
│  │  │   ├── Terminology: Australian spelling (e.g., "paediatric")      │   │
│  │  │   ├── Units: SI units (mg/L, not mg/dL)                          │   │
│  │  │   └── Coding: MBS item numbers (not CPT codes)                   │   │
│  │  ├── Expected Output:                                               │   │
│  │  │   ├── Compliance report: australian_compliance_report.json       │   │
│  │  │   ├── ~5% non-compliant items flagged (~900 MCQs)                │   │
│  │  │   └── Estimated time: 2 days (automated)                         │   │
│  │  └── Acceptance Criteria:                                           │   │
│  │      ├── All medications checked against PBS                        │   │
│  │      ├── All clinical guidelines verified as Australian             │   │
│  │      └── Non-compliant items queued for correction                  │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  WEEK 2: MANUAL REVIEW (SAMPLING)                                   │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │                                                                      │   │
│  │  Task 2.1: Clinical Accuracy Review (Days 1-5)                      │   │
│  │  ├── Reviewer: Medical professional (GP or specialist)              │   │
│  │  ├── Sample Size: 500 MCQs (stratified random sample)               │   │
│  │  │   ├── 25 MCQs per specialty (18 specialties)                     │   │
│  │  │   ├── Include high-risk topics (emergency, pharmacology)         │   │
│  │  │   └── Oversample flagged items from Week 1                       │   │
│  │  ├── Review Criteria:                                               │   │
│  │  │   ├── Is the question stem clinically accurate?                  │   │
│  │  │   ├── Are all answer options plausible?                          │   │
│  │  │   ├── Is the correct answer defensible?                          │   │
│  │  │   ├── Is the explanation clear and evidence-based?               │   │
│  │  │   └── Are citations relevant and accurate?                       │   │
│  │  ├── Review Tool:                                                   │   │
│  │  │   ├── Custom review interface (React app)                        │   │
│  │  │   ├── Show MCQ + citations side-by-side                          │   │
│  │  │   ├── Reviewer marks: Pass / Fail / Needs Revision               │   │
│  │  │   └── Comments field for specific issues                         │   │
│  │  ├── Expected Output:                                               │   │
│  │  │   ├── Review report: clinical_accuracy_review.json               │   │
│  │  │   ├── Pass rate target: >95% (i.e., <25 failures)                │   │
│  │  │   ├── Failed items: Queued for regeneration                      │   │
│  │  │   └── Estimated time: 1 week (25 MCQs/day)                       │   │
│  │  └── Acceptance Criteria:                                           │   │
│  │      ├── All 500 sampled MCQs reviewed                              │   │
│  │      ├── Pass rate ≥95%                                             │   │
│  │      └── If <95%, expand sample and re-review                       │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  WEEK 3: REMEDIATION                                                │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │                                                                      │   │
│  │  Task 3.1: Fix Flagged Items (Days 1-5)                             │   │
│  │  ├── Input: Combined list from Weeks 1-2                            │   │
│  │  │   ├── Low-confidence citations (~8,100 facts)                    │   │
│  │  │   ├── Non-compliant items (~900 MCQs)                            │   │
│  │  │   └── Failed clinical review (~25 MCQs)                          │   │
│  │  │   TOTAL: ~9,000 items needing attention                          │   │
│  │  ├── Triage:                                                        │   │
│  │  │   ├── Critical (failed clinical review): Fix immediately         │   │
│  │  │   ├── High (non-compliant): Fix before launch                    │   │
│  │  │   └── Medium (low confidence): Improve or flag as "pending"      │   │
│  │  ├── Remediation Process:                                           │   │
│  │  │   ├── Critical: Regenerate with Claude 3.5 Sonnet                │   │
│  │  │   ├── High: Manual correction + re-validation                    │   │
│  │  │   └── Medium: Add "Citation verification in progress" note       │   │
│  │  ├── Expected Output:                                               │   │
│  │  │   ├── All critical items fixed (25 MCQs)                         │   │
│  │  │   ├── 80%+ high-priority items fixed (~720 MCQs)                 │   │
│  │  │   ├── Medium items flagged for Phase 1 improvement               │   │
│  │  │   └── Updated database with corrections                          │   │
│  │  └── Acceptance Criteria:                                           │   │
│  │      ├── Zero clinically inaccurate MCQs in production              │   │
│  │      ├── 100% Australian compliance for drug names/guidelines       │   │
│  │      └── >85% citation confidence for launch content                │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  WEEK 4: COPYRIGHT CLEARANCE                                        │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │                                                                      │   │
│  │  Task 4.1: Copyright Risk Assessment (Days 1-2)                     │   │
│  │  ├── Review Source Materials:                                       │   │
│  │  │   ├── AMC Handbook of Clinical Assessment (copyrighted)          │   │
│  │  │   ├── Talley & O'Connor Clinical Examination (copyrighted)       │   │
│  │  │   ├── Oxford Handbook Emergency Medicine (copyrighted)           │   │
│  │  │   ├── eTG Complete (subscription required, may be OK)            │   │
│  │  │   └── RACGP Guidelines (public domain, OK)                       │   │
│  │  ├── Risk Analysis:                                                 │   │
│  │  │   ├── Are we copying verbatim or paraphrasing?                   │   │
│  │  │   ├── Does this qualify as "fair use" (education)?               │   │
│  │  │   ├── Do we need licensing agreements?                           │   │
│  │  │   └── Could publishers issue DMCA takedown?                      │   │
│  │  ├── Expected Output:                                               │   │
│  │  │   ├── Copyright assessment report                                │   │
│  │  │   ├── List of high-risk sources                                  │   │
│  │  │   └── Recommended actions (license, remove, paraphrase)          │   │
│  │  └── Acceptance Criteria:                                           │   │
│  │      ├── Clear legal risk assessment for each source                │   │
│  │      └── Mitigation plan documented                                 │   │
│  │                                                                      │   │
│  │  Task 4.2: Licensing & Legal (Days 3-5)                             │   │
│  │  ├── Option 1: Fair Use Defense                                     │   │
│  │  │   ├── Consult IP lawyer (AUD $2K-5K)                             │   │
│  │  │   ├── Document fair use rationale:                               │   │
│  │  │   │   ├── Educational purpose ✓                                  │   │
│  │  │   │   ├── Transformative (questions, not copying text) ✓         │   │
│  │  │   │   ├── Small portions of original work ✓                      │   │
│  │  │   │   └── No market substitution (we're selling service) ✓       │   │
│  │  │   └── Get legal opinion in writing                               │   │
│  │  ├── Option 2: Licensing Agreements                                 │   │
│  │  │   ├── Contact publishers:                                        │   │
│  │  │   │   ├── Elsevier (Talley & O'Connor)                           │   │
│  │  │   │   ├── Oxford University Press (Oxford Handbook)              │   │
│  │  │   │   └── AMC (AMC Handbook)                                     │   │
│  │  │   ├── Negotiate licensing fees (budget: $5K-20K/yr)              │   │
│  │  │   └── Get written permission                                     │   │
│  │  ├── Option 3: Source Replacement                                   │   │
│  │  │   ├── Remove copyrighted sources from RAG                        │   │
│  │  │   ├── Use only public domain sources:                            │   │
│  │  │   │   ├── eTG (with subscription)                                │   │
│  │  │   │   ├── RACGP Guidelines (free)                                │   │
│  │  │   │   ├── NSW Health Guidelines (free)                           │   │
│  │  │   │   ├── Cochrane Reviews (open access)                         │   │
│  │  │   │   └── StatPearls (public domain)                             │   │
│  │  │   └── Regenerate MCQs using only these sources                   │   │
│  │  ├── Expected Output:                                               │   │
│  │  │   ├── Legal opinion OR licensing agreements OR source cleanup    │   │
│  │  │   ├── Updated RAG database (if Option 3)                         │   │
│  │  │   └── Copyright compliance certificate                           │   │
│  │  └── Acceptance Criteria:                                           │   │
│  │      ├── Legal risk mitigated to acceptable level                   │   │
│  │      ├── Documentation for any licensing agreements                 │   │
│  │      └── Platform can launch without copyright liability            │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  PHASE 0 DELIVERABLES:                                                      │
│  ├── ✅ Citation Validation Report (54,000 facts validated)                │
│  ├── ✅ Australian Compliance Report (18,000 MCQs checked)                 │
│  ├── ✅ Clinical Accuracy Review (500 MCQs manually reviewed, >95% pass)   │
│  ├── ✅ Remediation Report (critical issues fixed)                         │
│  ├── ✅ Copyright Clearance (legal opinion or licenses)                    │
│  └── ✅ VALIDATED CONTENT DATABASE ready for import to production          │
│                                                                             │
│  BUDGET:                                                                    │
│  ├── Medical reviewer: $2,000 (1 week part-time at $100/hr × 20h)          │
│  ├── Legal consultation: $3,000 (IP lawyer review)                         │
│  ├── Licensing (optional): $5,000-20,000/yr (if needed)                    │
│  └── TOTAL: $5,000-25,000 one-time + potential annual licensing            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Ongoing Content Quality Process

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CONTINUOUS QUALITY ASSURANCE (POST-LAUNCH)                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  User Feedback Loop:                                                        │
│  ├── Feature: "Report an Issue" button on every MCQ                         │
│  ├── Categories:                                                            │
│  │   ├── Incorrect answer                                                   │
│  │   ├── Outdated guideline                                                 │
│  │   ├── Unclear explanation                                                │
│  │   └── Missing/wrong citation                                             │
│  ├── Process:                                                               │
│  │   ├── User submits report → Stored in database                           │
│  │   ├── Admin reviews weekly                                               │
│  │   ├── If valid: Flag for correction                                      │
│  │   └── Corrected MCQ re-validated before republishing                     │
│  └── SLA: Critical errors fixed within 48h, minor issues within 2 weeks     │
│                                                                             │
│  Quarterly Content Audits:                                                  │
│  ├── Sample 100 random MCQs                                                 │
│  ├── Check for guideline updates (eTG releases new version)                 │
│  ├── Re-validate citations against latest sources                           │
│  └── Update outdated content                                                │
│                                                                             │
│  Performance Analytics:                                                     │
│  ├── Track MCQ difficulty (% users getting wrong)                           │
│  ├── Flag outliers:                                                         │
│  │   ├── Too easy (>90% correct) → Review if question is ambiguous          │
│  │   ├── Too hard (<30% correct) → Review if answer is wrong                │
│  │   └── High skip rate → Review if question is unclear                     │
│  └── Monthly review meeting to discuss outliers                             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🎨 PART 3: CITATION UI/UX SPECIFICATIONS

### 3.1 Citation Display Component Design

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CITATION COMPONENT SPECIFICATIONS                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Component Name: CitationPanel                                              │
│  Location: src/components/mcq/CitationPanel.tsx                             │
│  Purpose: Display 3 evidence-based citations per MCQ explanation            │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  VISUAL DESIGN (Figma Mockup)                                       │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │                                                                      │   │
│  │  ┌──────────────────────────────────────────────────────────────┐   │   │
│  │  │  📚 Evidence Base                                            │   │   │
│  │  ├──────────────────────────────────────────────────────────────┤   │   │
│  │  │                                                              │   │   │
│  │  │  This answer is supported by current Australian guidelines: │   │   │
│  │  │                                                              │   │   │
│  │  │  [1] eTG Complete (March 2024)                              │   │   │
│  │  │      Cardiovascular Expert Group                            │   │   │
│  │  │      "Atrial Fibrillation Management" → Page 147            │   │   │
│  │  │      🔍 View Source  ✓ RAG Verified (92% confidence)        │   │   │
│  │  │                                                              │   │   │
│  │  │  [2] Australian Medicines Handbook (2024)                   │   │   │
│  │  │      Chapter: Cardiovascular Drugs                          │   │   │
│  │  │      Section: Oral Anticoagulants → Page 123                │   │   │
│  │  │      🔍 View Source  ✓ RAG Verified (88% confidence)        │   │   │
│  │  │                                                              │   │   │
│  │  │  [3] RACGP Guidelines (Updated 2023)                        │   │   │
│  │  │      Red Book - Part 3: Clinical Guidelines                 │   │   │
│  │  │      AF Stroke Prevention → Page 67                         │   │   │
│  │  │      🔍 View Source  ✓ RAG Verified (95% confidence)        │   │   │
│  │  │                                                              │   │   │
│  │  │  ℹ️ All citations verified against original source texts    │   │   │
│  │  │     using retrieval-augmented generation (RAG).             │   │   │
│  │  │                                                              │   │   │
│  │  └──────────────────────────────────────────────────────────────┘   │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  DATA STRUCTURE                                                     │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │                                                                      │   │
│  │  interface Citation {                                               │   │
│  │    id: string;                                                      │   │
│  │    source_name: string;          // "eTG Complete"                  │   │
│  │    edition: string;               // "March 2024"                   │   │
│  │    author_org: string;            // "Cardiovascular Expert Group"  │   │
│  │    chapter_section: string;       // "Atrial Fibrillation Mgmt"     │   │
│  │    page_number: number;           // 147                            │   │
│  │    url?: string;                  // Deep link to eTG (if avail)    │   │
│  │    rag_verified: boolean;         // true if matched in Qdrant      │   │
│  │    confidence_score: number;      // 0.92 (92% similarity)          │   │
│  │    verification_date: string;     // "2026-02-06"                   │   │
│  │    chunk_id?: string;             // Qdrant vector ID               │   │
│  │  }                                                                   │   │
│  │                                                                      │   │
│  │  interface MCQWithCitations {                                       │   │
│  │    id: string;                                                      │   │
│  │    question: string;                                                │   │
│  │    options: Option[];                                               │   │
│  │    correct_answer: string;                                          │   │
│  │    explanation: string;                                             │   │
│  │    citations: Citation[];         // EXACTLY 3 citations            │   │
│  │    citation_status: "complete" | "partial" | "pending";             │   │
│  │  }                                                                   │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  INTERACTION STATES                                                 │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │                                                                      │   │
│  │  STATE 1: Complete (3 verified citations)                           │   │
│  │    • Show all 3 citations                                           │   │
│  │    • Green checkmark ✓ for RAG-verified                             │   │
│  │    • Confidence score in tooltip                                    │   │
│  │    • "View Source" button opens modal                               │   │
│  │                                                                      │   │
│  │  STATE 2: Partial (1-2 citations)                                   │   │
│  │    • Show available citations                                       │   │
│  │    • Warning icon ⚠️ "Additional citations pending review"          │   │
│  │    • Still allow user to proceed                                    │   │
│  │                                                                      │   │
│  │  STATE 3: Pending (0 citations)                                     │   │
│  │    • Show placeholder:                                              │   │
│  │      "📝 Citations for this question are under review.              │   │
│  │       This content has been clinically validated but                │   │
│  │       source verification is in progress."                          │   │
│  │    • Don't show "Evidence Base" section                             │   │
│  │                                                                      │   │
│  │  STATE 4: Citation Modal (when "View Source" clicked)               │   │
│  │    ┌────────────────────────────────────────────────────────────┐   │   │
│  │    │  📖 Source: eTG Complete March 2024                       │   │   │
│  │    ├────────────────────────────────────────────────────────────┤   │   │
│  │    │                                                            │   │   │
│  │    │  Full Reference:                                           │   │   │
│  │    │  Therapeutic Guidelines Ltd. (2024). eTG Complete.         │   │   │
│  │    │  Melbourne: Therapeutic Guidelines Limited.                │   │   │
│  │    │  Cardiovascular Expert Group.                              │   │   │
│  │    │  Chapter: Atrial Fibrillation Management, Page 147.        │   │   │
│  │    │                                                            │   │   │
│  │    │  Verified Excerpt (from RAG database):                     │   │   │
│  │    │  "Before initiating rhythm or rate control strategies      │   │   │
│  │    │   in atrial fibrillation, stroke risk stratification       │   │   │
│  │    │   using the CHA₂DS₂-VASc score is essential..."            │   │   │
│  │    │                                                            │   │   │
│  │    │  RAG Verification:                                         │   │   │
│  │    │  • Matched Chunk ID: etg-2024-cardio-147-chunk-3           │   │   │
│  │    │  • Similarity Score: 92%                                   │   │   │
│  │    │  • Verified: 2026-02-06                                    │   │   │
│  │    │                                                            │   │   │
│  │    │  [Close]  [Report Issue with Citation]                    │   │   │
│  │    └────────────────────────────────────────────────────────────┘   │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  ACCESSIBILITY (WCAG 2.1 AA)                                        │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │  • Semantic HTML: <cite> tags for citations                         │   │
│  │  • ARIA labels: aria-label="Citation 1 of 3"                        │   │
│  │  • Keyboard navigation: Tab through citations, Enter to open modal  │   │
│  │  • Screen reader: Read full citation text                           │   │
│  │  • Color contrast: 4.5:1 minimum (green checkmark on white bg)      │   │
│  │  • Focus indicators: 2px outline on keyboard focus                  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  RESPONSIVE DESIGN                                                  │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │  Desktop (>1024px):                                                 │   │
│  │    • Full citation display (3 citations stacked)                    │   │
│  │    • "View Source" buttons inline                                   │   │
│  │                                                                      │   │
│  │  Tablet (768-1024px):                                               │   │
│  │    • Slightly condensed (hide author/org line)                      │   │
│  │    • Citations still visible                                        │   │
│  │                                                                      │   │
│  │  Mobile (<768px):                                                   │   │
│  │    • Accordion: Click "📚 Evidence (3)" to expand                   │   │
│  │    • Show citation titles only, tap to see details                  │   │
│  │    • "View Source" opens full-screen modal                          │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Citation Management API

```typescript
// Backend API Endpoint
POST /api/v1/mcqs/{mcq_id}/validate-citations

Request:
{
  "mcq_id": "cardio_af_001",
  "explanation": "Before rhythm control, assess stroke risk with CHA₂DS₂-VASc...",
  "force_revalidation": false  // Optional: re-run RAG validation
}

Response:
{
  "mcq_id": "cardio_af_001",
  "citations": [
    {
      "id": "cit_001",
      "source_name": "eTG Complete",
      "edition": "March 2024",
      "author_org": "Cardiovascular Expert Group",
      "chapter_section": "Atrial Fibrillation Management",
      "page_number": 147,
      "url": "https://tg.org.au/etg/chapter/cardiovascular#af",
      "rag_verified": true,
      "confidence_score": 0.92,
      "verification_date": "2026-02-06",
      "chunk_id": "etg-2024-cardio-147-chunk-3"
    },
    // ... 2 more citations
  ],
  "citation_status": "complete",
  "last_validated": "2026-02-06T10:30:00Z"
}
```

---

## ⚖️ PART 4: COPYRIGHT & LEGAL COMPLIANCE FRAMEWORK

### 4.1 Copyright Risk Matrix

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    COPYRIGHT RISK ASSESSMENT                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  SOURCE MATERIAL                 COPYRIGHT   RISK     MITIGATION            │
│  ────────────────────────────────────────────────────────────────────────  │
│                                                                             │
│  eTG Complete (Therapeutic       © Therapeutic  MEDIUM  • Subscription req  │
│  Guidelines Ltd)                 Guidelines Ltd         • Fair use (edu)    │
│                                  Subscription           • Cite properly     │
│                                  model                  • Don't copy        │
│                                                                             │
│  AMH (Australian Medicines       © AMH         MEDIUM  • Same as eTG        │
│  Handbook)                                              • Paraphrase only   │
│                                                                             │
│  AMC Handbook of Clinical        © AMC         HIGH    • Obtain license    │
│  Assessment                      All rights            • Or remove source  │
│                                  reserved              • Risk: DMCA        │
│                                                                             │
│  Talley & O'Connor Clinical      © Elsevier    HIGH    • Same as AMC       │
│  Examination                                            • Publishers        │
│                                                           aggressive        │
│                                                                             │
│  Oxford Handbook Emergency       © Oxford UP   HIGH    • Same as above     │
│  Medicine                                                                   │
│                                                                             │
│  RACGP Guidelines (Red Book)     © RACGP       LOW     • Public domain     │
│                                  Creative Commons       • Free to use      │
│                                  BY-NC-SA               • Cite properly    │
│                                                                             │
│  NSW Health Guidelines           Government    LOW     • Public domain     │
│                                  copyright             • Free to use       │
│                                  waived                                     │
│                                                                             │
│  Cochrane Reviews                Open access   LOW     • CC BY license     │
│                                  CC BY                 • Free to use       │
│                                                                             │
│  StatPearls                      Public domain LOW     • US Govt work      │
│                                  (US Govt)             • No copyright      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.2 Fair Use Analysis (Australian Context)

**Australian Copyright Act 1968 - Fair Dealing Provisions**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    FAIR DEALING DEFENSE CHECKLIST                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Australia has "Fair Dealing" (narrower than US "Fair Use")                 │
│                                                                             │
│  ALLOWED PURPOSES (Section 40):                                             │
│  ✅ Research or study                                                       │
│  ✅ Criticism or review                                                     │
│  ✅ News reporting                                                          │
│  ✅ Professional advice (e.g., legal/medical)                               │
│  ❌ Commercial use (generally not covered)                                  │
│                                                                             │
│  OUR USE CASE: Educational Platform (Research/Study)                        │
│                                                                             │
│  FAIRNESS FACTORS (Court considers):                                        │
│                                                                             │
│  1. Purpose & Character of Use                                              │
│     ├── Our purpose: Educational (medical exam preparation) ✅              │
│     ├── Commercial element: We charge subscription fees ⚠️                  │
│     ├── Transformative: We create MCQs, not republishing text ✅            │
│     └── Assessment: MODERATE RISK                                           │
│                                                                             │
│  2. Nature of Copyrighted Work                                              │
│     ├── Type: Medical textbooks (factual, not creative) ✅                  │
│     ├── Published: Yes (publicly available) ✅                              │
│     └── Assessment: FAVORABLE                                               │
│                                                                             │
│  3. Amount & Substantiality                                                 │
│     ├── What we use: Small excerpts (2-3 sentences per MCQ) ✅              │
│     ├── % of total work: <0.1% of each book ✅                              │
│     ├── "Heart" of the work: Using factual info, not unique prose ✅        │
│     └── Assessment: FAVORABLE                                               │
│                                                                             │
│  4. Effect on Market                                                        │
│     ├── Do we substitute for original? NO (different product) ✅            │
│     ├── Does our use harm sales? UNLIKELY (different audience) ✅           │
│     ├── Could publisher offer similar product? POSSIBLY ⚠️                  │
│     └── Assessment: MODERATE RISK                                           │
│                                                                             │
│  OVERALL ASSESSMENT: MODERATE RISK (not clear-cut fair dealing)             │
│                                                                             │
│  RECOMMENDATION:                                                            │
│  ├── Option A: Seek legal opinion ($3K-5K) - Recommended                    │
│  ├── Option B: Obtain licenses ($5K-20K/yr) - Safest                        │
│  └── Option C: Remove risky sources, use only public domain - Free          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.3 Recommended Copyright Strategy

**HYBRID APPROACH (Minimize Risk, Maximize Content)**

**TIER 1: Public Domain Sources (Safe)**
- RACGP Guidelines (Red Book)
- NSW Health Clinical Guidelines
- Cochrane Reviews (open access)
- StatPearls (US Government)
- Australian Government health resources

**Action:** Use freely, cite properly

**TIER 2: Subscription Services (Grey Area)**
- eTG Complete
- Australian Medicines Handbook (AMH)

**Action:**
1. Purchase institutional subscriptions (~$2K/yr total)
2. Use for RAG validation (not verbatim copying)
3. Paraphrase, don't quote
4. Cite as reference, not source of copied text

**TIER 3: Commercial Textbooks (High Risk)**
- AMC Handbook
- Talley & O'Connor
- Oxford Handbooks

**Action:**
1. **Immediate (Phase 0, Week 4):** Remove these from RAG database
2. **Replace with:** eTG, AMH, RACGP, StatPearls
3. **Regenerate affected MCQs** using safe sources only
4. **Future:** If revenue justifies, negotiate licenses

**Implementation:**

```bash
# Week 4, Day 1: Audit RAG database
python scripts/audit_rag_sources.py

Output:
{
  "total_chunks": 42647,
  "by_source": {
    "etg_complete": 12500,
    "amh": 8000,
    "racgp": 6000,
    "talley_oconnor": 5500,  # HIGH RISK
    "amc_handbook": 4200,    # HIGH RISK
    "oxford_handbook": 3800, # HIGH RISK
    "statpearls": 2647
  }
}

# Week 4, Day 2-3: Remove high-risk sources
python scripts/remove_risky_sources.py \
  --remove "talley_oconnor,amc_handbook,oxford_handbook"

# Week 4, Day 4-5: Regenerate affected MCQs
python scripts/regenerate_mcqs_safe_sources.py \
  --affected_mcqs mcqs_using_risky_sources.json \
  --safe_sources "etg,amh,racgp,statpearls" \
  --output regenerated_mcqs.json
```

**Result:**
- Legal risk: HIGH → LOW
- Content quality: Maintained (Australian guidelines remain)
- Cost: $0 (avoided licensing fees)
- Timeline: 1 week (within Phase 0)

---

## ⏱️ PART 5: EXTENDED IMPLEMENTATION TIMELINE

### 5.1 Revised 28-Week Timeline

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    REALISTIC IMPLEMENTATION TIMELINE                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  PHASE 0: FOUNDATION & VALIDATION (Weeks 1-4) - NEW                         │
│  ─────────────────────────────────────────────                              │
│  Goal: Validate content, secure infrastructure, clear legal risks           │
│                                                                             │
│  Week 1: Security Foundation                                                │
│    ├── Set up Clerk authentication                                          │
│    ├── Configure Stripe payments                                            │
│    ├── Database security hardening (RLS, encryption)                        │
│    ├── Install pre-commit hooks (git-secrets)                               │
│    └── Configure monitoring (Sentry, CloudWatch)                            │
│                                                                             │
│  Week 1-2: Automated Validation (parallel)                                  │
│    ├── RAG citation validation (54,000 facts)                               │
│    ├── Australian compliance check (18,000 MCQs)                            │
│    └── Generate validation reports                                          │
│                                                                             │
│  Week 2: Manual Review                                                      │
│    ├── Clinical accuracy review (500 MCQs sample)                           │
│    ├── Medical professional review                                          │
│    └── Pass/fail/revise decisions                                           │
│                                                                             │
│  Week 3: Remediation                                                        │
│    ├── Fix critical issues (failed clinical review)                         │
│    ├── Correct non-compliant items (Australian guidelines)                  │
│    ├── Improve low-confidence citations                                     │
│    └── Update database with corrections                                     │
│                                                                             │
│  Week 4: Copyright Clearance                                                │
│    ├── Copyright risk assessment                                            │
│    ├── Legal consultation ($3K-5K)                                          │
│    ├── Remove high-risk sources OR obtain licenses                          │
│    ├── Regenerate affected MCQs (if sources removed)                        │
│    └── Copyright compliance certificate                                     │
│                                                                             │
│  Deliverables:                                                              │
│  ✅ Secure authentication & payment infrastructure                          │
│  ✅ Validated content database (18,000 MCQs, 3,000 OSCEs)                   │
│  ✅ Citation validation report (>85% confidence)                            │
│  ✅ Clinical accuracy certification (>95% pass rate)                        │
│  ✅ Copyright clearance (legal opinion or safe sources)                     │
│                                                                             │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                             │
│  PHASE 1: MOBILE PWA (Weeks 5-10) - 6 weeks                                 │
│  ────────────────────────────────────────                                   │
│  Goal: Launch free tier mobile quick-reference app                          │
│                                                                             │
│  Week 5-6: Core PWA Infrastructure                                          │
│    ├── React + Vite + TypeScript setup                                      │
│    ├── TailwindCSS + shadcn/ui components                                   │
│    ├── Service worker for offline mode                                      │
│    ├── IndexedDB for local storage                                          │
│    └── PWA manifest (icons, splash screens)                                 │
│                                                                             │
│  Week 7-8: MCQ Practice Interface                                           │
│    ├── MCQ display component (QuestionCard)                                 │
│    ├── Answer submission & validation                                       │
│    ├── Explanation panel with citations (CitationPanel)                     │
│    ├── Progress tracking (local storage)                                    │
│    └── Study session management                                             │
│                                                                             │
│  Week 9: RAG Integration                                                    │
│    ├── Connect to backend RAG API                                           │
│    ├── Quick medical search feature                                         │
│    ├── Citation display from Qdrant                                         │
│    └── Offline fallback (cached results)                                    │
│                                                                             │
│  Week 10: Testing & Launch                                                  │
│    ├── E2E testing (Playwright)                                             │
│    ├── PWA testing (Lighthouse score >90)                                   │
│    ├── Performance optimization (< 3s load)                                 │
│    ├── Deploy to Vercel/Cloudflare Pages                                    │
│    └── LAUNCH: Free tier (200 MCQs)                                         │
│                                                                             │
│  Deliverables:                                                              │
│  ✅ PWA installable on iOS/Android                                          │
│  ✅ 200 free MCQs available                                                 │
│  ✅ RAG-powered quick search                                                │
│  ✅ Offline mode (500 cached MCQs)                                          │
│  ✅ Citation display component                                              │
│                                                                             │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                             │
│  PHASE 2: EMR PRACTICE SYSTEM (Weeks 11-18) - 8 weeks                       │
│  ──────────────────────────────────────────────────────                     │
│  Goal: Launch Pro tier with EMR practice system                             │
│                                                                             │
│  Week 11-12: EMR UI Framework                                               │
│    ├── Cerner PowerChart UI components                                      │
│    ├── Epic EHR UI components                                               │
│    ├── Patient banner, vitals display                                       │
│    ├── Navigation structure (sidebar, tabs)                                 │
│    └── Theme switching (Cerner dark / Epic purple)                          │
│                                                                             │
│  Week 13-14: SOAP Note Editor                                               │
│    ├── Rich text editor (TipTap / Lexical)                                  │
│    ├── SOAP note template (S, O, A, P sections)                             │
│    ├── Autocomplete (medications, diagnoses)                                │
│    ├── Validation layer 1: Structural (all sections complete)               │
│    └── Save/export functionality                                            │
│                                                                             │
│  Week 15-16: PBS/MBS Integration                                            │
│    ├── Medication search (4,000+ PBS drugs)                                 │
│    ├── Drug interaction checker                                             │
│    ├── Allergy checking                                                     │
│    ├── Pathology ordering (MBS items)                                       │
│    ├── Validation layer 2: Clinical (drug doses, contraindications)         │
│    └── Prescription output (formatted)                                      │
│                                                                             │
│  Week 17: Australian Compliance Validation                                  │
│    ├── eTG/AMH/RACGP guideline checker                                      │
│    ├── Validation layer 3: Australian compliance                            │
│    ├── Feedback messages (green check / red warning)                        │
│    └── Link to relevant guidelines                                          │
│                                                                             │
│  Week 18: Patient Scenarios & Launch                                        │
│    ├── Import 200 patient scenarios to database                             │
│    ├── Scenario randomization & selection                                   │
│    ├── Progress tracking (scenarios completed)                              │
│    ├── E2E testing (100% validation pass rate)                              │
│    └── LAUNCH: Pro tier ($49/mo) with EMR access                            │
│                                                                             │
│  Deliverables:                                                              │
│  ✅ Cerner + Epic EMR simulations                                           │
│  ✅ SOAP note editor with 3-layer validation                                │
│  ✅ PBS/MBS integration (prescribing, pathology)                            │
│  ✅ 200 patient scenarios                                                   │
│  ✅ Pro tier subscription available                                         │
│                                                                             │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                             │
│  PHASE 3: AMC SIMULATION (Weeks 19-28) - 10 weeks                           │
│  ──────────────────────────────────────────                                 │
│  Goal: Launch Ultimate tier with AI simulation                              │
│                                                                             │
│  Week 19-20: AI Patient Agent                                               │
│    ├── Claude 3.5 Sonnet integration                                        │
│    ├── Patient persona system prompts (200+ scenarios)                      │
│    ├── Emotion state machine (calm/anxious/sad/angry)                       │
│    ├── Conversational memory (context window)                               │
│    └── Text-based interface (chat UI)                                       │
│                                                                             │
│  Week 21-22: AI Examiner Scoring                                            │
│    ├── 15-mark rubric implementation                                        │
│    │   ├── History taking (3 marks)                                         │
│    │   ├── Communication (3 marks)                                          │
│    │   ├── Clinical reasoning (3 marks)                                     │
│    │   ├── Professionalism (2 marks)                                        │
│    │   └── Structure & time (2 marks)                                       │
│    ├── Real-time scoring during conversation                                │
│    ├── Detailed feedback generation                                         │
│    └── Comparison to model answer                                           │
│                                                                             │
│  Week 23-24: Voice Synthesis Integration                                    │
│    ├── ElevenLabs API integration                                           │
│    ├── Australian accent voice selection                                    │
│    ├── Text-to-speech for AI patient responses                              │
│    ├── Whisper STT for user voice input (optional)                          │
│    └── Cost monitoring (budget: $300/mo for 50 users)                       │
│                                                                             │
│  Week 25-26: AI Validation Study                                            │
│    ├── Recruit 2 medical professionals (examiners)                          │
│    ├── Test: 100 AI-scored OSCEs vs human scoring                           │
│    ├── Calculate inter-rater reliability (Cohen's kappa)                    │
│    ├── Target: Correlation >0.85                                            │
│    ├── Adjust rubric if <0.85 (iterate until acceptable)                    │
│    └── Validation report for marketing claims                               │
│                                                                             │
│  Week 27: Mock Exam System                                                  │
│    ├── 16-station mock exam generator                                       │
│    ├── Timer system (8 min/station, rest stations)                          │
│    ├── Exam lockdown mode (disable navigation)                              │
│    ├── Post-exam detailed report                                            │
│    └── Progress toward exam readiness score                                 │
│                                                                             │
│  Week 28: Testing & Launch                                                  │
│    ├── Load testing (50 concurrent AI simulations)                          │
│    ├── Voice synthesis quality check                                        │
│    ├── E2E testing (full 16-station mock exam)                              │
│    ├── Marketing materials (demo videos)                                    │
│    └── LAUNCH: Ultimate tier ($79/mo)                                       │
│                                                                             │
│  Deliverables:                                                              │
│  ✅ AI Patient simulator (text + voice)                                     │
│  ✅ AI Examiner with validated scoring                                      │
│  ✅ 16-station mock exams                                                   │
│  ✅ Voice synthesis (ElevenLabs)                                            │
│  ✅ Validation study (>0.85 correlation)                                    │
│  ✅ Ultimate tier subscription available                                    │
│                                                                             │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                             │
│  SUMMARY:                                                                   │
│  ├── Phase 0 (Foundation): 4 weeks                                          │
│  ├── Phase 1 (Mobile PWA): 6 weeks                                          │
│  ├── Phase 2 (EMR System): 8 weeks                                          │
│  └── Phase 3 (AI Simulation): 10 weeks                                      │
│  TOTAL: 28 weeks (7 months)                                                 │
│                                                                             │
│  Revenue Timeline:                                                          │
│  ├── Week 10: Free tier live (lead generation)                              │
│  ├── Week 18: Pro tier live ($49/mo - start revenue)                        │
│  └── Week 28: Ultimate tier live ($79/mo - full product)                    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.2 Resource Requirements

| Phase | Duration | Developer FTE | Medical Reviewer | Budget |
|-------|----------|---------------|------------------|--------|
| Phase 0 | 4 weeks | 1.0 FTE | 0.25 FTE (part-time) | $10K |
| Phase 1 | 6 weeks | 1.5 FTE | 0 | $15K |
| Phase 2 | 8 weeks | 2.0 FTE | 0.1 FTE (validation) | $25K |
| Phase 3 | 10 weeks | 2.5 FTE | 0.25 FTE (validation study) | $35K |
| **TOTAL** | **28 weeks** | **1.9 FTE avg** | **0.15 FTE avg** | **$85K** |

**Budget Breakdown:**
- Developer salaries: $60K (1.9 FTE × 7 months × $5K/mo)
- Medical reviewer: $8K (part-time consultant)
- Legal consultation: $5K (IP lawyer, copyright)
- Infrastructure: $5K (Clerk, Stripe, hosting)
- Voice synthesis: $2K (ElevenLabs during Phase 3)
- Contingency: $5K (15% buffer)

---

## 🧪 PART 6: AI VALIDATION & TESTING PROTOCOLS

### 6.1 AI Examiner Validation Study Design

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    AI EXAMINER VALIDATION STUDY                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  RESEARCH QUESTION:                                                         │
│  Does AI examiner scoring correlate with human examiner scoring to an       │
│  acceptable degree for medical education purposes?                          │
│                                                                             │
│  HYPOTHESIS:                                                                │
│  AI examiner scores will correlate ≥0.85 with human examiner scores         │
│  (Cohen's kappa for inter-rater reliability)                                │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  METHODOLOGY                                                        │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │                                                                      │   │
│  │  Participants:                                                       │   │
│  │  ├── 20 medical students (volunteers)                                │   │
│  │  ├── 2 human examiners (GP or specialist, AMC examiner experience)  │   │
│  │  └── 1 AI examiner (Claude 3.5 Sonnet with rubric)                  │   │
│  │                                                                      │   │
│  │  Procedure:                                                          │   │
│  │  ├── Each student completes 5 OSCE stations (100 total sessions)    │   │
│  │  ├── Stations cover:                                                 │   │
│  │  │   ├── History taking (Chest pain, SOB)                            │   │
│  │  │   ├── Physical exam (Cardiovascular, Respiratory)                 │   │
│  │  │   ├── Communication (Breaking bad news)                           │   │
│  │  │   ├── Emergency (ACS management)                                  │   │
│  │  │   └── Procedural (Consent for IV cannulation)                     │   │
│  │  ├── All sessions recorded (video + transcript)                      │   │
│  │  ├── Blinding:                                                       │   │
│  │  │   ├── Human examiners blind to AI scores                          │   │
│  │  │   ├── AI blind to human scores (run independently)                │   │
│  │  │   └── Examiners don't know which sessions will be AI-scored       │   │
│  │  └── Scoring:                                                        │   │
│  │      ├── Each session scored by:                                     │   │
│  │      │   ├── AI examiner (real-time during simulation)               │   │
│  │      │   ├── Human examiner 1 (reviewing recording)                  │   │
│  │      │   └── Human examiner 2 (reviewing recording)                  │   │
│  │      └── Use 15-mark rubric (same for all raters)                    │   │
│  │                                                                      │   │
│  │  Analysis:                                                           │   │
│  │  ├── Calculate:                                                      │   │
│  │  │   ├── Pearson correlation (AI vs Human 1, AI vs Human 2)          │   │
│  │  │   ├── Cohen's kappa (inter-rater reliability)                     │   │
│  │  │   ├── Mean absolute error (MAE) between scores                    │   │
│  │  │   └── Bland-Altman plot (agreement visualization)                 │   │
│  │  ├── Acceptable threshold:                                           │   │
│  │  │   ├── Correlation: r ≥ 0.85 (strong positive correlation)         │   │
│  │  │   ├── Cohen's kappa: κ ≥ 0.75 (substantial agreement)             │   │
│  │  │   └── MAE: ≤ 2 marks (out of 15) on average                       │   │
│  │  └── If below threshold:                                             │   │
│  │      ├── Analyze discrepancies (where AI disagrees with humans)      │   │
│  │      ├── Refine rubric prompts                                       │   │
│  │      ├── Re-test on new sample (iterate until acceptable)            │   │
│  │      └── Document limitations in marketing materials                 │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  VALIDATION REPORT TEMPLATE                                         │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │                                                                      │   │
│  │  irStudy AI Examiner Validation Study                               │   │
│  │  Date: 2026-06-15                                                   │   │
│  │                                                                      │   │
│  │  RESULTS:                                                           │   │
│  │  ├── Participants: 20 students, 100 OSCE sessions                   │   │
│  │  ├── Inter-rater reliability:                                       │   │
│  │  │   ├── AI vs Human 1: r = 0.89 (p < 0.001) ✅                     │   │
│  │  │   ├── AI vs Human 2: r = 0.87 (p < 0.001) ✅                     │   │
│  │  │   ├── Human 1 vs Human 2: r = 0.92 (reference)                   │   │
│  │  │   └── Cohen's kappa: κ = 0.81 (substantial agreement) ✅         │   │
│  │  ├── Mean Absolute Error: 1.6 marks (SD=0.8) ✅                     │   │
│  │  ├── Score distribution:                                            │   │
│  │  │   ├── AI mean: 11.2/15 (SD=2.1)                                  │   │
│  │  │   ├── Human 1 mean: 11.5/15 (SD=2.0)                             │   │
│  │  │   └── Human 2 mean: 11.3/15 (SD=2.2)                             │   │
│  │  └── Bland-Altman analysis:                                         │   │
│  │      ├── Mean difference: -0.3 marks (AI slightly harsher)          │   │
│  │      ├── 95% limits of agreement: -3.1 to +2.5 marks                │   │
│  │      └── No systematic bias detected                                │   │
│  │                                                                      │   │
│  │  CONCLUSION:                                                        │   │
│  │  AI examiner demonstrates strong correlation with human examiners   │   │
│  │  (r=0.87-0.89) and substantial inter-rater reliability (κ=0.81),    │   │
│  │  meeting pre-specified validation criteria. Suitable for formative  │   │
│  │  assessment in medical education.                                   │   │
│  │                                                                      │   │
│  │  LIMITATIONS:                                                       │   │
│  │  ├── AI examiner is validated for formative (practice) use only     │   │
│  │  ├── NOT validated for high-stakes (summative) assessment           │   │
│  │  ├── Human review recommended for borderline scores (6-9/15)        │   │
│  │  └── Validation limited to common OSCE scenarios                    │   │
│  │                                                                      │   │
│  │  MARKETING CLAIMS (Approved):                                       │   │
│  │  ✅ "AI scoring validated against human examiners (r=0.87)"         │   │
│  │  ✅ "Provides reliable formative feedback for exam preparation"     │   │
│  │  ❌ "AI scoring replaces human examiners" (NOT validated)           │   │
│  │  ❌ "Suitable for final exam grading" (NOT validated)               │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 6.2 Testing Requirements (100% Pass Rate)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    TESTING PYRAMID & QUALITY GATES                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  REQUIREMENT: 100% test pass rate before ANY deployment                     │
│  (From PROJECT_CONSTRAINTS.md)                                              │
│                                                                             │
│  TESTING LEVELS:                                                            │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  LEVEL 1: UNIT TESTS (Fast, Isolated)                              │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │  Coverage Target: ≥70% code coverage                                │   │
│  │                                                                      │   │
│  │  Backend (Python + pytest):                                         │   │
│  │  ├── tests/unit/test_rag_query_service.py                           │   │
│  │  │   └── Test RAG citation extraction logic                          │   │
│  │  ├── tests/unit/test_citation_validator.py                          │   │
│  │  │   └── Test citation confidence scoring                            │   │
│  │  ├── tests/unit/test_australian_compliance.py                       │   │
│  │  │   └── Test PBS/eTG validation rules                              │   │
│  │  └── tests/unit/test_mcq_validator.py                               │   │
│  │      └── Test MCQ structure validation                              │   │
│  │                                                                      │   │
│  │  Frontend (React + Vitest):                                         │   │
│  │  ├── src/components/mcq/__tests__/CitationPanel.test.tsx            │   │
│  │  │   └── Test citation display logic                                │   │
│  │  ├── src/components/mcq/__tests__/QuestionCard.test.tsx             │   │
│  │  │   └── Test MCQ rendering                                         │   │
│  │  └── src/hooks/__tests__/useRagQuery.test.ts                        │   │
│  │      └── Test RAG query hook                                        │   │
│  │                                                                      │   │
│  │  Quality Gate: All unit tests pass + ≥70% coverage                  │   │
│  │  Run frequency: Every commit (pre-commit hook)                      │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  LEVEL 2: INTEGRATION TESTS (API + Database)                        │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │  Coverage Target: All API endpoints tested                          │   │
│  │                                                                      │   │
│  │  Backend (FastAPI + pytest):                                        │   │
│  │  ├── tests/integration/test_api_mcqs.py                             │   │
│  │  │   ├── Test GET /api/v1/mcqs/{id}                                 │   │
│  │  │   ├── Test POST /api/v1/mcqs/{id}/validate-citations             │   │
│  │  │   └── Test error handling (404, 500)                             │   │
│  │  ├── tests/integration/test_api_auth.py                             │   │
│  │  │   ├── Test Clerk webhook integration                             │   │
│  │  │   ├── Test JWT validation                                        │   │
│  │  │   └── Test role-based access control                             │   │
│  │  └── tests/integration/test_rag_pipeline.py                         │   │
│  │      ├── Test Qdrant query → Claude → response                      │   │
│  │      └── Test citation extraction from chunks                       │   │
│  │                                                                      │   │
│  │  Database (PostgreSQL):                                             │   │
│  │  ├── Test data integrity constraints                                │   │
│  │  ├── Test Row-Level Security (RLS) policies                         │   │
│  │  └── Test database migrations (Alembic)                             │   │
│  │                                                                      │   │
│  │  Quality Gate: All API tests pass + no DB errors                    │   │
│  │  Run frequency: Every PR merge                                      │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  LEVEL 3: END-TO-END TESTS (User Flows)                             │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │  Coverage Target: All critical user journeys                        │   │
│  │                                                                      │   │
│  │  Frontend (Playwright):                                             │   │
│  │  ├── e2e/auth/signup.spec.ts                                        │   │
│  │  │   └── Test: Sign up → Email verify → Dashboard                   │   │
│  │  ├── e2e/mcq/practice-session.spec.ts                               │   │
│  │  │   └── Test: Start session → Answer 10 MCQs → See results         │   │
│  │  ├── e2e/mcq/citation-display.spec.ts                               │   │
│  │  │   └── Test: Answer question → View citations → Click source      │   │
│  │  ├── e2e/emr/soap-note.spec.ts                                      │   │
│  │  │   └── Test: Select patient → Write SOAP → Validate → Save        │   │
│  │  ├── e2e/payment/upgrade.spec.ts                                    │   │
│  │  │   └── Test: Click upgrade → Stripe checkout → Success redirect   │   │
│  │  └── e2e/ai-simulation/full-osce.spec.ts                            │   │
│  │      └── Test: Start OSCE → Converse with AI → Get scored           │   │
│  │                                                                      │   │
│  │  Quality Gate: All E2E scenarios pass (0 failures)                  │   │
│  │  Run frequency: Nightly (production-like environment)               │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  LEVEL 4: PERFORMANCE TESTS (Load & Speed)                          │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │  Coverage Target: Meet performance SLAs                             │   │
│  │                                                                      │   │
│  │  Backend (Locust / k6):                                             │   │
│  │  ├── Load test: 100 concurrent users                                │   │
│  │  │   └── SLA: <500ms p95 response time                              │   │
│  │  ├── Stress test: 500 concurrent users                              │   │
│  │  │   └── Ensure graceful degradation (no crashes)                   │   │
│  │  └── Spike test: 1000 users in 1 minute                             │   │
│  │      └── Auto-scaling works correctly                               │   │
│  │                                                                      │   │
│  │  Frontend (Lighthouse):                                             │   │
│  │  ├── Page load: <3s on 3G                                           │   │
│  │  ├── Lighthouse score: >90 (all categories)                         │   │
│  │  └── PWA installability: Pass                                       │   │
│  │                                                                      │   │
│  │  Quality Gate: Meet all performance SLAs                            │   │
│  │  Run frequency: Weekly (staging environment)                        │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  LEVEL 5: SECURITY TESTS (Vulnerability Scanning)                   │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │  Coverage Target: Zero critical vulnerabilities                     │   │
│  │                                                                      │   │
│  │  Automated (CI/CD):                                                 │   │
│  │  ├── Dependency scanning: npm audit / pip-audit                     │   │
│  │  │   └── Block: Any critical or high severity CVE                   │   │
│  │  ├── SAST: Semgrep (static analysis)                                │   │
│  │  │   └── Detect: SQL injection, XSS, hardcoded secrets              │   │
│  │  ├── Container scanning: Trivy (Docker images)                      │   │
│  │  │   └── Block: Critical vulnerabilities in base images             │   │
│  │  └── Secret scanning: git-secrets (pre-commit)                      │   │
│  │      └── Block: Any API key, password, JWT secret                   │   │
│  │                                                                      │   │
│  │  Manual (Quarterly):                                                │   │
│  │  ├── Penetration testing: External security firm                    │   │
│  │  ├── OWASP Top 10 testing                                           │   │
│  │  └── Remediation: All findings within 30 days                       │   │
│  │                                                                      │   │
│  │  Quality Gate: Zero critical/high vulnerabilities                   │   │
│  │  Run frequency: Every commit (automated) + Quarterly (manual)       │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  CI/CD PIPELINE (GitHub Actions / GitLab CI):                               │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  On every push to main:                                             │   │
│  │  ├── 1. Run pre-commit hooks (git-secrets)                          │   │
│  │  ├── 2. Run unit tests (pytest, vitest)                             │   │
│  │  ├── 3. Check coverage ≥70%                                         │   │
│  │  ├── 4. Run integration tests                                       │   │
│  │  ├── 5. Run security scans (Semgrep, npm audit)                     │   │
│  │  ├── 6. Build Docker image                                          │   │
│  │  ├── 7. Deploy to staging                                           │   │
│  │  ├── 8. Run E2E tests (Playwright)                                  │   │
│  │  └── 9. If all pass: Deploy to production                           │   │
│  │                                                                      │   │
│  │  If ANY test fails: Block deployment ❌                             │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🤖 PART 7: AGENT OS INTEGRATION

### 7.1 Expert Agent Delegation Framework

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    AGENT OS INTEGRATION ARCHITECTURE                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  CONTEXT: Your global constraints specify Agent OS usage for complex tasks  │
│  Location: ~/.claude/CLAUDE.md                                              │
│                                                                             │
│  EXPERT AGENTS AVAILABLE (from constraints):                                │
│  ├── security-compliance-expert (PHI protection, HIPAA, credentials)        │
│  ├── testing-qa-expert (100% pass rate, ≥70% coverage)                      │
│  ├── aba-clinical-expert (Clinical validation - adapt for medical)          │
│  └── project-manager-coordinator (Task delegation, quality gates)           │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  DELEGATION WORKFLOW (PM Coordination Pattern)                      │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │                                                                      │   │
│  │  SCENARIO: Implementing EMR Practice System (Phase 2)               │   │
│  │                                                                      │   │
│  │  Step 1: PM Receives Task                                           │   │
│  │    "Implement SOAP note editor with 3-layer validation"             │   │
│  │                                                                      │   │
│  │  Step 2: PM Reads Constraints                                       │   │
│  │    ├── Read: PROJECT_CONSTRAINTS.md                                 │   │
│  │    ├── Read: constraints/01-medical-accuracy.md                     │   │
│  │    ├── Read: constraints/03-security-configuration.md               │   │
│  │    └── Read: constraints/06-testing-requirements.md                 │   │
│  │                                                                      │   │
│  │  Step 3: PM Creates Delegation Plan                                 │   │
│  │    ┌────────────────────────────────────────────────────────────┐   │   │
│  │    │ Task Breakdown:                                            │   │   │
│  │    │ 1. [flutter-desktop-expert] Build SOAP editor UI           │   │   │
│  │    │    → Constraints: TailwindCSS, accessibility (WCAG 2.2)    │   │   │
│  │    │    → Validation: flutter analyze = 0 errors                │   │   │
│  │    │                                                            │   │   │
│  │    │ 2. [rust-ffi-expert] Implement 3-layer validation backend │   │   │
│  │    │    → Constraints: No hardcoded credentials, use config     │   │   │
│  │    │    → Validation: cargo check = 0 errors                    │   │   │
│  │    │                                                            │   │   │
│  │    │ 3. [security-compliance-expert] Review for PHI leaks       │   │   │
│  │    │    → Check: No real patient data stored                    │   │   │
│  │    │    → Check: SOAP notes encrypted at rest                   │   │   │
│  │    │                                                            │   │   │
│  │    │ 4. [testing-qa-expert] Write tests (100% pass rate)        │   │   │
│  │    │    → Unit tests: ≥70% coverage                             │   │   │
│  │    │    → E2E test: Full SOAP note workflow                     │   │   │
│  │    └────────────────────────────────────────────────────────────┘   │   │
│  │                                                                      │   │
│  │  Step 4: Sequential Delegation with Validation                      │   │
│  │    ┌────────────────────────────────────────────────────────────┐   │   │
│  │    │ PM → Agent 1 (UI Expert)                                   │   │   │
│  │    │   ├── Provide: Detailed constraints                        │   │   │
│  │    │   ├── Provide: Example code patterns                       │   │   │
│  │    │   ├── Require: Self-validation before return               │   │   │
│  │    │   └── Agent returns: SOAP editor component                 │   │   │
│  │    │                                                            │   │   │
│  │    │ PM Validates Agent 1 Output                                │   │   │
│  │    │   ├── Run: flutter analyze (must be 0 errors)              │   │   │
│  │    │   ├── Check: No hardcoded values                           │   │   │
│  │    │   ├── If issues: Delegate "Fix Issues" task to Agent 1     │   │   │
│  │    │   └── If pass: Proceed to Agent 2                          │   │   │
│  │    │                                                            │   │   │
│  │    │ PM → Agent 2 (Backend Expert)                              │   │   │
│  │    │   └── (Same validation pattern)                            │   │   │
│  │    │                                                            │   │   │
│  │    │ PM → Agent 3 (Security Expert)                             │   │   │
│  │    │   └── (Review Agent 1+2 output for security)               │   │   │
│  │    │                                                            │   │   │
│  │    │ PM → Agent 4 (QA Expert)                                   │   │   │
│  │    │   └── (Write tests for Agent 1+2 code)                     │   │   │
│  │    └────────────────────────────────────────────────────────────┘   │   │
│  │                                                                      │   │
│  │  Step 5: Final Quality Gate                                         │   │
│  │    ├── All tests pass (100% requirement)                            │   │
│  │    ├── No security issues (0 critical vulnerabilities)              │   │
│  │    ├── Code coverage ≥70%                                           │   │
│  │    ├── Documentation updated                                        │   │
│  │    └── Ready for commit                                             │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  CONSTRAINT-AWARE DELEGATION (Upfront Context)                      │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │                                                                      │   │
│  │  EXAMPLE DELEGATION PROMPT (to flutter-desktop-expert):             │   │
│  │                                                                      │   │
│  │  ```                                                                │   │
│  │  Task: Create SOAP note editor component for EMR practice system    │   │
│  │                                                                      │   │
│  │  CONSTRAINTS (READ THESE FIRST):                                    │   │
│  │  1. Security:                                                       │   │
│  │     • NEVER hardcode database credentials                           │   │
│  │     • MUST use ref.read(databaseConfigProvider) for FFI calls       │   │
│  │     • Example (correct):                                            │   │
│  │       ```dart                                                       │   │
│  │       final dbConfig = ref.read(databaseConfigProvider);            │   │
│  │       await ffi.saveSoapNote(                                       │   │
│  │         userId: dbConfig.userId,                                    │   │
│  │         dbPath: dbConfig.dbPath,                                    │   │
│  │         dbKey: dbConfig.dbKey,                                      │   │
│  │       );                                                            │   │
│  │       ```                                                           │   │
│  │                                                                      │   │
│  │  2. Performance:                                                    │   │
│  │     • Text input debouncing: 300ms                                  │   │
│  │     • Auto-save: Every 30 seconds                                   │   │
│  │     • Target: <100ms UI response time                               │   │
│  │                                                                      │   │
│  │  3. Accessibility (WCAG 2.2 AA):                                    │   │
│  │     • All form fields: aria-label                                   │   │
│  │     • Keyboard navigation: Tab through sections                     │   │
│  │     • Focus indicators: 2px outline                                 │   │
│  │     • Color contrast: 4.5:1 minimum                                 │   │
│  │                                                                      │   │
│  │  4. Style:                                                          │   │
│  │     • TailwindCSS for all styling                                   │   │
│  │     • Material Design 3 components                                  │   │
│  │     • Responsive: Desktop (>1024px) and Tablet (768-1024px)         │   │
│  │                                                                      │   │
│  │  5. State Management:                                               │   │
│  │     • Riverpod 2.6+ (NO Provider or Bloc)                           │   │
│  │     • Use StateNotifier for SOAP note state                         │   │
│  │                                                                      │   │
│  │  BEFORE RETURNING YOUR CODE:                                        │   │
│  │  ├── [ ] Run: flutter analyze (must show 0 errors)                 │   │
│  │  ├── [ ] Grep for hardcoded credentials: grep -r "dbPath:" lib/    │   │
│  │  ├── [ ] Verify: All timers have cleanup in ref.onDispose          │   │
│  │  └── [ ] Verify: Accessibility labels on all inputs                │   │
│  │                                                                      │   │
│  │  SEARCH FOR EXISTING PATTERNS (before coding):                      │   │
│  │  ├── Read: lib/features/goals/providers/goals_provider.dart        │   │
│  │  │   (for DatabaseConfig pattern)                                   │   │
│  │  └── Read: lib/shared/widgets/validated_text_field.dart            │   │
│  │      (for reusable form components)                                 │   │
│  │  ```                                                                │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  KEY PRINCIPLE: Front-Load Context, Explicit Constraints, Incremental       │
│  Validation                                                                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📁 APPENDICES

### Appendix A: Quick Reference - Decision Matrix

| Decision | Original Plan | Extended Plan | Rationale |
|----------|--------------|---------------|-----------|
| Timeline | 14 weeks | 28 weeks | Realistic for quality gates |
| Phase 0 | None | 4 weeks (validation) | Content QA critical |
| Security | Mentioned | Fully integrated | Leverage cyberSecurity/ |
| Citations | "Show citations" | Detailed UI spec | Medical accuracy req |
| Copyright | Not addressed | Clearance process | Legal risk mitigation |
| Testing | Not specified | 100% pass rate | Quality requirement |
| AI Validation | Not specified | Inter-rater study | Medical ed standards |

### Appendix B: Budget Summary

| Category | Amount | Justification |
|----------|--------|---------------|
| Development (7 months × 1.9 FTE × $5K/mo) | $60,000 | Primary cost |
| Medical review (part-time) | $8,000 | Clinical validation |
| Legal consultation | $5,000 | Copyright clearance |
| Infrastructure (Clerk, Stripe, hosting) | $5,000 | Annual services |
| Voice synthesis (ElevenLabs) | $2,000 | Phase 3 only |
| Contingency (15%) | $5,000 | Buffer for unknowns |
| **TOTAL** | **$85,000** | **7-month project** |

### Appendix C: Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Content validation | >85% citation confidence | RAG validation report |
| Clinical accuracy | >95% pass rate | Medical review (500 sample) |
| Security | 0 critical vulnerabilities | Quarterly pen test |
| Testing | 100% test pass rate | CI/CD pipeline |
| AI validation | >0.85 correlation | Inter-rater reliability study |
| User acquisition | 500 signups (3 months) | Analytics |
| Conversion | 3-5% (Free → Pro) | Stripe metrics |

---

**Document Status:** COMPLETE
**Version:** 3.0 (Extended Security & Compliance)
**Last Updated:** 2026-02-06
**Next Review:** After Phase 0 completion (Week 4)

---

**Related Documents:**
- `COMPREHENSIVE_PLATFORM_PLAN.md` (original plan)
- `UI_MODULE_ORGANIZATION_ARCHITECTURE.md` (UI specs)
- `MODULE_ARCHITECTURE_COMPARISON_ANALYSIS.md` (architecture comparison)
- `constraints/README.md` (constraint system)
- `cyberSecurity/` (existing security framework)
