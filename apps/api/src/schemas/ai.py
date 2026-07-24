from __future__ import annotations

from pydantic import BaseModel


class ChatMessage(BaseModel):
    role: str  # user or assistant
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    mode: str = "mentor"  # mentor, code-review, debugger, interviewer, etc.
    temperature: float = 0.7
    max_tokens: int | None = None


class ChatResponse(BaseModel):
    content: str
    model: str
    prompt_tokens: int = 0
    completion_tokens: int = 0


class CodeReviewRequest(BaseModel):
    code: str
    language: str
    context: str | None = None


class CodeReviewResponse(BaseModel):
    feedback: str
    suggestions: list[str] = []
    issues: list[str] = []
