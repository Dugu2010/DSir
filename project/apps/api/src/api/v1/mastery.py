from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.dependencies import get_current_active_user
from src.db.session import get_db
from src.models.content import Concept
from src.models.learning import ConceptMastery
from src.models.user import User
from src.schemas.common import PaginatedResponse, PaginationParams
from src.schemas.mastery import ConceptMasteryRead, StrengthsWeaknesses
from src.services.mastery import MasteryEngine

router = APIRouter()


@router.get("/", response_model=PaginatedResponse)
async def list_mastery(
    pagination: PaginationParams = Depends(),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse:
    query = select(ConceptMastery).where(ConceptMastery.user_id == current_user.id)
    total_result = await db.execute(query)
    total = len(total_result.scalars().all())

    result = await db.execute(
        query.order_by(ConceptMastery.score.asc())
        .offset((pagination.page - 1) * pagination.per_page)
        .limit(pagination.per_page)
    )
    masteries = result.scalars().all()

    return PaginatedResponse(
        items=[ConceptMasteryRead.model_validate(m).model_dump() for m in masteries],
        total=total,
        page=pagination.page,
        per_page=pagination.per_page,
        pages=(total + pagination.per_page - 1) // pagination.per_page,
    )


@router.get("/concept/{concept_id}", response_model=ConceptMasteryRead)
async def get_concept_mastery(
    concept_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ConceptMasteryRead:
    engine = MasteryEngine(db)
    mastery = await engine.get_mastery(current_user.id, concept_id)
    return ConceptMasteryRead.model_validate(mastery)


@router.get("/strengths-weaknesses", response_model=StrengthsWeaknesses)
async def get_strengths_weaknesses(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StrengthsWeaknesses:
    engine = MasteryEngine(db)
    strengths, weaknesses = await engine.get_strengths_and_weaknesses(current_user.id)
    return StrengthsWeaknesses(
        strengths=[ConceptMasteryRead.model_validate(m) for m in strengths],
        weaknesses=[ConceptMasteryRead.model_validate(m) for m in weaknesses],
    )


@router.post("/record", response_model=ConceptMasteryRead)
async def record_attempt(
    concept_id: UUID,
    is_correct: bool,
    source: str = "exercise",
    difficulty: float = 1.0,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ConceptMasteryRead:
    result = await db.execute(select(Concept).where(Concept.id == concept_id))
    if result.scalar_one_or_none() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Concept not found")

    engine = MasteryEngine(db)
    mastery = await engine.record_attempt(current_user.id, concept_id, is_correct, difficulty, source)
    response = ConceptMasteryRead.model_validate(mastery)
    await db.commit()
    return response


@router.post("/apply-decay/{concept_id}", response_model=ConceptMasteryRead)
async def apply_decay(
    concept_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ConceptMasteryRead:
    engine = MasteryEngine(db)
    mastery = await engine.apply_decay(current_user.id, concept_id)
    await db.commit()
    return ConceptMasteryRead.model_validate(mastery)
