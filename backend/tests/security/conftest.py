"""
Security Test Fixtures
======================

Provides authentication fixtures for security penetration tests.

This module creates test users with proper credentials and generates
authentication headers for testing security controls.
"""

import pytest
from src.db.models import User, MockPatient, EMRSession
from src.auth.security import hash_password, create_access_token


# ============================================================================
# TEST USER FIXTURES
# ============================================================================


@pytest.fixture
def security_test_user1(db_session):
    """
    Create security test user 1 (student role)

    Returns:
        User: Test user with student role
    """
    user = User(
        email="student1@test.com",
        password_hash=hash_password("TestPassword123!@#"),
        full_name="Security Test User 1",
        role="student",
        is_verified=True,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def security_test_user2(db_session):
    """
    Create security test user 2 (student role)

    Returns:
        User: Test user with student role
    """
    user = User(
        email="student2@test.com",
        password_hash=hash_password("TestPassword456!@#"),
        full_name="Security Test User 2",
        role="student",
        is_verified=True,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


# ============================================================================
# AUTHENTICATION HEADER FIXTURES
# ============================================================================


@pytest.fixture
def auth_headers_user1(security_test_user1):
    """
    Generate authentication headers for test user 1

    Uses JWT token generation directly (bypasses login endpoint) for speed.

    Args:
        security_test_user1: Test user fixture

    Returns:
        dict: Authorization headers with Bearer token
    """
    access_token = create_access_token(
        data={
            "sub": security_test_user1.email,
            "user_id": str(security_test_user1.id),
            "role": security_test_user1.role
        }
    )
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def auth_headers_user2(security_test_user2):
    """
    Generate authentication headers for test user 2

    Uses JWT token generation directly (bypasses login endpoint) for speed.

    Args:
        security_test_user2: Test user fixture

    Returns:
        dict: Authorization headers with Bearer token
    """
    access_token = create_access_token(
        data={
            "sub": security_test_user2.email,
            "user_id": str(security_test_user2.id),
            "role": security_test_user2.role
        }
    )
    return {"Authorization": f"Bearer {access_token}"}


# ============================================================================
# EMR SESSION FIXTURES (for tests requiring existing session data)
# ============================================================================


@pytest.fixture(autouse=True)
def mock_patient(db_session):
    """
    Create mock patient for EMR session tests

    Returns:
        MockPatient: Test patient record
    """
    patient = MockPatient(
        mrn="MRN123456",
        name="John Doe",
        age=45,
        gender="male",
        presenting_complaint="Chest pain",
        vital_signs={"bp": "140/90", "hr": 85, "temp": 37.0},
        medical_history=["Hypertension"],
        specialty="Cardiology",
        difficulty="Intermediate"
    )
    db_session.add(patient)
    db_session.commit()
    db_session.refresh(patient)
    return patient


@pytest.fixture
def session_id(db_session, security_test_user1, mock_patient):
    """
    Create EMR session for security tests

    Returns:
        str: Session ID for testing
    """
    session = EMRSession(
        user_id=security_test_user1.id,
        patient_id=mock_patient.id,
        status="in_progress",
        emr_system="cerner",
        specialty="Cardiology",
        difficulty="Intermediate"
    )
    db_session.add(session)
    db_session.commit()
    db_session.refresh(session)
    return str(session.id)
