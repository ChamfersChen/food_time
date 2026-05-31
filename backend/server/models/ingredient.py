import uuid
from datetime import date, datetime
from sqlalchemy import String, Boolean, Integer, Float, Date, DateTime, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from server.database import Base


class Ingredient(Base):
    __tablename__ = "ingredients"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    household_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("households.id"), index=True, nullable=False)
    added_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    category: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    zone: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    quantity: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    unit: Mapped[str] = mapped_column(String(16), nullable=False)
    purchase_date: Mapped[date | None] = mapped_column(Date)
    expire_date: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    freshness: Mapped[str] = mapped_column(String(16), index=True, default="fresh", nullable=False)
    barcode: Mapped[str | None] = mapped_column(String(64))
    icon_url: Mapped[str | None] = mapped_column(String(512))
    image_url: Mapped[str | None] = mapped_column(String(512))
    note: Mapped[str | None] = mapped_column(Text)
    is_consumed: Mapped[bool] = mapped_column(Boolean, index=True, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)