from __future__ import annotations

import asyncio
import base64
import logging
from dataclasses import dataclass, field
from typing import Any, Optional

from google.genai import types

from connection.connect_manager import manager
from .tutor_agent import TUTOR_TOOL_MAP
from .visual_task import (
    generate_tutor_background_brief,
    get_gemini_client,
    get_live_connect_config,
    get_tutor_live_model_candidates,
)

logger = logging.getLogger("KamaraLogger")

_ACTIVE_TUTOR_SESSIONS: dict[str, "TutorLiveSession"] = {}


def _session_key(student_uuid: str, session_id: str) -> str:
    return f"{student_uuid}:{session_id}"


def get_or_create_tutor_session(
    *,
    student_uuid: str,
    session_id: str,
    frontend_ws=None,
    syllabus_rows: Optional[list] = None,
) -> tuple["TutorLiveSession", bool]:
    key = _session_key(student_uuid, session_id)
    existing = _ACTIVE_TUTOR_SESSIONS.get(key)
    if existing is not None:
        return existing, False

    session = TutorLiveSession(
        student_uuid=student_uuid,
        session_id=session_id,
        frontend_ws=frontend_ws,
        syllabus_rows=syllabus_rows or [],
    )
    _ACTIVE_TUTOR_SESSIONS[key] = session
    return session, True


def release_tutor_session(student_uuid: str, session_id: str) -> None:
    _ACTIVE_TUTOR_SESSIONS.pop(_session_key(student_uuid, session_id), None)


@dataclass
class TutorLiveSession:
    student_uuid: str
    session_id: str
    frontend_ws: Any | None = None
    syllabus_rows: list = field(default_factory=list)
    tutor_brief: str = ""
    _client: Any | None = field(default=None, init=False, repr=False)
    _client_cm: Any | None = field(default=None, init=False, repr=False)
    _live_session: Any | None = field(default=None, init=False, repr=False)
    _relay_task: asyncio.Task | None = field(default=None, init=False, repr=False)
    _closing: bool = field(default=False, init=False, repr=False)
    _active_model: str | None = field(default=None, init=False, repr=False)

    async def prepare_brief(self) -> str:
        if self.tutor_brief.strip():
            return self.tutor_brief

        self.tutor_brief = await generate_tutor_background_brief(self.syllabus_rows)
        return self.tutor_brief

    async def open(self) -> None:
        if self._live_session is not None:
            return

        if self._client is None:
            self._client = get_gemini_client()

        if not self.tutor_brief.strip():
            await self.prepare_brief()

        config = get_live_connect_config(self.syllabus_rows, tutor_brief=self.tutor_brief)
        last_error: Exception | None = None

        for model_name in get_tutor_live_model_candidates():
            try:
                self._client_cm = self._client.aio.live.connect(model=model_name, config=config)
                self._live_session = await self._client_cm.__aenter__()
                self._active_model = model_name
                logger.info(
                    "Tutor Live session opened for student=%s session=%s model=%s",
                    self.student_uuid,
                    self.session_id,
                    model_name,
                )
                return
            except Exception as exc:
                last_error = exc
                self._live_session = None
                self._client_cm = None
                logger.warning(
                    "Tutor Live model candidate failed for student=%s session=%s model=%s: %s",
                    self.student_uuid,
                    self.session_id,
                    model_name,
                    str(exc),
                )

        raise RuntimeError(f"Could not open Gemini Live session: {last_error}")

    def start_relay(self) -> None:
        if self._relay_task and not self._relay_task.done():
            return

        self._relay_task = asyncio.create_task(self._relay_loop())

    async def send_audio(self, audio_bytes: bytes) -> None:
        if not self._live_session:
            return

        await self._live_session.send_realtime_input(
            audio=types.Blob(data=audio_bytes, mime_type="audio/pcm;rate=16000")
        )

    async def send_board_snapshot(self, snapshot: str) -> None:
        if not self._live_session or not snapshot:
            return

        await self._live_session.send_client_content(
            turns=types.Content(
                role="user",
                parts=[
                    types.Part.from_text(
                        text=f"BOARD_SNAPSHOT_CONTEXT:\n{snapshot}"
                    )
                ],
            ),
            turn_complete=True,
        )

    async def send_board_vision_frame(self, image_bytes: str | bytes) -> None:
        if not self._live_session or not image_bytes:
            return

        raw_bytes = image_bytes
        if isinstance(raw_bytes, str):
            try:
                raw_bytes = base64.b64decode(raw_bytes)
            except Exception:
                raw_bytes = raw_bytes.encode("utf-8")

        await self._live_session.send_realtime_input(
            media=types.Blob(data=raw_bytes, mime_type="image/png")
        )

    async def close(self) -> None:
        self._closing = True

        if self._relay_task and not self._relay_task.done():
            self._relay_task.cancel()
            try:
                await self._relay_task
            except asyncio.CancelledError:
                pass
            except Exception:
                logger.debug("Relay task closed with an error.", exc_info=True)

        if self._client_cm is not None:
            try:
                await self._client_cm.__aexit__(None, None, None)
            except Exception:
                logger.debug("Tutor Live client context exit failed.", exc_info=True)

        self._relay_task = None
        self._live_session = None
        self._client_cm = None

    async def _relay_loop(self) -> None:
        if not self._live_session:
            return

        try:
            async for response in self._live_session.receive():
                server_content = getattr(response, "server_content", None)
                if server_content and getattr(server_content, "model_turn", None):
                    for part in server_content.model_turn.parts:
                        if getattr(part, "text", None):
                            await manager.send_json_message(
                                {
                                    "type": "assistant_text",
                                    "content": part.text,
                                },
                                self.student_uuid,
                            )

                        inline_data = getattr(part, "inline_data", None)
                        if inline_data and getattr(inline_data, "data", None):
                            await manager.send_binary_audio(
                                inline_data.data,
                                self.student_uuid,
                            )

                tool_call = getattr(response, "tool_call", None)
                if not tool_call:
                    continue

                for call in tool_call.function_calls:
                    tool_name = call.name
                    tool_args = call.args or {}
                    call_id = call.id

                    await manager.send_json_message(
                        {
                            "type": "tool_call",
                            "name": tool_name,
                            "call_id": call_id,
                            "args": tool_args,
                        },
                        self.student_uuid,
                    )

                    tool_wrapper = TUTOR_TOOL_MAP.get(tool_name)
                    if tool_wrapper is None:
                        result = {
                            "status": "error",
                            "message": f"Unknown tutor tool: {tool_name}",
                        }
                    else:
                        try:
                            result = await tool_wrapper.run_async(
                                args=tool_args,
                                tool_context=_TutorToolContext(self.session_id)
                            )
                        except Exception as exc:
                            logger.error(
                                "Tutor tool '%s' failed for student=%s: %s",
                                tool_name,
                                self.student_uuid,
                                str(exc),
                                exc_info=True,
                            )
                            result = {
                                "status": "error",
                                "message": f"Tool {tool_name} failed.",
                            }

                    await manager.send_json_message(
                        {
                            "type": "tool_result",
                            "name": tool_name,
                            "call_id": call_id,
                            "result": result,
                        },
                        self.student_uuid,
                    )

                    try:
                        await self._live_session.send_tool_response(
                            function_responses=types.FunctionResponse(
                                name=tool_name,
                                id=call_id,
                                response=result,
                            )
                        )
                    except Exception as exc:
                        logger.error(
                            "Failed to send tool response back to Gemini for %s: %s",
                            tool_name,
                            str(exc),
                            exc_info=True,
                        )
        except asyncio.CancelledError:
            pass
        except Exception as exc:
            if not self._closing:
                logger.error(
                    "Tutor relay loop failed for student=%s session=%s: %s",
                    self.student_uuid,
                    self.session_id,
                    str(exc),
                    exc_info=True,
                )
        finally:
            release_tutor_session(self.student_uuid, self.session_id)


class _TutorToolContext:
    def __init__(self, session_id: str):
        self.session_id = session_id
