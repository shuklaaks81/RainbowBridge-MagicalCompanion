"""
Routine service for Rainbow Bridge
Handles routine management, creation, and execution logic.
"""

import logging
from datetime import datetime, time
from typing import List, Dict, Any, Optional

from src.models.entities import (
    Routine, Activity, RoutineStatus, ActivityStatus,
    RoutineStatusResponse
)
from src.services.database import DatabaseService
from src.mcp.client import MCPClient

logger = logging.getLogger(__name__)


class RoutineService:
    """Service for managing routines and activities."""
    
    def __init__(self, database_service: DatabaseService, mcp_client: MCPClient):
        self.db = database_service
        self.mcp_client = mcp_client
    
    async def create_routine(
        self,
        child_id: int,
        name: str,
        activity_names: List[str],
        schedule_time: str = "",
        days_of_week: List[str] = None
    ) -> Routine:
        """Create a new routine with activities."""
        
        try:
            # Create activities
            activities = []
            for i, activity_name in enumerate(activity_names):
                activity = Activity(
                    name=activity_name.strip(),
                    description=f"Activity: {activity_name.strip()}",
                    estimated_duration=5,
                    status=ActivityStatus.NOT_STARTED
                )
                activities.append(activity)
            
            # Parse schedule time
            parsed_time = None
            if schedule_time:
                try:
                    parsed_time = datetime.strptime(schedule_time, "%H:%M").time()
                except ValueError:
                    logger.warning(f"Invalid time format: {schedule_time}")
            
            # Create routine
            routine = Routine(
                child_id=child_id,
                name=name,
                description=f"Routine for {name}",
                activities=activities,
                schedule_time=parsed_time,
                days_of_week=days_of_week or [],
                status=RoutineStatus.INACTIVE,
                current_activity_index=0
            )
            
            # Save to database
            routine_id = await self.db.create_routine(routine)
            routine.id = routine_id
            
            logger.info(f"Created routine: {name} (ID: {routine_id}) for child {child_id}")
            return routine
            
        except Exception as e:
            logger.error(f"Error creating routine: {e}")
            raise
    
    async def start_routine(self, routine_id: int) -> bool:
        """Start a routine."""
        
        try:
            routine = await self.db.get_routine(routine_id)
            if not routine:
                logger.error(f"Routine not found: {routine_id}")
                return False
            
            # Update routine status
            routine.status = RoutineStatus.ACTIVE
            routine.started_at = datetime.now()
            routine.current_activity_index = 0
            
            # Reset all activities
            for activity in routine.activities:
                activity.status = ActivityStatus.NOT_STARTED
                activity.completed_at = None
            
            # This would normally update the database
            # For now, we'll use the MCP client's start_routine method
            success = await self.mcp_client.start_routine(routine.child_id, routine.name)
            
            if success:
                logger.info(f"Started routine: {routine.name} (ID: {routine_id})")
            
            return success
            
        except Exception as e:
            logger.error(f"Error starting routine: {e}")
            return False
    
    async def complete_activity(
        self, 
        routine_id: int, 
        activity_name: str
    ) -> bool:
        """Complete an activity in a routine."""
        
        try:
            return await self.mcp_client.complete_activity(routine_id, activity_name)
            
        except Exception as e:
            logger.error(f"Error completing activity: {e}")
            return False
    
    async def get_routine_status(self, routine_id: int) -> Dict[str, Any]:
        """Get the current status of a routine."""
        
        try:
            routine = await self.db.get_routine(routine_id)
            if not routine:
                raise ValueError(f"Routine not found: {routine_id}")
            
            # Calculate progress
            total_activities = len(routine.activities)
            completed_activities = sum(
                1 for activity in routine.activities 
                if activity.status == ActivityStatus.COMPLETED
            )
            
            progress_percentage = (
                (completed_activities / total_activities * 100) 
                if total_activities > 0 else 0
            )
            
            # Get current activity
            current_activity = None
            if (routine.current_activity_index < len(routine.activities) and 
                routine.status == RoutineStatus.ACTIVE):
                current_activity = routine.activities[routine.current_activity_index].name
            
            # Estimate completion time
            estimated_completion = None
            if routine.started_at and routine.status == RoutineStatus.ACTIVE:
                remaining_activities = total_activities - completed_activities
                estimated_minutes = remaining_activities * 5  # Average 5 minutes per activity
                estimated_completion = (
                    datetime.now().timestamp() + (estimated_minutes * 60)
                )
            
            return {
                "routine_id": routine.id,
                "name": routine.name,
                "status": routine.status.value,
                "progress_percentage": round(progress_percentage, 1),
                "current_activity": current_activity,
                "completed_activities": completed_activities,
                "total_activities": total_activities,
                "started_at": routine.started_at.isoformat() if routine.started_at else None,
                "estimated_completion": (
                    datetime.fromtimestamp(estimated_completion).isoformat() 
                    if estimated_completion else None
                )
            }
            
        except Exception as e:
            logger.error(f"Error getting routine status: {e}")
            raise
    
    async def calculate_progress(self, routine_id: int) -> float:
        """Calculate the progress percentage of a routine."""
        
        try:
            routine = await self.db.get_routine(routine_id)
            if not routine or not routine.activities:
                return 0.0
            
            completed_count = sum(
                1 for activity in routine.activities 
                if activity.status == ActivityStatus.COMPLETED
            )
            
            total_count = len(routine.activities)
            return round((completed_count / total_count * 100), 1)
            
        except Exception as e:
            logger.error(f"Error calculating progress: {e}")
            return 0.0
    
    async def get_next_activity(self, routine_id: int) -> Optional[Activity]:
        """Get the next activity to be completed in a routine."""
        
        try:
            routine = await self.db.get_routine(routine_id)
            if not routine:
                return None
            
            # Find the first incomplete activity
            for activity in routine.activities:
                if activity.status != ActivityStatus.COMPLETED:
                    return activity
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting next activity: {e}")
            return None
    
    async def pause_routine(self, routine_id: int) -> bool:
        """Pause a routine."""
        
        try:
            routine = await self.db.get_routine(routine_id)
            if not routine:
                return False
            
            if routine.status == RoutineStatus.ACTIVE:
                routine.status = RoutineStatus.PAUSED
                # This would normally update the database
                logger.info(f"Paused routine: {routine.name} (ID: {routine_id})")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error pausing routine: {e}")
            return False
    
    async def resume_routine(self, routine_id: int) -> bool:
        """Resume a paused routine."""
        
        try:
            routine = await self.db.get_routine(routine_id)
            if not routine:
                return False
            
            if routine.status == RoutineStatus.PAUSED:
                routine.status = RoutineStatus.ACTIVE
                # This would normally update the database
                logger.info(f"Resumed routine: {routine.name} (ID: {routine_id})")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error resuming routine: {e}")
            return False
    
    async def get_active_routine_for_child(self, child_id: int) -> Optional[Routine]:
        """Get the currently active routine for a child."""
        
        try:
            routines = await self.db.get_child_routines(child_id)
            
            for routine in routines:
                if routine.status == RoutineStatus.ACTIVE:
                    return routine
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting active routine: {e}")
            return None
    
    async def suggest_activities(
        self, 
        child_id: int, 
        routine_type: str = "general"
    ) -> List[str]:
        """Suggest activities based on routine type and child preferences."""
        
        # Default activity suggestions by type
        activity_suggestions = {
            "morning": [
                "Wake Up Gently",
                "Get Dressed",
                "Brush Teeth",
                "Eat Breakfast",
                "Pack School Bag"
            ],
            "bedtime": [
                "Put on Pajamas",
                "Brush Teeth",
                "Read a Story",
                "Say Goodnight",
                "Go to Sleep"
            ],
            "homework": [
                "Set Up Study Space",
                "Review Assignments",
                "Complete Math Work",
                "Complete Reading",
                "Pack Homework"
            ],
            "general": [
                "Get Ready",
                "Complete Task",
                "Take a Break",
                "Clean Up",
                "Celebrate Success"
            ]
        }
        
        return activity_suggestions.get(routine_type, activity_suggestions["general"])
    
    async def get_routine_analytics(self, child_id: int) -> Dict[str, Any]:
        """Get analytics for a child's routine performance."""
        
        try:
            routines = await self.db.get_child_routines(child_id)
            
            total_routines = len(routines)
            completed_routines = sum(
                1 for routine in routines 
                if routine.status == RoutineStatus.COMPLETED
            )
            
            total_activities = sum(len(routine.activities) for routine in routines)
            completed_activities = sum(
                sum(1 for activity in routine.activities 
                    if activity.status == ActivityStatus.COMPLETED)
                for routine in routines
            )
            
            return {
                "total_routines": total_routines,
                "completed_routines": completed_routines,
                "routine_completion_rate": (
                    (completed_routines / total_routines * 100) 
                    if total_routines > 0 else 0
                ),
                "total_activities": total_activities,
                "completed_activities": completed_activities,
                "activity_completion_rate": (
                    (completed_activities / total_activities * 100) 
                    if total_activities > 0 else 0
                )
            }
            
        except Exception as e:
            logger.error(f"Error getting routine analytics: {e}")
            return {
                "total_routines": 0,
                "completed_routines": 0,
                "routine_completion_rate": 0,
                "total_activities": 0,
                "completed_activities": 0,
                "activity_completion_rate": 0
            }
