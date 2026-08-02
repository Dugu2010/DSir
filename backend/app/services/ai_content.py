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
    """Smart sample: head 50% + middle 25% + tail 25%."""
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
    prompt = f"""Analyze this educational content and create a course outline. Output ONLY valid JSON, no other text, no markdown fences:

{{"course":{{"title":"...","slug":"...","description":"...","long_description":"...","difficulty":"beginner","estimated_duration_minutes":600,"skill_tags":[...],"learning_objectives":[...]}},"modules":[{{"title":"01. ...","slug":"...","description":"...","display_order":1,"lessons":[{{"title":"...","slug":"...","description":"...","difficulty":"beginner","estimated_duration_minutes":30,"skill_tags":[...],"learning_objectives":[...]}}]}}]}}

Rules: 5-8 modules, 2-4 lessons each, lowercase-hyphenated slugs, cover FULL scope.
Topic: {topic_hint}
Content (sampled from {len(raw_text)} chars):
{sampled}"""
    logger.info("preview.prompt", total_chars=len(raw_text), sampled_chars=len(sampled))
    resp = _call_text_llm(prompt, max_tokens=8192)
    result = _parse_json(resp)
    logger.info("preview.done", course=result.get("course", {}).get("title"))
    return result


def generate_lesson_content(course_title: str, module_title: str, lesson_title: str) -> dict:
    prompt = f"""Write a detailed programming lesson. Output ONLY valid JSON (no markdown fences):

{{"content_markdown":"## Introduction\\n\\nEngaging intro...\\n\\n## Core Concepts\\n\\nExplanation with examples...\\n\\n```python\\n# Working code\\nprint('hello')\\n```\\n\\n## Key Takeaways\\n\\n- Point 1\\n- Point 2\\n\\n## Practice\\n\\nInstructions...","exercises":[{{"title":"Practice: Exercise Name","description":"What to practice","instructions":"Step by step","exercise_type":"code_completion","difficulty":"easy","starter_code":"# Write code here\\ndef solve():\\n    pass","solution_code":"# Solution\\ndef solve():\\n    return True","test_code":"assert solve() == True","hints":[{{"level":1,"content":"Think about..."}}],"points":10}}]}}

Requirements: 400-600 words, 2-3 python blocks, 1-2 exercises, valid JSON, no trailing commas.
Course: {course_title}
Module: {module_title}
Lesson: {lesson_title}"""
    resp = _call_text_llm(prompt, max_tokens=4096)
    return _parse_json(resp)


def ai_edit_lesson(current_content: str, course_title: str, lesson_title: str, edit_instruction: str) -> dict:
    prompt = f"""Edit a programming lesson based on instructions. Output ONLY valid JSON:

{{"content_markdown":"Full updated content with edits applied","exercises":[{{"title":"...","description":"...","instructions":"...","exercise_type":"code_completion","difficulty":"easy","starter_code":"# code\\n","solution_code":"# solution\\n","test_code":"pass","hints":[{{"level":1,"content":"..."}}],"points":10}}]}}

Course: {course_title}
Lesson: {lesson_title}

CURRENT CONTENT:
{current_content}

EDIT INSTRUCTION:
{edit_instruction}

Apply the edit. Keep unchanged parts as-is. Return COMPLETE content."""
    resp = _call_text_llm(prompt, max_tokens=4096)
    return _parse_json(resp)


def ai_improve_course(course_data: dict) -> dict:
    prompt = f"""Improve course metadata. Output ONLY valid JSON:

Current: {json.dumps(course_data)}

Return: {{"title":"...","description":"...","long_description":"...","difficulty":"...","skill_tags":[...],"learning_objectives":[...],"improvements_made":[...],"suggestions":[...]}}"""
    resp = _call_text_llm(prompt, max_tokens=4096)
    return _parse_json(resp)


def ai_generate_module(course_title: str, course_description: str, existing_modules: list, module_topic: str = "") -> dict:
    existing = "\n".join(f"- {m.get('title', '')}: {m.get('description', '')}" for m in existing_modules)
    topic_line = f"Topic: {module_topic}" if module_topic else "Fill gaps in existing modules"
    prompt = f"""Create a module for: {course_title}
Description: {course_description}
Existing: {existing}
{topic_line}

Output ONLY valid JSON: {{"title":"XX. Title","slug":"slug","description":"...","display_order":{len(existing_modules)+1},"lessons":[{{"title":"...","slug":"...","description":"...","difficulty":"beginner","estimated_duration_minutes":30,"skill_tags":[...],"learning_objectives":[...]}}]}}
2-4 lessons, hyphenated slugs."""
    resp = _call_text_llm(prompt, max_tokens=4096)
    return _parse_json(resp)


def ai_evaluate_course(course_data: dict) -> dict:
    prompt = f"""Evaluate course quality honestly. Output ONLY valid JSON:

Course: {json.dumps(course_data)}

Return: {{"quality_score":7.5,"recommendation":"keep","strengths":[...],"weaknesses":[...],"action_suggestions":[...],"should_delete":false,"reasoning":"..."}}
Score 1-10. should_delete=true only if score<4 and unsalvageable."""
    resp = _call_text_llm(prompt, max_tokens=4096)
    return _parse_json(resp)


def ai_regenerate_lesson(course_title: str, module_title: str, lesson_title: str, original_content: str = "", improvement_notes: str = "") -> dict:
    ctx = f"\nPrevious: {original_content[:2000]}" if original_content else ""
    notes = f"\nImprove: {improvement_notes}" if improvement_notes else ""
    prompt = f"""Write an EXCEPTIONAL programming lesson. Output ONLY valid JSON:

{{"content_markdown":"## Introduction\\n\\nEngaging hook...\\n\\n## Core Concepts\\n\\nClear step-by-step...\\n\\n```python\\n# Practical code\\n```\\n\\n## Deep Dive\\n\\nAdvanced insights...\\n\\n## Common Pitfalls\\n\\n- Mistake and fix...\\n\\n## Key Takeaways\\n\\n- Point 1\\n- Point 2\\n\\n## Practice\\n\\nInstructions...","exercises":[{{"title":"Practice: ...","description":"...","instructions":"...","exercise_type":"code_completion","difficulty":"easy","starter_code":"# code\\ndef solve():\\n    pass","solution_code":"# solution\\ndef solve():\\n    return result","test_code":"assert solve() == expected","hints":[{{"level":1,"content":"..."}},{{"level":2,"content":"..."}}],"points":10}}]}}

500-800 words, 2-3 python blocks, Common Pitfalls section, 1-2 exercises, valid JSON.
Course: {course_title}
Module: {module_title}
Lesson: {lesson_title}{ctx}{notes}"""
    resp = _call_text_llm(prompt, max_tokens=4096)
    return _parse_json(resp)


def _sanitize_json_escapes(text: str) -> str:
    return re.sub(r'\\([^"\\/bfnrtu])', r'\\\\\\1', text)


def _parse_json(text: str) -> dict:
    text = text.strip()
    if not text:
        raise ValueError("Empty AI response")
    logger.info("parse.start", preview=text[:200])
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    try:
        return json.loads(_sanitize_json_escapes(text))
    except json.JSONDecodeError:
        pass
    # NB: use byte patterns to avoid double-escaping through JSON transport
    _fence_re = r'```(?:json)?[ \t]*\n([\s\S]*?)\n[ \t]*```'
    m = re.search(_fence_re, text)
    if m:
        inner = m.group(1).strip()
        try:
            return json.loads(inner)
        except json.JSONDecodeError:
            pass
        try:
            return json.loads(_sanitize_json_escapes(inner))
        except json.JSONDecodeError:
            pass
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
                c = text[start_pos:i + 1]
                try:
                    return json.loads(c)
                except json.JSONDecodeError:
                    pass
                try:
                    return json.loads(_sanitize_json_escapes(c))
                except json.JSONDecodeError:
                    pass
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
            f = re.sub(r',[ \t]*}', '}', chunk)
            f = re.sub(r',[ \t]*]', ']', f)
            return json.loads(f)
        except json.JSONDecodeError:
            continue
        try:
            f = re.sub(r',[ \t]*}', '}', chunk)
            f = re.sub(r',[ \t]*]', ']', f)
            return json.loads(_sanitize_json_escapes(f))
        except json.JSONDecodeError:
            continue
    logger.error("parse.all_failed", text=text[:3000])
    raise ValueError(f"Parse failed. Preview: {text[:200]}")
