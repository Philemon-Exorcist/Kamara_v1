import logging

from fastapi import WebSocket
from google.genai import types

from connection.connect_manager import manager

from .delete_and_clear import clear_board, delete_board_item
from .draw import draw_on_board
from .draw_line_and_curve import draw_line
from .move_and_adjust import adjust_item_size, move_item_on_screen
from .write import write_on_board

logger = logging.getLogger("KamaraLogger")


tools = {
    "function_declarations": [
        {
            "name": "async_draw",
            "description": "Draw a geometric shape such as a rectangle, circle, triangle, or diamond on the tutor whiteboard.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "shape_id": {"type": "STRING"},
                    "shape": {"type": "STRING"},
                    "x": {"type": "INTEGER"},
                    "y": {"type": "INTEGER"},
                    "width": {"type": "INTEGER"},
                    "height": {"type": "INTEGER"},
                },
                "required": ["shape_id", "shape", "x", "y"],
            },
            "behavior": "NON_BLOCKING",
        },
        {
            "name": "clear_whiteboard",
            "description": "Clear every item from the tutor whiteboard at once.",
            "parameters": {
                "type": "OBJECT",
                "properties": {},
            },
            "behavior": "NON_BLOCKING",
        },
        {
            "name": "write_board",
            "description": "Write text, labels, equations, or short hints on the tutor whiteboard.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "text_id": {"type": "STRING"},
                    "text": {"type": "STRING"},
                    "x": {"type": "INTEGER"},
                    "y": {"type": "INTEGER"},
                    "text_size": {"type": "INTEGER"},
                },
                "required": ["text_id", "text", "x", "y"],
            },
            "behavior": "NON_BLOCKING",
        },
        {
            "name": "delete_item",
            "description": "Delete a specific board object by ID.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "item_id": {"type": "STRING"},
                },
                "required": ["item_id"],
            },
            "behavior": "NON_BLOCKING",
        },
        {
            "name": "move_item",
            "description": "Move an existing board object to a new x/y position.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "item_id": {"type": "STRING"},
                    "x": {"type": "INTEGER"},
                    "y": {"type": "INTEGER"},
                },
                "required": ["item_id", "x", "y"],
            },
        },
        {
            "name": "adjust_item_size",
            "description": "Resize an existing board object on the tutor canvas.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "item_id": {"type": "STRING"},
                    "width": {"type": "INTEGER"},
                    "height": {"type": "INTEGER"},
                },
                "required": ["item_id", "width", "height"],
            },
        },
        {
            "name": "draw_line",
            "description": "Draw a straight line on the tutor whiteboard.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "line_id": {"type": "STRING"},
                    "x": {"type": "INTEGER"},
                    "y": {"type": "INTEGER"},
                    "line_type": {"type": "STRING"},
                },
                "required": ["line_id", "x", "y"],
            },
        },
    ]
}


async def tools_handler(student_id: str, session, tool_call, websocket: WebSocket):
    """
    Process tool calls from Gemini, broadcast board commands to every active
    socket for the student, and return receipts to Gemini once per call.
    """
    if not tool_call or not tool_call.function_calls:
        return

    function_responses: list[types.Part] = []

    for fc in tool_call.function_calls:
        payload = None
        gemini_receipt = {"success": "true"}

        try:
            if fc.name == "async_draw":
                payload = await draw_on_board(**fc.args)
            elif fc.name == "write_board":
                payload = await write_on_board(**fc.args)
            elif fc.name == "clear_whiteboard":
                payload = await clear_board()
            elif fc.name == "delete_item":
                payload = await delete_board_item(**fc.args)
            elif fc.name == "move_item":
                payload = await move_item_on_screen(**fc.args)
            elif fc.name == "adjust_item_size":
                payload = await adjust_item_size(**fc.args)
            elif fc.name == "draw_line":
                payload = await draw_line(**fc.args)
            else:
                gemini_receipt = {
                    "success": "false",
                    "error_message": f"Unknown tutor tool: {fc.name}",
                }

            if payload:
                browser_command = {
                    "type": "tool_call",
                    "name": fc.name,
                    "action": payload.get("action"),
                    "data": payload.get("data", {}),
                    "payload": payload,
                }

                await manager.send_json_message(browser_command, student_id)
                logger.info("Broadcast tutor tool '%s' to student %s", fc.name, student_id)

                gemini_receipt = {
                    "success": "true",
                    "action_executed": str(fc.name),
                    "status_message": "Tool Call (Whiteboard updated successfully)",
                }

        except Exception as exc:
            logger.error("Whiteboard execution failed for tool %s: %s", fc.name, str(exc), exc_info=True)
            gemini_receipt = {
                "success": "false",
                "error_message": str(exc)[:120],
            }

        function_responses.append(
            types.Part(
                function_response=types.FunctionResponse(
                    name=fc.name,
                    id=fc.id,
                    response=gemini_receipt,
                )
            )
        )

    try:
        await session.send(
            input=types.LiveClientRealtimeInput(
                function_responses=function_responses
            )
        )
        logger.info("Sent %s tool response receipt(s) back to Gemini.", len(function_responses))
    except Exception as stream_err:
        logger.error("Failed to stream tool confirmation back to Gemini: %s", str(stream_err))
