from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models import Exercise, ExerciseHint, Submission, SubmissionStatus, ExerciseType, ExerciseDifficulty, Project, ProjectSubmission, UserStats, User
from app.schemas import ExerciseResponse, ExerciseDetailResponse, CodeSubmission, SubmissionResponse, PaginatedResponse, ProjectDetailResponse, ProjectSubmitRequest, ProjectSubmissionResponse
from app.utils.deps import get_current_active_user
from app.services import gamification
from uuid import UUID
from datetime import date
from app.utils.redis import get_cache, set_cache

router = APIRouter(prefix="/practice", tags=["Practice"])

@router.get("/exercises", response_model=PaginatedResponse)
async def list_exercises(page: int = Query(default=1, ge=1), size: int = Query(default=20, ge=1, le=100), difficulty: str = Query(default=None), exercise_type: str = Query(default=None), skill: str = Query(default=None), current_user: User = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)):
    query = select(Exercise)
    if difficulty:
        try: query = query.where(Exercise.difficulty == ExerciseDifficulty(difficulty))
        except ValueError: pass
    if exercise_type:
        try: query = query.where(Exercise.exercise_type == ExerciseType(exercise_type))
        except ValueError: pass
    if skill: query = query.where(Exercise.skill_tags.any(skill))
    count_query = select(func.count(Exercise.id))
    if difficulty:
        try: count_query = count_query.where(Exercise.difficulty == ExerciseDifficulty(difficulty))
        except ValueError: pass
    total = (await db.execute(count_query)).scalar() or 0
    result = await db.execute(query.order_by(Exercise.display_order).offset((page - 1) * size).limit(size))
    items = []
    for ex in result.scalars().all():
        resp = ExerciseResponse.model_validate(ex); resp.hints_count = len(ex.hints) if ex.hints else 0; items.append(resp)
    return PaginatedResponse(items=items, total=total, page=page, size=size, pages=(total + size - 1) // size)

@router.get("/exercises/{exercise_id}", response_model=ExerciseDetailResponse)
async def get_exercise(exercise_id: UUID, current_user: User = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)):
    cache_key = f"exercise:detail:{exercise_id}"
    cached = await get_cache(cache_key)
    if cached is not None: return cached
    result = await db.execute(select(Exercise).where(Exercise.id == exercise_id))
    exercise = result.scalar_one_or_none()
    if not exercise: raise HTTPException(status_code=404, detail="Exercise not found")
    hints_result = await db.execute(select(ExerciseHint).where(ExerciseHint.exercise_id == exercise_id).order_by(ExerciseHint.hint_level))
    hints = [{"level": h.hint_level, "content": h.content, "cost_percentage": h.cost_percentage} for h in hints_result.scalars().all()]
    payload = ExerciseDetailResponse(**ExerciseResponse.model_validate(exercise).model_dump(), hints=hints, test_count=len(exercise.test_code.splitlines()) if exercise.test_code else 0)
    # Browser grading needs the exercise's test program. This is intentionally client-side;
    # the API only records the resulting score/progress and never executes learner code.
    data = payload.model_dump(); data["test_code"] = exercise.test_code or ""
    await set_cache(cache_key, data, expire=60)
    return data

@router.post("/exercises/{exercise_id}/submit", response_model=SubmissionResponse)
async def submit_solution(exercise_id: UUID, data: CodeSubmission, current_user: User = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Exercise).where(Exercise.id == exercise_id))
    exercise = result.scalar_one_or_none()
    if not exercise: raise HTTPException(status_code=404, detail="Exercise not found")
    client_result = getattr(data, "client_result", None)
    if not isinstance(client_result, dict):
        raise HTTPException(status_code=422, detail="Browser test result is required")
    try:
        total = int(client_result.get("total", 0)); passed = int(client_result.get("passed", 0))
    except (TypeError, ValueError):
        raise HTTPException(status_code=422, detail="Invalid browser test result")
    if total < 1 or total > 100 or passed < 0 or passed > total:
        raise HTTPException(status_code=422, detail="Invalid browser test result")
    details = client_result.get("details", [])
    if not isinstance(details, list) or len(details) > 100: raise HTTPException(status_code=422, detail="Invalid test details")
    score = round(passed / total * 100, 1)
    attempts = (await db.execute(select(func.count(Submission.id)).where(Submission.user_id == current_user.id, Submission.exercise_id == exercise_id))).scalar() or 0
    submission = Submission(user_id=current_user.id, exercise_id=exercise_id, code=data.code, language=data.language, attempt_number=attempts + 1)
    submission.status = SubmissionStatus.PASSED if score >= 80 else SubmissionStatus.FAILED
    submission.score = score
    submission.test_results = {"verification_mode": "browser", "passed": passed, "failed": total - passed, "total": total, "details": details}
    submission.error_message = str(client_result.get("error"))[:2000] if client_result.get("error") else None
    db.add(submission); await db.flush()
    if submission.status == SubmissionStatus.PASSED:
        await gamification.add_xp(db, current_user, exercise.points)
        stats = await gamification.record_activity(db, current_user, exercises=1, minutes=exercise.estimated_duration_minutes or 5)
        stats.exercises_completed += 1
    else: await gamification.record_activity(db, current_user)
    return submission

@router.get("/submissions", response_model=PaginatedResponse)
async def get_submissions(page: int = Query(default=1, ge=1), size: int = Query(default=20, ge=1, le=100), exercise_id: UUID = Query(default=None), current_user: User = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)):
    query = select(Submission).where(Submission.user_id == current_user.id)
    count_query = select(func.count(Submission.id)).where(Submission.user_id == current_user.id)
    if exercise_id: query = query.where(Submission.exercise_id == exercise_id); count_query = count_query.where(Submission.exercise_id == exercise_id)
    total = (await db.execute(count_query)).scalar() or 0
    result = await db.execute(query.order_by(Submission.submitted_at.desc()).offset((page - 1) * size).limit(size))
    return PaginatedResponse(items=[SubmissionResponse.model_validate(s) for s in result.scalars().all()], total=total, page=page, size=size, pages=(total + size - 1) // size)

@router.get("/projects", response_model=PaginatedResponse)
async def list_projects(page: int = Query(default=1, ge=1), size: int = Query(default=20, ge=1, le=100), course_id: UUID = Query(default=None), difficulty: str = Query(default=None), is_capstone: bool = Query(default=None), current_user: User = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)):
    query = select(Project)
    if course_id: query = query.where(Project.course_id == course_id)
    if difficulty:
        try: query = query.where(Project.difficulty == ExerciseDifficulty(difficulty))
        except ValueError: pass
    if is_capstone is not None: query = query.where(Project.is_capstone == is_capstone)
    total = (await db.execute(select(func.count(Project.id)))).scalar() or 0
    result = await db.execute(query.order_by(Project.created_at.desc()).offset((page - 1) * size).limit(size))
    projects = result.scalars().all()
    items = [{"id": str(p.id), "title": p.title, "description": p.description, "difficulty": p.difficulty.value if p.difficulty else "medium", "is_capstone": p.is_capstone, "estimated_duration_hours": p.estimated_duration_hours, "skill_tags": p.skill_tags} for p in projects]
    return PaginatedResponse(items=items, total=total, page=page, size=size, pages=(total + size - 1) // size)

@router.get("/projects/submissions", response_model=PaginatedResponse)
async def get_project_submissions(page: int = Query(default=1, ge=1), size: int = Query(default=20, ge=1, le=100), current_user: User = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)):
    count_query = select(func.count(ProjectSubmission.id)).where(ProjectSubmission.user_id == current_user.id)
    total = (await db.execute(count_query)).scalar() or 0
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
