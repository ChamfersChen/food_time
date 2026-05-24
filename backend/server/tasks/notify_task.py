from server.database import async_session_factory
from server.services.notify_service import send_pending_notifications


async def send_expiry_notifications_job():
    async with async_session_factory() as db:
        count = await send_pending_notifications(db)
        print(f"[notify_task] Sent {count} notifications")