from __future__ import annotations

import os
from collections.abc import AsyncGenerator
from typing import Any

import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool

from src.core.config import settings
from src.db.base import Base
from src.db.session import get_db
from src.main import app

# Disable rate limiting in tests; individual test cases can opt-in by overriding.
settings.RATE_LIMIT_ENABLED = False

TEST_DB_PATH = os.path.join(os.path.dirname(__file__), ".test_db.sqlite")
TEST_DATABASE_URL = f"sqlite+aiosqlite:///{TEST_DB_PATH}"


@pytest_asyncio.fixture(scope="session")
def test_engine() -> Any:
    engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)
    return engine


@pytest_asyncio.fixture(scope="session", autouse=True)
async def create_test_tables(test_engine: AsyncEngine) -> AsyncGenerator[None, None]:
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session(test_engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    conn = await test_engine.connect()
    session = AsyncSession(bind=conn, expire_on_commit=False)

    yield session

    await session.close()
    # Cleanup all data after each test for isolation
    async with test_engine.begin() as cleanup_conn:
        for table in reversed(Base.metadata.sorted_tables):
            await cleanup_conn.execute(table.delete())
    await conn.close()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[TestClient, None]:
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def auth_client(db_session: AsyncSession) -> AsyncGenerator[TestClient, None]:
    from src.core.security import get_password_hash
    from src.models.user import User, UserRole

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    test_client = TestClient(app)

    # Seed a test user with admin/content_creator roles
    user = User(email="test@example.com", hashed_password=get_password_hash("Password1"))
    db_session.add(user)
    await db_session.flush()
    db_session.add_all(
        [
            UserRole(user_id=user.id, role="learner"),
            UserRole(user_id=user.id, role="admin"),
            UserRole(user_id=user.id, role="content_creator"),
        ]
    )
    await db_session.commit()

    login = test_client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "Password1"},
    )
    token = login.json()["access_token"]
    test_client.headers["Authorization"] = f"Bearer {token}"

    yield test_client

    app.dependency_overrides.clear()
