from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from server.database import get_db
from server.models.user import User
from server.models.cooking_log import CookingLog
from server.models.ingredient import Ingredient
from server.schemas.user import UserUpdateRequest, UserResponse
from server.middleware.auth_middleware import get_current_user
from server.utils.minio_client import upload_avatar, validate_image_ext
from server.config import get_settings
from datetime import date, timedelta
from pydantic import BaseModel

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
                            "notification_open", "notify_days_before", "notify_hour",
                            "notify_expiry", "notify_stock", "notify_inactive",
                            "inactive_days", "subscribed_templates")}
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
            Ingredient.is_consumed == False,
        )
    )
    saved_items = saved_result.scalar() or 0

    return {
        "totalMeals": total_meals,
        "streakDays": streak_days,
        "savedItems": saved_items,
    }


class SubscribeRequest(BaseModel):
    templates: list[str]


@router.post("/subscribe")
async def subscribe_templates(
    data: SubscribeRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    current_user.subscribed_templates = list(set(current_user.subscribed_templates + data.templates))
    await db.commit()
    return {"subscribed_templates": current_user.subscribed_templates}


@router.post("/avatar")
async def upload_user_avatar(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    settings = get_settings()
    if not file.filename:
        raise HTTPException(status_code=400, detail="文件名为空")

    file_ext = validate_image_ext(file.filename)
    if file_ext is None:
        raise HTTPException(status_code=400, detail="仅支持 jpg/jpeg/png/webp 格式")

    contents = await file.read()
    if len(contents) > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail=f"文件大小不能超过 {settings.MAX_FILE_SIZE_MB}MB")

    url = await upload_avatar(contents, file_ext)
    current_user.avatar_url = url
    await db.commit()
    await db.refresh(current_user)

    return {"avatar_url": url, "user": UserResponse.model_validate(current_user)}