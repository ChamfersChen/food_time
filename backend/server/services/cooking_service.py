import uuid
from datetime import date, datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from server.models.cooking_log import CookingLog
from server.models.ingredient import Ingredient
from server.models.recipe import Recipe
from server.schemas.cooking_log import CookingLogCreate, CookingStatsResponse
from server.models import User


async def get_cooking_logs(
    db: AsyncSession,
    user_id: uuid.UUID | None = None,
    household_id: uuid.UUID | None = None,
    page: int = 1,
    page_size: int = 20,
    meal_type: str | None = None,
) -> tuple[list[CookingLog], int]:
    from sqlalchemy import func

    if household_id:
        cond = CookingLog.household_id == household_id
    elif user_id:
        cond = CookingLog.user_id == user_id
    else:
        return [], 0

    if meal_type:
        cond = cond & (CookingLog.meal_type == meal_type)

    total_result = await db.execute(
        select(func.count()).select_from(CookingLog).where(cond)
    )
    total = total_result.scalar() or 0

    result = await db.execute(
        select(CookingLog)
        .where(cond)
        .order_by(CookingLog.cooked_at.desc(), CookingLog.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    items = list(result.scalars().all())
    return items, total


async def create_cooking_log(
    db: AsyncSession,
    data: CookingLogCreate,
    user: User,
) -> CookingLog:
    if data.cooked_at is None:
        data.cooked_at = datetime.now()

    log = CookingLog(
        user_id=user.id,
        household_id=user.household_id,
        recipe_id=uuid.UUID(data.recipe_id) if data.recipe_id else None,
        recipe_name=data.recipe_name,
        cooked_at=data.cooked_at,
        meal_type=data.meal_type,
        duration=data.duration,
        rating=data.rating,
        note=data.note,
        photo_urls=data.photo_urls,
        mood=data.mood,
        consumed_ingredients=data.consumed_ingredients,
    )
    db.add(log)

    for item in data.consumed_ingredients:
        ing_id = item.get("ingredient_id")
        if ing_id:
            result = await db.execute(
                select(Ingredient).where(Ingredient.id == uuid.UUID(ing_id))
            )
            ingredient = result.scalar_one_or_none()
            if ingredient and not ingredient.is_consumed:
                qty_used = item.get("quantity_used", 0)
                ingredient.quantity = max(0, ingredient.quantity - qty_used)
                if ingredient.quantity <= 0:
                    ingredient.is_consumed = True

    if data.recipe_id and data.rating:
        recipe_result = await db.execute(
            select(Recipe).where(Recipe.id == uuid.UUID(data.recipe_id))
        )
        recipe = recipe_result.scalar_one_or_none()
        if recipe:
            recipe.rating_count += 1
            recipe.rating_avg = (
                (recipe.rating_avg * (recipe.rating_count - 1) + data.rating) / recipe.rating_count
            )

    await db.flush()
    return log


async def get_stats(db: AsyncSession, user_id: uuid.UUID) -> CookingStatsResponse:
    from sqlalchemy import func, extract

    now = date.today()
    month_start = now.replace(day=1)

    result = await db.execute(
        select(func.count()).select_from(CookingLog).where(
            CookingLog.user_id == user_id,
            CookingLog.cooked_at >= month_start,
        )
    )
    total_meals = result.scalar() or 0

    result = await db.execute(
        select(func.count()).select_from(CookingLog).where(
            CookingLog.user_id == user_id,
        )
    )
    all_meals = result.scalar() or 0

    result = await db.execute(
        select(func.count(func.distinct(func.date(CookingLog.cooked_at)))).select_from(
            CookingLog
        ).where(CookingLog.user_id == user_id)
    )

    streak_days = 0
    d = now
    while True:
        result = await db.execute(
            select(func.count()).select_from(CookingLog).where(
                CookingLog.user_id == user_id,
                func.date(CookingLog.cooked_at) == d,
            )
        )
        if (result.scalar() or 0) > 0:
            streak_days += 1
            d = d - __import__("datetime").timedelta(days=1)
        else:
            break

    return CookingStatsResponse(
        total_meals=total_meals,
        ingredients_consumed=total_meals * 3,
        streak_days=streak_days,
    )