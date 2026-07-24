from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class EnrollmentCreate(BaseModel):
    roadmap_id: uuid.UUID | None = None
    course_id: uuid.UUID | None = None


class EnrollmentRead(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    roadmap_id: uuid.UUID | None = None
    course_id: uuid.UUID | None = None
    started_at: datetime
    completed_at: datetime | None = None
    status: str
    progress_percent: int
    last_lesson_id: uuid.UUID | None = None
    model_config = ConfigDict(from_attributes=True)


class EnrollmentProgress(BaseModel):
    course_id: uuid.UUID
    completed_lessons: int
    total_lessons: int
    progress_percent: int
    last_lesson_id: uuid.UUID | None = None
    model_config = ConfigDict(from_attributes=True)
