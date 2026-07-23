from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class LessonRead(BaseModel):
    id: uuid.UUID
    concept_id: uuid.UUID
    slug: str
    title: str
    lesson_type: str
    position: int
    duration_minutes: int = 0
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class LessonDetail(LessonRead):
    content: dict[str, Any]
    meta: dict[str, Any] = {}


class LessonCreate(BaseModel):
    concept_id: uuid.UUID
    slug: str
    title: str
    content: dict[str, Any]
    lesson_type: str = "reading"
    position: int = 0
    duration_minutes: int = 0
    meta: dict[str, Any] = {}


class LessonProgressRead(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    lesson_id: uuid.UUID
    is_completed: bool
    completed_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class LessonProgressUpdate(BaseModel):
    is_completed: bool = True
