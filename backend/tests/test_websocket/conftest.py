"""
Pytest configuration for WebSocket tests
Adds backend directory to Python path and provides Redis mocking fixtures
"""
import sys
from pathlib import Path
import pytest
from unittest.mock import Mock

# Add backend directory to Python path
backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_dir))


@pytest.fixture(autouse=True)
def mock_redis_client(monkeypatch):
    """
    Auto-use fixture to mock Redis client for all WebSocket tests.
    This prevents Redis initialization errors in tests.
    """
    mock_client = Mock()

    # Mock the get_redis_client function to return our mock
    import src.core.redis_client
    monkeypatch.setattr(src.core.redis_client, 'redis_client', mock_client)

    # Also mock get_redis_client to return the mock
    monkeypatch.setattr(src.core.redis_client, 'get_redis_client', lambda: mock_client)

    yield mock_client
