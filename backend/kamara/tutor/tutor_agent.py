from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Awaitable, Callable

from google.genai import types

from .delete_and_clear import clear_board, delete_board_item
from .draw import draw_on_board
from .draw_line_and_curve import draw_line
from .move_and_adjust import adjust_item_size, move_item_on_screen
from .write import write_on_board

TutorToolFn = Callable[..., Awaitable[dict]]


@dataclass(frozen=True)
class TutorTool:
    name: str
    description: str
    parameters: dict[str, Any]
    func: TutorToolFn
    behavior: str = "NON_BLOCKING"

    def _get_declaration(self) -> types.FunctionDeclaration:
        return types.FunctionDeclaration(
            name=self.name,
            description=self.description,
            parameters=self.parameters,
        )

    async def run_async(self, *, args: dict[str, Any] | None = None, tool_context=None) -> dict:
        kwargs = dict(args or {})
        kwargs["tool_context"] = tool_context
        return await self.func(**kwargs)


TUTOR_TOOLS: list[TutorTool] = [
    TutorTool(
        name="async_draw",
        description="Draw a geometric shape on the shared tutor whiteboard.",
        parameters={
            "type": "OBJECT",
            "properties": {
                "shape_id": {"type": "STRING"},
                "shape": {"type": "STRING"},
                "x": {"type": "INTEGER"},
                "y": {"type": "INTEGER"},
                "width": {"type": "INTEGER"},
                "height": {"type": "INTEGER"},
            },
            "required": ["shape_id", "shape", "x", "y"],
        },
        func=draw_on_board,
    ),
    TutorTool(
        name="clear_whiteboard",
        description="Clear the full tutor whiteboard.",
        parameters={
            "type": "OBJECT",
            "properties": {},
        },
        func=clear_board,
    ),
    TutorTool(
        name="write_board",
        description="Write text or equations on the tutor whiteboard.",
        parameters={
            "type": "OBJECT",
            "properties": {
                "text_id": {"type": "STRING"},
                "text": {"type": "STRING"},
                "x": {"type": "INTEGER"},
                "y": {"type": "INTEGER"},
                "text_size": {"type": "INTEGER"},
            },
            "required": ["text_id", "text", "x", "y", "text_size"],
        },
        func=write_on_board,
    ),
    TutorTool(
        name="delete_item",
        description="Delete a board item from the tutor canvas.",
        parameters={
            "type": "OBJECT",
            "properties": {
                "item_id": {"type": "STRING"},
            },
            "required": ["item_id"],
        },
        func=delete_board_item,
    ),
    TutorTool(
        name="move_item",
        description="Move a board item to a new location.",
        parameters={
            "type": "OBJECT",
            "properties": {
                "item_id": {"type": "STRING"},
                "x": {"type": "INTEGER"},
                "y": {"type": "INTEGER"},
            },
            "required": ["item_id", "x", "y"],
        },
        func=move_item_on_screen,
    ),
    TutorTool(
        name="adjust_item_size",
        description="Resize an existing board item.",
        parameters={
            "type": "OBJECT",
            "properties": {
                "item_id": {"type": "STRING"},
                "width": {"type": "INTEGER"},
                "height": {"type": "INTEGER"},
            },
            "required": ["item_id", "width", "height"],
        },
        func=adjust_item_size,
    ),
    TutorTool(
        name="draw_line",
        description="Draw a straight line on the tutor whiteboard.",
        parameters={
            "type": "OBJECT",
            "properties": {
                "line_id": {"type": "STRING"},
                "x": {"type": "INTEGER"},
                "y": {"type": "INTEGER"},
            },
            "required": ["line_id", "x", "y"],
        },
        func=draw_line,
    ),
]

TUTOR_TOOL_MAP = {tool.name: tool for tool in TUTOR_TOOLS}
