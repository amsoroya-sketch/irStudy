"""
Conftest for tests/test_api/.

This module-specific conftest provides fixtures for API tests:
- test_engine: SQLite engine for schema inspection tests
- mock_anthropic_api_key: Mock API key for study card generator tests

All other fixtures (db_session, client, auth_headers, test_user) come from
the global conftest.py.
"""
import pytest
import os
from sqlalchemy import create_engine

from src.db.base import Base

# ============================================================================
# SCHEMA INSPECTION FIXTURES (SQLite for CI/CD compatibility)
# ============================================================================

@pytest.fixture
def test_engine():
    """
    Expose a test SQLite engine for schema inspection tests.
    
    Used by test_study_card_optimization.py to verify indexed columns exist.
    Creates tables, yields engine, then drops tables.
    """
    SQLALCHEMY_DATABASE_URL = "sqlite:///./test_schema_inspection.db"
    
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
    )
    
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


# ============================================================================
# CLAUDE API MOCK FIXTURES (for study card generator tests)
# ============================================================================

@pytest.fixture(autouse=True)
def mock_anthropic_api_key(monkeypatch):
    """
    Set ANTHROPIC_API_KEY environment variable for all tests in test_api.

    This prevents StudyCardGenerator from failing during initialization when
    Vault is unavailable in test environments. The generator's _get_api_key()
    will fall back to this environment variable.

    Autouse=True ensures this runs for all tests in this directory.
    """
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-mock-api-key-for-testing")
    yield
