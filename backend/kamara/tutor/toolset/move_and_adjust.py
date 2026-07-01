# ==========================================================================
# 🎨 TOOL 1: MOVE ITEM ON WHITEBOARD
# ==========================================================================
async def move_item_on_screen(
    item_id: str, 
    x: int, 
    y: int
) -> dict:
    """
    Moves an existing geometric shape, vector arrow, or text block to a brand-new 
    (x, y) coordinate position on the interactive whiteboard canvas. 
    Use this tool immediately whenever you need to animate or shift elements for clarification.
    """

    
    # Structure the precise JSON transform payload for the React frontend canvas
    payload = {
        "action": "move_shape",
        "data": {
            "shapeId": f"shape:{item_id}",
            "x": x,
            "y": y
        }
    }

    return payload
    

# ==========================================================================
# 📐 TOOL 2: ADJUST ITEM SIZE ON WHITEBOARD
# ==========================================================================
async def adjust_item_size(
    item_id: str, 
    width: int, 
    height: int
) -> dict:
    """
    Adjusts the bounding box scale (width and height size dimensions) of any existing 
    shape, visual equation element, or text item on the whiteboard layout.
    """
    
    # Structure the precise JSON scaling payload for the React frontend canvas
    payload = {
        "action": "resize_item",
        "data": {
            "shapeId": f"shape:{item_id}",
            "width": width,
            "height": height
        }
    }
    
    return payload