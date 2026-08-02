"""AI-powered content extraction and course generation for DSir admin.

Uses Google Gemini 2.0 Flash REST API directly.
Two-pass chunking: structure first, then each lesson individually.
Handles books of ANY size including image-based/scanned PDFs."""
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

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"


def _call_gemini(prompt: str, image_data: Optional[dict] = None, max_tokens: int = 8192) -> str:
    """Call Gemini REST API directly. Returns text response."""
    url = f"{GEMINI_API_URL}?key={settings.GEMINI_API_KEY}"
    if not settings.GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY not configured. Set it in Render environment variables.")

    parts = []
    if image_data:
        parts.append({"inline_data": {"mime_type": image_data["mime_type"], "data": image_data["data"]}})
    parts.append({"text": prompt})

    payload = {
        "contents": [{"parts": parts}],
        "generationConfig": {"temperature": 0.3, "maxOutputTokens": max_tokens, "topP": 0.95},
        "safetySettings": [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ],
    }

    try:
        resp = httpx.post(url, json=payload, timeout=180.0)
        resp.raise_for_status()
        data = resp.json()
        if "candidates" not in data or not data["candidates"]:
            reason = data.get("promptFeedback", {}).get("blockReason", "unknown")
            raise RuntimeError(f"Gemini blocked: {reason}")
        candidate = data["candidates"][0]
        if candidate.get("finishReason") == "SAFETY":
            raise RuntimeError("Gemini blocked by safety filter")
        parts = candidate.get("content", {}).get("parts", [])
        text = "".join(p.get("text", "") for p in parts)
        if not text:
            raise RuntimeError(f"Gemini empty response. finishReason={candidate.get('finishReason')}")
        return text
    except httpx.HTTPStatusError as e:
        raise RuntimeError(f"Gemini HTTP {e.response.status_code}: {e.response.text[:400]}")
    except RuntimeError:
        raise
    except Exception as e:
        raise RuntimeError(f"Gemini call failed: {e}")


# ── File Processing ───────────────────────────────────────────

def extract_text_from_bytes(data: bytes, filename: str = "") -> str:
    """Extract text from file. Falls back to Gemini Vision for image-based PDFs."""
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "txt"

    # PDF — try pdfplumber, then PyPDF2, then Gemini Vision
    if ext == "pdf":
        text = ""
        try:
            import pdfplumber
            with pdfplumber.open(io.BytesIO(data)) as pdf:
                pages = [p.extract_text() or "" for p in pdf.pages]
            text = "\n\n".join(pages).strip()
        except ImportError:
            pass
        if not text:
            try:
                import PyPDF2
                reader = PyPDF2.PdfReader(io.BytesIO(data))
                text = "\n\n".join((p.extract_text() or "") for p in reader.pages).strip()
            except ImportError:
                pass
        if text:
            return text
        # Image-based PDF — OCR via Gemini Vision
        logger.info("ai_content.pdf_image_based", filename=filename)
        return _ocr_pdf_via_gemini(data)

    # Images
    if ext in ("png", "jpg", "jpeg", "gif", "webp", "bmp", "tiff"):
        return _ocr_with_gemini(data, ext)

    # Text
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return data.decode("latin-1")


def _ocr_pdf_via_gemini(data: bytes) -> str:
    """Use Gemini Vision to OCR an image-based PDF page by page."""
    try:
        import pdfplumber
    except ImportError:
        raise RuntimeError("pdfplumber required for PDF processing")
    from PIL import Image

    with pdfplumber.open(io.BytesIO(data)) as pdf:
        all_text = []
        for i, page in enumerate(pdf.pages[:20]):  # Max 20 pages for OCR
            img = page.to_image(resolution=150)
            img_bytes = io.BytesIO()
            img.original.save(img_bytes, format="PNG")
            img_b64 = base64.b64encode(img_bytes.getvalue()).decode()
            try:
                page_text = _call_gemini(
                    "Extract ALL text from this textbook page verbatim. Include headings, code, bullet points exactly.",
                    image_data={"mime_type": "image/png", "data": img_b64},
                    max_tokens=4096,
                )
                all_text.append(page_text)
                logger.info("ai_content.ocr_page", page=i+1)
            except Exception as e:
                logger.warning("ai_content.ocr_page_failed", page=i+1, error=str(e))
        return "\n\n".join(all_text)


def _ocr_with_gemini(data: bytes, ext: str) -> str:
    """OCR a single image via Gemini Vision."""
    mime = f"image/{ext}" if ext != "jpg" else "image/jpeg"
    return _call_gemini(
        "Extract ALL text from this image verbatim. Include headings, code blocks, bullet points exactly as they appear. Do not summarize. Output ONLY the text.",
        image_data={"mime_type": mime, "data": base64.b64encode(data).decode()},
    )


# ── TWO-PASS COURSE GENERATION ────────────────────────────────

STRUCTURE_PROMPT = """Analyze this content and design a course STRUCTURE. Output ONLY valid JSON.

JSON format:
```json
{
  "course": {
    "title": "Course Title",
    "slug": "course-slug",
    "description": "2-sentence summary",
    "long_description": "Detailed paragraph",
    "difficulty": "beginner",
    "estimated_duration_minutes": 600,
    "skill_tags": ["tag1"],
    "learning_objectives": ["obj1"]
  },
  "modules": [
    {
      "title": "Module Title",
      "slug": "module-slug",
      "description": "Brief summary",
      "display_order": 1,
      "lessons": [
        {
          "title": "Lesson Title",
          "slug": "lesson-slug",
          "description": "One line",
          "difficulty": "beginner",
          "estimated_duration_minutes": 30,
          "skill_tags": ["tag"],
          "learning_objectives": ["obj"]
        }
      ]
    }
  ]
}
```

Rules: 3-7 modules, 2-4 lessons each. Slugs: lowercase-hyphens. JSON only.

Content:
{content}"""

LESSON_PROMPT = """Write a COMPLETE programming lesson. Output ONLY this JSON:

```json
{
  "content_markdown": "## Section\\n\\nFull markdown with ```python code```",
  "exercises": [
    {
      "title": "Practice: Name",
      "description": "Tests what",
      "instructions": "The task",
      "exercise_type": "code_completion",
      "difficulty": "easy",
      "starter_code": "# TODO",
      "solution_code": "# solution",
      "test_code": "assert True",
      "hints": [{"level": 1, "content": "Hint"}],
      "points": 10
    }
  ]
}
```

Requirements:
- 300-500 words of markdown with ## sections
- At least 2 ```python blocks with runnable examples
- 1-2 exercises per lesson
- "Practice Exercise" section at end
- Slug: lowercase-with-hyphens

Topic: {title}
Course: {course_title}
Module: {module_title}

JSON only. No other text."""


def generate_course_structure(raw_content: str, course_hint: str = "") -> dict:
    """Two-pass: structure first, then generate each lesson individually."""
    # PASS 1: Structure outline
    prompt = STRUCTURE_PROMPT.format(content=raw_content[:20000])
    if course_hint:
        prompt += f"\n\nTopic context: {course_hint}"
    logger.info("ai_content.pass1.start", content_len=len(raw_content))
    resp = _call_gemini(prompt, max_tokens=4096)
    structure = _parse_json(resp, "structure")
    course_title = structure.get("course", {}).get("title", "Course")
    total_lessons = sum(len(m.get("lessons", [])) for m in structure.get("modules", []))
    logger.info("ai_content.pass1.done", course=course_title, modules=len(structure.get("modules", [])), lessons=total_lessons)

    # PASS 2: Each lesson
    filled = 0
    for mod in structure.get("modules", []):
        for les in mod.get("lessons", []):
            filled += 1
            logger.info("ai_content.pass2.lesson", progress=f"{filled}/{total_lessons}", title=les.get("title"))
            try:
                r = _call_gemini(LESSON_PROMPT.format(title=les.get("title", ""), course_title=course_title, module_title=mod.get("title", "")), max_tokens=4096)
                d = _parse_json(r, f"lesson:{les.get('title')}")
                les["content_markdown"] = d.get("content_markdown", "")
                les["exercises"] = d.get("exercises", [])
            except Exception as e:
                logger.warning("ai_content.pass2.failed", lesson=les.get("title"), error=str(e))
                les["content_markdown"] = f"# {les.get('title')}\n\nContent generation encountered an error: {e}"
                les["exercises"] = []
    return structure


def _parse_json(text: str, ctx: str = "") -> dict:
    """Multi-strategy JSON extraction."""
    if not text or not text.strip():
        raise ValueError(f"[{ctx}] Empty response")
    # Direct
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    # Fence
    m = re.search(r'```(?:json)?\s*\n?([\s\S]*?)\n?```', text)
    if m:
        try:
            return json.loads(m.group(1).strip())
        except json.JSONDecodeError:
            pass
    # Balanced braces
    depth = start = 0
    for i, ch in enumerate(text):
        if ch == '{':
            if depth == 0:
                start = i
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0 and start >= 0:
                try:
                    return json.loads(text[start:i+1])
                except json.JSONDecodeError:
                    continue
    # Per-line
    for line in text.split('\n'):
        line = line.strip()
        if line.startswith('{') and line.endswith('}'):
            try:
                return json.loads(line)
            except json.JSONDecodeError:
                continue
    raise ValueError(f"[{ctx}] JSON parse failed. Preview: {text[:400]}")
