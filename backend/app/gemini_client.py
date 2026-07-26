from __future__ import annotations

from functools import lru_cache
import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai

_BACKEND_ENV_PATH = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(_BACKEND_ENV_PATH)


def _clean_env_value(value: str | None) -> str | None:
    if value is None:
        return None

    cleaned = value.strip().strip('"').strip("'").strip()
    return cleaned or None


def get_gemini_api_key() -> str:
    api_key = _clean_env_value(
        os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    )

    if not api_key:
        raise RuntimeError("Missing Gemini API key. Set GEMINI_API_KEY in backend/.env")

    if api_key.lower() in {"your_api_key_here", "replace_me", "replace-me"}:
        raise RuntimeError("Gemini API key is still set to a placeholder value.")

    return api_key


@lru_cache(maxsize=1)
def get_gemini_client() -> genai.Client:
    return genai.Client(
        api_key=get_gemini_api_key(),
        http_options={"api_version": "v1alpha"},
    )
