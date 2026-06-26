import logging

logger = logging.getLogger("KamaraLogger")
from connection.connect_manager import manager 


# is there going to be depend in the tool or that is already handled by the conection manager
async def draw_line(line_id: str,
                    x: int,
                    type : str,
                    y: int,
                    tool_context=None
                    ) -> dict :
    
    """
    draws a straight line on the white board
    Args
    line_id : the id of the line to be drawn
    type : line
    x: horizontal position of the line to be drawn in integer
    y: vertical position of the line to be drawn in integer
    return 
    success if the tool ran successfully
    """
    if not tool_context or not getattr(tool_context, "session_id", None):
        return {"status": "error", "message": "Failed to determine active classroom session boundaries."}
        
    student_uuid = str(tool_context.session_id)

    payload = {
        "action": "draw_line",
        "data" : {
             "type" : "line",
            "id" : f"line:{line_id}",
            "x": x,
            "y": y

        }
    }
    try:
            # 🚨 FIX 4: Pass both required arguments to the connection manager
            # Use send_json_message to push data directly over the open websocket pipe frame
        await manager.send_json_message(message=payload, student_id=student_uuid)
            
        logger.info(f"🎨 Whiteboard Tool broadcasted line '{type}' (ID: {line_id}) to user {student_uuid}")
        return {
                "status": "success", 
                "message": f"line '{type}' successfully projected onto the student's canvas canvas."
            }
            
    except Exception as e:
            logger.error(f"❌ Whiteboard tool rendering failed to stream: {str(e)}")
            return {
                "status": "error", 
                "message": f"Hardware error drawing shape {line_id} on the visual display system."
            }
