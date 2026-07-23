from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict


class ProfileUpdate(BaseModel):
    full_name: str | None = None
    timezone: str | None = None
    daily_goal_minutes: int | None = None
    preferred_language: str | None = None
    preferences: dict[str, Any] | None = None


class ProfileRead(BaseModel):
    user_id: str
    timezone: str | None = "UTC"
    daily_goal_minutes: int = 30
    preferred_language: str = "en"
    onboarding_completed: bool = False
    preferences: dict[str, Any] = {}
    model_config = ConfigDict(from_attributes=True)
