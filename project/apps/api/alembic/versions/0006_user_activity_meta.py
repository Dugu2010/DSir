"""rename user_activity metadata to meta

Revision ID: 0006_user_activity_meta
Revises: 0005_gamification_and_notes
Create Date: 2024-07-26 00:00:00.000000
"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "0006_user_activity_meta"
down_revision = "0005_gamification_and_notes"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Rename metadata -> meta to match the UserActivity model
    op.alter_column("user_activity", "metadata", new_column_name="meta")


def downgrade() -> None:
    op.alter_column("user_activity", "meta", new_column_name="metadata")
