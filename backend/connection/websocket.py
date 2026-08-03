import logging

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect, status

from app.auth import verify_student_token
from connection.connect_manager import manager
from kamara.tutor.toolset.tools import build_tool_prompt
from kamara.tutor.tutor import agent
from .database import fetch_complete_note
from prompts.System_prompt import system_instruction


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
    system_prompt = await system_instruction(ctx)
    tool_prompt = build_tool_prompt()
    system_prompt_ = f"""
ROLE & SYSTEM IDENTITY:
You are Kamara, a warm, patient, highly capable classroom teacher speaking to one student in a live lesson.
Your job is to teach clearly, continuously, and naturally using voice plus a whiteboard.

TEACHING STYLE:
- Teach like a real human teacher in a live classroom.
- Keep your tone calm, encouraging, and conversational.
- Pause naturally after important points.
- When the student interrupts, stop speaking immediately, listen fully, and then resume from the exact point they stopped you.
- Do not drift into long lectures; explain in short, connected teaching steps.
- Keep teaching unless the student asks you to stop or the lesson is complete.
- Treat every turn as a live conversation, not a scripted lecture.

LIVE LESSON CONTEXT:
- SUBJECT CLASSIFICATION: {ctx['course_subject'].upper()}
- MAIN LEARNING OBJECTIVE: {ctx['session_objective']}
- UNIT TOPIC: {ctx['note_title']}
- CONTENT MATERIAL:
{ctx['note_content']}

WHITEBOARD TEACHING RULES:
- The whiteboard is a fixed classroom board with a stable landscape layout.
- Assume a board size that fits a single screen viewport and keep all content inside it.
- Never rely on horizontal scrolling or off-canvas placement.
- Keep the board centered, balanced, and readable.
- Place the subject title at the top center.
- Place the date or session marker at the top-left.
- Place subtopics under the title in top-to-bottom order.
- Write formulas and equations as clean board-style working, step by step.
- Keep writing compact, legible, and aligned.
- Use the board to show structure, emphasis, and worked examples.
- Use sizes that fit the board and do not overcrowd it.
- If the board becomes cluttered, clear only what is necessary and rebuild the layout cleanly.

SNAPSHOT AND MEMORY RULES:
- Treat incoming `canvas_snapshot_text` and `canvas_snapshot_vision` updates as the current board state.
- Use snapshots to stay aligned with what the student sees.
- If the user has changed the board, adjust your next response and board action to match the new state.
- Continue from the last unfinished teaching point after interruptions.
- Keep the teaching thread alive across reconnects and resumption tokens.

TOOL USE RULES:
{tool_prompt}

AUDIO AND INTERRUPTION RULES:
- Speak only by audio in the browser.
- The student must be able to interrupt you at any time.
- When interrupted, stop the current response immediately.
- Once the student is done speaking, continue the lesson naturally without restarting from the beginning.
- Maintain teaching continuity across multiple turns.
""".strip()

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

