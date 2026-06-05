import uuid
from datetime import date, datetime
from sqlalchemy import String, Integer, Float, Date, DateTime, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column
from server.database import Base


class CookingLog(Base):
    __tablename__ = "cooking_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), index=True, nullable=False)
    household_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("households.id"), index=True, nullable=True)
    recipe_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("recipes.id"))
    recipe_name: Mapped[str] = mapped_column(String(128), nullable=False)
    cooked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    meal_type: Mapped[str | None] = mapped_column(String(32), index=True)
    duration: Mapped[int | None] = mapped_column(Integer)
    rating: Mapped[int | None] = mapped_column(Integer)
    note: Mapped[str | None] = mapped_column(Text)
    photo_urls: Mapped[list] = mapped_column(JSONB, default=list, server_default="[]")
    mood: Mapped[str | None] = mapped_column(String(32))
    consumed_ingredients: Mapped[list] = mapped_column(JSONB, default=list, server_default="[]")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)