from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models import (
    Course, Module, Lesson, ContentStatus, LessonProgress,
    RecentlyViewed, Enrollment, Bookmark, UserNote,
    Exercise, Quiz, Question, QuestionOption, Submission,
)
from app.schemas import (
    LessonCreate, LessonUpdate, LessonResponse, LessonProgressUpdate,
    ExerciseResponse, QuizResponse, QuestionResponse,
    CodeSubmission, SubmissionResponse,
)
from app.utils.deps import get_current_active_user, require_teacher, get_optional_user
from app.models import User
from uuid import UUID
from datetime import datetime, timezone

router = APIRouter(prefix="/learn", tags=["Learning"])


# ── Lesson Content ──────────────────────────────────────────────

@router.get("/{course_slug}/{module_slug}/{lesson_slug}", response_model=LessonResponse)
async def get_lesson(
    course_slug: str,
    module_slug: str,
    lesson_slug: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Lesson)
        .join(Module).join(Course)
        .where(
            Course.slug == course_slug,
            Module.slug == module_slug,
            Lesson.slug == lesson_slug,
            Lesson.status == ContentStatus.PUBLISHED,
        )
    )
    lesson = result.scalar_one_or_none()
    if not lesson:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found")

    # Track recently viewed
    existing_rv = await db.execute(
        select(RecentlyViewed).where(
            RecentlyViewed.user_id == current_user.id,
            RecentlyViewed.lesson_id == lesson.id,
        )
    )
    rv = existing_rv.scalar_one_or_none()
    if rv:
        rv.viewed_at = datetime.now(timezone.utc)
    else:
        db.add(RecentlyViewed(user_id=current_user.id, lesson_id=lesson.id))

    # Update enrollment last accessed
    course_result = await db.execute(select(Course).where(Course.slug == course_slug))
    course = course_result.scalar_one_or_none()
    if course:
        enrollment_result = await db.execute(
            select(Enrollment).where(Enrollment.user_id == current_user.id, Enrollment.course_id == course.id)
        )
        enrollment = enrollment_result.scalar_one_or_none()
        if enrollment:
            enrollment.last_accessed_at = datetime.now(timezone.utc)

    return lesson


@router.get("/{course_slug}/{module_slug}/{lesson_slug}/progress")
async def get_lesson_progress(
    course_slug: str,
    module_slug: str,
    lesson_slug: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Lesson)
        .join(Module).join(Course)
        .where(Course.slug == course_slug, Module.slug == module_slug, Lesson.slug == lesson_slug)
    )
    lesson = result.scalar_one_or_none()
    if not lesson:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found")

    progress_result = await db.execute(
        select(LessonProgress).where(
            LessonProgress.user_id == current_user.id,
            LessonProgress.lesson_id == lesson.id,
        )
    )
    progress = progress_result.scalar_one_or_none()
    if not progress:
        return {
            "is_completed": False,
            "time_spent_seconds": 0,
            "completion_percentage": 0,
            "last_position": None,
        }
    return {
        "is_completed": progress.is_completed,
        "time_spent_seconds": progress.time_spent_seconds,
        "completion_percentage": float(progress.completion_percentage),
        "last_position": progress.last_position,
    }


@router.put("/{course_slug}/{module_slug}/{lesson_slug}/progress")
async def update_lesson_progress(
    course_slug: str,
    module_slug: str,
    lesson_slug: str,
    data: LessonProgressUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Lesson)
        .join(Module).join(Course)
        .where(Course.slug == course_slug, Module.slug == module_slug, Lesson.slug == lesson_slug)
    )
    lesson = result.scalar_one_or_none()
    if not lesson:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found")

    progress_result = await db.execute(
        select(LessonProgress).where(
            LessonProgress.user_id == current_user.id,
            LessonProgress.lesson_id == lesson.id,
        )
    )
    progress = progress_result.scalar_one_or_none()

    if not progress:
        progress = LessonProgress(user_id=current_user.id, lesson_id=lesson.id)
        db.add(progress)

    if data.is_completed is not None:
        progress.is_completed = data.is_completed
        if data.is_completed and not progress.completed_at:
            progress.completed_at = datetime.now(timezone.utc)
    if data.time_spent_seconds is not None:
        progress.time_spent_seconds += data.time_spent_seconds
    if data.completion_percentage is not None:
        progress.completion_percentage = data.completion_percentage
    if data.last_position is not None:
        progress.last_position = data.last_position

    # Update course progress
    if progress.is_completed:
        await _recalculate_course_progress(current_user.id, lesson.module_id, db)

    return {"detail": "Progress updated"}


async def _recalculate_course_progress(user_id: UUID, module_id: UUID, db: AsyncSession):
    module_result = await db.execute(select(Module).where(Module.id == module_id))
    module = module_result.scalar_one_or_none()
    if not module:
        return

    # Count total lessons in course
    total_result = await db.execute(
        select(func.count(Lesson.id))
        .join(Module).where(Module.course_id == module.course_id, Lesson.status == ContentStatus.PUBLISHED)
    )
    total_lessons = total_result.scalar() or 0

    # Count completed lessons
    completed_result = await db.execute(
        select(func.count(LessonProgress.id))
        .join(Lesson).join(Module)
        .where(
            Module.course_id == module.course_id,
            LessonProgress.user_id == user_id,
            LessonProgress.is_completed == True,
        )
    )
    completed = completed_result.scalar() or 0

    if total_lessons > 0:
        percentage = (completed / total_lessons) * 100

        enrollment_result = await db.execute(
            select(Enrollment).where(
                Enrollment.user_id == user_id,
                Enrollment.course_id == module.course_id,
            )
        )
        enrollment = enrollment_result.scalar_one_or_none()
        if enrollment:
            enrollment.progress_percentage = percentage
            if percentage >= 100 and not enrollment.is_completed:
                enrollment.is_completed = True
                enrollment.completed_at = datetime.now(timezone.utc)


# ── Recently Viewed ─────────────────────────────────────────────

@router.get("/me/recently-viewed", response_model=list[dict])
async def get_recently_viewed(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(RecentlyViewed, Lesson, Module, Course)
        .join(Lesson, RecentlyViewed.lesson_id == Lesson.id)
        .join(Module, Lesson.module_id == Module.id)
        .join(Course, Module.course_id == Course.id)
        .where(RecentlyViewed.user_id == current_user.id)
        .order_by(RecentlyViewed.viewed_at.desc())
        .limit(20)
    )
    items = []
    for rv, lesson, module, course in result.all():
        items.append({
            "lesson_id": str(lesson.id),
            "lesson_title": lesson.title,
            "lesson_slug": lesson.slug,
            "module_slug": module.slug,
            "course_slug": course.slug,
            "course_title": course.title,
            "viewed_at": rv.viewed_at.isoformat() if rv.viewed_at else None,
        })
    return items


# ── Lesson Exercises ────────────────────────────────────────────

@router.get("/{course_slug}/{module_slug}/{lesson_slug}/exercises", response_model=list[ExerciseResponse])
async def get_lesson_exercises(
    course_slug: str,
    module_slug: str,
    lesson_slug: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Lesson)
        .join(Module).join(Course)
        .where(Course.slug == course_slug, Module.slug == module_slug, Lesson.slug == lesson_slug)
    )
    lesson = result.scalar_one_or_none()
    if not lesson:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found")

    exercises_result = await db.execute(
        select(Exercise)
        .where(Exercise.lesson_id == lesson.id)
        .order_by(Exercise.display_order)
    )
    exercises = exercises_result.scalars().all()

    response = []
    for ex in exercises:
        hints_count = len(ex.hints) if ex.hints else 0
        resp = ExerciseResponse.model_validate(ex)
        resp.hints_count = hints_count
        response.append(resp)

    return response


# ── Lesson Quizzes ──────────────────────────────────────────────

@router.get("/{course_slug}/{module_slug}/{lesson_slug}/quizzes", response_model=list[QuizResponse])
async def get_lesson_quizzes(
    course_slug: str,
    module_slug: str,
    lesson_slug: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Lesson)
        .join(Module).join(Course)
        .where(Course.slug == course_slug, Module.slug == module_slug, Lesson.slug == lesson_slug)
    )
    lesson = result.scalar_one_or_none()
    if not lesson:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found")

    quizzes_result = await db.execute(
        select(Quiz).where(Quiz.lesson_id == lesson.id).order_by(Quiz.display_order)
    )
    return quizzes_result.scalars().all()
