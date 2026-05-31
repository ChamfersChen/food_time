import uuid
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from server.database import get_db
from server.models.user import User
from server.schemas.recipe import RecipeCreate, RecipeUpdate, RecipeResponse, RecipeListResponse
from server.services.recipe_service import (
    get_recipes,
    get_recipe,
    create_recipe,
    update_recipe,
    delete_recipe,
    get_random_recipe,
)
from server.services.recommend_service import get_recommendations
from server.models.favorite import UserFavorite
from server.middleware.auth_middleware import get_current_user
from sqlalchemy import select

router = APIRouter(prefix="/recipes", tags=["菜谱"])


@router.get("", response_model=RecipeListResponse)
async def list_recipes(
    tags: str | None = None,
    difficulty: str | None = None,
    q: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, total = await get_recipes(db, tags, difficulty, q, page, page_size, current_user.household_id)
    recipe_responses = []
    for r in items:
        resp = RecipeResponse.model_validate(r)
        # check if favorited
        fav_result = await db.execute(
            select(UserFavorite).where(
                UserFavorite.user_id == current_user.id,
                UserFavorite.recipe_id == r.id,
            )
        )
        resp.is_favorited = fav_result.scalar_one_or_none() is not None
        recipe_responses.append(resp)
    await db.commit()
    return RecipeListResponse(list=recipe_responses, total=total)


@router.get("/recommend", response_model=list[RecipeResponse])
async def recommend_recipes(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    results = await get_recommendations(db, current_user, limit)
    recipe_responses = []
    for r in results:
        recipe = r["recipe"]
        resp = RecipeResponse.model_validate(recipe)
        resp.match_percent = r["match_percent"]
        resp.has_expiring_ingredient = r["has_expiring_ingredient"]
        fav_result = await db.execute(
            select(UserFavorite).where(
                UserFavorite.user_id == current_user.id,
                UserFavorite.recipe_id == recipe.id,
            )
        )
        resp.is_favorited = fav_result.scalar_one_or_none() is not None
        recipe_responses.append(resp)
    await db.commit()
    return recipe_responses


@router.get("/recommended", response_model=list[RecipeResponse])
async def recommended_recipes_alias(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await recommend_recipes(limit, db, current_user)


@router.get("/search", response_model=RecipeListResponse)
async def search_recipes(
    keyword: str | None = None,
    tags: str | None = None,
    difficulty: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, total = await get_recipes(db, tags, difficulty, keyword, page, page_size)
    recipe_responses = []
    for r in items:
        resp = RecipeResponse.model_validate(r)
        fav_result = await db.execute(
            select(UserFavorite).where(
                UserFavorite.user_id == current_user.id,
                UserFavorite.recipe_id == r.id,
            )
        )
        resp.is_favorited = fav_result.scalar_one_or_none() is not None
        recipe_responses.append(resp)
    await db.commit()
    return RecipeListResponse(list=recipe_responses, total=total)


@router.get("/random", response_model=RecipeResponse)
async def random_recipe(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    recipe = await get_random_recipe(db, current_user.household_id)
    if recipe is None:
        raise HTTPException(status_code=404, detail="暂无菜谱")
    await db.commit()
    resp = RecipeResponse.model_validate(recipe)
    return resp


@router.get("/{recipe_id}", response_model=RecipeResponse)
async def get_recipe_detail(
    recipe_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    recipe = await get_recipe(db, recipe_id)
    if recipe is None:
        raise HTTPException(status_code=404, detail="菜谱不存在")
    await db.commit()
    resp = RecipeResponse.model_validate(recipe)
    # check favorites
    fav_result = await db.execute(
        select(UserFavorite).where(
            UserFavorite.user_id == current_user.id,
            UserFavorite.recipe_id == recipe.id,
        )
    )
    resp.is_favorited = fav_result.scalar_one_or_none() is not None
    return resp


@router.post("", response_model=RecipeResponse, status_code=201)
async def create_recipe_api(
    data: RecipeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    recipe = await create_recipe(db, data.model_dump(), current_user.id, current_user.household_id)
    await db.commit()
    await db.refresh(recipe)
    return RecipeResponse.model_validate(recipe)


@router.put("/{recipe_id}", response_model=RecipeResponse)
async def update_recipe_api(
    recipe_id: uuid.UUID,
    data: RecipeUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    recipe = await get_recipe(db, recipe_id)
    if recipe is None:
        raise HTTPException(status_code=404, detail="菜谱不存在")
    if recipe.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="只能修改自己创建的菜谱")
    updated = await update_recipe(db, recipe_id, data.model_dump(exclude_unset=True))
    await db.commit()
    return RecipeResponse.model_validate(updated)


@router.delete("/{recipe_id}")
async def delete_recipe_api(
    recipe_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    recipe = await get_recipe(db, recipe_id)
    if recipe is None:
        raise HTTPException(status_code=404, detail="菜谱不存在")
    if recipe.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="只能删除自己创建的菜谱")
    await delete_recipe(db, recipe_id)
    await db.commit()
    return {"code": 0, "message": "删除成功"}


@router.post("/{recipe_id}/favorite")
async def toggle_favorite(
    recipe_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(UserFavorite).where(
            UserFavorite.user_id == current_user.id,
            UserFavorite.recipe_id == recipe_id,
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        await db.delete(existing)
        await db.commit()
        return {"code": 0, "message": "取消收藏", "is_favorited": False}
    else:
        fav = UserFavorite(user_id=current_user.id, recipe_id=recipe_id)
        db.add(fav)
        await db.commit()
        return {"code": 0, "message": "收藏成功", "is_favorited": True}