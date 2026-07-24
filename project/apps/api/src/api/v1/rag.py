from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.ai.manager import get_ai_manager
from src.core.dependencies import get_current_active_user, require_content_creator
from src.db.session import get_db
from src.models.learning import Enrollment
from src.models.user import User
from src.schemas.rag import (
    CourseKnowledgeRequest,
    KnowledgeChunkCreate,
    KnowledgeChunkRead,
    LearnerMemoryRequest,
    SearchRequest,
    SearchResponse,
)
from src.services.rag import RAGService

router = APIRouter()


async def _get_rag_service(
    db: AsyncSession = Depends(get_db),
) -> RAGService:
    return RAGService(db, get_ai_manager())


@router.post("/index", response_model=KnowledgeChunkRead, status_code=status.HTTP_201_CREATED)
async def index_knowledge(
    data: KnowledgeChunkCreate,
    current_user: User = Depends(require_content_creator),
    service: RAGService = Depends(_get_rag_service),
    db: AsyncSession = Depends(get_db),
) -> KnowledgeChunkRead:
    chunk = await service.index_chunk(
        content=data.content,
        chunk_type=data.chunk_type,
        course_id=data.course_id,
        concept_id=data.concept_id,
        meta=data.meta,
    )
    await db.commit()
    return KnowledgeChunkRead.model_validate(chunk)


@router.post("/search", response_model=SearchResponse)
async def search_knowledge(
    data: SearchRequest,
    current_user: User = Depends(get_current_active_user),
    service: RAGService = Depends(_get_rag_service),
    db: AsyncSession = Depends(get_db),
) -> SearchResponse:
    if data.course_id is not None:
        enrollment = await db.execute(
            select(Enrollment).where(
                Enrollment.user_id == current_user.id,
                Enrollment.course_id == data.course_id,
            )
        )
        if not enrollment.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enrolled")

    results = await service.search(
        query=data.query,
        limit=data.limit,
        course_id=data.course_id,
        concept_id=data.concept_id,
    )
    return SearchResponse(
        query=data.query,
        results=[KnowledgeChunkRead.model_validate(r) for r in results],
    )


@router.post("/memory", response_model=SearchResponse)
async def search_learner_memory(
    data: LearnerMemoryRequest,
    current_user: User = Depends(get_current_active_user),
    service: RAGService = Depends(_get_rag_service),
) -> SearchResponse:
    results = await service.search_for_user(current_user.id, data.query, limit=data.limit)
    return SearchResponse(
        query=data.query,
        results=[KnowledgeChunkRead.model_validate(r) for r in results],
    )


@router.post("/course-knowledge", response_model=SearchResponse)
async def search_course_knowledge(
    data: CourseKnowledgeRequest,
    current_user: User = Depends(get_current_active_user),
    service: RAGService = Depends(_get_rag_service),
    db: AsyncSession = Depends(get_db),
) -> SearchResponse:
    enrollment = await db.execute(
        select(Enrollment).where(
            Enrollment.user_id == current_user.id,
            Enrollment.course_id == data.course_id,
        )
    )
    if not enrollment.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enrolled")

    results = await service.course_knowledge(data.course_id, data.query, limit=data.limit)
    return SearchResponse(
        query=data.query,
        results=[KnowledgeChunkRead.model_validate(r) for r in results],
    )
