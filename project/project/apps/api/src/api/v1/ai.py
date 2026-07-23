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
from src.schemas.ai import ChatRequest, ChatResponse, CodeReviewRequest, CodeReviewResponse

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
    messages = [
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
    messages = [
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


@router.post("/hints", response_model=ChatResponse)
async def generate_hint(
    concept_slug: str,
    problem: str,
    _current_user: User = Depends(get_current_active_user),
    _rate_limit: None = Depends(RateLimiter("30/minute")),
) -> ChatResponse:
    manager = get_ai_manager()
    prompt = PromptManager.get("hint").render(concept=concept_slug, problem=problem)

    messages = [Message(role=Role.USER, content=prompt)]
    response = await manager.generate(messages)
    return ChatResponse(
        content=response.content,
        model=response.model,
        prompt_tokens=response.prompt_tokens,
        completion_tokens=response.completion_tokens,
    )
