# -*- coding: utf-8 -*-
"""
Security Event Logging System with Vault Integration
Task 2.2: Comprehensive security event logging for SIEM analysis

FEATURES:
- Batch processing (flush every 60 seconds)
- Redis: 1000 most recent events
- Vault: Permanent audit log storage
- Prometheus metrics
- Background task for async flush
- Graceful error handling

SECURITY:
- NO hardcoded Vault credentials (from environment)
- Anonymized PII in logs
- Encrypted Vault storage

PERFORMANCE:
- <5ms logging overhead
- Non-blocking batch flush
- Prometheus instrumentation

Per PROJECT_CONSTRAINTS.md Section 3.1: NO hardcoded credentials
"""

import asyncio
import json
import logging
import os
import time
from dataclasses import dataclass, asdict
from datetime import datetime, UTC
from typing import Optional, Dict, List
import redis.asyncio as redis

try:
    import hvac
    from prometheus_client import Counter, Histogram
except ImportError:
    print("ERROR: Install required packages: pip install hvac prometheus-client")
    raise


logger = logging.getLogger(__name__)


# ============================================================================
# PROMETHEUS METRICS
# ============================================================================

security_events_total = Counter(
    'security_events_total',
    'Total security events logged',
    ['event_type', 'severity']
)

security_events_flush_latency_ms = Histogram(
    'security_events_flush_latency_ms',
    'Latency of batch flush to Vault in milliseconds',
    buckets=[10, 50, 100, 200, 500, 1000, 2000, 5000]
)

security_events_vault_errors_total = Counter(
    'security_events_vault_errors_total',
    'Total Vault errors during event flush',
    ['error_type']
)


# ============================================================================
# SECURITY EVENT DATACLASS
# ============================================================================

@dataclass
class SecurityEvent:
    """
    Security event structure
    
    Fields:
        timestamp: ISO 8601 timestamp (UTC)
        event_type: Event type (ws_auth_success, ws_auth_failed, etc.)
        user_id: Anonymized user identifier
        ip_address: Client IP address (anonymized)
        metadata: Additional event context (dict)
        severity: Event severity (info, low, medium, high, critical)
    """
    timestamp: str
    event_type: str
    user_id: Optional[str]
    ip_address: Optional[str]
    metadata: Dict
    severity: str
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'SecurityEvent':
        """Create SecurityEvent from dictionary"""
        return cls(**data)


# ============================================================================
# SECURITY EVENT LOGGER
# ============================================================================

class SecurityEventLogger:
    """
    Security event logger with Vault integration
    
    FEATURES:
    - Batch processing (flush every 60 seconds)
    - Redis: Max 1000 most recent events
    - Vault: Permanent audit log at audit/security_events/{date}
    - Prometheus metrics
    - Background task for async flush
    
    USAGE:
        logger = SecurityEventLogger(redis_client, vault_client)
        await logger.start_background_task()
        
        await logger.log_event(
            event_type="ws_auth_failed",
            user_id="user-123",
            ip_address="192.168.1.100",
            metadata={"reason": "invalid_token"},
            severity="high"
        )
        
        await logger.stop_background_task()
    """
    
    MAX_REDIS_EVENTS = 1000
    FLUSH_INTERVAL_SECONDS = 60
    REDIS_KEY = "security:events"
    
    def __init__(
        self,
        redis_client: redis.Redis,
        vault_client: Optional[hvac.Client] = None
    ):
        """
        Initialize security event logger
        
        Args:
            redis_client: Async Redis client
            vault_client: Optional Vault client (created from env if not provided)
            
        SECURITY:
        - Vault credentials from environment (VAULT_ADDR, VAULT_ROOT_TOKEN)
        - NO hardcoded credentials
        """
        self.redis = redis_client
        
        # Initialize Vault client
        if vault_client:
            self.vault = vault_client
        else:
            # Create Vault client from environment
            vault_addr = os.getenv("VAULT_ADDR", "http://localhost:8200")
            vault_token = os.getenv("VAULT_ROOT_TOKEN")
            
            if not vault_token:
                logger.warning(
                    "VAULT_ROOT_TOKEN not set - Vault audit logging disabled. "
                    "Events will be stored in Redis only."
                )
                self.vault = None
            else:
                self.vault = hvac.Client(url=vault_addr, token=vault_token)
                
                if not self.vault.is_authenticated():
                    logger.error(f"Failed to authenticate with Vault at {vault_addr}")
                    self.vault = None
        
        # Background task
        self._flush_task = None
        self._pending_events: List[SecurityEvent] = []
        self._lock = asyncio.Lock()
    
    async def log_event(
        self,
        event_type: str,
        user_id: Optional[str],
        ip_address: Optional[str],
        metadata: Dict,
        severity: str
    ) -> None:
        """
        Log security event
        
        Args:
            event_type: Event type (ws_auth_success, ws_auth_failed, etc.)
            user_id: User identifier (will be anonymized)
            ip_address: Client IP address (will be anonymized)
            metadata: Additional event context
            severity: Event severity (info, low, medium, high, critical)
            
        PERFORMANCE TARGET: <5ms
        """
        start_time = time.time()
        
        # Create event
        event = SecurityEvent(
            timestamp=datetime.now(UTC).isoformat(),
            event_type=event_type,
            user_id=self._anonymize_user_id(user_id),
            ip_address=self._anonymize_ip(ip_address),
            metadata=metadata,
            severity=severity
        )
        
        # Update Prometheus metrics
        security_events_total.labels(
            event_type=event_type,
            severity=severity
        ).inc()
        
        # Store in Redis (most recent 1000 events)
        try:
            await self.redis.lpush(self.REDIS_KEY, json.dumps(event.to_dict()))
            await self.redis.ltrim(self.REDIS_KEY, 0, self.MAX_REDIS_EVENTS - 1)
        except Exception as e:
            logger.error(f"Failed to store event in Redis: {e}")
        
        # Add to pending batch
        async with self._lock:
            self._pending_events.append(event)
        
        # Log event
        elapsed_ms = (time.time() - start_time) * 1000
        if elapsed_ms > 5.0:
            logger.warning(
                f"Event logging took {elapsed_ms:.2f}ms (target: <5ms) - "
                f"Event: {event_type}"
            )
    
    async def batch_flush(self) -> None:
        """
        Flush pending events to Vault
        
        PERFORMANCE:
        - Non-blocking (runs in background)
        - Prometheus metrics for latency
        - Graceful error handling
        """
        if not self.vault:
            # Vault not configured - skip flush
            return
        
        start_time = time.time()
        
        # Get pending events
        async with self._lock:
            events_to_flush = self._pending_events.copy()
            self._pending_events.clear()
        
        if not events_to_flush:
            return
        
        try:
            # Store in Vault at path: audit/security_events/{date}
            date_str = datetime.now(UTC).strftime("%Y-%m-%d")
            vault_path = f"audit/security_events/{date_str}"
            
            # Convert events to dict
            events_dict = [event.to_dict() for event in events_to_flush]
            
            # Append to existing events or create new
            existing_events = []
            try:
                secret = self.vault.secrets.kv.v2.read_secret_version(path=vault_path)
                existing_events = secret['data']['data'].get('events', [])
            except Exception:
                # Path doesn't exist yet - create it
                pass
            
            # Merge events
            all_events = existing_events + events_dict
            
            # Store in Vault
            self.vault.secrets.kv.v2.create_or_update_secret(
                path=vault_path,
                secret={
                    'events': all_events,
                    'count': len(all_events),
                    'last_updated': datetime.now(UTC).isoformat()
                }
            )
            
            # Update Prometheus metrics
            elapsed_ms = (time.time() - start_time) * 1000
            security_events_flush_latency_ms.observe(elapsed_ms)
            
            logger.info(
                f"Flushed {len(events_to_flush)} events to Vault "
                f"in {elapsed_ms:.2f}ms"
            )
        
        except Exception as e:
            logger.error(f"Failed to flush events to Vault: {e}", exc_info=True)
            
            # Update error metrics
            error_type = type(e).__name__
            security_events_vault_errors_total.labels(error_type=error_type).inc()
            
            # Put events back in pending queue
            async with self._lock:
                self._pending_events = events_to_flush + self._pending_events
    
    async def get_recent_events(
        self,
        limit: int = 100,
        event_type: Optional[str] = None,
        severity: Optional[str] = None
    ) -> List[SecurityEvent]:
        """
        Get recent security events from Redis
        
        Args:
            limit: Maximum number of events to return
            event_type: Optional filter by event type
            severity: Optional filter by severity
            
        Returns:
            List of SecurityEvent objects
        """
        try:
            # Get events from Redis
            events_json = await self.redis.lrange(
                self.REDIS_KEY,
                0,
                min(limit, self.MAX_REDIS_EVENTS) - 1
            )
            
            # Parse events
            events = []
            for event_json in events_json:
                event_dict = json.loads(event_json)
                event = SecurityEvent.from_dict(event_dict)
                
                # Apply filters
                if event_type and event.event_type != event_type:
                    continue
                if severity and event.severity != severity:
                    continue
                
                events.append(event)
            
            return events[:limit]
        
        except Exception as e:
            logger.error(f"Failed to retrieve events from Redis: {e}")
            return []
    
    async def start_background_task(self) -> None:
        """
        Start batch flush background task
        
        USAGE:
            await logger.start_background_task()
        """
        if self._flush_task is None:
            self._flush_task = asyncio.create_task(self._background_flush())
            logger.info("Security event background flush task started")
    
    async def stop_background_task(self) -> None:
        """
        Stop background task gracefully
        
        USAGE:
            await logger.stop_background_task()
        """
        if self._flush_task:
            self._flush_task.cancel()
            try:
                await self._flush_task
            except asyncio.CancelledError:
                pass
            
            # Flush remaining events
            await self.batch_flush()
            
            logger.info("Security event background flush task stopped")
    
    async def _background_flush(self) -> None:
        """
        Background task to flush events every 60 seconds
        
        PERFORMANCE:
        - Runs in background (non-blocking)
        - Flushes every 60 seconds
        - Graceful cancellation
        """
        while True:
            try:
                await asyncio.sleep(self.FLUSH_INTERVAL_SECONDS)
                await self.batch_flush()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Background flush error: {e}", exc_info=True)
    
    def _anonymize_user_id(self, user_id: Optional[str]) -> Optional[str]:
        """
        Anonymize user ID (first 8 chars only)
        
        Args:
            user_id: User identifier
            
        Returns:
            Anonymized user ID
        """
        if not user_id:
            return None
        return f"{user_id[:8]}***"
    
    def _anonymize_ip(self, ip_address: Optional[str]) -> Optional[str]:
        """
        Anonymize IP address (first 3 octets only)
        
        Args:
            ip_address: IP address
            
        Returns:
            Anonymized IP address
        """
        if not ip_address:
            return None
        
        ip_parts = ip_address.split('.')
        if len(ip_parts) == 4:
            return f"{'.'.join(ip_parts[:3])}.***"
        else:
            return "***"
