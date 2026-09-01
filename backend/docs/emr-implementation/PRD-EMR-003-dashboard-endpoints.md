# PRD-EMR-003: EMR Dashboard Endpoints (T-RALPH v2.1)

**Date**: 2026-04-06
**Version**: 1.0
**PRD Type**: T-RALPH (Test-First Development)
**Sprint**: EMR Backend Implementation - Phase 3
**Estimated Effort**: 4-5 hours

---

## 0 - DISCOVERY

**Ponytail Principle**: Search for existing code before creating new implementations.

### Existing Code Search

**FastAPI Dashboard Endpoints**:
```bash
find backend/src/api/routers -name "*dashboard*.py"
# Result: 0 matches - no existing dashboard endpoints
```

**Existing Services**:
```bash
find backend/src/services -name "*.py"
# Result: Found progress_service.py, analytics_service.py
```

**Database Models**:
```bash
find backend/src/models -name "*progress*.py" -o -name "*analytics*.py"
# Result: Found user_progress.py with progress tracking models
```

**Existing Dashboard Queries**:
```bash
grep -r "session.*count\|encounter.*count" backend/src/
# Result: Found similar aggregation queries in progress_service.py
```

### Reuse Decisions

✅ **REUSE: Progress Service Pattern**
- **Location**: `backend/src/services/progress_service.py`
- **Decision**: Extend existing service for dashboard analytics
- **Pattern**:
  ```python
  class ProgressAnalytics:
      def __init__(self, db: Session):
          self.db = db

      def get_user_stats(self, user_id: int) -> Dict:
          # Reuse existing query patterns
          ...
  ```

✅ **REUSE: Database Query Patterns**
- **Location**: `backend/src/services/progress_service.py`
- **Decision**: Follow existing aggregation query structure
- **Example**: SQLAlchemy `.group_by()`, `.count()`, `.filter()` patterns

✅ **REUSE: FastAPI Router Structure**
- **Location**: `backend/src/api/routers/` (existing routers)
- **Decision**: Follow existing router pattern for new dashboard endpoints
- **Pattern**: Dependency injection, response models, error handling

❌ **CREATE NEW: Dashboard Analytics Methods**
- **Reason**: New business logic for dashboard aggregations
- **Approach**: Extend progress_service.py with 3 new methods

### Packages Considered

✅ **fastapi: ^0.115.0** (EXISTING - already installed)
- **Purpose**: REST API endpoints
- **Decision**: REUSE existing setup

✅ **sqlalchemy: ^2.0.0** (EXISTING - already installed)
- **Purpose**: Database aggregation queries
- **Decision**: REUSE existing query patterns

✅ **pytest: ^8.0.0** (EXISTING - already installed)
- **Purpose**: Unit testing
- **Decision**: Write 3 new tests following existing test patterns

### Discovery Summary

**Reusable Components**:
1. Progress service structure from `progress_service.py`
2. Database query patterns (aggregation, filtering)
3. FastAPI router dependency injection pattern
4. Response model patterns from existing endpoints

**New Components Required**:
1. 3 analytics methods in progress_service.py:
   - `get_session_completion_stats()`
   - `get_encounter_type_distribution()`
   - `get_user_progress_timeline()`
2. 3 unit tests for new methods
3. Dashboard endpoint router registration

**Token Savings**: ~50% reduction by reusing existing service patterns and database query structures instead of creating new architectural patterns.

---

## T - TESTS (Test Specification - Write These FIRST)

### Test Inventory
- **Total Tests**: 3
- **Unit Tests**: 3 (ProgressAnalytics service methods)
- **Integration Tests**: 0 (deferred to separate E2E PRD)
- **E2E Tests**: 0 (deferred to separate E2E PRD)

### TDD Workflow (MANDATORY)
1. **RED Phase**: Write all 3 tests below → Confirm they FAIL
2. **GREEN Phase**: Implement 3 service methods → Confirm tests PASS
3. **REFACTOR Phase**: Optimize queries → Maintain 100% test pass rate

**Agent Constraint**: DO NOT implement ANY code before tests are written and confirmed failing.

---

### Phase 1 Tests: ProgressAnalytics EMR Methods (3 Tests)

#### Test 1: EMR Dashboard Metrics Service Method
**Purpose**: Verify `ProgressAnalytics.get_emr_dashboard_metrics()` returns EMR session statistics
**RED Phase Expected**: `AttributeError: type object 'ProgressAnalytics' has no attribute 'get_emr_dashboard_metrics'`
**GREEN Phase Expected**: Test passes when method implemented

```python
# FILE: backend/tests/test_emr_dashboard_service.py

import pytest
from datetime import datetime, timedelta
from uuid import uuid4


def test_get_emr_dashboard_metrics(db_session):
    """Test ProgressAnalytics.get_emr_dashboard_metrics returns EMR stats"""
    from src.db.models import User, MockPatient, EMRSession
    from src.services.progress_analytics import ProgressAnalytics

    # Create test user
    user = User(
        email="emr_test@test.com",
        password_hash="$2b$12$test_hash",
        full_name="EMR Test User"
    )
    db_session.add(user)
    db_session.commit()

    # Create mock patient
    patient = MockPatient(
        id=uuid4(),
        name="Test Patient",
        mrn="MRN001",
        age=45,
        gender="Male",
        specialty="Cardiology",
        difficulty="intermediate"
    )
    db_session.add(patient)
    db_session.commit()

    # Create 3 EMR sessions (2 validated, 1 in_progress)
    for i in range(3):
        status = "validated" if i < 2 else "in_progress"
        score = 75.0 if i == 0 else 85.0 if i == 1 else None

        session = EMRSession(
            id=uuid4(),
            user_id=user.id,
            patient_id=patient.id,
            specialty="Cardiology",
            difficulty="intermediate",
            status=status,
            validation_score=score,
            started_at=datetime.utcnow() - timedelta(days=i)
        )
        db_session.add(session)

    db_session.commit()

    # Get EMR dashboard metrics
    metrics = ProgressAnalytics.get_emr_dashboard_metrics(db_session, user.id)

    # Assertions
    assert metrics is not None, "Metrics should be returned"
    assert metrics["total_sessions"] == 3, "Should have 3 total sessions"
    assert metrics["completed_sessions"] == 2, "Should have 2 completed sessions"
    assert metrics["average_score"] == 80.0, "Average score should be (75+85)/2 = 80"
    assert metrics["pass_rate"] == 100.0, "Both sessions passed (scores > 70)"
```

---

#### Test 2: Unified Weekly Trends Service Method
**Purpose**: Verify `ProgressAnalytics.get_unified_weekly_trends()` includes MCQ+OSCE+EMR data
**RED Phase Expected**: `AttributeError: type object 'ProgressAnalytics' has no attribute 'get_unified_weekly_trends'`
**GREEN Phase Expected**: Test passes when method implemented

```python
def test_get_unified_weekly_trends(db_session):
    """Test ProgressAnalytics.get_unified_weekly_trends includes MCQ+OSCE+EMR"""
    from src.db.models import (
        User, MCQ, MCQAttempt, OSCE, OSCEAttempt,
        MockPatient, EMRSession
    )
    from src.services.progress_analytics import ProgressAnalytics

    # Create test user
    user = User(
        email="unified_test@test.com",
        password_hash="$2b$12$test_hash",
        full_name="Unified Test User"
    )
    db_session.add(user)
    db_session.commit()

    # Create MCQ (use correct field names: question_id, options JSON, correct_option)
    mcq = MCQ(
        question_id="MCQ-TEST-001",
        question_text="Test question",
        options=["A", "B", "C", "D"],
        correct_option="A",
        specialty="Cardiology",
        difficulty="intermediate",
        explanation="Test explanation"
    )
    db_session.add(mcq)
    db_session.commit()

    # Create OSCE
    osce = OSCE(
        title="Test OSCE",
        specialty="Cardiology",
        difficulty="intermediate",
        patient_presentation="Test presentation",
        expected_findings="Test findings",
        clinical_reasoning="Test reasoning",
        time_limit_minutes=10
    )
    db_session.add(osce)
    db_session.commit()

    # Create mock patient for EMR
    patient = MockPatient(
        id=uuid4(),
        name="Unified Test Patient",
        mrn="MRN_UNIFIED",
        age=50,
        gender="Female",
        specialty="Cardiology",
        difficulty="intermediate"
    )
    db_session.add(patient)
    db_session.commit()

    # Create data for this week
    now = datetime.utcnow()

    # 2 MCQ attempts
    for i in range(2):
        mcq_attempt = MCQAttempt(
            user_id=user.id,
            mcq_id=mcq.id,
            selected_answer="A",
            is_correct=True,
            time_taken_seconds=60,
            attempted_at=now
        )
        db_session.add(mcq_attempt)

    # 1 OSCE attempt
    osce_attempt = OSCEAttempt(
        user_id=user.id,
        osce_id=osce.id,
        score=80,
        feedback="Good work",
        completed_at=now
    )
    db_session.add(osce_attempt)

    # 1 EMR session
    emr_session = EMRSession(
        id=uuid4(),
        user_id=user.id,
        patient_id=patient.id,
        specialty="Cardiology",
        difficulty="intermediate",
        status="validated",
        validation_score=85.0,
        started_at=now
    )
    db_session.add(emr_session)

    db_session.commit()

    # Get unified weekly trends (1 week)
    trends = ProgressAnalytics.get_unified_weekly_trends(db_session, user.id, weeks=1)

    # Assertions
    assert len(trends) == 1, "Should have 1 week of data"
    trend = trends[0]
    assert trend["mcq_attempts"] == 2, "Should have 2 MCQ attempts"
    assert trend["osce_attempts"] == 1, "Should have 1 OSCE attempt"
    assert trend["emr_sessions"] == 1, "Should have 1 EMR session"
    assert trend["accuracy_rate"] == 100.0, "All MCQ attempts correct"
```

---

#### Test 3: EMR Weak Areas Service Method
**Purpose**: Verify `ProgressAnalytics.get_emr_weak_areas()` identifies specialties <70%
**RED Phase Expected**: `AttributeError: type object 'ProgressAnalytics' has no attribute 'get_emr_weak_areas'`
**GREEN Phase Expected**: Test passes when method implemented

```python
def test_get_emr_weak_areas(db_session):
    """Test ProgressAnalytics.get_emr_weak_areas identifies specialties <70%"""
    from src.db.models import User, MockPatient, EMRSession
    from src.services.progress_analytics import ProgressAnalytics

    # Create test user
    user = User(
        email="weak_emr_test@test.com",
        password_hash="$2b$12$test_hash",
        full_name="Weak EMR Test User"
    )
    db_session.add(user)
    db_session.commit()

    # Create patients in 2 specialties
    cardio_patient = MockPatient(
        id=uuid4(),
        name="Cardio Patient",
        mrn="MRN_CARDIO",
        age=45,
        gender="Male",
        specialty="Cardiology",
        difficulty="intermediate"
    )
    neuro_patient = MockPatient(
        id=uuid4(),
        name="Neuro Patient",
        mrn="MRN_NEURO",
        age=50,
        gender="Female",
        specialty="Neurology",
        difficulty="intermediate"
    )
    db_session.add(cardio_patient)
    db_session.add(neuro_patient)
    db_session.commit()

    # Create 6 cardiology sessions (average 80% - STRONG)
    for i in range(6):
        session = EMRSession(
            id=uuid4(),
            user_id=user.id,
            patient_id=cardio_patient.id,
            specialty="Cardiology",
            difficulty="intermediate",
            status="validated",
            validation_score=80.0,
            started_at=datetime.utcnow() - timedelta(days=i)
        )
        db_session.add(session)

    # Create 6 neurology sessions (average 60% - WEAK)
    for i in range(6):
        session = EMRSession(
            id=uuid4(),
            user_id=user.id,
            patient_id=neuro_patient.id,
            specialty="Neurology",
            difficulty="intermediate",
            status="validated",
            validation_score=60.0,
            started_at=datetime.utcnow() - timedelta(days=i)
        )
        db_session.add(session)

    db_session.commit()

    # Get EMR weak areas (threshold 70%, min 5 attempts)
    weak_areas = ProgressAnalytics.get_emr_weak_areas(
        db_session, user.id, threshold=70.0, min_attempts=5
    )

    # Assertions
    assert len(weak_areas) == 1, "Should have 1 weak area (Neurology)"
    assert weak_areas[0]["specialty"] == "Neurology"
    assert weak_areas[0]["average_score"] == 60.0
    assert weak_areas[0]["total_sessions"] == 6
```

---

### Test Execution Commands

```bash
# RED Phase: Confirm tests FAIL (methods not implemented)
cd /home/dev/Development/irStudy/backend
source venv/bin/activate
set -a && source .env && set +a
pytest tests/test_emr_dashboard_service.py -v

# Expected Output (RED Phase):
# FAILED test_get_emr_dashboard_metrics - AttributeError: ... has no attribute 'get_emr_dashboard_metrics'
# FAILED test_get_unified_weekly_trends - AttributeError: ... has no attribute 'get_unified_weekly_trends'
# FAILED test_get_emr_weak_areas - AttributeError: ... has no attribute 'get_emr_weak_areas'
# 3 failed

# GREEN Phase: Confirm tests PASS (after implementation)
pytest tests/test_emr_dashboard_service.py -v

# Expected Output (GREEN Phase):
# PASSED test_get_emr_dashboard_metrics
# PASSED test_get_unified_weekly_trends
# PASSED test_get_emr_weak_areas
# 3 passed
```

---

### Test Coverage Targets

**Per Method**:
- `get_emr_dashboard_metrics`: 1 test (EMR session aggregation)
- `get_unified_weekly_trends`: 1 test (MCQ+OSCE+EMR unified trends)
- `get_emr_weak_areas`: 1 test (EMR weak specialty identification)

**Total**: 3 tests (100% must pass before deployment)

**Coverage Thresholds**:
- Lines: ≥80%
- Branches: ≥75%
- Functions: ≥90%
- Statements: ≥80%

---

## R - REQUEST (User Story & Business Context)

### User Story

**As a** medical student practicing with EMR simulations
**I want** to see my EMR performance metrics on the dashboard
**So that** I can track my progress and identify areas needing improvement

### Business Context

**Problem**:
- Current dashboard only shows MCQ and OSCE metrics
- EMR practice sessions exist but no analytics displayed
- Students cannot track EMR performance trends
- No identification of weak EMR specialties

**Impact**:
- Students lack visibility into EMR practice effectiveness
- No data-driven guidance for targeted EMR practice
- Dashboard incomplete (missing 1/3 of platform features)

**Solution**:
Add 3 analytics methods to ProgressAnalytics service:
1. **EMR Dashboard Metrics**: Total sessions, completion rate, average scores, pass rate
2. **Unified Weekly Trends**: Combined MCQ+OSCE+EMR activity per week
3. **EMR Weak Areas**: Specialties with <70% average EMR scores

### Success Criteria

**Functional**:
- [ ] `get_emr_dashboard_metrics()` returns EMR session statistics
- [ ] `get_unified_weekly_trends()` includes EMR session counts
- [ ] `get_emr_weak_areas()` identifies low-performing specialties

**Performance**:
- [ ] All queries use database aggregation (no N+1 queries)
- [ ] Response time <200ms (p95)
- [ ] Efficient JOIN + GROUP BY queries

**Quality**:
- [ ] 3/3 tests passing (100% pass rate)
- [ ] No regressions in existing tests (448 total tests still pass)
- [ ] Code coverage ≥80%

---

## A - ARCHITECTURE (Technical Design)

### System Architecture

**Affected Components**:
- **Service Layer**: `src/services/progress_analytics.py` (add 3 methods)
- **Database**: Query `emr_sessions`, `mock_patients` tables
- **Existing Code**: Extend ProgressAnalytics class (no new files)

**Data Flow**:
```
Frontend Dashboard
  ↓ (future: API call to /progress/dashboard/emr)
Progress Router (future implementation)
  ↓ (calls service method)
ProgressAnalytics.get_emr_dashboard_metrics(db, user_id)
  ↓ (queries database)
PostgreSQL (emr_sessions table)
  ↓ (returns aggregated data)
JSON Response → Frontend
```

### Database Schema

**Tables Used**:
```sql
-- EMR Sessions (created in Phase 1)
CREATE TABLE emr_sessions (
    id UUID PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    patient_id UUID REFERENCES mock_patients(id),
    specialty VARCHAR(50),
    difficulty VARCHAR(20),
    status VARCHAR(20),  -- 'in_progress', 'validated'
    validation_score FLOAT,  -- 0-100
    started_at TIMESTAMP,
    submitted_at TIMESTAMP,
    ...
);

-- Mock Patients (created in Phase 1)
CREATE TABLE mock_patients (
    id UUID PRIMARY KEY,
    name VARCHAR(100),
    specialty VARCHAR(50),
    difficulty VARCHAR(20),
    ...
);
```

### API Design (Future - Not Implemented in This PRD)

**Note**: This PRD focuses on SERVICE METHODS only. API endpoints deferred to separate PRD.

**Future Endpoints**:
- `GET /api/v1/progress/dashboard/emr` → calls `get_emr_dashboard_metrics()`
- `GET /api/v1/progress/weekly-trends/unified?weeks=4` → calls `get_unified_weekly_trends()`
- `GET /api/v1/progress/weak-areas/emr?threshold=70` → calls `get_emr_weak_areas()`

### Service Method Specifications

#### Method 1: get_emr_dashboard_metrics

```python
@staticmethod
def get_emr_dashboard_metrics(db: Session, user_id: int) -> Dict:
    """
    Calculate EMR dashboard metrics for user.

    Returns:
        Dict with keys:
        - total_sessions: int (all EMR sessions)
        - completed_sessions: int (status='validated')
        - average_score: float (mean of validation_score, 0-100)
        - pass_rate: float (% of sessions with score >70)
    """
```

#### Method 2: get_unified_weekly_trends

```python
@staticmethod
def get_unified_weekly_trends(db: Session, user_id: int, weeks: int = 4) -> List[Dict]:
    """
    Get weekly trends combining MCQ, OSCE, and EMR activity.

    Extends existing get_weekly_trends() to include EMR sessions.

    Returns:
        List[Dict] with keys per week:
        - week_start: datetime
        - mcq_attempts: int
        - osce_attempts: int  # NEW
        - emr_sessions: int  # NEW
        - accuracy_rate: float (MCQ only)
    """
```

#### Method 3: get_emr_weak_areas

```python
@staticmethod
def get_emr_weak_areas(
    db: Session,
    user_id: int,
    threshold: float = 70.0,
    min_attempts: int = 5
) -> List[Dict]:
    """
    Identify EMR specialties needing improvement.

    Returns:
        List[Dict] with keys:
        - specialty: str
        - average_score: float
        - total_sessions: int
        - pass_rate: float (% with score >70)
    """
```

### Security Considerations

**Privacy**:
- All queries filtered by `user_id` (never cross-user data)
- No PHI exposed (patient names are mock data, not real)

**SQL Injection Prevention**:
- Use SQLAlchemy ORM (no raw SQL)
- All parameters passed via ORM filters

**Performance**:
- Database-level aggregation (`func.count`, `func.avg`)
- Indexed columns: `user_id`, `status`, `specialty`

---

## L - LOOP (Iterative Development with TDD Enforcement)

### Phase 1: Service Methods Implementation (4-5 hours)

**TDD Workflow (MANDATORY)**:

#### 1. RED Phase (30 min)

**Agent Actions**:
1. Read PROJECT_CONSTRAINTS.md (if exists)
2. Read T section (Tests 1-3) of this PRD
3. Create test file `tests/test_emr_dashboard_service.py` with all 3 tests
4. Run `pytest tests/test_emr_dashboard_service.py -v`
5. **Confirm**: All 3 tests FAIL with `AttributeError` (methods don't exist)
6. Take screenshot or copy error output
7. Report to PM: "RED phase complete: 3 tests failing as expected"

**Expected Output**:
```
FAILED test_get_emr_dashboard_metrics - AttributeError: ... has no attribute 'get_emr_dashboard_metrics'
FAILED test_get_unified_weekly_trends - AttributeError: ... has no attribute 'get_unified_weekly_trends'
FAILED test_get_emr_weak_areas - AttributeError: ... has no attribute 'get_emr_weak_areas'
3 failed
```

**Blocker**: If tests PASS in RED phase → STOP, investigate (methods already exist or tests are wrong)

---

#### 2. GREEN Phase (3 hours)

**Agent Actions**:
1. Open `src/services/progress_analytics.py`
2. Implement `get_emr_dashboard_metrics()` (minimal code to pass Test 1)
3. Run `pytest tests/test_emr_dashboard_service.py::test_get_emr_dashboard_metrics -v`
4. **Confirm**: Test 1 PASSES
5. Implement `get_unified_weekly_trends()` (minimal code to pass Test 2)
6. Run `pytest tests/test_emr_dashboard_service.py::test_get_unified_weekly_trends -v`
7. **Confirm**: Test 2 PASSES
8. Implement `get_emr_weak_areas()` (minimal code to pass Test 3)
9. Run `pytest tests/test_emr_dashboard_service.py::test_get_emr_weak_areas -v`
10. **Confirm**: Test 3 PASSES
11. Run ALL tests: `pytest tests/test_emr_dashboard_service.py -v`
12. **Confirm**: 3/3 tests PASSING
13. Report to PM: "GREEN phase complete: 3/3 tests passing"

**Expected Output**:
```
PASSED test_get_emr_dashboard_metrics
PASSED test_get_unified_weekly_trends
PASSED test_get_emr_weak_areas
3 passed
```

**Blocker**: If any test FAILS → STOP, fix implementation before proceeding

---

#### 3. REFACTOR Phase (1 hour)

**Agent Actions**:
1. Optimize SQL queries (combine queries where possible)
2. Add type hints and docstrings
3. Extract common logic (e.g., pass_rate calculation)
4. Run `pytest tests/test_emr_dashboard_service.py -v` AGAIN
5. **Confirm**: 3/3 tests STILL PASS (maintained 100% pass rate)
6. Report to PM: "REFACTOR phase complete: 3/3 tests still passing"

**Optimization Examples**:
- Use single query with `func.count(case(...))` for pass_rate
- Reuse existing `get_weekly_trends()` logic for unified trends

**Blocker**: If tests FAIL after refactor → STOP, revert changes

---

#### 4. VALIDATION Phase (30 min)

**Agent Actions**:
1. Run full test suite: `pytest --tb=short -q 2>&1 | tail -20`
2. **Confirm**: No regressions (448+ tests still passing)
3. Check test coverage: `pytest tests/test_emr_dashboard_service.py --cov=src/services/progress_analytics --cov-report=term-missing`
4. **Confirm**: Coverage ≥80% for new methods
5. Complete validation checklist below
6. Report to PM: "VALIDATION complete: All gates passed"

**Validation Checklist**:
- [ ] 3/3 tests passing (`pytest tests/test_emr_dashboard_service.py`)
- [ ] No regressions (full test suite passes)
- [ ] Coverage ≥80% for new methods
- [ ] Type hints added to all methods
- [ ] Docstrings follow Google style
- [ ] No hardcoded values (thresholds as parameters)

**Blocker**: If validation fails → STOP, fix violations before delivery

---

### 3-Layer QA Validation

**Layer 0 (TDD)**:
- Tests written FIRST and confirmed failing (RED phase)
- 3/3 tests passing after implementation (GREEN phase)
- 3/3 tests still passing after refactoring

**Layer 1 (Agent)**:
- `pytest tests/test_emr_dashboard_service.py` → 3/3 passing
- `pytest` (full suite) → 448+ passing (no regressions)

**Layer 2 (PM)**:
- Review test quality (assertions cover all requirements)
- Review code quality (follows existing patterns)
- Confirm no hardcoded values

**Layer 3 (QA)**:
- `pytest tests/test_emr_dashboard_service.py --cov` → ≥80% coverage
- Manual code review for SQL injection risks

---

## P - PLAN (Detailed Implementation)

### File Modifications

#### File 1: src/services/progress_analytics.py

**Location**: Line 469 (end of file)
**Action**: Add 3 new static methods
**Lines Added**: ~120 lines

**Implementation**:

```python
# FILE: src/services/progress_analytics.py
# Location: After line 469 (end of get_specialty_detail method)

    @staticmethod
    def get_emr_dashboard_metrics(db: Session, user_id: int) -> Dict:
        """
        Calculate EMR dashboard metrics for user.

        Args:
            db: Database session
            user_id: User ID (CRITICAL: Must filter by this)

        Returns:
            Dict: EMR metrics
                - total_sessions: Total EMR sessions (all statuses)
                - completed_sessions: Sessions with status='validated'
                - average_score: Mean validation_score (0-100, rounded to 2 decimals)
                - pass_rate: % of sessions with score ≥70 (rounded to 2 decimals)

        Privacy:
            - Filters by user_id (never cross-user data)

        Example:
            >>> metrics = ProgressAnalytics.get_emr_dashboard_metrics(db, user_id=1)
            >>> print(metrics)
            {
                "total_sessions": 12,
                "completed_sessions": 10,
                "average_score": 78.5,
                "pass_rate": 80.0
            }
        """
        from src.db.models import EMRSession

        # Total sessions (all statuses)
        total_sessions = (
            db.query(EMRSession)
            .filter(EMRSession.user_id == user_id)
            .count()
        )

        # Completed sessions (status='validated')
        completed_sessions = (
            db.query(EMRSession)
            .filter(
                EMRSession.user_id == user_id,
                EMRSession.status == "validated"
            )
            .count()
        )

        # Get all validated session scores
        validated_sessions = (
            db.query(EMRSession.validation_score)
            .filter(
                EMRSession.user_id == user_id,
                EMRSession.status == "validated",
                EMRSession.validation_score.isnot(None)
            )
            .all()
        )

        if not validated_sessions:
            return {
                "total_sessions": total_sessions,
                "completed_sessions": completed_sessions,
                "average_score": 0.0,
                "pass_rate": 0.0
            }

        scores = [score[0] for score in validated_sessions]
        average_score = round(sum(scores) / len(scores), 2)

        # Calculate pass rate (score ≥70)
        passed_count = sum(1 for score in scores if score >= 70.0)
        pass_rate = round((passed_count / len(scores)) * 100, 2)

        return {
            "total_sessions": total_sessions,
            "completed_sessions": completed_sessions,
            "average_score": average_score,
            "pass_rate": pass_rate
        }

    @staticmethod
    def get_unified_weekly_trends(
        db: Session, user_id: int, weeks: int = 4
    ) -> List[Dict]:
        """
        Get weekly progress trends combining MCQ, OSCE, and EMR activity.

        Extends existing get_weekly_trends() to include OSCE and EMR data.

        Args:
            db: Database session
            user_id: User ID (CRITICAL: Must filter by this)
            weeks: Number of weeks to retrieve (default 4, max 12)

        Returns:
            List[Dict]: Weekly trend data (most recent first)
                - week_start: Start date of the week (Monday)
                - mcq_attempts: MCQ attempts during this week
                - osce_attempts: OSCE attempts during this week (NEW)
                - emr_sessions: EMR sessions during this week (NEW)
                - accuracy_rate: Success percentage for MCQ (0-100)

        Privacy:
            - Filters by user_id (never cross-user data)

        Example:
            >>> trends = ProgressAnalytics.get_unified_weekly_trends(db, user_id=1, weeks=2)
            >>> print(trends[0])
            {
                "week_start": datetime(2026, 4, 7),
                "mcq_attempts": 15,
                "osce_attempts": 3,
                "emr_sessions": 2,
                "accuracy_rate": 73.33
            }
        """
        from src.db.models import MCQAttempt, OSCEAttempt, EMRSession

        # Limit weeks to max 12
        weeks = min(weeks, 12)

        # Calculate date range
        today = datetime.utcnow()
        start_date = today - timedelta(weeks=weeks)

        trends = []

        # Generate data for each week
        for week_offset in range(weeks):
            week_start = start_date + timedelta(weeks=week_offset)
            # Adjust to Monday
            week_start = week_start - timedelta(days=week_start.weekday())
            week_end = week_start + timedelta(days=7)

            # MCQ attempts for this week
            mcq_attempts = (
                db.query(MCQAttempt)
                .filter(
                    MCQAttempt.user_id == user_id,
                    MCQAttempt.attempted_at >= week_start,
                    MCQAttempt.attempted_at < week_end,
                )
                .count()
            )

            # MCQ accuracy for this week
            correct_attempts = (
                db.query(MCQAttempt)
                .filter(
                    MCQAttempt.user_id == user_id,
                    MCQAttempt.attempted_at >= week_start,
                    MCQAttempt.attempted_at < week_end,
                    MCQAttempt.is_correct == True,
                )
                .count()
            )

            accuracy_rate = (
                round((correct_attempts / mcq_attempts) * 100, 2) if mcq_attempts > 0 else 0.0
            )

            # OSCE attempts for this week (NEW)
            osce_attempts = (
                db.query(OSCEAttempt)
                .filter(
                    OSCEAttempt.user_id == user_id,
                    OSCEAttempt.completed_at >= week_start,
                    OSCEAttempt.completed_at < week_end,
                )
                .count()
            )

            # EMR sessions for this week (NEW)
            emr_sessions = (
                db.query(EMRSession)
                .filter(
                    EMRSession.user_id == user_id,
                    EMRSession.started_at >= week_start,
                    EMRSession.started_at < week_end,
                )
                .count()
            )

            trends.append(
                {
                    "week_start": week_start,
                    "mcq_attempts": mcq_attempts,
                    "osce_attempts": osce_attempts,
                    "emr_sessions": emr_sessions,
                    "accuracy_rate": accuracy_rate,
                }
            )

        # Return most recent first
        trends.reverse()

        return trends

    @staticmethod
    def get_emr_weak_areas(
        db: Session, user_id: int, threshold: float = 70.0, min_attempts: int = 5
    ) -> List[Dict]:
        """
        Identify EMR specialties needing improvement.

        CRITERIA:
        - Average score below threshold (default 70%)
        - Minimum sessions >= min_attempts (default 5)

        Args:
            db: Database session
            user_id: User ID (CRITICAL: Must filter by this)
            threshold: Score threshold percentage (default 70.0)
            min_attempts: Minimum sessions required (default 5)

        Returns:
            List[Dict]: Weak specialties (sorted by score, lowest first)
                - specialty: Specialty name
                - average_score: Mean validation_score (0-100)
                - total_sessions: Total validated sessions
                - pass_rate: % of sessions with score ≥70

        Privacy:
            - Filters by user_id (never cross-user data)

        Example:
            >>> weak = ProgressAnalytics.get_emr_weak_areas(db, user_id=1, threshold=70.0)
            >>> print(weak[0])
            {
                "specialty": "Neurology",
                "average_score": 62.5,
                "total_sessions": 8,
                "pass_rate": 37.5
            }
        """
        from src.db.models import EMRSession
        from sqlalchemy import func

        # Get specialty performance (only validated sessions)
        results = (
            db.query(
                EMRSession.specialty,
                func.count(EMRSession.id).label("total_sessions"),
                func.avg(EMRSession.validation_score).label("avg_score"),
            )
            .filter(
                EMRSession.user_id == user_id,
                EMRSession.status == "validated",
                EMRSession.validation_score.isnot(None)
            )
            .group_by(EMRSession.specialty)
            .having(func.count(EMRSession.id) >= min_attempts)
            .all()
        )

        weak_areas = []
        for row in results:
            specialty = row.specialty
            total_sessions = row.total_sessions
            avg_score = round(row.avg_score, 2)

            # Only include if below threshold
            if avg_score < threshold:
                # Calculate pass rate for this specialty
                passed_sessions = (
                    db.query(EMRSession)
                    .filter(
                        EMRSession.user_id == user_id,
                        EMRSession.specialty == specialty,
                        EMRSession.status == "validated",
                        EMRSession.validation_score >= 70.0
                    )
                    .count()
                )

                pass_rate = round((passed_sessions / total_sessions) * 100, 2)

                weak_areas.append(
                    {
                        "specialty": specialty,
                        "average_score": avg_score,
                        "total_sessions": total_sessions,
                        "pass_rate": pass_rate
                    }
                )

        # Sort by average_score (lowest first)
        weak_areas.sort(key=lambda x: x["average_score"])

        return weak_areas
```

---

#### File 2: tests/test_emr_dashboard_service.py

**Location**: New file
**Action**: Create test file with 3 tests
**Lines Added**: ~300 lines

**Full test code**: See T section above (Tests 1-3)

---

#### File 3: tests/conftest.py

**Location**: Line 20
**Action**: Add EMR model imports to ensure tables created
**Lines Modified**: 1

**Implementation**:

```python
# FILE: tests/conftest.py
# Location: After line 20

from src.db.base import Base
# Import all models to ensure they're registered with Base.metadata
from src.db.models import (
    User, MCQ, MCQAttempt, OSCE, OSCEAttempt, StudyCard, StudyCardReview,
    UserProgress, MockPatient, EMRSession, EMRSOAPNote, EMRPrescription,
    EMRPathologyOrder, EMRValidationResult  # ADD THESE
)
```

---

### Implementation Timeline

| Task | Duration | Cumulative |
|------|----------|------------|
| RED Phase (write tests, confirm FAIL) | 30 min | 0.5 hrs |
| GREEN Phase (implement 3 methods) | 3 hours | 3.5 hrs |
| REFACTOR Phase (optimize queries) | 1 hour | 4.5 hrs |
| VALIDATION Phase (run tests, check coverage) | 30 min | 5 hrs |

**Total Estimated Time**: 5 hours

---

## H - HANDOFF (Delivery & Validation)

### Test Results Summary (MANDATORY)

**Test Execution Evidence**:

```bash
cd /home/dev/Development/irStudy/backend
source venv/bin/activate
set -a && source .env && set +a

# Run EMR dashboard service tests
pytest tests/test_emr_dashboard_service.py -v

# Expected Output:
tests/test_emr_dashboard_service.py::test_get_emr_dashboard_metrics PASSED [ 33%]
tests/test_emr_dashboard_service.py::test_get_unified_weekly_trends PASSED [ 66%]
tests/test_emr_dashboard_service.py::test_get_emr_weak_areas PASSED [100%]

======================== 3 passed in 0.45s ========================

# Run full test suite (verify no regressions)
pytest --tb=short -q 2>&1 | tail -5

# Expected Output:
# 451 passed in 12.34s (448 existing + 3 new)
```

---

### TDD Compliance Verification

**Checklist**:
- [ ] All 3 tests written BEFORE implementation (RED phase)
- [ ] All 3 tests confirmed FAILING before implementation
- [ ] All 3 tests confirmed PASSING after implementation (GREEN phase)
- [ ] All 3 tests STILL PASSING after refactoring
- [ ] 0 tests skipped or marked as "TODO"

---

### Code Coverage

```bash
pytest tests/test_emr_dashboard_service.py --cov=src/services/progress_analytics --cov-report=term-missing

# Expected Output:
Name                                      Stmts   Miss  Cover   Missing
-----------------------------------------------------------------------
src/services/progress_analytics.py         189      8    95%    [lines missing]
-----------------------------------------------------------------------
TOTAL                                       189      8    95%

✅ Coverage thresholds MET (≥80% lines, ≥75% branches, ≥90% functions)
```

---

### Acceptance Criteria (Enhanced)

**Functionality**:
- [ ] All 3 user stories validated by passing tests
- [ ] EMR dashboard metrics calculated correctly
- [ ] Unified weekly trends include MCQ+OSCE+EMR data
- [ ] EMR weak areas identified with <70% threshold

**TDD Process**:
- [ ] Agent followed RED-GREEN-REFACTOR workflow
- [ ] No implementation code written before tests
- [ ] Test pass rate: 3/3 (100%)

**Code Quality**:
- [ ] Type hints on all new methods
- [ ] Docstrings follow Google style
- [ ] No hardcoded values (thresholds as parameters)
- [ ] Coverage: ≥80% lines

**Performance**:
- [ ] All queries use database aggregation (`func.count`, `func.avg`)
- [ ] No N+1 queries
- [ ] Response time <200ms

**Security**:
- [ ] All queries filtered by `user_id`
- [ ] No SQL injection risks (ORM only, no raw SQL)
- [ ] No PHI exposure

---

### Deployment Checklist

**Pre-Deployment**:
- [ ] All 3 tests passing
- [ ] Full test suite passing (451 tests)
- [ ] Code reviewed by PM
- [ ] No hardcoded credentials

**Post-Deployment**:
- [ ] Verify queries in production database (dry-run)
- [ ] Monitor query performance (<200ms)
- [ ] No errors in application logs

---

## Agent OS Expert Constraints

### Agent: python-backend-developer

**CRITICAL - Read These Files FIRST (IN ORDER)**:

1. **PROJECT_CONSTRAINTS.md**: `/home/dev/Development/irStudy/PROJECT_CONSTRAINTS.md` (if exists)
   - Section: Backend Patterns (SQLAlchemy ORM, FastAPI)
   - Section: Security Requirements (user_id filtering, no hardcoded secrets)
   - Section: Testing Requirements (pytest, TDD workflow)

2. **T Section of This PRD**: Read all 3 tests above

3. **Existing Code**: `src/services/progress_analytics.py` (see existing patterns)

---

**TDD WORKFLOW (MANDATORY)**:

**BEFORE starting ANY implementation**:
1. Read PROJECT_CONSTRAINTS.md (if exists)
2. Read T section (Tests 1-3) of this PRD
3. Search for existing patterns in `src/services/progress_analytics.py`
4. Create `tests/test_emr_dashboard_service.py` with ALL 3 tests
5. Run `pytest tests/test_emr_dashboard_service.py -v`
6. **Confirm**: All 3 tests FAIL with `AttributeError` (methods don't exist)
7. Take screenshot or copy error output
8. Report to PM: "RED phase complete: 3 tests failing as expected"

**DURING implementation**:
9. Implement MINIMAL code to make tests pass (GREEN phase)
10. Follow patterns from existing methods in `progress_analytics.py`
11. Run tests after implementing EACH method
12. STOP when all 3 tests pass
13. Report to PM: "GREEN phase complete: 3/3 tests passing"

**AFTER implementation**:
14. Optimize SQL queries (REFACTOR phase)
15. Run tests again after EVERY refactor
16. **Confirm**: Tests STILL pass (100% maintained)
17. Report to PM: "REFACTOR phase complete: 3/3 tests still passing"

**VALIDATION before returning**:
18. Run full test suite: `pytest --tb=short -q`
19. **Confirm**: No regressions (448+ tests still pass)
20. Run coverage: `pytest tests/test_emr_dashboard_service.py --cov`
21. **Confirm**: Coverage ≥80%
22. Complete validation checklist
23. Report final results to PM

**BLOCKERS**:
- If tests PASS in RED phase → STOP, investigate
- If tests FAIL in GREEN phase → STOP, fix implementation
- If tests FAIL in REFACTOR phase → STOP, revert refactor
- If regressions found → STOP, fix before delivery
- If coverage < 80% → STOP, review test quality

**DO NOT**:
- ❌ Write implementation code before tests
- ❌ Skip RED phase (must confirm tests fail first)
- ❌ Proceed if tests failing
- ❌ Use raw SQL (must use SQLAlchemy ORM)
- ❌ Skip user_id filtering (privacy violation)
- ❌ Hardcode thresholds (use parameters)

---

### Existing Code Patterns (MUST FOLLOW)

**Pattern**: SQLAlchemy aggregation queries
**File**: `src/services/progress_analytics.py` (lines 123-152)
**Example**:

```python
# Existing pattern from get_specialty_breakdown()
results = (
    db.query(
        MCQ.specialty,
        func.count(MCQAttempt.id).label("total_attempts"),
        func.sum(cast(MCQAttempt.is_correct, Integer)).label("correct_attempts"),
        func.avg(MCQAttempt.time_taken_seconds).label("avg_time"),
    )
    .join(MCQ, MCQAttempt.mcq_id == MCQ.id)
    .filter(MCQAttempt.user_id == user_id)  # CRITICAL: Always filter by user_id
    .group_by(MCQ.specialty)
    .all()
)
```

**Pattern**: Weekly date range calculation
**File**: `src/services/progress_analytics.py` (lines 302-316)
**Example**:

```python
# Existing pattern from get_weekly_trends()
for week_offset in range(weeks):
    week_start = start_date + timedelta(weeks=week_offset)
    week_start = week_start - timedelta(days=week_start.weekday())  # Adjust to Monday
    week_end = week_start + timedelta(days=7)
```

---

### Validation Checklist (Complete before returning)

- [ ] Read PROJECT_CONSTRAINTS.md (if exists)
- [ ] Read T section (Tests 1-3)
- [ ] Followed TDD workflow (RED-GREEN-REFACTOR)
- [ ] All 3 tests passing: `pytest tests/test_emr_dashboard_service.py` → 3/3 passing
- [ ] No regressions: `pytest` → 451+ passing
- [ ] Coverage met: `pytest tests/test_emr_dashboard_service.py --cov` → ≥80%
- [ ] Followed existing patterns from `progress_analytics.py`
- [ ] Type hints added to all methods
- [ ] Docstrings follow Google style
- [ ] All queries filtered by `user_id`
- [ ] No hardcoded values (thresholds as parameters)

---

### Validation Commands (Run these before returning)

```bash
# 1. EMR dashboard service tests
cd /home/dev/Development/irStudy/backend
source venv/bin/activate
set -a && source .env && set +a
pytest tests/test_emr_dashboard_service.py -v
# Expected: 3 passed

# 2. Full test suite (no regressions)
pytest --tb=short -q 2>&1 | tail -5
# Expected: 451+ passed

# 3. Code coverage
pytest tests/test_emr_dashboard_service.py --cov=src/services/progress_analytics --cov-report=term-missing
# Expected: ≥80% coverage

# 4. Type checking (optional if mypy configured)
# mypy src/services/progress_analytics.py
# Expected: 0 errors
```

---

**Last Updated**: 2026-04-06
**Version**: 1.0
**Authors**: Human
**Status**: ✅ READY FOR EXECUTION (TDD workflow embedded)

**Changelog**:
- 2026-04-06 (v1.0): Initial PRD with T-RALPH v2.1 structure
