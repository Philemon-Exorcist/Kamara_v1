from fastapi import APIRouter, HTTPException, Depends
from uuid import UUID
from .supabase_client import supabase_admin
from .auth import verify_student_token
from .routes import logger, router




@router.get("/library/handouts")
async def get_all_student_handouts(user=Depends(verify_student_token)):
    """
    🔐 SECURE LIBRARY ENDPOINT: Fetches every single markdown textbook note 
    compiled by Kamara AI for the logged-in student across all past sessions.
    """
    student_uuid = user.id
    logger.info(f"📚 Library catalog requested by student UUID: {student_uuid}")
    
    try:
        # Fetch sessions belonging to this user that actually have notes generated
        db_query = supabase_admin.table("sessions")\
            .select("id, subject, topic, generated_notes, created_at")\
            .eq("student_id", student_uuid)\
            #.not.is_("generated_notes", "null")\
            .not.is("generated_notes", "null")\
            .order("created_at", desc=True)\
            .execute()
            
        return {
            "status": "success",
            "total_books": len(db_query.data),
            "handouts": db_query.data
        }
    except Exception as e:
        logger.error(f"❌ LIBRARY ENDPOINT CRASHED: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to load your personal AI library.")


# levels