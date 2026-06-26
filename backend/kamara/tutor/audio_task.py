import asyncio
import logging

from fastapi import APIRouter, WebSocket
from google.genai import types

from .tutor_agent import TUTOR_TOOL_MAP


logger = logging.getLogger("KamaraLogger")

router = APIRouter(tags=["Real-Time Vision & Voice Streaming Engine"])


async def _safe_send_json(frontend_ws: WebSocket, payload: dict) -> None:
    try:
        await frontend_ws.send_json(payload)
    except Exception as exc:
        logger.error("Failed to send tutor JSON event to frontend: %s", str(exc), exc_info=True)


async def _safe_send_bytes(frontend_ws: WebSocket, payload: bytes) -> None:
    try:
        await frontend_ws.send_bytes(payload)
    except Exception as exc:
        logger.error("Failed to send tutor audio bytes to frontend: %s", str(exc), exc_info=True)


async def forward_frontend_mic_to_gemini(frontend_ws: WebSocket, gemini_session):
    """Continuously forward mic audio bytes straight to Gemini."""
    try:
        while True:
            data = await frontend_ws.receive_bytes()
            await gemini_session.send(input={"media_chunks": [{"data": data, "mime_type": "audio/pcm"}]})
    except asyncio.CancelledError:
        pass
    except Exception as e:
        logger.error(f"Error streaming mic bytes to Gemini: {str(e)}")


async def receive_gemini_stream_and_relay(frontend_ws: WebSocket, student_uuid: str, gemini_session):
    """Parse Gemini output voice bytes, text, and tool-call frames."""
    try:
        async for response in gemini_session.receive():
            server_content = response.server_content
            if server_content and server_content.model_turn:
                for part in server_content.model_turn.parts:
                    if part.text:
                        await _safe_send_json(
                            frontend_ws,
                            {
                                "type": "assistant_text",
                                "content": part.text,
                            }
                        )

                    if part.inline_data:
                        await _safe_send_bytes(frontend_ws, part.inline_data.data)

            if response.tool_call:
                for call in response.tool_call.function_calls:
                    tool_name = call.name
                    tool_args = call.args
                    call_id = call.id

                    await _safe_send_json(
                        frontend_ws,
                        {
                            "type": "tool_call",
                            "name": tool_name,
                            "call_id": call_id,
                            "args": tool_args,
                        }
                    )

                    logger.info(f"AI Tutor executed canvas tool command: {tool_name}")

                    class MockContext:
                        session_id = student_uuid

                    tool_function = TUTOR_TOOL_MAP.get(tool_name)

                    if tool_function:
                        try:
                            result = await tool_function.run_async(
                                args=tool_args,
                                tool_context=MockContext(),
                            )
                        except Exception as exc:
                            logger.error("Tutor tool '%s' failed: %s", tool_name, str(exc), exc_info=True)
                            result = {"status": "error", "message": f"Tool {tool_name} failed."}

                        await _safe_send_json(
                            frontend_ws,
                            {
                                "type": "tool_result",
                                "name": tool_name,
                                "call_id": call_id,
                                "result": result,
                            }
                        )

                        try:
                            await gemini_session.send(
                                input=types.LiveClientToolResponse(
                                    function_responses=[
                                        types.FunctionResponse(name=tool_name, id=call_id, response=result)
                                    ]
                                )
                            )
                        except Exception as exc:
                            logger.error("Failed to send tool response back to Gemini: %s", str(exc), exc_info=True)
                    else:
                        await _safe_send_json(
                            frontend_ws,
                            {
                                "type": "tool_result",
                                "name": tool_name,
                                "call_id": call_id,
                                "result": {
                                    "status": "error",
                                    "message": f"Unknown tutor tool: {tool_name}",
                                },
                            }
                        )
    except asyncio.CancelledError:
        pass
    except Exception as e:
        logger.error(f"Error relaying Gemini stream: {str(e)}")
