from __future__ import annotations

"""
Legacy tutor tool registry kept for compatibility.

The current tutor runtime uses `tutor_agent.py` as the canonical registry,
but some older call sites still import this module directly.
"""

from google.genai import types

from .delete_and_clear import clear_board, delete_board_item
from .draw import draw_on_board
from .draw_line_and_curve import draw_line
from .move_and_adjust import adjust_item_size, move_item_on_screen
from .tutor_agent import TUTOR_TOOL_MAP, TUTOR_TOOLS
from .write import write_on_board


WHITEBOARD_TOOL_MAP = {
    "async_draw": draw_on_board,
    "clear_whiteboard": clear_board,
    "write_board": write_on_board,
    "delete_item": delete_board_item,
    "move_item": move_item_on_screen,
    "adjust_item_size": adjust_item_size,
    "draw_line": draw_line,
}


async def tools_handler(client_id, session, tool_call):
    """Compatibility wrapper for older live-session code paths."""
    all_responses = []

    class MockContext:
        session_id = client_id

    for fc in tool_call.function_calls:
        tool_wrapper = TUTOR_TOOL_MAP.get(fc.name)
        if tool_wrapper is None:
            result = {
                "status": "error",
                "message": f"Unknown tutor tool: {fc.name}",
            }
        else:
            try:
                result = await tool_wrapper.run_async(
                    args=fc.args,
                    tool_context=MockContext(),
                )
            except Exception as exc:
                result = {
                    "status": "error",
                    "message": f"Tool {fc.name} failed: {str(exc)}",
                }

        all_responses.append(
            types.FunctionResponse(
                name=fc.name,
                id=fc.id,
                response=result,
            )
        )

    await session.send_tool_response(function_responses=all_responses)


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
