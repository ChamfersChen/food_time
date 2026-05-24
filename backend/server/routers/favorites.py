from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from server.database import get_db
from server.models.user import User
from server.models.favorite import UserFavorite
from server.models.recipe import Recipe
from server.schemas.recipe import RecipeResponse
from server.middleware.auth_middleware import get_current_user
from pydantic import BaseModel
import uuid


class FavoriteCreate(BaseModel):
    recipe_id: str

router = APIRouter(prefix="/favorites", tags=["收藏"])


@router.get("")
async def list_favorites(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(UserFavorite, Recipe)
        .join(Recipe, UserFavorite.recipe_id == Recipe.id)
        .where(UserFavorite.user_id == current_user.id)
        .order_by(UserFavorite.created_at.desc())
    )
    rows = result.all()
    return [
        {"id": str(fav.id), "recipe_id": str(fav.recipe_id), "created_at": fav.created_at.isoformat(), "recipe": RecipeResponse.model_validate(recipe).model_dump()}
        for fav, recipe in rows
    ]


@router.post("")
async def add_favorite(
    body: FavoriteCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rid = uuid.UUID(body.recipe_id)
    result = await db.execute(
        select(UserFavorite).where(
            UserFavorite.user_id == current_user.id,
            UserFavorite.recipe_id == rid,
        )
    )
    if result.scalar_one_or_none():
        return {"code": 0, "message": "已收藏"}

    fav = UserFavorite(user_id=current_user.id, recipe_id=rid)
    db.add(fav)
    await db.commit()
    return {"code": 0, "message": "收藏成功", "is_favorited": True}


@router.delete("/{recipe_id}")
async def remove_favorite(
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
    fav = result.scalar_one_or_none()
    if fav:
        await db.delete(fav)
        await db.commit()
    return {"code": 0, "message": "取消收藏", "is_favorited": False}