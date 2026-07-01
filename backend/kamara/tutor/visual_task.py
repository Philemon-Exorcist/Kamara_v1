import base64
import logging

from google.genai import types

logger = logging.getLogger("KamaraLogger")


async def get_tldraw_text_snapshot(session, student_id: str, snapshot_json: dict):
    """
    Compatibility helper for pushing whiteboard state into Gemini.
    The active websocket bridge now does this in task_handler.py, so this
    function is only kept for older call sites.
    """
    try:
        serialized_snapshot = f"CURRENT_WHITEBOARD_OBJECTS_STORE:\n{snapshot_json}"
        await session.send(
            input=types.LiveClientContent(
                turns=[
                    types.Content(
                        role="user",
                        parts=[types.Part.from_text(text=serialized_snapshot)],
                    )
                ]
            )
        )
        logger.info("📐 Injected structural layout snapshot update for %s", student_id)
    except Exception as e:
        logger.error("Failed to inject whiteboard text metadata for %s: %s", student_id, str(e))


async def get_tldraw_vision_frame(session, student_id: str, image_payload: str | bytes):
    """
    Compatibility helper for pushing a canvas image into Gemini.
    The live socket bridge now handles this directly.
    """
    try:
        raw_bytes = image_payload

        if isinstance(raw_bytes, str):
            if "," in raw_bytes:
                raw_bytes = raw_bytes.split(",")[-1]
            raw_bytes = base64.b64decode(raw_bytes)

        await session.send(
            input=types.LiveClientContent(
                turns=[
                    types.Content(
                        role="user",
                        parts=[
                            types.Part.from_bytes(
                                data=raw_bytes,
                                mime_type="image/png",
                            )
                        ],
                    )
                ]
            )
        )
        logger.info("👁️ Injected live vision frame update for student %s", student_id)
    except Exception as e:
        logger.error("Failed to inject canvas vision frame for %s: %s", student_id, str(e))
