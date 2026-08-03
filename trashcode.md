""""""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, field_validator

#from .supabase_client import supabase_admin
from .supabase_client import get_supabase_admin
from .auth import verify_student_token

logger = logging.getLogger("KamaraLogger")

router = APIRouter(prefix="/api/v1")


class UserAuthCredentials(BaseModel):
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, value):
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        return value

class SignupCredentials(UserAuthCredentials):
    first_name: str
    last_name: str

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_name_part(cls, value):
        if len(value.strip()) < 2:
            raise ValueError("Please enter a valid name.")
        return value.strip()


class ForgotPassword(BaseModel):
    email : EmailStr


class UpdatePasswordRequest(BaseModel):
    access_token: str
    new_password: str


# this is for verifying email
class EmailVerification(BaseModel):
    token_hash : str


@router.post("/auth/signup")
async def process_signup(payload: SignupCredentials):
    logger.info("Attempting to register new student: %s", payload.email)
    
    supabase_admin = get_supabase_admin()
    #full_name = f"{payload.first_name} {payload.last_name}".strip()
    first_name = f"{payload.first_name}".strip()
    last_name = f"{payload.last_name}".strip()

    try:
        auth_user = supabase_admin.auth.admin.create_user(
            {
                "email": payload.email,
                "password": payload.password,
                "email_confirm": False,
                "user_metadata": {
                    "first_name": first_name,
                    "last_name": last_name
                },
            }
        )
    except Exception as e:
        logger.error("SUPABASE AUTH CREATE USER FAILED: %s: %s", type(e).__name__, str(e))
        raise HTTPException(
            status_code=400,
            detail=f"Supabase Auth user creation failed: {str(e)}",
        )

    student_id = auth_user.user.id
    logger.info("Successfully registered user in auth.users. Assigned UUID: %s", student_id)

    try:
        supabase_admin.table("profiles").insert(
            {
                "id": student_id,
                "email": auth_user.user.email,
                "first_name": first_name,
                "last_name": last_name
            }
        ).execute()
    except Exception as e:
        logger.error("SUPABASE PROFILE INSERT FAILED: %s: %s", type(e).__name__, str(e))
        raise HTTPException(
            status_code=400,
            detail=f"Profile creation failed: {str(e)}",
        )

    logger.info("Public profile database row tracking written successfully.")
    return {
        "status": "pending_verification", 
        "message": "Awesome! Please check your email inbox to verify your account."
    }


@router.post("/auth/login")
async def process_login(payload: UserAuthCredentials):

    supabase_admin = get_supabase_admin()
    try:
        session = supabase_admin.auth.sign_in_with_password(
            {
                "email": payload.email,
                "password": payload.password,
            }
        )
        return {
            "access_token": session.session.access_token,
            "user_id": session.user.id,
            "user": {
                "id": session.user.id,
                "email": session.user.email,
                "full_name": (getattr(session.user, "user_metadata", None) or {}).get("full_name", ""),
            },
        }
    except Exception as e:
        logger.error("SUPABASE AUTH LOGIN FAILED: %s", str(e))
        raise HTTPException(status_code=401, detail="Authentication failed.")


@router.get("/auth/me")
async def get_current_auth_user(current_user=Depends(verify_student_token)):
    student_id = current_user.id
    supabase_admin = get_supabase_admin()
# hello
    profile = {}
    try:
        profile_query = supabase_admin.table("profiles")\
            .select("email, full_name")\
            .eq("id", student_id)\
            .maybe_single()\
            .execute()
        profile = getattr(profile_query, "data", None) or {}
    except Exception as e:
        logger.warning("PROFILE LOOKUP FAILED FOR /auth/me: %s", str(e))

    metadata = getattr(current_user, "user_metadata", {}) or {}
    email = profile.get("email") or getattr(current_user, "email", "")
    full_name = profile.get("full_name") or metadata.get("full_name", "")

    return {
        "id": student_id,
        "email": email,
        "name": full_name or email or "Student",
        "full_name": full_name,
    }
    


@router.post("/auth/verify")
async def verify_email_token(payload: EmailVerification):
    logger.info("Received email token verification request.")
    
    supabase = get_supabase_admin()
    
    try:
        # Hand the token over to Supabase Identity Core to activate the account
        response = supabase.auth.verify_otp({
            "token_hash": payload.token_hash,
            "type": "signup"  # Tells Supabase this is a new signup verification
        })
        
        logger.info("Email verification successful for user.")
        return {
            "status": "success",
            "message": "Your email has been successfully verified! and account. You can now log in.",
            "user_id": response.user.id
        }
        
    except Exception as e:
        logger.error("EMAIL VERIFICATION FAILED: %s", str(e))
        raise HTTPException(
            status_code=400,
            detail="The verification link is invalid or has expired. Please try signing up again."
        )



@router.post("/auth/forgot-password",status_code=status.HTTP_200_OK)
async def forgot_password(payload:ForgotPassword):
    clean_email = payload.email.strip().lower()
    logger.info("Password reset requested for: %s", clean_email)
    
    supabase_admin = get_supabase_admin()
    
    try:
        # Supabase will look up the email and send them a secure recovery link
        supabase_admin.auth.reset_password_for_email(
            clean_email,
            options={
                # Tell Supabase where to redirect the user's browser when they click the email link
                "redirect_to": "http://localhost:3000/reset-password"  # Change to live frontend URL 
            }
        )
        
        logger.info("Password reset email dispatched successfully.")
        return {
            "status": "success",
            "message": "If an account exists with that email, a password reset link has been sent."
        }
    except Exception as e:
        logger.error("FORGOT PASSWORD ERROR: %s", str(e))
        # Pro-tip: For security, still return success so hackers don't know who has an account
        return {
            "status": "success",
            "message": "If an account exists with that email, a password reset link has been sent."
        }


@router.post("/auth/update-password")
async def process_password_update(payload: UpdatePasswordRequest):
    logger.info("Attempting to process user password update.")
    
    # Crucial: We must create a client that sets the user's specific session token 
    # so Supabase knows WHICH user's password is being changed.
    supabase = get_supabase_admin()
    
    try:
        # 1. Authenticate the temporary session using the token React sent down
        supabase.auth.set_session(payload.access_token, "")
        
        # 2. Update the user's password securely
        supabase.auth.update_user({"password": payload.new_password})
        
        logger.info("User password successfully updated in Supabase Auth.")
        return {
            "status": "success",
            "message": "Your password has been changed successfully! You can now log in with your new password."
        }
    except Exception as e:
        logger.error("PASSWORD UPDATE CRASH: %s", str(e))
        raise HTTPException(
            status_code=400,
            detail="Failed to update password. The link may have expired or is invalid."
        )









# authentication 


from fastapi import Header, HTTPException, status
#from .supabase_client import supabase_admin # old supabase client initialization
from .supabase_client import get_supabase_admin

async def verify_student_token(authorization: str = Header(None)) -> dict:
    """ Firewall layer intercepting incoming tokens from React """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Access denied.Missing or Malformed Token")
    
    token = authorization.split(" ")[1]
    
    supabase_admin = get_supabase_admin()
    try:
        # Validate the token directly with Supabase Identity core
        user_response = supabase_admin.auth.get_user(token)
        return user_response.user
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session token.")







import os
import base64
import json
from pathlib import Path
from urllib.parse import urlparse
from dotenv import load_dotenv
from supabase import create_client, Client, ClientOptions

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

if not SUPABASE_URL or not SUPABASE_ANON_KEY or not SUPABASE_SERVICE_KEY:
    raise RuntimeError(
        "SUPABASE_URL, SUPABASE_ANON_KEY, and SUPABASE_SERVICE_KEY must be set in backend/.env or the environment."
    )

parsed_url = urlparse(SUPABASE_URL)
if parsed_url.scheme not in ("http", "https") or not parsed_url.netloc:
    raise RuntimeError(
        "SUPABASE_URL must be a valid URL, e.g. https://<project-ref>.supabase.co"
    )

if parsed_url.netloc.lower() == "supabase.co":
    raise RuntimeError(
        "SUPABASE_URL appears invalid. Use your project-specific Supabase URL like https://<project-ref>.supabase.co"
    )

def _get_supabase_key_role(key: str) -> str | None:
    try:
        payload = key.split(".")[1]
        payload += "=" * (-len(payload) % 4)
        decoded = base64.urlsafe_b64decode(payload.encode("utf-8"))
        claims = json.loads(decoded)
        return claims.get("role")
    except Exception:
        return None

SUPABASE_KEY_ROLE = _get_supabase_key_role(SUPABASE_SERVICE_KEY)

if SUPABASE_KEY_ROLE != "service_role":
    raise RuntimeError(
        "SUPABASE_SERVICE_KEY must be the Supabase service_role secret key, not the anon/public key."
    )

SUPABASE_PROJECT_URL = f"{parsed_url.scheme}://{parsed_url.netloc}"

# ✅ THE FIXED FACTORY WORKER:
# Instead of initializing a single global variable, this function creates
# an isolated, fresh client configuration every single time a route calls it.
def get_supabase_admin() -> Client:
    """
    Spins up a clean, completely independent administrative client instance.
    This safely prevents user session token contamination on concurrent threads.
    """
    return create_client(
        SUPABASE_PROJECT_URL, 
        SUPABASE_SERVICE_KEY,
        options=ClientOptions(
            auto_refresh_token=False,  
            persist_session=False      
        )
    )


def get_supabase_public() -> Client:
    """
    Creates a public Supabase client for user-facing auth flows like sign_up.
    """
    return create_client(
        SUPABASE_PROJECT_URL,
        SUPABASE_ANON_KEY,
        options=ClientOptions(
            auto_refresh_token=False,
            persist_session=False,
        ),
    )
""""""
"""
import os
import base64
import json
from pathlib import Path
from urllib.parse import urlparse
from dotenv import load_dotenv
from supabase import create_client, Client, ClientOptions  # Added ClientOptions

#load_dotenv(Path(__file__).resolve().parents[1] / ".env")
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    raise RuntimeError(
        "SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in backend/.env or the environment."
    )

parsed_url = urlparse(SUPABASE_URL)
if parsed_url.scheme not in ("http", "https") or not parsed_url.netloc:
    raise RuntimeError(
        "SUPABASE_URL must be a valid URL, e.g. https://<project-ref>.supabase.co"
    )

if parsed_url.netloc.lower() == "supabase.co":
    raise RuntimeError(
        "SUPABASE_URL appears invalid. Use your project-specific Supabase URL like https://<project-ref>.supabase.co"
    )

def _get_supabase_key_role(key: str) -> str | None:
    try:
        payload = key.split(".")[1]
        payload += "=" * (-len(payload) % 4)
        decoded = base64.urlsafe_b64decode(payload.encode("utf-8"))
        claims = json.loads(decoded)
        return claims.get("role")
    except Exception:
        return None

SUPABASE_KEY_ROLE = _get_supabase_key_role(SUPABASE_SERVICE_KEY)

if SUPABASE_KEY_ROLE != "service_role":
    raise RuntimeError(
        "SUPABASE_SERVICE_KEY must be the Supabase service_role secret key, not the anon/public key."
    )

SUPABASE_PROJECT_URL = f"{parsed_url.scheme}://{parsed_url.netloc}"

# ✅ FIXED: This master client explicitly stops session persistence and auto-refreshes.
# This forces the client to use the verified service_role authorization header on every single request.
supabase_admin: Client = create_client(
    SUPABASE_PROJECT_URL, 
    SUPABASE_SERVICE_KEY,
    options=ClientOptions(
        auto_refresh_token=False,  # Bypasses client-side student session token refreshing
        persist_session=False      # Prevents student tokens from replacing your master service_role key
    )
)

"""

"""
import os
import base64
import json
from pathlib import Path
from urllib.parse import urlparse
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    raise RuntimeError(
        "SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in backend/.env or the environment."
    )

parsed_url = urlparse(SUPABASE_URL)
if parsed_url.scheme not in ("http", "https") or not parsed_url.netloc:
    raise RuntimeError(
        "SUPABASE_URL must be a valid URL, e.g. https://<project-ref>.supabase.co"
    )

if parsed_url.netloc.lower() == "supabase.co":
    raise RuntimeError(
        "SUPABASE_URL appears invalid. Use your project-specific Supabase URL like https://<project-ref>.supabase.co"
    )

def _get_supabase_key_role(key: str) -> str | None:
    try:
        payload = key.split(".")[1]
        payload += "=" * (-len(payload) % 4)
        decoded = base64.urlsafe_b64decode(payload.encode("utf-8"))
        claims = json.loads(decoded)
        return claims.get("role")
    except Exception:
        return None

SUPABASE_KEY_ROLE = _get_supabase_key_role(SUPABASE_SERVICE_KEY)

if SUPABASE_KEY_ROLE != "service_role":
    raise RuntimeError(
        "SUPABASE_SERVICE_KEY must be the Supabase service_role secret key, not the anon/public key."
    )

SUPABASE_PROJECT_URL = f"{parsed_url.scheme}://{parsed_url.netloc}"

# This master client bypasses Row Level Security (RLS) to register/log in users from your backend
supabase_admin: Client = create_client(SUPABASE_PROJECT_URL, SUPABASE_SERVICE_KEY)


"""






@router.post("/auth/verify")
async def verify_email_token(payload: EmailVerification):
    logger.info("Received email token verification request.")
    
    supabase = get_supabase_admin()
    
    try:
        # Hand the token over to Supabase Identity Core to activate the account
        response = supabase.auth.verify_otp({
            "token_hash": payload.token_hash,
            "type": "signup"  # Tells Supabase this is a new signup verification
        })
        
        logger.info("Email verification successful for user.")
        return {
            "status": "success",
            "message": "Your email has been successfully verified! and account. You can now log in.",
            "user_id": response.user.id
        }
        
    except Exception as e:
        logger.error("EMAIL VERIFICATION FAILED: %s", str(e))
        raise HTTPException(
            status_code=400,
            detail="The verification link is invalid or has expired. Please try signing up again."
        )






"""
import asyncio
import base64
import logging

from google.genai import types

from connection.connect_manager import manager
from .toolset.tools import tools_handler
from fastapi import WebSocket

logger = logging.getLogger("KamaraLogger")


async def receive_response_from_ai(session, student_id: str,
                                   websocket: WebSocket
                                   ):
    
    Receives text, voice, and tool calls from Gemini Live and streams them to the browser.

    try:
        async for response in session.receive():
            try:
                 # 🔍 VISIBILITY LOG 1: Track every single response wrapper frame hitting your server
                logger.info(f"📥 Received raw response packet from Gemini for {student_id}")
                if response.server_content and response.server_content.model_turn:
                    logger.info(f"🗣️ Gemini model turn detected for {student_id}")

                    for part in response.server_content.model_turn.parts:
                        # Print if text strings are coming through
                        #if part.text:
                       #     logger.info(f"📝 Gemini Text Output: {part.text}")
                       #     await websocket.send_json({"type": "assistant_text", "content": part.text})

                        if part.inline_data and part.inline_data.data:
                            logger.info(
                                "🔥 SUCCESS: Received raw voice bytes from Gemini for %s | Length=%s bytes",
                                student_id,
                                len(audio_bytes)
                            )

                            audio_bytes = part.inline_data.data
                          

                            logger.info(
                                "Gemini audio chunk ready for %s | bytes=%s | mime_type=%s",
                                student_id,
                                len(audio_bytes)
                            )

                            await websocket.send_bytes(audio_bytes)

                     
                            #await manager.send_binary_audio(audio_bytes,student_id)

                if response.server_content and response.server_content.interrupted:
                    logger.info("🤫 Student %s interrupted the AI tutor.", student_id)
                    await manager.send_json_message({"action": "stop_audio_playback"}, student_id)

                if response.tool_call:
                    logger.info("🎨 Gemini triggered whiteboard tool for student: %s", student_id)

                    await tools_handler(
                        student_id=student_id,
                        session=session,
                        tool_call=response.tool_call,
                        websocket=websocket
                    )
            except Exception as item_err:
                logger.error("Failed to process stream frame for student %s: %s", student_id, str(item_err))
                continue

    except asyncio.CancelledError:
        logger.info("Gemini stream receiver task safely cancelled for student %s.", student_id)
    except Exception as e:
        logger.error("❌ Error in AI response listener loop for student %s: %s", student_id, str(e))

        
"""




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






import asyncio
from google.genai.errors import APIError

try:
    response = await client.aio.models.generate_content(
        model='gemini-3.5-flash',
        contents=contents,
        config=final_parsed_config_to_call
    )
except APIError as e:
    if e.code == 503:
        print("Gemini server overloaded. Triggering local fallback...")
        # Insert your local static fallback definitions logic here
        response = get_local_fallback_content()
    else:
        # Handle other API errors (e.g., 400 Bad Request, 403 Invalid Key)
        raise e



TOOL_PROMPT = """
AVAILABLE WHITEBOARD TOOLS:

1. async_draw
   - Purpose: Create one geometric shape on the board.
   - Use for: rectangles, circles, triangles, diamonds, and other simple diagram blocks.
   - Inputs:
     - shape_id: stable unique id for the shape
     - shape: the visual shape type
     - x, y: top-left placement on the board
     - width, height: the shape size
   - Behavior: place the shape once, then let the frontend render it.

2. write_board
   - Purpose: Write text, labels, headings, formulas, and short explanations.
   - Use for: subject titles, date, subtopics, labels, definitions, short worked steps, and annotations.
   - Inputs:
     - text_id: stable unique id for the text block
     - text: the content to write
     - x, y: placement coordinates
     - text_size: font size if a specific size is needed
   - Behavior: keep the text block compact and readable.

3. move_item
   - Purpose: Move an existing item to a new position.
   - Use for: repositioning after layout adjustments.

4. adjust_item_size
   - Purpose: Resize an existing shape or text container.
   - Use for: making headings wider, formulas compact, or shapes fit the board.

5. delete_item
   - Purpose: Remove one specific item from the board.
   - Use for: corrections, clutter cleanup, or replacing a wrong block.

6. clear_whiteboard
   - Purpose: Remove all current board items.
   - Use for: starting a brand-new topic or resetting the working board.

7. draw_line
   - Purpose: Draw a straight line or curve connector.
   - Use for: arrows, relations, timelines, and process flow.

BOARD LAYOUT RULES:
- Treat the board as a fixed classroom whiteboard.
- Place the subject title at the top center.
- Place the date/session header at the top-left.
- Place subtopics underneath the title in reading order from top to bottom.
- Use short text blocks rather than long paragraphs.
- Use formulas and equations as separated working steps, not as dense prose.
- Keep every item within the visible board area and avoid oversized text blocks.
""".strip()
