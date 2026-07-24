from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ExecutionRequest(BaseModel):
    code: str
    language: str
    timeout_ms: int = Field(default=3000, ge=100, le=30000)
    memory_limit_mb: int = Field(default=128, ge=16, le=1024)


class ExecutionResponse(BaseModel):
    stdout: str
    stderr: str
    exit_code: int
    execution_time_ms: int
    is_timeout: bool = False


class CodeReviewResult(BaseModel):
    feedback: str
    model: str | None = None


class ExecutionHistoryRead(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID | None
    language: str
    code: str
    stdout: str | None = None
    stderr: str | None = None
    exit_code: int | None = None
    execution_time_ms: int | None = None
    is_timeout: bool
    requested_timeout_ms: int
    requested_memory_mb: int
    provider: str
    status: str
    ai_review: CodeReviewResult | None = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ExecutionReviewResponse(BaseModel):
    execution: ExecutionResponse
    history_id: uuid.UUID
    ai_review: CodeReviewResult | None = None
