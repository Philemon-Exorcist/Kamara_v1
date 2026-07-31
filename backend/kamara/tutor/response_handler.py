import asyncio
import logging

from fastapi import WebSocket, WebSocketDisconnect

from connection.connect_manager import manager

from .session_resume_store import save_session_resumption_handle
from .toolset.tools import tools_handler

logger = logging.getLogger("KamaraLogger")


async def _async_trigger_greeting(session, student_id: str):
    """Hidden helper task that wakes up Gemini asynchronously without blocking."""
    try:
        await asyncio.sleep(0.1)
        await session.send(
            input="The student has successfully connected to the classroom. Please speak immediately and give them a warm, short greeting to begin the session.",
            end_of_turn=True,
        )
        logger.info("Successfully injected asynchronous initialization greeting packet upstream.")
    except Exception as exc:
        logger.warning("Bypassed non-fatal startup greeting injection: %s", str(exc))


async def receive_response_from_ai(session, student_id: str, websocket: WebSocket, session_id: str | None = None):
    """
    Receives text, voice, and tool calls from Gemini Live and streams them directly to the browser.
    """
    try:
        logger.info("AI Response streaming task fully activated for user: %s", student_id)
        asyncio.create_task(_async_trigger_greeting(session, student_id))

        async for response in session.receive():
            try:
                logger.info("Received raw response packet from Gemini for %s", student_id)

                session_resumption_update = getattr(response, "session_resumption_update", None)
                if session_resumption_update:
                    handle = getattr(session_resumption_update, "handle", None)
                    if isinstance(handle, str) and handle.strip():
                        await save_session_resumption_handle(student_id, session_id, handle)

                go_away = getattr(response, "go_away", None)
                if go_away:
                    logger.info("Gemini issued GoAway for %s | time_left=%s", student_id, getattr(go_away, "time_left", None))

                if response.server_content:
                    logger.info("Server content frame data metadata present.")

                    if response.server_content.model_turn:
                        logger.info("Gemini model turn detected for %s", student_id)

                        for part in response.server_content.model_turn.parts:
                            if part.inline_data and part.inline_data.data:
                                audio_bytes = part.inline_data.data

                                logger.info(
                                    "Received raw voice bytes from Gemini for %s | Length=%s bytes",
                                    student_id,
                                    len(audio_bytes),
                                )
                                logger.info("Gemini audio chunk ready for %s | bytes=%s", student_id, len(audio_bytes))
                                await manager.send_binary_audio(audio_bytes, student_id)

                            if part.text:
                                logger.debug("Gemini text fragment for %s: %s", student_id, part.text)

                    if response.server_content.interrupted:
                        logger.info("Student %s interrupted the AI tutor.", student_id)
                        await manager.send_json_message(
                            {"type": "interrupted", "action": "stop_audio_playback"},
                            student_id,
                        )

                if response.tool_call:
                    logger.info("Gemini triggered whiteboard tool(s) for student: %s", student_id)
                    await tools_handler(
                        student_id=student_id,
                        session=session,
                        tool_call=response.tool_call,
                        websocket=websocket,
                    )

            except (WebSocketDisconnect, RuntimeError) as socket_dead_err:
                logger.warning("Browser wire connection dropped for %s. Breaking outbound streaming loop.", student_id)
                raise WebSocketDisconnect() from socket_dead_err
            except Exception as item_err:
                logger.error(
                    "Failed to process individual Gemini stream frame for student %s: %s",
                    student_id,
                    str(item_err),
                    exc_info=True,
                )
                continue

    except asyncio.CancelledError:
        logger.info("Gemini stream receiver task safely cancelled for student %s.", student_id)
    except Exception as exc:
        logger.error("Fatal crash in AI response listener loop for student %s: %s", student_id, str(exc), exc_info=True)
