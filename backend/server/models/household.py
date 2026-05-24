import uuid
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from server.database import Base
from server.models.mixins import TimestampMixin


class Household(Base, TimestampMixin):
    __tablename__ = "households"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    owner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    invite_code: Mapped[str] = mapped_column(String(6), unique=True, index=True, nullable=False)
    default_zone: Mapped[str] = mapped_column(String(32), default="refrigeration", nullable=False)

    members = relationship("User", backref="household", foreign_keys="User.household_id")