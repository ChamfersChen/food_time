import uuid
from datetime import date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from server.models.notification import Notification
from server.models.ingredient import Ingredient
from server.models.user import User
from server.utils.wechat import send_subscribe_message
from server.config import get_settings

settings = get_settings()


async def create_expiry_notifications(db: AsyncSession) -> int:
    today = date.today()

    # find ingredients expiring within N days per user preference
    result = await db.execute(
        select(Ingredient).where(
            Ingredient.is_consumed == False,
            Ingredient.is_deleted == False,
        )
    )
    ingredients = list(result.scalars().all())

    count = 0
    for ing in ingredients:
        user_result = await db.execute(
            select(User).where(User.household_id == ing.household_id, User.notification_open == True)
        )
        users = list(user_result.scalars().all())

        for user in users:
            trigger_date = ing.expire_date - timedelta(days=user.notify_days_before)
            if trigger_date <= today:
                existing = await db.execute(
                    select(Notification).where(
                        Notification.ingredient_id == ing.id,
                        Notification.user_id == user.id,
                        Notification.type == "expiring_soon",
                        Notification.trigger_date == today,
                    )
                )
                if existing.scalar_one_or_none() is None:
                    notif_type = "expired" if ing.expire_date < today else "expiring_soon"
                    notif = Notification(
                        household_id=ing.household_id,
                        user_id=user.id,
                        openid=user.openid,
                        ingredient_id=ing.id,
                        type=notif_type,
                        trigger_date=today,
                    )
                    db.add(notif)
                    count += 1

    await db.flush()
    return count


async def send_pending_notifications(db: AsyncSession) -> int:
    today = date.today()
    result = await db.execute(
        select(Notification).where(
            Notification.is_sent == False,
            Notification.trigger_date <= today,
        )
    )
    notifications = list(result.scalars().all())

    sent_count = 0
    for notif in notifications:
        if notif.ingredient_id:
            ing_result = await db.execute(
                select(Ingredient).where(Ingredient.id == notif.ingredient_id)
            )
            ingredient = ing_result.scalar_one_or_none()
            ing_name = ingredient.name if ingredient else "食材"
            exp_date = str(ingredient.expire_date) if ingredient else "未知"
        else:
            ing_name = "今日推荐菜谱"
            exp_date = ""

        success = await send_subscribe_message(
            openid=notif.openid,
            template_id=settings.WX_EXPIRY_TMPL_ID,
            data={
                "thing1": {"value": ing_name[:20]},
                "date2": {"value": exp_date},
            },
        )
        if success:
            notif.is_sent = True
            sent_count += 1

    await db.flush()
    return sent_count