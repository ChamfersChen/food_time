import uuid
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class RecipeCreate(BaseModel):
    name: str = Field(..., max_length=128)
    description: Optional[str] = None
    cover_url: Optional[str] = None
    tags: list[str] = []
    cuisine: Optional[str] = None
    cook_time: int = Field(..., ge=0)
    difficulty: str = "easy"
    calories: Optional[int] = None
    servings: int = 2
    ingredients: list[dict] = []
    steps: list[dict] = []
    is_public: bool = True


class RecipeUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=128)
    description: Optional[str] = None
    cover_url: Optional[str] = None
    tags: Optional[list[str]] = None
    cuisine: Optional[str] = None
    cook_time: Optional[int] = Field(None, ge=0)
    difficulty: Optional[str] = None
    calories: Optional[int] = None
    servings: Optional[int] = None
    ingredients: Optional[list[dict]] = None
    steps: Optional[list[dict]] = None
    is_public: Optional[bool] = None


class RecipeResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str] = None
    cover_url: Optional[str] = None
    tags: list[str] = []
    cuisine: Optional[str] = None
    cook_time: int
    difficulty: str
    calories: Optional[int] = None
    servings: int
    ingredients: list[dict] = []
    steps: list[dict] = []
    source: str
    author_id: Optional[uuid.UUID] = None
    household_id: Optional[uuid.UUID] = None
    is_public: bool
    rating_avg: float = 0
    rating_count: int = 0
    view_count: int = 0
    is_favorited: bool = False
    match_percent: Optional[int] = None
    has_expiring_ingredient: bool = False
    created_at: datetime

    model_config = {"from_attributes": True}


class RecipeListResponse(BaseModel):
    list: list[RecipeResponse]
    total: int