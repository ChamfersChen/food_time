from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from server.database import get_db
from server.models.user import User
from server.models.cooking_log import CookingLog
from server.models.ingredient import Ingredient
from server.schemas.user import UserUpdateRequest, UserResponse
from server.middleware.auth_middleware import get_current_user
from datetime import date, timedelta

router = APIRouter(prefix="/users", tags=["用户"])


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)


@router.get("/profile", response_model=UserResponse)
async def get_profile(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    data: UserUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(current_user, key, value)
    await db.commit()
    await db.refresh(current_user)
    return UserResponse.model_validate(current_user)


@router.put("/preferences")
async def update_preferences(
    data: UserUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    pref_fields = {k: v for k, v in data.model_dump(exclude_unset=True).items()
                   if k in ("diet_type", "disliked", "skill_level", "flavor_pref",
                            "notification_open", "notify_days_before")}
    for key, value in pref_fields.items():
        setattr(current_user, key, value)
    await db.commit()
    await db.refresh(current_user)
    return UserResponse.model_validate(current_user).model_dump()


@router.put("/me", response_model=UserResponse)
async def update_me(
    data: UserUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(current_user, key, value)
    await db.commit()
    await db.refresh(current_user)
    return UserResponse.model_validate(current_user)


@router.get("/statistics")
async def get_statistics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    now = date.today()
    month_start = now.replace(day=1)

    total_meals_result = await db.execute(
        select(func.count()).select_from(CookingLog).where(
            CookingLog.user_id == current_user.id,
            CookingLog.cooked_at >= month_start,
        )
    )
    total_meals = total_meals_result.scalar() or 0

    streak_days = 0
    d = now
    for _ in range(365):
        r = await db.execute(
            select(func.count()).select_from(CookingLog).where(
                CookingLog.user_id == current_user.id,
                CookingLog.cooked_at == d,
            )
        )
        if (r.scalar() or 0) > 0:
            streak_days += 1
            d -= timedelta(days=1)
        else:
            break

    saved_result = await db.execute(
        select(func.count()).select_from(Ingredient).where(
            Ingredient.added_by == current_user.id,
            Ingredient.is_deleted == False,
            Ingredient.is_consumed == False,
        )
    )
    saved_items = saved_result.scalar() or 0

    return {
        "totalMeals": total_meals,
        "streakDays": streak_days,
        "savedItems": saved_items,
    }