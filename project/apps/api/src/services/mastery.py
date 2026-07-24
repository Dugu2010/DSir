from __future__ import annotations

import math
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.learning import ConceptMastery

if TYPE_CHECKING:
    pass


class MasteryEngine:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_mastery(self, user_id: UUID, concept_id: UUID) -> ConceptMastery:
        result = await self.db.execute(
            select(ConceptMastery)
            .where(
                ConceptMastery.user_id == user_id,
                ConceptMastery.concept_id == concept_id,
            )
            .with_for_update()
        )
        mastery = result.scalar_one_or_none()
        if mastery is None:
            mastery = ConceptMastery(
                user_id=user_id,
                concept_id=concept_id,
                score=0,
                confidence=0,
                attempts=0,
                correct_streak=0,
            )
            self.db.add(mastery)
            await self.db.flush()
        return mastery

    async def record_attempt(
        self,
        user_id: UUID,
        concept_id: UUID,
        is_correct: bool,
        difficulty: float = 1.0,
        source: str = "exercise",
    ) -> ConceptMastery:
        source_weights = {
            "exercise": 1.0,
            "quiz": 0.8,
            "revision": 1.2,
            "project": 1.5,
            "assessment": 2.0,
        }
        weight = source_weights.get(source, 1.0)

        mastery = await self.get_mastery(user_id, concept_id)
        mastery.attempts += 1
        if is_correct:
            mastery.correct_streak += 1
            gain = self._calculate_gain(mastery, difficulty * weight)
            mastery.score = min(100, mastery.score + gain)
            mastery.confidence = min(100, mastery.confidence + self._confidence_gain(mastery))
        else:
            mastery.correct_streak = 0
            penalty = self._calculate_penalty(mastery)
            mastery.score = max(0, mastery.score - penalty)
            mastery.confidence = max(0, mastery.confidence - 10)

        mastery.last_reviewed_at = datetime.now(UTC)
        mastery.next_review_at = datetime.now(UTC) + timedelta(days=1)
        mastery.updated_at = datetime.now(UTC)
        await self.db.flush()
        return mastery

    async def record_score(
        self,
        user_id: UUID,
        concept_id: UUID,
        score: int,
        source: str = "assessment",
        difficulty: float = 1.0,
    ) -> ConceptMastery:
        """Record a 0-100 score from a project or assessment."""
        mastery = await self.get_mastery(user_id, concept_id)
        normalized = max(0, min(100, score))
        weight = {"project": 1.5, "assessment": 2.0}.get(source, 1.0) * difficulty
        current = mastery.score
        # Move score toward the new score, weighted by source weight
        new_score = (current * (1 - 0.1 * weight)) + (normalized * 0.1 * weight)
        mastery.score = max(0, min(100, int(new_score)))
        mastery.attempts += 1
        if normalized >= 80:
            mastery.correct_streak += 1
        else:
            mastery.correct_streak = 0
        mastery.confidence = min(100, mastery.confidence + self._confidence_gain(mastery))
        mastery.last_reviewed_at = datetime.now(UTC)
        mastery.next_review_at = datetime.now(UTC) + timedelta(days=1)
        mastery.updated_at = datetime.now(UTC)
        await self.db.flush()
        return mastery

    def _calculate_gain(self, mastery: ConceptMastery, difficulty: float) -> int:
        base_gain = int(10 * difficulty)
        streak_bonus = min(mastery.correct_streak * 2, 20)
        diminishing = max(0, (100 - mastery.score) // 10)
        return min(base_gain + streak_bonus, base_gain + diminishing)

    def _calculate_penalty(self, mastery: ConceptMastery) -> int:
        confidence_factor = 1 + (mastery.confidence / 100)
        return int(10 * confidence_factor)

    def _confidence_gain(self, mastery: ConceptMastery) -> int:
        # Confidence grows faster early, then plateaus
        if mastery.confidence >= 90:
            return 1
        if mastery.confidence >= 70:
            return 3
        return 5

    async def apply_decay(self, user_id: UUID, concept_id: UUID) -> ConceptMastery:
        mastery = await self.get_mastery(user_id, concept_id)
        if mastery.last_reviewed_at is None:
            return mastery

        days_since_review = (datetime.now(UTC) - mastery.last_reviewed_at).days
        if days_since_review <= 0:
            return mastery

        # Decay slower for high confidence
        lambda_decay = 0.03 + max(0, 0.07 - (mastery.confidence / 1000))
        confidence_decay = math.exp(-lambda_decay * days_since_review * 0.5)
        score_decay = math.exp(-lambda_decay * days_since_review)

        mastery.score = int(mastery.score * score_decay)
        mastery.confidence = int(mastery.confidence * confidence_decay)
        mastery.next_review_at = None
        mastery.updated_at = datetime.now(UTC)
        await self.db.flush()
        return mastery

    async def get_strengths_and_weaknesses(self, user_id: UUID) -> tuple[list[ConceptMastery], list[ConceptMastery]]:
        result = await self.db.execute(select(ConceptMastery).where(ConceptMastery.user_id == user_id))
        masteries = list(result.scalars().all())
        strengths = [m for m in masteries if m.score >= 80 and m.confidence >= 70]
        weaknesses = [m for m in masteries if m.score < 50 or m.confidence < 40]
        return strengths, weaknesses

    async def learning_velocity(self, user_id: UUID, window_days: int = 30) -> float:
        """Average mastery gain per day over the last window_days."""
        from src.models.learning import ConceptMastery

        cutoff = datetime.now(UTC) - timedelta(days=window_days)
        result = await self.db.execute(
            select(ConceptMastery).where(
                ConceptMastery.user_id == user_id,
                ConceptMastery.updated_at >= cutoff,
            )
        )
        masteries = result.scalars().all()
        if not masteries:
            return 0.0
        return sum(m.score for m in masteries) / window_days
