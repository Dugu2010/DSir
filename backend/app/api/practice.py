import asyncio

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models import (
    Exercise, ExerciseHint, Submission, SubmissionStatus, ExerciseType,
    ExerciseDifficulty, Project, ProjectSubmission, UserStats, User,
    SavedSnippet,
)
from app.schemas import (
    ExerciseResponse, ExerciseDetailResponse, SubmissionResponse,
    PaginatedResponse, ProjectDetailResponse, ProjectSubmitRequest,
    ProjectSubmissionResponse, SavedSnippetCreate, SavedSnippetUpdate,
    SavedSnippetResponse,
)
from app.utils.deps import get_current_active_user
from app.services import gamification
from app.services import code_runner
from uuid import UUID
from datetime import date

router = APIRouter(prefix="/practice", tags=["Practice"])
# Keep concurrent child-process graders bounded on small Render instances.
_GRADING_SLOTS = asyncio.Semaphore(2)

@router.get("/exercises", response_model=PaginatedResponse)
async def list_exercises(page: int = Query(1, ge=1), size: int = Query(20, ge=1, le=100), difficulty: str = None, exercise_type: str = None, skill: str = None, current_user: User = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)):
    # Soft-deleted and empty legacy exercises must never appear in the catalog.
    filters = [Exercise.deleted_at.is_(None)]
    if difficulty:
        try: filters.append(Exercise.difficulty == ExerciseDifficulty(difficulty))
        except ValueError: pass
    if exercise_type:
        try: filters.append(Exercise.exercise_type == ExerciseType(exercise_type))
        except ValueError: pass
    if skill:
        filters.append(Exercise.skill_tags.any(skill))
    query = select(Exercise).where(*filters)
    total = (await db.execute(select(func.count(Exercise.id)).where(*filters))).scalar() or 0
    result = await db.execute(query.order_by(Exercise.display_order, Exercise.title).offset((page - 1) * size).limit(size))
    items = []
    for ex in result.scalars().all():
        item = ExerciseResponse.model_validate(ex); item.hints_count = len(ex.hints) if ex.hints else 0; items.append(item)
    return PaginatedResponse(items=items, total=total, page=page, size=size, pages=(total + size - 1) // size)

@router.get("/exercises/{exercise_id}")
async def get_exercise(exercise_id: UUID, current_user: User = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Exercise).where(Exercise.id == exercise_id, Exercise.deleted_at.is_(None)))
    exercise = result.scalar_one_or_none()
    if not exercise: raise HTTPException(status_code=404, detail="Exercise not found")
    hints_result = await db.execute(select(ExerciseHint).where(ExerciseHint.exercise_id == exercise_id).order_by(ExerciseHint.hint_level))
    hints = [{"level": h.hint_level, "content": h.content, "cost_percentage": h.cost_percentage} for h in hints_result.scalars().all()]
    payload = ExerciseDetailResponse(**ExerciseResponse.model_validate(exercise).model_dump(), hints=hints, test_count=len(exercise.test_code.splitlines()) if exercise.test_code else 0).model_dump()
    payload["test_code"] = exercise.test_code or ""
    return payload

@router.post("/exercises/{exercise_id}/submit", response_model=SubmissionResponse)
async def submit_solution(exercise_id: UUID, data: dict, current_user: User = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)):
    """Authoritative server-side grading.

    Submitted code is executed only inside the hardened child-process sandbox.
    The FastAPI request process never evaluates learner code. Client-reported
    browser results are ignored for the score.
    """
    result = await db.execute(select(Exercise).where(Exercise.id == exercise_id, Exercise.deleted_at.is_(None)))
    exercise = result.scalar_one_or_none()
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")

    code = data.get("code") if isinstance(data, dict) else None
    language = data.get("language", "python") if isinstance(data, dict) else "python"
    if not isinstance(code, str) or not code.strip() or len(code.encode("utf-8")) > 64 * 1024:
        raise HTTPException(status_code=422, detail="Invalid code or code exceeds the 64 KB limit")
    if str(language).lower() != "python":
        raise HTTPException(status_code=422, detail="Python exercises only")

    async with _GRADING_SLOTS:
        grading = await asyncio.to_thread(code_runner.run_tests, code, exercise.test_code or "")

    total = int(grading.get("total", 0) or 0)
    passed = int(grading.get("passed", 0) or 0)
    failed = int(grading.get("failed", max(total - passed, 0)) or 0)
    score = round(passed / total * 100, 1) if total else 0.0

    attempts = (await db.execute(select(func.count(Submission.id)).where(Submission.user_id == current_user.id, Submission.exercise_id == exercise_id))).scalar() or 0
    submission = Submission(user_id=current_user.id, exercise_id=exercise_id, code=code, language="python", attempt_number=attempts + 1)
    submission.status = SubmissionStatus.PASSED if score >= 80 else SubmissionStatus.FAILED
    submission.score = score
    submission.test_results = {
        "verification_mode": "server_sandbox",
        "passed": passed,
        "failed": failed,
        "total": total,
        "details": grading.get("details", [])[:100],
    }
    submission.error_message = str(grading.get("error"))[:2000] if grading.get("error") else None
    db.add(submission)
    await db.flush()
    if submission.status == SubmissionStatus.PASSED:
        await gamification.add_xp(db, current_user, exercise.points)
        stats = await gamification.record_activity(db, current_user, exercises=1, minutes=exercise.estimated_duration_minutes or 5)
        stats.exercises_completed += 1
    else:
        await gamification.record_activity(db, current_user)
    await db.commit()
    return submission

@router.get("/exercises/{exercise_id}/solution")
async def reveal_solution(
    exercise_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Reveal a reference solution only after the learner has attempted it.

    Solutions stay hidden until at least one submission exists, so the
    independent practice flow still asks for genuine effort first.
    """
    exercise = (await db.execute(
        select(Exercise).where(Exercise.id == exercise_id, Exercise.deleted_at.is_(None))
    )).scalar_one_or_none()
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")

    attempts = (await db.execute(
        select(func.count(Submission.id)).where(
            Submission.user_id == current_user.id,
            Submission.exercise_id == exercise_id,
        )
    )).scalar() or 0
    if attempts == 0:
        raise HTTPException(
            status_code=403,
            detail="Submit an attempt before revealing the reference solution.",
        )

    return {
        "exercise_id": str(exercise.id),
        "solution_code": exercise.solution_code,
        "explanation": "Compare this with your attempt. There is often more than one valid solution.",
        "attempts": attempts,
    }


@router.get("/submissions", response_model=PaginatedResponse)
async def get_submissions(page: int = Query(1, ge=1), size: int = Query(20, ge=1, le=100), exercise_id: UUID = None, current_user: User = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)):
    query = select(Submission).where(Submission.user_id == current_user.id); count_query = select(func.count(Submission.id)).where(Submission.user_id == current_user.id)
    if exercise_id: query = query.where(Submission.exercise_id == exercise_id); count_query = count_query.where(Submission.exercise_id == exercise_id)
    total = (await db.execute(count_query)).scalar() or 0; result = await db.execute(query.order_by(Submission.submitted_at.desc()).offset((page - 1) * size).limit(size))
    return PaginatedResponse(items=[SubmissionResponse.model_validate(s) for s in result.scalars().all()], total=total, page=page, size=size, pages=(total + size - 1) // size)

@router.get("/projects", response_model=PaginatedResponse)
async def list_projects(page: int = Query(1, ge=1), size: int = Query(20, ge=1, le=100), course_id: UUID = None, difficulty: str = None, is_capstone: bool = None, current_user: User = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)):
    filters = []
    if course_id: filters.append(Project.course_id == course_id)
    if difficulty:
        try: filters.append(Project.difficulty == ExerciseDifficulty(difficulty))
        except ValueError: pass
    if is_capstone is not None: filters.append(Project.is_capstone == is_capstone)
    total = (await db.execute(select(func.count(Project.id)).where(*filters))).scalar() or 0
    result = await db.execute(select(Project).where(*filters).order_by(Project.created_at.desc()).offset((page - 1) * size).limit(size))
    items = [{"id": str(p.id), "title": p.title, "description": p.description, "difficulty": p.difficulty.value if p.difficulty else "medium", "is_capstone": p.is_capstone, "estimated_duration_hours": p.estimated_duration_hours, "skill_tags": p.skill_tags} for p in result.scalars().all()]
    return PaginatedResponse(items=items, total=total, page=page, size=size, pages=(total + size - 1) // size)


# Keep this route above /projects/{project_id}; otherwise "submissions" is
# parsed as a UUID and the endpoint returns a validation error.
@router.get("/projects/submissions", response_model=PaginatedResponse)
async def get_project_submissions(page: int = Query(1, ge=1), size: int = Query(20, ge=1, le=100), current_user: User = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)):
    count_query = select(func.count(ProjectSubmission.id)).where(ProjectSubmission.user_id == current_user.id); total = (await db.execute(count_query)).scalar() or 0
    result = await db.execute(select(ProjectSubmission).where(ProjectSubmission.user_id == current_user.id).order_by(ProjectSubmission.submitted_at.desc()).offset((page - 1) * size).limit(size))
    return PaginatedResponse(items=[ProjectSubmissionResponse.model_validate(s) for s in result.scalars().all()], total=total, page=page, size=size, pages=(total + size - 1) // size if total else 0)


@router.get("/projects/{project_id}", response_model=ProjectDetailResponse)
async def get_project(project_id: UUID, current_user: User = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Project).where(Project.id == project_id)); project = result.scalar_one_or_none()
    if not project: raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.post("/projects/{project_id}/submit", response_model=ProjectSubmissionResponse, status_code=201)
async def submit_project(project_id: UUID, data: ProjectSubmitRequest, current_user: User = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Project).where(Project.id == project_id)); project = result.scalar_one_or_none()
    if not project: raise HTTPException(status_code=404, detail="Project not found")
    submission = ProjectSubmission(user_id=current_user.id, project_id=project_id, code_files=data.code_files, review_status="pending"); db.add(submission)
    stats_result = await db.execute(select(UserStats).where(UserStats.user_id == current_user.id)); stats = stats_result.scalar_one_or_none()
    if stats: stats.projects_completed += 1; stats.last_activity_date = date.today()
    await db.flush(); await db.commit(); return submission


# ── Saved snippets (independent workspace) ──────────────────────

@router.get("/snippets", response_model=list[SavedSnippetResponse])
async def list_snippets(current_user: User = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)):
    rows = await db.execute(
        select(SavedSnippet)
        .where(SavedSnippet.user_id == current_user.id)
        .order_by(SavedSnippet.updated_at.desc())
    )
    return rows.scalars().all()


@router.post("/snippets", response_model=SavedSnippetResponse, status_code=201)
async def create_snippet(data: SavedSnippetCreate, current_user: User = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)):
    snippet = SavedSnippet(
        user_id=current_user.id,
        title=data.title.strip(),
        language="python",
        code=data.code,
        stdin=data.stdin,
    )
    db.add(snippet)
    await db.flush()
    await db.commit()
    await db.refresh(snippet)
    return snippet


@router.put("/snippets/{snippet_id}", response_model=SavedSnippetResponse)
async def update_snippet(snippet_id: UUID, data: SavedSnippetUpdate, current_user: User = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)):
    snippet = (await db.execute(
        select(SavedSnippet).where(SavedSnippet.id == snippet_id, SavedSnippet.user_id == current_user.id)
    )).scalar_one_or_none()
    if not snippet:
        raise HTTPException(status_code=404, detail="Snippet not found")
    if data.title is not None:
        snippet.title = data.title.strip()
    if data.code is not None:
        snippet.code = data.code
    if data.stdin is not None:
        snippet.stdin = data.stdin
    await db.flush()
    await db.commit()
    await db.refresh(snippet)
    return snippet


@router.delete("/snippets/{snippet_id}", status_code=204)
async def delete_snippet(snippet_id: UUID, current_user: User = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)):
    snippet = (await db.execute(
        select(SavedSnippet).where(SavedSnippet.id == snippet_id, SavedSnippet.user_id == current_user.id)
    )).scalar_one_or_none()
    if not snippet:
        raise HTTPException(status_code=404, detail="Snippet not found")
    await db.delete(snippet)
    await db.flush()
    await db.commit()
