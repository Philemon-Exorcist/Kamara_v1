from __future__ import annotations

import tempfile
from pathlib import Path
from urllib.parse import urlparse
from google import genai

import httpx
from dotenv import load_dotenv
import os
from google.genai import Client,types

from .schemas import WriterContentBundle, WriterSourceType

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client = Client(api_key=api_key,http_options={"api_version": "v1alpha"})





IMAGE_EXTENSIONS = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
    ".gif": "image/gif",
    ".heic": "image/heic",
}

TEXT_EXTENSIONS = {
    ".txt",
    ".md",
    ".markdown",
    ".csv",
    ".json",
    ".rtf",
    ".html",
    ".htm",
}


def _guess_extension(url: str, content_type: str | None) -> str:
    parsed = urlparse(url)
    suffix = Path(parsed.path).suffix.lower()

    if suffix:
        return suffix

    if content_type:
        if "pdf" in content_type:
            return ".pdf"
        if content_type.startswith("image/"):
            return ".png"
        if content_type.startswith("text/"):
            return ".txt"

    return ""


async def _download_remote_source(url: str) -> tuple[bytes, str | None]:
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.content, response.headers.get("content-type")


def _build_text_bundle(prompt: str, helper_text: str | None = None) -> WriterContentBundle:
    source_summary = "Prompt-only request from the student."

    if helper_text:
        source_summary = "Prompt plus extracted text attachment."
        return WriterContentBundle(
            source_type=WriterSourceType.mixed,
            source_summary=source_summary,
            contents=[helper_text],
        )

    return WriterContentBundle(
        source_type=WriterSourceType.prompt,
        source_summary=source_summary,
        contents=[],
    )


async def build_writer_content_bundle(prompt: str, helper_material_url: str | None = None) -> WriterContentBundle:
    if not helper_material_url:
        return _build_text_bundle(prompt)

    raw_bytes, content_type = await _download_remote_source(helper_material_url)
    source_name = helper_material_url.rsplit("/", 1)[-1] or "attached material"
    suffix = _guess_extension(helper_material_url, content_type)

    if suffix in IMAGE_EXTENSIONS:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix or ".png") as temp_file:
            temp_file.write(raw_bytes)
            temp_path = Path(temp_file.name)

        try:
            uploaded_file = await client.files.upload(file=temp_path)
            return WriterContentBundle(
                source_type=WriterSourceType.mixed,
                source_summary=f"Image attachment: {source_name}",
                contents=[uploaded_file],
            )
        finally:
            temp_path.unlink(missing_ok=True)

    if suffix == ".pdf" or content_type == "application/pdf":
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(raw_bytes)
            temp_path = Path(temp_file.name)

        try:
            uploaded_file = client.files.upload(file=temp_path)
            return WriterContentBundle(
                source_type=WriterSourceType.mixed,
                source_summary=f"PDF attachment: {source_name}",
                contents=[uploaded_file],
            )
        finally:
            temp_path.unlink(missing_ok=True)

    if suffix in TEXT_EXTENSIONS or (content_type and content_type.startswith("text/")):
        try:
            helper_text = raw_bytes.decode("utf-8")
        except UnicodeDecodeError:
            helper_text = raw_bytes.decode("utf-8", errors="ignore")

        return _build_text_bundle(prompt, helper_text)

    return _build_text_bundle(prompt)
