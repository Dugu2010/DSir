from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class RevisionScheduleRead(BaseModel):
    concept_id: uuid.UUID
    interval_days: int
    ease_factor: float
    repetitions: int
    due_at: datetime
    last_reviewed_at: datetime | None = None
    model_config = ConfigDict(from_attributes=True)


class RevisionSessionStart(BaseModel):
    concept_ids: list[uuid.UUID] | None = None


class RevisionSessionRead(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    started_at: datetime
    completed_at: datetime | None = None
    concepts: list[uuid.UUID]
    results: dict[str, Any]
    model_config = ConfigDict(from_attributes=True)


class ReviewRequest(BaseModel):
    concept_id: uuid.UUID
    quality: int  # 0-5


class ReviewResponse(BaseModel):
    concept_id: uuid.UUID
    quality: int
    new_interval_days: int
    new_ease_factor: float
    due_at: datetime


class ActiveRecallProblemRead(BaseModel):
    concept_id: uuid.UUID
    problem: dict[str, Any]
    due_at: datetime | None = None
    model_config = ConfigDict(from_attributes=True)


class ActiveRecallSessionRead(BaseModel):
    session_id: uuid.UUID
    problems: list[ActiveRecallProblemRead]


class RevisionAnalyticsRead(BaseModel):
    due_count: int
    total_scheduled: int
    sessions_count: int


class GenerateProblemRequest(BaseModel):
    concept_id: uuid.UUID
    difficulty: str = Field(default="medium", pattern="^(easy|medium|hard)$")
    mistakes: str = ""
