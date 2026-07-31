import logging
import os
from google.genai import types,Client
from dotenv import load_dotenv


from .prompts import build_writer_system_prompt, build_writer_user_prompt
from .schemas import WriterContentBundle, WriterModuleSchema, WriterRequestSchema, WriterResponseSchema
from .source_loader import build_writer_content_bundle

logger = logging.getLogger("KamaraLogger")
#WRITER_MODEL = "gemini-3.5-flash"
WRITER_MODEL="gemini-3.6-flash"
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client = Client(api_key=api_key,http_options={"api_version": "v1alpha"})

def _extract_course_context(message: str) -> tuple[str, str]:
    import re

    subject_match = re.search(r"Course Subject Classification:\s*(.+)", message)
    goal_match = re.search(r"Student Main Learning Goal:\s*(.+)", message)

    subject = subject_match.group(1).strip() if subject_match else "General Studies"
    goal = goal_match.group(1).strip() if goal_match else "the requested topic"
    return subject or "General Studies", goal or "the requested topic"


def _fallback_syllabus(message: str) -> WriterResponseSchema:
    subject, goal = _extract_course_context(message)
    topic = goal[:90].strip(". ") or subject

    modules = [
        WriterModuleSchema(
            sub_topic=f"{subject.title()} foundations",
            teaching_guidelines=(
                f"Introduce the key vocabulary behind {topic}. On the board, place the main idea in the center, "
                "draw three labeled branches for definitions, assumptions, and common mistakes, then add one "
                "short worked example beside each branch."
            ),
        ),
        WriterModuleSchema(
            sub_topic="Core methods and worked examples",
            teaching_guidelines=(
                "Build two side-by-side examples: one basic case and one exam-style case. Number every step, "
                "circle each formula or rule when it first appears, and end with a short checkpoint question."
            ),
        ),
        WriterModuleSchema(
            sub_topic="Practice pathway and mastery checks",
            teaching_guidelines=(
                "Create a three-level practice ladder labeled warm-up, standard, and challenge. For each level, "
                "show the expected first move, the reasoning cue, and the final answer-check habit."
            ),
        ),
    ]

    notes = (
        f"# Study Guide: {subject.title()}\n\n"
        f"## Learning Goal\n{goal}\n\n"
        "## How To Study This Topic\n"
        "Start with the definitions, then work through guided examples before attempting independent practice. "
        "After each example, explain why the method works in your own words.\n\n"
        "## Core Roadmap\n"
        "1. Identify the key terms and what each one means.\n"
        "2. Learn the standard method or rule set.\n"
        "3. Apply the method to simple examples.\n"
        "4. Increase difficulty with mixed practice.\n"
        "5. Review mistakes and rewrite the correct reasoning.\n\n"
        "> **Concept Check:** You understand the topic when you can solve a fresh problem and explain each step "
        "without copying the example.\n\n"
        "## Practice Routine\n"
        "- Complete three warm-up questions.\n"
        "- Complete two standard questions without notes.\n"
        "- Write one summary paragraph explaining the method.\n"
    )

    return WriterResponseSchema(
        title=f"{subject.title()} Study Guide",
        source_type="prompt",
        source_summary="Fallback prompt-only note package.",
        modules=modules,
        textbook_handout_notes=notes,
    )


async def run_writer_agent(request: WriterRequestSchema, user_id: str = "course-generator") -> WriterResponseSchema:
    """
    Build a structured study note package from a prompt, PDF, image, or text attachment.
    """
    try:
        bundle: WriterContentBundle = await build_writer_content_bundle(
            prompt=request.prompt,
            helper_material_url=request.helper_material_url,
        )
        user_prompt = build_writer_user_prompt(
            course=request.course,
            prompt=request.prompt,
            source_type=bundle.source_type.value,
            source_summary=bundle.source_summary,
        )

        contents: list[object] = [user_prompt, *bundle.contents]

        response = await client.aio.models.generate_content(
            model=WRITER_MODEL,
            contents=contents,
            config=types.GenerateContentConfig(
                systemInstruction=build_writer_system_prompt(),
                responseMimeType="application/json",
                responseSchema=WriterResponseSchema,
            ),
        )

        if getattr(response, "parsed", None) is not None:
            parsed = response.parsed
            return WriterResponseSchema.model_validate(parsed)

        if response.text:
            return WriterResponseSchema.model_validate_json(response.text)

        raise RuntimeError("Writer agent returned an empty response.")

    except Exception as exc:
        logger.error(
            "Core Google GenAI SDK Writer failed; rolling over to local static fallback definitions: %s",
            str(exc),
            exc_info=True,
        )
        fallback = _fallback_syllabus(request.prompt)
        return WriterResponseSchema(
            title=fallback.title,
            source_type=fallback.source_type,
            source_summary=fallback.source_summary,
            modules=[WriterModuleSchema.model_validate(module.model_dump()) for module in fallback.modules],
            textbook_handout_notes=fallback.textbook_handout_notes,
        )
    finally:
        logger.info("Writer engine finished for designer instance: %s", user_id)


async def run_syllabus_designer(message: str, user_id: str = "course-generator") -> WriterResponseSchema:
    """
    Backward-compatible wrapper for older call sites that still pass a combined prompt string.
    """
    request = WriterRequestSchema(course="General Studies", prompt=message, helper_material_url=None)
    return await run_writer_agent(request=request, user_id=user_id)
