import uuid
from datetime import date
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
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
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, total = await get_cooking_logs(db, current_user.id, page, page_size)
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


@router.get("/by-date", response_model=dict)
async def logs_by_date(
    date: date = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(CookingLog).where(
            CookingLog.user_id == current_user.id,
            CookingLog.cooked_at == date,
        ).order_by(CookingLog.created_at.desc())
    )
    items = list(result.scalars().all())
    await db.commit()
    return {"list": [CookingLogResponse.model_validate(i) for i in items], "total": len(items)}


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