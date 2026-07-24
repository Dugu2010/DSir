import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.content import Concept, Course
from src.services.knowledge_graph import KnowledgeGraph


@pytest.fixture
def knowledge_graph(db_session: AsyncSession) -> KnowledgeGraph:
    return KnowledgeGraph(db_session)


@pytest.mark.asyncio
async def test_topological_sort(knowledge_graph: KnowledgeGraph, db_session: AsyncSession) -> None:
    course = Course(
        slug="python", title="Python", technology="python", programming_language="python", difficulty="beginner"
    )
    db_session.add(course)
    await db_session.flush()

    c1 = Concept(course_id=course.id, slug="variables", title="Variables")
    c2 = Concept(course_id=course.id, slug="functions", title="Functions", prerequisites=[c1.id])
    db_session.add_all([c1, c2])
    await db_session.flush()

    ordered = await knowledge_graph.topological_sort(course.id)
    assert ordered == [c1.id, c2.id]
