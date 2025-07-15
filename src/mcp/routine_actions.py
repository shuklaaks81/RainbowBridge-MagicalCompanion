"""
Routine action handler for Rainbow Bridge
Handles routine start and activity completion actions with state management.
"""

import json
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging

from src.models.entities import Routine, Activity, RoutineStatus, ActivityStatus, ActivityLog
from src.services.database import DatabaseService
from src.mcp.intent_detector import IntentDetector

logger = logging.getLogger(__name__)


class RoutineActionHandler:
    """Handler for routine-related actions like starting routines and completing activities."""
    
    def __init__(self, database_service: DatabaseService):
        self.db = database_service
        self.intent_detector = IntentDetector()
    
    async def complete_activity(self, routine_id: int, activity_name: str) -> Dict[str, Any]:
        """Complete an activity in a routine and return detailed result."""
        
        try:
            routine = await self.db.get_routine(routine_id)
            if not routine:
                return {'success': False, 'error': 'Routine not found'}
            
            # Find the activity to complete
            activity_to_complete = None
            activity_index = -1
            
            # First, try to find by exact name match
            for i, activity in enumerate(routine.activities):
                if activity.name.lower().strip() == activity_name.lower().strip():
                    activity_to_complete = activity
                    activity_index = i
                    break
            
            # If not found, try fuzzy matching
            if not activity_to_complete:
                best_match = self.intent_detector.fuzzy_match_activity(activity_name, 
                    [a.name for a in routine.activities])
                if best_match:
                    for i, activity in enumerate(routine.activities):
                        if activity.name == best_match:
                            activity_to_complete = activity
                            activity_index = i
                            break
            
            # If still not found, try current activity
            if not activity_to_complete and routine.current_activity_index < len(routine.activities):
                current_activity = routine.activities[routine.current_activity_index]
                if current_activity.status != ActivityStatus.COMPLETED:
                    activity_to_complete = current_activity
                    activity_index = routine.current_activity_index
            
            if not activity_to_complete:
                return {
                    'success': False, 
                    'error': f'Activity "{activity_name}" not found or already completed'
                }
            
            # Mark activity as completed in database
            await self.db.update_activity_status(
                activity_to_complete.id, 
                'completed', 
                datetime.now()
            )
            
            # Update local status
            activity_to_complete.status = ActivityStatus.COMPLETED
            activity_to_complete.completed_at = datetime.now()
            
            # Calculate new progress
            completed_count = sum(
                1 for a in routine.activities 
                if a.status == ActivityStatus.COMPLETED or a.id == activity_to_complete.id
            )
            total_count = len(routine.activities)
            progress_percentage = (completed_count / total_count * 100)
            
            # Determine next activity and update routine
            next_activity = None
            next_activity_index = routine.current_activity_index
            
            if completed_count >= total_count:
                # All activities completed
                await self.db.update_routine_status(routine_id, 'completed')
                routine.status = RoutineStatus.COMPLETED
                routine.completed_at = datetime.now()
            else:
                # Find next incomplete activity
                for i in range(activity_index + 1, len(routine.activities)):
                    if routine.activities[i].status != ActivityStatus.COMPLETED:
                        next_activity = routine.activities[i]
                        next_activity_index = i
                        break
                
                # Update routine's current activity index
                await self.db.update_routine_status(routine_id, 'active', next_activity_index)
                routine.current_activity_index = next_activity_index
            
            # Log activity completion
            activity_log = ActivityLog(
                child_id=routine.child_id,
                routine_id=routine.id,
                activity_id=activity_to_complete.id,
                activity_name=activity_to_complete.name,
                completed_at=datetime.now(),
                duration_minutes=5  # Default duration, could be calculated
            )
            await self.db.log_activity_completion(activity_log)
            
            result = {
                'success': True,
                'completed_activity': {
                    'name': activity_to_complete.name,
                    'index': activity_index
                },
                'next_activity': {
                    'name': next_activity.name,
                    'index': next_activity_index
                } if next_activity else None,
                'progress': {
                    'completed_count': completed_count,
                    'total_count': total_count,
                    'percentage': round(progress_percentage, 1),
                    'remaining_count': total_count - completed_count
                },
                'routine_completed': completed_count >= total_count,
                'routine_status': routine.status.value
            }
            
            logger.info(f"Activity completed: {activity_to_complete.name} ({completed_count}/{total_count})")
            return result
            
        except Exception as e:
            logger.error(f"Error completing activity: {e}")
            return {'success': False, 'error': str(e)}
    
    async def start_routine(self, child_id: int, routine_name: str) -> Dict[str, Any]:
        """Start a routine for a child with proper state management."""
        
        try:
            routines = await self.db.get_child_routines(child_id)
            
            # Find routine by name (fuzzy matching if needed)
            routine_to_start = None
            for routine in routines:
                if routine.name.lower().strip() == routine_name.lower().strip():
                    routine_to_start = routine
                    break
            
            # Try fuzzy matching if exact match not found
            if not routine_to_start:
                best_match = self.intent_detector.fuzzy_match_routine_name(
                    routine_name, [r.name for r in routines]
                )
                if best_match:
                    routine_to_start = next(r for r in routines if r.name == best_match)
            
            if not routine_to_start:
                return {
                    'success': False,
                    'error': f'Routine "{routine_name}" not found'
                }
            
            # Stop any other active routines for this child
            for routine in routines:
                if routine.status == RoutineStatus.ACTIVE and routine.id != routine_to_start.id:
                    await self.db.update_routine_status(routine.id, 'inactive')
            
            # Start the routine in database
            await self.db.update_routine_status(routine_to_start.id, 'active', 0)
            
            # Reset all activities to pending if this is a fresh start
            for activity in routine_to_start.activities:
                if activity.status == ActivityStatus.COMPLETED:
                    await self.db.update_activity_status(activity.id, 'pending')
                    activity.status = ActivityStatus.PENDING
                    activity.completed_at = None
            
            # Update local routine state
            routine_to_start.status = RoutineStatus.ACTIVE
            routine_to_start.current_activity_index = 0
            
            # Get first activity
            first_activity = None
            if routine_to_start.activities:
                first_activity = routine_to_start.activities[0]
                first_activity.status = ActivityStatus.IN_PROGRESS
                await self.db.update_activity_status(first_activity.id, 'in_progress')
            
            result = {
                'success': True,
                'routine_id': routine_to_start.id,
                'routine_name': routine_to_start.name,
                'first_activity': {
                    'name': first_activity.name,
                    'description': first_activity.description,
                    'instructions': first_activity.instructions,
                    'index': 0
                } if first_activity else None,
                'total_activities': len(routine_to_start.activities),
                'routine_status': routine_to_start.status.value
            }
            
            logger.info(f"Routine started: {routine_to_start.name} for child {child_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error starting routine: {e}")
            return {'success': False, 'error': str(e)}
    
    async def get_routine_status(self, routine_id: int) -> Dict[str, Any]:
        """Get current status and progress of a routine."""
        
        try:
            routine = await self.db.get_routine(routine_id)
            if not routine:
                return {'success': False, 'error': 'Routine not found'}
            
            progress_info = await self.db.get_routine_progress(routine_id)
            
            # Get current activity details
            current_activity = None
            if (routine.current_activity_index < len(routine.activities) and 
                routine.status == RoutineStatus.ACTIVE):
                current_activity = routine.activities[routine.current_activity_index]
            
            return {
                'success': True,
                'routine_id': routine_id,
                'routine_name': routine.name,
                'status': routine.status.value,
                'progress': progress_info,
                'current_activity': {
                    'name': current_activity.name,
                    'description': current_activity.description,
                    'instructions': current_activity.instructions,
                    'index': routine.current_activity_index
                } if current_activity else None,
                'is_completed': routine.status == RoutineStatus.COMPLETED
            }
            
        except Exception as e:
            logger.error(f"Error getting routine status: {e}")
            return {'success': False, 'error': str(e)}
    
    async def pause_routine(self, routine_id: int) -> Dict[str, Any]:
        """Pause an active routine."""
        
        try:
            await self.db.update_routine_status(routine_id, 'paused')
            
            return {
                'success': True,
                'routine_id': routine_id,
                'status': 'paused',
                'message': 'Routine has been paused. You can resume it anytime!'
            }
            
        except Exception as e:
            logger.error(f"Error pausing routine: {e}")
            return {'success': False, 'error': str(e)}
    
    async def resume_routine(self, routine_id: int) -> Dict[str, Any]:
        """Resume a paused routine."""
        
        try:
            routine = await self.db.get_routine(routine_id)
            if not routine:
                return {'success': False, 'error': 'Routine not found'}
            
            await self.db.update_routine_status(routine_id, 'active', routine.current_activity_index)
            
            current_activity = None
            if routine.current_activity_index < len(routine.activities):
                current_activity = routine.activities[routine.current_activity_index]
            
            return {
                'success': True,
                'routine_id': routine_id,
                'status': 'active',
                'current_activity': {
                    'name': current_activity.name,
                    'index': routine.current_activity_index
                } if current_activity else None,
                'message': 'Routine has been resumed. Let\'s continue where we left off!'
            }
            
        except Exception as e:
            logger.error(f"Error resuming routine: {e}")
            return {'success': False, 'error': str(e)}
