from __future__ import annotations

import asyncio
import logging
import time
from collections import defaultdict
from typing import ClassVar

from fastapi import HTTPException, Request, status

from src.core.config import settings

try:
    import redis.asyncio as redis

    HAS_REDIS = True
except ImportError:  # pragma: no cover
    HAS_REDIS = False


logger = logging.getLogger(__name__)


class _MemoryStore:
    _data: ClassVar[dict[str, list[float]]] = defaultdict(list)
    _lock = asyncio.Lock()

    async def increment(self, key: str, window: int, limit: int) -> int:
        now = time.time()
        async with self._lock:
            cutoff = now - window
            current = [ts for ts in self._data[key] if ts > cutoff]
            if not current:
                self._data.pop(key, None)
            else:
                self._data[key] = current
            current.append(now)
            self._data[key] = current
            return len(current)


_memory_store = _MemoryStore()

_redis_client = redis.from_url(settings.REDIS_URL) if HAS_REDIS else None  # type: ignore[no-untyped-call]


class RateLimitExceeded(HTTPException):
    def __init__(self, detail: str = "Rate limit exceeded") -> None:
        super().__init__(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=detail)


def _parse_rate(rate: str) -> tuple[int, int]:
    # rate format: "<count>/<unit>" e.g. "10/minute"
    count_str, unit = rate.split("/")
    count = int(count_str)
    if unit.startswith("minute"):
        window = 60
    elif unit.startswith("hour"):
        window = 3600
    elif unit.startswith("day"):
        window = 86400
    elif unit.startswith("second"):
        window = 1
    else:
        window = 60
    return count, window


class RateLimiter:
    def __init__(self, rate: str = "100/minute") -> None:
        self.limit, self.window = _parse_rate(rate)

    async def check(self, key: str) -> None:
        if not settings.RATE_LIMIT_ENABLED:
            return
        if _redis_client is not None:
            try:
                now = int(time.time())
                window_key = f"rate_limit:{key}:{now // self.window}"
                current = await _redis_client.incr(window_key)
                if current == 1:
                    await _redis_client.expire(window_key, self.window)
                if current > self.limit:
                    raise RateLimitExceeded()
            except redis.RedisError:  # pragma: no cover - fallback when Redis is unavailable
                logger.warning("Redis unavailable for rate limiting; falling back to in-memory store")
                count = await _memory_store.increment(key, self.window, self.limit)
                if count > self.limit:
                    raise RateLimitExceeded() from None
        else:
            count = await _memory_store.increment(key, self.window, self.limit)
            if count > self.limit:
                raise RateLimitExceeded()

    async def __call__(self, request: Request) -> None:
        if not settings.RATE_LIMIT_ENABLED:
            return
        key = rate_limit_key(request)
        await self.check(key)


def rate_limit_key(request: Request, suffix: str | None = None) -> str:
    client_ip = request.client.host if request.client else "unknown"
    key = f"{client_ip}:{suffix}" if suffix else client_ip
    return key
