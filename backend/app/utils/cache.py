import functools
import json
from typing import Any, Callable, Optional
from app.utils.redis import get_cache, set_cache
import structlog

logger = structlog.get_logger()


def cached(key_prefix: str, expire: int = 300):
    """
    Decorator to cache function results in Redis.
    
    Args:
        key_prefix: Prefix for the cache key
        expire: Expiration time in seconds (default 5 minutes)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            # Generate cache key from function arguments
            key_parts = [key_prefix]
            
            # Add positional arguments
            for arg in args:
                if hasattr(arg, '__dict__'):
                    # For objects, try to get an ID or use string representation
                    if hasattr(arg, 'id'):
                        key_parts.append(str(arg.id))
                    else:
                        key_parts.append(str(arg))
                else:
                    key_parts.append(str(arg))
            
            # Add keyword arguments
            for k, v in sorted(kwargs.items()):
                if hasattr(v, '__dict__'):
                    if hasattr(v, 'id'):
                        key_parts.append(f"{k}:{v.id}")
                    else:
                        key_parts.append(f"{k}:{v}")
                else:
                    key_parts.append(f"{k}:{v}")
            
            cache_key = ":".join(key_parts)
            
            # Try to get from cache
            cached_value = await get_cache(cache_key)
            if cached_value is not None:
                logger.debug("Cache hit", key=cache_key)
                return cached_value
            
            # If not in cache, call the function
            logger.debug("Cache miss", key=cache_key)
            result = await func(*args, **kwargs)
            
            # Store in cache
            await set_cache(cache_key, result, expire=expire)
            
            return result
        return wrapper
    return decorator