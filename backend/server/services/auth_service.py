import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from server.models import User, Household
from server.utils.security import create_access_token
from server.utils.wechat import code2session, WechatAuthError
from server.config import get_settings
import random
import string

settings = get_settings()


async def wechat_login(db: AsyncSession, code: str) -> tuple[User, str]:
    wx_data = await code2session(code)
    openid = wx_data["openid"]

    result = await db.execute(select(User).where(User.openid == openid))
    user = result.scalar_one_or_none()

    if user is None:
        user = User(openid=openid, nickname=f"美食家{random.randint(1000,9999)}")
        db.add(user)
        await db.flush()

        # auto-create household
        invite_code = "".join(random.choices(string.digits, k=6))
        household = Household(
            name=f"{user.nickname}的冰箱",
            owner_id=user.id,
            invite_code=invite_code,
        )
        db.add(household)
        await db.flush()

        user.household_id = household.id
        await db.flush()

    # create household for users without one
    if user.household_id is None:
        invite_code = "".join(random.choices(string.digits, k=6))
        household = Household(
            name=f"{user.nickname}的冰箱",
            owner_id=user.id,
            invite_code=invite_code,
        )
        db.add(household)
        await db.flush()
        user.household_id = household.id
        await db.flush()

    token = create_access_token({"sub": str(user.id)})
    return user, token