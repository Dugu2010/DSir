from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models import (
    Quiz, Question, QuestionOption, QuizAttempt, Course,
)
from app.schemas import (
    QuizDetailResponse, QuizResultResponse, QuizAttemptStartResponse,
    QuestionResponse, QuestionOptionResponse,
    QuizSubmission, PaginatedResponse, QuizResponse,
)
from app.utils.deps import get_current_active_user
from app.services import gamification
from app.services import quiz_sessions as quiz_rules
from app.models import User
from uuid import UUID
from datetime import datetime, timezone

router = APIRouter(prefix="/quizzes", tags=["Quizzes"])

# Attempt states that have spent one of the learner's attempts. An attempt
# that is still in progress can be resumed and does not count yet.
SPENT_ATTEMPT_STATUSES = ("submitted", "expired")


async def _attempt_usage(
    db: AsyncSession,
    quiz_id: UUID,
    user_id: UUID,
) -> tuple[int, float, int, bool]:
    """Return (attempts spent, best score, best earned points, passed before)."""
    rows = (
        await db.execute(
            select(QuizAttempt.score, QuizAttempt.earned_points, QuizAttempt.passed)
            .where(
                QuizAttempt.quiz_id == quiz_id,
                QuizAttempt.user_id == user_id,
                QuizAttempt.status.in_(SPENT_ATTEMPT_STATUSES),
            )
        )
    ).all()
    used = len(rows)
    best_score = max((float(row.score) for row in rows), default=0.0)
    best_earned = max((int(row.earned_points) for row in rows), default=0)
    already_passed = any(bool(row.passed) for row in rows)
    return used, best_score, best_earned, already_passed


async def _get_quiz_or_404(db: AsyncSession, quiz_id: UUID) -> Quiz:
    quiz = (
        await db.execute(select(Quiz).where(Quiz.id == quiz_id))
    ).scalar_one_or_none()
    if not quiz:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz not found")
    return quiz


def _start_payload(
    attempt: QuizAttempt,
    quiz: Quiz,
    attempts_used: int,
    best_score: float,
) -> QuizAttemptStartResponse:
    started_at = quiz_rules.as_utc(attempt.started_at or datetime.now(timezone.utc))
    return QuizAttemptStartResponse(
        attempt_id=attempt.id,
        started_at=started_at,
        expires_at=quiz_rules.attempt_expires_at(started_at, quiz.time_limit_minutes),
        time_limit_seconds=quiz_rules.time_limit_seconds(quiz.time_limit_minutes),
        attempts_used=attempts_used,
        attempts_remaining=quiz_rules.remaining_attempts(quiz.max_attempts, attempts_used),
        max_attempts=quiz.max_attempts,
        best_score=best_score,
    )


# ── Quiz Discovery ──────────────────────────────────────────────

@router.get("/", response_model=PaginatedResponse)
async def list_quizzes(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=50, ge=1, le=100),
    course_id: UUID = Query(default=None),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Quiz)
    if course_id:
        query = query.where(Quiz.course_id == course_id)
    count_query = select(func.count(Quiz.id))
    if course_id:
        count_query = count_query.where(Quiz.course_id == course_id)

    total = (await db.execute(count_query)).scalar() or 0
    result = await db.execute(
        query.order_by(Quiz.display_order).offset((page - 1) * size).limit(size)
    )
    quizzes = result.scalars().all()

    # Attach course title/slug for display
    items = []
    for q in quizzes:
        qd = QuizResponse.model_validate(q).model_dump()
        if q.course_id:
            c = (await db.execute(select(Course).where(Course.id == q.course_id))).scalar_one_or_none()
            qd["course_title"] = c.title if c else None
            qd["course_slug"] = c.slug if c else None
        elif q.module_id:
            from app.models import Module
            m = (await db.execute(select(Module).where(Module.id == q.module_id))).scalar_one_or_none()
            if m:
                c = (await db.execute(select(Course).where(Course.id == m.course_id))).scalar_one_or_none()
                qd["course_title"] = c.title if c else None
                qd["course_slug"] = c.slug if c else None
        items.append(qd)

    return PaginatedResponse(
        items=items, total=total, page=page, size=size,
        pages=(total + size - 1) // size if total > 0 else 0,
    )


# ── Quiz Detail ─────────────────────────────────────────────────

@router.get("/{quiz_id}", response_model=QuizDetailResponse)
async def get_quiz_detail(
    quiz_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    quiz = await _get_quiz_or_404(db, quiz_id)

    questions_result = await db.execute(
        select(Question)
        .where(Question.quiz_id == quiz_id)
        .order_by(Question.display_order)
    )
    questions = questions_result.scalars().all()

    q_responses = []
    for q in questions:
        opts_result = await db.execute(
            select(QuestionOption)
            .where(QuestionOption.question_id == q.id)
            .order_by(QuestionOption.display_order)
        )
        # Never ship the answer key to the browser. Correctness is returned
        # only after the learner submits an attempt.
        opts = [
            QuestionOptionResponse(id=o.id, content=o.content, is_correct=False)
            for o in opts_result.scalars().all()
        ]
        q_responses.append(QuestionResponse(
            id=q.id,
            question_type=q.question_type.value if hasattr(q.question_type, "value") else str(q.question_type),
            content=q.content,
            # Explanations are part of the post-submission review, not the
            # question payload; otherwise the answer key leaks via dev tools.
            explanation=None,
            points=q.points,
            options=opts,
        ))

    used, best_score, _, _ = await _attempt_usage(db, quiz_id, current_user.id)

    return QuizDetailResponse(
        id=quiz.id,
        title=quiz.title,
        description=quiz.description,
        passing_score=quiz.passing_score,
        time_limit_minutes=quiz.time_limit_minutes,
        max_attempts=quiz.max_attempts,
        attempts_used=used,
        attempts_remaining=quiz_rules.remaining_attempts(quiz.max_attempts, used),
        best_score=best_score,
        can_attempt=quiz_rules.can_start_attempt(quiz.max_attempts, used),
        questions=q_responses,
    )


# ── Start Attempt ───────────────────────────────────────────────

@router.post("/{quiz_id}/attempts", response_model=QuizAttemptStartResponse)
async def start_quiz_attempt(
    quiz_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Start or resume a graded attempt.

    Reloading the page resumes the open attempt instead of resetting its
    clock, so a learner cannot refresh their way out of a time limit or into
    extra attempts. An open attempt whose limit has passed is marked expired,
    which spends it.
    """
    quiz = await _get_quiz_or_404(db, quiz_id)
    now = datetime.now(timezone.utc)
    used, best_score, _, _ = await _attempt_usage(db, quiz_id, current_user.id)

    active = (
        await db.execute(
            select(QuizAttempt)
            .where(
                QuizAttempt.quiz_id == quiz_id,
                QuizAttempt.user_id == current_user.id,
                QuizAttempt.status == "in_progress",
            )
            .order_by(QuizAttempt.started_at.desc())
            .limit(1)
            .with_for_update()
        )
    ).scalar_one_or_none()

    if active is not None:
        active_started = active.started_at or active.created_at
        if not quiz_rules.attempt_has_expired(active_started, quiz.time_limit_minutes, now):
            return _start_payload(active, quiz, used, best_score)
        active.status = "expired"
        active.completed_at = now
        active.duration_seconds = quiz_rules.elapsed_seconds(active_started, now)
        used += 1
        await db.flush()

    if not quiz_rules.can_start_attempt(quiz.max_attempts, used):
        # Commit the expiry before raising so it is not rolled back and the
        # answer cannot be retried to reset the clock.
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No attempts remaining for this quiz.",
        )

    attempt = QuizAttempt(
        user_id=current_user.id,
        quiz_id=quiz.id,
        status="in_progress",
        started_at=now,
        completed_at=None,
    )
    db.add(attempt)
    await db.flush()
    # Commit before replying: the client submits against this attempt
    # immediately, and that request runs in a separate session.
    await db.commit()
    return _start_payload(attempt, quiz, used, best_score)


# ── Quiz Submission ─────────────────────────────────────────────

@router.post("/{quiz_id}/submit", response_model=QuizResultResponse)
async def submit_quiz(
    quiz_id: UUID,
    data: QuizSubmission,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    quiz = await _get_quiz_or_404(db, quiz_id)
    now = datetime.now(timezone.utc)

    if data.attempt_id is not None:
        attempt = (
            await db.execute(
                select(QuizAttempt)
                .where(
                    QuizAttempt.id == data.attempt_id,
                    QuizAttempt.quiz_id == quiz_id,
                    QuizAttempt.user_id == current_user.id,
                )
                .with_for_update()
            )
        ).scalar_one_or_none()
        if attempt is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attempt not found for this quiz.",
            )
        if attempt.status != "in_progress":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This attempt has already been submitted.",
            )
        started_at = attempt.started_at or now
    else:
        # Older clients submit without starting an attempt. They still spend
        # an attempt and get no measured duration.
        used, _, _, _ = await _attempt_usage(db, quiz_id, current_user.id)
        if not quiz_rules.can_start_attempt(quiz.max_attempts, used):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="No attempts remaining for this quiz.",
            )
        attempt = QuizAttempt(
            user_id=current_user.id,
            quiz_id=quiz_id,
            status="in_progress",
            started_at=now,
            completed_at=None,
        )
        db.add(attempt)
        await db.flush()
        started_at = now

    if quiz_rules.attempt_has_expired(started_at, quiz.time_limit_minutes, now):
        attempt.status = "expired"
        attempt.completed_at = now
        attempt.duration_seconds = quiz_rules.elapsed_seconds(started_at, now)
        attempt.answers = data.answers
        # Persist the expiry: an unanswered timed attempt still spends a try.
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The time limit for this attempt has passed.",
        )

    # Get all questions with correct answers
    questions_result = await db.execute(
        select(Question).where(Question.quiz_id == quiz_id)
    )
    questions = questions_result.scalars().all()

    total_points = 0
    earned_points = 0
    correct_answers = 0
    feedback = []

    for q in questions:
        opts_result = await db.execute(
            select(QuestionOption).where(QuestionOption.question_id == q.id)
        )
        opts = opts_result.scalars().all()
        qtype = q.question_type.value if hasattr(q.question_type, "value") else str(q.question_type)

        raw_answer = data.answers.get(str(q.id))
        if raw_answer is None:
            selected_ids: list[str] = []
        elif isinstance(raw_answer, list):
            selected_ids = [str(item) for item in raw_answer]
        else:
            selected_ids = [str(raw_answer)]
        correct_ids = [str(o.id) for o in opts if o.is_correct]

        if qtype == "multiple_choice":
            is_correct = bool(correct_ids) and set(correct_ids) == set(selected_ids)
        else:
            is_correct = bool(correct_ids) and set(correct_ids) == set(selected_ids)

        total_points += q.points
        if is_correct:
            earned_points += q.points
            correct_answers += 1

        feedback.append({
            "question_id": str(q.id),
            "question": q.content,
            "correct": is_correct,
            "explanation": q.explanation,
            "correct_option_ids": correct_ids,
            "selected_option_ids": selected_ids,
        })

    score = (earned_points / total_points * 100) if total_points > 0 else 0
    passed = score >= quiz.passing_score

    used_before, best_score_before, best_earned_before, already_passed = await _attempt_usage(
        db, quiz_id, current_user.id
    )

    elapsed = quiz_rules.elapsed_seconds(started_at, now)
    limit = quiz_rules.time_limit_seconds(quiz.time_limit_minutes)
    duration = min(elapsed, limit) if limit is not None else elapsed
    question_times = quiz_rules.clamp_question_times(
        data.question_times,
        [q.id for q in questions],
        duration,
    )

    # XP is only the improvement over the learner's previous best. Replaying
    # a quiz (or scoring worse) therefore grants nothing.
    xp_earned = quiz_rules.xp_delta(earned_points, best_earned_before)

    attempt.status = "submitted"
    attempt.score = round(score, 1)
    attempt.passed = passed
    attempt.earned_points = int(earned_points)
    attempt.total_points = int(total_points)
    attempt.correct_answers = correct_answers
    attempt.total_questions = len(questions)
    attempt.answers = data.answers
    attempt.completed_at = now
    attempt.duration_seconds = duration
    attempt.question_times = question_times
    attempt.xp_awarded = xp_earned

    # Gamification: XP for new points, streak + daily goal + achievements.
    if xp_earned > 0:
        await gamification.add_xp(db, current_user, xp_earned)
    # Count the activity once per quiz pass, not once per retake.
    await gamification.record_activity(
        db, current_user, exercises=1 if (passed and not already_passed) else 0
    )

    # Commit before replying so the attempt, XP and counters are visible to
    # the next attempt started by this learner.
    await db.commit()

    return QuizResultResponse(
        quiz_id=quiz_id,
        attempt_id=attempt.id,
        score=round(score, 1),
        passed=passed,
        total_points=int(total_points),
        earned_points=int(earned_points),
        xp_earned=xp_earned,
        correct_answers=correct_answers,
        total_questions=len(questions),
        attempt_number=used_before + 1,
        attempts_remaining=quiz_rules.remaining_attempts(
            quiz.max_attempts, used_before + 1
        ),
        best_score=max(best_score_before, round(score, 1)),
        duration_seconds=duration,
        question_times=question_times,
        completed_at=now,
        feedback=feedback,
    )


# ── Quiz Results (user history) ─────────────────────────────────

@router.get("/{quiz_id}/results", response_model=QuizResultResponse)
async def get_quiz_results(
    quiz_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    quiz = await _get_quiz_or_404(db, quiz_id)
    result = await db.execute(
        select(QuizAttempt)
        .where(
            QuizAttempt.quiz_id == quiz_id,
            QuizAttempt.user_id == current_user.id,
            QuizAttempt.status == "submitted",
        )
        .order_by(QuizAttempt.completed_at.desc())
        .limit(1)
    )
    attempt = result.scalar_one_or_none()
    if not attempt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No attempts for this quiz yet")

    # Rebuild review feedback from the stored attempt. The answer key is only
    # returned to a learner reviewing their own submitted attempt.
    questions = (await db.execute(
        select(Question).where(Question.quiz_id == quiz_id).order_by(Question.display_order)
    )).scalars().all()
    feedback = []
    answers = attempt.answers or {}
    for q in questions:
        opts = (await db.execute(
            select(QuestionOption).where(QuestionOption.question_id == q.id)
        )).scalars().all()
        raw_answer = answers.get(str(q.id))
        selected_ids = [str(item) for item in raw_answer] if isinstance(raw_answer, list) else ([str(raw_answer)] if raw_answer is not None else [])
        correct_ids = [str(o.id) for o in opts if o.is_correct]
        feedback.append({
            "question_id": str(q.id),
            "question": q.content,
            "correct": bool(correct_ids) and set(correct_ids) == set(selected_ids),
            "explanation": q.explanation,
            "correct_option_ids": correct_ids,
            "selected_option_ids": selected_ids,
        })

    used, best_score, _, _ = await _attempt_usage(db, quiz_id, current_user.id)

    return QuizResultResponse(
        quiz_id=quiz_id,
        attempt_id=attempt.id,
        score=float(attempt.score),
        passed=attempt.passed,
        total_points=attempt.total_points,
        earned_points=attempt.earned_points,
        xp_earned=attempt.xp_awarded or 0,
        correct_answers=attempt.correct_answers,
        total_questions=attempt.total_questions,
        attempt_number=used,
        attempts_remaining=quiz_rules.remaining_attempts(quiz.max_attempts, used),
        best_score=best_score,
        duration_seconds=attempt.duration_seconds or 0,
        question_times={
            str(qid): int(seconds)
            for qid, seconds in (attempt.question_times or {}).items()
        },
        completed_at=attempt.completed_at or attempt.created_at,
        feedback=feedback,
    )
