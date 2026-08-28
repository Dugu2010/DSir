from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models import (
    Quiz, Question, QuestionOption, UserStats, QuizAttempt, Course,
)
from app.schemas import (
    QuizDetailResponse, QuizResultResponse, QuizAttemptResponse,
    QuestionResponse, QuestionOptionResponse,
    QuizSubmission, PaginatedResponse, QuizResponse,
)
from app.utils.deps import get_current_active_user
from app.services import gamification
from app.models import User
from uuid import UUID
from datetime import datetime, timezone, date

router = APIRouter(prefix="/quizzes", tags=["Quizzes"])


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
    result = await db.execute(select(Quiz).where(Quiz.id == quiz_id))
    quiz = result.scalar_one_or_none()
    if not quiz:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz not found")

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
        opts = [
            QuestionOptionResponse(id=o.id, content=o.content, is_correct=o.is_correct)
            for o in opts_result.scalars().all()
        ]
        q_responses.append(QuestionResponse(
            id=q.id,
            question_type=q.question_type.value if hasattr(q.question_type, "value") else str(q.question_type),
            content=q.content,
            explanation=q.explanation,
            points=q.points,
            options=opts,
        ))

    return QuizDetailResponse(
        id=quiz.id,
        title=quiz.title,
        description=quiz.description,
        passing_score=quiz.passing_score,
        time_limit_minutes=quiz.time_limit_minutes,
        questions=q_responses,
    )


# ── Quiz Submission ─────────────────────────────────────────────

@router.post("/{quiz_id}/submit", response_model=QuizResultResponse)
async def submit_quiz(
    quiz_id: UUID,
    data: QuizSubmission,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Quiz).where(Quiz.id == quiz_id))
    quiz = result.scalar_one_or_none()
    if not quiz:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz not found")

    # Get all questions with correct answers
    questions_result = await db.execute(
        select(Question).where(Question.quiz_id == quiz_id)
    )
    questions = questions_result.scalars().all()

    total_points = 0
    earned_points = 0
    correct_answers = 0

    for q in questions:
        opts_result = await db.execute(
            select(QuestionOption).where(QuestionOption.question_id == q.id)
        )
        opts = opts_result.scalars().all()

        user_answer = data.answers.get(str(q.id))
        total_points += q.points

        if user_answer is not None:
            if q.question_type == "multiple_choice":
                correct_ids = {str(o.id) for o in opts if o.is_correct}
                user_ids = set(user_answer) if isinstance(user_answer, list) else {str(user_answer)}
                if correct_ids == user_ids:
                    earned_points += q.points
                    correct_answers += 1
            elif q.question_type == "single_choice":
                correct_ids = [o for o in opts if o.is_correct]
                if correct_ids and str(correct_ids[0].id) == str(user_answer):
                    earned_points += q.points
                    correct_answers += 1
            elif q.question_type == "true_false":
                correct_ids = [o for o in opts if o.is_correct]
                if correct_ids and str(correct_ids[0].id) == str(user_answer):
                    earned_points += q.points
                    correct_answers += 1

    score = (earned_points / total_points * 100) if total_points > 0 else 0
    passed = score >= quiz.passing_score

    # Persist the attempt so results survive (no more hardcoded zeros).
    attempt = QuizAttempt(
        user_id=current_user.id,
        quiz_id=quiz_id,
        score=round(score, 1),
        passed=passed,
        earned_points=int(earned_points),
        total_points=int(total_points),
        correct_answers=correct_answers,
        total_questions=len(questions),
        answers=data.answers,
    )
    db.add(attempt)

    # Gamification: XP for correct answers, streak + daily goal + achievements.
    if earned_points > 0:
        await gamification.add_xp(db, current_user, int(earned_points))
    await gamification.record_activity(db, current_user, exercises=1 if passed else 0)

    return QuizResultResponse(
        quiz_id=quiz_id,
        score=round(score, 1),
        passed=passed,
        total_points=int(total_points),
        earned_points=int(earned_points),
        correct_answers=correct_answers,
        total_questions=len(questions),
        completed_at=datetime.now(timezone.utc),
    )


# ── Quiz Results (user history) ─────────────────────────────────

@router.get("/{quiz_id}/results", response_model=QuizResultResponse)
async def get_quiz_results(
    quiz_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(QuizAttempt)
        .where(QuizAttempt.quiz_id == quiz_id, QuizAttempt.user_id == current_user.id)
        .order_by(QuizAttempt.completed_at.desc())
        .limit(1)
    )
    attempt = result.scalar_one_or_none()
    if not attempt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No attempts for this quiz yet")

    return QuizResultResponse(
        quiz_id=quiz_id,
        score=float(attempt.score),
        passed=attempt.passed,
        total_points=attempt.total_points,
        earned_points=attempt.earned_points,
        correct_answers=attempt.correct_answers,
        total_questions=attempt.total_questions,
        completed_at=attempt.completed_at,
    )
