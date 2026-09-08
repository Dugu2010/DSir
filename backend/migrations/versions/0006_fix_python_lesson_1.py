"""Repair the Python lesson seed migration chain.

Revision ID: 0006_fix_python_lesson_1
Revises: 0005_python_lesson_1

This migration intentionally performs no database changes. It exists only
as a safe chain marker while the lesson seed file is corrected before use.
"""
from typing import Sequence, Union

revision: str = "0006_fix_python_lesson_1"
down_revision: Union[str, None] = "0005_python_lesson_1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
