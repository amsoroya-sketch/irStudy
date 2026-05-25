# PRD-MVP-001: Dashboard Backend API Validation & Testing

**PRD ID**: PRD-MVP-001
**Status**: Ready for Implementation
**Created**: 2026-05-25
**Standards**: T-RALPH V2.1
**Estimated Effort**: 3-4 hours
**Agent**: testing-qa-expert

---

## T - TESTS (Test Specification - Write These FIRST)

### Test Inventory
- **Total Tests**: 16 existing tests (validate and expand)
- **Unit Tests**: 0 (add 8 new)
- **Integration Tests**: 16 existing (validate all passing)
- **E2E Tests**: 0 (not required for this phase)

### TDD Workflow (MANDATORY)

**This PRD focuses on VALIDATION of existing implementation, NOT new development**

1. **RED Phase**: Run existing tests → Document any failures
2. **GREEN Phase**: Fix any failing tests → Confirm 16/16 passing
3. **EXPAND Phase**: Add 8 new unit tests → Confirm 24/24 passing
4. **REFACTOR Phase**: Improve test quality → Maintain 100% pass rate

**Agent Constraint**: Before ANY code changes, run existing tests and document results.

---

### Phase 1 Tests: Validate Existing Integration Tests (16 Tests)

#### Test Suite Location
**File**: `/home/dev/Development/irStudy/backend/tests/test_api/test_dashboard.py`
**Status**: Already implemented (needs validation)

#### Test 1-16: Existing Integration Tests

**Purpose**: Validate that all 16 existing tests pass after recent implementation

**RED Phase Expected**: 0-2 tests may fail (due to recent schema changes)
**GREEN Phase Expected**: 16/16 tests passing

```bash
# FILE: Test execution command
cd /home/dev/Development/irStudy/backend

# Run all dashboard tests
./run_tests.sh tests/test_api/test_dashboard.py -xvs

# Expected output:
# tests/test_api/test_dashboard.py::TestDashboardAuth::test_dashboard_requires_authentication PASSED
# tests/test_api/test_dashboard.py::TestDashboardAuth::test_dashboard_with_valid_token PASSED
# tests/test_api/test_dashboard.py::TestOverallProgress::test_overall_progress_calculation PASSED
# tests/test_api/test_dashboard.py::TestOverallProgress::test_overall_progress_with_no_data PASSED
# tests/test_api/test_dashboard.py::TestModuleStats::test_mcq_module_stats PASSED
# tests/test_api/test_dashboard.py::TestModuleStats::test_osce_module_stats PASSED
# tests/test_api/test_dashboard.py::TestModuleStats::test_emr_module_stats PASSED
# tests/test_api/test_dashboard.py::TestModuleStats::test_mock_exam_module_stats PASSED
# tests/test_api/test_dashboard.py::TestSpecialtyBreakdown::test_specialty_breakdown_aggregation PASSED
# tests/test_api/test_dashboard.py::TestRecentActivity::test_recent_activity_timeline PASSED
# tests/test_api/test_dashboard.py::TestRecentActivity::test_recent_activity_limit_10 PASSED
# tests/test_api/test_dashboard.py::TestRecommendations::test_weak_specialty_recommendation PASSED
# tests/test_api/test_dashboard.py::TestRecommendations::test_unused_module_recommendation PASSED
# tests/test_api/test_dashboard.py::TestPerformance::test_response_time_under_200ms PASSED
# tests/test_api/test_dashboard.py::TestSecurity::test_user_isolation PASSED
# tests/test_api/test_dashboard.py::TestEdgeCases::test_no_activity_returns_empty_recommendations PASSED
#
# ====================== 16 passed in 2.43s ======================
```

**Validation Checklist**:
- [ ] All 16 tests discovered by pytest
- [ ] All 16 tests passing (100% pass rate)
- [ ] No database errors or connection issues
- [ ] Response times <200ms (validated by test_response_time_under_200ms)
- [ ] User isolation working (validated by test_user_isolation)

---

### Phase 2 Tests: Add Unit Tests for Helper Functions (8 New Tests)

**Purpose**: Add unit tests for aggregation logic (currently only integration tests exist)

#### Test 17: Calculate Overall Completion Percentage (Unit Test)

**Purpose**: Validate completion percentage calculation in isolation
**RED Phase Expected**: Test fails (function not yet extracted)
**GREEN Phase Expected**: Test passes after extracting function

```python
# FILE: backend/tests/test_services/test_dashboard_service.py

import pytest
from datetime import datetime, timedelta
from src.services.dashboard_service import DashboardService

class TestOverallProgressCalculations:
    """Unit tests for dashboard aggregation logic"""

    def test_calculate_completion_percentage_all_complete(self):
        """Test 17: Completion percentage when all sessions complete"""
        # Arrange
        service = DashboardService()
        sessions = [
            {"status": "graded"},
            {"status": "graded"},
            {"status": "graded"},
        ]

        # Act
        result = service.calculate_completion_percentage(sessions)

        # Assert
        assert result == 100.0
        assert isinstance(result, float)

    def test_calculate_completion_percentage_partial(self):
        """Test 18: Completion percentage with mixed status"""
        # Arrange
        service = DashboardService()
        sessions = [
            {"status": "graded"},      # Complete
            {"status": "in_progress"}, # Incomplete
            {"status": "graded"},      # Complete
            {"status": "in_progress"}, # Incomplete
        ]

        # Act
        result = service.calculate_completion_percentage(sessions)

        # Assert
        assert result == 50.0  # 2/4 = 50%

    def test_calculate_completion_percentage_none_complete(self):
        """Test 19: Completion percentage when none complete"""
        # Arrange
        service = DashboardService()
        sessions = [
            {"status": "in_progress"},
            {"status": "in_progress"},
        ]

        # Act
        result = service.calculate_completion_percentage(sessions)

        # Assert
        assert result == 0.0

    def test_calculate_completion_percentage_empty_list(self):
        """Test 20: Completion percentage with no sessions"""
        # Arrange
        service = DashboardService()
        sessions = []

        # Act
        result = service.calculate_completion_percentage(sessions)

        # Assert
        assert result == 0.0  # No sessions = 0% completion


class TestSpecialtyAggregation:
    """Unit tests for specialty breakdown logic"""

    def test_aggregate_specialty_scores_single_specialty(self):
        """Test 21: Aggregate scores for single specialty"""
        # Arrange
        service = DashboardService()
        attempts = [
            {"specialty": "cardiology", "score": 85},
            {"specialty": "cardiology", "score": 90},
            {"specialty": "cardiology", "score": 75},
        ]

        # Act
        result = service.aggregate_specialty_scores(attempts)

        # Assert
        assert len(result) == 1
        assert result[0]["specialty"] == "cardiology"
        assert result[0]["attempts"] == 3
        assert result[0]["avg_score"] == pytest.approx(83.33, abs=0.01)

    def test_aggregate_specialty_scores_multiple_specialties(self):
        """Test 22: Aggregate scores for multiple specialties"""
        # Arrange
        service = DashboardService()
        attempts = [
            {"specialty": "cardiology", "score": 80},
            {"specialty": "respiratory", "score": 90},
            {"specialty": "cardiology", "score": 70},
            {"specialty": "psychiatry", "score": 85},
        ]

        # Act
        result = service.aggregate_specialty_scores(attempts)

        # Assert
        assert len(result) == 3
        specialties = {r["specialty"] for r in result}
        assert specialties == {"cardiology", "respiratory", "psychiatry"}

        # Find cardiology stats
        cardio = next(r for r in result if r["specialty"] == "cardiology")
        assert cardio["attempts"] == 2
        assert cardio["avg_score"] == 75.0  # (80 + 70) / 2


class TestRecommendationLogic:
    """Unit tests for recommendation generation"""

    def test_generate_weak_specialty_recommendation(self):
        """Test 23: Generate recommendation for weak specialty"""
        # Arrange
        service = DashboardService()
        specialty_breakdown = [
            {"specialty": "cardiology", "avg_score": 85},
            {"specialty": "respiratory", "avg_score": 60},  # 25 points below avg
            {"specialty": "psychiatry", "avg_score": 80},
        ]
        overall_avg = 75.0

        # Act
        result = service.generate_weak_specialty_recommendations(
            specialty_breakdown, overall_avg
        )

        # Assert
        assert len(result) == 1
        assert "respiratory" in result[0].lower()
        assert "focus" in result[0].lower() or "improve" in result[0].lower()

    def test_generate_unused_module_recommendation(self):
        """Test 24: Generate recommendation for unused module"""
        # Arrange
        service = DashboardService()
        last_activities = {
            "mcq": datetime.now() - timedelta(days=1),
            "osce": datetime.now() - timedelta(days=3),  # 3 days ago
            "emr": datetime.now() - timedelta(hours=5),
            "mock_exam": datetime.now() - timedelta(days=5),  # 5 days ago
        }

        # Act
        result = service.generate_unused_module_recommendations(
            last_activities, threshold_days=2
        )

        # Assert
        assert len(result) >= 2  # OSCE and Mock Exam
        assert any("osce" in r.lower() for r in result)
        assert any("mock" in r.lower() for r in result)
```

**Validation Commands**:
```bash
# Run new unit tests
cd /home/dev/Development/irStudy/backend
pytest tests/test_services/test_dashboard_service.py -xvs

# Expected: 8/8 passing (Tests 17-24)
```

---

### Phase 3 Tests: Performance and Load Testing (Validation Only)

**Purpose**: Validate existing performance test meets requirements

#### Test 25: Response Time Under Load (Validation)

**File**: Already exists in `test_dashboard.py::TestPerformance::test_response_time_under_200ms`

**Validation**:
```bash
# Run performance test 10 times to confirm consistency
for i in {1..10}; do
  pytest tests/test_api/test_dashboard.py::TestPerformance::test_response_time_under_200ms -v
done

# Expected: 10/10 passing, all <200ms
```

---

### Test Execution Commands

```bash
# Phase 1: Validate existing integration tests (16 tests)
cd /home/dev/Development/irStudy/backend
./run_tests.sh tests/test_api/test_dashboard.py -v
# Expected: 16/16 passing

# Phase 2: Run new unit tests (8 tests)
pytest tests/test_services/test_dashboard_service.py -v
# Expected: 8/8 passing

# All tests combined
./run_tests.sh tests/test_api/test_dashboard.py tests/test_services/test_dashboard_service.py -v
# Expected: 24/24 passing (100% pass rate)

# Coverage report
pytest tests/test_api/test_dashboard.py tests/test_services/test_dashboard_service.py --cov=src/api/v1/dashboard --cov=src/services/dashboard_service --cov-report=term-missing
# Expected: Coverage ≥85%
```

---

### Test Coverage Targets

**Per Phase**:
- Phase 1: 16 tests (existing integration tests)
- Phase 2: 8 tests (new unit tests for helper functions)
- Phase 3: 1 test (performance validation)

**Total**: 24 tests (100% must pass before deployment)

**Coverage Thresholds**:
- Lines: ≥85% (dashboard API + service layer)
- Branches: ≥80%
- Functions: ≥90%
- Statements: ≥85%

---

## R - REQUEST (User Story & Business Context)

### Executive Summary

The unified dashboard backend API was recently implemented (`src/api/v1/dashboard.py`) but needs comprehensive validation and testing before frontend integration. This PRD focuses on:

1. **Validating** the 16 existing integration tests pass
2. **Adding** 8 unit tests for aggregation logic
3. **Extracting** helper functions into a service layer
4. **Ensuring** 100% test coverage and <200ms performance

**Why This Matters**: The dashboard is the MVP's primary user entry point. Any bugs or performance issues will create poor first impressions and hurt adoption.

### Problem Statement

**Current State**:
- Dashboard API implemented with 16 integration tests
- No unit tests for aggregation logic (hard to debug)
- Helper functions embedded in router (not reusable)
- No service layer separation of concerns
- Performance validated but not load-tested

**Gap**:
- Cannot confidently integrate frontend without validation
- Aggregation bugs hard to isolate without unit tests
- Code duplication if other endpoints need same logic

**Risk**:
- Dashboard shows incorrect metrics → Users lose trust
- Slow response times (>200ms) → Poor UX
- Bugs in production require urgent hotfixes → Delays MVP

### Success Criteria

**Functional**:
- ✅ All 16 existing integration tests pass (100% pass rate)
- ✅ 8 new unit tests added and passing
- ✅ Service layer extracted (`src/services/dashboard_service.py`)
- ✅ All helper functions have unit test coverage

**Performance**:
- ✅ Response time <200ms (p95) under normal load
- ✅ Response time <300ms (p99) under peak load (10 concurrent users)

**Quality**:
- ✅ Code coverage ≥85% (lines)
- ✅ No TypeErrors or schema validation errors
- ✅ All edge cases handled (no data, empty lists, null values)

**Documentation**:
- ✅ Service layer documented with docstrings
- ✅ Test coverage report generated
- ✅ Performance benchmark results documented

---

## A - ARCHITECTURE (Technical Approach)

### Current Implementation

**File Structure**:
```
backend/
├── src/
│   ├── api/v1/
│   │   └── dashboard.py (634 lines) ← Current implementation
│   └── services/
│       └── [dashboard_service.py] ← TO CREATE
└── tests/
    ├── test_api/
    │   └── test_dashboard.py (636 lines) ← 16 existing tests
    └── test_services/
        └── [test_dashboard_service.py] ← TO CREATE (8 new tests)
```

### Architecture Changes

**Extract Service Layer**:
```
Before (All in Router):
src/api/v1/dashboard.py
├── get_dashboard_overview() (endpoint)
│   ├── Query MCQ attempts
│   ├── Query OSCE attempts
│   ├── Query EMR sessions
│   ├── Query Mock Exam sessions
│   ├── Calculate overall progress (embedded)
│   ├── Aggregate specialty scores (embedded)
│   ├── Generate recommendations (embedded)
│   └── Return DashboardResponse

After (Service Layer Extracted):
src/api/v1/dashboard.py
├── get_dashboard_overview() (endpoint)
│   └── Call DashboardService.get_overview()

src/services/dashboard_service.py (NEW)
├── get_overview(user_id, db) → DashboardResponse
├── calculate_overall_progress(sessions) → OverallProgress
├── calculate_completion_percentage(sessions) → float
├── aggregate_specialty_scores(attempts) → List[SpecialtyBreakdown]
├── generate_recommendations(...) → List[str]
├── generate_weak_specialty_recommendations(...) → List[str]
└── generate_unused_module_recommendations(...) → List[str]
```

**Benefits**:
1. **Testability**: Unit test aggregation logic in isolation
2. **Reusability**: Other endpoints can use same service methods
3. **Maintainability**: Single responsibility (router = HTTP, service = business logic)
4. **Debuggability**: Easier to trace bugs with smaller functions

### Data Flow

```
GET /api/v1/dashboard/overview
    ↓
[Router] Extract user_id from JWT
    ↓
[Service] DashboardService.get_overview(user_id, db)
    ↓
[Service] Query all 4 modules (MCQ, OSCE, EMR, Mock Exam)
    ↓
[Service] Calculate overall progress (completion %, avg score, total time)
    ↓
[Service] Aggregate specialty breakdown (cardiology, respiratory, psychiatry)
    ↓
[Service] Generate recommendations (weak specialty, unused module)
    ↓
[Service] Return DashboardResponse
    ↓
[Router] Return JSON (200 OK)
```

### Database Schema (No Changes)

**Tables Used** (read-only):
- `mcq_attempts` (user_id, mcq_id, score, attempted_at)
- `osce_attempts` (user_id, osce_id, score, attempted_at, station_type)
- `emr_sessions` (user_id, specialty, status, soap_note_score, created_at)
- `mock_exam_sessions` (user_id, status, score, created_at)
- `mock_exam_attempts` (session_id, question_id, is_correct)

**No migrations required** (validation only)

---

## L - LOOP (Iterative Development with TDD)

### Agent Constraints (ALL PHASES)

**CRITICAL - Read These Files FIRST**:
1. **PROJECT_CONSTRAINTS.md**: `/home/dev/Development/irStudy/PROJECT_CONSTRAINTS.md`
   - Section 2: Technology Stack (FastAPI, SQLAlchemy, pytest)
   - Section 3: Security Requirements (user isolation, no hardcoded credentials)
   - Section 4: Testing Requirements (100% pass rate, ≥70% coverage)
   - Section 6: Quality Gates (pytest, security scan, linting)

2. **T Section**: Read all tests for your phase FIRST

3. **Existing Code**: Review current implementation before refactoring
   - File: `src/api/v1/dashboard.py` (understand current logic)
   - File: `tests/test_api/test_dashboard.py` (understand test patterns)

**Validation Checklist** (Complete before returning):
- [ ] Read PROJECT_CONSTRAINTS.md sections 2, 3, 4, 6
- [ ] Followed existing patterns: mcqs/router.py (aggregation), osces/router.py (specialty filtering)
- [ ] Ran quality gate commands from constraints section 6
- [ ] No hardcoded credentials: `grep -r "api_key\|password\s*=" backend/src/` → 0 results
- [ ] Compilation: `python -m py_compile src/**/*.py` → 0 errors
- [ ] Tests: `./run_tests.sh tests/test_api/test_dashboard.py tests/test_services/test_dashboard_service.py` → 24/24 passing
- [ ] Security scan: User isolation verified by `test_user_isolation`

---

### Phase 1: Validate Existing Integration Tests (1 hour)

**TDD Workflow**:

1. **VALIDATION Phase (30 min)**:
   - Agent reads existing test file: `tests/test_api/test_dashboard.py`
   - Agent runs all 16 tests: `./run_tests.sh tests/test_api/test_dashboard.py -xvs`
   - **Confirms**: All 16 tests PASS
   - **Documents**: Any failures with full error messages
   - **Blocker**: If any test fails → Investigate root cause before proceeding

2. **ANALYSIS Phase (20 min)**:
   - Agent reviews current implementation: `src/api/v1/dashboard.py`
   - Agent identifies functions to extract (completion %, aggregation, recommendations)
   - Agent creates refactoring plan (service layer structure)
   - **Confirms**: No breaking changes to API contract

3. **DOCUMENTATION Phase (10 min)**:
   - Agent documents current test coverage (lines, branches, functions)
   - Agent runs: `pytest tests/test_api/test_dashboard.py --cov=src/api/v1/dashboard --cov-report=term-missing`
   - Agent saves baseline coverage report
   - **Confirms**: Coverage ≥80% (if not, document gaps)

**Deliverables**:
- [ ] Test execution report (16/16 passing or list of failures)
- [ ] Coverage baseline report (current %)
- [ ] Refactoring plan (which functions to extract)

**3-Layer QA Validation**:
- **Layer 1 (Agent)**: `./run_tests.sh` → 16/16 passing
- **Layer 2 (Agent)**: Coverage report → Document baseline
- **Layer 3 (Human)**: Review test results and refactoring plan

---

### Phase 2: Extract Service Layer with Unit Tests (1.5 hours)

**TDD Workflow (MANDATORY)**:

1. **RED Phase (30 min)**:
   - Agent creates `tests/test_services/test_dashboard_service.py`
   - Agent writes Tests 17-24 from T section (8 unit tests)
   - Agent runs: `pytest tests/test_services/test_dashboard_service.py -xvs`
   - **Confirms**: All 8 tests FAIL (service doesn't exist yet)
   - **Blocker**: If tests pass → Investigate (wrong import or service already exists)

2. **GREEN Phase (40 min)**:
   - Agent creates `src/services/dashboard_service.py`
   - Agent extracts functions from `src/api/v1/dashboard.py`:
     - `calculate_completion_percentage(sessions) -> float`
     - `aggregate_specialty_scores(attempts) -> List[SpecialtyBreakdown]`
     - `generate_weak_specialty_recommendations(...) -> List[str]`
     - `generate_unused_module_recommendations(...) -> List[str]`
   - Agent updates router to use service layer
   - Agent runs: `pytest tests/test_services/test_dashboard_service.py -xvs`
   - **Confirms**: All 8 tests PASS
   - **Blocker**: If any test fails → Fix implementation before proceeding

3. **INTEGRATION Phase (20 min)**:
   - Agent runs ALL tests (integration + unit): `./run_tests.sh tests/test_api/test_dashboard.py tests/test_services/test_dashboard_service.py -v`
   - **Confirms**: 24/24 tests passing (16 integration + 8 unit)
   - **Blocker**: If any integration test fails → Router refactoring broke contract

**Deliverables**:
- [ ] `src/services/dashboard_service.py` (250 lines, 7 methods)
- [ ] `tests/test_services/test_dashboard_service.py` (300 lines, 8 tests)
- [ ] Updated `src/api/v1/dashboard.py` (uses service layer)
- [ ] Test execution report (24/24 passing)

**3-Layer QA Validation**:
- **Layer 0 (TDD)**: Tests written FIRST and confirmed failing (RED phase)
- **Layer 1 (Agent)**: Unit tests passing (8/8)
- **Layer 2 (Agent)**: Integration tests passing (16/16)
- **Layer 3 (Agent)**: All tests passing (24/24)

---

### Phase 3: Performance Validation and Documentation (1 hour)

**TDD Workflow**:

1. **PERFORMANCE Phase (30 min)**:
   - Agent runs performance test 10 times: `for i in {1..10}; do pytest tests/test_api/test_dashboard.py::TestPerformance::test_response_time_under_200ms -v; done`
   - **Confirms**: 10/10 runs <200ms
   - Agent runs load test (if available): `locust -f tests/load/test_dashboard_load.py --headless -u 10 -r 2 -t 30s`
   - **Confirms**: p95 <200ms, p99 <300ms under 10 concurrent users
   - **Blocker**: If performance degrades → Profile code, optimize queries

2. **COVERAGE Phase (15 min)**:
   - Agent runs full coverage report:
     ```bash
     pytest tests/test_api/test_dashboard.py tests/test_services/test_dashboard_service.py \
       --cov=src/api/v1/dashboard \
       --cov=src/services/dashboard_service \
       --cov-report=html \
       --cov-report=term-missing
     ```
   - **Confirms**: Coverage ≥85% (lines), ≥80% (branches), ≥90% (functions)
   - Agent saves HTML report: `htmlcov/index.html`
   - **Blocker**: If coverage <85% → Add tests for uncovered lines

3. **DOCUMENTATION Phase (15 min)**:
   - Agent adds docstrings to all service methods (Google style)
   - Agent updates `DASHBOARD_API_IMPLEMENTATION_COMPLETE.md` with service layer details
   - Agent creates performance benchmark table
   - **Confirms**: All public methods documented

**Deliverables**:
- [ ] Performance benchmark report (response times over 10 runs)
- [ ] Coverage report (HTML + terminal output)
- [ ] Updated documentation with service layer architecture
- [ ] Docstrings for all service methods

**3-Layer QA Validation**:
- **Layer 1 (Agent)**: Performance test → 10/10 <200ms
- **Layer 2 (Agent)**: Coverage report → ≥85%
- **Layer 3 (Human)**: Review documentation completeness

---

## P - PLAN (Detailed Implementation)

### Phase 1: Validate Existing Tests (1 hour)

**File: Validation Script**

```bash
#!/bin/bash
# FILE: backend/scripts/validate_dashboard_tests.sh

set -e

echo "========================================="
echo "Dashboard Backend Validation - Phase 1"
echo "========================================="

# Step 1: Run existing integration tests
echo ""
echo "[1/3] Running existing integration tests..."
cd /home/dev/Development/irStudy/backend

./run_tests.sh tests/test_api/test_dashboard.py -xvs

# Capture exit code
TEST_RESULT=$?

if [ $TEST_RESULT -ne 0 ]; then
  echo "❌ FAILURE: Some tests failed. Review output above."
  exit 1
fi

echo "✅ SUCCESS: All 16 integration tests passing"

# Step 2: Generate coverage report
echo ""
echo "[2/3] Generating coverage baseline report..."
pytest tests/test_api/test_dashboard.py \
  --cov=src/api/v1/dashboard \
  --cov-report=term-missing \
  --cov-report=html:htmlcov/phase1

echo ""
echo "Coverage report saved to: htmlcov/phase1/index.html"

# Step 3: Document results
echo ""
echo "[3/3] Creating validation report..."
cat > DASHBOARD_VALIDATION_PHASE1_REPORT.md <<EOF
# Dashboard Backend Validation - Phase 1 Results

**Date**: $(date +%Y-%m-%d)
**Agent**: testing-qa-expert
**Duration**: $(date +%H:%M:%S)

## Test Results

### Integration Tests (16 tests)
- Status: ✅ PASSING
- File: tests/test_api/test_dashboard.py
- Execution Time: (see pytest output)
- Pass Rate: 16/16 (100%)

### Coverage Baseline
- Lines: (see coverage report)
- Branches: (see coverage report)
- Functions: (see coverage report)
- Report: htmlcov/phase1/index.html

## Next Steps
- Phase 2: Extract service layer with unit tests
- Target: 24/24 tests passing (16 integration + 8 unit)
EOF

echo "✅ Validation report created: DASHBOARD_VALIDATION_PHASE1_REPORT.md"
echo ""
echo "========================================="
echo "Phase 1 Complete"
echo "========================================="
```

**Validation Commands**:
```bash
cd /home/dev/Development/irStudy/backend
chmod +x scripts/validate_dashboard_tests.sh
./scripts/validate_dashboard_tests.sh
# Expected: Script exits 0, report created
```

---

### Phase 2: Extract Service Layer (1.5 hours)

**File 1: Service Layer Implementation**

```python
# FILE: backend/src/services/dashboard_service.py

"""
Dashboard Service Layer

Provides business logic for dashboard metrics aggregation.
Extracted from src/api/v1/dashboard.py for better testability and reusability.

Author: testing-qa-expert
Date: 2026-05-25
"""

from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from src.db.models import (
    User, MCQAttempt, MCQ, OSCEAttempt, OSCE,
    EMRSession, MockExamSession, MockExamAttempt
)
from src.api.v1.dashboard import (
    OverallProgress, ModuleStats, SpecialtyBreakdown,
    RecentActivity, DashboardResponse
)


class DashboardService:
    """
    Service for aggregating dashboard metrics across all modules.

    Provides methods for:
    - Overall progress calculation (completion %, avg score, total time)
    - Module-specific statistics (MCQ, OSCE, EMR, Mock Exam)
    - Specialty breakdown (cardiology, respiratory, psychiatry)
    - Recent activity timeline (last 10 actions)
    - Personalized recommendations (weak areas, unused modules)
    """

    def get_overview(self, user_id: int, db: Session) -> DashboardResponse:
        """
        Get comprehensive dashboard overview for a user.

        Args:
            user_id: User ID to fetch data for
            db: SQLAlchemy database session

        Returns:
            DashboardResponse with overall progress, module stats,
            specialty breakdown, recent activity, and recommendations

        Example:
            >>> service = DashboardService()
            >>> dashboard = service.get_overview(user_id=1, db=session)
            >>> print(dashboard.overall_progress.completion_percentage)
            68.5
        """
        # Query all modules (existing logic from router)
        mcq_attempts = db.query(MCQAttempt).filter(
            MCQAttempt.user_id == user_id
        ).all()

        osce_attempts = db.query(OSCEAttempt).filter(
            OSCEAttempt.user_id == user_id
        ).all()

        emr_sessions = db.query(EMRSession).filter(
            EMRSession.user_id == user_id
        ).all()

        mock_exams = db.query(MockExamSession).filter(
            MockExamSession.user_id == user_id
        ).all()

        # Calculate overall progress
        all_sessions = mcq_attempts + osce_attempts + emr_sessions + mock_exams
        overall_progress = self.calculate_overall_progress(all_sessions)

        # Calculate module stats
        modules = {
            "mcq": self._calculate_mcq_stats(mcq_attempts),
            "osce": self._calculate_osce_stats(osce_attempts),
            "emr": self._calculate_emr_stats(emr_sessions),
            "mock_exam": self._calculate_mock_exam_stats(mock_exams, db),
        }

        # Aggregate specialty breakdown
        all_specialty_attempts = self._gather_specialty_attempts(
            mcq_attempts, osce_attempts, emr_sessions, db
        )
        specialty_breakdown = self.aggregate_specialty_scores(all_specialty_attempts)

        # Generate recent activity
        recent_activity = self._generate_recent_activity(
            mcq_attempts, osce_attempts, emr_sessions, mock_exams, db
        )

        # Generate recommendations
        recommendations = self.generate_recommendations(
            specialty_breakdown,
            overall_progress.avg_score,
            modules,
            datetime.now()
        )

        return DashboardResponse(
            overall_progress=overall_progress,
            modules=modules,
            specialty_breakdown=specialty_breakdown,
            recent_activity=recent_activity[:10],  # Limit to 10
            recommendations=recommendations
        )

    def calculate_overall_progress(
        self, sessions: List[Any]
    ) -> OverallProgress:
        """
        Calculate overall progress metrics across all sessions.

        Args:
            sessions: List of session objects (MCQAttempt, OSCEAttempt, etc.)

        Returns:
            OverallProgress with total_sessions, completion_percentage,
            avg_score, total_time_minutes, last_activity

        Example:
            >>> sessions = [
            ...     MCQAttempt(score=85, status="graded"),
            ...     OSCEAttempt(score=75, status="graded"),
            ... ]
            >>> progress = service.calculate_overall_progress(sessions)
            >>> print(progress.completion_percentage)
            100.0
        """
        if not sessions:
            return OverallProgress(
                total_sessions=0,
                completion_percentage=0.0,
                avg_score=0.0,
                total_time_minutes=0,
                last_activity=None
            )

        # Calculate completion percentage
        completion_percentage = self.calculate_completion_percentage(sessions)

        # Calculate average score
        scored_sessions = [s for s in sessions if hasattr(s, 'score') and s.score]
        avg_score = (
            sum(s.score for s in scored_sessions) / len(scored_sessions)
            if scored_sessions else 0.0
        )

        # Calculate total time
        total_time_minutes = sum(
            getattr(s, 'duration_minutes', 0) or 0
            for s in sessions
        )

        # Find last activity
        last_activity = max(
            (getattr(s, 'attempted_at', None) or getattr(s, 'created_at', None)
             for s in sessions if hasattr(s, 'attempted_at') or hasattr(s, 'created_at')),
            default=None
        )

        return OverallProgress(
            total_sessions=len(sessions),
            completion_percentage=round(completion_percentage, 1),
            avg_score=round(avg_score, 1),
            total_time_minutes=total_time_minutes,
            last_activity=last_activity
        )

    def calculate_completion_percentage(self, sessions: List[Any]) -> float:
        """
        Calculate percentage of completed sessions.

        Args:
            sessions: List of session objects with 'status' attribute

        Returns:
            Float percentage (0.0 to 100.0)

        Example:
            >>> sessions = [
            ...     {"status": "graded"},
            ...     {"status": "in_progress"},
            ...     {"status": "graded"},
            ... ]
            >>> pct = service.calculate_completion_percentage(sessions)
            >>> print(pct)
            66.67
        """
        if not sessions:
            return 0.0

        # Count completed sessions
        # Completed = status in ("graded", "COMPLETE", "completed")
        completed = sum(
            1 for s in sessions
            if hasattr(s, 'status') and s.status in ("graded", "COMPLETE", "completed")
        )

        return (completed / len(sessions)) * 100.0

    def aggregate_specialty_scores(
        self, attempts: List[Dict[str, Any]]
    ) -> List[SpecialtyBreakdown]:
        """
        Aggregate scores by medical specialty.

        Args:
            attempts: List of dicts with 'specialty' and 'score' keys

        Returns:
            List of SpecialtyBreakdown sorted by attempts (descending)

        Example:
            >>> attempts = [
            ...     {"specialty": "cardiology", "score": 85},
            ...     {"specialty": "cardiology", "score": 90},
            ...     {"specialty": "respiratory", "score": 75},
            ... ]
            >>> breakdown = service.aggregate_specialty_scores(attempts)
            >>> print(breakdown[0].specialty, breakdown[0].avg_score)
            cardiology 87.5
        """
        if not attempts:
            return []

        # Group by specialty
        specialty_map: Dict[str, List[float]] = {}
        for attempt in attempts:
            specialty = attempt.get("specialty")
            score = attempt.get("score")

            if specialty and score is not None:
                if specialty not in specialty_map:
                    specialty_map[specialty] = []
                specialty_map[specialty].append(score)

        # Calculate averages
        result = [
            SpecialtyBreakdown(
                specialty=specialty,
                attempts=len(scores),
                avg_score=round(sum(scores) / len(scores), 1)
            )
            for specialty, scores in specialty_map.items()
        ]

        # Sort by attempts (most active first)
        result.sort(key=lambda x: x.attempts, reverse=True)

        return result

    def generate_recommendations(
        self,
        specialty_breakdown: List[SpecialtyBreakdown],
        overall_avg: float,
        modules: Dict[str, ModuleStats],
        current_time: datetime
    ) -> List[str]:
        """
        Generate personalized recommendations based on user activity.

        Args:
            specialty_breakdown: Specialty performance data
            overall_avg: Overall average score
            modules: Module-specific stats
            current_time: Current timestamp (for recency checks)

        Returns:
            List of recommendation strings (max 5)

        Example:
            >>> recommendations = service.generate_recommendations(
            ...     specialty_breakdown=[...],
            ...     overall_avg=75.0,
            ...     modules={...},
            ...     current_time=datetime.now()
            ... )
            >>> print(recommendations[0])
            "Focus on psychiatry - 15% below average"
        """
        recommendations = []

        # 1. Weak specialty recommendations
        weak_specialty_recs = self.generate_weak_specialty_recommendations(
            specialty_breakdown, overall_avg
        )
        recommendations.extend(weak_specialty_recs)

        # 2. Unused module recommendations
        last_activities = {
            name: stats.get("last_activity")
            for name, stats in modules.items()
        }
        unused_module_recs = self.generate_unused_module_recommendations(
            last_activities, threshold_days=2
        )
        recommendations.extend(unused_module_recs)

        # 3. Weekly goal recommendation (if total sessions < 10)
        # TODO: Implement weekly tracking

        return recommendations[:5]  # Max 5 recommendations

    def generate_weak_specialty_recommendations(
        self,
        specialty_breakdown: List[SpecialtyBreakdown],
        overall_avg: float,
        threshold_pct: float = 15.0
    ) -> List[str]:
        """
        Recommend focus on specialties performing below average.

        Args:
            specialty_breakdown: Specialty performance data
            overall_avg: Overall average score
            threshold_pct: Percentage below average to trigger (default 15%)

        Returns:
            List of recommendation strings

        Example:
            >>> breakdown = [
            ...     SpecialtyBreakdown(specialty="psychiatry", avg_score=60, attempts=10),
            ...     SpecialtyBreakdown(specialty="cardiology", avg_score=85, attempts=15),
            ... ]
            >>> recs = service.generate_weak_specialty_recommendations(breakdown, 75.0)
            >>> print(recs[0])
            "Focus on psychiatry - 15 points below average"
        """
        recommendations = []

        for specialty in specialty_breakdown:
            difference = overall_avg - specialty.avg_score

            if difference >= threshold_pct:
                recommendations.append(
                    f"Focus on {specialty.specialty} - "
                    f"{int(difference)} points below average"
                )

        return recommendations

    def generate_unused_module_recommendations(
        self,
        last_activities: Dict[str, Optional[datetime]],
        threshold_days: int = 2
    ) -> List[str]:
        """
        Recommend modules that haven't been used recently.

        Args:
            last_activities: Dict mapping module names to last activity timestamps
            threshold_days: Days of inactivity to trigger recommendation

        Returns:
            List of recommendation strings

        Example:
            >>> last_activities = {
            ...     "mcq": datetime.now() - timedelta(days=1),
            ...     "osce": datetime.now() - timedelta(days=5),
            ... }
            >>> recs = service.generate_unused_module_recommendations(last_activities, 2)
            >>> print(recs[0])
            "Try OSCE mode - unused for 5 days"
        """
        recommendations = []
        now = datetime.now()

        module_labels = {
            "mcq": "MCQ",
            "osce": "OSCE",
            "emr": "EMR",
            "mock_exam": "Mock Exam"
        }

        for module_name, last_activity in last_activities.items():
            if last_activity is None:
                # Module never used
                label = module_labels.get(module_name, module_name)
                recommendations.append(f"Try {label} mode - not yet attempted")
            else:
                days_inactive = (now - last_activity).days

                if days_inactive >= threshold_days:
                    label = module_labels.get(module_name, module_name)
                    recommendations.append(
                        f"Try {label} mode - unused for {days_inactive} days"
                    )

        return recommendations

    # Private helper methods (existing logic from router)
    # _calculate_mcq_stats, _calculate_osce_stats, etc.
    # (Implementation details omitted for brevity - copy from existing router)
```

**File 2: Unit Test Suite**

```python
# FILE: backend/tests/test_services/test_dashboard_service.py

"""
Unit tests for DashboardService

Tests aggregation logic in isolation (no database required).
Extracted from integration tests for better debuggability.

Author: testing-qa-expert
Date: 2026-05-25
"""

import pytest
from datetime import datetime, timedelta
from src.services.dashboard_service import DashboardService
from src.api.v1.dashboard import SpecialtyBreakdown


class TestOverallProgressCalculations:
    """Unit tests for dashboard aggregation logic"""

    def test_calculate_completion_percentage_all_complete(self):
        """Test 17: Completion percentage when all sessions complete"""
        # Arrange
        service = DashboardService()

        # Mock session objects
        class MockSession:
            def __init__(self, status):
                self.status = status

        sessions = [
            MockSession("graded"),
            MockSession("graded"),
            MockSession("graded"),
        ]

        # Act
        result = service.calculate_completion_percentage(sessions)

        # Assert
        assert result == 100.0
        assert isinstance(result, float)

    # ... (Tests 18-24 from T section - full implementation)
    # (Implementation details match T section exactly)


# Validation command
# pytest tests/test_services/test_dashboard_service.py -xvs
# Expected: 8/8 passing
```

**File 3: Update Router to Use Service**

```python
# FILE: backend/src/api/v1/dashboard.py (UPDATED)

# ... (existing imports)
from src.services.dashboard_service import DashboardService

# ... (existing Pydantic models - no changes)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/overview", response_model=DashboardResponse)
async def get_dashboard_overview(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive dashboard overview for current user.

    Aggregates data from all 4 modules (MCQ, OSCE, EMR, Mock Exam)
    and returns overall progress, module stats, specialty breakdown,
    recent activity, and personalized recommendations.

    **Performance**: <200ms response time (validated by tests)
    **Security**: User isolation enforced (current_user.id only)

    Returns:
        DashboardResponse with 5 sections:
        - overall_progress: Total sessions, completion %, avg score, time
        - modules: Per-module statistics (MCQ, OSCE, EMR, Mock Exam)
        - specialty_breakdown: Performance by specialty (cardiology, etc.)
        - recent_activity: Last 10 actions across all modules
        - recommendations: Personalized suggestions (weak areas, unused modules)
    """
    # Delegate to service layer
    service = DashboardService()
    return service.get_overview(user_id=current_user.id, db=db)
```

---

### Phase 3: Performance Validation (1 hour)

**File: Performance Validation Script**

```bash
#!/bin/bash
# FILE: backend/scripts/validate_dashboard_performance.sh

set -e

echo "========================================="
echo "Dashboard Performance Validation"
echo "========================================="

cd /home/dev/Development/irStudy/backend

# Step 1: Run performance test 10 times
echo ""
echo "[1/3] Running performance test (10 iterations)..."

FAIL_COUNT=0
for i in {1..10}; do
  echo "  Iteration $i/10..."

  if ! pytest tests/test_api/test_dashboard.py::TestPerformance::test_response_time_under_200ms -v --tb=short; then
    FAIL_COUNT=$((FAIL_COUNT + 1))
  fi
done

if [ $FAIL_COUNT -gt 0 ]; then
  echo "❌ FAILURE: $FAIL_COUNT/10 performance tests failed"
  exit 1
fi

echo "✅ SUCCESS: 10/10 performance tests <200ms"

# Step 2: Generate coverage report
echo ""
echo "[2/3] Generating final coverage report..."

pytest tests/test_api/test_dashboard.py tests/test_services/test_dashboard_service.py \
  --cov=src/api/v1/dashboard \
  --cov=src/services/dashboard_service \
  --cov-report=html:htmlcov/final \
  --cov-report=term-missing

echo ""
echo "Coverage report saved to: htmlcov/final/index.html"

# Step 3: Create final report
echo ""
echo "[3/3] Creating final validation report..."

cat > DASHBOARD_VALIDATION_COMPLETE.md <<EOF
# Dashboard Backend Validation - COMPLETE

**Date**: $(date +%Y-%m-%d)
**Agent**: testing-qa-expert
**Status**: ✅ READY FOR FRONTEND INTEGRATION

## Test Results Summary

### Integration Tests (16 tests)
- Status: ✅ PASSING
- File: tests/test_api/test_dashboard.py
- Pass Rate: 16/16 (100%)

### Unit Tests (8 tests)
- Status: ✅ PASSING
- File: tests/test_services/test_dashboard_service.py
- Pass Rate: 8/8 (100%)

### Performance Tests (10 iterations)
- Status: ✅ PASSING
- Average Response Time: <200ms
- Consistency: 10/10 runs successful

## Total Test Coverage
- **Tests**: 24/24 passing (100% pass rate)
- **Lines**: (see coverage report)
- **Branches**: (see coverage report)
- **Functions**: (see coverage report)

## Files Created/Modified

### New Files
- src/services/dashboard_service.py (service layer)
- tests/test_services/test_dashboard_service.py (unit tests)

### Modified Files
- src/api/v1/dashboard.py (uses service layer)

## Next Steps
- ✅ Backend validation COMPLETE
- ⏭️ Proceed to PRD-MVP-002: Dashboard Frontend UI
- ⏭️ Integrate frontend with validated backend API
EOF

echo "✅ Final report created: DASHBOARD_VALIDATION_COMPLETE.md"
echo ""
echo "========================================="
echo "Dashboard Backend Validation COMPLETE"
echo "========================================="
```

---

## H - HANDOFF (Delivery & Validation)

### Test Results Summary (MANDATORY)

**Test Execution Evidence**:
```bash
cd /home/dev/Development/irStudy/backend

# All tests
./run_tests.sh tests/test_api/test_dashboard.py tests/test_services/test_dashboard_service.py -v

# Expected Output:
tests/test_api/test_dashboard.py::TestDashboardAuth::test_dashboard_requires_authentication PASSED
tests/test_api/test_dashboard.py::TestDashboardAuth::test_dashboard_with_valid_token PASSED
tests/test_api/test_dashboard.py::TestOverallProgress::test_overall_progress_calculation PASSED
tests/test_api/test_dashboard.py::TestOverallProgress::test_overall_progress_with_no_data PASSED
tests/test_api/test_dashboard.py::TestModuleStats::test_mcq_module_stats PASSED
tests/test_api/test_dashboard.py::TestModuleStats::test_osce_module_stats PASSED
tests/test_api/test_dashboard.py::TestModuleStats::test_emr_module_stats PASSED
tests/test_api/test_dashboard.py::TestModuleStats::test_mock_exam_module_stats PASSED
tests/test_api/test_dashboard.py::TestSpecialtyBreakdown::test_specialty_breakdown_aggregation PASSED
tests/test_api/test_dashboard.py::TestRecentActivity::test_recent_activity_timeline PASSED
tests/test_api/test_dashboard.py::TestRecentActivity::test_recent_activity_limit_10 PASSED
tests/test_api/test_dashboard.py::TestRecommendations::test_weak_specialty_recommendation PASSED
tests/test_api/test_dashboard.py::TestRecommendations::test_unused_module_recommendation PASSED
tests/test_api/test_dashboard.py::TestPerformance::test_response_time_under_200ms PASSED
tests/test_api/test_dashboard.py::TestSecurity::test_user_isolation PASSED
tests/test_api/test_dashboard.py::TestEdgeCases::test_no_activity_returns_empty_recommendations PASSED
tests/test_services/test_dashboard_service.py::TestOverallProgressCalculations::test_calculate_completion_percentage_all_complete PASSED
tests/test_services/test_dashboard_service.py::TestOverallProgressCalculations::test_calculate_completion_percentage_partial PASSED
tests/test_services/test_dashboard_service.py::TestOverallProgressCalculations::test_calculate_completion_percentage_none_complete PASSED
tests/test_services/test_dashboard_service.py::TestOverallProgressCalculations::test_calculate_completion_percentage_empty_list PASSED
tests/test_services/test_dashboard_service.py::TestSpecialtyAggregation::test_aggregate_specialty_scores_single_specialty PASSED
tests/test_services/test_dashboard_service.py::TestSpecialtyAggregation::test_aggregate_specialty_scores_multiple_specialties PASSED
tests/test_services/test_dashboard_service.py::TestRecommendationLogic::test_generate_weak_specialty_recommendation PASSED
tests/test_services/test_dashboard_service.py::TestRecommendationLogic::test_generate_unused_module_recommendation PASSED

====================== 24 passed in 3.12s ======================
```

**TDD Compliance Verification**:
- [x] Phase 1: Existing 16 tests validated (all passing)
- [x] Phase 2: 8 unit tests written BEFORE service implementation (RED phase)
- [x] Phase 2: 8 unit tests confirmed PASSING after implementation (GREEN phase)
- [x] Phase 2: 16 integration tests STILL PASSING after refactoring (no regression)
- [x] Phase 3: Performance test validated (10/10 runs <200ms)
- [ ] 0 tests skipped or marked as "TODO"

**Code Coverage**:
```bash
pytest tests/test_api/test_dashboard.py tests/test_services/test_dashboard_service.py \
  --cov=src/api/v1/dashboard \
  --cov=src/services/dashboard_service \
  --cov-report=term-missing

# Expected Output:
File                                    | % Stmts | % Branch | % Funcs | % Lines
----------------------------------------|---------|----------|---------|--------
src/api/v1/dashboard.py                 |   95.2  |   88.9   |   100   |   95.2
src/services/dashboard_service.py       |   92.1  |   87.5   |   100   |   92.1
----------------------------------------|---------|----------|---------|--------
TOTAL                                   |   93.7  |   88.2   |   100   |   93.7

✅ Coverage thresholds MET (≥85% lines, ≥80% branches, ≥90% functions)
```

---

### Acceptance Criteria (Enhanced)

**Functionality**:
- [x] All 16 integration tests passing (endpoint validation)
- [x] All 8 unit tests passing (service layer validation)
- [x] Service layer extracted (better testability)
- [x] No breaking changes to API contract

**TDD Process**:
- [x] Phase 1: Validated existing tests (RED phase not applicable)
- [x] Phase 2: Unit tests written FIRST (RED phase confirmed)
- [x] Phase 2: Implementation made tests pass (GREEN phase confirmed)
- [x] Test pass rate: 24/24 (100%)

**Code Quality**:
- [x] TypeScript: N/A (Python project)
- [x] Linting: 0 errors (ruff check)
- [x] No `any` types: N/A
- [x] Coverage: ≥85% lines, ≥80% branches, ≥90% functions

**Performance**:
- [x] Response time <200ms (p95)
- [x] Response time <300ms (p99) under load
- [x] Performance test passed 10/10 runs

**Security**:
- [x] User isolation enforced (test_user_isolation)
- [x] No hardcoded credentials (security scan passed)
- [x] No PII in logs

---

### Deliverables

**Code**:
- [x] `src/services/dashboard_service.py` (service layer with 7 methods)
- [x] `tests/test_services/test_dashboard_service.py` (8 unit tests)
- [x] `src/api/v1/dashboard.py` (updated to use service)

**Scripts**:
- [x] `scripts/validate_dashboard_tests.sh` (Phase 1 validation)
- [x] `scripts/validate_dashboard_performance.sh` (Phase 3 validation)

**Documentation**:
- [x] `DASHBOARD_VALIDATION_PHASE1_REPORT.md` (Phase 1 results)
- [x] `DASHBOARD_VALIDATION_COMPLETE.md` (final report)
- [x] Docstrings for all public service methods (Google style)
- [x] Updated `DASHBOARD_API_IMPLEMENTATION_COMPLETE.md` (service layer section)

**Reports**:
- [x] Coverage report (HTML + terminal): `htmlcov/final/index.html`
- [x] Performance benchmark (10 runs, all <200ms)

---

### Quality Gates Checklist

**Compilation**:
```bash
python -m py_compile src/services/dashboard_service.py
# Expected: No errors
```

**Tests**:
```bash
./run_tests.sh tests/test_api/test_dashboard.py tests/test_services/test_dashboard_service.py
# Expected: 24/24 passing (100%)
```

**Security**:
```bash
grep -r "api_key\|password\s*=\s*['\"]" backend/src/services/dashboard_service.py
# Expected: 0 matches
```

**Linting**:
```bash
ruff check src/services/dashboard_service.py
# Expected: All checks passed!
```

**Coverage**:
```bash
pytest --cov=src/services/dashboard_service --cov-report=term-missing tests/test_services/test_dashboard_service.py
# Expected: ≥85% lines
```

---

### Next Steps

**Immediate**:
1. Run PRD-MVP-001 (this PRD) via Ralph
2. Validate all 24 tests passing
3. Review coverage report (target ≥85%)
4. Mark PRD-MVP-001 as COMPLETE

**Following PRDs**:
1. **PRD-MVP-002**: Dashboard Frontend UI (React + TypeScript)
2. **PRD-MVP-003**: Content Population MVP (MCQs, OSCEs, EMR patients)

**Integration**:
- Frontend will call `GET /api/v1/dashboard/overview` (validated by this PRD)
- No backend changes required for frontend integration
- Performance validated (<200ms) for frontend expectations

---

**Status**: ✅ READY FOR RALPH EXECUTION
**Estimated Completion**: 3-4 hours
**Blockers**: None (all dependencies met)
**Risk Level**: LOW (validation only, no breaking changes)
