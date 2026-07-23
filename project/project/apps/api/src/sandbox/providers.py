from __future__ import annotations

import httpx

from src.core.config import settings
from src.sandbox.interfaces import CodeSandbox, ExecutionRequest, ExecutionResponse


class MockSandbox(CodeSandbox):
    """In-memory sandbox for testing and local development."""

    async def execute(self, request: ExecutionRequest) -> ExecutionResponse:
        language = request.language.lower()
        if language in {"html", "css", "js", "javascript"}:
            return ExecutionResponse(
                stdout=request.code,
                stderr="",
                exit_code=0,
                execution_time_ms=1,
            )
        return ExecutionResponse(
            stdout="Mock execution output",
            stderr="",
            exit_code=0,
            execution_time_ms=1,
        )


class PistonSandbox(CodeSandbox):
    """Piston-based sandbox providing isolated code execution."""

    def __init__(self, base_url: str | None = None):
        self.base_url = base_url or settings.PISTON_BASE_URL or "http://localhost:2000"

    async def execute(self, request: ExecutionRequest) -> ExecutionResponse:
        # Clamp limits to safe defaults if not provided
        timeout_ms = max(1, min(request.timeout_ms, settings.EXECUTION_TIMEOUT_MS))
        memory_mb = max(1, min(request.memory_limit_mb, settings.EXECUTION_MEMORY_MB))

        payload: dict[str, object] = {
            "language": request.language,
            "version": "*",
            "files": [{"content": request.code}],
            "run_timeout": timeout_ms,
            "compile_timeout": timeout_ms,
        }
        # Piston v2 optionally supports run_memory_limit and compile_memory_limit in bytes
        memory_bytes = memory_mb * 1024 * 1024
        payload.update(
            {
                "run_memory_limit": memory_bytes,
                "compile_memory_limit": memory_bytes,
            }
        )

        try:
            async with httpx.AsyncClient(timeout=timeout_ms / 1000 + 1.0) as client:
                response = await client.post(f"{self.base_url}/api/v2/execute", json=payload)
                response.raise_for_status()
                data = response.json()
        except httpx.TimeoutException:
            return ExecutionResponse(
                stdout="",
                stderr="Execution timed out",
                exit_code=124,
                execution_time_ms=timeout_ms,
                is_timeout=True,
            )
        except httpx.HTTPError as exc:
            return ExecutionResponse(
                stdout="",
                stderr=f"Sandbox request failed: {exc}",
                exit_code=503,
                execution_time_ms=0,
                is_timeout=False,
            )

        run = data.get("run", {})
        stdout = run.get("stdout", "")[:10000]
        stderr = run.get("stderr", "")[:10000]
        return ExecutionResponse(
            stdout=stdout,
            stderr=stderr,
            exit_code=run.get("code", 1),
            execution_time_ms=int(run.get("cpuUsage", 0) or 0),
            is_timeout=False,
        )
