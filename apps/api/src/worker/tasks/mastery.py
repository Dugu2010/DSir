from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import select

from src.db.session import AsyncSessionLocal
from src.models.learning import ConceptMastery
from src.services.mastery import MasteryEngine
from src.worker.celery_app import celery_app
from src.worker.utils import async_to_sync


@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    autoretry_for=(Exception,),
    queue="mastery",
)  # type: ignore[untyped-decorator]
def apply_decay_for_mastery(self: Any, user_id: str, concept_id: str) -> dict[str, object]:
    """Apply mastery decay for a single user/concept pair."""

    async def _run() -> dict[str, object]:
        async with AsyncSessionLocal() as db:
            engine = MasteryEngine(db)
            mastery = await engine.apply_decay(UUID(user_id), UUID(concept_id))
            await db.commit()
        return {
            "user_id": str(user_id),
            "concept_id": str(concept_id),
            "score": mastery.score,
            "confidence": mastery.confidence,
        }

    return async_to_sync(_run)()


@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    autoretry_for=(Exception,),
    queue="mastery",
)  # type: ignore[untyped-decorator]
def apply_decay_all(self: Any) -> dict[str, int]:
    """Apply mastery decay to all masteries that haven't been reviewed recently."""

    async def _run() -> dict[str, int]:
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(ConceptMastery.id, ConceptMastery.user_id, ConceptMastery.concept_id))
            rows = result.all()

        total = 0
        for row in rows:
            apply_decay_for_mastery.delay(str(row.user_id), str(row.concept_id))
            total += 1
        return {"queued": total}

    return async_to_sync(_run)()
