"""Unit tests for quiz attempt limits, timing clamps, and XP accounting.

These rules are pure functions, so no database is required.
"""

from datetime import datetime, timedelta, timezone

import pytest

from app.services.quiz_sessions import (
    QUIZ_LATE_SUBMIT_GRACE_SECONDS,
    attempt_expires_at,
    attempt_has_expired,
    can_start_attempt,
    clamp_question_times,
    elapsed_seconds,
    remaining_attempts,
    time_limit_seconds,
    xp_delta,
)

QIDS = ["q1", "q2", "q3"]


# ── Attempt limits ──────────────────────────────────────────────

def test_unlimited_quiz_never_blocks_attempts():
    assert remaining_attempts(None, 99) is None
    assert can_start_attempt(None, 99) is True
    assert remaining_attempts(0, 1) is None


def test_attempt_limit_counts_down_and_stops_at_zero():
    assert remaining_attempts(3, 0) == 3
    assert remaining_attempts(3, 2) == 1
    assert remaining_attempts(3, 3) == 0
    assert remaining_attempts(3, 4) == 0
    assert can_start_attempt(3, 2) is True
    assert can_start_attempt(3, 3) is False


# ── Time limits / expiry ────────────────────────────────────────

def test_time_limit_seconds_treats_missing_or_zero_as_untimed():
    assert time_limit_seconds(None) is None
    assert time_limit_seconds(0) is None
    assert time_limit_seconds(10) == 600


def test_expires_at_only_when_timed():
    started = datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)
    assert attempt_expires_at(started, None) is None
    assert attempt_expires_at(started, 10) == started + timedelta(minutes=10)


def test_expiry_allows_a_grace_window_for_late_network():
    started = datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)
    just_inside = started + timedelta(minutes=10, seconds=QUIZ_LATE_SUBMIT_GRACE_SECONDS - 1)
    just_outside = started + timedelta(minutes=10, seconds=QUIZ_LATE_SUBMIT_GRACE_SECONDS + 1)

    assert attempt_has_expired(started, 10, just_inside) is False
    assert attempt_has_expired(started, 10, just_outside) is True
    assert attempt_has_expired(started, None, just_outside) is False
    assert attempt_has_expired(None, 10, just_outside) is False


def test_expiry_accepts_naive_database_datetimes():
    started = datetime(2026, 1, 1, 12, 0)  # naive, as SQLAlchemy may return it
    now = datetime(2026, 1, 1, 12, 30, tzinfo=timezone.utc)
    assert attempt_has_expired(started, 10, now) is True


def test_elapsed_seconds_is_never_negative_and_handles_missing_start():
    now = datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)
    assert elapsed_seconds(None, now) == 0
    assert elapsed_seconds(now + timedelta(seconds=30), now) == 0
    assert elapsed_seconds(now - timedelta(seconds=90), now) == 90


# ── XP ──────────────────────────────────────────────────────────

def test_first_attempt_earns_its_points():
    assert xp_delta(8, 0) == 8


def test_repeating_the_same_score_earns_no_xp():
    assert xp_delta(8, 8) == 0


def test_retake_earns_only_the_improvement():
    assert xp_delta(9, 6) == 3
    assert xp_delta(6, 9) == 0


@pytest.mark.parametrize("earned,best", [(0, 0), (0, 5), (3, 0), (10, 3)])
def test_total_xp_across_retakes_is_capped_by_best_score(earned, best):
    """Granting deltas means attempts can never exceed the achieved score."""
    first = xp_delta(best, 0)
    retake = xp_delta(earned, best)
    assert first + retake == max(best, earned)


# ── Per-question timing ─────────────────────────────────────────

def test_question_times_are_clamped_to_real_elapsed_time():
    raw = {"q1": 30, "q2": 45, "q3": 60}
    times = clamp_question_times(raw, QIDS, duration_seconds=90)
    assert sum(times.values()) <= 90
    # 135 reported seconds are scaled down proportionally to the 90 observed.
    assert times["q1"] == 20
    assert times["q2"] == 30
    assert times["q3"] == 40
    assert times["q1"] < times["q2"] < times["q3"]


def test_question_times_drop_unknown_questions_and_bad_values():
    raw = {
        "q1": 10,
        "not-a-question": 500,
        "q2": "not a number",
        "q3": -3,
    }
    assert clamp_question_times(raw, QIDS, duration_seconds=60) == {"q1": 10}


def test_question_times_ignore_non_finite_values():
    raw = {"q1": float("nan"), "q2": float("inf"), "q3": 5}
    assert clamp_question_times(raw, QIDS, duration_seconds=60) == {"q3": 5}


def test_question_times_cannot_exceed_attempt_duration():
    raw = {"q1": 600, "q2": 600}
    times = clamp_question_times(raw, QIDS, duration_seconds=30)
    assert sum(times.values()) <= 30
    assert all(seconds <= 30 for seconds in times.values())


def test_question_times_empty_when_attempt_had_no_duration():
    assert clamp_question_times({"q1": 10}, QIDS, duration_seconds=0) == {}
    assert clamp_question_times(None, QIDS, duration_seconds=60) == {}
