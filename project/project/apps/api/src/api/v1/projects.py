from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.dependencies import get_current_active_user, require_content_creator
from src.db.session import get_db
from src.models.assessment import Project, ProjectSubmission
from src.models.user import User
from src.schemas.common import PaginatedResponse, PaginationParams
from src.schemas.project import (
    ProjectDetail,
    ProjectRead,
    ProjectSubmissionCreate,
    ProjectSubmissionDetail,
    ProjectSubmissionRead,
)

router = APIRouter()


@router.get("/course/{course_id}", response_model=PaginatedResponse)
async def list_course_projects(
    course_id: UUID,
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse:
    from src.core.pagination import paginated_response

    query = select(Project).where(Project.course_id == course_id)
    return await paginated_response(db, query, pagination, ProjectRead)


@router.get("/{project_id}", response_model=ProjectDetail)
async def get_project(project_id: UUID, db: AsyncSession = Depends(get_db)) -> Project:
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project


@router.post("/", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
async def create_project(
    project: ProjectDetail,
    current_user: User = Depends(require_content_creator),
    db: AsyncSession = Depends(get_db),
) -> Project:
    existing = await db.execute(
        select(Project).where(Project.course_id == project.course_id, Project.slug == project.slug)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Project slug already exists")

    db_project = Project(**project.model_dump(exclude={"id", "created_at"}))
    db.add(db_project)
    await db.commit()
    await db.refresh(db_project)
    return db_project


@router.post("/submissions", response_model=ProjectSubmissionRead, status_code=status.HTTP_201_CREATED)
async def submit_project(
    data: ProjectSubmissionCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ProjectSubmission:
    result = await db.execute(select(Project).where(Project.id == data.project_id))
    if result.scalar_one_or_none() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    submission = ProjectSubmission(
        user_id=current_user.id,
        project_id=data.project_id,
        repository_url=data.repository_url,
        files=data.files,
    )
    db.add(submission)
    await db.commit()
    await db.refresh(submission)
    return submission


@router.get("/submissions/{submission_id}", response_model=ProjectSubmissionDetail)
async def get_submission(
    submission_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ProjectSubmission:
    result = await db.execute(select(ProjectSubmission).where(ProjectSubmission.id == submission_id))
    submission = result.scalar_one_or_none()
    if submission is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found")
    if submission.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return submission


@router.get("/submissions/me", response_model=PaginatedResponse)
async def list_my_project_submissions(
    pagination: PaginationParams = Depends(),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse:
    from src.core.pagination import paginated_response

    query = select(ProjectSubmission).where(ProjectSubmission.user_id == current_user.id)
    return await paginated_response(db, query, pagination, ProjectSubmissionRead)
