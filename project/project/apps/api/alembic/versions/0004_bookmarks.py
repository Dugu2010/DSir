"""add bookmarks table and user_activity indexes

Revision ID: 0004_bookmarks
Revises: 0003_course_fields
Create Date: 2024-09-01 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0004_bookmarks"
down_revision: str | None = "0003_course_fields"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "bookmarks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False, index=True),
        sa.Column("course_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("courses.id"), nullable=False, index=True),
        sa.Column("created_at", sa.DateTime(timezone=True), default=sa.func.now()),
        sa.UniqueConstraint("user_id", "course_id"),
    )
    op.create_index("ix_user_activity_user_id_created_at", "user_activity", ["user_id", "created_at"])


def downgrade() -> None:
    op.drop_index("ix_user_activity_user_id_created_at", table_name="user_activity")
    op.drop_table("bookmarks")
