from __future__ import annotations

import dataclasses
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.ai.manager import AIManager
from src.ai.prompts import PromptManager
from src.ai.protocols import Message, Role
from src.models.execution import ExecutionHistory
from src.sandbox.interfaces import CodeSandbox, ExecutionRequest
from src.schemas.execution import ExecutionRequest as ExecutionRequestSchema
from src.schemas.execution import ExecutionResponse as ExecutionResponseSchema


class ExecutionService:
    """Service for running code, logging history, and requesting AI reviews."""

    MAX_OUTPUT_LENGTH = 10_000

    def __init__(self, db: AsyncSession, sandbox: CodeSandbox, ai: AIManager):
        self.db = db
        self.sandbox = sandbox
        self.ai = ai

    @classmethod
    def _truncate(cls, text: str | None) -> str:
        if text is None:
            return ""
        return text[: cls.MAX_OUTPUT_LENGTH]

    async def execute_and_log(
        self,
        user_id: UUID | None,
        request: ExecutionRequestSchema,
    ) -> tuple[ExecutionResponseSchema, UUID]:
        """Execute code, log the result, and optionally queue a background AI review.

        Returns the execution result and the persisted history entry id.
        """
        internal_request = ExecutionRequest(
            code=request.code,
            language=request.language,
            timeout_ms=request.timeout_ms,
            memory_limit_mb=request.memory_limit_mb,
        )

        history = ExecutionHistory(
            user_id=user_id,
            language=request.language,
            code=request.code,
            requested_timeout_ms=request.timeout_ms,
            requested_memory_mb=request.memory_limit_mb,
            provider=self.sandbox.__class__.__name__,
            status="running",
        )
        self.db.add(history)
        await self.db.flush()

        raw_result = await self.sandbox.execute(internal_request)
        result = ExecutionResponseSchema(**dataclasses.asdict(raw_result))

        history.stdout = self._truncate(raw_result.stdout)
        history.stderr = self._truncate(raw_result.stderr)
        history.exit_code = raw_result.exit_code
        history.execution_time_ms = raw_result.execution_time_ms
        history.is_timeout = raw_result.is_timeout
        history.status = "success" if raw_result.exit_code == 0 else "error"
        await self.db.commit()

        return result, history.id

    async def review_code(self, history_id: UUID, code: str, language: str) -> dict[str, str]:
        """Generate an AI review synchronously and store it on the history record."""
        prompt = PromptManager.get("code-review").render(
            language=language,
            code=code,
            context="Review execution output and correctness.",
        )
        response = await self.ai.generate([Message(role=Role.USER, content=prompt)])
        review = {"feedback": response.content, "model": response.model}
        history = await self.db.get(ExecutionHistory, history_id)
        if history is not None:
            history.ai_review = review
            await self.db.commit()
        return review

    async def get_history(
        self,
        user_id: UUID | None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[ExecutionHistory]:
        from sqlalchemy import select

        query = select(ExecutionHistory)
        if user_id is not None:
            query = query.where(ExecutionHistory.user_id == user_id)
        query = query.order_by(ExecutionHistory.created_at.desc()).limit(limit).offset(offset)
        result = await self.db.execute(query)
        return list(result.scalars().all())
