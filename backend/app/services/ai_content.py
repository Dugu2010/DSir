"""AI content extraction and course generation. Multi-provider."""
import base64, json, io, re, time
import httpx, structlog
from app.config import get_settings

settings = get_settings()
logger = structlog.get_logger()


def ai_provider_available() -> bool:
    """True when at least one AI provider has an API key configured."""
    return bool(settings.GEMINI_API_KEY or settings.OPENAI_API_KEY or settings.ANTHROPIC_API_KEY)


def _sample_text(raw_text: str, max_chars: int = 12000) -> str:
    """Return a representative sample of a (possibly huge) document.

    Spreads the budget across the head, several evenly-spaced middle
    sections, and the tail so a 100-page book still yields a balanced
    course outline instead of just the first few pages."""
    text = raw_text.strip()
    if len(text) <= max_chars:
        return text
    # Split into paragraphs; if the doc has few paragraphs, fall back to chars.
    paragraphs = [p.strip() for p in re.split(r'\n\s*\n', text) if p.strip()]
    if len(paragraphs) < 20:
        # Character-level spread sampling.
        parts = []
        n = 5
        step = len(text) // n
        for i in range(n):
            parts.append(text[i * step: i * step + max_chars // n])
        return '\n\n[...]\n\n'.join(parts)
    head = '\n\n'.join(paragraphs[:3])
    tail = '\n\n'.join(paragraphs[-2:])
    mid_paragraphs = paragraphs[3:-2]
    n_sections = 4
    budget = max_chars - len(head) - len(tail) - 200
    per_section = max(400, budget // n_sections)
    sections = []
    step = max(1, len(mid_paragraphs) // n_sections)
    for i in range(n_sections):
        start = i * step
        chunk = mid_paragraphs[start:start + step]
        section = '\n\n'.join(chunk)
        if len(section) > per_section:
            section = section[:per_section]
        sections.append(section)
    return head + '\n\n[...]\n\n' + '\n\n[...]\n\n'.join(sections) + '\n\n[...]\n\n' + tail


def _chunk_text(raw_text: str, chunk_size: int = 6000, overlap: int = 500) -> list[str]:
    """Split a document into overlapping text chunks for grounded generation."""
    text = raw_text.strip()
    if len(text) <= chunk_size:
        return [text] if text else []
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(text):
            break
        # Prefer to break on a paragraph boundary within the overlap window.
        next_start = end - overlap
        boundary = text.rfind('\n\n', start + 1, next_start)
        if boundary > start + chunk_size // 2:
            next_start = boundary
        start = next_start
    return chunks


_STOPWORDS = {
    'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'any', 'can', 'had', 'her',
    'was', 'one', 'our', 'out', 'own', 'she', 'him', 'his', 'they', 'them', 'their',
    'what', 'when', 'where', 'which', 'who', 'whom', 'why', 'how', 'this', 'that',
    'these', 'those', 'with', 'without', 'from', 'into', 'onto', 'about', 'above',
    'below', 'over', 'under', 'again', 'then', 'than', 'too', 'very', 'just', 'only',
    'each', 'both', 'few', 'more', 'most', 'other', 'some', 'such', 'also', 'will',
    'would', 'should', 'could', 'might', 'must', 'shall', 'may', 'been', 'being',
    'have', 'has', 'had', 'does', 'did', 'doing', 'introduction', 'introductionto',
    'chapter', 'section', 'part', 'basic', 'basics', 'fundamentals', 'overview',
    'getting', 'started', 'guide', 'tutorial', 'lesson', 'module', 'course', 'learn',
    'learning', 'example', 'examples', 'data', 'using', 'use', 'used', 'understand',
    'understanding', 'concept', 'concepts', 'key', 'terms', 'summary', 'conclusion',
}


def _keywords(text: str) -> set[str]:
    """Extract meaningful lowercase keywords (3+ chars, no stopwords)."""
    words = re.findall(r'[a-z0-9]{3,}', (text or '').lower())
    return {w for w in words if w not in _STOPWORDS}


def _stem(word: str) -> str:
    """Crude singularization so 'databases' matches 'database', 'queries' matches 'query'."""
    w = word.lower()
    if w.endswith('ies') and len(w) > 4:
        return w[:-3] + 'y'
    if w.endswith('s') and not w.endswith('ss') and not w.endswith('us') and len(w) > 3:
        return w[:-1]
    return w


def _score_text(low: str, topic_words: set[str]) -> int:
    """Count keyword hits using word-boundary, stem-tolerant matching."""
    score = 0
    for w in topic_words:
        stem = _stem(w)
        if len(stem) < 3:
            continue
        pat = re.compile(r'\b' + re.escape(stem) + r'\w*\b')
        score += len(pat.findall(low))
    return score


def _split_sections(text: str) -> list[tuple[str, str]]:
    """Split a document into (heading, body) sections by markdown headings."""
    parts = re.split(r'(?m)^(#{1,6}\s+.+)$', text)
    sections: list[tuple[str, str]] = []
    if parts[0].strip():
        sections.append(('', parts[0]))
    for i in range(1, len(parts), 2):
        heading = parts[i].strip()
        body = parts[i + 1] if i + 1 < len(parts) else ''
        sections.append((heading, body))
    return sections


def find_relevant_excerpt(source_text: str, *topics: str, max_chars: int = 3000) -> str:
    """Return the portion of source_text most relevant to the given topics.

    Prefers heading-delimited sections (so the right chapter of a book is
    returned), falling back to overlapping chunks for unstructured text.
    Keyword scoring is stopword-filtered and stem-tolerant."""
    text = (source_text or '').strip()
    if not text:
        return ''
    if len(text) <= max_chars:
        return text
    topic_words: set[str] = set()
    for t in topics:
        topic_words |= _keywords(t or '')
    if not topic_words:
        return _sample_text(text, max_chars=max_chars)

    sections = _split_sections(text)
    if len(sections) > 1:
        best_text = ''
        best_score = -1
        for heading, body in sections:
            hlow = (heading or '').lower()
            blow = (body or '').lower()
            # Heading words are a much stronger signal than body words.
            score = 3 * _score_text(hlow, topic_words) + _score_text(blow, topic_words)
            if score > best_score:
                best_score = score
                best_text = (heading + '\n\n' + body).strip()
        if best_score > 0 and best_text:
            if len(best_text) <= max_chars:
                return best_text
            return best_text[:max_chars]

    # No headings — fall back to chunk scoring.
    chunks = _chunk_text(text, chunk_size=max_chars, overlap=200)
    best = chunks[0]
    best_score = -1
    for chunk in chunks:
        score = _score_text(chunk.lower(), topic_words)
        if score > best_score:
            best_score = score
            best = chunk
    if best_score <= 0:
        return _sample_text(text, max_chars=max_chars)
    return best[:max_chars]


def _call_text_llm(prompt: str, max_tokens: int = 4096) -> str:
    provider = settings.AI_DEFAULT_PROVIDER.lower()
    if provider == "gemini" and settings.GEMINI_API_KEY: return _call_gemini_text(prompt, max_tokens)
    if provider in ("openai", "anthropic", "nvidia") and settings.OPENAI_API_KEY: return _call_openai_text(prompt, max_tokens)
    if settings.GEMINI_API_KEY: return _call_gemini_text(prompt, max_tokens)
    if settings.OPENAI_API_KEY: return _call_openai_text(prompt, max_tokens)
    raise RuntimeError("No AI provider. Set GEMINI_API_KEY or OPENAI_API_KEY.")


def _call_gemini_text(prompt: str, max_tokens: int = 4096) -> str:
    model = settings.AI_DEFAULT_MODEL or "gemini-2.0-flash"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    body = {"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"temperature": 0.2, "maxOutputTokens": max_tokens}, "safetySettings": [{"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_ONLY_HIGH"}, {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_ONLY_HIGH"}, {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_ONLY_HIGH"}, {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_ONLY_HIGH"}]}
    resp = httpx.post(f"{url}?key={settings.GEMINI_API_KEY}", json=body, timeout=180.0)
    if resp.status_code != 200: raise RuntimeError(f"Gemini HTTP {resp.status_code}")
    data = resp.json()
    if not data.get("candidates"): raise RuntimeError("Gemini blocked")
    text = "".join(p.get("text", "") for p in data["candidates"][0].get("content", {}).get("parts", []))
    if not text: raise RuntimeError("Gemini empty")
    return text


def _call_gemini_multimodal(prompt: str, image: dict, max_tokens: int = 4096) -> str:
    model = settings.AI_DEFAULT_MODEL or "gemini-2.0-flash"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    body = {"contents": [{"parts": [{"inline_data": {"mime_type": image["mime"], "data": image["data"]}}, {"text": prompt}]}], "generationConfig": {"temperature": 0.2, "maxOutputTokens": max_tokens}, "safetySettings": [{"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_ONLY_HIGH"}, {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_ONLY_HIGH"}, {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_ONLY_HIGH"}, {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_ONLY_HIGH"}]}
    resp = httpx.post(f"{url}?key={settings.GEMINI_API_KEY}", json=body, timeout=180.0)
    if resp.status_code != 200: raise RuntimeError(f"Gemini HTTP {resp.status_code}")
    data = resp.json()
    if not data.get("candidates"): raise RuntimeError("Gemini blocked")
    text = "".join(p.get("text", "") for p in data["candidates"][0].get("content", {}).get("parts", []))
    if not text: raise RuntimeError("Gemini empty")
    return text


def _call_openai_text(prompt: str, max_tokens: int = 4096) -> str:
    base_url = (settings.AI_OPENAI_BASE_URL or "https://api.openai.com/v1").rstrip("/")
    model = settings.AI_DEFAULT_MODEL or "gpt-4o-mini"
    body = {"model": model, "messages": [{"role": "user", "content": prompt}], "max_tokens": max_tokens, "temperature": 0.2}
    # NVIDIA's OpenAI-compatible endpoint accepts an extra hint to disable
    # reasoning/thinking output. Only send it to NVIDIA — OpenAI, Groq,
    # DeepSeek, Cloudflare, and OpenRouter reject unknown fields.
    if "nvidia" in base_url:
        body["chat_template_kwargs"] = {"enable_thinking": False}
    for attempt in range(5):
        resp = httpx.post(f"{base_url}/chat/completions", headers={"Authorization": f"Bearer {settings.OPENAI_API_KEY}", "Content-Type": "application/json"}, json=body, timeout=90.0)
        if resp.status_code == 200:
            data = resp.json()
            if not data.get("choices"): raise RuntimeError("No choices")
            text = data["choices"][0].get("message", {}).get("content", "")
            if not text: raise RuntimeError("Empty response")
            logger.info("openai.ok", model=model, response_len=len(text))
            return text
        if resp.status_code == 429:
            wait = 5.0
            try:
                err = resp.json(); msg = err.get("error", {}).get("message", "")
                m = re.search(r'try again in ([\d.]+)s', msg)
                if m: wait = float(m.group(1)) + 0.5
            except Exception: pass
            wait = wait * (2 ** attempt)
            logger.info("openai.rate_limited", attempt=attempt + 1, wait=round(wait, 1))
            time.sleep(wait); continue
        raise RuntimeError(f"HTTP {resp.status_code}: {resp.text[:300]}")
    raise RuntimeError("Failed after 5 retries")


def extract_text(data: bytes, filename: str = "") -> str:
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "txt"
    if ext == "pdf":
        text = _pdf_extract(data)
        if text and len(text) > 100: return text
        if not settings.GEMINI_API_KEY: raise RuntimeError("Image-based PDF needs GEMINI_API_KEY for OCR")
        return _pdf_ocr(data)
    if ext in ("png", "jpg", "jpeg", "webp", "bmp", "tiff", "gif"):
        if not settings.GEMINI_API_KEY: raise RuntimeError("Image OCR needs GEMINI_API_KEY")
        mime = f"image/{ext}" if ext != "jpg" else "image/jpeg"
        return _call_gemini_multimodal("Transcribe all text from this image verbatim.", image={"mime": mime, "data": base64.b64encode(data).decode()})
    try: return data.decode("utf-8")
    except UnicodeDecodeError: return data.decode("latin-1", errors="replace")


def _pdf_extract(data: bytes) -> str:
    for lib in ("pdfplumber", "pypdf2"):
        try:
            if lib == "pdfplumber":
                import pdfplumber, warnings; warnings.filterwarnings("ignore")
                with pdfplumber.open(io.BytesIO(data)) as pdf: pages = [p.extract_text() or "" for p in pdf.pages]
                return "\n\n".join(pages).strip()
            else:
                import PyPDF2
                reader = PyPDF2.PdfReader(io.BytesIO(data))
                return "\n\n".join((p.extract_text() or "") for p in reader.pages).strip()
        except Exception: continue
    return ""


def _pdf_ocr(data: bytes) -> str:
    import pdfplumber, warnings; warnings.filterwarnings("ignore")
    from PIL import Image
    texts = []
    with pdfplumber.open(io.BytesIO(data)) as pdf:
        for i, page in enumerate(pdf.pages[:25]):
            try:
                img = page.to_image(resolution=150); buf = io.BytesIO()
                img.original.save(buf, format="PNG")
                b64 = base64.b64encode(buf.getvalue()).decode()
                t = _call_gemini_multimodal("Extract ALL text from this page verbatim.", image={"mime": "image/png", "data": b64}, max_tokens=4096)
                texts.append(t)
            except Exception as e: logger.warning("ocr_page_failed", page=i + 1, error=str(e)[:100])
    return "\n\n".join(texts)


def generate_structure_preview(raw_text: str, topic_hint: str = "") -> dict:
    sampled = _sample_text(raw_text, max_chars=8000)
    prompt = f"""Analyze this educational content and create a course outline. Output ONLY valid JSON in this exact structure:

{{"course":{{"title":"Course Title","slug":"course-slug","description":"Short description","long_description":"Detailed description","difficulty":"beginner","estimated_duration_minutes":600,"skill_tags":["python"],"learning_objectives":["learn x"]}},"modules":[{{"title":"01. Module","slug":"module-slug","description":"Module description","display_order":1,"lessons":[{{"title":"Lesson","slug":"lesson-slug","description":"Lesson desc","difficulty":"beginner","estimated_duration_minutes":30,"skill_tags":["python"]}}]}}]}}

Rules: 5-8 modules, 2-4 lessons each, lowercase-hyphenated slugs. Output ONLY JSON, no markdown, no reasoning, no triple quotes.

Topic: {topic_hint}
Content ({len(raw_text)} chars):
{sampled}"""
    logger.info("preview.prompt", total_chars=len(raw_text), sampled_chars=len(sampled))
    resp = _call_text_llm(prompt, max_tokens=8192)
    result = _parse_json(resp)
    logger.info("preview.done", course=result.get("course", {}).get("title"))
    return result


def generate_lesson_content(course_title: str, module_title: str, lesson_title: str, source_excerpt: str = "") -> dict:
    ground = ""
    if source_excerpt:
        ground = f"\n\nSOURCE EXCERPT (base the lesson ONLY on this material):\n{source_excerpt[:3000]}"
    prompt = f"""You are a JSON API. Output ONE compact JSON object on a single line (no pretty-printing, no newlines, no markdown, no reasoning). Fields:
- content_markdown: a concise lesson in Markdown (~150-250 words, 1-2 fenced ```python or ```code examples), grounded in the source excerpt when provided.
- exercises: array of exactly 2 objects {{title, description, instructions, starter_code, solution_code, hints, points}}.
- references: array of exactly 2 objects {{title, content}} summarizing key terms/concepts from the source excerpt (title = concept name, content = 1-2 sentence explanation).
Use \\n for newlines inside strings. NEVER use triple double quotes.

Course: {course_title}
Module: {module_title}
Lesson: {lesson_title}{ground}

JSON:"""
    resp = _call_text_llm(prompt, max_tokens=8192)
    return _parse_json(resp)


def generate_module_quiz(course_title: str, module_title: str, lesson_titles: list[str], source_excerpt: str = "") -> dict:
    ground = ""
    if source_excerpt:
        ground = f"\n\nSOURCE EXCERPT (base the questions ONLY on this material):\n{source_excerpt[:3000]}"
    lessons = ", ".join(lesson_titles[:10])
    prompt = f"""You are a JSON API. Output ONE compact JSON object on a single line (no pretty-printing, no newlines, no markdown). Fields:
- title: a quiz title.
- description: one short sentence.
- questions: array of exactly 5 objects {{question, options (array of exactly 4 strings), correct_index (0-3), explanation}}.
Base every question strictly on the source excerpt. Use \\n for newlines inside strings.

Course: {course_title}
Module: {module_title}
Lessons: {lessons}{ground}

JSON:"""
    resp = _call_text_llm(prompt, max_tokens=8192)
    return _parse_json(resp)


def _parse_json(text: str) -> dict:
    text = text.strip()
    for ch in ('\ufeff', '\u200b', '\u200c', '\u200d', '\u200e', '\u200f', '\u2028', '\u2029'): text = text.replace(ch, '')
    if not text: raise ValueError("Empty AI response")
    logger.info("parse.start", preview=text[:200])
    def _try_all(t: str):
        for s in (t, _sanitize(t), _fix_quotes(t), _sanitize(_fix_quotes(t))):
            try: return json.loads(s)
            except (json.JSONDecodeError, ValueError): continue
        return None
    r = _try_all(text)
    if r is not None: return r
    m = re.search(r'```(?:json)?[ \t]*\n([\s\S]*?)\n[ \t]*```', text)
    if m:
        r = _try_all(m.group(1).strip())
        if r is not None: return r
    # String-aware extraction of the top-level JSON object (the first '{' to
    # its matching '}'), ignoring braces that appear inside string values
    # (e.g. code examples like `d = {}` in content_markdown).
    def _extract_top_object(t: str):
        start = t.find('{')
        if start == -1:
            return None
        depth = 0; in_string = False; escape = False
        for i in range(start, len(t)):
            ch = t[i]
            if in_string:
                if escape: escape = False
                elif ch == '\\': escape = True
                elif ch == '"': in_string = False
            else:
                if ch == '"': in_string = True
                elif ch == '{': depth += 1
                elif ch == '}':
                    depth -= 1
                    if depth == 0:
                        return t[start:i + 1]
        return None
    top = _extract_top_object(text)
    if top:
        r = _try_all(top)
        if r is not None: return r
        for fixed in (re.sub(r',[ \t]*}', '}', top), re.sub(r',[ \t]*]', ']', top)):
            r = _try_all(fixed)
            if r is not None: return r
    for fixup in (lambda t: t.replace('True','true').replace('False','false').replace('None','null'), lambda t: re.sub(r'\\x[0-9a-fA-F]{2}','',t)):
        try: return json.loads(fixup(text))
        except Exception: continue
    # Last resort: the response may have been truncated mid-JSON. Salvage the
    # fields we can recover so a single over-long lesson doesn't fail entirely.
    salvaged = _salvage_truncated(text)
    if salvaged.get("content_markdown") or salvaged.get("exercises") or salvaged.get("questions") or salvaged.get("references"):
        logger.warning("parse.salvaged", recovered=set(salvaged.keys()))
        return salvaged
    logger.error("parse.all_failed", text=text[:3000])
    raise ValueError(f"Parse failed. Preview: {text[:200]}")


def _salvage_array(text: str, key: str) -> list | None:
    """Recover complete JSON objects from a (possibly truncated) array field."""
    m = re.search(r'"' + re.escape(key) + r'"\s*:\s*\[', text)
    if not m:
        return None
    items = []
    depth = 0
    obj_start = -1
    in_string = False
    escape = False
    i = m.end()
    while i < len(text):
        ch = text[i]
        if in_string:
            if escape:
                escape = False
            elif ch == '\\':
                escape = True
            elif ch == '"':
                in_string = False
        else:
            if ch == '"':
                in_string = True
            elif ch == '{':
                if depth == 0:
                    obj_start = i
                depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0 and obj_start >= 0:
                    obj = text[obj_start:i + 1]
                    try:
                        items.append(json.loads(obj))
                    except Exception:
                        break
                    obj_start = -1
            elif ch == ']' and depth == 0:
                break
        i += 1
    return items if items else None


def _salvage_truncated(text: str) -> dict:
    result: dict = {}
    m = re.search(r'"content_markdown"\s*:\s*"((?:[^"\\]|\\.)*)"', text, re.DOTALL)
    if m:
        val = m.group(1)
        val = val.replace('\\n', '\n').replace('\\t', '\t').replace('\\"', '"').replace('\\\\', '\\')
        result['content_markdown'] = val
    for key in ('exercises', 'questions', 'references'):
        arr = _salvage_array(text, key)
        if arr:
            result[key] = arr
    return result


def _sanitize(text: str) -> str: return re.sub(r'\\([^"\\/bfnrtu])', r'\\\\\\1', text)


def _fix_quotes(text: str) -> str:
    out = []; in_string = False; escape_next = False; i = 0
    while i < len(text):
        ch = text[i]
        if not in_string:
            if ch == '"': in_string = True
            out.append(ch)
        else:
            if escape_next: escape_next = False; out.append(ch)
            elif ch == '\\': escape_next = True; out.append(ch)
            elif ch == '"' and i + 1 < len(text) and text[i + 1] == '"': out.append('\\"')
            else:
                if ch == '"': in_string = False
                out.append(ch)
        i += 1
    return ''.join(out)
