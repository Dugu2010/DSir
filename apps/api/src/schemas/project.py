from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class ProjectRead(BaseModel):
    id: uuid.UUID
    course_id: uuid.UUID
    slug: str
    title: str
    description: str | None = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ProjectDetail(ProjectRead):
    requirements: dict[str, Any] = {}
    starter_files: dict[str, Any] = {}
    meta: dict[str, Any] = {}


class ProjectSubmissionCreate(BaseModel):
    project_id: uuid.UUID
    repository_url: str | None = None
    files: dict[str, Any] | None = None


class ProjectSubmissionRead(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    project_id: uuid.UUID
    repository_url: str | None = None
    score: int | None = None
    submitted_at: datetime
    reviewed_at: datetime | None = None
    model_config = ConfigDict(from_attributes=True)


class ProjectSubmissionDetail(ProjectSubmissionRead):
    files: dict[str, Any] | None = None
    feedback: dict[str, Any] | None = None
