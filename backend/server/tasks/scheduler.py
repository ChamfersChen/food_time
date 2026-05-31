from apscheduler.schedulers.asyncio import AsyncIOScheduler
from server.tasks.freshness_task import update_freshness_job
from server.tasks.notify_task import create_all_notifications_job, send_expiry_notifications_job

scheduler = AsyncIOScheduler()

scheduler.add_job(
    update_freshness_job,
    "cron",
    hour=1,
    minute=0,
    id="update_freshness",
    replace_existing=True,
)

scheduler.add_job(
    create_all_notifications_job,
    "cron",
    hour=8,
    minute=0,
    id="create_notifications",
    replace_existing=True,
)

scheduler.add_job(
    send_expiry_notifications_job,
    "cron",
    hour=9,
    minute=0,
    id="send_expiry_notifications",
    replace_existing=True,
)