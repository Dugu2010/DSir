"""Seed the DSir Python curriculum idempotently.

Run with::

    python -m app.seed_curriculum

Design rules
------------
* Content is upserted by stable natural keys (course slug, module slug,
  lesson slug, lesson + exercise title, module + quiz title, project title).
* Lessons marked ``preserve_content`` keep substantive existing content. This
  lets the original interactive first lesson survive a migration.
* Nothing is deleted from user-facing tables. Existing submissions, quiz
  attempts, lesson progress, bookmarks, and enrollments are never touched.
* The legacy duplicate course (slug ``python``) is archived, not deleted. Its
  rich foundation module is adopted by the canonical course first so existing
  lesson IDs and progress remain valid.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone

from sqlalchemy import select

from app.content import COURSE_META
from app.content.modules import MODULES
from app.database import async_session_factory
from app.models import (
    ContentStatus,
    Course,
    DifficultyLevel,
    Exercise,
    ExerciseDifficulty,
    ExerciseType,
    Lesson,
    LessonResource,
    Module,
    Project,
    Question,
    QuestionOption,
    QuestionType,
    Quiz,
)

CANONICAL_COURSE_SLUG = "python-programming"
LEGACY_COURSE_SLUG = "python"
LEGACY_MODULE_SLUG = "python-foundations"

PLACEHOLDER_MARKERS = (
    "Content not available",
    "content from handbook",
    "String content from handbook",
)

# Modules created by the old placeholder seed. They are soft-archived (never
# deleted) so a migration does not destroy rows or foreign-key history.
LEGACY_MODULE_SLUGS = {
    "python-basics",
    "strings",
    "lists-tuples",
    "dicts-sets",
    "control-flow",
    "functions",
    "file-io",
    "oop-basics",
    "oop-advanced",
    "advanced-python",
    "projects",
}


def _is_placeholder(content: str | None) -> bool:
    if not content:
        return True
    if len(content.strip()) < 600:
        return True
    return any(marker in content for marker in PLACEHOLDER_MARKERS)


def _difficulty(value: str) -> DifficultyLevel:
    try:
        return DifficultyLevel(value)
    except ValueError:
        return DifficultyLevel.BEGINNER


def _exercise_difficulty(value: str) -> ExerciseDifficulty:
    try:
        return ExerciseDifficulty(value)
    except ValueError:
        return ExerciseDifficulty.MEDIUM


def _exercise_type(value: str) -> ExerciseType:
    try:
        return ExerciseType(value)
    except ValueError:
        return ExerciseType.CODE_COMPLETION


async def _adopt_legacy_foundation(db, course: Course) -> bool:
    """Move the original rich foundation module into the canonical course.

    This preserves lesson IDs, exercises, and any progress attached to them.
    Returns True when a move happened.
    """
    legacy_course = (
        await db.execute(select(Course).where(Course.slug == LEGACY_COURSE_SLUG))
    ).scalar_one_or_none()
    if legacy_course is None or legacy_course.id == course.id:
        return False

    existing = (
        await db.execute(
            select(Module).where(
                Module.course_id == course.id,
                Module.slug == LEGACY_MODULE_SLUG,
            )
        )
    ).scalar_one_or_none()
    if existing is not None:
        return False

    legacy_module = (
        await db.execute(
            select(Module).where(
                Module.course_id == legacy_course.id,
                Module.slug == LEGACY_MODULE_SLUG,
            )
        )
    ).scalar_one_or_none()
    if legacy_module is None:
        return False

    legacy_module.course_id = course.id
    legacy_module.display_order = 1
    await db.flush()

    # Exercises attached to the adopted lessons now belong to the canonical course.
    lessons = (
        await db.execute(select(Lesson).where(Lesson.module_id == legacy_module.id))
    ).scalars().all()
    for lesson in lessons:
        rows = (
            await db.execute(select(Exercise).where(Exercise.lesson_id == lesson.id))
        ).scalars().all()
        for exercise in rows:
            exercise.course_id = course.id

    # Archive, never delete, the now-empty legacy course.
    legacy_course.status = ContentStatus.ARCHIVED
    legacy_course.is_featured = False
    print(f"  adopted legacy module and archived course '{legacy_course.slug}'")
    return True


async def _archive_legacy_modules(db, course: Course) -> int:
    """Soft-archive only the known placeholder modules from the old seed."""
    archived = 0
    for slug in LEGACY_MODULE_SLUGS:
        module = (
            await db.execute(
                select(Module).where(
                    Module.course_id == course.id,
                    Module.slug == slug,
                    Module.deleted_at.is_(None),
                )
            )
        ).scalar_one_or_none()
        if module is None:
            continue
        module.deleted_at = datetime.now(timezone.utc)
        lessons = (
            await db.execute(select(Lesson).where(Lesson.module_id == module.id))
        ).scalars().all()
        for lesson in lessons:
            lesson.deleted_at = module.deleted_at
            exercises = (
                await db.execute(select(Exercise).where(Exercise.lesson_id == lesson.id))
            ).scalars().all()
            for exercise in exercises:
                exercise.deleted_at = module.deleted_at
        archived += 1
    return archived


async def _upsert_resources(db, lesson: Lesson, resources: list[dict]) -> None:
    existing = (
        await db.execute(select(LessonResource).where(LessonResource.lesson_id == lesson.id))
    ).scalars().all()
    by_url = {row.url: row for row in existing if row.url}
    for order, resource in enumerate(resources):
        row = by_url.get(resource["url"])
        if row is None:
            db.add(
                LessonResource(
                    lesson_id=lesson.id,
                    title=resource["title"],
                    resource_type=resource.get("resource_type", "reference"),
                    url=resource["url"],
                    display_order=order,
                )
            )
        else:
            row.title = resource["title"]
            row.resource_type = resource.get("resource_type", "reference")
            row.display_order = order


async def _upsert_exercises(
    db, course: Course, lesson: Lesson, exercises: list[dict]
) -> tuple[int, int]:
    created = updated = 0
    existing = (
        await db.execute(select(Exercise).where(Exercise.lesson_id == lesson.id))
    ).scalars().all()
    by_title = {row.title: row for row in existing}

    for order, payload in enumerate(exercises):
        row = by_title.get(payload["title"])
        values = dict(
            course_id=course.id,
            lesson_id=lesson.id,
            description=payload["description"],
            instructions=payload["instructions"],
            language="python",
            exercise_type=_exercise_type(payload["type"]),
            difficulty=_exercise_difficulty(payload["difficulty"]),
            starter_code=payload.get("starter", ""),
            solution_code=payload["solution"],
            test_code=payload.get("tests", ""),
            hints=list(payload.get("hints") or []),
            skill_tags=list(payload.get("tags") or []),
            estimated_duration_minutes=payload.get("minutes"),
            points=payload.get("points", 10),
            display_order=order,
            deleted_at=None,
        )
        if row is None:
            db.add(Exercise(title=payload["title"], **values))
            created += 1
        else:
            for key, value in values.items():
                setattr(row, key, value)
            updated += 1
    return created, updated


async def _upsert_quiz(db, course: Course, module: Module, payload: dict | None) -> None:
    if not payload:
        return
    quiz = (
        await db.execute(
            select(Quiz).where(
                Quiz.module_id == module.id,
                Quiz.title == payload["title"],
            )
        )
    ).scalar_one_or_none()
    if quiz is None:
        quiz = Quiz(
            module_id=module.id,
            course_id=course.id,
            title=payload["title"],
            description=payload.get("description"),
            passing_score=payload.get("passing_score", 70),
            max_attempts=payload.get("max_attempts", 3),
            question_count=0,
            display_order=1,
        )
        db.add(quiz)
        await db.flush()

    quiz.course_id = course.id
    quiz.description = payload.get("description")
    quiz.passing_score = payload.get("passing_score", 70)
    quiz.max_attempts = payload.get("max_attempts", 3)

    desired = [(item["content"], item) for item in payload["questions"]]
    current = (
        await db.execute(select(Question).where(Question.quiz_id == quiz.id))
    ).scalars().all()
    by_content = {row.content: row for row in current}

    for order, (content, item) in enumerate(desired):
        question = by_content.get(content)
        if question is None:
            question = Question(
                quiz_id=quiz.id,
                question_type=QuestionType.MULTIPLE_CHOICE,
                content=content,
            )
            db.add(question)
            await db.flush()
        question.explanation = item.get("explanation")
        question.points = 1
        question.display_order = order

        existing_options = (
            await db.execute(
                select(QuestionOption).where(QuestionOption.question_id == question.id)
            )
        ).scalars().all()
        option_by_content = {row.content: row for row in existing_options}
        keep = set()
        # Rotate option order deterministically so the correct answer is not
        # always the first button. Authors naturally write the right answer
        # first; shipping that order lets learners game every quiz.
        options = list(item["options"])
        shift = (order + 1) % len(options) if options else 0
        rotated = options[shift:] + options[:shift]
        for option_order, (label, is_correct) in enumerate(rotated):
            option = option_by_content.get(label)
            if option is None:
                option = QuestionOption(
                    question_id=question.id,
                    content=label,
                )
                db.add(option)
            option.is_correct = bool(is_correct)
            option.display_order = option_order
            keep.add(label)
        # Only remove options that are not part of the authored question.
        for option in existing_options:
            if option.content not in keep:
                await db.delete(option)

    quiz.question_count = len(desired)


async def _upsert_projects(db, course: Course, module: Module, slug: str, projects: list[dict], order: int) -> None:
    for payload in projects:
        project = (
            await db.execute(
                select(Project).where(
                    Project.course_id == course.id,
                    Project.title == payload["title"],
                )
            )
        ).scalar_one_or_none()
        values = dict(
            course_id=course.id,
            module_id=module.id,
            description=payload["description"],
            requirements=payload["requirements"],
            difficulty=_exercise_difficulty(payload.get("difficulty", "medium")),
            is_capstone=bool(payload.get("is_capstone", False)),
            estimated_duration_hours=payload.get("estimated_duration_hours"),
            skill_tags=list(payload.get("skill_tags") or []),
            starter_files=payload.get("starter_files") or {},
            rubric=payload.get("rubric") or [],
        )
        if project is None:
            db.add(Project(title=payload["title"], **values))
        else:
            for key, value in values.items():
                setattr(project, key, value)


async def seed_curriculum() -> None:
    now = datetime.now(timezone.utc)
    async with async_session_factory() as db:
        course = (
            await db.execute(
                select(Course).where(Course.slug == CANONICAL_COURSE_SLUG)
            )
        ).scalar_one_or_none()
        if course is None:
            # description is NOT NULL, so it must be present before the flush
            # that assigns the course id used by modules and lessons.
            course = Course(
                slug=CANONICAL_COURSE_SLUG,
                title=COURSE_META["title"],
                description=COURSE_META["description"],
            )
            db.add(course)
            await db.flush()

        course.title = COURSE_META["title"]
        course.description = COURSE_META["description"]
        course.long_description = COURSE_META["long_description"]
        course.difficulty = DifficultyLevel.BEGINNER
        course.learning_objectives = list(COURSE_META["learning_objectives"])
        course.prerequisites = list(COURSE_META["prerequisites"])
        course.skill_tags = list(COURSE_META["skill_tags"])
        course.estimated_duration_minutes = COURSE_META["estimated_duration_minutes"]
        course.language = "python"
        course.status = ContentStatus.PUBLISHED
        course.is_featured = True
        course.is_free = True
        course.source_text = COURSE_META["sources"]
        course.published_at = course.published_at or now
        await db.flush()

        await _adopt_legacy_foundation(db, course)

        modules_created = modules_updated = 0
        lessons_created = lessons_updated = 0
        exercises_created = exercises_updated = 0
        projects_created = 0

        for module_order, module_payload in enumerate(MODULES, start=1):
            module = (
                await db.execute(
                    select(Module).where(
                        Module.course_id == course.id,
                        Module.slug == module_payload["slug"],
                    )
                )
            ).scalar_one_or_none()
            module_values = dict(
                title=module_payload["title"],
                description=module_payload["description"],
                learning_objectives=list(module_payload["objectives"]),
                display_order=module_order,
                estimated_duration_minutes=module_payload["estimated_duration_minutes"],
                deleted_at=None,
            )
            if module is None:
                module = Module(
                    course_id=course.id,
                    slug=module_payload["slug"],
                    **module_values,
                )
                db.add(module)
                await db.flush()
                modules_created += 1
            else:
                for key, value in module_values.items():
                    setattr(module, key, value)
                modules_updated += 1

            lesson_count = 0
            for lesson_order, lesson_payload in enumerate(
                module_payload["lessons"], start=1
            ):
                lesson = (
                    await db.execute(
                        select(Lesson).where(
                            Lesson.module_id == module.id,
                            Lesson.slug == lesson_payload["slug"],
                        )
                    )
                ).scalar_one_or_none()
                lesson_values = dict(
                    title=lesson_payload["title"],
                    description=lesson_payload["description"],
                    learning_objectives=list(lesson_payload["objectives"]),
                    difficulty=_difficulty(lesson_payload["difficulty"]),
                    estimated_duration_minutes=lesson_payload["minutes"],
                    display_order=lesson_order,
                    skill_tags=list(lesson_payload["tags"]),
                    status=ContentStatus.PUBLISHED,
                    deleted_at=None,
                )
                if lesson is None:
                    lesson = Lesson(
                        module_id=module.id,
                        slug=lesson_payload["slug"],
                        content=lesson_payload["content"],
                        content_markdown=lesson_payload["content"],
                        published_at=now,
                        **lesson_values,
                    )
                    db.add(lesson)
                    await db.flush()
                    lessons_created += 1
                else:
                    for key, value in lesson_values.items():
                        setattr(lesson, key, value)
                    preserve = lesson_payload.get("preserve_content") and not _is_placeholder(
                        lesson.content
                    )
                    if not preserve:
                        lesson.content = lesson_payload["content"]
                        lesson.content_markdown = lesson_payload["content"]
                    lesson.published_at = lesson.published_at or now
                    lessons_updated += 1

                lesson_count += 1
                await _upsert_resources(db, lesson, lesson_payload["resources"])
                created, updated = await _upsert_exercises(
                    db, course, lesson, lesson_payload["exercises"]
                )
                exercises_created += created
                exercises_updated += updated

            module.lesson_count = lesson_count
            await _upsert_quiz(db, course, module, module_payload.get("quiz"))
            await _upsert_projects(
                db,
                course,
                module,
                module_payload["slug"],
                module_payload.get("projects") or [],
                module_order,
            )
            projects_created += len(module_payload.get("projects") or [])

        archived_modules = await _archive_legacy_modules(db, course)
        await db.flush()

        # Keep the catalogue counters truthful.
        module_rows = (
            await db.execute(
                select(Module).where(
                    Module.course_id == course.id,
                    Module.deleted_at.is_(None),
                )
            )
        ).scalars().all()
        lesson_rows = (
            await db.execute(
                select(Lesson).join(Module).where(
                    Module.course_id == course.id,
                    Lesson.deleted_at.is_(None),
                )
            )
        ).scalars().all()
        course.module_count = len(module_rows)
        course.lesson_count = len(lesson_rows)

        await db.commit()

        total_exercises = (
            await db.execute(
                select(Exercise).where(
                    Exercise.course_id == course.id,
                    Exercise.deleted_at.is_(None),
                )
            )
        ).scalars().all()
        total_quizzes = (
            await db.execute(select(Quiz).where(Quiz.course_id == course.id))
        ).scalars().all()
        total_projects = (
            await db.execute(select(Project).where(Project.course_id == course.id))
        ).scalars().all()

        print("Curriculum seeded:")
        print(f"  course:     {course.title} ({course.slug})")
        print(f"  modules:    {len(module_rows)} ({modules_created} created, {modules_updated} updated)")
        print(f"  lessons:    {len(lesson_rows)} ({lessons_created} created, {lessons_updated} updated)")
        print(f"  exercises:  {len(total_exercises)} ({exercises_created} created, {exercises_updated} updated)")
        print(f"  quizzes:    {len(total_quizzes)} (module assessments)")
        print(f"  projects:   {len(total_projects)} ({projects_created} authored)")
        if archived_modules:
            print(f"  archived:   {archived_modules} legacy placeholder modules (rows preserved)")


if __name__ == "__main__":
    asyncio.run(seed_curriculum())
