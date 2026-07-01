
import time
import logging
import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.supabase_client import SUPABASE_KEY_ROLE, SUPABASE_PROJECT_URL
from app.routes import router
from app import dashboard as dashboard_routes
from app.waitlist import waitlist_router
from connection.websocket import socket_router
from pages.profile import profile_router
from pages.dashboard import dashboard_router
from pages.courses import course_router


# 1. Initialize Python's built-in logging tool formatting style
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("KamaraLogger")


# check if the frontend can send raw audio and if it is also configured to receive audio
app = FastAPI(title="AI Agentic Microservice")

# Cross-Origin resource allowances so React client can fetch records securely
app.add_middleware(
    CORSMiddleware,
   # allow_origins=[
      #  "http://localhost:3000",
      #  "http://127.0.0.1:3000",
       # "http://localhost:5173",
       # "http://127.0.0.1:5173",
       # "http://localhost:5174",
       # "http://127.0.0.1:5174",
   # ],
    allow_origins=["*"],  # 👈 For development, we allow all origins. Lock this down in production!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 2. Add the Global Tracking Middleware Interceptor
@app.middleware("http")
async def log_incoming_requests(request: Request, call_next):
    # This block executes the moment React flings a packet over the network
    start_time = time.time()
    
    logger.info(f"🚀 INCOMING REQUEST: {request.method} -> {request.url.path}")
    
    # Process the request and proceed to your routes
    response = await call_next(request)
    
    # This block executes right before sending data back to React
    process_time = (time.time() - start_time) * 1000
    logger.info(f"✅ COMPLETED REQUEST: {request.method} -> {request.url.path} | Status: {response.status_code} | Time: {process_time:.2f}ms\n")
    
    return response




# 🚨 ADD THIS GET REQUEST CONFIRMATION ROUTE HERE:
@app.get("/")
@app.get("/health")
@app.get("/health-check")
@app.get("/api/v1/health-check")
async def health_check():
    """ A completely open public GET endpoint that returns a test dictionary """
    return {
        "status": "online",
        "message": "FastAPI is working perfectly!",
        "server_status": "healthy"
    }


@app.get("/api/v1/debug/config")
async def debug_config():
    return {
        "supabase_url": SUPABASE_PROJECT_URL,
        "supabase_key_role": SUPABASE_KEY_ROLE,
        "has_gemini_api_key": bool(os.getenv("GEMINI_API_KEY")),
        "cloud_run_service": os.getenv("K_SERVICE"),
    }


app.include_router(router)
app.include_router(waitlist_router)
app.include_router(profile_router)
app.include_router(dashboard_router)
app.include_router(course_router)
app.include_router(socket_router) # websocket router

if __name__ == "__main__":
    import uvicorn
    import os

    # 1. Fall back to 8001 locally, but let Cloud Run or Render inject the proper port
    port = int(os.environ.get("PORT", 8001))
    
    # 2. Check for Google Cloud Run (K_SERVICE) or Render (RENDER) production tokens
    is_cloud_run = os.environ.get("K_SERVICE") is not None
    is_render = os.environ.get("RENDER") is not None
    
    # 3. Disable reload if the app detects either production environment
    if is_cloud_run or is_render:
        reload_setting = False
    else:
        reload_setting = True

    print(f"Booting server on port {port} | Production Mode: {is_cloud_run or is_render}")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=reload_setting)


"""
if __name__ == "__main__":
    import uvicorn
    import os

    # Get the port from Render's environment, or default to 8001 for local development
    port = int(os.environ.get("PORT", 8001))
    
    # Turn off reload in production (Render), keep it on for local development
    is_production = os.environ.get("RENDER") is not None
    reload_setting = False if is_production else True

    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=reload_setting)
"""
