import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.content import Concept, Course
from src.models.user import User
from src.services.revision import RevisionEngine


@pytest.fixture
def revision_engine(db_session: AsyncSession) -> RevisionEngine:
    return RevisionEngine(db_session)


@pytest.mark.asyncio
async def test_schedule_review(revision_engine: RevisionEngine, db_session: AsyncSession) -> None:
    user = User(email="learner@example.com", hashed_password="secret")
    course = Course(
        slug="python", title="Python", technology="python", programming_language="python", difficulty="beginner"
    )
    db_session.add_all([user, course])
    await db_session.flush()

    concept = Concept(course_id=course.id, slug="variables", title="Variables")
    db_session.add(concept)
    await db_session.flush()

    schedule = await revision_engine.schedule_review(user.id, concept.id, quality=4)
    assert schedule.interval_days > 0
