from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class KnowledgeChunkCreate(BaseModel):
    content: str
    chunk_type: str = "lesson"
    course_id: uuid.UUID | None = None
    concept_id: uuid.UUID | None = None
    meta: dict[str, Any] = {}


class KnowledgeChunkRead(BaseModel):
    id: uuid.UUID
    course_id: uuid.UUID | None
    concept_id: uuid.UUID | None
    chunk_type: str
    content: str
    meta: dict[str, Any]
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class SearchRequest(BaseModel):
    query: str
    course_id: uuid.UUID | None = None
    concept_id: uuid.UUID | None = None
    limit: int = 5


class SearchResponse(BaseModel):
    query: str
    results: list[KnowledgeChunkRead]


class LearnerMemoryRequest(BaseModel):
    query: str
    limit: int = 5


class CourseKnowledgeRequest(BaseModel):
    course_id: uuid.UUID
    query: str
    limit: int = 5
