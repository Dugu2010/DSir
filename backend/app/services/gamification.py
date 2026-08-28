"""Gamification engine.

Centralizes XP, levels, streaks, achievements, daily goals, leaderboard
entries, and notification generation so every learning action feeds the same
consistent pipeline (no placeholders — each helper does real work).
"""

import structlog
from datetime import date, datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    User, UserStats, Achievement, UserAchievement, Notification,
    NotificationType, DailyGoal, LeaderboardEntry, Enrollment,
    Lesson, Module, Course, LessonProgress, Submission,
    KnowledgeTopic, UserKnowledge,
)

logger = structlog.get_logger()


async def _invalidate_user_caches(user_id: UUID) -> None:
    """Drop cached dashboard/stats so gamification changes show immediately."""
    from app.utils.redis import delete_cache
    await delete_cache(f"user:dashboard:{user_id}")
    await delete_cache(f"user:stats:{user_id}")


# XP required to *reach* a given level (mirrors the frontend xpForLevel).
def xp_for_level(level: int) -> int:
    return int(100 * (level ** 1.5))


def level_for_xp(xp: int) -> int:
    level = 1
    while xp >= xp_for_level(level + 1):
        level += 1
    return level


async def _get_stats(db: AsyncSession, user_id: UUID) -> UserStats:
    result = await db.execute(select(UserStats).where(UserStats.user_id == user_id))
    stats = result.scalar_one_or_none()
    if not stats:
        stats = UserStats(user_id=user_id)
        db.add(stats)
        await db.flush()
    return stats


# ── Notifications ────────────────────────────────────────────────

async def notify(
    db: AsyncSession,
    user_id: UUID,
    type_: NotificationType,
    title: str,
    body: Optional[str] = None,
    data: Optional[dict] = None,
) -> Optional[Notification]:
    """Create a notification, de-duplicating identical unread ones."""
    dup = await db.execute(
        select(Notification).where(
            Notification.user_id == user_id,
            Notification.title == title,
            Notification.is_read == False,
        ).limit(1)
    )
    if dup.scalar_one_or_none():
        return None
    notif = Notification(user_id=user_id, type=type_, title=title, body=body, data=data)
    db.add(notif)
    return notif


# ── Streaks ──────────────────────────────────────────────────────

async def update_streak(db: AsyncSession, user: User) -> UserStats:
    """Advance the user's streak based on their last activity date."""
    stats = await _get_stats(db, user.id)
    today = date.today()
    last = stats.last_activity_date
    if last == today:
        return stats
    if last == today - timedelta(days=1):
        stats.current_streak += 1
    else:
        stats.current_streak = 1
    stats.last_activity_date = today
    if stats.current_streak > stats.longest_streak:
        stats.longest_streak = stats.current_streak
    return stats


# ── XP / Levels / Leaderboard ────────────────────────────────────

async def add_xp(db: AsyncSession, user: User, xp: int) -> UserStats:
    if xp <= 0:
        return await _get_stats(db, user.id)
    stats = await _get_stats(db, user.id)
    stats.total_xp += xp
    new_level = level_for_xp(stats.total_xp)
    if new_level > stats.current_level:
        stats.current_level = new_level
        await notify(
            db, user.id, NotificationType.SYSTEM,
            f"Level {new_level} reached! 🎉",
            f"You are now level {new_level}. Keep going!",
        )
    await _record_leaderboard(db, user.id, xp)
    await _invalidate_user_caches(user.id)
    return stats


async def _record_leaderboard(db: AsyncSession, user_id: UUID, xp: int) -> None:
    today = date.today()
    periods = {
        "daily": (today, today),
        "weekly": (today - timedelta(days=today.weekday()), today),
        "monthly": (today.replace(day=1), today),
        "all_time": (date(2020, 1, 1), today),
    }
    for period_type, (start, end) in periods.items():
        result = await db.execute(
            select(LeaderboardEntry).where(
                LeaderboardEntry.user_id == user_id,
                LeaderboardEntry.period_type == period_type,
                LeaderboardEntry.period_start == start,
            )
        )
        entry = result.scalar_one_or_none()
        if not entry:
            entry = LeaderboardEntry(
                user_id=user_id, period_type=period_type,
                period_start=start, period_end=end, xp_earned=0,
            )
            db.add(entry)
        entry.xp_earned = (entry.xp_earned or 0) + xp
        entry.period_end = end


# ── Daily Goals ──────────────────────────────────────────────────

async def _get_daily_goal(db: AsyncSession, user: User) -> DailyGoal:
    today = date.today()
    result = await db.execute(
        select(DailyGoal).where(DailyGoal.user_id == user.id, DailyGoal.goal_date == today)
    )
    goal = result.scalar_one_or_none()
    if not goal:
        prefs = user.preferences or {}
        goal = DailyGoal(
            user_id=user.id,
            goal_date=today,
            target_minutes=int(prefs.get("daily_goal_minutes", 30) or 30),
        )
        db.add(goal)
        await db.flush()
    return goal


async def record_daily_goal(
    db: AsyncSession,
    user: User,
    *,
    minutes: int = 0,
    lessons: int = 0,
    exercises: int = 0,
) -> DailyGoal:
    goal = await _get_daily_goal(db, user)
    goal.actual_minutes += minutes
    goal.actual_lessons += lessons
    goal.actual_exercises += exercises
    if (
        not goal.is_completed
        and goal.actual_minutes >= goal.target_minutes
        and goal.actual_lessons >= goal.target_lessons
        and goal.actual_exercises >= goal.target_exercises
    ):
        goal.is_completed = True
        await notify(
            db, user.id, NotificationType.STREAK,
            "Daily goal completed! 🎯",
            "You hit your daily learning goal. Great work!",
        )
    await _invalidate_user_caches(user.id)
    return goal


# ── Achievements ─────────────────────────────────────────────────

async def check_achievements(db: AsyncSession, user: User) -> list[Achievement]:
    """Evaluate all locked achievements against real user progress and
    unlock any newly earned ones (awarding XP + a notification)."""
    all_result = await db.execute(select(Achievement))
    all_achs = all_result.scalars().all()

    unlocked_result = await db.execute(
        select(UserAchievement.achievement_id).where(UserAchievement.user_id == user.id)
    )
    unlocked_ids = {str(row[0]) for row in unlocked_result.all()}

    stats = await _get_stats(db, user.id)
    ctx = await _build_achievement_context(db, user.id, stats)

    newly = []
    for ach in all_achs:
        if str(ach.id) in unlocked_ids:
            continue
        key = (ach.criteria or {}).get("type") or ach.name
        if _meets_criteria(key, ctx):
            db.add(UserAchievement(user_id=user.id, achievement_id=ach.id))
            await notify(
                db, user.id, NotificationType.ACHIEVEMENT,
                f"Achievement unlocked: {ach.name} {ach.icon}",
                ach.description,
                {"achievement": ach.name},
            )
            if ach.xp_reward > 0:
                await add_xp(db, user, ach.xp_reward)
            newly.append(ach)

    stats = await _get_stats(db, user.id)
    stats.current_level = level_for_xp(stats.total_xp)
    return newly


async def _build_achievement_context(db: AsyncSession, user_id: UUID, stats: UserStats) -> dict:
    perfect = (
        await db.execute(
            select(Submission).where(
                Submission.user_id == user_id,
                Submission.status == "passed",
                Submission.score == 100,
            ).limit(1)
        )
    ).scalar_one_or_none()

    course_count = (
        await db.execute(
            select(func.count(Enrollment.id)).where(
                Enrollment.user_id == user_id, Enrollment.is_completed == True
            )
        )
    ).scalar() or 0

    return {
        "lessons_completed": stats.lessons_completed,
        "exercises_completed": stats.exercises_completed,
        "current_streak": stats.current_streak,
        "perfect_score": perfect is not None,
        "courses_completed": course_count,
        "html_completed": await _course_completed(db, user_id, "html-css-fundamentals"),
        "js_completed": await _course_completed(db, user_id, "javascript-complete-guide"),
    }


async def _course_completed(db: AsyncSession, user_id: UUID, course_slug: str) -> bool:
    row = (
        await db.execute(
            select(Enrollment)
            .join(Course, Course.id == Enrollment.course_id)
            .where(
                Enrollment.user_id == user_id,
                Enrollment.is_completed == True,
                Course.slug == course_slug,
            ).limit(1)
        )
    ).scalar_one_or_none()
    return row is not None


def _meets_criteria(key: str, ctx: dict) -> bool:
    checks = {
        "python-starter": ctx["lessons_completed"] >= 1,
        "code-warrior": ctx["exercises_completed"] >= 10,
        "week-streak": ctx["current_streak"] >= 7,
        "course-complete": ctx["courses_completed"] >= 1,
        "perfect-score": ctx["perfect_score"],
        "html-master": ctx["html_completed"],
        "js-ninja": ctx["js_completed"],
    }
    return checks.get(key, False)


# ── One-shot activity hook ───────────────────────────────────────

async def record_activity(
    db: AsyncSession,
    user: User,
    *,
    minutes: int = 0,
    lessons: int = 0,
    exercises: int = 0,
) -> UserStats:
    """Advance streak + daily goal, then re-evaluate achievements.

    Called after any meaningful learning action (lesson completed, exercise
    passed, quiz passed). XP should be awarded separately via add_xp so the
    caller can pass the exercise/quiz point value. Returns the user's stats."""
    stats = await update_streak(db, user)
    if minutes or lessons or exercises:
        await record_daily_goal(
            db, user, minutes=minutes, lessons=lessons, exercises=exercises
        )
    await check_achievements(db, user)
    return stats


# ── Knowledge / Mastery ──────────────────────────────────────────

async def update_knowledge(db: AsyncSession, user: User, skill_tags: Optional[list]) -> None:
    """Increase mastery/confidence for the topics a completed lesson covers.

    Creates KnowledgeTopic rows on first sight so the mastery graph grows
    organically as content is consumed."""
    if not skill_tags:
        return
    for tag in skill_tags:
        slug = tag.lower().strip().replace(" ", "-").replace("_", "-")
        if not slug:
            continue
        topic = (await db.execute(
            select(KnowledgeTopic).where(KnowledgeTopic.slug == slug)
        )).scalar_one_or_none()
        if not topic:
            topic = KnowledgeTopic(name=tag.strip(), slug=slug)
            db.add(topic)
            await db.flush()

        uk = (await db.execute(
            select(UserKnowledge).where(
                UserKnowledge.user_id == user.id, UserKnowledge.topic_id == topic.id
            )
        )).scalar_one_or_none()
        if not uk:
            uk = UserKnowledge(user_id=user.id, topic_id=topic.id)
            db.add(uk)
            await db.flush()
        uk.mastery_level = min(100, float(uk.mastery_level) + 15)
        uk.confidence = min(100, float(uk.confidence) + 10)
        uk.assessment_count += 1
        uk.last_practiced_at = datetime.now(timezone.utc)
