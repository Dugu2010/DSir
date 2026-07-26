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


class ImportContentRequest(BaseModel):
    """Request to preview/approve course import. AI decides title, language, category, and per-module difficulty."""
    source_text: str
    provider: str | None = None
    api_key: str | None = None
    api_url: str | None = None


class ImportContentResponse(BaseModel):
    course_id: str
    course_title: str
    modules_created: int
    lessons_created: int
    message: str


class LessonProposal(BaseModel):
    title: str
    body: str
    code_language: str
    code_example: str
    quiz: dict[str, str | list[str]]
    best_practices: list[str]
    common_mistakes: list[str]
    try_it: str


class ModuleProposal(BaseModel):
    title: str
    description: str
    difficulty: str  # AI decides per-module: beginner, intermediate, advanced
    lessons: list[LessonProposal]


class ImportPreviewResponse(BaseModel):
    """AI-generated course proposal before saving. User reviews and approves."""
    title: str
    description: str
    programming_language: str
    technology: str
    category: str
    skills: list[str]
    learning_objectives: list[str]
    modules: list[ModuleProposal]


class ImportApproveRequest(BaseModel):
    """User-approved proposal to create the course in DB.

    The user can edit any field before approving. Exactly the same shape as ImportPreviewResponse.
    """
    title: str
    description: str
    programming_language: str
    technology: str
    category: str
    instructor: str = "DSir Learning Team"
    skills: list[str]
    learning_objectives: list[str]
    modules: list[ModuleProposal]
