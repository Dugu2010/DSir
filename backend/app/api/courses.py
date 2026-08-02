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
    # Allow draft courses to be listed (removed ContentStatus.PUBLISHED check)
    query = select(Course).where(Course.deleted_at.is_(None))

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
    count_query = select(func.count(Course.id)).where(Course.deleted_at.is_(None))
    if difficulty:
        try:
            count_query = count_query.where(Course.difficulty == DifficultyLevel(difficulty))
        except ValueError:
            pass
    if category:
        count_query = count_query.join(CourseTechnology).join(TechnologyStack).join(Category).where(Category.slug == category)
    if technology:
        count_query = count_query.join(CourseTechnology).join(TechnologyStack).where(TechnologyStack.slug == technology)
    if search:
        count_query = count_query.where(Course.title.ilike(f"%{search}%") | Course.description.ilike(f"%{search}%"))

    total = (await db.execute(count_query)).scalar() or 0

    # Sorting
    if sort == "newest":
        query = query.order_by(Course.created_at.desc())
    elif sort == "popular":
        query = query.order_by(Course.enrollment_count.desc())
    elif sort == "rating":
        query = query.order_by(Course.rating_average.desc().nulls_last())

    result = await db.execute(query.offset((page - 1) * size).limit(size))
    courses = result.scalars().all()

    return PaginatedResponse(
        items=[CourseListItem.model_validate(c) for c in courses],
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size if total > 0 else 0,
    )


@router.get("/featured", response_model=list[CourseResponse])
async def list_featured_courses(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Course)
        .where(Course.is_featured == True, Course.deleted_at.is_(None))
    )
    return result.scalars().all()


@router.get("/{course_slug}", response_model=CourseResponse)
async def get_course_detail(course_slug: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Course).where(Course.slug == course_slug, Course.deleted_at.is_(None))
    )
    course = result.scalar_one_or_none()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course


@router.post("/", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
async def create_course(
    data: CourseCreate,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db),
):
    # Check unique slug
    existing = await db.execute(select(Course).where(Course.slug == data.slug))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Slug already exists")

    course = Course(
        title=data.title,
        slug=data.slug,
        description=data.description,
        long_description=data.long_description,
        difficulty=DifficultyLevel(data.difficulty),
        estimated_duration_minutes=data.estimated_duration_minutes,
        learning_objectives=data.learning_objectives,
        skill_tags=data.skill_tags,
        is_free=data.is_free,
        is_featured=data.is_featured,
        status=ContentStatus(data.status or "draft"),
        author_id=current_user.id,
    )
    db.add(course)
    await db.flush()
    await db.commit()
    return course


@router.patch("/{course_id}", response_model=CourseResponse)
async def update_course(
    course_id: UUID,
    data: CourseUpdate,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Course).where(Course.id == course_id, Course.deleted_at.is_(None))
    )
    course = result.scalar_one_or_none()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Authorize - only owner or admin can edit
    if course.author_id != current_user.id and current_user.role not in ("admin", "superadmin"):
        raise HTTPException(status_code=403, detail="Not authorized")

    for field, value in data.model_dump(exclude_unset=True).items():
        if field == "difficulty":
            setattr(course, field, DifficultyLevel(value))
        elif field == "status":
            setattr(course, field, ContentStatus(value))
        else:
            setattr(course, field, value)

    course.updated_at = datetime.now(timezone.utc)
    await db.flush()
    await db.commit()
    return course


# ── Modules CRUD ────────────────────────────────────────────────

@router.get("/{course_slug}/modules", response_model=list[ModuleResponse])
async def list_course_modules(course_slug: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Course).where(Course.slug == course_slug, Course.deleted_at.is_(None))
    )
    course = result.scalar_one_or_none()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    modules_result = await db.execute(
        select(Module)
        .where(Module.course_id == course.id, Module.deleted_at.is_(None))
        .order_by(Module.display_order.asc())
    )
    return modules_result.scalars().all()


@router.post("/{course_slug}/modules", response_model=ModuleResponse, status_code=status.HTTP_201_CREATED)
async def create_module(
    course_slug: str,
    data: ModuleCreate,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Course).where(Course.slug == course_slug, Course.deleted_at.is_(None))
    )
    course = result.scalar_one_or_none()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    if course.author_id != current_user.id and current_user.role not in ("admin", "superadmin"):
        raise HTTPException(status_code=403, detail="Not authorized")

    module = Module(
        course_id=course.id,
        title=data.title,
        slug=data.slug,
        description=data.description,
        display_order=data.display_order,
    )
    db.add(module)
    await db.flush()
    await db.commit()
    return module
