"""
Redis-backed Rate Limiter for WebSocket Connections

ALGORITHM: Sliding window with Redis sorted sets
LIMITS: 10 connections per 60 seconds per user
SECURITY: All Redis URLs from environment/Vault (zero tolerance)

Per PROJECT_CONSTRAINTS.md Section 3.1: NO hardcoded credentials
"""

import time
from typing import Optional
import redis.asyncio as redis
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Redis-backed sliding window rate limiter
    
    ALGORITHM:
    - Uses Redis sorted sets (ZADD, ZREMRANGEBYSCORE, ZCOUNT)
    - Scores are timestamps (allows time-based operations)
    - Automatic cleanup of old entries
    
    PERFORMANCE:
    - O(log N) for ZADD
    - O(log N) for ZREMRANGEBYSCORE
    - O(1) for ZCOUNT
    - Target: <5ms per check
    
    SECURITY:
    - No hardcoded Redis URLs (fetched from config)
    - Rate limit prevents DoS attacks
    - Automatic cleanup prevents memory exhaustion
    """
    
    def __init__(
        self,
        redis_client: redis.Redis,
        max_requests: int = 10,
        window_seconds: int = 60,
        key_prefix: str = "ratelimit:ws"
    ):
        """
        Initialize rate limiter
        
        Args:
            redis_client: Async Redis client (from config.redis_url)
            max_requests: Maximum requests per window (default: 10)
            window_seconds: Time window in seconds (default: 60)
            key_prefix: Redis key prefix for isolation
        """
        self.redis = redis_client
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.key_prefix = key_prefix
        
    def _get_key(self, user_id: str) -> str:
        """Generate Redis key for user rate limit"""
        return f"{self.key_prefix}:{user_id}"
    
    async def check_rate_limit(self, user_id: str) -> tuple[bool, int, int]:
        """
        Check if user is within rate limit (sliding window)
        
        Args:
            user_id: User identifier
            
        Returns:
            Tuple of (allowed: bool, current_count: int, remaining: int)
            
        PERFORMANCE TARGET: <5ms
        """
        key = self._get_key(user_id)
        current_time = time.time()
        window_start = current_time - self.window_seconds
        
        # Pipeline for atomic operations (performance optimization)
        pipe = self.redis.pipeline()
        
        # Remove entries older than window
        pipe.zremrangebyscore(key, 0, window_start)
        
        # Count current entries in window
        pipe.zcount(key, window_start, current_time)
        
        # Add current request
        pipe.zadd(key, {str(current_time): current_time})
        
        # Set expiration (cleanup)
        pipe.expire(key, self.window_seconds + 10)
        
        # Execute pipeline
        results = await pipe.execute()
        current_count = results[1]  # ZCOUNT result
        
        # Check if allowed
        allowed = current_count < self.max_requests
        remaining = max(0, self.max_requests - current_count - 1)
        
        if not allowed:
            logger.warning(
                f"Rate limit exceeded for user {user_id[:8]}*** "
                f"({current_count}/{self.max_requests} requests in {self.window_seconds}s)"
            )
        
        return allowed, current_count, remaining
    
    async def reset_rate_limit(self, user_id: str) -> None:
        """
        Reset rate limit for user (admin function)
        
        Args:
            user_id: User identifier
        """
        key = self._get_key(user_id)
        await self.redis.delete(key)
        logger.info(f"Rate limit reset for user {user_id[:8]}***")
    
    async def get_rate_limit_info(self, user_id: str) -> dict:
        """
        Get rate limit information for user
        
        Args:
            user_id: User identifier
            
        Returns:
            Dict with current_count, max_requests, window_seconds, time_until_reset
        """
        key = self._get_key(user_id)
        current_time = time.time()
        window_start = current_time - self.window_seconds
        
        # Get count in current window
        current_count = await self.redis.zcount(key, window_start, current_time)
        
        # Get oldest entry to calculate time until reset
        oldest_entries = await self.redis.zrange(key, 0, 0, withscores=True)
        time_until_reset = 0
        if oldest_entries:
            oldest_timestamp = oldest_entries[0][1]
            time_until_reset = max(0, int(self.window_seconds - (current_time - oldest_timestamp)))
        
        return {
            "current_count": current_count,
            "max_requests": self.max_requests,
            "window_seconds": self.window_seconds,
            "time_until_reset": time_until_reset,
            "allowed": current_count < self.max_requests
        }
