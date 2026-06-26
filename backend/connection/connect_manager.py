# app/connection/connect_manager.py
from collections import defaultdict
import logging

from fastapi import WebSocket

logger = logging.getLogger("KamaraLogger")


class ConnectionManager:
    def __init__(self):
        # Each student can have more than one websocket open at a time.
        self.active_connections: dict[str, set[WebSocket]] = defaultdict(set)

    async def connect(self, student_id: str, websocket: WebSocket):
        await websocket.accept()
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
        """Broadcast a JSON message to every live websocket for the student."""
        for websocket in list(self.active_connections.get(student_id, set())):
            await websocket.send_json(message)

    async def send_binary_audio(self, audio_bytes: bytes, student_id: str):
        """Broadcast raw model audio bytes to every live websocket for the student."""
        for websocket in list(self.active_connections.get(student_id, set())):
            await websocket.send_bytes(audio_bytes)


manager = ConnectionManager()
