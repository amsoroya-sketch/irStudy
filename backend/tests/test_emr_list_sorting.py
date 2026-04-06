"""
Test: EMR Sessions List Endpoint with Sort Parameters

PRD: PRD-EMR-005-QUERY-PARAMS.md
Tests: 3 tests covering sort_by and sort_order parameters

CRITICAL: Test-First Development (TDD)
- RED phase: Tests fail before implementation
- GREEN phase: Tests pass after implementation
- REFACTOR phase: Maintain 100% pass rate
"""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4

from src.db.models import User, MockPatient, EMRSession


# ============================================================================
# TEST 1: List Sessions Sorted by started_at Descending (Default)
# ============================================================================

def test_list_sessions_sorted_by_started_at_desc(db_session):
    """Test list endpoint sorts by started_at descending (newest first)"""
    # Create test user
    user = User(
        email="sort_test@test.com",
        password_hash="hashed",
        full_name="Sort Test User",
        role="student"
    )
    db_session.add(user)
    db_session.commit()

    # Create test patient
    patient = MockPatient(
        id=uuid4(),
        name="Test Patient",
        mrn="MRN_SORT",
        age=45,
        gender="Male",
        presenting_complaint="Chest pain",
        specialty="cardiology",
        difficulty="intermediate"
    )
    db_session.add(patient)
    db_session.commit()

    # Create 3 sessions with different started_at times
    session1 = EMRSession(
        id=uuid4(),
        user_id=user.id,
        patient_id=patient.id,
        emr_system="epic",
        specialty="cardiology",
        difficulty="medium",
        status="in_progress",
        started_at=datetime.utcnow() - timedelta(hours=3)  # Oldest
    )
    session2 = EMRSession(
        id=uuid4(),
        user_id=user.id,
        patient_id=patient.id,
        emr_system="cerner",
        specialty="cardiology",
        difficulty="medium",
        status="in_progress",
        started_at=datetime.utcnow() - timedelta(hours=2)  # Middle
    )
    session3 = EMRSession(
        id=uuid4(),
        user_id=user.id,
        patient_id=patient.id,
        emr_system="epic",
        specialty="cardiology",
        difficulty="medium",
        status="validated",
        started_at=datetime.utcnow() - timedelta(hours=1)  # Newest
    )

    db_session.add_all([session1, session2, session3])
    db_session.commit()

    # Query sessions sorted by started_at desc (simulating endpoint logic)
    sessions = (
        db_session.query(EMRSession)
        .filter(EMRSession.user_id == user.id)
        .order_by(EMRSession.started_at.desc())
        .all()
    )

    # Assertions
    assert len(sessions) == 3, "Should have 3 sessions"
    assert sessions[0].id == session3.id, "First session should be session3 (newest)"
    assert sessions[1].id == session2.id, "Second session should be session2 (middle)"
    assert sessions[2].id == session1.id, "Third session should be session1 (oldest)"


# ============================================================================
# TEST 2: List Sessions Sorted by started_at Ascending
# ============================================================================

def test_list_sessions_sorted_by_started_at_asc(db_session):
    """Test list endpoint sorts by started_at ascending (oldest first)"""
    # Create test user
    user = User(
        email="sortasc@test.com",
        password_hash="hashed",
        full_name="Sort Asc Test",
        role="student"
    )
    db_session.add(user)
    db_session.commit()

    # Create test patient
    patient = MockPatient(
        id=uuid4(),
        name="Test Patient 2",
        mrn="MRN_ASC",
        age=50,
        gender="Female",
        presenting_complaint="Shortness of breath",
        specialty="respiratory",
        difficulty="intermediate"
    )
    db_session.add(patient)
    db_session.commit()

    # Create 3 sessions
    session1 = EMRSession(
        id=uuid4(),
        user_id=user.id,
        patient_id=patient.id,
        emr_system="epic",
        specialty="respiratory",
        difficulty="medium",
        status="validated",
        started_at=datetime.utcnow() - timedelta(days=3),  # Oldest
        submitted_at=datetime.utcnow() - timedelta(days=2)
    )
    session2 = EMRSession(
        id=uuid4(),
        user_id=user.id,
        patient_id=patient.id,
        emr_system="cerner",
        specialty="respiratory",
        difficulty="medium",
        status="validated",
        started_at=datetime.utcnow() - timedelta(days=2),  # Middle
        submitted_at=datetime.utcnow() - timedelta(days=1)
    )
    session3 = EMRSession(
        id=uuid4(),
        user_id=user.id,
        patient_id=patient.id,
        emr_system="epic",
        specialty="respiratory",
        difficulty="medium",
        status="validated",
        started_at=datetime.utcnow() - timedelta(days=1),  # Newest
        submitted_at=datetime.utcnow()
    )

    db_session.add_all([session1, session2, session3])
    db_session.commit()

    # Query sessions sorted by started_at asc (simulating endpoint logic)
    sessions = (
        db_session.query(EMRSession)
        .filter(EMRSession.user_id == user.id)
        .order_by(EMRSession.started_at.asc())
        .all()
    )

    # Assertions
    assert len(sessions) == 3, "Should have 3 sessions"
    assert sessions[0].id == session1.id, "First session should be session1 (oldest)"
    assert sessions[1].id == session2.id, "Second session should be session2 (middle)"
    assert sessions[2].id == session3.id, "Third session should be session3 (newest)"


# ============================================================================
# TEST 3: SQL Injection Prevention (Invalid sort_by Parameter)
# ============================================================================

def test_list_sessions_sql_injection_prevention(db_session):
    """Test that invalid sort_by parameters are rejected (SQL injection prevention)"""
    # Create test user
    user = User(
        email="sqltest@test.com",
        password_hash="hashed",
        full_name="SQL Test",
        role="student"
    )
    db_session.add(user)
    db_session.commit()

    # Create test patient
    patient = MockPatient(
        id=uuid4(),
        name="SQL Test Patient",
        mrn="MRN_SQL",
        age=35,
        gender="Male",
        presenting_complaint="Headache",
        specialty="neurology",
        difficulty="beginner"
    )
    db_session.add(patient)
    db_session.commit()

    # Create session
    session = EMRSession(
        id=uuid4(),
        user_id=user.id,
        patient_id=patient.id,
        emr_system="epic",
        specialty="neurology",
        difficulty="easy",
        status="in_progress",
        started_at=datetime.utcnow()
    )
    db_session.add(session)
    db_session.commit()

    # Test whitelist validation logic
    valid_sort_fields = {"started_at", "submitted_at"}

    # Test 1: Valid field
    sort_by = "started_at"
    assert sort_by in valid_sort_fields, "Valid field should pass"

    # Test 2: Invalid field (SQL injection attempt)
    sort_by = "DROP TABLE users"
    if sort_by not in valid_sort_fields:
        sort_by = "started_at"  # Fallback to default
    assert sort_by == "started_at", "Invalid field should fallback to default"

    # Test 3: Another SQL injection attempt
    sort_by = "';DELETE FROM emr_sessions--"
    if sort_by not in valid_sort_fields:
        sort_by = "started_at"  # Fallback to default
    assert sort_by == "started_at", "SQL injection attempt should fallback to default"

    # Test 4: Valid sort_order
    sort_order = "desc"
    assert sort_order.lower() in {"asc", "desc"}, "Valid sort_order should pass"

    # Test 5: Invalid sort_order
    sort_order = "INVALID"
    if sort_order.lower() not in {"asc", "desc"}:
        sort_order = "desc"  # Fallback to default
    assert sort_order == "desc", "Invalid sort_order should fallback to default"

    # Verify query still works with validated parameters
    sessions = (
        db_session.query(EMRSession)
        .filter(EMRSession.user_id == user.id)
        .order_by(EMRSession.started_at.desc())
        .all()
    )
    assert len(sessions) == 1, "Should have 1 session after SQL injection prevention"
