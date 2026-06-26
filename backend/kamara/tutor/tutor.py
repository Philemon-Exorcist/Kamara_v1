"""Compatibility entry point for the tutor runtime."""

from __future__ import annotations

import asyncio
import logging
import os

from dotenv import load_dotenv

from .tutor_runtime import TutorLiveSession

load_dotenv()
logger = logging.getLogger("KamaraLogger")


async def agent(student_uuid: str = "demo-student", session_id: str = "demo-session", syllabus_rows: list | None = None):
    """Start the shared Gemini Live tutor session."""
    tutor_session = TutorLiveSession(
        student_uuid=student_uuid,
        session_id=session_id,
        syllabus_rows=syllabus_rows or [],
    )
    await tutor_session.prepare_brief()
    await tutor_session.open()
    tutor_session.start_relay()

    try:
        await asyncio.Event().wait()
    finally:
        await tutor_session.close()


if __name__ == "__main__":
    try:
        asyncio.run(
            agent(
                student_uuid=os.getenv("KAMARA_STUDENT_UUID", "demo-student"),
                session_id=os.getenv("KAMARA_SESSION_ID", "demo-session"),
            )
        )
    except KeyboardInterrupt:
        logger.info("Tutor runtime stopped by user.")
