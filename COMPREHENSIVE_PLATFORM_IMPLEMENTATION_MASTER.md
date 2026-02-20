# 🎯 COMPREHENSIVE PLATFORM IMPLEMENTATION MASTER PLAN
## irStudy Medical Education Platform - Complete Integration Strategy

**Date**: 2026-02-16
**Version**: 1.0
**Scope**: EMR Practice System + AI OSCE Simulation System (Complete Platform)
**Status**: Ready for Implementation

---

## 📋 EXECUTIVE SUMMARY

The irStudy Medical Education Platform consists of **two major integrated systems** designed for AMC Clinical Examination preparation:

### System Overview

| System | Status | Scope | Timeline | Effort |
|--------|--------|-------|----------|--------|
| **EMR Practice System** | PRDs Complete | 18 critical fixes, SOAP documentation | 3 weeks | 67.5-73.5 hours |
| **AI OSCE Simulation** | PRDs Complete | 8 PRDs, AI Patient/Examiner | 4-6 weeks | 192-236 hours |
| **Integration Layer** | Planned | Unified workflows, shared infrastructure | 1-2 weeks | 36-48 hours |
| **TOTAL PLATFORM** | Ready to Build | 14 EMR + 8 OSCE + 2 Integration PRDs | **6-8 weeks** | **296-358 hours** |

### Key Integration Points

**Shared Infrastructure** (Week 1):
- ✅ HashiCorp Vault (credentials management)
- ✅ Redis (EMR caching + OSCE session state)
- ✅ HTTPS/TLS (security headers)
- ✅ JWT Authentication (unified token format)
- ✅ Security test suite (35 tests covering both systems)

**Cross-System Workflows**:
- ✅ AI OSCE practice → EMR documentation (OSCE-to-EMR converter)
- ✅ Unified progress dashboard (MCQ + OSCE + AI OSCE + EMR metrics)
- ✅ Shared Golden Dataset (50 scenarios in both systems for pedagogical validation)
- ✅ Content reuse (360 AI OSCE personas → EMR SOAP templates)

### Combined Cost Analysis

| Usage Tier | EMR | AI OSCE | Total | Monthly Cost |
|------------|-----|---------|-------|--------------|
| **Baseline** (500 users, 25% adoption) | $8 Claude + $12 Redis | $36 Claude + $10 Redis | Shared | $66/month |
| **Scale** (1000 users, 50% EMR + 30% OSCE) | $8 Claude + $12 Redis | $64 Claude + $20 Redis | Shared | $104/month |
| **Peak** (2000 users, 60% adoption) | $12 Claude + $15 Redis | $96 Claude + $30 Redis | Shared | $153/month |

**Budget Recommendation**: $200/month (30% buffer for growth)

---

## 🏗️ SYSTEM ARCHITECTURE

### High-Level Component Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    irStudy Platform (Frontend)                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ MCQ Practice │  │ OSCE Station │  │ EMR Documentation    │  │
│  │ (Existing)   │  │ Browser      │  │ (Epic/Cerner UI)     │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │        Unified Progress Dashboard (NEW)                   │  │
│  │  MCQ + OSCE + AI OSCE + EMR Metrics (Integrated View)    │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                  ┌───────────┴───────────┐
                  │                       │
    ┌─────────────▼────────┐  ┌──────────▼──────────┐
    │  EMR Backend API     │  │ AI OSCE Backend API │
    │  (FastAPI/Python)    │  │ (FastAPI/Python)    │
    │                      │  │                     │
    │  - SOAP validation   │  │ - WebSocket server  │
    │  - Template mgmt     │  │ - AI Patient/Examiner│
    │  - Analytics API     │  │ - AMC scoring       │
    └──────┬───────────────┘  └──────┬──────────────┘
           │                         │
    ┌──────▼─────────────────────────▼───────┐
    │     Shared Infrastructure (Week 1)     │
    │  ┌─────────────────────────────────┐  │
    │  │ HashiCorp Vault (Secrets)       │  │
    │  │  - EMR: DB password, Claude key │  │
    │  │  - OSCE: Redis pwd, WS secret   │  │
    │  └─────────────────────────────────┘  │
    │                                        │
    │  ┌─────────────────────────────────┐  │
    │  │ Redis (In-Memory Store)         │  │
    │  │  - emr:* namespace (cache)      │  │
    │  │  - osce:* namespace (sessions)  │  │
    │  │  - 2.5 GB total allocation      │  │
    │  └─────────────────────────────────┘  │
    │                                        │
    │  ┌─────────────────────────────────┐  │
    │  │ Claude API (Shared Rate Limit)  │  │
    │  │  - Priority: AI Patient > EMR   │  │
    │  │  - Fallback: Kimi API (OSCE)    │  │
    │  └─────────────────────────────────┘  │
    │                                        │
    │  ┌─────────────────────────────────┐  │
    │  │ Security Layer (HTTPS/JWT)      │  │
    │  │  - 9 security headers           │  │
    │  │  - Unified JWT format           │  │
    │  └─────────────────────────────────┘  │
    └────────────────────────────────────────┘
                    │
         ┌──────────┴──────────┐
         │                     │
   ┌─────▼──────┐   ┌─────────▼────────┐
   │ PostgreSQL │   │ Qdrant Vector DB │
   │  (Primary) │   │  (RAG for OSCE)  │
   │            │   │                  │
   │ - users    │   │ - eTG chunks     │
   │ - mcq_*    │   │ - AMH chunks     │
   │ - osce_*   │   │ - AMC Handbook   │
   │ - emr_*    │   │   42,647 medical │
   │ - patient_ │   │   text chunks    │
   │   personas │   │                  │
   └────────────┘   └──────────────────┘
```

### Database Integration Strategy

**Current Tables** (Existing):
- `users` (authentication, base user data)
- `user_progress` (⚠️ **BOTH systems extend this table**)
- `mcq_questions`, `mcq_attempts` (MCQ practice)
- `osce_scenarios`, `osce_results` (static OSCE reference content)

**EMR System Tables** (NEW):
- `mock_patients` (500+ patients from OSCE converter)
- `emr_sessions` (student EMR practice attempts)
- `emr_soap_notes` (submitted SOAP notes)
- `emr_validations` (Claude AI feedback)
- `emr_templates` (SOAP note templates library)

**AI OSCE System Tables** (NEW):
- `patient_personas` (360 AI patient profiles)
- `osce_attempts` (8-min conversation sessions)
- `osce_scores` (AMC 15-mark rubric results)
- `mock_exams` (16-station exam orchestration)

**Critical Integration Point**:
Both systems add columns to `user_progress`:
- **EMR adds**: `emr_sessions_completed`, `avg_soap_score`, `last_emr_activity`
- **AI OSCE adds**: `osce_attempts_count`, `avg_osce_score`, `last_osce_activity`, `mock_exams_completed`

**Solution**: Combined Alembic migration adding ALL 7 columns at once (prevents conflicts).

---

## 🔒 PART 1: SHARED INFRASTRUCTURE (WEEK 1 - FOUNDATION)

**Timeline**: Week 1 (5 working days)
**Total Effort**: 15 hours
**Priority**: P0-CRITICAL (BLOCKS both EMR and AI OSCE)

### 1.1 HashiCorp Vault Integration (4 hours)

**Reference Document**: `docs/VAULT_INTEGRATION.md` (update with AI OSCE keys)

**Key Hierarchy**:
```
secret/
├── database/
│   ├── postgres-irstudy-password (both systems)
│   └── postgres-connection-string (both systems)
├── emr/
│   ├── claude-api-key (EMR SOAP validator)
│   ├── session-encryption-key (EMR data at rest)
│   └── template-signing-key (EMR template integrity)
├── ai-osce/
│   ├── claude-api-key (AI Patient/Examiner - shared with EMR)
│   ├── kimi-api-key (fallback for AI Patient)
│   ├── redis-password (OSCE session storage)
│   ├── websocket-secret (JWT for WebSocket auth)
│   └── session-encryption-key (transcript encryption)
└── shared/
    ├── jwt-secret (authentication token signing)
    ├── https-tls-cert (SSL certificate)
    └── https-tls-key (SSL private key)
```

**Access Control Policies**:
- EMR backend service: Read `secret/emr/*`, `secret/database/*`, `secret/shared/jwt-secret`
- AI OSCE backend service: Read `secret/ai-osce/*`, `secret/database/*`, `secret/shared/jwt-secret`
- Admin: Full access (rotate keys, create policies)

**Implementation Tasks**:
1. Install Vault server (self-hosted, development mode for testing)
2. Create key hierarchy (script: `scripts/vault-setup.sh`)
3. Write access policies (HCL format)
4. Update backend code to read from Vault (replace hardcoded placeholders)
5. Test key rotation workflow

**Agent**: security-compliance-expert
**Quality Gate**: 0 hardcoded credentials in codebase (verified by `scripts/security-audit.sh`)

---

### 1.2 Redis Architecture & Deployment (3 hours)

**Reference Document**: `backend/infrastructure/REDIS_ARCHITECTURE.md` (NEW - to create)

**Namespace Strategy**:
```redis
# EMR System (512 MB allocation)
emr:dashboard:user:{user_id}           # Dashboard analytics cache (TTL: 5 min)
emr:ratelimit:{ip_address}             # API rate limiting (TTL: 1 min)
emr:session:{session_id}:autosave      # Auto-save buffer (TTL: 1 hour)

# AI OSCE System (2 GB allocation)
osce:session:{session_id}:state        # Active session state (8-min conversations)
osce:session:{session_id}:transcript   # Real-time transcript (synced to PostgreSQL every 30s)
osce:session:{session_id}:emotional    # Emotional state machine (6 states)
osce:ratelimit:claude:{user_id}        # Claude API rate limiting (TTL: 1 min)
```

**Memory Configuration**:
```conf
# redis.conf
maxmemory 2560mb                       # 2.5 GB total (512 MB EMR + 2 GB OSCE)
maxmemory-policy allkeys-lru           # Evict least recently used (EMR cache only)

# Namespace-specific eviction (via Redis modules)
maxmemory-namespace emr:* policy lru   # LRU for EMR (cache can be evicted)
maxmemory-namespace osce:* policy noeviction  # Never evict active OSCE sessions
```

**Persistence Strategy**:
- **RDB snapshots**: Every 5 minutes (safety for OSCE sessions)
- **AOF (Append-Only File)**: Enabled for OSCE session data (durability)
- **Backup**: Daily snapshot to S3/object storage

**Implementation Tasks**:
1. Deploy Redis server (Docker container or managed service)
2. Configure namespace eviction policies
3. Enable persistence (RDB + AOF)
4. Update backend code with Redis clients (EMR: `backend/src/core/redis_emr.py`, OSCE: `backend/src/core/redis_osce.py`)
5. Test failover and recovery

**Agent**: rust-ffi-expert
**Quality Gate**: Redis operational, 0 namespace collisions (integration test)

---

### 1.3 Unified Security Test Suite (6 hours)

**Reference Document**: `backend/tests/test_security/test_security_comprehensive.py` (expand from 15 → 35 tests)

**Test Coverage**:

**EMR Security Tests** (15 existing):
1. No hardcoded database credentials
2. PHI encrypted at rest (AES-256-GCM)
3. PHI anonymized in Claude API calls
4. HTTPS enforced (HTTP → HTTPS redirect)
5. JWT validation on all endpoints
6. SQL injection prevention (Pydantic validation)
7. XSS prevention (output encoding)
8. CSRF protection (SameSite cookies)
9. Rate limiting active (60 req/min per IP)
10. Prompt injection blocked (Claude validator)
11. Vault integration operational
12. Security headers present (9 headers)
13. Password hashing (Argon2id)
14. Session timeout (30 min inactivity)
15. Audit logging (all PHI access logged)

**AI OSCE Security Tests** (20 new):
16. OSCE transcripts encrypted at rest (AES-256-GCM)
17. WebSocket JWT authentication enforced
18. WebSocket connection rate limiting (5 connections/min per user)
19. Redis session data encrypted in transit (TLS)
20. Claude API PHI anonymization (AI Patient responses)
21. Kimi API fallback credential security
22. Prompt injection blocked (AI Patient system prompts)
23. OSCE conversation PII redaction (names, MRNs)
24. Mock exam data integrity (cannot modify scores post-submission)
25. Patient persona content validation (no PHI in personas)
26. WebSocket message size limits (prevent DoS)
27. Session hijacking prevention (JWT rotation)
28. OSCE session timeout (8 min hard limit)
29. AI Examiner scoring tampering prevention
30. Redis key expiration enforced (no orphaned sessions)
31. HTTPS for WebSocket (wss:// only)
32. Cross-origin WebSocket blocked (same-origin policy)
33. AI Patient emotional state integrity (cannot be client-manipulated)
34. Claude API key rotation tested (zero downtime)
35. Unified audit log (EMR + OSCE actions logged)

**Implementation Tasks**:
1. Expand `test_security_comprehensive.py` with 20 OSCE tests
2. Create `backend/tests/test_security/test_websocket_security.py` (WebSocket-specific)
3. Create `backend/tests/test_security/test_ai_prompt_injection.py` (LLM security)
4. Run full suite (target: 100% pass rate)
5. Integrate with CI/CD (block deployment if any test fails)

**Agent**: security-compliance-expert
**Quality Gate**: 35/35 tests pass (100%), 0 HIGH/CRITICAL findings in security audit

---

### 1.4 HTTPS & JWT Configuration (2 hours)

**Reference Document**: `backend/src/middleware/https_redirect.py` (apply to both systems)

**Security Headers** (9 headers, consistent across EMR + OSCE):
```python
headers = {
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Content-Security-Policy": "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
    "Cache-Control": "no-store, max-age=0",
    "Pragma": "no-cache"
}
```

**Unified JWT Format**:
```json
{
  "user_id": "uuid",
  "email": "student@example.com",
  "role": "student",
  "user_progress_id": "uuid",
  "subscription_tier": "premium",
  "mock_exam_access": true,
  "emr_session_limit": 50,
  "osce_session_limit": 30,
  "iat": 1708041600,
  "exp": 1708045200
}
```

**Implementation Tasks**:
1. Update `backend/src/core/auth.py` to include all JWT claims
2. Apply HTTPS middleware to EMR endpoints (`/api/v1/emr/*`)
3. Apply HTTPS middleware to AI OSCE endpoints (`/api/v1/osce/*`)
4. Configure WebSocket TLS (wss://)
5. Test HTTP → HTTPS redirect (integration test)

**Agent**: security-compliance-expert
**Quality Gate**: All endpoints HTTPS-only, JWT validation passes for both systems

---

### Week 1 Summary

**Deliverables**:
- ✅ Vault operational with unified key hierarchy
- ✅ Redis deployed with namespace separation (emr:* vs osce:*)
- ✅ 35 security tests passing (15 EMR + 20 OSCE)
- ✅ HTTPS enforced with 9 security headers
- ✅ Unified JWT format deployed

**Total Effort**: 15 hours
**Agents**: security-compliance-expert (12 hours), rust-ffi-expert (3 hours)
**Blocker Status**: CLEARS path for EMR and AI OSCE implementation

---

## 📋 PART 2: EMR PRACTICE SYSTEM (WEEK 2-4)

**Timeline**: Week 2-4 (3 weeks)
**Total Effort**: 67.5-73.5 hours
**Status**: PRDs complete, ready for implementation

### Reference Documents
- **COMPREHENSIVE_EMR_IMPLEMENTATION_SUMMARY.md** (detailed implementation plan)
- **16-feb-ralph-prds/** (14 EMR PRDs)

### Quick Summary

**18 Critical Fixes** implemented across:
1. **Backend** (12 fixes - 21.5 hours):
   - Transaction safety (ACID-compliant submit endpoint)
   - Database encryption (PHI encrypted at rest)
   - Claude API fallback (100% uptime)
   - Performance optimization (submit <500ms)
   - Security hardening (PHI anonymization, prompt injection prevention)
   - Health checks for Kubernetes
   - AI validation accuracy (≥85% vs expert SOAP notes)

2. **Frontend** (6 fixes - 14-18 hours):
   - Dashboard performance (2s → 500-700ms via parallel requests)
   - Auto-save efficiency (60 API calls/min → 2-3 calls/min)
   - Error recovery (React Error Boundaries)
   - Theme switching (Epic light / Cerner dark auto-detection)
   - API contract standardization (snake_case ↔ camelCase)

3. **Security Infrastructure** (5 areas - 8-10 hours):
   - Vault integration (completed in Week 1)
   - PHI detection (automated scanning)
   - HTTPS enforcement (completed in Week 1)
   - Security audit script (`scripts/security-audit.sh`)

4. **Testing** (2 suites - 24 hours):
   - Accessibility (56 WCAG 2.2 AA/AAA tests)
   - Security penetration testing (35 OWASP tests, includes 15 from Week 1)

### Implementation Phases

**Phase 1: Critical Security** (Week 2, 8 hours)
- Database encryption (Fix #2)
- PHI anonymization (Fix #5)
- Transaction handling (Fix #1)

**Phase 2: Reliability** (Week 2, 5 hours)
- Claude API fallback (Fix #3)
- Health checks (Fix #9)
- Database constraints (Fix #8)

**Phase 3: Performance** (Week 3, 4 hours)
- Parallel dashboard requests (Frontend Fix #3)
- Auto-save debounce (Frontend Fix #4)
- Performance targets updated (Fix #4)

**Phase 4: Security Hardening** (Week 3, 3.5 hours)
- Prompt injection prevention (Fix #6)
- Rate limiting (Fix #7)
- Error boundaries (Frontend Fix #5)

**Phase 5: Quality & Testing** (Week 4, 24 hours)
- AI benchmark dataset (Fix #11)
- Accessibility tests (56 tests)
- Security penetration tests (35 tests total)

**Phase 6: Integration** (Week 4, 10 hours)
- PRD_BACKEND_005 (Dashboard API - 3 missing endpoints)
- Theme switching (Frontend Fix #2)
- API contract standardization (Frontend Fix #6)

### Agents Assigned
- **rust-ffi-expert**: 12 backend fixes (21.5 hours)
- **flutter-desktop-expert**: 6 frontend fixes (14-18 hours)
- **security-compliance-expert**: Security infrastructure (coordinated with Week 1)
- **testing-qa-expert**: Accessibility & penetration testing (24 hours)

### Quality Gates (MUST PASS)
- [ ] All 18 critical fixes implemented
- [ ] 328 tests pass (237 existing + 91 new) - 100% pass rate
- [ ] Performance: <500ms submit, <1s dashboard, <200ms auto-save
- [ ] Security: 0 hardcoded credentials, PHI encrypted, HTTPS enforced
- [ ] Accessibility: 56 WCAG 2.2 AA/AAA tests pass, 0 axe-core violations

### Dependencies
- ✅ Requires Week 1 (Shared Infrastructure) COMPLETE before starting
- ✅ Can run IN PARALLEL with AI OSCE Phase 1 (different codebases, minimal overlap)

---

## 🤖 PART 3: AI OSCE SIMULATION SYSTEM (WEEK 3-8)

**Timeline**: Week 3-8 (4-6 weeks)
**Total Effort**: 192-236 hours
**Status**: PRDs complete, implementation not started

### Reference Documents
- **ai-osce-ralph-prds/IMPLEMENTATION_STATUS.md** (detailed status)
- **ai-osce-ralph-prds/PRD_AI_OSCE_001-008.md** (8 PRDs, 476 KB, 11,459 lines)

### System Overview

**8 PRDs** covering complete AI OSCE simulation:
1. **PRD_001**: Database & APIs (82 KB, 2,201 lines) - 16-20 hours
2. **PRD_002**: AI Integration (88 KB, 1,956 lines) - 20-24 hours
3. **PRD_003**: WebSocket Infrastructure (44 KB, 1,081 lines) - 18-20 hours
4. **PRD_004**: Scoring System (57 KB, 1,359 lines) - 24-28 hours
5. **PRD_005**: Frontend Implementation (51 KB, 1,162 lines) - 20-24 hours
6. **PRD_006**: Mock Exam Mode (55 KB, 1,395 lines) - 20-24 hours
7. **PRD_007**: Testing & Validation (54 KB, 1,288 lines) - 32-36 hours
8. **PRD_008**: Content Creation (45 KB, 1,017 lines) - 80-100 hours

### Implementation Phases

#### Phase 1: Foundation (Week 3-4, 59-70 hours)

**PRD_001: Database & APIs** (16-20 hours)
- Create 4 new tables: `patient_personas`, `osce_attempts`, `osce_scores`, `mock_exams`
- Extend `user_progress` table (⚠️ **coordinate with EMR** - combined migration)
- Implement 6 API endpoints (personas, sessions, transcripts, scoring)
- Alembic migration: `20260217_1200_011_ai_osce_tables.py`

**PRD_003: WebSocket Infrastructure** (18-20 hours)
- WebSocket server with JWT authentication
- 8-minute timer with 1-minute warning
- Redis session state management (namespace: `osce:*`)
- Background sync to PostgreSQL (every 30 seconds)
- Message queuing and error handling

**PRD_008: Content Creation - Phase 1** (25-30 hours)
- Create persona template (JSON schema)
- Generate 120 foundation personas (15 per specialty × 8 specialties)
- Expert clinical review (≥2 clinicians per persona)
- Cultural diversity audit (3.3% Aboriginal/TSI in foundation set)

**Agent Assignment**:
- **rust-ffi-expert**: PRD_001 + PRD_003 (backend infrastructure)
- **aba-clinical-expert**: PRD_008 Phase 1 (content creation)

**Quality Gates**:
- [ ] Database migrations run successfully (4 tables created)
- [ ] WebSocket connections established (JWT auth working)
- [ ] 120 foundation personas validated by experts
- [ ] Redis `osce:*` namespace operational

---

#### Phase 2: AI Integration (Week 5, 45-54 hours)

**PRD_002: AI Integration** (20-24 hours)
- AI Patient system prompts (emotional intelligence, 6-state machine)
- AI Examiner scoring prompts (AMC 15-mark rubric)
- RAG integration with Qdrant (eTG/AMH/AMC Handbook references)
- AI Router (Claude primary, Kimi fallback)
- Progressive disclosure logic

**PRD_008: Content Creation - Phase 2** (25-30 hours)
- Generate 180 intermediate personas (22 per specialty × 8 specialties)
- Expert clinical review (≥2 clinicians per persona)
- Cultural diversity audit (3.3% Aboriginal/TSI in intermediate set)
- Emotional state machine testing (10 sample personas)

**Agent Assignment**:
- **aba-clinical-expert**: PRD_002 + PRD_008 Phase 2

**Quality Gates**:
- [ ] AI Patient responds naturally (emotional states transition correctly)
- [ ] RAG integration operational (eTG/AMH references validated)
- [ ] 180 intermediate personas validated by experts
- [ ] Claude API fallback tested (Kimi API working)

---

#### Phase 3: Scoring & Frontend (Week 6-7, 64-82 hours)

**PRD_004: Scoring System** (24-28 hours)
- AMC 15-mark rubric implementation
- Critical error detection (20+ rules, auto-fail conditions)
- Scoring confidence calculation (0.0-1.0)
- Feedback generation (strengths, improvements, narrative)
- Golden Dataset management (200 expert-scored scenarios)
- Scoring prompt versioning

**PRD_005: Frontend Implementation** (20-24 hours)
- Persona browser with filters (specialty, difficulty)
- Chat interface with WebSocket integration
- 8-minute timer display with warnings
- Results display (score breakdown, AMC rubric visualization)
- Transcript viewer with emotional state annotations
- WCAG 2.2 AA accessibility compliance

**PRD_008: Content Creation - Phase 3** (30-40 hours)
- Generate 60 advanced personas (8 per specialty × 8 specialties)
- Expert clinical review (≥2 clinicians per persona)
- Final cultural diversity validation (12 Aboriginal/TSI total across 360)
- Database import (all 360 personas to PostgreSQL)
- End-to-end QA testing (20 sample personas with students)

**Agent Assignment**:
- **aba-clinical-expert**: PRD_004 + PRD_008 Phase 3
- **flutter-desktop-expert**: PRD_005 (React frontend)

**Quality Gates**:
- [ ] AMC 15-mark scoring accurate (±2 marks vs human examiner)
- [ ] Golden Dataset validated (200 scenarios, AI vs expert agreement)
- [ ] Frontend WCAG 2.2 AA compliant (automated axe-core tests)
- [ ] 360 personas imported to database and accessible
- [ ] E2E test: Select persona → Complete OSCE → View score

---

#### Phase 4: Advanced Features (Week 8, 52-60 hours)

**PRD_006: Mock Exam Mode** (20-24 hours)
- 16-station sequential exam orchestration
- Auto-persona selection (balanced across 8 specialties)
- Station progression (8 min each, 5-sec breaks between)
- Overall scoring calculation (sum of 16 stations, /240 marks)
- Comprehensive PDF report generation

**PRD_007: Testing & Validation** (32-36 hours)
- Load testing (100 concurrent sessions with Locust)
- Golden Dataset validation (200 scenarios)
- E2E testing with Playwright (6 critical workflows)
- Security testing (JWT, WebSocket, prompt injection, XSS, SQL injection)
- Performance benchmarks (<3s AI response, <500ms API, <100ms DB)
- Unit + Integration coverage (≥70%, 100% pass rate)

**Agent Assignment**:
- **general-purpose**: PRD_006 (mock exam orchestration)
- **testing-qa-expert**: PRD_007 (comprehensive testing)

**Quality Gates**:
- [ ] Mock exam mode functional (16 stations, 2.5 hours total)
- [ ] PDF reports generated correctly (score breakdown, feedback)
- [ ] Load testing: 100 concurrent sessions supported
- [ ] Performance: <3s AI response, <500ms API, <100ms DB queries
- [ ] Test coverage ≥70%, 100% pass rate

---

### AI OSCE Summary

**Total Effort**: 192-236 hours across 6 weeks
**Agents**: 5 specialists (Backend, AI/Clinical, Frontend, Testing, Content)
**Dependencies**: Requires Week 1 (Shared Infrastructure) + EMR database migration (user_progress table)

---

## 🔗 PART 4: INTEGRATION LAYER (WEEK 7-8)

**Timeline**: Week 7-8 (1-2 weeks, overlaps with AI OSCE Phase 4)
**Total Effort**: 36-48 hours
**Priority**: P1-High (enables cross-system workflows)

### 4.1 PRD_INTEGRATION_004: AI_OSCE_TO_EMR_CONVERTER (12-16 hours)

**Business Value**: Students complete AI OSCE → Automatically generate pre-filled EMR SOAP note

**File**: `16-feb-ralph-prds/integration/PRD_INTEGRATION_004_AI_OSCE_TO_EMR_CONVERTER.md`

#### Request (What & Why)

**User Story**:
> As a medical student preparing for AMC Clinical Exam,
> I want to convert my AI OSCE conversation transcript into a pre-filled EMR SOAP note,
> So that I can practice documentation skills on the same patient scenario without re-entering all the clinical information.

**Business Context**:
- AI OSCE develops history-taking and communication skills (8-minute conversations)
- EMR practice develops documentation skills (SOAP note writing)
- Currently: Students must manually re-type patient history from OSCE → EMR (10+ minutes wasted)
- Solution: Auto-convert OSCE transcript → pre-filled SOAP note (saves 5-10 minutes, demonstrates learning transfer)

**Success Metrics**:
- SOAP note ≥70% pre-filled (Subjective, Objective sections auto-populated)
- Conversion time <3 seconds (user experience)
- Adoption rate >20% of students (measure pedagogical value)

#### Architecture (How)

**Data Flow**:
```
AI OSCE Attempt (osce_attempts table)
    ↓
Conversation Transcript (JSONB)
    ↓
NLP Extraction Algorithm
    ↓ (extracts)
Subjective Data (patient statements)
Objective Data (examination findings from AI Patient responses)
Assessment (AI Examiner feedback hints)
Plan (student's management suggestions)
    ↓
EMR Session (emr_sessions table)
    ↓
Pre-filled SOAP Note (editable by student)
```

**Extraction Algorithm** (Python + Claude API):
```python
def convert_osce_to_soap(osce_attempt_id: UUID) -> dict:
    """
    Convert AI OSCE transcript to pre-filled SOAP note.

    Returns:
        {
            "subjective": "HPI, PMHx, FHx, SHx extracted from patient responses",
            "objective": "Vital signs, examination findings mentioned by AI Patient",
            "assessment": "Differentials suggested by AI Examiner feedback",
            "plan": "Management steps proposed by student during OSCE"
        }
    """
    # Fetch OSCE transcript
    transcript = get_osce_transcript(osce_attempt_id)

    # Extract patient statements (speaker == "patient")
    patient_responses = [msg for msg in transcript if msg['speaker'] == 'patient']

    # Use Claude API to structure into SOAP format
    prompt = f"""
    You are a medical documentation assistant. Extract clinical information from this OSCE transcript
    and format it into SOAP note sections (Subjective, Objective, Assessment, Plan).

    OSCE Transcript:
    {json.dumps(patient_responses, indent=2)}

    Student Questions and Management Suggestions:
    {json.dumps([msg for msg in transcript if msg['speaker'] == 'student'], indent=2)}

    Return JSON with keys: subjective, objective, assessment, plan.
    Use Australian medical terminology (paracetamol, salbutamol, adrenaline).
    """

    soap_data = claude_api_call(prompt, model="claude-sonnet-4-5-20250929")

    return soap_data
```

**API Endpoint**:
```
POST /api/v1/integration/osce-to-emr
Request:
{
  "osce_attempt_id": "uuid"
}

Response:
{
  "emr_session_id": "uuid",
  "soap_note": {
    "subjective": "...",
    "objective": "...",
    "assessment": "...",
    "plan": "..."
  },
  "prefill_percentage": 73.5,  // How much was auto-filled
  "conversion_time_ms": 2847
}
```

#### Implementation Tasks (12-16 hours)

1. **Task 1**: Create extraction algorithm (`backend/src/services/integration/osce_to_emr_converter.py`) - 4 hours
2. **Task 2**: Create API endpoint (`backend/src/api/v1/integration.py`) - 2 hours
3. **Task 3**: Add frontend "Convert to EMR" button on OSCE results page - 2 hours
4. **Task 4**: Create integration tests (10 scenarios: OSCE → EMR → validate pre-fill accuracy) - 3 hours
5. **Task 5**: Golden Dataset validation (50 OSCE attempts → EMR notes, measure ≥70% pre-fill) - 2-3 hours

**Agent**: rust-ffi-expert (backend) + flutter-desktop-expert (frontend button)

**Quality Gates**:
- [ ] ≥70% SOAP note pre-filled (measured on 50 Golden Dataset cases)
- [ ] Conversion <3 seconds (p95)
- [ ] Australian medical terminology used (paracetamol, eTG references)
- [ ] Integration test: OSCE → EMR → Submit → Validate (E2E workflow)

---

### 4.2 PRD_INTEGRATION_005: UNIFIED_PROGRESS_DASHBOARD (8-12 hours)

**Business Value**: Single dashboard showing MCQ + OSCE + AI OSCE + EMR metrics with correlation analysis

**File**: `16-feb-ralph-prds/integration/PRD_INTEGRATION_005_UNIFIED_PROGRESS_DASHBOARD.md`

#### Request (What & Why)

**User Story**:
> As a medical student using irStudy platform,
> I want to see ALL my practice metrics (MCQ, OSCE, AI OSCE, EMR) in one dashboard,
> So that I can understand my overall progress and see how skills transfer across modalities.

**Success Metrics**:
- Dashboard load time <1 second (all metrics fetched in parallel)
- Correlation visualization: "OSCE practice → EMR accuracy improvement" (pedagogical validation)
- User engagement: >60% of students view dashboard weekly

#### Architecture (How)

**Dashboard Widgets**:
1. **Overall Progress Card**:
   - MCQ: 1,847 questions attempted, 78.3% accuracy
   - OSCE (Static): 45 scenarios reviewed, avg score 12.5/15
   - AI OSCE: 23 attempts, avg score 11.8/15
   - EMR: 67 sessions, 82.1% SOAP accuracy

2. **Specialty Breakdown**:
   - Cardiology: OSCE 13/15, EMR 88% → Strong
   - Respiratory: OSCE 9/15, EMR 71% → Needs improvement
   - etc.

3. **Correlation Analysis** (NEW):
   - Graph: X-axis = OSCE attempts, Y-axis = EMR SOAP accuracy
   - Trendline: "12% EMR improvement after 8 OSCE sessions"
   - Recommendation: "Complete 5 more Respiratory OSCEs to improve EMR documentation in this specialty"

4. **Activity Timeline**:
   - Chronological view of all practice (MCQ, OSCE, AI OSCE, EMR mixed)
   - Date | Activity | Score | Time Spent

**API Endpoints** (extend PRD_BACKEND_005):
```
GET /api/v1/dashboard/unified-progress
Response:
{
  "mcq_stats": {...},
  "osce_static_stats": {...},
  "ai_osce_stats": {...},
  "emr_stats": {...},
  "correlation": {
    "osce_to_emr_improvement": 12.3,  // Percentage improvement
    "sample_size": 23  // Number of students in cohort
  },
  "recommendations": [
    "Complete 5 Respiratory OSCEs to improve EMR accuracy in this specialty"
  ]
}
```

**Frontend Component**:
```tsx
// frontend/src/components/UnifiedProgressDashboard.tsx
export function UnifiedProgressDashboard() {
  const { data, isLoading } = useUnifiedProgressData();  // Parallel API requests

  return (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <OverallProgressCard data={data} />
      </Grid>
      <Grid item xs={6}>
        <SpecialtyBreakdownChart data={data.specialty_breakdown} />
      </Grid>
      <Grid item xs={6}>
        <CorrelationGraph data={data.correlation} />  {/* NEW */}
      </Grid>
      <Grid item xs={12}>
        <ActivityTimeline events={data.timeline} />
      </Grid>
    </Grid>
  );
}
```

#### Implementation Tasks (8-12 hours)

1. **Task 1**: Create unified progress API endpoint (`backend/src/api/v1/dashboard.py`) - 3 hours
2. **Task 2**: Implement correlation calculation (OSCE → EMR improvement algorithm) - 2 hours
3. **Task 3**: Create React dashboard component (`frontend/src/components/UnifiedProgressDashboard.tsx`) - 3 hours
4. **Task 4**: Add correlation graph visualization (Chart.js or Recharts) - 2 hours
5. **Task 5**: Integration testing (verify all metrics appear, load time <1s) - 1-2 hours

**Agent**: flutter-desktop-expert (frontend) + rust-ffi-expert (API endpoint)

**Quality Gates**:
- [ ] Dashboard loads in <1 second (parallel API requests)
- [ ] All 4 practice modalities visible (MCQ, static OSCE, AI OSCE, EMR)
- [ ] Correlation graph accurate (validated on 50+ student cohort)
- [ ] WCAG 2.2 AA accessible (keyboard navigation, screen reader support)

---

### 4.3 Cross-System Integration Testing (16-20 hours)

**Test Suite**: `testing/playwright/tests/integration/cross-system.spec.ts`

**Test Scenarios** (12 E2E workflows):

1. **OSCE → EMR Conversion**:
   - Student completes AI OSCE (8 min)
   - Clicks "Convert to EMR"
   - Verifies SOAP note ≥70% pre-filled
   - Submits EMR → Claude validation
   - Checks score appears in unified dashboard

2. **Mock Exam → Dashboard**:
   - Student completes 16-station mock exam
   - Views PDF report
   - Checks unified dashboard shows overall mock exam score
   - Verifies specialty breakdown updated

3. **Progress Correlation**:
   - Seed database with 50 students (OSCE + EMR data)
   - Call correlation API
   - Verify "OSCE → EMR improvement" calculation correct

4. **Security**:
   - Attempt to access other user's OSCE transcripts (should fail)
   - Attempt to modify submitted EMR scores (should fail)
   - Verify JWT required for all integration endpoints

5-12. [Additional E2E scenarios covering error cases, edge cases, performance]

**Agent**: testing-qa-expert

**Quality Gates**:
- [ ] 12/12 integration tests pass (100%)
- [ ] No data leakage between users
- [ ] Performance: OSCE → EMR conversion <3s, Dashboard load <1s

---

### Integration Layer Summary

**Total Effort**: 36-48 hours
**Deliverables**:
- PRD_INTEGRATION_004: OSCE-to-EMR Converter (40-50 KB PRD + implementation)
- PRD_INTEGRATION_005: Unified Progress Dashboard (35-45 KB PRD + implementation)
- 12 cross-system E2E tests

**Value**:
- Demonstrates pedagogical link (OSCE practice improves EMR skills)
- Saves students 5-10 minutes per scenario (auto-conversion)
- Unified view of all practice modalities (better UX)

---

## 📊 DEPENDENCY GRAPH & TIMELINE

### Critical Path Analysis

```
Week 1: SHARED INFRASTRUCTURE (BLOCKS everything)
├── Vault Integration (4h)
├── Redis Architecture (3h)
├── Security Tests (6h)
└── HTTPS/JWT (2h)
        ↓
Week 2-4: EMR IMPLEMENTATION (can run parallel with OSCE Phase 1)
├── Backend Fixes (21.5h)
├── Frontend Fixes (14-18h)
├── Security Infrastructure (coordinated with Week 1)
└── Testing (24h)
        ↓
Week 3-4: AI OSCE PHASE 1 - FOUNDATION (parallel with EMR)
├── Database & APIs (16-20h)
├── WebSocket Infrastructure (18-20h)
└── Content Creation - Phase 1 (25-30h)
        ↓
Week 5: AI OSCE PHASE 2 - AI INTEGRATION
├── AI Patient/Examiner (20-24h)
└── Content Creation - Phase 2 (25-30h)
        ↓
Week 6-7: AI OSCE PHASE 3 - SCORING & FRONTEND
├── Scoring System (24-28h)
├── Frontend Implementation (20-24h)
└── Content Creation - Phase 3 (30-40h)
        ↓
Week 7-8: INTEGRATION LAYER (overlaps with Phase 4)
├── OSCE-to-EMR Converter (12-16h)
├── Unified Dashboard (8-12h)
└── Cross-System Testing (16-20h)
        ↓
Week 8: AI OSCE PHASE 4 - ADVANCED FEATURES
├── Mock Exam Mode (20-24h)
└── Testing & Validation (32-36h)
        ↓
Week 9: FINAL VALIDATION & DEPLOYMENT
├── Unified Test Suite (all 500+ tests)
├── Security Audit (35 tests + penetration)
├── Performance Benchmarks (all endpoints)
└── Production Deployment
```

### Parallel Work Opportunities

**Weeks 2-4**: EMR + OSCE Phase 1 can run **fully in parallel**
- Different codebases (minimal conflicts)
- Shared infrastructure already complete (Week 1)
- Only dependency: Combined `user_progress` migration (coordinate once)

**Weeks 6-7**: Content Creation Phase 3 + Scoring System can run **in parallel**
- Content team creates personas
- Backend team implements scoring

**Week 7-8**: Integration Layer + OSCE Phase 4 can **overlap**
- Integration testing can start while mock exam mode is being built

---

## 💰 COST ANALYSIS & RESOURCE ALLOCATION

### Monthly Cost Projection

#### Current State (MCQ Only)
- PostgreSQL: $0 (self-hosted)
- Claude API: $0 (no AI features deployed)
- Redis: $0 (not deployed)
- **Total**: $0/month

#### After EMR Implementation (Month 1-2)
- Claude API: $8/month (40% usage, 60% fallback to rule-based)
- Redis: $12/month (dashboard caching, rate limiting)
- Vault: $0 (self-hosted)
- **Total**: $20/month

#### After AI OSCE Implementation (Month 3+)

| User Scenario | EMR Claude | OSCE Claude | Redis | Total |
|---------------|------------|-------------|-------|-------|
| **500 users, 25% adoption** | $8 | $36 | $22 | **$66/month** |
| **1000 users, 50% EMR + 30% OSCE** | $8 | $64 | $32 | **$104/month** |
| **2000 users, 60% adoption** | $12 | $96 | $45 | **$153/month** |

**Assumptions**:
- EMR: 50 sessions/month per active user, $0.002/session (Claude API)
- AI OSCE: 4 sessions/month per active user, $0.06/session (Claude API for AI Patient + Examiner)
- Redis: $12 base + $10 per 500 active OSCE users
- Vault: $0 (self-hosted development mode, production may need HashiCorp Enterprise)

**Budget Recommendation**: $200/month (30% buffer for growth, Black Friday surge, etc.)

---

### Resource Allocation (Agent Hours)

| Agent | Week 1 | Week 2-4 | Week 5-7 | Week 8 | Total Hours |
|-------|--------|----------|----------|--------|-------------|
| **security-compliance-expert** | 12h (Vault, security tests) | Coordinated | - | - | **12h** |
| **rust-ffi-expert** | 3h (Redis) | 21.5h (EMR backend) + 34-40h (OSCE DB/WebSocket) | - | 12-16h (Integration) | **70.5-91.5h** |
| **flutter-desktop-expert** | - | 14-18h (EMR frontend) | 20-24h (OSCE frontend) | 8-12h (Dashboard) | **42-54h** |
| **aba-clinical-expert** | - | - | 45-54h (AI integration) + 55-70h (Content Phase 2-3) | 24-28h (Scoring) | **124-152h** |
| **testing-qa-expert** | - | 24h (EMR tests) | - | 32-36h (OSCE tests) + 16-20h (Integration) | **72-80h** |
| **general-purpose** | - | - | - | 20-24h (Mock exam) | **20-24h** |
| **TOTAL** | **15h** | **59.5-79.5h** | **120-148h** | **112-136h** | **306.5-378.5h** |

**Adjusted for Parallel Work**:
- Weeks 2-4: EMR (35.5h) + OSCE Phase 1 (59-70h) run parallel → **Actual: 4 weeks elapsed**
- Weeks 5-7: OSCE Phase 2-3 (120-148h) → **Actual: 3 weeks elapsed**
- Week 8: OSCE Phase 4 + Integration (overlap) → **Actual: 1-2 weeks elapsed**

**Timeline**: 6-8 weeks calendar time (with parallel work)
**Total Effort**: 306.5-378.5 agent hours
**Average**: ~50 hours/week (across 6-7 parallel agents)

---

## ✅ UNIFIED QUALITY GATES

### Must Pass Before Production Deployment

#### Shared Infrastructure (Week 1)
- [ ] **Vault**: Operational, 0 hardcoded credentials detected by `scripts/security-audit.sh`
- [ ] **Redis**: Namespaces configured (emr:* vs osce:*), 0 key collisions in integration tests
- [ ] **Security Tests**: 35/35 pass (15 EMR + 20 OSCE)
- [ ] **HTTPS**: All endpoints redirect HTTP → HTTPS, 9 security headers present
- [ ] **JWT**: Unified token format deployed, validation working for both systems

#### EMR System (Week 2-4)
- [ ] **Tests**: 328/328 pass (100% pass rate)
- [ ] **Performance**: <500ms submit (p95), <1s dashboard (p95), <200ms auto-save (p95)
- [ ] **Security**: PHI encrypted at rest, PHI anonymized in Claude API, prompt injection blocked
- [ ] **Accessibility**: 56/56 WCAG 2.2 AA/AAA tests pass, 0 axe-core violations
- [ ] **AI Accuracy**: Claude validator ≥85% accuracy vs 100 expert SOAP notes

#### AI OSCE System (Week 3-8)
- [ ] **Content**: 360 patient personas loaded, ≥2 clinicians validated each
- [ ] **Cultural Diversity**: 12 Aboriginal/TSI personas (3.3% of 360)
- [ ] **AI Patient**: Emotional state transitions working (6 states)
- [ ] **AI Examiner**: Scoring ±2 marks vs human examiner (96%+ accuracy)
- [ ] **Performance**: <3s AI response (p95), <500ms API (p95), <100ms DB queries (p95)
- [ ] **WebSocket**: 8-min sessions working, Redis sync every 30s
- [ ] **Mock Exam**: 16-station mode functional, PDF reports generated
- [ ] **Tests**: ≥70% coverage, 100% pass rate
- [ ] **Load Testing**: 100 concurrent sessions supported (Locust)

#### Integration Layer (Week 7-8)
- [ ] **OSCE-to-EMR**: ≥70% SOAP pre-fill (measured on 50 Golden Dataset cases)
- [ ] **Conversion Speed**: <3 seconds (p95)
- [ ] **Unified Dashboard**: Load time <1s, correlation graph accurate
- [ ] **Cross-System Tests**: 12/12 integration tests pass (100%)
- [ ] **Security**: No data leakage between users, JWT required for all endpoints

#### Platform-Wide (Week 9)
- [ ] **All Tests**: 500+ tests pass (EMR + OSCE + Integration) - 100% pass rate
- [ ] **Security Audit**: 0 HIGH/CRITICAL findings (OWASP Top 10 coverage)
- [ ] **Performance**: All benchmarks met (see targets above)
- [ ] **Accessibility**: WCAG 2.2 AA compliance across all UIs
- [ ] **Documentation**: All PRDs up-to-date, deployment runbook complete
- [ ] **Monitoring**: Health checks operational (Kubernetes probes)
- [ ] **Cost**: Monthly spend <$200 (within budget)

---

## 🚀 DEPLOYMENT STRATEGY

### Pre-Deployment Checklist

**Infrastructure**:
- [ ] Vault server deployed (production mode, HA if using managed service)
- [ ] Redis cluster deployed (2.5 GB memory, RDB+AOF persistence enabled)
- [ ] PostgreSQL backups automated (daily snapshots to S3/object storage)
- [ ] Qdrant vector DB operational (42,647 chunks indexed)
- [ ] TLS certificates valid (Let's Encrypt or commercial CA)

**Configuration**:
- [ ] Environment variables set (`VAULT_ADDR`, `REDIS_URL`, `DATABASE_URL`)
- [ ] Vault policies applied (EMR service, OSCE service, admin)
- [ ] Redis namespaces configured (maxmemory policies set)
- [ ] JWT secret rotated (production key, not dev placeholder)
- [ ] Claude API key valid (Tier 2+ for production load)

**Monitoring**:
- [ ] Prometheus metrics enabled (all endpoints instrumented)
- [ ] Grafana dashboards configured (performance, errors, costs)
- [ ] Alerting rules set (API latency >5s, error rate >5%, Redis memory >80%)
- [ ] Log aggregation operational (CloudWatch, ELK, or similar)

### Rollout Plan

**Phase 1: Soft Launch** (Week 9, 50 beta users)
- Deploy EMR + AI OSCE to staging environment
- Invite 50 volunteer students (diverse specialties)
- Monitor: Error rates, performance, user feedback
- Duration: 1 week
- Success criteria: <5% error rate, >4/5 user satisfaction

**Phase 2: Gradual Rollout** (Week 10-11, 500 users)
- Deploy to production (25% traffic)
- Enable EMR for 250 users, AI OSCE for 150 users
- Monitor costs (should be ~$50-70/month at this scale)
- Duration: 2 weeks
- Success criteria: Costs within budget, performance targets met

**Phase 3: Full Deployment** (Week 12+, all users)
- Enable for all 1000+ users
- Monitor: Claude API rate limits (may need to upgrade to Tier 3)
- Auto-scaling: Redis memory, PostgreSQL connections
- Success criteria: 99.5%+ uptime, <$200/month costs

### Rollback Plan

**If critical issues detected**:
1. Feature flag toggle (disable EMR or OSCE via admin panel)
2. Revert database migrations (Alembic downgrade)
3. Restore Redis snapshot (last 5-min backup)
4. Notify users (email: "Platform maintenance, estimated restoration 2 hours")

**Rollback triggers**:
- Error rate >10% for 5 consecutive minutes
- API latency >10s p95 for 5 consecutive minutes
- Security breach detected (unauthorized data access)
- Cost spike >$500/day (Claude API abuse)

---

## 📚 SUPPORTING DOCUMENTATION

### Documents to Create (10-13 hours)

1. **SHARED_INFRASTRUCTURE_SPEC.md** (15-20 KB, 2 hours)
   - Vault key hierarchy
   - Redis architecture
   - JWT token format
   - Security headers
   - Encryption standards

2. **backend/infrastructure/REDIS_ARCHITECTURE.md** (8-10 KB, 1 hour)
   - Namespace strategy
   - Memory allocation
   - Eviction policies
   - Persistence (RDB + AOF)
   - Backup procedures

3. **docs/VAULT_INTEGRATION.md** (update, +5 KB, 1 hour)
   - Add AI OSCE secret hierarchy
   - Access control policies
   - Key rotation procedures

4. **PRD_INTEGRATION_004: AI_OSCE_TO_EMR_CONVERTER.md** (40-50 KB, 4 hours)
   - Full RALPH structure
   - NLP extraction algorithm
   - API specification
   - Testing requirements

5. **PRD_INTEGRATION_005: UNIFIED_PROGRESS_DASHBOARD.md** (35-45 KB, 3 hours)
   - Full RALPH structure
   - Dashboard widgets
   - Correlation calculation
   - API endpoints

6. **docs/DEPLOYMENT_RUNBOOK.md** (20-25 KB, 2 hours)
   - Pre-deployment checklist
   - Rollout plan
   - Monitoring setup
   - Rollback procedures

**Total**: 10-13 hours documentation effort

---

## 🎯 SUCCESS METRICS

### Technical Metrics

**Performance**:
- [ ] EMR submit endpoint: <500ms p95 ✅
- [ ] EMR dashboard load: <1s p95 ✅
- [ ] AI OSCE AI response: <3s p95 ✅
- [ ] AI OSCE API: <500ms p95 ✅
- [ ] Database queries: <100ms p95 ✅
- [ ] Unified dashboard: <1s p95 ✅

**Reliability**:
- [ ] Platform uptime: 99.5%+ (measured monthly)
- [ ] Claude API uptime: 100% (via fallback mechanisms)
- [ ] Redis availability: 99.9%+ (HA deployment)
- [ ] Zero data loss (PostgreSQL + Redis persistence)

**Security**:
- [ ] 0 hardcoded credentials (continuous monitoring)
- [ ] 0 HIGH/CRITICAL security findings (monthly scans)
- [ ] 100% HTTPS coverage (all endpoints)
- [ ] PHI encrypted (EMR + OSCE transcripts)
- [ ] Audit logs complete (all PHI access logged)

**Quality**:
- [ ] Test pass rate: 100% (500+ tests)
- [ ] Test coverage: ≥70% (unit + integration)
- [ ] Accessibility: WCAG 2.2 AA compliant (0 axe-core violations)
- [ ] AI accuracy: EMR ≥85%, OSCE ±2 marks

### User Experience Metrics

**Adoption**:
- [ ] EMR practice: >50% of active students (Month 3)
- [ ] AI OSCE practice: >30% of active students (Month 3)
- [ ] OSCE-to-EMR conversion: >20% adoption (Month 6)
- [ ] Unified dashboard views: >60% weekly active users

**Satisfaction**:
- [ ] Platform rating: ≥4.5/5 (user surveys)
- [ ] EMR practice: ≥4/5 satisfaction
- [ ] AI OSCE realism: ≥4/5 satisfaction
- [ ] Dashboard usefulness: ≥4/5 satisfaction

**Pedagogical Value**:
- [ ] OSCE practice → EMR accuracy correlation: >10% improvement (validated)
- [ ] Mock exam → Real AMC exam correlation: >0.7 (Pearson's r)
- [ ] Session completion rate: >90% (students finish what they start)

### Cost Metrics

- [ ] Monthly costs: <$200 (within budget)
- [ ] Cost per active user: <$0.20/month (at 1000 users)
- [ ] Claude API efficiency: >60% fallback rate (EMR), >30% Kimi usage (OSCE)
- [ ] Redis memory efficiency: <80% utilization (no eviction of active sessions)

---

## 📞 CONTACTS & OWNERSHIP

### Agent Assignments

| Agent | Responsibility | Contact (Task Tool) |
|-------|----------------|---------------------|
| **project-manager-coordinator** | Overall coordination, quality gates | `subagent_type: project-manager-coordinator` |
| **security-compliance-expert** | Vault, security tests, HTTPS | `subagent_type: security-compliance-expert` |
| **rust-ffi-expert** | Backend (EMR + OSCE APIs, WebSocket) | `subagent_type: rust-ffi-expert` |
| **flutter-desktop-expert** | Frontend (React, dashboards) | `subagent_type: flutter-desktop-expert` |
| **aba-clinical-expert** | AI integration, content creation, scoring | `subagent_type: aba-clinical-expert` |
| **testing-qa-expert** | Testing, QA, accessibility | `subagent_type: testing-qa-expert` |
| **general-purpose** | Mock exam mode, misc tasks | `subagent_type: general-purpose` |

### Documentation References

**Master Plans**:
- This document: `COMPREHENSIVE_PLATFORM_IMPLEMENTATION_MASTER.md`
- EMR-specific: `COMPREHENSIVE_EMR_IMPLEMENTATION_SUMMARY.md`
- AI OSCE-specific: `ai-osce-ralph-prds/IMPLEMENTATION_STATUS.md`

**PRDs**:
- EMR PRDs: `16-feb-ralph-prds/` (14 PRDs)
- AI OSCE PRDs: `ai-osce-ralph-prds/` (8 PRDs)
- Integration PRDs: `16-feb-ralph-prds/integration/` (3 existing + 2 new)

**Infrastructure**:
- `SHARED_INFRASTRUCTURE_SPEC.md` (to be created)
- `backend/infrastructure/REDIS_ARCHITECTURE.md` (to be created)
- `docs/VAULT_INTEGRATION.md` (to be updated)

**Constraints & Guidelines**:
- `constraints/README.md` (project constraints)
- `~/.claude/CLAUDE.md` (agent coordination protocol)
- `CLAUDE.md` (project-specific instructions)

---

## 🏁 NEXT STEPS

### Immediate Actions (Today)

1. **PM Review** (1-2 hours):
   - Review this master plan
   - Approve combined approach (EMR + AI OSCE integration)
   - Sign off on 6-8 week timeline

2. **User Approval**:
   - Present cost analysis ($104-153/month at scale)
   - Present pedagogical value (OSCE → EMR correlation)
   - Get budget approval ($200/month recommended)

3. **Begin Week 1** (Shared Infrastructure):
   - Delegate to security-compliance-expert: Vault + security tests (12 hours)
   - Delegate to rust-ffi-expert: Redis architecture (3 hours)
   - Target completion: Friday (5 working days)

### Week 1 Kickoff

**Monday**:
- security-compliance-expert: Vault setup (4 hours)
- rust-ffi-expert: Redis deployment (3 hours)

**Tuesday-Wednesday**:
- security-compliance-expert: Security test suite expansion (6 hours)

**Thursday**:
- security-compliance-expert: HTTPS/JWT configuration (2 hours)
- PM: Validate Week 1 quality gates

**Friday**:
- All: Week 1 review meeting
- PM: Approve EMR + OSCE Phase 1 to start Monday Week 2

### Week 2+ Planning

**Week 2**: EMR Phase 1-2 + OSCE Phase 1 (parallel)
**Week 3-4**: EMR Phase 3-6 + OSCE Phase 1 completion
**Week 5**: OSCE Phase 2 (AI integration)
**Week 6-7**: OSCE Phase 3 (scoring + frontend)
**Week 7-8**: Integration Layer + OSCE Phase 4
**Week 9**: Final validation + production deployment

---

## 📈 RISK REGISTER

### High-Risk Items (Mitigation Required)

**RISK-1: Claude API Rate Limits**
- **Probability**: High (90 req/min combined exceeds Tier 1 limit of 50 req/min)
- **Impact**: HIGH (blocks both EMR validation and AI OSCE)
- **Mitigation**:
  - Priority queue: AI Patient > AI Examiner > EMR validator
  - Fallback: Kimi API for AI Patient (70% quality, lower cost)
  - Upgrade: Claude Tier 2 ($500/month minimum, 200 req/min)
- **Owner**: rust-ffi-expert (implement priority queue)

**RISK-2: Redis Memory Exhaustion**
- **Probability**: Medium (OSCE sessions = 2 GB at 100 concurrent users)
- **Impact**: HIGH (active sessions lost, student frustration)
- **Mitigation**:
  - Monitoring: Alert at 80% memory usage
  - Auto-scaling: Add Redis instance at 85%
  - Persistence: RDB+AOF ensures no data loss
- **Owner**: rust-ffi-expert

**RISK-3: Content Creation Delays (360 Personas)**
- **Probability**: High (80-100 hours, expert clinician availability)
- **Impact**: MEDIUM (blocks OSCE frontend testing)
- **Mitigation**:
  - Start Phase 1 (120 personas) early (Week 3)
  - Parallel work: Frontend can use 120 personas for testing
  - Contingency: Reduce scope to 240 personas (30 per specialty)
- **Owner**: aba-clinical-expert + PM

**RISK-4: Agent Coordination Failures**
- **Probability**: Medium (9-11 agents working parallel/sequential)
- **Impact**: HIGH (systematic mistakes like 124 hardcoded credentials)
- **Mitigation**:
  - Sequential validation (Agent → Self-validate → PM validate → Next agent)
  - Reference: `~/.claude/CLAUDE.md` Expert Agent Workflow
  - Front-load context: All agents read `SHARED_INFRASTRUCTURE_SPEC.md`
- **Owner**: project-manager-coordinator

**RISK-5: OSCE-to-EMR Conversion Quality**
- **Probability**: Medium (NLP extraction is complex)
- **Impact**: MEDIUM (low adoption if <70% pre-fill)
- **Mitigation**:
  - Golden Dataset: Test on 50 scenarios before production
  - Claude API: Use Claude Sonnet 4.5 (high accuracy)
  - Fallback: Manual editing (students can fix auto-filled sections)
- **Owner**: rust-ffi-expert + aba-clinical-expert

### Medium-Risk Items (Monitor)

**RISK-6**: Database migration conflicts (`user_progress` extended by both systems)
**RISK-7**: WebSocket scaling (100 concurrent connections per server instance)
**RISK-8**: Cost overruns (Black Friday exam season spike)
**RISK-9**: Accessibility test failures (WCAG 2.2 AA compliance for OSCE chat)
**RISK-10**: Performance degradation (PostgreSQL query optimization needed)

---

## 🎉 CONCLUSION

This **Comprehensive Platform Implementation Master Plan** provides a unified strategy for deploying both the EMR Practice System and AI OSCE Simulation System with proper integration.

### Key Achievements

✅ **Single Source of Truth**: One master plan for entire platform
✅ **Shared Infrastructure**: Vault, Redis, security tests (prevents duplicate work)
✅ **Integration Layer**: OSCE-to-EMR converter, unified dashboard (pedagogical value)
✅ **Realistic Timeline**: 6-8 weeks with parallel work (not 9-11 weeks sequential)
✅ **Cost Transparency**: $104-153/month at scale (vs unclear before)
✅ **Quality Gates**: 500+ tests, 100% pass rate, WCAG 2.2 AA compliance
✅ **Risk Mitigation**: 10 risks identified with mitigation strategies

### Total Scope

- **24 PRDs**: 14 EMR + 8 AI OSCE + 2 Integration
- **296-358 hours**: Across 6-7 specialist agents
- **6-8 weeks**: Calendar time with parallel work
- **$104-153/month**: At scale (1000-2000 users)

### Success Criteria

**This platform is ready for production when**:
- ✅ All 500+ tests pass (100% pass rate)
- ✅ All quality gates met (performance, security, accessibility)
- ✅ 360 patient personas validated by ≥2 clinicians
- ✅ OSCE → EMR correlation proven (>10% improvement)
- ✅ Monthly costs <$200 (within budget)
- ✅ 99.5%+ uptime (monitoring operational)

**Required Sign-Offs**:
- PM Coordinator
- Security Expert
- Clinical Expert (persona validation)
- QA Expert (test coverage)
- DevOps (infrastructure deployment)

---

**Document Status**: ✅ Ready for Implementation
**Created**: 2026-02-16
**Last Updated**: 2026-02-16
**Version**: 1.0
**Owner**: PM Coordinator
**Next Review**: After Week 1 completion

---

**END OF COMPREHENSIVE PLATFORM IMPLEMENTATION MASTER PLAN**
