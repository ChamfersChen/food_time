"""make cooking_logs.household_id nullable

Revision ID: 006
Revises: 005
Create Date: 2025-05-31
"""
from alembic import op
from sqlalchemy.dialects.postgresql import UUID


revision = "006"
down_revision = "005"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column("cooking_logs", "household_id", nullable=True, type_=UUID(as_uuid=True))


def downgrade():
    op.alter_column("cooking_logs", "household_id", nullable=False, type_=UUID(as_uuid=True))
