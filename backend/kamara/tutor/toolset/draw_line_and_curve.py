

async def draw_line(
    line_id: str,
    x: int,
    y: int,
    line_type: str = "line"
) -> dict:
    """
    Draws a straight line on the whiteboard.
    """

    # maybe add height(length and width of line)

    payload = {
        "action": "draw_line",
        "data": {
            "type": line_type,
            "id": f"line:{line_id}",
            "x": x,
            "y": y,
        }
    }


    return payload
