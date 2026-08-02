from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Body
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
    AICourseImportRequest, AICourseImportResponse,
)
from app.utils.deps import require_admin, require_superadmin
from app.models import User as UserModel
from uuid import UUID, uuid4
from datetime import datetime, timezone, timedelta, date
import structlog

logger = structlog.get_logger()

router = APIRouter(prefix="/admin", tags=["Admin"])


# -- Dashboard Stats --

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


# -- User Management --

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
        total=total, page=page, size=size, pages=(total + size - 1) // size,
    )


@router.patch("/users/{user_id}/role")
async def update_user_role(
    user_id: UUID, role: str = Query(...),
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


# -- Course Management (Admin) --

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
        total=total, page=page, size=size, pages=(total + size - 1) // size,
    )


# -- Feature Flags --

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
    flag_name: str, is_enabled: bool = Query(...),
    admin_user: UserModel = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(FeatureFlag).where(FeatureFlag.name == flag_name))
    flag = result.scalar_one_or_none()
    if not flag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feature flag not found")
    flag.is_enabled = is_enabled
    return {"name": flag.name, "is_enabled": flag.is_enabled}


# -- Analytics --

@router.get("/analytics/overview")
async def analytics_overview(
    admin_user: UserModel = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    now = datetime.now(timezone.utc)
    signups = []
    for i in range(30):
        day = now - timedelta(days=i)
        day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        count = (await db.execute(
            select(func.count(UserModel.id)).where(
                UserModel.created_at >= day_start, UserModel.created_at < day_end,
            )
        )).scalar() or 0
        signups.append({"date": day_start.date().isoformat(), "count": count})
    course_stats = await db.execute(
        select(Course.title, Course.enrollment_count)
        .where(Course.status == ContentStatus.PUBLISHED, Course.deleted_at.is_(None))
        .order_by(Course.enrollment_count.desc()).limit(10)
    )
    popular_courses = [{"title": row[0], "enrollments": row[1]} for row in course_stats.all()]
    return {"daily_signups": list(reversed(signups)), "popular_courses": popular_courses}


# ================================================================
# AI CONTENT GENERATION
# Flow: Upload -> Extract -> Preview -> [Admin Approves] -> Import
# ================================================================

@router.post("/ai/preview")
async def ai_preview(
    file: UploadFile = File(...),
    topic: str = Query(default=""),
    admin_user: UserModel = Depends(require_admin),
):
    """Step 1: Upload file -> extract text -> AI generates course structure preview.
    Returns structure with module/lesson titles for admin review."""
    from app.services.ai_content import extract_text, generate_structure_preview

    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Empty file")

    logger.info("ai.preview.start", file=file.filename, size=len(data))

    raw_text = extract_text(data, file.filename or "")
    if not raw_text or len(raw_text.strip()) < 50:
        raise HTTPException(
            status_code=400,
            detail=f"Could not extract enough text from this file. Extracted {len(raw_text)} characters. Try a text-based PDF or image."
        )
    logger.info("ai.preview.extracted", text_len=len(raw_text))

    structure = generate_structure_preview(raw_text, topic)

    mod_count = len(structure.get("modules", []))
    les_count = sum(len(m.get("lessons", [])) for m in structure.get("modules", []))

    return {
        "success": True,
        "text_length": len(raw_text),
        "text_preview": raw_text[:1500],
        "structure": structure,
        "summary": {
            "title": structure.get("course", {}).get("title", ""),
            "modules": mod_count,
            "lessons": les_count,
            "difficulty": structure.get("course", {}).get("difficulty", ""),
            "description": structure.get("course", {}).get("description", ""),
            "skill_tags": structure.get("course", {}).get("skill_tags", []),
        },
        "modules_preview": [
            {
                "title": m.get("title", ""),
                "lessons": [l.get("title", "") for l in m.get("lessons", [])]
            }
            for m in structure.get("modules", [])
        ],
    }


@router.post("/ai/import", response_model=AICourseImportResponse)
async def ai_import_course(
    structure: dict = Body(...),
    admin_user: UserModel = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Step 2: Admin approved the structure -> generate lesson content via AI -> import into DB."""
    from app.services.ai_content import generate_lesson_content

    c = structure.get("course", {})
    modules_data = structure.get("modules", [])

    if not c or not modules_data:
        raise HTTPException(status_code=400, detail="Missing course or modules in structure")

    slug = c.get("slug", "ai-course")
    existing = await db.execute(select(Course).where(Course.slug == slug))
    if existing.scalar_one_or_none():
        slug = f"{slug}-{uuid4().hex[:6]}"

    now = datetime.now(timezone.utc)
    course = Course(
        id=uuid4(), title=c.get("title", "Course"), slug=slug,
        description=c.get("description", ""), long_description=c.get("long_description", ""),
        difficulty=DifficultyLevel(c.get("difficulty", "beginner")),
        estimated_duration_minutes=c.get("estimated_duration_minutes", 600),
        learning_objectives=c.get("learning_objectives", []),
        skill_tags=c.get("skill_tags", []),
        status=ContentStatus.PUBLISHED, published_at=now, is_featured=False, is_free=True,
        author_id=admin_user.id,
        enrollment_count=0, rating_average=0.0, rating_count=0,
        module_count=len(modules_data),
        lesson_count=sum(len(m.get("lessons", [])) for m in modules_data),
    )
    db.add(course)
    await db.flush()

    total_lessons = 0
    total_exercises = 0
    course_title = c.get("title", "Course")

    for mi, mod in enumerate(modules_data):
        module = Module(
            id=uuid4(), course_id=course.id,
            title=mod.get("title", f"Module {mi+1}"),
            slug=mod.get("slug", f"module-{mi+1}"),
            description=mod.get("description", ""),
            display_order=mi+1, lesson_count=len(mod.get("lessons", [])),
        )
        db.add(module)
        await db.flush()

        for li, les in enumerate(mod.get("lessons", [])):
            logger.info("ai.import.lesson", mod=mi+1, les=li+1, title=les.get("title"))

            try:
                content = generate_lesson_content(
                    course_title, mod.get("title", ""), les.get("title", "")
                )
            except Exception as e:
                logger.warning("ai.import.gen_failed", title=les.get("title"), error=str(e))
                content = {
                    "content_markdown": f"# {les.get('title')}\n\nContent generating...",
                    "exercises": [],
                }

            lesson = Lesson(
                id=uuid4(), module_id=module.id,
                title=les.get("title", f"L{li+1}"),
                slug=les.get("slug", f"lesson-{li+1}"),
                description=les.get("description", ""),
                content=content.get("content_markdown", ""),
                content_markdown=content.get("content_markdown", ""),
                learning_objectives=les.get("learning_objectives", []),
                difficulty=DifficultyLevel(les.get("difficulty", "beginner")),
                estimated_duration_minutes=les.get("estimated_duration_minutes", 30),
                display_order=li+1,
                skill_tags=les.get("skill_tags", []),
                status=ContentStatus.PUBLISHED,
            )
            db.add(lesson)
            await db.flush()
            total_lessons += 1

            for ei, ex in enumerate(content.get("exercises", [])):
                try:
                    et = ExerciseType(ex.get("exercise_type", "code_completion"))
                except ValueError:
                    et = ExerciseType.CODE_COMPLETION
                try:
                    ed = ExerciseDifficulty(ex.get("difficulty", "easy"))
                except ValueError:
                    ed = ExerciseDifficulty.EASY

                exercise = Exercise(
                    id=uuid4(), lesson_id=lesson.id,
                    title=ex.get("title", f"Ex {ei+1}"),
                    description=ex.get("description", ""),
                    instructions=ex.get("instructions", ""),
                    exercise_type=et, difficulty=ed,
                    starter_code=ex.get("starter_code", ""),
                    solution_code=ex.get("solution_code", ""),
                    test_code=ex.get("test_code", ""),
                    hints=ex.get("hints", []),
                    skill_tags=les.get("skill_tags", []),
                    points=ex.get("points", 10),
                    display_order=ei+1,
                )
                db.add(exercise)
                total_exercises += 1

    await db.flush()
    await db.commit()

    logger.info("ai.import.done", slug=slug, modules=len(modules_data),
                lessons=total_lessons, exercises=total_exercises)

    return AICourseImportResponse(
        course_id=course.id, course_slug=slug,
        module_count=len(modules_data),
        lesson_count=total_lessons,
        exercise_count=total_exercises,
    )
