# app/connection/gemini_stream.py
import json
import logging
import os
from functools import lru_cache
from pathlib import Path

from google import genai
from google.genai import types

logger = logging.getLogger("KamaraLogger")


def _resolve_gemini_api_key() -> str:
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("Missing GEMINI_API_KEY or GOOGLE_API_KEY for Gemini access.")
    return api_key


def _build_http_options() -> types.HttpOptions | None:
    proxy_url = (
        os.getenv("KAMARA_GEMINI_PROXY_URL")
        or os.getenv("HTTPS_PROXY")
        or os.getenv("HTTP_PROXY")
    )

    if not proxy_url:
        return None

    shared_http_args = {"proxy": proxy_url}
    return types.HttpOptions(
        client_args=shared_http_args,
        async_client_args=shared_http_args,
    )

"""
TUTOR_LIVE_MODEL = os.getenv(
    "KAMARA_TUTOR_MODEL",
    "gemini-2.5-flash-native-audio-preview-12-2025",
)
"""
TUTOR_LIVE_MODEL = "gemini-live-2.5-flash-native-audio"
TUTOR_BACKGROUND_MODEL = os.getenv("KAMARA_TUTOR_TEXT_MODEL", "gemini-2.5-flash")


@lru_cache(maxsize=1)
def get_gemini_client() -> genai.Client:
    """Create and cache a Gemini client only when the tutor actually needs it."""
    return genai.Client(api_key=_resolve_gemini_api_key(), http_options=_build_http_options())


@lru_cache(maxsize=1)
def get_live_gemini_client() -> genai.Client:
    """Create a Live-capable client using the API version the live endpoint expects."""
    live_http_options = types.HttpOptions(
        api_version=os.getenv("KAMARA_TUTOR_API_VERSION", "v1alpha"),
    )
    return genai.Client(api_key=_resolve_gemini_api_key(), http_options=live_http_options)


def get_tutor_system_instruction(syllabus_rows: list, tutor_brief: str = "") -> str:
    """Combines static skills.md with dynamic syllabus rows for Gemini Live initialization"""
    skills_path = Path(__file__).resolve().parents[2] / "skills" / "Maths_Skills.md"
    try:
        with open(skills_path, "r", encoding="utf-8") as file:
            base_tutor_skills = file.read()
    except Exception:
        base_tutor_skills = "You are Kamara AI, a live voice-first whiteboard mathematics tutor."

    syllabus_string = json.dumps(syllabus_rows, indent=2)

    brief_block = ""
    if tutor_brief.strip():
        brief_block = (
            "======================================================================\n"
            "PRECOMPUTED TEACHING BRIEF:\n"
            f"{tutor_brief.strip()}\n"
            "======================================================================\n\n"
        )

    return (
        f"{base_tutor_skills}\n\n"
        "======================================================================\n"
        f"ACTIVE ROADMAP SYLLABUS CONTEXT (Follow this sequentially):\n{syllabus_string}\n"
        "======================================================================\n\n"
        f"{brief_block}"
        "EXECUTION INSTRUCTION:\n"
        "As soon as the live session connects, speak immediately with a short greeting. "
        "Do not wait for the student to speak first. Keep the opening under 15 words. "
        "After the greeting, pause and invite the student to respond. "
        "Monitor incoming 'board_snapshot' text payloads and 'board_vision_frame' image stream chunks "
        "to visually witness what is rendered on the student's monitor screen, and coordinate your whiteboard tools to match."
    )


def get_live_connect_config(model_name: str, syllabus_rows: list, tutor_brief: str = "") -> types.LiveConnectConfig:
    """Compiles the official Google GenAI configuration layout including tools and vision"""
    from .tutor_agent import TUTOR_TOOLS

    master_instruction = get_tutor_system_instruction(syllabus_rows, tutor_brief=tutor_brief)
    function_declarations = [
        declaration
        for tool in TUTOR_TOOLS
        if (declaration := tool._get_declaration()) is not None
    ]

    response_modalities = [types.Modality.AUDIO]
    if "native-audio" not in model_name:
        response_modalities = [types.Modality.AUDIO, types.Modality.TEXT]

    return types.LiveConnectConfig(
        response_modalities=response_modalities,
        system_instruction=types.Content(
            parts=[types.Part.from_text(text=master_instruction)]
        ),
        tools=[types.Tool(function_declarations=function_declarations)],
    )


def get_tutor_live_model_candidates() -> list[str]:
    """Return the preferred live model name."""
    preferred = os.getenv(
        "KAMARA_TUTOR_MODEL",
        "gemini-2.5-flash-native-audio-preview-12-2025",
    )
    return [preferred]


def build_tutor_background_prompt(syllabus_rows: list) -> str:
    """Create a compact live-session brief for the smaller model."""
    syllabus = json.dumps(syllabus_rows, indent=2)
    return (
        "You are Kamara AI preparing a live tutoring session.\n"
        "Summarize the following syllabus into 3 bullets: goal, teaching order, and one board strategy.\n\n"
        f"{syllabus}"
    )


async def generate_tutor_background_brief(syllabus_rows: list) -> str:
    """Use the smaller model to precompute a short tutor plan before opening Live."""
    prompt = build_tutor_background_prompt(syllabus_rows)
    try:
        response = await get_gemini_client().aio.models.generate_content(
            model=TUTOR_BACKGROUND_MODEL,
            contents=prompt,
        )
        brief = (response.text or "").strip()
        if brief:
            return brief
    except Exception as exc:
        logger.warning("Tutor background brief generation failed: %s", str(exc), exc_info=True)

    return "Goal: teach the current lesson. Order: definitions, examples, then practice. Board strategy: keep steps short and visual."
