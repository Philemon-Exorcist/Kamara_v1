import logging
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr, field_validator
#from .supabase_client import supabase_admin
from .supabase_client import get_supabase_admin

logger = logging.getLogger("KamaraLogger")
waitlist_router = APIRouter(prefix="/api/v1")

# 1. Pydantic schema validation for incoming text fields
class WaitlistSubmission(BaseModel):
    email: EmailStr
    full_name: str

    @field_validator('full_name')
    @classmethod
    def clean_name(cls, value: str) -> str:
        if not value.strip():
            raise ValueError('Name field cannot be left blank.')
        return value.strip()


# 2. Optimized Single POST Endpoint
@waitlist_router.post("/waitlist/join", status_code=status.HTTP_201_CREATED)
async def join_waitlist_pipeline(payload: WaitlistSubmission):
    # Clean the string inputs to prevent case-sensitive bypasses
    clean_email = payload.email.strip().lower()
    
    logger.info(f"📋 Waitlist request received for: {clean_email}")
    supabase_admin = get_supabase_admin()
    
    try:
        # Step A: Query Supabase to see if this exact email exists in the waitlist table
        duplicate_check = supabase_admin.table("waitlist")\
            .select("id")\
            .eq("email", clean_email)\
            .execute()

        # 🚨 THE LOGIC GATE: If the array has data, they are already on the list!
        if duplicate_check and hasattr(duplicate_check, 'data') and duplicate_check.data:
            logger.info(f"🤝 Handled existing user: '{clean_email}' tried to join again.")
            return {
                "status": "already_joined",
                "message": "You have already joined the waitlist! We will notify you as soon as a slot opens up."
            }
        
        # Step B: Write directly to the PostgreSQL database table
        #  we DO NOT pass "id" or "userid" here anymore. 
        # PostgreSQL will automatically increment the 'id' and handle 'created_at'.
        supabase_admin.table("waitlist").insert({
            "email": clean_email,
            "full_name": payload.full_name
        }).execute()

        logger.info(f"🎉 Success: Added '{clean_email}' to the waitlist rows.")
        return {
            "status": "success",
            "message": "Awesome! You have successfully secured your spot on the Kamara AI waitlist."
        }
        
    except Exception as e:
        logger.error(f"❌ WAITLIST ENGINE FAILURE: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process your waitlist entry. Please try again later."
        )




"""

import logging

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr, field_validator
from .supabase_client import supabase_admin

logger = logging.getLogger("KamaraLogger")
waitlist_router = APIRouter(prefix="/api/v1")

# 1. Pydantic schema validation for incoming text fields
class WaitlistSubmission(BaseModel):
    email: EmailStr
    full_name: str

    @field_validator('full_name')
    @classmethod
    def clean_name(cls, value: str) -> str:
        if not value.strip():
            raise ValueError('Name field cannot be left blank.')
        return value.strip()


# 2. Optimized Single POST Endpoint
@waitlist_router.post("/waitlist/join", status_code=status.HTTP_201_CREATED)
async def join_waitlist_pipeline(payload: WaitlistSubmission):
    # Clean the string inputs to prevent case-sensitive bypasses
    clean_email = payload.email.strip().lower()
    
    logger.info(f"📋 Waitlist request received for: {clean_email}")
    
    try:
        # Step A: Query Supabase to see if this exact email exists
        duplicate_check = supabase_admin.table("waitlist")\
            .select("id")\
            .eq("email", clean_email)\
            .execute()

        # 🚨 THE LOGIC GATE: If the array has data, they are already on the list!
        if duplicate_check and hasattr(duplicate_check, 'data') and duplicate_check.data:
            logger.info(f"🤝 Handled existing user: '{clean_email}' tried to join again.")
            return {
                "status": "already_joined",
                "message": "You have already joined the waitlist! We will notify you as soon as a slot opens up."
            }
        
        # waitlist user, should this be like this
        waitlist_user = supabase_admin.auth.admin.create_user({
                "email" : clean_email,
                "user_metadata" : {
                    "full_name": payload.full_name
                }
            })
        
        student_id = waitlist_user.user.id

        # Step B: If the array is empty, write them to the PostgreSQL database table
        insert_result = supabase_admin.table("waitlist").insert({
            "id" : student_id, 
            "email": clean_email,
            "full_name": payload.full_name
        }).execute()


        logger.info(f"🎉 Success: Added '{clean_email}' to the waitlist rows.")
        return {
            "status": "success",
            "message": "Awesome! You have successfully secured your spot on the Kamara AI waitlist."
        }
        
    except Exception as e:
        logger.error(f"❌ WAITLIST ENGINE FAILURE: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail="Failed to process your waitlist entry. Please try again later."
        )



"""