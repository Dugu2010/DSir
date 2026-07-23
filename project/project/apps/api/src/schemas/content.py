from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict

if TYPE_CHECKING:
    from src.schemas.lesson import LessonRead


class CourseRead(BaseModel):
    id: uuid.UUID
    slug: str
    title: str
    description: str | None = None
    thumbnail: str | None = None
    category: str | None = None
    programming_language: str
    difficulty: str
    estimated_duration: int
    instructor: str | None = None
    skills: list[str] = []
    learning_objectives: list[str] = []
    technology: str
    is_published: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class CourseCreate(BaseModel):
    slug: str
    title: str
    description: str | None = None
    thumbnail: str | None = None
    category: str | None = None
    programming_language: str
    difficulty: str = "beginner"
    estimated_duration: int = 0
    instructor: str | None = None
    skills: list[str] = []
    learning_objectives: list[str] = []
    technology: str
    is_published: bool = False


class CourseUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    thumbnail: str | None = None
    category: str | None = None
    programming_language: str | None = None
    difficulty: str | None = None
    estimated_duration: int | None = None
    instructor: str | None = None
    skills: list[str] | None = None
    learning_objectives: list[str] | None = None
    technology: str | None = None
    is_published: bool | None = None


class ConceptRead(BaseModel):
    id: uuid.UUID
    slug: str
    title: str
    description: str | None = None
    difficulty: str | None = None
    order: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ConceptCreate(BaseModel):
    slug: str
    title: str
    description: str | None = None
    difficulty: str | None = None
    order: int = 0


class ConceptDetail(BaseModel):
    id: uuid.UUID
    slug: str
    title: str
    description: str | None = None
    difficulty: str | None = None
    order: int
    created_at: datetime
    lessons: list[LessonRead] = []
    model_config = ConfigDict(from_attributes=True)
