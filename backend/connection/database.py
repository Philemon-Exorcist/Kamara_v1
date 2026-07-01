
import logging
from app.supabase_client import get_supabase_admin

logger = logging.getLogger("KamaraLogger")

async def fetch_complete_note(session_id: str, student_id: str) -> dict | None:
    """
    Uses the Supabase Python SDK to fetch the note details and joined 
    session attributes securely using a service-role admin client.
    """
    supabase = get_supabase_admin()
    
    try:
        #  Supabase Join syntax: Fetch library columns and traverse the foreign key 
        # to pull matching fields out of the parent 'sessions' table automatically
        response = (
            supabase.table("library")
            .select("title, body_text, sessions(course, user_prompt)")
            .eq("session_id", session_id)
            .eq("student_id", student_id)
            .limit(2)
            .execute()
        )
        
        # Validate data array contains an active matching row
        if not response or not response.data:
            return None
            
        record = response.data[0]
        parent_session = record.get("sessions", {})
        
        return {
            "course_subject": parent_session.get("course", "General Study"),
            "session_objective": parent_session.get("user_prompt", "Teach the current topic."),
            "note_title": record.get("title", "Untitled Module"),
            "note_content": record.get("body_text", "")
        }
        
    except Exception as e:
        logger.error(f"Supabase SDK connection lookup failed for session {session_id}: {str(e)}", exc_info=True)
        return None
