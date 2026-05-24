import uuid
from pydantic import BaseModel, Field


class WechatLoginRequest(BaseModel):
    code: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserInfoResponse"


class UserInfoResponse(BaseModel):
    id: uuid.UUID
    nickname: str | None = None
    avatar_url: str | None = None
    household_id: uuid.UUID | None = None
    diet_type: str = "omnivore"
    disliked: list[str] = []
    skill_level: str = "beginner"
    flavor_pref: list[str] = []

    model_config = {"from_attributes": True}


from server.schemas.auth import UserInfoResponse