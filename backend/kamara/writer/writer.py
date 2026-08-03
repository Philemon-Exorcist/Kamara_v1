import logging
import os
from google.genai import types,Client
from dotenv import load_dotenv


from .prompts import build_writer_system_prompt, build_writer_user_prompt
from .schemas import WriterContentBundle, WriterModuleSchema, WriterRequestSchema, WriterResponseSchema
from .source_loader import build_writer_content_bundle

logger = logging.getLogger("KamaraLogger")
#WRITER_MODEL = "gemini-3.5-flash"
WRITER_MODEL="gemini-3.6-flash" # will switch to a lower model later if we want to save costs, but for now we want the best quality possible
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
            section_notes=(
                f"## {subject.title()} Foundations\n\n"
                f"This section introduces the core vocabulary and ideas behind "
                f"{topic}, starting from a plain-language definition before any "
                "formal notation is used.\n\n"
                f"**Definition:** {topic} refers to the foundational concept "
                "being studied in this lesson; the precise definition depends "
                "on the specific subject and should be verified against a "
                "current, reliable source.\n\n"
                "**Worked Example:** A simple case applying the definition "
                "above, with the complete solution shown step by step, goes "
                "here."
            ),
        ),
        WriterModuleSchema(
            sub_topic="Core methods",
            section_notes=(
                "## Core Methods\n\n"
                "This section lays out the standard method or rule set used "
                "to work through problems on this topic.\n\n"
                "**Example 1 (basic case):** A straightforward worked example "
                "with its full solution.\n\n"
                "**Example 2 (exam-style case):** A more advanced worked "
                "example, closer to what appears in exam questions, with its "
                "full solution."
            ),
        ),
        WriterModuleSchema(
            sub_topic="Summary and key takeaways",
            section_notes=(
                "## Summary\n\n"
                "A concise recap of the key definitions, formulas, and "
                "methods covered above, presented as a short list a student "
                "could review quickly before an exam."
            ),
        ),
    ]

    notes = (
        f"# Study Guide: {subject.title()}\n\n"
        f"## Learning Goal\n{goal}\n\n"
        f"{modules[0].section_notes}\n\n"
        f"{modules[1].section_notes}\n\n"
        f"{modules[2].section_notes}\n"
    )

    assessment_questions = [
        f"State, in your own words, the core definition covered under {subject.title()}.",
        "Work through one basic example using the standard method described above, showing every step.",
        "Attempt one exam-style question on this topic and check your reasoning against the worked examples.",
    ]

    return WriterResponseSchema(
        title=f"{subject.title()} Study Guide",
        source_type="prompt",
        source_summary="Fallback prompt-only note package.",
        modules=modules,
        textbook_handout_notes=notes,
        assessment_questions=assessment_questions,
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
                tools=[types.Tool(google_search=types.GoogleSearch())],
                temperature=1.0, 
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
            assessment_questions=fallback.assessment_questions,
        )
    finally:
        logger.info("Writer engine finished for designer instance: %s", user_id)


async def run_syllabus_designer(message: str, user_id: str = "course-generator") -> WriterResponseSchema:
    """
    Backward-compatible wrapper for older call sites that still pass a combined prompt string.
    """
    request = WriterRequestSchema(course="General Studies", prompt=message, helper_material_url=None)
    return await run_writer_agent(request=request, user_id=user_id)