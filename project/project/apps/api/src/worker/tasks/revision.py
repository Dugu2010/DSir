from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import select

from src.ai.manager import get_ai_manager
from src.db.session import AsyncSessionLocal
from src.models.learning import Enrollment
from src.services.revision import RevisionEngine
from src.worker.celery_app import celery_app
from src.worker.utils import async_to_sync


@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    autoretry_for=(Exception,),
    queue="revision",
)  # type: ignore[untyped-decorator]
def pregenerate_revisions_for_user(self: Any, user_id: str) -> dict[str, int]:
    """Pre-generate active recall problems for a single user's due concepts."""

    async def _run() -> dict[str, int]:
        async with AsyncSessionLocal() as db:
            engine = RevisionEngine(db, get_ai_manager())
            due = await engine.build_revision_queue(UUID(user_id), limit=10)
            count = 0
            for schedule in due:
                await engine.generate_problem(
                    user_id=schedule.user_id,
                    concept_id=schedule.concept_id,
                    concept_title="",
                )
                count += 1
            await db.commit()
        return {"generated": count}

    return async_to_sync(_run)()


@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    autoretry_for=(Exception,),
    queue="revision",
)  # type: ignore[untyped-decorator]
def pregenerate_all(self: Any) -> dict[str, int]:
    """Pre-generate revision problems for all active learners."""

    async def _run() -> dict[str, int]:
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(Enrollment.user_id).distinct())
            user_ids = [row[0] for row in result.all()]

        total = 0
        for user_id in user_ids:
            res = pregenerate_revisions_for_user.delay(str(user_id))
            if res:
                total += 1
        return {"queued": total, "users": len(user_ids)}

    return async_to_sync(_run)()
