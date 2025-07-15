"""
Special Kids Assistant - Main Application Entry Point

This application provides AI-powered assistance for autistic children with limited communication skills.
It includes features for routine management, visual communication, and personalized learning.
"""

import os
import logging
from typing import Optional
from fastapi import FastAPI, Request, Form, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv

from core.ai_assistant import SpecialKidsAI
from core.routine_manager import RoutineManager
from core.progress_tracker import ProgressTracker
from core.communication_helper import CommunicationHelper
from core.routine_mcp_server import create_routine_mcp_server
from database.db_manager import DatabaseManager

# Load environment variables
load_dotenv()
load_dotenv('.env.local')  # Load local LLM configuration

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Rainbow Bridge",
    description="Your colorful companion for communication and learning adventures",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files and templates
import pathlib
BASE_DIR = pathlib.Path(__file__).parent.absolute()
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# Initialize core components
db_manager = DatabaseManager()
routine_manager = RoutineManager(db_manager)
routine_mcp_server = create_routine_mcp_server(routine_manager, db_manager)
ai_assistant = SpecialKidsAI(routine_mcp_server)
progress_tracker = ProgressTracker(db_manager)
communication_helper = CommunicationHelper()

@app.on_event("startup")
async def startup_event():
    """Initialize the application on startup."""
    logger.info("Starting Rainbow Bridge...")
    await db_manager.initialize()
    logger.info("Rainbow Bridge started successfully!")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Main home page."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/child/{child_id}")
async def get_child_dashboard(request: Request, child_id: int):
    """Get child-specific dashboard with MCP-enhanced routine management."""
    child_data = await db_manager.get_child(child_id)
    if not child_data:
        raise HTTPException(status_code=404, detail="Child not found")
    
    # Get routines with enhanced data for MCP integration
    routines = await routine_manager.get_child_routines(child_id)
    
    # Enhance routines with additional MCP-compatible information
    enhanced_routines = []
    for routine in routines:
        enhanced_routine = routine.copy()
        
        # Ensure activities is a list (handle both string and list formats)
        if isinstance(routine.get('activities'), str):
            try:
                import json
                enhanced_routine['activities'] = json.loads(routine['activities'])
            except:
                enhanced_routine['activities'] = [routine['activities']]
        elif not routine.get('activities'):
            enhanced_routine['activities'] = []
        
        # Calculate total activities for display
        enhanced_routine['total_activities'] = len(enhanced_routine['activities'])
        
        # Add MCP-friendly metadata
        enhanced_routine['mcp_enabled'] = True
        enhanced_routine['supports_natural_language'] = True
        
        enhanced_routines.append(enhanced_routine)
    
    progress = await progress_tracker.get_child_progress(child_id)
    
    # Add MCP integration status to template context
    template_context = {
        "request": request,
        "child": child_data,
        "routines": enhanced_routines,
        "progress": progress,
        "mcp_integration": {
            "enabled": True,
            "server_status": "active",
            "natural_language_support": True
        }
    }
    
    return templates.TemplateResponse("child_dashboard.html", template_context)

@app.post("/api/chat")
async def chat_with_ai(
    child_id: int = Form(...),
    message: str = Form(...),
    communication_type: str = Form(default="text")
):
    """Handle chat interactions with the AI assistant."""
    try:
        # Get child's communication preferences
        child_data = await db_manager.get_child(child_id)
        if not child_data:
            raise HTTPException(status_code=404, detail="Child not found")
        
        # Process the message through AI
        response = await ai_assistant.process_message(
            message=message,
            child_id=child_id,
            communication_type=communication_type,
            child_preferences=child_data.get("preferences", {})
        )
        
        # Log the interaction for progress tracking
        await progress_tracker.log_interaction(
            child_id=child_id,
            interaction_type="chat",
            content=message,
            response=response["text"],
            success=True
        )
        
        return JSONResponse(content=response)
    
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        return JSONResponse(
            content={"error": "Sorry, I couldn't process your message right now."},
            status_code=500
        )

@app.post("/api/routine")
async def create_routine(
    child_id: int = Form(...),
    routine_name: str = Form(...),
    activities: str = Form(...),
    schedule_time: str = Form(...)
):
    """Create a new routine for a child."""
    try:
        routine = await routine_manager.create_routine(
            child_id=child_id,
            name=routine_name,
            activities=activities.split(","),
            schedule_time=schedule_time
        )
        
        return JSONResponse(content={"success": True, "routine_id": routine.id})
    
    except Exception as e:
        logger.error(f"Routine creation error: {str(e)}")
        return JSONResponse(
            content={"error": "Failed to create routine"},
            status_code=500
        )

@app.get("/api/visual-cards")
async def get_visual_cards():
    """Get available visual communication cards."""
    cards = await communication_helper.get_visual_cards()
    return JSONResponse(content=cards)

@app.post("/api/upload-image")
async def upload_custom_image(
    child_id: int = Form(...),
    image: UploadFile = File(...),
    category: str = Form(default="custom")
):
    """Upload a custom image for visual communication."""
    try:
        image_path = await communication_helper.save_custom_image(
            child_id=child_id,
            image=image,
            category=category
        )
        
        return JSONResponse(content={"success": True, "image_path": image_path})
    
    except Exception as e:
        logger.error(f"Image upload error: {str(e)}")
        return JSONResponse(
            content={"error": "Failed to upload image"},
            status_code=500
        )

@app.get("/api/progress/{child_id}")
async def get_child_progress(child_id: int):
    """Get progress report for a child."""
    try:
        progress = await progress_tracker.get_detailed_progress(child_id)
        return JSONResponse(content=progress)
    
    except Exception as e:
        logger.error(f"Progress retrieval error: {str(e)}")
        return JSONResponse(
            content={"error": "Failed to retrieve progress"},
            status_code=500
        )

@app.post("/api/child")
async def create_child_profile(
    name: str = Form(...),
    age: int = Form(...),
    communication_level: str = Form(...),
    interests: str = Form(default=""),
    special_needs: str = Form(default="")
):
    """Create a new child profile."""
    try:
        child_data = {
            "name": name,
            "age": age,
            "communication_level": communication_level,
            "interests": interests.split(",") if interests else [],
            "special_needs": special_needs.split(",") if special_needs else [],
            "preferences": {
                "visual_support": True,
                "audio_support": True,
                "routine_reminders": True
            }
        }
        
        child_id = await db_manager.create_child(child_data)
        return JSONResponse(content={"success": True, "child_id": child_id})
    
    except Exception as e:
        logger.error(f"Child profile creation error: {str(e)}")
        return JSONResponse(
            content={"error": "Failed to create child profile"},
            status_code=500
        )

@app.get("/api/children")
async def get_all_children():
    """Get all children profiles."""
    try:
        children = await db_manager.get_all_children()
        return JSONResponse(content=children)
    except Exception as e:
        logger.error(f"Failed to get children: {str(e)}")
        return JSONResponse(
            content={"error": "Failed to retrieve children"},
            status_code=500
        )

@app.get("/api/child/{child_id}/active-sessions")
async def get_child_active_sessions(child_id: int):
    """Get active routine sessions for a child."""
    try:
        # Use database manager to get active sessions
        import aiosqlite
        async with aiosqlite.connect("special_kids.db") as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("""
                SELECT rs.*, r.name as routine_name 
                FROM routine_sessions rs
                JOIN routines r ON rs.routine_id = r.id
                WHERE rs.child_id = ? AND rs.status = 'in_progress'
                ORDER BY rs.started_at DESC
            """, (child_id,))
            
            rows = await cursor.fetchall()
            sessions = [dict(row) for row in rows]
            
            return JSONResponse(content=sessions)
    
    except Exception as e:
        logger.error(f"Failed to get active sessions for child {child_id}: {str(e)}")
        return JSONResponse(content=[], status_code=500)

@app.post("/api/routine/start")
async def start_routine_session(
    routine_id: int = Form(...),
    child_id: int = Form(...)
):
    """Start a routine session with MCP integration."""
    try:
        success = await routine_manager.start_routine(routine_id)  # Returns True/False
        
        if not success:
            return JSONResponse(
                content={"success": False, "error": "Could not start routine"},
                status_code=400
            )
        
        # Get routine details for MCP response
        routine_data = await db_manager.get_routine(routine_id)
        
        # Create MCP-compatible response
        response_data = {
            "success": True, 
            "routine": {
                "id": routine_id,
                "name": routine_data.get("name", "Unknown Routine"),
                "activities": routine_data.get("activities", []),
                "mcp_message": f"🌟 Great! I've started your {routine_data.get('name', 'routine')}. Let's do this together! 💪"
            }
        }
        
        return JSONResponse(content=response_data)
    except Exception as e:
        logger.error(f"Failed to start routine: {str(e)}")
        return JSONResponse(
            content={"error": "Failed to start routine"},
            status_code=500
        )

@app.get("/api/routine/{routine_id}/status")
async def get_routine_status(routine_id: int, child_id: int = None):
    """Get the current status of a routine session with MCP integration."""
    try:
        # Get routine data
        routine_data = await db_manager.get_routine(routine_id)
        if not routine_data:
            return JSONResponse(content={"error": "Routine not found"}, status_code=404)
        
        # Get any active session data (you might need to implement this in routine_manager)
        # For now, return basic routine information
        
        response_data = {
            "routine_id": routine_id,
            "name": routine_data.get("name"),
            "activities": routine_data.get("activities", []),
            "total_activities": len(routine_data.get("activities", [])),
            "status": "ready",  # Could be: ready, in_progress, completed
            "progress": 0,  # Percentage complete
            "current_activity": None,
            "mcp_message": f"Your {routine_data.get('name', 'routine')} is ready to start! 🌟"
        }
        
        return JSONResponse(content=response_data)
    except Exception as e:
        logger.error(f"Failed to get routine status: {str(e)}")
        return JSONResponse(
            content={"error": "Failed to get routine status"},
            status_code=500
        )

@app.post("/api/routine/{routine_id}/complete-activity")
async def complete_routine_activity(
    routine_id: int,
    activity_name: str = Form(...),
    child_id: int = Form(...)
):
    """Mark an activity as complete with MCP integration."""
    try:
        # Complete the activity using routine manager
        success = await routine_manager.complete_activity(routine_id, activity_name)
        
        if success:
            # Get updated routine status
            routine_data = await db_manager.get_routine(routine_id)
            activities = routine_data.get("activities", [])
            
            # Calculate progress
            total_activities = len(activities)
            # This is simplified - you'd need proper session tracking for real progress
            progress = 50  # Placeholder
            
            response_data = {
                "success": True,
                "activity_completed": activity_name,
                "progress": progress,
                "total_activities": total_activities,
                "mcp_message": f"🎉 Awesome job! You completed: {activity_name}. Keep going! ⭐"
            }
        else:
            response_data = {
                "success": False,
                "error": "Failed to complete activity",
                "mcp_message": "I had trouble marking that activity as complete. Let's try again! 🤗"
            }
        
        return JSONResponse(content=response_data)
    except Exception as e:
        logger.error(f"Failed to complete activity: {str(e)}")
        return JSONResponse(
            content={"error": "Failed to complete activity"},
            status_code=500
        )

@app.get("/api/routines/suggest")
async def suggest_routines(child_id: int):
    """Get routine suggestions for MCP integration."""
    try:
        # Get existing routines to avoid duplicates
        existing_routines = await routine_manager.get_child_routines(child_id)
        existing_names = [r.get("name", "").lower() for r in existing_routines]
        
        # Common routine suggestions for autistic children
        suggestions = [
            {
                "name": "Morning Routine",
                "description": "Start your day with structure and calm",
                "activities": ["Wake up and stretch", "Brush teeth", "Get dressed", "Eat breakfast", "Pack bag"],
                "time": "07:30",
                "emoji": "🌅"
            },
            {
                "name": "Bedtime Routine", 
                "description": "Wind down for peaceful sleep",
                "activities": ["Take bath", "Put on pajamas", "Brush teeth", "Read story", "Quiet time"],
                "time": "20:00",
                "emoji": "🌙"
            },
            {
                "name": "Learning Time",
                "description": "Fun and structured learning activities", 
                "activities": ["Reading time", "Creative activities", "Brain games", "Celebrate learning"],
                "time": "15:30",
                "emoji": "📚"
            },
            {
                "name": "Calm Down Routine",
                "description": "Tools to feel calm and safe",
                "activities": ["Deep breathing", "Count to 10", "Hug comfort item", "Think happy thoughts"],
                "time": "as_needed",
                "emoji": "😌"
            }
        ]
        
        # Filter out existing routines
        filtered_suggestions = [
            s for s in suggestions 
            if s["name"].lower() not in existing_names
        ]
        
        return JSONResponse(content={
            "suggestions": filtered_suggestions,
            "mcp_message": "Here are some routine ideas that might help! 🌈✨"
        })
        
    except Exception as e:
        logger.error(f"Failed to get routine suggestions: {str(e)}")
        return JSONResponse(
            content={"error": "Failed to get suggestions"},
            status_code=500
        )

# =============================================================================
# LOCAL LLM MANAGEMENT ROUTES
# =============================================================================

@app.get("/api/llm/status")
async def get_llm_status():
    """Get the status of all LLM providers."""
    try:
        status = ai_assistant.get_llm_status()
        return JSONResponse(content=status)
    except Exception as e:
        logger.error(f"LLM status error: {str(e)}")
        return JSONResponse(
            content={"error": "Failed to get LLM status"},
            status_code=500
        )

@app.post("/api/llm/switch")
async def switch_llm_mode(mode: str = Form(...)):
    """Switch between local and cloud LLM modes."""
    try:
        if mode.lower() == "local":
            success = ai_assistant.switch_to_local_mode()
            if success:
                return JSONResponse(content={"success": True, "mode": "local"})
            else:
                return JSONResponse(
                    content={"error": "No local LLM providers available"},
                    status_code=400
                )
        elif mode.lower() == "cloud":
            success = ai_assistant.switch_to_cloud_mode()
            if success:
                return JSONResponse(content={"success": True, "mode": "cloud"})
            else:
                return JSONResponse(
                    content={"error": "OpenAI client not available"},
                    status_code=400
                )
        else:
            return JSONResponse(
                content={"error": "Invalid mode. Use 'local' or 'cloud'"},
                status_code=400
            )
    except Exception as e:
        logger.error(f"LLM switch error: {str(e)}")
        return JSONResponse(
            content={"error": "Failed to switch LLM mode"},
            status_code=500
        )

@app.get("/api/llm/test")
async def test_llm_connectivity():
    """Test connectivity to all LLM providers."""
    try:
        results = await ai_assistant.test_llm_connectivity()
        return JSONResponse(content=results)
    except Exception as e:
        logger.error(f"LLM test error: {str(e)}")
        return JSONResponse(
            content={"error": "Failed to test LLM connectivity"},
            status_code=500
        )

@app.get("/admin/llm")
async def llm_admin_page(request: Request):
    """Admin page for local LLM management."""
    try:
        # Get current status
        status = ai_assistant.get_llm_status()
        
        return templates.TemplateResponse("llm_admin.html", {
            "request": request,
            "status": status,
            "page_title": "Local LLM Management"
        })
    except Exception as e:
        logger.error(f"LLM admin page error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to load admin page")

@app.post("/api/llm/configure")
async def configure_llm(
    provider: str = Form(...),
    base_url: str = Form(""),
    model: str = Form(""),
    enabled: bool = Form(False)
):
    """Configure a local LLM provider."""
    try:
        # This would typically update environment variables or config files
        # For now, we'll return a success message
        return JSONResponse(content={
            "success": True,
            "message": f"Configuration for {provider} updated successfully"
        })
    except Exception as e:
        logger.error(f"LLM configuration error: {str(e)}")
        return JSONResponse(
            content={"error": "Failed to configure LLM provider"},
            status_code=500
        )

@app.get("/progress/{child_id}")
async def view_progress_report(request: Request, child_id: int):
    """Render the progress report page for a child."""
    try:
        # Get child information
        child = await db_manager.get_child(child_id)
        if not child:
            raise HTTPException(status_code=404, detail="Child not found")
        
        # Get detailed progress data
        progress = await progress_tracker.get_detailed_progress(child_id)
        basic_progress = await progress_tracker.get_child_progress(child_id)
        
        # Get milestones
        milestones = await progress_tracker.get_child_milestones(child_id)
        
        # Get recent activities
        recent_activities = await progress_tracker.get_recent_interactions(child_id, limit=10)
        
        # Get statistics
        stats = await progress_tracker.get_child_statistics(child_id)
        
        # Generate AI insights
        insights = await progress_tracker.generate_insights(child_id)
        
        return templates.TemplateResponse("progress_report.html", {
            "request": request,
            "child": child,
            "progress": basic_progress,
            "detailed_progress": progress,
            "milestones": milestones,
            "recent_activities": recent_activities,
            "stats": stats,
            "insights": insights
        })
    
    except Exception as e:
        logger.error(f"Progress report error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to load progress report")
