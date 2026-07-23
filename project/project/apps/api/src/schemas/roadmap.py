from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class RoadmapCreate(BaseModel):
    slug: str
    title: str
    description: str | None = None
    is_published: bool = False


class RoadmapUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    is_published: bool | None = None


class RoadmapRead(BaseModel):
    id: uuid.UUID
    slug: str
    title: str
    description: str | None = None
    is_published: bool
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class RoadmapCourseLink(BaseModel):
    roadmap_id: uuid.UUID
    course_id: uuid.UUID
    position: int
    model_config = ConfigDict(from_attributes=True)


class RoadmapDetail(RoadmapRead):
    roadmap_courses: list[RoadmapCourseLink] = []


class CourseReadWithConcepts(BaseModel):
    id: uuid.UUID
    slug: str
    title: str
    description: str | None = None
    technology: str
    is_published: bool
    model_config = ConfigDict(from_attributes=True)
