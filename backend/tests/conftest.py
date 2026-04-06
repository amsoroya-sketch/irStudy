"""
Global pytest configuration for backend tests

Provides shared fixtures for all test modules:
- Database session (db_session)
- Test users
- Python path setup
"""

import sys
from pathlib import Path
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from src.db.base import Base
# Import all models to ensure they're registered with Base.metadata
from src.db.models import (
    User, MCQ, MCQAttempt, OSCE, OSCEAttempt, StudyCard, StudyCardReview,
    UserProgress, MockPatient, EMRSession, EMRSOAPNote, EMRPrescription,
    EMRPathologyOrder, EMRValidationResult
)


# ============================================================================
# TEST DATABASE SETUP
# ============================================================================

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ============================================================================
# DATABASE FIXTURES
# ============================================================================


@pytest.fixture(scope="function")
def db_session():
    """
    Create fresh in-memory SQLite database for each test.

    This fixture:
    1. Creates all tables from Base metadata
    2. Yields a database session
    3. Closes the session and drops all tables after test completes

    Usage:
        def test_something(db_session):
            # Use db_session to interact with database
            user = User(email="test@test.com")
            db_session.add(user)
            db_session.commit()
    """
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


# ============================================================================
# FASTAPI TEST CLIENT FIXTURES
# ============================================================================


@pytest.fixture
def client(db_session):
    """FastAPI test client with database dependency override"""
    from fastapi.testclient import TestClient
    from src.main import app
    from src.db.base import get_db

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    test_client = TestClient(app)
    yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session):
    """Create authenticated test user"""
    from src.auth.security import hash_password

    user = User(
        email="test@test.com",
        password_hash=hash_password("TestPassword123!"),
        full_name="Test User",
        role="student",
        is_verified=True,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user):
    """Create Authorization header with valid JWT"""
    from src.auth.security import create_access_token

    access_token = create_access_token(
        data={"sub": test_user.email, "user_id": str(test_user.id)}
    )
    return {"Authorization": f"Bearer {access_token}"}
