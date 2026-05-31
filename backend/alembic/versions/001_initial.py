"""init revision

Revision ID: 001
Revises:
Create Date: 2024-01-01 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "households",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("invite_code", sa.String(6), unique=True, nullable=False, index=True),
        sa.Column("default_zone", sa.String(32), server_default="refrigeration", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("openid", sa.String(128), unique=True, nullable=False, index=True),
        sa.Column("nickname", sa.String(64)),
        sa.Column("avatar_url", sa.String(512)),
        sa.Column("household_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("households.id"), index=True),
        sa.Column("diet_type", sa.String(32), server_default="omnivore", nullable=False),
        sa.Column("disliked", postgresql.JSONB, server_default="[]"),
        sa.Column("skill_level", sa.String(32), server_default="beginner", nullable=False),
        sa.Column("flavor_pref", postgresql.JSONB, server_default="[]"),
        sa.Column("notification_open", sa.Boolean, server_default="true", nullable=False),
        sa.Column("notify_days_before", sa.Integer, server_default="3", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_foreign_key("fk_households_owner_id", "households", "users", ["owner_id"], ["id"])

    op.create_table(
        "ingredients",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("household_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("households.id"), index=True, nullable=False),
        sa.Column("added_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("name", sa.String(64), index=True, nullable=False),
        sa.Column("category", sa.String(32), index=True, nullable=False),
        sa.Column("zone", sa.String(32), index=True, nullable=False),
        sa.Column("quantity", sa.Float, nullable=False),
        sa.Column("unit", sa.String(16), nullable=False),
        sa.Column("purchase_date", sa.Date),
        sa.Column("expire_date", sa.Date, index=True, nullable=False),
        sa.Column("freshness", sa.String(16), index=True, server_default="fresh", nullable=False),
        sa.Column("barcode", sa.String(64)),
        sa.Column("icon_url", sa.String(512)),
        sa.Column("image_url", sa.String(512)),
        sa.Column("note", sa.Text),
        sa.Column("is_consumed", sa.Boolean, index=True, server_default="false", nullable=False),
        sa.Column("is_deleted", sa.Boolean, index=True, server_default="false", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_ingredients_household_expire", "ingredients", ["household_id", "expire_date"])
    op.create_index("ix_ingredients_household_category", "ingredients", ["household_id", "category"])
    op.create_index("ix_ingredients_household_freshness", "ingredients", ["household_id", "freshness"])
    op.create_index("ix_ingredients_household_consumed", "ingredients", ["household_id", "is_consumed"])

    op.create_table(
        "recipes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(128), index=True, nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("cover_url", sa.String(512)),
        sa.Column("tags", postgresql.JSONB, server_default="[]"),
        sa.Column("cuisine", sa.String(32)),
        sa.Column("cook_time", sa.Integer, nullable=False),
        sa.Column("difficulty", sa.String(16), server_default="easy", nullable=False),
        sa.Column("calories", sa.Integer),
        sa.Column("servings", sa.Integer, server_default="2", nullable=False),
        sa.Column("ingredients", postgresql.JSONB, server_default="[]"),
        sa.Column("steps", postgresql.JSONB, server_default="[]"),
        sa.Column("source", sa.String(16), index=True, server_default="system", nullable=False),
        sa.Column("author_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id")),
        sa.Column("is_public", sa.Boolean, server_default="true", nullable=False),
        sa.Column("rating_avg", sa.Float, server_default="0", nullable=False),
        sa.Column("rating_count", sa.Integer, server_default="0", nullable=False),
        sa.Column("view_count", sa.Integer, server_default="0", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "cooking_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), index=True, nullable=False),
        sa.Column("household_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("households.id"), index=True, nullable=False),
        sa.Column("recipe_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("recipes.id")),
        sa.Column("recipe_name", sa.String(128), nullable=False),
        sa.Column("cooked_at", sa.Date, index=True, nullable=False),
        sa.Column("duration", sa.Integer),
        sa.Column("rating", sa.Integer),
        sa.Column("note", sa.Text),
        sa.Column("photo_urls", postgresql.JSONB, server_default="[]"),
        sa.Column("mood", sa.String(32)),
        sa.Column("consumed_ingredients", postgresql.JSONB, server_default="[]"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_cooking_logs_user_cooked", "cooking_logs", ["user_id", "cooked_at"])
    op.create_index("ix_cooking_logs_household_cooked", "cooking_logs", ["household_id", "cooked_at"])

    op.create_table(
        "user_favorites",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), index=True, nullable=False),
        sa.Column("recipe_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("recipes.id"), index=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("user_id", "recipe_id", name="uq_user_recipe"),
    )

    op.create_table(
        "notifications",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("household_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("households.id"), index=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), index=True, nullable=False),
        sa.Column("openid", sa.String(128), nullable=False),
        sa.Column("ingredient_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ingredients.id")),
        sa.Column("type", sa.String(32), index=True, nullable=False),
        sa.Column("is_sent", sa.Boolean, index=True, server_default="false", nullable=False),
        sa.Column("trigger_date", sa.Date, index=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_notifications_user_sent", "notifications", ["user_id", "is_sent"])


def downgrade() -> None:
    op.drop_constraint("fk_households_owner_id", "households", type_="foreignkey")
    op.drop_table("notifications")
    op.drop_table("user_favorites")
    op.drop_table("cooking_logs")
    op.drop_table("recipes")
    op.drop_table("ingredients")
    op.drop_table("users")
    op.drop_table("households")