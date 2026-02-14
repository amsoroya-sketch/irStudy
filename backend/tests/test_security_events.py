# -*- coding: utf-8 -*-
"""
AMC Clinical Exam Simulation - Security Event Logging Tests
Task 2.2: Security Event Logging System

COVERAGE:
- Event logging to Redis (max 1000 events)
- Batch flush to Vault (every 60 seconds)
- Background task lifecycle (start/stop)
- Prometheus metrics (total, latency, errors)
- Vault error handling (graceful degradation)
- Event retrieval with filtering
- PII anonymization

Run with: pytest backend/tests/test_security_events.py -v
"""

import pytest
import pytest_asyncio
import asyncio
import json
import time
from datetime import datetime, UTC
from unittest.mock import AsyncMock, MagicMock, patch

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    import redis.asyncio as redis
    import hvac
    from src.security.events import SecurityEvent, SecurityEventLogger
    from prometheus_client import REGISTRY
except ImportError as e:
    pytest.skip(f"Required packages not installed: {e}", allow_module_level=True)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest_asyncio.fixture
async def redis_client():
    """Create mock Redis client for testing"""
    mock_redis = AsyncMock(spec=redis.Redis)
    
    # Mock storage
    mock_redis._storage = {}
    mock_redis._lists = {}
    
    # Mock Redis list operations
    async def mock_lpush(key, value):
        if key not in mock_redis._lists:
            mock_redis._lists[key] = []
        mock_redis._lists[key].insert(0, value)
        return len(mock_redis._lists[key])
    
    async def mock_ltrim(key, start, stop):
        if key in mock_redis._lists:
            mock_redis._lists[key] = mock_redis._lists[key][start:stop+1]
        return True
    
    async def mock_lrange(key, start, stop):
        if key not in mock_redis._lists:
            return []
        return mock_redis._lists[key][start:stop+1 if stop >= 0 else None]
    
    async def mock_llen(key):
        return len(mock_redis._lists.get(key, []))
    
    # Attach mock methods
    mock_redis.lpush = mock_lpush
    mock_redis.ltrim = mock_ltrim
    mock_redis.lrange = mock_lrange
    mock_redis.llen = mock_llen
    
    return mock_redis


@pytest_asyncio.fixture
async def vault_client():
    """Create mock Vault client for testing"""
    mock_vault = MagicMock(spec=hvac.Client)
    
    # Mock Vault storage
    mock_vault._storage = {}
    
    # Mock is_authenticated
    mock_vault.is_authenticated.return_value = True
    
    # Mock secrets.kv.v2 methods
    mock_vault.secrets.kv.v2 = MagicMock()
    
    def mock_read_secret(path):
        if path not in mock_vault._storage:
            raise Exception(f"Path {path} not found")
        return {
            'data': {
                'data': mock_vault._storage[path]
            }
        }
    
    def mock_create_or_update(path, secret):
        mock_vault._storage[path] = secret
    
    mock_vault.secrets.kv.v2.read_secret_version = mock_read_secret
    mock_vault.secrets.kv.v2.create_or_update_secret = mock_create_or_update
    
    return mock_vault


@pytest_asyncio.fixture
async def event_logger(redis_client, vault_client):
    """Create SecurityEventLogger instance"""
    logger = SecurityEventLogger(redis_client, vault_client)
    yield logger
    
    # Cleanup
    if logger._flush_task:
        await logger.stop_background_task()


# ============================================================================
# TEST: SECURITY EVENT DATACLASS
# ============================================================================

class TestSecurityEvent:
    """Test SecurityEvent dataclass"""
    
    def test_create_security_event(self):
        """Test creating SecurityEvent"""
        event = SecurityEvent(
            timestamp="2026-02-07T10:00:00Z",
            event_type="ws_auth_success",
            user_id="user-123",
            ip_address="192.168.1.100",
            metadata={"connection_id": "conn-456"},
            severity="info"
        )
        
        assert event.timestamp == "2026-02-07T10:00:00Z"
        assert event.event_type == "ws_auth_success"
        assert event.user_id == "user-123"
        assert event.ip_address == "192.168.1.100"
        assert event.metadata == {"connection_id": "conn-456"}
        assert event.severity == "info"
    
    def test_event_to_dict(self):
        """Test converting SecurityEvent to dictionary"""
        event = SecurityEvent(
            timestamp="2026-02-07T10:00:00Z",
            event_type="ws_auth_failed",
            user_id="user-789",
            ip_address="192.168.1.200",
            metadata={"reason": "invalid_token"},
            severity="high"
        )
        
        event_dict = event.to_dict()
        
        assert event_dict["timestamp"] == "2026-02-07T10:00:00Z"
        assert event_dict["event_type"] == "ws_auth_failed"
        assert event_dict["user_id"] == "user-789"
        assert event_dict["severity"] == "high"
    
    def test_event_from_dict(self):
        """Test creating SecurityEvent from dictionary"""
        event_dict = {
            "timestamp": "2026-02-07T10:00:00Z",
            "event_type": "ws_auth_success",
            "user_id": "user-123",
            "ip_address": "192.168.1.100",
            "metadata": {"latency_ms": 25.5},
            "severity": "info"
        }
        
        event = SecurityEvent.from_dict(event_dict)
        
        assert event.event_type == "ws_auth_success"
        assert event.metadata == {"latency_ms": 25.5}


# ============================================================================
# TEST: EVENT LOGGING TO REDIS
# ============================================================================

class TestEventLogging:
    """Test event logging functionality"""
    
    @pytest.mark.asyncio
    async def test_log_event_to_redis(self, event_logger, redis_client):
        """Test event is stored in Redis"""
        await event_logger.log_event(
            event_type="ws_auth_success",
            user_id="user-12345678901234",
            ip_address="192.168.1.100",
            metadata={"connection_id": "conn-123"},
            severity="info"
        )
        
        # Verify event stored in Redis
        events = await redis_client.lrange("security:events", 0, -1)
        assert len(events) == 1
        
        # Parse event
        event_dict = json.loads(events[0])
        assert event_dict["event_type"] == "ws_auth_success"
        assert event_dict["severity"] == "info"
        
        # Verify anonymization
        assert event_dict["user_id"] == "user-123***"
        assert event_dict["ip_address"] == "192.168.1.***"
    
    @pytest.mark.asyncio
    async def test_max_events_retention(self, event_logger, redis_client):
        """Test only 1000 most recent events are kept in Redis"""
        # Log 1100 events
        for i in range(1100):
            await event_logger.log_event(
                event_type=f"test_event_{i}",
                user_id=f"user-{i}",
                ip_address="192.168.1.100",
                metadata={"index": i},
                severity="info"
            )
        
        # Verify only 1000 events in Redis
        events_count = await redis_client.llen("security:events")
        assert events_count == 1000
    
    @pytest.mark.asyncio
    async def test_event_logging_performance(self, event_logger):
        """Test event logging is <5ms"""
        start_time = time.time()
        
        await event_logger.log_event(
            event_type="ws_auth_success",
            user_id="user-123",
            ip_address="192.168.1.100",
            metadata={"test": "performance"},
            severity="info"
        )
        
        elapsed_ms = (time.time() - start_time) * 1000
        
        # Should be well under 5ms (target)
        assert elapsed_ms < 10.0  # Allow 10ms buffer for test environment


# ============================================================================
# TEST: BATCH FLUSH TO VAULT
# ============================================================================

class TestBatchFlush:
    """Test batch flush to Vault"""
    
    @pytest.mark.asyncio
    async def test_batch_flush_to_vault(self, event_logger, vault_client):
        """Test events are flushed to Vault"""
        # Log events
        await event_logger.log_event(
            event_type="ws_auth_success",
            user_id="user-123",
            ip_address="192.168.1.100",
            metadata={"test": "flush"},
            severity="info"
        )
        
        await event_logger.log_event(
            event_type="ws_auth_failed",
            user_id="user-456",
            ip_address="192.168.1.200",
            metadata={"reason": "invalid_token"},
            severity="high"
        )
        
        # Flush to Vault
        await event_logger.batch_flush()
        
        # Verify events in Vault
        date_str = datetime.now(UTC).strftime("%Y-%m-%d")
        vault_path = f"audit/security_events/{date_str}"
        
        assert vault_path in vault_client._storage
        
        vault_data = vault_client._storage[vault_path]
        assert vault_data["count"] == 2
        assert len(vault_data["events"]) == 2
        
        # Verify event types
        event_types = [e["event_type"] for e in vault_data["events"]]
        assert "ws_auth_success" in event_types
        assert "ws_auth_failed" in event_types
    
    @pytest.mark.asyncio
    async def test_vault_append_events(self, event_logger, vault_client):
        """Test events are appended to existing Vault data"""
        # Pre-populate Vault with existing events
        date_str = datetime.now(UTC).strftime("%Y-%m-%d")
        vault_path = f"audit/security_events/{date_str}"
        
        vault_client._storage[vault_path] = {
            "events": [
                {
                    "timestamp": "2026-02-07T09:00:00Z",
                    "event_type": "existing_event",
                    "user_id": "user-000",
                    "ip_address": "192.168.1.1",
                    "metadata": {},
                    "severity": "info"
                }
            ],
            "count": 1
        }
        
        # Log new event
        await event_logger.log_event(
            event_type="new_event",
            user_id="user-999",
            ip_address="192.168.1.2",
            metadata={"test": "append"},
            severity="info"
        )
        
        # Flush
        await event_logger.batch_flush()
        
        # Verify events appended (not replaced)
        vault_data = vault_client._storage[vault_path]
        assert vault_data["count"] == 2
        assert len(vault_data["events"]) == 2
        
        event_types = [e["event_type"] for e in vault_data["events"]]
        assert "existing_event" in event_types
        assert "new_event" in event_types
    
    @pytest.mark.asyncio
    async def test_vault_error_handling(self, event_logger, redis_client):
        """Test graceful handling of Vault errors"""
        # Create logger with failing Vault client
        failing_vault = MagicMock(spec=hvac.Client)
        failing_vault.is_authenticated.return_value = True
        failing_vault.secrets.kv.v2.create_or_update_secret.side_effect = Exception("Vault error")
        
        logger = SecurityEventLogger(redis_client, failing_vault)
        
        # Log event
        await logger.log_event(
            event_type="test_event",
            user_id="user-123",
            ip_address="192.168.1.100",
            metadata={},
            severity="info"
        )
        
        # Flush should not raise exception
        try:
            await logger.batch_flush()
        except Exception as e:
            pytest.fail(f"batch_flush raised exception: {e}")
        
        # Event should be back in pending queue
        assert len(logger._pending_events) > 0


# ============================================================================
# TEST: BACKGROUND TASK
# ============================================================================

class TestBackgroundTask:
    """Test background flush task"""
    
    @pytest.mark.asyncio
    async def test_background_task_lifecycle(self, event_logger):
        """Test background task starts and stops properly"""
        # Start task
        await event_logger.start_background_task()
        assert event_logger._flush_task is not None
        assert not event_logger._flush_task.done()
        
        # Stop task
        await event_logger.stop_background_task()
        assert event_logger._flush_task.done() or event_logger._flush_task.cancelled()
    
    @pytest.mark.asyncio
    async def test_background_task_flushes_periodically(self, redis_client, vault_client):
        """Test background task flushes events every 60 seconds"""
        # Create logger with short flush interval for testing
        logger = SecurityEventLogger(redis_client, vault_client)
        logger.FLUSH_INTERVAL_SECONDS = 0.1  # 100ms for testing
        
        # Start background task
        await logger.start_background_task()
        
        # Log event
        await logger.log_event(
            event_type="test_event",
            user_id="user-123",
            ip_address="192.168.1.100",
            metadata={},
            severity="info"
        )
        
        # Wait for flush (200ms > 100ms interval)
        await asyncio.sleep(0.2)
        
        # Verify event flushed to Vault
        date_str = datetime.now(UTC).strftime("%Y-%m-%d")
        vault_path = f"audit/security_events/{date_str}"
        assert vault_path in vault_client._storage
        
        # Stop task
        await logger.stop_background_task()


# ============================================================================
# TEST: EVENT RETRIEVAL
# ============================================================================

class TestEventRetrieval:
    """Test event retrieval functionality"""
    
    @pytest.mark.asyncio
    async def test_get_recent_events(self, event_logger, redis_client):
        """Test retrieving recent events"""
        # Log multiple events
        for i in range(5):
            await event_logger.log_event(
                event_type=f"event_{i}",
                user_id=f"user-{i}",
                ip_address="192.168.1.100",
                metadata={"index": i},
                severity="info"
            )
        
        # Retrieve events
        events = await event_logger.get_recent_events(limit=3)
        
        assert len(events) == 3
        assert all(isinstance(e, SecurityEvent) for e in events)
    
    @pytest.mark.asyncio
    async def test_filter_by_event_type(self, event_logger):
        """Test filtering events by event type"""
        # Log different event types
        await event_logger.log_event(
            event_type="ws_auth_success",
            user_id="user-1",
            ip_address="192.168.1.100",
            metadata={},
            severity="info"
        )
        
        await event_logger.log_event(
            event_type="ws_auth_failed",
            user_id="user-2",
            ip_address="192.168.1.200",
            metadata={},
            severity="high"
        )
        
        await event_logger.log_event(
            event_type="ws_auth_success",
            user_id="user-3",
            ip_address="192.168.1.300",
            metadata={},
            severity="info"
        )
        
        # Filter by event type
        success_events = await event_logger.get_recent_events(
            event_type="ws_auth_success"
        )
        
        assert len(success_events) == 2
        assert all(e.event_type == "ws_auth_success" for e in success_events)
    
    @pytest.mark.asyncio
    async def test_filter_by_severity(self, event_logger):
        """Test filtering events by severity"""
        # Log events with different severities
        await event_logger.log_event(
            event_type="test_event",
            user_id="user-1",
            ip_address="192.168.1.100",
            metadata={},
            severity="info"
        )
        
        await event_logger.log_event(
            event_type="test_event",
            user_id="user-2",
            ip_address="192.168.1.200",
            metadata={},
            severity="critical"
        )
        
        # Filter by severity
        critical_events = await event_logger.get_recent_events(
            severity="critical"
        )
        
        assert len(critical_events) == 1
        assert critical_events[0].severity == "critical"


# ============================================================================
# TEST: PROMETHEUS METRICS
# ============================================================================

class TestPrometheusMetrics:
    """Test Prometheus metrics export"""
    
    @pytest.mark.asyncio
    async def test_prometheus_metrics_exported(self, event_logger):
        """Test Prometheus metrics are exported correctly"""
        from src.security.events import (
            security_events_total,
            security_events_flush_latency_ms,
            security_events_vault_errors_total
        )
        
        # Log events
        await event_logger.log_event(
            event_type="ws_auth_success",
            user_id="user-123",
            ip_address="192.168.1.100",
            metadata={},
            severity="info"
        )
        
        await event_logger.log_event(
            event_type="ws_auth_failed",
            user_id="user-456",
            ip_address="192.168.1.200",
            metadata={},
            severity="high"
        )
        
        # Verify metrics are Counter/Histogram objects (they exist)
        assert security_events_total is not None
        assert security_events_flush_latency_ms is not None
        assert security_events_vault_errors_total is not None
        
        # Verify metrics have correct types
        from prometheus_client import Counter, Histogram
        assert isinstance(security_events_total, Counter)
        assert isinstance(security_events_flush_latency_ms, Histogram)
        assert isinstance(security_events_vault_errors_total, Counter)


# ============================================================================
# TEST: PII ANONYMIZATION
# ============================================================================

class TestAnonymization:
    """Test PII anonymization"""
    
    @pytest.mark.asyncio
    async def test_user_id_anonymization(self, event_logger, redis_client):
        """Test user IDs are anonymized"""
        await event_logger.log_event(
            event_type="test_event",
            user_id="user-12345678901234567890",
            ip_address="192.168.1.100",
            metadata={},
            severity="info"
        )
        
        # Get event from Redis
        events = await redis_client.lrange("security:events", 0, 0)
        event_dict = json.loads(events[0])
        
        # Verify only first 8 chars visible
        assert event_dict["user_id"] == "user-123***"
    
    @pytest.mark.asyncio
    async def test_ip_address_anonymization(self, event_logger, redis_client):
        """Test IP addresses are anonymized"""
        await event_logger.log_event(
            event_type="test_event",
            user_id="user-123",
            ip_address="192.168.1.100",
            metadata={},
            severity="info"
        )
        
        # Get event from Redis
        events = await redis_client.lrange("security:events", 0, 0)
        event_dict = json.loads(events[0])
        
        # Verify only first 3 octets visible
        assert event_dict["ip_address"] == "192.168.1.***"


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
