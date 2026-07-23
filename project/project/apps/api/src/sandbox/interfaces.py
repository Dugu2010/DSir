from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass
class ExecutionRequest:
    code: str
    language: str
    timeout_ms: int = 3000
    memory_limit_mb: int = 128


@dataclass
class ExecutionResponse:
    stdout: str
    stderr: str
    exit_code: int
    execution_time_ms: int
    is_timeout: bool = False


class CodeSandbox(Protocol):
    async def execute(self, request: ExecutionRequest) -> ExecutionResponse: ...
