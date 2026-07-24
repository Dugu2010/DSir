from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.core.dependencies import get_current_active_user
from src.db.session import get_db
from src.models.content import Course
from src.models.learning import Bookmark
from src.models.user import User
from src.schemas.bookmark import BookmarkCreate, BookmarkRead
from src.schemas.common import PaginatedResponse, PaginationParams
from src.schemas.content import CourseRead

router = APIRouter()


@router.get("/", response_model=PaginatedResponse)
async def list_bookmarks(
    pagination: PaginationParams = Depends(),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse:
    query = (
        select(Bookmark)
        .where(Bookmark.user_id == current_user.id)
        .options(selectinload(Bookmark.course))
    )
    total_result = await db.execute(query)
    total = len(total_result.scalars().all())

    result = await db.execute(
        query.order_by(Bookmark.created_at.desc())
        .offset((pagination.page - 1) * pagination.per_page)
        .limit(pagination.per_page)
    )
    bookmarks = result.unique().scalars().all()

    items = []
    for bookmark in bookmarks:
        item = BookmarkRead.model_validate(bookmark).model_dump()
        item["course"] = CourseRead.model_validate(bookmark.course).model_dump() if bookmark.course else None
        items.append(item)

    return PaginatedResponse(
        items=items,
        total=total,
        page=pagination.page,
        per_page=pagination.per_page,
        pages=(total + pagination.per_page - 1) // pagination.per_page,
    )


@router.post("/", response_model=BookmarkRead, status_code=status.HTTP_201_CREATED)
async def create_bookmark(
    data: BookmarkCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Bookmark:
    course = await db.execute(select(Course).where(Course.id == data.course_id))
    if course.scalar_one_or_none() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    existing = await db.execute(
        select(Bookmark).where(Bookmark.user_id == current_user.id, Bookmark.course_id == data.course_id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Already bookmarked")

    bookmark = Bookmark(user_id=current_user.id, course_id=data.course_id)
    db.add(bookmark)
    await db.commit()
    await db.refresh(bookmark)
    return bookmark


@router.delete("/{bookmark_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_bookmark(
    bookmark_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    result = await db.execute(
        select(Bookmark).where(Bookmark.id == bookmark_id, Bookmark.user_id == current_user.id)
    )
    bookmark = result.scalar_one_or_none()
    if bookmark is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bookmark not found")
    await db.delete(bookmark)
    await db.commit()
