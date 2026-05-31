"""add notification preference columns to users

Revision ID: 003
Revises: 002
Create Date: 2025-05-31
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("notify_hour", sa.Integer, server_default="9", nullable=False))
    op.add_column("users", sa.Column("notify_expiry", sa.Boolean, server_default="true", nullable=False))
    op.add_column("users", sa.Column("notify_stock", sa.Boolean, server_default="true", nullable=False))
    op.add_column("users", sa.Column("notify_inactive", sa.Boolean, server_default="false", nullable=False))
    op.add_column("users", sa.Column("inactive_days", sa.Integer, server_default="7", nullable=False))
    op.add_column("users", sa.Column("subscribed_templates", JSONB, server_default="[]"))


def downgrade() -> None:
    op.drop_column("users", "subscribed_templates")
    op.drop_column("users", "inactive_days")
    op.drop_column("users", "notify_inactive")
    op.drop_column("users", "notify_stock")
    op.drop_column("users", "notify_expiry")
    op.drop_column("users", "notify_hour")
