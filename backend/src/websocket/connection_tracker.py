"""
Redis-backed WebSocket Connection Tracker

FEATURES:
- Track active connections per user (max 3 concurrent)
- Store connection metadata (IP, User-Agent, timestamp)
- Heartbeat mechanism to prevent stale connections
- Automatic cleanup of inactive connections

SECURITY:
- No hardcoded Redis URLs (from config)
- Connection metadata for security audit
- IP address tracking for anomaly detection

Per PROJECT_CONSTRAINTS.md Section 3.1: NO hardcoded credentials
"""

import time
import json
from typing import Optional, List, Dict
import redis.asyncio as redis
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ConnectionTracker:
    """
    Redis-backed connection tracker for WebSocket sessions
    
    DATA STRUCTURE:
    - Redis hash: connections:{user_id} -> {connection_id: metadata_json}
    - Metadata includes: IP, User-Agent, timestamp, last_heartbeat
    
    LIMITS:
    - Max 3 concurrent connections per user
    - Heartbeat interval: 30 seconds
    - Connection timeout: 5 minutes without heartbeat
    
    PERFORMANCE:
    - O(1) for connection add/remove
    - O(N) for cleanup (N = connections per user, typically 1-3)
    - Target: <10ms per operation
    """
    
    def __init__(
        self,
        redis_client: redis.Redis,
        max_connections_per_user: int = 3,
        heartbeat_interval_seconds: int = 30,
        connection_timeout_seconds: int = 300,
        key_prefix: str = "connections"
    ):
        """
        Initialize connection tracker
        
        Args:
            redis_client: Async Redis client (from config.redis_url)
            max_connections_per_user: Maximum concurrent connections (default: 3)
            heartbeat_interval_seconds: Expected heartbeat interval (default: 30s)
            connection_timeout_seconds: Connection timeout (default: 5 minutes)
            key_prefix: Redis key prefix for isolation
        """
        self.redis = redis_client
        self.max_connections = max_connections_per_user
        self.heartbeat_interval = heartbeat_interval_seconds
        self.connection_timeout = connection_timeout_seconds
        self.key_prefix = key_prefix
    
    def _get_key(self, user_id: str) -> str:
        """Generate Redis key for user connections"""
        return f"{self.key_prefix}:{user_id}"
    
    async def add_connection(
        self,
        user_id: str,
        connection_id: str,
        ip_address: str,
        user_agent: str,
        metadata: Optional[Dict] = None
    ) -> tuple[bool, str]:
        """
        Add new connection for user
        
        Args:
            user_id: User identifier
            connection_id: Unique connection identifier
            ip_address: Client IP address
            user_agent: Client User-Agent header
            metadata: Optional additional metadata
            
        Returns:
            Tuple of (success: bool, message: str)
            
        SECURITY:
        - IP address anonymized in logs (first 3 octets only)
        - Connection metadata stored for audit trail
        """
        key = self._get_key(user_id)
        
        # Cleanup stale connections first
        await self._cleanup_stale_connections(user_id)
        
        # Check connection limit
        active_connections = await self.redis.hlen(key)
        if active_connections >= self.max_connections:
            logger.warning(
                f"Connection limit reached for user {user_id[:8]}*** "
                f"({active_connections}/{self.max_connections})"
            )
            return False, f"Maximum {self.max_connections} concurrent connections allowed"
        
        # Create connection metadata
        current_time = time.time()
        connection_data = {
            "connection_id": connection_id,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "connected_at": current_time,
            "last_heartbeat": current_time,
            "metadata": metadata or {}
        }
        
        # Store connection
        await self.redis.hset(
            key,
            connection_id,
            json.dumps(connection_data)
        )
        
        # Set expiration (cleanup)
        await self.redis.expire(key, self.connection_timeout + 60)
        
        # Anonymize IP for logging (SECURITY: don't log full IP)
        ip_parts = ip_address.split('.')
        anonymized_ip = f"{'.'.join(ip_parts[:3])}.***" if len(ip_parts) == 4 else "***"
        
        logger.info(
            f"Connection added for user {user_id[:8]}*** "
            f"(connection_id: {connection_id[:16]}..., IP: {anonymized_ip})"
        )
        
        return True, "Connection added successfully"
    
    async def remove_connection(self, user_id: str, connection_id: str) -> bool:
        """
        Remove connection for user
        
        Args:
            user_id: User identifier
            connection_id: Connection identifier to remove
            
        Returns:
            True if removed, False if not found
        """
        key = self._get_key(user_id)
        removed = await self.redis.hdel(key, connection_id)
        
        if removed:
            logger.info(
                f"Connection removed for user {user_id[:8]}*** "
                f"(connection_id: {connection_id[:16]}...)"
            )
        
        return bool(removed)
    
    async def update_heartbeat(self, user_id: str, connection_id: str) -> bool:
        """
        Update connection heartbeat timestamp
        
        Args:
            user_id: User identifier
            connection_id: Connection identifier
            
        Returns:
            True if updated, False if connection not found
        """
        key = self._get_key(user_id)
        
        # Get connection data
        connection_json = await self.redis.hget(key, connection_id)
        if not connection_json:
            return False
        
        # Update heartbeat
        connection_data = json.loads(connection_json)
        connection_data["last_heartbeat"] = time.time()
        
        # Save updated data
        await self.redis.hset(key, connection_id, json.dumps(connection_data))
        
        return True
    
    async def get_active_connections(self, user_id: str) -> List[Dict]:
        """
        Get all active connections for user
        
        Args:
            user_id: User identifier
            
        Returns:
            List of connection metadata dicts
        """
        key = self._get_key(user_id)
        
        # Cleanup stale connections first
        await self._cleanup_stale_connections(user_id)
        
        # Get all connections
        connections_data = await self.redis.hgetall(key)
        
        connections = []
        for connection_id, connection_json in connections_data.items():
            connection_data = json.loads(connection_json)
            connections.append(connection_data)
        
        return connections
    
    async def get_connection_count(self, user_id: str) -> int:
        """
        Get count of active connections for user
        
        Args:
            user_id: User identifier
            
        Returns:
            Number of active connections
        """
        key = self._get_key(user_id)
        
        # Cleanup stale connections first
        await self._cleanup_stale_connections(user_id)
        
        return await self.redis.hlen(key)
    
    async def _cleanup_stale_connections(self, user_id: str) -> int:
        """
        Remove stale connections (no heartbeat within timeout)
        
        Args:
            user_id: User identifier
            
        Returns:
            Number of stale connections removed
        """
        key = self._get_key(user_id)
        current_time = time.time()
        
        # Get all connections
        connections_data = await self.redis.hgetall(key)
        
        stale_count = 0
        for connection_id, connection_json in connections_data.items():
            connection_data = json.loads(connection_json)
            last_heartbeat = connection_data.get("last_heartbeat", 0)
            
            # Check if stale
            if current_time - last_heartbeat > self.connection_timeout:
                await self.redis.hdel(key, connection_id)
                stale_count += 1
                
                logger.warning(
                    f"Stale connection removed for user {user_id[:8]}*** "
                    f"(connection_id: {connection_id[:16]}..., "
                    f"last heartbeat: {int(current_time - last_heartbeat)}s ago)"
                )
        
        return stale_count
    
    async def cleanup_all_user_connections(self, user_id: str) -> int:
        """
        Remove all connections for user (logout/ban)
        
        Args:
            user_id: User identifier
            
        Returns:
            Number of connections removed
        """
        key = self._get_key(user_id)
        count = await self.redis.hlen(key)
        await self.redis.delete(key)
        
        logger.info(f"All connections removed for user {user_id[:8]}*** (count: {count})")
        
        return count
