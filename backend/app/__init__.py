import logging

import structlog

from app.config import get_settings

settings = get_settings()


def configure_structlog() -> None:
    """Configure structlog based on application settings."""
    if settings.LOG_FORMAT == "json":
        renderers = [structlog.processors.JSONRenderer()]
    else:
        renderers = [structlog.dev.ConsoleRenderer(colors=True)]

    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
        ]
        + renderers,
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=False,
    )


configure_structlog()
