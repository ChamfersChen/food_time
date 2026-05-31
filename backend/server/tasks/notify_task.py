from server.database import async_session_factory
from server.services.notify_service import (
    create_expiry_notifications,
    create_stock_notifications,
    create_inactive_notifications,
    send_pending_notifications,
)


async def create_all_notifications_job():
    async with async_session_factory() as db:
        c1 = await create_expiry_notifications(db)
        c2 = await create_stock_notifications(db)
        c3 = await create_inactive_notifications(db)
        await db.commit()
        print(f"[notify_task] Created {c1} expiry + {c2} stock + {c3} inactive notifications")


async def send_expiry_notifications_job():
    async with async_session_factory() as db:
        count = await send_pending_notifications(db)
        await db.commit()
        print(f"[notify_task] Sent {count} notifications")