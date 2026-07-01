
import asyncio
import base64
import json
import logging
import time  # 🚀 Added time for the gate check

from fastapi import WebSocketDisconnect
from google.genai import types

logger = logging.getLogger("KamaraLogger")


async def forward_frontend_mic_and_canvas_to_gemini(student_id: str, websocket, session):
    """
    Read the student WebSocket directly and forward mic and canvas frames to Gemini.
    Resilient to frontend framework object wrapping on both binary and text channels.
    """
    # 🚀 TIME-GATE GUARD STATE: Tracks the last time we allowed a canvas update to hit Gemini
    last_canvas_update_time = 0.0

    try:
        logger.info("📡 Multimodal inbound streaming worker activated for %s", student_id)

        while True:
            try:
                frame = await websocket.receive()
                
                # Turn off high-frequency verbose logs if they crowd your terminal panel
                # logger.info("Inbound websocket frame received for %s", student_id)

                # ==================================================================
                # CHANNEL 1: PROCESSING INBOUND MIC FRAMES (Arriving via 'bytes')
                # ==================================================================
                if "bytes" in frame and frame["bytes"]:
                    raw_data = frame["bytes"]
                    if not raw_data:
                        continue

                    audio_data = None

                    # Detect if the frontend packed a JSON object inside binary bytes
                    if raw_data.startswith(b'{"') or b'"type"' in raw_data:
                        try:
                            parsed_payload = json.loads(raw_data.decode("utf-8", errors="ignore"))
                            inner_bytes_data = parsed_payload.get("bytes")
                            
                            if isinstance(inner_bytes_data, str):
                                audio_data = base64.b64decode(inner_bytes_data)
                            elif inner_bytes_data:
                                audio_data = bytes(inner_bytes_data)
                        except Exception as parse_err:
                            logger.warning("Failed parsing binary-wrapped JSON audio metadata: %s", str(parse_err))
                            continue
                    else:
                        audio_data = raw_data

                    if not audio_data or len(audio_data) == 0:
                        continue

                    # Forward microphone data IMMEDIATELY without delays [0xa9059cbb]
                    await session.send(
                        input=types.LiveClientContent(
                            turns=[
                                types.Content(
                                    role="user",
                                    parts=[
                                        types.Part.from_bytes(
                                            data=audio_data,
                                            mime_type="audio/pcm;rate=16000",
                                        )
                                    ],
                                )
                            ]
                        )
                    )

                # ==================================================================
                # CHANNEL 2: PROCESSING CANVAS EVENTS (Arriving via 'text')
                # ==================================================================
                elif "text" in frame and frame["text"]:
                    payload = json.loads(frame["text"])
                    event_type = payload.get("type")

                    # 🚀 TIME-GATE GUARD: Check if the frontend is flooding canvas requests
                    current_time = time.time()
                    
                    if event_type in ("canvas_snapshot_text", "canvas_snapshot_vision"):
                        # Only let canvas mutations hit Gemini if at least 2.5 seconds have passed
                        # This prevents interrupting Gemini before it can speak [0xa9059cbb]
                        if (current_time - last_canvas_update_time) < 2.5:
                            logger.info("⏳ Dropped high-frequency canvas frame to let Gemini speak.")
                            continue
                        
                        # Update the timestamp marker if we pass the validation gate
                        last_canvas_update_time = current_time

                    # Case A: Structural text element placement on the board
                    if event_type == "canvas_snapshot_text":
                        snapshot_data = f"CURRENT_WHITEBOARD_OBJECTS_STORE:\n{payload.get('data', '')}"
                        await session.send(
                            input=types.LiveClientContent(
                                turns=[
                                    types.Content(
                                        role="user",
                                        parts=[types.Part.from_text(text=snapshot_data)],
                                    )
                                ]
                            )
                        )
                        logger.info("📐 Injected throttled tldraw snapshot for %s", student_id)

                    # Case B: Exported Base64 visual screen capture canvas thumbnail frames
                    elif event_type == "canvas_snapshot_vision":
                        image_string = payload.get("image", "")
                        if "," in image_string:
                            image_string = image_string.split(",")[-1]

                        raw_image_bytes = base64.b64decode(image_string)
                        await session.send(
                            input=types.LiveClientContent(
                                turns=[
                                    types.Content(
                                        role="user",
                                        parts=[
                                            types.Part.from_bytes(
                                                data=raw_image_bytes,
                                                mime_type="image/png",
                                            )
                                        ],
                                    )
                                ]
                            )
                        )
                        logger.info("👁️ Injected throttled canvas vision frame for %s", student_id)

            except (WebSocketDisconnect, RuntimeError):
                logger.info("Connection drop detected for student %s. Stopping inbound worker thread.", student_id)
                return
            except json.JSONDecodeError as decode_err:
                logger.warning("Skipping malformed canvas payload for %s: %s", student_id, str(decode_err))
            except Exception as e:
                logger.warning("Recoverable frame skipping on pipeline for %s: %s", student_id, str(e))
                await asyncio.sleep(0.01)

            await asyncio.sleep(0.001)

    except asyncio.CancelledError:
        logger.info("Multimodal input worker safely cancelled for student %s.", student_id)
    except Exception as fatal_err:
        logger.error("Non-fatal collapse caught inside inbound processor for %s: %s", student_id, str(fatal_err))




"""
import asyncio
import base64
import json
import logging

from fastapi import WebSocketDisconnect
from google.genai import types

logger = logging.getLogger("KamaraLogger")


async def forward_frontend_mic_and_canvas_to_gemini(student_id: str, websocket, session):
    
    Read the student WebSocket directly and forward mic and canvas frames to Gemini.

    Read the student WebSocket directly and forward mic and canvas frames to Gemini.
    Resilient to frontend framework object wrapping on both binary and text channels.
    
    try:
        logger.info("📡 Multimodal inbound streaming worker activated for %s", student_id)

        while True:
            try:
                frame = await websocket.receive()
                logger.info(
                    "Inbound websocket frame received for %s | keys=%s | has_bytes=%s | has_text=%s",
                    student_id,
                    list(frame.keys()),
                    bool(frame.get("bytes")),
                    bool(frame.get("text")),
                )

                # ==================================================================
                # CHANNEL 1: PROCESSING INBOUND MIC FRAMES (Arriving via 'bytes')
                # ==================================================================
                if "bytes" in frame and frame["bytes"]:
                    raw_data = frame["bytes"]
                    if not raw_data:
                        continue

                    audio_data = None

                    # 🚀 CRITICAL FIX: Detect if the frontend packed a JSON object inside binary bytes
                    if raw_data.startswith(b'{"') or b'"type"' in raw_data:
                        try:
                            # Decode the binary string slice into a readable Python dictionary
                            parsed_payload = json.loads(raw_data.decode("utf-8", errors="ignore"))
                            inner_bytes_data = parsed_payload.get("bytes")
                            
                            if isinstance(inner_bytes_data, str):
                                # Clean up base64 wrappers if stringified by the framework
                                audio_data = base64.b64decode(inner_bytes_data)
                            elif inner_bytes_data:
                                audio_data = bytes(inner_bytes_data)
                        except Exception as parse_err:
                            logger.warning("Failed parsing binary-wrapped JSON audio metadata: %s", str(parse_err))
                            continue
                    else:
                        # Stream consists of standard, clean un-wrapped binary array buffer chunks
                        audio_data = raw_data

                    if not audio_data or len(audio_data) == 0:
                        continue

                    logger.info(
                        "🔊 Extracted and routing %s clean PCM audio bytes upstream to Gemini for %s",
                        len(audio_data),
                        student_id,
                    )
                    
                    # Forward the clean, un-wrapped binary bytes down Google's live network stream
                    await session.send(
                        input=types.LiveClientContent(
                            turns=[
                                types.Content(
                                    role="user",
                                    parts=[
                                        types.Part.from_bytes(
                                            data=audio_data,
                                            mime_type="audio/pcm;rate=16000",
                                        )
                                    ],
                                )
                            ]
                        )
                    )

                # ==================================================================
                # CHANNEL 2: PROCESSING CANVAS EVENTS (Arriving via 'text')
                # ==================================================================
                elif "text" in frame and frame["text"]:
                    payload = json.loads(frame["text"])
                    event_type = payload.get("type")
                    
                    logger.info(
                        "Canvas/control payload received for %s | type=%s | size=%s",
                        student_id,
                        event_type,
                        len(frame["text"]),
                    )

                    # Case A: Structural text element placement on the board
                    if event_type == "canvas_snapshot_text":
                        snapshot_data = f"CURRENT_WHITEBOARD_OBJECTS_STORE:\n{payload.get('data', '')}"
                        logger.info(
                            "Forwarding canvas snapshot text for %s | snapshot_chars=%s",
                            student_id,
                            len(payload.get("data", "") or ""),
                        )
                        await session.send(
                            input=types.LiveClientContent(
                                turns=[
                                    types.Content(
                                        role="user",
                                        parts=[types.Part.from_text(text=snapshot_data)],
                                    )
                                ]
                            )
                        )
                        logger.info("📐 Injected tldraw structural snapshot for %s", student_id)

                    # Case B: Exported Base64 visual screen capture canvas thumbnail frames
                    elif event_type == "canvas_snapshot_vision":
                        image_string = payload.get("image", "")
                        if "," in image_string:
                            image_string = image_string.split(",")[-1]

                        logger.info(
                            "Forwarding canvas snapshot vision for %s | image_b64_chars=%s",
                            student_id,
                            len(image_string),
                        )
                        raw_image_bytes = base64.b64decode(image_string)
                        await session.send(
                            input=types.LiveClientContent(
                                turns=[
                                    types.Content(
                                        role="user",
                                        parts=[
                                            types.Part.from_bytes(
                                                data=raw_image_bytes,
                                                mime_type="image/png",
                                            )
                                        ],
                                    )
                                ]
                            )
                        )
                        logger.info("👁️ Injected tldraw canvas vision frame for %s", student_id)

            except (WebSocketDisconnect, RuntimeError):
                logger.info("Connection drop detected for student %s. Stopping inbound worker thread.", student_id)
                return
            except json.JSONDecodeError as decode_err:
                logger.warning("Skipping malformed canvas payload for %s: %s", student_id, str(decode_err))
            except Exception as e:
                logger.warning("Recoverable frame skipping on pipeline for %s: %s", student_id, str(e))
                await asyncio.sleep(0.01)

            await asyncio.sleep(0.001)

    except asyncio.CancelledError:
        logger.info("Multimodal input worker safely cancelled for student %s.", student_id)
    except Exception as fatal_err:
        logger.error("Non-fatal collapse caught inside inbound processor for %s: %s", student_id, str(fatal_err))






difference




    try:
        logger.info("📡 Multimodal inbound streaming worker activated for %s", student_id)

        while True:
            try:
                frame = await websocket.receive()
                logger.info(
                    "Inbound websocket frame received for %s | keys=%s | has_bytes=%s | has_text=%s",
                    student_id,
                    list(frame.keys()),
                    bool(frame.get("bytes")),
                    bool(frame.get("text")),
                )

                if "bytes" in frame and frame["bytes"]:
                    audio_data = frame["bytes"]
                    if not audio_data:
                        continue

                    logger.info(
                        "Mic audio chunk received for %s | bytes=%s | mime=audio/pcm;rate=16000",
                        student_id,
                        len(audio_data),
                    )
                    await session.send(
                        input=types.LiveClientContent(
                            turns=[
                                types.Content(
                                    role="user",
                                    parts=[
                                        types.Part.from_bytes(
                                            data=audio_data,
                                            mime_type="audio/pcm;rate=16000",
                                        )
                                    ],
                                )
                            ]
                        )
                    )

                elif "text" in frame and frame["text"]:
                    payload = json.loads(frame["text"]) # this code for audio byte
                    event_type = payload.get("type")
                    logger.info(
                        "Canvas/control payload received for %s | type=%s | size=%s",
                        student_id,
                        event_type,
                        len(frame["text"]),
                    )

                    if event_type == "canvas_snapshot_text":
                        snapshot_data = f"CURRENT_WHITEBOARD_OBJECTS_STORE:\n{payload.get('data', '')}"
                        logger.info(
                            "Forwarding canvas snapshot text for %s | snapshot_chars=%s",
                            student_id,
                            len(payload.get("data", "") or ""),
                        )
                        await session.send(
                            input=types.LiveClientContent(
                                turns=[
                                    types.Content(
                                        role="user",
                                        parts=[types.Part.from_text(text=snapshot_data)],
                                    )
                                ]
                            )
                        )
                        logger.info("📐 Injected tldraw structural snapshot for %s", student_id)

                    elif event_type == "canvas_snapshot_vision":
                        image_string = payload.get("image", "")
                        if "," in image_string:
                            image_string = image_string.split(",")[-1]

                        logger.info(
                            "Forwarding canvas snapshot vision for %s | image_b64_chars=%s",
                            student_id,
                            len(image_string),
                        )
                        raw_image_bytes = base64.b64decode(image_string)
                        await session.send(
                            input=types.LiveClientContent(
                                turns=[
                                    types.Content(
                                        role="user",
                                        parts=[
                                            types.Part.from_bytes(
                                                data=raw_image_bytes,
                                                mime_type="image/png",
                                            )
                                        ],
                                    )
                                ]
                            )
                        )
                        logger.info("👁️ Injected tldraw canvas vision frame for %s", student_id)

            except (WebSocketDisconnect, RuntimeError):
                logger.info("Connection drop detected for student %s. Stopping inbound worker thread.", student_id)
                return
            except json.JSONDecodeError as decode_err:
                logger.warning("Skipping malformed canvas payload for %s: %s", student_id, str(decode_err))
            except Exception as e:
                logger.warning("Recoverable frame skipping on pipeline for %s: %s", student_id, str(e))
                await asyncio.sleep(0.01)

            await asyncio.sleep(0.001)

    except asyncio.CancelledError:
        logger.info("Multimodal input worker safely cancelled for student %s.", student_id)
    except Exception as fatal_err:
        logger.error("Non-fatal collapse caught inside inbound processor for %s: %s", student_id, str(fatal_err))


        

"""