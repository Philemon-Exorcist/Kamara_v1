import asyncio
import logging
import os

from dotenv import load_dotenv
from fastapi import WebSocket
from google import genai
from google.genai import types

from .response_handler import receive_response_from_ai
from .task_handler import forward_frontend_mic_and_canvas_to_gemini
from .toolset.tools import tools

load_dotenv()
logger = logging.getLogger("KamaraLogger")

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("Missing API KEY")

client = genai.Client(api_key=api_key, http_options={"api_version": "v1alpha"})


async def agent(student_id: str, websocket: WebSocket, system_prompt: str):
    """
    Orchestrates the Gemini Live session and bridges the browser WebSocket.
    """
    model =  "gemini-2.5-flash-native-audio-preview-12-2025"
    #model =  "gemini-live-2.5-flash-native-audio"
    config = types.LiveConnectConfig(
        response_modalities=["AUDIO"],
        system_instruction=types.Content(
            parts=[types.Part.from_text(text=system_prompt)]
        ),
        speech_config={
            "voice_config": {"prebuilt_voice_config": {"voice_name": "Kore"}}
        },
        tools=[tools, {"google_search": {}}],
    )

    try:
        async with client.aio.live.connect(model=model, config=config) as session:
            logger.info("🚀 AI Orchestrator running live session for student: %s", student_id)



            async with asyncio.TaskGroup() as tg:

                tg.create_task(
                    forward_frontend_mic_and_canvas_to_gemini(
                        student_id=student_id,
                        websocket=websocket,
                        session=session,
                    )
                )

                tg.create_task(
                        receive_response_from_ai(
                        session=session,
                       student_id=student_id,
                       websocket=websocket
                  )
                )


    
    except TimeoutError:
       logger.error("Time out, failed to connect")

    #except* Exception as exc:
    except Exception as exc:
        import traceback

        logger.error("Detailed TaskGroup Failure:\n%s", "".join(traceback.format_exception(exc)))
        logger.error("Error occurred inside the runtime orchestrator for %s: %s", student_id, str(exc))
