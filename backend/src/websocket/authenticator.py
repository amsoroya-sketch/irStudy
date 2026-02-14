"""
WebSocket Authentication Layer with Zero-Trust Architecture

SECURITY FEATURES:
- JWT token validation (reuses backend/src/auth/security.py)
- Session correlation with Redis (session:{user_id})
- Token fingerprinting (SHA-256 hash of IP + User-Agent + screen resolution)
- Rate limiting (10 connections/minute per user)
- Connection tracking (max 3 concurrent connections)
- Security event logging (all authentication attempts)

PERFORMANCE:
- Target: <50ms authentication latency (p95)
- Redis pipeline for atomic operations
- Cached JWT verification

Per PROJECT_CONSTRAINTS.md Section 3.1: NO hardcoded credentials
"""

import hashlib
import time
import json
from typing import Optional, Dict, Tuple
import redis.asyncio as redis
from datetime import datetime
import logging

from ..auth.security import verify_access_token
from .rate_limiter import RateLimiter
from .connection_tracker import ConnectionTracker

from ..security.events import SecurityEventLogger

logger = logging.getLogger(__name__)


class AuthenticationResult:
    """
    Result of WebSocket authentication attempt
    
    Fields:
        success: Whether authentication succeeded
        user_id: User identifier (if successful)
        message: Human-readable message
        metadata: Additional context (rate limit info, etc.)
    """
    
    def __init__(
        self,
        success: bool,
        user_id: Optional[str] = None,
        message: str = "",
        metadata: Optional[Dict] = None
    ):
        self.success = success
        self.user_id = user_id
        self.message = message
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "success": self.success,
            "user_id": self.user_id,
            "message": self.message,
            "metadata": self.metadata
        }


class WebSocketAuthenticator:
    """
    Zero-trust WebSocket authenticator
    
    AUTHENTICATION FLOW:
    1. JWT token validation (signature, expiration, type)
    2. Session correlation (verify session exists in Redis)
    3. Token fingerprinting (verify client metadata matches)
    4. Rate limiting (prevent DoS attacks)
    5. Connection tracking (enforce max concurrent connections)
    6. Security event logging (audit trail)
    
    PERFORMANCE TARGET: <50ms (p95)
    
    SECURITY:
    - No hardcoded Redis URLs (from config)
    - All secrets from environment/Vault
    - PHI anonymization in logs
    """
    
    def __init__(
        self,
        redis_client: redis.Redis,
        rate_limiter: Optional[RateLimiter] = None,
        connection_tracker: Optional[ConnectionTracker] = None,
        event_logger: Optional[SecurityEventLogger] = None
    ):
        """
        Initialize WebSocket authenticator
        
        Args:
            redis_client: Async Redis client (from config.redis_url)
            rate_limiter: Optional rate limiter (created if not provided)
            connection_tracker: Optional connection tracker (created if not provided)
            event_logger: Optional security event logger (created if not provided)
        """
        self.redis = redis_client
        
        # Initialize rate limiter
        self.rate_limiter = rate_limiter or RateLimiter(redis_client)
        
        # Initialize connection tracker
        self.connection_tracker = connection_tracker or ConnectionTracker(redis_client)
        
        # Initialize security event logger
        self.event_logger = event_logger or SecurityEventLogger(redis_client)
    
    async def authenticate(
        self,
        token: str,
        connection_id: str,
        ip_address: str,
        user_agent: str,
        fingerprint_data: Optional[Dict] = None
    ) -> AuthenticationResult:
        """
        Authenticate WebSocket connection
        
        Args:
            token: JWT access token
            connection_id: Unique connection identifier
            ip_address: Client IP address
            user_agent: Client User-Agent header
            fingerprint_data: Optional fingerprinting data (screen resolution, etc.)
            
        Returns:
            AuthenticationResult with success/failure and metadata
            
        PERFORMANCE TARGET: <50ms (p95)
        """
        start_time = time.time()
        
        try:
            # Step 1: JWT token validation
            payload = verify_access_token(token)
            if not payload:
                await self.event_logger.log_event(
                    event_type="ws_auth_failed",
                    user_id=None,
                    ip_address=ip_address,
                    metadata={"reason": "invalid_token"},
                    severity="medium"
                )
                return AuthenticationResult(
                    success=False,
                    message="Invalid or expired token"
                )
            
            user_id = payload.get("sub")  # Subject = user_id
            if not user_id:
                return AuthenticationResult(
                    success=False,
                    message="Token missing user identifier"
                )
            
            # Step 2: Session correlation (verify session exists in Redis)
            session_key = f"session:{user_id}"
            session_exists = await self.redis.exists(session_key)
            if not session_exists:
                await self.event_logger.log_event(
                    event_type="ws_auth_failed",
                    user_id=user_id,
                    ip_address=ip_address,
                    metadata={"reason": "session_not_found"},
                    severity="high"
                )
                return AuthenticationResult(
                    success=False,
                    message="Session not found or expired"
                )
            
            # Step 3: Token fingerprinting (verify client metadata)
            fingerprint = self._generate_fingerprint(ip_address, user_agent, fingerprint_data)
            fingerprint_match = await self._verify_fingerprint(user_id, fingerprint)
            if not fingerprint_match:
                await self.event_logger.log_event(
                    event_type="ws_auth_failed",
                    user_id=user_id,
                    ip_address=ip_address,
                    metadata={"reason": "fingerprint_mismatch"},
                    severity="critical"
                )
                return AuthenticationResult(
                    success=False,
                    message="Token fingerprint mismatch (possible session hijacking)"
                )
            
            # Step 4: Rate limiting
            allowed, current_count, remaining = await self.rate_limiter.check_rate_limit(user_id)
            if not allowed:
                await self.event_logger.log_event(
                    event_type="ws_auth_failed",
                    user_id=user_id,
                    ip_address=ip_address,
                    metadata={"reason": "rate_limit_exceeded", "count": current_count},
                    severity="medium"
                )
                return AuthenticationResult(
                    success=False,
                    message=f"Rate limit exceeded ({current_count} connections/minute)",
                    metadata={"rate_limit_remaining": 0}
                )
            
            # Step 5: Connection tracking
            connection_success, connection_message = await self.connection_tracker.add_connection(
                user_id=user_id,
                connection_id=connection_id,
                ip_address=ip_address,
                user_agent=user_agent,
                metadata=fingerprint_data
            )
            if not connection_success:
                await self.event_logger.log_event(
                    event_type="ws_auth_failed",
                    user_id=user_id,
                    ip_address=ip_address,
                    metadata={"reason": "max_connections_exceeded"},
                    severity="low"
                )
                return AuthenticationResult(
                    success=False,
                    message=connection_message
                )
            
            # Step 6: Security event logging (successful authentication)
            elapsed_ms = (time.time() - start_time) * 1000
            await self.event_logger.log_event(
                event_type="ws_auth_success",
                user_id=user_id,
                ip_address=ip_address,
                metadata={
                    "connection_id": connection_id,
                    "latency_ms": round(elapsed_ms, 2)
                },
                severity="info"
            )
            
            return AuthenticationResult(
                success=True,
                user_id=user_id,
                message="Authentication successful",
                metadata={
                    "connection_id": connection_id,
                    "rate_limit_remaining": remaining,
                    "latency_ms": round(elapsed_ms, 2)
                }
            )
        
        except Exception as e:
            logger.error(f"Authentication error: {e}", exc_info=True)
            return AuthenticationResult(
                success=False,
                message="Internal authentication error"
            )
    
    async def disconnect(self, user_id: str, connection_id: str) -> None:
        """
        Handle WebSocket disconnect
        
        Args:
            user_id: User identifier
            connection_id: Connection identifier
        """
        await self.connection_tracker.remove_connection(user_id, connection_id)
        
        await self.event_logger.log_event(
            event_type="ws_disconnect",
            user_id=user_id,
            ip_address=None,
            metadata={"connection_id": connection_id},
            severity="info"
        )
    
    async def update_heartbeat(self, user_id: str, connection_id: str) -> bool:
        """
        Update connection heartbeat
        
        Args:
            user_id: User identifier
            connection_id: Connection identifier
            
        Returns:
            True if updated, False if connection not found
        """
        return await self.connection_tracker.update_heartbeat(user_id, connection_id)
    
    def _generate_fingerprint(
        self,
        ip_address: str,
        user_agent: str,
        fingerprint_data: Optional[Dict] = None
    ) -> str:
        """
        Generate SHA-256 fingerprint from client metadata
        
        Args:
            ip_address: Client IP address
            user_agent: Client User-Agent header
            fingerprint_data: Optional additional data (screen resolution, etc.)
            
        Returns:
            SHA-256 hash (hex string)
        """
        components = [
            ip_address,
            user_agent,
        ]
        
        # Add additional fingerprint data if provided
        if fingerprint_data:
            screen_resolution = fingerprint_data.get("screen_resolution", "")
            if screen_resolution:
                components.append(screen_resolution)
        
        # Generate SHA-256 hash
        fingerprint_str = "|".join(components)
        fingerprint_hash = hashlib.sha256(fingerprint_str.encode()).hexdigest()
        
        return fingerprint_hash
    
    async def _verify_fingerprint(self, user_id: str, fingerprint: str) -> bool:
        """
        Verify token fingerprint matches stored value
        
        Args:
            user_id: User identifier
            fingerprint: Generated fingerprint
            
        Returns:
            True if fingerprint matches or no stored fingerprint
        """
        session_key = f"session:{user_id}"
        
        # Get stored fingerprint
        session_data_json = await self.redis.get(session_key)
        if not session_data_json:
            return False
        
        session_data = json.loads(session_data_json)
        stored_fingerprint = session_data.get("fingerprint")
        
        # If no stored fingerprint, store current one
        if not stored_fingerprint:
            session_data["fingerprint"] = fingerprint
            await self.redis.set(session_key, json.dumps(session_data))
            return True
        
        # Verify fingerprint matches
        return stored_fingerprint == fingerprint
