from __future__ import annotations

import json
from typing import Any

from pydantic_settings import BaseSettings, SettingsConfigDict


def parse_cors_origins(value: Any) -> list[str]:
    """Parse CORS_ORIGINS from a JSON list or comma-separated string."""
    if not isinstance(value, str):
        return value if isinstance(value, list) else []
    stripped = value.strip()
    if stripped.startswith("["):
        try:
            parsed = json.loads(stripped)
            if isinstance(parsed, list):
                return [str(item).strip() for item in parsed if str(item).strip()]
        except json.JSONDecodeError:
            pass
    return [origin.strip() for origin in value.split(",") if origin.strip()]


class Settings(BaseSettings):
    # Environment
    ENVIRONMENT: str = "development"

    # Database / Cache
    DATABASE_URL: str = "postgresql+asyncpg://dsir:dsir@localhost:5432/dsir"
    REDIS_URL: str = "redis://localhost:6379/0"

    # Security
    SECRET_KEY: str = "dev-secret-change-me"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"

    # CORS
    CORS_ORIGINS: str = "http://localhost:3000"

    # AI
    AI_DEFAULT_PROVIDER: str = "mock"
    AI_FALLBACK_PROVIDER: str | None = None
    OPENAI_API_KEY: str | None = None
    ANTHROPIC_API_KEY: str | None = None
    GEMINI_API_KEY: str | None = None
    OLLAMA_BASE_URL: str | None = None

    # Rate limiting (requests per minute)
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_DEFAULT: str = "100/minute"
    RATE_LIMIT_AUTH: str = "10/minute"

    # Code execution
    PISTON_BASE_URL: str | None = None
    EXECUTION_TIMEOUT_MS: int = 3000
    EXECUTION_MEMORY_MB: int = 128

    # Workers
    CELERY_BROKER_URL: str | None = None
    CELERY_RESULT_BACKEND: str | None = None

    # Observability
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env")


def _validate_secret_key(secret: str, environment: str) -> None:
    if environment.lower() == "production":
        insecure = {
            "dev-secret-change-me",
            "secret",
            "changeme",
            "password",
        }
        if not secret or secret.strip().lower() in insecure:
            raise ValueError("SECRET_KEY must be set to a strong random value in production")


settings = Settings()
_validate_secret_key(settings.SECRET_KEY, settings.ENVIRONMENT)
