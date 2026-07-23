"""add course fields and lesson progress

Revision ID: 0003_add_course_fields_and_lesson_progress
Revises: 0002_add_execution_knowledge_audit_and_rename_meta
Create Date: 2024-08-01 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0003_course_fields"
down_revision: str | None = "0002_execution_knowledge_audit"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Course fields
    op.add_column("courses", sa.Column("thumbnail", sa.Text(), nullable=True))
    op.add_column("courses", sa.Column("category", sa.String(100), nullable=True))
    op.add_column("courses", sa.Column("programming_language", sa.String(100), nullable=True))
    op.add_column("courses", sa.Column("difficulty", sa.String(50), nullable=True))
    op.add_column("courses", sa.Column("estimated_duration", sa.Integer(), nullable=True))
    op.add_column("courses", sa.Column("instructor", sa.String(255), nullable=True))
    op.add_column("courses", sa.Column("skills", postgresql.JSONB(), default="[]"))
    op.add_column("courses", sa.Column("learning_objectives", postgresql.JSONB(), default="[]"))

    # Backfill required fields where NULL
    op.execute("UPDATE courses SET programming_language = technology WHERE programming_language IS NULL")
    op.execute("UPDATE courses SET difficulty = 'beginner' WHERE difficulty IS NULL")
    op.execute("UPDATE courses SET estimated_duration = 0 WHERE estimated_duration IS NULL")

    # Make non-nullable after backfill
    op.alter_column("courses", "programming_language", nullable=False)
    op.alter_column("courses", "difficulty", nullable=False)
    op.alter_column("courses", "estimated_duration", nullable=False)

    # Concept order
    op.add_column("concepts", sa.Column("order", sa.Integer(), nullable=True))
    op.execute('UPDATE concepts SET "order" = 0 WHERE "order" IS NULL')
    op.alter_column("concepts", "order", nullable=False)

    # Lesson duration
    op.add_column("lessons", sa.Column("duration_minutes", sa.Integer(), nullable=True))
    op.execute("UPDATE lessons SET duration_minutes = 0 WHERE duration_minutes IS NULL")
    op.alter_column("lessons", "duration_minutes", nullable=False)

    # Enrollment progress fields
    op.add_column("enrollments", sa.Column("progress_percent", sa.Integer(), nullable=True))
    op.add_column(
        "enrollments",
        sa.Column("last_lesson_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("lessons.id"), nullable=True),
    )
    op.execute("UPDATE enrollments SET progress_percent = 0 WHERE progress_percent IS NULL")
    op.alter_column("enrollments", "progress_percent", nullable=False)

    # Lesson progress table
    op.create_table(
        "lesson_progress",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("lesson_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("lessons.id"), nullable=False),
        sa.Column("is_completed", sa.Boolean(), default=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), default=sa.func.now()),
        sa.UniqueConstraint("user_id", "lesson_id"),
    )


def downgrade() -> None:
    op.drop_table("lesson_progress")
    op.drop_column("enrollments", "last_lesson_id")
    op.drop_column("enrollments", "progress_percent")
    op.drop_column("lessons", "duration_minutes")
    op.drop_column("concepts", "order")

    op.drop_column("courses", "learning_objectives")
    op.drop_column("courses", "skills")
    op.drop_column("courses", "instructor")
    op.drop_column("courses", "estimated_duration")
    op.drop_column("courses", "difficulty")
    op.drop_column("courses", "programming_language")
    op.drop_column("courses", "category")
    op.drop_column("courses", "thumbnail")
