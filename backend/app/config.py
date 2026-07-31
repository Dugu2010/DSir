from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "DSir API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 4

    # Database - Render provides postgres:// which we convert to postgresql+psycopg://
    DATABASE_URL: str = "postgresql+psycopg://postgres:postgres@localhost:5432/dsir"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10
    DATABASE_POOL_RECYCLE: int = 3600

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_PASSWORD: Optional[str] = None

    # JWT / Auth
    JWT_SECRET_KEY: str = "change-me-in-production-use-a-strong-random-secret"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # OAuth
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GITHUB_CLIENT_ID: Optional[str] = None
    GITHUB_CLIENT_SECRET: Optional[str] = None

    # AI Providers
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    AI_DEFAULT_PROVIDER: str = "openai"
    AI_DEFAULT_MODEL: str = "gpt-4o-mini"

    # Sandbox
    SANDBOX_DOCKER_IMAGE: str = "dsir-sandbox:latest"
    SANDBOX_MAX_EXECUTION_TIME: int = 30
    SANDBOX_MAX_MEMORY_MB: int = 256
    SANDBOX_MAX_CONCURRENT: int = 10

    # Storage
    STORAGE_BACKEND: str = "local"
    STORAGE_LOCAL_PATH: str = "./uploads"
    S3_BUCKET: Optional[str] = None
    S3_ENDPOINT: Optional[str] = None
    S3_ACCESS_KEY: Optional[str] = None
    S3_SECRET_KEY: Optional[str] = None

    # Rate Limiting
    RATE_LIMIT_GLOBAL: int = 100
    RATE_LIMIT_GLOBAL_WINDOW: int = 60
    RATE_LIMIT_AUTH: int = 10
    RATE_LIMIT_AUTH_WINDOW: int = 60

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "https://dsir-umber.vercel.app", "https://dsir.vercel.app"]

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    # Email
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: Optional[int] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAIL_FROM: str = "noreply@dsir.dev"

    # Feature Flags
    ENABLE_AI_FEATURES: bool = True
    ENABLE_SANDBOX: bool = True
    ENABLE_REGISTRATION: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()
