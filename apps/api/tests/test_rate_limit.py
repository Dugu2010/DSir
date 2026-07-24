from __future__ import annotations

from collections.abc import Generator

import pytest
from fastapi import Depends, FastAPI, Request, status
from fastapi.testclient import TestClient

from src.core.config import settings
from src.core.rate_limit import RateLimiter, RateLimitExceeded, _MemoryStore


@pytest.fixture(autouse=True)
def _reset_rate_limit_state() -> Generator[None, None, None]:
    _MemoryStore._data.clear()
    original = settings.RATE_LIMIT_ENABLED
    settings.RATE_LIMIT_ENABLED = True
    yield
    settings.RATE_LIMIT_ENABLED = original
    _MemoryStore._data.clear()


@pytest.mark.asyncio
async def test_memory_store_cleans_expired_keys() -> None:
    store = _MemoryStore()
    # Seed a timestamp that is well outside the 1-second window.
    store._data["key-a"].append(0.0)
    count = await store.increment("key-a", window=1, limit=10)
    # Expired entry should be removed and a new one appended.
    assert count == 1
    assert "key-a" in store._data


@pytest.mark.asyncio
async def test_rate_limiter_enforces_limit() -> None:
    limiter = RateLimiter("2/minute")
    await limiter.check("key-b")
    await limiter.check("key-b")
    with pytest.raises(RateLimitExceeded):
        await limiter.check("key-b")


def test_rate_limiter_dependency_rejects_excess_requests() -> None:
    app = FastAPI()

    @app.get("/test")
    async def test_endpoint(
        request: Request,
        _rate_limit: None = Depends(RateLimiter("2/minute")),
    ) -> dict[str, str]:
        return {"ok": "true"}

    client = TestClient(app)
    assert client.get("/test").status_code == 200
    assert client.get("/test").status_code == 200
    response = client.get("/test")
    assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
