from __future__ import annotations

from datetime import date, datetime, timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.core.dependencies import get_current_active_user
from src.db.session import get_db
from src.models.content import Course
from src.models.learning import Achievement, Enrollment, LessonProgress, UserAchievement, UserActivity
from src.models.user import User
from src.schemas.common import PaginatedResponse
from src.schemas.gamification import UserAchievementRead, UserStatsRead
from src.schemas.content import CourseRead
from src.services.gamification import _calculate_streak, _ensure_profile

router = APIRouter()


@router.get("/me/stats", response_model=UserStatsRead)
async def get_my_stats(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> UserStatsRead:
    profile = await _ensure_profile(current_user, db)

    # Completed lessons count
    completed_result = await db.execute(
        select(func.count(LessonProgress.id)).where(
            LessonProgress.user_id == current_user.id,
            LessonProgress.is_completed.is_(True),
        )
    )
    lessons_completed = completed_result.scalar() or 0

    # Completed courses count (100% progress)
    enrollments_result = await db.execute(
        select(Enrollment).where(
            Enrollment.user_id == current_user.id,
            Enrollment.progress_percent == 100,
        )
    )
    courses_completed = len(enrollments_result.scalars().all())

    # Weekly minutes (last 7 days) derived from lesson completion activity
    weekly_minutes: list[tuple[date, int]] = []
    since = datetime.now(UTC) - timedelta(days=7)
    activity_result = await db.execute(
        select(UserActivity.created_at).where(
            UserActivity.user_id == current_user.id,
            UserActivity.activity_type == "completed_lesson",
            UserActivity.created_at >= since,
        )
    )
    minutes_by_day: dict[date, int] = {}
    for row in activity_result.all():
        activity_date = row[0].date()
        # Approximate 10 minutes per completed lesson activity
        minutes_by_day[activity_date] = minutes_by_day.get(activity_date, 0) + 10

    for i in range(6, -1, -1):
        day = datetime.now(UTC).date() - timedelta(days=i)
        weekly_minutes.append((day, minutes_by_day.get(day, 0)))

    return UserStatsRead(
        xp=profile.xp,
        current_streak=_calculate_streak(profile.current_streak, profile.last_activity_date.date() if profile.last_activity_date else None),
        longest_streak=profile.longest_streak,
        last_activity_date=profile.last_activity_date,
        daily_goal_minutes=profile.daily_goal_minutes,
        lessons_completed=lessons_completed,
        courses_completed=courses_completed,
        weekly_minutes=weekly_minutes,
    )


@router.get("/me/achievements", response_model=PaginatedResponse)
async def get_my_achievements(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse:
    result = await db.execute(
        select(UserAchievement)
        .where(UserAchievement.user_id == current_user.id)
        .options(selectinload(UserAchievement.achievement))
        .order_by(UserAchievement.earned_at.desc())
    )
    user_achievements = result.unique().scalars().all()
    total = len(user_achievements)

    return PaginatedResponse(
        items=[
            UserAchievementRead.model_validate(ua).model_dump()
            for ua in user_achievements
        ],
        total=total,
        page=1,
        per_page=max(total, 1),
        pages=1,
    )


@router.get("/recommendations", response_model=PaginatedResponse)
async def get_recommendations(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse:
    # Simple recommendation: suggest published courses the user is not enrolled in.
    enrolled_result = await db.execute(
        select(Enrollment.course_id).where(
            Enrollment.user_id == current_user.id,
            Enrollment.course_id.isnot(None),
        )
    )
    enrolled_ids = {row[0] for row in enrolled_result.all()}

    courses_result = await db.execute(
        select(Course).where(Course.is_published.is_(True)).order_by(Course.created_at.desc())
    )
    courses = courses_result.scalars().all()
    recommended = [c for c in courses if c.id not in enrolled_ids][:6]

    return PaginatedResponse(
        items=[CourseRead.model_validate(c).model_dump() for c in recommended],
        total=len(recommended),
        page=1,
        per_page=max(len(recommended), 1),
        pages=1,
    )
