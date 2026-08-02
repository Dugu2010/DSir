def generate_structure_preview(raw_text: str, topic_hint: str = "") -> dict:
    sampled = _sample_text(raw_text, max_chars=8000)
    prompt = f"""Analyze this educational content and create a course outline. Output ONLY valid JSON in this exact structure:

{{"course":{{"title":"...","slug":"...","description":"...","long_description":"...","difficulty":"beginner","estimated_duration_minutes":600,"skill_tags":[...],"learning_objectives":[...]}},"modules":[{{"title":"01. Module","slug":"module-slug","description":"...","display_order":1,"lessons":[{{"title":"Lesson Title","slug":"lesson-slug","description":"...","difficulty":"beginner","estimated_duration_minutes":30,"skill_tags":[...]}}]}}]}}

Rules: 5-8 modules, 2-4 lessons each, hyphenated slugs, cover FULL scope. IMPORTANT: Never use three double quotes in a row inside JSON values.

Topic: {topic_hint}
Content (sampled from {len(raw_text)} chars):
{sampled}"""
    logger.info("preview.prompt", total_chars=len(raw_text), sampled_chars=len(sampled))
    resp = _call_text_llm(prompt, max_tokens=8192)
    result = _parse_json(resp)
    logger.info("preview.done", course=result.get("course", {}).get("title"))
    return result