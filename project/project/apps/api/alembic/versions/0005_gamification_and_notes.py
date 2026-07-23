"""add gamification, notes, achievements

Revision ID: 0005_gamification_and_notes
Revises: 0004_bookmarks
Create Date: 2024-10-01 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0005_gamification_and_notes"
down_revision: str | None = "0004_bookmarks"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Gamification fields on user_profiles
    op.add_column("user_profiles", sa.Column("xp", sa.Integer(), nullable=True))
    op.add_column("user_profiles", sa.Column("current_streak", sa.Integer(), nullable=True))
    op.add_column("user_profiles", sa.Column("longest_streak", sa.Integer(), nullable=True))
    op.add_column("user_profiles", sa.Column("last_activity_date", sa.DateTime(timezone=True), nullable=True))
    op.execute("UPDATE user_profiles SET xp = 0 WHERE xp IS NULL")
    op.execute("UPDATE user_profiles SET current_streak = 0 WHERE current_streak IS NULL")
    op.execute("UPDATE user_profiles SET longest_streak = 0 WHERE longest_streak IS NULL")
    op.alter_column("user_profiles", "xp", nullable=False)
    op.alter_column("user_profiles", "current_streak", nullable=False)
    op.alter_column("user_profiles", "longest_streak", nullable=False)

    # Notes
    op.create_table(
        "notes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False, index=True),
        sa.Column("lesson_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("lessons.id"), nullable=False, index=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), default=sa.func.now()),
        sa.UniqueConstraint("user_id", "lesson_id"),
    )

    # Achievements
    op.create_table(
        "achievements",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("slug", sa.String(100), nullable=False, unique=True, index=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("icon", sa.String(255), nullable=True),
        sa.Column("xp_reward", sa.Integer(), default=0),
        sa.Column("created_at", sa.DateTime(timezone=True), default=sa.func.now()),
    )

    # User achievements
    op.create_table(
        "user_achievements",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False, index=True),
        sa.Column(
            "achievement_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("achievements.id"),
            nullable=False,
            index=True,
        ),
        sa.Column("earned_at", sa.DateTime(timezone=True), default=sa.func.now()),
        sa.UniqueConstraint("user_id", "achievement_id"),
    )


def downgrade() -> None:
    op.drop_table("user_achievements")
    op.drop_table("achievements")
    op.drop_table("notes")
    op.drop_column("user_profiles", "last_activity_date")
    op.drop_column("user_profiles", "longest_streak")
    op.drop_column("user_profiles", "current_streak")
    op.drop_column("user_profiles", "xp")
