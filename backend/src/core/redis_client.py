"""
Redis Client Wrapper for irStudy Platform
Provides namespace isolation for EMR and AI OSCE systems

Namespaces:
- emr:* (512 MB) - Dashboard cache, rate limiting, auto-save
- osce:* (2 GB) - Session state, transcripts, emotional states
"""

import redis
from typing import Optional, Any, Dict
import json


class RedisClient:
    """Redis client with namespace isolation for EMR and OSCE"""
    
    def __init__(self, host='localhost', port=6380, password=None, db=0):
        """
        Initialize Redis client with connection pooling
        
        Args:
            host: Redis server hostname
            port: Redis server port (6380 for irStudy)
            password: Redis password (from Vault: secret/ai-osce/redis-password)
            db: Redis database number (default: 0)
        """
        self.pool = redis.ConnectionPool(
            host=host,
            port=port,
            password=password,
            db=db,
            decode_responses=True,
            max_connections=50
        )
        self.client = redis.Redis(connection_pool=self.pool)
    
    # EMR Namespace Methods (emr:*)
    
    def set_emr(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Set EMR-namespaced key
        
        Args:
            key: Key name (will be prefixed with 'emr:')
            value: Value to store (will be JSON-serialized if dict/list)
            ttl: Time-to-live in seconds (optional)
        
        Returns:
            True if successful
        """
        full_key = f"emr:{key}"
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        
        if ttl:
            return self.client.setex(full_key, ttl, value)
        return self.client.set(full_key, value)
    
    def get_emr(self, key: str) -> Optional[str]:
        """
        Get EMR-namespaced key
        
        Args:
            key: Key name (will be prefixed with 'emr:')
        
        Returns:
            Value or None if not found
        """
        value = self.client.get(f"emr:{key}")
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return None
    
    def delete_emr(self, key: str) -> int:
        """Delete EMR-namespaced key"""
        return self.client.delete(f"emr:{key}")
    
    # OSCE Namespace Methods (osce:*)
    
    def set_osce(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Set OSCE-namespaced key
        
        Args:
            key: Key name (will be prefixed with 'osce:')
            value: Value to store (will be JSON-serialized if dict/list)
            ttl: Time-to-live in seconds (optional, usually None for sessions)
        
        Returns:
            True if successful
        """
        full_key = f"osce:{key}"
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        
        if ttl:
            return self.client.setex(full_key, ttl, value)
        return self.client.set(full_key, value)
    
    def get_osce(self, key: str) -> Optional[Any]:
        """
        Get OSCE-namespaced key
        
        Args:
            key: Key name (will be prefixed with 'osce:')
        
        Returns:
            Value or None if not found
        """
        value = self.client.get(f"osce:{key}")
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return None
    
    def delete_osce(self, key: str) -> int:
        """Delete OSCE-namespaced key"""
        return self.client.delete(f"osce:{key}")
    
    # Utility Methods
    
    def ping(self) -> bool:
        """Test Redis connection"""
        try:
            return self.client.ping()
        except redis.ConnectionError:
            return False
    
    def get_info(self) -> Dict:
        """Get Redis server info"""
        return self.client.info()
    
    def get_memory_stats(self) -> Dict:
        """Get memory usage statistics"""
        info = self.client.info('memory')
        return {
            'used_memory_human': info.get('used_memory_human'),
            'maxmemory_human': info.get('maxmemory_human'),
            'maxmemory_policy': info.get('maxmemory_policy')
        }
    
    def keys_by_namespace(self, namespace: str) -> list:
        """
        Get all keys in a namespace
        
        Args:
            namespace: 'emr' or 'osce'
        
        Returns:
            List of keys (without namespace prefix)
        """
        pattern = f"{namespace}:*"
        keys = self.client.keys(pattern)
        return [k.replace(f"{namespace}:", "") for k in keys]


# Global Redis client instance (initialize in application startup)
redis_client: Optional[RedisClient] = None


def get_redis_client() -> RedisClient:
    """
    Get global Redis client instance
    
    Returns:
        Initialized RedisClient
    
    Raises:
        RuntimeError: If client not initialized
    """
    global redis_client
    if redis_client is None:
        raise RuntimeError("Redis client not initialized. Call init_redis() first.")
    return redis_client


def init_redis(password: Optional[str] = None) -> RedisClient:
    """
    Initialize global Redis client
    
    Args:
        password: Redis password (from Vault)
    
    Returns:
        Initialized RedisClient
    """
    global redis_client
    redis_client = RedisClient(password=password)
    return redis_client
