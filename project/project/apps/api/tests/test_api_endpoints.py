from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.assessment import Project
from src.models.content import Concept, Course, Lesson, Roadmap


async def test_list_roadmaps(auth_client: TestClient, db_session: AsyncSession) -> None:
    db_session.add(
        Roadmap(
            id=uuid4(),
            slug="test-roadmap",
            title="Test Roadmap",
            is_published=True,
        )
    )
    db_session.add(
        Roadmap(
            id=uuid4(),
            slug="unpublished",
            title="Unpublished",
            is_published=False,
        )
    )
    await db_session.flush()

    response = auth_client.get("/api/v1/roadmaps/")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["slug"] == "test-roadmap"


def test_get_roadmap_not_found(auth_client: TestClient) -> None:
    response = auth_client.get(f"/api/v1/roadmaps/{uuid4()}")
    assert response.status_code == 404


async def test_list_courses(auth_client: TestClient, db_session: AsyncSession) -> None:
    db_session.add(
        Course(
            id=uuid4(),
            slug="python",
            title="Python",
            technology="python",
            is_published=True,
            programming_language="python",
            difficulty="beginner",
        )
    )
    await db_session.flush()

    response = auth_client.get("/api/v1/courses/")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["items"]) == 1


async def test_get_course(auth_client: TestClient, db_session: AsyncSession) -> None:
    course_id = uuid4()
    db_session.add(
        Course(
            id=course_id,
            slug="python",
            title="Python",
            technology="python",
            is_published=True,
            programming_language="python",
            difficulty="beginner",
        )
    )
    await db_session.flush()

    response = auth_client.get(f"/api/v1/courses/{course_id}")
    assert response.status_code == 200
    assert response.json()["slug"] == "python"


async def test_list_course_concepts(auth_client: TestClient, db_session: AsyncSession) -> None:
    course_id = uuid4()
    db_session.add(
        Course(
            id=course_id,
            slug="python",
            title="Python",
            technology="python",
            programming_language="python",
            is_published=True,
            difficulty="beginner",
        )
    )
    await db_session.flush()

    db_session.add(Concept(course_id=course_id, slug="variables", title="Variables"))
    await db_session.flush()

    response = auth_client.get(f"/api/v1/courses/{course_id}/concepts")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["items"]) == 1


async def test_get_concept_by_slug(auth_client: TestClient, db_session: AsyncSession) -> None:
    course_id = uuid4()
    db_session.add(
        Course(
            id=course_id,
            slug="python",
            title="Python",
            technology="python",
            programming_language="python",
            is_published=True,
            difficulty="beginner",
        )
    )
    await db_session.flush()

    db_session.add(Concept(course_id=course_id, slug="variables", title="Variables"))
    await db_session.flush()

    response = auth_client.get(f"/api/v1/courses/{course_id}/concepts/variables")
    assert response.status_code == 200
    assert response.json()["slug"] == "variables"


async def test_create_enrollment(auth_client: TestClient, db_session: AsyncSession) -> None:
    course_id = uuid4()
    db_session.add(
        Course(
            id=course_id,
            slug="python",
            title="Python",
            technology="python",
            programming_language="python",
            is_published=True,
            difficulty="beginner",
        )
    )
    await db_session.flush()

    response = auth_client.post(
        "/api/v1/enrollments/",
        json={"course_id": str(course_id), "roadmap_id": None},
    )
    assert response.status_code == 201
    assert response.json()["status"] == "active"


async def test_create_submission(auth_client: TestClient, db_session: AsyncSession) -> None:
    response = auth_client.post(
        "/api/v1/submissions/",
        json={
            "submission_type": "code",
            "payload": {"code": "print('hello')"},
            "lesson_id": None,
            "concept_id": None,
        },
    )
    assert response.status_code == 201
    assert response.json()["submission_type"] == "code"


async def test_record_mastery(auth_client: TestClient, db_session: AsyncSession) -> None:
    course_id = uuid4()
    concept_id = uuid4()
    db_session.add(
        Course(
            id=course_id,
            slug="python",
            title="Python",
            technology="python",
            programming_language="python",
            is_published=True,
            difficulty="beginner",
        )
    )
    db_session.add(Concept(id=concept_id, course_id=course_id, slug="variables", title="Variables"))
    await db_session.flush()

    response = auth_client.post(f"/api/v1/mastery/record?concept_id={concept_id}&is_correct=true")
    assert response.status_code == 200
    data = response.json()
    assert data["score"] > 0
    assert data["attempts"] == 1


async def test_revision_submit_review(auth_client: TestClient, db_session: AsyncSession) -> None:
    course_id = uuid4()
    concept_id = uuid4()
    db_session.add(
        Course(
            id=course_id,
            slug="python",
            title="Python",
            technology="python",
            programming_language="python",
            is_published=True,
            difficulty="beginner",
        )
    )
    db_session.add(Concept(id=concept_id, course_id=course_id, slug="variables", title="Variables"))
    await db_session.flush()

    response = auth_client.post(
        "/api/v1/revision/review",
        json={"concept_id": str(concept_id), "quality": 4},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["new_interval_days"] > 0


def test_ai_chat(auth_client: TestClient) -> None:
    response = auth_client.post(
        "/api/v1/ai/chat",
        json={"messages": [{"role": "user", "content": "Hello"}], "mode": "mentor"},
    )
    assert response.status_code == 200
    assert "mock" in response.json()["content"].lower()


def test_ai_code_review(auth_client: TestClient) -> None:
    response = auth_client.post(
        "/api/v1/ai/code-review",
        json={"code": "print('hello')", "language": "python"},
    )
    assert response.status_code == 200
    assert response.json()["feedback"]


def test_execute_code(auth_client: TestClient) -> None:
    response = auth_client.post(
        "/api/v1/execution/run",
        json={"code": "print('hello')", "language": "python"},
    )
    assert response.status_code == 200
    assert response.json()["exit_code"] == 0


def test_get_profile_not_found(auth_client: TestClient) -> None:
    response = auth_client.get("/api/v1/profiles/me")
    # Profile is not created for the seeded user in conftest, so 404
    assert response.status_code == 404


async def test_list_lessons(auth_client: TestClient, db_session: AsyncSession) -> None:
    course_id = uuid4()
    concept_id = uuid4()
    db_session.add(
        Course(
            id=course_id,
            slug="python",
            title="Python",
            technology="python",
            programming_language="python",
            is_published=True,
            difficulty="beginner",
        )
    )
    db_session.add(Concept(id=concept_id, course_id=course_id, slug="variables", title="Variables"))
    db_session.add(
        Lesson(
            id=uuid4(),
            concept_id=concept_id,
            slug="intro",
            title="Introduction",
            content={"text": "Hello"},
            position=1,
        )
    )
    await db_session.flush()

    response = auth_client.get(f"/api/v1/lessons/concept/{concept_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["items"]) == 1


async def test_get_lesson(auth_client: TestClient, db_session: AsyncSession) -> None:
    lesson_id = uuid4()
    concept_id = uuid4()
    course_id = uuid4()
    db_session.add(
        Course(
            id=course_id,
            slug="python",
            title="Python",
            technology="python",
            programming_language="python",
            is_published=True,
            difficulty="beginner",
        )
    )
    db_session.add(Concept(id=concept_id, course_id=course_id, slug="variables", title="Variables"))
    db_session.add(
        Lesson(
            id=lesson_id,
            concept_id=concept_id,
            slug="intro",
            title="Introduction",
            content={"text": "Hello"},
            position=1,
        )
    )
    await db_session.flush()

    response = auth_client.get(f"/api/v1/lessons/{lesson_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Introduction"


async def test_create_roadmap(auth_client: TestClient, db_session: AsyncSession) -> None:
    response = auth_client.post(
        "/api/v1/roadmaps/",
        json={"slug": "new-roadmap", "title": "New Roadmap", "is_published": False},
    )
    assert response.status_code == 201
    assert response.json()["slug"] == "new-roadmap"


async def test_list_projects(auth_client: TestClient, db_session: AsyncSession) -> None:
    course_id = uuid4()
    db_session.add(
        Course(
            id=course_id,
            slug="python",
            title="Python",
            technology="python",
            programming_language="python",
            is_published=True,
            difficulty="beginner",
        )
    )
    db_session.add(
        Project(
            id=uuid4(),
            course_id=course_id,
            slug="calculator",
            title="Calculator App",
        )
    )
    await db_session.flush()

    response = auth_client.get(f"/api/v1/projects/course/{course_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["items"]) == 1
