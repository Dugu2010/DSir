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

STRUCTURE_PROMPT = """You are an expert curriculum designer and educational content creator for a programming education platform called DSir.

I will give you raw educational content extracted from a handbook, textbook, or notes. Your job is to structure it into a complete course.

Output MUST be valid JSON with this exact structure:

```json
{
  "course": {
    "title": "Course Title — Catchy & Professional",
    "slug": "course-slug-with-hyphens",
    "description": "2-3 sentence compelling description",
    "long_description": "Detailed paragraph about what students will learn",
    "difficulty": "beginner|intermediate|advanced|expert",
    "estimated_duration_minutes": 1200,
    "skill_tags": ["tag1", "tag2", "tag3"],
    "learning_objectives": ["objective 1", "objective 2", "objective 3"]
  },
  "modules": [
    {
      "title": "01. Module Title",
      "slug": "module-slug",
      "description": "Brief module description",
      "display_order": 1,
      "lessons": [
        {
          "title": "Lesson Title",
          "slug": "lesson-slug",
          "description": "What this lesson covers in one line",
          "difficulty": "beginner|intermediate|advanced",
          "estimated_duration_minutes": 45,
          "skill_tags": ["tag"],
          "learning_objectives": ["objective"],
          "content_markdown": "Full lesson content in markdown with ## headers, ```python code blocks, bullet points, etc.",
          "exercises": [
            {
              "title": "Practice: Topic",
              "description": "Test understanding of X",
              "instructions": "Complete the challenge",
              "exercise_type": "code_completion|debugging|bug_fixing|output_prediction|refactoring|optimization",
              "difficulty": "easy|medium|hard",
              "starter_code": "# starter code\\n",
              "solution_code": "# solution\\n",
              "test_code": "assert True\\n",
              "hints": [{"level": 1, "content": "Hint text"}],
              "points": 15
            }
          ]
        }
      ]
    }
  ]
}
```

RULES:
1. Create 4-8 modules that flow logically from basics to advanced.
2. Each module should have 2-4 lessons.
3. Every lesson MUST have content_markdown — at least 500 words of real educational content with code examples in ```python blocks.
4. Every lesson MUST have at least 1 exercise.
5. Use proper markdown: ## headers, ```python code blocks, bullet lists, **bold**, *italic*.
6. Make the content pedagogically sound — explain concepts, show examples, provide practice.
7. For code-heavy topics, include runnable examples with print() statements.
8. The JSON must be valid and complete — no truncation, no ellipsis.
9. Slug values: lowercase, hyphen-separated, no special chars.

Here is the raw content to structure:

{content}"""


def generate_course_structure(raw_content: str, course_hint: str = "") -> dict:
    """Send raw content to Gemini and get back a fully structured course."""
    genai = _get_gemini()
    model = genai.GenerativeModel(
        "gemini-2.0-flash",
        generation_config={"temperature": 0.3, "max_output_tokens": 8192},
    )

    prompt = STRUCTURE_PROMPT.format(content=raw_content[:30000])
    if course_hint:
        prompt += f"\n\nAdditional context: This content is about {course_hint}."

    logger.info("ai_content.generate_course_structure.start", content_len=len(raw_content))
    resp = model.generate_content(prompt)
    text = resp.text or ""

    return _parse_json_response(text)


def _parse_json_response(text: str) -> dict:
    """Extract and parse JSON from LLM response, handling markdown fences."""
    # Try to extract from ```json ... ``` fences
    m = re.search(r'```(?:json)?\s*([\s\S]*?)```', text)
    if m:
        text = m.group(1)

    # Try direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try finding { ... } block
    m = re.search(r'\{[\s\S]*\}', text)
    if m:
        try:
            return json.loads(m.group(0))
        except json.JSONDecodeError:
            pass

    raise ValueError(f"Failed to parse AI response as JSON. Response preview: {text[:500]}")


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
