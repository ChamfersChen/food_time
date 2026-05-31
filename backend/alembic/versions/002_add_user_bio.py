"""add bio column to users

Revision ID: 002
Revises: 001
Create Date: 2025-05-31
"""
from alembic import op
import sqlalchemy as sa

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("bio", sa.String(256)))


def downgrade() -> None:
    op.drop_column("users", "bio")
