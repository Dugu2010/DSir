"""initial

Revision ID: 0001_initial
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0001_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), unique=True, nullable=False, index=True),
        sa.Column("hashed_password", sa.String(255), nullable=True),
        sa.Column("full_name", sa.String(255), nullable=True),
        sa.Column("avatar_url", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), default=True),
        sa.Column("created_at", sa.DateTime(timezone=True), default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), default=sa.func.now()),
    )
    op.create_table(
        "user_profiles",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), primary_key=True),
        sa.Column("timezone", sa.String(50), default="UTC"),
        sa.Column("daily_goal_minutes", sa.Integer(), default=30),
        sa.Column("preferred_language", sa.String(10), default="en"),
        sa.Column("onboarding_completed", sa.Boolean(), default=False),
        sa.Column("preferences", postgresql.JSONB(), default="{}"),
    )
    op.create_table(
        "user_roles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("role", sa.String(50), nullable=False),
        sa.UniqueConstraint("user_id", "role"),
    )
    op.create_table(
        "refresh_tokens",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("token_hash", sa.String(255), nullable=False, index=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked", sa.Boolean(), default=False),
        sa.Column("created_at", sa.DateTime(timezone=True), default=sa.func.now()),
    )
    op.create_table(
        "roadmaps",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("slug", sa.String(255), unique=True, nullable=False, index=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_published", sa.Boolean(), default=False),
        sa.Column("metadata", postgresql.JSONB(), default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), default=sa.func.now()),
    )
    op.create_table(
        "courses",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("slug", sa.String(255), unique=True, nullable=False, index=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("technology", sa.String(100), nullable=False),
        sa.Column("is_published", sa.Boolean(), default=False),
        sa.Column("metadata", postgresql.JSONB(), default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), default=sa.func.now()),
    )
    op.create_table(
        "roadmap_courses",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("roadmap_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("roadmaps.id"), nullable=False),
        sa.Column("course_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("courses.id"), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.UniqueConstraint("roadmap_id", "course_id"),
    )
    op.create_table(
        "concepts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("course_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("courses.id"), nullable=False),
        sa.Column("slug", sa.String(255), nullable=False, index=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("difficulty", sa.String(50), nullable=True),
        sa.Column("prerequisites", postgresql.JSONB(), default="[]"),
        sa.Column("metadata", postgresql.JSONB(), default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), default=sa.func.now()),
        sa.UniqueConstraint("course_id", "slug"),
    )
    op.create_table(
        "lessons",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("concept_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("concepts.id"), nullable=False),
        sa.Column("slug", sa.String(255), nullable=False, index=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("content", postgresql.JSONB(), nullable=False),
        sa.Column("lesson_type", sa.String(50), default="reading"),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("metadata", postgresql.JSONB(), default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), default=sa.func.now()),
        sa.UniqueConstraint("concept_id", "slug"),
    )
    op.create_table(
        "enrollments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("roadmap_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("roadmaps.id"), nullable=True),
        sa.Column("course_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("courses.id"), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), default=sa.func.now()),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(50), default="active"),
        sa.UniqueConstraint("user_id", "roadmap_id", "course_id"),
    )
    op.create_table(
        "concept_mastery",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("concept_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("concepts.id"), nullable=False),
        sa.Column("score", sa.Integer(), default=0),
        sa.Column("confidence", sa.Integer(), default=0),
        sa.Column("attempts", sa.Integer(), default=0),
        sa.Column("correct_streak", sa.Integer(), default=0),
        sa.Column("last_reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("next_review_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), default=sa.func.now()),
        sa.UniqueConstraint("user_id", "concept_id"),
    )
    op.create_table(
        "user_activity",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("activity_type", sa.String(100), nullable=False),
        sa.Column("entity_type", sa.String(100), nullable=True),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("metadata", postgresql.JSONB(), default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), default=sa.func.now()),
    )
    op.create_table(
        "submissions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("lesson_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("lessons.id"), nullable=True),
        sa.Column("concept_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("concepts.id"), nullable=True),
        sa.Column("submission_type", sa.String(50), nullable=False),
        sa.Column("payload", postgresql.JSONB(), nullable=False),
        sa.Column("evaluation", postgresql.JSONB(), nullable=True),
        sa.Column("score", sa.Integer(), nullable=True),
        sa.Column("submitted_at", sa.DateTime(timezone=True), default=sa.func.now()),
        sa.Column("evaluated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_table(
        "projects",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("course_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("courses.id"), nullable=False),
        sa.Column("slug", sa.String(255), nullable=False, index=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("requirements", postgresql.JSONB(), default="{}"),
        sa.Column("starter_files", postgresql.JSONB(), default="{}"),
        sa.Column("metadata", postgresql.JSONB(), default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), default=sa.func.now()),
        sa.UniqueConstraint("course_id", "slug"),
    )
    op.create_table(
        "project_submissions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("repository_url", sa.Text(), nullable=True),
        sa.Column("files", postgresql.JSONB(), nullable=True),
        sa.Column("feedback", postgresql.JSONB(), nullable=True),
        sa.Column("score", sa.Integer(), nullable=True),
        sa.Column("submitted_at", sa.DateTime(timezone=True), default=sa.func.now()),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_table(
        "revision_schedules",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("concept_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("concepts.id"), nullable=False),
        sa.Column("interval_days", sa.Integer(), default=1),
        sa.Column("ease_factor", sa.Numeric(4, 2), default=2.5),
        sa.Column("repetitions", sa.Integer(), default=0),
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), default=sa.func.now()),
        sa.UniqueConstraint("user_id", "concept_id"),
    )
    op.create_table(
        "revision_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), default=sa.func.now()),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("concepts", postgresql.JSONB(), default="[]"),
        sa.Column("results", postgresql.JSONB(), default="{}"),
    )
    op.create_table(
        "revision_problem_queue",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("concept_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("concepts.id"), nullable=False),
        sa.Column("problem_data", postgresql.JSONB(), default="{}"),
        sa.Column("generated_at", sa.DateTime(timezone=True), default=sa.func.now()),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    tables = [
        "revision_problem_queue",
        "revision_sessions",
        "revision_schedules",
        "project_submissions",
        "projects",
        "submissions",
        "user_activity",
        "concept_mastery",
        "enrollments",
        "lessons",
        "concepts",
        "roadmap_courses",
        "courses",
        "roadmaps",
        "refresh_tokens",
        "user_roles",
        "user_profiles",
        "users",
    ]
    for table in tables:
        op.drop_table(table)
