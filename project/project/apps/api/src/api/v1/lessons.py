from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.dependencies import get_current_active_user, require_content_creator
from src.db.session import get_db
from src.models.content import Concept, Lesson
from src.models.learning import Enrollment, LessonProgress, UserActivity
from src.models.user import User
from src.schemas.common import PaginatedResponse, PaginationParams
from src.schemas.lesson import LessonCreate, LessonDetail, LessonProgressUpdate, LessonRead
from src.services.gamification import record_activity

router = APIRouter()


@router.get("/concept/{concept_id}", response_model=PaginatedResponse)
async def list_lessons(
    concept_id: UUID,
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse:
    total_result = await db.execute(select(Lesson).where(Lesson.concept_id == concept_id))
    total = len(total_result.scalars().all())

    result = await db.execute(
        select(Lesson)
        .where(Lesson.concept_id == concept_id)
        .order_by(Lesson.position)
        .offset((pagination.page - 1) * pagination.per_page)
        .limit(pagination.per_page)
    )
    lessons = result.scalars().all()

    return PaginatedResponse(
        items=[LessonRead.model_validate(lesson).model_dump() for lesson in lessons],
        total=total,
        page=pagination.page,
        per_page=pagination.per_page,
        pages=(total + pagination.per_page - 1) // pagination.per_page,
    )


@router.get("/{lesson_id}", response_model=LessonDetail)
async def get_lesson(lesson_id: UUID, db: AsyncSession = Depends(get_db)) -> Lesson:
    result = await db.execute(select(Lesson).where(Lesson.id == lesson_id))
    lesson = result.scalar_one_or_none()
    if lesson is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found")
    return lesson


@router.get("/concept/{concept_id}/next", response_model=LessonRead | None)
async def get_next_lesson(
    concept_id: UUID, current_lesson_id: UUID, db: AsyncSession = Depends(get_db)
) -> Lesson | None:
    result = await db.execute(
        select(Lesson)
        .where(Lesson.concept_id == concept_id, Lesson.id != current_lesson_id)
        .order_by(Lesson.position)
        .limit(1)
    )
    return result.scalar_one_or_none()


@router.post("/", response_model=LessonRead, status_code=status.HTTP_201_CREATED)
async def create_lesson(
    lesson: LessonCreate,
    current_user: User = Depends(require_content_creator),
    db: AsyncSession = Depends(get_db),
) -> Lesson:
    concept = await db.execute(select(Concept).where(Concept.id == lesson.concept_id))
    if concept.scalar_one_or_none() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Concept not found")

    db_lesson = Lesson(**lesson.model_dump(exclude={"id", "created_at"}))
    db.add(db_lesson)
    await db.commit()
    await db.refresh(db_lesson)
    return db_lesson


@router.post("/{lesson_id}/progress", response_model=dict)
async def update_lesson_progress(
    lesson_id: UUID,
    data: LessonProgressUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, object]:
    result = await db.execute(select(Lesson).where(Lesson.id == lesson_id))
    lesson = result.scalar_one_or_none()
    if lesson is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found")

    progress_result = await db.execute(
        select(LessonProgress).where(
            LessonProgress.user_id == current_user.id,
            LessonProgress.lesson_id == lesson_id,
        )
    )
    progress = progress_result.scalar_one_or_none()
    if progress is None:
        progress = LessonProgress(user_id=current_user.id, lesson_id=lesson_id)
        db.add(progress)

    newly_completed = data.is_completed and not progress.is_completed
    if newly_completed:
        progress.completed_at = datetime.now(UTC)
    progress.is_completed = data.is_completed
    if not data.is_completed:
        progress.completed_at = None

    await db.flush()

    if newly_completed:
        await record_activity(current_user, db, xp_gain=10)
        activity = UserActivity(
            user_id=current_user.id,
            activity_type="completed_lesson",
            entity_type="lesson",
            entity_id=lesson_id,
        )
        db.add(activity)

    # Update enrollment progress for this course
    concept_result = await db.execute(select(Concept).where(Concept.id == lesson.concept_id))
    concept = concept_result.scalar_one_or_none()
    if concept:
        enrollment_result = await db.execute(
            select(Enrollment).where(
                Enrollment.user_id == current_user.id,
                Enrollment.course_id == concept.course_id,
            )
        )
        enrollment = enrollment_result.scalar_one_or_none()
        if enrollment:
            total_result = await db.execute(
                select(Lesson.id).where(
                    Lesson.concept_id.in_(select(Concept.id).where(Concept.course_id == concept.course_id))
                )
            )
            total_lessons = len(total_result.scalars().all())
            completed_result = await db.execute(
                select(LessonProgress)
                .join(Lesson)
                .join(Concept)
                .where(
                    LessonProgress.user_id == current_user.id,
                    Concept.course_id == concept.course_id,
                    LessonProgress.is_completed.is_(True),
                )
            )
            completed_count = len(completed_result.scalars().all())
            enrollment.progress_percent = int((completed_count / max(total_lessons, 1)) * 100)
            if data.is_completed:
                enrollment.last_lesson_id = lesson_id

    await db.commit()
    await db.refresh(progress)

    return {
        "id": str(progress.id),
        "user_id": str(progress.user_id),
        "lesson_id": str(progress.lesson_id),
        "is_completed": progress.is_completed,
        "completed_at": progress.completed_at.isoformat() if progress.completed_at else None,
        "created_at": progress.created_at.isoformat() if progress.created_at else None,
        "updated_at": progress.updated_at.isoformat() if progress.updated_at else None,
    }


@router.get("/{lesson_id}/progress", response_model=dict)
async def get_lesson_progress(
    lesson_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, object]:
    result = await db.execute(
        select(LessonProgress).where(
            LessonProgress.user_id == current_user.id,
            LessonProgress.lesson_id == lesson_id,
        )
    )
    progress = result.scalar_one_or_none()
    if progress is None:
        return {
            "lesson_id": str(lesson_id),
            "is_completed": False,
            "completed_at": None,
        }
    return {
        "id": str(progress.id),
        "user_id": str(progress.user_id),
        "lesson_id": str(progress.lesson_id),
        "is_completed": progress.is_completed,
        "completed_at": progress.completed_at.isoformat() if progress.completed_at else None,
        "created_at": progress.created_at.isoformat() if progress.created_at else None,
        "updated_at": progress.updated_at.isoformat() if progress.updated_at else None,
    }
