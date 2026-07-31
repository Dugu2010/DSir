from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text
from app.database import get_db
from app.models import (
    User, Course, Enrollment, LessonProgress, Submission,
    UserStats, FeatureFlag, AuditLog, ContentStatus,
)
from app.schemas import (
    AdminDashboardStats, PaginatedResponse,
    CourseCreate, CourseUpdate, CourseResponse,
    UserResponse, FeatureFlag as FeatureFlagSchema,
)
from app.utils.deps import require_admin, require_superadmin
from app.models import User as UserModel
from uuid import UUID
from datetime import datetime, timezone, timedelta, date

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
