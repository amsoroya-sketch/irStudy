"""
RAG Query Caching Service
Implements Redis caching for Qdrant vector search results
"""

import redis
import json
import hashlib
from typing import List, Dict, Optional
import logging
from datetime import timedelta

logger = logging.getLogger(__name__)


class RAGCache:
    """
    Redis cache for RAG query results

    Purpose:
    - Cache expensive Qdrant vector searches
    - Reduce query latency from ~200ms to <10ms for repeated queries
    - Save Qdrant resources for high-traffic scenarios

    Cache Strategy:
    - Key: SHA256 hash of (query_text + limit + filters)
    - Value: JSON-serialized search results
    - TTL: 1 hour (medical knowledge is relatively stable)
    """

    def __init__(self, redis_url: str = "redis://:password@localhost:6380/0"):
        """
        Initialize Redis connection

        Args:
            redis_url: Redis connection URL (default uses Docker Redis)
        """
        try:
            self.redis_client = redis.from_url(
                redis_url, decode_responses=True, socket_connect_timeout=5
            )
            # Test connection
            self.redis_client.ping()
            logger.info(f"✓ Connected to Redis cache")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Cache disabled.")
            self.redis_client = None

    def _generate_cache_key(
        self, query: str, limit: int = 5, filters: Optional[Dict] = None
    ) -> str:
        """
        Generate deterministic cache key from query parameters

        Args:
            query: Search query text
            limit: Number of results requested
            filters: Optional Qdrant filters

        Returns:
            SHA256 hash as cache key
        """
        key_data = {
            "query": query,
            "limit": limit,
            "filters": filters or {},
        }
        key_string = json.dumps(key_data, sort_keys=True)
        return f"rag:query:{hashlib.sha256(key_string.encode()).hexdigest()}"

    def get_cached_results(
        self, query: str, limit: int = 5, filters: Optional[Dict] = None
    ) -> Optional[List[Dict]]:
        """
        Retrieve cached search results

        Args:
            query: Search query text
            limit: Number of results
            filters: Optional filters

        Returns:
            Cached results if found, None otherwise
        """
        if not self.redis_client:
            return None

        try:
            cache_key = self._generate_cache_key(query, limit, filters)
            cached_data = self.redis_client.get(cache_key)

            if cached_data:
                logger.info(f"✓ Cache HIT for query: '{query[:50]}...'")
                return json.loads(cached_data)
            else:
                logger.info(f"Cache MISS for query: '{query[:50]}...'")
                return None

        except Exception as e:
            logger.warning(f"Cache retrieval error: {e}")
            return None

    def cache_results(
        self,
        query: str,
        results: List[Dict],
        limit: int = 5,
        filters: Optional[Dict] = None,
        ttl_hours: int = 1,
    ) -> bool:
        """
        Cache search results

        Args:
            query: Search query text
            results: Search results to cache
            limit: Number of results
            filters: Optional filters
            ttl_hours: Cache TTL in hours (default 1 hour)

        Returns:
            True if cached successfully, False otherwise
        """
        if not self.redis_client:
            return False

        try:
            cache_key = self._generate_cache_key(query, limit, filters)
            cached_data = json.dumps(results)

            # Store with TTL
            self.redis_client.setex(
                cache_key, timedelta(hours=ttl_hours), cached_data
            )

            logger.info(f"✓ Cached results for query: '{query[:50]}...'")
            return True

        except Exception as e:
            logger.warning(f"Cache storage error: {e}")
            return False

    def invalidate_cache(self, pattern: str = "rag:query:*") -> int:
        """
        Invalidate cached queries matching pattern

        Args:
            pattern: Redis key pattern (default: all RAG queries)

        Returns:
            Number of keys deleted
        """
        if not self.redis_client:
            return 0

        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                deleted = self.redis_client.delete(*keys)
                logger.info(f"✓ Invalidated {deleted} cached queries")
                return deleted
            return 0

        except Exception as e:
            logger.warning(f"Cache invalidation error: {e}")
            return 0

    def get_cache_stats(self) -> Dict:
        """
        Get cache statistics

        Returns:
            Dictionary with cache metrics
        """
        if not self.redis_client:
            return {"enabled": False}

        try:
            info = self.redis_client.info()
            keys_count = len(self.redis_client.keys("rag:query:*"))

            return {
                "enabled": True,
                "keys_count": keys_count,
                "used_memory_human": info.get("used_memory_human", "N/A"),
                "hit_rate": info.get("keyspace_hits", 0)
                / max(info.get("keyspace_hits", 0) + info.get("keyspace_misses", 0), 1),
            }

        except Exception as e:
            logger.warning(f"Stats retrieval error: {e}")
            return {"enabled": True, "error": str(e)}


# Global cache instance
_cache_instance: Optional[RAGCache] = None


def get_rag_cache(redis_url: str = "redis://:password@localhost:6380/0") -> RAGCache:
    """
    Get or create global RAG cache instance

    Args:
        redis_url: Redis connection URL

    Returns:
        RAGCache instance
    """
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = RAGCache(redis_url=redis_url)
    return _cache_instance
