import json
import pickle
from typing import Any, Optional, Union
import redis.asyncio as redis
from app.config import get_settings
import structlog

settings = get_settings()
logger = structlog.get_logger()

# Global Redis client
_redis_client: Optional[redis.Redis] = None


async def get_redis_client() -> redis.Redis:
    """Get or create Redis client."""
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.from_url(
            settings.REDIS_URL,
            password=settings.REDIS_PASSWORD,
            encoding="utf-8",
            decode_responses=False,  # We'll handle encoding/decoding ourselves
        )
        # Test connection
        try:
            await _redis_client.ping()
            logger.info("Redis connection established")
        except Exception as e:
            logger.error("Failed to connect to Redis", error=str(e))
            _redis_client = None
            raise
    return _redis_client


async def close_redis_client():
    """Close Redis client."""
    global _redis_client
    if _redis_client is not None:
        await _redis_client.close()
        _redis_client = None
        logger.info("Redis connection closed")


async def get_cache(key: str) -> Optional[Any]:
    """Get value from cache."""
    try:
        client = await get_redis_client()
        value = await client.get(key)
        if value is None:
            return None
        # Try to deserialize as JSON first, then pickle
        try:
            return json.loads(value.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return pickle.loads(value)
    except Exception as e:
        logger.warning("Cache get failed", key=key, error=str(e))
        return None


async def set_cache(key: str, value: Any, expire: int = 300) -> bool:
    """Set value in cache with expiration in seconds."""
    try:
        client = await get_redis_client()
        # Try to serialize as JSON first, then pickle
        try:
            serialized = json.dumps(value).encode('utf-8')
        except (TypeError, ValueError):
            serialized = pickle.dumps(value)
        
        await client.set(key, serialized, ex=expire)
        logger.debug("Cache set", key=key, expire=expire)
        return True
    except Exception as e:
        logger.warning("Cache set failed", key=key, error=str(e))
        return False


async def delete_cache(key: str) -> bool:
    """Delete value from cache."""
    try:
        client = await get_redis_client()
        await client.delete(key)
        logger.debug("Cache deleted", key=key)
        return True
    except Exception as e:
        logger.warning("Cache delete failed", key=key, error=str(e))
        return False


async def clear_cache_pattern(pattern: str) -> int:
    """Clear all keys matching pattern."""
    try:
        client = await get_redis_client()
        keys = await client.keys(pattern)
        if keys:
            await client.delete(*keys)
            logger.info("Cache pattern cleared", pattern=pattern, count=len(keys))
        return len(keys)
    except Exception as e:
        logger.warning("Cache clear pattern failed", pattern=pattern, error=str(e))
        return 0