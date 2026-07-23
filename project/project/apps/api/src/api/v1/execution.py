from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.ai.manager import get_ai_manager
from src.core.dependencies import get_current_active_user
from src.core.rate_limit import RateLimiter
from src.db.session import get_db
from src.models.execution import ExecutionHistory
from src.models.user import User
from src.sandbox.registry import SandboxRegistry
from src.schemas.execution import (
    CodeReviewResult,
    ExecutionHistoryRead,
    ExecutionRequest,
    ExecutionResponse,
    ExecutionReviewResponse,
)
from src.services.execution import ExecutionService

router = APIRouter()


async def _get_execution_service(
    db: AsyncSession = Depends(get_db),
) -> ExecutionService:
    sandbox = SandboxRegistry.get()
    ai_manager = get_ai_manager()
    return ExecutionService(db, sandbox, ai_manager)


@router.post("/run", response_model=ExecutionResponse)
async def execute_code(
    data: ExecutionRequest,
    current_user: User = Depends(get_current_active_user),
    service: ExecutionService = Depends(_get_execution_service),
    _rate_limit: None = Depends(RateLimiter("20/minute")),
) -> ExecutionResponse:
    result, _ = await service.execute_and_log(
        user_id=current_user.id,
        request=data,
    )
    return result


@router.post("/run/review", response_model=ExecutionReviewResponse)
async def execute_and_review(
    data: ExecutionRequest,
    current_user: User = Depends(get_current_active_user),
    service: ExecutionService = Depends(_get_execution_service),
    _rate_limit: None = Depends(RateLimiter("20/minute")),
) -> ExecutionReviewResponse:
    result, history_id = await service.execute_and_log(
        user_id=current_user.id,
        request=data,
    )
    review = await service.review_code(history_id, data.code, data.language)
    return ExecutionReviewResponse(
        execution=result,
        history_id=history_id,
        ai_review=CodeReviewResult(**review),
    )


@router.get("/history", response_model=list[ExecutionHistoryRead])
async def list_execution_history(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_active_user),
    service: ExecutionService = Depends(_get_execution_service),
) -> list[ExecutionHistoryRead]:
    history = await service.get_history(current_user.id, limit=limit, offset=offset)
    return [ExecutionHistoryRead.model_validate(h) for h in history]


@router.get("/history/{history_id}", response_model=ExecutionHistoryRead)
async def get_execution_history(
    history_id: UUID,
    current_user: User = Depends(get_current_active_user),
    service: ExecutionService = Depends(_get_execution_service),
) -> ExecutionHistoryRead:
    result = await service.db.execute(
        select(ExecutionHistory).where(
            ExecutionHistory.id == history_id,
            ExecutionHistory.user_id == current_user.id,
        )
    )
    history = result.scalar_one_or_none()
    if history is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Execution not found")
    return ExecutionHistoryRead.model_validate(history)
