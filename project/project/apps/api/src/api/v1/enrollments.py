from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.core.dependencies import get_current_active_user
from src.db.session import get_db
from src.models.content import Concept, Course, Lesson, Roadmap
from src.models.learning import Enrollment, LessonProgress
from src.models.user import User
from src.schemas.common import PaginatedResponse, PaginationParams
from src.schemas.content import CourseRead
from src.schemas.enrollment import EnrollmentCreate, EnrollmentRead

router = APIRouter()


@router.get("/", response_model=PaginatedResponse)
async def list_enrollments(
    pagination: PaginationParams = Depends(),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse:
    query = select(Enrollment).where(Enrollment.user_id == current_user.id).options(selectinload(Enrollment.course))
    total_result = await db.execute(query)
    total = len(total_result.scalars().all())

    result = await db.execute(
        query.order_by(Enrollment.started_at.desc())
        .offset((pagination.page - 1) * pagination.per_page)
        .limit(pagination.per_page)
    )
    enrollments = result.unique().scalars().all()

    items = []
    for enrollment in enrollments:
        item = EnrollmentRead.model_validate(enrollment).model_dump()
        item["course"] = CourseRead.model_validate(enrollment.course).model_dump() if enrollment.course else None
        items.append(item)

    return PaginatedResponse(
        items=items,
        total=total,
        page=pagination.page,
        per_page=pagination.per_page,
        pages=(total + pagination.per_page - 1) // pagination.per_page,
    )


@router.get("/my-learning", response_model=dict)
async def get_my_learning(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, object]:
    enrollments_result = await db.execute(
        select(Enrollment).where(Enrollment.user_id == current_user.id).options(selectinload(Enrollment.course))
    )
    enrollments = enrollments_result.unique().scalars().all()

    # Get completed lessons per course
    completed_counts: dict[UUID, int] = {}
    total_counts: dict[UUID, int] = {}

    for enrollment in enrollments:
        if enrollment.course_id is None:
            continue
        total_result = await db.execute(
            select(func.count(Lesson.id)).join(Concept).where(Concept.course_id == enrollment.course_id)
        )
        total_counts[enrollment.course_id] = total_result.scalar() or 0

        completed_result = await db.execute(
            select(func.count(LessonProgress.id))
            .join(Lesson)
            .join(Concept)
            .where(
                LessonProgress.user_id == current_user.id,
                Concept.course_id == enrollment.course_id,
                LessonProgress.is_completed.is_(True),
            )
        )
        completed_counts[enrollment.course_id] = completed_result.scalar() or 0

    items = []
    for enrollment in enrollments:
        total = total_counts.get(enrollment.course_id, 0) if enrollment.course_id else 0
        completed = completed_counts.get(enrollment.course_id, 0) if enrollment.course_id else 0
        progress_percent = int((completed / max(total, 1)) * 100)

        items.append(
            {
                "enrollment": EnrollmentRead.model_validate(enrollment).model_dump(),
                "course": CourseRead.model_validate(enrollment.course).model_dump() if enrollment.course else None,
                "progress": {
                    "completed_lessons": completed,
                    "total_lessons": total,
                    "progress_percent": progress_percent,
                },
            }
        )

    return {"items": items}


@router.post("/", response_model=EnrollmentRead, status_code=status.HTTP_201_CREATED)
async def create_enrollment(
    data: EnrollmentCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Enrollment:
    if data.roadmap_id:
        result = await db.execute(select(Roadmap).where(Roadmap.id == data.roadmap_id))
        if result.scalar_one_or_none() is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Roadmap not found")

    if data.course_id:
        result = await db.execute(select(Course).where(Course.id == data.course_id))
        if result.scalar_one_or_none() is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    existing = await db.execute(
        select(Enrollment).where(
            Enrollment.user_id == current_user.id,
            Enrollment.roadmap_id == data.roadmap_id,
            Enrollment.course_id == data.course_id,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Already enrolled")

    enrollment = Enrollment(
        user_id=current_user.id,
        roadmap_id=data.roadmap_id,
        course_id=data.course_id,
    )
    db.add(enrollment)
    await db.commit()
    await db.refresh(enrollment)
    return enrollment


@router.delete("/{enrollment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_enrollment(
    enrollment_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    result = await db.execute(
        select(Enrollment).where(Enrollment.id == enrollment_id, Enrollment.user_id == current_user.id)
    )
    enrollment = result.scalar_one_or_none()
    if enrollment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Enrollment not found")
    await db.delete(enrollment)
    await db.commit()
