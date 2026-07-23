from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.dependencies import get_current_active_user
from src.db.session import get_db
from src.models.assessment import Submission
from src.models.content import Concept, Lesson
from src.models.user import User
from src.schemas.common import PaginatedResponse, PaginationParams
from src.schemas.submission import SubmissionCreate, SubmissionDetail, SubmissionRead

router = APIRouter()


@router.post("/", response_model=SubmissionRead, status_code=status.HTTP_201_CREATED)
async def create_submission(
    data: SubmissionCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Submission:
    if data.lesson_id:
        result = await db.execute(select(Lesson).where(Lesson.id == data.lesson_id))
        if result.scalar_one_or_none() is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found")

    if data.concept_id:
        result = await db.execute(select(Concept).where(Concept.id == data.concept_id))
        if result.scalar_one_or_none() is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Concept not found")

    submission = Submission(
        user_id=current_user.id,
        lesson_id=data.lesson_id,
        concept_id=data.concept_id,
        submission_type=data.submission_type,
        payload=data.payload,
    )
    db.add(submission)
    await db.commit()
    await db.refresh(submission)
    return submission


@router.get("/{submission_id}", response_model=SubmissionDetail)
async def get_submission(
    submission_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Submission:
    result = await db.execute(select(Submission).where(Submission.id == submission_id))
    submission = result.scalar_one_or_none()
    if submission is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found")
    if submission.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return submission


@router.get("/user/me", response_model=PaginatedResponse)
async def list_my_submissions(
    pagination: PaginationParams = Depends(),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse:
    query = select(Submission).where(Submission.user_id == current_user.id)
    total_result = await db.execute(query)
    total = len(total_result.scalars().all())

    result = await db.execute(
        query.order_by(Submission.submitted_at.desc())
        .offset((pagination.page - 1) * pagination.per_page)
        .limit(pagination.per_page)
    )
    submissions = result.scalars().all()

    return PaginatedResponse(
        items=[SubmissionRead.model_validate(s).model_dump() for s in submissions],
        total=total,
        page=pagination.page,
        per_page=pagination.per_page,
        pages=(total + pagination.per_page - 1) // pagination.per_page,
    )
