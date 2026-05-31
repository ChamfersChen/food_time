import uuid
from datetime import date, datetime
from sqlalchemy import String, Boolean, Date, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from server.database import Base


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    household_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("households.id"), index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), index=True, nullable=False)
    openid: Mapped[str] = mapped_column(String(128), nullable=False)
    ingredient_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("ingredients.id"))
    type: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    is_sent: Mapped[bool] = mapped_column(Boolean, index=True, default=False, nullable=False)
    trigger_date: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)