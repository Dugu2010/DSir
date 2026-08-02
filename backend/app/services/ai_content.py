"""AI content extraction and course generation - multi-provider edition.

Supports: Gemini (free), OpenAI, NVIDIA Nemotron, Groq, DeepSeek, OpenRouter.
"""
import base64, json, io, re, time
import httpx, structlog
from typing import Optional
from app.config import get_settings

settings = get_settings()
logger = structlog.get_logger()


def _sample_text(raw_text: str, max_chars: int = 8000) -> str:
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
    return head + '\n\n[...]\n\n' + sample + '\n\n[...]\n\n' + tail


def _call_text_llm(prompt: str, max_tokens: int = 4096) -> str:
    provider = settings.AI_DEFAULT_PROVIDER.lower()
    if provider == "gemini" and settings.GEMINI_API_KEY:
        return _call_gemini_text(prompt, max_tokens)
    if provider in ("openai", "anthropic", "nvidia") and settings.OPENAI_API_KEY:
        return _call_openai_text(prompt, max_tokens)
    if settings.GEMINI_API_KEY:
        return _call_gemini_text(prompt, max_tokens)
    if settings.OPENAI_API_KEY:
        return _call_openai_text(prompt, max_tokens)
    raise RuntimeError("No AI provider. Set GEMINI_API_KEY or OPENAI_API_KEY.")


def _call_gemini_text(prompt: str, max_tokens: int = 4096) -> str:
    model = settings.AI_DEFAULT_MODEL or "gemini-2.0-flash"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    body = {"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"temperature": 0.2, "maxOutputTokens": max_tokens}, "safetySettings": [{"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"}, {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"}, {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"}, {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}]}
    resp = httpx.post(f"{url}?key={settings.GEMINI_API_KEY}", json=body, timeout=180.0)
    if resp.status_code != 200:
        raise RuntimeError(f"Gemini HTTP {resp.status_code}")
    data = resp.json()
    if not data.get("candidates"):
        raise RuntimeError("Gemini blocked")
    text = "".join(p.get("text", "") for p in data["candidates"][0].get("content", {}).get("parts", []))
    if not text:
        raise RuntimeError("Gemini empty")
    return text


def _call_gemini_multimodal(prompt: str, image: dict, max_tokens: int = 4096) -> str:
    model = settings.AI_DEFAULT_MODEL or "gemini-2.0-flash"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    body = {"contents": [{"parts": [{"inline_data": {"mime_type": image["mime"], "data": image["data"]}}, {"text": prompt}]}], "generationConfig": {"temperature": 0.2, "maxOutputTokens": max_tokens}, "safetySettings": [{"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"}, {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"}, {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"}, {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}]}
    resp = httpx.post(f"{url}?key={settings.GEMINI_API_KEY}", json=body, timeout=180.0)
    if resp.status_code != 200:
        raise RuntimeError(f"Gemini HTTP {resp.status_code}")
    data = resp.json()
    if not data.get("candidates"):
        raise RuntimeError("Gemini blocked")
    text = "".join(p.get("text", "") for p in data["candidates"][0].get("content", {}).get("parts", []))
    if not text:
        raise RuntimeError("Gemini empty")
    return text


def _call_openai_text(prompt: str, max_tokens: int = 4096) -> str:
    base_url = (settings.AI_OPENAI_BASE_URL or "https://api.openai.com/v1").rstrip("/")
    model = settings.AI_DEFAULT_MODEL or "gpt-4o-mini"
    body = {"model": model, "messages": [{"role": "user", "content": prompt}], "max_tokens": max_tokens, "temperature": 0.2}
    for attempt in range(5):
        resp = httpx.post(f"{base_url}/chat/completions", headers={"Authorization": f"Bearer {settings.OPENAI_API_KEY}", "Content-Type": "application/json"}, json=body, timeout=180.0)
        if resp.status_code == 200:
            data = resp.json()
            if not data.get("choices"):
                raise RuntimeError("No choices")
            text = data["choices"][0].get("message", {}).get("content", "")
            if not text:
                raise RuntimeError("Empty response")
            logger.info("openai.ok", model=model, response_len=len(text))
            return text
        if resp.status_code == 429:
            wait = 5.0
            try:
                err = resp.json()
                msg = err.get("error", {}).get("message", "")
                m = re.search(r'try again in ([\d.]+)s', msg)
                if m:
                    wait = float(m.group(1)) + 0.5
            except Exception:
                pass
            wait = wait * (2 ** attempt)
            logger.info("openai.rate_limited", attempt=attempt + 1, wait=round(wait, 1))
            time.sleep(wait)
            continue
        raise RuntimeError(f"HTTP {resp.status_code}: {resp.text[:300]}")
    raise RuntimeError("Failed after 5 retries")


def extract_text(data: bytes, filename: str = "") -> str:
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "txt"
    if ext == "pdf":
        text = _pdf_extract(data)
        if text and len(text) > 100:
            return text
        if not settings.GEMINI_API_KEY:
            raise RuntimeError("Image-based PDF needs GEMINI_API_KEY for OCR")
        return _pdf_ocr(data)
    if ext in ("png", "jpg", "jpeg", "webp", "bmp", "tiff", "gif"):
        if not settings.GEMINI_API_KEY:
            raise RuntimeError("Image OCR needs GEMINI_API_KEY")
        mime = f"image/{ext}" if ext != "jpg" else "image/jpeg"
        return _call_gemini_multimodal("Transcribe all text from this image verbatim.", image={"mime": mime, "data": base64.b64encode(data).decode()})
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
                t = _call_gemini_multimodal("Extract ALL text from this page verbatim.", image={"mime": "image/png", "data": b64}, max_tokens=4096)
                texts.append(t)
            except Exception as e:
                logger.warning("ocr_page_failed", page=i + 1, error=str(e)[:100])
    return "\n\n".join(texts)


def generate_structure_preview(raw_text: str, topic_hint: str = "") -> dict:
    sampled = _sample_text(raw_text, max_chars=8000)
    prompt = f"""Analyze this educational content and create a course outline. Output ONLY valid JSON in this exact structure (fill in the ... values):

{{"course":{{"title":"Course Title","slug":"course-slug","description":"Short description","long_description":"Detailed description","difficulty":"beginner","estimated_duration_minutes":600,"skill_tags":["python"],"learning_objectives":["learn x"]}},"modules":[{{"title":"01. Module Name","slug":"module-slug","description":"Module description","display_order":1,"lessons":[{{"title":"Lesson Title","slug":"lesson-slug","description":"Lesson description","difficulty":"beginner","estimated_duration_minutes":30,"skill_tags":["python"]}}]}}]}}

Rules: 5-8 modules, 2-4 lessons each, hyphenated slugs, cover FULL scope. Output ONLY the JSON object -- no markdown fences, no extra text. Never use three double quotes in a row inside JSON values.

Topic: {topic_hint}
Content (sampled from {len(raw_text)} chars):
{sampled}"""
    logger.info("preview.prompt", total_chars=len(raw_text), sampled_chars=len(sampled))
    resp = _call_text_llm(prompt, max_tokens=8192)
    result = _parse_json(resp)
    logger.info("preview.done", course=result.get("course", {}).get("title"))
    return result


def generate_lesson_content(course_title: str, module_title: str, lesson_title: str) -> dict:
    prompt = f"""You are a JSON API. Output ONLY a raw JSON object, no explanation, no markdown, no reasoning. START with {{ and END with }}. Fields: content_markdown (detailed lesson in markdown, 400-600 words, 2-3 code examples), exercises (array of {{title, description, instructions, starter_code, solution_code, hints, points}}). CRITICAL RULES: Never use triple double quotes. Escape all backslashes. Use single backticks for inline code.

Course: {course_title}
Module: {module_title}
Lesson: {lesson_title}

JSON:"""
    resp = _call_text_llm(prompt, max_tokens=4096)
    return _parse_json(resp)


def ai_edit_lesson(current_content: str, course_title: str, lesson_title: str, edit_instruction: str) -> dict:
    prompt = f"""Edit a programming lesson. Output ONLY valid JSON with content_markdown and exercises. Never use three double quotes in a row.
Course: {course_title}
Lesson: {lesson_title}
CURRENT: {current_content}
EDIT: {edit_instruction}"""
    resp = _call_text_llm(prompt, max_tokens=4096)
    return _parse_json(resp)


def ai_improve_course(course_data: dict) -> dict:
    prompt = f"Improve this course metadata. Output ONLY valid JSON. Course: {json.dumps(course_data)}"
    resp = _call_text_llm(prompt, max_tokens=4096)
    return _parse_json(resp)


def ai_generate_module(course_title: str, course_description: str, existing_modules: list, module_topic: str = "") -> dict:
    existing = "\n".join(f"- {m.get('title', '')}: {m.get('description', '')}" for m in existing_modules)
    topic_line = f"Topic: {module_topic}" if module_topic else "Fill gaps in existing modules"
    prompt = f"Create a module for: {course_title}\nDesc: {course_description}\nExisting: {existing}\n{topic_line}\nOutput ONLY valid JSON. Never use three double quotes in a row."
    resp = _call_text_llm(prompt, max_tokens=4096)
    return _parse_json(resp)


def ai_evaluate_course(course_data: dict) -> dict:
    prompt = f"Evaluate this course quality 1-10. Output ONLY valid JSON. Course: {json.dumps(course_data)}"
    resp = _call_text_llm(prompt, max_tokens=4096)
    return _parse_json(resp)


def ai_regenerate_lesson(course_title: str, module_title: str, lesson_title: str, original_content: str = "", improvement_notes: str = "") -> dict:
    ctx = f"\nPrevious: {original_content[:2000]}" if original_content else ""
    notes = f"\nImprove: {improvement_notes}" if improvement_notes else ""
    prompt = f"Write an EXCEPTIONAL lesson. Output ONLY valid JSON with content_markdown and exercises. CRITICAL: Never use three double quotes in a row. 500-800 words, 2-3 python blocks, 1-2 exercises.\nCourse: {course_title}\nModule: {module_title}\nLesson: {lesson_title}{ctx}{notes}"
    resp = _call_text_llm(prompt, max_tokens=4096)
    return _parse_json(resp)


def _sanitize_json_escapes(text: str) -> str:
    return re.sub(r'\\([^"\\/bfnrtu])', r'\\\\\\1', text)


def _fix_triple_quotes(text: str) -> str:
    """Escape double-quote sequences inside JSON string values.
    LLMs teaching Python often include triple-quote examples in markdown,
    creating unescaped quote sequences that break JSON parsing."""
    out = []
    in_string = False
    escape_next = False
    i = 0
    while i < len(text):
        ch = text[i]
        if not in_string:
            if ch == '"':
                in_string = True
            out.append(ch)
        else:
            if escape_next:
                escape_next = False
                out.append(ch)
            elif ch == '\\':
                escape_next = True
                out.append(ch)
            elif ch == '"' and i + 1 < len(text) and text[i + 1] == '"':
                out.append('\\"')
            else:
                if ch == '"':
                    in_string = False
                out.append(ch)
        i += 1
    return ''.join(out)


def _parse_json(text: str) -> dict:
    text = text.strip()
    # Strip BOM, zero-width spaces, and other invisible unicode junk
    for ch in ('\ufeff', '\u200b', '\u200c', '\u200d', '\u200e', '\u200f', '\u2028', '\u2029'):
        text = text.replace(ch, '')
    if not text:
        raise ValueError("Empty AI response")
    logger.info("parse.start", preview=text[:200])

    def _try_all(t: str):
        for s in (t, _sanitize_json_escapes(t), _fix_triple_quotes(t), _sanitize_json_escapes(_fix_triple_quotes(t))):
            try:
                return json.loads(s)
            except (json.JSONDecodeError, ValueError):
                continue
        return None

    r = _try_all(text)
    if r is not None:
        return r

    _fence_re = r'```(?:json)?[ \t]*\n([\s\S]*?)\n[ \t]*```'
    m = re.search(_fence_re, text)
    if m:
        r = _try_all(m.group(1).strip())
        if r is not None:
            return r

    depth = sp = 0
    start_pos = -1
    for i, ch in enumerate(text):
        if ch == '{':
            if depth == 0:
                start_pos = i
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0 and start_pos >= 0:
                r = _try_all(text[start_pos:i + 1])
                if r is not None:
                    return r
                start_pos = -1

    chunks = []
    depth = sc = 0
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
        r = _try_all(chunk)
        if r is not None:
            return r
        try:
            f = re.sub(r',[ \t]*}', '}', chunk)
            f = re.sub(r',[ \t]*]', ']', f)
            r = _try_all(f)
            if r is not None:
                return r
        except Exception:
            continue

    # Final fallback: try common JSON fixups
    final = text
    for fixup in (
        lambda t: t.replace('True', 'true').replace('False', 'false').replace('None', 'null'),
        lambda t: re.sub(r'\\x[0-9a-fA-F]{2}', '', t),
    ):
        try:
            f = fixup(final)
            return json.loads(f)
        except Exception:
            continue

    logger.error("parse.all_failed", text=text[:3000])
    raise ValueError(f"Parse failed. Preview: {text[:200]}")
