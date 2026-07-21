import logging
import httpx
import os
import asyncio
from typing import Any

logger = logging.getLogger("Monicare.cron")

KEEP_ALIVE_URL = os.environ.get("KEEP_ALIVE_URL", "https://monicare.onrender.com/health")
KEEP_ALIVE_INTERVAL_SECONDS = int(os.environ.get("KEEP_ALIVE_INTERVAL_SECONDS", 60))
ENABLE_KEEP_ALIVE = os.environ.get("ENABLE_KEEP_ALIVE", "true").lower() in ("1", "true", "yes")


async def keep_alive_loop() -> None:
    async with httpx.AsyncClient(timeout=10.0) as client:
        while True:
            try:
                response = await client.get(KEEP_ALIVE_URL)
                logger.info("Keepalive ping %s -> %s", KEEP_ALIVE_URL, response.status_code)
            except Exception as err:
                logger.warning("Keepalive ping failed: %s", err)
            await asyncio.sleep(KEEP_ALIVE_INTERVAL_SECONDS)




def register_background_tasks(app: Any) -> None:
    app.state.keepalive_task = None


async def start_background_tasks(app: Any) -> None:
    if ENABLE_KEEP_ALIVE:
        logger.info("Keepalive enabled. Pinging %s every %s seconds.", KEEP_ALIVE_URL, KEEP_ALIVE_INTERVAL_SECONDS)
        app.state.keepalive_task = asyncio.create_task(keep_alive_loop())

async def stop_background_tasks(app: Any) -> None:
    for task_name in ("keepalive_task", "auto_activate_task", "group_collection_task", "payout_processing_task", "nomba_history_sync_task"):
        task = getattr(app.state, task_name, None)
        if task is not None:
            task.cancel()

