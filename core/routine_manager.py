"""
Routine Manager - Handles routine creation, scheduling, and management

This module manages daily routines, schedules, and activity planning
for autistic children, focusing on predictability and visual support.
"""

import asyncio
import schedule
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import json
import logging

logger = logging.getLogger(__name__)

@dataclass
class Activity:
    """Represents a single activity in a routine."""
    name: str
    duration_minutes: int
    description: str
    visual_cue: str
    instructions: List[str]
    sensory_considerations: List[str]
    completed: bool = False

@dataclass
class Routine:
    """Represents a complete routine for a child."""
    id: Optional[int]
    child_id: int
    name: str
    activities: List[Activity]
    schedule_time: str
    days_of_week: List[str]
    active: bool = True
    created_at: Optional[datetime] = None

class RoutineManager:
    """Manages routines and schedules for special needs children."""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.active_routines: Dict[int, List[Routine]] = {}
        self.routine_templates = self._load_routine_templates()
    
    def _load_routine_templates(self) -> Dict[str, List[Dict]]:
        """Load pre-defined routine templates for different needs."""
        return {
            "morning": [
                {
                    "name": "Wake Up Gently",
                    "duration_minutes": 10,
                    "description": "Gentle wake-up with soft music or lighting",
                    "visual_cue": "sunrise",
                    "instructions": [
                        "Turn on soft light",
                        "Play calming music",
                        "Give child time to adjust"
                    ],
                    "sensory_considerations": ["gradual lighting", "low volume sounds"]
                },
                {
                    "name": "Morning Hygiene",
                    "duration_minutes": 20,
                    "description": "Brush teeth and wash face",
                    "visual_cue": "toothbrush",
                    "instructions": [
                        "Get toothbrush and toothpaste",
                        "Brush teeth for 2 minutes",
                        "Wash face with warm water",
                        "Dry with soft towel"
                    ],
                    "sensory_considerations": ["soft toothbrush", "lukewarm water"]
                },
                {
                    "name": "Get Dressed",
                    "duration_minutes": 15,
                    "description": "Put on comfortable clothes for the day",
                    "visual_cue": "clothes",
                    "instructions": [
                        "Choose clothes together",
                        "Put on underwear first",
                        "Then shirt and pants",
                        "Shoes last"
                    ],
                    "sensory_considerations": ["soft fabrics", "loose fitting", "no scratchy tags"]
                }
            ],
            "learning": [
                {
                    "name": "Visual Learning Time",
                    "duration_minutes": 30,
                    "description": "Interactive learning with pictures and symbols",
                    "visual_cue": "book",
                    "instructions": [
                        "Set up learning materials",
                        "Start with favorite topic",
                        "Use pictures and symbols",
                        "Take breaks as needed"
                    ],
                    "sensory_considerations": ["quiet environment", "good lighting"]
                },
                {
                    "name": "Hands-On Activity",
                    "duration_minutes": 20,
                    "description": "Tactile learning with safe materials",
                    "visual_cue": "hands",
                    "instructions": [
                        "Prepare activity materials",
                        "Demonstrate first",
                        "Let child explore",
                        "Praise efforts"
                    ],
                    "sensory_considerations": ["safe textures", "washable materials"]
                }
            ],
            "calming": [
                {
                    "name": "Deep Breathing",
                    "duration_minutes": 5,
                    "description": "Calming breathing exercises",
                    "visual_cue": "breath",
                    "instructions": [
                        "Sit comfortably",
                        "Breathe in slowly",
                        "Hold for 3 seconds",
                        "Breathe out slowly"
                    ],
                    "sensory_considerations": ["comfortable seating", "quiet space"]
                },
                {
                    "name": "Quiet Time",
                    "duration_minutes": 15,
                    "description": "Peaceful quiet activity",
                    "visual_cue": "peace",
                    "instructions": [
                        "Choose quiet activity",
                        "Dim the lights",
                        "Remove distractions",
                        "Stay nearby for comfort"
                    ],
                    "sensory_considerations": ["minimal stimulation", "comfort items"]
                }
            ]
        }
    
    async def create_routine(
        self,
        child_id: int,
        name: str,
        activities: List[str],
        schedule_time: str,
        days_of_week: Optional[List[str]] = None
    ) -> Routine:
        """Create a new routine for a child."""
        try:
            # Convert activity names to Activity objects
            activity_objects = []
            for activity_name in activities:
                activity_data = self._find_activity_template(activity_name)
                if activity_data:
                    activity_objects.append(Activity(**activity_data))
                else:
                    # Create custom activity
                    activity_objects.append(Activity(
                        name=activity_name,
                        duration_minutes=15,
                        description=f"Custom activity: {activity_name}",
                        visual_cue="custom",
                        instructions=[f"Complete {activity_name} activity"],
                        sensory_considerations=["Monitor comfort level"]
                    ))
            
            routine = Routine(
                id=None,
                child_id=child_id,
                name=name,
                activities=activity_objects,
                schedule_time=schedule_time,
                days_of_week=days_of_week or ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
                created_at=datetime.now()
            )
            
            # Save to database
            routine_id = await self.db_manager.save_routine(routine)
            routine.id = routine_id
            
            # Add to active routines
            if child_id not in self.active_routines:
                self.active_routines[child_id] = []
            self.active_routines[child_id].append(routine)
            
            # Schedule the routine
            self._schedule_routine(routine)
            
            logger.info(f"Created routine '{name}' for child {child_id}")
            return routine
        
        except Exception as e:
            logger.error(f"Failed to create routine: {str(e)}")
            raise
    
    def _find_activity_template(self, activity_name: str) -> Optional[Dict]:
        """Find an activity template by name."""
        activity_name_lower = activity_name.lower()
        
        for template_type, activities in self.routine_templates.items():
            for activity in activities:
                if activity_name_lower in activity["name"].lower():
                    return activity
        
        return None
    
    async def get_child_routines(self, child_id: int) -> List[Dict]:
        """Get all routines for a specific child."""
        try:
            routines = await self.db_manager.get_routines_by_child(child_id)
            
            # Convert to dictionaries for JSON serialization
            return [self._routine_to_dict(routine) for routine in routines]
        
        except Exception as e:
            logger.error(f"Failed to get routines for child {child_id}: {str(e)}")
            return []
    
    def _routine_to_dict(self, routine: Routine) -> Dict:
        """Convert a Routine object to a dictionary."""
        routine_dict = asdict(routine)
        if routine_dict.get("created_at"):
            routine_dict["created_at"] = routine_dict["created_at"].isoformat()
        return routine_dict
    
    async def start_routine(self, routine_id: int, child_id: int) -> Dict[str, Any]:
        """Start a routine session for a child."""
        try:
            routine = await self.db_manager.get_routine(routine_id)
            if not routine or routine.child_id != child_id:
                raise ValueError("Routine not found or not accessible")
            
            # Reset activity completion status
            for activity in routine.activities:
                activity.completed = False
            
            # Create a routine session
            session_data = {
                "routine_id": routine_id,
                "child_id": child_id,
                "started_at": datetime.now(),
                "current_activity": 0,
                "total_activities": len(routine.activities),
                "status": "in_progress"
            }
            
            session_id = await self.db_manager.create_routine_session(session_data)
            
            # Return the first activity
            first_activity = routine.activities[0] if routine.activities else None
            
            return {
                "session_id": session_id,
                "routine": self._routine_to_dict(routine),
                "current_activity": asdict(first_activity) if first_activity else None,
                "progress": 0
            }
        
        except Exception as e:
            logger.error(f"Failed to start routine: {str(e)}")
            raise
    
    async def complete_activity(
        self,
        session_id: int,
        activity_index: int,
        child_id: int
    ) -> Dict[str, Any]:
        """Mark an activity as completed and move to the next one."""
        try:
            session = await self.db_manager.get_routine_session(session_id)
            if not session or session["child_id"] != child_id:
                raise ValueError("Session not found or not accessible")
            
            routine = await self.db_manager.get_routine(session["routine_id"])
            
            # Mark current activity as completed
            if activity_index < len(routine.activities):
                routine.activities[activity_index].completed = True
            
            # Calculate progress
            completed_activities = sum(1 for activity in routine.activities if activity.completed)
            total_activities = len(routine.activities)
            progress = (completed_activities / total_activities) * 100
            
            # Get next activity
            next_index = activity_index + 1
            next_activity = None
            if next_index < len(routine.activities):
                next_activity = routine.activities[next_index]
            
            # Update session
            await self.db_manager.update_routine_session(session_id, {
                "current_activity": next_index,
                "progress": progress,
                "status": "completed" if progress == 100 else "in_progress"
            })
            
            # Log the completed activity
            await self.db_manager.log_activity_completion(
                child_id=child_id,
                activity_name=routine.activities[activity_index].name,
                completed_at=datetime.now()
            )
            
            return {
                "progress": progress,
                "completed": progress == 100,
                "next_activity": asdict(next_activity) if next_activity else None,
                "celebration_message": self._get_celebration_message(progress)
            }
        
        except Exception as e:
            logger.error(f"Failed to complete activity: {str(e)}")
            raise
    
    def _get_celebration_message(self, progress: float) -> str:
        """Get an appropriate celebration message based on progress."""
        if progress == 100:
            return "🎉 Amazing! You completed your whole routine! Great job! 🌟"
        elif progress >= 75:
            return "🌟 You're doing so well! Almost finished! 💪"
        elif progress >= 50:
            return "👏 Great work! You're halfway there! Keep going! 🚀"
        elif progress >= 25:
            return "😊 Good start! You're making great progress! 🌈"
        else:
            return "✨ Every step counts! You're doing great! 💖"
    
    def _schedule_routine(self, routine: Routine):
        """Schedule a routine to run at specified times."""
        try:
            # Parse schedule time
            hour, minute = map(int, routine.schedule_time.split(':'))
            
            # Schedule for each day of the week
            for day in routine.days_of_week:
                if day.lower() == "monday":
                    schedule.every().monday.at(routine.schedule_time).do(
                        self._send_routine_reminder, routine.child_id, routine.id
                    )
                elif day.lower() == "tuesday":
                    schedule.every().tuesday.at(routine.schedule_time).do(
                        self._send_routine_reminder, routine.child_id, routine.id
                    )
                # Add other days as needed...
            
            logger.info(f"Scheduled routine {routine.id} for {routine.schedule_time}")
        
        except Exception as e:
            logger.error(f"Failed to schedule routine: {str(e)}")
    
    def _send_routine_reminder(self, child_id: int, routine_id: int):
        """Send a reminder notification for a scheduled routine."""
        # This would integrate with a notification system
        logger.info(f"Routine reminder for child {child_id}, routine {routine_id}")
    
    async def get_routine_suggestions(
        self,
        child_id: int,
        time_of_day: str,
        child_preferences: Dict
    ) -> List[Dict]:
        """Get routine suggestions based on time and preferences."""
        try:
            # Determine appropriate template based on time
            if "morning" in time_of_day.lower():
                template_key = "morning"
            elif any(word in time_of_day.lower() for word in ["learn", "study", "activity"]):
                template_key = "learning"
            elif any(word in time_of_day.lower() for word in ["calm", "relax", "quiet"]):
                template_key = "calming"
            else:
                template_key = "learning"  # Default
            
            activities = self.routine_templates.get(template_key, [])
            
            # Customize based on preferences
            if child_preferences.get("interests"):
                interests = child_preferences["interests"]
                # Modify activities to incorporate interests
                for activity in activities:
                    if any(interest in activity["name"].lower() for interest in interests):
                        activity["customized"] = True
            
            return activities[:5]  # Return top 5 suggestions
        
        except Exception as e:
            logger.error(f"Failed to get routine suggestions: {str(e)}")
            return []
