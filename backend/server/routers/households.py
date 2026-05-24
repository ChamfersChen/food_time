import uuid
import string
import random
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from server.database import get_db
from server.models.user import User
from server.models.household import Household
from server.middleware.auth_middleware import get_current_user

router = APIRouter(prefix="/households", tags=["家庭"])


@router.post("")
async def create_household(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.household_id:
        raise HTTPException(status_code=400, detail="已加入家庭冰箱")

    invite_code = "".join(random.choices(string.digits, k=6))
    household = Household(
        name=f"{current_user.nickname or '我的'}的冰箱",
        owner_id=current_user.id,
        invite_code=invite_code,
    )
    db.add(household)
    await db.flush()
    current_user.household_id = household.id
    await db.commit()
    await db.refresh(household)
    return {
        "id": str(household.id),
        "name": household.name,
        "owner_id": str(household.owner_id),
        "invite_code": household.invite_code,
        "members": [str(current_user.id)],
    }


@router.get("/current")
async def get_current_household(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user.household_id:
        raise HTTPException(status_code=400, detail="未加入家庭冰箱")

    result = await db.execute(
        select(Household).where(Household.id == current_user.household_id)
    )
    household = result.scalar_one_or_none()
    if not household:
        raise HTTPException(status_code=404, detail="家庭冰箱不存在")

    members_result = await db.execute(
        select(User).where(User.household_id == household.id)
    )
    members = list(members_result.scalars().all())

    return {
        "id": str(household.id),
        "name": household.name,
        "owner_id": str(household.owner_id),
        "invite_code": household.invite_code,
        "members": [
            {
                "id": str(m.id),
                "nickname": m.nickname,
                "avatar_url": m.avatar_url,
            }
            for m in members
        ],
    }


@router.post("/join")
async def join_household(
    invite_code: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Household).where(Household.invite_code == invite_code)
    )
    household = result.scalar_one_or_none()
    if not household:
        raise HTTPException(status_code=404, detail="邀请码无效")

    current_user.household_id = household.id
    await db.commit()
    return {"code": 0, "message": "加入成功", "household_id": str(household.id)}


@router.delete("/leave")
async def leave_household(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user.household_id:
        raise HTTPException(status_code=400, detail="未加入家庭冰箱")

    current_user.household_id = None
    await db.commit()
    return {"code": 0, "message": "已退出家庭冰箱"}