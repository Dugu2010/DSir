from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models import (
    Course, Module, Lesson, Category, TechnologyStack,
    CourseTechnology, ContentStatus, DifficultyLevel,
    Enrollment, Exercise, CourseReview,
)
from app.schemas import (
    CourseCreate, CourseUpdate, CourseResponse, CourseListItem,
    ModuleCreate, ModuleUpdate, ModuleResponse,
    PaginatedResponse, PaginationParams,
    CourseReviewCreate, CourseReviewResponse,
)
from app.utils.deps import get_current_active_user, require_teacher, get_optional_user
from app.utils.redis import get_cache, set_cache, delete_cache, clear_cache_pattern
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
    cache_key = f"courses:list:{page}:{size}:{difficulty or ''}:{category or ''}:{technology or ''}:{search or ''}:{sort or ''}"
    cached_response = await get_cache(cache_key)
    if cached_response is not None:
        return cached_response

    # Public catalog endpoints must never expose drafts or archived content.
    query = select(Course).where(
        Course.deleted_at.is_(None),
        Course.status == ContentStatus.PUBLISHED,
    )

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

    count_query = select(func.count(Course.id)).where(
        Course.deleted_at.is_(None),
        Course.status == ContentStatus.PUBLISHED,
    )
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

    if sort == "newest":
        query = query.order_by(Course.created_at.desc())
    elif sort == "popular":
        query = query.order_by(Course.enrollment_count.desc())
    elif sort == "rating":
        query = query.order_by(Course.rating_average.desc().nulls_last())

    result = await db.execute(query.offset((page - 1) * size).limit(size))
    courses = result.scalars().all()

    response = PaginatedResponse(
        items=[CourseListItem.model_validate(c) for c in courses],
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size if total > 0 else 0,
    )
    await set_cache(cache_key, response, expire=60)
    return response


@router.get("/featured", response_model=list[CourseResponse])
async def list_featured_courses(db: AsyncSession = Depends(get_db)):
    cache_key = "courses:featured"
    cached_response = await get_cache(cache_key)
    if cached_response is not None:
        return cached_response

    result = await db.execute(
        select(Course).where(
            Course.is_featured.is_(True),
            Course.status == ContentStatus.PUBLISHED,
            Course.deleted_at.is_(None),
        )
    )
    response = result.scalars().all()
    await set_cache(cache_key, response, expire=300)
    return response


@router.get("/{course_slug}", response_model=CourseResponse)
async def get_course_detail(course_slug: str, db: AsyncSession = Depends(get_db)):
    cache_key = f"course:detail:{course_slug}"
    cached_course = await get_cache(cache_key)
    if cached_course is not None:
        return cached_course

    result = await db.execute(
        select(Course).where(
            Course.slug == course_slug,
            Course.status == ContentStatus.PUBLISHED,
            Course.deleted_at.is_(None),
        )
    )
    course = result.scalar_one_or_none()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    await set_cache(cache_key, course, expire=300)
    return course


@router.post("/", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
async def create_course(
    data: CourseCreate,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db),
):
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
    await clear_cache_pattern("courses:list:*")
    await delete_cache("courses:featured")
    await delete_cache(f"course:detail:{course.slug}")
    return course


@router.patch("/{course_id}", response_model=CourseResponse)
async def update_course(
    course_id: UUID,
    data: CourseUpdate,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Course).where(Course.id == course_id, Course.deleted_at.is_(None)))
    course = result.scalar_one_or_none()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

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
    await clear_cache_pattern("courses:list:*")
    await delete_cache("courses:featured")
    await delete_cache(f"course:detail:{course.slug}")
    await clear_cache_pattern(f"course:modules:{course.id}:*")
    return course


# ── Modules CRUD ────────────────────────────────────────────────

@router.get("/{course_slug}/modules", response_model=list[ModuleResponse])
async def list_course_modules(course_slug: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Course).where(
            Course.slug == course_slug,
            Course.status == ContentStatus.PUBLISHED,
            Course.deleted_at.is_(None),
        )
    )
    course = result.scalar_one_or_none()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    modules_result = await db.execute(
        select(Module)
        .where(Module.course_id == course.id, Module.deleted_at.is_(None))
        .order_by(Module.display_order.asc())
    )
    modules = modules_result.scalars().all()

    from app.schemas import LessonListItem
    module_ids = [m.id for m in modules]
    lessons_by_module: dict = {}
    if module_ids:
        lessons_result = await db.execute(
            select(Lesson)
            .where(
                Lesson.module_id.in_(module_ids),
                Lesson.status == ContentStatus.PUBLISHED,
                Lesson.deleted_at.is_(None),
            )
            .order_by(Lesson.module_id.asc(), Lesson.display_order.asc())
        )
        for lesson in lessons_result.scalars().all():
            mid = str(lesson.module_id)
            lessons_by_module.setdefault(mid, []).append(LessonListItem.model_validate(lesson).model_dump())

    from sqlalchemy.orm import class_mapper
    result_list = []
    mapper = class_mapper(Module)
    cols = [c.key for c in mapper.columns]
    for module in modules:
        md = {col: getattr(module, col) for col in cols}
        md["lessons"] = lessons_by_module.get(str(md["id"]), [])
        result_list.append(md)
    return result_list


@router.post("/{course_slug}/modules", response_model=ModuleResponse, status_code=status.HTTP_201_CREATED)
async def create_module(
    course_slug: str,
    data: ModuleCreate,
    current_user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Course).where(Course.slug == course_slug, Course.deleted_at.is_(None)))
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
    await clear_cache_pattern(f"course:modules:{course.id}:*")
    return module


# ── Course Reviews ──────────────────────────────────────────────

@router.get("/{course_slug}/reviews", response_model=PaginatedResponse)
async def list_course_reviews(
    course_slug: str,
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Course).where(Course.slug == course_slug, Course.status == ContentStatus.PUBLISHED, Course.deleted_at.is_(None)))
    course = result.scalar_one_or_none()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    count = (await db.execute(select(func.count(CourseReview.id)).where(CourseReview.course_id == course.id))).scalar() or 0
    rows = await db.execute(
        select(CourseReview, User.display_name)
        .join(User, User.id == CourseReview.user_id)
        .where(CourseReview.course_id == course.id)
        .order_by(CourseReview.created_at.desc())
        .offset((page - 1) * size)
        .limit(size)
    )
    items = [
        CourseReviewResponse(
            id=r.id, user_id=r.user_id, display_name=display_name,
            rating=r.rating, review=r.review, created_at=r.created_at,
        ).model_dump()
        for r, display_name in rows.all()
    ]
    return PaginatedResponse(
        items=items, total=count, page=page, size=size,
        pages=(count + size - 1) // size if count > 0 else 0,
    )


@router.post("/{course_slug}/reviews", response_model=CourseReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review(
    course_slug: str,
    data: CourseReviewCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Course).where(Course.slug == course_slug, Course.status == ContentStatus.PUBLISHED, Course.deleted_at.is_(None)))
    course = result.scalar_one_or_none()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    enrolled = (await db.execute(
        select(Enrollment).where(Enrollment.user_id == current_user.id, Enrollment.course_id == course.id)
    )).scalar_one_or_none()
    if not enrolled:
        raise HTTPException(status_code=403, detail="Enroll before reviewing this course")

    existing = (await db.execute(
        select(CourseReview).where(CourseReview.user_id == current_user.id, CourseReview.course_id == course.id)
    )).scalar_one_or_none()
    if existing:
        existing.rating = data.rating
        existing.review = data.review
        existing.updated_at = datetime.now(timezone.utc)
        review = existing
    else:
        review = CourseReview(user_id=current_user.id, course_id=course.id, rating=data.rating, review=data.review)
        db.add(review)

    await db.flush()
    agg = (await db.execute(
        select(func.avg(CourseReview.rating), func.count(CourseReview.id)).where(CourseReview.course_id == course.id)
    )).one()
    course.rating_average = round(float(agg[0] or 0), 2)
    course.rating_count = int(agg[1] or 0)

    await delete_cache(f"course:detail:{course.slug}")
    await clear_cache_pattern("courses:list:*")

    return CourseReviewResponse(
        id=review.id, user_id=review.user_id,
        display_name=current_user.display_name,
        rating=review.rating, review=review.review,
        created_at=review.created_at or datetime.now(timezone.utc),
    )
