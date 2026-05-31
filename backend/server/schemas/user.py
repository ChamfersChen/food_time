import uuid
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class UserUpdateRequest(BaseModel):
    nickname: Optional[str] = Field(None, max_length=64)
    avatar_url: Optional[str] = None
    bio: Optional[str] = Field(None, max_length=256)
    diet_type: Optional[str] = None
    disliked: Optional[list[str]] = None
    skill_level: Optional[str] = None
    flavor_pref: Optional[list[str]] = None
    notification_open: Optional[bool] = None
    notify_days_before: Optional[int] = Field(None, ge=1, le=14)
    notify_hour: Optional[int] = Field(None, ge=0, le=23)
    notify_expiry: Optional[bool] = None
    notify_stock: Optional[bool] = None
    notify_inactive: Optional[bool] = None
    inactive_days: Optional[int] = Field(None, ge=1, le=30)
    subscribed_templates: Optional[list[str]] = None


class UserResponse(BaseModel):
    id: uuid.UUID
    openid: str
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    household_id: Optional[uuid.UUID] = None
    diet_type: str = "omnivore"
    disliked: list[str] = []
    skill_level: str = "beginner"
    flavor_pref: list[str] = []
    notification_open: bool = True
    notify_days_before: int = 3
    notify_hour: int = 9
    notify_expiry: bool = True
    notify_stock: bool = True
    notify_inactive: bool = False
    inactive_days: int = 7
    subscribed_templates: list[str] = []
    created_at: datetime

    model_config = {"from_attributes": True}