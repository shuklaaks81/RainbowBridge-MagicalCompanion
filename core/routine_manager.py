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
            "bedtime": [
                {
                    "name": "Evening Wind Down",
                    "duration_minutes": 15,
                    "description": "Quiet activities to prepare for bed",
                    "visual_cue": "moon",
                    "instructions": [
                        "Dim the lights",
                        "Put away toys",
                        "Choose a quiet activity",
                        "Speak in soft voices"
                    ],
                    "sensory_considerations": ["low lighting", "quiet sounds"]
                },
                {
                    "name": "Bedtime Hygiene",
                    "duration_minutes": 20,
                    "description": "Brush teeth and get ready for bed",
                    "visual_cue": "toothbrush",
                    "instructions": [
                        "Brush teeth carefully",
                        "Wash face and hands",
                        "Use the bathroom",
                        "Put on pajamas"
                    ],
                    "sensory_considerations": ["soft toothbrush", "lukewarm water"]
                },
                {
                    "name": "Bedtime Story",
                    "duration_minutes": 15,
                    "description": "Read a calming bedtime story",
                    "visual_cue": "book",
                    "instructions": [
                        "Choose a familiar story",
                        "Get comfortable in bed",
                        "Read with soft voice",
                        "Talk about the story"
                    ],
                    "sensory_considerations": ["comfortable bedding", "dim reading light"]
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
            ],
            "custom": [
                {
                    "name": "Free Play Time",
                    "duration_minutes": 20,
                    "description": "Open-ended play with favorite activities",
                    "visual_cue": "play",
                    "instructions": [
                        "Choose favorite activities",
                        "Allow free exploration",
                        "Join in if invited",
                        "Follow child's lead"
                    ],
                    "sensory_considerations": ["child's preferences", "safe environment"]
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
            
            # Routines are already dictionaries from the database
            return routines
        
        except Exception as e:
            logger.error(f"Failed to get routines for child {child_id}: {str(e)}")
            return []
    
    def _routine_to_dict(self, routine: Routine) -> Dict:
        """Convert a Routine object to a dictionary."""
        routine_dict = asdict(routine)
        if routine_dict.get("created_at"):
            routine_dict["created_at"] = routine_dict["created_at"].isoformat()
        return routine_dict
    
    async def get_routine(self, routine_id: int) -> Optional[Routine]:
        """Get a specific routine by ID."""
        try:
            routine_data = await self.db_manager.get_routine(routine_id)
            if routine_data:
                return self._dict_to_routine(routine_data)
            return None
        except Exception as e:
            logger.error(f"Failed to get routine {routine_id}: {str(e)}")
            return None
    
    async def start_routine(self, routine_id: int) -> bool:
        """Start a routine session."""
        try:
            logger.info(f"🔄 Starting routine {routine_id}...")
            routine = await self.get_routine(routine_id)
            if not routine:
                logger.error(f"❌ Routine {routine_id} not found")
                return False
            
            logger.info(f"✅ Found routine: {routine.name}")
            
            # Check for existing active sessions for this child and routine
            try:
                existing_session = await self._get_active_session(routine.child_id, routine_id)
                if existing_session:
                    logger.info(f"📋 Resuming existing session {existing_session['id']} for routine {routine_id}")
                    return True
            except Exception as e:
                logger.warning(f"Could not check for existing sessions: {str(e)}")
            
            # Create a new routine session
            logger.info(f"🔄 Creating session for child {routine.child_id}...")
            
            # Get activities count safely
            activities_count = 0
            if hasattr(routine, 'activities') and routine.activities:
                if isinstance(routine.activities, list):
                    activities_count = len(routine.activities)
                else:
                    logger.warning(f"Routine activities is not a list: {type(routine.activities)}")
            
            session_data = {
                "routine_id": routine_id,
                "child_id": routine.child_id,
                "started_at": datetime.now(),
                "current_activity": 0,
                "total_activities": activities_count,
                "status": "in_progress",
                "progress": 0.0
            }
            
            logger.info(f"Session data: {session_data}")
            session_id = await self.db_manager.create_routine_session(session_data)
            logger.info(f"✅ Started routine session {session_id} for routine {routine_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start routine {routine_id}: {str(e)}")
            return False
    
    async def complete_activity(self, routine_id: int, activity_name: str) -> bool:
        """Mark an activity as completed in a routine."""
        try:
            routine = await self.get_routine(routine_id)
            if not routine:
                return False
            
            # Find the activity index with fuzzy matching
            activity_index = None
            activity_name_lower = activity_name.lower()
            
            # First try exact match
            for i, activity in enumerate(routine.activities):
                if activity.name.lower() == activity_name_lower:
                    activity_index = i
                    break
            
            # If no exact match, try partial matching
            if activity_index is None:
                for i, activity in enumerate(routine.activities):
                    activity_lower = activity.name.lower()
                    # Check if activity name contains the input or vice versa
                    if (activity_name_lower in activity_lower or 
                        activity_lower in activity_name_lower or
                        self._fuzzy_match_activity(activity_name_lower, activity_lower)):
                        activity_index = i
                        logger.info(f"🔍 Fuzzy matched '{activity_name}' to '{activity.name}'")
                        break
            
            if activity_index is None:
                logger.warning(f"Activity '{activity_name}' not found in routine {routine_id}")
                # List available activities for debugging
                available_activities = [a.name for a in routine.activities]
                logger.info(f"Available activities: {available_activities}")
                return False
            
            # Mark as completed
            routine.activities[activity_index].completed = True
            
            # Update in database
            await self.db_manager.update_routine_activity_status(
                routine_id, activity_index, True
            )
            
            # Sync routine session progress
            await self._sync_routine_session_progress(routine_id)
            
            # Log the completion
            await self.db_manager.log_activity_completion(
                child_id=routine.child_id,
                activity_name=activity_name,
                routine_id=routine_id,
                completed_at=datetime.now()
            )
            
            logger.info(f"Completed activity {activity_name} in routine {routine_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to complete activity {activity_name}: {str(e)}")
            return False
    
    async def update_routine(self, routine_id: int, updates: Dict[str, Any]) -> bool:
        """Update an existing routine."""
        try:
            routine = await self.get_routine(routine_id)
            if not routine:
                return False
            
            # Apply updates
            if "name" in updates:
                routine.name = updates["name"]
            if "schedule_time" in updates:
                routine.schedule_time = updates["schedule_time"]
            if "days_of_week" in updates:
                routine.days_of_week = updates["days_of_week"]
            if "active" in updates:
                routine.active = updates["active"]
            
            # Update in database
            await self.db_manager.update_routine(routine_id, asdict(routine))
            
            logger.info(f"Updated routine {routine_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update routine {routine_id}: {str(e)}")
            return False
    
    def _dict_to_routine(self, routine_data: Dict) -> Routine:
        """Convert dictionary data to Routine object."""
        activities_data = routine_data.get("activities", [])
        activities = []
        
        for activity_data in activities_data:
            if isinstance(activity_data, dict):
                activities.append(Activity(**activity_data))
            else:
                # Handle string activity names
                activities.append(Activity(
                    name=str(activity_data),
                    duration_minutes=15,
                    description=f"Activity: {activity_data}",
                    visual_cue="activity",
                    instructions=[f"Complete {activity_data}"],
                    sensory_considerations=[]
                ))
        
        return Routine(
            id=routine_data.get("id"),
            child_id=routine_data["child_id"],
            name=routine_data["name"],
            activities=activities,
            schedule_time=routine_data["schedule_time"],
            days_of_week=routine_data.get("days_of_week", []),
            active=routine_data.get("active", True),
            created_at=routine_data.get("created_at")
        )
    
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
    
    async def _get_active_session(self, child_id: int, routine_id: int) -> Optional[Dict]:
        """Get active session for a specific child and routine."""
        try:
            # Use raw SQL query to check for active sessions
            import aiosqlite
            async with aiosqlite.connect(self.db_manager.db_path) as db:
                db.row_factory = aiosqlite.Row
                cursor = await db.execute("""
                    SELECT * FROM routine_sessions 
                    WHERE child_id = ? AND routine_id = ? AND status = 'in_progress'
                    ORDER BY started_at DESC LIMIT 1
                """, (child_id, routine_id))
                
                row = await cursor.fetchone()
                if row:
                    return dict(row)
                return None
                
        except Exception as e:
            logger.error(f"Failed to get active session: {str(e)}")
            return None
    
    def _fuzzy_match_activity(self, input_name: str, activity_name: str) -> bool:
        """Enhanced fuzzy match activity names to handle variations and general phrases."""
        
        # Enhanced activity mappings that match the MCP client mappings
        activity_mappings = {
            # Wake up variations
            "wake up": ["wake", "woke", "awake", "morning", "got up", "get up", "wake up gently", "morning wake"],
            
            # Teeth/brushing variations  
            "brush teeth": ["teeth", "brush", "brushing", "tooth", "toothbrush", "clean teeth", "dental"],
            
            # Getting dressed variations
            "get dressed": ["dressed", "dress", "clothes", "clothing", "shirt", "pants", "outfit", "getting dressed"],
            
            # Eating variations
            "eat breakfast": ["breakfast", "morning food", "ate", "eating", "morning meal"],
            "eat lunch": ["lunch", "midday meal", "noon food", "afternoon meal"],
            "eat dinner": ["dinner", "evening meal", "supper", "night food"],
            
            # Washing variations
            "wash hands": ["hands", "wash hands", "clean hands", "hand washing"],
            "wash face": ["face", "wash face", "clean face", "face washing"],
            "take shower": ["shower", "showering", "bath", "bathing", "wash", "cleaning"],
            
            # Other activities
            "do homework": ["homework", "study", "schoolwork", "reading", "book"],
            "play": ["playing", "game", "toy", "fun", "playtime"],
            "clean room": ["clean", "cleanup", "tidy", "organize", "room"],
            "put on shoes": ["shoes", "socks", "footwear"],
            "put on pajamas": ["pajamas", "pjs", "nightclothes", "sleeping clothes"],
            "go to bed": ["bed", "sleep", "sleeping", "bedtime", "sleepy"],
            "comb hair": ["hair", "comb", "brush hair"],
            "take medicine": ["medicine", "medication", "pills", "vitamin"]
        }
        
        input_lower = input_name.lower().strip()
        activity_lower = activity_name.lower().strip()
        
        # Direct string matching
        if input_lower == activity_lower:
            return True
        
        # Check if input is contained in activity or vice versa
        if input_lower in activity_lower or activity_lower in input_lower:
            return True
        
        # Check enhanced mappings - both directions
        for canonical_activity, variations in activity_mappings.items():
            # If the routine activity matches canonical form
            if canonical_activity in activity_lower:
                # Check if input matches any variation
                if any(var in input_lower for var in variations):
                    return True
                if input_lower in variations:
                    return True
            
            # If input matches canonical form
            if canonical_activity in input_lower:
                # Check if activity matches any variation  
                if any(var in activity_lower for var in variations):
                    return True
        
        # Check if input matches any variation and activity matches canonical
        for canonical_activity, variations in activity_mappings.items():
            if any(var in input_lower for var in variations):
                if canonical_activity in activity_lower:
                    return True
        
        # Word-based matching for more flexibility
        input_words = set(input_lower.split())
        activity_words = set(activity_lower.split())
        
        if len(input_words) > 0 and len(activity_words) > 0:
            common_words = input_words.intersection(activity_words)
            # Lower threshold for shorter phrases
            min_length = min(len(input_words), len(activity_words))
            threshold = 0.5 if min_length > 1 else 0.8
            overlap_ratio = len(common_words) / min_length
            if overlap_ratio >= threshold:
                return True
        
        # Special case: single word matching for key activity words
        key_words = {
            "teeth": "brush teeth",
            "breakfast": "eat breakfast", 
            "lunch": "eat lunch",
            "dinner": "eat dinner",
            "dressed": "get dressed",
            "clothes": "get dressed",
            "shower": "take shower",
            "bath": "take shower",
            "homework": "do homework",
            "sleep": "go to bed",
            "bed": "go to bed"
        }
        
        for key_word, target_activity in key_words.items():
            if key_word in input_lower and target_activity in activity_lower:
                return True
            if key_word in activity_lower and target_activity in input_lower:
                return True
        
        return False
    
    async def _sync_routine_session_progress(self, routine_id: int) -> None:
        """Sync routine session progress with actual activity completion status."""
        try:
            import aiosqlite
            import json
            
            async with aiosqlite.connect(self.db_manager.db_path) as db:
                # Get routine and its activities
                cursor = await db.execute("""
                    SELECT r.activities, rs.id as session_id
                    FROM routines r
                    JOIN routine_sessions rs ON r.id = rs.routine_id
                    WHERE r.id = ? AND rs.status = 'in_progress'
                    ORDER BY rs.started_at DESC
                    LIMIT 1
                """, (routine_id,))
                
                result = await cursor.fetchone()
                if not result:
                    return
                
                activities_json, session_id = result
                activities = json.loads(activities_json) if activities_json else []
                
                if not activities:
                    return
                
                # Calculate progress
                total_activities = len(activities)
                completed_count = sum(1 for a in activities if a.get('completed', False))
                progress = (completed_count / total_activities * 100) if total_activities > 0 else 0
                
                # Find current activity index (first incomplete activity)
                current_activity_index = 0
                for i, activity in enumerate(activities):
                    if not activity.get('completed', False):
                        current_activity_index = i
                        break
                
                # Check if routine is completed
                if completed_count == total_activities:
                    # Mark session as completed
                    await db.execute("""
                        UPDATE routine_sessions 
                        SET status = 'completed', 
                            progress = 100.0, 
                            current_activity = ?,
                            completed_at = CURRENT_TIMESTAMP
                        WHERE id = ?
                    """, (total_activities - 1, session_id))
                    logger.info(f"✅ Routine session {session_id} marked as completed")
                else:
                    # Update session progress
                    await db.execute("""
                        UPDATE routine_sessions 
                        SET current_activity = ?, 
                            total_activities = ?,
                            progress = ?
                        WHERE id = ?
                    """, (current_activity_index, total_activities, progress, session_id))
                    logger.info(f"📊 Updated routine session {session_id}: {completed_count}/{total_activities} ({progress:.1f}%)")
                
                await db.commit()
                
        except Exception as e:
            logger.error(f"Failed to sync routine session progress for routine {routine_id}: {e}")
