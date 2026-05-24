import uuid
from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional


class IngredientCreate(BaseModel):
    name: str = Field(..., max_length=64)
    category: str = Field(..., max_length=32)
    zone: str = Field(..., max_length=32)
    quantity: float = Field(..., ge=0)
    unit: str = Field(..., max_length=16)
    purchase_date: Optional[date] = None
    expire_date: date
    barcode: Optional[str] = None
    icon_url: Optional[str] = None
    image_url: Optional[str] = None
    note: Optional[str] = None


class IngredientUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=64)
    category: Optional[str] = Field(None, max_length=32)
    zone: Optional[str] = Field(None, max_length=32)
    quantity: Optional[float] = Field(None, ge=0)
    unit: Optional[str] = Field(None, max_length=16)
    purchase_date: Optional[date] = None
    expire_date: Optional[date] = None
    barcode: Optional[str] = None
    icon_url: Optional[str] = None
    image_url: Optional[str] = None
    note: Optional[str] = None


class IngredientResponse(BaseModel):
    id: uuid.UUID
    household_id: uuid.UUID
    added_by: uuid.UUID
    name: str
    category: str
    zone: str
    quantity: float
    unit: str
    purchase_date: Optional[date] = None
    expire_date: date
    freshness: str
    barcode: Optional[str] = None
    icon_url: Optional[str] = None
    image_url: Optional[str] = None
    note: Optional[str] = None
    is_consumed: bool
    is_deleted: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class IngredientListResponse(BaseModel):
    list: list[IngredientResponse]
    total: int


class ConsumeRequest(BaseModel):
    quantity: Optional[float] = None


class BatchDeleteRequest(BaseModel):
    ids: list[str]