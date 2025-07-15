"""
Routine management service for Rainbow Bridge
Handles routine-specific database operations and state management.
"""

import json
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging

from src.models.entities import Routine, Activity, ActivityStatus, RoutineStatus
from src.services.database_core import DatabaseCore

logger = logging.getLogger(__name__)


class RoutineManager:
    """Service for managing routine operations and state."""
    
    def __init__(self, db_core: DatabaseCore):
        self.db_core = db_core
    
    async def get_routine(self, routine_id: int) -> Optional[Routine]:
        """Get a routine by ID with all activities."""
        rows = await self.db_core.execute_query(
            "SELECT * FROM routines WHERE id = ?", (routine_id,)
        )
        
        if not rows:
            return None
        
        routine_row = rows[0]
        
        # Get activities for this routine
        activity_rows = await self.db_core.execute_query("""
            SELECT * FROM activities WHERE routine_id = ? 
            ORDER BY sequence_order
        """, (routine_id,))
        
        activities = []
        for activity_row in activity_rows:
            activity = Activity(
                id=activity_row[0],
                routine_id=activity_row[1],
                name=activity_row[2],
                description=activity_row[3] or "",
                type=activity_row[4] or "task",
                sequence_order=activity_row[5],
                estimated_duration=activity_row[6] or 5,
                instructions=activity_row[7] or "",
                visual_aids=json.loads(activity_row[8]) if activity_row[8] else [],
                status=ActivityStatus(activity_row[9] or "pending"),
                completed_at=datetime.fromisoformat(activity_row[10]) if activity_row[10] else None,
                created_at=datetime.fromisoformat(activity_row[11]) if activity_row[11] else None,
                updated_at=datetime.fromisoformat(activity_row[12]) if activity_row[12] else None
            )
            activities.append(activity)
        
        return Routine(
            id=routine_row[0],
            child_id=routine_row[1],
            name=routine_row[2],
            description=routine_row[3] or "",
            category=routine_row[4] or "daily",
            activities=activities,
            status=RoutineStatus(routine_row[6] or "inactive"),
            current_activity_index=routine_row[7] or 0,
            scheduled_time=routine_row[8],
            completed_at=datetime.fromisoformat(routine_row[9]) if routine_row[9] else None,
            created_at=datetime.fromisoformat(routine_row[10]) if routine_row[10] else None,
            updated_at=datetime.fromisoformat(routine_row[11]) if routine_row[11] else None
        )
    
    async def get_child_routines(self, child_id: int) -> List[Routine]:
        """Get all routines for a child."""
        rows = await self.db_core.execute_query(
            "SELECT id FROM routines WHERE child_id = ? ORDER BY created_at DESC",
            (child_id,)
        )
        
        routines = []
        for row in rows:
            routine = await self.get_routine(row[0])
            if routine:
                routines.append(routine)
        
        return routines
    
    async def get_active_routine(self, child_id: int) -> Optional[Routine]:
        """Get the currently active routine for a child."""
        rows = await self.db_core.execute_query(
            "SELECT id FROM routines WHERE child_id = ? AND status = 'active' LIMIT 1",
            (child_id,)
        )
        
        if not rows:
            return None
        
        return await self.get_routine(rows[0][0])
    
    async def update_routine_status(self, routine_id: int, status: str, current_activity_index: int = None) -> bool:
        """Update routine status and current activity index."""
        if current_activity_index is not None:
            await self.db_core.execute_update("""
                UPDATE routines 
                SET status = ?, current_activity_index = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (status, current_activity_index, routine_id))
        else:
            await self.db_core.execute_update("""
                UPDATE routines 
                SET status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (status, routine_id))
        return True
    
    async def update_activity_status(self, activity_id: int, status: str, completed_at: datetime = None) -> bool:
        """Update activity status and completion time."""
        if completed_at:
            await self.db_core.execute_update("""
                UPDATE activities 
                SET status = ?, completed_at = ?
                WHERE id = ?
            """, (status, completed_at.isoformat(), activity_id))
        else:
            await self.db_core.execute_update("""
                UPDATE activities 
                SET status = ?
                WHERE id = ?
            """, (status, activity_id))
        return True
    
    async def get_routine_progress(self, routine_id: int) -> Dict[str, Any]:
        """Get detailed routine progress information."""
        # Get routine info
        routine_rows = await self.db_core.execute_query(
            "SELECT * FROM routines WHERE id = ?", (routine_id,)
        )
        if not routine_rows:
            return {}
        
        routine_row = routine_rows[0]
        
        # Get activities with their status
        activity_rows = await self.db_core.execute_query("""
            SELECT id, name, status, completed_at, sequence_order
            FROM activities WHERE routine_id = ? 
            ORDER BY sequence_order
        """, (routine_id,))
        
        total_activities = len(activity_rows)
        completed_activities = sum(1 for row in activity_rows if row[2] == 'completed')
        progress_percentage = (completed_activities / total_activities * 100) if total_activities > 0 else 0
        
        # Find current activity
        current_activity = None
        current_activity_index = routine_row[7]  # current_activity_index column
        
        if current_activity_index < len(activity_rows):
            current_row = activity_rows[current_activity_index]
            current_activity = {
                'id': current_row[0],
                'name': current_row[1],
                'status': current_row[2],
                'index': current_activity_index
            }
        
        return {
            'routine_id': routine_id,
            'routine_name': routine_row[2],
            'status': routine_row[6],
            'total_activities': total_activities,
            'completed_activities': completed_activities,
            'progress_percentage': round(progress_percentage, 1),
            'current_activity': current_activity,
            'remaining_activities': total_activities - completed_activities
        }
    
    async def create_routine(self, routine: Routine) -> int:
        """Create a new routine with activities."""
        # Insert routine
        routine_id = await self.db_core.get_last_insert_id("""
            INSERT INTO routines (
                child_id, name, description, category, status, 
                current_activity_index, scheduled_time, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """, (
            routine.child_id, routine.name, routine.description,
            routine.category, routine.status.value, routine.current_activity_index,
            routine.scheduled_time
        ))
        
        # Insert activities
        for activity in routine.activities:
            await self.db_core.execute_update("""
                INSERT INTO activities (
                    routine_id, name, description, type, sequence_order,
                    estimated_duration, instructions, visual_aids, status,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """, (
                routine_id, activity.name, activity.description, activity.type,
                activity.sequence_order, activity.estimated_duration,
                activity.instructions, json.dumps(activity.visual_aids),
                activity.status.value
            ))
        
        return routine_id
