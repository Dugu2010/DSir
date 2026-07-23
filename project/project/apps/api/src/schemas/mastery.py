from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ConceptMasteryRead(BaseModel):
    concept_id: uuid.UUID
    score: int
    confidence: int
    attempts: int
    correct_streak: int
    last_reviewed_at: datetime | None = None
    next_review_at: datetime | None = None
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class StrengthsWeaknesses(BaseModel):
    strengths: list[ConceptMasteryRead]
    weaknesses: list[ConceptMasteryRead]
