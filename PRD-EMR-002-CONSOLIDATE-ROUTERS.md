# PRD-EMR-002: Consolidate Duplicate EMR Router Endpoints

**Status**: READY FOR IMPLEMENTATION
**Priority**: P0 (CRITICAL - Blocks EMR dashboard functionality)
**Estimated Time**: 1-2 hours
**Agent**: `python-backend-developer`
**Created**: 2026-04-06
**Format**: T-RALPH v2.1 (Test-First Development)
**Depends On**: PRD-EMR-001-MODELS-MIGRATION (MUST complete first)

---

## Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2026-04-06 | Initial PRD - Consolidate duplicate EMR routers | PM Agent |

---

## Table of Contents

1. [T - TESTS (6 Tests Total)](#t---tests-6-tests-total)
2. [R - REQUEST (User Story)](#r---request-user-story)
3. [A - ARCHITECTURE (Current vs Target)](#a---architecture-current-vs-target)
4. [L - LOOP (TDD Workflow)](#l---loop-tdd-workflow)
5. [P - PLAN (Implementation Steps)](#p---plan-implementation-steps)
6. [H - HANDOFF (Validation & Rollback)](#h---handoff-validation--rollback)

---

# T - TESTS (6 Tests Total)

**CRITICAL**: All tests MUST be written BEFORE implementation.
**TDD Workflow**: RED (tests fail) → GREEN (tests pass) → REFACTOR (maintain 100% pass rate)

## Test File Location

```
backend/tests/test_emr_router_consolidation.py
```

## Test 1: Legacy Router No Longer Registered

**Purpose**: Verify `emr_sessions.router` is NOT registered in `router.py`

```python
"""
Test: Legacy EMR router is not registered in API v1 router

EXPECTED BEHAVIOR:
- router.py should NOT import emr_sessions module
- router.py should NOT include emr_sessions.router
- Only emr_router (from src.api.v1.emr) should be registered

TDD PHASE: RED (will fail until legacy router removed)
"""

def test_legacy_emr_router_not_registered():
    """Verify emr_sessions.router is not registered in router.py"""
    import src.api.v1.router as router_module

    # Read router.py source code
    import inspect
    source = inspect.getsource(router_module)

    # Assert emr_sessions is NOT imported
    assert "from src.api.v1 import (" in source or "import emr_sessions" not in source, \
        "emr_sessions should not be imported in router.py"

    # Assert emr_sessions.router is NOT registered
    assert "emr_sessions.router" not in source, \
        "emr_sessions.router should not be included in api_router"

    # Assert emr_router (new) IS registered
    assert "from src.api.v1.emr import router as emr_router" in source, \
        "emr_router (new implementation) should be imported"

    assert "api_router.include_router(emr_router)" in source, \
        "emr_router should be included in api_router"
```

## Test 2: Legacy Router File Deleted

**Purpose**: Verify `emr_sessions.py` file no longer exists

```python
"""
Test: Legacy emr_sessions.py file is deleted

EXPECTED BEHAVIOR:
- File backend/src/api/v1/emr_sessions.py should NOT exist
- File backend/src/api/v1/emr/sessions.py SHOULD exist (new implementation)

TDD PHASE: RED (will fail until file deleted)
"""

import os

def test_legacy_emr_sessions_file_deleted():
    """Verify emr_sessions.py is deleted"""
    legacy_file = "/home/dev/Development/irStudy/backend/src/api/v1/emr_sessions.py"
    new_file = "/home/dev/Development/irStudy/backend/src/api/v1/emr/sessions.py"

    # Legacy file should NOT exist
    assert not os.path.exists(legacy_file), \
        f"Legacy file {legacy_file} should be deleted"

    # New file SHOULD exist
    assert os.path.exists(new_file), \
        f"New file {new_file} should exist"
```

## Test 3: EMR Endpoints Return 200 OK (Not 404)

**Purpose**: Verify EMR endpoints work after consolidation

```python
"""
Test: EMR endpoints return 200 OK after router consolidation

EXPECTED BEHAVIOR:
- POST /api/v1/emr/sessions/start returns 200 (or 201)
- GET /api/v1/emr/sessions returns 200
- GET /api/v1/emr/sessions/{session_id} returns 200 (or 404 if not found)

TDD PHASE: GREEN (should pass after consolidation)
"""

import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.auth.security import create_access_token

client = TestClient(app)

def test_emr_endpoints_return_200_ok():
    """Verify EMR endpoints work after consolidation"""
    # Create test JWT token
    token = create_access_token(data={"sub": "student@test.com", "user_id": 1})
    headers = {"Authorization": f"Bearer {token}"}

    # Test 1: List sessions endpoint
    response = client.get("/api/v1/emr/sessions", headers=headers)
    assert response.status_code == 200, \
        f"GET /api/v1/emr/sessions should return 200, got {response.status_code}"

    # Test 2: Start session endpoint (may fail if no patients, but should not 404)
    response = client.post(
        "/api/v1/emr/sessions/start",
        json={"emr_system": "epic"},
        headers=headers
    )
    assert response.status_code in [200, 201, 404, 429], \
        f"POST /api/v1/emr/sessions/start should return 200/201/404/429, got {response.status_code}"

    # 404 is OK if no patients exist
    # 429 is OK if too many active sessions
    # But should NOT be 500 (server error)
```

## Test 4: No Duplicate Route Registration

**Purpose**: Verify no duplicate routes registered in FastAPI app

```python
"""
Test: No duplicate EMR routes registered in FastAPI app

EXPECTED BEHAVIOR:
- Each EMR endpoint path should be registered ONCE only
- No duplicate routes like /emr/sessions (from both routers)

TDD PHASE: GREEN (should pass after removing duplicate router)
"""

from src.main import app

def test_no_duplicate_emr_routes():
    """Verify no duplicate EMR routes in FastAPI app"""
    # Get all registered routes
    routes = [route.path for route in app.routes]

    # EMR routes we expect (from emr_router only)
    emr_routes = [
        "/api/v1/emr/sessions/start",
        "/api/v1/emr/sessions/{session_id}",
        "/api/v1/emr/sessions/{session_id}/submit",
        "/api/v1/emr/sessions",  # List endpoint
    ]

    # Count occurrences of each route
    for route_path in emr_routes:
        count = routes.count(route_path)
        assert count == 1, \
            f"Route {route_path} registered {count} times, expected 1 (no duplicates)"
```

## Test 5: Router Import Does Not Fail

**Purpose**: Verify `router.py` imports successfully after cleanup

```python
"""
Test: router.py imports successfully without emr_sessions

EXPECTED BEHAVIOR:
- import src.api.v1.router should succeed
- No ImportError for missing emr_sessions module

TDD PHASE: GREEN (should pass after removing import)
"""

def test_router_import_succeeds():
    """Verify router.py imports successfully"""
    try:
        import src.api.v1.router
        from src.api.v1.router import api_router

        # Should succeed without errors
        assert api_router is not None, "api_router should be defined"

    except ImportError as e:
        pytest.fail(f"router.py import failed: {e}")
```

## Test 6: Uvicorn Startup Succeeds

**Purpose**: Verify backend starts without errors after router consolidation

```python
"""
Test: Backend (uvicorn) starts successfully after router consolidation

EXPECTED BEHAVIOR:
- FastAPI app should initialize without errors
- No duplicate route warnings
- No missing module errors

TDD PHASE: GREEN (should pass after consolidation)
"""

import subprocess
import time
import requests
import signal

def test_uvicorn_startup_succeeds():
    """Verify uvicorn starts successfully"""
    # Start uvicorn in background
    proc = subprocess.Popen(
        [
            "bash", "-c",
            "cd /home/dev/Development/irStudy/backend && "
            "source venv/bin/activate && "
            "set -a && source .env && set +a && "
            "uvicorn src.main:app --port 8002 --host 127.0.0.1"
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    try:
        # Wait 5 seconds for startup
        time.sleep(5)

        # Check if process is still running (didn't crash)
        assert proc.poll() is None, \
            f"Uvicorn crashed during startup. stderr: {proc.stderr.read()}"

        # Check health endpoint
        response = requests.get("http://127.0.0.1:8002/api/v1/health", timeout=3)
        assert response.status_code == 200, \
            f"Health endpoint should return 200, got {response.status_code}"

    finally:
        # Kill uvicorn process
        proc.send_signal(signal.SIGTERM)
        proc.wait(timeout=5)
```

---

# R - REQUEST (User Story)

## Problem Statement

**Current Issue**: Two EMR router implementations exist in the codebase, causing conflicts:

1. **Legacy Router**: `backend/src/api/v1/emr_sessions.py` (registered on line 52 of `router.py`)
   - Has inline model definitions (violates Phase 1 - models should be in `models.py`)
   - Limited functionality: 3 endpoints (create, get, submit)
   - Uses local schemas (`.schemas`) that don't exist in new structure
   - Uses `get_current_user` dependency (should use `get_current_active_user`)

2. **New Router**: `backend/src/api/v1/emr/sessions.py` (registered on line 51 of `router.py`)
   - Clean implementation importing from `src.schemas.emr` and `src.services.emr.*`
   - Comprehensive functionality: 6 endpoints (start, update, submit, get, list, delete)
   - Proper service layer separation
   - Uses correct `get_current_active_user` dependency

**Impact**:
- ❌ Duplicate route registrations in FastAPI app
- ❌ Frontend requests to `/api/v1/emr/sessions` may hit wrong router
- ❌ Confusing for developers (which implementation to use?)
- ❌ Blocks Phase 3 (dashboard endpoints) - unclear which router to extend

## User Story

**As a** backend developer implementing EMR dashboard endpoints,
**I want** a single, authoritative EMR router implementation,
**So that** I can confidently extend it with new endpoints without conflicts.

**Acceptance Criteria**:
- [ ] Only ONE EMR router registered in `router.py` (the newer `emr_router`)
- [ ] Legacy `emr_sessions.py` file deleted from codebase
- [ ] No import errors when starting backend
- [ ] All EMR endpoints return correct status codes (not 500)
- [ ] No duplicate route warnings in uvicorn startup logs
- [ ] 100% test pass rate (6 tests)

## Success Metrics

| Metric | Current | Target | Validation |
|--------|---------|--------|------------|
| Duplicate routers | 2 | 1 | Test 1: Legacy router not registered |
| Duplicate routes | YES | NO | Test 4: No duplicate route registration |
| Import errors | 0 | 0 | Test 5: Router import succeeds |
| Test pass rate | N/A | 100% | pytest exit code 0 |
| Uvicorn startup | SUCCESS | SUCCESS | Test 6: Uvicorn starts without errors |

---

# A - ARCHITECTURE (Current vs Target)

## Current Architecture (BROKEN)

```
backend/src/api/v1/
├── router.py (PROBLEM: registers BOTH routers)
│   ├── Line 29: import emr_sessions (legacy)
│   ├── Line 32: from src.api.v1.emr import router as emr_router (new)
│   ├── Line 51: api_router.include_router(emr_router) ← NEW
│   └── Line 52: api_router.include_router(emr_sessions.router) ← LEGACY (duplicate!)
│
├── emr_sessions.py (LEGACY - TO DELETE)
│   ├── Lines 43-100: Inline model definitions (violates Phase 1)
│   ├── Lines 22-31: Local imports (.schemas, .validation)
│   ├── Line 102: router = APIRouter() (no prefix)
│   └── 3 endpoints: POST /sessions, GET /sessions/{id}, POST /sessions/{id}/submit
│
└── emr/
    ├── __init__.py (exports emr_router)
    └── sessions.py (NEW - KEEP THIS)
        ├── Line 53: router = APIRouter(prefix="/emr/sessions", tags=["EMR Sessions"])
        ├── Imports from src.schemas.emr, src.services.emr.*
        └── 6 endpoints: start, update, submit, get, list, delete
```

**Problems**:
1. **Duplicate Registration**: Both routers registered → duplicate routes
2. **Inline Models**: Legacy router has inline models (Phase 1 violation)
3. **Confusion**: Developers don't know which implementation to use
4. **Maintenance Burden**: Fixing bugs requires updating 2 files

## Target Architecture (CLEAN)

```
backend/src/api/v1/
├── router.py (FIXED: registers ONLY new router)
│   ├── Line 32: from src.api.v1.emr import router as emr_router (KEEP)
│   ├── Line 51: api_router.include_router(emr_router) (KEEP)
│   └── ❌ REMOVED: Lines 29, 52 (emr_sessions import + registration)
│
├── ❌ DELETED: emr_sessions.py (legacy file removed)
│
└── emr/
    ├── __init__.py (exports emr_router)
    └── sessions.py (SINGLE SOURCE OF TRUTH)
        ├── router = APIRouter(prefix="/emr/sessions", tags=["EMR Sessions"])
        ├── Imports from src.schemas.emr, src.services.emr.*
        └── 6 endpoints: start, update, submit, get, list, delete
```

**Benefits**:
- ✅ Single source of truth for EMR endpoints
- ✅ No duplicate route registrations
- ✅ Clean codebase (no legacy files)
- ✅ Easier to extend (Phase 3 can confidently modify `emr/sessions.py`)

## Endpoint Mapping

| Endpoint | Legacy (DELETE) | New (KEEP) | Notes |
|----------|----------------|------------|-------|
| Create session | POST /sessions | POST /emr/sessions/start | New has better path |
| Get session | GET /sessions/{id} | GET /emr/sessions/{id} | Same functionality |
| Submit session | POST /sessions/{id}/submit | POST /emr/sessions/{id}/submit | Same functionality |
| Update (auto-save) | ❌ Not implemented | PUT /emr/sessions/{id} | New router only |
| List sessions | ❌ Not implemented | GET /emr/sessions | New router only |
| Delete session | ❌ Not implemented | DELETE /emr/sessions/{id} | New router only |

**Verdict**: New router (`emr/sessions.py`) is more comprehensive and should be kept.

---

# L - LOOP (TDD Workflow)

## Phase 1: RED (Tests Fail) - Write Tests First

**Estimated Time**: 15 minutes

### Actions:
1. Create test file: `backend/tests/test_emr_router_consolidation.py`
2. Copy all 6 test functions from T section above
3. Run tests:
   ```bash
   cd /home/dev/Development/irStudy/backend
   source venv/bin/activate
   pytest tests/test_emr_router_consolidation.py -v
   ```

### Expected Result (RED):
```
FAILED test_legacy_emr_router_not_registered - AssertionError: emr_sessions.router should not be included
FAILED test_legacy_emr_sessions_file_deleted - AssertionError: Legacy file should be deleted
PASSED test_emr_endpoints_return_200_ok (may pass or fail depending on data)
FAILED test_no_duplicate_emr_routes - AssertionError: Route /api/v1/emr/sessions registered 2 times
PASSED test_router_import_succeeds (will pass)
PASSED test_uvicorn_startup_succeeds (may show duplicate route warnings)
```

**Validation**: Tests 1, 2, 4 MUST fail (RED phase confirmed).

---

## Phase 2: GREEN (Tests Pass) - Implement Consolidation

**Estimated Time**: 30 minutes

### Actions:
1. **Remove legacy router registration from `router.py`**:
   - Delete line 29: `emr_sessions,` import
   - Delete line 52: `api_router.include_router(emr_sessions.router)`

2. **Delete legacy router file**:
   ```bash
   rm /home/dev/Development/irStudy/backend/src/api/v1/emr_sessions.py
   ```

3. **Run tests again**:
   ```bash
   pytest tests/test_emr_router_consolidation.py -v
   ```

### Expected Result (GREEN):
```
PASSED test_legacy_emr_router_not_registered
PASSED test_legacy_emr_sessions_file_deleted
PASSED test_emr_endpoints_return_200_ok
PASSED test_no_duplicate_emr_routes
PASSED test_router_import_succeeds
PASSED test_uvicorn_startup_succeeds

========================= 6 passed in 12.34s =========================
```

**Validation**: ALL 6 tests MUST pass (GREEN phase confirmed).

---

## Phase 3: REFACTOR (Cleanup) - Verify No Regressions

**Estimated Time**: 15 minutes

### Actions:
1. **Run full backend test suite**:
   ```bash
   cd /home/dev/Development/irStudy/backend
   source venv/bin/activate
   pytest --cov=src --cov-report=term-missing -v
   ```

2. **Verify TypeScript frontend compilation** (should still work):
   ```bash
   cd /home/dev/Development/irStudy/frontend
   npx tsc --noEmit
   ```

3. **Test backend startup** (no errors):
   ```bash
   cd /home/dev/Development/irStudy/backend
   source venv/bin/activate
   set -a && source .env && set +a
   uvicorn src.main:app --reload --port 8001 --host 0.0.0.0
   # Check startup logs for duplicate route warnings (should be NONE)
   ```

4. **Test EMR endpoint manually**:
   ```bash
   # Login to get JWT token
   curl -X POST http://localhost:8001/api/v1/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email":"student@test.com","password":"Student123!@#"}'

   # Use token to test EMR list endpoint
   curl -X GET http://localhost:8001/api/v1/emr/sessions \
     -H "Authorization: Bearer <token>"

   # Should return 200 OK with JSON array
   ```

### Expected Result (REFACTOR):
```
✅ All tests pass (100% pass rate)
✅ No duplicate route warnings in uvicorn logs
✅ TypeScript compilation: 0 errors
✅ EMR endpoints return 200 OK
✅ No import errors
```

**Validation Checklist**:
- [ ] All 6 consolidation tests pass
- [ ] Full test suite passes (100% pass rate)
- [ ] No uvicorn startup errors
- [ ] No duplicate route warnings
- [ ] TypeScript compiles successfully
- [ ] EMR endpoints work via curl

---

# P - PLAN (Implementation Steps)

## File 1: Create Test File

**Path**: `backend/tests/test_emr_router_consolidation.py`

**Action**: Write all 6 tests from T section

```python
"""
EMR Router Consolidation Tests

PURPOSE: Verify legacy emr_sessions.py router is removed and only
         emr/sessions.py router remains registered.

TESTS (6 total):
1. test_legacy_emr_router_not_registered - Legacy router not in router.py
2. test_legacy_emr_sessions_file_deleted - emr_sessions.py file deleted
3. test_emr_endpoints_return_200_ok - EMR endpoints work after consolidation
4. test_no_duplicate_emr_routes - No duplicate routes in FastAPI app
5. test_router_import_succeeds - router.py imports without errors
6. test_uvicorn_startup_succeeds - Backend starts successfully

TDD WORKFLOW: RED → GREEN → REFACTOR
Expected: Tests 1, 2, 4 fail initially (RED phase)
After implementation: All 6 tests pass (GREEN phase)
"""

import os
import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.auth.security import create_access_token
import subprocess
import time
import requests
import signal


# ============================================================================
# TEST 1: Legacy Router Not Registered
# ============================================================================

def test_legacy_emr_router_not_registered():
    """Verify emr_sessions.router is not registered in router.py"""
    import src.api.v1.router as router_module
    import inspect

    source = inspect.getsource(router_module)

    # Assert emr_sessions is NOT imported
    assert "import emr_sessions" not in source, \
        "emr_sessions should not be imported in router.py"

    # Assert emr_sessions.router is NOT registered
    assert "emr_sessions.router" not in source, \
        "emr_sessions.router should not be included in api_router"

    # Assert emr_router (new) IS registered
    assert "from src.api.v1.emr import router as emr_router" in source, \
        "emr_router (new implementation) should be imported"

    assert "api_router.include_router(emr_router)" in source, \
        "emr_router should be included in api_router"


# ============================================================================
# TEST 2: Legacy Router File Deleted
# ============================================================================

def test_legacy_emr_sessions_file_deleted():
    """Verify emr_sessions.py is deleted"""
    legacy_file = "/home/dev/Development/irStudy/backend/src/api/v1/emr_sessions.py"
    new_file = "/home/dev/Development/irStudy/backend/src/api/v1/emr/sessions.py"

    # Legacy file should NOT exist
    assert not os.path.exists(legacy_file), \
        f"Legacy file {legacy_file} should be deleted"

    # New file SHOULD exist
    assert os.path.exists(new_file), \
        f"New file {new_file} should exist"


# ============================================================================
# TEST 3: EMR Endpoints Return 200 OK
# ============================================================================

client = TestClient(app)

def test_emr_endpoints_return_200_ok():
    """Verify EMR endpoints work after consolidation"""
    # Create test JWT token
    token = create_access_token(data={"sub": "student@test.com", "user_id": 1})
    headers = {"Authorization": f"Bearer {token}"}

    # Test 1: List sessions endpoint
    response = client.get("/api/v1/emr/sessions", headers=headers)
    assert response.status_code == 200, \
        f"GET /api/v1/emr/sessions should return 200, got {response.status_code}"

    # Test 2: Start session endpoint (may fail if no patients, but should not 404)
    response = client.post(
        "/api/v1/emr/sessions/start",
        json={"emr_system": "epic"},
        headers=headers
    )
    assert response.status_code in [200, 201, 404, 429], \
        f"POST /api/v1/emr/sessions/start should return 200/201/404/429, got {response.status_code}"


# ============================================================================
# TEST 4: No Duplicate Route Registration
# ============================================================================

def test_no_duplicate_emr_routes():
    """Verify no duplicate EMR routes in FastAPI app"""
    routes = [route.path for route in app.routes]

    # EMR routes we expect (from emr_router only)
    emr_routes = [
        "/api/v1/emr/sessions/start",
        "/api/v1/emr/sessions/{session_id}",
        "/api/v1/emr/sessions/{session_id}/submit",
        "/api/v1/emr/sessions",
    ]

    # Count occurrences of each route
    for route_path in emr_routes:
        count = routes.count(route_path)
        assert count == 1, \
            f"Route {route_path} registered {count} times, expected 1 (no duplicates)"


# ============================================================================
# TEST 5: Router Import Succeeds
# ============================================================================

def test_router_import_succeeds():
    """Verify router.py imports successfully"""
    try:
        import src.api.v1.router
        from src.api.v1.router import api_router

        assert api_router is not None, "api_router should be defined"

    except ImportError as e:
        pytest.fail(f"router.py import failed: {e}")


# ============================================================================
# TEST 6: Uvicorn Startup Succeeds
# ============================================================================

def test_uvicorn_startup_succeeds():
    """Verify uvicorn starts successfully"""
    # Start uvicorn in background
    proc = subprocess.Popen(
        [
            "bash", "-c",
            "cd /home/dev/Development/irStudy/backend && "
            "source venv/bin/activate && "
            "set -a && source .env && set +a && "
            "uvicorn src.main:app --port 8002 --host 127.0.0.1"
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    try:
        # Wait 5 seconds for startup
        time.sleep(5)

        # Check if process is still running (didn't crash)
        assert proc.poll() is None, \
            f"Uvicorn crashed during startup. stderr: {proc.stderr.read()}"

        # Check health endpoint
        response = requests.get("http://127.0.0.1:8002/api/v1/health", timeout=3)
        assert response.status_code == 200, \
            f"Health endpoint should return 200, got {response.status_code}"

    finally:
        # Kill uvicorn process
        proc.send_signal(signal.SIGTERM)
        proc.wait(timeout=5)
```

---

## File 2: Modify `router.py` - Remove Legacy Router

**Path**: `backend/src/api/v1/router.py`

**Action**: Remove legacy `emr_sessions` import and registration

**BEFORE** (lines 16-32, 51-52):
```python
from src.api.v1 import (
    auth,
    users,
    mcqs,
    osces,
    progress,
    permissions,
    gdpr,
    study_cards,
    study_cards_optimized,
    patient_personas,
    osce_sessions,
    health,
    emr_sessions,  # ← DELETE THIS LINE
    mock_exams,
)
from src.api.v1.emr import router as emr_router

# ... (lines 36-50)

api_router.include_router(emr_router)  # PRD GAP 002: EMR API Endpoints (existing)
api_router.include_router(emr_sessions.router)  # ← DELETE THIS LINE
api_router.include_router(health.router)  # Health check endpoints (Kubernetes probes)
```

**AFTER**:
```python
from src.api.v1 import (
    auth,
    users,
    mcqs,
    osces,
    progress,
    permissions,
    gdpr,
    study_cards,
    study_cards_optimized,
    patient_personas,
    osce_sessions,
    health,
    mock_exams,
)
from src.api.v1.emr import router as emr_router

# ... (lines 36-50)

api_router.include_router(emr_router)  # PRD GAP 002: EMR API Endpoints (existing)
api_router.include_router(health.router)  # Health check endpoints (Kubernetes probes)
```

**Changes**:
- Line 29: REMOVE `emr_sessions,` from import list
- Line 52: REMOVE `api_router.include_router(emr_sessions.router)` registration

---

## File 3: Delete Legacy Router File

**Path**: `backend/src/api/v1/emr_sessions.py`

**Action**: Delete entire file

```bash
rm /home/dev/Development/irStudy/backend/src/api/v1/emr_sessions.py
```

**Verification**:
```bash
# File should NOT exist after deletion
ls /home/dev/Development/irStudy/backend/src/api/v1/emr_sessions.py
# Expected: ls: cannot access ... No such file or directory
```

---

# H - HANDOFF (Validation & Rollback)

## Pre-Implementation Checklist

- [ ] **Read PROJECT_CONSTRAINTS.md** (All agents MUST read before starting)
- [ ] **Verify Phase 1 complete**: PRD-EMR-001-MODELS-MIGRATION finished (models in `models.py`)
- [ ] **Understand router structure**: Read `router.py` and `emr/sessions.py`
- [ ] **Backend running**: Start backend to test after changes

## Implementation Checklist

### Phase 1: RED (Write Tests)
- [ ] Create `backend/tests/test_emr_router_consolidation.py`
- [ ] Copy all 6 test functions from T section
- [ ] Run tests: `pytest tests/test_emr_router_consolidation.py -v`
- [ ] **Verify RED**: Tests 1, 2, 4 MUST fail initially
- [ ] Commit tests: `git add tests/test_emr_router_consolidation.py && git commit -m "test: Add EMR router consolidation tests (TDD RED)"`

### Phase 2: GREEN (Implement Consolidation)
- [ ] Open `backend/src/api/v1/router.py` in editor
- [ ] Remove line 29: `emr_sessions,` from import list
- [ ] Remove line 52: `api_router.include_router(emr_sessions.router)`
- [ ] Save file and verify syntax (no trailing commas issues)
- [ ] Delete legacy file: `rm backend/src/api/v1/emr_sessions.py`
- [ ] Run tests: `pytest tests/test_emr_router_consolidation.py -v`
- [ ] **Verify GREEN**: ALL 6 tests MUST pass
- [ ] Commit changes: `git add . && git commit -m "refactor: Consolidate EMR routers (remove duplicate emr_sessions.py)"`

### Phase 3: REFACTOR (Verify No Regressions)
- [ ] Run full backend test suite: `pytest --cov=src --cov-report=term-missing`
- [ ] Verify 100% test pass rate (no failures)
- [ ] Test TypeScript compilation: `cd frontend && npx tsc --noEmit`
- [ ] Verify 0 TypeScript errors
- [ ] Start backend: `cd backend && source venv/bin/activate && set -a && source .env && set +a && uvicorn src.main:app --reload --port 8001`
- [ ] Check uvicorn logs for duplicate route warnings (should be NONE)
- [ ] Test EMR endpoint via curl:
  ```bash
  # Login
  TOKEN=$(curl -X POST http://localhost:8001/api/v1/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email":"student@test.com","password":"Student123!@#"}' \
    | jq -r '.access_token')

  # Test EMR list endpoint
  curl -X GET http://localhost:8001/api/v1/emr/sessions \
    -H "Authorization: Bearer $TOKEN"
  # Expected: {"sessions":[],"total_count":0,"limit":20,"offset":0}
  ```
- [ ] Verify response is 200 OK (not 404 or 500)

## Quality Gates

| Gate | Requirement | Validation Command | Expected Result |
|------|-------------|-------------------|-----------------|
| **1. Tests Pass** | 100% pass rate (6/6 tests) | `pytest tests/test_emr_router_consolidation.py -v` | `6 passed in X.XXs` |
| **2. No Regressions** | Full test suite passes | `pytest --cov=src` | `100% pass rate` |
| **3. No Import Errors** | Backend starts successfully | `uvicorn src.main:app` | No errors in logs |
| **4. No Duplicate Routes** | FastAPI app has unique routes | Check uvicorn startup logs | No duplicate warnings |
| **5. TypeScript Compiles** | Frontend code valid | `npx tsc --noEmit` | `0 errors` |
| **6. Endpoints Work** | EMR endpoints return 200 OK | `curl /api/v1/emr/sessions` | HTTP 200 |

**ALL quality gates MUST pass before marking Phase 2 complete.**

## Rollback Plan

If implementation fails quality gates, revert changes:

```bash
# Rollback git commit
cd /home/dev/Development/irStudy
git log --oneline -5  # Find commit hash before consolidation
git revert <commit-hash>

# Or restore files manually
git checkout HEAD~1 backend/src/api/v1/router.py
git checkout HEAD~1 backend/src/api/v1/emr_sessions.py  # Restore deleted file

# Restart backend
cd backend
source venv/bin/activate
set -a && source .env && set +a
uvicorn src.main:app --reload --port 8001
```

## Success Criteria

Phase 2 is COMPLETE when:
- ✅ All 6 consolidation tests pass (100% pass rate)
- ✅ Full backend test suite passes (no regressions)
- ✅ Backend starts without errors (no duplicate routes)
- ✅ TypeScript compilation succeeds (0 errors)
- ✅ EMR endpoints return 200 OK (tested via curl)
- ✅ Code committed to git with descriptive message

## Next Steps

After Phase 2 completion:
1. **Mark Phase 2 DONE** in todo list
2. **Proceed to Phase 3**: PRD-EMR-003-DASHBOARD-ENDPOINTS (implement missing endpoints)
3. **Update PROJECT_CONSTRAINTS.md**: Document router consolidation pattern

---

## Appendix A: Router Comparison

### Legacy Router (`emr_sessions.py`) - TO DELETE

**Endpoints** (3 total):
- POST `/sessions` - Create session
- GET `/sessions/{session_id}` - Get session
- POST `/sessions/{session_id}/submit` - Submit session

**Issues**:
- ❌ Inline model definitions (violates Phase 1)
- ❌ Local imports (`.schemas`, `.validation`) don't exist
- ❌ No prefix in router (path would be `/sessions`, not `/emr/sessions`)
- ❌ Missing endpoints: update (auto-save), list, delete
- ❌ Uses `get_current_user` instead of `get_current_active_user`

### New Router (`emr/sessions.py`) - TO KEEP

**Endpoints** (6 total):
- POST `/emr/sessions/start` - Start session
- PUT `/emr/sessions/{session_id}` - Auto-save draft
- POST `/emr/sessions/{session_id}/submit` - Submit session
- GET `/emr/sessions/{session_id}` - Get session details
- GET `/emr/sessions` - List sessions (pagination, filters)
- DELETE `/emr/sessions/{session_id}` - Delete draft

**Advantages**:
- ✅ Clean imports from `src.schemas.emr`, `src.services.emr.*`
- ✅ Service layer separation (SessionService, PatientService)
- ✅ Proper prefix: `APIRouter(prefix="/emr/sessions")`
- ✅ Comprehensive functionality (6 endpoints vs 3)
- ✅ Correct dependency: `get_current_active_user`
- ✅ Performance targets documented (<200ms auto-save, <500ms submit)

---

## Appendix B: Testing Strategy

### Unit Tests (6 tests in this PRD)
- `test_legacy_emr_router_not_registered` - Static code analysis of `router.py`
- `test_legacy_emr_sessions_file_deleted` - File system check
- `test_emr_endpoints_return_200_ok` - Integration test (TestClient)
- `test_no_duplicate_emr_routes` - FastAPI app introspection
- `test_router_import_succeeds` - Import test
- `test_uvicorn_startup_succeeds` - End-to-end startup test

### Integration Tests (existing suite)
- All existing EMR tests should continue to pass
- Endpoints remain accessible (path unchanged: `/api/v1/emr/sessions`)

### Manual Testing
- Start backend → Check uvicorn logs (no warnings)
- Login via curl → Get JWT token
- Test EMR endpoints → Verify 200 OK responses

---

**END OF PRD-EMR-002-CONSOLIDATE-ROUTERS**
