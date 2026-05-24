from datetime import date, timedelta
from sqlalchemy import update, case, and_
from server.models.ingredient import Ingredient
from server.database import async_session_factory


async def update_freshness_job():
    async with async_session_factory() as db:
        today = date.today()
        three_days_later = today + timedelta(days=3)

        await db.execute(
            update(Ingredient)
            .where(
                Ingredient.is_consumed == False,
                Ingredient.is_deleted == False,
            )
            .values(
                freshness=case(
                    (Ingredient.expire_date < today, "expired"),
                    (Ingredient.expire_date <= three_days_later, "expiring"),
                    else_="fresh",
                )
            )
        )
        await db.commit()
        print(f"[freshness_task] Updated freshness for all ingredients at {today}")