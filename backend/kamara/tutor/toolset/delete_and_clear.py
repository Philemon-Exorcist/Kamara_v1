# app/kamara/tutor/tutor_tools/delete.py

# ==========================================================================
# 🎨 TOOL 1: DELETE A PARTICULAR ITEM FROM THE WHITEBOARD
# ==========================================================================
async def delete_board_item(
    item_id: str
) -> dict:
    """
    Deletes a specific geometric shape, text notation, or vector component from the whiteboard canvas.
    Use this tool whenever you need to erase an incorrect formula or remove clutter from the board.
    """

    payload = {
        "action": "delete_shape",
        "data": {
            "shapeId": f"shape:{item_id}"
        }
    }

    return payload

# ==========================================================================
# 🎨 TOOL 2: CLEAR THE ENTIRE WHITEBOARD
# ==========================================================================
async def clear_board() -> dict:
    """
    Completely wipes out the entire whiteboard canvas, deleting all shapes, drawings, 
    and text notations at once. Use this tool whenever transitioning to a brand-new sub-topic.
    """

    payload = {
        "action": "clear_board"
    }

    return payload


