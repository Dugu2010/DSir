from __future__ import annotations

from pydantic import BaseModel


class ChatMessage(BaseModel):
    role: str  # user or assistant
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    mode: str = "mentor"  # mentor, code-review, debugger, interviewer, etc.
    context: str | None = None
    temperature: float = 0.7
    max_tokens: int | None = None


class RoadmapGenerateRequest(BaseModel):
    goal: str
    experience: str = "beginner"
    technologies: list[str] | None = None


class RoadmapGenerateResponse(BaseModel):
    title: str
    description: str
    stages: list[str]
    content: str


class InterviewCoachRequest(BaseModel):
    role: str
    level: str = "mid-level"
    topic: str | None = None


class InterviewCoachResponse(BaseModel):
    question: str
    hints: list[str]
    follow_ups: list[str]


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


class HintRequest(BaseModel):
    concept: str
    problem: str


class HintResponse(BaseModel):
    hint: str
