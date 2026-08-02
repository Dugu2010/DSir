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
import time
import httpx
from typing import Optional
import structlog

from app.config import get_settings

settings = get_settings()
logger = structlog.get_logger()


def _sample_text(raw_text: str, max_chars: int = 8000) -> str:
    """Smart sample from large text: head + key excerpts + tail."""
    if len(raw_text) <= max_chars:
        return raw_text
    head_size = max_chars // 2
    tail_size = max_chars // 4
    sample_size = max_chars - head_size - tail_size
    head = raw_text[:head_size]
    tail = raw_text[-tail_size:]
    middle = raw_text[head_size:-tail_size]
    paragraphs = [p.strip() for p in middle.split('\n\n') if p.strip()]
    if len(paragraphs) <= 3:
        sample = middle[:sample_size]
    else:
        step = max(1, len(paragraphs) // 5)
        sampled_paras = paragraphs[::step][:8]
        sample = '\n\n'.join(sampled_paras)
        if len(sample) > sample_size:
            sample = sample[:sample_size]
    return (
        head
        + '\n\n[... middle sections summarized ...]\n\n'
        + sample
        + '\n\n[... remaining chapters ...]\n\n'
        + tail
    )


def _call_text_llm(prompt: str, max_tokens: int = 4096) -> str:
    provider = settings.AI_DEFAULT_PROVIDER.lower()
    if provider == "gemini" and settings.GEMINI_API_KEY:
        return _call_gemini_text(prompt, max_tokens)
    if provider in ("openai", "anthropic") and settings.OPENAI_API_KEY:
        return _call_openai_compatible_text(prompt, max_tokens)
    if settings.GEMINI_API_KEY:
        return _call_gemini_text(prompt, max_tokens)
    if settings.OPENAI_API_KEY:
        return _call_openai_compatible_text(prompt, max_tokens)
    raise RuntimeError(
        "No AI provider available. Set GEMINI_API_KEY or OPENAI_API_KEY."
    )


def _call_gemini_text(prompt: str, max_tokens: int = 4096) -> str:
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
        raise RuntimeError(f"Gemini blocked: {reason}")
    cand = candidates[0]
    finish = cand.get("finishReason", "STOP")
    if finish not in ("STOP", "MAX_TOKENS"):
        raise RuntimeError(f"Gemini finish: {finish}")
    text = "".join(p.get("text", "") for p in cand.get("content", {}).get("parts", []))
    if not text:
        raise RuntimeError(f"Gemini empty text")
    return text


def _call_gemini_multimodal(prompt: str, image: dict, max_tokens: int = 4096) -> str:
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
        raise RuntimeError(f"Gemini HTTP {resp.status_code}")
    data = resp.json()
    candidates = data.get("candidates") or []
    if not candidates:
        raise RuntimeError("Gemini blocked")
    cand = candidates[0]
    text = "".join(p.get("text", "") for p in cand.get("content", {}).get("parts", []))
    if not text:
        raise RuntimeError("Gemini empty text")
    return text


def _call_openai_compatible_text(prompt: str, max_tokens: int = 4096) -> str:
    base_url = settings.AI_OPENAI_BASE_URL or "https://api.openai.com/v1"
    model = settings.AI_DEFAULT_MODEL or "gpt-4o-mini"
    base_url = base_url.rstrip("/")
    url = f"{base_url}/chat/completions"
    body = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.2,
    }
    last_error = None
    for attempt in range(5):
        resp = httpx.post(url, headers={
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
            "Content-Type": "application/json",
        }, json=body, timeout=180.0)
        if resp.status_code == 200:
            data = resp.json()
            choices = data.get("choices", [])
            if not choices:
                raise RuntimeError("No choices")
            text = choices[0].get("message", {}).get("content", "")
            if not text:
                raise RuntimeError("Empty response")
            logger.info("openai_compatible.ok", model=model, response_len=len(text))
            return text
        if resp.status_code == 429:
            retry_secs = 5.0
            try:
                err = resp.json()
                msg = err.get("error", {}).get("message", "")
                m = re.search(r'try again in ([\d.]+)s', msg)
                if m:
                    retry_secs = float(m.group(1)) + 0.5
            except Exception:
                pass
            wait = retry_secs * (2 ** attempt)
            logger.info("openai_compatible.rate_limited", attempt=attempt + 1, wait_secs=round(wait, 1))
            time.sleep(wait)
            last_error = f"Rate limited after {attempt + 1} attempts"
            continue
        raise RuntimeError(f"HTTP {resp.status_code}: {resp.text[:300]}")
    raise RuntimeError(last_error or "Failed after 5 retries")


def extract_text(data: bytes, filename: str = "") -> str:
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "txt"
    if ext == "pdf":
        text = _pdf_extract(data)
        if text and len(text) > 100:
            return text
        if not settings.GEMINI_API_KEY:
            raise RuntimeError("Image-based PDF requires GEMINI_API_KEY")
        return _pdf_ocr(data)
    if ext in ("png", "jpg", "jpeg", "webp", "bmp", "tiff", "gif"):
        if not settings.GEMINI_API_KEY:
            raise RuntimeError("Image OCR requires GEMINI_API_KEY")
        mime = f"image/{ext}" if ext != "jpg" else "image/jpeg"
        return _call_gemini_multimodal(
            "Transcribe all text from this image verbatim.",
            image={"mime": mime, "data": base64.b64encode(data).decode()},
        )
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return data.decode("latin-1", errors="replace")


def _pdf_extract(data: bytes) -> str:
    for lib in ("pdfplumber", "pypdf2"):
        try:
            if lib == "pdfplumber":
                import pdfplumber, warnings
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
    import pdfplumber, warnings
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
                    "Extract ALL text from this page verbatim.",
                    image={"mime": "image/png", "data": b64},
                    max_tokens=4096,
                )
                texts.append(t)
                logger.info("ocr_page", page=i + 1, chars=len(t))
            except Exception as e:
                logger.warning("ocr_page_failed", page=i + 1, error=str(e)[:100])
    return "\n\n".join(texts)


def generate_structure_preview(raw_text: str, topic_hint: str = "") -> dict:
    sampled = _sample_text(raw_text, max_chars=8000)
    prompt = f"""Analyze this educational content and create a course outline.
Output ONLY valid JSON with this structure:
{{"course":{{"title":"...","slug":"...","description":"...","long_description":"...","difficulty":"beginner","estimated_duration_minutes":600,"skill_tags":[...],"learning_objectives":[...]}},"modules":[{{"title":"...","slug":"...","description":"...","display_order":1,"lessons":[{{"title":"...","slug":"...","description":"...","difficulty":"beginner","estimated_duration_minutes":30,"skill_tags":[...],"learning_objectives":[...]}}]}}]}}
Rules: 4-8 modules, 2-4 lessons each. lowercase-hyphenated slugs.
Context: {topic_hint}
Content ({len(raw_text)} total chars, sampled):
{sampled}"""
    logger.info("preview.prompt_size", total_chars=len(raw_text), sampled_chars=len(sampled))
    resp = _call_text_llm(prompt, max_tokens=8192)
    result = _parse_json(resp)
    logger.info("preview_generated", course=result.get("course", {}).get("title"))
    return result


def generate_lesson_content(course_title: str, module_title: str, lesson_title: str) -> dict:
    prompt = f"""Write a programming lesson. Output ONLY this JSON:
{{"content_markdown":"## Section\\n\\nParagraph...\\n\\n```python\\ncode\\n```","exercises":[{{"title":"Practice: ...","description":"...","instructions":"...","exercise_type":"code_completion","difficulty":"easy","starter_code":"# code\\n","solution_code":"# solution\\n","test_code":"pass","hints":[{{"level":1,"content":"..."}}],"points":10}}]}}
Requirements: 300-500 words markdown, 2+ python code blocks, 1-2 exercises, valid JSON.
Course: {course_title}
Module: {module_title}
Lesson: {lesson_title}"""
    resp = _call_text_llm(prompt, max_tokens=4096)
    return _parse_json(resp)


def _sanitize_json_escapes(text: str) -> str:
    """Fix invalid JSON escape sequences from LLM outputs like backslash-d etc."""
    for ch in ['d', 's', 'w', 'D', 'S', 'W', '.', '(', ')', '[', ']', '{', '}', '+', '*', '?', '|', '^', '$']:
        text = text.replace('\\' + ch, '\\\\' + ch)
    return text


def _parse_json(text: str) -> dict:
    text = text.strip()
    if not text:
        raise ValueError("Empty AI response")
    logger.info("parse_json.start", preview=text[:200])
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    try:
        return json.loads(_sanitize_json_escapes(text))
    except json.JSONDecodeError:
        pass
    for pat in [r'```json\s*\n([\s\S]*?)\n```', r'```\s*\n([\s\S]*?)\n```']:
        m = re.search(pat, text)
        if m:
            try:
                return json.loads(m.group(1).strip())
            except json.JSONDecodeError:
                pass
            try:
                return json.loads(_sanitize_json_escapes(m.group(1).strip()))
            except json.JSONDecodeError:
                pass
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
                    return json.loads(text[best_start:i + 1])
                except json.JSONDecodeError:
                    pass
                try:
                    return json.loads(_sanitize_json_escapes(text[best_start:i + 1]))
                except json.JSONDecodeError:
                    best_start = -1
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
    for chunk in sorted(chunks, key=len, reverse=True):
        try:
            return json.loads(chunk)
        except json.JSONDecodeError:
            continue
        try:
            return json.loads(_sanitize_json_escapes(chunk))
        except json.JSONDecodeError:
            continue
    for chunk in chunks:
        try:
            fixed = re.sub(r',\s*}', '}', chunk)
            fixed = re.sub(r',\s*]', ']', fixed)
            return json.loads(fixed)
        except json.JSONDecodeError:
            continue
        try:
            fixed = re.sub(r',\s*}', '}', chunk)
            fixed = re.sub(r',\s*]', ']', fixed)
            return json.loads(_sanitize_json_escapes(fixed))
        except json.JSONDecodeError:
            continue
    logger.error("parse_json.all_failed", full_response=text[:3000])
    raise ValueError(f"Could not parse AI response as JSON")
