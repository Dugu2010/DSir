from __future__ import annotations

from celery import Celery

from src.core.config import settings

celery_app = Celery(
    "dsir_worker",
    broker=settings.CELERY_BROKER_URL or settings.REDIS_URL,
    backend=settings.CELERY_RESULT_BACKEND or settings.REDIS_URL,
    include=[
        "src.worker.tasks.revision",
        "src.worker.tasks.mastery",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_default_queue="default",
    task_routes={
        "revision.*": {"queue": "revision"},
        "mastery.*": {"queue": "mastery"},
        "ai.*": {"queue": "ai"},
    },
    result_expires=3600,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,
)

celery_app.conf.beat_schedule = {
    "nightly-mastery-decay": {
        "task": "mastery.apply_decay_all",
        "schedule": 60 * 60 * 24,  # daily
    },
    "pregenerate-revisions": {
        "task": "revision.pregenerate_all",
        "schedule": 60 * 60 * 6,  # every 6 hours
    },
}
