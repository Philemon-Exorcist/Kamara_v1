import json
import logging
from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect, status

from app.auth import verify_student_token
from app.supabase_client import get_supabase_admin
from connection.connect_manager import manager
from kamara.tutor.tutor import agent
from .database import fetch_complete_note

logger = logging.getLogger("KamaraLogger")

socket_router = APIRouter(tags=["Real-Time Vision & Voice Streaming Engine"])


@socket_router.websocket("/ws/api/v1/live")
async def live_classroom_session_stream(websocket: WebSocket, 
                token: str = Query(...),
                session_id: str | None = Query(None)):

               # session_id:Optional[str]= Query(None)):
    await websocket.accept()
    logger.info("WebSocket accepted for live tutoring | session_id=%s", session_id)

    try:
        mock_auth_header = f"Bearer {token}"
        current_user = await verify_student_token(authorization=mock_auth_header)
        student_id = current_user.id
    except Exception:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        logger.warning("Rejected WebSocket connection attempt: Invalid authentication token token.")
        return

    ctx = await fetch_complete_note(session_id=session_id, student_id=str(student_id))
    
    if not ctx:
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
        logger.error("WebSocket setup aborted: Curated notes data unreachable for session %s", session_id)
        return

    #system_prompt = get_system_prompt(ctx)# instruct is the skill that is passed to the function
     # 3. Compile the Multi-Modal System Prompt blueprint
    system_prompt = f"""
    ROLE & SYSTEM IDENTITY:
    You are an advanced interactive multi-modal AI Classroom Tutor. Maintain high engagement.
    
    ACTIVE COURSE ENVIRONMENT:
    - SUBJECT CLASSIFICATION: {ctx['course_subject'].upper()}
    - MAIN LEARNING OBJECTIVE: {ctx['session_objective']}
    
    MANDATORY LESSON TEXTBOOK NOTES (Your absolute source of truth):
    - UNIT TOPIC: {ctx['note_title']}
    - CONTENT MATERIAL:
    {ctx['note_content']}
    
    WHITEBOARD INTERACTION RULES:
    - Use your whiteboard drawing tools (`async_draw`, `write_board`, `draw_line`) immediately to illustrate items found in these notes.
    - Read coming `canvas_snapshot_vision` image frame updates as the absolute source of truth for what is on  the  board.
    start teaching immmediately, immediately draw a line and write suitable topic on the whiteboard
    teach and write what you want to write one at a time, step by step and continue teaching until
    the students interrupts you, your class must last five minutes
    """

    # 4. Accept Connection and Register to Manager
   # await websocket.accept()
    await manager.connect(str(student_id), websocket)
    logger.info(f"🔑 Live streaming pipeline initialized for student {student_id} on topic {ctx['note_title']}")

    try:
        # 5. Kickoff your concurrent multimodal TaskGroup orchestrator loop
        await agent(
            student_id=str(student_id),
            system_prompt=system_prompt,
            websocket=websocket
        )
    except* WebSocketDisconnect:
        logger.info("Student %s disconnected naturally from room session %s.", student_id, session_id)
    except* Exception as err:
        logger.error("Exception thrown inside connection thread loop for %s: %s", student_id, str(err))
    finally:
        # 6. Unregister connection mapping from RAM to prevent leaks
        manager.disconnect(str(student_id), websocket)
        logger.info("🧹 Cleaned up and disconnected network footprint for user: %s", student_id)


