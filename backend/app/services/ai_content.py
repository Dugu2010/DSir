"""AI content extraction and course generation — multi-provider edition.

Supports: Gemini (free), OpenAI, or any OpenAI-compatible API (Groq, DeepSeek, etc.)
Configure via: AI_DEFAULT_PROVIDER, AI_OPENAI_BASE_URL, GEMINI_API_KEY, OPENAI_API_KEY

Flow: extract → preview (structure) → approve → generate content → import

Multimodal/OCR calls always use Gemini (needs vision).
Text-only calls (structure, lesson content) use the configured provider.
"""
import base64
import json
import io
import re
import httpx
from typing import Optional
import structlog

from app.config import get_settings

settings = get_settings()
logger = structlog.get_logger()

# ═══════════════════════════════════════════════════════════════
# SMART TEXT SAMPLING — stays under free tier token limits
# ═══════════════════════════════════════════════════════════════

def _sample_text(raw_text: str, max_chars: int = 8000) -> str:
    """Smart sample from large text: head + key excerpts + tail.

    Strategy:
    - Head (50%): intro, TOC, early chapters — usually most important
    - Middle samples (25%): evenly-spaced paragraph excerpts
    - Tail (25%): advanced topics, appendices

    Keeps total prompt well under free tier TPM limits (Groq: 12K).
    """
    if len(raw_text) <= max_chars:
        return raw_text

    head_size = max_chars // 2
    tail_size = max_chars // 4
    sample_size = max_chars - head_size - tail_size

    head = raw_text[:head_size]
    tail = raw_text[-tail_size:]

    # Sample from middle: evenly-spaced paragraph excerpts
    middle = raw_text[head_size:-tail_size]
    paragraphs = [p.strip() for p in middle.split('\n\n') if p.strip()]

    if len(paragraphs) <= 3:
        sample = middle[:sample_size]
    else:
        # Take evenly-spaced paragraphs to cover the full range
        step = max(1, len(paragraphs) // 5)
        sampled_paras = paragraphs[::step][:8]
        sample = '\n\n'.join(sampled_paras)
        if len(sample) > sample_size:
            sample = sample[:sample_size]

    return (
        head
        + '\n\n[... middle sections summarized from chapter headings ...]\n\n'
        + sample
        + '\n\n[... remaining chapters covering advanced topics ...]\n\n'
        + tail
    )


# ═══════════════════════════════════════════════════════════════
# PROVIDER ROUTING — text-only LLM calls
# ═══════════════════════════════════════════════════════════════

def _call_text_llm(prompt: str, max_tokens: int = 4096) -> str:
    """Route text-only LLM calls to the best available provider.

    Priority:
    1. Configured provider (AI_DEFAULT_PROVIDER) if its key is set
    2. Any available provider as fallback
    """
    provider = settings.AI_DEFAULT_PROVIDER.lower()

    # ── Gemini ──
    if provider == "gemini" and settings.GEMINI_API_KEY:
        return _call_gemini_text(prompt, max_tokens)

    # ── OpenAI or OpenAI-compatible (Groq, DeepSeek, OpenRouter, etc.) ──
    if provider in ("openai", "anthropic") and settings.OPENAI_API_KEY:
        return _call_openai_compatible_text(prompt, max_tokens)

    # ── Fallback: try any available provider ──
    if settings.GEMINI_API_KEY:
        logger.info("text_llm.fallback_to_gemini", provider=provider)
        return _call_gemini_text(prompt, max_tokens)

    if settings.OPENAI_API_KEY:
        logger.info("text_llm.fallback_to_openai", provider=provider)
        return _call_openai_compatible_text(prompt, max_tokens)

    raise RuntimeError(
        "No AI provider available for text generation. "
        "Set GEMINI_API_KEY (free at https://aistudio.google.com/apikey) "
        "or OPENAI_API_KEY (with optional AI_OPENAI_BASE_URL for Groq/DeepSeek)."
    )


# ═══════════════════════════════════════════════════════════════
# GEMINI — text-only + multimodal
# ═══════════════════════════════════════════════════════════════

def _call_gemini_text(prompt: str, max_tokens: int = 4096) -> str:
    """Call Gemini for text-only generation."""
    model = settings.AI_DEFAULT_MODEL or "gemini-2.0-flash"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.2, "maxOutputTokens": max_tokens},
        "safetySettings": [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ],
    }

    resp = httpx.post(f"{url}?key={settings.GEMINI_API_KEY}", json=body, timeout=180.0)
    if resp.status_code != 200:
        raise RuntimeError(f"Gemini HTTP {resp.status_code}: {resp.text[:300]}")

    data = resp.json()
    candidates = data.get("candidates") or []

    if not candidates:
        fb = data.get("promptFeedback", {})
        reason = fb.get("blockReason", "unknown")
        if fb.get("safetyRatings"):
            reasons = [f"{s['category']}={s['probability']}" for s in fb["safetyRatings"]]
            reason = ", ".join(reasons)
        raise RuntimeError(f"Gemini blocked response: {reason}")

    cand = candidates[0]
    finish = cand.get("finishReason", "STOP")
    if finish not in ("STOP", "MAX_TOKENS"):
        raise RuntimeError(f"Gemini finish reason: {finish}")

    text = "".join(p.get("text", "") for p in cand.get("content", {}).get("parts", []))
    if not text:
        raise RuntimeError(f"Gemini returned empty text (finish={finish})")

    logger.info("gemini_text.ok", prompt_len=len(prompt), response_len=len(text), finish=finish)
    return text


def _call_gemini_multimodal(prompt: str, image: dict, max_tokens: int = 4096) -> str:
    """Call Gemini with an image (for OCR / multimodal). Kept separate from text-only."""
    model = settings.AI_DEFAULT_MODEL or "gemini-2.0-flash"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

    parts = [
        {"inline_data": {"mime_type": image["mime"], "data": image["data"]}},
        {"text": prompt},
    ]

    body = {
        "contents": [{"parts": parts}],
        "generationConfig": {"temperature": 0.2, "maxOutputTokens": max_tokens},
        "safetySettings": [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ],
    }

    resp = httpx.post(f"{url}?key={settings.GEMINI_API_KEY}", json=body, timeout=180.0)
    if resp.status_code != 200:
        raise RuntimeError(f"Gemini HTTP {resp.status_code}: {resp.text[:300]}")

    data = resp.json()
    candidates = data.get("candidates") or []

    if not candidates:
        fb = data.get("promptFeedback", {})
        reason = fb.get("blockReason", "unknown")
        raise RuntimeError(f"Gemini blocked response: {reason}")

    cand = candidates[0]
    finish = cand.get("finishReason", "STOP")
    text = "".join(p.get("text", "") for p in cand.get("content", {}).get("parts", []))
    if not text:
        raise RuntimeError(f"Gemini returned empty text (finish={finish})")

    logger.info("gemini_multimodal.ok", prompt_len=len(prompt), response_len=len(text))
    return text


# ═══════════════════════════════════════════════════════════════
# OPENAI-COMPATIBLE — text-only (OpenAI, Groq, DeepSeek, etc.)
# ═══════════════════════════════════════════════════════════════

def _call_openai_compatible_text(prompt: str, max_tokens: int = 4096) -> str:
    """Call any OpenAI-compatible Chat Completions API.

    Works with: OpenAI, Groq, DeepSeek, OpenRouter, Together AI, etc.
    Set AI_OPENAI_BASE_URL for non-OpenAI providers.
    """
    base_url = settings.AI_OPENAI_BASE_URL or "https://api.openai.com/v1"
    model = settings.AI_DEFAULT_MODEL or "gpt-4o-mini"

    # Strip trailing slash from base URL
    base_url = base_url.rstrip("/")
    url = f"{base_url}/chat/completions"

    body = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.2,
    }

    resp = httpx.post(
        url,
        headers={
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
            "Content-Type": "application/json",
        },
        json=body,
        timeout=180.0,
    )

    if resp.status_code != 200:
        raise RuntimeError(
            f"OpenAI-compatible HTTP {resp.status_code}: {resp.text[:300]}"
        )

    data = resp.json()
    choices = data.get("choices", [])
    if not choices:
        raise RuntimeError("OpenAI-compatible returned no choices")

    text = choices[0].get("message", {}).get("content", "")
    if not text:
        finish = choices[0].get("finish_reason", "unknown")
        raise RuntimeError(f"OpenAI-compatible empty response (finish={finish})")

    logger.info(
        "openai_compatible.ok",
        model=model,
        base_url=base_url,
        prompt_len=len(prompt),
        response_len=len(text),
    )
    return text


# ═══════════════════════════════════════════════════════════════
# FILE EXTRACTION
# ═══════════════════════════════════════════════════════════════

def extract_text(data: bytes, filename: str = "") -> str:
    """Extract text from any file. Falls back to Gemini OCR for images/scanned PDFs."""
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "txt"

    if ext == "pdf":
        text = _pdf_extract(data)
        if text and len(text) > 100:
            return text
        # Image-based PDF — OCR each page (multimodal, Gemini only)
        if not settings.GEMINI_API_KEY:
            raise RuntimeError(
                "This PDF has no extractable text (scanned/image-based). "
                "OCR requires GEMINI_API_KEY (free at https://aistudio.google.com/apikey)."
            )
        logger.info("extract.pdf_ocr_fallback", filename=filename)
        return _pdf_ocr(data)

    if ext in ("png", "jpg", "jpeg", "webp", "bmp", "tiff", "gif"):
        if not settings.GEMINI_API_KEY:
            raise RuntimeError(
                "Image OCR requires GEMINI_API_KEY (free at https://aistudio.google.com/apikey)."
            )
        mime = f"image/{ext}" if ext != "jpg" else "image/jpeg"
        return _call_gemini_multimodal(
            "Transcribe all text from this image verbatim. Include code, headings, lists exactly. Output ONLY the extracted text.",
            image={"mime": mime, "data": base64.b64encode(data).decode()},
        )

    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return data.decode("latin-1", errors="replace")


def _pdf_extract(data: bytes) -> str:
    """Try pdfplumber, then PyPDF2."""
    for lib in ("pdfplumber", "pypdf2"):
        try:
            if lib == "pdfplumber":
                import pdfplumber
                import warnings
                warnings.filterwarnings("ignore")
                with pdfplumber.open(io.BytesIO(data)) as pdf:
                    pages = [p.extract_text() or "" for p in pdf.pages]
                return "\n\n".join(pages).strip()
            else:
                import PyPDF2
                reader = PyPDF2.PdfReader(io.BytesIO(data))
                return "\n\n".join((p.extract_text() or "") for p in reader.pages).strip()
        except Exception:
            continue
    return ""


def _pdf_ocr(data: bytes) -> str:
    """OCR PDF by converting each page to image and sending to Gemini."""
    import pdfplumber
    import warnings
    warnings.filterwarnings("ignore")
    from PIL import Image

    texts = []
    with pdfplumber.open(io.BytesIO(data)) as pdf:
        for i, page in enumerate(pdf.pages[:25]):
            try:
                img = page.to_image(resolution=150)
                buf = io.BytesIO()
                img.original.save(buf, format="PNG")
                b64 = base64.b64encode(buf.getvalue()).decode()
                t = _call_gemini_multimodal(
                    "Extract ALL text from this page verbatim. Include code, headings, lists exactly as they appear.",
                    image={"mime": "image/png", "data": b64},
                    max_tokens=4096,
                )
                texts.append(t)
                logger.info("ocr_page", page=i + 1, chars=len(t))
            except Exception as e:
                logger.warning("ocr_page_failed", page=i + 1, error=str(e)[:100])
    return "\n\n".join(texts)


# ═══════════════════════════════════════════════════════════════
# COURSE STRUCTURE (PASS 1) — uses smart sampling + text provider
# ═══════════════════════════════════════════════════════════════

def generate_structure_preview(raw_text: str, topic_hint: str = "") -> dict:
    """Step 1: Generate course structure (titles + slugs only, no content).

    Returns dict with course info and modules/lessons structure for preview.
    Uses smart text sampling to stay under free tier token limits.
    Uses the configured AI text provider (Gemini, OpenAI, Groq, etc.)
    """
    # Smart sample to stay under free tier limits (Groq: 12K TPM)
    sampled = _sample_text(raw_text, max_chars=8000)

    prompt = f"""Analyze this educational content and create a course outline.

Output ONLY this exact JSON format (no other text):
{{
  "course": {{
    "title": "Course Title",
    "slug": "course-slug",
    "description": "Brief description (1-2 sentences)",
    "long_description": "What students will learn (paragraph)",
    "difficulty": "beginner",
    "estimated_duration_minutes": 600,
    "skill_tags": ["python", "programming"],
    "learning_objectives": ["Master Python basics"]
  }},
  "modules": [
    {{
      "title": "01. Getting Started",
      "slug": "getting-started",
      "description": "Module description",
      "display_order": 1,
      "lessons": [
        {{
          "title": "Lesson Name",
          "slug": "lesson-slug",
          "description": "What this covers",
          "difficulty": "beginner",
          "estimated_duration_minutes": 30,
          "skill_tags": ["basics"],
          "learning_objectives": ["Understand X"]
        }}
      ]
    }}
  ]
}}

Rules: 4-8 modules, 2-4 lessons each. lowercase-hyphenated slugs.

Additional context: {topic_hint}

Content to analyze (smart-sampled from {len(raw_text)} total chars):
{sampled}"""

    logger.info("preview.prompt_size", total_chars=len(raw_text), sampled_chars=len(sampled))
    resp = _call_text_llm(prompt, max_tokens=8192)
    result = _parse_json(resp)
    logger.info("preview_generated", course=result.get("course", {}).get("title"))
    return result


# ═══════════════════════════════════════════════════════════════
# LESSON CONTENT (PASS 2) — uses configured text provider
# ═══════════════════════════════════════════════════════════════

def generate_lesson_content(course_title: str, module_title: str, lesson_title: str) -> dict:
    """Step 2: Generate full content + exercises for a single lesson.

    Uses the configured AI text provider (Gemini, OpenAI, Groq, etc.)
    """
    prompt = f"""Write a programming lesson. Output ONLY this JSON:

{{
  "content_markdown": "## Section Title\\n\\nParagraph text with **bold** and *italic*.\\n\\n```python\\nprint('code example')\\n```\\n\\n## Practice\\n\\nExercise instructions...",
  "exercises": [
    {{
      "title": "Practice: Exercise Name",
      "description": "What student practices",
      "instructions": "Complete this task...",
      "exercise_type": "code_completion",
      "difficulty": "easy",
      "starter_code": "# Write your code here\\n",
      "solution_code": "# Solution\\n",
      "test_code": "pass",
      "hints": [{{"level": 1, "content": "Try thinking about..."}}],
      "points": 10
    }}
  ]
}}

Requirements:
- content_markdown: 300-500 words, 2+ ```python blocks, ## headers, Practice section
- 1-2 exercises with starter/solution code
- Valid JSON only, no trailing commas

Course: {course_title}
Module: {module_title}
Lesson: {lesson_title}"""

    resp = _call_text_llm(prompt, max_tokens=4096)
    return _parse_json(resp)


# ═══════════════════════════════════════════════════════════════
# JSON PARSING (bulletproof)
# ═══════════════════════════════════════════════════════════════

def _parse_json(text: str) -> dict:
    """Extract JSON from any AI response. Multiple strategies."""
    text = text.strip()
    if not text:
        raise ValueError("Empty AI response")

    logger.info("parse_json.start", preview=text[:200])

    # Strategy 1: direct
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        logger.info("parse_json.direct_failed", error=str(e)[:100])

    # Strategy 2: extract from ```json or ``` fences
    for pat in [r'```json\s*\n([\s\S]*?)\n```', r'```\s*\n([\s\S]*?)\n```']:
        m = re.search(pat, text)
        if m:
            try:
                return json.loads(m.group(1).strip())
            except json.JSONDecodeError:
                pass

    # Strategy 3: find outermost balanced { } pair
    depth = 0
    best_start = -1
    for i, ch in enumerate(text):
        if ch == '{':
            if depth == 0:
                best_start = i
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0 and best_start >= 0:
                try:
                    candidate = text[best_start:i + 1]
                    return json.loads(candidate)
                except json.JSONDecodeError:
                    best_start = -1

    # Strategy 4: try the largest chunk between { and }
    chunks = []
    depth = 0
    start = -1
    for i, ch in enumerate(text):
        if ch == '{':
            if depth == 0:
                start = i
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0 and start >= 0:
                chunks.append(text[start:i + 1])
                start = -1
    # Try from largest to smallest
    for chunk in sorted(chunks, key=len, reverse=True):
        try:
            return json.loads(chunk)
        except json.JSONDecodeError:
            continue

    # Strategy 5: try to fix common JSON issues
    for chunk in chunks:
        try:
            # Fix trailing commas
            fixed = re.sub(r',\s*}', '}', chunk)
            fixed = re.sub(r',\s*]', ']', fixed)
            return json.loads(fixed)
        except json.JSONDecodeError:
            continue

    # All strategies failed — log the full response for debugging
    logger.error("parse_json.all_failed", full_response=text[:3000])
    raise ValueError(f"Could not parse AI response as JSON. First 200 chars: {text[:200]}")
