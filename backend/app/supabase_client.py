

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




