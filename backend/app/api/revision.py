from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models import (
    Flashcard, FlashcardReview, FlashcardStatus,
    KnowledgeTopic, UserKnowledge, Lesson,
)
from app.schemas import (
    FlashcardCreate, FlashcardResponse, FlashcardReviewSubmit,
    PaginatedResponse,
)
from app.utils.deps import get_current_active_user
from app.models import User
from uuid import UUID
from datetime import datetime, timezone, date, timedelta

router = APIRouter(prefix="/revision", tags=["Revision"])


# ── Flashcards ──────────────────────────────────────────────────

@router.get("/flashcards", response_model=PaginatedResponse)
async def list_flashcards(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    status_filter: str = Query(default=None, alias="status"),
    lesson_id: UUID = Query(default=None),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Flashcard).where(Flashcard.user_id == current_user.id)
    if status_filter:
        try:
            query = query.where(Flashcard.status == FlashcardStatus(status_filter))
        except ValueError:
            pass
    if lesson_id:
        query = query.where(Flashcard.lesson_id == lesson_id)

    count_query = select(func.count(Flashcard.id)).where(Flashcard.user_id == current_user.id)

    total = (await db.execute(count_query)).scalar()
    result = await db.execute(
        query.order_by(Flashcard.next_review_at.asc().nullsfirst())
        .offset((page - 1) * size)
        .limit(size)
    )

    return PaginatedResponse(
        items=[FlashcardResponse.model_validate(f) for f in result.scalars().all()],
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size,
    )


@router.get("/flashcards/due", response_model=list[FlashcardResponse])
async def get_due_flashcards(
    limit: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    now = datetime.now(timezone.utc)
    result = await db.execute(
        select(Flashcard)
        .where(
            Flashcard.user_id == current_user.id,
            (Flashcard.next_review_at <= now) | (Flashcard.next_review_at.is_(None)),
        )
        .order_by(Flashcard.ease_factor.asc())
        .limit(limit)
    )
    return [FlashcardResponse.model_validate(f) for f in result.scalars().all()]


@router.post("/flashcards", response_model=FlashcardResponse, status_code=status.HTTP_201_CREATED)
async def create_flashcard(
    data: FlashcardCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    card = Flashcard(
        user_id=current_user.id,
        lesson_id=data.lesson_id,
        front_content=data.front_content,
        back_content=data.back_content,
    )
    db.add(card)
    await db.flush()
    return card


@router.post("/flashcards/{card_id}/review")
async def review_flashcard(
    card_id: UUID,
    data: FlashcardReviewSubmit,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Flashcard).where(Flashcard.id == card_id, Flashcard.user_id == current_user.id)
    )
    card = result.scalar_one_or_none()
    if not card:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Flashcard not found")

    # SM-2 Spaced Repetition Algorithm
    quality = data.quality

    if quality >= 3:
        if card.repetitions == 0:
            card.interval_days = 1
        elif card.repetitions == 1:
            card.interval_days = 6
        else:
            card.interval_days = int(card.interval_days * card.ease_factor)

        card.repetitions += 1
        card.status = FlashcardStatus.REVIEW
    else:
        card.repetitions = 0
        card.interval_days = 1
        card.status = FlashcardStatus.RELEARNING

    # Update ease factor
    card.ease_factor = max(1.3, float(card.ease_factor) + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)))

    card.last_reviewed_at = datetime.now(timezone.utc)
    card.next_review_at = datetime.now(timezone.utc) + timedelta(days=card.interval_days)

    # Record review
    review = FlashcardReview(
        flashcard_id=card_id,
        user_id=current_user.id,
        quality=quality,
        time_spent_seconds=data.time_spent_seconds,
    )
    db.add(review)

    return {
        "detail": "Flashcard reviewed",
        "next_review_at": card.next_review_at.isoformat(),
        "interval_days": card.interval_days,
    }


@router.delete("/flashcards/{card_id}")
async def delete_flashcard(
    card_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Flashcard).where(Flashcard.id == card_id, Flashcard.user_id == current_user.id)
    )
    card = result.scalar_one_or_none()
    if not card:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Flashcard not found")
    await db.delete(card)
    return {"detail": "Flashcard deleted"}


# ── Revision Stats ──────────────────────────────────────────────

@router.get("/stats")
async def get_revision_stats(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    # Count cards by status
    status_counts = {}
    for s in FlashcardStatus:
        count_result = await db.execute(
            select(func.count(Flashcard.id)).where(
                Flashcard.user_id == current_user.id,
                Flashcard.status == s,
            )
        )
        status_counts[s.value] = count_result.scalar() or 0

    # Due today
    now = datetime.now(timezone.utc)
    due_result = await db.execute(
        select(func.count(Flashcard.id)).where(
            Flashcard.user_id == current_user.id,
            (Flashcard.next_review_at <= now) | (Flashcard.next_review_at.is_(None)),
        )
    )

    # Weekly reviews
    week_ago = now - timedelta(days=7)
    weekly_result = await db.execute(
        select(func.count(FlashcardReview.id)).where(
            FlashcardReview.user_id == current_user.id,
            FlashcardReview.reviewed_at >= week_ago,
        )
    )

    # Average ease
    ease_result = await db.execute(
        select(func.avg(Flashcard.ease_factor)).where(Flashcard.user_id == current_user.id)
    )

    return {
        "total_cards": sum(status_counts.values()),
        "by_status": status_counts,
        "due_today": due_result.scalar() or 0,
        "reviewed_this_week": weekly_result.scalar() or 0,
        "average_ease_factor": round(float(ease_result.scalar() or 2.5), 2),
    }
