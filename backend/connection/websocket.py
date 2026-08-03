import logging

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect, status

from app.auth import verify_student_token
from connection.connect_manager import manager
from kamara.tutor.tutor import agent
from .database import fetch_complete_note
from prompts.tutor_prompt import tutor_system_instruction


logger = logging.getLogger("KamaraLogger")

socket_router = APIRouter(tags=["Real-Time Vision & Voice Streaming Engine"])


@socket_router.websocket("/ws/api/v1/live")
async def live_classroom_session_stream(
    websocket: WebSocket,
    token: str = Query(...),
    session_id: str | None = Query(None),
):
    await websocket.accept()
    logger.info("WebSocket accepted for live tutoring | session_id=%s", session_id)

    try:
        current_user = await verify_student_token(authorization=f"Bearer {token}")
        student_id = current_user.id
    except Exception:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        logger.warning("Rejected WebSocket connection attempt: invalid authentication token.")
        return

    ctx = await fetch_complete_note(session_id=session_id, student_id=str(student_id))
    if not ctx:
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
        logger.error("WebSocket setup aborted: curated notes data unreachable for session %s", session_id)
        return
    system_prompt = await tutor_system_instruction(ctx)


    await manager.connect(str(student_id), websocket)
    logger.info("Live streaming pipeline initialized for student %s on topic %s", student_id, ctx["note_title"])

    try:
        await agent(
            student_id=str(student_id),
            system_prompt=system_prompt,
            websocket=websocket,
            session_id=session_id,
        )
    except* WebSocketDisconnect:
        logger.info("Student %s disconnected naturally from room session %s.", student_id, session_id)
    except* Exception as err:
        logger.error("Exception thrown inside connection thread loop for %s: %s", student_id, str(err))
    finally:
        manager.disconnect(str(student_id), websocket)
        logger.info("Cleaned up and disconnected network footprint for user: %s", student_id)





"""
One note: the “Upgrade to Pro” button on the upgrade page currently points back to signup as a placeholder, since there isn’t a billing checkout wired in yet. If you want, I can hook that button to Stripe, Paystack, or your existing payment flow next.

"""