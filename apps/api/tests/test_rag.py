import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.content import Concept, Course
from src.services.rag import RAGService


@pytest.fixture
def rag_service(db_session: AsyncSession) -> RAGService:
    from src.ai.manager import get_ai_manager

    return RAGService(db_session, get_ai_manager())


@pytest.mark.asyncio
async def test_index_and_search(rag_service: RAGService, db_session: AsyncSession) -> None:
    chunk = await rag_service.index_chunk(
        content="Python lists are ordered, mutable collections.",
        chunk_type="lesson",
    )
    await db_session.commit()

    results = await rag_service.search("ordered collections", limit=5)
    assert len(results) >= 1
    assert chunk.id in {r.id for r in results}


@pytest.mark.asyncio
async def test_search_for_user(rag_service: RAGService, db_session: AsyncSession) -> None:
    from src.models.learning import ConceptMastery
    from src.models.user import User

    user = User(email="rag@example.com", hashed_password="secret")
    course = Course(
        slug="python", title="Python", technology="python", programming_language="python", difficulty="beginner"
    )
    db_session.add_all([user, course])
    await db_session.flush()

    concept = Concept(course_id=course.id, slug="lists", title="Lists")
    db_session.add(concept)
    await db_session.flush()

    db_session.add(ConceptMastery(user_id=user.id, concept_id=concept.id, score=50, confidence=40))
    await db_session.flush()

    chunk = await rag_service.index_chunk(
        content="Python list comprehensions provide a concise way to create lists.",
        concept_id=concept.id,
        course_id=course.id,
    )
    await db_session.commit()

    results = await rag_service.search_for_user(user.id, "lists")
    assert any(r.id == chunk.id for r in results)
