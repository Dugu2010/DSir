from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from src.schemas.content import CourseRead


class BookmarkCreate(BaseModel):
    course_id: uuid.UUID


class BookmarkRead(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    course_id: uuid.UUID
    created_at: datetime
    course: CourseRead | None = None
    model_config = ConfigDict(from_attributes=True)
