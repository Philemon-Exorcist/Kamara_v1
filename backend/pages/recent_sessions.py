
# get the previous session for a user  

from fastapi import HTTPException, Depends
from app.supabase_client import get_supabase_admin
from app.auth import verify_student_token
from app.routes import router, logger

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
            .select("id, course, user_prompt,created_at, helper_material_url")\
            .eq("student_id", student_uuid)\
            .order("created_at", desc=True)\
            .execute()
        # will add generated note later and how will gemini pickup from where it stopped
        sessions = []
        for row in db_query.data or []:
            sessions.append({
                **row,
                "subject": row.get("course"),
                "topic": row.get("user_prompt"),
                "course": row.get("course"),
                "user_prompt": row.get("user_prompt"),
               # "is_active": bool(row.get("generated_notes")),
            })
            
        return {
            "status": "success",
            "total_sessions": len(sessions),
            "sessions": sessions
        }
    except Exception as e:
        logger.error(f"❌ Failed to load historic sessions: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch workspace history.")
