"""add quiz attempt limits and per-question timing

Revision ID: 0009_quiz_attempt_limits
Revises: 0008_saved_snippets
Create Date: 2026-10-25 00:00:00.000000

Attempt limits only work if a graded attempt is a single server-side object,
so an attempt can start (status ``in_progress``), be submitted, or expire
unanswered. Per-question timing and the XP actually granted are stored on that
attempt, which is what prevents repeat submissions from farming XP.

Existing attempts are treated as submitted, and existing quizzes receive the
three-attempt default (``NULL`` still means unlimited).
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0009_quiz_attempt_limits"
down_revision: Union[str, None] = "0008_saved_snippets"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("quizzes", sa.Column("max_attempts", sa.Integer(), nullable=True))

    op.add_column(
        "quiz_attempts",
        sa.Column("status", sa.String(16), nullable=False, server_default="submitted"),
    )
    op.add_column(
        "quiz_attempts",
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "quiz_attempts",
        sa.Column("duration_seconds", sa.Integer(), nullable=True),
    )
    op.add_column(
        "quiz_attempts",
        sa.Column("question_times", sa.JSON(), nullable=True),
    )
    op.add_column(
        "quiz_attempts",
        sa.Column("xp_awarded", sa.Integer(), nullable=False, server_default="0"),
    )
    # In-progress attempts have no completion time yet.
    op.alter_column(
        "quiz_attempts",
        "completed_at",
        existing_type=sa.DateTime(timezone=True),
        nullable=True,
    )

    op.create_index(
        "ix_quiz_attempts_user_quiz_status",
        "quiz_attempts",
        ["user_id", "quiz_id", "status"],
    )

    op.execute("UPDATE quiz_attempts SET started_at = completed_at WHERE started_at IS NULL")
    op.execute("UPDATE quizzes SET max_attempts = 3 WHERE max_attempts IS NULL")


def downgrade() -> None:
    # Drop rows that a downgraded schema cannot represent (unfinished attempts).
    op.execute("DELETE FROM quiz_attempts WHERE completed_at IS NULL")
    op.alter_column(
        "quiz_attempts",
        "completed_at",
        existing_type=sa.DateTime(timezone=True),
        nullable=False,
    )
    op.drop_index("ix_quiz_attempts_user_quiz_status", table_name="quiz_attempts")
    op.drop_column("quiz_attempts", "xp_awarded")
    op.drop_column("quiz_attempts", "question_times")
    op.drop_column("quiz_attempts", "duration_seconds")
    op.drop_column("quiz_attempts", "started_at")
    op.drop_column("quiz_attempts", "status")
    op.drop_column("quizzes", "max_attempts")
