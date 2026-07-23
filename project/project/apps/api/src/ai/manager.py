from __future__ import annotations

import asyncio
import os
from collections.abc import AsyncGenerator, Awaitable, Callable
from functools import wraps
from typing import Any, ParamSpec, TypeVar

from src.ai.protocols import AIProvider, AIResponse, Message
from src.ai.providers import (
    AnthropicProvider,
    GeminiProvider,
    MockProvider,
    OllamaProvider,
    OpenAIProvider,
)


class AIError(Exception):
    pass


_P = ParamSpec("_P")
_R = TypeVar("_R")


def _with_retries(
    max_retries: int = 3,
    backoff: float = 1.0,
) -> Callable[[Callable[_P, Awaitable[_R]]], Callable[_P, Awaitable[_R]]]:
    def decorator(func: Callable[_P, Awaitable[_R]]) -> Callable[_P, Awaitable[_R]]:
        @wraps(func)
        async def wrapper(*args: _P.args, **kwargs: _P.kwargs) -> _R:
            last_exc: Exception | None = None
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as exc:
                    last_exc = exc
                    await asyncio.sleep(backoff * (2**attempt))
            raise AIError(f"AI provider failed after {max_retries} attempts: {last_exc}")

        return wrapper

    return decorator


class AIManager:
    def __init__(self, primary: AIProvider, fallback: AIProvider | None = None):
        self.primary = primary
        self.fallback = fallback

    @_with_retries()
    async def generate(
        self,
        messages: list[Message],
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> AIResponse:
        try:
            return await self.primary.generate(messages, temperature, max_tokens)
        except Exception:
            if self.fallback is None:
                raise
            try:
                return await self.fallback.generate(messages, temperature, max_tokens)
            except Exception as exc2:
                raise AIError("Primary and fallback AI providers failed") from exc2

    async def generate_stream(
        self,
        messages: list[Message],
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> AsyncGenerator[str, None]:
        try:
            async for chunk in self.primary.generate_stream(messages, temperature, max_tokens):
                yield chunk
        except Exception:
            if self.fallback is None:
                raise
            async for chunk in self.fallback.generate_stream(messages, temperature, max_tokens):
                yield chunk

    async def generate_text(self, *args: Any, **kwargs: Any) -> str:
        response = await self.generate(*args, **kwargs)
        return response.content

    async def embed(self, text: str, dimensions: int = 1536) -> list[float]:
        return await self.primary.embed(text, dimensions=dimensions)


def get_ai_manager(provider_name: str | None = None) -> AIManager:
    from src.core.config import settings

    name = (provider_name or settings.AI_DEFAULT_PROVIDER).lower()
    primary = _build_provider(name)
    fallback_name = settings.AI_FALLBACK_PROVIDER
    fallback = _build_provider(fallback_name) if fallback_name else None
    return AIManager(primary, fallback)


def _build_provider(name: str) -> AIProvider:
    if name == "openai":
        return OpenAIProvider(api_key=os.getenv("OPENAI_API_KEY"))
    if name == "anthropic":
        return AnthropicProvider(api_key=os.getenv("ANTHROPIC_API_KEY"))
    if name == "gemini":
        return GeminiProvider(api_key=os.getenv("GEMINI_API_KEY"))
    if name == "ollama":
        return OllamaProvider(base_url=os.getenv("OLLAMA_BASE_URL"))
    return MockProvider()
