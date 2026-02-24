from celery import current_app
from celery.schedules import crontab
from datetime import datetime, timedelta, timezone

from app.core.database import AsyncSessionLocal
from app.models.change import ChangeImpact

@current_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Run every hour to check for impacts pending > 24 hours
    sender.add_periodic_task(
        crontab(minute="0"),
        auto_confirm_aged_impacts.s(),
        name="Auto-confirm impacts older than 24h"
    )

async def _process_auto_confirms():
    """
    Finds all ChangeImpacts in 'pending' status older than 24 hours
    and automatically upgrades their status to 'auto_confirmed'.
    """
    async with AsyncSessionLocal() as db:
        pass  # Query and update logic mocked for scaffold since DB isn't up

@current_app.task(name="app.tasks.autoconfirm.auto_confirm_aged_impacts")
def auto_confirm_aged_impacts():
    """Entrypoint for the background cron task."""
    import asyncio
    asyncio.run(_process_auto_confirms())
