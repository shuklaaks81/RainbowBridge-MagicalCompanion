"""
Database service for Rainbow Bridge
Main database service that coordinates specialized database managers.
"""

from typing import Dict, List, Optional, Any
import logging

from src.models.entities import (
    Child, Routine, Activity, Interaction, Milestone, 
    ActivityLog, VisualCard
)
from src.services.database_core import DatabaseCore
from src.services.routine_manager import RoutineManager
from src.services.progress_tracker import ProgressTracker
from src.services.child_manager import ChildManager

logger = logging.getLogger(__name__)


class DatabaseService:
    """Main database service that coordinates specialized managers."""
    
    def __init__(self, db_path: str = "special_kids.db"):
        self.db_path = db_path
        self.core = DatabaseCore(db_path)
        self.routine_manager = RoutineManager(self.core)
        self.progress_tracker = ProgressTracker(self.core)
        self.child_manager = ChildManager(self.core)
    
    async def initialize(self):
        """Initialize the database with required tables."""
        await self.core.initialize()
    
    # Child management methods (delegate to child_manager)
    async def get_child_profile(self, child_id: int) -> Optional[Child]:
        """Get a child profile by ID."""
        return await self.child_manager.get_child_profile(child_id)
    
    async def create_child_profile(self, child: Child) -> int:
        """Create a new child profile."""
        return await self.child_manager.create_child_profile(child)
    
    async def update_child_profile(self, child_id: int, updates: Dict[str, Any]) -> bool:
        """Update a child profile."""
        return await self.child_manager.update_child_profile(child_id, updates)
    
    async def get_all_children(self) -> List[Child]:
        """Get all child profiles."""
        return await self.child_manager.get_all_children()
    
    async def get_child_visual_cards(self, child_id: int) -> List[VisualCard]:
        """Get visual cards for a child."""
        return await self.child_manager.get_child_visual_cards(child_id)
    
    async def get_child_context_summary(self, child_id: int) -> Dict[str, Any]:
        """Get child context summary."""
        return await self.child_manager.get_child_context_summary(child_id)
    
    # Routine management methods (delegate to routine_manager)
    async def get_routine(self, routine_id: int) -> Optional[Routine]:
        """Get a routine by ID."""
        return await self.routine_manager.get_routine(routine_id)
    
    async def get_child_routines(self, child_id: int) -> List[Routine]:
        """Get all routines for a child."""
        return await self.routine_manager.get_child_routines(child_id)
    
    async def get_active_routine(self, child_id: int) -> Optional[Routine]:
        """Get the active routine for a child."""
        return await self.routine_manager.get_active_routine(child_id)
    
    async def create_routine(self, routine: Routine) -> int:
        """Create a new routine."""
        return await self.routine_manager.create_routine(routine)
    
    async def update_routine_status(self, routine_id: int, status: str, current_activity_index: int = None) -> bool:
        """Update routine status."""
        return await self.routine_manager.update_routine_status(routine_id, status, current_activity_index)
    
    async def update_activity_status(self, activity_id: int, status: str, completed_at = None) -> bool:
        """Update activity status."""
        return await self.routine_manager.update_activity_status(activity_id, status, completed_at)
    
    async def get_routine_progress(self, routine_id: int) -> Dict[str, Any]:
        """Get routine progress information."""
        return await self.routine_manager.get_routine_progress(routine_id)
    
    # Progress tracking methods (delegate to progress_tracker)
    async def log_activity_completion(self, activity_log: ActivityLog) -> int:
        """Log an activity completion."""
        return await self.progress_tracker.log_activity_completion(activity_log)
    
    async def log_interaction(self, interaction: Interaction) -> int:
        """Log a communication interaction."""
        return await self.progress_tracker.log_interaction(interaction)
    
    async def add_milestone(self, milestone: Milestone) -> int:
        """Add a milestone achievement."""
        return await self.progress_tracker.add_milestone(milestone)
    
    async def get_child_progress_summary(self, child_id: int, days: int = 7) -> Dict[str, Any]:
        """Get child progress summary."""
        return await self.progress_tracker.get_child_progress_summary(child_id, days)
    
    async def get_routine_completion_stats(self, child_id: int, routine_id: int = None) -> Dict[str, Any]:
        """Get routine completion statistics."""
        return await self.progress_tracker.get_routine_completion_stats(child_id, routine_id)
    
    async def get_streak_information(self, child_id: int) -> Dict[str, Any]:
        """Get activity streak information."""
        return await self.progress_tracker.get_streak_information(child_id)
