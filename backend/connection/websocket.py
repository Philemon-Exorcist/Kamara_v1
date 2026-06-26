import json
import logging

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from app.auth import verify_student_token
from app.supabase_client import get_supabase_admin
from connection.connect_manager import manager
from kamara.tutor.tutor_runtime import TutorLiveSession, get_or_create_tutor_session

logger = logging.getLogger("KamaraLogger")

router = APIRouter(tags=["Real-Time Vision & Voice Streaming Engine"])
socket_router = router


@router.websocket("/ws/api/v1/live")
async def live_classroom_session_stream(websocket: WebSocket, token: str = Query(...)):
    try:
        mock_auth_header = f"Bearer {token}"
        verified_user = await verify_student_token(authorization=mock_auth_header)
        student_uuid = verified_user.id
    except Exception:
        await websocket.close(code=4001)
        return

    await manager.connect(student_uuid, websocket)
    tutor_session: TutorLiveSession | None = None
    active_session_id: str | None = None
    latest_board_snapshot: str | None = None

    try:
        while True:
            frame = await websocket.receive()

            if "text" in frame:
                payload = json.loads(frame["text"])
                action = payload.get("action")

                if action == "start_session":
                    session_uuid = payload.get("session_id")
                    if not session_uuid:
                        await websocket.send_json(
                            {
                                "type": "system_error",
                                "content": "Tutor engine could not start.",
                                "detail": "Missing session_id in start_session payload.",
                            }
                        )
                        break

                    active_session_id = str(session_uuid)
                    logger.info("Launching classroom engine for session: %s", active_session_id)

                    await websocket.send_json(
                        {
                            "type": "system_status",
                            "content": "Connecting tutor engine...",
                        }
                    )

                    try:
                        db_modules = (
                            get_supabase_admin()
                            .table("modules")
                            .select("sub_topic, teaching_guidelines")
                            .eq("session_id", active_session_id)
                            .eq("is_completed", False)
                            .order("sort_order")
                            .execute()
                        )

                        syllabus_rows = list(db_modules.data or [])

                        if not syllabus_rows:
                            library_rows = (
                                get_supabase_admin()
                                .table("library")
                                .select("title, body_text, content_type")
                                .eq("session_id", active_session_id)
                                .eq("student_id", student_uuid)
                                .eq("content_type", "ai_module")
                                .order("created_at")
                                .execute()
                            )

                            syllabus_rows = [
                                {
                                    "sub_topic": row.get("title") or f"Module {index}",
                                    "teaching_guidelines": row.get("body_text") or "",
                                }
                                for index, row in enumerate(library_rows.data or [], start=1)
                            ]

                        if not syllabus_rows:
                            logger.warning(
                                "No tutor syllabus rows were found in modules or library for session %s; trying session notes fallback.",
                                active_session_id,
                            )

                            session_notes = (
                                get_supabase_admin()
                                .table("sessions")
                                .select("generated_notes, subject, topic")
                                .eq("id", active_session_id)
                                .eq("student_id", student_uuid)
                                .maybe_single()
                                .execute()
                            )

                            session_data = session_notes.data or {}
                            generated_notes = session_data.get("generated_notes") or ""
                            if generated_notes:
                                syllabus_rows = [
                                    {
                                        "sub_topic": session_data.get("topic") or session_data.get("subject") or "Tutor Overview",
                                        "teaching_guidelines": generated_notes,
                                    }
                                ]

                        if not syllabus_rows:
                            logger.warning(
                                "No active classroom syllabus content found for session %s; connecting tutor with empty syllabus.",
                                active_session_id,
                            )

                        tutor_session, created = get_or_create_tutor_session(
                            student_uuid=str(student_uuid),
                            session_id=active_session_id,
                            frontend_ws=websocket,
                            syllabus_rows=syllabus_rows,
                        )

                        tutor_brief = await tutor_session.prepare_brief()
                        await websocket.send_json(
                            {
                                "type": "system_status",
                                "content": "Tutor lesson brief prepared.",
                            }
                        )

                        await tutor_session.open()
                        tutor_session.start_relay()

                        await websocket.send_json(
                            {
                                "type": "system_status",
                                "content": "Tutor engine connected.",
                                "detail": tutor_brief,
                                "reused": not created,
                            }
                        )

                        if latest_board_snapshot:
                            await tutor_session.send_board_snapshot(latest_board_snapshot)
                    except Exception as exc:
                        message = str(exc)
                        if "403" in message or "Forbidden" in message:
                            message = (
                                "Gemini Live rejected the request with 403 Forbidden. "
                                "This usually means the API key/project does not have access to the selected live model."
                            )
                        logger.error("Tutor engine failed to initialize: %s", str(exc), exc_info=True)
                        await websocket.send_json(
                            {
                                "type": "system_error",
                                "content": "Tutor engine failed to initialize.",
                                "detail": message,
                            }
                        )
                        break

                elif action == "board_vision_frame":
                    base64_image_bytes = payload.get("image_bytes")
                    if tutor_session and base64_image_bytes:
                        await tutor_session.send_board_vision_frame(base64_image_bytes)

                elif action == "board_snapshot":
                    latest_board_snapshot = payload.get("snapshot")
                    if tutor_session and latest_board_snapshot:
                        await tutor_session.send_board_snapshot(latest_board_snapshot)

                elif action == "end_session":
                    break

            elif "bytes" in frame and tutor_session:
                try:
                    await tutor_session.send_audio(frame["bytes"])
                except Exception as exc:
                    message = str(exc)
                    if "keepalive ping timeout" in message or "ConnectionClosed" in message:
                        message = (
                            "Gemini Live audio connection timed out while streaming microphone input. "
                            "Please reconnect the tutor call."
                        )

                    logger.error("Tutor audio stream failed: %s", str(exc), exc_info=True)
                    await websocket.send_json(
                        {
                            "type": "system_error",
                            "content": "Tutor audio stream failed.",
                            "detail": message,
                        }
                    )
                    break

    except WebSocketDisconnect:
        logger.info("Connection dropped by student close event.")
    finally:
        manager.disconnect(str(student_uuid), websocket)

        if tutor_session and active_session_id and not manager.active_connections.get(str(student_uuid)):
            await tutor_session.close()

        logger.info(
            "Cleaned up socket connection and background tasks for student UUID: %s",
            student_uuid,
        )
