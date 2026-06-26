
import json
from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from .supabase_client import supabase_admin
from .auth import verify_student_token
from .routes import logger, router
from pydantic import BaseModel
from ..kamara.writer.writer import syllabus_designer
from google.adk.runners import Runner
#  what is inmemory runner and when to use





class StartSessionPayload(BaseModel):
    subject: str  # e.g., "Maths"
    topic: str    # e.g., "Linear Algebra"

class PrepareSessionPayload(BaseModel):
    session_id: UUID

# will figure out what this is for
class UserChatPrompt(BaseModel):
    session_id: UUID
    message: str


# ==========================================================================
# 🚀 STEP 1: INITIAL WORKSPACE CONTAINER INITIALIZATION
# ==========================================================================
@router.post("/sessions/start", status_code=status.HTTP_201_CREATED)
async def start_learning_session(payload: StartSessionPayload, user=Depends(verify_student_token)):
    """
    PHASE 1: Triggered when the student selects a subject and topic on the UI.
    Initializes a blank, parent session row container inside Supabase.
    """
    student_uuid = user.id
    logger.info(f"🚀 Initializing fresh {payload.subject} container for: '{payload.topic}'")
    
    try:
        # Insert the core structural parent row. Supabase auto-generates a clean UUIDv4!
        session_db = supabase_admin.table("sessions").insert({
            "student_id": student_uuid,
            "subject": payload.subject,
            "topic": payload.topic,
            "generated_notes": "" # Initialized as empty text, will be populated during preparation
        }).execute()
        
        if not session_db.data or len(session_db.data) == 0:
            raise ValueError("Database failed to initialize the workspace tracking row.")
            
        new_session = session_db.data[0]
        session_uuid = new_session["id"]
        
        logger.info(f"⚡ Success: Blank workspace initialized. Assigned Session UUIDv4: {session_uuid}")
        return {
            "status": "started",
            "session_id": session_uuid,
            "topic": payload.topic,
            "subject": payload.subject
        }
        
    except Exception as e:
        logger.error(f"❌ SESSION START CRASHED: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initialize a new learning session workspace container."
        )


# ==========================================================================
# ⏳ STEP 2: REASEARCH & PREPARE SYLLABUS (Writer Agent Core)
# ==========================================================================
@router.post("/sessions/prepare", status_code=status.HTTP_200_OK)
async def prepare_modules_and_textbook(payload: PrepareSessionPayload, user=Depends(verify_student_token)):
    """
    PHASE 2: Automatically triggered right after the session starts.
    Runs the asynchronous Writer Agent to research Google and compile the syllabus and notes.
    """
    student_uuid = user.id
    session_str = str(payload.session_id)
    logger.info(f"⏳ Async Writer Agent processing started for Workspace Session: {session_str}")
    
    try:
        # A. Fetch the original metadata from the database to give context to our prompt
        current_session = supabase_admin.table("sessions")\
            .select("subject, topic")\
            .eq("id", session_str)\
            .eq("student_id", student_uuid)\
            .single()\
            .execute()
            
        if not current_session.data:
            raise HTTPException(status_code=404, detail="Workspace container mismatch or not found.")
            
        subject = current_session.data["subject"]
        topic = current_session.data["topic"]

        # B. Boot the Google ADK Agent Runner for the Writer Agent
        logger.info("🤖 Launching Async [SyllabusDesigner Agent] to execute tool research...")
        runner = Runner(agent=syllabus_designer)
        
        ai_prompt = f"Compile a complete academic learning syllabus breakdown and textbook handout for the topic: '{topic}' under the subject: '{subject}'."
        
        # Await the asynchronous AI generation pipeline (Google Search + Synthesis)
        ai_result = await runner.run_async(prompt=ai_prompt, session_id=session_str)
        logger.info("✨ Success: Writer Agent completed research and data synthesis.")

        # C. Parse the structured response schema fields out of Gemini's JSON
        structured_data = json.loads(ai_result.text)
        generated_modules = structured_data.get("modules", [])
        textbook_notes = structured_data.get("textbook_handout_notes", "")

        # D. Save the compiled textbook notes string back to the parent sessions row
        supabase_admin.table("sessions").update({
            "generated_notes": textbook_notes
        }).eq("id", session_str).execute()
        logger.info("📝 Master textbook notes stored safely inside public.sessions table.")

        # E. Bulk-insert the dynamic curriculum nodes into public.modules table rows
        module_rows = [
            {
                "session_id": session_str,
                "sub_topic": item["sub_topic"],
                "sort_order": index, # Sequenced 1, 2, 3...
                "teaching_guidelines": item["teaching_guidelines"],
                "is_completed": False
            } for index, item in enumerate(generated_modules, start=1)
        ]
        
        if module_rows:
            supabase_admin.table("modules").insert(module_rows).execute()
            logger.info(f"📈 Sync complete. Saved {len(module_rows)} lesson units to public.modules table.")

        # Return everything back to React so the UI can render the syllabus roadmap review card
        return {
            "status": "prepared",
            "session_id": session_str,
            "topic": topic,
            "syllabus_preview": [m["sub_topic"] for m in module_rows]
        }
        
    except Exception as e:
        if isinstance(e, HTTPException): raise e
        logger.error(f"❌ ASYNC PREPARATION FAILURE: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Failed to compile course roadmap: {str(e)}"
        )
