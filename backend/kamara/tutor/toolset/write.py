"""Whiteboard text tool."""

from __future__ import annotations


async def write_on_board(
    text_id: str,
    text: str,
    x: int,
    y: int,
    text_size: int | None = None,
) -> dict:
    payload = {
        "action": "write_text",
        "data": {
            "id": f"text:{text_id}",
            "text": text,
            "x": x,
            "y": y,
        },
    }

    if text_size is not None:
        payload["data"]["size"] = text_size

    return payload
