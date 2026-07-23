import pytest

from src.sandbox.interfaces import ExecutionRequest
from src.sandbox.providers import MockSandbox


@pytest.mark.asyncio
async def test_mock_sandbox_execute() -> None:
    sandbox = MockSandbox()
    request = ExecutionRequest(code="print('hello')", language="python")
    response = await sandbox.execute(request)
    assert response.exit_code == 0
    assert "Mock" in response.stdout
