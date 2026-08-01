"""AI-powered content extraction and course generation for DSir admin."""
import base64
import json
import io
import re
from typing import Optional
import structlog

from app.config import get_settings

settings = get_settings()
logger = structlog.get_logger()


# ── Gemini client (lazy init) ────────────────────────────────

_genai_client = None


def _get_gemini():
    global _genai_client
    if _genai_client is None:
        try:
            import google.generativeai as genai
            genai.configure(api_key=settings.GEMINI_API_KEY)
            _genai_client = genai
        except ImportError:
            raise RuntimeError("google-generativeai not installed. Run: pip install google-generativeai")
        except Exception as e:
            raise RuntimeError(f"Failed to configure Gemini: {e}")
    return _genai_client


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

    # Images (handwritten/scanned) — use Gemini vision directly
    if ext in ("png", "jpg", "jpeg", "gif", "webp", "bmp", "tiff"):
        return _ocr_with_gemini(data, ext)

    # Text / Markdown / Code
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return data.decode("latin-1")


def _ocr_with_gemini(data: bytes, ext: str) -> str:
    """Use Gemini Vision to OCR an image (supports handwritten text)."""
    genai = _get_gemini()
    mime = f"image/{ext}" if ext != "jpg" else "image/jpeg"
    model = genai.GenerativeModel("gemini-2.0-flash")
    image_part = {"mime_type": mime, "data": base64.b64encode(data).decode()}
    resp = model.generate_content([
        "Extract ALL text from this image verbatim. Include code blocks, headings, bullet points exactly as they appear. Do not summarize or paraphrase. If it appears to be a handwritten note or textbook scan, transcribe every word carefully. Output ONLY the extracted text.",
        image_part,
    ])
    return resp.text or ""


# ── AI Content Structuring ────────────────────────────────────

STRUCTURE_PROMPT = """You are an expert curriculum designer. Output ONLY valid JSON — no explanations, no markdown outside the JSON.

I will give you educational content. Structure it into this JSON:

```json
{
  "course": {
    "title": "Course Title",
    "slug": "course-slug",
    "description": "2-sentence description",
    "long_description": "Detailed paragraph",
    "difficulty": "beginner|intermediate|advanced",
    "estimated_duration_minutes": 1200,
    "skill_tags": ["tag1", "tag2"],
    "learning_objectives": ["obj1", "obj2"]
  },
  "modules": [
    {
      "title": "Module Title",
      "slug": "module-slug",
      "description": "Brief description",
      "display_order": 1,
      "lessons": [
        {
          "title": "Lesson Title",
          "slug": "lesson-slug",
          "description": "One line summary",
          "difficulty": "beginner",
          "estimated_duration_minutes": 30,
          "skill_tags": ["tag"],
          "learning_objectives": ["obj"],
          "content_markdown": "## Section\\n\\nFull markdown content with ```python code blocks```",
          "exercises": [
            {
              "title": "Practice: Name",
              "description": "Test X",
              "instructions": "Complete the task",
              "exercise_type": "code_completion",
              "difficulty": "easy",
              "starter_code": "# starter",
              "solution_code": "# solution",
              "test_code": "assert True",
              "hints": [{"level": 1, "content": "Hint"}],
              "points": 10
            }
          ]
        }
      ]
    }
  ]
}
```

RULES:
- Output ONLY the JSON. No other text.
- 3-5 modules, 2-3 lessons per module, 1-2 exercises per lesson.
- Every content_markdown: 200+ words with at least 1 ```python code block.
- Slugs: lowercase-with-hyphens.
- Valid JSON only. No trailing commas.

Content:\n{content}"""


def generate_course_structure(raw_content: str, course_hint: str = "") -> dict:
    """Send raw content to Gemini and get back a fully structured course."""
    genai = _get_gemini()
    model = genai.GenerativeModel(
        "gemini-2.0-flash",
        generation_config={"temperature": 0.3, "max_output_tokens": 16384},
    )

    prompt = STRUCTURE_PROMPT.format(content=raw_content[:25000])
    if course_hint:
        prompt += f"\n\nAdditional context: This content is about {course_hint}."

    logger.info("ai_content.generate_course_structure.start", content_len=len(raw_content))
    resp = model.generate_content(prompt)
    text = (resp.text or "").strip()

    try:
        return _parse_json_response(text)
    except ValueError:
        logger.error("ai_content.parse_json.failed", raw_response=text[:2000])
        raise


def _parse_json_response(text: str) -> dict:
    """Extract and parse JSON from LLM response, handling many edge cases."""
    if not text or not text.strip():
        raise ValueError("AI returned empty response")

    # Log first 200 chars for debugging
    logger.info("ai_content.parse_json.start", preview=text[:200])

    # Strategy 1: Direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Strategy 2: Extract from ```json ... ``` fence
    m = re.search(r'```(?:json)?\s*\n?([\s\S]*?)\n?```', text)
    if m:
        try:
            return json.loads(m.group(1).strip())
        except json.JSONDecodeError:
            pass

    # Strategy 3: Find outermost balanced {} pair
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
    if start < 0:
        raise ValueError(f"AI response contained no JSON object. Preview: {text[:500]}")

    # Strategy 4: Find any { ... } via regex (non-greedy)
    for m in re.finditer(r'\{[^{}]*\{[\s\S]*?\}[^{}]*\}', text):
        try:
            return json.loads(m.group(0))
        except json.JSONDecodeError:
            continue

    # Strategy 5: Split on common delimiters and try each block
    for block in re.split(r'\n\n|```|\\n\\n', text):
        block = block.strip()
        if block.startswith('{'):
            try:
                return json.loads(block)
            except json.JSONDecodeError:
                continue

    raise ValueError(f"Failed to parse AI response as JSON. Raw preview: {text[:500]}")


def generate_lesson_content(topic: str, context: str = "") -> str:
    """Generate a single lesson's markdown content on demand."""
    genai = _get_gemini()
    model = genai.GenerativeModel("gemini-2.0-flash")

    prompt = f"""Write a comprehensive programming lesson on: {topic}

Requirements:
- At least 500 words of educational content
- Multiple ## sections (Concepts, Code Examples, Practice, Key Takeaways)
- At least 3 ```python code blocks with runnable examples
- Use proper markdown formatting
- Include practice exercises at the end
- Tone: encouraging, clear, professional

Context: {context[:2000] if context else 'General programming education'}

Output ONLY the markdown content."""
    resp = model.generate_content(prompt)
    return resp.text or f"# {topic}\n\nContent generation failed. Please try again."
