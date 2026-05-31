import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, Integer, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from server.database import Base
from server.models.mixins import TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    openid: Mapped[str] = mapped_column(String(128), unique=True, index=True, nullable=False)
    nickname: Mapped[str | None] = mapped_column(String(64))
    avatar_url: Mapped[str | None] = mapped_column(String(512))
    household_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("households.id"), index=True)

    diet_type: Mapped[str] = mapped_column(String(32), default="omnivore", nullable=False)
    disliked: Mapped[list] = mapped_column(JSONB, default=list, server_default="[]")
    skill_level: Mapped[str] = mapped_column(String(32), default="beginner", nullable=False)
    flavor_pref: Mapped[list] = mapped_column(JSONB, default=list, server_default="[]")
    notification_open: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    notify_days_before: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    notify_hour: Mapped[int] = mapped_column(Integer, default=9, nullable=False)
    notify_expiry: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    notify_stock: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    notify_inactive: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    inactive_days: Mapped[int] = mapped_column(Integer, default=7, nullable=False)
    subscribed_templates: Mapped[list] = mapped_column(JSONB, default=list, server_default="[]")
    bio: Mapped[str | None] = mapped_column(String(256))