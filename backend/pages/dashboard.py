
import logging
from fastapi import HTTPException,status,APIRouter,Depends
from pydantic import BaseModel
from typing import List, Dict, Any
from app.supabase_client import get_supabase_admin
from app.auth import verify_student_token

logger = logging.getLogger("KamaraLogger")
dashboard_router = APIRouter(prefix="/api/v1/pages", tags=["Dashboard Page"])

# 1. Define the clean data structures for our dashboard dashboard components
class StudyStats(BaseModel):
    hours_studied: float
    questions_asked: int
    average_score: int

class RecentActivity(BaseModel):
    id: str
    type: str  # e.g., "chat", "exam", "upload"
    title: str
    timestamp: str

class DashboardResponse(BaseModel):
    full_name: str
    plan_tier: str
    stats: StudyStats
    recent_activity: List[RecentActivity]
    recommended_topics: List[str]

@dashboard_router.get("/dashboard", response_model=DashboardResponse)
async def get_student_dashboard_view(current_user: dict = Depends(verify_student_token)):
    """
    Page-driven endpoint combining real identity tracking with high-fidelity 
    mocked performance data to build a complete dashboard experience for React.
    """
    student_id = current_user.id
    logger.info("Assembling core dashboard components for student UUID: %s", student_id)
    
    supabase = get_supabase_admin()
    
    try:
        # Step A: Fetch real user metadata from profiles
        profile_query = supabase.table("profiles")\
            .select("full_name")\
            .eq("id", student_id)\
            .maybe_single()\
            .execute()
            
        full_name = "Student"
        if profile_query and getattr(profile_query, 'data', None):
            full_name = profile_query.data.get("full_name", "Student")

        plan_tier = "starter"
        try:
            # Optional table: some deployments do not have subscription tracking yet.
            sub_query = supabase.table("subscriptions")\
                .select("plan_tier")\
                .eq("user_id", student_id)\
                .maybe_single()\
                .execute()

            if sub_query and getattr(sub_query, 'data', None):
                plan_tier = sub_query.data.get("plan_tier", "starter")
        except Exception as subscription_error:
            logger.warning("Subscription lookup skipped for dashboard: %s", str(subscription_error))

        # 🌟 Step C: High-Fidelity Mock Values (Swapped for database queries later!)
        mock_stats = {
            "hours_studied": 12.5,
            "questions_asked": 34,
            "average_score": 78
        }
        
        mock_activity = [
            {
                "id": "act_001",
                "type": "chat",
                "title": "Interrogated AI Tutor regarding Organic Chemistry mechanisms",
                "timestamp": "2 hours ago"
            },
            {
                "id": "act_002",
                "type": "upload",
                "title": "Uploaded PHY 102 Lecture_Note_Week3.pdf",
                "timestamp": "Yesterday"
            },
            {
                "id": "act_003",
                "type": "exam",
                "title": "Completed Mock Quiz: Introduction to Computer Science",
                "timestamp": "3 days ago"
            }
        ]
        
        mock_recommendations = [
            "Review weak areas in Calculus derivatives before your test",
            "Generate a fresh Mock Exam for GST 101 basic grammar principles",
            "Continue your conversation with the AI Tutor on Thermodynamics"
        ]

        # Step D: Package and return everything to the client
        return {
            "full_name": full_name,
            "plan_tier": plan_tier,
            "stats": mock_stats,
            "recent_activity": mock_activity,
            "recommended_topics": mock_recommendations
        }

    except Exception as e:
        logger.error("❌ DASHBOARD GENERATION CRASH: %s", str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initialize dashboard parameters. Please try again later."
        )
