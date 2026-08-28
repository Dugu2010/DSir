"""Add source_text to courses for AI import grounding.

Revision ID: 0004
Revises: 0003
"""
from alembic import op
import sqlalchemy as sa


revision = "0004_source_text"
down_revision = "0003_quiz_reviews"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("courses", sa.Column("source_text", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("courses", "source_text")
