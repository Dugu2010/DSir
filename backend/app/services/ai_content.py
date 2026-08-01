"""AI-powered content extraction and course generation for DSir admin.

Uses Google Gemini 2.0 Flash via direct REST API (not deprecated SDK).
Strategy: two-pass chunking — extract structure first, then generate each lesson separately.
Handles books of ANY size."""
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

    parts = []
    if image_data:
        parts.append({
            "inline_data": {"mime_type": image_data["mime_type"], "data": image_data["data"]}
        })
    parts.append({"text": prompt})

    payload = {
        "contents": [{"parts": parts}],
        "generationConfig": {
            "temperature": 0.3,
            "maxOutputTokens": max_tokens,
            "topP": 0.95,
        },
        "safetySettings": [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ],
    }

    try:
        resp = httpx.post(url, json=payload, timeout=120.0)
        resp.raise_for_status()
        data = resp.json()

        # Check for safety blocks
        if "candidates" not in data or not data["candidates"]:
            block_reason = data.get("promptFeedback", {}).get("blockReason", "unknown")
            raise RuntimeError(f"Gemini blocked response: {block_reason}")

        candidate = data["candidates"][0]
        if candidate.get("finishReason") == "SAFETY":
            raise RuntimeError("Gemini response blocked by safety filter")

        parts = candidate.get("content", {}).get("parts", [])
        text = "".join(p.get("text", "") for p in parts)
        if not text:
            raise RuntimeError(f"Gemini returned empty response. Finish reason: {candidate.get('finishReason')}")
        return text
    except httpx.HTTPStatusError as e:
        raise RuntimeError(f"Gemini API error {e.response.status_code}: {e.response.text[:500]}")
    except Exception as e:
        raise RuntimeError(f"Gemini API call failed: {str(e)}")


# ── File Processing ───────────────────────────────────────────

def extract_text_from_bytes(data: bytes, filename: str = "") -> str:
    """Extract raw text from uploaded file bytes. Supports PDF, images, and text."""
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "txt"

    # PDF
    if ext == "pdf":
        try:
            import pdfplumber
            with pdfplumber.open(io.BytesIO(data)) as pdf:
                pages = [p.extract_text() or "" for p in pdf.pages]
            return "\n\n".join(pages)
        except ImportError:
            pass
        try:
            import PyPDF2
            reader = PyPDF2.PdfReader(io.BytesIO(data))
            return "\n\n".join(p.extract_text() or "" for p in reader.pages)
        except ImportError:
            raise RuntimeError("No PDF library available. Install pdfplumber or PyPDF2.")

    # Images (handwritten/scanned) — use Gemini vision
    if ext in ("png", "jpg", "jpeg", "gif", "webp", "bmp", "tiff"):
        return _ocr_with_gemini(data, ext)

    # Text / Markdown / Code
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return data.decode("latin-1")


def _ocr_with_gemini(data: bytes, ext: str) -> str:
    """Use Gemini Vision to OCR an image (supports handwritten text)."""
    mime = f"image/{ext}" if ext != "jpg" else "image/jpeg"
    image_part = {"mime_type": mime, "data": base64.b64encode(data).decode()}
    return _call_gemini(
        "Extract ALL text from this image verbatim. Include code blocks, headings, bullet points exactly as they appear. Do not summarize. Output ONLY the extracted text.",
        image_data=image_part,
    )


# ── TWO-PASS COURSE GENERATION ────────────────────────────────

STRUCTURE_PROMPT = """You are an expert curriculum designer. Output ONLY valid JSON.

Analyze this educational content and create a course STRUCTURE (titles, descriptions, slugs — NO lesson content yet).

Output exactly this JSON:
```json
{
  "course": {
    "title": "Course Title",
    "slug": "course-slug",
    "description": "2-sentence description",
    "long_description": "Detailed paragraph about what students learn",
    "difficulty": "beginner",
    "estimated_duration_minutes": 600,
    "skill_tags": ["tag1"],
    "learning_objectives": ["obj1"]
  },
  "modules": [
    {
      "title": "Module Title",
      "slug": "module-slug",
      "description": "Brief module description",
      "display_order": 1,
      "lessons": [
        {
          "title": "Lesson Title",
          "slug": "lesson-slug",
          "description": "One-line summary",
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

RULES:
- 3-7 modules, 2-4 lessons per module
- Make slugs lowercase-with-hyphens
- Output ONLY valid JSON — no other text, no explanations
- DO NOT include content_markdown or exercises in this step

Content:
{content}"""

LESSON_PROMPT = """You are an expert programming educator. Write a COMPLETE lesson on this topic.

Topic: {title}
Course context: {course_title}
Module: {module_title}

Write 300-500 words of educational content in markdown format with:
- ## sections with clear headers
- At least 2 ```python code blocks with runnable examples
- Bullet lists for key concepts
- A "Practice Exercise" section at the end
- Professional, encouraging tone

Also create 1-2 coding exercises:

Output ONLY this JSON format:
```json
{
  "content_markdown": "## Section\\n\\nFull markdown...",
  "exercises": [
    {
      "title": "Practice: Name",
      "description": "What this tests",
      "instructions": "Complete the task",
      "exercise_type": "code_completion",
      "difficulty": "easy",
      "starter_code": "# TODO: complete",
      "solution_code": "# solution code",
      "test_code": "assert True",
      "hints": [{"level": 1, "content": "Think about..."}],
      "points": 10
    }
  ]
}
```

Output ONLY the JSON. No other text."""


def generate_course_structure(raw_content: str, course_hint: str = "") -> dict:
    """Two-pass: generate structure from content, then fill each lesson with AI.

    Step 1: Analyze content → get course outline (titles, slugs, no content yet)
    Step 2: For each lesson, generate content + exercises individually
    """
    # ── PASS 1: Get course structure ──
    prompt = STRUCTURE_PROMPT.format(content=raw_content[:20000])
    if course_hint:
        prompt += f"\n\nContext: {course_hint}"
    logger.info("ai_content.pass1.structure", content_len=len(raw_content))

    resp_text = _call_gemini(prompt, max_tokens=4096)
    structure = _parse_json(resp_text, "structure")
    logger.info("ai_content.pass1.done", course=structure.get("course", {}).get("title"),
                modules=len(structure.get("modules", [])))

    # ── PASS 2: Generate content for each lesson ──
    course_title = structure.get("course", {}).get("title", "Course")
    total_lessons = sum(len(m.get("lessons", [])) for m in structure.get("modules", []))
    filled = 0

    for mod in structure.get("modules", []):
        module_title = mod.get("title", "")
        for les in mod.get("lessons", []):
            filled += 1
            logger.info("ai_content.pass2.lesson", progress=f"{filled}/{total_lessons}",
                        lesson=les.get("title"))
            try:
                lesson_resp = _call_gemini(
                    LESSON_PROMPT.format(
                        title=les.get("title", ""),
                        course_title=course_title,
                        module_title=module_title,
                    ),
                    max_tokens=4096,
                )
                lesson_data = _parse_json(lesson_resp, f"lesson {les.get('title')}")
                les["content_markdown"] = lesson_data.get("content_markdown", "")
                les["exercises"] = lesson_data.get("exercises", [])
            except Exception as e:
                logger.warning("ai_content.pass2.lesson_failed", lesson=les.get("title"), error=str(e))
                les["content_markdown"] = f"# {les.get('title')}\n\nContent generation failed: {e}"
                les["exercises"] = []

    return structure


def _parse_json(text: str, context: str = "") -> dict:
    """Multi-strategy JSON extraction from LLM output."""
    if not text or not text.strip():
        raise ValueError(f"[{context}] Empty response")

    # Strategy 1: Direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        logger.info("ai_content.parse.direct_failed", context=context, error=str(e)[:100])

    # Strategy 2: ```json fence
    m = re.search(r'```(?:json)?\s*\n?([\s\S]*?)\n?```', text)
    if m:
        try:
            return json.loads(m.group(1).strip())
        except json.JSONDecodeError:
            pass

    # Strategy 3: Balanced braces (find outermost {})
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
                try:
                    return json.loads(text[start:i+1])
                except json.JSONDecodeError:
                    continue

    # Strategy 4: Try every line
    for line in text.split('\n'):
        line = line.strip()
        if line.startswith('{') and line.endswith('}'):
            try:
                return json.loads(line)
            except json.JSONDecodeError:
                continue

    raise ValueError(
        f"[{context}] Failed to parse JSON. Response: {text[:500]}"
    )
