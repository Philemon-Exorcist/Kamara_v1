import logging
import re

from fastapi import WebSocket
from google.genai import types

from connection.connect_manager import manager

logger = logging.getLogger("KamaraLogger")

canvas_tools = {
    "function_declarations": [
        {
            "name": "tldraw_canvas_exec",
            "description": (
                "Execute raw JavaScript against the mounted tldraw editor instance. "
                "Use this for create, update, delete, move, resize, style and grouping actions."
            ),
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "javascript_code": {
                        "type": "STRING",
                        "description": "Raw JavaScript that uses the provided editor variable.",
                    }
                },
                "required": ["javascript_code"],
            },
            "behavior": "NON_BLOCKING",
        }
    ]
}


def _sanitize_js_code(code: str) -> str:
    cleaned = code.strip()
    cleaned = re.sub(r"^```(?:javascript|js)?\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    return cleaned.strip()


async def canvas_exec_handler(student_id: str, session, tool_call, websocket: WebSocket):
    """
    Broadcasts raw tldraw editor JavaScript to the frontend and acknowledges the tool
    call back to Gemini.
    """
    if not tool_call or not tool_call.function_calls:
        return

    function_responses: list[types.FunctionResponse] = []

    for fc in tool_call.function_calls:
        if fc.name != "tldraw_canvas_exec":
            continue

        args = getattr(fc, "args", None) or {}
        javascript_code = _sanitize_js_code(str(args.get("javascript_code", "")))

        if not javascript_code:
            receipt = {
                "success": "false",
                "error_message": "Missing javascript_code argument.",
            }
        else:
            try:
                await manager.send_json_message(
                    {
                        "type": "exec_js",
                        "tool": "tldraw_canvas_exec",
                        "code": javascript_code,
                        "tool_call_id": getattr(fc, "id", None),
                    },
                    student_id,
                )
                logger.info("Broadcast canvas exec tool to student %s", student_id)
                receipt = {
                    "success": "true",
                    "action_executed": "tldraw_canvas_exec",
                    "status_message": "Canvas JavaScript delivered to the frontend.",
                }
            except Exception as exc:
                logger.error("Canvas exec broadcast failed for %s: %s", student_id, str(exc), exc_info=True)
                receipt = {
                    "success": "false",
                    "error_message": str(exc)[:120],
                }

        function_responses.append(
            types.FunctionResponse(
                name=fc.name,
                id=fc.id,
                response=receipt,
            )
        )

    if function_responses:
        await session.send_tool_response(function_responses=function_responses)
        logger.info("Sent %s canvas response receipt(s) back to Gemini.", len(function_responses))
