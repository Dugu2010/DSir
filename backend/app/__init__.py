import structlog
from app.config import get_settings

settings = get_settings()


def configure_structlog() -> None:
    """Configure structlog based on application settings."""
    # Configure structlog for JSON logging in production, console in debug
    if settings.LOG_FORMAT == "json":
        renderers = [structlog.processors.JSONRenderer()]
    else:
        renderers = [
            structlog.dev.ConsoleRenderer(colors=True)
        ]

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
        ]
        + renderers
        ,
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(structlog.stdlib, settings.LOG_LEVEL.upper(), structlog.INFO)
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=False,
    )


# Configure structlog when the app package is imported
configure_structlog()