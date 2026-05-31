import uuid
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_, func
from server.models.ingredient import Ingredient
from server.schemas.ingredient import IngredientCreate, IngredientUpdate
from server.utils.freshness import calc_freshness


async def get_ingredients(
    db: AsyncSession,
    household_id: uuid.UUID,
    zone: str | None = None,
    category: str | None = None,
    freshness: str | None = None,
    search: str | None = None,
    is_consumed: bool | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[Ingredient], int]:
    query = select(Ingredient).where(
        Ingredient.household_id == household_id,
    )

    if is_consumed is not None:
        query = query.where(Ingredient.is_consumed == is_consumed)
    else:
        query = query.where(Ingredient.is_consumed == False)

    if zone:
        query = query.where(Ingredient.zone == zone)
    if category:
        query = query.where(Ingredient.category == category)
    if freshness:
        query = query.where(Ingredient.freshness == freshness)
    if search:
        query = query.where(Ingredient.name.ilike(f"%{search}%"))

    count_query = select(func.count()).select_from(Ingredient).where(
        Ingredient.household_id == household_id,
    )
    if is_consumed is not None:
        count_query = count_query.where(Ingredient.is_consumed == is_consumed)
    else:
        count_query = count_query.where(Ingredient.is_consumed == False)

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.order_by(Ingredient.expire_date.asc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    items = result.scalars().all()
    return list(items), total


async def get_expiring_ingredients(db: AsyncSession, household_id: uuid.UUID, days: int = 3) -> list[Ingredient]:
    from datetime import timedelta
    cutoff = date.today() + timedelta(days=days)
    result = await db.execute(
        select(Ingredient).where(
            Ingredient.household_id == household_id,
            Ingredient.is_consumed == False,
            Ingredient.expire_date <= cutoff,
        ).order_by(Ingredient.expire_date.asc())
    )
    return list(result.scalars().all())


async def get_ingredient(db: AsyncSession, ingredient_id: uuid.UUID) -> Ingredient | None:
    result = await db.execute(select(Ingredient).where(Ingredient.id == ingredient_id))
    return result.scalar_one_or_none()


async def create_ingredient(db: AsyncSession, data: IngredientCreate, household_id: uuid.UUID, user_id: uuid.UUID) -> Ingredient:
    f = calc_freshness(data.expire_date)
    ingredient = Ingredient(
        household_id=household_id,
        added_by=user_id,
        name=data.name,
        category=data.category,
        zone=data.zone,
        quantity=data.quantity,
        unit=data.unit,
        purchase_date=data.purchase_date,
        expire_date=data.expire_date,
        freshness=f["status"],
        barcode=data.barcode,
        icon_url=data.icon_url,
        image_url=data.image_url,
        note=data.note,
    )
    db.add(ingredient)
    await db.flush()
    return ingredient


async def update_ingredient(db: AsyncSession, ingredient_id: uuid.UUID, data: IngredientUpdate) -> Ingredient | None:
    ingredient = await get_ingredient(db, ingredient_id)
    if ingredient is None:
        return None

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(ingredient, key, value)

    if "expire_date" in update_data:
        f = calc_freshness(ingredient.expire_date)
        ingredient.freshness = f["status"]

    await db.flush()
    return ingredient


async def delete_ingredient(db: AsyncSession, ingredient_id: uuid.UUID) -> bool:
    ingredient = await get_ingredient(db, ingredient_id)
    if ingredient is None:
        return False
    await db.delete(ingredient)
    await db.flush()
    return True


async def mark_consumed(db: AsyncSession, ingredient_id: uuid.UUID, quantity: float | None = None) -> Ingredient | None:
    ingredient = await get_ingredient(db, ingredient_id)
    if ingredient is None:
        return None

    if quantity is not None:
        ingredient.quantity = max(0, ingredient.quantity - quantity)
        if ingredient.quantity <= 0:
            ingredient.is_consumed = True
    else:
        ingredient.is_consumed = True
        ingredient.quantity = 0

    await db.flush()
    return ingredient


async def batch_delete(db: AsyncSession, ids: list[str]) -> int:
    count = 0
    for id_str in ids:
        ingredient = await get_ingredient(db, uuid.UUID(id_str))
        if ingredient:
            await db.delete(ingredient)
            count += 1
    await db.flush()
    return count