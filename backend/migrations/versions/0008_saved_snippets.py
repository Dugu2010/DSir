"""add saved practice snippets

Revision ID: 0008_saved_snippets
Revises: 0007_python_lesson_1_interactive
Create Date: 2026-10-24 00:00:00.000000

Additive only: stores learner-created snippets from the independent workspace.
It does not touch courses, lessons, progress, or submissions.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0008_saved_snippets"
down_revision: Union[str, None] = "0007_python_lesson_1_interactive"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "saved_snippets",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(120), nullable=False),
        sa.Column("language", sa.String(20), nullable=False, server_default="python"),
        sa.Column("code", sa.Text(), nullable=False),
        sa.Column("stdin", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_saved_snippets_user_id", "saved_snippets", ["user_id"])
    op.create_index("ix_saved_snippets_user_updated", "saved_snippets", ["user_id", "updated_at"])


def downgrade() -> None:
    op.drop_index("ix_saved_snippets_user_updated", table_name="saved_snippets")
    op.drop_index("ix_saved_snippets_user_id", table_name="saved_snippets")
    op.drop_table("saved_snippets")
