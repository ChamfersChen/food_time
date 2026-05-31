import uuid
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class CommentCreate(BaseModel):
    log_id: str
    content: str = Field(..., min_length=1, max_length=500)


class CommentResponse(BaseModel):
    id: uuid.UUID
    log_id: uuid.UUID
    user_id: uuid.UUID
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}
