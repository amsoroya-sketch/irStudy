"""
EMR Dashboard Service Method Tests

PURPOSE: Verify EMR-specific ProgressAnalytics service methods work correctly.

TESTS (3 total):
1. ProgressAnalytics.get_emr_dashboard_metrics
2. ProgressAnalytics.get_unified_weekly_trends
3. ProgressAnalytics.get_emr_weak_areas

TDD WORKFLOW: RED → GREEN → REFACTOR
Expected: All 3 tests fail initially (methods not implemented yet)
After implementation: All 3 tests pass
"""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4


# ============================================================================
# TEST 1: EMR Dashboard Service Method
# ============================================================================

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
        specialty="cardiology",
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
            specialty="cardiology",
            difficulty="medium",
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


# ============================================================================
# TEST 2: Unified Weekly Trends Service Method
# ============================================================================

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

    # Create MCQ (use correct field names: question_id, options JSON, correct_answer)
    mcq = MCQ(
        question_id="MCQ-TEST-001",
        question_text="Test question",
        options={"A": "Option A", "B": "Option B", "C": "Option C", "D": "Option D"},
        correct_answer="A",
        specialty="cardiology",
        difficulty="medium",
        explanation="Test explanation",
        citation="Test citation - Australian guidelines"
    )
    db_session.add(mcq)
    db_session.commit()

    # Create OSCE
    osce = OSCE(
        osce_id="OSCE-TEST-001",
        station_title="Test OSCE Station",
        station_type="history_taking",
        specialty="cardiology",
        difficulty="medium",
        patient_instructions="Simulated patient presents with chest pain",
        candidate_instructions="Take a focused cardiovascular history",
        rubric={
            "introduction": {"max_marks": 1, "criteria": "Introduces self"},
            "history": {"max_marks": 14, "criteria": "Systematic history"}
        },
        time_limit_minutes=8
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
        specialty="cardiology",
        difficulty="intermediate"
    )
    db_session.add(patient)
    db_session.commit()

    # Create data for this week
    # Match EXACTLY the same logic as get_unified_weekly_trends()
    # Service calculates: start_date = today - timedelta(weeks=weeks)
    # Then generates weeks from start_date, adjusting to Monday
    # For weeks=1, we need data in the LAST week (most recent week of the range)
    today = datetime.utcnow()
    start_date = today - timedelta(weeks=1)  # Start of 1-week range
    # Find the LAST week in the range (most recent)
    week_start = start_date
    week_start = week_start - timedelta(days=week_start.weekday())  # Adjust to Monday
    # Put data in middle of that week (Wednesday = Monday + 2 days)
    now = week_start + timedelta(days=2)

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
        scores={"introduction": 1, "history": 11, "examination": 2, "diagnosis": 1, "management": 0},
        total_score=12,
        passed=True,
        time_taken_seconds=420,
        attempted_at=now
    )
    db_session.add(osce_attempt)

    # 1 EMR session
    emr_session = EMRSession(
        id=uuid4(),
        user_id=user.id,
        patient_id=patient.id,
        specialty="cardiology",
        difficulty="medium",
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


# ============================================================================
# TEST 3: EMR Weak Areas Service Method
# ============================================================================

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
        specialty="cardiology",
        difficulty="intermediate"
    )
    neuro_patient = MockPatient(
        id=uuid4(),
        name="Neuro Patient",
        mrn="MRN_NEURO",
        age=50,
        gender="Female",
        specialty="neurology",
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
            specialty="cardiology",
            difficulty="medium",
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
            specialty="neurology",
            difficulty="medium",
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
    assert weak_areas[0]["specialty"] == "neurology"
    assert weak_areas[0]["average_score"] == 60.0
    assert weak_areas[0]["total_sessions"] == 6
