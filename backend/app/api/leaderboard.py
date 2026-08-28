from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models import LeaderboardEntry, UserStats
from app.schemas import LeaderboardEntryResponse, UserRankResponse
from app.utils.deps import get_current_active_user
from app.models import User
from uuid import UUID
from datetime import date, timedelta

router = APIRouter(prefix="/leaderboard", tags=["Leaderboard"])


# ── Leaderboard ─────────────────────────────────────────────────

@router.get("/", response_model=list[LeaderboardEntryResponse])
async def get_leaderboard(
    period: str = Query(default="weekly", pattern="^(daily|weekly|monthly|all_time)$"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    today = date.today()

    if period == "daily":
        period_start = today
        period_end = today
    elif period == "weekly":
        period_start = today - timedelta(days=today.weekday())
        period_end = today
    elif period == "monthly":
        period_start = today.replace(day=1)
        period_end = today
    else:
        period_start = date(2020, 1, 1)
        period_end = today

    # Query leaderboard entries
    result = await db.execute(
        select(LeaderboardEntry)
        .where(
            LeaderboardEntry.period_type == period,
            LeaderboardEntry.period_start == period_start,
        )
        .order_by(LeaderboardEntry.xp_earned.desc())
        .limit(100)
    )
    entries = result.scalars().all()

    # If no entries exist for this period, build from UserStats
    if not entries:
        rank = 0
        response = []
        stats_result = await db.execute(
            select(UserStats)
            .order_by(UserStats.total_xp.desc())
            .limit(100)
        )
        for stats in stats_result.scalars().all():
            rank += 1
            user_result = await db.execute(select(User).where(User.id == stats.user_id))
            user = user_result.scalar_one_or_none()
            if user:
                response.append(LeaderboardEntryResponse(
                    user_id=stats.user_id,
                    display_name=user.display_name,
                    avatar_url=user.avatar_url,
                    xp_earned=stats.total_xp,
                    rank=rank,
                    current_level=stats.current_level,
                ))
        return response

    # Build response from leaderboard entries
    response = []
    for i, entry in enumerate(entries):
        user_result = await db.execute(select(User).where(User.id == entry.user_id))
        user = user_result.scalar_one_or_none()
        if user:
            response.append(LeaderboardEntryResponse(
                user_id=entry.user_id,
                display_name=user.display_name,
                avatar_url=user.avatar_url,
                xp_earned=entry.xp_earned,
                rank=i + 1,
                current_level=0,  # Could join with UserStats
            ))

    return response


# ── My Rank ─────────────────────────────────────────────────────

@router.get("/me", response_model=UserRankResponse)
async def get_my_rank(
    period: str = Query(default="weekly", pattern="^(daily|weekly|monthly|all_time)$"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    today = date.today()

    if period == "weekly":
        period_start = today - timedelta(days=today.weekday())
    elif period == "monthly":
        period_start = today.replace(day=1)
    elif period == "daily":
        period_start = today
    else:
        period_start = date(2020, 1, 1)

    # Find user's rank
    result = await db.execute(
        select(LeaderboardEntry)
        .where(LeaderboardEntry.user_id == current_user.id, LeaderboardEntry.period_type == period)
    )
    entry = result.scalar_one_or_none()

    if entry and entry.rank:
        return UserRankResponse(rank=entry.rank, xp_earned=entry.xp_earned, period_type=period)

    # Fallback: count from stats
    stats_result = await db.execute(select(UserStats).where(UserStats.user_id == current_user.id))
    stats = stats_result.scalar_one_or_none()

    if stats:
        # Count users with more XP
        rank_result = await db.execute(
            select(func.count(UserStats.id))
            .where(UserStats.total_xp > stats.total_xp)
        )
        rank = (rank_result.scalar() or 0) + 1
        return UserRankResponse(rank=rank, xp_earned=stats.total_xp, period_type=period)

    return UserRankResponse(rank=0, xp_earned=0, period_type=period)
