# app/kamara/tutor/tutor_tools/modify.py
import logging

# Import your global connection manager singleton
from connection.connect_manager import manager 


logger = logging.getLogger("KamaraLogger")



# ==========================================================================
# 🎨 TOOL 1: MOVE ITEM ON WHITEBOARD
# ==========================================================================
async def move_item_on_screen(
    item_id: str, 
    x: int, 
    y: int,
    tool_context=None  # 🧠 Injected automatically by the Google ADK runtime
) -> dict:
    """
    Moves an existing geometric shape, vector arrow, or text block to a brand-new 
    (x, y) coordinate position on the interactive whiteboard canvas. 
    Use this tool immediately whenever you need to animate or shift elements for clarification.
    """
    # 🚨 FIX 2: Securely extract the active student's UUID out of the context hook
    if not tool_context or not getattr(tool_context, "session_id", None):
        return {"status": "error", "message": "Failed to determine the active classroom session context."}
        
    student_uuid = str(tool_context.session_id)
    
    # Structure the precise JSON transform payload for the React frontend canvas
    payload = {
        "action": "move_shape",
        "data": {
            "shapeId": f"shape:{item_id}",
            "x": x,
            "y": y
        }
    }
    
    try:
        # 🚨 FIX 3: Route parameters through your manager's single-send JSON pipe
        await manager.send_json_message(message=payload, student_id=student_uuid)
        
        logger.info(f"🔄 Canvas Move: Shifted item '{item_id}' to coordinates ({x}, {y}) for user {student_uuid}")
        return {
            "status": "success", 
            "message": f"Item {item_id} successfully repositioned on the student's canvas canvas."
        }
        
    except Exception as e:
        logger.error(f"❌ Whiteboard move tool failed to execute: {str(e)}")
        return {
            "status": "error", 
            "message": f"Network delivery failure processing layout animation on the display system."
        }


# ==========================================================================
# 📐 TOOL 2: ADJUST ITEM SIZE ON WHITEBOARD
# ==========================================================================
async def adjust_item_size(
    item_id: str, 
    width: int, 
    height: int,
    tool_context=None  # 🧠 Injected automatically by the Google ADK runtime
) -> dict:
    """
    Adjusts the bounding box scale (width and height size dimensions) of any existing 
    shape, visual equation element, or text item on the whiteboard layout.
    """
    # 🚨 FIX 4: Securely extract the active student's UUID out of the context hook
    if not tool_context or not getattr(tool_context, "session_id", None):
        return {"status": "error", "message": "Failed to determine the active classroom session context."}
        
    student_uuid = str(tool_context.session_id)
    
    # Structure the precise JSON scaling payload for the React frontend canvas
    payload = {
        "action": "resize_item",
        "data": {
            "shapeId": f"shape:{item_id}",
            "width": width,
            "height": height
        }
    }
    
    try:
        # Route parameters through your manager's single-send JSON pipe
        await manager.send_json_message(message=payload, student_id=student_uuid)
        
        logger.info(f"📐 Canvas Scale: Resized item '{item_id}' to {width}x{height} for user {student_uuid}")
        return {
            "status": "success", 
            "message": f"Item {item_id} successfully resized on the student's whiteboard canvas."
        }
        
    except Exception as e:
        logger.error(f"❌ Whiteboard resize tool failed to execute: {str(e)}")
        return {
            "status": "error", 
            "message": f"Hardware routing error adapting item size profiles on the canvas system."
        }
