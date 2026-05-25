# PRD: Mock Exam Test Suite Refactoring

**PRD ID**: PRD-MOCK-EXAM-001
**Created**: 2026-05-23
**Status**: READY FOR IMPLEMENTATION
**Priority**: MEDIUM-HIGH
**Estimated Effort**: 3-4 hours
**Expected Impact**: +25 tests (88.8% → 92.4% pass rate)

---

## 1. Executive Summary

### Objective
Refactor mock exam test suite to use FastAPI dependency overrides instead of `unittest.mock.patch`, fix UUID validation issues, and update Pydantic V2 schemas to achieve 100% test pass rate.

### Success Criteria
- [ ] All 57 mock exam tests passing (32 currently passing, 25 failing)
- [ ] No `unittest.mock` usage (use FastAPI dependency overrides)
- [ ] All UUID fixtures use valid UUID format
- [ ] Pydantic V2 schemas updated (no deprecation warnings)
- [ ] Authentication mocking working correctly
- [ ] Test execution time <30 seconds

### Current Status
- **Total tests**: 57 (32 passing, 25 failing)
- **Pass rate**: 56.1%
- **Main issue**: Authentication mocking doesn't work with FastAPI dependency injection
- **Secondary issues**: UUID validation, Pydantic V2 deprecations

**Test Files**:
- `tests/test_mock_exam/test_api.py` - 13 failing (API endpoints)
- `tests/test_mock_exam/test_orchestration.py` - 12 failing (business logic)
- `tests/test_mock_exam/test_schemas.py` - 0 failing (schemas OK)

---

## 2. Root Cause Analysis

### Issue 1: Authentication Mocking Failure

**Current Approach** (DOESN'T WORK):
```python
@patch("src.api.v1.mock_exams.get_current_active_user")
def test_create_mock_exam_success(mock_get_user, client):
    mock_get_user.return_value = mock_user  # ❌ FastAPI ignores this
    response = client.post("/api/v1/mock-exams")
    assert response.status_code == 401  # ❌ Still unauthorized
```

**Why it fails**:
- FastAPI resolves dependencies at import time
- `unittest.mock.patch` patches the module reference, not the actual dependency
- TestClient makes requests through FastAPI's dependency injection system
- The patched function is never called

**Correct Approach** (WILL WORK):
```python
def test_create_mock_exam_success(client):
    # Override the dependency with a test implementation
    def override_get_user():
        return User(id=1, email="test@test.com", role="student")

    app.dependency_overrides[get_current_active_user] = override_get_user

    response = client.post("/api/v1/mock-exams")
    assert response.status_code == 201  # ✅ Works

    # Cleanup
    app.dependency_overrides.clear()
```

### Issue 2: UUID Validation Errors

**Current Fixtures** (FAIL):
```python
mock_orchestrator.create_exam = AsyncMock(return_value=MockExamCreateResponse(
    exam_id="exam-123",  # ❌ Invalid UUID
    stations=[
        {"station_number": 1, "persona_id": "persona-1"}  # ❌ Invalid UUID
    ]
))
```

**Error**:
```
ValidationError: persona_id must be a valid UUID, got: persona-1
```

**Correct Fixtures** (PASS):
```python
from uuid import uuid4

mock_orchestrator.create_exam = AsyncMock(return_value=MockExamCreateResponse(
    exam_id=str(uuid4()),  # ✅ Valid UUID
    stations=[
        {"station_number": 1, "persona_id": str(uuid4())}  # ✅ Valid UUID
    ]
))
```

### Issue 3: Pydantic V2 Deprecations

**Current Schemas** (DEPRECATED):
```python
class MockExamStatusResponse(BaseModel):
    class Config:  # ❌ Deprecated in Pydantic V2
        json_schema_extra = {"example": {...}}
```

**Updated Schemas** (V2 COMPLIANT):
```python
from pydantic import ConfigDict

class MockExamStatusResponse(BaseModel):
    model_config = ConfigDict(  # ✅ Pydantic V2
        json_schema_extra={"example": {...}}
    )
```

---

## 3. Implementation Plan

### Phase 1: Update Schemas (30 minutes)

**File**: `src/schemas/mock_exam.py`

**Tasks**:
1. Replace `class Config` with `model_config = ConfigDict(...)`
2. Update all 9 schema classes
3. Fix UUID field validators
4. Remove deprecated imports

**Changes** (already partially done from earlier session):
```python
# BEFORE
from pydantic import BaseModel, UUID4

class PersonaInfo(BaseModel):
    persona_id: UUID4  # ❌ UUID4 is deprecated
    class Config:
        json_schema_extra = {"example": {...}}

# AFTER
from pydantic import BaseModel, ConfigDict
from uuid import UUID

class PersonaInfo(BaseModel):
    persona_id: UUID  # ✅ Use standard UUID type
    model_config = ConfigDict(
        json_schema_extra={"example": {...}}
    )
```

**Schemas to Update**:
1. `PersonaInfo`
2. `StationInfo`
3. `MockExamCreateRequest`
4. `MockExamCreateResponse`
5. `MockExamStatusResponse`
6. `StationCompleteRequest`
7. `StationCompleteResponse`
8. `StationResult`
9. `SummaryStatistics`
10. `MockExamResultsResponse`

**Validation**:
```bash
python -c "from src.schemas.mock_exam import *; print('Schemas OK')"
pytest tests/test_mock_exam/test_schemas.py -v  # Should still pass
```

### Phase 2: Refactor Test Fixtures (1 hour)

**File**: `tests/test_mock_exam/conftest.py`

**Tasks**:
1. Create dependency override fixtures
2. Add valid UUID fixtures
3. Create mock orchestrator with proper types
4. Remove all `unittest.mock` imports

**New Fixtures**:

```python
import pytest
from uuid import uuid4
from fastapi.testclient import TestClient
from src.main import app
from src.db.models import User
from src.auth.dependencies import get_current_active_user
from src.services.mock_exam.orchestrator import MockExamOrchestrator

@pytest.fixture
def valid_exam_id():
    """Generate valid exam UUID"""
    return str(uuid4())

@pytest.fixture
def valid_persona_ids():
    """Generate list of valid persona UUIDs"""
    return [str(uuid4()) for _ in range(8)]

@pytest.fixture
def mock_user_fixture():
    """Create mock user for dependency override"""
    return User(
        id=1,
        email="student@test.com",
        role="student",
        is_active=True,
        is_verified=True
    )

@pytest.fixture
def auth_override(mock_user_fixture):
    """Override authentication dependency"""
    def override():
        return mock_user_fixture

    app.dependency_overrides[get_current_active_user] = override
    yield override
    app.dependency_overrides.clear()

@pytest.fixture
def mock_orchestrator_response(valid_exam_id, valid_persona_ids):
    """Mock orchestrator response with valid UUIDs"""
    from src.schemas.mock_exam import MockExamCreateResponse, StationInfo

    return MockExamCreateResponse(
        exam_id=valid_exam_id,
        user_id=1,
        stations=[
            StationInfo(
                station_number=i+1,
                persona_id=persona_id,
                specialty="cardiology",
                difficulty="medium"
            )
            for i, persona_id in enumerate(valid_persona_ids)
        ],
        total_stations=8,
        current_station=1,
        status="in_progress",
        created_at=datetime.now(timezone.utc)
    )

@pytest.fixture
def orchestrator_override(mock_orchestrator_response):
    """Override MockExamOrchestrator dependency"""
    class MockOrchestrator:
        async def create_exam(self, *args, **kwargs):
            return mock_orchestrator_response

        async def get_exam_status(self, *args, **kwargs):
            return mock_orchestrator_response

        async def advance_station(self, *args, **kwargs):
            return mock_orchestrator_response

        async def get_exam_results(self, *args, **kwargs):
            from src.schemas.mock_exam import MockExamResultsResponse
            return MockExamResultsResponse(
                exam_id=mock_orchestrator_response.exam_id,
                user_id=1,
                overall_score=75.0,
                total_stations=8,
                stations_completed=8,
                passed=True,
                summary_statistics={...},
                station_results=[...]
            )

    def override():
        return MockOrchestrator()

    # Find and override the actual dependency
    # (needs to be adjusted based on how orchestrator is injected)
    from src.api.v1 import mock_exams
    original_orchestrator = mock_exams.get_orchestrator

    def get_mock_orchestrator():
        return MockOrchestrator()

    mock_exams.get_orchestrator = get_mock_orchestrator
    yield get_mock_orchestrator
    mock_exams.get_orchestrator = original_orchestrator
```

**Validation**:
```bash
python -c "from tests.test_mock_exam.conftest import *; print('Fixtures OK')"
```

### Phase 3: Refactor API Tests (1 hour)

**File**: `tests/test_mock_exam/test_api.py`

**Current Pattern** (FAILS):
```python
@patch("src.api.v1.mock_exams.MockExamOrchestrator")
@patch("src.api.v1.mock_exams.get_current_active_user")
def test_create_mock_exam_success(mock_get_user, mock_orchestrator_class, client):
    # Complex mocking that doesn't work
    mock_get_user.return_value = mock_user
    mock_orchestrator = MagicMock()
    mock_orchestrator.create_exam = AsyncMock(return_value=...)
    mock_orchestrator_class.return_value = mock_orchestrator

    response = client.post("/api/v1/mock-exams", headers=auth_headers)
    assert response.status_code == 401  # ❌ Still fails
```

**New Pattern** (PASSES):
```python
def test_create_mock_exam_success(
    client,
    auth_override,  # Fixture that overrides auth
    orchestrator_override,  # Fixture that overrides orchestrator
    valid_exam_id
):
    """Test successful exam creation using dependency overrides"""
    response = client.post(
        "/api/v1/mock-exams",
        json={"num_stations": 8, "difficulty": "medium"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["exam_id"] == valid_exam_id
    assert data["total_stations"] == 8
    assert data["status"] == "in_progress"
```

**Tests to Refactor** (13 in test_api.py):
1. `test_create_mock_exam_success`
2. `test_create_mock_exam_insufficient_personas`
3. `test_get_exam_status_success`
4. `test_get_exam_status_not_found`
5. `test_get_exam_status_unauthorized`
6. `test_complete_station_success`
7. `test_complete_station_exam_complete`
8. `test_complete_station_invalid_score`
9. `test_complete_station_missing_body`
10. `test_get_exam_results_success`
11. `test_get_exam_results_not_completed`
12. `test_invalid_exam_id_format`
13. `test_invalid_station_number`

**Pattern for Each Test**:
1. Remove all `@patch` decorators
2. Add `auth_override` and `orchestrator_override` fixtures
3. Update assertions to expect 200/201 instead of 401
4. Use valid UUIDs from fixtures

### Phase 4: Refactor Orchestration Tests (1 hour)

**File**: `tests/test_mock_exam/test_orchestration.py`

**Current Issues**:
- Same auth mocking problems
- UUID validation errors
- AsyncMock complexity

**New Approach**:
```python
def test_create_exam_success(
    db,  # Database session from conftest
    test_user,  # User from conftest
    valid_persona_ids  # Valid UUIDs from conftest
):
    """Test exam creation with real database"""
    from src.services.mock_exam.orchestrator import MockExamOrchestrator

    # Use real orchestrator with test database
    orchestrator = MockExamOrchestrator(db)

    # Create exam
    result = await orchestrator.create_exam(
        user_id=test_user.id,
        num_stations=8,
        difficulty="medium"
    )

    # Assertions
    assert result.exam_id is not None
    assert result.total_stations == 8
    assert result.status == "in_progress"
    assert len(result.stations) == 8

    # Verify database persistence
    from src.db.models import MockExam
    db_exam = db.query(MockExam).filter_by(id=result.exam_id).first()
    assert db_exam is not None
    assert db_exam.user_id == test_user.id
```

**Tests to Refactor** (12 in test_orchestration.py):
1. `test_auto_select_personas_insufficient_personas`
2. `test_create_exam_success`
3. `test_get_exam_status_in_progress`
4. `test_get_exam_status_unauthorized`
5. `test_advance_station_success`
6. `test_advance_station_fail`
7. `test_advance_station_complete_exam`
8. `test_advance_station_exam_fail`
9. `test_advance_station_wrong_state`
10. `test_get_exam_results_not_completed`
11. `test_get_exam_results_success`
12. `test_score_aggregation_multiple_stations`

**Key Changes**:
1. Use real `MockExamOrchestrator` instead of mocking
2. Use test database (SQLite in-memory)
3. Remove all `@patch` decorators
4. Test actual business logic, not mocks

### Phase 5: Database Model Check (30 minutes)

**File**: `src/db/models.py`

**Check if MockExam model exists**:
```python
class MockExam(Base):
    __tablename__ = "mock_exams"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    num_stations = Column(Integer, nullable=False)
    difficulty = Column(String, nullable=False)
    status = Column(String, nullable=False)  # in_progress, completed, failed
    current_station = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", back_populates="mock_exams")
    stations = relationship("MockExamStation", back_populates="exam", cascade="all, delete-orphan")

class MockExamStation(Base):
    __tablename__ = "mock_exam_stations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    exam_id = Column(UUID(as_uuid=True), ForeignKey("mock_exams.id"), nullable=False)
    station_number = Column(Integer, nullable=False)
    persona_id = Column(UUID(as_uuid=True), ForeignKey("patient_personas.id"), nullable=False)
    score = Column(Float, nullable=True)  # 0-15 (AMC scale)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    exam = relationship("MockExam", back_populates="stations")
    persona = relationship("PatientPersona")
```

**If models don't exist**: Create Alembic migration

```bash
cd backend
alembic revision -m "Add mock exam tables"
# Edit migration file to add tables
alembic upgrade head
```

### Phase 6: Orchestrator Implementation Check (30 minutes)

**File**: `src/services/mock_exam/orchestrator.py`

**Check if MockExamOrchestrator exists**:

```python
class MockExamOrchestrator:
    def __init__(self, db: Session):
        self.db = db

    async def create_exam(
        self,
        user_id: int,
        num_stations: int = 8,
        difficulty: str = "medium"
    ) -> MockExamCreateResponse:
        """Create new mock exam with random persona selection"""

        # Check sufficient personas available
        personas = self._select_personas(num_stations, difficulty)

        if len(personas) < num_stations:
            raise HTTPException(400, "Insufficient patient personas available")

        # Create exam record
        exam = MockExam(
            user_id=user_id,
            num_stations=num_stations,
            difficulty=difficulty,
            status="in_progress"
        )
        self.db.add(exam)
        self.db.flush()

        # Create stations
        stations = []
        for i, persona in enumerate(personas):
            station = MockExamStation(
                exam_id=exam.id,
                station_number=i + 1,
                persona_id=persona.id
            )
            stations.append(station)
            self.db.add(station)

        self.db.commit()

        return self._to_response(exam, stations)

    async def advance_station(
        self,
        exam_id: str,
        station_number: int,
        score: float,
        user_id: int
    ) -> MockExamStatusResponse:
        """Complete station and advance to next"""
        # Implementation...

    async def get_exam_results(
        self,
        exam_id: str,
        user_id: int
    ) -> MockExamResultsResponse:
        """Get final exam results after completion"""
        # Implementation...
```

**If orchestrator doesn't exist**: Create minimal implementation to pass tests

---

## 4. Testing Strategy

### Test Pyramid

**Unit Tests** (test_orchestration.py - 12 tests):
- Business logic isolation
- Real database (SQLite in-memory)
- No API layer
- Fast execution (<5 seconds)

**Integration Tests** (test_api.py - 13 tests):
- Full request/response cycle
- Dependency overrides for external services
- Database + API layer
- Medium execution (<15 seconds)

**Schema Tests** (test_schemas.py - 32 tests):
- Pydantic validation
- UUID handling
- Already passing (100%)

### Dependency Override Pattern

**Centralized in conftest.py**:
```python
@pytest.fixture(autouse=True)
def mock_exam_dependencies(db, test_user):
    """Auto-apply all mock exam dependency overrides"""

    # Auth override
    def override_auth():
        return test_user

    # Orchestrator override (use real orchestrator with test DB)
    def override_orchestrator():
        from src.services.mock_exam.orchestrator import MockExamOrchestrator
        return MockExamOrchestrator(db)

    app.dependency_overrides[get_current_active_user] = override_auth
    app.dependency_overrides[get_orchestrator] = override_orchestrator

    yield

    app.dependency_overrides.clear()
```

**Benefits**:
- All tests automatically use test database
- No manual override setup in each test
- Easy cleanup with `autouse=True`

---

## 5. Migration from Mock to Real Implementation

### Current Test Philosophy (WRONG)
- Mock everything
- Test that mocks are called correctly
- Never test real implementation

### New Test Philosophy (CORRECT)
- Test real implementation with test database
- Only mock external services (Claude API, etc.)
- Integration tests use full stack

### What to Mock vs. What to Use Real

**Mock** (External Dependencies):
- ✅ Claude API calls
- ✅ Email sending
- ✅ Payment processing

**Use Real** (Internal Services):
- ✅ Database (SQLite in-memory for tests)
- ✅ Business logic (MockExamOrchestrator)
- ✅ Authentication (with test users)
- ✅ Validation logic

---

## 6. Risks & Mitigation

### Risk 1: Orchestrator Not Implemented
**Probability**: MEDIUM
**Impact**: HIGH (can't test business logic)
**Mitigation**:
- Check if orchestrator exists first
- If not, create minimal implementation
- Focus on data flow, not complex algorithms
- Can use simplified persona selection

### Risk 2: Database Models Missing
**Probability**: LOW
**Impact**: HIGH (can't persist exams)
**Mitigation**:
- Check models.py first
- Create Alembic migration if needed
- Use UUID TypeDecorator (already exists for OSCE)

### Risk 3: Async/Await Complexity
**Probability**: LOW
**Impact**: MEDIUM (test execution issues)
**Mitigation**:
- Use pytest-asyncio
- Mark async tests with `@pytest.mark.asyncio`
- Ensure event loop properly configured

### Risk 4: Test Execution Time
**Probability**: MEDIUM
**Impact**: LOW (slower CI/CD)
**Mitigation**:
- Use SQLite `:memory:` for speed
- Parallel test execution
- Database fixtures with `scope="function"`

---

## 7. Success Metrics

### Functional
- [ ] 57/57 mock exam tests passing (100%)
- [ ] Zero `unittest.mock` usage
- [ ] All UUIDs valid
- [ ] No Pydantic V2 warnings

### Performance
- [ ] Test execution <30 seconds
- [ ] No database connection leaks
- [ ] Memory usage <200MB

### Quality
- [ ] Zero flaky tests
- [ ] Clear error messages
- [ ] Easy to debug failures
- [ ] Good test coverage (>80%)

---

## 8. Timeline

| Phase | Duration | Cumulative | Deliverable |
|-------|----------|------------|-------------|
| Phase 1: Schemas | 30 min | 0:30 | mock_exam.py updated |
| Phase 2: Fixtures | 1 hour | 1:30 | conftest.py with overrides |
| Phase 3: API Tests | 1 hour | 2:30 | test_api.py refactored |
| Phase 4: Orchestration Tests | 1 hour | 3:30 | test_orchestration.py refactored |
| Phase 5: Database Check | 30 min | 4:00 | Models verified/created |
| Phase 6: Orchestrator Check | 30 min | 4:30 | Orchestrator verified/created |

**Total Estimated Time**: 4.5 hours
**Buffer**: 1 hour
**Total with Buffer**: **5.5 hours maximum**

---

## 9. Acceptance Criteria

**Definition of Done**:
- [ ] All 57 mock exam tests passing (100%)
- [ ] No `unittest.mock` imports in test files
- [ ] All UUID fixtures use `str(uuid.uuid4())`
- [ ] Pydantic V2 schemas (no deprecations)
- [ ] FastAPI dependency overrides working
- [ ] Test execution time <30 seconds
- [ ] Documentation updated
- [ ] Test pass rate: 634/686 (92.4%) ✅ **92% MILESTONE EXCEEDED**
- [ ] Zero errors maintained

---

## 10. Rollout Strategy

### Approach 1: All-at-Once (RISKY)
- Refactor all 25 tests simultaneously
- Higher risk of breaking existing 32 passing tests
- Faster if successful

### Approach 2: Incremental (RECOMMENDED)
**Step 1**: Fix 5 easiest API tests (30 min)
- Verify dependency override pattern works
- Get quick win

**Step 2**: Fix remaining 8 API tests (30 min)
- Apply same pattern
- 13/13 API tests passing

**Step 3**: Fix orchestration tests (2 hours)
- More complex, needs orchestrator implementation
- 12/12 orchestration tests passing

**Step 4**: Validate all tests (30 min)
- Run full suite
- Fix any regressions
- 57/57 tests passing

---

**Status**: READY FOR IMPLEMENTATION
**Next Action**: Check if MockExamOrchestrator and database models exist
**Expected Outcome**: 92.4% test pass rate (+3.6% from current 88.8%)
**Combined with EMR Validation**: 650/686 (94.8% pass rate) 🚀
