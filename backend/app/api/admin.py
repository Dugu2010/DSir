from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text
from app.database import get_db
from app.models import (
    User, Course, Module, Lesson, Exercise, Enrollment,
    LessonProgress, Submission, ContentStatus,
    UserStats, FeatureFlag, AuditLog, ExerciseType,
    ExerciseDifficulty, DifficultyLevel,
)
from app.schemas import (
    AdminDashboardStats, PaginatedResponse,
    CourseCreate, CourseUpdate, CourseResponse,
    UserResponse, FeatureFlag as FeatureFlagSchema,
    AICourseGenerateRequest, AICourseGenerateResponse,
    AICourseImportRequest, AICourseImportResponse,
)
from app.utils.deps import require_admin, require_superadmin
from app.services.ai_content import extract_text_from_bytes, generate_course_structure
from app.models import User as UserModel
from uuid import UUID, uuid4
from datetime import datetime, timezone, timedelta, date
import structlog

logger = structlog.get_logger()

router = APIRouter(prefix="/admin", tags=["Admin"])


# ── Dashboard Stats ─────────────────────────────────────────────

@router.get("/dashboard", response_model=AdminDashboardStats)
async def admin_dashboard(
    admin_user: UserModel = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    now = datetime.now(timezone.utc)
    week_ago = now - timedelta(days=7)
    today = date.today()

    total_users = (await db.execute(select(func.count(UserModel.id)).where(UserModel.deleted_at.is_(None)))).scalar() or 0
    total_courses = (await db.execute(
        select(func.count(Course.id)).where(Course.deleted_at.is_(None), Course.status == ContentStatus.PUBLISHED)
    )).scalar() or 0
    total_enrollments = (await db.execute(select(func.count(Enrollment.id)))).scalar() or 0
    total_completions = (await db.execute(
        select(func.count(Enrollment.id)).where(Enrollment.is_completed == True)
    )).scalar() or 0

    active_today = (await db.execute(
        select(func.count(UserModel.id)).where(
            UserModel.last_active_at >= now - timedelta(hours=24),
            UserModel.deleted_at.is_(None),
        )
    )).scalar() or 0

    new_users_week = (await db.execute(
        select(func.count(UserModel.id)).where(
            UserModel.created_at >= week_ago,
            UserModel.deleted_at.is_(None),
        )
    )).scalar() or 0

    return AdminDashboardStats(
        total_users=total_users,
        total_courses=total_courses,
        total_enrollments=total_enrollments,
        total_completions=total_completions,
        active_today=active_today,
        new_users_week=new_users_week,
    )


# ── User Management ─────────────────────────────────────────────

@router.get("/users", response_model=PaginatedResponse)
async def admin_list_users(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    search: str = Query(default=""),
    admin_user: UserModel = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    query = select(UserModel).where(UserModel.deleted_at.is_(None))
    if search:
        query = query.where(
            UserModel.email.ilike(f"%{search}%") |
            UserModel.username.ilike(f"%{search}%") |
            UserModel.display_name.ilike(f"%{search}%")
        )

    count_query = select(func.count(UserModel.id)).where(UserModel.deleted_at.is_(None))

    total = (await db.execute(count_query)).scalar()
    result = await db.execute(
        query.order_by(UserModel.created_at.desc()).offset((page - 1) * size).limit(size)
    )

    return PaginatedResponse(
        items=[UserResponse.model_validate(u) for u in result.scalars().all()],
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size,
    )


@router.patch("/users/{user_id}/role")
async def update_user_role(
    user_id: UUID,
    role: str = Query(...),
    admin_user: UserModel = Depends(require_superadmin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(UserModel).where(UserModel.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    from app.models import UserRole
    try:
        user.role = UserRole(role)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid role")

    return {"detail": f"User role updated to {role}"}


@router.delete("/users/{user_id}")
async def admin_delete_user(
    user_id: UUID,
    admin_user: UserModel = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(UserModel).where(UserModel.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user.deleted_at = datetime.now(timezone.utc)
    return {"detail": "User deleted"}


# ── Course Management (Admin) ───────────────────────────────────

@router.get("/courses", response_model=PaginatedResponse)
async def admin_list_courses(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    status: str = Query(default=None),
    admin_user: UserModel = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    query = select(Course).where(Course.deleted_at.is_(None))
    if status:
        try:
            query = query.where(Course.status == ContentStatus(status))
        except ValueError:
            pass

    count_query = select(func.count(Course.id)).where(Course.deleted_at.is_(None))

    total = (await db.execute(count_query)).scalar()
    result = await db.execute(
        query.order_by(Course.updated_at.desc()).offset((page - 1) * size).limit(size)
    )

    return PaginatedResponse(
        items=[CourseResponse.model_validate(c) for c in result.scalars().all()],
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size,
    )


# ── Feature Flags ───────────────────────────────────────────────

@router.get("/feature-flags")
async def list_feature_flags(
    admin_user: UserModel = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(FeatureFlag))
    flags = result.scalars().all()
    return [{"name": f.name, "is_enabled": f.is_enabled, "description": f.description} for f in flags]


@router.patch("/feature-flags/{flag_name}")
async def toggle_feature_flag(
    flag_name: str,
    is_enabled: bool = Query(...),
    admin_user: UserModel = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(FeatureFlag).where(FeatureFlag.name == flag_name))
    flag = result.scalar_one_or_none()
    if not flag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feature flag not found")
    flag.is_enabled = is_enabled
    return {"name": flag.name, "is_enabled": flag.is_enabled}


# ── Analytics ───────────────────────────────────────────────────

@router.get("/analytics/overview")
async def analytics_overview(
    admin_user: UserModel = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    now = datetime.now(timezone.utc)

    # Daily signups (last 30 days)
    signups = []
    for i in range(30):
        day = now - timedelta(days=i)
        day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        count = (await db.execute(
            select(func.count(UserModel.id)).where(
                UserModel.created_at >= day_start,
                UserModel.created_at < day_end,
            )
        )).scalar() or 0
        signups.append({"date": day_start.date().isoformat(), "count": count})

    # Course popularity
    course_stats = await db.execute(
        select(Course.title, Course.enrollment_count)
        .where(Course.status == ContentStatus.PUBLISHED, Course.deleted_at.is_(None))
        .order_by(Course.enrollment_count.desc())
        .limit(10)
    )
    popular_courses = [{"title": row[0], "enrollments": row[1]} for row in course_stats.all()]

    return {
        "daily_signups": list(reversed(signups)),
        "popular_courses": popular_courses,
    }


# ── AI Content Generation ───────────────────────────────────────

@router.post("/ai/extract", response_model=dict)
async def ai_extract_content(
    file: UploadFile = File(...),
    topic: str = Query(default=""),
    admin_user: UserModel = Depends(require_admin),
):
    """Upload a file (PDF/image/text) and extract structured course content with AI."""
    try:
        data = await file.read()
        # Extract raw text from file
        raw_text = extract_text_from_bytes(data, file.filename or "")
        if not raw_text.strip():
            raise HTTPException(status_code=400, detail="Could not extract text from file")
        logger.info("ai_extract.text_extracted", filename=file.filename, text_len=len(raw_text))

        # Generate course structure with AI
        result = generate_course_structure(raw_text, topic)
        logger.info("ai_extract.structure_generated", course_title=result.get("course", {}).get("title"))

        return {
            "success": True,
            "filename": file.filename,
            "extracted_length": len(raw_text),
            "extracted_preview": raw_text[:2000],
            "course_data": result,
            "preview": _format_preview(result),
        }
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error("ai_extract.error", error=str(e), filename=file.filename)
        raise HTTPException(status_code=500, detail=f"AI processing failed: {str(e)}")


@router.post("/ai/import", response_model=AICourseImportResponse)
async def ai_import_course(
    data: AICourseImportRequest,
    admin_user: UserModel = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Import AI-generated course data into the database."""
    course_data = data.course_data
    c = course_data.get("course", {})
    modules_data = course_data.get("modules", [])

    # Check slug uniqueness
    slug = c.get("slug", "")
    existing = await db.execute(select(Course).where(Course.slug == slug))
    if existing.scalar_one_or_none():
        slug = f"{slug}-{uuid4().hex[:6]}"

    # Create course
    course = Course(
        id=uuid4(),
        title=c.get("title", "Untitled Course"),
        slug=slug,
        description=c.get("description", ""),
        long_description=c.get("long_description", ""),
        difficulty=DifficultyLevel(c.get("difficulty", "beginner")),
        estimated_duration_minutes=c.get("estimated_duration_minutes", 1200),
        learning_objectives=c.get("learning_objectives", []),
        skill_tags=c.get("skill_tags", []),
        status=ContentStatus.DRAFT,
        is_featured=False,
        is_free=True,
        author_id=admin_user.id,
        enrollment_count=0,
        rating_average=0.0,
        rating_count=0,
        module_count=len(modules_data),
        lesson_count=sum(len(m.get("lessons", [])) for m in modules_data),
    )
    db.add(course)
    await db.flush()

    total_lessons = 0
    total_exercises = 0

    for mi, mod in enumerate(modules_data):
        module = Module(
            id=uuid4(),
            course_id=course.id,
            title=mod.get("title", f"Module {mi+1}"),
            slug=mod.get("slug", f"module-{mi+1}"),
            description=mod.get("description", ""),
            display_order=mi + 1,
            lesson_count=len(mod.get("lessons", [])),
        )
        db.add(module)
        await db.flush()

        for li, les in enumerate(mod.get("lessons", [])):
            lesson = Lesson(
                id=uuid4(),
                module_id=module.id,
                title=les.get("title", f"Lesson {li+1}"),
                slug=les.get("slug", f"lesson-{li+1}"),
                description=les.get("description", ""),
                content=les.get("content_markdown", ""),
                content_markdown=les.get("content_markdown", ""),
                learning_objectives=les.get("learning_objectives", []),
                difficulty=DifficultyLevel(les.get("difficulty", "beginner")),
                estimated_duration_minutes=les.get("estimated_duration_minutes", 45),
                display_order=li + 1,
                skill_tags=les.get("skill_tags", []),
                status=ContentStatus.DRAFT,
            )
            db.add(lesson)
            await db.flush()
            total_lessons += 1

            for ei, ex in enumerate(les.get("exercises", [])):
                try:
                    ex_type = ExerciseType(ex.get("exercise_type", "code_completion"))
                except ValueError:
                    ex_type = ExerciseType.CODE_COMPLETION
                try:
                    ex_diff = ExerciseDifficulty(ex.get("difficulty", "easy"))
                except ValueError:
                    ex_diff = ExerciseDifficulty.EASY

                exercise = Exercise(
                    id=uuid4(),
                    lesson_id=lesson.id,
                    title=ex.get("title", f"Exercise {ei+1}"),
                    description=ex.get("description", ""),
                    instructions=ex.get("instructions", ""),
                    exercise_type=ex_type,
                    difficulty=ex_diff,
                    starter_code=ex.get("starter_code", ""),
                    solution_code=ex.get("solution_code", ""),
                    test_code=ex.get("test_code", ""),
                    hints=ex.get("hints", []),
                    skill_tags=les.get("skill_tags", []),
                    points=ex.get("points", 15),
                    display_order=ei + 1,
                )
                db.add(exercise)
                total_exercises += 1

    await db.flush()
    await db.commit()

    logger.info("ai_import.success", course_slug=slug, modules=len(modules_data),
                lessons=total_lessons, exercises=total_exercises)

    return AICourseImportResponse(
        course_id=course.id,
        course_slug=slug,
        module_count=len(modules_data),
        lesson_count=total_lessons,
        exercise_count=total_exercises,
    )


def _format_preview(data: dict) -> str:
    """Format course data into a human-readable preview."""
    c = data.get("course", {})
    mods = data.get("modules", [])
    lines = [f"## {c.get('title', 'Course')}\n",
             f"**Difficulty:** {c.get('difficulty', 'N/A')} | **Duration:** {c.get('estimated_duration_minutes', 'N/A')} min\n",
             f"**Tags:** {', '.join(c.get('skill_tags', []))}\n",
             f"\n{c.get('description', '')}\n",
             "\n---\n"]
    for mi, m in enumerate(mods):
        lines.append(f"\n### Module {mi+1}: {m.get('title', 'Module')}")
        for li, l in enumerate(m.get("lessons", [])):
            lines.append(f"  - Lesson {li+1}: {l.get('title', 'Lesson')} ({l.get('difficulty', 'N/A')}) "
                        f"[{len(l.get('exercises', []))} exercises]")
    return "\n".join(lines)

