from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models import AIConversation, AIMessage
from app.schemas import (
    AIConversationCreate, AIConversationResponse,
    AIMessageCreate, AIMessageResponse,
    PaginatedResponse,
)
from app.utils.deps import get_current_active_user
from app.models import User
from app.config import get_settings
from uuid import UUID
from datetime import datetime, timezone
import httpx
import structlog

settings = get_settings()
logger = structlog.get_logger()
router = APIRouter(prefix="/ai", tags=["AI"])


# ── Conversations ───────────────────────────────────────────────

@router.get("/conversations", response_model=list[AIConversationResponse])
async def list_conversations(
    assistant_type: str = Query(default=None),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(AIConversation).where(
        AIConversation.user_id == current_user.id,
        AIConversation.is_archived == False,
    )
    if assistant_type:
        query = query.where(AIConversation.assistant_type == assistant_type)
    query = query.order_by(AIConversation.updated_at.desc())

    result = await db.execute(query)
    conversations = result.scalars().all()

    response = []
    for conv in conversations:
        msg_count_result = await db.execute(
            select(func.count(AIMessage.id)).where(AIMessage.conversation_id == conv.id)
        )
        resp = AIConversationResponse.model_validate(conv)
        resp.message_count = msg_count_result.scalar() or 0
        response.append(resp)

    return response


@router.post("/conversations", response_model=AIConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    data: AIConversationCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    conv = AIConversation(
        user_id=current_user.id,
        assistant_type=data.assistant_type,
        title=data.title,
        context_data=data.context_data,
    )
    db.add(conv)
    await db.flush()
    resp = AIConversationResponse.model_validate(conv)
    resp.message_count = 0
    return resp


@router.get("/conversations/{conv_id}/messages", response_model=list[AIMessageResponse])
async def get_messages(
    conv_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    conv_result = await db.execute(
        select(AIConversation).where(
            AIConversation.id == conv_id,
            AIConversation.user_id == current_user.id,
        )
    )
    conv = conv_result.scalar_one_or_none()
    if not conv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")

    msg_result = await db.execute(
        select(AIMessage)
        .where(AIMessage.conversation_id == conv_id)
        .order_by(AIMessage.created_at)
    )
    return msg_result.scalars().all()


@router.post("/conversations/{conv_id}/messages", response_model=AIMessageResponse)
async def send_message(
    conv_id: UUID,
    data: AIMessageCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    conv_result = await db.execute(
        select(AIConversation).where(
            AIConversation.id == conv_id,
            AIConversation.user_id == current_user.id,
        )
    )
    conv = conv_result.scalar_one_or_none()
    if not conv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")

    # Save user message
    user_msg = AIMessage(
        conversation_id=conv_id,
        role="user",
        content=data.content,
    )
    db.add(user_msg)

    # Get conversation history for context
    history_result = await db.execute(
        select(AIMessage)
        .where(AIMessage.conversation_id == conv_id)
        .order_by(AIMessage.created_at.desc())
        .limit(20)
    )
    history = history_result.scalars().all()

    # Build AI prompt based on assistant type
    system_prompt = _get_system_prompt(conv.assistant_type)
    messages = [{"role": "system", "content": system_prompt}]

    for msg in reversed(history):
        messages.append({"role": msg.role, "content": msg.content})
    messages.append({"role": "user", "content": data.content})

    # Call AI provider
    ai_response_text = await _call_ai_provider(messages)

    assistant_msg = AIMessage(
        conversation_id=conv_id,
        role="assistant",
        content=ai_response_text,
        tokens_used=len(ai_response_text.split()) if ai_response_text else 0,
    )
    db.add(assistant_msg)
    conv.updated_at = datetime.now(timezone.utc)

    # Auto-title conversation if no title
    if not conv.title:
        conv.title = data.content[:80] + ("..." if len(data.content) > 80 else "")

    await db.flush()
    return assistant_msg


# ═══════════════════════════════════════════════════════════════
# AI PROVIDER ROUTING
# ═══════════════════════════════════════════════════════════════

async def _call_ai_provider(messages: list[dict]) -> str:
    """Call the configured AI provider. Supports Gemini, OpenAI, and Anthropic."""
    provider = settings.AI_DEFAULT_PROVIDER.lower()

    # ── Gemini (Google AI) — free tier, best default ──
    if provider == "gemini" and settings.GEMINI_API_KEY:
        return await _call_gemini_chat(messages)

    # ── OpenAI ──
    elif provider == "openai" and settings.OPENAI_API_KEY:
        return await _call_openai_chat(messages)

    # ── Anthropic ──
    elif provider == "anthropic" and settings.ANTHROPIC_API_KEY:
        return await _call_anthropic_chat(messages)

    # ── No provider configured ──
    logger.warning("ai_provider.unavailable", provider=provider,
                   has_gemini=bool(settings.GEMINI_API_KEY),
                   has_openai=bool(settings.OPENAI_API_KEY),
                   has_anthropic=bool(settings.ANTHROPIC_API_KEY))
    return _get_fallback_response(messages[-1]["content"])


# ═══════════════════════════════════════════════════════════════
# GEMINI CHAT (Google AI — FREE tier)
# ═══════════════════════════════════════════════════════════════

async def _call_gemini_chat(messages: list[dict]) -> str:
    """Call Gemini REST API for chat.

    Converts OpenAI-format messages to Gemini format:
    - systemInstruction for the system prompt
    - contents[] with alternating user/model turns
    """
    model = settings.AI_DEFAULT_MODEL or "gemini-2.0-flash"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

    # Extract system prompt (first message if role=system)
    system_prompt = ""
    system_msgs = [m for m in messages if m["role"] == "system"]
    if system_msgs:
        system_prompt = "\n\n".join(m["content"] for m in system_msgs)

    # Convert conversation to Gemini contents format
    # Skip the system message, use alternating user/model
    contents = []
    chat_msgs = [m for m in messages if m["role"] != "system"]
    for msg in chat_msgs:
        role = "user" if msg["role"] == "user" else "model"
        contents.append({
            "role": role,
            "parts": [{"text": msg["content"]}]
        })

    body = {
        "contents": contents,
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 2000,
        },
        "safetySettings": [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ],
    }

    if system_prompt:
        body["systemInstruction"] = {
            "role": "system",
            "parts": [{"text": system_prompt}]
        }

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{url}?key={settings.GEMINI_API_KEY}",
                json=body,
            )
            if response.status_code != 200:
                logger.warning("gemini_chat.http_error",
                               status=response.status_code,
                               body=response.text[:300])
                return _get_fallback_response(messages[-1]["content"])

            data = response.json()
            candidates = data.get("candidates", [])
            if not candidates:
                fb = data.get("promptFeedback", {})
                reason = fb.get("blockReason", "unknown")
                logger.warning("gemini_chat.blocked", reason=reason)
                return _get_fallback_response(messages[-1]["content"])

            cand = candidates[0]
            finish = cand.get("finishReason", "STOP")
            text = "".join(
                p.get("text", "") for p in cand.get("content", {}).get("parts", [])
            )

            if not text:
                logger.warning("gemini_chat.empty_text", finish=finish)
                return _get_fallback_response(messages[-1]["content"])

            logger.info("gemini_chat.ok", response_len=len(text), finish=finish)
            return text

    except Exception as e:
        logger.error("gemini_chat.exception", error=str(e)[:200])
        return _get_fallback_response(messages[-1]["content"])


# ═══════════════════════════════════════════════════════════════
# OPENAI CHAT
# ═══════════════════════════════════════════════════════════════

async def _call_openai_chat(messages: list[dict]) -> str:
    """Call OpenAI Chat Completions API."""
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": settings.AI_DEFAULT_MODEL or "gpt-4o-mini",
                    "messages": messages,
                    "max_tokens": 2000,
                    "temperature": 0.7,
                },
            )
            if response.status_code == 200:
                data = response.json()
                return data["choices"][0]["message"]["content"]
            logger.warning("openai_chat.http_error",
                           status=response.status_code,
                           body=response.text[:300])
            return _get_fallback_response(messages[-1]["content"])
    except Exception as e:
        logger.error("openai_chat.exception", error=str(e)[:200])
        return _get_fallback_response(messages[-1]["content"])


# ═══════════════════════════════════════════════════════════════
# ANTHROPIC CHAT
# ═══════════════════════════════════════════════════════════════

async def _call_anthropic_chat(messages: list[dict]) -> str:
    """Call Anthropic Messages API."""
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": settings.ANTHROPIC_API_KEY,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "claude-3-5-sonnet-20241022",
                    "max_tokens": 2000,
                    "messages": [m for m in messages if m["role"] != "system"],
                    "system": next((m["content"] for m in messages if m["role"] == "system"), ""),
                },
            )
            if response.status_code == 200:
                data = response.json()
                return data["content"][0]["text"]
            logger.warning("anthropic_chat.http_error",
                           status=response.status_code,
                           body=response.text[:300])
            return _get_fallback_response(messages[-1]["content"])
    except Exception as e:
        logger.error("anthropic_chat.exception", error=str(e)[:200])
        return _get_fallback_response(messages[-1]["content"])


# ═══════════════════════════════════════════════════════════════
# FALLBACK & SYSTEM PROMPTS
# ═══════════════════════════════════════════════════════════════

def _get_fallback_response(user_message: str) -> str:
    """Provide a helpful fallback when AI APIs are unavailable."""
    return (
        "I'm here to help you learn! I noticed the AI service is currently unavailable. "
        "Here are some things you can try:\n\n"
        "1. **Review the lesson material** — Go back through the concepts covered in this section.\n"
        "2. **Practice exercises** — Apply what you've learned with hands-on coding exercises.\n"
        "3. **Create flashcards** — Use the revision system to reinforce key concepts.\n"
        "4. **Check the Q&A section** — See if other learners have asked similar questions.\n\n"
        "If you'd like, try rephrasing your question, or I can help with a specific concept from your current course."
    )


def _get_system_prompt(assistant_type: str) -> str:
    prompts = {
        "tutor": (
            "You are an expert programming tutor on the DSir learning platform. "
            "Your role is to help students understand programming concepts clearly and patiently. "
            "Explain concepts step by step. Use analogies when helpful. "
            "Provide code examples with explanations. "
            "Encourage the student and celebrate their progress. "
            "Never give complete solutions to exercises — guide them to discover the answer. "
            "Ask questions to check their understanding. "
            "Be friendly, supportive, and focused on their learning journey."
        ),
        "mentor": (
            "You are a senior software engineering mentor on the DSir platform. "
            "You provide career guidance, industry best practices, and architectural advice. "
            "Share real-world experiences and practical wisdom. "
            "Help learners understand what skills matter in the industry. "
            "Be honest about challenges while remaining encouraging. "
            "Focus on long-term growth and sustainable learning habits."
        ),
        "reviewer": (
            "You are an expert code reviewer on the DSir platform. "
            "Review code submissions for correctness, style, performance, and best practices. "
            "Be constructive and specific in your feedback. "
            "Point out what's good first, then suggest improvements. "
            "Explain WHY changes would be better, not just what to change. "
            "Reference relevant concepts and patterns."
        ),
        "debugger": (
            "You are an expert debugging assistant on the DSir platform. "
            "Help students identify and fix bugs in their code. "
            "Guide them through the debugging process step by step. "
            "Teach debugging strategies, not just fixes. "
            "Explain common error patterns and how to avoid them. "
            "Be patient — debugging is a skill that develops over time."
        ),
        "career": (
            "You are a career advisor specialized in software engineering careers on the DSir platform. "
            "Provide guidance on job searching, resume building, interview preparation, and career paths. "
            "Share insights on different roles (frontend, backend, DevOps, AI, etc.). "
            "Help learners understand what companies look for. "
            "Be realistic about the job market while remaining supportive."
        ),
    }
    return prompts.get(assistant_type, prompts["tutor"])


@router.delete("/conversations/{conv_id}")
async def delete_conversation(
    conv_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(AIConversation).where(
            AIConversation.id == conv_id,
            AIConversation.user_id == current_user.id,
        )
    )
    conv = result.scalar_one_or_none()
    if not conv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    conv.is_archived = True
    return {"detail": "Conversation archived"}
