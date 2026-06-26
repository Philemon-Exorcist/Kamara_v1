import logging

from connection.connect_manager import manager

logger = logging.getLogger("KamaraLogger")


async def draw_line(
    line_id: str,
    x: int,
    y: int,
    line_type: str = "line",
    tool_context=None,
) -> dict:
    """
    Draws a straight line on the whiteboard.
    """
    if not tool_context or not getattr(tool_context, "session_id", None):
        return {"status": "error", "message": "Failed to determine active classroom session boundaries."}

    student_uuid = str(tool_context.session_id)

    payload = {
        "action": "draw_line",
        "data": {
            "type": line_type,
            "id": f"line:{line_id}",
            "x": x,
            "y": y,
        },
    }

    try:
        await manager.send_json_message(message=payload, student_id=student_uuid)

        logger.info(
            "Whiteboard Tool broadcasted line '%s' (ID: %s) to user %s",
            line_type,
            line_id,
            student_uuid,
        )
        return {
            "status": "success",
            "message": f"line '{line_type}' successfully projected onto the student's canvas.",
        }
    except Exception as e:
        logger.error("Whiteboard tool rendering failed to stream: %s", str(e))
        return {
            "status": "error",
            "message": f"Hardware error drawing shape {line_id} on the visual display system.",
        }
