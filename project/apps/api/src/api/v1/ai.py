from __future__ import annotations

from collections.abc import AsyncGenerator

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from src.ai.manager import get_ai_manager
from src.ai.prompts import PromptManager
from src.ai.protocols import Message, Role
from src.core.dependencies import get_current_active_user
from src.core.rate_limit import RateLimiter
from src.models.user import User
from src.schemas.ai import (
    ChatRequest,
    ChatResponse,
    CodeReviewRequest,
    CodeReviewResponse,
    HintRequest,
    HintResponse,
    InterviewCoachRequest,
    InterviewCoachResponse,
    RoadmapGenerateRequest,
    RoadmapGenerateResponse,
)

router = APIRouter()


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

    # Simple fallback parsing: treat response as title/desc/stages delimited by newlines.
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

    # Basic parsing for question, hints, follow-ups.
    lines = [line.strip() for line in response.content.strip().splitlines() if line.strip()]
    question = next(
        (
            line
            for line in lines
            if not line.lower().startswith("hint") and not line.lower().startswith("follow")
        ),
        response.content,
    )
    hints = [line.lstrip("- ").lstrip("* ") for line in lines if line.lower().startswith("hint")]
    follow_ups = [
        line.lstrip("- ").lstrip("* ") for line in lines if line.lower().startswith("follow")
    ]

    return InterviewCoachResponse(
        question=question,
        hints=hints or ["Think about the core concepts related to this role."],
        follow_ups=follow_ups or ["Can you explain your reasoning?"],
    )
