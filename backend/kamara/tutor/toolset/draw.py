"""Whiteboard shape tool."""

from __future__ import annotations


async def draw_on_board(
    shape_id: str,
    shape: str,
    x: int,
    y: int,
    width: int,
    height: int,
) -> dict:
    return {
        "action": "draw_shape",
        "data": {
            "id": f"shape:{shape_id}",
            "shape": shape.lower().strip(),
            "x": x,
            "y": y,
            "width": width,
            "height": height,
        },
    }
