

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




