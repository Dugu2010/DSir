from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.dependencies import get_current_active_user, get_current_user_optional, require_content_creator
from src.db.session import get_db
from src.models.content import Concept, Course, Lesson
from src.models.learning import Enrollment, LessonProgress, UserActivity
from src.models.user import User
from src.schemas.common import PaginatedResponse, PaginationParams
from src.schemas.content import (
    ConceptRead,
    CourseCreate,
    CourseRead,
    CourseUpdate,
)
from src.schemas.enrollment import EnrollmentRead
from src.schemas.lesson import LessonRead

router = APIRouter()


@router.get("/", response_model=PaginatedResponse)
async def list_courses(
    technology: str | None = None,
    programming_language: str | None = None,
    difficulty: str | None = None,
    category: str | None = None,
    search: str | None = None,
    published_only: bool = True,
    sort: str = Query("title", pattern="^(title|created_at|difficulty|estimated_duration)$"),
    order: str = Query("asc", pattern="^(asc|desc)$"),
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse:
    query = select(Course)
    if published_only:
        query = query.where(Course.is_published.is_(True))
    if technology:
        query = query.where(Course.technology == technology)
    if programming_language:
        query = query.where(Course.programming_language == programming_language)
    if difficulty:
        query = query.where(Course.difficulty.ilike(difficulty))
    if category:
        query = query.where(Course.category.ilike(category))
    if search:
        query = query.where(Course.title.ilike(f"%{search}%") | Course.description.ilike(f"%{search}%"))

    total_result = await db.execute(query)
    total = len(total_result.scalars().all())

    sort_column = getattr(Course, sort, Course.title)
    sort_column = sort_column.desc() if order == "desc" else sort_column.asc()

    result = await db.execute(
        query.order_by(sort_column).offset((pagination.page - 1) * pagination.per_page).limit(pagination.per_page)
    )
    courses = result.scalars().all()

    return PaginatedResponse(
        items=[CourseRead.model_validate(c).model_dump() for c in courses],
        total=total,
        page=pagination.page,
        per_page=pagination.per_page,
        pages=(total + pagination.per_page - 1) // pagination.per_page,
    )


@router.get("/{course_id}", response_model=CourseRead)
async def get_course(course_id: UUID, db: AsyncSession = Depends(get_db)) -> Course:
    result = await db.execute(select(Course).where(Course.id == course_id))
    course = result.scalar_one_or_none()
    if course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    return course


@router.get("/{course_id}/detail", response_model=dict)
async def get_course_detail_with_activity(
    course_id: UUID,
    current_user: User | None = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
) -> dict[str, object]:
    result = await db.execute(select(Course).where(Course.id == course_id))
    course = result.unique().scalar_one_or_none()
    if course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    # Get all concepts (modules) ordered
    concepts_result = await db.execute(
        select(Concept).where(Concept.course_id == course_id).order_by(Concept.order, Concept.created_at)
    )
    concepts = concepts_result.scalars().all()

    # Get all lessons grouped by concept
    lessons_result = await db.execute(
        select(Lesson).where(Lesson.concept_id.in_([c.id for c in concepts])).order_by(Lesson.position)
    )
    lessons = lessons_result.scalars().all()
    lessons_by_concept: dict[UUID, list[Lesson]] = {}
    for lesson in lessons:
        lessons_by_concept.setdefault(lesson.concept_id, []).append(lesson)

    # Get progress and enrollment for authenticated users
    completed_lesson_ids: set[UUID] = set()
    enrollment: Enrollment | None = None
    if current_user is not None:
        progress_result = await db.execute(
            select(LessonProgress.lesson_id).where(
                LessonProgress.user_id == current_user.id,
                LessonProgress.is_completed.is_(True),
            )
        )
        completed_lesson_ids = {row[0] for row in progress_result.all()}

        enrollment_result = await db.execute(
            select(Enrollment).where(
                Enrollment.user_id == current_user.id,
                Enrollment.course_id == course_id,
            )
        )
        enrollment = enrollment_result.scalar_one_or_none()

    modules_out = []
    total_lessons = 0
    completed_count = 0
    for concept in concepts:
        concept_lessons = lessons_by_concept.get(concept.id, [])
        module_lessons = []
        for lesson in concept_lessons:
            total_lessons += 1
            is_completed = lesson.id in completed_lesson_ids
            if is_completed:
                completed_count += 1
            module_lessons.append(
                {
                    **LessonRead.model_validate(lesson).model_dump(),
                    "is_completed": is_completed,
                }
            )

        modules_out.append(
            {
                **ConceptRead.model_validate(concept).model_dump(),
                "lessons": module_lessons,
            }
        )

    total = total_lessons if total_lessons > 0 else 1
    progress_percent = int((completed_count / total) * 100)

    if current_user is not None:
        activity = UserActivity(
            user_id=current_user.id,
            activity_type="viewed_course",
            entity_type="course",
            entity_id=course_id,
            meta={},
        )
        db.add(activity)
        await db.commit()

    return {
        "course": CourseRead.model_validate(course).model_dump(),
        "modules": modules_out,
        "enrollment": EnrollmentRead.model_validate(enrollment).model_dump() if enrollment else None,
        "progress": {
            "completed_lessons": completed_count,
            "total_lessons": total_lessons,
            "progress_percent": progress_percent,
        },
    }


@router.get("/{course_id}/continue", response_model=dict)
async def continue_course(
    course_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, object]:
    course_result = await db.execute(select(Course).where(Course.id == course_id))
    course = course_result.scalar_one_or_none()
    if course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    concepts_result = await db.execute(
        select(Concept).where(Concept.course_id == course_id).order_by(Concept.order, Concept.created_at)
    )
    concepts = concepts_result.scalars().all()
    concept_ids = [c.id for c in concepts]

    lessons_result = await db.execute(
        select(Lesson)
        .join(Concept)
        .where(Lesson.concept_id.in_(concept_ids))
        .order_by(Concept.order, Lesson.position)
    )
    lessons = lessons_result.scalars().all()
    if not lessons:
        return {"course_id": str(course_id), "lesson_id": None}

    completed_result = await db.execute(
        select(LessonProgress.lesson_id).where(
            LessonProgress.user_id == current_user.id,
            LessonProgress.is_completed.is_(True),
            LessonProgress.lesson_id.in_([l.id for l in lessons]),
        )
    )
    completed_ids = {row[0] for row in completed_result.all()}

    for lesson in lessons:
        if lesson.id not in completed_ids:
            return {"course_id": str(course_id), "lesson_id": str(lesson.id)}

    return {"course_id": str(course_id), "lesson_id": str(lessons[-1].id)}


@router.post("/", response_model=CourseRead, status_code=status.HTTP_201_CREATED)
async def create_course(
    course: CourseCreate,
    current_user: User = Depends(require_content_creator),
    db: AsyncSession = Depends(get_db),
) -> Course:
    existing = await db.execute(select(Course).where(Course.slug == course.slug))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Slug already exists")
    db_course = Course(**course.model_dump(exclude={"id", "created_at"}))
    db.add(db_course)
    await db.commit()
    await db.refresh(db_course)
    return db_course


@router.patch("/{course_id}", response_model=CourseRead)
async def update_course(
    course_id: UUID,
    course_update: CourseUpdate,
    current_user: User = Depends(require_content_creator),
    db: AsyncSession = Depends(get_db),
) -> Course:
    result = await db.execute(select(Course).where(Course.id == course_id))
    course = result.scalar_one_or_none()
    if course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    update_data = course_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(course, field, value)

    await db.commit()
    await db.refresh(course)
    return course


@router.get("/{course_id}/concepts", response_model=PaginatedResponse)
async def list_course_concepts(
    course_id: UUID,
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse:
    total_result = await db.execute(
        select(Concept).where(Concept.course_id == course_id).order_by(Concept.order, Concept.created_at)
    )
    total = len(total_result.scalars().all())

    result = await db.execute(
        select(Concept)
        .where(Concept.course_id == course_id)
        .order_by(Concept.order, Concept.created_at)
        .offset((pagination.page - 1) * pagination.per_page)
        .limit(pagination.per_page)
    )
    concepts = result.scalars().all()

    return PaginatedResponse(
        items=[ConceptRead.model_validate(c).model_dump() for c in concepts],
        total=total,
        page=pagination.page,
        per_page=pagination.per_page,
        pages=(total + pagination.per_page - 1) // pagination.per_page,
    )


@router.get("/{course_id}/concepts/{concept_slug}", response_model=ConceptRead)
async def get_concept(course_id: UUID, concept_slug: str, db: AsyncSession = Depends(get_db)) -> Concept:
    result = await db.execute(select(Concept).where(Concept.course_id == course_id, Concept.slug == concept_slug))
    concept = result.scalar_one_or_none()
    if concept is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Concept not found")
    return concept
