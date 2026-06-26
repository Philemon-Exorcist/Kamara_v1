# app/kamara/tutor/tutor_tools/text_write.py
import logging

# Import your global connection manager singleton
from connection.connect_manager import manager 

logger = logging.getLogger("KamaraLogger")

async def write_on_board(
    text_id: str, 
    text: str, 
    x: int, 
    y: int, 
   # text_size: int,
    tool_context=None  # 🧠 Framework context hook injected automatically by Google ADK
) -> dict:
    """
    Writes mathematical formulas, step-by-step variable simplifications, or text 
    explanations directly on the student's interactive whiteboard canvas. 
    Use this tool immediately whenever you want to illustrate text notation visually on the board.
    """
    # 🚨 FIX 1: Securely extract the student's ID from the active session context
    if not tool_context or not getattr(tool_context, "session_id", None):
        return {"status": "error", "message": "Failed to determine the active classroom session context."}
        
    student_uuid = str(tool_context.session_id)
    
    # Structure the precise JSON action schema for the React canvas
    payload = {
        "action": "write_text",
        "data": {
            "id": f"text:{text_id}",
            "text": text,
            "x": x,
            "y": y,
            #"size": text_size
        }
    }
    
    try:
        # 🚨 FIX 2: Pass both the message AND the student_id to the manager
        # We call your manager's optimized JSON broadcasting pipeline
        await manager.send_json_message(message=payload, student_id=student_uuid)
        
        logger.info(f"📝 Text Tool broadcasted notation: '{text}' (ID: {text_id}) to user {student_uuid}")
        return {
            "status": "success", 
            "message": f"Text successfully written onto the student's whiteboard display."
        }
        
    except Exception as e:
        logger.error(f"❌ Whiteboard text tool failed to stream data packet: {str(e)}")
        return {
            "status": "error", 
            "message": f"Network delivery failure writing text notation on the canvas system."
        }
