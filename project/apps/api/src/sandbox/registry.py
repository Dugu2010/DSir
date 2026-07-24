from __future__ import annotations

from src.core.config import settings
from src.sandbox.interfaces import CodeSandbox
from src.sandbox.providers import MockSandbox, PistonSandbox


class SandboxRegistry:
    """Registry of code execution sandbox providers."""

    _providers: dict[str, type[CodeSandbox]] = {
        "mock": MockSandbox,
        "piston": PistonSandbox,
    }

    @classmethod
    def register(cls, name: str, provider: type[CodeSandbox]) -> None:
        """Register a new sandbox provider."""
        cls._providers[name] = provider

    @classmethod
    def get(cls, name: str | None = None, **kwargs: object) -> CodeSandbox:
        """Return a sandbox provider instance by name.

        Defaults to the configured provider or the first registered one.
        """
        provider_name = name or ("piston" if settings.PISTON_BASE_URL else "mock")
        provider_cls = cls._providers.get(provider_name)
        if provider_cls is None:
            raise ValueError(f"Unknown sandbox provider: {provider_name}")
        return provider_cls(**kwargs)

    @classmethod
    def list_providers(cls) -> list[str]:
        """Return the names of all registered providers."""
        return list(cls._providers.keys())
