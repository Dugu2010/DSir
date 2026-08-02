"""AI content extraction and course generation — bulletproof edition.

Uses Gemini 2.0 Flash REST API. Handles any file type including scanned/handwritten.
Flow: extract → preview (structure) → approve → generate content → import"""
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

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"


def _gemini(prompt: str, image: Optional[dict] = None, max_tokens: int = 4096) -> str:
    """Call Gemini API. Returns text or raises with clear message."""
    if not settings.GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY not set in environment")

    parts = []
    if image:
        parts.append({"inline_data": {"mime_type": image["mime"], "data": image["data"]}})
    parts.append({"text": prompt})

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

    resp = httpx.post(f"{GEMINI_URL}?key={settings.GEMINI_API_KEY}", json=body, timeout=180.0)
    if resp.status_code != 200:
        raise RuntimeError(f"Gemini HTTP {resp.status_code}: {resp.text[:300]}")

    data = resp.json()
    candidates = data.get("candidates") or []

    # Safety block
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

    logger.info("gemini_call.ok", prompt_len=len(prompt), response_len=len(text), finish=finish)
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
        # Image-based PDF — OCR each page
        logger.info("extract.pdf_ocr_fallback", filename=filename)
        return _pdf_ocr(data)

    if ext in ("png", "jpg", "jpeg", "webp", "bmp", "tiff", "gif"):
        mime = f"image/{ext}" if ext != "jpg" else "image/jpeg"
        return _gemini("Transcribe all text from this image verbatim. Include code, headings, lists exactly. Output ONLY the extracted text.",
                       image={"mime": mime, "data": base64.b64encode(data).decode()})

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
                t = _gemini(
                    "Extract ALL text from this page verbatim. Include code, headings, lists exactly as they appear.",
                    image={"mime": "image/png", "data": b64},
                    max_tokens=4096,
                )
                texts.append(t)
                logger.info("ocr_page", page=i+1, chars=len(t))
            except Exception as e:
                logger.warning("ocr_page_failed", page=i+1, error=str(e)[:100])
    return "\n\n".join(texts)


# ═══════════════════════════════════════════════════════════════
# COURSE STRUCTURE (PASS 1)
# ═══════════════════════════════════════════════════════════════

def generate_structure_preview(raw_text: str, topic_hint: str = "") -> dict:
    """Step 1: Generate course structure (titles + slugs only, no content).

    Returns dict with course info and modules/lessons structure for preview.
    """
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

Content to analyze (first 15000 chars):
{raw_text[:15000]}"""

    resp = _gemini(prompt, max_tokens=8192)
    result = _parse_json(resp)
    logger.info("preview_generated", course=result.get("course", {}).get("title"))
    return result


def generate_lesson_content(course_title: str, module_title: str, lesson_title: str) -> dict:
    """Step 2: Generate full content + exercises for a single lesson."""
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

    resp = _gemini(prompt, max_tokens=4096)
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
                    candidate = text[best_start:i+1]
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
                chunks.append(text[start:i+1])
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
