"""add household_id to recipes

Revision ID: 005
Revises: 004
Create Date: 2025-05-31
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


revision = "005"
down_revision = "004"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("recipes", sa.Column("household_id", UUID(as_uuid=True), sa.ForeignKey("households.id"), index=True, nullable=True))


def downgrade():
    op.drop_column("recipes", "household_id")
