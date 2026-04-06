# PRD-EMR-005: Add Sort Query Parameters to EMR Sessions List Endpoint

**Status**: READY FOR IMPLEMENTATION
**Priority**: P1 (Important - Improves UX)
**Estimated Time**: 30 minutes
**Created**: 2026-04-06
**Format**: T-RALPH v2.1 (Test-First Development)
**Depends On**: PRD-EMR-001 (Models), PRD-EMR-002 (Router Consolidation)

## Multi-Agent Assignment

**Primary Agent**: `python-backend-developer`
- **Role**: Implementation (add sort_by/sort_order parameters, SQL ORDER BY)
- **Deliverables**: Working sort parameters, 3 passing tests

**Secondary Agent**: `security-compliance-expert`
- **Role**: Security validation (SQL injection prevention, input sanitization)
- **Deliverables**: Security scan (0 SQL injection vulnerabilities)

**Handoff Procedure**:
1. `python-backend-developer` implements sort parameters → Runs all 3 tests (GREEN)
2. `security-compliance-expert` validates SQL injection prevention → Tests invalid inputs
3. Both agents approve → Phase 5 COMPLETE

---

## Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2026-04-06 | Initial PRD - Add sort query parameters to list endpoint | PM Agent |

---

## Table of Contents

1. [T - TESTS (3 Tests Total)](#t---tests-3-tests-total)
2. [R - REQUEST (User Story)](#r---request-user-story)
3. [A - ARCHITECTURE (Current vs Target)](#a---architecture-current-vs-target)
4. [L - LOOP (TDD Workflow)](#l---loop-tdd-workflow)
5. [P - PLAN (Implementation Steps)](#p---plan-implementation-steps)
6. [H - HANDOFF (Validation & Rollback)](#h---handoff-validation--rollback)

---

# T - TESTS (3 Tests Total)

**CRITICAL**: All tests MUST be written BEFORE implementation.
**TDD Workflow**: RED (tests fail) → GREEN (tests pass) → REFACTOR (maintain 100% pass rate)

## Test File Location

```
backend/tests/test_emr_list_sorting.py
```

## Test 1: List Sessions Sorted by created_at Descending

**Purpose**: Verify list endpoint supports sort_by=created_at, sort_order=desc

```python
"""
Test: GET /emr/sessions?sort_by=created_at&sort_order=desc returns sorted sessions

EXPECTED BEHAVIOR:
- Accepts sort_by and sort_order query parameters
- Returns sessions sorted by created_at descending (newest first)
- Frontend receives sessions in correct order

TDD PHASE: RED (will fail until sort parameters added)
"""

import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.db.models import User, EMRSession, MockPatient
from src.auth.security import create_access_token
from datetime import datetime, timedelta
from uuid import uuid4

client = TestClient(app)

def test_list_sessions_sorted_by_created_at_desc(db_session):
    """Test list endpoint sorts by created_at descending"""
    # Create test user
    user = User(
        id=200,
        email="sort@test.com",
        password_hash="hashed",
        full_name="Sort Test",
        role="student"
    )
    db_session.add(user)
    db_session.commit()

    # Create test patient
    patient = MockPatient(
        patient_id=uuid4(),
        full_name="Test Patient",
        mrn="MRN_SORT",
        age=45,
        gender="Male",
        specialty="Cardiology",
        difficulty="intermediate"
    )
    db_session.add(patient)
    db_session.commit()

    # Create 3 sessions with different created_at times
    session1 = EMRSession(
        session_id=uuid4(),
        user_id=user.id,
        patient_id=patient.patient_id,
        emr_system="epic",
        specialty="Cardiology",
        difficulty="intermediate",
        started_at=datetime.utcnow() - timedelta(hours=3),  # Oldest
        submitted_at=None
    )
    session2 = EMRSession(
        session_id=uuid4(),
        user_id=user.id,
        patient_id=patient.patient_id,
        emr_system="cerner",
        specialty="Cardiology",
        difficulty="intermediate",
        started_at=datetime.utcnow() - timedelta(hours=2),  # Middle
        submitted_at=None
    )
    session3 = EMRSession(
        session_id=uuid4(),
        user_id=user.id,
        patient_id=patient.patient_id,
        emr_system="epic",
        specialty="Cardiology",
        difficulty="intermediate",
        started_at=datetime.utcnow() - timedelta(hours=1),  # Newest
        submitted_at=None
    )

    db_session.add_all([session1, session2, session3])
    db_session.commit()

    # Create JWT token
    token = create_access_token(data={"sub": "sort@test.com", "user_id": 200})
    headers = {"Authorization": f"Bearer {token}"}

    # Call list endpoint with sort parameters
    response = client.get(
        "/api/v1/emr/sessions",
        params={"sort_by": "created_at", "sort_order": "desc", "limit": 10},
        headers=headers
    )

    # Assertions
    assert response.status_code == 200, \
        f"Expected 200, got {response.status_code}: {response.text}"

    data = response.json()

    assert "sessions" in data, "Missing sessions field in response"
    assert len(data["sessions"]) == 3, f"Expected 3 sessions, got {len(data['sessions'])}"

    # Verify sorting: Newest first (session3 → session2 → session1)
    sessions = data["sessions"]

    # Compare started_at timestamps (newest first)
    session_times = [datetime.fromisoformat(s["started_at"].replace("Z", "+00:00")) for s in sessions]

    assert session_times[0] > session_times[1], \
        "First session should be newer than second (descending order)"
    assert session_times[1] > session_times[2], \
        "Second session should be newer than third (descending order)"
```

## Test 2: List Sessions Sorted by created_at Ascending

**Purpose**: Verify sort_order=asc works correctly

```python
"""
Test: GET /emr/sessions?sort_by=created_at&sort_order=asc returns sorted sessions

EXPECTED BEHAVIOR:
- Accepts sort_order=asc
- Returns sessions sorted by created_at ascending (oldest first)

TDD PHASE: RED (will fail until sort parameters added)
"""

def test_list_sessions_sorted_by_created_at_asc(db_session):
    """Test list endpoint sorts by created_at ascending"""
    # Create test user
    user = User(
        id=201,
        email="sortasc@test.com",
        password_hash="hashed",
        full_name="Sort Asc Test",
        role="student"
    )
    db_session.add(user)
    db_session.commit()

    # Create test patient
    patient = MockPatient(
        patient_id=uuid4(),
        full_name="Test Patient 2",
        mrn="MRN_ASC",
        age=50,
        gender="Female",
        specialty="Respiratory",
        difficulty="intermediate"
    )
    db_session.add(patient)
    db_session.commit()

    # Create 3 sessions
    session1 = EMRSession(
        session_id=uuid4(),
        user_id=user.id,
        patient_id=patient.patient_id,
        emr_system="epic",
        specialty="Respiratory",
        difficulty="intermediate",
        started_at=datetime.utcnow() - timedelta(days=3),  # Oldest
        submitted_at=datetime.utcnow() - timedelta(days=2)
    )
    session2 = EMRSession(
        session_id=uuid4(),
        user_id=user.id,
        patient_id=patient.patient_id,
        emr_system="cerner",
        specialty="Respiratory",
        difficulty="intermediate",
        started_at=datetime.utcnow() - timedelta(days=2),  # Middle
        submitted_at=datetime.utcnow() - timedelta(days=1)
    )
    session3 = EMRSession(
        session_id=uuid4(),
        user_id=user.id,
        patient_id=patient.patient_id,
        emr_system="epic",
        specialty="Respiratory",
        difficulty="intermediate",
        started_at=datetime.utcnow() - timedelta(days=1),  # Newest
        submitted_at=datetime.utcnow()
    )

    db_session.add_all([session1, session2, session3])
    db_session.commit()

    # Create JWT token
    token = create_access_token(data={"sub": "sortasc@test.com", "user_id": 201})
    headers = {"Authorization": f"Bearer {token}"}

    # Call list endpoint with sort_order=asc
    response = client.get(
        "/api/v1/emr/sessions",
        params={"sort_by": "created_at", "sort_order": "asc", "limit": 10},
        headers=headers
    )

    # Assertions
    assert response.status_code == 200

    data = response.json()
    sessions = data["sessions"]

    assert len(sessions) == 3

    # Verify sorting: Oldest first (session1 → session2 → session3)
    session_times = [datetime.fromisoformat(s["started_at"].replace("Z", "+00:00")) for s in sessions]

    assert session_times[0] < session_times[1], \
        "First session should be older than second (ascending order)"
    assert session_times[1] < session_times[2], \
        "Second session should be older than third (ascending order)"
```

## Test 3: List Sessions with Invalid Sort Parameters Falls Back to Default

**Purpose**: Verify invalid sort parameters are handled gracefully

```python
"""
Test: Invalid sort parameters fall back to default sorting

EXPECTED BEHAVIOR:
- Invalid sort_by values ignored (use default)
- Invalid sort_order values default to "desc"
- No 500 error thrown

TDD PHASE: GREEN (should pass after implementation)
"""

def test_list_sessions_invalid_sort_params_fallback(db_session):
    """Test invalid sort parameters fall back to default"""
    # Create test user
    user = User(
        id=202,
        email="sortinvalid@test.com",
        password_hash="hashed",
        full_name="Sort Invalid Test",
        role="student"
    )
    db_session.add(user)
    db_session.commit()

    # Create JWT token
    token = create_access_token(data={"sub": "sortinvalid@test.com", "user_id": 202})
    headers = {"Authorization": f"Bearer {token}"}

    # Call with invalid sort_by
    response = client.get(
        "/api/v1/emr/sessions",
        params={"sort_by": "invalid_field", "sort_order": "desc"},
        headers=headers
    )

    # Should NOT return 500 error
    assert response.status_code == 200, \
        f"Should return 200 (fallback to default), got {response.status_code}"

    # Call with invalid sort_order
    response = client.get(
        "/api/v1/emr/sessions",
        params={"sort_by": "created_at", "sort_order": "invalid_order"},
        headers=headers
    )

    # Should NOT return 500 error
    assert response.status_code == 200, \
        f"Should return 200 (fallback to default), got {response.status_code}"
```

---

# R - REQUEST (User Story)

## Problem Statement

**Current Issue**: Frontend passes `sort_by` and `sort_order` parameters, but backend ignores them

**Evidence from Frontend Code**:
```typescript
// frontend/src/hooks/useEMRDashboardData.ts:136-138
const response = await axiosInstance.get<{ sessions: RecentSession[] }>(
  '/emr/sessions',
  {
    params: {
      limit: 10,
      sort_by: 'created_at',      // ❌ IGNORED by backend
      sort_order: 'desc',          // ❌ IGNORED by backend
    },
  }
);
```

**Current Backend Code**:
```python
# backend/src/api/v1/emr_sessions.py:463-469 (LEGACY - to be deleted)
async def list_sessions(
    is_active: Optional[bool] = Query(None, ...),
    specialty: Optional[str] = Query(None, ...),
    limit: int = Query(20, le=100, ...),
    offset: int = Query(0, ge=0, ...),
    # ❌ MISSING: sort_by parameter
    # ❌ MISSING: sort_order parameter
    ...
)
```

**Impact**:
- Dashboard always shows sessions in database insertion order (unpredictable)
- Frontend expects newest sessions first, but may get oldest first
- Poor UX: Users see stale sessions at top of list

## User Story

**As a** medical student viewing my EMR session history,
**I want** to see my most recent sessions first,
**So that** I can quickly resume my latest practice session.

**Acceptance Criteria**:
- [ ] GET `/emr/sessions` accepts `sort_by` query parameter
- [ ] GET `/emr/sessions` accepts `sort_order` query parameter (asc/desc)
- [ ] Default sorting: created_at descending (newest first)
- [ ] Invalid sort_by values fall back to default (no 500 error)
- [ ] Invalid sort_order values default to "desc"
- [ ] Frontend receives sessions sorted correctly
- [ ] All 3 tests pass (100% pass rate)

## Success Metrics

| Metric | Current | Target | Validation |
|--------|---------|--------|------------|
| Sort parameters supported | NO | YES | Test 1-2 pass |
| Default sort order | UNDEFINED | created_at DESC | API response |
| Invalid params handled | UNTESTED | Graceful fallback | Test 3 passes |
| Test pass rate | N/A | 100% (3/3 tests) | pytest exit code 0 |
| Frontend dashboard order | Random | Newest first | Manual test |

---

# A - ARCHITECTURE (Current vs Target)

## Current Architecture (BROKEN)

```
backend/src/api/v1/emr_sessions.py (LEGACY - to be deleted in Phase 2)
├── @router.get("", ...)
├── async def list_sessions(
│       is_active: Optional[bool],
│       specialty: Optional[str],
│       limit: int = 20,
│       offset: int = 0,
│       # ❌ MISSING: sort_by
│       # ❌ MISSING: sort_order
│   )
└── SessionService.list_sessions(db, user_id, is_active, specialty, limit, offset)
    └── ❌ No ORDER BY clause (undefined sort order)

frontend/src/hooks/useEMRDashboardData.ts:136-138
└── Passes sort_by='created_at', sort_order='desc' ← ❌ IGNORED
```

**Problem**: Frontend passes sort parameters but backend doesn't accept them!

## Target Architecture (FIXED)

```
backend/src/api/v1/emr/sessions.py (NEW - Phase 2)
├── @router.get("", ...)
├── async def list_sessions(
│       is_active: Optional[bool],
│       specialty: Optional[str],
│       limit: int = 20,
│       offset: int = 0,
│       sort_by: str = "created_at",       ✅ ADDED
│       sort_order: str = "desc",          ✅ ADDED
│   )
└── SessionService.list_sessions(db, user_id, ..., sort_by, sort_order)
    └── SQL Query with ORDER BY {sort_by} {sort_order} ✅ ADDED

Allowed Values:
- sort_by: "created_at", "submitted_at", "validation_score"
- sort_order: "asc", "desc"
```

**Benefits**:
- ✅ Frontend parameters now accepted
- ✅ Predictable sorting (newest first by default)
- ✅ Better UX (most recent sessions at top)

## SQL Query Changes

### Before (No Sorting):
```sql
SELECT * FROM emr_sessions
WHERE user_id = ?
  AND (submitted_at IS NULL OR submitted_at IS NOT NULL)  -- is_active filter
  AND specialty = ?  -- specialty filter
LIMIT ? OFFSET ?;
-- ❌ No ORDER BY clause
```

### After (With Sorting):
```sql
SELECT * FROM emr_sessions
WHERE user_id = ?
  AND (submitted_at IS NULL OR submitted_at IS NOT NULL)
  AND specialty = ?
ORDER BY {sort_by} {sort_order}  -- ✅ ADDED
LIMIT ? OFFSET ?;
```

**Example**: `ORDER BY started_at DESC` (newest sessions first)

---

# L - LOOP (TDD Workflow)

## Phase 1: RED (Tests Fail) - Write Tests First

**Estimated Time**: 10 minutes

### Actions:
1. Create test file: `backend/tests/test_emr_list_sorting.py`
2. Copy all 3 test functions from T section
3. Run tests:
   ```bash
   cd /home/dev/Development/irStudy/backend
   source venv/bin/activate
   pytest tests/test_emr_list_sorting.py -v
   ```

### Expected Result (RED):
```
FAILED test_list_sessions_sorted_by_created_at_desc - Sessions not sorted (random order)
FAILED test_list_sessions_sorted_by_created_at_asc - Sessions not sorted (random order)
PASSED test_list_sessions_invalid_sort_params_fallback - Returns 200 (may pass)
```

**Validation**: Tests 1-2 MUST fail (RED phase confirmed).

---

## Phase 2: GREEN (Tests Pass) - Add Sort Parameters

**Estimated Time**: 15 minutes

### Actions:
1. **Update router endpoint**:
   ```python
   # backend/src/api/v1/emr_sessions.py (or emr/sessions.py after Phase 2)

   @router.get("", response_model=SessionListResponse, ...)
   async def list_sessions(
       is_active: Optional[bool] = Query(None, ...),
       specialty: Optional[str] = Query(None, ...),
       limit: int = Query(20, le=100, ...),
       offset: int = Query(0, ge=0, ...),
       sort_by: str = Query("created_at", description="Sort field (created_at, submitted_at, validation_score)"),  # ✅ ADDED
       sort_order: str = Query("desc", description="Sort order (asc, desc)"),  # ✅ ADDED
       db: Session = Depends(get_db),
       current_user: User = Depends(get_current_active_user),
   ):
       # Validate sort_by (prevent SQL injection)
       valid_sort_fields = ["created_at", "submitted_at", "validation_score", "started_at"]
       if sort_by not in valid_sort_fields:
           sort_by = "created_at"  # Fallback to default

       # Validate sort_order
       if sort_order not in ["asc", "desc"]:
           sort_order = "desc"  # Fallback to default

       result = SessionService.list_sessions(
           db,
           user_id=current_user.id,
           is_active=is_active,
           specialty=specialty,
           limit=limit,
           offset=offset,
           sort_by=sort_by,      # ✅ PASS TO SERVICE
           sort_order=sort_order # ✅ PASS TO SERVICE
       )
   ```

2. **Update service layer**:
   ```python
   # backend/src/services/emr/session_service.py

   @staticmethod
   def list_sessions(
       db: Session,
       user_id: int,
       is_active: Optional[bool] = None,
       specialty: Optional[str] = None,
       limit: int = 20,
       offset: int = 0,
       sort_by: str = "created_at",      # ✅ ADDED
       sort_order: str = "desc"          # ✅ ADDED
   ) -> dict:
       # Build query
       query = db.query(EMRSession).filter(EMRSession.user_id == user_id)

       # Apply filters (is_active, specialty)
       if is_active is not None:
           if is_active:
               query = query.filter(EMRSession.submitted_at.is_(None))
           else:
               query = query.filter(EMRSession.submitted_at.isnot(None))

       if specialty:
           query = query.filter(EMRSession.specialty == specialty)

       # Apply sorting ✅ ADDED
       sort_column = getattr(EMRSession, sort_by)  # Get column by name
       if sort_order == "asc":
           query = query.order_by(sort_column.asc())
       else:
           query = query.order_by(sort_column.desc())

       # Count total (before pagination)
       total_count = query.count()

       # Apply pagination
       sessions = query.offset(offset).limit(limit).all()

       return {
           "sessions": sessions,
           "total_count": total_count,
           "limit": limit,
           "offset": offset
       }
   ```

3. **Run tests again**:
   ```bash
   pytest tests/test_emr_list_sorting.py -v
   ```

### Expected Result (GREEN):
```
PASSED test_list_sessions_sorted_by_created_at_desc
PASSED test_list_sessions_sorted_by_created_at_asc
PASSED test_list_sessions_invalid_sort_params_fallback

========================= 3 passed in 3.45s =========================
```

**Validation**: ALL 3 tests MUST pass (GREEN phase confirmed).

---

## Phase 3: REFACTOR (Cleanup) - Verify No Regressions

**Estimated Time**: 5 minutes

### Actions:
1. **Run full backend test suite**:
   ```bash
   pytest --cov=src --cov-report=term-missing -v
   ```

2. **Test API manually**:
   ```bash
   TOKEN=$(curl -X POST http://localhost:8001/api/v1/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email":"student@test.com","password":"Student123!@#"}' \
     | jq -r '.access_token')

   # Test 1: Sort by created_at descending (default)
   curl -H "Authorization: Bearer $TOKEN" \
     "http://localhost:8001/api/v1/emr/sessions?sort_by=created_at&sort_order=desc&limit=5" \
     | jq '.sessions[] | .started_at'

   # Test 2: Sort by created_at ascending
   curl -H "Authorization: Bearer $TOKEN" \
     "http://localhost:8001/api/v1/emr/sessions?sort_by=created_at&sort_order=asc&limit=5" \
     | jq '.sessions[] | .started_at'

   # Test 3: Invalid sort_by (should fallback)
   curl -H "Authorization: Bearer $TOKEN" \
     "http://localhost:8001/api/v1/emr/sessions?sort_by=invalid_field&sort_order=desc&limit=5"
   # Expected: 200 OK (not 500)
   ```

3. **Test frontend integration**:
   ```bash
   cd /home/dev/Development/irStudy/frontend
   npm run dev

   # Open http://localhost:5173/dashboard
   # Check: Recent sessions list shows newest sessions first
   ```

### Expected Result (REFACTOR):
```
✅ All tests pass (100% pass rate)
✅ API returns sorted sessions
✅ Frontend dashboard shows newest sessions first
✅ No 500 errors on invalid parameters
```

**Validation Checklist**:
- [ ] All 3 sorting tests pass
- [ ] Full test suite passes (100% pass rate)
- [ ] API responses are sorted correctly
- [ ] Frontend dashboard displays sessions in correct order
- [ ] Invalid parameters handled gracefully

---

# P - PLAN (Implementation Steps)

## File 1: Create Test File

**Path**: `backend/tests/test_emr_list_sorting.py`

**Action**: Create test suite (3 tests from T section)

```python
"""
EMR List Sorting Tests

PURPOSE: Verify list_sessions endpoint supports sort_by and sort_order parameters

TESTS (3 total):
1. test_list_sessions_sorted_by_created_at_desc
2. test_list_sessions_sorted_by_created_at_asc
3. test_list_sessions_invalid_sort_params_fallback

TDD WORKFLOW: RED → GREEN → REFACTOR
Expected: Tests 1-2 fail initially (RED phase)
After adding sort parameters: All 3 tests pass (GREEN phase)
"""

import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.db.models import User, EMRSession, MockPatient
from src.auth.security import create_access_token
from datetime import datetime, timedelta
from uuid import uuid4

client = TestClient(app)

# [Include all 3 test functions from T section above]
# Test 1: test_list_sessions_sorted_by_created_at_desc
# Test 2: test_list_sessions_sorted_by_created_at_asc
# Test 3: test_list_sessions_invalid_sort_params_fallback
```

---

## File 2: Update Router - Add Sort Parameters

**Path**: `backend/src/api/v1/emr_sessions.py` (or `emr/sessions.py` after Phase 2)

**Action**: Add `sort_by` and `sort_order` query parameters

**BEFORE** (lines 463-470 approximate):
```python
@router.get("", response_model=SessionListResponse, ...)
async def list_sessions(
    is_active: Optional[bool] = Query(None, ...),
    specialty: Optional[str] = Query(None, ...),
    limit: int = Query(20, le=100, ...),
    offset: int = Query(0, ge=0, ...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
```

**AFTER**:
```python
@router.get("", response_model=SessionListResponse, ...)
async def list_sessions(
    is_active: Optional[bool] = Query(None, description="Filter by completion status"),
    specialty: Optional[str] = Query(None, description="Filter by specialty"),
    limit: int = Query(20, le=100, description="Page size"),
    offset: int = Query(0, ge=0, description="Page offset"),
    sort_by: str = Query("started_at", description="Sort field (started_at, submitted_at, validation_score)"),  # ✅ ADDED
    sort_order: str = Query("desc", description="Sort order (asc, desc)"),  # ✅ ADDED
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    List sessions with pagination, filtering, and sorting.

    Query Parameters:
    - is_active: Filter by completion status
    - specialty: Filter by patient specialty
    - limit: Page size (max 100)
    - offset: Page offset
    - sort_by: Sort field (started_at, submitted_at, validation_score)
    - sort_order: Sort order (asc, desc)
    """
    # Validate sort_by (prevent SQL injection)
    valid_sort_fields = ["started_at", "submitted_at", "validation_score", "created_at"]
    if sort_by not in valid_sort_fields:
        logger.warning(f"Invalid sort_by parameter: {sort_by}, falling back to 'started_at'")
        sort_by = "started_at"

    # Validate sort_order
    if sort_order not in ["asc", "desc"]:
        logger.warning(f"Invalid sort_order parameter: {sort_order}, falling back to 'desc'")
        sort_order = "desc"

    try:
        result = SessionService.list_sessions(
            db,
            user_id=current_user.id,
            is_active=is_active,
            specialty=specialty,
            limit=limit,
            offset=offset,
            sort_by=sort_by,      # ✅ PASS TO SERVICE
            sort_order=sort_order # ✅ PASS TO SERVICE
        )

        # Convert to response format
        sessions = [
            SessionSummary(
                session_id=str(s["id"]),
                patient_name=s.get("patient_name", "Unknown"),
                patient_specialty=s.get("specialty", "Unknown"),
                emr_system="epic",  # TODO: Add to table
                is_active=s["submitted_at"] is None,
                started_at=s["started_at"],
                completed_at=s.get("submitted_at"),
                validation_score=s.get("validation_score")
            )
            for s in result["sessions"]
        ]

        return SessionListResponse(
            sessions=sessions,
            total_count=result["total_count"],
            limit=result["limit"],
            offset=result["offset"]
        )

    except Exception as e:
        logger.error(f"Error listing sessions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list sessions"
        )
```

**Changes**:
- Add `sort_by` parameter with Query validator
- Add `sort_order` parameter with Query validator
- Add validation logic (prevent SQL injection)
- Pass both parameters to SessionService.list_sessions()

---

## File 3: Update Service Layer - Add Sorting Logic

**Path**: `backend/src/services/emr/session_service.py`

**Action**: Add sorting support to `list_sessions()` method

**BEFORE** (find existing list_sessions method):
```python
@staticmethod
def list_sessions(
    db: Session,
    user_id: int,
    is_active: Optional[bool] = None,
    specialty: Optional[str] = None,
    limit: int = 20,
    offset: int = 0
) -> dict:
    # Build query
    query = db.query(EMRSession).filter(EMRSession.user_id == user_id)

    # Apply filters
    if is_active is not None:
        if is_active:
            query = query.filter(EMRSession.submitted_at.is_(None))
        else:
            query = query.filter(EMRSession.submitted_at.isnot(None))

    if specialty:
        query = query.filter(EMRSession.specialty == specialty)

    # Count total
    total_count = query.count()

    # Apply pagination
    sessions = query.offset(offset).limit(limit).all()

    return {
        "sessions": [session_to_dict(s) for s in sessions],
        "total_count": total_count,
        "limit": limit,
        "offset": offset
    }
```

**AFTER**:
```python
@staticmethod
def list_sessions(
    db: Session,
    user_id: int,
    is_active: Optional[bool] = None,
    specialty: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    sort_by: str = "started_at",      # ✅ ADDED
    sort_order: str = "desc"          # ✅ ADDED
) -> dict:
    """
    List EMR sessions with filtering, sorting, and pagination.

    Args:
        db: Database session
        user_id: User ID
        is_active: Filter by completion status
        specialty: Filter by patient specialty
        limit: Page size
        offset: Page offset
        sort_by: Sort field (started_at, submitted_at, validation_score)
        sort_order: Sort order (asc, desc)

    Returns:
        dict: {"sessions": [...], "total_count": int, "limit": int, "offset": int}
    """
    # Build query
    query = db.query(EMRSession).filter(EMRSession.user_id == user_id)

    # Apply filters (is_active, specialty)
    if is_active is not None:
        if is_active:
            query = query.filter(EMRSession.submitted_at.is_(None))
        else:
            query = query.filter(EMRSession.submitted_at.isnot(None))

    if specialty:
        query = query.filter(EMRSession.specialty == specialty)

    # Apply sorting ✅ ADDED
    try:
        sort_column = getattr(EMRSession, sort_by)  # Get column by name
        if sort_order == "asc":
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())
    except AttributeError:
        # Invalid sort_by field, fallback to default
        logger.warning(f"Invalid sort field: {sort_by}, using started_at instead")
        query = query.order_by(EMRSession.started_at.desc())

    # Count total (before pagination)
    total_count = query.count()

    # Apply pagination
    sessions = query.offset(offset).limit(limit).all()

    return {
        "sessions": [session_to_dict(s) for s in sessions],
        "total_count": total_count,
        "limit": limit,
        "offset": offset
    }
```

**Changes**:
- Add `sort_by` and `sort_order` parameters
- Get sort column dynamically using `getattr()`
- Apply ORDER BY clause before pagination
- Handle invalid sort_by gracefully (fallback to default)

---

# H - HANDOFF (Validation & Rollback)

## Pre-Implementation Checklist

- [ ] **Read PROJECT_CONSTRAINTS.md** (All agents MUST read before starting)
- [ ] **Verify Phase 1-4 complete**: Models in `models.py`, single router, dashboard endpoints, patient aliases implemented
- [ ] **Understand sorting requirement**: Frontend passes sort_by/sort_order but backend ignores them

## Implementation Checklist

### Phase 1: RED (Write Tests)
- [ ] Create `backend/tests/test_emr_list_sorting.py`
- [ ] Copy all 3 test functions from T section
- [ ] Run tests: `pytest tests/test_emr_list_sorting.py -v`
- [ ] **Verify RED**: Tests 1-2 MUST fail initially
- [ ] Commit tests: `git add tests/test_emr_list_sorting.py && git commit -m "test: Add EMR list sorting tests (TDD RED)"`

### Phase 2: GREEN (Add Sort Parameters)
- [ ] Open `backend/src/api/v1/emr_sessions.py` (or `emr/sessions.py` after Phase 2)
- [ ] Add `sort_by` query parameter with Query validator
- [ ] Add `sort_order` query parameter with Query validator
- [ ] Add validation logic (check valid_sort_fields list)
- [ ] Open `backend/src/services/emr/session_service.py`
- [ ] Add `sort_by` and `sort_order` parameters to `list_sessions()` method
- [ ] Add ORDER BY logic using `getattr()` and `order_by()`
- [ ] Run tests: `pytest tests/test_emr_list_sorting.py -v`
- [ ] **Verify GREEN**: ALL 3 tests MUST pass
- [ ] Commit changes: `git add . && git commit -m "feat: Add sort parameters to EMR list endpoint (Phase 5)"`

### Phase 3: REFACTOR (Verify No Regressions)
- [ ] Run full backend test suite: `pytest --cov=src --cov-report=term-missing`
- [ ] Verify 100% test pass rate
- [ ] Test API manually (3 curl commands from L section)
- [ ] Verify sorting works correctly
- [ ] Test frontend dashboard (newest sessions appear first)

## Quality Gates

| Gate | Requirement | Validation Command | Expected Result |
|------|-------------|-------------------|-----------------|
| **1. Tests Pass** | 100% pass rate (3/3 tests) | `pytest tests/test_emr_list_sorting.py -v` | `3 passed in X.XXs` |
| **2. No Regressions** | Full test suite passes | `pytest --cov=src` | `100% pass rate` |
| **3. Sorting Works** | Sessions sorted correctly | `curl ... | jq '.sessions[] | .started_at'` | Timestamps in order |
| **4. No SQL Injection** | Invalid sort_by handled | `curl ...?sort_by=DROP%20TABLE` | 200 OK (not 500) |
| **5. Frontend Works** | Dashboard shows newest first | Open http://localhost:5173/dashboard | Correct order |

**ALL quality gates MUST pass before marking Phase 5 complete.**

## Rollback Plan

If implementation fails quality gates, revert changes:

```bash
# Rollback git commit
cd /home/dev/Development/irStudy
git log --oneline -5
git revert <commit-hash>

# Or restore files manually
git checkout HEAD~1 backend/src/api/v1/emr_sessions.py
git checkout HEAD~1 backend/src/services/emr/session_service.py

# Restart backend
cd backend
source venv/bin/activate
set -a && source .env && set +a
uvicorn src.main:app --reload --port 8001
```

## Success Criteria

Phase 5 is COMPLETE when:
- ✅ All 3 sorting tests pass (100% pass rate)
- ✅ Full backend test suite passes (no regressions)
- ✅ List endpoint accepts sort_by and sort_order parameters
- ✅ Sessions returned in correct sorted order
- ✅ Invalid parameters handled gracefully (no 500 errors)
- ✅ Frontend dashboard shows newest sessions first
- ✅ Code committed to git with descriptive message

## Next Steps

After Phase 5 completion:
1. **Mark ALL PRDs DONE** in todo list (Phases 1-5 complete)
2. **Update PROJECT_CONSTRAINTS.md**: Document all 5 phases completed
3. **Prepare for Ralph execution**: All PRDs ready for implementation
4. **Run E2E tests**: Verify frontend dashboard works end-to-end

---

**END OF PRD-EMR-005-QUERY-PARAMS**

---

# Summary: All 5 PRDs Complete

**Phase 1**: PRD-EMR-001-MODELS-MIGRATION (Move models to models.py)
**Phase 2**: PRD-EMR-002-CONSOLIDATE-ROUTERS (Remove duplicate router)
**Phase 3**: PRD-EMR-003-DASHBOARD-ENDPOINTS (Implement 3 missing endpoints)
**Phase 4**: PRD-EMR-004-PATIENT-ALIAS (Add name/full_name field aliases)
**Phase 5**: PRD-EMR-005-QUERY-PARAMS (Add sort parameters to list endpoint)

**Total Estimated Time**: 8.5-10 hours
**Total Tests**: 33 tests (12 + 6 + 9 + 3 + 3)
**Format**: T-RALPH v2.1 (Test-First Development)
**Agent**: python-backend-developer

**All PRDs are ready for implementation via Ralph loop!**
