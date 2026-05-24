import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from server.models.recipe import Recipe
from server.models.user import User


async def get_recipes(
    db: AsyncSession,
    tags: str | None = None,
    difficulty: str | None = None,
    q: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[Recipe], int]:
    query = select(Recipe).where(Recipe.is_public == True)

    if tags:
        tag_list = [t.strip() for t in tags.split(",")]
        query = query.where(Recipe.tags.op("@>")(tag_list))

    if difficulty:
        query = query.where(Recipe.difficulty == difficulty)

    if q:
        query = query.where(Recipe.name.ilike(f"%{q}%"))

    total_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = total_result.scalar() or 0

    query = query.order_by(Recipe.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    items = list(result.scalars().all())
    return items, total


async def get_recipe(db: AsyncSession, recipe_id: uuid.UUID) -> Recipe | None:
    result = await db.execute(select(Recipe).where(Recipe.id == recipe_id))
    recipe = result.scalar_one_or_none()
    if recipe:
        recipe.view_count += 1
        await db.flush()
    return recipe


async def create_recipe(db: AsyncSession, data: dict, author_id: uuid.UUID) -> Recipe:
    recipe = Recipe(
        name=data["name"],
        description=data.get("description"),
        cover_url=data.get("cover_url"),
        tags=data.get("tags", []),
        cuisine=data.get("cuisine"),
        cook_time=data["cook_time"],
        difficulty=data.get("difficulty", "easy"),
        calories=data.get("calories"),
        servings=data.get("servings", 2),
        ingredients=data.get("ingredients", []),
        steps=data.get("steps", []),
        source="user",
        author_id=author_id,
        is_public=data.get("is_public", True),
    )
    db.add(recipe)
    await db.flush()
    return recipe


async def update_recipe(db: AsyncSession, recipe_id: uuid.UUID, data: dict) -> Recipe | None:
    recipe = await get_recipe(db, recipe_id)
    if recipe is None:
        return None

    for key, value in data.items():
        if value is not None:
            setattr(recipe, key, value)

    await db.flush()
    return recipe


async def delete_recipe(db: AsyncSession, recipe_id: uuid.UUID) -> bool:
    recipe = await get_recipe(db, recipe_id)
    if recipe is None:
        return False
    await db.delete(recipe)
    await db.flush()
    return True


async def get_random_recipe(db: AsyncSession) -> Recipe | None:
    from sqlalchemy.sql.expression import func as sqlfunc
    result = await db.execute(
        select(Recipe).where(Recipe.is_public == True).order_by(sqlfunc.random()).limit(1)
    )
    return result.scalar_one_or_none()