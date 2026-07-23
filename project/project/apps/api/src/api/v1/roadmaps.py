from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.core.dependencies import require_content_creator
from src.db.session import get_db
from src.models.content import Course, Roadmap, RoadmapCourse
from src.models.user import User
from src.schemas.common import PaginatedResponse, PaginationParams
from src.schemas.roadmap import (
    RoadmapCreate,
    RoadmapDetail,
    RoadmapRead,
    RoadmapUpdate,
)

router = APIRouter()


@router.get("/", response_model=PaginatedResponse)
async def list_roadmaps(
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse:
    query = select(Roadmap).where(Roadmap.is_published.is_(True))
    total_result = await db.execute(query)
    total = len(total_result.scalars().all())

    result = await db.execute(
        query.order_by(Roadmap.title).offset((pagination.page - 1) * pagination.per_page).limit(pagination.per_page)
    )
    roadmaps = result.scalars().all()

    return PaginatedResponse(
        items=[RoadmapRead.model_validate(r).model_dump() for r in roadmaps],
        total=total,
        page=pagination.page,
        per_page=pagination.per_page,
        pages=(total + pagination.per_page - 1) // pagination.per_page,
    )


@router.get("/{roadmap_id}", response_model=RoadmapDetail)
async def get_roadmap(roadmap_id: UUID, db: AsyncSession = Depends(get_db)) -> Roadmap:
    result = await db.execute(
        select(Roadmap).where(Roadmap.id == roadmap_id).options(selectinload(Roadmap.roadmap_courses))
    )
    roadmap = result.scalar_one_or_none()
    if roadmap is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Roadmap not found")
    return roadmap


@router.post("/", response_model=RoadmapRead, status_code=status.HTTP_201_CREATED)
async def create_roadmap(
    data: RoadmapCreate,
    current_user: User = Depends(require_content_creator),
    db: AsyncSession = Depends(get_db),
) -> Roadmap:
    existing = await db.execute(select(Roadmap).where(Roadmap.slug == data.slug))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Slug already exists")
    roadmap = Roadmap(**data.model_dump())
    db.add(roadmap)
    await db.commit()
    await db.refresh(roadmap)
    return roadmap


@router.put("/{roadmap_id}", response_model=RoadmapRead)
async def update_roadmap(
    roadmap_id: UUID,
    data: RoadmapUpdate,
    current_user: User = Depends(require_content_creator),
    db: AsyncSession = Depends(get_db),
) -> Roadmap:
    result = await db.execute(select(Roadmap).where(Roadmap.id == roadmap_id))
    roadmap = result.scalar_one_or_none()
    if roadmap is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Roadmap not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(roadmap, field, value)

    await db.commit()
    await db.refresh(roadmap)
    return roadmap


@router.delete("/{roadmap_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_roadmap(
    roadmap_id: UUID,
    current_user: User = Depends(require_content_creator),
    db: AsyncSession = Depends(get_db),
) -> None:
    result = await db.execute(select(Roadmap).where(Roadmap.id == roadmap_id))
    roadmap = result.scalar_one_or_none()
    if roadmap is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Roadmap not found")
    await db.delete(roadmap)
    await db.commit()


@router.post("/{roadmap_id}/courses", status_code=status.HTTP_201_CREATED)
async def link_course_to_roadmap(
    roadmap_id: UUID,
    course_id: UUID,
    position: int = 0,
    current_user: User = Depends(require_content_creator),
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    roadmap = await db.execute(select(Roadmap).where(Roadmap.id == roadmap_id))
    if roadmap.scalar_one_or_none() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Roadmap not found")

    course = await db.execute(select(Course).where(Course.id == course_id))
    if course.scalar_one_or_none() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    existing = await db.execute(
        select(RoadmapCourse).where(RoadmapCourse.roadmap_id == roadmap_id, RoadmapCourse.course_id == course_id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Course already linked")

    link = RoadmapCourse(roadmap_id=roadmap_id, course_id=course_id, position=position)
    db.add(link)
    await db.commit()
    return {"status": "ok"}


@router.get("/{roadmap_id}/courses", response_model=PaginatedResponse)
async def get_roadmap_courses(
    roadmap_id: UUID,
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse:
    query = (
        select(Course)
        .join(RoadmapCourse, RoadmapCourse.course_id == Course.id)
        .where(RoadmapCourse.roadmap_id == roadmap_id)
        .order_by(RoadmapCourse.position)
    )
    total_result = await db.execute(query)
    total = len(total_result.scalars().all())

    result = await db.execute(query.offset((pagination.page - 1) * pagination.per_page).limit(pagination.per_page))
    courses = result.scalars().all()

    return PaginatedResponse(
        items=[
            {
                "id": str(c.id),
                "slug": c.slug,
                "title": c.title,
                "technology": c.technology,
                "description": c.description,
            }
            for c in courses
        ],
        total=total,
        page=pagination.page,
        per_page=pagination.per_page,
        pages=(total + pagination.per_page - 1) // pagination.per_page,
    )
