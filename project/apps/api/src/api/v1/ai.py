from __future__ import annotations

import json
import uuid
from collections.abc import AsyncGenerator
from typing import Any

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.ai.manager import AIError, AIManager, get_ai_manager
from src.ai.prompts import PromptManager
from src.ai.protocols import Message, Role
from src.ai.providers import (
    AnthropicProvider,
    CustomProvider,
    GeminiProvider,
    OllamaProvider,
    OpenAIProvider,
)
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
    ImportApproveRequest,
    ImportContentRequest,
    ImportContentResponse,
    ImportPreviewResponse,
    InterviewCoachRequest,
    InterviewCoachResponse,
    LessonProposal,
    ModuleProposal,
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


_COURSE_PREVIEW_SYSTEM_PROMPT = (
    "You are an expert curriculum designer. Given source text from a programming book or article, "
    "transform it into a structured course.\\n\\n"
    "Your task:\\n"
    "1. Analyze the source text thoroughly\\n"
    "2. Decide the course title, programming language, technology, and category based on the content\\n"
    "3. Create 4-8 modules (concepts) that cover the content, assigning EACH module its appropriate difficulty "
    "(beginner, intermediate, or advanced) based on how complex the content in that module is\\n"
    "4. Each module should have 2-4 lessons with real, working code examples\\n"
    "5. Each lesson must include:\\n"
    "   - A clear explanation body\\n"
    "   - Code example(s) in the specified language\\n"
    "   - A quiz question with options and the correct answer\\n"
    "   - Best practices\\n"
    "   - Common mistakes\\n"
    '   - A "try it yourself" exercise that builds a small real-world project piece\\n'
    "\\n"
    "IMPORTANT: Modernize and improve the content. If the source is outdated, update concepts, "
    "syntax, and examples to current best practices. Simplify explanations for beginners. "
    "Add new relevant topics that are missing.\\n\\n"
    "Respond ONLY with valid JSON. No markdown, no code fences. "
    'Use this exact structure:\\n'
    '{\\n'
    '  "title": "Course Title",\\n'
    '  "description": "Course description",\\n'
    '  "programming_language": "Python",\\n'
    '  "technology": "Python",\\n'
    '  "category": "Backend",\\n'
    '  "skills": ["Skill 1", "Skill 2"],\\n'
    '  "learning_objectives": ["Objective 1", "Objective 2"],\\n'
    '  "modules": [\\n'
    '    {\\n'
    '      "title": "Module/Concept Title",\\n'
    '      "description": "Module description",\\n'
    '      "difficulty": "beginner|intermediate|advanced",\\n'
    '      "lessons": [\\n'
    '        {\\n'
    '          "title": "Lesson Title",\\n'
    '          "body": "Markdown explanation text...",\\n'
    '          "code_language": "python",\\n'
    '          "code_example": "code here...",\\n'
    '          "quiz": {\\n'
    '            "question": "Quiz question?",\\n'
    '            "options": ["Option A", "Option B", "Option C"],\\n'
    '            "answer": "Correct option text"\\n'
    '          },\\n'
    '          "best_practices": ["Practice 1", "Practice 2"],\\n'
    '          "common_mistakes": ["Mistake 1", "Mistake 2"],\\n'
    '          "try_it": "Exercise description"\\n'
    '        }\\n'
    '      ]\\n'
    '    }\\n'
    '  ]\\n'
    '}'
)


def _parse_modules_from_ai_response(parsed: dict[str, Any]) -> list[ModuleProposal]:
    """Parse the AI response JSON into a list of ModuleProposal objects."""
    modules: list[ModuleProposal] = []
    for m in parsed.get("modules", []):
        lessons_raw = m.get("lessons", [])
        lessons: list[LessonProposal] = []
        for lsn in lessons_raw:
            lessons.append(LessonProposal(
                title=lsn.get("title", ""),
                body=lsn.get("body", ""),
                code_language=lsn.get("code_language", "text"),
                code_example=lsn.get("code_example", ""),
                quiz=lsn.get("quiz", {}),
                best_practices=lsn.get("best_practices", []),
                common_mistakes=lsn.get("common_mistakes", []),
                try_it=lsn.get("try_it", ""),
            ))
        modules.append(ModuleProposal(
            title=m.get("title", ""),
            description=m.get("description", ""),
            difficulty=m.get("difficulty", "intermediate"),
            lessons=lessons,
        ))
    return modules


def _build_provider_from_request(
    provider: str,
    api_key: str,
    api_url: str | None,
):
    """Build an AI provider from user-supplied request parameters."""
    name = provider.lower()
    if name == "openai":
        return OpenAIProvider(api_key=api_key)
    if name == "anthropic":
        return AnthropicProvider(api_key=api_key)
    if name == "gemini":
        return GeminiProvider(api_key=api_key)
    if name == "ollama":
        return OllamaProvider(base_url=api_url)
    if name == "custom":
        return CustomProvider(api_key=api_key, base_url=api_url)
    from src.ai.providers import MockProvider

    return MockProvider()


async def _get_ai_response(
    source_text: str,
    provider: str | None,
    api_key: str | None,
    api_url: str | None,
) -> dict[str, Any]:
    """Call AI with source text, return parsed JSON proposal."""
    messages = [
        Message(role=Role.SYSTEM, content=_COURSE_PREVIEW_SYSTEM_PROMPT),
        Message(
            role=Role.USER,
            content=f"Source text to transform into a course:\\n\\n{source_text}",
        ),
    ]

    if provider and api_key:
        prov = _build_provider_from_request(provider, api_key, api_url)
        manager = AIManager(prov)
    elif provider:
        manager = get_ai_manager(provider)
    else:
        manager = get_ai_manager()

    try:
        response = await manager.generate(messages, temperature=0.4, max_tokens=8000)
    except AIError as exc:
        error_msg = str(exc)
        # Extract the underlying error message from the retry wrapper
        if "failed after" in error_msg and ":" in error_msg:
            underlying = error_msg.split(":", 1)[-1].strip()
            if underlying:
                error_msg = underlying
        raise HTTPException(
            status_code=502,
            detail=f"AI provider error: {error_msg}. Check your API key and endpoint URL.",
        ) from None

    try:
        return _extract_json(response.content)
    except (json.JSONDecodeError, ValueError, IndexError):
        raise HTTPException(
            status_code=500,
            detail="AI returned invalid JSON. Try again or simplify the source text.",
        ) from None


async def _create_course_from_proposal(
    proposal: ImportPreviewResponse | ImportApproveRequest,
    db: AsyncSession,
) -> Course:
    """Create Course, Concept, and Lesson records in DB from an approved proposal.
    Does NOT commit — caller must commit."""
    course_title = proposal.title
    course_slug = _to_slug(course_title)

    existing = await db.execute(select(Course).where(Course.slug == course_slug))
    if existing.scalar_one_or_none():
        course_slug = f"{course_slug}-{uuid.uuid4().hex[:6]}"

    # Collect skills from module titles if empty
    skills = proposal.skills
    if not skills:
        skills = [m.title for m in proposal.modules if m.title]

    instructor = getattr(proposal, "instructor", "DSir Learning Team")

    course = Course(
        id=uuid.uuid4(),
        slug=course_slug,
        title=course_title,
        description=proposal.description,
        category=proposal.category,
        programming_language=proposal.programming_language,
        technology=proposal.technology,
        difficulty="mixed",
        instructor=instructor,
        is_published=True,
        estimated_duration=0,
        skills=skills,
        learning_objectives=proposal.learning_objectives,
    )
    db.add(course)
    await db.flush()

    total_duration = 0
    for module_idx, module_data in enumerate(proposal.modules, start=1):
        concept = Concept(
            id=uuid.uuid4(),
            course_id=course.id,
            slug=_to_slug(module_data.title),
            title=module_data.title,
            description=module_data.description or f"{module_data.title} - learn through examples.",
            order=module_idx,
            difficulty=module_data.difficulty,
            prerequisites=[],
        )
        db.add(concept)
        await db.flush()

        for lesson_idx, lesson_data in enumerate(module_data.lessons, start=1):
            quiz_data = lesson_data.quiz if isinstance(lesson_data.quiz, dict) else {}
            lesson = Lesson(
                id=uuid.uuid4(),
                concept_id=concept.id,
                slug=f"{_to_slug(module_data.title)}-lesson-{lesson_idx}",
                title=lesson_data.title,
                content={
                    "body": lesson_data.body or "",
                    "code_language": lesson_data.code_language or proposal.programming_language.lower(),
                    "code_example": lesson_data.code_example or "",
                    "quiz": [quiz_data] if quiz_data else [],
                    "best_practices": lesson_data.best_practices,
                    "common_mistakes": lesson_data.common_mistakes,
                    "try_it": lesson_data.try_it or "",
                },
                lesson_type="reading",
                position=lesson_idx,
                duration_minutes=15 + lesson_idx * 5,
            )
            db.add(lesson)
            total_duration += lesson.duration_minutes

    course.estimated_duration = total_duration
    return course


@router.post("/import-preview", response_model=ImportPreviewResponse)
async def import_preview(
    data: ImportContentRequest,
    _current_user: User = Depends(get_current_active_user),
    _rate_limit: None = Depends(RateLimiter("5/minute")),
) -> ImportPreviewResponse:
    """Analyze source text and return an AI-generated course proposal without saving to DB.
    User reviews the proposal and can edit before approving."""
    if not data.source_text.strip():
        raise HTTPException(status_code=400, detail="Source text is required")

    parsed = await _get_ai_response(data.source_text, data.provider, data.api_key, data.api_url)
    modules = _parse_modules_from_ai_response(parsed)

    return ImportPreviewResponse(
        title=parsed.get("title", "Untitled Course"),
        description=parsed.get("description", ""),
        programming_language=parsed.get("programming_language", "Python"),
        technology=parsed.get("technology", "Python"),
        category=parsed.get("category", "Backend"),
        skills=parsed.get("skills", []),
        learning_objectives=parsed.get("learning_objectives", []),
        modules=modules,
    )


@router.post("/import-approve", response_model=ImportContentResponse)
async def import_approve(
    proposal: ImportApproveRequest,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(require_content_creator),
    _rate_limit: None = Depends(RateLimiter("10/minute")),
) -> ImportContentResponse:
    """Create a course in the database from an approved (possibly user-edited) proposal.
    Requires content_creator, instructor, or admin role."""
    course = await _create_course_from_proposal(proposal, db)
    await db.commit()
    await db.refresh(course)

    modules_created = len(proposal.modules)
    lessons_created = sum(len(m.lessons) for m in proposal.modules)
    return ImportContentResponse(
        course_id=str(course.id),
        course_title=course.title,
        modules_created=modules_created,
        lessons_created=lessons_created,
        message=f"Course '{course.title}' created with {modules_created} modules and {lessons_created} lessons.",
    )


# ── Legacy endpoints (kept for backward compatibility) ──────────────────────


@router.post("/import-content", response_model=ImportContentResponse)
async def import_content(
    data: ImportContentRequest,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(require_content_creator),
    _rate_limit: None = Depends(RateLimiter("5/minute")),
) -> ImportContentResponse:
    """[Legacy] Import content directly. Prefer preview+approve workflow."""
    if not data.source_text.strip():
        raise HTTPException(status_code=400, detail="Source text is required")

    parsed = await _get_ai_response(data.source_text, data.provider, data.api_key, data.api_url)

    modules = _parse_modules_from_ai_response(parsed)

    proposal_data = ImportApproveRequest(
        title=parsed.get("title", "Imported Course"),
        description=parsed.get("description", ""),
        programming_language=parsed.get("programming_language", "Python"),
        technology=parsed.get("technology", "Python"),
        category=parsed.get("category", "Backend"),
        instructor="DSir Learning Team",
        skills=parsed.get("skills", []),
        learning_objectives=parsed.get("learning_objectives", []),
        modules=modules,
    )

    course = await _create_course_from_proposal(proposal_data, db)
    await db.commit()
    await db.refresh(course)

    modules_created = len(modules)
    lessons_created = sum(len(m.lessons) for m in modules)
    return ImportContentResponse(
        course_id=str(course.id),
        course_title=course.title,
        modules_created=modules_created,
        lessons_created=lessons_created,
        message=f"Course '{course.title}' created with {modules_created} modules and {lessons_created} lessons.",
    )


@router.post("/import-pdf", response_model=ImportPreviewResponse)
async def import_pdf(
    file: UploadFile = File(...),
    provider: str | None = Form(None),
    api_key: str | None = Form(None),
    api_url: str | None = Form(None),
    _current_user: User = Depends(get_current_active_user),
    _rate_limit: None = Depends(RateLimiter("5/minute")),
) -> ImportPreviewResponse:
    """Upload a PDF file and return an AI preview of the course structure (no DB save)."""
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    content_bytes = await file.read()
    if len(content_bytes) > 100 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="PDF file exceeds the 100 MB size limit")

    try:
        import fitz
    except ImportError:
        raise HTTPException(
            status_code=500,
            detail="PDF extraction library not installed. Contact the server administrator.",
        ) from None

    text_parts: list[str] = []
    try:
        doc = fitz.open(stream=content_bytes, filetype="pdf")
        try:
            for page in doc:
                text_parts.append(page.get_text())
        finally:
            doc.close()
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to extract text from PDF: {exc!s}",
        ) from None

    source_text = "\n\n".join(text_parts).strip()
    if not source_text:
        raise HTTPException(status_code=400, detail="No text could be extracted from the PDF")

    parsed = await _get_ai_response(source_text, provider, api_key, api_url)
    modules = _parse_modules_from_ai_response(parsed)

    return ImportPreviewResponse(
        title=parsed.get("title", "Untitled Course"),
        description=parsed.get("description", ""),
        programming_language=parsed.get("programming_language", "Python"),
        technology=parsed.get("technology", "Python"),
        category=parsed.get("category", "Backend"),
        skills=parsed.get("skills", []),
        learning_objectives=parsed.get("learning_objectives", []),
        modules=modules,
    )


# ── Chat / AI endpoints ────────────────────────────────────────────────────


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
