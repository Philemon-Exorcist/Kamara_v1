# app/connection/connect_manager.py
from collections import defaultdict
import logging
from fastapi import WebSocket


logger = logging.getLogger("KamaraLogger")

class ConnectionManager:
    def __init__(self):
        # Maps a student_id string to a SET of active WebSockets (supports multi-tab/device)
        self.active_connections: dict[str, set[WebSocket]] = defaultdict(set)

    async def connect(self, student_id: str, websocket: WebSocket):
       # await websocket.accept()
        self.active_connections[student_id].add(websocket)
        logger.info("Student websocket attached for UUID: %s", student_id)

    def disconnect(self, student_id: str, websocket: WebSocket | None = None):
        sockets = self.active_connections.get(student_id)
        if not sockets:
            return

        if websocket is not None:
            sockets.discard(websocket)
        else:
            sockets.clear()

        if not sockets:
            self.active_connections.pop(student_id, None)
            logger.info("Socket session closed for Student ID: %s", student_id)

    async def send_json_message(self, message: dict, student_id: str):
        """Broadcasts a whiteboard tool payload or state update to ALL of a student's active connections."""
        active_targets = list(self.active_connections.get(student_id, set()))
        logger.info(
            "Broadcasting JSON payload to student %s | targets=%s | type=%s",
            student_id,
            len(active_targets),
            message.get("type") or message.get("action"),
        )
        for websocket in active_targets:
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error("Failed broadcasting JSON payload to student socket: %s", str(e))

    async def send_binary_audio(self, audio_bytes: bytes, student_id: str):
        """Broadcasts raw voice audio bytes to ALL of a student's active streaming connection endpoints."""
        active_targets = list(self.active_connections.get(student_id, set()))
        logger.info(
            "Broadcasting binary audio to student %s | targets=%s | bytes=%s",
            student_id,
            len(active_targets),
            len(audio_bytes),
        )
        for websocket in active_targets:
            try:
                await websocket.send_bytes(audio_bytes)
            except Exception as e:
                logger.error("Failed broadcasting audio streaming bytes to student socket: %s", str(e))

    async def send_private_tab_message(self, message: dict, websocket: WebSocket):
        """Sends a JSON message strictly to ONE specific socket instance (e.g., error alert back to sender)."""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error("Failed delivering direct target socket frame payload: %s", str(e))

manager = ConnectionManager()
