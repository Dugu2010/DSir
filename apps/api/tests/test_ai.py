import pytest

from src.ai.manager import AIManager, get_ai_manager
from src.ai.protocols import Message, Role
from src.ai.providers import MockProvider


@pytest.mark.asyncio
async def test_mock_provider_generate() -> None:
    provider = MockProvider()
    response = await provider.generate([Message(role=Role.USER, content="Hello")])
    assert "mock" in response.content.lower()


@pytest.mark.asyncio
async def test_ai_manager_generate() -> None:
    manager = AIManager(MockProvider())
    response = await manager.generate([Message(role=Role.USER, content="Hello")])
    assert "mock" in response.content.lower()


def test_get_ai_manager() -> None:
    manager = get_ai_manager("mock")
    assert manager is not None
