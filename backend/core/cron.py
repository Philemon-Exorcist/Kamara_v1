import logging
import httpx
import os
import asyncio
from typing import Any

from app.subscriptions.service import expire_due_trials

logger = logging.getLogger("Monicare.cron")

KEEP_ALIVE_URL = os.environ.get("KEEP_ALIVE_URL", "https://kamara.onrender.com/health")
KEEP_ALIVE_INTERVAL_SECONDS = int(os.environ.get("KEEP_ALIVE_INTERVAL_SECONDS", 600))
ENABLE_KEEP_ALIVE = os.environ.get("ENABLE_KEEP_ALIVE", "true").lower() in ("1", "true", "yes")
TRIAL_EXPIRY_INTERVAL_SECONDS = int(os.environ.get("TRIAL_EXPIRY_INTERVAL_SECONDS", 3600))


async def keep_alive_loop() -> None:
    async with httpx.AsyncClient(timeout=10.0) as client:
        while True:
            try:
                response = await client.get(KEEP_ALIVE_URL)
                logger.info("Keepalive ping %s -> %s", KEEP_ALIVE_URL, response.status_code)
            except Exception as err:
                logger.warning("Keepalive ping failed: %s", err)
            await asyncio.sleep(KEEP_ALIVE_INTERVAL_SECONDS)


async def trial_expiry_loop() -> None:
    while True:
        try:
            expired_count = expire_due_trials()
            if expired_count:
                logger.info("Expired %s trial subscription(s).", expired_count)
        except Exception as err:
            logger.warning("Trial expiry sweep failed: %s", err)
        await asyncio.sleep(TRIAL_EXPIRY_INTERVAL_SECONDS)




def register_background_tasks(app: Any) -> None:
    app.state.keepalive_task = None
    app.state.trial_expiry_task = None


async def start_background_tasks(app: Any) -> None:
    if ENABLE_KEEP_ALIVE:
        logger.info("Keepalive enabled. Pinging %s every %s seconds.", KEEP_ALIVE_URL, KEEP_ALIVE_INTERVAL_SECONDS)
        app.state.keepalive_task = asyncio.create_task(keep_alive_loop())
    app.state.trial_expiry_task = asyncio.create_task(trial_expiry_loop())

async def stop_background_tasks(app: Any) -> None:
    for task_name in ("keepalive_task", "trial_expiry_task", "auto_activate_task", "group_collection_task", "payout_processing_task", "nomba_history_sync_task"):
        task = getattr(app.state, task_name, None)
        if task is not None:
            task.cancel()

