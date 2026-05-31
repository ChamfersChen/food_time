"""drop is_deleted column from ingredients

Revision ID: 007
Revises: 006
Create Date: 2025-05-31
"""
from alembic import op


revision = "007"
down_revision = "006"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column("ingredients", "is_deleted")


def downgrade():
    op.add_column("ingredients", sa.Column("is_deleted", sa.Boolean, index=True, server_default="false", nullable=False))
