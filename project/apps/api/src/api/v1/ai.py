from __future__ import annotations

import json
import uuid
from collections.abc import AsyncGenerator
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.ai.manager import get_ai_manager
from src.ai.prompts import PromptManager
from src.ai.protocols import Message, Role
from src.core.dependencies import get_current_active_user, require_content_creator
from src.core.rate_limit import RateLimiter
from src.db.session import get_db
from src.models.content import Concept, Course, Lesson
from src.models.user import User
from src.schemas.ai import (
    ChatRequest,
    ChatResponse,
    CodeReviewRequest,
    CodeReviewResponse,
    HintRequest,
    HintResponse,
    ImportContentRequest,
    ImportContentResponse,
    InterviewCoachRequest,
    InterviewCoachResponse,
    RoadmapGenerateRequest,
    RoadmapGenerateResponse,
)


def _extract_json(text: str) -> dict[str, Any]:
    """Extract a JSON object from AI response text, handling code fences and surrounding text."""
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        data: dict[str, Any] = json.loads(text[start : end + 1])
        return data
    raise ValueError("No JSON object found in AI response")


router = APIRouter()


def _to_slug(text: str) -> str:
    """Convert text to a URL-friendly slug."""
    return text.lower().replace(" ", "-").replace(".", "").replace("&", "and")[:50]


_COURSE_IMPORT_SYSTEM_PROMPT = (
    "You are an expert curriculum designer. Given source text from a programming book or article, "
    "transform it into a structured course.\n\n"
    "Your task:\n"
    "1. Analyze the source text thoroughly\n"
    "2. Create 4-8 modules (concepts) that cover the content from beginner to advanced\n"
    "3. Each module should have 2-4 lessons with real, working code examples\n"
    "4. Each lesson must include:\n"
    "   - A clear explanation body\n"
    "   - Code example(s) in the specified language\n"
    "   - A quiz question with options and the correct answer\n"
    "   - Best practices\n"
    "   - Common mistakes\n"
    '   - A "try it yourself" exercise that builds a small real-world project piece\n'  # noqa: E501
    "\n"
    "IMPORTANT: Modernize and improve the content. If the source is outdated, update concepts, "
    "syntax, and examples to current best practices. Simplify explanations for beginners. "
    "Add new relevant topics that are missing.\n\n"
    "Respond ONLY with valid JSON. No markdown, no code fences. "
    'Use this exact structure:\n'
    '{\n'
    '  "title": "Course Title",\n'
    '  "description": "Course description",\n'
    '  "skills": ["Skill 1", "Skill 2"],\n'
    '  "learning_objectives": ["Objective 1", "Objective 2"],\n'
    '  "modules": [\n'
    '    {\n'
    '      "title": "Module/Concept Title",\n'
    '      "lessons": [\n'
    '        {\n'
    '          "title": "Lesson Title",\n'
    '          "body": "Markdown explanation text...",\n'
    '          "code_language": "python",\n'
    '          "code_example": "code here...",\n'
    '          "quiz": {\n'
    '            "question": "Quiz question?",\n'
    '            "options": ["Option A", "Option B", "Option C"],\n'
    '            "answer": "Correct option text"\n'
    '          },\n'
    '          "best_practices": ["Practice 1", "Practice 2"],\n'
    '          "common_mistakes": ["Mistake 1", "Mistake 2"],\n'
    '          "try_it": "Exercise description"\n'
    '        }\n'
    '      ]\n'
    '    }\n'
    '  ]\n'
    '}'  # noqa: E501
)


@router.post("/import-content", response_model=ImportContentResponse)
async def import_content(
    data: ImportContentRequest,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(require_content_creator),
    _rate_limit: None = Depends(RateLimiter("5/minute")),
) -> ImportContentResponse:
    """Import and transform content source text into a full course with modules and lessons."""
    if not data.source_text.strip():
        raise HTTPException(status_code=400, detail="Source text is required")

    manager = get_ai_manager()

    messages = [
        Message(
            role=Role.SYSTEM,
            content=_COURSE_IMPORT_SYSTEM_PROMPT,
        ),
        Message(
            role=Role.USER,
            content=(
                f"Course title: {data.course_title or 'Untitled Course'}\n"
                f"Programming language: {data.programming_language}\n"
                f"Category: {data.category}\n"
                f"Difficulty: {data.difficulty}\n\n"
                f"Source text to transform into a course:\n\n{data.source_text}"
            ),
        ),
    ]

    response = await manager.generate(messages, temperature=0.4, max_tokens=8000)

    try:
        parsed = _extract_json(response.content)
    except (json.JSONDecodeError, ValueError, IndexError):
        raise HTTPException(
            status_code=500,
            detail="AI returned invalid JSON. Try again or simplify the source text.",
        ) from None

    course_title = parsed.get("title", data.course_title or "Imported Course")
    course_slug = _to_slug(course_title)

    # Check slug uniqueness
    existing = await db.execute(select(Course).where(Course.slug == course_slug))
    if existing.scalar_one_or_none():
        course_slug = f"{course_slug}-{uuid.uuid4().hex[:6]}"

    skills = parsed.get("skills", [])
    if not skills:
        modules_raw = parsed.get("modules", [])
        skills = [m.get("title", "") for m in modules_raw if isinstance(m, dict) and m.get("title")]

    learning_objectives = parsed.get("learning_objectives", [])
    if not learning_objectives:
        modules_raw = parsed.get("modules", [])
        learning_objectives = [
            f"Understand {m.get('title', 'the concepts')}"
            for m in modules_raw[:4]
            if isinstance(m, dict)
        ]

    course = Course(
        id=uuid.uuid4(),
        slug=course_slug,
        title=course_title,
        description=parsed.get("description", ""),
        category=data.category,
        programming_language=data.programming_language,
        technology=data.technology,
        difficulty=data.difficulty,
        instructor=data.instructor,
        is_published=True,
        estimated_duration=0,
        skills=skills,
        learning_objectives=learning_objectives,
    )
    db.add(course)
    await db.flush()

    total_duration = 0
    modules_created = 0
    lessons_created = 0

    for module_idx, module_data in enumerate(parsed.get("modules", []), start=1):
        module_title = module_data.get("title", f"Module {module_idx}")
        concept = Concept(
            id=uuid.uuid4(),
            course_id=course.id,
            slug=_to_slug(module_title),
            title=module_title,
            description=module_data.get("description", f"{module_title} - learn through examples."),
            order=module_idx,
            prerequisites=[],
        )
        db.add(concept)
        await db.flush()
        modules_created += 1

        for lesson_idx, lesson_data in enumerate(module_data.get("lessons", []), start=1):
            lesson_title = lesson_data.get("title", f"Lesson {lesson_idx}")
            quiz_data = lesson_data.get("quiz", {})
            lesson = Lesson(
                id=uuid.uuid4(),
                concept_id=concept.id,
                slug=f"{_to_slug(module_title)}-lesson-{lesson_idx}",
                title=lesson_title,
                content={
                    "body": lesson_data.get("body", ""),
                    "code_language": lesson_data.get("code_language", data.programming_language.lower()),
                    "code_example": lesson_data.get("code_example", ""),
                    "quiz": [quiz_data] if quiz_data else [],
                    "best_practices": lesson_data.get("best_practices", []),
                    "common_mistakes": lesson_data.get("common_mistakes", []),
                    "try_it": lesson_data.get("try_it", ""),
                },
                lesson_type="reading",
                position=lesson_idx,
                duration_minutes=15 + lesson_idx * 5,
            )
            db.add(lesson)
            total_duration += lesson.duration_minutes
            lessons_created += 1

    course.estimated_duration = total_duration
    await db.commit()
    await db.refresh(course)

    return ImportContentResponse(
        course_id=str(course.id),
        course_title=course.title,
        modules_created=modules_created,
        lessons_created=lessons_created,
        message=f"Course '{course.title}' created with {modules_created} modules and {lessons_created} lessons.",
    )


@router.post("/chat", response_model=ChatResponse)
async def chat(
    data: ChatRequest,
    _current_user: User = Depends(get_current_active_user),
    _rate_limit: None = Depends(RateLimiter("30/minute")),
) -> ChatResponse:
    if not data.messages:
        raise HTTPException(status_code=400, detail="Messages are required")

    manager = get_ai_manager()
    system_message = Message(
        role=Role.SYSTEM,
        content=PromptManager.get("mentor-system").render(context=data.context or "DSir programming lesson"),
    )
    messages = [system_message] + [
        Message(role=Role.USER if m.role == "user" else Role.ASSISTANT, content=m.content) for m in data.messages
    ]

    response = await manager.generate(messages, data.temperature, data.max_tokens)
    return ChatResponse(
        content=response.content,
        model=response.model,
        prompt_tokens=response.prompt_tokens,
        completion_tokens=response.completion_tokens,
    )


@router.post("/chat/stream")
async def chat_stream(
    data: ChatRequest,
    _current_user: User = Depends(get_current_active_user),
    _rate_limit: None = Depends(RateLimiter("30/minute")),
) -> StreamingResponse:
    if not data.messages:
        raise HTTPException(status_code=400, detail="Messages are required")

    manager = get_ai_manager()
    system_message = Message(
        role=Role.SYSTEM,
        content=PromptManager.get("mentor-system").render(context=data.context or "DSir programming lesson"),
    )
    messages = [system_message] + [
        Message(role=Role.USER if m.role == "user" else Role.ASSISTANT, content=m.content) for m in data.messages
    ]

    async def event_generator() -> AsyncGenerator[str, None]:
        async for chunk in manager.generate_stream(messages, data.temperature, data.max_tokens):
            yield f"data: {chunk}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.post("/code-review", response_model=CodeReviewResponse)
async def code_review(
    data: CodeReviewRequest,
    _current_user: User = Depends(get_current_active_user),
    _rate_limit: None = Depends(RateLimiter("20/minute")),
) -> CodeReviewResponse:
    manager = get_ai_manager()
    prompt = PromptManager.get("code-review").render(
        language=data.language,
        code=data.code,
        context=data.context or "",
    )

    messages = [Message(role=Role.USER, content=prompt)]
    response = await manager.generate(messages)

    return CodeReviewResponse(
        feedback=response.content,
        suggestions=[],
        issues=[],
    )


@router.post("/hints", response_model=HintResponse)
async def generate_hint(
    data: HintRequest,
    _current_user: User = Depends(get_current_active_user),
    _rate_limit: None = Depends(RateLimiter("30/minute")),
) -> HintResponse:
    manager = get_ai_manager()
    prompt = PromptManager.get("hint").render(concept=data.concept, problem=data.problem)

    messages = [Message(role=Role.USER, content=prompt)]
    response = await manager.generate(messages)
    return HintResponse(hint=response.content)


@router.post("/roadmap/generate", response_model=RoadmapGenerateResponse)
async def generate_roadmap(
    data: RoadmapGenerateRequest,
    _current_user: User = Depends(get_current_active_user),
    _rate_limit: None = Depends(RateLimiter("10/minute")),
) -> RoadmapGenerateResponse:
    manager = get_ai_manager()
    prompt = PromptManager.get("roadmap-generator").render(
        goal=data.goal,
        experience=data.experience,
        technologies=", ".join(data.technologies or []),
    )
    messages = [Message(role=Role.USER, content=prompt)]
    response = await manager.generate(messages)

    lines = [line.strip() for line in response.content.strip().splitlines() if line.strip()]
    title = lines[0] if lines else f"Roadmap to {data.goal}"
    description = lines[1] if len(lines) > 1 else ""
    stages = [line.lstrip("- ").lstrip("* ") for line in lines[2:]]

    return RoadmapGenerateResponse(
        title=title,
        description=description,
        stages=stages,
        content=response.content,
    )


@router.post("/interview", response_model=InterviewCoachResponse)
async def interview_coach(
    data: InterviewCoachRequest,
    _current_user: User = Depends(get_current_active_user),
    _rate_limit: None = Depends(RateLimiter("20/minute")),
) -> InterviewCoachResponse:
    manager = get_ai_manager()
    prompt = PromptManager.get("interview-coach").render(
        role=data.role,
        level=data.level,
        topic=data.topic or "general",
    )
    messages = [Message(role=Role.USER, content=prompt)]
    response = await manager.generate(messages)

    lines = [line.strip() for line in response.content.strip().splitlines() if line.strip()]
    question = next(
        (line for line in lines if not line.lower().startswith("hint") and not line.lower().startswith("follow")),
        response.content,
    )
    hints = [line.lstrip("- ").lstrip("* ") for line in lines if line.lower().startswith("hint")]
    follow_ups = [line.lstrip("- ").lstrip("* ") for line in lines if line.lower().startswith("follow")]

    return InterviewCoachResponse(
        question=question,
        hints=hints or ["Think about the core concepts related to this role."],
        follow_ups=follow_ups or ["Can you explain your reasoning?"],
    )
