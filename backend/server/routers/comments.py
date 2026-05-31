import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from server.database import get_db
from server.models.user import User
from server.models.comment import CookingLogComment
from server.schemas.comment import CommentCreate, CommentResponse
from server.middleware.auth_middleware import get_current_user

router = APIRouter(prefix="/comments", tags=["评论"])


@router.get("/log/{log_id}", response_model=list[CommentResponse])
async def get_log_comments(
    log_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(CookingLogComment).where(CookingLogComment.log_id == log_id).order_by(CookingLogComment.created_at.asc())
    )
    comments = list(result.scalars().all())

    resp = []
    for c in comments:
        user_result = await db.execute(select(User).where(User.id == c.user_id))
        user = user_result.scalar_one_or_none()
        resp.append(CommentResponse(
            id=c.id,
            log_id=c.log_id,
            user_id=c.user_id,
            nickname=user.nickname if user else None,
            avatar_url=user.avatar_url if user else None,
            content=c.content,
            created_at=c.created_at,
        ))
    await db.commit()
    return resp


@router.post("", response_model=CommentResponse, status_code=201)
async def create_comment(
    data: CommentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    comment = CookingLogComment(
        log_id=uuid.UUID(data.log_id),
        user_id=current_user.id,
        content=data.content,
    )
    db.add(comment)
    await db.flush()
    await db.refresh(comment)
    await db.commit()

    return CommentResponse(
        id=comment.id,
        log_id=comment.log_id,
        user_id=comment.user_id,
        nickname=current_user.nickname,
        avatar_url=current_user.avatar_url,
        content=comment.content,
        created_at=comment.created_at,
    )
