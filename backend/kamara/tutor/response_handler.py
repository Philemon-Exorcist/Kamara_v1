



# app/tutor/outbound_worker.py
import asyncio
import logging
from fastapi import WebSocket, WebSocketDisconnect
from connection.connect_manager import manager
from .toolset.tools import tools_handler

logger = logging.getLogger("KamaraLogger")





async def _async_trigger_greeting(session, student_id: str):
    """Hidden helper task that wakes up Gemini asynchronously without blocking."""
    try:
        # Wait a tiny fraction of a second to ensure the listen loops are fully active
        await asyncio.sleep(0.1)
        
        # Send a clean text chunk using standard text properties
        await session.send(
            input="The student has successfully connected to the classroom. Please speak immediately and give them a warm, short greeting to begin the session.",
            end_of_turn=True
        )
        logger.info("📤 Successfully injected asynchronous initialization greeting packet upstream.")
    except Exception as e:
        logger.warning("Bypassed non-fatal startup greeting injection: %s", str(e))




async def receive_response_from_ai(session, student_id: str, websocket: WebSocket):
    """
    Receives text, voice, and tool calls from Gemini Live and streams them directly to the browser.
    """
    try:
        # 🔍 VISIBILITY DETECTOR: Confirms this loop is running at all
        logger.info("🤖 AI Response streaming task fully activated for user: %s", student_id)

        asyncio.create_task(_async_trigger_greeting(session, student_id))
        
        async for response in session.receive():
            try:
                # 🔍 VISIBILITY LOG 1: Track every single response wrapper frame hitting your server
                logger.info("📥 Received raw response packet from Gemini for %s", student_id)
                
                # Check for server content wrappers
                if response.server_content:
                    # Log if it's an empty turn or system heartbeat ping
                    logger.info("ℹ️ Server content frame data metadata present.")

                    if response.server_content.model_turn:
                        logger.info("🗣️ Gemini model turn detected for %s", student_id)

                        for part in response.server_content.model_turn.parts:
                            # Text output is intentionally not forwarded to the frontend.
                            if part.text:
                                continue

                            # Handle voice binary data packets
                            if part.inline_data and part.inline_data.data:
                                # 🚀 FIX: Assign the data to the variable FIRST before printing or routing!
                                audio_bytes = part.inline_data.data
                                audio_mime_type = getattr(part.inline_data, "mime_type", None) or "audio/pcm;rate=24000"

                                logger.info(
                                    "🔥 SUCCESS: Received raw voice bytes from Gemini for %s | Length=%s bytes",
                                    student_id,
                                    len(audio_bytes)
                                )

                                logger.info(
                                    "Gemini audio chunk ready for %s | bytes=%s",
                                    student_id,
                                    len(audio_bytes)
                                )

                                # Send raw audio bytes directly to the browser for lower latency playback.
                                await manager.send_binary_audio(audio_bytes, student_id)

                    # Capture conversational interruptions
                    if response.server_content.interrupted:
                        logger.info("🤫 Student %s interrupted the AI tutor.", student_id)
                        await manager.send_json_message(
                            {"type": "interrupted", "action": "stop_audio_playback"},
                            student_id,
                        )

                # Handle tool operations
                if response.tool_call:
                    logger.info("🎨 Gemini triggered whiteboard tool(s) for student: %s", student_id)
                    await tools_handler(
                        student_id=student_id,
                        session=session,
                        tool_call=response.tool_call,
                        websocket=websocket,
                    )

            except (WebSocketDisconnect, RuntimeError) as socket_dead_err:
                # Raising this error tells the TaskGroup to cleanly shut down everything.
                logger.warning(f"📡 Browser wire connection dropped for {student_id}. Breaking outbound streaming loop.")
                raise WebSocketDisconnect() from socket_dead_err

            except Exception as item_err:
                # 🔍 FIXED: Changed log to exc_info=True so you see exactly what lines crash inside the loop
                logger.error("❌ Failed to process individual Gemini stream frame for student %s: %s", student_id, str(item_err), exc_info=True)
                continue

    except asyncio.CancelledError:
        logger.info("Gemini stream receiver task safely cancelled for student %s.", student_id)
    except Exception as e:
        logger.error("❌ Fatal crash in AI response listener loop for student %s: %s", student_id, str(e), exc_info=True)




