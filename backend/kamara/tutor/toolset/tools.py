import logging

from connection.connect_manager import manager

from .delete_and_clear import clear_board, delete_board_item
from .draw import draw_on_board
from .draw_line_and_curve import draw_line
from .move_and_adjust import adjust_item_size, move_item_on_screen
from .write import write_on_board
from fastapi import WebSocket
from google.genai import types

logger = logging.getLogger("Kamara Logger")


WHITEBOARD_TOOL_MAP = {
    "async_draw": draw_on_board,
    "clear_whiteboard": clear_board,
    "write_board": write_on_board,
    "delete_item": delete_board_item,
    "move_item": move_item_on_screen,
    "adjust_item_size": adjust_item_size,
    "draw_line": draw_line,
}


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




async def tools_handler(student_id: str, session, tool_call, websocket):
    """
    Processes incoming function calls from Gemini, relays drawing payloads
    directly over the active WebSocket, and returns receipts to the AI model stream.
    """
    if not tool_call or not tool_call.function_calls:
        return

    function_responses = []

    for fc in tool_call.function_calls:
        payload = None
        result = None

        try:
            # 1. EXECUTE THE TOOL (Run with ONLY the arguments Gemini generated)
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
                result = {"status": "error", "message": f"Unknown tutor tool: {fc.name}"}

            # 2. RELAY DYNAMIC LAYOUT ACTIONS DIRECTLY TO BROWSER CANVAS
            if payload:
                # 🚀 DIRECT WIRE: Send tldraw commands directly over the explicit socket
                await websocket.send_json({
                    "type": "tool_call",
                    "name": fc.name,
                    "payload": payload
                })
                logger.info(f"🎨 Whiteboard action '{fc.name}' sent directly to student {student_id}")
                result = {"status": "success", "message": "Whiteboard canvas updated successfully."}

                gemini_receipt = {
                    "success": "true",
                    "action_executed": str(fc.name),
                    "status_message": "Tool Call (Whiteboard updated successfully)"}

        except Exception as e:
            logger.error(f"❌ Whiteboard execution failed for tool {fc.name}: {str(e)}", exc_info=True)
            result = {"status": "error", "message": f"Execution error: {str(e)}"}
        
            gemini_receipt = {
                    "success": "false",
                    "error_message": str(e)[:120] }  # Flat text string
        
    
        # Google's live server rejects nested keys. It wants a direct key-value map.
        function_responses.append(
            types.Part(
                function_response=types.FunctionResponse(
                    name=fc.name,
                    id=fc.id,
                    # Pass the direct execution statement dictionary smoothly
                    #response=result if isinstance(result, dict) else {"status": "success"}
                    response=gemini_receipt if gemini_receipt else {"success": "true"}
                )
            )
        )


        
        # 4. Stream the compiled tool confirmations straight back to Gemini's loop
        if function_responses:
            try:
                await session.send(
                    input=types.LiveClientRealtimeInput(
                    function_responses=function_responses
                )
            )
                logger.info("✅ Successfully sent clean real-time tool response receipts back to Gemini stream.")

                """
                await session.send(
                    input=types.LiveClientContent(
                        turns=[
                            types.Content(
                                role="user",
                                parts=function_responses
                            )
                        ]
                    )
                )
                """
        
                logger.info("✅ Successfully sent tool execution receipts back to Gemini stream.")
            except Exception as stream_err:
                logger.error(f"❌ Failed to stream tool confirmation back to Gemini: {str(stream_err)}")

    

                logger.info("✅ Successfully sent tool execution receipts back to Gemini stream.")
            except Exception as stream_err:
                logger.error(f"❌ Failed to stream tool confirmation back to Gemini: {str(stream_err)}")
        









