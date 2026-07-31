import logging
import os
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, field_validator

from datetime import datetime, timedelta, timezone

#from .supabase_client import supabase_admin
from .supabase_client import get_supabase_admin, get_supabase_public
from .runtime import ensure_auth_flow_enabled
from .auth import verify_student_token

logger = logging.getLogger("KamaraLogger")

router = APIRouter(prefix="/api/v1")


def get_frontend_app_url() -> str:
    return os.getenv("FRONTEND_APP_URL", "http://localhost:5173").rstrip("/")


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
    access_token: str | None = None
    refresh_token: str | None = None
    code: str | None = None
    new_password: str

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, value):
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        return value


# this is for verifying email
class EmailVerification(BaseModel):
    token_hash : str


@router.post("/auth/signup")
async def process_signup(payload: SignupCredentials):
    ensure_auth_flow_enabled()
    logger.info("Attempting to register new student: %s", payload.email)
    
    first_name = f"{payload.first_name}".strip()
    last_name = f"{payload.last_name}".strip()

    try:
        supabase_public = get_supabase_public()
        auth_user = supabase_public.auth.sign_up(
            {
                "email": payload.email,
                "password": payload.password,
                "options": {
                    "data": {
                        "first_name": first_name,
                        "last_name": last_name,
                    },
                    "email_redirect_to": f"{get_frontend_app_url()}/login",
                },
            }
        )
    except Exception as e:
        logger.error("SUPABASE AUTH SIGNUP FAILED: %s: %s", type(e).__name__, str(e))
        raise HTTPException(
            status_code=400,
            detail=f"Supabase Auth signup failed: {str(e)}",
        )

    user = getattr(auth_user, "user", None)
    if not user:
        raise HTTPException(
            status_code=400,
            detail="Supabase signup did not return a user.",
        )

    student_id = user.id
    logger.info("Successfully registered user in auth.users. Assigned UUID: %s", student_id)

    try:
        supabase_admin = get_supabase_admin()
        supabase_admin.table("profiles").insert(
            {
                "id": student_id,
                "email": user.email,
                "first_name": first_name,
                "last_name": last_name
            }
        ).execute()


        trial_start = datetime.now(timezone.utc)
        trial_end = trial_start + timedelta(days=7)

        supabase_admin.table("subscriptions").insert({
            "user_id": student_id,
            "plan": "starter",
            "status": "trial",
            "trial_started_at": trial_start.isoformat(),
            "trial_ends_at": trial_end.isoformat()
        }).execute()


        
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
    ensure_auth_flow_enabled()

    supabase_public = get_supabase_public()
    try:
        session = supabase_public.auth.sign_in_with_password(
            {
                "email": payload.email,
                "password": payload.password,
            }
        )
        user_metadata = getattr(session.user, "user_metadata", None) or {}
        display_name = " ".join(
            part for part in [
                user_metadata.get("first_name", ""),
                user_metadata.get("last_name", ""),
            ]
            if part
        ).strip() or user_metadata.get("full_name", "") or session.user.email or "Student"
        return {
            "access_token": session.session.access_token,
            "user_id": session.user.id,
            "user": {
                "id": session.user.id,
                "email": session.user.email,
                "name": display_name,
                "full_name": display_name,
                "first_name": user_metadata.get("first_name", ""),
                "last_name": user_metadata.get("last_name", ""),
            },
        }
    except Exception as e:
        logger.error("SUPABASE AUTH LOGIN FAILED: %s", str(e))
        raise HTTPException(status_code=401, detail="Authentication failed.")


@router.get("/auth/me")
async def get_current_auth_user(current_user=Depends(verify_student_token)):
    ensure_auth_flow_enabled()
    student_id = current_user.id
    supabase_admin = get_supabase_admin()
# hello
    profile = {}
    try:
        profile_query = supabase_admin.table("profiles")\
            .select("email, first_name, last_name, avatar_url")\
            .eq("id", student_id)\
            .maybe_single()\
            .execute()
        profile = getattr(profile_query, "data", None) or {}
    except Exception as e:
        logger.warning("PROFILE LOOKUP FAILED FOR /auth/me: %s", str(e))

    metadata = getattr(current_user, "user_metadata", {}) or {}
    email = profile.get("email") or getattr(current_user, "email", "")
    first_name = profile.get("first_name") or metadata.get("first_name", "")
    last_name = profile.get("last_name") or metadata.get("last_name", "")
    full_name = profile.get("full_name") or metadata.get("full_name", "") or " ".join(
        part for part in [first_name, last_name] if part
    ).strip()

    return {
        "id": student_id,
        "email": email,
        "name": full_name or email or "Student",
        "full_name": full_name,
        "first_name": first_name,
        "last_name": last_name,
        "avatar_url": profile.get("avatar_url"),
    }
    



@router.post("/auth/forgot-password",status_code=status.HTTP_200_OK)
async def forgot_password(payload:ForgotPassword):
    ensure_auth_flow_enabled()
    clean_email = payload.email.strip().lower()
    logger.info("Password reset requested for: %s", clean_email)
    
    supabase_public = get_supabase_public()
    
    try:
        # Supabase will look up the email and send them a secure recovery link
        supabase_public.auth.reset_password_for_email(
            clean_email,
            options={
                # Tell Supabase where to redirect the user's browser when they click the email link
                "redirect_to": f"{get_frontend_app_url()}/update-password"
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
    ensure_auth_flow_enabled()
    logger.info("Attempting to process user password update.")
    
    # Crucial: use the user's recovery session, not the service role client.
    supabase = get_supabase_public()
    
    try:
        # 1. Authenticate the temporary session using the recovery link data.
        if payload.code:
            supabase.auth.exchange_code_for_session(payload.code)
        elif payload.access_token and payload.refresh_token:
            supabase.auth.set_session(payload.access_token, payload.refresh_token)
        else:
            raise HTTPException(
                status_code=400,
                detail="Missing recovery credentials from the password reset link.",
            )
        
        # 2. Update the user's password securely
        supabase.auth.update_user({"password": payload.new_password})
        
        logger.info("User password successfully updated in Supabase Auth.")
        return {
            "status": "success",
            "message": "Your password has been changed successfully! You can now log in with your new password."
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("PASSWORD UPDATE CRASH: %s", str(e))
        raise HTTPException(
            status_code=400,
            detail="Failed to update password. The link may have expired or is invalid."
        )










