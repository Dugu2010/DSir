from __future__ import annotations

import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class AchievementRead(BaseModel):
    id: uuid.UUID
    slug: str
    title: str
    description: str | None
    icon: str | None
    xp_reward: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class UserAchievementRead(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    achievement_id: uuid.UUID
    earned_at: datetime
    achievement: AchievementRead
    model_config = ConfigDict(from_attributes=True)


class UserStatsRead(BaseModel):
    xp: int
    current_streak: int
    longest_streak: int
    last_activity_date: datetime | None
    daily_goal_minutes: int
    lessons_completed: int
    courses_completed: int
    weekly_minutes: list[tuple[date, int]]
