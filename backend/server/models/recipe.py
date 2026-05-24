import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, Integer, Float, ForeignKey, Text, DateTime, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column
from server.database import Base


class Recipe(Base):
    __tablename__ = "recipes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    cover_url: Mapped[str | None] = mapped_column(String(512))
    tags: Mapped[list] = mapped_column(JSONB, default=list, server_default="[]")
    cuisine: Mapped[str | None] = mapped_column(String(32))
    cook_time: Mapped[int] = mapped_column(Integer, nullable=False)
    difficulty: Mapped[str] = mapped_column(String(16), default="easy", nullable=False)
    calories: Mapped[int | None] = mapped_column(Integer)
    servings: Mapped[int] = mapped_column(Integer, default=2)
    ingredients: Mapped[list] = mapped_column(JSONB, default=list, server_default="[]")
    steps: Mapped[list] = mapped_column(JSONB, default=list, server_default="[]")
    source: Mapped[str] = mapped_column(String(16), index=True, default="system", nullable=False)
    author_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    is_public: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    rating_avg: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    rating_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    view_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)