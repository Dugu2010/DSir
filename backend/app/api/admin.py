from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Body, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete
from app.database import get_db
from app.models import User, Course, Module, Lesson, Exercise, Enrollment, LessonProgress, Submission, ContentStatus, UserStats, FeatureFlag, AuditLog, ExerciseType, ExerciseDifficulty, DifficultyLevel
from app.schemas import AdminDashboardStats, PaginatedResponse, CourseResponse, UserResponse, AICourseImportResponse
from app.utils.deps import require_admin, require_superadmin
from app.models import User as UserModel
from uuid import UUID, uuid4
from datetime import datetime, timezone, timedelta
import structlog, asyncio

logger = structlog.get_logger()
router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/dashboard", response_model=AdminDashboardStats)
async def admin_dashboard(admin_user: UserModel = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    now = datetime.now(timezone.utc); week_ago = now - timedelta(days=7)
    total_users = (await db.execute(select(func.count(UserModel.id)).where(UserModel.deleted_at.is_(None)))).scalar() or 0
    total_courses = (await db.execute(select(func.count(Course.id)).where(Course.deleted_at.is_(None), Course.status == ContentStatus.PUBLISHED))).scalar() or 0
    total_enrollments = (await db.execute(select(func.count(Enrollment.id)))).scalar() or 0
    total_completions = (await db.execute(select(func.count(Enrollment.id)).where(Enrollment.is_completed == True))).scalar() or 0
    active_today = (await db.execute(select(func.count(UserModel.id)).where(UserModel.last_active_at >= now - timedelta(hours=24), UserModel.deleted_at.is_(None)))).scalar() or 0
    new_users_week = (await db.execute(select(func.count(UserModel.id)).where(UserModel.created_at >= week_ago, UserModel.deleted_at.is_(None)))).scalar() or 0
    return AdminDashboardStats(total_users=total_users, total_courses=total_courses, total_enrollments=total_enrollments, total_completions=total_completions, active_today=active_today, new_users_week=new_users_week)


@router.get("/users", response_model=PaginatedResponse)
async def admin_list_users(page: int = Query(default=1, ge=1), size: int = Query(default=20, ge=1, le=100), search: str = Query(default=""), admin_user: UserModel = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    query = select(UserModel).where(UserModel.deleted_at.is_(None))
    if search: query = query.where(UserModel.email.ilike(f"%{search}%") | UserModel.username.ilike(f"%{search}%") | UserModel.display_name.ilike(f"%{search}%"))
    total = (await db.execute(select(func.count(UserModel.id)).where(UserModel.deleted_at.is_(None)))).scalar()
    result = await db.execute(query.order_by(UserModel.created_at.desc()).offset((page - 1) * size).limit(size))
    return PaginatedResponse(items=[UserResponse.model_validate(u) for u in result.scalars().all()], total=total, page=page, size=size, pages=(total + size - 1) // size)


@router.patch("/users/{user_id}/role")
async def update_user_role(user_id: UUID, role: str = Query(...), admin_user: UserModel = Depends(require_superadmin), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(UserModel).where(UserModel.id == user_id)); user = result.scalar_one_or_none()
    if not user: raise HTTPException(status_code=404, detail="User not found")
    from app.models import UserRole
    try: user.role = UserRole(role)
    except ValueError: raise HTTPException(status_code=400, detail="Invalid role")
    return {"detail": f"User role updated to {role}"}


@router.delete("/users/{user_id}")
async def admin_delete_user(user_id: UUID, admin_user: UserModel = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(UserModel).where(UserModel.id == user_id)); user = result.scalar_one_or_none()
    if not user: raise HTTPException(status_code=404, detail="User not found")
    user.deleted_at = datetime.now(timezone.utc); return {"detail": "User deleted"}


@router.get("/courses", response_model=PaginatedResponse)
async def admin_list_courses(page: int = Query(default=1, ge=1), size: int = Query(default=20, ge=1, le=100), status: str = Query(default=None), admin_user: UserModel = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    query = select(Course).where(Course.deleted_at.is_(None))
    if status:
        try: query = query.where(Course.status == ContentStatus(status))
        except ValueError: pass
    total = (await db.execute(select(func.count(Course.id)).where(Course.deleted_at.is_(None)))).scalar()
    result = await db.execute(query.order_by(Course.updated_at.desc()).offset((page - 1) * size).limit(size))
    return PaginatedResponse(items=[CourseResponse.model_validate(c) for c in result.scalars().all()], total=total, page=page, size=size, pages=(total + size - 1) // size)


@router.delete("/courses/{course_id}")
async def admin_delete_course(course_id: UUID, admin_user: UserModel = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Course).where(Course.id == course_id, Course.deleted_at.is_(None))); course = result.scalar_one_or_none()
    if not course: raise HTTPException(status_code=404, detail="Course not found")
    now = datetime.now(timezone.utc); course.deleted_at = now
    for mod in (await db.execute(select(Module).where(Module.course_id == course_id))).scalars().all():
        mod.deleted_at = now
        for les in (await db.execute(select(Lesson).where(Lesson.module_id == mod.id))).scalars().all():
            les.deleted_at = now
            for ex in (await db.execute(select(Exercise).where(Exercise.lesson_id == les.id))).scalars().all():
                ex.deleted_at = now
    await db.commit(); return {"detail": f"Course '{course.title}' deleted"}


@router.get("/feature-flags")
async def list_feature_flags(admin_user: UserModel = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(FeatureFlag))
    return [{"name": f.name, "is_enabled": f.is_enabled, "description": f.description} for f in result.scalars().all()]


@router.patch("/feature-flags/{flag_name}")
async def toggle_feature_flag(flag_name: str, is_enabled: bool = Query(...), admin_user: UserModel = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(FeatureFlag).where(FeatureFlag.name == flag_name)); flag = result.scalar_one_or_none()
    if not flag: raise HTTPException(status_code=404, detail="Feature flag not found")
    flag.is_enabled = is_enabled; return {"name": flag.name, "is_enabled": flag.is_enabled}


@router.get("/analytics/overview")
async def analytics_overview(admin_user: UserModel = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    now = datetime.now(timezone.utc); signups = []
    for i in range(30):
        day = now - timedelta(days=i); day_start = day.replace(hour=0, minute=0, second=0, microsecond=0); day_end = day_start + timedelta(days=1)
        count = (await db.execute(select(func.count(UserModel.id)).where(UserModel.created_at >= day_start, UserModel.created_at < day_end))).scalar() or 0
        signups.append({"date": day_start.date().isoformat(), "count": count})
    course_stats = await db.execute(select(Course.title, Course.enrollment_count).where(Course.status == ContentStatus.PUBLISHED, Course.deleted_at.is_(None)).order_by(Course.enrollment_count.desc()).limit(10))
    popular_courses = [{"title": row[0], "enrollments": row[1]} for row in course_stats.all()]
    return {"daily_signups": list(reversed(signups)), "popular_courses": popular_courses}


# AI CONTENT GENERATION (ASYNC)

@router.post("/ai/preview")
async def ai_preview(file: UploadFile = File(...), topic: str = Query(default=""), admin_user: UserModel = Depends(require_admin)):
    from app.services.ai_content import extract_text, generate_structure_preview
    data = await file.read()
    if not data: raise HTTPException(status_code=400, detail="Empty file")
    logger.info("ai.preview.start", file=file.filename, size=len(data))
    raw_text = extract_text(data, file.filename or "")
    if not raw_text or len(raw_text.strip()) < 50:
        raise HTTPException(status_code=400, detail=f"Could not extract enough text. Extracted {len(raw_text)} chars.")
    logger.info("ai.preview.extracted", text_len=len(raw_text))
    structure = await asyncio.to_thread(generate_structure_preview, raw_text, topic)
    mod_count = len(structure.get("modules", [])); les_count = sum(len(m.get("lessons", [])) for m in structure.get("modules", []))
    return {"success": True, "text_length": len(raw_text), "text_preview": raw_text[:1500], "structure": structure, "summary": {"title": structure.get("course", {}).get("title", ""), "modules": mod_count, "lessons": les_count, "difficulty": structure.get("course", {}).get("difficulty", ""), "description": structure.get("course", {}).get("description", ""), "skill_tags": structure.get("course", {}).get("skill_tags", [])}, "modules_preview": [{"title": m.get("title", ""), "lessons": [l.get("title", "") for l in m.get("lessons", [])]} for m in structure.get("modules", [])]}


@router.post("/ai/import", response_model=AICourseImportResponse)
async def ai_import_course(background_tasks: BackgroundTasks, structure: dict = Body(...), admin_user: UserModel = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    c = structure.get("course", {}); modules_data = structure.get("modules", [])
    if not c or not modules_data: raise HTTPException(status_code=400, detail="Missing course or modules")
    slug = c.get("slug", "ai-course"); existing = await db.execute(select(Course).where(Course.slug == slug))
    if existing.scalar_one_or_none(): slug = f"{slug}-{uuid4().hex[:6]}"
    now = datetime.now(timezone.utc)
    course = Course(id=uuid4(), title=c.get("title", "Course"), slug=slug, description=c.get("description", ""), long_description=c.get("long_description", ""), difficulty=DifficultyLevel(c.get("difficulty", "beginner")), estimated_duration_minutes=c.get("estimated_duration_minutes", 600), learning_objectives=c.get("learning_objectives", []), skill_tags=c.get("skill_tags", []), status=ContentStatus.PUBLISHED, published_at=now, is_featured=False, is_free=True, author_id=admin_user.id, enrollment_count=0, rating_average=0.0, rating_count=0, module_count=len(modules_data), lesson_count=sum(len(m.get("lessons", [])) for m in modules_data))
    db.add(course); await db.flush()
    total_lessons = 0; course_title = c.get("title", "Course")
    for mi, mod in enumerate(modules_data):
        module = Module(id=uuid4(), course_id=course.id, title=mod.get("title", f"Module {mi+1}"), slug=mod.get("slug", f"module-{mi+1}"), description=mod.get("description", ""), display_order=mi+1, lesson_count=len(mod.get("lessons", [])))
        db.add(module); await db.flush()
        for li, les in enumerate(mod.get("lessons", [])):
            lesson = Lesson(id=uuid4(), module_id=module.id, title=les.get("title", f"L{li+1}"), slug=les.get("slug", f"lesson-{li+1}"), description=les.get("description", ""), content="Generating content...", content_markdown="Generating content...", learning_objectives=les.get("learning_objectives", []), difficulty=DifficultyLevel(les.get("difficulty", "beginner")), estimated_duration_minutes=les.get("estimated_duration_minutes", 30), display_order=li+1, skill_tags=les.get("skill_tags", []), status=ContentStatus.PUBLISHED)
            db.add(lesson); total_lessons += 1
    await db.commit()
    background_tasks.add_task(_bg_generate_lessons, str(course.id), course_title, modules_data)
    logger.info("ai.import.queued", slug=slug, lessons=total_lessons)
    return AICourseImportResponse(course_id=course.id, course_slug=slug, module_count=len(modules_data), lesson_count=total_lessons, exercise_count=0)


@router.get("/ai/import/{course_slug}/status")
async def ai_import_status(course_slug: str, admin_user: UserModel = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Course).where(Course.slug == course_slug, Course.deleted_at.is_(None))); course = result.scalar_one_or_none()
    if not course: raise HTTPException(status_code=404, detail="Course not found")
    total = (await db.execute(select(func.count(Lesson.id)).join(Module).where(Module.course_id == course.id))).scalar() or 0
    P = "Generating content..."
    generated = (await db.execute(select(func.count(Lesson.id)).join(Module).where(Module.course_id == course.id, Lesson.content_markdown != P))).scalar() or 0
    ls = []
    for mod in (await db.execute(select(Module).where(Module.course_id == course.id).order_by(Module.display_order))).scalars().all():
        for les in (await db.execute(select(Lesson).where(Lesson.module_id == mod.id).order_by(Lesson.display_order))).scalars().all():
            ls.append({"id": str(les.id), "title": les.title, "slug": les.slug, "module_title": mod.title, "generated": les.content_markdown != P})
    return {"generated": generated, "total": total, "done": generated >= total, "lessons": ls}


async def _bg_generate_lessons(course_id_str: str, course_title: str, modules_data: list):
    from app.database import async_session_factory; from app.services.ai_content import generate_lesson_content
    from app.models import Module as M, Lesson as L, Exercise as E, ExerciseType as ET, ExerciseDifficulty as ED
    logger.info("bg.gen.start", course=course_title, modules=len(modules_data))
    async with async_session_factory() as db:
        course_id = UUID(course_id_str); generated = failed = 0
        for mod_data in modules_data:
            mod_slug = mod_data.get("slug", ""); result = await db.execute(select(M).where(M.course_id == course_id, M.slug == mod_slug)); module = result.scalar_one_or_none()
            if not module: continue
            for les_data in mod_data.get("lessons", []):
                les_slug = les_data.get("slug", ""); result = await db.execute(select(L).where(L.module_id == module.id, L.slug == les_slug)); lesson = result.scalar_one_or_none()
                if not lesson: continue
                try:
                    content = await asyncio.to_thread(generate_lesson_content, course_title, mod_data.get("title", ""), les_data.get("title", ""))
                    md = content.get("content_markdown", ""); lesson.content = md; lesson.content_markdown = md
                    await db.execute(delete(E).where(E.lesson_id == lesson.id))
                    for ei, ex in enumerate(content.get("exercises", [])):
                        try: et = ET(ex.get("exercise_type", "code_completion"))
                        except ValueError: et = ET.CODE_COMPLETION
                        try: ed = ED(ex.get("difficulty", "easy"))
                        except ValueError: ed = ED.EASY
                        db.add(E(id=uuid4(), lesson_id=lesson.id, title=ex.get("title", f"Ex {ei+1}"), description=ex.get("description", ""), instructions=ex.get("instructions", ""), exercise_type=et, difficulty=ed, starter_code=ex.get("starter_code", ""), solution_code=ex.get("solution_code", ""), test_code=ex.get("test_code", ""), hints=ex.get("hints", []), skill_tags=les_data.get("skill_tags", []), points=ex.get("points", 10), display_order=ei+1))
                    await db.commit(); generated += 1
                except Exception as e:
                    failed += 1; lesson.content_markdown = f"# {les_data.get('title')}\n\nGeneration failed. Try regenerating."; lesson.content = lesson.content_markdown
                    await db.commit(); logger.warning("bg.gen.failed", title=les_data.get("title"), error=str(e)[:100])
        logger.info("bg.gen.done", generated=generated, failed=failed)
