from __future__ import annotations

from fastapi import APIRouter, Depends, status

from src.core.dependencies import require_admin
from src.models.user import User
from src.worker.tasks.mastery import apply_decay_all
from src.worker.tasks.revision import pregenerate_all

router = APIRouter()


@router.post("/pregenerate-revisions", status_code=status.HTTP_202_ACCEPTED)
async def trigger_pregenerate_revisions(
    current_user: User = Depends(require_admin),
) -> dict[str, str]:
    """Trigger pre-generation of revision problems for all active learners."""
    pregenerate_all.delay()
    return {"status": "queued", "task": "pregenerate_all"}


@router.post("/apply-decay", status_code=status.HTTP_202_ACCEPTED)
async def trigger_apply_decay(
    current_user: User = Depends(require_admin),
) -> dict[str, str]:
    """Trigger application of mastery decay for all learners."""
    apply_decay_all.delay()
    return {"status": "queued", "task": "apply_decay_all"}
