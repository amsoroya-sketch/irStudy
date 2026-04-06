# EMR Backend Implementation - Multi-Agent Execution Plan

**Project**: irStudy EMR Backend Missing Endpoints
**Format**: T-RALPH v2.1 (Test-First Development)
**Total Phases**: 5
**Total Tests**: 33
**Estimated Time**: 8.5-10 hours
**Created**: 2026-04-06

---

## Executive Summary

This document provides the **multi-agent execution plan** for implementing 5 missing EMR backend endpoints using T-RALPH v2.1 test-first development methodology.

**Key Features**:
- ✅ **Multi-agent coordination** (Primary + Secondary agents per phase)
- ✅ **Quality gates** (Security, QA, Performance)
- ✅ **Sequential dependencies** (Phase 1 blocks Phase 2-5)
- ✅ **33 comprehensive tests** embedded in PRDs
- ✅ **Complete implementation code** (copy-paste ready)

---

## Phase Execution Order (CRITICAL)

**MUST execute in this exact order** (dependencies block later phases):

```
Phase 1: Models Migration (CRITICAL - BLOCKS ALL)
   ↓
Phase 2: Router Consolidation (CRITICAL - BLOCKS Phase 3-5)
   ↓
Phase 3: Dashboard Endpoints (CRITICAL - Fixes 404 errors)
   ↓
Phase 4: Patient Field Aliases (Can run parallel with Phase 5)
   ↓
Phase 5: Query Parameters (Can run parallel with Phase 4)
```

---

## Multi-Agent Architecture

### Phase 1: Models Migration (PRD-EMR-001)

**Primary Agent**: `python-backend-developer`
- **Tasks**:
  - Move 6 EMR models to `models.py`
  - Update 7 files with new imports
  - Write 12 tests (TDD RED → GREEN)
- **Deliverables**:
  - `backend/src/db/models.py` (6 new models)
  - 12 passing tests
  - 7 updated import statements

**Secondary Agent**: `security-compliance-expert`
- **Tasks**:
  - Security scan of model definitions
  - Validate no hardcoded credentials
  - Check PHI protection measures
- **Deliverables**:
  - Security scan report
  - Credential scan (expect 0 violations)

**Handoff Procedure**:
1. Primary completes implementation → All 12 tests GREEN
2. Secondary runs security scan → 0 violations found
3. Both agents approve → **Phase 1 COMPLETE**

**Validation Command**:
```bash
# Primary agent
cd /home/dev/Development/irStudy/backend
source venv/bin/activate
pytest tests/test_emr_models_migration.py -v
# Expected: 12 passed

# Secondary agent
grep -r "dbPath:\|dbKey:\|hardcoded" backend/src/db/models.py
# Expected: 0 matches (no hardcoded credentials)
```

---

### Phase 2: Router Consolidation (PRD-EMR-002)

**Primary Agent**: `python-backend-developer`
- **Tasks**:
  - Delete `emr_sessions.py` (legacy router)
  - Update `router.py` (remove duplicate registration)
  - Write 6 tests (TDD RED → GREEN)
- **Deliverables**:
  - Deleted file: `emr_sessions.py`
  - Updated file: `router.py` (2 lines removed)
  - 6 passing tests

**Secondary Agent**: NONE (simple router cleanup)

**Validation Command**:
```bash
# Primary agent
pytest tests/test_emr_router_consolidation.py -v
# Expected: 6 passed

# Verify file deleted
ls backend/src/api/v1/emr_sessions.py
# Expected: No such file or directory
```

---

### Phase 3: Dashboard Endpoints (PRD-EMR-003)

**Primary Agent**: `python-backend-developer`
- **Tasks**:
  - Implement 3 new endpoints (dashboard/emr, weekly-trends/unified, weak-areas/emr)
  - Add 3 service layer methods to `ProgressAnalytics`
  - Add 3 Pydantic response schemas
  - Write 9 tests (TDD RED → GREEN)
- **Deliverables**:
  - 3 working endpoints (return 200 OK)
  - 3 service methods
  - 3 Pydantic schemas
  - 9 passing tests

**Secondary Agent**: `testing-qa-expert`
- **Tasks**:
  - Validate test coverage (≥70%)
  - Check edge cases (empty data, no sessions, invalid user)
  - Performance testing (p95 <300ms)
- **Deliverables**:
  - Test coverage report
  - Performance benchmark results

**Handoff Procedure**:
1. Primary completes 3 endpoints → All 9 tests GREEN
2. Secondary validates test quality → Coverage ≥70%, performance <300ms
3. Both agents approve → **Phase 3 COMPLETE**

**Validation Command**:
```bash
# Primary agent
pytest tests/test_emr_dashboard_endpoints.py -v
# Expected: 9 passed

# Secondary agent (QA)
pytest --cov=src.api.v1.progress --cov=src.services.progress_analytics
# Expected: Coverage ≥70%

# Performance test
curl -w "@curl-format.txt" \
  -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8001/api/v1/progress/dashboard/emr"
# Expected: time_total <0.300s
```

---

### Phase 4: Patient Field Aliases (PRD-EMR-004)

**Primary Agent**: `python-backend-developer`
- **Tasks**:
  - Add `name` computed field to `MockPatientResponse`
  - Write 3 tests (TDD RED → GREEN)
- **Deliverables**:
  - Updated `MockPatientResponse` schema
  - 3 passing tests

**Secondary Agent**: NONE (simple Pydantic schema change)

**Validation Command**:
```bash
# Primary agent
pytest tests/test_patient_field_aliases.py -v
# Expected: 3 passed

# Verify alias works
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8001/api/v1/emr/sessions/start" \
  -X POST -d '{"emr_system":"epic"}' | jq '.patient | {name, full_name}'
# Expected: Both fields present with same value
```

---

### Phase 5: Query Parameters (PRD-EMR-005)

**Primary Agent**: `python-backend-developer`
- **Tasks**:
  - Add `sort_by` and `sort_order` parameters to list endpoint
  - Update service layer with ORDER BY logic
  - Write 3 tests (TDD RED → GREEN)
- **Deliverables**:
  - Working sort parameters
  - 3 passing tests

**Secondary Agent**: `security-compliance-expert`
- **Tasks**:
  - Validate SQL injection prevention
  - Test invalid sort_by values (SQL keywords)
  - Verify input sanitization
- **Deliverables**:
  - Security scan (0 SQL injection vulnerabilities)

**Handoff Procedure**:
1. Primary implements sort parameters → All 3 tests GREEN
2. Secondary validates SQL injection prevention → 0 vulnerabilities
3. Both agents approve → **Phase 5 COMPLETE**

**Validation Command**:
```bash
# Primary agent
pytest tests/test_emr_list_sorting.py -v
# Expected: 3 passed

# Secondary agent (Security)
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8001/api/v1/emr/sessions?sort_by=DROP%20TABLE&sort_order=desc"
# Expected: 200 OK (not 500 error), no SQL injection

curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8001/api/v1/emr/sessions?sort_by=';DELETE%20FROM%20users--&sort_order=desc"
# Expected: 200 OK (fallback to default), no SQL execution
```

---

## Agent Summary

| Agent | Phases | Total Tasks | Deliverables |
|-------|--------|-------------|--------------|
| **python-backend-developer** | 1, 2, 3, 4, 5 | Implementation (all phases) | 33 tests, 6 models, 3 endpoints, code |
| **security-compliance-expert** | 1, 5 | Security validation | 2 security reports, 0 violations |
| **testing-qa-expert** | 3 | QA validation | Coverage report, performance benchmarks |

---

## Quality Gates (ALL MUST PASS)

### Global Quality Gates (Every Phase)

- [ ] **100% test pass rate** (all tests GREEN)
- [ ] **No regressions** (full test suite passes)
- [ ] **TypeScript compiles** (frontend compatibility)
- [ ] **Code committed** (git commit with descriptive message)

### Phase-Specific Quality Gates

**Phase 1**:
- [ ] All 6 models importable from `models.py`
- [ ] 0 hardcoded credentials (security scan)
- [ ] Database migration successful

**Phase 2**:
- [ ] Legacy router file deleted
- [ ] No duplicate route warnings
- [ ] Single EMR router registered

**Phase 3**:
- [ ] All 3 endpoints return 200 OK
- [ ] Test coverage ≥70%
- [ ] Response time <300ms (p95)

**Phase 4**:
- [ ] Patient responses have both `name` and `full_name`
- [ ] Frontend displays patient names correctly

**Phase 5**:
- [ ] Sessions sorted correctly (newest first by default)
- [ ] 0 SQL injection vulnerabilities
- [ ] Invalid parameters handled gracefully

---

## Execution Commands

### Option 1: Sequential Manual Execution

```bash
# Phase 1
cd /home/dev/Development/irStudy
# Follow PRD-EMR-001-MODELS-MIGRATION.md (TDD workflow)
pytest backend/tests/test_emr_models_migration.py -v

# Phase 2 (after Phase 1 complete)
# Follow PRD-EMR-002-CONSOLIDATE-ROUTERS.md
pytest backend/tests/test_emr_router_consolidation.py -v

# Phase 3 (after Phase 2 complete)
# Follow PRD-EMR-003-DASHBOARD-ENDPOINTS.md
pytest backend/tests/test_emr_dashboard_endpoints.py -v

# Phase 4 (after Phase 3 complete)
# Follow PRD-EMR-004-PATIENT-ALIAS.md
pytest backend/tests/test_patient_field_aliases.py -v

# Phase 5 (after Phase 4 complete)
# Follow PRD-EMR-005-QUERY-PARAMS.md
pytest backend/tests/test_emr_list_sorting.py -v
```

### Option 2: Ralph Loop Execution

```bash
# Execute all PRDs sequentially via Ralph loop
cd /home/dev/Development/irStudy

# Phase 1
ralph --prd PRD-EMR-001-MODELS-MIGRATION.md --agent python-backend-developer

# After Phase 1 approval, run security validation
ralph --prd PRD-EMR-001-MODELS-MIGRATION.md --agent security-compliance-expert --validate

# Phase 2
ralph --prd PRD-EMR-002-CONSOLIDATE-ROUTERS.md --agent python-backend-developer

# Phase 3
ralph --prd PRD-EMR-003-DASHBOARD-ENDPOINTS.md --agent python-backend-developer

# After Phase 3 approval, run QA validation
ralph --prd PRD-EMR-003-DASHBOARD-ENDPOINTS.md --agent testing-qa-expert --validate

# Phase 4
ralph --prd PRD-EMR-004-PATIENT-ALIAS.md --agent python-backend-developer

# Phase 5
ralph --prd PRD-EMR-005-QUERY-PARAMS.md --agent python-backend-developer

# After Phase 5 approval, run security validation
ralph --prd PRD-EMR-005-QUERY-PARAMS.md --agent security-compliance-expert --validate
```

**NOTE**: Ralph command syntax may vary based on your Ralph CLI version. Adjust accordingly.

---

## Expected Outcomes (After All Phases Complete)

### Backend Changes

**Files Created** (7 new files):
```
backend/tests/test_emr_models_migration.py (12 tests)
backend/tests/test_emr_router_consolidation.py (6 tests)
backend/tests/test_emr_dashboard_endpoints.py (9 tests)
backend/tests/test_patient_field_aliases.py (3 tests)
backend/tests/test_emr_list_sorting.py (3 tests)
```

**Files Modified** (10 files):
```
backend/src/db/models.py (6 models added)
backend/src/api/v1/router.py (2 lines removed)
backend/src/api/v1/progress.py (3 endpoints added)
backend/src/services/progress_analytics.py (3 methods added)
backend/src/schemas/progress.py (3 schemas added)
backend/src/schemas/emr.py (1 computed field added)
backend/src/api/v1/emr/sessions.py (2 parameters added to list endpoint)
backend/src/services/emr/session_service.py (sorting logic added)
```

**Files Deleted** (1 file):
```
backend/src/api/v1/emr_sessions.py (legacy router)
```

### Test Results

```
✅ Total Tests: 33
✅ Pass Rate: 100%
✅ Coverage: ≥70%
✅ Security: 0 violations
✅ Performance: <300ms p95
```

### Frontend Impact

```
✅ Dashboard loads successfully (no 404 errors)
✅ EMR metrics display correctly
✅ Recent sessions sorted newest-first
✅ Patient names display correctly
✅ Progress charts render with data
```

---

## Rollback Plan (If Any Phase Fails)

### Phase 1 Rollback
```bash
git revert <commit-hash>  # Revert models.py changes
# Or restore 7 files manually
git checkout HEAD~1 backend/src/db/models.py
# ... restore other 6 files
```

### Phase 2 Rollback
```bash
git checkout HEAD~1 backend/src/api/v1/emr_sessions.py  # Restore deleted file
git checkout HEAD~1 backend/src/api/v1/router.py  # Restore router registration
```

### Phase 3 Rollback
```bash
git revert <commit-hash>  # Revert dashboard endpoints
# Remove 3 endpoints from progress.py
# Remove 3 methods from progress_analytics.py
# Remove 3 schemas from progress.py schemas
```

### Phase 4 Rollback
```bash
git checkout HEAD~1 backend/src/schemas/emr.py  # Remove computed field
```

### Phase 5 Rollback
```bash
git checkout HEAD~1 backend/src/api/v1/emr/sessions.py  # Remove sort parameters
git checkout HEAD~1 backend/src/services/emr/session_service.py  # Remove ORDER BY logic
```

---

## Success Criteria (Final Validation)

**Phase 1-5 are COMPLETE when:**
- ✅ All 33 tests pass (100% pass rate)
- ✅ Full backend test suite passes (no regressions)
- ✅ TypeScript compilation succeeds (0 errors)
- ✅ Backend starts without errors (uvicorn)
- ✅ Frontend dashboard loads successfully
- ✅ All 3 dashboard endpoints return 200 OK
- ✅ Security scans pass (0 hardcoded credentials, 0 SQL injection)
- ✅ Performance targets met (<300ms p95)
- ✅ All code committed to git (5 commits minimum)

---

## Contact & Support

**Questions?**
- Review individual PRD files for detailed implementation steps
- Check `PROJECT_CONSTRAINTS.md` for project-specific requirements
- Refer to `constraints/13-ralph-execution.md` for Ralph execution patterns

**PRD Files**:
- `PRD-EMR-001-MODELS-MIGRATION.md` (Phase 1)
- `PRD-EMR-002-CONSOLIDATE-ROUTERS.md` (Phase 2)
- `PRD-EMR-003-DASHBOARD-ENDPOINTS.md` (Phase 3)
- `PRD-EMR-004-PATIENT-ALIAS.md` (Phase 4)
- `PRD-EMR-005-QUERY-PARAMS.md` (Phase 5)

---

**READY FOR EXECUTION** ✅

All 5 PRDs are T-RALPH v2.1 compliant with multi-agent coordination.
Execute sequentially (Phase 1 → 2 → 3 → 4 → 5) for best results.
