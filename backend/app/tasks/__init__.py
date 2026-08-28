"""
Background tasks package (Celery optional).

The package exists so tasks are importable as ``app.tasks.<module>``. Celery is
optional: if the ``celery`` package is not installed, ``celery_app`` is ``None``
and the API falls back to in-process background tasks so nothing breaks.
"""
import structlog
from app.config import get_settings

logger = structlog.get_logger()
settings = get_settings()

try:
    from celery import Celery

    celery_app = Celery(
        "dsir_backend",
        broker=settings.REDIS_URL,
        backend=settings.REDIS_URL,
        include=[
            "app.tasks.ai_tasks",
            "app.tasks.email_tasks",
            "app.tasks.processing_tasks",
        ],
    )

    celery_app.conf.update(
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="UTC",
        enable_utc=True,
        task_track_started=True,
        task_time_limit=30 * 60,          # 30 minutes hard limit
        task_soft_time_limit=25 * 60,     # 25 minutes soft limit
        worker_prefetch_multiplier=1,
        worker_max_tasks_per_child=1000,
    )
    logger.info("celery.configured", broker=settings.REDIS_URL)
except ImportError:  # pragma: no cover
    celery_app = None
    logger.warning("celery.not_installed", detail="Running without a background worker")
