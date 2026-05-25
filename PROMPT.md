# Task: Implement EMR Sessions API Endpoints

## Objective

Implement 6 REST API endpoints for EMR Practice Sessions following the specification in `PRD-EMR-SESSIONS-API.md`.

**Goal**: Convert 42 failing EMR tests → 29 passing tests (100% pass rate)

---

## Instructions (EXECUTE IN ORDER)

### 1. Read Required Documentation

**CRITICAL - Read these FIRST before ANY implementation**:

1. **PRD**: Read `PRD-EMR-SESSIONS-API.md` completely (especially T, L, P sections)
2. **Constraints**: Read `/home/dev/Development/irStudy/PROJECT_CONSTRAINTS.md`:
   - Section 1: Medical Accuracy Standards (Australian context)
   - Section 3: Security & Configuration (no hardcoded credentials)
   - Section 6: Testing Requirements (100% pass rate)
   - Top 10 Critical Constraints table
3. **Tests**: Read `backend/tests/test_api/test_emr/test_emr_sessions.py` (ALL 29 tests)
4. **Existing Code**: Search for similar patterns in `backend/src/api/v1/`

---

### 2. Implementation Phases

Execute these phases **SEQUENTIALLY** with validation after each:

#### Phase 1: Session CRUD Endpoints (3 hours)
**Target**: 16/29 tests passing

**Files to Create/Update**:
1. Create `backend/src/schemas/emr.py` (Pydantic request/response models)
2. Update `backend/src/services/emr/session_service.py` (add missing methods)
3. Update `backend/src/api/v1/emr/sessions.py` (add missing endpoints)

**Endpoints**:
- `POST /api/v1/emr/sessions/start` (6 tests)
- `GET /api/v1/emr/sessions/{session_id}` (5 tests)
- `GET /api/v1/emr/sessions` (5 tests)

**Validation**:
```bash
cd /home/dev/Development/irStudy/backend
source venv/bin/activate
export DATABASE_PASSWORD="test_password"
export SECRET_KEY="0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
python -m pytest tests/test_api/test_emr/test_emr_sessions.py -k "start_session or get_session or list_sessions" -v --tb=short
```
**Expected**: 16 tests PASS

**Do NOT proceed to Phase 2 until Phase 1 validation passes!**

---

#### Phase 2: Auto-Save Endpoint (1 hour)
**Target**: 21/29 tests passing

**Files to Update**:
- `backend/src/services/emr/session_service.py` (add `update_session` method)
- `backend/src/api/v1/emr/sessions.py` (add `PUT /sessions/{id}` endpoint)

**Endpoint**:
- `PUT /api/v1/emr/sessions/{session_id}` (5 tests)

**Validation**:
```bash
python -m pytest tests/test_api/test_emr/test_emr_sessions.py -k "update_session" -v --tb=short
```
**Expected**: 5 additional tests PASS (total: 21/29)

**Do NOT proceed to Phase 3 until Phase 2 validation passes!**

---

#### Phase 3: Submit Endpoint with Validation (2 hours)
**Target**: 26/29 tests passing

**Files to Update**:
- `backend/src/services/emr/session_service.py` (add `submit_session` method)
- `backend/src/api/v1/emr/sessions.py` (add `POST /sessions/{id}/submit` endpoint)
- Integrate with existing `backend/src/api/v1/emr/validation.py` (3-layer validator)

**Endpoint**:
- `POST /api/v1/emr/sessions/{session_id}/submit` (5 tests)

**Validation**:
```bash
python -m pytest tests/test_api/test_emr/test_emr_sessions.py -k "submit_session" -v --tb=short
```
**Expected**: 5 additional tests PASS (total: 26/29)

**Do NOT proceed to Phase 4 until Phase 3 validation passes!**

---

#### Phase 4: Delete Endpoint (30 min)
**Target**: 29/29 tests passing

**Files to Update**:
- `backend/src/services/emr/session_service.py` (add `delete_session` method)
- `backend/src/api/v1/emr/sessions.py` (add `DELETE /sessions/{id}` endpoint)

**Endpoint**:
- `DELETE /api/v1/emr/sessions/{session_id}` (3 tests)

**Validation**:
```bash
python -m pytest tests/test_api/test_emr/test_emr_sessions.py -k "delete_session" -v --tb=short
```
**Expected**: 3 additional tests PASS (total: 29/29)

---

#### Phase 5: Full Integration & Regression Check (1 hour)

**Final Validation**:
```bash
# Run ALL EMR session tests
python -m pytest tests/test_api/test_emr/test_emr_sessions.py -v --tb=short

# Check for regressions
python -m pytest tests/ --tb=no -q | tail -5
```

**Expected**:
- ✅ 29/29 EMR session tests PASS (100%)
- ✅ 0 ERRORS in full test suite (maintain zero error status)
- ✅ 0 new regressions

---

## Quality Gates (RUN AFTER EACH PHASE)

### Security Scan
```bash
grep -r "password\|api_key\|secret" backend/src/api/v1/emr/ --exclude-dir=__pycache__ | grep -v "export\|Query\|Field" || echo "✅ No hardcoded secrets"
```
**Expected**: No matches (or only safe matches like "export SECRET_KEY")

### Australian Terminology Check
```bash
grep -ri "acetaminophen\|albuterol\|epinephrine" backend/src/api/v1/emr/ || echo "✅ Australian terminology used"
```
**Expected**: 0 matches (must use paracetamol, salbutamol, adrenaline)

### Type Checking (if mypy installed)
```bash
mypy backend/src/api/v1/emr/sessions.py 2>/dev/null || echo "⚠️  Mypy not installed (optional)"
```

---

## Success Criteria

**Task is COMPLETE when ALL of these are true**:

1. ✅ All 29 tests in `tests/test_api/test_emr/test_emr_sessions.py` PASS
2. ✅ 0 ERRORS in full test suite (`pytest tests/ --tb=no -q`)
3. ✅ Security scan passes (no hardcoded secrets)
4. ✅ Australian terminology used (no American terms)
5. ✅ All quality gates pass
6. ✅ No regressions introduced

---

## Completion Signal

When ALL success criteria are met:

1. Create file `@fix_plan.md` with content:
```markdown
# EMR Sessions API - COMPLETE

## Status: DONE ✅

All 29 tests passing. Implementation complete.

## Test Results
[Paste pytest output showing 29/29 PASS]

## Files Modified
- backend/src/schemas/emr.py
- backend/src/services/emr/session_service.py
- backend/src/api/v1/emr/sessions.py
- backend/src/api/v1/emr/__init__.py

## Validation
- ✅ 29/29 tests PASS
- ✅ 0 errors in full suite
- ✅ No hardcoded credentials
- ✅ Australian terminology
```

2. Exit with message: "EMR Sessions API implementation complete. All 29 tests passing."

---

## Anti-Patterns to AVOID

❌ **DO NOT**:
- Skip reading PROJECT_CONSTRAINTS.md
- Proceed to next phase with failing tests
- Hardcode database credentials or API keys
- Use American medical terminology (acetaminophen, epinephrine, albuterol)
- Create placeholder/TODO code
- Skip quality gate validation
- Mark as complete without running full test suite

---

## Estimated Timeline

- **Phase 1**: 3 hours (CRUD endpoints)
- **Phase 2**: 1 hour (Auto-save)
- **Phase 3**: 2 hours (Submit with validation)
- **Phase 4**: 30 minutes (Delete)
- **Phase 5**: 1 hour (Integration & validation)

**Total**: ~7.5 hours

---

## EXECUTE NOW

Start with Phase 1. Read the documentation listed in section 1, then implement the CRUD endpoints.

Validate after EACH phase. Do NOT skip validation steps.

Mark complete ONLY when all 29 tests pass and quality gates pass.

Good luck! 🚀
