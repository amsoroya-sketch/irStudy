# Quick Start: EMR Backend Implementation

**Status**: Ready for Execution
**Created**: 2026-04-06
**Estimated Time**: 8.5-10 hours total
**Tests**: 33 comprehensive tests (all embedded in PRDs)

---

## 🚀 What This Fixes

Your EMR dashboard currently shows **404 errors** for 3 critical endpoints. This implementation plan fixes all missing endpoints and related issues.

**Before Implementation**:
```
❌ Dashboard stuck on loading screen (404 errors)
❌ GET /api/v1/progress/dashboard/emr → 404 Not Found
❌ GET /api/v1/progress/weekly-trends/unified → 404 Not Found
❌ GET /api/v1/progress/weak-areas/emr → 404 Not Found
❌ Duplicate EMR routers causing conflicts
❌ Patient names showing as "Unknown"
```

**After Implementation**:
```
✅ Dashboard loads successfully (<1s)
✅ EMR metrics display (sessions, scores, trends)
✅ Weekly progress charts render
✅ Weak areas panel shows recommendations
✅ Patient names display correctly
✅ Sessions sorted newest-first
✅ 100% test pass rate (33/33 tests)
```

---

## 📋 Execution Options

### Option 1: Automated (Ralph Loop) - RECOMMENDED

Ralph will autonomously execute all 5 PRDs with multi-agent coordination.

```bash
cd /home/dev/Development/irStudy

# Run Ralph loop for all phases sequentially
# NOTE: Ralph must be executed in a SEPARATE terminal
# (per PROJECT_CONSTRAINTS.md - never run Ralph directly in main terminal)

# Phase 1: Models Migration (CRITICAL - blocks all other phases)
ralph loop --prd PRD-EMR-001-MODELS-MIGRATION.md

# Phase 2: Router Consolidation
ralph loop --prd PRD-EMR-002-CONSOLIDATE-ROUTERS.md

# Phase 3: Dashboard Endpoints
ralph loop --prd PRD-EMR-003-DASHBOARD-ENDPOINTS.md

# Phase 4: Patient Aliases
ralph loop --prd PRD-EMR-004-PATIENT-ALIAS.md

# Phase 5: Query Parameters
ralph loop --prd PRD-EMR-005-QUERY-PARAMS.md
```

**Total Time**: ~10 hours (Ralph executes autonomously)

---

### Option 2: Manual (Follow PRDs Step-by-Step)

Execute each phase manually following the T-RALPH v2.1 TDD workflow.

#### Phase 1: Models Migration (3-4 hours)

**Goal**: Move 6 EMR models from inline definitions to `models.py`

**Steps**:
1. Open `PRD-EMR-001-MODELS-MIGRATION.md`
2. Read **T section** (Tests) → Copy all 12 test functions
3. Create `backend/tests/test_emr_models_migration.py`
4. Paste test code → Run tests (expect RED - all fail)
   ```bash
   cd /home/dev/Development/irStudy/backend
   source venv/bin/activate
   pytest tests/test_emr_models_migration.py -v
   # Expected: 12 failed (RED phase)
   ```
5. Read **P section** (Plan) → Copy implementation code
6. Update `backend/src/db/models.py` (add 6 models)
7. Update 7 files with new imports (follow P section)
8. Run tests again (expect GREEN - all pass)
   ```bash
   pytest tests/test_emr_models_migration.py -v
   # Expected: 12 passed (GREEN phase)
   ```
9. Run full test suite (expect no regressions)
   ```bash
   pytest --cov=src -v
   # Expected: 100% pass rate
   ```
10. Commit changes:
    ```bash
    git add .
    git commit -m "feat: Migrate EMR models to central models.py (Phase 1)

    - Move 6 EMR models from inline definitions to models.py
    - Update 7 files with new imports
    - Add 12 comprehensive tests (100% pass rate)
    - Follows PRD-EMR-001-MODELS-MIGRATION.md

    🤖 Generated with Claude Code
    Co-Authored-By: Claude <noreply@anthropic.com>"
    ```

**Quality Gates**:
- [ ] All 12 tests pass (100%)
- [ ] No hardcoded credentials (security scan)
- [ ] TypeScript compiles (0 errors)

---

#### Phase 2: Router Consolidation (1-2 hours)

**Goal**: Delete duplicate `emr_sessions.py` router

**Steps**:
1. Open `PRD-EMR-002-CONSOLIDATE-ROUTERS.md`
2. Create test file from **T section**
   ```bash
   # Copy tests to backend/tests/test_emr_router_consolidation.py
   pytest tests/test_emr_router_consolidation.py -v
   # Expected: 3-4 failed (RED phase)
   ```
3. Follow **P section** implementation:
   - Delete `backend/src/api/v1/emr_sessions.py`
   - Update `backend/src/api/v1/router.py` (remove 2 lines)
4. Run tests:
   ```bash
   pytest tests/test_emr_router_consolidation.py -v
   # Expected: 6 passed (GREEN phase)
   ```
5. Start backend → Verify no duplicate route warnings:
   ```bash
   cd backend
   source venv/bin/activate
   set -a && source .env && set +a
   uvicorn src.main:app --reload --port 8001
   # Check logs: should see NO "Duplicate route" warnings
   ```
6. Commit changes:
   ```bash
   git add .
   git commit -m "refactor: Consolidate EMR routers (Phase 2)

    - Delete duplicate emr_sessions.py router
    - Keep emr/sessions.py (comprehensive, 6 endpoints)
    - Update router.py registration
    - Fixes duplicate route conflicts

    🤖 Generated with Claude Code
    Co-Authored-By: Claude <noreply@anthropic.com>"
    ```

**Quality Gates**:
- [ ] All 6 tests pass (100%)
- [ ] Backend starts without errors
- [ ] No duplicate route warnings

---

#### Phase 3: Dashboard Endpoints (4-5 hours)

**Goal**: Implement 3 missing dashboard endpoints

**Steps**:
1. Open `PRD-EMR-003-DASHBOARD-ENDPOINTS.md`
2. Create test file from **T section**
   ```bash
   pytest tests/test_emr_dashboard_endpoints.py -v
   # Expected: 9 failed (RED phase)
   ```
3. Follow **P section** - 4 files to modify:
   - File 1: Create test file ✅ (done in step 2)
   - File 2: Add 3 service methods to `progress_analytics.py`
   - File 3: Add 3 Pydantic schemas to `progress.py`
   - File 4: Add 3 endpoints to `progress.py` router
4. Run tests:
   ```bash
   pytest tests/test_emr_dashboard_endpoints.py -v
   # Expected: 9 passed (GREEN phase)
   ```
5. Test endpoints manually:
   ```bash
   TOKEN=$(curl -X POST http://localhost:8001/api/v1/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email":"student@test.com","password":"Student123!@#"}' \
     | jq -r '.access_token')

   curl -H "Authorization: Bearer $TOKEN" \
     http://localhost:8001/api/v1/progress/dashboard/emr
   # Expected: 200 OK with EMR metrics JSON
   ```
6. Commit changes:
   ```bash
   git add .
   git commit -m "feat: Implement 3 missing EMR dashboard endpoints (Phase 3)

    - Add GET /progress/dashboard/emr (EMR metrics)
    - Add GET /progress/weekly-trends/unified (MCQ+OSCE+EMR trends)
    - Add GET /progress/weak-areas/emr (specialties <70%)
    - Add 3 service methods to ProgressAnalytics
    - Add 3 Pydantic response schemas
    - Fixes 404 errors on dashboard

    🤖 Generated with Claude Code
    Co-Authored-By: Claude <noreply@anthropic.com>"
    ```

**Quality Gates**:
- [ ] All 9 tests pass (100%)
- [ ] All 3 endpoints return 200 OK
- [ ] Response time <300ms (p95)
- [ ] Frontend dashboard loads successfully

---

#### Phase 4: Patient Aliases (30 minutes)

**Goal**: Add `name` field alias to `MockPatientResponse`

**Steps**:
1. Open `PRD-EMR-004-PATIENT-ALIAS.md`
2. Create test file:
   ```bash
   pytest tests/test_patient_field_aliases.py -v
   # Expected: 3 failed (RED phase)
   ```
3. Add computed field to `backend/src/schemas/emr.py`:
   ```python
   from pydantic import BaseModel, computed_field

   class MockPatientResponse(BaseModel):
       # ... existing fields

       @computed_field
       @property
       def name(self) -> str:
           """Alias for full_name (backward compatibility)"""
           return self.full_name
   ```
4. Run tests:
   ```bash
   pytest tests/test_patient_field_aliases.py -v
   # Expected: 3 passed (GREEN phase)
   ```
5. Commit changes:
   ```bash
   git add .
   git commit -m "feat: Add name alias to MockPatientResponse (Phase 4)

    - Add computed field name (alias for full_name)
    - Fixes patient name display issue
    - Backward compatibility with frontend

    🤖 Generated with Claude Code
    Co-Authored-By: Claude <noreply@anthropic.com>"
    ```

**Quality Gates**:
- [ ] All 3 tests pass (100%)
- [ ] Patient responses have both `name` and `full_name`

---

#### Phase 5: Query Parameters (30 minutes)

**Goal**: Add `sort_by` and `sort_order` parameters to list endpoint

**Steps**:
1. Open `PRD-EMR-005-QUERY-PARAMS.md`
2. Create test file:
   ```bash
   pytest tests/test_emr_list_sorting.py -v
   # Expected: 2 failed (RED phase)
   ```
3. Update `backend/src/api/v1/emr/sessions.py` router:
   - Add `sort_by` query parameter
   - Add `sort_order` query parameter
   - Add validation logic
4. Update `backend/src/services/emr/session_service.py`:
   - Add sorting logic (ORDER BY)
5. Run tests:
   ```bash
   pytest tests/test_emr_list_sorting.py -v
   # Expected: 3 passed (GREEN phase)
   ```
6. Test SQL injection prevention:
   ```bash
   curl -H "Authorization: Bearer $TOKEN" \
     "http://localhost:8001/api/v1/emr/sessions?sort_by=DROP%20TABLE&sort_order=desc"
   # Expected: 200 OK (not 500), no SQL execution
   ```
7. Commit changes:
   ```bash
   git add .
   git commit -m "feat: Add sort parameters to EMR list endpoint (Phase 5)

    - Add sort_by and sort_order query parameters
    - Add SQL ORDER BY logic to service layer
    - Add SQL injection prevention validation
    - Fixes frontend sorting (newest sessions first)

    🤖 Generated with Claude Code
    Co-Authored-By: Claude <noreply@anthropic.com>"
    ```

**Quality Gates**:
- [ ] All 3 tests pass (100%)
- [ ] Sessions sorted correctly
- [ ] 0 SQL injection vulnerabilities

---

## ✅ Final Validation (After All 5 Phases Complete)

### 1. Run All Tests

```bash
cd /home/dev/Development/irStudy/backend
source venv/bin/activate

# Run all EMR tests
pytest tests/test_emr_*.py -v

# Expected output:
# test_emr_models_migration.py::test_1 PASSED
# test_emr_models_migration.py::test_2 PASSED
# ... (12 tests)
# test_emr_router_consolidation.py::test_1 PASSED
# ... (6 tests)
# test_emr_dashboard_endpoints.py::test_1 PASSED
# ... (9 tests)
# test_patient_field_aliases.py::test_1 PASSED
# ... (3 tests)
# test_emr_list_sorting.py::test_1 PASSED
# ... (3 tests)
#
# ========================= 33 passed in 45.67s =========================
```

### 2. Test Backend API

```bash
# Get JWT token
TOKEN=$(curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"student@test.com","password":"Student123!@#"}' \
  | jq -r '.access_token')

# Test 1: EMR Dashboard Metrics
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8001/api/v1/progress/dashboard/emr | jq
# Expected: 200 OK, JSON with total_sessions, avg_score, etc.

# Test 2: Unified Weekly Trends
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8001/api/v1/progress/weekly-trends/unified?weeks=12" | jq
# Expected: 200 OK, array of weekly trends

# Test 3: EMR Weak Areas
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8001/api/v1/progress/weak-areas/emr?limit=5" | jq
# Expected: 200 OK, array of weak areas

# Test 4: List Sessions (sorted)
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8001/api/v1/emr/sessions?sort_by=started_at&sort_order=desc&limit=10" | jq
# Expected: 200 OK, sessions sorted newest first
```

### 3. Test Frontend Dashboard

```bash
cd /home/dev/Development/irStudy/frontend

# Compile TypeScript (should have 0 errors)
npx tsc --noEmit
# Expected: No output (0 errors)

# Start frontend dev server
npm run dev

# Open browser
# URL: http://localhost:5173/dashboard
# Expected:
# ✅ Dashboard loads without errors
# ✅ EMR metrics card displays (total sessions, avg score)
# ✅ Recent sessions list shows (sorted newest first)
# ✅ Weekly progress chart renders
# ✅ Weak areas panel shows recommendations
# ✅ No 404 errors in browser console
```

---

## 📊 Success Criteria

**All 5 phases are COMPLETE when:**

- ✅ **33/33 tests pass** (100% pass rate)
- ✅ **Backend starts without errors** (uvicorn)
- ✅ **Frontend compiles** (0 TypeScript errors)
- ✅ **Dashboard loads** (no 404 errors)
- ✅ **API responses valid** (all endpoints return 200 OK)
- ✅ **Performance met** (response time <300ms p95)
- ✅ **Security validated** (0 hardcoded credentials, 0 SQL injection)
- ✅ **Code committed** (5 git commits minimum)

---

## 🔧 Troubleshooting

### Issue: Tests fail with ImportError

**Solution**: Phase 1 not complete. Models must be in `models.py` first.

```bash
# Check if models.py has EMR models
grep -n "class MockPatient" backend/src/db/models.py
# Expected: Line number (e.g., "45:class MockPatient(Base):")
```

### Issue: 404 errors persist after Phase 3

**Solution**: Backend not restarted. Restart uvicorn:

```bash
cd /home/dev/Development/irStudy/backend
# Kill existing uvicorn processes
pkill -f uvicorn

# Restart with .env loaded
source venv/bin/activate
set -a && source .env && set +a
uvicorn src.main:app --reload --port 8001 --host 0.0.0.0
```

### Issue: Duplicate route warnings

**Solution**: Phase 2 not complete. Delete legacy router:

```bash
rm backend/src/api/v1/emr_sessions.py
# Verify file deleted
ls backend/src/api/v1/emr_sessions.py
# Expected: No such file or directory
```

### Issue: Patient names still showing "Unknown"

**Solution**: Phase 4 not complete or backend not restarted.

```bash
# Check if computed field exists
grep -A 5 "@computed_field" backend/src/schemas/emr.py
# Expected: Should see name() method

# Restart backend
pkill -f uvicorn
cd backend && source venv/bin/activate && uvicorn src.main:app --reload --port 8001
```

---

## 📚 Reference Documents

- **EMR-IMPLEMENTATION-EXECUTION-PLAN.md** - Detailed multi-agent execution plan
- **PRD-EMR-001-MODELS-MIGRATION.md** - Phase 1 PRD (models migration)
- **PRD-EMR-002-CONSOLIDATE-ROUTERS.md** - Phase 2 PRD (router consolidation)
- **PRD-EMR-003-DASHBOARD-ENDPOINTS.md** - Phase 3 PRD (dashboard endpoints)
- **PRD-EMR-004-PATIENT-ALIAS.md** - Phase 4 PRD (patient aliases)
- **PRD-EMR-005-QUERY-PARAMS.md** - Phase 5 PRD (query parameters)
- **PROJECT_CONSTRAINTS.md** - Project-wide constraints and patterns

---

## 🎯 Quick Commands Cheat Sheet

```bash
# Backend test suite
cd /home/dev/Development/irStudy/backend && source venv/bin/activate && pytest tests/test_emr_*.py -v

# Start backend
cd /home/dev/Development/irStudy/backend && source venv/bin/activate && set -a && source .env && set +a && uvicorn src.main:app --reload --port 8001

# Frontend TypeScript check
cd /home/dev/Development/irStudy/frontend && npx tsc --noEmit

# Frontend dev server
cd /home/dev/Development/irStudy/frontend && npm run dev

# Get JWT token
TOKEN=$(curl -X POST http://localhost:8001/api/v1/auth/login -H "Content-Type: application/json" -d '{"email":"student@test.com","password":"Student123!@#"}' | jq -r '.access_token')

# Test dashboard endpoint
curl -H "Authorization: Bearer $TOKEN" http://localhost:8001/api/v1/progress/dashboard/emr | jq
```

---

**Ready to execute!** Choose Option 1 (Ralph loop) or Option 2 (manual) and get started.

Good luck! 🚀
