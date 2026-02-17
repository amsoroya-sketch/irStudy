"""
Conftest for tests/test_api/.
Uses the same pattern as test_study_cards.py (module-level engine + create/drop per test).

Fixtures provided:
- db: Fresh SQLite session per test
- client: FastAPI TestClient wired to test DB
- auth_headers: JWT Authorization header for authenticated requests
- test_engine: The SQLite engine (for schema inspection in tests)
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.main import app
from src.db.base import Base, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_progress.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override DB dependency for tests."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Install override at module level
app.dependency_overrides[get_db] = override_get_db
test_client = TestClient(app)


@pytest.fixture(scope="function")
def db():
    """Fresh DB (create + drop tables) for each test."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db):
    """FastAPI test client (uses module-level override)."""
    return test_client


@pytest.fixture
def test_engine():
    """Expose the test SQLite engine for schema inspection tests."""
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def auth_headers(db):
    """
    Create Authorization header with valid JWT containing user_id.

    Required by endpoints that call get_current_active_user(),
    which reads payload.get("user_id") from the JWT.
    """
    from src.db.models import User, UserRole
    from src.auth.security import create_access_token

    user = User(
        email="conftest_auth@example.com",
        password_hash="$2b$12$fakehashfortest",  # Not used for auth in tests
        full_name="Conftest Auth User",
        role=UserRole.STUDENT,
        is_active=True,
        is_verified=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(data={"sub": user.email, "user_id": user.id})
    return {"Authorization": f"Bearer {token}"}
