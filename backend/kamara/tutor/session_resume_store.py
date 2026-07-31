from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from app.supabase_client import get_supabase_admin

logger = logging.getLogger("KamaraLogger")

_RAM_RESUME_HANDLES: dict[str, str] = {}
_HANDLE_FIELD_CANDIDATES = (
    "live_session_handle",
    "session_resumption_handle",
    "resume_handle",
    "gemini_live_handle",
)


def _cache_key(student_id: str, session_id: str | None) -> str:
    return f"{student_id}:{session_id or 'anonymous'}"


def _extract_handle(record: dict[str, Any] | None) -> str | None:
    if not record:
        return None

    for field_name in _HANDLE_FIELD_CANDIDATES:
        value = record.get(field_name)
        if isinstance(value, str) and value.strip():
            return value.strip()

    metadata = record.get("metadata")
    if isinstance(metadata, dict):
        for field_name in _HANDLE_FIELD_CANDIDATES:
            value = metadata.get(field_name)
            if isinstance(value, str) and value.strip():
                return value.strip()

    return None


async def load_session_resumption_handle(student_id: str, session_id: str | None) -> str | None:
    """
    Load the last Gemini Live resumption handle for this student/session pair.
    Falls back to the in-memory cache if the database row is unavailable.
    """
    cache_key = _cache_key(student_id, session_id)
    if cache_key in _RAM_RESUME_HANDLES:
        return _RAM_RESUME_HANDLES[cache_key]

    if not session_id:
        return None

    try:
        supabase = get_supabase_admin()
        response = (
            supabase.table("sessions")
            .select("*")
            .eq("id", session_id)
            .eq("student_id", student_id)
            .limit(1)
            .execute()
        )

        handle = _extract_handle((response.data or [None])[0])
        if handle:
            _RAM_RESUME_HANDLES[cache_key] = handle
            return handle
    except Exception as exc:
        logger.warning("Could not load stored Gemini resumption handle for %s: %s", cache_key, str(exc))

    return None


async def save_session_resumption_handle(student_id: str, session_id: str | None, handle: str) -> None:
    """
    Persist the latest Gemini Live resumption handle.
    Uses a best-effort Supabase update and always keeps an in-memory fallback.
    """
    if not handle:
        return

    cache_key = _cache_key(student_id, session_id)
    cleaned_handle = handle.strip()
    _RAM_RESUME_HANDLES[cache_key] = cleaned_handle

    if not session_id:
        return

    timestamp = datetime.now(timezone.utc).isoformat()
    update_payloads: list[dict[str, Any]] = [
        {"live_session_handle": cleaned_handle, "live_session_handle_updated_at": timestamp},
        {"session_resumption_handle": cleaned_handle, "session_resumption_handle_updated_at": timestamp},
        {"resume_handle": cleaned_handle, "resume_handle_updated_at": timestamp},
        {"gemini_live_handle": cleaned_handle, "gemini_live_handle_updated_at": timestamp},
        {
            "metadata": {
                "live_session_handle": cleaned_handle,
                "live_session_handle_updated_at": timestamp,
            }
        },
    ]

    try:
        supabase = get_supabase_admin()
        last_error: Exception | None = None

        for payload in update_payloads:
            try:
                response = (
                    supabase.table("sessions")
                    .update(payload)
                    .eq("id", session_id)
                    .eq("student_id", student_id)
                    .execute()
                )

                if response is not None:
                    logger.info(
                        "Saved Gemini resumption handle for student=%s session=%s",
                        student_id,
                        session_id,
                    )
                    return
            except Exception as exc:
                last_error = exc
                continue

        if last_error:
            raise last_error
    except Exception as exc:
        logger.warning(
            "Could not persist Gemini resumption handle for student=%s session=%s: %s",
            student_id,
            session_id,
            str(exc),
        )

