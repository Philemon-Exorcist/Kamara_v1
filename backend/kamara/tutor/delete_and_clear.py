# app/kamara/tutor/tutor_tools/delete.py
import logging

# Import your global connection manager singleton
from connection.connect_manager import manager 

logger = logging.getLogger("KamaraLogger")

# ==========================================================================
# 🎨 TOOL 1: DELETE A PARTICULAR ITEM FROM THE WHITEBOARD
# ==========================================================================
async def delete_board_item(
    item_id: str,
    tool_context=None  # 🧠 Injected automatically by the Google ADK runtime
) -> dict:
    """
    Deletes a specific geometric shape, text notation, or vector component from the whiteboard canvas.
    Use this tool whenever you need to erase an incorrect formula or remove clutter from the board.
    """
    # Securely extract the active student's UUID out of the context hook
    if not tool_context or not getattr(tool_context, "session_id", None):
        return {"status": "error", "message": "Failed to determine the active classroom session context."}
        
    student_uuid = str(tool_context.session_id)

    payload = {
        "action": "delete_shape",
        "data": {
            "shapeId": f"shape:{item_id}"
        }
    }

    try:
        # Route parameters through your manager's single-send JSON pipe
        await manager.send_json_message(message=payload, student_id=student_uuid)
        
        logger.info(f"🗑️ Canvas Eraser: Deleted item '{item_id}' for user {student_uuid}")
        return {
            "status": "success", 
            "message": f"Item {item_id} successfully deleted from the student's canvas."
        }
    except Exception as e:
        logger.error(f"❌ Whiteboard delete tool failed to execute: {str(e)}")
        return {
            "status": "error", 
            "message": f"Network delivery failure processing erasure on the display system."
        }


# ==========================================================================
# 🎨 TOOL 2: CLEAR THE ENTIRE WHITEBOARD
# ==========================================================================
async def clear_board(
    tool_context=None  # 🧠 Injected automatically by the Google ADK runtime
) -> dict:
    """
    Completely wipes out the entire whiteboard canvas, deleting all shapes, drawings, 
    and text notations at once. Use this tool whenever transitioning to a brand-new sub-topic.
    """
    # Securely extract the active student's UUID out of the context hook
    if not tool_context or not getattr(tool_context, "session_id", None):
        return {"status": "error", "message": "Failed to determine the active classroom session context."}
        
    student_uuid = str(tool_context.session_id)

    payload = {
        "action": "clear_board"
    }

    try:
        # Route parameters through your manager's single-send JSON pipe
        await manager.send_json_message(message=payload, student_id=student_uuid)
        
        logger.info(f"🧼 Canvas Cleanse: Wiped the entire board clear for user {student_uuid}")
        return {
            "status": "success", 
            "message": "Whiteboard successfully cleared of all visual elements."
        }
    except Exception as e:
        logger.error(f"❌ Whiteboard clear tool failed to execute: {str(e)}")
        return {
            "status": "error", 
            "message": f"Network delivery failure wiping the canvas display layout."
        }



