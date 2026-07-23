from __future__ import annotations

import random
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.ai.manager import AIManager
from src.ai.prompts import PromptManager
from src.ai.protocols import Message, Role
from src.models.revision import RevisionProblemQueue, RevisionSchedule, RevisionSession

if TYPE_CHECKING:
    pass


class RevisionEngine:
    def __init__(self, db: AsyncSession, ai: AIManager | None = None):
        self.db = db
        self.ai = ai

    async def get_schedule(self, user_id: UUID, concept_id: UUID) -> RevisionSchedule:
        result = await self.db.execute(
            select(RevisionSchedule).where(
                RevisionSchedule.user_id == user_id,
                RevisionSchedule.concept_id == concept_id,
            )
        )
        schedule = result.scalar_one_or_none()
        if schedule is None:
            schedule = RevisionSchedule(
                user_id=user_id,
                concept_id=concept_id,
                interval_days=1,
                ease_factor=2.5,
                repetitions=0,
                due_at=datetime.now(UTC),
            )
            self.db.add(schedule)
        return schedule

    async def schedule_review(self, user_id: UUID, concept_id: UUID, quality: int) -> RevisionSchedule:
        schedule = await self.get_schedule(user_id, concept_id)
        quality = max(0, min(5, quality))

        if quality < 3:
            schedule.repetitions = 0
            schedule.interval_days = 1
        else:
            schedule.repetitions += 1
            if schedule.repetitions == 1:
                schedule.interval_days = 1
            elif schedule.repetitions == 2:
                schedule.interval_days = 6
            else:
                schedule.interval_days = max(1, int(schedule.interval_days * schedule.ease_factor))

        ease_delta = 0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)
        schedule.ease_factor = max(1.3, schedule.ease_factor + ease_delta)
        schedule.last_reviewed_at = datetime.now(UTC)
        schedule.due_at = datetime.now(UTC) + timedelta(days=schedule.interval_days)
        await self.db.flush()
        return schedule

    async def get_due_concepts(self, user_id: UUID, limit: int = 20) -> list[RevisionSchedule]:
        result = await self.db.execute(
            select(RevisionSchedule)
            .where(
                RevisionSchedule.user_id == user_id,
                RevisionSchedule.due_at <= datetime.now(UTC),
            )
            .order_by(RevisionSchedule.due_at)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def build_revision_queue(self, user_id: UUID, limit: int = 10) -> list[RevisionSchedule]:
        due = await self.get_due_concepts(user_id, limit=limit * 2)
        return due[:limit]

    async def generate_problem(
        self,
        user_id: UUID,
        concept_id: UUID,
        difficulty: str = "medium",
        mistakes: str = "none",
        concept_title: str = "",
    ) -> RevisionProblemQueue:
        """Generate or refresh a revision problem for active recall.

        If an AI manager is configured, an AI-generated problem is produced.
        Otherwise a generic problem is created.
        """
        problem_text = f"Explain {concept_title or 'this concept'} in your own words."
        if self.ai is not None:
            prompt = PromptManager.get("revision-problem").render(
                concept=concept_title or "the concept",
                difficulty=difficulty,
                mistakes=mistakes,
            )
            response = await self.ai.generate([Message(role=Role.USER, content=prompt)])
            problem_text = response.content

        problem = RevisionProblemQueue(
            user_id=user_id,
            concept_id=concept_id,
            problem_data={
                "type": "active_recall",
                "difficulty": difficulty,
                "question": problem_text,
                "hints": [],
            },
            expires_at=datetime.now(UTC) + timedelta(hours=24),
        )
        self.db.add(problem)
        await self.db.flush()
        return problem

    async def get_active_recall_problem(
        self, user_id: UUID, concept_id: UUID, concept_title: str = ""
    ) -> RevisionProblemQueue:
        """Return a cached active-recall problem or generate a new one."""
        result = await self.db.execute(
            select(RevisionProblemQueue)
            .where(
                RevisionProblemQueue.user_id == user_id,
                RevisionProblemQueue.concept_id == concept_id,
                RevisionProblemQueue.expires_at > datetime.now(UTC),
            )
            .order_by(RevisionProblemQueue.generated_at.desc())
            .limit(1)
        )
        problem = result.scalar_one_or_none()
        if problem is None:
            difficulty = random.choice(["easy", "medium", "hard"])
            problem = await self.generate_problem(
                user_id, concept_id, difficulty=difficulty, concept_title=concept_title
            )
        return problem

    async def start_active_recall_session(
        self, user_id: UUID, concept_ids: list[UUID] | None = None
    ) -> dict[str, object]:
        """Start an active recall session and return problems for the due concepts."""
        if concept_ids:
            schedules: list[RevisionSchedule] = []
            for cid in concept_ids:
                schedule = await self.get_schedule(user_id, cid)
                schedules.append(schedule)
        else:
            schedules = await self.build_revision_queue(user_id, limit=10)

        problems: list[dict[str, object]] = []
        for schedule in schedules:
            problem = await self.get_active_recall_problem(user_id, schedule.concept_id)
            problems.append(
                {
                    "concept_id": str(schedule.concept_id),
                    "due_at": schedule.due_at.isoformat() if schedule.due_at else None,
                    "problem": problem.problem_data,
                }
            )

        session = RevisionSession(
            user_id=user_id,
            concepts=[s.concept_id for s in schedules],
        )
        self.db.add(session)
        await self.db.flush()

        return {
            "session_id": str(session.id),
            "problems": problems,
        }

    async def get_analytics(self, user_id: UUID) -> dict[str, object]:
        """Return revision analytics for the learner."""
        due_count = await self.db.scalar(
            select(func.count(RevisionSchedule.id)).where(
                RevisionSchedule.user_id == user_id,
                RevisionSchedule.due_at <= datetime.now(UTC),
            )
        )
        total_scheduled = await self.db.scalar(
            select(func.count(RevisionSchedule.id)).where(
                RevisionSchedule.user_id == user_id,
            )
        )
        sessions_count = await self.db.scalar(
            select(func.count(RevisionSession.id)).where(
                RevisionSession.user_id == user_id,
            )
        )
        return {
            "due_count": due_count or 0,
            "total_scheduled": total_scheduled or 0,
            "sessions_count": sessions_count or 0,
        }
