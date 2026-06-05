"""add meal_type to cooking_logs and change cooked_at to DateTime

Revision ID: 008
Revises: 007
Create Date: 2026-06-05
"""
import sqlalchemy as sa
from alembic import op


revision = "008"
down_revision = "007"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        "cooking_logs",
        "cooked_at",
        existing_type=sa.Date(),
        type_=sa.DateTime(timezone=True),
        postgresql_using="cooked_at::timestamp with time zone",
    )
    op.add_column(
        "cooking_logs",
        sa.Column("meal_type", sa.String(32), nullable=True),
    )
    op.create_index(
        "ix_cooking_logs_meal_type",
        "cooking_logs",
        ["meal_type"],
    )


def downgrade():
    op.drop_index("ix_cooking_logs_meal_type", table_name="cooking_logs")
    op.drop_column("cooking_logs", "meal_type")
    op.alter_column(
        "cooking_logs",
        "cooked_at",
        existing_type=sa.DateTime(timezone=True),
        type_=sa.Date(),
        postgresql_using="(cooked_at AT TIME ZONE 'UTC')::date",
    )
