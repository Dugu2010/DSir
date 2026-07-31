from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models import (
    Course, Module, Lesson, Category, TechnologyStack,
    CourseTechnology, ContentStatus, DifficultyLevel,
    Enrollment, Exercise,
)
from app.schemas import (
    CourseCreate, CourseUpdate, CourseResponse, CourseListItem,
    ModuleCreate, ModuleUpdate, ModuleResponse,
    PaginatedResponse, PaginationParams,
)
from app.utils.deps import get_current_active_user, require_teacher, get_optional_user
from app.models import User
from uuid import UUID
from datetime import datetime, timezone

router = APIRouter(prefix="/courses", tags=["Courses"])


# ── Courses CRUD ────────────────────────────────────────────────

@router.get("/", response_model=PaginatedResponse)
async def list_courses(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    difficulty: str = Query(default=None),
    category: str = Query(default=None),
    technology: str = Query(default=None),
    search: str = Query(default=""),
    sort: str = Query(default="newest"),
    current_user: User = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Course).where(Course.status == ContentStatus.PUBLISHED, Course.deleted_at.is_(None))

    if difficulty:
        try:
            query = query.where(Course.difficulty == DifficultyLevel(difficulty))
        except ValueError:
            pass

    if category:
        query = query.join(CourseTechnology).join(TechnologyStack).join(Category).where(Category.slug == category)

    if technology:
        query = query.join(CourseTechnology).join(TechnologyStack).where(TechnologyStack.slug == technology)

    if search:
        query = query.where(Course.title.ilike(f"%{search}%") | Course.description.ilike(f"%{search}%"))

    # Count
    count_query = select(func.count(Course.id)).where(
        Course.status == ContentStatus.PUBLISHED, Course.deleted_at.is_(None)
    )
    if difficulty:
        try:
            count_query = count_query.where(Course.difficulty == DifficultyLevel(difficulty))
        except ValueError:
            pass

    total = (await db.execute(count_query)).scalar()

    # Sort
    if sort == "popular":
        query = query.order_by(Course.enrollment_count.desc())
    elif sort == "rating":
        query = query.order_by(Course.rating_average.desc())
    else:
        query = query.order_by(Course.published_at.desc())

    result = await db.execute(query.offset((page - 1) * size).limit(size))

    return PaginatedResponse(
        items=[CourseListItem.model_validate(c) for c in result.scalars().all()],
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size,
    )


@router.get("/featured", response_model=list[CourseListItem])
async def get_featured_courses(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Course)
        .where(Course.is_featured == True, Course.status == ContentStatus.PUBLISHED, Course.deleted_at.is_(None))
        .order_by(Course.display_order)
        .limit(10)
    )
    return [CourseListItem.model_validate(c) for c in result.scalars().all()]


@router.get("/{course_slug}", response_model=CourseResponse)
async def get_course(
    course_slug: str,
    current_user: User = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Course).where(Course.slug == course_slug, Course.deleted_at.is_(None))
    )
    course = result.scalar_one_or_none()
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    if course.status != ContentStatus.PUBLISHED:
        if not current_user or current_user.role.value not in ("teacher", "admin", "superadmin"):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    return course


@router.post("/", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
async def create_course(
    data: CourseCreate,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db),
):
    existing = await db.execute(select(Course).where(Course.slug == data.slug))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Course slug already exists")

    course = Course(
        **data.model_dump(exclude={"category_ids", "technology_ids"}),
        author_id=current_user.id,
    )
    db.add(course)
    await db.flush()

    if data.technology_ids:
        for tech_id in data.technology_ids:
            ct = CourseTechnology(course_id=course.id, technology_id=tech_id)
            db.add(ct)

    return course


@router.patch("/{course_slug}", response_model=CourseResponse)
async def update_course(
    course_slug: str,
    data: CourseUpdate,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Course).where(Course.slug == course_slug))
    course = result.scalar_one_or_none()
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if hasattr(course, key):
            setattr(course, key, value)

    course.updated_at = datetime.now(timezone.utc)
    if update_data.get("status") == "published" and not course.published_at:
        course.published_at = datetime.now(timezone.utc)

    return course


@router.delete("/{course_slug}")
async def delete_course(
    course_slug: str,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Course).where(Course.slug == course_slug))
    course = result.scalar_one_or_none()
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    course.deleted_at = datetime.now(timezone.utc)
    return {"detail": "Course deleted"}


# ── Modules ─────────────────────────────────────────────────────

@router.get("/{course_slug}/modules", response_model=list[ModuleResponse])
async def list_modules(
    course_slug: str,
    current_user: User = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Course).where(Course.slug == course_slug))
    course = result.scalar_one_or_none()
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    modules_result = await db.execute(
        select(Module)
        .where(Module.course_id == course.id)
        .order_by(Module.display_order)
    )
    return modules_result.scalars().all()


@router.post("/{course_slug}/modules", response_model=ModuleResponse, status_code=status.HTTP_201_CREATED)
async def create_module(
    course_slug: str,
    data: ModuleCreate,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Course).where(Course.slug == course_slug))
    course = result.scalar_one_or_none()
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    module = Module(course_id=course.id, **data.model_dump())
    db.add(module)
    course.module_count = (course.module_count or 0) + 1
    await db.flush()
    return module


@router.patch("/{course_slug}/modules/{module_slug}", response_model=ModuleResponse)
async def update_module(
    course_slug: str,
    module_slug: str,
    data: ModuleUpdate,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Module).join(Course).where(Course.slug == course_slug, Module.slug == module_slug)
    )
    module = result.scalar_one_or_none()
    if not module:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Module not found")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if hasattr(module, key):
            setattr(module, key, value)

    return module


# ── Lessons ─────────────────────────────────────────────────────

@router.get("/{course_slug}/lessons", response_model=list[dict])
async def get_course_lessons(
    course_slug: str,
    current_user: User = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Course).where(Course.slug == course_slug))
    course = result.scalar_one_or_none()
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    modules_result = await db.execute(
        select(Module)
        .where(Module.course_id == course.id)
        .order_by(Module.display_order)
    )
    modules = modules_result.scalars().all()

    course_structure = []
    for module in modules:
        lessons_result = await db.execute(
            select(Lesson)
            .where(Lesson.module_id == module.id, Lesson.status == ContentStatus.PUBLISHED)
            .order_by(Lesson.display_order)
        )
        lessons = []
        for lesson in lessons_result.scalars().all():
            lesson_data = {
                "id": str(lesson.id),
                "title": lesson.title,
                "slug": lesson.slug,
                "description": lesson.description,
                "difficulty": lesson.difficulty.value if lesson.difficulty else "beginner",
                "estimated_duration_minutes": lesson.estimated_duration_minutes,
                "display_order": lesson.display_order,
                "is_free_preview": lesson.is_free_preview,
                "skill_tags": lesson.skill_tags,
            }
            lessons.append(lesson_data)

        course_structure.append({
            "id": str(module.id),
            "title": module.title,
            "slug": module.slug,
            "description": module.description,
            "display_order": module.display_order,
            "lessons": lessons,
        })

    return course_structure
