from __future__ import annotations

from datetime import datetime
from typing import Any, cast
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.ai.manager import get_ai_manager
from src.core.dependencies import get_current_active_user
from src.db.session import get_db
from src.models.revision import RevisionSchedule, RevisionSession
from src.models.user import User
from src.schemas.common import PaginatedResponse, PaginationParams
from src.schemas.revision import (
    ActiveRecallProblemRead,
    ActiveRecallSessionRead,
    GenerateProblemRequest,
    ReviewRequest,
    ReviewResponse,
    RevisionAnalyticsRead,
    RevisionScheduleRead,
    RevisionSessionRead,
    RevisionSessionStart,
)
from src.services.revision import RevisionEngine

router = APIRouter()


async def _get_revision_engine(
    db: AsyncSession = Depends(get_db),
) -> RevisionEngine:
    return RevisionEngine(db, get_ai_manager())


@router.get("/due", response_model=list[RevisionScheduleRead])
async def get_due_revisions(
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    engine: RevisionEngine = Depends(_get_revision_engine),
) -> list[RevisionSchedule]:
    return await engine.build_revision_queue(current_user.id, limit=limit)


@router.get("/schedule/{concept_id}", response_model=RevisionScheduleRead)
async def get_schedule(
    concept_id: UUID,
    current_user: User = Depends(get_current_active_user),
    engine: RevisionEngine = Depends(_get_revision_engine),
) -> RevisionSchedule:
    schedule = await engine.get_schedule(current_user.id, concept_id)
    return schedule


@router.post("/review", response_model=ReviewResponse)
async def submit_review(
    data: ReviewRequest,
    current_user: User = Depends(get_current_active_user),
    engine: RevisionEngine = Depends(_get_revision_engine),
    db: AsyncSession = Depends(get_db),
) -> ReviewResponse:
    schedule = await engine.schedule_review(current_user.id, data.concept_id, data.quality)

    response = ReviewResponse(
        concept_id=data.concept_id,
        quality=data.quality,
        new_interval_days=schedule.interval_days,
        new_ease_factor=schedule.ease_factor,
        due_at=schedule.due_at,
    )
    await db.commit()
    return response


@router.post("/problems/generate", response_model=ActiveRecallProblemRead, status_code=status.HTTP_201_CREATED)
async def generate_revision_problem(
    data: GenerateProblemRequest,
    current_user: User = Depends(get_current_active_user),
    engine: RevisionEngine = Depends(_get_revision_engine),
    db: AsyncSession = Depends(get_db),
) -> ActiveRecallProblemRead:
    problem = await engine.generate_problem(
        user_id=current_user.id,
        concept_id=data.concept_id,
        difficulty=data.difficulty,
        mistakes=data.mistakes,
    )
    await db.commit()
    return ActiveRecallProblemRead(
        concept_id=problem.concept_id,
        problem=problem.problem_data,
        due_at=None,
    )


@router.post("/problems/active/{concept_id}", response_model=ActiveRecallProblemRead)
async def get_active_recall_problem(
    concept_id: UUID,
    current_user: User = Depends(get_current_active_user),
    engine: RevisionEngine = Depends(_get_revision_engine),
    db: AsyncSession = Depends(get_db),
) -> ActiveRecallProblemRead:
    problem = await engine.get_active_recall_problem(current_user.id, concept_id)
    await db.commit()
    return ActiveRecallProblemRead(
        concept_id=problem.concept_id,
        problem=problem.problem_data,
        due_at=None,
    )


@router.post("/sessions/active", response_model=ActiveRecallSessionRead, status_code=status.HTTP_201_CREATED)
async def start_active_recall_session(
    data: RevisionSessionStart,
    current_user: User = Depends(get_current_active_user),
    engine: RevisionEngine = Depends(_get_revision_engine),
    db: AsyncSession = Depends(get_db),
) -> ActiveRecallSessionRead:
    result: dict[str, object] = await engine.start_active_recall_session(current_user.id, data.concept_ids)
    await db.commit()
    raw_problems = cast(list[dict[str, Any]], result["problems"])

    def _parse_due(value: object) -> datetime | None:
        if value is None:
            return None
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            return datetime.fromisoformat(value)
        return None

    problems = [
        ActiveRecallProblemRead(
            concept_id=UUID(str(p["concept_id"])),
            problem=cast(dict[str, Any], p["problem"]),
            due_at=_parse_due(p.get("due_at")),
        )
        for p in raw_problems
    ]
    return ActiveRecallSessionRead(session_id=UUID(str(result["session_id"])), problems=problems)


@router.post("/sessions", response_model=RevisionSessionRead, status_code=status.HTTP_201_CREATED)
async def start_revision_session(
    data: RevisionSessionStart,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> RevisionSession:
    session = RevisionSession(
        user_id=current_user.id,
        concepts=data.concept_ids or [],
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session


@router.put("/sessions/{session_id}/complete", response_model=RevisionSessionRead)
async def complete_revision_session(
    session_id: UUID,
    results: dict[str, Any],
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> RevisionSession:
    result = await db.execute(select(RevisionSession).where(RevisionSession.id == session_id))
    session = result.scalar_one_or_none()
    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    from datetime import UTC, datetime

    session.completed_at = datetime.now(UTC)
    session.results = results
    await db.commit()
    await db.refresh(session)
    return session


@router.get("/sessions", response_model=PaginatedResponse)
async def list_revision_sessions(
    pagination: PaginationParams = Depends(),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse:
    from src.core.pagination import paginated_response
    from src.schemas.revision import RevisionSessionRead

    query = select(RevisionSession).where(RevisionSession.user_id == current_user.id)
    return await paginated_response(db, query, pagination, RevisionSessionRead)


@router.get("/analytics", response_model=RevisionAnalyticsRead)
async def get_revision_analytics(
    current_user: User = Depends(get_current_active_user),
    engine: RevisionEngine = Depends(_get_revision_engine),
) -> RevisionAnalyticsRead:
    data = cast(dict[str, int], await engine.get_analytics(current_user.id))
    return RevisionAnalyticsRead(**data)
