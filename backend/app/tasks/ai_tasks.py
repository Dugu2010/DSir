"""
AI-related background tasks (Celery, optional).
"""
import asyncio
import structlog
from uuid import UUID, uuid4

from app.tasks import celery_app
from app.database import async_session_factory

logger = structlog.get_logger()


async def _persist_lesson_content(db, lesson, content: dict, lesson_title: str) -> dict:
    """Write generated markdown, exercises and references to a lesson."""
    from sqlalchemy import delete
    from app.models import Exercise, ExerciseType, ExerciseDifficulty, LessonResource

    md = content.get("content_markdown", "") or ""
    if not md:
        raise ValueError("AI returned empty lesson content")
    lesson.content = md
    lesson.content_markdown = md

    await db.execute(delete(Exercise).where(Exercise.lesson_id == lesson.id))
    for ei, ex in enumerate(content.get("exercises", [])):
        try:
            et = ExerciseType(ex.get("exercise_type", "code_completion"))
        except ValueError:
            et = ExerciseType.CODE_COMPLETION
        try:
            ed = ExerciseDifficulty(ex.get("difficulty", "easy"))
        except ValueError:
            ed = ExerciseDifficulty.EASY
        db.add(Exercise(
            id=uuid4(),
            lesson_id=lesson.id,
            title=ex.get("title", f"Exercise {ei+1}"),
            description=ex.get("description", ""),
            instructions=ex.get("instructions", ""),
            exercise_type=et,
            difficulty=ed,
            starter_code=ex.get("starter_code", ""),
            solution_code=ex.get("solution_code", ""),
            test_code=ex.get("test_code", ""),
            hints=ex.get("hints", []),
            skill_tags=lesson.skill_tags or [],
            points=ex.get("points", 10),
            display_order=ei + 1,
        ))

    # References (key concepts/terms grounded in the source document).
    await db.execute(delete(LessonResource).where(LessonResource.lesson_id == lesson.id))
    for ri, ref in enumerate(content.get("references", [])):
        title = ref.get("title", "")
        body = ref.get("content", "")
        if not title and not body:
            continue
        db.add(LessonResource(
            id=uuid4(),
            lesson_id=lesson.id,
            title=title or f"Reference {ri+1}",
            resource_type="reference",
            content=body,
            display_order=ri + 1,
        ))

    return {"status": "success", "lesson_id": str(lesson.id),
            "exercises": len(content.get("exercises", [])),
            "references": len(content.get("references", []))}


async def _generate_for_lesson(lesson_id: str, course_title: str, module_title: str, lesson_title: str) -> dict:
    """Load a lesson (+ its course source text), generate grounded content, persist it."""
    from sqlalchemy import select
    from app.models import Lesson, Module, Course
    from app.services.ai_content import generate_lesson_content, find_relevant_excerpt

    async with async_session_factory() as db:
        result = await db.execute(select(Lesson).where(Lesson.id == UUID(lesson_id)))
        lesson = result.scalar_one_or_none()
        if not lesson:
            return {"status": "failure", "lesson_id": lesson_id, "error": "lesson not found"}

        source_text = ""
        mod = await db.get(Module, lesson.module_id)
        if mod is not None and mod.course_id is not None:
            course = await db.get(Course, mod.course_id)
            if course is not None:
                source_text = course.source_text or ""

        excerpt = find_relevant_excerpt(source_text, module_title, lesson_title, max_chars=3000)
        content = await asyncio.to_thread(
            generate_lesson_content, course_title, module_title, lesson_title, excerpt
        )
        out = await _persist_lesson_content(db, lesson, content, lesson_title)
        await db.commit()
        logger.info("ai.lesson.generated", lesson_id=lesson_id,
                    exercises=out.get("exercises"), references=out.get("references"),
                    grounded=bool(excerpt))
        return out


async def _generate_quiz_for_module(module_id: str, course_title: str, module_title: str, lesson_titles: list) -> dict:
    """Generate a quiz for a module, grounded in the course source text."""
    from sqlalchemy import select
    from app.models import Module, Course, Quiz, Question, QuestionOption, QuestionType
    from app.services.ai_content import generate_module_quiz, find_relevant_excerpt

    async with async_session_factory() as db:
        mod = await db.get(Module, UUID(module_id))
        if not mod:
            return {"status": "failure", "module_id": module_id, "error": "module not found"}

        source_text = ""
        if mod.course_id is not None:
            course = await db.get(Course, mod.course_id)
            if course is not None:
                source_text = course.source_text or ""

        excerpt = find_relevant_excerpt(source_text, module_title, *lesson_titles, max_chars=3000)
        quiz_data = await asyncio.to_thread(
            generate_module_quiz, course_title, module_title, list(lesson_titles), excerpt
        )

        questions = quiz_data.get("questions", [])
        if not questions:
            logger.warning("ai.quiz.empty", module_id=module_id)
            return {"status": "failure", "module_id": module_id, "error": "no questions generated"}

        quiz = Quiz(
            id=uuid4(),
            module_id=mod.id,
            course_id=mod.course_id,
            title=quiz_data.get("title", f"{module_title} Quiz"),
            description=quiz_data.get("description", ""),
            passing_score=70,
            question_count=len(questions),
            display_order=mod.display_order,
        )
        db.add(quiz)
        await db.flush()

        for qi, q in enumerate(questions):
            opts = q.get("options", [])
            correct = q.get("correct_index", 0)
            if not isinstance(correct, int) or not (0 <= correct < len(opts)):
                correct = 0
            question = Question(
                id=uuid4(),
                quiz_id=quiz.id,
                question_type=QuestionType.SINGLE_CHOICE,
                content=q.get("question", ""),
                explanation=q.get("explanation", ""),
                points=1,
                display_order=qi + 1,
            )
            db.add(question)
            await db.flush()
            for oi, opt in enumerate(opts):
                db.add(QuestionOption(
                    id=uuid4(),
                    question_id=question.id,
                    content=opt,
                    is_correct=(oi == correct),
                    display_order=oi,
                ))
        await db.commit()
        logger.info("ai.quiz.generated", module_id=module_id, questions=len(questions), grounded=bool(excerpt))
        return {"status": "success", "module_id": module_id, "quiz_id": str(quiz.id), "questions": len(questions)}


def generate_lesson_content_sync(lesson_id: str, course_title: str, module_title: str, lesson_title: str) -> dict:
    """Synchronous wrapper (for Celery). Persists grounded AI lesson content."""
    return asyncio.run(_generate_for_lesson(lesson_id, course_title, module_title, lesson_title))


async def generate_lesson_content_inline(lesson_id: str, course_title: str, module_title: str, lesson_title: str) -> dict:
    """Generate + persist lesson content in-process (no Celery worker needed)."""
    try:
        return await _generate_for_lesson(lesson_id, course_title, module_title, lesson_title)
    except Exception as e:
        logger.error("ai.inline.failure", lesson_id=lesson_id, error=str(e)[:200])
        try:
            from sqlalchemy import select
            from app.models import Lesson
            async with async_session_factory() as db:
                result = await db.execute(select(Lesson).where(Lesson.id == UUID(lesson_id)))
                lesson = result.scalar_one_or_none()
                if lesson:
                    lesson.content_markdown = f"# {lesson_title}\n\nContent generation failed: {str(e)[:200]}"
                    lesson.content = lesson.content_markdown
                    await db.commit()
        except Exception:
            pass
        return {"status": "failure", "lesson_id": lesson_id, "error": str(e)[:200]}


async def generate_module_quiz_inline(module_id: str, course_title: str, module_title: str, lesson_titles: list) -> dict:
    """Generate + persist a module quiz in-process."""
    try:
        return await _generate_quiz_for_module(module_id, course_title, module_title, lesson_titles)
    except Exception as e:
        logger.error("ai.quiz.failure", module_id=module_id, error=str(e)[:200])
        return {"status": "failure", "module_id": module_id, "error": str(e)[:200]}


if celery_app is not None:

    @celery_app.task(bind=True, max_retries=3)
    def generate_lesson_content_task(self, lesson_id: str, course_title: str, module_title: str, lesson_title: str):
        """Generate AI content for a lesson and persist it."""
        try:
            result = generate_lesson_content_sync(lesson_id, course_title, module_title, lesson_title)
            logger.info("ai.task.success", task="generate_lesson_content", lesson_id=lesson_id)
            return result
        except Exception as exc:
            logger.error("ai.task.failure", task="generate_lesson_content", lesson_id=lesson_id, error=str(exc))
            if self.request.retries < self.max_retries:
                raise self.retry(countdown=60 * (self.request.retries + 1), exc=exc)
            return {"status": "failure", "lesson_id": lesson_id, "error": str(exc)}

    @celery_app.task(bind=True)
    def generate_course_structure_task(self, topic: str, outline: str = ""):
        """Generate course structure from a topic."""
        from app.services.ai_content import generate_structure_preview
        try:
            structure = generate_structure_preview(outline, topic)
            logger.info("ai.task.success", task="generate_course_structure", topic=topic)
            return {"status": "success", "topic": topic, "structure": structure}
        except Exception as exc:
            logger.error("ai.task.failure", task="generate_course_structure", topic=topic, error=str(exc))
            return {"status": "failure", "topic": topic, "error": str(exc)}
