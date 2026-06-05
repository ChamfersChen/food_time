import uuid
from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional


class CookingLogCreate(BaseModel):
    recipe_id: Optional[str] = None
    recipe_name: str
    cooked_at: Optional[datetime] = None
    meal_type: Optional[str] = None
    duration: Optional[int] = None
    rating: Optional[int] = Field(None, ge=1, le=5)
    note: Optional[str] = None
    photo_urls: list[str] = []
    mood: Optional[str] = None
    consumed_ingredients: list[dict] = []


class CookingLogUpdate(BaseModel):
    rating: Optional[int] = Field(None, ge=1, le=5)
    note: Optional[str] = None
    photo_urls: Optional[list[str]] = None
    mood: Optional[str] = None


class CookingLogResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    household_id: uuid.UUID
    recipe_id: Optional[uuid.UUID] = None
    recipe_name: str
    cooked_at: datetime
    meal_type: Optional[str] = None
    duration: Optional[int] = None
    rating: Optional[int] = None
    note: Optional[str] = None
    photo_urls: list[str] = []
    mood: Optional[str] = None
    consumed_ingredients: list[dict] = []
    created_at: datetime

    model_config = {"from_attributes": True}


class CookingStatsResponse(BaseModel):
    total_meals: int
    ingredients_consumed: int
    streak_days: int