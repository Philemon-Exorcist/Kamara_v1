# backend/app/routes.py
from fastapi import HTTPException, Depends
from .supabase_client import get_supabase_admin
from .auth import verify_student_token
from .routes import router, logger





# ==========================================================================
# 📊 ENDPOINT 1: FETCH DASHBOARD PROFILE DETAILS
# ==========================================================================

@router.get("/dashboard/profile")
async def get_user_profile_details(user=Depends(verify_student_token)):
    """
    🔐 SECURE ENDPOINT: Fetches the personal profile data of the logged-in user.
    """
    student_uuid = user.id
    supabase_admin = get_supabase_admin()
    logger.info(f"👤 Profile request received for student UUID: {student_uuid}")
    
    try:
        # Query public.profiles table filtering strictly by the user's token UUID
        db_query = supabase_admin.table("profiles")\
            .select("id, email, full_name, created_at")\
            .eq("id", student_uuid)\
            .single()\
            .execute()
            
        if not db_query.data:
            raise HTTPException(status_code=404, detail="Profile record not found.")
            
        return {
            "status": "success",
            "profile": db_query.data
        }
    except Exception as e:
        logger.error(f"❌ Failed to retrieve profile matrix: {str(e)}")
        raise HTTPException(status_code=500, detail="Could not retrieve profile info.")


# ==========================================================================
# 📂 ENDPOINT 2: FETCH PREVIOUS WHITEBOARD SESSIONS
# ==========================================================================

@router.get("/dashboard/sessions")
async def get_user_historical_sessions(user=Depends(verify_student_token)):
    """
    🔐 SECURE ENDPOINT: Lists previous learning workspaces belonging ONLY to this student.
    Used by React to populate the 'Reload History' sidebar menu.
    """
    student_uuid = user.id
    supabase_admin = get_supabase_admin()
    logger.info(f"📂 Session log history requested for user: {student_uuid}")
    
    try:
        # Fetch matching whiteboard sessions ordered by newest first
        db_query = supabase_admin.table("sessions")\
            .select("id, subject, topic, generated_notes, created_at")\
            .eq("student_id", student_uuid)\
            .order("created_at", desc=True)\
            .execute()
            
        return {
            "status": "success",
            "total_sessions": len(db_query.data),
            "sessions": db_query.data
        }
    except Exception as e:
        logger.error(f"❌ Failed to load historic sessions: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch workspace history.")








