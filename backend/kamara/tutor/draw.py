# app/kamara/tutor/tutor_tools/draw.py
import logging

# Import your global connection tracking tracker singleton
from connection.connect_manager import manager 

logger = logging.getLogger("KamaraLogger")


# how do we know which student is being  draw or any other tool being called for
async def draw_on_board(
    shape_id: str, 
    shape: str, 
   # color: str, 
    x: int, 
    y: int, 
    width: int, 
    height: int,  # 🚨 FIX 2: Added missing integer type validation linter hint
    tool_context=None  # 🧠 Framework parameter injections context hook
) -> dict:
    """
    Renders a specific geometric shape or structural vector component on the 
    interactive classroom whiteboard canvas layout. Use this tool immediately 
    whenever you need to visually illustrate math operations or vector coordinate changes.
    """
    # 🚨 FIX 3: Extract the student's secure UUID dynamically out of the active session context
    # This prevents the AI from needing to guess or hardcode the user's ID
    if not tool_context or not getattr(tool_context, "session_id", None):
        return {"status": "error", "message": "Failed to determine active classroom session boundaries."}
        
    student_uuid = str(tool_context.session_id)
    
    
    # Compile the crisp, visual tracking action schema
    payload = {
        "action": "draw_shape",
        "data": {
            "id": f"shape:{shape_id}",
            "shape": shape.lower().strip(), # Normalize shapes (e.g., 'rectangle', 'circle')
           # "color": color,
            "x": x,
            "y": y,
            "width": width,
            "height": height
        }
    }
    
    try:
        # 🚨 FIX 4: Pass both required arguments to the connection manager
        # Use send_json_message to push data directly over the open websocket pipe frame
        await manager.send_json_message(message=payload, student_id=student_uuid)
        
        logger.info(f"🎨 Whiteboard Tool broadcasted shape '{shape}' (ID: {shape_id}) to user {student_uuid}")
        return {
            "status": "success", 
            "message": f"Shape '{shape}' successfully projected onto the student's canvas canvas."
        }
        
    except Exception as e:
        logger.error(f"❌ Whiteboard tool rendering failed to stream: {str(e)}")
        return {
            "status": "error", 
            "message": f"Hardware error drawing shape {shape} on the visual display system."
        }
