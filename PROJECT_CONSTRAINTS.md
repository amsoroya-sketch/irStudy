# Project Constraints & Standards - Quick Reference

**Project**: irStudy - ICRP Medical Education AI System
**Version**: 3.0.0 (Modular Structure)
**Last Updated**: 2026-01-26
**Format**: Lightweight index + detailed constraint modules

---

## 🚨 CRITICAL: Read Before Starting Work

**ALL agents MUST read relevant constraints before starting ANY work.**

This file provides a quick reference. For detailed requirements, see individual constraint files in `/constraints/` folder.

---

## Top 10 Critical Constraints (Must Know)

| # | Constraint | Details | File |
|---|------------|---------|------|
| 1 | **Australian Medical Context** | Use eTG, PBS, AHPRA, Australian spelling (paracetamol not acetaminophen) | [constraints/1-medical-accuracy.md](constraints/1-medical-accuracy.md) |
| 2 | **NO Placeholder Content** | 100% real content - NO templates, NO "Option A", NO "Clinical scenario for..." | [constraints/1-medical-accuracy.md](constraints/1-medical-accuracy.md) |
| 3 | **Python venv REQUIRED** | ALWAYS `source venv/bin/activate` before running Python scripts | [constraints/4-llm-integration.md](constraints/4-llm-integration.md) |
| 4 | **Local LLMs CANNOT generate MCQs** | Use Claude (Anthropic API) for ALL MCQ/OSCE generation | [constraints/4-llm-integration.md](constraints/4-llm-integration.md#42-claude-vs-local-llms-for-medical-content-critical) |
| 5 | **RAG citations REQUIRED** | Exactly 3 citations per MCQ, >0.70 confidence, with page numbers | [constraints/1-medical-accuracy.md](constraints/1-medical-accuracy.md) |
| 6 | **NO hardcoded credentials** | Use `ref.read(databaseConfigProvider)` - NEVER mock IDs | [constraints/3-security.md](constraints/3-security.md) |
| 7 | **100% test pass rate** | ALL tests must pass before commit - NO exceptions | [constraints/6-testing.md](constraints/6-testing.md) |
| 8 | **UTF-8 encoding** | ALWAYS `open(file, 'r', encoding='utf-8')` for JSON/text files | [constraints/5-data-processing.md](constraints/5-data-processing.md) |
| 9 | **No PHI in logs** | Hash/truncate patient identifiers - NEVER log MRN, DOB, email | [constraints/3-security.md](constraints/3-security.md) |
| 10 | **Australian drug names** | paracetamol, salbutamol, adrenaline (NOT acetaminophen, albuterol, epinephrine) | [constraints/1-medical-accuracy.md](constraints/1-medical-accuracy.md) |
| 11 | **Ralph PROMPT.md Directives** | Use "EXECUTE NOW", NOT "Would you like..." - Prevents premature Ralph exits | [constraints/13-ralph-execution.md](constraints/13-ralph-execution.md) |
| 12 | **Medical Content Quality Gates** | ALL medical content MUST pass 13-gate QA + FRACP validation, 100% RAG citations | [constraints/14-ralph-medical-content-standards.md](constraints/14-ralph-medical-content-standards.md) |

---

## Constraint Modules (Detailed)

### 1. Medical Accuracy Standards
**File**: [constraints/1-medical-accuracy.md](constraints/1-medical-accuracy.md)
**Status**: MANDATORY
**Key Topics**: Australian context, spelling, citations, clinical accuracy

**Critical Rules**:
- ✅ Use: eTG, PBS, AHPRA, AMH, Australian spelling
- ❌ Never: American sources without context, placeholder content
- 📊 Quality: 100% citation validation, 3 citations per MCQ

### 2. Code Architecture & Patterns
**File**: [constraints/2-code-architecture.md](constraints/2-code-architecture.md)
**Status**: MANDATORY (TO BE CREATED)
**Key Topics**: Agent patterns, project structure, naming conventions

### 3. Security & Configuration
**File**: [constraints/3-security.md](constraints/3-security.md)
**Status**: MANDATORY (TO BE CREATED)
**Key Topics**: No hardcoded credentials, PHI protection, HIPAA compliance

**Critical Rules**:
- ❌ NEVER: Hardcode database paths, mock user IDs, log PHI
- ✅ ALWAYS: Use config providers, hash identifiers, sanitize logs

### 4. LLM Integration Patterns ⚠️ NEW
**File**: [constraints/4-llm-integration.md](constraints/4-llm-integration.md)
**Status**: CRITICAL - Read before ANY LLM work
**Last Updated**: 2026-01-26 (Added Section 4.2)

**Sections**:
- 4.0: Python Environment & LLM Requirements
- 4.1: Ollama Client Usage
- 4.2: **Claude vs Local LLMs for Medical Content** (NEW)

**Critical Discovery (2026-01-26)**:
- ❌ Local LLMs (Ollama 7B models) **CANNOT** generate complex MCQs
- ✅ **MUST** use Claude (Anthropic API) for MCQ/OSCE generation
- 📊 Evidence: 200 MCQs failed with local LLMs → all placeholders
- 💰 Cost: ~$0.02/MCQ (acceptable vs quality compromise)

**Task Complexity Matrix**:
| Task | Local LLMs (Ollama) | Claude (Anthropic API) |
|------|---------------------|------------------------|
| MCQ generation | ❌ FAILS | ✅ REQUIRED |
| OSCE generation | ❌ FAILS | ✅ REQUIRED |
| Simple validation | ✅ OK | ✅ OK |

### 5. Data Processing Standards
**File**: [constraints/5-data-processing.md](constraints/5-data-processing.md)
**Status**: MANDATORY (TO BE CREATED)
**Key Topics**: JSON handling, UTF-8 encoding, large file processing

### 6. Testing Requirements
**File**: [constraints/6-testing.md](constraints/6-testing.md)
**Status**: MANDATORY (TO BE CREATED)
**Key Topics**: 100% pass rate, test coverage, quality gates

### 7. Documentation Standards
**File**: [constraints/7-documentation.md](constraints/7-documentation.md)
**Status**: MANDATORY (TO BE CREATED)
**Key Topics**: Code comments, API docs, constraint documentation

### 8. Agent-Specific Requirements
**File**: [constraints/8-agent-requirements.md](constraints/8-agent-requirements.md)
**Status**: MANDATORY (TO BE CREATED)
**Key Topics**: Medical agents (MED-001-046), QA agents, specialist requirements

### 9. Project-Specific Context
**File**: [constraints/9-project-context.md](constraints/9-project-context.md)
**Status**: MANDATORY (TO BE CREATED)
**Key Topics**: ICRP exam preparation, AMC standards, 46-agent system

### 10. Anti-Patterns (What NOT to Do)
**File**: [constraints/10-anti-patterns.md](constraints/10-anti-patterns.md)
**Status**: MANDATORY (TO BE CREATED)
**Key Topics**: Common mistakes, violations discovered, historical lessons

### 11. ICRP Clinical Training Standards
**File**: [constraints/11-icrp-standards.md](constraints/11-icrp-standards.md)
**Status**: MANDATORY (TO BE CREATED)
**Key Topics**: AMC Clinical Exam, OSCE requirements, Australian medical training

### 12. RAG Citation Requirements
**File**: [constraints/12-rag-citation.md](constraints/12-rag-citation.md)
**Status**: MANDATORY (TO BE CREATED)
**Key Topics**: Citation format, confidence scores, verification badges

### 13. Ralph Execution Requirements ⚠️ NEW
**File**: [constraints/13-ralph-execution.md](constraints/13-ralph-execution.md)
**Status**: MANDATORY - Read before creating PROMPT.md or PRD files
**Last Updated**: 2026-02-07

**Critical Rules**:
- ✅ ALWAYS: Use "AUTONOMOUS EXECUTION MODE" header, "EXECUTE NOW" commands
- ❌ NEVER: Use "Would you like...", "Should I...", "Please..." phrasing
- 📊 Requirements: Exact bash commands (no placeholders), verification commands, success criteria

**Problem Solved**: Prevents Ralph loop premature exits caused by question-based prompts

**Sections**:
- 13.1: AUTONOMOUS EXECUTION MODE Header (required)
- 13.2: Directive Language Only (no questions)
- 13.3: Exact Commands (no placeholders)
- 13.4: Success Criteria with Verification
- 13.5: PRD Template Structure
- 13.6: Quality Checks Before Running Ralph

### 14. Ralph Medical Content Quality Standards ⚠️ NEW
**File**: [constraints/14-ralph-medical-content-standards.md](constraints/14-ralph-medical-content-standards.md)
**Status**: **MANDATORY** - Auto-enforced in all medical content PRDs
**Last Updated**: 2026-03-21

**Critical Rules**:
- ✅ ALWAYS: Use clinical expert agents (clinical-documentation-expert, history-taking-expert, physical-examination-expert)
- ✅ ALWAYS: Include 3 required skills (rag-citation-verification, australian-medical-terminology, fracp-clinical-validation)
- ✅ ALWAYS: Include 5 required validations (QA 13-gate, FRACP clinical, security scan, RAG coverage, database)
- ❌ NEVER: Generate medical content without RAG citations (100% coverage required)
- ❌ NEVER: Use placeholder content ("Clinical scenario for...", "Option A/B/C/D")
- 📊 Quality Gates: 13-gate QA validation + FRACP clinical validation (≥8.0/10)

**Problem Solved**: Prevents medical content generation without proper quality gates

**Sections**:
- 14.1: Overview - Automatic Quality Enforcement
- 14.2: Mandatory PRD Components for Medical Content
- 14.3: Quality Gate Enforcement Flow
- 14.4: RAG System Requirements
- 14.5: 13-Gate QA Validation System
- 14.6: FRACP Clinical Validation
- 14.7: Auto-Fix Common Errors
- 14.8: Enforcement Checklist for PRD Authors
- 14.9: Example Medical Content PRD Template
- 14.10: Monitoring and Metrics

**Current Metrics (Batch 1 - 207 Personas)**:
- ✅ 100% RAG citation coverage (3,726 citations with qdrant_point_id)
- ✅ 96.5% deployment readiness (200/207 approved)
- ✅ 0 hallucinated citations (100% verified)
- ✅ 66.1% Australian sources (exceeds 60% target)

---

## Quick Start Guide

### Before Writing Code
1. Read Top 10 Critical Constraints (above)
2. Identify your task type (MCQ generation? Testing? Security?)
3. Read relevant constraint module(s)
4. Follow implementation checklist in constraint file

### Before Committing Code
- [ ] All tests pass (100% pass rate)
- [ ] No hardcoded credentials
- [ ] No placeholder content
- [ ] Australian spelling used
- [ ] Citations validated (if MCQ/OSCE)
- [ ] UTF-8 encoding specified
- [ ] No PHI in logs

---

## Recent Changes

### v3.0.0 (2026-01-26) - Modular Structure
- **Restructured**: Split 30,000+ token file into modular constraint files
- **Added**: `constraints/4-llm-integration.md` with Section 4.2 (LLM Capabilities)
- **Created**: Lightweight quick reference (this file)
- **Benefit**: Easier to read, navigate, and maintain

### v2.1.0 (2026-01-26) - LLM Capabilities Constraint
- **Added**: Section 4.2 documenting that local 7B models cannot generate complex MCQs
- **Mandated**: Claude Code client for all MCQ/OSCE generation
- **Evidence**: 200 placeholder MCQs from failed local model generation
- **Impact**: Prevents future quality compromises

---

## File Structure

```
/home/dev/Development/irStudy/
├── PROJECT_CONSTRAINTS_V3.md (this file - quick reference)
├── PROJECT_CONSTRAINTS.md (legacy - 30,000+ tokens)
└── constraints/
    ├── README.md (constraint system overview)
    ├── 4-llm-integration.md (✅ created 2026-01-26)
    └── (other constraint files - to be created)
```

---

## Need Help?

1. **Can't find a constraint?** Check the detailed file in `/constraints/` folder
2. **Constraint unclear?** Ask PM to clarify or update constraint file
3. **Discovered new constraint?** Document it and add to relevant constraint file
4. **File too large?** Consider splitting into sub-sections

---

## For Agents

**CRITICAL**: Before starting ANY work:
1. Identify task type (MCQ generation, testing, security, etc.)
2. Read relevant constraint file(s) from `/constraints/` folder
3. Follow implementation checklist
4. Validate work against constraints before returning

**If constraint file doesn't exist yet**: Read legacy `PROJECT_CONSTRAINTS.md` and extract relevant section.

---

**Status**: ✅ ACTIVE (v3.0.0 Modular Structure)
**Maintenance**: Update constraint files as new requirements discovered
**Legacy File**: `PROJECT_CONSTRAINTS.md` (kept for reference until all modules created)

---

## Recent Issues & Fixes

### 2026-02-02: Docker Python 3.12 Compatibility (CRITICAL FIX)
**Issue**: PyTorch 2.1.2 incompatible with Python 3.12 causing Docker build failures
**Services Affected**: flower, celery-worker, celery-beat, backend
**Error**: `ERROR: Could not find a version that satisfies the requirement torch==2.1.2`
**Root Cause**: PyTorch 2.1.x only supports Python 3.8-3.11; Docker uses Python 3.12
**Fix Applied**:
- Updated `backend/requirements.txt` lines 47-50
- torch==2.1.2 → torch==2.10.0 (Python 3.12 compatible)
- sentence-transformers==2.3.1 → sentence-transformers==3.3.1
- transformers==4.37.0 → transformers==4.48.0
**Documentation**: See `constraints/10-anti-patterns.md` section 10.8
**Prevention**: Always verify Python version compatibility before pinning ML packages

### 2026-04-06: Playwright E2E Testing Patterns (CRITICAL)
**Issue**: Test authentication failures and API endpoint configuration issues
**Tests Affected**: `testing/playwright/tests/integration/osce/osce-video-sample.spec.ts`

**Key Learnings**:

1. **E2E Test User Setup** (scripts/create_test_users.py:21)
   - MUST create test users in database before running E2E tests
   - Script is idempotent (updates existing users instead of failing)
   - Uses correct `hash_password()` function from `src.auth.security` (NOT `get_password_hash`)
   - Creates 5 test users: student@test.com, educator@test.com, admin@test.com, inactive@test.com, unverified@test.com

2. **Backend Startup for E2E Tests** (backend/.env:1)
   - MUST load .env before starting: `set -a && source .env && set +a && uvicorn src.main:app --reload --port 8001`
   - Failing to load .env causes: `ValueError: Database password not found`
   - Port 8001 required (frontend expects backend on http://localhost:8001)

3. **Test Authentication Pattern** (testing/playwright/utils/helpers/login.ts:25)
   - ALL protected page tests MUST call `await login(page, TEST_USERS.STUDENT)` in beforeEach
   - Login helper waits for redirect to `/dashboard` (10s timeout)
   - Login fills email/password with blur events to trigger validation before submit

4. **API Endpoint Path Issues** (DISCOVERED)
   - **CRITICAL BUG**: Frontend is requesting `/api/v1/api/v1/...` (doubled `/api/v1/`)
   - Affected endpoints: `/permissions/me`, `/progress/dashboard/emr`, `/emr/sessions`, etc.
   - All return `404 Not Found` causing dashboard redirect loop
   - **Root Cause**: Likely hardcoded `/api/v1/` prefix in frontend API client with duplicate base URL
   - **Impact**: Login succeeds but dashboard fails to load, tests stuck on `/login`

5. **Test Debugging Commands**:
   ```bash
   # Create test users
   cd /home/dev/Development/irStudy
   export DATABASE_URL='postgresql://postgres:3K4cnsyxYOOHGzCcxmOesU7PExXHCMaH@localhost:5433/irstudy_medical'
   source backend/venv/bin/activate && python scripts/create_test_users.py

   # Start backend with env vars
   cd backend && source venv/bin/activate && set -a && source .env && set +a && uvicorn src.main:app --reload --port 8001

   # Run tests in headed mode (visible browser)
   cd testing/playwright && npx playwright test tests/integration/osce/osce-video-sample.spec.ts --headed --project=chromium --retries=0

   # Test backend login endpoint directly
   curl -X POST http://localhost:8001/api/v1/auth/login -H "Content-Type: application/json" -d '{"email":"student@test.com","password":"Student123!@#"}'
   ```

**Fixes Applied** (2026-04-06):
- [x] Fixed frontend API client paths (removed doubled `/api/v1/`)
  - frontend/src/api/permissions.ts:26-27, 39, 48
  - frontend/src/hooks/useEMRDashboardData.ts:118, 132, 153, 172
  - frontend/src/pages/emr/CernerEMRPage.tsx:59, 69
  - frontend/src/pages/emr/EpicEMRPage.tsx:59, 69
  - frontend/src/pages/emr/StartEMRSessionPage.tsx:38
  - frontend/src/hooks/useAutoSave.ts:89
- [x] Verified TypeScript compilation (0 errors)

**Remaining Fixes**:
- [x] Implement missing backend endpoints: `/permissions/me`, `/progress/dashboard/emr`, etc. (PRDs created - see below)
- [ ] Add endpoint existence checks to E2E test setup
- [ ] Document E2E test prerequisites in testing/playwright/README.md
- [ ] Implement OSCE video page route (`/osces/:id`)

**Prevention**:
- ALWAYS run E2E tests after backend API changes
- ALWAYS check backend logs for 404 errors during test failures
- ALWAYS verify frontend API client configuration matches backend routes

---

### 2026-04-06: EMR Backend Missing Endpoints - PRDs Created (T-RALPH v2.1)

**Issue**: Frontend dashboard requests 3 EMR endpoints that don't exist, causing 404 errors:
- GET `/api/v1/progress/dashboard/emr` - EMR metrics (404 Not Found)
- GET `/api/v1/progress/weekly-trends/unified` - Unified trends (404 Not Found)
- GET `/api/v1/progress/weak-areas/emr` - Weak areas (404 Not Found)

**Root Causes Discovered**:
1. **Duplicate routers**: Two EMR router implementations (emr_sessions.py + emr/sessions.py)
2. **Inline models**: EMR models defined in router files instead of models.py
3. **Missing endpoints**: 3 dashboard endpoints never implemented
4. **Field name mismatch**: Backend uses `full_name`, frontend expects `name`
5. **Ignored query params**: Frontend passes `sort_by`/`sort_order` but backend ignores them

**Solution**: 5-Phase Implementation Plan (T-RALPH v2.1 with Multi-Agent Coordination)

**PRD Files Created** (All located in `/home/dev/Development/irStudy/`):

| Phase | PRD File | Scope | Time | Tests | Agents |
|-------|----------|-------|------|-------|--------|
| **1** | `PRD-EMR-001-MODELS-MIGRATION.md` | Move 6 EMR models to models.py | 3-4h | 12 | python-backend-developer + security-compliance-expert |
| **2** | `PRD-EMR-002-CONSOLIDATE-ROUTERS.md` | Delete duplicate emr_sessions.py router | 1-2h | 6 | python-backend-developer |
| **3** | `PRD-EMR-003-DASHBOARD-ENDPOINTS.md` | Implement 3 missing dashboard endpoints | 4-5h | 9 | python-backend-developer + testing-qa-expert |
| **4** | `PRD-EMR-004-PATIENT-ALIAS.md` | Add name/full_name field aliases | 30m | 3 | python-backend-developer |
| **5** | `PRD-EMR-005-QUERY-PARAMS.md` | Add sort_by/sort_order to list endpoint | 30m | 3 | python-backend-developer + security-compliance-expert |

**Total**: 8.5-10 hours, 33 tests, 6 agents (3 primary + 3 validation)

**Execution Plan**: See `EMR-IMPLEMENTATION-EXECUTION-PLAN.md` for detailed multi-agent coordination workflow

**Key Features**:
- ✅ T-RALPH v2.1 format (Test-First Development)
- ✅ Complete test code embedded in PRDs (copy-paste ready)
- ✅ Complete implementation code (no placeholders)
- ✅ Multi-agent quality gates (Security, QA, Performance)
- ✅ Sequential dependencies enforced (Phase 1 blocks 2-5)

**Expected Outcomes After Implementation**:
- ✅ Frontend dashboard loads without 404 errors
- ✅ EMR metrics, trends, and weak areas display correctly
- ✅ Recent sessions sorted newest-first (better UX)
- ✅ Patient names display correctly (backward compatibility)
- ✅ Clean codebase (no duplicate routers, centralized models)
- ✅ 100% test pass rate (33 tests)
- ✅ Performance targets met (<300ms p95)
- ✅ Security validated (0 hardcoded credentials, 0 SQL injection)

**Implementation Status**: READY FOR EXECUTION (PRDs complete, awaiting manual or Ralph loop execution)

**Next Steps**:
1. Execute Phase 1 (Models Migration) - CRITICAL, blocks all other phases
2. Execute Phase 2 (Router Consolidation) - CRITICAL, blocks Phase 3-5
3. Execute Phase 3 (Dashboard Endpoints) - CRITICAL, fixes 404 errors
4. Execute Phase 4 (Patient Aliases) - Can run parallel with Phase 5
5. Execute Phase 5 (Query Parameters) - Can run parallel with Phase 4

**Validation Commands** (After all phases complete):
```bash
# Run all 33 tests
cd /home/dev/Development/irStudy/backend
source venv/bin/activate
pytest tests/test_emr_*.py -v
# Expected: 33 passed in X.XXs

# Test dashboard endpoints
TOKEN=$(curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"student@test.com","password":"Student123!@#"}' \
  | jq -r '.access_token')

curl -H "Authorization: Bearer $TOKEN" http://localhost:8001/api/v1/progress/dashboard/emr
# Expected: 200 OK with EMR metrics JSON

# Verify frontend dashboard
cd /home/dev/Development/irStudy/frontend
npm run dev
# Open http://localhost:5173/dashboard
# Expected: Dashboard loads without 404 errors
```

---
