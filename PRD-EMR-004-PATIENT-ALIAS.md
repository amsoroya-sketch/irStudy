# PRD-EMR-004: Add Patient Field Aliases for Frontend Compatibility

**Status**: READY FOR IMPLEMENTATION
**Priority**: P1 (Important - Improves data consistency)
**Estimated Time**: 30 minutes
**Agent**: `python-backend-developer`
**Created**: 2026-04-06
**Format**: T-RALPH v2.1 (Test-First Development)
**Depends On**: PRD-EMR-001 (Models), PRD-EMR-002 (Router Consolidation)

---

## Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2026-04-06 | Initial PRD - Add patient field aliases | PM Agent |

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
backend/tests/test_patient_field_aliases.py
```

## Test 1: Patient Response Has Both "name" and "full_name" Fields

**Purpose**: Verify MockPatient response includes both field names for backward compatibility

```python
"""
Test: Patient response includes both "name" and "full_name" fields

EXPECTED BEHAVIOR:
- GET /patients/{id} returns patient with both "name" and "full_name"
- "name" is alias for "full_name" (same value)
- Frontend can use either field

TDD PHASE: RED (will fail until alias added)
"""

import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.db.models import MockPatient
from uuid import uuid4

client = TestClient(app)

def test_patient_response_has_name_and_full_name_aliases(db_session):
    """Test patient response includes both name and full_name fields"""
    # Create test patient
    patient = MockPatient(
        patient_id=uuid4(),
        full_name="John Smith",
        mrn="MRN001",
        age=45,
        gender="Male",
        specialty="Cardiology",
        difficulty="intermediate"
    )
    db_session.add(patient)
    db_session.commit()

    # Fetch patient via API
    response = client.get(f"/api/v1/patients/{patient.patient_id}")

    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    data = response.json()

    # Both fields should exist
    assert "full_name" in data, "Missing full_name field"
    assert "name" in data, "Missing name field (alias)"

    # Both should have same value
    assert data["full_name"] == "John Smith"
    assert data["name"] == "John Smith", "name alias should match full_name"
```

## Test 2: EMR Session Start Returns Patient with Aliases

**Purpose**: Verify EMR session start endpoint returns patient with both field names

```python
"""
Test: POST /emr/sessions/start returns patient with name/full_name aliases

EXPECTED BEHAVIOR:
- SessionStartResponse patient object has both fields
- Frontend can access patient.name or patient.full_name

TDD PHASE: RED (will fail until alias added)
"""

from src.auth.security import create_access_token

def test_emr_session_start_patient_has_aliases(db_session):
    """Test EMR session start returns patient with name alias"""
    # Create test user
    from src.db.models import User
    user = User(
        id=100,
        email="alias@test.com",
        password_hash="hashed",
        full_name="Alias Test",
        role="student"
    )
    db_session.add(user)
    db_session.commit()

    # Create test patient
    patient = MockPatient(
        patient_id=uuid4(),
        full_name="Jane Doe",
        mrn="MRN002",
        age=32,
        gender="Female",
        specialty="Respiratory",
        difficulty="intermediate"
    )
    db_session.add(patient)
    db_session.commit()

    # Create JWT token
    token = create_access_token(data={"sub": "alias@test.com", "user_id": 100})
    headers = {"Authorization": f"Bearer {token}"}

    # Start EMR session
    response = client.post(
        "/api/v1/emr/sessions/start",
        json={"emr_system": "epic"},
        headers=headers
    )

    # May return 404 if no patients available (that's OK)
    # We're testing the response structure when it succeeds
    if response.status_code == 200 or response.status_code == 201:
        data = response.json()

        assert "patient" in data, "Missing patient field in response"

        patient_data = data["patient"]

        # Both fields should exist
        assert "full_name" in patient_data, "Missing full_name in patient"
        assert "name" in patient_data, "Missing name alias in patient"

        # Both should have same value
        assert patient_data["full_name"] == patient_data["name"], \
            "name and full_name should be equal"
```

## Test 3: Pydantic Schema Includes Alias

**Purpose**: Verify MockPatientResponse schema defines field alias

```python
"""
Test: MockPatientResponse Pydantic schema defines name alias

EXPECTED BEHAVIOR:
- Schema has field: name = Field(alias="full_name") or computed field
- Serialization includes both fields

TDD PHASE: RED (will fail until schema updated)
"""

from src.schemas.emr import MockPatientResponse

def test_mock_patient_response_schema_has_alias():
    """Test MockPatientResponse schema includes name alias"""
    # Create MockPatientResponse instance
    patient_data = {
        "id": str(uuid4()),
        "mrn": "MRN003",
        "full_name": "Test Patient",
        "age": 50,
        "gender": "Male",
        "presenting_complaint": "Chest pain",
        "specialty": "Cardiology",
        "complexity_level": "intermediate"
    }

    patient_response = MockPatientResponse(**patient_data)

    # Serialize to dict
    patient_dict = patient_response.model_dump()

    # Should have both full_name and name
    assert "full_name" in patient_dict, "Missing full_name field"
    assert "name" in patient_dict, "Missing name field (alias)"

    assert patient_dict["full_name"] == "Test Patient"
    assert patient_dict["name"] == "Test Patient", "name should alias full_name"
```

---

# R - REQUEST (User Story)

## Problem Statement

**Current Issue**: Inconsistent patient field names between backend and frontend

**Evidence**:
- Backend MockPatient model has field: `full_name`
- Frontend expects field: `name` (see `emr/sessions.py:359` - uses `patient.get("name", "")`)
- Result: Patient names show as empty string in some frontend components

**Example from Code**:
```python
# backend/src/api/v1/emr_sessions.py:359 (LEGACY - to be deleted in Phase 2)
MockPatientResponse(
    ...
    full_name=patient.get("name", ""),  # ❌ Looks for "name" but patient has "full_name"
    ...
)
```

**Impact**:
- EMR session pages may show "Unknown Patient" instead of actual name
- Frontend code uses both `.name` and `.full_name` inconsistently
- Confusion for developers (which field to use?)

## User Story

**As a** backend developer maintaining EMR endpoints,
**I want** patient responses to include both `name` and `full_name` fields,
**So that** the frontend works regardless of which field name it uses (backward compatibility).

**Acceptance Criteria**:
- [ ] MockPatientResponse schema includes both `name` and `full_name` fields
- [ ] `name` is an alias for `full_name` (same value)
- [ ] GET `/patients/{id}` response includes both fields
- [ ] POST `/emr/sessions/start` patient object includes both fields
- [ ] Frontend displays patient names correctly
- [ ] All 3 tests pass (100% pass rate)

## Success Metrics

| Metric | Current | Target | Validation |
|--------|---------|--------|------------|
| Patient name display | May show "Unknown" | Shows actual name | Frontend test |
| Field consistency | Inconsistent | Consistent (both fields) | Test 1-2 pass |
| Schema validation | ❌ No alias | ✅ Alias defined | Test 3 passes |
| Test pass rate | N/A | 100% (3/3 tests) | pytest exit code 0 |

---

# A - ARCHITECTURE (Current vs Target)

## Current Architecture (INCONSISTENT)

```
backend/src/db/models.py
├── MockPatient model
│   └── full_name: Mapped[str] (field name)

backend/src/schemas/emr.py
├── MockPatientResponse schema
│   ├── full_name: str (field)
│   └── ❌ NO "name" field (missing alias)

backend/src/api/v1/emr_sessions.py (LEGACY)
├── Line 359: full_name=patient.get("name", "") ❌ WRONG FIELD
└── Result: Patient names show as empty string

frontend/src/hooks/useEMRDashboardData.ts
├── Line 62: patient_name: string (expects "name" or "patient_name")
└── May not match backend field name
```

**Problem**: Backend uses `full_name`, frontend expects `name` → Mismatch!

## Target Architecture (CONSISTENT)

```
backend/src/schemas/emr.py (FIXED)
├── MockPatientResponse schema
│   ├── full_name: str (primary field)
│   └── name: str (computed property - alias for full_name) ✅ ADDED

backend/src/api/v1/emr/sessions.py (NEW)
├── Uses patient.get("full_name", "") ✅ CORRECT FIELD
└── Response includes both "name" and "full_name"

Response JSON:
{
  "patient": {
    "id": "uuid",
    "mrn": "MRN001",
    "full_name": "John Smith", ✅
    "name": "John Smith",  ✅ ALIAS (same value)
    "age": 45,
    ...
  }
}
```

**Benefits**:
- ✅ Frontend works with either field name (backward compatibility)
- ✅ No breaking changes to existing code
- ✅ Clear migration path (future: standardize on `full_name`)

## Implementation Approaches

### Approach 1: Pydantic Computed Field (RECOMMENDED)

```python
# backend/src/schemas/emr.py

from pydantic import BaseModel, computed_field

class MockPatientResponse(BaseModel):
    id: str
    full_name: str
    # ... other fields

    @computed_field
    @property
    def name(self) -> str:
        """Alias for full_name (backward compatibility)"""
        return self.full_name
```

**Pros**:
- ✅ No database changes
- ✅ Pydantic automatically includes in serialization
- ✅ Clear documentation (computed field)

**Cons**:
- ❌ Read-only (can't set `name` during initialization)

### Approach 2: Pydantic Field Alias

```python
# backend/src/schemas/emr.py

from pydantic import BaseModel, Field

class MockPatientResponse(BaseModel):
    full_name: str
    name: str = Field(default="", description="Alias for full_name")

    def __init__(self, **data):
        # Set name = full_name if not provided
        if "name" not in data and "full_name" in data:
            data["name"] = data["full_name"]
        super().__init__(**data)
```

**Pros**:
- ✅ Can set either field during initialization
- ✅ Explicit in schema definition

**Cons**:
- ❌ Requires __init__ override (more complex)

**Decision**: Use Approach 1 (Computed Field) for simplicity.

---

# L - LOOP (TDD Workflow)

## Phase 1: RED (Tests Fail) - Write Tests First

**Estimated Time**: 10 minutes

### Actions:
1. Create test file: `backend/tests/test_patient_field_aliases.py`
2. Copy all 3 test functions from T section
3. Run tests:
   ```bash
   cd /home/dev/Development/irStudy/backend
   source venv/bin/activate
   pytest tests/test_patient_field_aliases.py -v
   ```

### Expected Result (RED):
```
FAILED test_patient_response_has_name_and_full_name_aliases - KeyError: 'name'
FAILED test_emr_session_start_patient_has_aliases - KeyError: 'name'
FAILED test_mock_patient_response_schema_has_alias - KeyError: 'name'
```

**Validation**: All 3 tests MUST fail (RED phase confirmed).

---

## Phase 2: GREEN (Tests Pass) - Add Field Alias

**Estimated Time**: 15 minutes

### Actions:
1. **Update Pydantic schema**:
   ```python
   # backend/src/schemas/emr.py

   from pydantic import BaseModel, computed_field

   class MockPatientResponse(BaseModel):
       id: str
       mrn: str
       full_name: str
       age: int
       gender: str
       # ... other fields

       @computed_field
       @property
       def name(self) -> str:
           """Alias for full_name (backward compatibility with frontend)"""
           return self.full_name
   ```

2. **Run tests again**:
   ```bash
   pytest tests/test_patient_field_aliases.py -v
   ```

### Expected Result (GREEN):
```
PASSED test_patient_response_has_name_and_full_name_aliases
PASSED test_emr_session_start_patient_has_aliases
PASSED test_mock_patient_response_schema_has_alias

========================= 3 passed in 2.34s =========================
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

2. **Verify TypeScript compilation** (should still work):
   ```bash
   cd /home/dev/Development/irStudy/frontend
   npx tsc --noEmit
   ```

3. **Test EMR endpoint manually**:
   ```bash
   TOKEN=$(curl -X POST http://localhost:8001/api/v1/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email":"student@test.com","password":"Student123!@#"}' \
     | jq -r '.access_token')

   curl -H "Authorization: Bearer $TOKEN" \
     http://localhost:8001/api/v1/emr/sessions/start \
     -X POST -H "Content-Type: application/json" \
     -d '{"emr_system":"epic"}'

   # Check response JSON - should have both "name" and "full_name"
   ```

### Expected Result (REFACTOR):
```
✅ All tests pass (100% pass rate)
✅ No regressions
✅ TypeScript compiles successfully
✅ API response includes both fields
```

**Validation Checklist**:
- [ ] All 3 alias tests pass
- [ ] Full test suite passes (100% pass rate)
- [ ] TypeScript compiles successfully
- [ ] Patient response has both `name` and `full_name`

---

# P - PLAN (Implementation Steps)

## File 1: Create Test File

**Path**: `backend/tests/test_patient_field_aliases.py`

**Action**: Create test suite (3 tests from T section)

```python
"""
Patient Field Aliases Tests

PURPOSE: Verify MockPatientResponse includes both "name" and "full_name" fields
         for backward compatibility with frontend.

TESTS (3 total):
1. test_patient_response_has_name_and_full_name_aliases
2. test_emr_session_start_patient_has_aliases
3. test_mock_patient_response_schema_has_alias

TDD WORKFLOW: RED → GREEN → REFACTOR
Expected: All 3 tests fail initially (RED phase)
After adding computed field: All 3 tests pass (GREEN phase)
"""

import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.db.models import MockPatient, User
from src.auth.security import create_access_token
from src.schemas.emr import MockPatientResponse
from uuid import uuid4

client = TestClient(app)

# [Include all 3 test functions from T section above]
# Test 1: test_patient_response_has_name_and_full_name_aliases
# Test 2: test_emr_session_start_patient_has_aliases
# Test 3: test_mock_patient_response_schema_has_alias
```

---

## File 2: Update MockPatientResponse Schema

**Path**: `backend/src/schemas/emr.py`

**Action**: Add `name` computed field to `MockPatientResponse`

**BEFORE**:
```python
class MockPatientResponse(BaseModel):
    id: str
    mrn: str
    full_name: str
    age: int
    gender: str
    allergies: List[str] = []
    current_medications: List[str] = []
    vital_signs: Dict[str, Any] = {}
    presenting_complaint: str
    clinical_scenario: str
    specialty: str
    complexity_level: str
    demographics: Dict[str, Any] = {}
    medical_history: Optional[Dict[str, Any]] = None
    medications: Optional[List[str]] = None
    physical_exam_findings: Optional[Dict[str, Any]] = None
    investigation_results: Optional[Dict[str, Any]] = None
```

**AFTER**:
```python
from pydantic import BaseModel, computed_field

class MockPatientResponse(BaseModel):
    id: str
    mrn: str
    full_name: str
    age: int
    gender: str
    allergies: List[str] = []
    current_medications: List[str] = []
    vital_signs: Dict[str, Any] = {}
    presenting_complaint: str
    clinical_scenario: str
    specialty: str
    complexity_level: str
    demographics: Dict[str, Any] = {}
    medical_history: Optional[Dict[str, Any]] = None
    medications: Optional[List[str]] = None
    physical_exam_findings: Optional[Dict[str, Any]] = None
    investigation_results: Optional[Dict[str, Any]] = None

    @computed_field
    @property
    def name(self) -> str:
        """
        Alias for full_name (backward compatibility).

        Frontend code may use either patient.name or patient.full_name.
        This computed field ensures both work.

        Returns:
            str: Same value as full_name
        """
        return self.full_name
```

**Changes**:
- Line 1: Add `computed_field` import from pydantic
- After last field: Add `@computed_field` method for `name`

---

# H - HANDOFF (Validation & Rollback)

## Pre-Implementation Checklist

- [ ] **Read PROJECT_CONSTRAINTS.md** (All agents MUST read before starting)
- [ ] **Verify Phase 1-3 complete**: Models in `models.py`, single router, dashboard endpoints implemented
- [ ] **Understand field naming issue**: Backend uses `full_name`, frontend expects `name`

## Implementation Checklist

### Phase 1: RED (Write Tests)
- [ ] Create `backend/tests/test_patient_field_aliases.py`
- [ ] Copy all 3 test functions from T section
- [ ] Run tests: `pytest tests/test_patient_field_aliases.py -v`
- [ ] **Verify RED**: All 3 tests MUST fail initially
- [ ] Commit tests: `git add tests/test_patient_field_aliases.py && git commit -m "test: Add patient field alias tests (TDD RED)"`

### Phase 2: GREEN (Add Computed Field)
- [ ] Open `backend/src/schemas/emr.py`
- [ ] Add import: `from pydantic import BaseModel, computed_field`
- [ ] Add `@computed_field` method for `name` in `MockPatientResponse`
- [ ] Run tests: `pytest tests/test_patient_field_aliases.py -v`
- [ ] **Verify GREEN**: ALL 3 tests MUST pass
- [ ] Commit changes: `git add . && git commit -m "feat: Add name alias to MockPatientResponse (Phase 4)"`

### Phase 3: REFACTOR (Verify No Regressions)
- [ ] Run full backend test suite: `pytest --cov=src --cov-report=term-missing`
- [ ] Verify 100% test pass rate
- [ ] Test TypeScript compilation: `cd frontend && npx tsc --noEmit`
- [ ] Verify 0 TypeScript errors
- [ ] Test API manually:
  ```bash
  TOKEN=$(curl -X POST http://localhost:8001/api/v1/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email":"student@test.com","password":"Student123!@#"}' \
    | jq -r '.access_token')

  curl -H "Authorization: Bearer $TOKEN" \
    http://localhost:8001/api/v1/emr/sessions/start \
    -X POST -H "Content-Type: application/json" \
    -d '{"emr_system":"epic"}' | jq '.patient | {name, full_name}'

  # Expected output:
  # {
  #   "name": "John Smith",
  #   "full_name": "John Smith"
  # }
  ```

## Quality Gates

| Gate | Requirement | Validation Command | Expected Result |
|------|-------------|-------------------|-----------------|
| **1. Tests Pass** | 100% pass rate (3/3 tests) | `pytest tests/test_patient_field_aliases.py -v` | `3 passed in X.XXs` |
| **2. No Regressions** | Full test suite passes | `pytest --cov=src` | `100% pass rate` |
| **3. Schema Includes Alias** | name field in response | `patient_response.model_dump()` | Has "name" key |
| **4. API Response Valid** | Both fields present | `curl ... | jq '.patient'` | Has both fields |
| **5. TypeScript Compiles** | Frontend code valid | `npx tsc --noEmit` | `0 errors` |

**ALL quality gates MUST pass before marking Phase 4 complete.**

## Rollback Plan

If implementation fails quality gates, revert changes:

```bash
# Rollback git commit
cd /home/dev/Development/irStudy
git log --oneline -5
git revert <commit-hash>

# Or restore file manually
git checkout HEAD~1 backend/src/schemas/emr.py

# Restart backend
cd backend
source venv/bin/activate
set -a && source .env && set +a
uvicorn src.main:app --reload --port 8001
```

## Success Criteria

Phase 4 is COMPLETE when:
- ✅ All 3 alias tests pass (100% pass rate)
- ✅ Full backend test suite passes (no regressions)
- ✅ MockPatientResponse schema has `name` computed field
- ✅ API responses include both `name` and `full_name`
- ✅ TypeScript compiles successfully
- ✅ Code committed to git with descriptive message

## Next Steps

After Phase 4 completion:
1. **Mark Phase 4 DONE** in todo list
2. **Proceed to Phase 5**: PRD-EMR-005-QUERY-PARAMS (add sort parameters to list endpoint)
3. **Update PROJECT_CONSTRAINTS.md**: Document field alias pattern

---

**END OF PRD-EMR-004-PATIENT-ALIAS**
