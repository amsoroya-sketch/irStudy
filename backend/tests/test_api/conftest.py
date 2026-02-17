"""
Conftest for tests/test_api/test_progress.py
Uses the same pattern as test_study_cards.py (module-level engine + create/drop per test).
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
