from __future__ import annotations

import uuid
from typing import Any

from pydantic import BaseModel, Field

DEFAULT_PAGE = 1
DEFAULT_PER_PAGE = 20
MAX_PER_PAGE = 100


class PaginationParams(BaseModel):
    page: int = Field(default=DEFAULT_PAGE, ge=1)
    per_page: int = Field(default=DEFAULT_PER_PAGE, ge=1, le=MAX_PER_PAGE)


class PaginatedResponse(BaseModel):
    items: list[dict[str, Any]]
    total: int
    page: int
    per_page: int
    pages: int


class ActivityCreate(BaseModel):
    activity_type: str
    entity_type: str | None = None
    entity_id: uuid.UUID | None = None
    meta: dict[str, Any] | None = None
