import uuid
from datetime import date
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from server.database import get_db
from server.models.user import User
from server.models.cooking_log import CookingLog
from server.schemas.cooking_log import (
    CookingLogCreate,
    CookingLogResponse,
    CookingStatsResponse,
)
from server.services.cooking_service import get_cooking_logs, create_cooking_log, get_stats
from server.middleware.auth_middleware import get_current_user

router = APIRouter(prefix="/cooking-logs", tags=["烹饪记录"])


@router.get("", response_model=dict)
async def list_cooking_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    meal_type: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, total = await get_cooking_logs(
        db,
        user_id=current_user.id,
        page=page,
        page_size=page_size,
        meal_type=meal_type,
    )
    await db.commit()
    return {
        "list": [CookingLogResponse.model_validate(i) for i in items],
        "total": total,
    }


@router.post("", response_model=CookingLogResponse, status_code=201)
async def create_log(
    data: CookingLogCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    log = await create_cooking_log(db, data, current_user)
    await db.commit()
    await db.refresh(log)
    return CookingLogResponse.model_validate(log)


@router.get("/stats", response_model=CookingStatsResponse)
async def cooking_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stats = await get_stats(db, current_user.id)
    await db.commit()
    return stats


@router.get("/calendar", response_model=dict)
async def calendar_dates(
    year: int = Query(...),
    month: int = Query(..., ge=1, le=12),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    next_month = month + 1
    next_year = year
    if next_month > 12:
        next_month = 1
        next_year = year + 1
    result = await db.execute(
        select(func.date(CookingLog.cooked_at)).where(
            CookingLog.user_id == current_user.id,
            CookingLog.cooked_at >= date(year, month, 1),
            CookingLog.cooked_at < date(next_year, next_month, 1),
        ).distinct()
    )
    dates = [row[0].isoformat() for row in result.all()]
    await db.commit()
    return {"dates": dates}


@router.get("/by-date", response_model=dict)
async def logs_by_date(
    date: date = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(CookingLog).where(
            CookingLog.user_id == current_user.id,
            func.date(CookingLog.cooked_at) == date,
        ).order_by(CookingLog.created_at.desc())
    )
    items = list(result.scalars().all())
    await db.commit()
    return {"list": [CookingLogResponse.model_validate(i) for i in items], "total": len(items)}


@router.get("/household", response_model=dict)
async def list_household_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user.household_id:
        raise HTTPException(status_code=400, detail="未加入家庭冰箱")
    items, total = await get_cooking_logs(db, household_id=current_user.household_id, page=page, page_size=page_size)
    await db.commit()
    return {
        "list": [CookingLogResponse.model_validate(i) for i in items],
        "total": total,
    }


@router.put("/{log_id}", response_model=CookingLogResponse)
async def update_log(
    log_id: uuid.UUID,
    data: CookingLogCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(CookingLog).where(
            CookingLog.id == log_id,
            CookingLog.user_id == current_user.id,
        )
    )
    log = result.scalar_one_or_none()
    if log is None:
        raise HTTPException(status_code=404, detail="烹饪记录不存在")

    log.recipe_name = data.recipe_name
    if data.cooked_at:
        log.cooked_at = data.cooked_at
    if data.meal_type is not None:
        log.meal_type = data.meal_type
    if data.duration is not None:
        log.duration = data.duration
    if data.rating is not None:
        log.rating = data.rating
    if data.note is not None:
        log.note = data.note
    if data.photo_urls:
        log.photo_urls = data.photo_urls

    await db.commit()
    await db.refresh(log)
    return CookingLogResponse.model_validate(log)


@router.delete("/{log_id}")
async def delete_log(
    log_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(CookingLog).where(
            CookingLog.id == log_id,
            CookingLog.user_id == current_user.id,
        )
    )
    log = result.scalar_one_or_none()
    if log is None:
        raise HTTPException(status_code=404, detail="烹饪记录不存在")
    await db.delete(log)
    await db.commit()
    return {"code": 0, "message": "删除成功"}


@router.get("/{log_id}", response_model=CookingLogResponse)
async def get_log_detail(
    log_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(CookingLog).where(
            CookingLog.id == log_id,
            CookingLog.user_id == current_user.id,
        )
    )
    log = result.scalar_one_or_none()
    if log is None:
        raise HTTPException(status_code=404, detail="烹饪记录不存在")
    await db.commit()
    return CookingLogResponse.model_validate(log)