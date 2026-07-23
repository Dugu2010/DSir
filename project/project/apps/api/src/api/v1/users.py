from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.core.dependencies import get_current_active_user, require_admin
from src.core.security import get_password_hash
from src.db.session import get_db
from src.models.content import Course
from src.models.learning import UserActivity
from src.models.user import User, UserRole
from src.schemas.common import ActivityCreate, PaginatedResponse, PaginationParams
from src.schemas.user import UserCreate, UserRead

router = APIRouter()


@router.get("/", response_model=PaginatedResponse)
async def list_users(
    pagination: PaginationParams = Depends(),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse:
    total_result = await db.execute(select(User))
    total = len(total_result.scalars().all())

    result = await db.execute(
        select(User)
        .order_by(User.created_at.desc())
        .offset((pagination.page - 1) * pagination.per_page)
        .limit(pagination.per_page)
    )
    users = result.scalars().all()

    return PaginatedResponse(
        items=[UserRead.model_validate(u).model_dump() for u in users],
        total=total,
        page=pagination.page,
        per_page=pagination.per_page,
        pages=(total + pagination.per_page - 1) // pagination.per_page,
    )


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserCreate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> User:
    existing = await db.execute(select(User).where(User.email == user.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    db_user = User(
        email=user.email,
        full_name=user.full_name,
        hashed_password=get_password_hash(user.password),
    )
    db.add(db_user)
    await db.flush()
    db.add(UserRole(user_id=db_user.id, role="learner"))
    await db.commit()
    await db.refresh(db_user)
    return db_user


@router.post("/{user_id}/roles", status_code=status.HTTP_201_CREATED)
async def add_role(
    user_id: UUID,
    role: str,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    existing = await db.execute(select(UserRole).where(UserRole.user_id == user_id, UserRole.role == role))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role already assigned")

    db.add(UserRole(user_id=user_id, role=role))
    await db.commit()
    return {"status": "ok"}


@router.get("/me/activity", response_model=PaginatedResponse)
async def get_my_activity(
    pagination: PaginationParams = Depends(),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse:
    query = (
        select(UserActivity)
        .where(UserActivity.user_id == current_user.id)
        .order_by(UserActivity.created_at.desc())
    )
    total_result = await db.execute(query)
    total = len(total_result.scalars().all())

    result = await db.execute(
        query.offset((pagination.page - 1) * pagination.per_page).limit(pagination.per_page)
    )
    activities = result.scalars().all()
    return PaginatedResponse(
        items=[
            {
                "id": str(activity.id),
                "activity_type": activity.activity_type,
                "entity_type": activity.entity_type,
                "entity_id": str(activity.entity_id) if activity.entity_id else None,
                "meta": activity.meta or {},
                "created_at": activity.created_at.isoformat() if activity.created_at else None,
            }
            for activity in activities
        ],
        total=total,
        page=pagination.page,
        per_page=pagination.per_page,
        pages=(total + pagination.per_page - 1) // pagination.per_page,
    )


@router.post("/me/activity", status_code=status.HTTP_204_NO_CONTENT)
async def log_my_activity(
    data: ActivityCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    activity = UserActivity(
        user_id=current_user.id,
        activity_type=data.activity_type,
        entity_type=data.entity_type,
        entity_id=data.entity_id,
        meta=data.meta or {},
    )
    db.add(activity)
    await db.commit()


@router.get("/me/recent-courses", response_model=PaginatedResponse)
async def get_recent_courses(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse:
    from src.schemas.content import CourseRead

    subquery = (
        select(
            UserActivity.entity_id,
            UserActivity.created_at.label("viewed_at"),
        )
        .where(
            UserActivity.user_id == current_user.id,
            UserActivity.activity_type == "viewed_course",
            UserActivity.entity_type == "course",
            UserActivity.entity_id.isnot(None),
        )
        .order_by(UserActivity.created_at.desc())
    ).subquery()

    query = (
        select(Course, subquery.c.viewed_at)
        .join(subquery, Course.id == subquery.c.entity_id)
        .order_by(subquery.c.viewed_at.desc())
    )
    total_result = await db.execute(query)
    rows = total_result.all()
    total = len(rows)

    items = []
    seen: set[UUID] = set()
    for row in rows:
        course = row[0]
        if course.id in seen:
            continue
        seen.add(course.id)
        items.append(
            {
                "course": CourseRead.model_validate(course).model_dump(),
                "viewed_at": row[1].isoformat() if row[1] else None,
            }
        )

    return PaginatedResponse(
        items=items[:20],
        total=total,
        page=1,
        per_page=20,
        pages=(total + 20 - 1) // 20,
    )
