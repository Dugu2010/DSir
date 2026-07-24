from __future__ import annotations

import asyncio
from collections.abc import Callable, Coroutine
from typing import Any, TypeVar

T = TypeVar("T")


def run_async(coro: Coroutine[Any, Any, T]) -> T:
    """Run an async coroutine from a synchronous Celery task."""
    return asyncio.run(coro)


def async_to_sync(func: Callable[..., Coroutine[Any, Any, T]]) -> Callable[..., T]:
    """Decorator that wraps an async function so it can be called as sync."""

    def wrapper(*args: Any, **kwargs: Any) -> T:
        return run_async(func(*args, **kwargs))

    return wrapper
