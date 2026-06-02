import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from server.models.ingredient import Ingredient
from server.models.recipe import Recipe
from server.models.cooking_log import CookingLog
from server.models.user import User


async def get_active_ingredients(db: AsyncSession, household_id: uuid.UUID) -> list[Ingredient]:
    result = await db.execute(
        select(Ingredient).where(
            Ingredient.household_id == household_id,
            Ingredient.is_consumed == False,
        )
    )
    return list(result.scalars().all())


async def get_recent_recipe_ids(db: AsyncSession, user_id: uuid.UUID, days: int = 7) -> set[uuid.UUID]:
    from datetime import timedelta
    from sqlalchemy import and_
    cutoff = __import__("datetime").date.today() - timedelta(days=days)
    result = await db.execute(
        select(CookingLog.recipe_id).where(
            CookingLog.user_id == user_id,
            CookingLog.cooked_at >= cutoff,
            CookingLog.recipe_id.isnot(None),
        )
    )
    return {row[0] for row in result.all()}


def calc_preference_score(recipe: Recipe, user: User) -> float:
    if not user.flavor_pref:
        return 0.5

    recipe_tags = set(recipe.tags or [])
    user_pref = set(user.flavor_pref or [])

    if not recipe_tags:
        return 0.0

    overlap = len(recipe_tags & user_pref)
    return min(overlap / max(len(user_pref), 1), 1.0)


async def get_recommendations(
    db: AsyncSession,
    user: User,
    limit: int = 10,
) -> list[dict]:
    ingredients = await get_active_ingredients(db, user.household_id)
    ingredient_names = {i.name for i in ingredients}
    expiring_names = {i.name for i in ingredients if i.freshness == "expiring"}

    recent_recipe_ids = await get_recent_recipe_ids(db, user.id)

    recipes_result = await db.execute(
        select(Recipe).where(Recipe.is_public == True)
    )
    recipes = list(recipes_result.scalars().all())

    scored = []
    for recipe in recipes:
        recipe_ingredients = recipe.ingredients or []
        essential = [i for i in recipe_ingredients if i.get("is_essential", False)]
        if not essential:
            continue

        matched = []
        for ing in essential:
            if ing["name"] in ingredient_names:
                matched.append(ing)
            elif "aliases" in ing:
                for alias in ing["aliases"]:
                    if alias in ingredient_names:
                        matched.append(ing)
                        break

        coverage = len(matched) / len(essential) if essential else 0

        expiring_hit = 0
        for ing in recipe_ingredients:
            name = ing["name"]
            if name in expiring_names:
                expiring_hit += 1
            if "aliases" in ing:
                for alias in ing["aliases"]:
                    if alias in expiring_names:
                        expiring_hit += 1
                        break

        expiring_score = min(expiring_hit / 3, 1.0)
        pref_score = calc_preference_score(recipe, user)
        diversity = 0.0 if recipe.id in recent_recipe_ids else 1.0

        score = (
            coverage * 0.40
            + expiring_score * 0.30
            + pref_score * 0.20
            + diversity * 0.10
        )

        if coverage < 0.5:
            continue

        scored.append({
            "recipe": recipe,
            "score": score,
            "match_percent": int(coverage * 100),
            "has_expiring_ingredient": expiring_hit > 0,
        })

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:limit]


def _normalize(s: str) -> str:
    return s.strip().lower()


async def check_recipe_ingredients(
    db: AsyncSession,
    recipe: Recipe,
    household_id: uuid.UUID,
) -> list[dict]:
    """For each recipe ingredient, check availability in the household fridge."""
    fridge_ings = await get_active_ingredients(db, household_id)
    fridge_map: dict[str, tuple[float, str]] = {}
    for fi in fridge_ings:
        key = _normalize(fi.name)
        fridge_map[key] = (fi.quantity, fi.unit)

    import re as _re

    result = []
    for ri in recipe.ingredients or []:
        name = ri.get("name", "")
        qty = ri.get("quantity")
        unit = ri.get("unit")
        if qty is None or unit is None:
            amount = ri.get("amount", "")
            if amount == "适量":
                qty, unit = 0, "适量"
            else:
                m = _re.match(r"^([\d.]+)\s*(.+)$", amount)
                if m:
                    qty, unit = float(m.group(1)), m.group(2)
                else:
                    qty, unit = 0, amount or "克"
        else:
            qty = float(qty) if qty else 0
        key = _normalize(name)

        in_fridge = False
        sufficient = False
        matched_name = None
        matched_qty = 0.0

        if key in fridge_map:
            in_fridge = True
            matched_qty, matched_unit = fridge_map[key]
            if matched_qty >= qty:
                sufficient = True
            matched_name = name
        else:
            for fk, (fq, fu) in fridge_map.items():
                if key in fk or fk in key:
                    in_fridge = True
                    matched_qty = fq
                    if fq >= qty:
                        sufficient = True
                    matched_name = fk
                    break

        result.append({
            "name": name,
            "quantity": qty,
            "unit": unit,
            "inFridge": in_fridge,
            "sufficient": sufficient,
            "matched_qty": matched_qty,
            "matched_name": matched_name,
        })

    return result