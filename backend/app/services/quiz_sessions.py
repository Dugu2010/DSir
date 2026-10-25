"""Attempt limits, per-question timing, and XP accounting for quizzes.

The rules live here as pure helpers so they can be unit-tested without a
database and reused by every quiz endpoint:

* an attempt is a single server-side object that starts, then is either
  submitted or expires unanswered (only those two states spend an attempt);
* a submission is only accepted inside the quiz's time limit plus a short
  network grace window;
* reported per-question times are clamped against the wall-clock the server
  actually observed, so a client cannot invent plausible-looking timings;
* XP is granted for the *improvement* over the learner's previous best score,
  never for replaying the same quiz, so retakes cannot farm XP.
"""

from __future__ import annotations

import math
from datetime import datetime, timedelta, timezone
from typing import Iterable, Mapping, Optional

# Network/clock slack allowed past the time limit before a submission is late.
QUIZ_LATE_SUBMIT_GRACE_SECONDS = 60


def as_utc(value: datetime) -> datetime:
    """Normalise a database datetime (often naive) to timezone-aware UTC."""
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def elapsed_seconds(
    started_at: Optional[datetime],
    now: Optional[datetime] = None,
) -> int:
    """Whole seconds since the attempt started (0 when unknown)."""
    if started_at is None:
        return 0
    current = now or datetime.now(timezone.utc)
    return max(0, int((as_utc(current) - as_utc(started_at)).total_seconds()))


def time_limit_seconds(time_limit_minutes: Optional[int]) -> Optional[int]:
    if not time_limit_minutes or time_limit_minutes <= 0:
        return None
    return int(time_limit_minutes) * 60


def attempt_expires_at(
    started_at: Optional[datetime],
    time_limit_minutes: Optional[int],
) -> Optional[datetime]:
    limit = time_limit_seconds(time_limit_minutes)
    if started_at is None or limit is None:
        return None
    return as_utc(started_at) + timedelta(seconds=limit)


def attempt_has_expired(
    started_at: Optional[datetime],
    time_limit_minutes: Optional[int],
    now: Optional[datetime] = None,
    grace_seconds: int = QUIZ_LATE_SUBMIT_GRACE_SECONDS,
) -> bool:
    """True when the attempt is past its limit and the grace window."""
    limit = time_limit_seconds(time_limit_minutes)
    if started_at is None or limit is None:
        return False
    current = as_utc(now or datetime.now(timezone.utc))
    return current > as_utc(started_at) + timedelta(seconds=limit + grace_seconds)


def remaining_attempts(max_attempts: Optional[int], used: int) -> Optional[int]:
    """Attempts left for a learner, or ``None`` when the quiz is unlimited."""
    if max_attempts is None or max_attempts <= 0:
        return None
    return max(0, int(max_attempts) - max(0, int(used)))


def can_start_attempt(max_attempts: Optional[int], used: int) -> bool:
    left = remaining_attempts(max_attempts, used)
    return left is None or left > 0


def xp_delta(earned_points: int, previous_best_points: int) -> int:
    """XP earned for this submission: only the improvement over the best.

    Replaying a quiz, or scoring worse, grants nothing. The sum of XP granted
    across all attempts is therefore capped by the quiz's total points.
    """
    return max(0, int(earned_points) - max(0, int(previous_best_points)))


def clamp_question_times(
    raw: Optional[Mapping[str, object]],
    question_ids: Iterable[object],
    duration_seconds: int,
) -> dict[str, int]:
    """Validate client-reported per-question seconds against real elapsed time.

    Unknown question ids and unusable values are dropped; negative or infinite
    values are treated as unusable; individual times are capped at the attempt
    duration; and if the total still exceeds the wall-clock duration, every
    value is scaled down proportionally. The stored timing can therefore never
    claim more time than the server observed.
    """
    allowed = {str(question_id) for question_id in question_ids}
    duration = max(0, int(duration_seconds))
    if duration <= 0 or not raw:
        return {}

    cleaned: dict[str, int] = {}
    for key, value in raw.items():
        question_id = str(key)
        if question_id not in allowed:
            continue
        try:
            seconds = float(value)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            continue
        if not math.isfinite(seconds) or seconds <= 0:
            continue
        whole = min(int(seconds), duration)
        if whole > 0:
            cleaned[question_id] = whole

    total = sum(cleaned.values())
    if total > duration:
        scale = duration / total
        cleaned = {
            question_id: int(seconds * scale)
            for question_id, seconds in cleaned.items()
        }
        cleaned = {qid: seconds for qid, seconds in cleaned.items() if seconds > 0}
    return cleaned
