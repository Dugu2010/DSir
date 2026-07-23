from __future__ import annotations

from datetime import UTC, date, datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.models.learning import UserProfile
from src.models.user import User


def _today() -> date:
    return datetime.now(UTC).date()


def _calculate_streak(current_streak: int, last_activity_date: date | None) -> int:
    if last_activity_date is None:
        return 0
    today = _today()
    if last_activity_date == today or last_activity_date == today - timedelta(days=1):
        return current_streak
    return 0


async def _ensure_profile(user: User, db: AsyncSession) -> UserProfile:
    result = await db.execute(select(UserProfile).where(UserProfile.user_id == user.id))
    profile = result.scalar_one_or_none()
    if profile is None:
        profile = UserProfile(user_id=user.id)
        db.add(profile)
        await db.flush()
    return profile


async def record_activity(
    user: User,
    db: AsyncSession,
    xp_gain: int = 0,
) -> UserProfile:
    """Update a user's XP and streak. Callers must commit the transaction."""
    profile = await _ensure_profile(user, db)
    today = _today()
    last_date = profile.last_activity_date.date() if profile.last_activity_date else None
    streak = _calculate_streak(profile.current_streak, last_date)

    if profile.last_activity_date is None or last_date is None or last_date < today:
        if last_date == today - timedelta(days=1):
            streak += 1
        else:
            streak = 1
        profile.last_activity_date = datetime.now(UTC)
        profile.current_streak = streak
        if streak > profile.longest_streak:
            profile.longest_streak = streak

    profile.xp += xp_gain
    return profile
