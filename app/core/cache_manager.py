import json
import logging
from typing import Any, Optional
from app.core.redis_manager import redis_client

logger = logging.getLogger(__name__)


class CacheManager:
    """
    Redis cache manager with JSON serialization and error handling.
    
    Features:
    - Async Redis operations
    - JSON serialization for complex objects
    - TTL support for automatic expiration
    - Pattern-based key deletion
    - Graceful fallback on Redis errors (cache miss)
    """

    def __init__(self, redis):
        self.redis = redis

    async def set(self, key: str, value: Any, ttl: int) -> bool:
        """
        Set a value in cache with TTL.
        
        Args:
            key: Cache key
            value: Value to cache (will be JSON serialized)
            ttl: Time to live in seconds
            
        Returns:
            True if successful, False if Redis error
        """
        try:
            serialized = json.dumps(value, default=str)
            await self.redis.set(key, serialized, ex=ttl)
            logger.debug(f"Cache SET: {key} (TTL: {ttl}s)")
            return True
        except Exception as e:
            logger.warning(f"Cache SET failed for key {key}: {str(e)}")
            return False

    async def get(self, key: str) -> Optional[Any]:
        """
        Get a value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Deserialized value if found, None if miss or error
        """
        try:
            data = await self.redis.get(key)
            if not data:
                logger.debug(f"Cache MISS: {key}")
                return None
            logger.debug(f"Cache HIT: {key}")
            return json.loads(data)
        except Exception as e:
            logger.warning(f"Cache GET failed for key {key}: {str(e)}")
            return None

    async def delete(self, key: str) -> bool:
        """
        Delete a key from cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if successful, False if error
        """
        try:
            await self.redis.delete(key)
            logger.debug(f"Cache DELETE: {key}")
            return True
        except Exception as e:
            logger.warning(f"Cache DELETE failed for key {key}: {str(e)}")
            return False

    async def delete_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching a pattern.
        
        Args:
            pattern: Redis glob pattern (e.g., "blog:list:*")
            
        Returns:
            Number of keys deleted, 0 if error
        """
        try:
            keys = await self.redis.keys(pattern)
            if keys:
                deleted = await self.redis.delete(*keys)
                logger.debug(f"Cache DELETE PATTERN: {pattern} ({deleted} keys)")
                return deleted
            logger.debug(f"Cache DELETE PATTERN: {pattern} (no keys found)")
            return 0
        except Exception as e:
            logger.warning(f"Cache DELETE PATTERN failed for pattern {pattern}: {str(e)}")
            return 0

    async def exists(self, key: str) -> bool:
        """Check if a key exists in cache."""
        try:
            return await self.redis.exists(key) > 0
        except Exception as e:
            logger.warning(f"Cache EXISTS check failed for key {key}: {str(e)}")
            return False