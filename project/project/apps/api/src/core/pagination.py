from __future__ import annotations

from typing import Any

from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from src.schemas.common import PaginatedResponse, PaginationParams


async def paginated_response(
    db: AsyncSession,
    query: Select[tuple[Any]],
    pagination: PaginationParams,
    schema: type[BaseModel],
) -> PaginatedResponse:
    total_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = total_result.scalar_one()

    paginated = query.offset((pagination.page - 1) * pagination.per_page).limit(pagination.per_page)
    result = await db.execute(paginated)
    items = result.scalars().all()

    return PaginatedResponse(
        items=[schema.model_validate(item).model_dump() for item in items],
        total=total,
        page=pagination.page,
        per_page=pagination.per_page,
        pages=(total + pagination.per_page - 1) // pagination.per_page,
    )
