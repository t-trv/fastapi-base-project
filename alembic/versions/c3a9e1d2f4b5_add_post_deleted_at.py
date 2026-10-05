"""add post deleted_at

Revision ID: c3a9e1d2f4b5
Revises: 8fca2dbbe7f0
Create Date: 2026-10-04
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "c3a9e1d2f4b5"
down_revision: Union[str, Sequence[str], None] = "8fca2dbbe7f0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("posts", sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True))
    op.create_index(op.f("ix_posts_deleted_at"), "posts", ["deleted_at"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_posts_deleted_at"), table_name="posts")
    op.drop_column("posts", "deleted_at")
