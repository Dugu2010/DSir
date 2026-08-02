"""AI content extraction and course generation - multi-provider edition."""
import base64, json, io, re, time
import httpx, structlog
from app.config import get_settings

settings = get_settings()
logger = structlog.get_logger()

def _sample_text(raw_text, max_chars=8000):
    if len(raw_text) <= max_chars: return raw_text
    head_size = max_chars // 2; tail_size = max_chars // 4
    sample_size = max_chars - head_size - tail_size
    head = raw_text[:head_size]; tail = raw_text[-tail_size:]
    middle = raw_text[head_size:-tail_size]
    paragraphs = [p.strip() for p in middle.split('\n\n') if p.strip()]
    if len(paragraphs) <= 3:
        sample = middle[:sample_size]
    else:
        step = max(1, len(paragraphs) // 5)
        sample = '\n\n'.join(paragraphs[::step][:8])
        if len(sample) > sample_size: sample = sample[:sample_size]
    return head + '\n\n[...]\n\n' + sample + '\n\n[...]\n\n' + tail

def _call_text_llm(prompt, max_tokens=4096):
    p = settings.AI_DEFAULT_PROVIDER.lower()
    if p == "gemini" and settings.GEMINI_API_KEY: return _call_gemini_text(prompt, max_tokens)
    if p in ("openai", "anthropic", "nvidia") and settings.OPENAI_API_KEY: return _call_openai_text(prompt, max_tokens)
    if settings.GEMINI_API_KEY: return _call_gemini_text(prompt, max_tokens)
    if settings.OPENAI_API_KEY: return _call_openai_text(prompt, max_tokens)
    raise RuntimeError("No AI provider configured")

def _call_gemini_text(prompt, max_tokens=4096):
    model = settings.AI_DEFAULT_MODEL or "gemini-2.0-flash"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    body = {"contents":[{"parts":[{"text":prompt}]}],"generationConfig":{"temperature":0.2,"maxOutputTokens":max_tokens},"safetySettings":[{"category":"HARM_CATEGORY_HARASSMENT","threshold":"BLOCK_NONE"},{"category":"HARM_CATEGORY_HATE_SPEECH","threshold":"BLOCK_NONE"},{"category":"HARM_CATEGORY_SEXUALLY_EXPLICIT","threshold":"BLOCK_NONE"},{"category":"HARM_CATEGORY_DANGEROUS_CONTENT","threshold":"BLOCK_NONE"}]}
    resp = httpx.post(f"{url}?key={settings.GEMINI_API_KEY}", json=body, timeout=180.0)
    if resp.status_code != 200: raise RuntimeError(f"Gemini HTTP {resp.status_code}")
    data = resp.json()
    if not data.get("candidates"): raise RuntimeError("Gemini blocked")
    return "".join(p.get("text","") for p in data["candidates"][0].get("content",{}).get("parts",[]))

def _call_gemini_multimodal(prompt, image, max_tokens=4096):
    model = settings.AI_DEFAULT_MODEL or "gemini-2.0-flash"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    body = {"contents":[{"parts":[{"inline_data":{"mime_type":image["mime"],"data":image["data"]}},{"text":prompt}]}],"generationConfig":{"temperature":0.2,"maxOutputTokens":max_tokens},"safetySettings":[{"category":"HARM_CATEGORY_HARASSMENT","threshold":"BLOCK_NONE"},{"category":"HARM_CATEGORY_HATE_SPEECH","threshold":"BLOCK_NONE"},{"category":"HARM_CATEGORY_SEXUALLY_EXPLICIT","threshold":"BLOCK_NONE"},{"category":"HARM_CATEGORY_DANGEROUS_CONTENT","threshold":"BLOCK_NONE"}]}
    resp = httpx.post(f"{url}?key={settings.GEMINI_API_KEY}", json=body, timeout=180.0)
    if resp.status_code != 200: raise RuntimeError(f"Gemini HTTP {resp.status_code}")
    data = resp.json()
    if not data.get("candidates"): raise RuntimeError("Gemini blocked")
    return "".join(p.get("text","") for p in data["candidates"][0].get("content",{}).get("parts",[]))

def _call_openai_text(prompt, max_tokens=4096):
    base_url = (settings.AI_OPENAI_BASE_URL or "https://api.openai.com/v1").rstrip("/")
    model = settings.AI_DEFAULT_MODEL or "gpt-4o-mini"
    body = {"model":model,"messages":[{"role":"user","content":prompt}],"max_tokens":max_tokens,"temperature":0.2}
    for attempt in range(5):
        resp = httpx.post(f"{base_url}/chat/completions", headers={"Authorization":f"Bearer {settings.OPENAI_API_KEY}","Content-Type":"application/json"}, json=body, timeout=180.0)
        if resp.status_code == 200:
            data = resp.json()
            if not data.get("choices"): raise RuntimeError("No choices")
            text = data["choices"][0].get("message",{}).get("content","")
            logger.info("openai.ok", model=model, response_len=len(text))
            return text
        if resp.status_code == 429:
            wait = 5.0
            try:
                m = re.search(r'try again in ([\d.]+)s', resp.json().get("error",{}).get("message",""))
                if m: wait = float(m.group(1)) + 0.5
            except: pass
            wait *= (2 ** attempt)
            logger.info("openai.rate_limited", attempt=attempt+1, wait=round(wait,1))
            time.sleep(wait)
            continue
        raise RuntimeError(f"HTTP {resp.status_code}: {resp.text[:300]}")
    raise RuntimeError("Failed after 5 retries")

def extract_text(data, filename=""):
    ext = filename.rsplit(".",1)[-1].lower() if "." in filename else "txt"
    if ext == "pdf":
        text = _pdf_extract(data)
        if text and len(text) > 100: return text
        if not settings.GEMINI_API_KEY: raise RuntimeError("Image-based PDF needs GEMINI_API_KEY")
        return _pdf_ocr(data)
    if ext in ("png","jpg","jpeg","webp","bmp","tiff","gif"):
        if not settings.GEMINI_API_KEY: raise RuntimeError("Image OCR needs GEMINI_API_KEY")
        mime = f"image/{ext}" if ext != "jpg" else "image/jpeg"
        return _call_gemini_multimodal("Transcribe all text verbatim.", image={"mime":mime,"data":base64.b64encode(data).decode()})
    try: return data.decode("utf-8")
    except: return data.decode("latin-1", errors="replace")

def _pdf_extract(data):
    for lib in ("pdfplumber","pypdf2"):
        try:
            if lib == "pdfplumber":
                import pdfplumber, warnings; warnings.filterwarnings("ignore")
                with pdfplumber.open(io.BytesIO(data)) as pdf:
                    return "\n\n".join((p.extract_text() or "") for p in pdf.pages).strip()
            else:
                import PyPDF2
                return "\n\n".join((p.extract_text() or "") for p in PyPDF2.PdfReader(io.BytesIO(data)).pages).strip()
        except: continue
    return ""

def _pdf_ocr(data):
    import pdfplumber, warnings; warnings.filterwarnings("ignore")
    from PIL import Image
    texts = []
    with pdfplumber.open(io.BytesIO(data)) as pdf:
        for i, page in enumerate(pdf.pages[:25]):
            try:
                img = page.to_image(resolution=150); buf = io.BytesIO(); img.original.save(buf, format="PNG")
                texts.append(_call_gemini_multimodal("Extract ALL text verbatim.", image={"mime":"image/png","data":base64.b64encode(buf.getvalue()).decode()}, max_tokens=4096))
            except Exception as e: logger.warning("ocr_page_failed", page=i+1, error=str(e)[:100])
    return "\n\n".join(texts)

def generate_structure_preview(raw_text, topic_hint=""):
    sampled = _sample_text(raw_text, max_chars=8000)
    prompt = f"""Analyze this educational content and create a course outline. Output ONLY valid JSON in this EXACT structure (fill in the ... values):

{{"course":{{"title":"Course Title","slug":"course-slug","description":"Short description","long_description":"Detailed description","difficulty":"beginner","estimated_duration_minutes":600,"skill_tags":["python"],"learning_objectives":["learn x"]}},"modules":[{{"title":"01. Module Name","slug":"module-slug","description":"Module description","display_order":1,"lessons":[{{"title":"Lesson Title","slug":"lesson-slug","description":"Lesson description","difficulty":"beginner","estimated_duration_minutes":30,"skill_tags":["python"]}}]}}]}}

Rules: 5-8 modules, 2-4 lessons each, hyphenated slugs, cover FULL scope. Never use three double quotes in a row inside JSON values. Do NOT use markdown fences.

Topic: {topic_hint}
Content (sampled from {len(raw_text)} chars):
{sampled}"""
    logger.info("preview.prompt", total_chars=len(raw_text), sampled_chars=len(sampled))
    resp = _call_text_llm(prompt, max_tokens=8192)
    result = _parse_json(resp)
    logger.info("preview.done", course=result.get("course",{}).get("title"))
    return result

def generate_lesson_content(course_title, module_title, lesson_title):
    prompt = f"""Write a detailed programming lesson. Output ONLY valid JSON with content_markdown and exercises fields.
CRITICAL: Never use three double quotes in a row. Use single backticks. Escape all backslashes properly.
Course: {course_title}\nModule: {module_title}\nLesson: {lesson_title}"""
    return _parse_json(_call_text_llm(prompt, max_tokens=4096))

def ai_edit_lesson(current_content, course_title, lesson_title, edit_instruction):
    prompt = f"Edit a programming lesson. Output ONLY valid JSON. Never use three double quotes in a row.\nCourse: {course_title}\nLesson: {lesson_title}\nCURRENT: {current_content}\nEDIT: {edit_instruction}"
    return _parse_json(_call_text_llm(prompt, max_tokens=4096))

def ai_improve_course(course_data):
    return _parse_json(_call_text_llm(f"Improve course metadata. Output valid JSON. Course: {json.dumps(course_data)}", max_tokens=4096))

def ai_generate_module(course_title, course_description, existing_modules, module_topic=""):
    existing = "\n".join(f"- {m.get('title','')}: {m.get('description','')}" for m in existing_modules)
    topic_line = f"Topic: {module_topic}" if module_topic else "Fill gaps"
    return _parse_json(_call_text_llm(f"Create a module for: {course_title}\nDesc: {course_description}\nExisting: {existing}\n{topic_line}\nValid JSON. No triple double quotes.", max_tokens=4096))

def ai_evaluate_course(course_data):
    return _parse_json(_call_text_llm(f"Evaluate this course 1-10. Valid JSON. Course: {json.dumps(course_data)}", max_tokens=4096))

def ai_regenerate_lesson(course_title, module_title, lesson_title, original_content="", improvement_notes=""):
    ctx = f"\nPrevious: {original_content[:2000]}" if original_content else ""
    notes = f"\nImprove: {improvement_notes}" if improvement_notes else ""
    return _parse_json(_call_text_llm(f"Write an EXCEPTIONAL lesson. Valid JSON. No triple double quotes. 500-800 words, 2-3 python blocks, 1-2 exercises.\nCourse: {course_title}\nModule: {module_title}\nLesson: {lesson_title}{ctx}{notes}", max_tokens=4096))

def _sanitize_json_escapes(text):
    return re.sub(r'\\([^"\\/bfnrtu])', r'\\\\\\1', text)

def _fix_triple_quotes(text):
    """Escape double-quote sequences inside JSON string values (common LLM error with Python docstring examples)."""
    out = []; in_string = False; escape_next = False; i = 0
    while i < len(text):
        ch = text[i]
        if not in_string:
            if ch == '"': in_string = True
            out.append(ch)
        else:
            if escape_next: escape_next = False; out.append(ch)
            elif ch == '\\': escape_next = True; out.append(ch)
            elif ch == '"' and i + 1 < len(text) and text[i+1] == '"': out.append('\\"')
            else:
                if ch == '"': in_string = False
                out.append(ch)
        i += 1
    return ''.join(out)

def _parse_json(text):
    text = text.strip()
    if not text: raise ValueError("Empty AI response")
    logger.info("parse.start", preview=text[:200])

    def _try_all(t):
        for s in (t, _sanitize_json_escapes(t), _fix_triple_quotes(t), _sanitize_json_escapes(_fix_triple_quotes(t))):
            try: return json.loads(s)
            except (json.JSONDecodeError, ValueError): continue
        return None

    r = _try_all(text)
    if r is not None: return r

    m = re.search(r'```(?:json)?[ \t]*\n([\s\S]*?)\n[ \t]*```', text)
    if m:
        r = _try_all(m.group(1).strip())
        if r is not None: return r

    depth = sp = 0; start_pos = -1
    for i, ch in enumerate(text):
        if ch == '{':
            if depth == 0: start_pos = i
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0 and start_pos >= 0:
                r = _try_all(text[start_pos:i+1])
                if r is not None: return r
                start_pos = -1

    chunks = []; depth = sc = 0; start = -1
    for i, ch in enumerate(text):
        if ch == '{':
            if depth == 0: start = i
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0 and start >= 0: chunks.append(text[start:i+1]); start = -1

    for chunk in sorted(chunks, key=len, reverse=True):
        r = _try_all(chunk)
        if r is not None: return r
        try:
            f = re.sub(r',[ \t]*}', '}', chunk); f = re.sub(r',[ \t]*]', ']', f)
            r = _try_all(f)
            if r is not None: return r
        except: continue

    logger.error("parse.all_failed", text=text[:3000])
    raise ValueError(f"Parse failed. Preview: {text[:200]}")
