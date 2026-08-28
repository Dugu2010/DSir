"""complete schema to match models + soft-delete columns

Revision ID: 0002_complete
Revises: 0001_initial
Create Date: 2026-08-11 00:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0002_complete"
down_revision: Union[str, None] = "0001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── Columns referenced by application code but missing from 0001 ──
    op.add_column("exercises", sa.Column("language", sa.String(50), nullable=False, server_default="python"))
    op.add_column("exercises", sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("modules", sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("lessons", sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True))

    # Partial index used by Flashcard model (spaced repetition queries)
    op.create_index(
        "idx_flashcards_review",
        "flashcards",
        ["user_id", "next_review_at"],
        postgresql_where=sa.text("next_review_at IS NOT NULL"),
    )

    # ── course_technologies ──
    op.create_table(
        "course_technologies",
        sa.Column("course_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("courses.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("technology_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("technology_stacks.id", ondelete="CASCADE"), primary_key=True),
    )

    # ── lesson_resources ──
    op.create_table(
        "lesson_resources",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("lesson_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("resource_type", sa.String(50), nullable=False),
        sa.Column("url", sa.Text, nullable=True),
        sa.Column("content", sa.Text, nullable=True),
        sa.Column("display_order", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("idx_lesson_resources_lesson", "lesson_resources", ["lesson_id"])

    # ── quizzes ──
    op.create_table(
        "quizzes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("lesson_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("lessons.id", ondelete="CASCADE"), nullable=True),
        sa.Column("module_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("modules.id", ondelete="CASCADE"), nullable=True),
        sa.Column("course_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("courses.id", ondelete="CASCADE"), nullable=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("passing_score", sa.Integer, nullable=False, server_default="70"),
        sa.Column("time_limit_minutes", sa.Integer, nullable=True),
        sa.Column("question_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("display_order", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("idx_quizzes_lesson", "quizzes", ["lesson_id"])
    op.create_index("idx_quizzes_module", "quizzes", ["module_id"])
    op.create_index("idx_quizzes_course", "quizzes", ["course_id"])

    # ── questions ──
    op.create_table(
        "questions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("quiz_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("question_type", postgresql.ENUM("multiple_choice", "single_choice", "true_false", "coding", "text", name="question_type", create_type=False), nullable=False, server_default="multiple_choice"),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("explanation", sa.Text, nullable=True),
        sa.Column("points", sa.Integer, nullable=False, server_default="1"),
        sa.Column("display_order", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("idx_questions_quiz", "questions", ["quiz_id"])

    # ── question_options ──
    op.create_table(
        "question_options",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("question_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("questions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("is_correct", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("display_order", sa.Integer, nullable=False, server_default="0"),
    )

    # ── exercise_hints ──
    op.create_table(
        "exercise_hints",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("exercise_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("exercises.id", ondelete="CASCADE"), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("hint_level", sa.Integer, nullable=False, server_default="1"),
        sa.Column("cost_percentage", sa.Integer, nullable=False, server_default="0"),
        sa.Column("display_order", sa.Integer, nullable=False, server_default="0"),
    )

    # ── projects ──
    op.create_table(
        "projects",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("course_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("courses.id", ondelete="CASCADE"), nullable=True),
        sa.Column("module_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("modules.id", ondelete="CASCADE"), nullable=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("requirements", sa.Text, nullable=False),
        sa.Column("difficulty", postgresql.ENUM("easy", "medium", "hard", name="exercise_difficulty", create_type=False), nullable=False, server_default="medium"),
        sa.Column("is_capstone", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("estimated_duration_hours", sa.Integer, nullable=True),
        sa.Column("skill_tags", postgresql.ARRAY(sa.Text), nullable=True),
        sa.Column("starter_files", postgresql.JSON, nullable=True),
        sa.Column("rubric", postgresql.JSON, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    # ── project_submissions ──
    op.create_table(
        "project_submissions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("code_files", postgresql.JSON, nullable=False),
        sa.Column("review_status", sa.String(50), nullable=False, server_default="pending"),
        sa.Column("review_feedback", sa.Text, nullable=True),
        sa.Column("review_score", sa.Numeric(5, 2), nullable=True),
        sa.Column("reviewed_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    # ── bookmarks ──
    op.create_table(
        "bookmarks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("lesson_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("lessons.id", ondelete="CASCADE"), nullable=True),
        sa.Column("exercise_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("exercises.id", ondelete="CASCADE"), nullable=True),
        sa.Column("note", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("user_id", "lesson_id", "exercise_id"),
    )
    op.create_index("idx_bookmarks_user", "bookmarks", ["user_id"])

    # ── user_notes ──
    op.create_table(
        "user_notes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("lesson_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("lessons.id", ondelete="CASCADE"), nullable=True),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("is_private", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    # ── recently_viewed ──
    op.create_table(
        "recently_viewed",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("lesson_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False),
        sa.Column("viewed_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("user_id", "lesson_id"),
    )

    # ── flashcard_reviews ──
    op.create_table(
        "flashcard_reviews",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("flashcard_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("flashcards.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("quality", sa.Integer, nullable=False),
        sa.Column("time_spent_seconds", sa.Integer, nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("idx_flashcard_reviews_user", "flashcard_reviews", ["user_id"])

    # ── knowledge_topics ──
    op.create_table(
        "knowledge_topics",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(255), unique=True, nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("parent_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("knowledge_topics.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    # ── knowledge_edges ──
    op.create_table(
        "knowledge_edges",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("source_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("knowledge_topics.id", ondelete="CASCADE"), nullable=False),
        sa.Column("target_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("knowledge_topics.id", ondelete="CASCADE"), nullable=False),
        sa.Column("relationship", sa.String(100), nullable=False),
        sa.UniqueConstraint("source_id", "target_id", "relationship"),
    )

    # ── user_knowledge ──
    op.create_table(
        "user_knowledge",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("topic_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("knowledge_topics.id", ondelete="CASCADE"), nullable=False),
        sa.Column("mastery_level", sa.Numeric(5, 2), nullable=False, server_default="0"),
        sa.Column("confidence", sa.Numeric(5, 2), nullable=False, server_default="0"),
        sa.Column("last_practiced_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("assessment_count", sa.Integer, nullable=False, server_default="0"),
        sa.UniqueConstraint("user_id", "topic_id"),
    )

    # ── leaderboard_entries ──
    op.create_table(
        "leaderboard_entries",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("period_type", sa.String(20), nullable=False),
        sa.Column("period_start", sa.Date, nullable=False),
        sa.Column("period_end", sa.Date, nullable=False),
        sa.Column("xp_earned", sa.Integer, nullable=False, server_default="0"),
        sa.Column("rank", sa.Integer, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("user_id", "period_type", "period_start"),
    )

    # ── discussion_replies ──
    op.create_table(
        "discussion_replies",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("discussion_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("discussions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("parent_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("discussion_replies.id"), nullable=True),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("is_solution", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("vote_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("idx_discussion_replies_discussion", "discussion_replies", ["discussion_id"])


def downgrade() -> None:
    op.drop_index("idx_discussion_replies_discussion", table_name="discussion_replies")
    op.drop_table("discussion_replies")
    op.drop_table("leaderboard_entries")
    op.drop_table("user_knowledge")
    op.drop_table("knowledge_edges")
    op.drop_table("knowledge_topics")
    op.drop_index("idx_flashcard_reviews_user", table_name="flashcard_reviews")
    op.drop_table("flashcard_reviews")
    op.drop_table("recently_viewed")
    op.drop_table("user_notes")
    op.drop_index("idx_bookmarks_user", table_name="bookmarks")
    op.drop_table("bookmarks")
    op.drop_table("project_submissions")
    op.drop_table("projects")
    op.drop_table("exercise_hints")
    op.drop_table("question_options")
    op.drop_index("idx_questions_quiz", table_name="questions")
    op.drop_table("questions")
    op.drop_index("idx_quizzes_course", table_name="quizzes")
    op.drop_index("idx_quizzes_module", table_name="quizzes")
    op.drop_index("idx_quizzes_lesson", table_name="quizzes")
    op.drop_table("quizzes")
    op.drop_index("idx_lesson_resources_lesson", table_name="lesson_resources")
    op.drop_table("lesson_resources")
    op.drop_table("course_technologies")
    op.drop_index("idx_flashcards_review", table_name="flashcards")
    op.drop_column("lessons", "deleted_at")
    op.drop_column("modules", "deleted_at")
    op.drop_column("exercises", "deleted_at")
    op.drop_column("exercises", "language")
