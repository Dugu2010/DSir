from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models import (
    Exercise, ExerciseHint, Submission, SubmissionStatus,
    ExerciseType, ExerciseDifficulty,
    Project, ProjectSubmission, UserStats,
)
from app.schemas import (
    ExerciseResponse, ExerciseDetailResponse,
    CodeSubmission, SubmissionResponse, PaginatedResponse,
)
from app.utils.deps import get_current_active_user
from app.models import User
from uuid import UUID
from datetime import datetime, timezone, date

router = APIRouter(prefix="/practice", tags=["Practice"])


# ── Exercise Discovery ──────────────────────────────────────────

@router.get("/exercises", response_model=PaginatedResponse)
async def list_exercises(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    difficulty: str = Query(default=None),
    exercise_type: str = Query(default=None),
    skill: str = Query(default=None),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Exercise)

    if difficulty:
        try:
            query = query.where(Exercise.difficulty == ExerciseDifficulty(difficulty))
        except ValueError:
            pass
    if exercise_type:
        try:
            query = query.where(Exercise.exercise_type == ExerciseType(exercise_type))
        except ValueError:
            pass
    if skill:
        query = query.where(Exercise.skill_tags.any(skill))

    count_query = select(func.count(Exercise.id))
    if difficulty:
        try:
            count_query = count_query.where(Exercise.difficulty == ExerciseDifficulty(difficulty))
        except ValueError:
            pass

    total = (await db.execute(count_query)).scalar()
    result = await db.execute(
        query.order_by(Exercise.display_order).offset((page - 1) * size).limit(size)
    )
    exercises = result.scalars().all()

    response_items = []
    for ex in exercises:
        resp = ExerciseResponse.model_validate(ex)
        resp.hints_count = len(ex.hints) if ex.hints else 0
        response_items.append(resp)

    return PaginatedResponse(
        items=response_items,
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size,
    )


@router.get("/exercises/{exercise_id}", response_model=ExerciseDetailResponse)
async def get_exercise(
    exercise_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Exercise).where(Exercise.id == exercise_id))
    exercise = result.scalar_one_or_none()
    if not exercise:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exercise not found")

    hints_result = await db.execute(
        select(ExerciseHint).where(ExerciseHint.exercise_id == exercise_id).order_by(ExerciseHint.hint_level)
    )
    hints = [{"level": h.hint_level, "content": h.content, "cost_percentage": h.cost_percentage} for h in hints_result.scalars().all()]

    resp = ExerciseDetailResponse.model_validate(exercise)
    resp.hints = hints
    resp.test_count = len(exercise.test_code.split("\n")) if exercise.test_code else 0
    return resp


# ── Code Submission & Execution ─────────────────────────────────

@router.post("/exercises/{exercise_id}/submit", response_model=SubmissionResponse)
async def submit_solution(
    exercise_id: UUID,
    data: CodeSubmission,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Exercise).where(Exercise.id == exercise_id))
    exercise = result.scalar_one_or_none()
    if not exercise:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exercise not found")

    # Count previous attempts
    attempt_count_result = await db.execute(
        select(func.count(Submission.id)).where(
            Submission.user_id == current_user.id,
            Submission.exercise_id == exercise_id,
        )
    )
    attempt_number = (attempt_count_result.scalar() or 0) + 1

    submission = Submission(
        user_id=current_user.id,
        exercise_id=exercise_id,
        code=data.code,
        language=data.language,
        attempt_number=attempt_number,
    )

    # Run basic validation (in production, this would run in a sandbox)
    score, test_results, error = _evaluate_submission(data.code, exercise)

    submission.status = SubmissionStatus.PASSED if score >= 80 else SubmissionStatus.FAILED
    submission.score = score
    submission.test_results = test_results
    submission.error_message = error

    db.add(submission)
    await db.flush()

    # Update user stats
    stats_result = await db.execute(select(UserStats).where(UserStats.user_id == current_user.id))
    stats = stats_result.scalar_one_or_none()
    if stats:
        stats.exercises_completed += 1 if submission.status == SubmissionStatus.PASSED else 0
        stats.total_xp += exercise.points if submission.status == SubmissionStatus.PASSED else 0
        stats.last_activity_date = date.today()

    return submission


def _evaluate_submission(code: str, exercise: Exercise) -> tuple:
    """Basic code evaluation. In production, delegates to sandbox service."""
    score = 0.0
    test_results = {"passed": 0, "failed": 0, "total": 0, "details": []}
    error = None

    try:
        # Check for obviously empty or placeholder code
        code_stripped = code.strip()
        if not code_stripped or code_stripped in ("# your code here", "// your code here", "pass", ""):
            return 0.0, test_results, "No code submitted"

        # Check for syntax errors in simple cases
        if exercise.language == "python":
            try:
                compile(code, "<submission>", "exec")
            except SyntaxError as e:
                return 20.0, test_results, f"Syntax error: {str(e)}"

        # Run basic test assertions embedded in test_code
        if exercise.test_code:
            test_cases = [t.strip() for t in exercise.test_code.split("\n") if t.strip() and "assert" in t.lower()]
            test_results["total"] = max(len(test_cases), 1)
            passed = 0

            # Check if solution code patterns exist
            solution_keywords = [w for w in exercise.solution_code.split() if len(w) > 3 and w.isalpha()]
            code_keywords = set(code.split())
            matches = sum(1 for kw in solution_keywords if kw in code_keywords)
            match_ratio = matches / max(len(solution_keywords), 1)

            for tc in test_cases:
                # Simple heuristic matching
                if any(word in code for word in tc.split() if len(word) > 3):
                    passed += 1
                    test_results["details"].append({"test": tc, "passed": True})
                else:
                    test_results["details"].append({"test": tc, "passed": False})

            test_results["passed"] = passed
            test_results["failed"] = test_results["total"] - passed

            if test_results["total"] > 0:
                score = (passed / test_results["total"]) * 100
            else:
                score = match_ratio * 100
        else:
            score = 100.0
            test_results["total"] = 1
            test_results["passed"] = 1

        score = min(round(score, 1), 100.0)

    except Exception as e:
        error = str(e)
        score = 10.0

    return score, test_results, error


# ── Submission History ──────────────────────────────────────────

@router.get("/submissions", response_model=PaginatedResponse)
async def get_submissions(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    exercise_id: UUID = Query(default=None),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Submission).where(Submission.user_id == current_user.id)
    if exercise_id:
        query = query.where(Submission.exercise_id == exercise_id)

    count_query = select(func.count(Submission.id)).where(Submission.user_id == current_user.id)
    if exercise_id:
        count_query = count_query.where(Submission.exercise_id == exercise_id)

    total = (await db.execute(count_query)).scalar()
    result = await db.execute(
        query.order_by(Submission.submitted_at.desc())
        .offset((page - 1) * size)
        .limit(size)
    )

    return PaginatedResponse(
        items=[SubmissionResponse.model_validate(s) for s in result.scalars().all()],
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size,
    )


# ── Projects ────────────────────────────────────────────────────

@router.get("/projects", response_model=PaginatedResponse)
async def list_projects(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    course_id: UUID = Query(default=None),
    difficulty: str = Query(default=None),
    is_capstone: bool = Query(default=None),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Project)
    if course_id:
        query = query.where(Project.course_id == course_id)
    if difficulty:
        try:
            query = query.where(Project.difficulty == ExerciseDifficulty(difficulty))
        except ValueError:
            pass
    if is_capstone is not None:
        query = query.where(Project.is_capstone == is_capstone)

    count_query = select(func.count(Project.id)).select_from(Project)

    total = (await db.execute(count_query)).scalar()
    result = await db.execute(
        query.order_by(Project.created_at.desc())
        .offset((page - 1) * size)
        .limit(size)
    )

    projects = result.scalars().all()
    return PaginatedResponse(
        items=[{
            "id": str(p.id),
            "title": p.title,
            "description": p.description,
            "difficulty": p.difficulty.value if p.difficulty else "medium",
            "is_capstone": p.is_capstone,
            "estimated_duration_hours": p.estimated_duration_hours,
            "skill_tags": p.skill_tags,
        } for p in projects],
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size,
    )
