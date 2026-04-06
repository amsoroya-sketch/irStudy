# PRD-EMR-003: Implement Missing EMR Dashboard Endpoints

**Status**: READY FOR IMPLEMENTATION
**Priority**: P0 (CRITICAL - Blocks EMR dashboard frontend)
**Estimated Time**: 4-5 hours
**Created**: 2026-04-06
**Format**: T-RALPH v2.1 (Test-First Development)
**Depends On**: PRD-EMR-001 (Models) + PRD-EMR-002 (Router Consolidation)

## Multi-Agent Assignment

**Primary Agent**: `python-backend-developer`
- **Role**: Implementation (3 endpoints, service layer methods, Pydantic schemas)
- **Deliverables**: 3 working endpoints, 3 service methods, 9 passing tests

**Secondary Agent**: `testing-qa-expert`
- **Role**: QA validation (test coverage, edge cases, performance)
- **Deliverables**: Test coverage report (≥70%), performance validation (<300ms p95)

**Handoff Procedure**:
1. `python-backend-developer` implements endpoints → Runs all 9 tests (GREEN)
2. `testing-qa-expert` validates test quality → Checks coverage, edge cases, performance
3. Both agents approve → Phase 3 COMPLETE

---

## Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2026-04-06 | Initial PRD - Implement 3 missing dashboard endpoints | PM Agent |

---

## Table of Contents

1. [T - TESTS (9 Tests Total)](#t---tests-9-tests-total)
2. [R - REQUEST (User Story)](#r---request-user-story)
3. [A - ARCHITECTURE (Current vs Target)](#a---architecture-current-vs-target)
4. [L - LOOP (TDD Workflow)](#l---loop-tdd-workflow)
5. [P - PLAN (Implementation Steps)](#p---plan-implementation-steps)
6. [H - HANDOFF (Validation & Rollback)](#h---handoff-validation--rollback)

---

# T - TESTS (9 Tests Total)

**CRITICAL**: All tests MUST be written BEFORE implementation.
**TDD Workflow**: RED (tests fail) → GREEN (tests pass) → REFACTOR (maintain 100% pass rate)

## Test File Location

```
backend/tests/test_emr_dashboard_endpoints.py
```

## Test 1: GET `/progress/dashboard/emr` Returns 200 OK

**Purpose**: Verify EMR dashboard metrics endpoint exists and returns correct data structure

```python
"""
Test: GET /api/v1/progress/dashboard/emr returns 200 OK with EMR metrics

EXPECTED BEHAVIOR:
- Returns 200 OK status code
- Returns JSON with EMR metrics (total_sessions, avg_score, etc.)
- Data scoped to current user only (privacy check)

TDD PHASE: RED (will fail until endpoint implemented)
"""

import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.auth.security import create_access_token
from src.db.models import User, EMRSession, MockPatient
from src.db.base import get_db
from datetime import datetime, timedelta
from uuid import uuid4

client = TestClient(app)

def test_get_emr_dashboard_metrics_returns_200(db_session):
    """Test GET /progress/dashboard/emr returns 200 OK"""
    # Create test user
    user = User(
        id=1,
        email="test@test.com",
        password_hash="hashed",
        full_name="Test User",
        role="student"
    )
    db_session.add(user)
    db_session.commit()

    # Create test EMR sessions
    patient = MockPatient(
        patient_id=uuid4(),
        full_name="Test Patient",
        mrn="MRN123",
        age=45,
        gender="Male",
        specialty="Cardiology",
        difficulty="intermediate"
    )
    db_session.add(patient)
    db_session.commit()

    # Create 3 completed sessions
    for i in range(3):
        session = EMRSession(
            session_id=uuid4(),
            user_id=user.id,
            patient_id=patient.patient_id,
            emr_system="epic",
            specialty="Cardiology",
            difficulty="intermediate",
            started_at=datetime.utcnow() - timedelta(hours=i+1),
            submitted_at=datetime.utcnow() - timedelta(hours=i),
            validation_score=75.0 + i*5,  # 75, 80, 85
            elapsed_time_seconds=1200
        )
        db_session.add(session)

    # Create 1 in-progress session
    session = EMRSession(
        session_id=uuid4(),
        user_id=user.id,
        patient_id=patient.patient_id,
        emr_system="cerner",
        specialty="Cardiology",
        difficulty="intermediate",
        started_at=datetime.utcnow(),
        submitted_at=None,  # Not submitted
        validation_score=None,
        elapsed_time_seconds=None
    )
    db_session.add(session)
    db_session.commit()

    # Create JWT token
    token = create_access_token(data={"sub": "test@test.com", "user_id": 1})
    headers = {"Authorization": f"Bearer {token}"}

    # Call endpoint
    response = client.get("/api/v1/progress/dashboard/emr", headers=headers)

    # Assertions
    assert response.status_code == 200, \
        f"Expected 200, got {response.status_code}: {response.text}"

    data = response.json()

    # Verify data structure
    assert "total_sessions" in data, "Missing total_sessions field"
    assert "completed_sessions" in data, "Missing completed_sessions field"
    assert "in_progress_sessions" in data, "Missing in_progress_sessions field"
    assert "avg_validation_score" in data, "Missing avg_validation_score field"
    assert "avg_typing_wpm" in data, "Missing avg_typing_wpm field"
    assert "improvement_percentage" in data, "Missing improvement_percentage field"
    assert "ahpra_compliance_rate" in data, "Missing ahpra_compliance_rate field"
    assert "total_time_spent_seconds" in data, "Missing total_time_spent_seconds field"
    assert "epic_sessions" in data, "Missing epic_sessions field"
    assert "cerner_sessions" in data, "Missing cerner_sessions field"
    assert "specialty_stats" in data, "Missing specialty_stats field"

    # Verify values
    assert data["total_sessions"] == 4, f"Expected 4 total sessions, got {data['total_sessions']}"
    assert data["completed_sessions"] == 3, f"Expected 3 completed, got {data['completed_sessions']}"
    assert data["in_progress_sessions"] == 1, f"Expected 1 in progress, got {data['in_progress_sessions']}"
    assert data["avg_validation_score"] == 80.0, \
        f"Expected avg 80.0 (mean of 75, 80, 85), got {data['avg_validation_score']}"
    assert data["epic_sessions"] == 3, f"Expected 3 Epic sessions, got {data['epic_sessions']}"
    assert data["cerner_sessions"] == 1, f"Expected 1 Cerner session, got {data['cerner_sessions']}"
    assert data["total_time_spent_seconds"] == 3600, \
        f"Expected 3600 seconds (3 sessions × 1200s), got {data['total_time_spent_seconds']}"

    # Verify specialty stats
    assert len(data["specialty_stats"]) == 1, \
        f"Expected 1 specialty (Cardiology), got {len(data['specialty_stats'])}"
    assert data["specialty_stats"][0]["specialty"] == "Cardiology"
    assert data["specialty_stats"][0]["session_count"] == 4
    assert data["specialty_stats"][0]["avg_score"] == 80.0  # Avg of completed sessions
```

## Test 2: GET `/progress/weekly-trends/unified` Returns 200 OK

**Purpose**: Verify unified weekly trends endpoint returns MCQ + OSCE + EMR data

```python
"""
Test: GET /api/v1/progress/weekly-trends/unified returns 200 OK

EXPECTED BEHAVIOR:
- Returns 200 OK status code
- Returns array of WeeklyTrend objects (last N weeks)
- Each trend has mcq_accuracy, osce_avg_score, emr_avg_score
- Accepts weeks query parameter (default 12)

TDD PHASE: RED (will fail until endpoint implemented)
"""

def test_get_unified_weekly_trends_returns_200(db_session):
    """Test GET /progress/weekly-trends/unified returns 200 OK"""
    # Create test user
    user = User(
        id=2,
        email="student@test.com",
        password_hash="hashed",
        full_name="Student Test",
        role="student"
    )
    db_session.add(user)
    db_session.commit()

    # Create JWT token
    token = create_access_token(data={"sub": "student@test.com", "user_id": 2})
    headers = {"Authorization": f"Bearer {token}"}

    # Call endpoint with weeks=12 parameter
    response = client.get(
        "/api/v1/progress/weekly-trends/unified",
        params={"weeks": 12},
        headers=headers
    )

    # Assertions
    assert response.status_code == 200, \
        f"Expected 200, got {response.status_code}: {response.text}"

    data = response.json()

    # Verify response structure
    assert "trends" in data, "Missing trends field in response"
    assert isinstance(data["trends"], list), "trends should be an array"

    # Should return up to 12 weeks of data (may be less if no data)
    assert len(data["trends"]) <= 12, \
        f"Expected max 12 weeks, got {len(data['trends'])}"

    # If data exists, verify structure
    if len(data["trends"]) > 0:
        trend = data["trends"][0]
        assert "week_start" in trend, "Missing week_start field"
        assert "mcq_accuracy" in trend, "Missing mcq_accuracy field"
        assert "osce_avg_score" in trend, "Missing osce_avg_score field"
        assert "emr_avg_score" in trend, "Missing emr_avg_score field"
        assert "mcq_attempts" in trend, "Missing mcq_attempts field"
        assert "osce_completions" in trend, "Missing osce_completions field"
        assert "emr_sessions" in trend, "Missing emr_sessions field"

        # Verify types (can be null if no data for that activity type)
        assert isinstance(trend["mcq_attempts"], int)
        assert isinstance(trend["osce_completions"], int)
        assert isinstance(trend["emr_sessions"], int)
```

## Test 3: GET `/progress/weak-areas/emr` Returns 200 OK

**Purpose**: Verify EMR weak areas endpoint identifies specialties below target

```python
"""
Test: GET /api/v1/progress/weak-areas/emr returns 200 OK

EXPECTED BEHAVIOR:
- Returns 200 OK status code
- Returns array of WeakArea objects (specialties with low avg scores)
- Sorted by gap_to_target (worst first)
- Accepts limit query parameter (default 5)

TDD PHASE: RED (will fail until endpoint implemented)
"""

def test_get_emr_weak_areas_returns_200(db_session):
    """Test GET /progress/weak-areas/emr returns 200 OK"""
    # Create test user
    user = User(
        id=3,
        email="weakareas@test.com",
        password_hash="hashed",
        full_name="Weak Areas Test",
        role="student"
    )
    db_session.add(user)
    db_session.commit()

    # Create test patients for different specialties
    specialties = ["Cardiology", "Respiratory", "Psychiatry"]
    for specialty in specialties:
        patient = MockPatient(
            patient_id=uuid4(),
            full_name=f"{specialty} Patient",
            mrn=f"MRN{specialty[:3].upper()}",
            age=50,
            gender="Male",
            specialty=specialty,
            difficulty="intermediate"
        )
        db_session.add(patient)
        db_session.commit()

        # Create EMR sessions with different avg scores
        if specialty == "Cardiology":
            scores = [85.0, 90.0, 88.0]  # Avg 87.67 (STRONG)
        elif specialty == "Respiratory":
            scores = [60.0, 65.0, 62.0]  # Avg 62.33 (WEAK)
        else:  # Psychiatry
            scores = [68.0, 72.0, 70.0]  # Avg 70.0 (BORDERLINE)

        for score in scores:
            session = EMRSession(
                session_id=uuid4(),
                user_id=user.id,
                patient_id=patient.patient_id,
                emr_system="epic",
                specialty=specialty,
                difficulty="intermediate",
                started_at=datetime.utcnow() - timedelta(days=7),
                submitted_at=datetime.utcnow() - timedelta(days=6),
                validation_score=score,
                elapsed_time_seconds=1200
            )
            db_session.add(session)

    db_session.commit()

    # Create JWT token
    token = create_access_token(data={"sub": "weakareas@test.com", "user_id": 3})
    headers = {"Authorization": f"Bearer {token}"}

    # Call endpoint with limit=5
    response = client.get(
        "/api/v1/progress/weak-areas/emr",
        params={"limit": 5},
        headers=headers
    )

    # Assertions
    assert response.status_code == 200, \
        f"Expected 200, got {response.status_code}: {response.text}"

    data = response.json()

    # Verify response structure
    assert "weak_areas" in data, "Missing weak_areas field in response"
    assert isinstance(data["weak_areas"], list), "weak_areas should be an array"

    # Should return specialties below 70% threshold
    # Expected: Respiratory (62.33%) and Psychiatry (70.0%) - NOT Cardiology (87.67%)
    assert len(data["weak_areas"]) >= 1, \
        f"Expected at least 1 weak area (Respiratory <70%), got {len(data['weak_areas'])}"

    # Verify structure
    if len(data["weak_areas"]) > 0:
        weak_area = data["weak_areas"][0]
        assert "specialty" in weak_area, "Missing specialty field"
        assert "session_count" in weak_area, "Missing session_count field"
        assert "avg_score" in weak_area, "Missing avg_score field"
        assert "gap_to_target" in weak_area, "Missing gap_to_target field"
        assert "recommended_practice_count" in weak_area, "Missing recommended_practice_count field"

        # Verify Respiratory is first (worst score)
        assert weak_area["specialty"] == "Respiratory", \
            f"Expected Respiratory to be weakest area, got {weak_area['specialty']}"
        assert weak_area["avg_score"] < 70.0, \
            f"Expected avg_score <70%, got {weak_area['avg_score']}"
        assert weak_area["gap_to_target"] > 0, \
            f"Expected positive gap_to_target, got {weak_area['gap_to_target']}"
```

## Test 4-6: Service Layer Tests

```python
"""
Tests 4-6: Service layer methods for EMR dashboard analytics

PURPOSE: Test ProgressAnalytics service methods independently of FastAPI

TDD PHASE: RED (will fail until service methods implemented)
"""

from src.services.progress_analytics import ProgressAnalytics

def test_progress_analytics_get_emr_metrics(db_session):
    """Test ProgressAnalytics.get_emr_dashboard_metrics() method"""
    # Create test data (same as Test 1)
    user = User(id=10, email="analytics@test.com", password_hash="hashed", full_name="Analytics Test", role="student")
    db_session.add(user)
    db_session.commit()

    patient = MockPatient(patient_id=uuid4(), full_name="Test Patient", mrn="MRN001", age=45, gender="Male", specialty="Cardiology", difficulty="intermediate")
    db_session.add(patient)
    db_session.commit()

    session = EMRSession(
        session_id=uuid4(),
        user_id=user.id,
        patient_id=patient.patient_id,
        emr_system="epic",
        specialty="Cardiology",
        difficulty="intermediate",
        started_at=datetime.utcnow() - timedelta(hours=2),
        submitted_at=datetime.utcnow() - timedelta(hours=1),
        validation_score=85.0,
        elapsed_time_seconds=1200
    )
    db_session.add(session)
    db_session.commit()

    # Call service method
    metrics = ProgressAnalytics.get_emr_dashboard_metrics(db_session, user_id=10)

    # Assertions
    assert metrics is not None, "Service method should return metrics dict"
    assert metrics["total_sessions"] == 1
    assert metrics["completed_sessions"] == 1
    assert metrics["avg_validation_score"] == 85.0
    assert metrics["epic_sessions"] == 1
    assert metrics["cerner_sessions"] == 0


def test_progress_analytics_get_unified_trends(db_session):
    """Test ProgressAnalytics.get_unified_weekly_trends() method"""
    user = User(id=11, email="trends@test.com", password_hash="hashed", full_name="Trends Test", role="student")
    db_session.add(user)
    db_session.commit()

    # Call service method
    trends = ProgressAnalytics.get_unified_weekly_trends(db_session, user_id=11, weeks=12)

    # Assertions
    assert trends is not None, "Service method should return trends list"
    assert isinstance(trends, list)
    assert len(trends) <= 12


def test_progress_analytics_get_emr_weak_areas(db_session):
    """Test ProgressAnalytics.get_emr_weak_areas() method"""
    user = User(id=12, email="weakareas2@test.com", password_hash="hashed", full_name="Weak Areas 2", role="student")
    db_session.add(user)
    db_session.commit()

    # Call service method
    weak_areas = ProgressAnalytics.get_emr_weak_areas(db_session, user_id=12, threshold=70.0, limit=5)

    # Assertions
    assert weak_areas is not None, "Service method should return weak areas list"
    assert isinstance(weak_areas, list)
    assert len(weak_areas) <= 5
```

## Test 7-9: Edge Cases & Security

```python
"""
Tests 7-9: Edge cases, error handling, and security

TDD PHASE: GREEN (should pass after implementation)
"""

def test_emr_dashboard_requires_authentication():
    """Test that endpoints require valid JWT token"""
    # No token
    response = client.get("/api/v1/progress/dashboard/emr")
    assert response.status_code == 401, "Should return 401 Unauthorized without token"

    # Invalid token
    headers = {"Authorization": "Bearer invalid-token"}
    response = client.get("/api/v1/progress/dashboard/emr", headers=headers)
    assert response.status_code == 401, "Should return 401 with invalid token"


def test_emr_dashboard_user_data_isolation():
    """Test that users only see their own EMR data (privacy check)"""
    # Create user 1 with sessions
    user1 = User(id=20, email="user1@test.com", password_hash="hashed", full_name="User 1", role="student")
    db_session.add(user1)

    # Create user 2 with NO sessions
    user2 = User(id=21, email="user2@test.com", password_hash="hashed", full_name="User 2", role="student")
    db_session.add(user2)
    db_session.commit()

    # Add session for user 1 only
    patient = MockPatient(patient_id=uuid4(), full_name="Test Patient", mrn="MRN777", age=45, gender="Male", specialty="Cardiology", difficulty="intermediate")
    db_session.add(patient)
    db_session.commit()

    session = EMRSession(
        session_id=uuid4(),
        user_id=user1.id,  # Belongs to user 1
        patient_id=patient.patient_id,
        emr_system="epic",
        specialty="Cardiology",
        difficulty="intermediate",
        started_at=datetime.utcnow() - timedelta(hours=2),
        submitted_at=datetime.utcnow() - timedelta(hours=1),
        validation_score=85.0,
        elapsed_time_seconds=1200
    )
    db_session.add(session)
    db_session.commit()

    # User 2 logs in and requests dashboard
    token = create_access_token(data={"sub": "user2@test.com", "user_id": 21})
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/v1/progress/dashboard/emr", headers=headers)

    assert response.status_code == 200
    data = response.json()

    # User 2 should see ZERO sessions (not user 1's session)
    assert data["total_sessions"] == 0, \
        f"User 2 should see 0 sessions (data isolation), got {data['total_sessions']}"
    assert data["completed_sessions"] == 0
    assert data["avg_validation_score"] == 0.0 or data["avg_validation_score"] is None


def test_weekly_trends_default_weeks_parameter():
    """Test that weeks parameter defaults to 12 if not provided"""
    token = create_access_token(data={"sub": "student@test.com", "user_id": 1})
    headers = {"Authorization": f"Bearer {token}"}

    # Call without weeks parameter
    response = client.get("/api/v1/progress/weekly-trends/unified", headers=headers)

    assert response.status_code == 200
    data = response.json()

    # Should return up to 12 weeks by default
    assert len(data["trends"]) <= 12
```

---

# R - REQUEST (User Story)

## Problem Statement

**Current Issue**: Frontend EMR dashboard cannot load because 3 critical API endpoints are missing:

1. **GET `/api/v1/progress/dashboard/emr`** - Returns EMR-specific metrics
   - **Error**: `404 Not Found`
   - **Frontend expects**: `EMRMetrics` object with 11 fields
   - **Impact**: Dashboard shows loading spinner indefinitely

2. **GET `/api/v1/progress/weekly-trends/unified`** - Returns MCQ + OSCE + EMR combined trends
   - **Error**: `404 Not Found`
   - **Frontend expects**: Array of `WeeklyTrend` objects (12 weeks)
   - **Impact**: Progress chart component fails to render

3. **GET `/api/v1/progress/weak-areas/emr`** - Returns EMR weak areas (specialties below 70%)
   - **Error**: `404 Not Found`
   - **Frontend expects**: Array of `WeakArea` objects (top 5)
   - **Impact**: "Areas for Improvement" panel shows error

**Root Cause**: These endpoints were planned but never implemented. The frontend was built assuming they exist (see `frontend/src/hooks/useEMRDashboardData.ts`).

**Evidence from Backend Logs**:
```
[ERROR] 2026-04-06 10:23:45 - GET /api/v1/progress/dashboard/emr - 404 Not Found
[ERROR] 2026-04-06 10:23:46 - GET /api/v1/progress/weekly-trends/unified - 404 Not Found
[ERROR] 2026-04-06 10:23:47 - GET /api/v1/progress/weak-areas/emr - 404 Not Found
```

## User Story

**As a** medical student using the EMR practice dashboard,
**I want** to see my EMR performance metrics, weekly trends, and weak areas,
**So that** I can track my progress and identify areas needing more practice.

**Acceptance Criteria**:
- [ ] GET `/api/v1/progress/dashboard/emr` returns 200 OK with EMR metrics
  - [ ] Returns all 11 required fields (total_sessions, avg_score, specialty_stats, etc.)
  - [ ] Data scoped to current user only (privacy check)
  - [ ] Response time <300ms (p95)

- [ ] GET `/api/v1/progress/weekly-trends/unified` returns 200 OK with unified trends
  - [ ] Returns array of WeeklyTrend objects (MCQ + OSCE + EMR)
  - [ ] Accepts `weeks` query parameter (default 12)
  - [ ] Handles cases where user has no activity (returns 0s, not errors)

- [ ] GET `/api/v1/progress/weak-areas/emr` returns 200 OK with weak areas
  - [ ] Returns specialties with avg_score < 70%
  - [ ] Sorted by gap_to_target (worst first)
  - [ ] Accepts `limit` query parameter (default 5)
  - [ ] Includes recommended_practice_count

- [ ] All 9 tests pass (100% pass rate)
- [ ] No regressions in existing progress endpoints
- [ ] Frontend dashboard loads successfully

## Success Metrics

| Metric | Current | Target | Validation |
|--------|---------|--------|------------|
| Missing endpoints | 3 | 0 | All return 200 OK |
| Test pass rate | N/A | 100% (9/9 tests) | pytest exit code 0 |
| Dashboard load time | ∞ (stuck) | <1s | Frontend test |
| Response time (p95) | N/A | <300ms | Load testing |
| Data privacy | UNTESTED | 100% isolation | Test 8 passes |

---

# A - ARCHITECTURE (Current vs Target)

## Current Architecture (BROKEN)

```
frontend/src/hooks/useEMRDashboardData.ts
├── Query 1: GET /progress/dashboard/emr ❌ 404 Not Found
├── Query 2: GET /emr/sessions ✅ Works (Phase 2)
├── Query 3: GET /progress/weekly-trends/unified ❌ 404 Not Found
└── Query 4: GET /progress/weak-areas/emr ❌ 404 Not Found

backend/src/api/v1/progress.py (INCOMPLETE)
├── GET /progress/dashboard ✅ Exists (MCQ + OSCE + Study Cards)
├── GET /progress/specialty/{name} ✅ Exists
├── GET /progress/weak-areas ✅ Exists (general, not EMR-specific)
├── GET /progress/trends/weekly ✅ Exists (general, not unified)
└── ❌ MISSING: 3 EMR endpoints

backend/src/services/progress_analytics.py (INCOMPLETE)
├── get_mcq_accuracy() ✅ Exists
├── get_specialty_breakdown() ✅ Exists
├── get_weak_areas() ✅ Exists (general)
├── get_weekly_trends() ✅ Exists (general)
└── ❌ MISSING: 3 EMR methods
```

**Problems**:
1. No EMR-specific dashboard metrics endpoint
2. No unified trends endpoint (MCQ + OSCE + EMR combined)
3. No EMR-specific weak areas endpoint
4. Service layer missing EMR analytics methods

## Target Architecture (COMPLETE)

```
backend/src/api/v1/progress.py (EXTENDED)
├── GET /progress/dashboard (existing)
├── GET /progress/dashboard/emr (NEW) ← Implements this PRD
├── GET /progress/specialty/{name} (existing)
├── GET /progress/weak-areas (existing)
├── GET /progress/weak-areas/emr (NEW) ← Implements this PRD
├── GET /progress/trends/weekly (existing)
└── GET /progress/weekly-trends/unified (NEW) ← Implements this PRD

backend/src/services/progress_analytics.py (EXTENDED)
├── get_mcq_accuracy() (existing)
├── get_emr_dashboard_metrics() (NEW) ← Service layer method
├── get_specialty_breakdown() (existing)
├── get_weak_areas() (existing)
├── get_emr_weak_areas() (NEW) ← Service layer method
├── get_weekly_trends() (existing)
└── get_unified_weekly_trends() (NEW) ← Service layer method

backend/src/schemas/progress.py (EXTENDED)
├── DashboardResponse (existing)
├── EMRDashboardResponse (NEW) ← Pydantic schema
├── UnifiedWeeklyTrendsResponse (NEW) ← Pydantic schema
├── EMRWeakAreasResponse (NEW) ← Pydantic schema
├── EMRMetrics (NEW) ← Sub-schema
├── WeeklyTrend (existing, may need extension)
└── WeakArea (existing, may need extension)
```

**Benefits**:
- ✅ Frontend queries succeed (200 OK, not 404)
- ✅ Dashboard loads in <1s (parallel queries)
- ✅ Clean separation: Router → Service → Database
- ✅ Reusable service methods for future endpoints
- ✅ Type-safe with Pydantic schemas

## Database Queries

### Query 1: EMR Dashboard Metrics

```sql
-- Total sessions
SELECT COUNT(*) FROM emr_sessions WHERE user_id = ?;

-- Completed sessions
SELECT COUNT(*) FROM emr_sessions WHERE user_id = ? AND submitted_at IS NOT NULL;

-- In-progress sessions
SELECT COUNT(*) FROM emr_sessions WHERE user_id = ? AND submitted_at IS NULL;

-- Avg validation score
SELECT AVG(validation_score) FROM emr_sessions
WHERE user_id = ? AND submitted_at IS NOT NULL;

-- Avg typing WPM (from SOAP notes)
SELECT AVG(typing_wpm) FROM emr_soap_notes esn
JOIN emr_sessions es ON esn.session_id = es.session_id
WHERE es.user_id = ?;

-- Epic vs Cerner sessions
SELECT emr_system, COUNT(*) FROM emr_sessions WHERE user_id = ? GROUP BY emr_system;

-- Specialty stats
SELECT specialty, COUNT(*) as session_count, AVG(validation_score) as avg_score
FROM emr_sessions WHERE user_id = ? GROUP BY specialty;

-- Total time spent
SELECT SUM(elapsed_time_seconds) FROM emr_sessions WHERE user_id = ?;
```

### Query 2: Unified Weekly Trends

```sql
-- MCQ accuracy per week
SELECT
  DATE_TRUNC('week', created_at) as week_start,
  AVG(CASE WHEN is_correct THEN 100.0 ELSE 0.0 END) as mcq_accuracy,
  COUNT(*) as mcq_attempts
FROM mcq_attempts WHERE user_id = ?
GROUP BY DATE_TRUNC('week', created_at)
ORDER BY week_start DESC LIMIT ?;

-- OSCE avg score per week
SELECT
  DATE_TRUNC('week', completed_at) as week_start,
  AVG(overall_score) as osce_avg_score,
  COUNT(*) as osce_completions
FROM osce_attempts WHERE user_id = ? AND completed_at IS NOT NULL
GROUP BY DATE_TRUNC('week', completed_at);

-- EMR avg score per week
SELECT
  DATE_TRUNC('week', submitted_at) as week_start,
  AVG(validation_score) as emr_avg_score,
  COUNT(*) as emr_sessions
FROM emr_sessions WHERE user_id = ? AND submitted_at IS NOT NULL
GROUP BY DATE_TRUNC('week', submitted_at);
```

### Query 3: EMR Weak Areas

```sql
SELECT
  specialty,
  COUNT(*) as session_count,
  AVG(validation_score) as avg_score,
  (70.0 - AVG(validation_score)) as gap_to_target,
  CEIL((70.0 - AVG(validation_score)) / 5.0) as recommended_practice_count
FROM emr_sessions
WHERE user_id = ? AND submitted_at IS NOT NULL
GROUP BY specialty
HAVING AVG(validation_score) < 70.0
ORDER BY avg_score ASC
LIMIT ?;
```

---

# L - LOOP (TDD Workflow)

## Phase 1: RED (Tests Fail) - Write Tests First

**Estimated Time**: 30 minutes

### Actions:
1. Create test file: `backend/tests/test_emr_dashboard_endpoints.py`
2. Copy all 9 test functions from T section
3. Create pytest fixtures for database session
4. Run tests:
   ```bash
   cd /home/dev/Development/irStudy/backend
   source venv/bin/activate
   pytest tests/test_emr_dashboard_endpoints.py -v
   ```

### Expected Result (RED):
```
FAILED test_get_emr_dashboard_metrics_returns_200 - 404 Not Found
FAILED test_get_unified_weekly_trends_returns_200 - 404 Not Found
FAILED test_get_emr_weak_areas_returns_200 - 404 Not Found
FAILED test_progress_analytics_get_emr_metrics - AttributeError: no method
FAILED test_progress_analytics_get_unified_trends - AttributeError: no method
FAILED test_progress_analytics_get_emr_weak_areas - AttributeError: no method
PASSED test_emr_dashboard_requires_authentication (may pass if decorator works)
FAILED test_emr_dashboard_user_data_isolation - 404 Not Found
FAILED test_weekly_trends_default_weeks_parameter - 404 Not Found
```

**Validation**: Tests 1-6, 8-9 MUST fail (RED phase confirmed).

---

## Phase 2: GREEN (Tests Pass) - Implement Endpoints

**Estimated Time**: 3 hours

### Sub-Phase 2A: Service Layer (1.5 hours)

**File**: `backend/src/services/progress_analytics.py`

**Actions**:
1. Add method `get_emr_dashboard_metrics(db, user_id) -> dict`
2. Add method `get_unified_weekly_trends(db, user_id, weeks=12) -> list`
3. Add method `get_emr_weak_areas(db, user_id, threshold=70.0, limit=5) -> list`
4. Run service layer tests:
   ```bash
   pytest tests/test_emr_dashboard_endpoints.py::test_progress_analytics_get_emr_metrics -v
   pytest tests/test_emr_dashboard_endpoints.py::test_progress_analytics_get_unified_trends -v
   pytest tests/test_emr_dashboard_endpoints.py::test_progress_analytics_get_emr_weak_areas -v
   ```
5. **Verify GREEN**: Tests 4-6 MUST pass

### Sub-Phase 2B: Pydantic Schemas (30 minutes)

**File**: `backend/src/schemas/progress.py`

**Actions**:
1. Add `EMRDashboardResponse` schema
2. Add `UnifiedWeeklyTrendsResponse` schema
3. Add `EMRWeakAreasResponse` schema
4. Add sub-schemas: `EMRMetrics`, `WeeklyTrend` (extend if needed), `WeakArea` (extend if needed)

### Sub-Phase 2C: Router Endpoints (1 hour)

**File**: `backend/src/api/v1/progress.py`

**Actions**:
1. Add endpoint: `@router.get("/dashboard/emr", response_model=EMRDashboardResponse)`
2. Add endpoint: `@router.get("/weekly-trends/unified", response_model=UnifiedWeeklyTrendsResponse)`
3. Add endpoint: `@router.get("/weak-areas/emr", response_model=EMRWeakAreasResponse)`
4. Run full test suite:
   ```bash
   pytest tests/test_emr_dashboard_endpoints.py -v
   ```

### Expected Result (GREEN):
```
PASSED test_get_emr_dashboard_metrics_returns_200
PASSED test_get_unified_weekly_trends_returns_200
PASSED test_get_emr_weak_areas_returns_200
PASSED test_progress_analytics_get_emr_metrics
PASSED test_progress_analytics_get_unified_trends
PASSED test_progress_analytics_get_emr_weak_areas
PASSED test_emr_dashboard_requires_authentication
PASSED test_emr_dashboard_user_data_isolation
PASSED test_weekly_trends_default_weeks_parameter

========================= 9 passed in 23.45s =========================
```

**Validation**: ALL 9 tests MUST pass (GREEN phase confirmed).

---

## Phase 3: REFACTOR (Cleanup) - Verify No Regressions

**Estimated Time**: 30 minutes

### Actions:
1. **Run full backend test suite**:
   ```bash
   pytest --cov=src --cov-report=term-missing -v
   ```

2. **Test frontend integration** (manual):
   ```bash
   # Start backend
   cd /home/dev/Development/irStudy/backend
   source venv/bin/activate
   set -a && source .env && set +a
   uvicorn src.main:app --reload --port 8001

   # In separate terminal, start frontend
   cd /home/dev/Development/irStudy/frontend
   npm run dev

   # Open browser: http://localhost:5173/dashboard
   # Check: EMR dashboard loads without errors
   # Check: Progress chart renders with data
   # Check: Weak areas panel shows recommendations
   ```

3. **Performance test** (response time <300ms):
   ```bash
   # Create test session
   TOKEN=$(curl -X POST http://localhost:8001/api/v1/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email":"student@test.com","password":"Student123!@#"}' \
     | jq -r '.access_token')

   # Test dashboard endpoint performance
   curl -w "@curl-format.txt" \
     -H "Authorization: Bearer $TOKEN" \
     "http://localhost:8001/api/v1/progress/dashboard/emr"
   # Expected: time_total < 0.300s
   ```

### Expected Result (REFACTOR):
```
✅ All tests pass (100% pass rate)
✅ No regressions in existing endpoints
✅ Frontend dashboard loads successfully
✅ Response time <300ms (p95)
✅ Type coverage: No mypy errors
```

**Validation Checklist**:
- [ ] All 9 dashboard tests pass
- [ ] Full test suite passes (100% pass rate)
- [ ] No uvicorn startup errors
- [ ] Frontend dashboard loads without 404 errors
- [ ] Response time meets <300ms target
- [ ] TypeScript compiles successfully (frontend)

---

# P - PLAN (Implementation Steps)

## File 1: Create Test File (Due to length constraints, showing abbreviated version)

**Path**: `backend/tests/test_emr_dashboard_endpoints.py`

**Action**: Create comprehensive test suite (9 tests from T section)

```python
"""
EMR Dashboard Endpoints Tests

PURPOSE: Verify 3 missing EMR dashboard endpoints work correctly:
- GET /progress/dashboard/emr
- GET /progress/weekly-trends/unified
- GET /progress/weak-areas/emr

TESTS (9 total):
1-3. Integration tests (FastAPI routes)
4-6. Service layer tests (ProgressAnalytics methods)
7-9. Edge cases (authentication, privacy, defaults)

TDD WORKFLOW: RED → GREEN → REFACTOR
Expected: Tests 1-6, 8-9 fail initially (RED phase)
After implementation: All 9 tests pass (GREEN phase)
"""

import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.auth.security import create_access_token
from src.db.models import User, EMRSession, MockPatient
from src.services.progress_analytics import ProgressAnalytics
from datetime import datetime, timedelta
from uuid import uuid4

client = TestClient(app)

# [Include all 9 test functions from T section above]
# Test 1: test_get_emr_dashboard_metrics_returns_200
# Test 2: test_get_unified_weekly_trends_returns_200
# Test 3: test_get_emr_weak_areas_returns_200
# Test 4: test_progress_analytics_get_emr_metrics
# Test 5: test_progress_analytics_get_unified_trends
# Test 6: test_progress_analytics_get_emr_weak_areas
# Test 7: test_emr_dashboard_requires_authentication
# Test 8: test_emr_dashboard_user_data_isolation
# Test 9: test_weekly_trends_default_weeks_parameter
```

---

## File 2: Extend Service Layer - Add EMR Analytics Methods

**Path**: `backend/src/services/progress_analytics.py`

**Action**: Add 3 new methods to `ProgressAnalytics` class

```python
# Add to existing ProgressAnalytics class

@staticmethod
def get_emr_dashboard_metrics(db: Session, user_id: int) -> dict:
    """
    Calculate EMR dashboard metrics for user.

    Args:
        db: Database session
        user_id: User ID

    Returns:
        dict: EMR metrics with 11 fields

    Example:
        {
            "total_sessions": 10,
            "completed_sessions": 8,
            "in_progress_sessions": 2,
            "avg_validation_score": 78.5,
            "avg_typing_wpm": 45.0,
            "improvement_percentage": 12.3,
            "ahpra_compliance_rate": 85.0,
            "total_time_spent_seconds": 9600,
            "epic_sessions": 5,
            "cerner_sessions": 5,
            "specialty_stats": [
                {"specialty": "Cardiology", "session_count": 4, "avg_score": 80.0},
                {"specialty": "Respiratory", "session_count": 3, "avg_score": 75.0}
            ]
        }
    """
    from src.db.models import EMRSession, EMRSOAPNote

    # Total sessions
    total_sessions = db.query(EMRSession).filter(EMRSession.user_id == user_id).count()

    if total_sessions == 0:
        return {
            "total_sessions": 0,
            "completed_sessions": 0,
            "in_progress_sessions": 0,
            "avg_validation_score": 0.0,
            "avg_typing_wpm": 0.0,
            "improvement_percentage": 0.0,
            "ahpra_compliance_rate": 0.0,
            "total_time_spent_seconds": 0,
            "epic_sessions": 0,
            "cerner_sessions": 0,
            "specialty_stats": []
        }

    # Completed sessions
    completed = db.query(EMRSession).filter(
        EMRSession.user_id == user_id,
        EMRSession.submitted_at.isnot(None)
    ).count()

    # In-progress sessions
    in_progress = total_sessions - completed

    # Avg validation score (completed sessions only)
    avg_score_result = db.query(func.avg(EMRSession.validation_score)).filter(
        EMRSession.user_id == user_id,
        EMRSession.submitted_at.isnot(None)
    ).scalar()
    avg_validation_score = round(float(avg_score_result or 0.0), 2)

    # Avg typing WPM (from SOAP notes)
    avg_typing_wpm_result = db.query(func.avg(EMRSOAPNote.typing_wpm)).join(
        EMRSession, EMRSOAPNote.session_id == EMRSession.session_id
    ).filter(
        EMRSession.user_id == user_id,
        EMRSOAPNote.typing_wpm.isnot(None)
    ).scalar()
    avg_typing_wpm = round(float(avg_typing_wpm_result or 0.0), 1)

    # Improvement percentage (compare first 3 vs last 3 sessions)
    first_3_sessions = db.query(func.avg(EMRSession.validation_score)).filter(
        EMRSession.user_id == user_id,
        EMRSession.submitted_at.isnot(None)
    ).order_by(EMRSession.submitted_at.asc()).limit(3).scalar()

    last_3_sessions = db.query(func.avg(EMRSession.validation_score)).filter(
        EMRSession.user_id == user_id,
        EMRSession.submitted_at.isnot(None)
    ).order_by(EMRSession.submitted_at.desc()).limit(3).scalar()

    if first_3_sessions and last_3_sessions and first_3_sessions > 0:
        improvement_percentage = round(
            ((last_3_sessions - first_3_sessions) / first_3_sessions) * 100,
            1
        )
    else:
        improvement_percentage = 0.0

    # AHPRA compliance rate (% of SOAP notes with ahpra_compliant=True)
    ahpra_compliant_count = db.query(func.count(EMRSOAPNote.id)).join(
        EMRSession, EMRSOAPNote.session_id == EMRSession.session_id
    ).filter(
        EMRSession.user_id == user_id,
        EMRSOAPNote.ahpra_compliant == True
    ).scalar()

    total_soap_notes = db.query(func.count(EMRSOAPNote.id)).join(
        EMRSession, EMRSOAPNote.session_id == EMRSession.session_id
    ).filter(
        EMRSession.user_id == user_id
    ).scalar()

    ahpra_compliance_rate = round(
        (ahpra_compliant_count / total_soap_notes * 100) if total_soap_notes > 0 else 0.0,
        1
    )

    # Total time spent
    total_time_result = db.query(func.sum(EMRSession.elapsed_time_seconds)).filter(
        EMRSession.user_id == user_id,
        EMRSession.elapsed_time_seconds.isnot(None)
    ).scalar()
    total_time_spent_seconds = int(total_time_result or 0)

    # Epic vs Cerner sessions
    emr_system_counts = db.query(
        EMRSession.emr_system,
        func.count(EMRSession.session_id)
    ).filter(
        EMRSession.user_id == user_id
    ).group_by(EMRSession.emr_system).all()

    epic_sessions = next((count for system, count in emr_system_counts if system == "epic"), 0)
    cerner_sessions = next((count for system, count in emr_system_counts if system == "cerner"), 0)

    # Specialty stats
    specialty_stats_raw = db.query(
        EMRSession.specialty,
        func.count(EMRSession.session_id).label("session_count"),
        func.avg(EMRSession.validation_score).label("avg_score")
    ).filter(
        EMRSession.user_id == user_id,
        EMRSession.submitted_at.isnot(None)
    ).group_by(EMRSession.specialty).all()

    specialty_stats = [
        {
            "specialty": specialty,
            "session_count": session_count,
            "avg_score": round(float(avg_score or 0.0), 2)
        }
        for specialty, session_count, avg_score in specialty_stats_raw
    ]

    return {
        "total_sessions": total_sessions,
        "completed_sessions": completed,
        "in_progress_sessions": in_progress,
        "avg_validation_score": avg_validation_score,
        "avg_typing_wpm": avg_typing_wpm,
        "improvement_percentage": improvement_percentage,
        "ahpra_compliance_rate": ahpra_compliance_rate,
        "total_time_spent_seconds": total_time_spent_seconds,
        "epic_sessions": epic_sessions,
        "cerner_sessions": cerner_sessions,
        "specialty_stats": specialty_stats
    }


@staticmethod
def get_unified_weekly_trends(db: Session, user_id: int, weeks: int = 12) -> list:
    """
    Calculate unified weekly trends (MCQ + OSCE + EMR).

    Args:
        db: Database session
        user_id: User ID
        weeks: Number of weeks to return (default 12)

    Returns:
        list: Array of WeeklyTrend objects

    Example:
        [
            {
                "week_start": "2026-03-31",
                "mcq_accuracy": 78.5,
                "osce_avg_score": 82.0,
                "emr_avg_score": 75.0,
                "mcq_attempts": 25,
                "osce_completions": 3,
                "emr_sessions": 2
            },
            ...
        ]
    """
    from src.db.models import MCQAttempt, OSCEAttempt, EMRSession

    # Calculate date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(weeks=weeks)

    # MCQ trends
    mcq_trends = db.query(
        func.date_trunc('week', MCQAttempt.created_at).label('week_start'),
        func.avg(case((MCQAttempt.is_correct == True, 100.0), else_=0.0)).label('mcq_accuracy'),
        func.count(MCQAttempt.id).label('mcq_attempts')
    ).filter(
        MCQAttempt.user_id == user_id,
        MCQAttempt.created_at >= start_date
    ).group_by(
        func.date_trunc('week', MCQAttempt.created_at)
    ).all()

    # OSCE trends
    osce_trends = db.query(
        func.date_trunc('week', OSCEAttempt.completed_at).label('week_start'),
        func.avg(OSCEAttempt.overall_score).label('osce_avg_score'),
        func.count(OSCEAttempt.id).label('osce_completions')
    ).filter(
        OSCEAttempt.user_id == user_id,
        OSCEAttempt.completed_at.isnot(None),
        OSCEAttempt.completed_at >= start_date
    ).group_by(
        func.date_trunc('week', OSCEAttempt.completed_at)
    ).all()

    # EMR trends
    emr_trends = db.query(
        func.date_trunc('week', EMRSession.submitted_at).label('week_start'),
        func.avg(EMRSession.validation_score).label('emr_avg_score'),
        func.count(EMRSession.session_id).label('emr_sessions')
    ).filter(
        EMRSession.user_id == user_id,
        EMRSession.submitted_at.isnot(None),
        EMRSession.submitted_at >= start_date
    ).group_by(
        func.date_trunc('week', EMRSession.submitted_at)
    ).all()

    # Merge trends by week_start
    trends_dict = {}

    for week_start, mcq_accuracy, mcq_attempts in mcq_trends:
        week_key = week_start.strftime("%Y-%m-%d")
        trends_dict[week_key] = {
            "week_start": week_key,
            "mcq_accuracy": round(float(mcq_accuracy), 2) if mcq_accuracy else None,
            "osce_avg_score": None,
            "emr_avg_score": None,
            "mcq_attempts": mcq_attempts,
            "osce_completions": 0,
            "emr_sessions": 0
        }

    for week_start, osce_avg_score, osce_completions in osce_trends:
        week_key = week_start.strftime("%Y-%m-%d")
        if week_key in trends_dict:
            trends_dict[week_key]["osce_avg_score"] = round(float(osce_avg_score), 2) if osce_avg_score else None
            trends_dict[week_key]["osce_completions"] = osce_completions
        else:
            trends_dict[week_key] = {
                "week_start": week_key,
                "mcq_accuracy": None,
                "osce_avg_score": round(float(osce_avg_score), 2) if osce_avg_score else None,
                "emr_avg_score": None,
                "mcq_attempts": 0,
                "osce_completions": osce_completions,
                "emr_sessions": 0
            }

    for week_start, emr_avg_score, emr_sessions in emr_trends:
        week_key = week_start.strftime("%Y-%m-%d")
        if week_key in trends_dict:
            trends_dict[week_key]["emr_avg_score"] = round(float(emr_avg_score), 2) if emr_avg_score else None
            trends_dict[week_key]["emr_sessions"] = emr_sessions
        else:
            trends_dict[week_key] = {
                "week_start": week_key,
                "mcq_accuracy": None,
                "osce_avg_score": None,
                "emr_avg_score": round(float(emr_avg_score), 2) if emr_avg_score else None,
                "mcq_attempts": 0,
                "osce_completions": 0,
                "emr_sessions": emr_sessions
            }

    # Sort by week_start descending (most recent first)
    sorted_trends = sorted(
        trends_dict.values(),
        key=lambda x: x["week_start"],
        reverse=True
    )

    return sorted_trends[:weeks]


@staticmethod
def get_emr_weak_areas(
    db: Session,
    user_id: int,
    threshold: float = 70.0,
    limit: int = 5
) -> list:
    """
    Identify EMR weak areas (specialties below threshold).

    Args:
        db: Database session
        user_id: User ID
        threshold: Score threshold (default 70%)
        limit: Max results (default 5)

    Returns:
        list: Array of WeakArea objects

    Example:
        [
            {
                "specialty": "Respiratory",
                "session_count": 5,
                "avg_score": 62.5,
                "gap_to_target": 7.5,
                "recommended_practice_count": 2
            },
            ...
        ]
    """
    from src.db.models import EMRSession

    weak_areas_raw = db.query(
        EMRSession.specialty,
        func.count(EMRSession.session_id).label("session_count"),
        func.avg(EMRSession.validation_score).label("avg_score")
    ).filter(
        EMRSession.user_id == user_id,
        EMRSession.submitted_at.isnot(None)
    ).group_by(
        EMRSession.specialty
    ).having(
        func.avg(EMRSession.validation_score) < threshold
    ).order_by(
        func.avg(EMRSession.validation_score).asc()
    ).limit(limit).all()

    weak_areas = []
    for specialty, session_count, avg_score in weak_areas_raw:
        avg_score_val = round(float(avg_score or 0.0), 2)
        gap_to_target = round(threshold - avg_score_val, 2)
        recommended_practice_count = max(1, int(gap_to_target / 5.0))  # 5 points per practice

        weak_areas.append({
            "specialty": specialty,
            "session_count": session_count,
            "avg_score": avg_score_val,
            "gap_to_target": gap_to_target,
            "recommended_practice_count": recommended_practice_count
        })

    return weak_areas
```

---

## File 3: Extend Pydantic Schemas

**Path**: `backend/src/schemas/progress.py`

**Action**: Add new response models

```python
# Add to existing progress.py schemas

from typing import List, Optional
from pydantic import BaseModel, Field

class SpecialtyStats(BaseModel):
    """Specialty-specific statistics"""
    specialty: str
    session_count: int
    avg_score: float

class EMRMetrics(BaseModel):
    """EMR dashboard metrics"""
    total_sessions: int
    completed_sessions: int
    in_progress_sessions: int
    avg_validation_score: float
    avg_typing_wpm: float
    improvement_percentage: float
    ahpra_compliance_rate: float
    total_time_spent_seconds: int
    epic_sessions: int
    cerner_sessions: int
    specialty_stats: List[SpecialtyStats]

class EMRDashboardResponse(BaseModel):
    """GET /progress/dashboard/emr response"""
    total_sessions: int
    completed_sessions: int
    in_progress_sessions: int
    avg_validation_score: float
    avg_typing_wpm: float
    improvement_percentage: float
    ahpra_compliance_rate: float
    total_time_spent_seconds: int
    epic_sessions: int
    cerner_sessions: int
    specialty_stats: List[SpecialtyStats]

class WeeklyTrend(BaseModel):
    """Unified weekly trend data"""
    week_start: str
    mcq_accuracy: Optional[float] = None
    osce_avg_score: Optional[float] = None
    emr_avg_score: Optional[float] = None
    mcq_attempts: int
    osce_completions: int
    emr_sessions: int

class UnifiedWeeklyTrendsResponse(BaseModel):
    """GET /progress/weekly-trends/unified response"""
    trends: List[WeeklyTrend]

class WeakArea(BaseModel):
    """Weak area (specialty below threshold)"""
    specialty: str
    session_count: int
    avg_score: float
    gap_to_target: float
    recommended_practice_count: int

class EMRWeakAreasResponse(BaseModel):
    """GET /progress/weak-areas/emr response"""
    weak_areas: List[WeakArea]
```

---

## File 4: Add Endpoints to Progress Router

**Path**: `backend/src/api/v1/progress.py`

**Action**: Add 3 new endpoints

```python
# Add to existing progress.py router (after existing endpoints)

from src.schemas.progress import (
    # ... existing imports
    EMRDashboardResponse,
    UnifiedWeeklyTrendsResponse,
    EMRWeakAreasResponse,
)

# ============================================================================
# GET EMR DASHBOARD METRICS
# ============================================================================

@router.get("/dashboard/emr", response_model=EMRDashboardResponse)
@limiter.limit("60/minute")
async def get_emr_dashboard(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get EMR-specific dashboard metrics for current user.

    FEATURES:
    - Total/completed/in-progress sessions
    - Avg validation score, typing WPM
    - Improvement percentage (first 3 vs last 3 sessions)
    - AHPRA compliance rate
    - Total time spent (seconds)
    - Epic vs Cerner session counts
    - Specialty-specific breakdown

    Returns:
    - EMRDashboardResponse: EMR metrics

    Privacy:
    - All data filtered by current_user.id

    Performance:
    - Response time: <300ms target
    """
    try:
        metrics = ProgressAnalytics.get_emr_dashboard_metrics(db, user_id=current_user.id)
        return EMRDashboardResponse(**metrics)

    except Exception as e:
        logger.error(f"Error fetching EMR dashboard for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch EMR dashboard metrics"
        )


# ============================================================================
# GET UNIFIED WEEKLY TRENDS
# ============================================================================

@router.get("/weekly-trends/unified", response_model=UnifiedWeeklyTrendsResponse)
@limiter.limit("60/minute")
async def get_unified_weekly_trends(
    request: Request,
    weeks: int = Query(12, ge=1, le=52, description="Number of weeks to return (1-52)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get unified weekly trends (MCQ + OSCE + EMR combined).

    FEATURES:
    - MCQ accuracy per week
    - OSCE avg score per week
    - EMR avg score per week
    - Activity counts (attempts, completions, sessions)

    Query Parameters:
    - weeks: Number of weeks to return (default 12, max 52)

    Returns:
    - UnifiedWeeklyTrendsResponse: Array of weekly trends

    Privacy:
    - All data filtered by current_user.id

    Performance:
    - Response time: <300ms target
    """
    try:
        trends = ProgressAnalytics.get_unified_weekly_trends(
            db,
            user_id=current_user.id,
            weeks=weeks
        )
        return UnifiedWeeklyTrendsResponse(trends=trends)

    except Exception as e:
        logger.error(f"Error fetching unified trends for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch weekly trends"
        )


# ============================================================================
# GET EMR WEAK AREAS
# ============================================================================

@router.get("/weak-areas/emr", response_model=EMRWeakAreasResponse)
@limiter.limit("60/minute")
async def get_emr_weak_areas(
    request: Request,
    limit: int = Query(5, ge=1, le=20, description="Max weak areas to return (1-20)"),
    threshold: float = Query(70.0, ge=0, le=100, description="Score threshold (default 70%)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get EMR weak areas (specialties below threshold).

    FEATURES:
    - Identifies specialties with avg_score < threshold
    - Calculates gap_to_target
    - Recommends practice count (gap / 5 points per session)
    - Sorted by avg_score (worst first)

    Query Parameters:
    - limit: Max results (default 5, max 20)
    - threshold: Score threshold (default 70%)

    Returns:
    - EMRWeakAreasResponse: Array of weak areas

    Privacy:
    - All data filtered by current_user.id

    Performance:
    - Response time: <300ms target
    """
    try:
        weak_areas = ProgressAnalytics.get_emr_weak_areas(
            db,
            user_id=current_user.id,
            threshold=threshold,
            limit=limit
        )
        return EMRWeakAreasResponse(weak_areas=weak_areas)

    except Exception as e:
        logger.error(f"Error fetching EMR weak areas for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch weak areas"
        )
```

---

# H - HANDOFF (Validation & Rollback)

## Pre-Implementation Checklist

- [ ] **Read PROJECT_CONSTRAINTS.md** (All agents MUST read before starting)
- [ ] **Verify Phase 1 & 2 complete**: Models in `models.py`, single EMR router
- [ ] **Understand frontend requirements**: Read `useEMRDashboardData.ts` hook
- [ ] **Backend running**: Start backend to test after implementation

## Implementation Checklist

### Phase 1: RED (Write Tests)
- [ ] Create `backend/tests/test_emr_dashboard_endpoints.py`
- [ ] Copy all 9 test functions from T section
- [ ] Add pytest fixtures for database session (conftest.py if needed)
- [ ] Run tests: `pytest tests/test_emr_dashboard_endpoints.py -v`
- [ ] **Verify RED**: Tests 1-6, 8-9 MUST fail initially
- [ ] Commit tests: `git add tests/test_emr_dashboard_endpoints.py && git commit -m "test: Add EMR dashboard endpoint tests (TDD RED)"`

### Phase 2: GREEN (Implement Endpoints)

#### Sub-Phase 2A: Service Layer
- [ ] Open `backend/src/services/progress_analytics.py`
- [ ] Add method: `get_emr_dashboard_metrics(db, user_id)`
- [ ] Add method: `get_unified_weekly_trends(db, user_id, weeks=12)`
- [ ] Add method: `get_emr_weak_areas(db, user_id, threshold=70.0, limit=5)`
- [ ] Run service tests: `pytest tests/test_emr_dashboard_endpoints.py::test_progress_analytics_get_emr_metrics -v`
- [ ] **Verify GREEN**: Tests 4-6 MUST pass

#### Sub-Phase 2B: Pydantic Schemas
- [ ] Open `backend/src/schemas/progress.py`
- [ ] Add schema: `EMRDashboardResponse`
- [ ] Add schema: `UnifiedWeeklyTrendsResponse`
- [ ] Add schema: `EMRWeakAreasResponse`
- [ ] Add sub-schemas: `SpecialtyStats`, `WeeklyTrend`, `WeakArea`

#### Sub-Phase 2C: Router Endpoints
- [ ] Open `backend/src/api/v1/progress.py`
- [ ] Add import: `from src.schemas.progress import EMRDashboardResponse, ...`
- [ ] Add endpoint: `@router.get("/dashboard/emr", ...)`
- [ ] Add endpoint: `@router.get("/weekly-trends/unified", ...)`
- [ ] Add endpoint: `@router.get("/weak-areas/emr", ...)`
- [ ] Run full test suite: `pytest tests/test_emr_dashboard_endpoints.py -v`
- [ ] **Verify GREEN**: ALL 9 tests MUST pass
- [ ] Commit changes: `git add . && git commit -m "feat: Implement 3 EMR dashboard endpoints (Phase 3)"`

### Phase 3: REFACTOR (Verify No Regressions)
- [ ] Run full backend test suite: `pytest --cov=src --cov-report=term-missing`
- [ ] Verify 100% test pass rate (no failures)
- [ ] Start backend: `cd backend && source venv/bin/activate && set -a && source .env && set +a && uvicorn src.main:app --reload --port 8001`
- [ ] Check uvicorn logs for errors (should be NONE)
- [ ] Test endpoints via curl:
  ```bash
  TOKEN=$(curl -X POST http://localhost:8001/api/v1/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email":"student@test.com","password":"Student123!@#"}' \
    | jq -r '.access_token')

  # Test 1: EMR Dashboard
  curl -H "Authorization: Bearer $TOKEN" http://localhost:8001/api/v1/progress/dashboard/emr

  # Test 2: Unified Trends
  curl -H "Authorization: Bearer $TOKEN" "http://localhost:8001/api/v1/progress/weekly-trends/unified?weeks=12"

  # Test 3: EMR Weak Areas
  curl -H "Authorization: Bearer $TOKEN" "http://localhost:8001/api/v1/progress/weak-areas/emr?limit=5"
  ```
- [ ] All 3 endpoints should return 200 OK (not 404 or 500)
- [ ] Test frontend integration:
  ```bash
  cd /home/dev/Development/irStudy/frontend
  npm run dev
  # Open http://localhost:5173/dashboard
  # Verify: Dashboard loads without 404 errors
  ```

## Quality Gates

| Gate | Requirement | Validation Command | Expected Result |
|------|-------------|-------------------|-----------------|
| **1. Tests Pass** | 100% pass rate (9/9 tests) | `pytest tests/test_emr_dashboard_endpoints.py -v` | `9 passed in X.XXs` |
| **2. No Regressions** | Full test suite passes | `pytest --cov=src` | `100% pass rate` |
| **3. Endpoints Exist** | All 3 return 200 OK | `curl /api/v1/progress/dashboard/emr` | HTTP 200 |
| **4. Response Time** | <300ms (p95) | Load test with curl-format.txt | `time_total < 0.300s` |
| **5. Frontend Works** | Dashboard loads | Open http://localhost:5173/dashboard | No 404 errors |
| **6. TypeScript Compiles** | Frontend code valid | `npx tsc --noEmit` | `0 errors` |

**ALL quality gates MUST pass before marking Phase 3 complete.**

## Rollback Plan

If implementation fails quality gates, revert changes:

```bash
# Rollback git commit
cd /home/dev/Development/irStudy
git log --oneline -5  # Find commit hash before Phase 3
git revert <commit-hash>

# Or restore files manually
git checkout HEAD~1 backend/src/api/v1/progress.py
git checkout HEAD~1 backend/src/services/progress_analytics.py
git checkout HEAD~1 backend/src/schemas/progress.py

# Restart backend
cd backend
source venv/bin/activate
set -a && source .env && set +a
uvicorn src.main:app --reload --port 8001
```

## Success Criteria

Phase 3 is COMPLETE when:
- ✅ All 9 dashboard tests pass (100% pass rate)
- ✅ Full backend test suite passes (no regressions)
- ✅ All 3 endpoints return 200 OK (tested via curl)
- ✅ Response time <300ms (p95)
- ✅ Frontend dashboard loads without 404 errors
- ✅ Code committed to git with descriptive message

## Next Steps

After Phase 3 completion:
1. **Mark Phase 3 DONE** in todo list
2. **Proceed to Phase 4**: PRD-EMR-004-PATIENT-ALIAS (add patient field aliases)
3. **Update PROJECT_CONSTRAINTS.md**: Document EMR dashboard endpoints pattern

---

**END OF PRD-EMR-003-DASHBOARD-ENDPOINTS**
