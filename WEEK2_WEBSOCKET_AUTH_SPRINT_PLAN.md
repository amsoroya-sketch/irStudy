# Week 2 Sprint Plan: Enhanced WebSocket Authentication
**Sprint**: Week 2 (2026-02-07 to 2026-02-17)  
**Project**: irStudy AMC Clinical Exam Simulation Platform v2.0  
**Sprint Goal**: Implement zero-trust WebSocket authentication with multi-factor validation, rate limiting, and security event logging  
**Success Metrics**: <50ms auth latency (p95), 100% test pass rate, 0 hardcoded credentials

---

## Sprint Overview

### Prerequisites (Week 1 - Completed ✅)
- Vault running at http://localhost:8200 with 13 secrets
- PostgreSQL at localhost:5433 with encrypted schema
- Redis Cluster with 6 nodes (7379-7384)
- JWT authentication infrastructure (backend/src/auth/security.py)
- All 14 validation tests passed

### Week 2 Architecture

**Zero-Trust WebSocket Security Model**:
```
Client WebSocket Connection
    ↓
1. JWT Token Validation (signature, expiration, claims)
    ↓
2. Session Correlation (verify session belongs to user)
    ↓
3. Token Fingerprinting (IP + User-Agent + screen resolution)
    ↓
4. Rate Limiting (Redis sliding window, max 10/min)
    ↓
5. Connection Tracking (max 3 concurrent per user)
    ↓
6. Security Event Logging (batched to Vault audit log)
    ↓
Authenticated WebSocket Connection Established
```

---

## Task Breakdown

### Task 2.1: WebSocket Authenticator Core (6 hours)
**Agent**: security-compliance-expert  
**Priority**: P0 (Critical Path)  
**Dependencies**: Week 1 JWT infrastructure  

#### 2.1.1 Create WebSocket Directory Structure
```bash
backend/src/websocket/
├── __init__.py
├── authenticator.py    # WebSocketAuthenticator class
├── rate_limiter.py     # Redis-backed rate limiting
├── connection_tracker.py  # Connection tracking
└── schemas.py          # WebSocket message schemas
```

#### 2.1.2 Implement WebSocketAuthenticator Class

**File**: `backend/src/websocket/authenticator.py`

**Requirements**:
1. JWT token validation (reuse existing auth.security module)
2. Session correlation (verify session exists in Redis)
3. Token fingerprinting (hash IP + User-Agent + screen resolution)
4. Integration with rate limiter
5. Integration with connection tracker
6. Security event logging for all authentication attempts

**Code Skeleton**:
```python
"""
WebSocket authentication with zero-trust security model

SECURITY:
- JWT token validation (signature, expiration, claims)
- Session correlation (prevent session hijacking)
- Token fingerprinting (IP + User-Agent + screen resolution)
- Rate limiting (10 connections/minute per user)
- Connection tracking (max 3 concurrent connections)
- Security event logging (all auth attempts)

USAGE:
    authenticator = WebSocketAuthenticator(redis_client, logger)
    
    # On WebSocket connection
    result = await authenticator.authenticate(
        token="jwt_token",
        ip_address="192.168.1.100",
        user_agent="Mozilla/5.0...",
        screen_resolution="1920x1080"
    )
    
    if result.success:
        # Allow connection
        connection_id = result.connection_id
    else:
        # Reject connection
        await websocket.close(code=4001, reason=result.error)
"""

from dataclasses import dataclass
from typing import Optional
import hashlib
import time
from datetime import datetime

from redis import Redis
from auth.security import verify_access_token
from .rate_limiter import RateLimiter
from .connection_tracker import ConnectionTracker


@dataclass
class AuthenticationResult:
    """Result of WebSocket authentication attempt"""
    success: bool
    connection_id: Optional[str] = None
    user_id: Optional[int] = None
    error: Optional[str] = None
    latency_ms: Optional[float] = None


class WebSocketAuthenticator:
    """
    Zero-trust WebSocket authentication
    
    Implements multi-factor validation:
    1. JWT token validation
    2. Session correlation
    3. Token fingerprinting
    4. Rate limiting
    5. Connection tracking
    """
    
    def __init__(
        self,
        redis_client: Redis,
        logger,
        max_connections_per_user: int = 3,
        rate_limit_per_minute: int = 10
    ):
        self.redis = redis_client
        self.logger = logger
        
        # Initialize rate limiter (sliding window)
        self.rate_limiter = RateLimiter(
            redis_client=redis_client,
            max_requests=rate_limit_per_minute,
            window_seconds=60
        )
        
        # Initialize connection tracker
        self.connection_tracker = ConnectionTracker(
            redis_client=redis_client,
            max_connections=max_connections_per_user
        )
    
    async def authenticate(
        self,
        token: str,
        ip_address: str,
        user_agent: str,
        screen_resolution: str
    ) -> AuthenticationResult:
        """
        Authenticate WebSocket connection with multi-factor validation
        
        Args:
            token: JWT access token
            ip_address: Client IP address
            user_agent: Client User-Agent header
            screen_resolution: Client screen resolution (e.g., "1920x1080")
        
        Returns:
            AuthenticationResult with success status and connection details
        """
        start_time = time.time()
        
        try:
            # Step 1: Validate JWT token
            payload = verify_access_token(token)
            if payload is None:
                await self._log_security_event(
                    event_type="ws_auth_failed",
                    reason="invalid_token",
                    ip_address=ip_address
                )
                return AuthenticationResult(
                    success=False,
                    error="Invalid or expired token"
                )
            
            user_id = payload.get("user_id")
            if user_id is None:
                return AuthenticationResult(
                    success=False,
                    error="Invalid token payload"
                )
            
            # Step 2: Verify session exists in Redis
            session_key = f"session:{user_id}"
            session_exists = await self.redis.exists(session_key)
            
            if not session_exists:
                await self._log_security_event(
                    event_type="ws_auth_failed",
                    reason="session_not_found",
                    user_id=user_id,
                    ip_address=ip_address
                )
                return AuthenticationResult(
                    success=False,
                    error="Session not found or expired"
                )
            
            # Step 3: Token fingerprinting (detect suspicious activity)
            fingerprint = self._generate_fingerprint(
                user_id=user_id,
                ip_address=ip_address,
                user_agent=user_agent,
                screen_resolution=screen_resolution
            )
            
            # Check if fingerprint changed (potential session hijacking)
            stored_fingerprint = await self.redis.get(f"fingerprint:{user_id}")
            if stored_fingerprint and stored_fingerprint != fingerprint:
                await self._log_security_event(
                    event_type="ws_auth_suspicious",
                    reason="fingerprint_mismatch",
                    user_id=user_id,
                    ip_address=ip_address,
                    severity="high"
                )
                # Don't reject immediately, but log for investigation
            
            # Store current fingerprint
            await self.redis.setex(
                f"fingerprint:{user_id}",
                3600,  # 1 hour expiry
                fingerprint
            )
            
            # Step 4: Rate limiting check
            rate_limit_key = f"user:{user_id}"
            rate_limit_allowed = await self.rate_limiter.allow(rate_limit_key)
            
            if not rate_limit_allowed:
                await self._log_security_event(
                    event_type="ws_auth_rate_limited",
                    user_id=user_id,
                    ip_address=ip_address,
                    severity="medium"
                )
                return AuthenticationResult(
                    success=False,
                    error="Too many connection attempts. Please try again later."
                )
            
            # Step 5: Connection tracking (max concurrent connections)
            can_connect = await self.connection_tracker.can_connect(user_id)
            
            if not can_connect:
                await self._log_security_event(
                    event_type="ws_auth_max_connections",
                    user_id=user_id,
                    ip_address=ip_address,
                    severity="low"
                )
                return AuthenticationResult(
                    success=False,
                    error="Maximum concurrent connections reached (3 max)"
                )
            
            # All checks passed - create connection
            connection_id = await self.connection_tracker.add_connection(
                user_id=user_id,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            # Calculate authentication latency
            latency_ms = (time.time() - start_time) * 1000
            
            # Log successful authentication
            await self._log_security_event(
                event_type="ws_auth_success",
                user_id=user_id,
                ip_address=ip_address,
                connection_id=connection_id,
                latency_ms=latency_ms,
                severity="info"
            )
            
            # Emit Prometheus metric
            self._emit_metric("websocket_auth_success", 1)
            self._emit_metric("websocket_auth_latency_ms", latency_ms)
            
            return AuthenticationResult(
                success=True,
                connection_id=connection_id,
                user_id=user_id,
                latency_ms=latency_ms
            )
        
        except Exception as e:
            self.logger.error(f"WebSocket authentication error: {e}")
            await self._log_security_event(
                event_type="ws_auth_error",
                reason=str(e),
                ip_address=ip_address,
                severity="critical"
            )
            return AuthenticationResult(
                success=False,
                error="Authentication failed due to server error"
            )
    
    def _generate_fingerprint(
        self,
        user_id: int,
        ip_address: str,
        user_agent: str,
        screen_resolution: str
    ) -> str:
        """
        Generate device fingerprint for session validation
        
        Combines multiple factors to create a unique fingerprint:
        - IP address (can change with VPN, so not strict)
        - User-Agent (browser/OS)
        - Screen resolution (device characteristic)
        
        Returns:
            SHA-256 hash of combined factors
        """
        fingerprint_data = f"{user_id}:{ip_address}:{user_agent}:{screen_resolution}"
        return hashlib.sha256(fingerprint_data.encode()).hexdigest()
    
    async def _log_security_event(
        self,
        event_type: str,
        user_id: Optional[int] = None,
        ip_address: Optional[str] = None,
        connection_id: Optional[str] = None,
        reason: Optional[str] = None,
        latency_ms: Optional[float] = None,
        severity: str = "info"
    ):
        """
        Log security event to Redis list (batched to Vault audit log)
        
        Events are stored in Redis and periodically flushed to Vault
        audit log for long-term SIEM integration.
        """
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "user_id": user_id,
            "ip_address": ip_address,
            "connection_id": connection_id,
            "reason": reason,
            "latency_ms": latency_ms,
            "severity": severity
        }
        
        # Push to Redis list (max 1000 events)
        await self.redis.lpush("security_events", str(event))
        await self.redis.ltrim("security_events", 0, 999)
        
        # Log to application logger
        log_message = f"[{severity.upper()}] {event_type}"
        if user_id:
            log_message += f" user_id={user_id}"
        if reason:
            log_message += f" reason={reason}"
        
        if severity == "critical":
            self.logger.critical(log_message)
        elif severity == "high":
            self.logger.error(log_message)
        elif severity == "medium":
            self.logger.warning(log_message)
        else:
            self.logger.info(log_message)
    
    def _emit_metric(self, metric_name: str, value: float):
        """
        Emit Prometheus metric
        
        In production, this would push to Prometheus pushgateway
        or be scraped by Prometheus server.
        """
        # TODO: Integrate with Prometheus client library
        self.logger.debug(f"METRIC: {metric_name}={value}")
    
    async def disconnect(self, user_id: int, connection_id: str):
        """
        Handle WebSocket disconnection
        
        Removes connection from tracking and logs event.
        """
        await self.connection_tracker.remove_connection(user_id, connection_id)
        
        await self._log_security_event(
            event_type="ws_disconnect",
            user_id=user_id,
            connection_id=connection_id,
            severity="info"
        )
```

#### 2.1.3 Implement Rate Limiter (Redis Sliding Window)

**File**: `backend/src/websocket/rate_limiter.py`

**Algorithm**: Redis sliding window (accurate rate limiting)

**Code Skeleton**:
```python
"""
Redis-backed rate limiter using sliding window algorithm

ALGORITHM:
- Sliding window counters (more accurate than fixed window)
- Uses Redis sorted sets for efficient time-based operations
- Automatically cleans up old entries

USAGE:
    limiter = RateLimiter(redis_client, max_requests=10, window_seconds=60)
    
    # Check if request allowed
    allowed = await limiter.allow("user:123")
    if allowed:
        # Process request
    else:
        # Reject with 429 Too Many Requests
"""

from redis import Redis
import time
from typing import Optional


class RateLimiter:
    """
    Sliding window rate limiter using Redis sorted sets
    
    More accurate than fixed window approach:
    - Fixed window: Can allow 2x requests at window boundary
    - Sliding window: Accurate limit across any time period
    """
    
    def __init__(
        self,
        redis_client: Redis,
        max_requests: int,
        window_seconds: int
    ):
        self.redis = redis_client
        self.max_requests = max_requests
        self.window_seconds = window_seconds
    
    async def allow(self, key: str) -> bool:
        """
        Check if request is allowed under rate limit
        
        Args:
            key: Rate limit key (e.g., "user:123", "ip:192.168.1.1")
        
        Returns:
            True if request allowed, False if rate limit exceeded
        """
        now = time.time()
        window_start = now - self.window_seconds
        
        # Redis key for sorted set
        rate_key = f"rate_limit:{key}"
        
        # Remove old entries (outside sliding window)
        await self.redis.zremrangebyscore(rate_key, 0, window_start)
        
        # Count current requests in window
        current_count = await self.redis.zcard(rate_key)
        
        if current_count >= self.max_requests:
            # Rate limit exceeded
            return False
        
        # Add current request to sorted set
        # Score = timestamp (for time-based sorting)
        # Value = unique ID (timestamp + random)
        request_id = f"{now}:{current_count}"
        await self.redis.zadd(rate_key, {request_id: now})
        
        # Set expiry on key (cleanup)
        await self.redis.expire(rate_key, self.window_seconds * 2)
        
        return True
    
    async def get_remaining(self, key: str) -> int:
        """
        Get remaining requests in current window
        
        Args:
            key: Rate limit key
        
        Returns:
            Number of requests remaining before rate limit
        """
        now = time.time()
        window_start = now - self.window_seconds
        
        rate_key = f"rate_limit:{key}"
        
        # Remove old entries
        await self.redis.zremrangebyscore(rate_key, 0, window_start)
        
        # Count current requests
        current_count = await self.redis.zcard(rate_key)
        
        remaining = max(0, self.max_requests - current_count)
        return remaining
    
    async def reset(self, key: str):
        """
        Reset rate limit for key (admin/testing use)
        
        Args:
            key: Rate limit key to reset
        """
        rate_key = f"rate_limit:{key}"
        await self.redis.delete(rate_key)
```

#### 2.1.4 Implement Connection Tracker

**File**: `backend/src/websocket/connection_tracker.py`

**Requirements**:
- Track active WebSocket connections per user
- Enforce max 3 concurrent connections
- Store connection metadata (IP, User-Agent, timestamp)
- Automatic cleanup on disconnect

**Code Skeleton**:
```python
"""
WebSocket connection tracker using Redis

FEATURES:
- Track active connections per user
- Enforce max concurrent connections limit
- Store connection metadata (IP, User-Agent, timestamp)
- Automatic expiry (heartbeat required)

USAGE:
    tracker = ConnectionTracker(redis_client, max_connections=3)
    
    # Check if user can connect
    can_connect = await tracker.can_connect(user_id=123)
    
    # Add connection
    connection_id = await tracker.add_connection(
        user_id=123,
        ip_address="192.168.1.100",
        user_agent="Mozilla/5.0..."
    )
    
    # Remove connection
    await tracker.remove_connection(user_id=123, connection_id=connection_id)
"""

from redis import Redis
import time
import uuid
from typing import Dict, List, Optional
import json


class ConnectionTracker:
    """
    Track WebSocket connections per user with Redis
    
    Uses Redis hash for connection metadata:
    Key: ws_connections:{user_id}
    Value: {connection_id: {ip, user_agent, timestamp}}
    """
    
    def __init__(
        self,
        redis_client: Redis,
        max_connections: int = 3,
        connection_ttl_seconds: int = 300  # 5 minutes without heartbeat
    ):
        self.redis = redis_client
        self.max_connections = max_connections
        self.connection_ttl = connection_ttl_seconds
    
    async def can_connect(self, user_id: int) -> bool:
        """
        Check if user can establish new connection
        
        Args:
            user_id: User ID
        
        Returns:
            True if under connection limit, False otherwise
        """
        connections_key = f"ws_connections:{user_id}"
        
        # Get current connection count
        connection_count = await self.redis.hlen(connections_key)
        
        return connection_count < self.max_connections
    
    async def add_connection(
        self,
        user_id: int,
        ip_address: str,
        user_agent: str
    ) -> str:
        """
        Add new WebSocket connection
        
        Args:
            user_id: User ID
            ip_address: Client IP address
            user_agent: Client User-Agent
        
        Returns:
            Connection ID (UUID)
        
        Raises:
            ValueError: If max connections exceeded
        """
        if not await self.can_connect(user_id):
            raise ValueError(f"User {user_id} has reached max connections ({self.max_connections})")
        
        # Generate unique connection ID
        connection_id = str(uuid.uuid4())
        
        # Store connection metadata
        connections_key = f"ws_connections:{user_id}"
        connection_data = {
            "ip_address": ip_address,
            "user_agent": user_agent,
            "connected_at": time.time()
        }
        
        await self.redis.hset(
            connections_key,
            connection_id,
            json.dumps(connection_data)
        )
        
        # Set expiry (requires periodic heartbeat to maintain)
        await self.redis.expire(connections_key, self.connection_ttl)
        
        return connection_id
    
    async def remove_connection(self, user_id: int, connection_id: str):
        """
        Remove WebSocket connection
        
        Args:
            user_id: User ID
            connection_id: Connection ID to remove
        """
        connections_key = f"ws_connections:{user_id}"
        await self.redis.hdel(connections_key, connection_id)
    
    async def get_connections(self, user_id: int) -> List[Dict]:
        """
        Get all active connections for user
        
        Args:
            user_id: User ID
        
        Returns:
            List of connection dictionaries with metadata
        """
        connections_key = f"ws_connections:{user_id}"
        
        # Get all connection data
        connections_raw = await self.redis.hgetall(connections_key)
        
        connections = []
        for connection_id, data_str in connections_raw.items():
            data = json.loads(data_str)
            data["connection_id"] = connection_id
            connections.append(data)
        
        return connections
    
    async def heartbeat(self, user_id: int, connection_id: str):
        """
        Update connection heartbeat (prevent expiry)
        
        Should be called periodically (every 30-60 seconds)
        to maintain connection tracking.
        
        Args:
            user_id: User ID
            connection_id: Connection ID
        """
        connections_key = f"ws_connections:{user_id}"
        
        # Check if connection exists
        exists = await self.redis.hexists(connections_key, connection_id)
        
        if exists:
            # Update timestamp
            connection_data_str = await self.redis.hget(connections_key, connection_id)
            connection_data = json.loads(connection_data_str)
            connection_data["last_heartbeat"] = time.time()
            
            await self.redis.hset(
                connections_key,
                connection_id,
                json.dumps(connection_data)
            )
            
            # Refresh expiry
            await self.redis.expire(connections_key, self.connection_ttl)
    
    async def cleanup_stale_connections(self, user_id: int):
        """
        Remove connections without recent heartbeat
        
        Args:
            user_id: User ID
        """
        connections = await self.get_connections(user_id)
        now = time.time()
        
        for connection in connections:
            last_heartbeat = connection.get("last_heartbeat", connection.get("connected_at"))
            
            if now - last_heartbeat > self.connection_ttl:
                # Connection stale, remove
                await self.remove_connection(user_id, connection["connection_id"])
```

#### 2.1.5 Validation Checklist

**Before marking Task 2.1 complete, verify:**
- [ ] WebSocketAuthenticator class implements all 5 validation steps
- [ ] RateLimiter uses Redis sorted sets (sliding window algorithm)
- [ ] ConnectionTracker enforces max 3 concurrent connections
- [ ] All secrets loaded from environment variables (no hardcoding)
- [ ] Security events logged to Redis list
- [ ] Prometheus metrics emitted
- [ ] Code follows PROJECT_CONSTRAINTS.md security requirements
- [ ] All files have proper docstrings and type hints

---

### Task 2.2: Security Event Logging System (4 hours)
**Agent**: security-compliance-expert  
**Priority**: P1 (Depends on Task 2.1)  
**Dependencies**: Task 2.1 (WebSocketAuthenticator)

#### 2.2.1 Create Security Event Logger

**File**: `backend/src/security/events.py`

**Requirements**:
1. Define security event schema (timestamp, type, metadata, severity)
2. Batch event processor (flush every 60 seconds to Vault audit log)
3. Prometheus metrics export (security_events_total, auth_failures_total)
4. Redis list storage (max 1000 events)
5. Vault audit log integration

**Code Skeleton**:
```python
"""
Security event logging with batched Vault audit log integration

FEATURES:
- Define security event schema
- Batch events to Redis (flush every 60 seconds)
- Export Prometheus metrics
- Integrate with Vault audit log for SIEM

USAGE:
    logger = SecurityEventLogger(redis_client, vault_client)
    
    # Log security event
    await logger.log_event(
        event_type="ws_auth_failed",
        user_id=123,
        ip_address="192.168.1.100",
        metadata={"reason": "invalid_token"},
        severity="high"
    )
    
    # Start background batch processor
    await logger.start_batch_processor()
"""

from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any
from datetime import datetime
import asyncio
import json
import os

from redis import Redis


@dataclass
class SecurityEvent:
    """Security event schema"""
    timestamp: str
    event_type: str
    user_id: Optional[int] = None
    ip_address: Optional[str] = None
    connection_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    severity: str = "info"  # info, low, medium, high, critical
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)


class SecurityEventLogger:
    """
    Security event logging with batched Vault audit integration
    
    Events flow:
    1. Log event → Store in Redis list (fast)
    2. Background processor → Batch flush every 60s
    3. Flush to Vault audit log → Long-term storage for SIEM
    4. Export Prometheus metrics → Real-time monitoring
    """
    
    def __init__(
        self,
        redis_client: Redis,
        vault_client,
        batch_interval_seconds: int = 60,
        max_events_in_redis: int = 1000
    ):
        self.redis = redis_client
        self.vault = vault_client
        self.batch_interval = batch_interval_seconds
        self.max_events = max_events_in_redis
        
        # Prometheus metrics counters
        self.metrics = {
            "security_events_total": 0,
            "auth_failures_total": 0,
            "auth_success_total": 0,
            "rate_limit_exceeded_total": 0
        }
        
        self._batch_task = None
    
    async def log_event(
        self,
        event_type: str,
        user_id: Optional[int] = None,
        ip_address: Optional[str] = None,
        connection_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        severity: str = "info"
    ):
        """
        Log security event to Redis
        
        Args:
            event_type: Event type (e.g., "ws_auth_failed", "ws_auth_success")
            user_id: User ID (if applicable)
            ip_address: Client IP address
            connection_id: WebSocket connection ID
            metadata: Additional event metadata
            severity: Event severity (info, low, medium, high, critical)
        """
        event = SecurityEvent(
            timestamp=datetime.utcnow().isoformat(),
            event_type=event_type,
            user_id=user_id,
            ip_address=ip_address,
            connection_id=connection_id,
            metadata=metadata,
            severity=severity
        )
        
        # Push to Redis list
        await self.redis.lpush("security_events", json.dumps(event.to_dict()))
        
        # Trim to max events (keep most recent)
        await self.redis.ltrim("security_events", 0, self.max_events - 1)
        
        # Update metrics
        self.metrics["security_events_total"] += 1
        
        if "auth_failed" in event_type:
            self.metrics["auth_failures_total"] += 1
        elif "auth_success" in event_type:
            self.metrics["auth_success_total"] += 1
        elif "rate_limited" in event_type:
            self.metrics["rate_limit_exceeded_total"] += 1
    
    async def start_batch_processor(self):
        """
        Start background task to batch flush events to Vault
        
        Flushes events every 60 seconds (configurable).
        """
        if self._batch_task is not None:
            raise RuntimeError("Batch processor already running")
        
        self._batch_task = asyncio.create_task(self._batch_flush_loop())
    
    async def stop_batch_processor(self):
        """Stop background batch processor"""
        if self._batch_task:
            self._batch_task.cancel()
            try:
                await self._batch_task
            except asyncio.CancelledError:
                pass
            self._batch_task = None
    
    async def _batch_flush_loop(self):
        """
        Background loop to flush events to Vault every N seconds
        """
        while True:
            try:
                await asyncio.sleep(self.batch_interval)
                await self._flush_to_vault()
            except asyncio.CancelledError:
                # Flush remaining events before shutdown
                await self._flush_to_vault()
                raise
            except Exception as e:
                print(f"Error in batch flush: {e}")
    
    async def _flush_to_vault(self):
        """
        Flush events from Redis to Vault audit log
        
        Writes events to Vault's audit backend for long-term
        storage and SIEM integration.
        """
        # Get all events from Redis
        events_raw = await self.redis.lrange("security_events", 0, -1)
        
        if not events_raw:
            return  # No events to flush
        
        events = [json.loads(e) for e in events_raw]
        
        # Write to Vault audit log
        # Note: Vault audit logs are append-only
        vault_path = os.getenv("VAULT_AUDIT_PATH", "sys/audit/security-events")
        
        try:
            # In production, write to Vault audit backend
            # For now, write to a Vault KV path
            await self.vault.secrets.kv.v2.create_or_update_secret(
                path=f"audit/{datetime.utcnow().strftime('%Y-%m-%d_%H-%M-%S')}",
                secret={"events": events}
            )
            
            # Clear flushed events from Redis
            await self.redis.delete("security_events")
            
        except Exception as e:
            print(f"Failed to flush events to Vault: {e}")
            # Keep events in Redis for retry
    
    def get_metrics(self) -> Dict[str, int]:
        """
        Get Prometheus metrics
        
        Returns:
            Dictionary of metric names and values
        """
        return self.metrics.copy()
    
    async def get_recent_events(self, limit: int = 100) -> list:
        """
        Get recent security events from Redis
        
        Args:
            limit: Maximum number of events to return
        
        Returns:
            List of security events (most recent first)
        """
        events_raw = await self.redis.lrange("security_events", 0, limit - 1)
        return [json.loads(e) for e in events_raw]
```

#### 2.2.2 Validation Checklist

**Before marking Task 2.2 complete, verify:**
- [ ] SecurityEvent dataclass defined with all required fields
- [ ] SecurityEventLogger implements batched flushing (60s interval)
- [ ] Prometheus metrics exported correctly
- [ ] Vault integration works (events written to audit log)
- [ ] Redis list trimmed to max 1000 events
- [ ] All Vault credentials from environment variables
- [ ] Background task cleanup on shutdown
- [ ] Error handling for Vault failures

---

### Task 2.3: Comprehensive Test Suite (6 hours)
**Agent**: testing-qa-expert  
**Priority**: P1 (Depends on Tasks 2.1 and 2.2)  
**Dependencies**: Tasks 2.1, 2.2

#### 2.3.1 Unit Tests

**File**: `backend/tests/test_websocket_auth.py`

**Test Cases**:
```python
"""
Unit tests for WebSocket authentication system

COVERAGE:
- JWT token validation (valid, expired, invalid signature)
- Session correlation (exists, not found, expired)
- Token fingerprinting (match, mismatch)
- Rate limiting (under limit, exceeded, reset)
- Connection tracking (under limit, max connections, disconnect)
- Security event logging
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta

from websocket.authenticator import WebSocketAuthenticator, AuthenticationResult
from websocket.rate_limiter import RateLimiter
from websocket.connection_tracker import ConnectionTracker
from auth.security import create_access_token


@pytest.fixture
def redis_mock():
    """Mock Redis client"""
    mock = AsyncMock()
    mock.exists = AsyncMock(return_value=True)
    mock.get = AsyncMock(return_value=None)
    mock.setex = AsyncMock()
    mock.lpush = AsyncMock()
    mock.ltrim = AsyncMock()
    mock.zremrangebyscore = AsyncMock()
    mock.zcard = AsyncMock(return_value=0)
    mock.zadd = AsyncMock()
    mock.expire = AsyncMock()
    mock.hlen = AsyncMock(return_value=0)
    mock.hset = AsyncMock()
    mock.hdel = AsyncMock()
    return mock


@pytest.fixture
def logger_mock():
    """Mock logger"""
    return Mock()


@pytest.fixture
def authenticator(redis_mock, logger_mock):
    """WebSocketAuthenticator instance with mocks"""
    return WebSocketAuthenticator(
        redis_client=redis_mock,
        logger=logger_mock,
        max_connections_per_user=3,
        rate_limit_per_minute=10
    )


# ============================================================================
# JWT Token Validation Tests
# ============================================================================

@pytest.mark.asyncio
async def test_authenticate_valid_token(authenticator, redis_mock):
    """Test authentication with valid JWT token"""
    # Create valid token
    token = create_access_token({"user_id": 123, "email": "test@example.com"})
    
    result = await authenticator.authenticate(
        token=token,
        ip_address="192.168.1.100",
        user_agent="Mozilla/5.0",
        screen_resolution="1920x1080"
    )
    
    assert result.success is True
    assert result.user_id == 123
    assert result.connection_id is not None
    assert result.latency_ms is not None
    assert result.latency_ms < 50  # Target: <50ms


@pytest.mark.asyncio
async def test_authenticate_expired_token(authenticator):
    """Test authentication with expired token"""
    # Create expired token (negative expiration)
    token = create_access_token(
        {"user_id": 123},
        expires_delta=timedelta(seconds=-10)
    )
    
    result = await authenticator.authenticate(
        token=token,
        ip_address="192.168.1.100",
        user_agent="Mozilla/5.0",
        screen_resolution="1920x1080"
    )
    
    assert result.success is False
    assert "Invalid or expired token" in result.error


@pytest.mark.asyncio
async def test_authenticate_invalid_signature(authenticator):
    """Test authentication with invalid JWT signature"""
    # Create token with wrong signature
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxMjN9.invalid_signature"
    
    result = await authenticator.authenticate(
        token=token,
        ip_address="192.168.1.100",
        user_agent="Mozilla/5.0",
        screen_resolution="1920x1080"
    )
    
    assert result.success is False
    assert result.error == "Invalid or expired token"


# ============================================================================
# Session Correlation Tests
# ============================================================================

@pytest.mark.asyncio
async def test_authenticate_session_not_found(authenticator, redis_mock):
    """Test authentication when session not found in Redis"""
    # Create valid token
    token = create_access_token({"user_id": 123})
    
    # Mock session not found
    redis_mock.exists.return_value = False
    
    result = await authenticator.authenticate(
        token=token,
        ip_address="192.168.1.100",
        user_agent="Mozilla/5.0",
        screen_resolution="1920x1080"
    )
    
    assert result.success is False
    assert "Session not found" in result.error


# ============================================================================
# Rate Limiting Tests
# ============================================================================

@pytest.mark.asyncio
async def test_rate_limiter_under_limit():
    """Test rate limiter allows requests under limit"""
    redis_mock = AsyncMock()
    redis_mock.zremrangebyscore = AsyncMock()
    redis_mock.zcard = AsyncMock(return_value=5)  # 5 requests in window
    redis_mock.zadd = AsyncMock()
    redis_mock.expire = AsyncMock()
    
    limiter = RateLimiter(
        redis_client=redis_mock,
        max_requests=10,
        window_seconds=60
    )
    
    allowed = await limiter.allow("user:123")
    
    assert allowed is True


@pytest.mark.asyncio
async def test_rate_limiter_exceeded():
    """Test rate limiter blocks when limit exceeded"""
    redis_mock = AsyncMock()
    redis_mock.zremrangebyscore = AsyncMock()
    redis_mock.zcard = AsyncMock(return_value=10)  # Already at limit
    redis_mock.zadd = AsyncMock()
    redis_mock.expire = AsyncMock()
    
    limiter = RateLimiter(
        redis_client=redis_mock,
        max_requests=10,
        window_seconds=60
    )
    
    allowed = await limiter.allow("user:123")
    
    assert allowed is False


# ============================================================================
# Connection Tracking Tests
# ============================================================================

@pytest.mark.asyncio
async def test_connection_tracker_under_limit():
    """Test connection tracker allows connections under limit"""
    redis_mock = AsyncMock()
    redis_mock.hlen = AsyncMock(return_value=2)  # 2 existing connections
    redis_mock.hset = AsyncMock()
    redis_mock.expire = AsyncMock()
    
    tracker = ConnectionTracker(
        redis_client=redis_mock,
        max_connections=3
    )
    
    can_connect = await tracker.can_connect(user_id=123)
    
    assert can_connect is True


@pytest.mark.asyncio
async def test_connection_tracker_max_connections():
    """Test connection tracker blocks at max connections"""
    redis_mock = AsyncMock()
    redis_mock.hlen = AsyncMock(return_value=3)  # Already at max
    
    tracker = ConnectionTracker(
        redis_client=redis_mock,
        max_connections=3
    )
    
    can_connect = await tracker.can_connect(user_id=123)
    
    assert can_connect is False


@pytest.mark.asyncio
async def test_connection_tracker_add_remove():
    """Test adding and removing connections"""
    redis_mock = AsyncMock()
    redis_mock.hlen = AsyncMock(return_value=0)
    redis_mock.hset = AsyncMock()
    redis_mock.expire = AsyncMock()
    redis_mock.hdel = AsyncMock()
    
    tracker = ConnectionTracker(
        redis_client=redis_mock,
        max_connections=3
    )
    
    # Add connection
    connection_id = await tracker.add_connection(
        user_id=123,
        ip_address="192.168.1.100",
        user_agent="Mozilla/5.0"
    )
    
    assert connection_id is not None
    
    # Remove connection
    await tracker.remove_connection(user_id=123, connection_id=connection_id)
    
    redis_mock.hdel.assert_called_once()


# ============================================================================
# Token Fingerprinting Tests
# ============================================================================

def test_fingerprint_generation(authenticator):
    """Test token fingerprint generation"""
    fingerprint1 = authenticator._generate_fingerprint(
        user_id=123,
        ip_address="192.168.1.100",
        user_agent="Mozilla/5.0",
        screen_resolution="1920x1080"
    )
    
    # Same inputs should generate same fingerprint
    fingerprint2 = authenticator._generate_fingerprint(
        user_id=123,
        ip_address="192.168.1.100",
        user_agent="Mozilla/5.0",
        screen_resolution="1920x1080"
    )
    
    assert fingerprint1 == fingerprint2
    
    # Different IP should generate different fingerprint
    fingerprint3 = authenticator._generate_fingerprint(
        user_id=123,
        ip_address="192.168.1.101",  # Different IP
        user_agent="Mozilla/5.0",
        screen_resolution="1920x1080"
    )
    
    assert fingerprint1 != fingerprint3


# ============================================================================
# Performance Tests
# ============================================================================

@pytest.mark.asyncio
async def test_authentication_latency_target(authenticator, redis_mock):
    """Test authentication latency meets <50ms target"""
    token = create_access_token({"user_id": 123})
    
    # Run 10 authentication attempts
    latencies = []
    for _ in range(10):
        result = await authenticator.authenticate(
            token=token,
            ip_address="192.168.1.100",
            user_agent="Mozilla/5.0",
            screen_resolution="1920x1080"
        )
        latencies.append(result.latency_ms)
    
    # Calculate p95 latency
    latencies.sort()
    p95_latency = latencies[int(len(latencies) * 0.95)]
    
    assert p95_latency < 50, f"p95 latency {p95_latency}ms exceeds 50ms target"


# ============================================================================
# Security Event Logging Tests
# ============================================================================

@pytest.mark.asyncio
async def test_security_event_logging(authenticator, redis_mock):
    """Test security events are logged correctly"""
    token = create_access_token({"user_id": 123})
    
    await authenticator.authenticate(
        token=token,
        ip_address="192.168.1.100",
        user_agent="Mozilla/5.0",
        screen_resolution="1920x1080"
    )
    
    # Verify security event logged to Redis
    redis_mock.lpush.assert_called()
    redis_mock.ltrim.assert_called()
```

#### 2.3.2 Integration Tests

**File**: `backend/tests/test_websocket_integration.py`

**Test Cases**:
- Full authentication flow (JWT → session → fingerprint → rate limit → connection)
- Real Redis integration (requires Docker Redis)
- Concurrent connection stress test
- Rate limit enforcement under load

#### 2.3.3 Load Test Script

**File**: `backend/tests/load_test_websocket.py`

**Requirements**:
- Simulate 100 concurrent WebSocket connections
- Verify rate limiting works under load
- Measure authentication latency distribution
- Generate report with metrics

**Code Skeleton**:
```python
"""
Load test script for WebSocket authentication

USAGE:
    python backend/tests/load_test_websocket.py
    
METRICS:
- Authentication success rate
- Authentication latency (p50, p95, p99)
- Rate limit effectiveness
- Connection tracking accuracy
"""

import asyncio
import time
from typing import List
import statistics

from websocket.authenticator import WebSocketAuthenticator
from auth.security import create_access_token
import redis.asyncio as redis


async def simulate_connection(
    authenticator: WebSocketAuthenticator,
    user_id: int,
    connection_num: int
) -> dict:
    """
    Simulate single WebSocket connection attempt
    
    Returns:
        Dictionary with result and latency
    """
    token = create_access_token({"user_id": user_id})
    
    start_time = time.time()
    
    result = await authenticator.authenticate(
        token=token,
        ip_address=f"192.168.1.{connection_num % 255}",
        user_agent="LoadTest/1.0",
        screen_resolution="1920x1080"
    )
    
    latency_ms = (time.time() - start_time) * 1000
    
    return {
        "success": result.success,
        "latency_ms": latency_ms,
        "error": result.error,
        "user_id": user_id,
        "connection_num": connection_num
    }


async def run_load_test(num_connections: int = 100, num_users: int = 10):
    """
    Run load test with multiple concurrent connections
    
    Args:
        num_connections: Total connections to simulate
        num_users: Number of unique users (connections distributed across users)
    """
    print(f"Starting load test: {num_connections} connections, {num_users} users")
    
    # Connect to Redis
    redis_client = redis.from_url("redis://localhost:7379")
    
    # Create authenticator
    import logging
    logger = logging.getLogger(__name__)
    authenticator = WebSocketAuthenticator(
        redis_client=redis_client,
        logger=logger
    )
    
    # Create tasks for concurrent connections
    tasks = []
    for i in range(num_connections):
        user_id = (i % num_users) + 1  # Distribute across users
        task = simulate_connection(authenticator, user_id, i)
        tasks.append(task)
    
    # Run all connections concurrently
    print(f"Launching {num_connections} concurrent connections...")
    start_time = time.time()
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    total_time = time.time() - start_time
    
    # Analyze results
    successful = [r for r in results if isinstance(r, dict) and r["success"]]
    failed = [r for r in results if isinstance(r, dict) and not r["success"]]
    errors = [r for r in results if isinstance(r, Exception)]
    
    latencies = [r["latency_ms"] for r in successful]
    
    # Calculate statistics
    success_rate = len(successful) / num_connections * 100
    
    if latencies:
        latencies.sort()
        p50 = latencies[int(len(latencies) * 0.50)]
        p95 = latencies[int(len(latencies) * 0.95)]
        p99 = latencies[int(len(latencies) * 0.99)]
        avg_latency = statistics.mean(latencies)
    else:
        p50 = p95 = p99 = avg_latency = 0
    
    # Print report
    print("\n" + "=" * 80)
    print("LOAD TEST RESULTS")
    print("=" * 80)
    print(f"Total connections:     {num_connections}")
    print(f"Unique users:          {num_users}")
    print(f"Total time:            {total_time:.2f}s")
    print(f"Connections/second:    {num_connections / total_time:.2f}")
    print()
    print(f"Successful:            {len(successful)} ({success_rate:.1f}%)")
    print(f"Failed:                {len(failed)}")
    print(f"Errors:                {len(errors)}")
    print()
    print("LATENCY METRICS:")
    print(f"  Average:             {avg_latency:.2f}ms")
    print(f"  p50:                 {p50:.2f}ms")
    print(f"  p95:                 {p95:.2f}ms")
    print(f"  p99:                 {p99:.2f}ms")
    print()
    
    # Check against targets
    if p95 < 50:
        print("✅ PASS: p95 latency < 50ms")
    else:
        print(f"❌ FAIL: p95 latency {p95:.2f}ms exceeds 50ms target")
    
    # Analyze failure reasons
    if failed:
        print("\nFAILURE REASONS:")
        failure_reasons = {}
        for f in failed:
            reason = f.get("error", "unknown")
            failure_reasons[reason] = failure_reasons.get(reason, 0) + 1
        
        for reason, count in failure_reasons.items():
            print(f"  {reason}: {count}")
    
    print("=" * 80)
    
    # Cleanup
    await redis_client.close()


if __name__ == "__main__":
    asyncio.run(run_load_test(num_connections=100, num_users=10))
```

#### 2.3.4 Validation Checklist

**Before marking Task 2.3 complete, verify:**
- [ ] All unit tests pass (100% pass rate)
- [ ] Integration tests pass with real Redis
- [ ] Load test completes successfully (100 concurrent connections)
- [ ] Authentication latency <50ms (p95)
- [ ] Rate limiting enforced under load
- [ ] Connection tracking accurate
- [ ] Test coverage >80% for all WebSocket modules
- [ ] Load test report generated

---

### Task 2.4: Documentation & Runbook (2 hours)
**Agent**: security-compliance-expert  
**Priority**: P2 (After implementation complete)

#### 2.4.1 Create WebSocket Security Runbook

**File**: `backend/docs/WEBSOCKET_SECURITY_RUNBOOK.md`

**Contents**:
1. Architecture overview
2. Authentication flow diagram
3. Rate limiting configuration
4. Connection tracking limits
5. Security event types
6. Troubleshooting guide
7. Monitoring dashboard setup (Prometheus + Grafana)

#### 2.4.2 Create API Documentation

**File**: `backend/docs/WEBSOCKET_API.md`

**Contents**:
- WebSocket connection endpoint
- Authentication handshake protocol
- Message format schemas
- Error codes and handling
- Client integration examples (JavaScript, Python)

#### 2.4.3 Validation Checklist

**Before marking Task 2.4 complete, verify:**
- [ ] Runbook covers all security features
- [ ] API documentation complete
- [ ] Troubleshooting guide tested
- [ ] Example code snippets included
- [ ] Diagrams created (Mermaid format)

---

## Quality Gates

### Pre-Implementation Gates
- [ ] Read PROJECT_CONSTRAINTS.md (all agents)
- [ ] Read constraints/03-security-configuration.md (security requirements)
- [ ] Understand existing JWT infrastructure (backend/src/auth/)
- [ ] Redis cluster available (6 nodes, 7379-7384)
- [ ] Vault available (http://localhost:8200)

### During Implementation Gates
- [ ] No hardcoded credentials (security scan every commit)
- [ ] All tests pass before moving to next task
- [ ] Code reviewed by PM before delegation to next agent
- [ ] Security events logged for all authentication attempts

### Post-Implementation Gates
- [ ] 100% test pass rate (pytest backend/tests/test_websocket_*.py)
- [ ] 0 hardcoded credentials (grep scan)
- [ ] Authentication latency <50ms (p95)
- [ ] Load test passes (100 concurrent connections)
- [ ] Security scan passes (./scripts/security-scan.sh)
- [ ] Documentation complete
- [ ] Prometheus metrics exported

---

## Sprint Schedule

### Week 2 Timeline (10 days)

**Day 1-2 (Feb 7-8)**: Task 2.1 - WebSocketAuthenticator
- Implement core authentication logic
- Implement rate limiter
- Implement connection tracker
- Unit tests for each module

**Day 3-4 (Feb 9-10)**: Task 2.2 - Security Event Logging
- Implement SecurityEventLogger
- Batch processor for Vault integration
- Prometheus metrics export
- Unit tests

**Day 5-6 (Feb 11-12)**: Task 2.3 - Comprehensive Testing
- Write integration tests
- Create load test script
- Run load tests
- Generate test report

**Day 7-8 (Feb 13-14)**: Task 2.4 - Documentation
- Write security runbook
- Create API documentation
- Create troubleshooting guide
- Review and polish

**Day 9 (Feb 15)**: Integration & Validation
- Run full test suite
- Security scan
- Performance validation
- Fix any issues

**Day 10 (Feb 16)**: Sprint Review & Retrospective
- Demo to stakeholders
- Review success metrics
- Document lessons learned
- Plan Week 3 tasks

---

## Success Metrics

### Performance Metrics
- **Authentication Latency**: <50ms (p95) ✅ Target
- **Throughput**: 100+ concurrent connections ✅ Target
- **Rate Limit Accuracy**: 100% (no bypass) ✅ Target

### Quality Metrics
- **Test Pass Rate**: 100% ✅ Target
- **Test Coverage**: >80% for WebSocket modules ✅ Target
- **Security Violations**: 0 (no hardcoded credentials) ✅ Target

### Security Metrics
- **Authentication Failures Logged**: 100% ✅ Target
- **Rate Limit Exceeded Events**: 100% logged ✅ Target
- **Suspicious Activity Detection**: Fingerprint mismatches logged ✅ Target

---

## Risk Mitigation

### Risk: Authentication Latency >50ms
**Mitigation**:
- Profile code to find bottlenecks
- Use Redis pipelining for multiple operations
- Cache JWT signature verification results

### Risk: Redis Unavailable
**Mitigation**:
- Implement Redis connection retry logic
- Fallback to in-memory rate limiting (less accurate)
- Alert on Redis connection failures

### Risk: Vault Integration Failure
**Mitigation**:
- Buffer security events in Redis (max 1000)
- Retry failed Vault writes
- Alert on Vault connection issues

---

## Delegation Instructions

### For security-compliance-expert (Tasks 2.1, 2.2, 2.4)

**Delegation Prompt Template**:
```markdown
## Task: Implement WebSocket Authentication (Task 2.1)

## Context
Week 1 completed JWT infrastructure. Now implementing zero-trust WebSocket authentication with multi-factor validation.

## Constraints (CRITICAL - Read First)
1. Read /home/dev/Development/irStudy/constraints/03-security-configuration.md
2. NO hardcoded credentials (use os.getenv() for ALL secrets)
3. Reuse existing JWT infrastructure (backend/src/auth/security.py)
4. All Redis operations async (use redis.asyncio)
5. Target <50ms authentication latency (p95)

## Implementation Checklist
- [ ] Create backend/src/websocket/ directory
- [ ] Implement WebSocketAuthenticator class (authenticator.py)
- [ ] Implement RateLimiter class (rate_limiter.py)
- [ ] Implement ConnectionTracker class (connection_tracker.py)
- [ ] Write unit tests (backend/tests/test_websocket_auth.py)
- [ ] Run tests: pytest backend/tests/test_websocket_auth.py -v
- [ ] Verify 100% pass rate
- [ ] Security scan: grep -r "redis://.*:.*@" backend/src/websocket/
- [ ] Verify 0 hardcoded credentials

## Validation Before Returning
Run these commands and verify output:
```bash
# Run tests
pytest backend/tests/test_websocket_auth.py -v

# Expected: 100% pass rate, 0 failures

# Security scan
grep -r "REDIS_URL\s*=\s*\"redis://" backend/src/websocket/

# Expected: no matches (all secrets from environment)

# Performance check
pytest backend/tests/test_websocket_auth.py::test_authentication_latency_target -v

# Expected: p95 latency <50ms
```

## Example Code Patterns
Refer to existing code:
- JWT validation: backend/src/auth/security.py (verify_access_token)
- Redis usage: backend/tests/test_vault.py (async Redis client)
- Security logging: backend/src/auth/dependencies.py (HTTPException patterns)

## Success Criteria
- ✅ All 5 authentication steps implemented
- ✅ 100% test pass rate
- ✅ 0 hardcoded credentials
- ✅ <50ms authentication latency (p95)
- ✅ Security events logged
```

### For testing-qa-expert (Task 2.3)

**Delegation Prompt Template**:
```markdown
## Task: Create Load Test for WebSocket Authentication (Task 2.3)

## Context
WebSocket authentication implemented (Task 2.1). Need comprehensive testing to validate performance under load.

## Constraints
1. Use pytest for unit tests
2. Use asyncio for load test (100 concurrent connections)
3. Real Redis integration required (Docker Redis at localhost:7379)
4. Target metrics: <50ms p95 latency, 100% rate limit enforcement

## Test Requirements
- [ ] Unit tests (backend/tests/test_websocket_auth.py)
- [ ] Integration tests (backend/tests/test_websocket_integration.py)
- [ ] Load test script (backend/tests/load_test_websocket.py)
- [ ] Test report (WEEK2_LOAD_TEST_REPORT.md)

## Validation Before Returning
```bash
# Run unit tests
pytest backend/tests/test_websocket_auth.py -v
# Expected: 100% pass rate

# Run load test
python backend/tests/load_test_websocket.py
# Expected: p95 latency <50ms, 100 concurrent connections successful

# Check test coverage
pytest --cov=backend/src/websocket backend/tests/ --cov-report=term
# Expected: >80% coverage
```

## Success Criteria
- ✅ 100% test pass rate
- ✅ Load test handles 100 concurrent connections
- ✅ p95 latency <50ms
- ✅ Rate limiting enforced under load
- ✅ Test report generated with metrics
```

---

## Appendix: Code Examples

### Example 1: Redis Async Client Setup
```python
import redis.asyncio as redis

# Create async Redis client
redis_client = redis.from_url(
    os.getenv("REDIS_URL", "redis://localhost:7379"),
    encoding="utf-8",
    decode_responses=True
)

# Use in async context
async with redis_client:
    await redis_client.set("key", "value")
    value = await redis_client.get("key")
```

### Example 2: JWT Token Validation
```python
from auth.security import verify_access_token

# Verify JWT token
payload = verify_access_token(token)

if payload is None:
    # Token invalid or expired
    raise HTTPException(status_code=401, detail="Invalid token")

user_id = payload.get("user_id")
```

### Example 3: Security Event Logging
```python
await self._log_security_event(
    event_type="ws_auth_failed",
    user_id=user_id,
    ip_address=ip_address,
    metadata={"reason": "invalid_token"},
    severity="high"
)
```

---

**Sprint Status**: Ready to start  
**Next Action**: Delegate Task 2.1 to security-compliance-expert  
**Estimated Completion**: 2026-02-17
