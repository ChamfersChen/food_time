from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from server.database import get_db
from server.models.user import User
from server.models.household import Household
from server.schemas.auth import WechatLoginRequest, TokenResponse, UserInfoResponse
from server.services.auth_service import wechat_login
from server.middleware.auth_middleware import get_current_user
from server.config import get_settings
from server.utils.security import create_access_token
import random
import string

router = APIRouter(prefix="/auth", tags=["认证"])
settings = get_settings()


@router.post("/login", response_model=TokenResponse)
async def login(request: WechatLoginRequest, db: AsyncSession = Depends(get_db)):
    user, token = await wechat_login(db, request.code)
    await db.commit()
    return TokenResponse(
        access_token=token,
        user=UserInfoResponse.model_validate(user),
    )


@router.post("/guest-login", response_model=TokenResponse)
async def guest_login(request: WechatLoginRequest, db: AsyncSession = Depends(get_db)):
    guest_id = request.code or "guest"
    openid = f"guest_{guest_id}"
    result = await db.execute(select(User).where(User.openid == openid))
    user = result.scalar_one_or_none()

    if user is None:
        nickname = f"访客{random.randint(1000,9999)}"
        user = User(openid=openid, nickname=nickname)
        db.add(user)
        await db.flush()
        invite_code = "".join(random.choices(string.digits, k=6))
        household = Household(
            name=f"{nickname}的冰箱",
            owner_id=user.id,
            invite_code=invite_code,
        )
        db.add(household)
        await db.flush()
        user.household_id = household.id
        await db.flush()

    token = create_access_token({"sub": str(user.id)})
    await db.commit()
    return TokenResponse(
        access_token=token,
        user=UserInfoResponse.model_validate(user),
    )


@router.get("/me", response_model=UserInfoResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return UserInfoResponse.model_validate(current_user)