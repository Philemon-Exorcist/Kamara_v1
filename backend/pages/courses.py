import asyncio
import json
import logging
import re
from typing import Optional
import httpx
from dotenv import load_dotenv
import os
from fastapi import APIRouter, Depends, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from google.genai import types, Client
from app.auth import verify_student_token
from app.supabase_client import get_supabase_admin
from kamara.writer.writer import _fallback_syllabus, run_syllabus_designer

logger = logging.getLogger("KamaraLogger")
course_router = APIRouter(prefix="/api/v1", tags=["Course Pipeline"])

# Lock to a supported model so older environment values cannot force 404s.
VISION_MODEL = "gemini-2.5-flash"
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("Missing API KEY")
client = Client(api_key=api_key, http_options={"api_version": "v1alpha"})


class CourseInitializationRequest(BaseModel):
    course: str
    prompt: str
    helper_material_url: Optional[str] = None


def _public_generation_error(error: Exception) -> str:
    message = str(error)
    if "403" in message or "Forbidden" in message:
        return "The AI provider refused the generation request. Please try again in a moment."

    clean_message = re.sub(r"<[^>]+>", " ", message)
    clean_message = " ".join(clean_message.split())
    return clean_message[:220] if clean_message else "Course generation failed. Please try again."


@course_router.post("/pages/course/generate")
@course_router.post("/courses/generate")
async def generate_course_modules(
    payload: CourseInitializationRequest,
    current_user: dict = Depends(verify_student_token),
):# want to use this kind of system to get user id 
    """
    Streaming pipeline that extracts text from uploaded materials, runs the writer
    agent, stores generated modules, and emits live progress updates.
    """
    student_id = current_user.id
    logger.info("Initializing course generation for student: %s", student_id)

    async def writer_agent_generator():
        supabase = get_supabase_admin()
        session_id = None
        finished_successfully = False

        try:
            yield f"data: {json.dumps({'status': 'init', 'message': 'Waking up Kamara Writer Agent...'})}\n\n"
            await asyncio.sleep(0.3)

            session_insert = supabase.table("sessions").insert({
                "student_id": student_id,
                "course": payload.course.strip().lower(),
                "user_prompt": payload.prompt.strip(),
                "helper_material_url": payload.helper_material_url,
            }).execute()

            if not session_insert or not session_insert.data:
                raise RuntimeError("Failed to register study session metadata row.")

            session_data = session_insert.data[0]
            session_id = session_data.get("id")

            yield f"data: {json.dumps({'status': 'processing', 'message': 'Checking attached learning materials...', 'session_id': str(session_id)})}\n\n"
            await asyncio.sleep(0.3)

            extracted_text_context = "No image attachments detected."

            if payload.helper_material_url:
                image_extensions = (".jpg", ".jpeg", ".png", ".webp", ".heic")

                if payload.helper_material_url.lower().endswith(image_extensions):
                    yield f"data: {json.dumps({'status': 'processing', 'message': 'Running Kamara Vision Engine OCR on uploaded image...'})}\n\n"

                    try:
                        async with httpx.AsyncClient() as client:
                            img_response = await client.get(payload.helper_material_url)
                            if img_response.status_code == 200:
                                image_bytes = img_response.content
                                ai_client = client
                                vision_pass = await ai_client.aio.models.generate_content(
                                    model=VISION_MODEL,
                                    contents=[
                                        types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
                                        "Read this image completely. Extract all text, headings, diagrams, mathematical equations, and handwritten notes into comprehensive clear text strings.",
                                    ],
                                )
                                extracted_text_context = vision_pass.text or "Could not extract clean text strings from the image."
                                logger.info("Successfully extracted text context from user image upload using core SDK.")
                            else:
                                extracted_text_context = "Image file was unreachable at storage target destination."
                    except Exception as vision_err:
                        logger.error("Vision conversion failed: %s", str(vision_err), exc_info=True)
                        extracted_text_context = f"Vision conversion bypassed due to extraction error: {str(vision_err)}"
                else:
                    extracted_text_context = "Helper material is a standard non-image document."

            yield f"data: {json.dumps({'status': 'processing', 'message': f'Kamara Writer Agent is running deep research and compiling textbook notes for {payload.course}...'})}\n\n"

            agent_input_prompt = (
                f"Course Subject Classification: {payload.course}\n"
                f"Student Main Learning Goal: {payload.prompt}\n\n"
                f"=========================================\n"
                f"EXTRACTED TEXT FROM USER ATTACHED IMAGE/MATERIAL:\n"
                f"{extracted_text_context}\n"
                f"=========================================\n\n"
                "Please execute deep research using your tools, analyze the attached material constraints above, "
                "and construct the complete study syllabus roadmap and notes text packages."
            )

            try:
                agent_response = await run_syllabus_designer(
                    message=agent_input_prompt,
                    user_id=str(student_id),
                )
            except Exception as e:
                logger.error(
                    "Writer Agent failed inside router pipeline loop; generating default fallback object: %s",
                    str(e),
                    exc_info=True,
                )
                agent_response = _fallback_syllabus(agent_input_prompt)

            modules_list = agent_response.modules
            full_textbook_notes = agent_response.textbook_handout_notes

            yield f"data: {json.dumps({'status': 'processing', 'message': 'Research completed! Unpacking your structured study modules...'})}\n\n"
            await asyncio.sleep(0.5)

            for index, mod_step in enumerate(modules_list, start=1):
                module_title = mod_step.sub_topic if mod_step.sub_topic else f"Module {index}"
                compiled_body = (
                    f"### Teaching & Learning Objectives\n"
                    f"{mod_step.teaching_guidelines}\n\n"
                    f"### Comprehensive Textbook Study Notes\n"
                    f"{full_textbook_notes}"
                )

                yield f"data: {json.dumps({'status': 'processing', 'message': f'Writing {module_title} into your Library...'})}\n\n"

                supabase.table("library").insert({
                    "session_id": session_id,
                    "student_id": student_id,
                    "content_type": "ai_module",
                    "title": module_title,
                    "body_text": compiled_body,
                }).execute()


        except Exception as err:
            logger.error("COURSE ROUTE FAILURE: %s", str(err), exc_info=True)
            yield f"data: {json.dumps({'status': 'error', 'message': f'Generation failure: {_public_generation_error(err)}'})}\n\n"
        finally:
            logger.info(
                "Course generation stream finished for student=%s session_id=%s success=%s",
                student_id,
                session_id,
                finished_successfully,
            )

    return StreamingResponse(writer_agent_generator(), media_type="text/event-stream", status_code=status.HTTP_200_OK)
