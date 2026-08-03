from __future__ import annotations

PLAN_CATALOG: dict[str, dict[str, object]] = {
    "starter": {
        "message_limit": 10,
        "max_note_chars": 8000,
        "max_pdf_mb": 5,
        "allow_external_sources": False,
        "allow_large_notes": False,
    },
    "pro": {
        "message_limit": None,
        "max_note_chars": None,
        "max_pdf_mb": 50,
        "allow_external_sources": True,
        "allow_large_notes": True,
    },
}

FEATURE_ALIASES: dict[str, str] = {
    "chat_message": "message_send",
    "message": "message_send",
    "course_generation": "message_send",
    "note": "note_size",
    "notes": "note_size",
    "pdf": "pdf_upload",
    "pdf_upload": "pdf_upload",
    "external_source": "external_source",
    "external_sources": "external_source",
    "upload": "pdf_upload",
}


def normalize_plan_name(plan_name: str | None) -> str:
    normalized = (plan_name or "starter").strip().lower()
    return normalized if normalized in PLAN_CATALOG else "starter"


def normalize_feature_name(feature_name: str) -> str:
    return FEATURE_ALIASES.get(feature_name.strip().lower(), feature_name.strip().lower())

