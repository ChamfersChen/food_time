import uuid
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from server.database import get_db
from server.models.user import User
from server.schemas.ingredient import (
    IngredientCreate,
    IngredientUpdate,
    IngredientResponse,
    IngredientListResponse,
    BatchDeleteRequest,
)
from server.services.ingredient_service import (
    get_ingredients,
    get_expiring_ingredients,
    get_ingredient,
    create_ingredient,
    update_ingredient,
    delete_ingredient,
    mark_consumed,
    batch_delete,
)
from server.middleware.auth_middleware import get_current_user

router = APIRouter(prefix="/ingredients", tags=["食材"])


@router.get("", response_model=IngredientListResponse)
async def list_ingredients(
    zone: str | None = None,
    category: str | None = None,
    freshness: str | None = None,
    search: str | None = None,
    is_consumed: bool | None = None,
    is_deleted: bool | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user.household_id:
        raise HTTPException(status_code=400, detail="请先创建家庭冰箱")
    items, total = await get_ingredients(
        db, current_user.household_id, zone, category, freshness, search,
        is_consumed, is_deleted, page, page_size
    )
    await db.commit()
    return IngredientListResponse(
        list=[IngredientResponse.model_validate(i) for i in items],
        total=total,
    )


@router.get("/expiring", response_model=list[IngredientResponse])
async def list_expiring(
    days: int = Query(3, ge=1, le=14),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user.household_id:
        raise HTTPException(status_code=400, detail="请先创建家庭冰箱")
    items = await get_expiring_ingredients(db, current_user.household_id, days)
    await db.commit()
    return [IngredientResponse.model_validate(i) for i in items]


@router.post("", response_model=IngredientResponse, status_code=status.HTTP_201_CREATED)
async def add_ingredient(
    data: IngredientCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user.household_id:
        raise HTTPException(status_code=400, detail="请先创建家庭冰箱")
    item = await create_ingredient(db, data, current_user.household_id, current_user.id)
    await db.commit()
    await db.refresh(item)
    return IngredientResponse.model_validate(item)


@router.get("/{ingredient_id}", response_model=IngredientResponse)
async def get_ingredient_detail(
    ingredient_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = await get_ingredient(db, ingredient_id)
    if item is None or item.is_deleted:
        raise HTTPException(status_code=404, detail="食材不存在")
    return IngredientResponse.model_validate(item)


@router.put("/{ingredient_id}", response_model=IngredientResponse)
async def update_ingredient_detail(
    ingredient_id: uuid.UUID,
    data: IngredientUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = await update_ingredient(db, ingredient_id, data)
    if item is None:
        raise HTTPException(status_code=404, detail="食材不存在")
    await db.commit()
    await db.refresh(item)
    return IngredientResponse.model_validate(item)


@router.delete("/{ingredient_id}")
async def delete_ingredient_api(
    ingredient_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    success = await delete_ingredient(db, ingredient_id)
    if not success:
        raise HTTPException(status_code=404, detail="食材不存在")
    await db.commit()
    return {"code": 0, "message": "删除成功"}


@router.put("/{ingredient_id}/consume", response_model=IngredientResponse)
async def consume_ingredient(
    ingredient_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from server.schemas.ingredient import ConsumeRequest
    item = await mark_consumed(db, ingredient_id)
    if item is None:
        raise HTTPException(status_code=404, detail="食材不存在")
    await db.commit()
    await db.refresh(item)
    return IngredientResponse.model_validate(item)


@router.post("/batch-delete")
async def batch_delete_api(
    data: BatchDeleteRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    count = await batch_delete(db, data.ids)
    await db.commit()
    return {"code": 0, "message": f"已删除 {count} 项"}