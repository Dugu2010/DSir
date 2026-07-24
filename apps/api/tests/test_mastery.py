import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.content import Concept, Course
from src.models.user import User
from src.services.mastery import MasteryEngine


@pytest.fixture
def mastery_engine(db_session: AsyncSession) -> MasteryEngine:
    return MasteryEngine(db_session)


@pytest.mark.asyncio
async def test_record_correct_attempt(mastery_engine: MasteryEngine, db_session: AsyncSession) -> None:
    user = User(email="learner@example.com", hashed_password="secret")
    course = Course(
        slug="python", title="Python", technology="python", programming_language="python", difficulty="beginner"
    )
    db_session.add_all([user, course])
    await db_session.flush()

    concept = Concept(course_id=course.id, slug="variables", title="Variables")
    db_session.add(concept)
    await db_session.flush()

    mastery = await mastery_engine.record_attempt(user.id, concept.id, True)
    assert mastery.score > 0
    assert mastery.attempts == 1
