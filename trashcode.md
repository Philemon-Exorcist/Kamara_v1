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

