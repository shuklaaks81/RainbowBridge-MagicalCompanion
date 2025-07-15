"""
Main API routes for Rainbow Bridge
Contains all FastAPI endpoints and route handlers.
"""

from fastapi import FastAPI, HTTPException, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, Dict, Any, List
import json
import logging

from src.models.entities import Child, Routine, ChatResponse, APIResponse
from src.services.database import DatabaseService
from src.ai.assistant import AIAssistantService
from src.mcp.client import MCPClient
from src.services.routine_service import RoutineService
from config.settings import config

logger = logging.getLogger(__name__)


class APIRouter:
    """Main API router for Rainbow Bridge."""
    
    def __init__(self):
        self.app = FastAPI(
            title=config.app_name,
            description=config.description,
            version=config.version
        )
        
        # Initialize services
        self.db_service = DatabaseService()
        self.mcp_client = MCPClient(self.db_service)
        self.ai_assistant = AIAssistantService(self.db_service, self.mcp_client)
        self.routine_service = RoutineService(self.db_service, self.mcp_client)
        
        # Setup middleware
        self._setup_middleware()
        
        # Setup static files and templates
        self._setup_static_files()
        
        # Register routes
        self._register_routes()
    
    def _setup_middleware(self):
        """Setup CORS and other middleware."""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=config.api.cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    def _setup_static_files(self):
        """Setup static files and templates."""
        self.app.mount("/static", StaticFiles(directory="static"), name="static")
        self.templates = Jinja2Templates(directory="templates")
    
    def _register_routes(self):
        """Register all API routes."""
        
        # Health check
        @self.app.get("/health")
        async def health_check():
            return {"status": "healthy", "version": config.version}
        
        # Main page
        @self.app.get("/", response_class=HTMLResponse)
        async def home(request: Request):
            children = await self.db_service.get_all_children()
            return self.templates.TemplateResponse(
                "index.html", 
                {"request": request, "children": children}
            )
        
        # Child dashboard
        @self.app.get("/child/{child_id}", response_class=HTMLResponse)
        async def child_dashboard(request: Request, child_id: int):
            child = await self.db_service.get_child_profile(child_id)
            if not child:
                raise HTTPException(status_code=404, detail="Child not found")
            
            try:
                routines = await self.db_service.get_child_routines(child_id)
            except Exception as e:
                logger.error(f"Error fetching routines for child {child_id}: {e}")
                routines = []
            
            # Create default progress data
            progress = {
                "communication_score": 75,
                "routine_completion": 80,
                "social_skills": 65,
                "learning_progress": 70
            }
            
            return self.templates.TemplateResponse(
                "child_dashboard.html",
                {
                    "request": request,
                    "child": child,
                    "routines": routines,
                    "progress": progress
                }
            )
        
        # API Endpoints
        
        # Children endpoints
        @self.app.post("/api/child")
        async def create_child_profile(
            name: str = Form(...),
            age: int = Form(...),
            communication_level: str = Form(...),
            interests: str = Form(""),
            special_needs: str = Form(""),
            profile_picture: str = Form("default.svg")
        ):
            try:
                child_data = {
                    "name": name,
                    "age": age,
                    "communication_level": communication_level,
                    "interests": interests.split(",") if interests else [],
                    "special_needs": special_needs.split(",") if special_needs else [],
                    "profile_picture": profile_picture
                }
                
                child_id = await self.db_service.create_child_profile(child_data)
                return APIResponse(
                    success=True,
                    message="Child profile created successfully",
                    data={"child_id": child_id}
                )
                
            except Exception as e:
                logger.error(f"Error creating child profile: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/children")
        async def get_all_children():
            try:
                children = await self.db_service.get_all_children()
                return [
                    {
                        "id": child.id,
                        "name": child.name,
                        "age": child.age,
                        "communication_level": child.communication_level.value,
                        "created_at": child.created_at.isoformat() if child.created_at else None
                    }
                    for child in children
                ]
            except Exception as e:
                logger.error(f"Error fetching children: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/child/{child_id}")
        async def get_child_profile(child_id: int):
            try:
                child = await self.db_service.get_child_profile(child_id)
                if not child:
                    raise HTTPException(status_code=404, detail="Child not found")
                
                return {
                    "id": child.id,
                    "name": child.name,
                    "age": child.age,
                    "communication_level": child.communication_level.value,
                    "interests": child.interests,
                    "special_needs": child.special_needs,
                    "preferences": child.preferences,
                    "profile_picture": child.profile_picture,
                    "created_at": child.created_at.isoformat() if child.created_at else None
                }
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error fetching child profile: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        # Chat endpoint
        @self.app.post("/api/chat")
        async def chat(
            child_id: int = Form(...),
            message: str = Form(...),
            communication_type: str = Form("text")
        ):
            try:
                response = await self.ai_assistant.process_message(
                    child_id, message, communication_type
                )
                
                return {
                    "message": response.message,
                    "text": response.text,
                    "visual_cards": response.visual_cards,
                    "audio_response": response.audio_response,
                    "routine_action": response.routine_action,
                    "current_activity_context": response.current_activity_context,
                    "suggestions": response.suggestions
                }
                
            except Exception as e:
                logger.error(f"Error processing chat message: {e}")
                return {
                    "message": "I'm having trouble understanding right now. Let me try again! 🌈",
                    "text": "I'm having trouble understanding right now. Let me try again! 🌈",
                    "error": str(e)
                }
        
        # Routine endpoints
        @self.app.post("/api/routine")
        async def create_routine(
            child_id: int = Form(...),
            name: str = Form(...),
            activities: str = Form(...),  # JSON string of activity names
            schedule_time: str = Form(""),
            days_of_week: str = Form("")  # JSON string of days
        ):
            try:
                activity_names = json.loads(activities) if activities else []
                days = json.loads(days_of_week) if days_of_week else []
                
                routine = await self.routine_service.create_routine(
                    child_id, name, activity_names, schedule_time, days
                )
                
                return APIResponse(
                    success=True,
                    message="Routine created successfully",
                    data={"routine_id": routine.id}
                )
                
            except Exception as e:
                logger.error(f"Error creating routine: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/routine/{routine_id}")
        async def get_routine(routine_id: int):
            try:
                routine = await self.db_service.get_routine(routine_id)
                if not routine:
                    raise HTTPException(status_code=404, detail="Routine not found")
                
                return {
                    "id": routine.id,
                    "child_id": routine.child_id,
                    "name": routine.name,
                    "description": routine.description,
                    "activities": [
                        {
                            "id": activity.id,
                            "name": activity.name,
                            "description": activity.description,
                            "status": activity.status.value,
                            "completed_at": activity.completed_at.isoformat() if activity.completed_at else None
                        }
                        for activity in routine.activities
                    ],
                    "status": routine.status.value,
                    "current_activity_index": routine.current_activity_index,
                    "started_at": routine.started_at.isoformat() if routine.started_at else None,
                    "created_at": routine.created_at.isoformat() if routine.created_at else None
                }
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error fetching routine: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/routine/{routine_id}/status")
        async def get_routine_status(routine_id: int):
            try:
                return await self.routine_service.get_routine_status(routine_id)
                
            except Exception as e:
                logger.error(f"Error fetching routine status: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/api/routine/{routine_id}/start")
        async def start_routine(routine_id: int):
            try:
                success = await self.routine_service.start_routine(routine_id)
                
                return APIResponse(
                    success=success,
                    message="Routine started successfully" if success else "Failed to start routine"
                )
                
            except Exception as e:
                logger.error(f"Error starting routine: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/child/{child_id}/routines")
        async def get_child_routines(child_id: int):
            try:
                routines = await self.db_service.get_child_routines(child_id)
                
                return [
                    {
                        "id": routine.id,
                        "name": routine.name,
                        "status": routine.status.value,
                        "activities_count": len(routine.activities),
                        "progress_percentage": await self.routine_service.calculate_progress(routine.id),
                        "created_at": routine.created_at.isoformat() if routine.created_at else None
                    }
                    for routine in routines
                ]
                
            except Exception as e:
                logger.error(f"Error fetching child routines: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        # Progress and analytics endpoints
        @self.app.get("/api/child/{child_id}/progress")
        async def get_child_progress(child_id: int):
            try:
                # This would be implemented with more detailed analytics
                return {
                    "child_id": child_id,
                    "total_routines": 0,
                    "completed_routines": 0,
                    "total_activities": 0,
                    "completed_activities": 0,
                    "communication_improvements": {},
                    "recent_achievements": []
                }
                
            except Exception as e:
                logger.error(f"Error fetching progress: {e}")
                raise HTTPException(status_code=500, detail=str(e))
    
    def get_app(self) -> FastAPI:
        """Get the FastAPI application instance."""
        return self.app


# Create the router instance
router = APIRouter()
app = router.get_app()
