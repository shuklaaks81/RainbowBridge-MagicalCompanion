"""
Database service for Rainbow Bridge
Main database service that coordinates specialized database managers.
"""

from typing import Dict, List, Optional, Any
import logging
import aiosqlite
import json
from datetime import datetime

from src.models.entities import (
    Child, Routine, Activity, Interaction, Milestone, 
    ActivityLog, VisualCard, CommunicationLevel, ActivityStatus, RoutineStatus
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
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await self._create_tables(db)
                await db.commit()
                logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise
    
    async def _create_tables(self, db: aiosqlite.Connection):
        """Create all required database tables."""
        
        # Children table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS children (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER NOT NULL,
                communication_level TEXT NOT NULL,
                interests TEXT,  -- JSON array
                special_needs TEXT,  -- JSON array
                preferences TEXT,  -- JSON object
                profile_picture TEXT DEFAULT 'default.svg',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Routines table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS routines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                child_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                schedule_time TEXT,
                days_of_week TEXT,  -- JSON array
                status TEXT DEFAULT 'inactive',
                current_activity_index INTEGER DEFAULT 0,
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (child_id) REFERENCES children (id)
            )
        """)
        
        # Activities table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                routine_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                sequence_order INTEGER NOT NULL,
                estimated_duration INTEGER DEFAULT 5,
                visual_cue TEXT,
                audio_cue TEXT,
                instructions TEXT,  -- JSON array
                status TEXT DEFAULT 'not_started',
                completed_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (routine_id) REFERENCES routines (id)
            )
        """)
        
        # Interactions table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                child_id INTEGER NOT NULL,
                message TEXT NOT NULL,
                ai_response TEXT NOT NULL,
                communication_type TEXT DEFAULT 'text',
                context TEXT,  -- JSON object
                routine_id INTEGER,
                activity_id INTEGER,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (child_id) REFERENCES children (id),
                FOREIGN KEY (routine_id) REFERENCES routines (id),
                FOREIGN KEY (activity_id) REFERENCES activities (id)
            )
        """)
        
        # Milestones table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS milestones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                child_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                category TEXT NOT NULL,
                achieved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data TEXT,  -- JSON object
                FOREIGN KEY (child_id) REFERENCES children (id)
            )
        """)
        
        # Activity logs table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS activity_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                child_id INTEGER NOT NULL,
                routine_id INTEGER NOT NULL,
                activity_id INTEGER NOT NULL,
                activity_name TEXT NOT NULL,
                completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                duration_minutes INTEGER,
                notes TEXT,
                satisfaction_level INTEGER,
                FOREIGN KEY (child_id) REFERENCES children (id),
                FOREIGN KEY (routine_id) REFERENCES routines (id),
                FOREIGN KEY (activity_id) REFERENCES activities (id)
            )
        """)
        
        # Visual cards table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS visual_cards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                image_path TEXT NOT NULL,
                description TEXT,
                keywords TEXT,  -- JSON array
                is_custom BOOLEAN DEFAULT FALSE,
                child_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (child_id) REFERENCES children (id)
            )
        """)
    
    # Child profile operations
    async def create_child_profile(self, child_data: Dict[str, Any]) -> int:
        """Create a new child profile."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                INSERT INTO children (name, age, communication_level, interests, 
                                    special_needs, preferences, profile_picture)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                child_data.get('name'),
                child_data.get('age'),
                child_data.get('communication_level'),
                json.dumps(child_data.get('interests', [])),
                json.dumps(child_data.get('special_needs', [])),
                json.dumps(child_data.get('preferences', {})),
                child_data.get('profile_picture', 'default.svg')
            ))
            await db.commit()
            return cursor.lastrowid
    
    async def get_child_profile(self, child_id: int) -> Optional[Child]:
        """Get a child profile by ID."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT * FROM children WHERE id = ?", (child_id,)
            )
            row = await cursor.fetchone()
            if row:
                return self._row_to_child(row)
            return None
    
    async def get_all_children(self) -> List[Child]:
        """Get all child profiles."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT * FROM children ORDER BY name")
            rows = await cursor.fetchall()
            return [self._row_to_child(row) for row in rows]
    
    async def update_child_profile(self, child_id: int, child_data: Dict[str, Any]) -> bool:
        """Update a child profile."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                UPDATE children 
                SET name = ?, age = ?, communication_level = ?, interests = ?,
                    special_needs = ?, preferences = ?, profile_picture = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (
                child_data.get('name'),
                child_data.get('age'),
                child_data.get('communication_level'),
                json.dumps(child_data.get('interests', [])),
                json.dumps(child_data.get('special_needs', [])),
                json.dumps(child_data.get('preferences', {})),
                child_data.get('profile_picture', 'default.svg'),
                child_id
            ))
            await db.commit()
            return True
    
    # Routine operations
    async def create_routine(self, routine: Routine) -> int:
        """Create a new routine with activities."""
        async with aiosqlite.connect(self.db_path) as db:
            # Create routine
            cursor = await db.execute("""
                INSERT INTO routines (child_id, name, description, schedule_time, 
                                    days_of_week, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                routine.child_id,
                routine.name,
                routine.description,
                routine.schedule_time.strftime("%H:%M") if routine.schedule_time else None,
                json.dumps(routine.days_of_week),
                routine.status.value
            ))
            routine_id = cursor.lastrowid
            
            # Create activities
            for i, activity in enumerate(routine.activities):
                await db.execute("""
                    INSERT INTO activities (routine_id, name, description, sequence_order,
                                          estimated_duration, visual_cue, audio_cue, 
                                          instructions, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    routine_id,
                    activity.name,
                    activity.description,
                    i,
                    activity.estimated_duration,
                    activity.visual_cue,
                    activity.audio_cue,
                    json.dumps(activity.instructions),
                    activity.status.value
                ))
            
            await db.commit()
            return routine_id
    
    async def get_routine(self, routine_id: int) -> Optional[Routine]:
        """Get a routine with its activities."""
        async with aiosqlite.connect(self.db_path) as db:
            # Get routine
            cursor = await db.execute(
                "SELECT * FROM routines WHERE id = ?", (routine_id,)
            )
            routine_row = await cursor.fetchone()
            if not routine_row:
                return None
            
            # Get activities
            cursor = await db.execute("""
                SELECT * FROM activities WHERE routine_id = ? 
                ORDER BY sequence_order
            """, (routine_id,))
            activity_rows = await cursor.fetchall()
            
            return self._rows_to_routine(routine_row, activity_rows)
    
    async def get_child_routines(self, child_id: int) -> List[Routine]:
        """Get all routines for a child."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT * FROM routines WHERE child_id = ? ORDER BY created_at DESC",
                (child_id,)
            )
            routine_rows = await cursor.fetchall()
            
            routines = []
            for routine_row in routine_rows:
                try:
                    # Get activities for each routine
                    cursor = await db.execute("""
                        SELECT * FROM activities WHERE routine_id = ? 
                        ORDER BY sequence_order
                    """, (routine_row[0],))  # routine_row[0] is the id
                    activity_rows = await cursor.fetchall()
                    
                    routine = self._rows_to_routine(routine_row, activity_rows)
                    routines.append(routine)
                except Exception as e:
                    logger.error(f"Error processing routine {routine_row[0] if routine_row else 'unknown'}: {e}")
                    continue
            
            return routines
    
    # Interaction logging
    async def log_interaction(self, interaction: Interaction) -> int:
        """Log a new interaction."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                INSERT INTO interactions (child_id, message, ai_response, 
                                        communication_type, context, routine_id, 
                                        activity_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                interaction.child_id,
                interaction.message,
                interaction.ai_response,
                interaction.communication_type,
                json.dumps(interaction.context),
                interaction.routine_id,
                interaction.activity_id
            ))
            await db.commit()
            return cursor.lastrowid
    
    # Activity logging
    async def log_activity_completion(self, activity_log: ActivityLog) -> int:
        """Log activity completion."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                INSERT INTO activity_logs (child_id, routine_id, activity_id, 
                                         activity_name, completed_at, duration_minutes,
                                         notes, satisfaction_level)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                activity_log.child_id,
                activity_log.routine_id,
                activity_log.activity_id,
                activity_log.activity_name,
                activity_log.completed_at.isoformat(),
                activity_log.duration_minutes,
                activity_log.notes,
                activity_log.satisfaction_level
            ))
            await db.commit()
            return cursor.lastrowid
    
    # Enhanced routine state management
    async def update_routine_status(self, routine_id: int, status: str, current_activity_index: int = None) -> bool:
        """Update routine status and current activity index."""
        async with aiosqlite.connect(self.db_path) as db:
            if current_activity_index is not None:
                await db.execute("""
                    UPDATE routines 
                    SET status = ?, current_activity_index = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (status, current_activity_index, routine_id))
            else:
                await db.execute("""
                    UPDATE routines 
                    SET status = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (status, routine_id))
            await db.commit()
            return True
    
    async def update_activity_status(self, activity_id: int, status: str, completed_at: datetime = None) -> bool:
        """Update activity status and completion time."""
        async with aiosqlite.connect(self.db_path) as db:
            if completed_at:
                await db.execute("""
                    UPDATE activities 
                    SET status = ?, completed_at = ?
                    WHERE id = ?
                """, (status, completed_at.isoformat(), activity_id))
            else:
                await db.execute("""
                    UPDATE activities 
                    SET status = ?
                    WHERE id = ?
                """, (status, activity_id))
            await db.commit()
            return True
    
    async def get_routine_progress(self, routine_id: int) -> Dict[str, Any]:
        """Get detailed routine progress information (legacy database version)."""
        async with aiosqlite.connect(self.db_path) as db:
            # Get routine info from legacy database
            cursor = await db.execute(
                "SELECT id, child_id, name, activities, schedule_time, days_of_week, active, total_activities, created_at, updated_at FROM routines WHERE id = ?", 
                (routine_id,)
            )
            routine_row = await cursor.fetchone()
            if not routine_row:
                return {}
            
            try:
                # Parse activities from JSON
                activities_json = routine_row[3]  # activities column
                if activities_json:
                    activities = json.loads(activities_json)
                else:
                    activities = []
                
                total_activities = len(activities)
                completed_activities = sum(1 for activity in activities if activity.get('completed', False))
                progress_percentage = (completed_activities / total_activities * 100) if total_activities > 0 else 0
                
                # Find current activity (first non-completed one)
                current_activity = None
                current_activity_index = 0
                
                for i, activity in enumerate(activities):
                    if not activity.get('completed', False):
                        current_activity = {
                            'name': activity.get('name', f'Activity {i+1}'),
                            'description': activity.get('description', ''),
                            'index': i
                        }
                        current_activity_index = i
                        break
                
                # If all activities are completed, show the last one
                if current_activity is None and activities:
                    last_activity = activities[-1]
                    current_activity = {
                        'name': last_activity.get('name', f'Activity {len(activities)}'),
                        'description': last_activity.get('description', ''),
                        'index': len(activities) - 1
                    }
                    current_activity_index = len(activities) - 1
                
                return {
                    'routine_id': routine_id,
                    'routine_name': routine_row[2],  # name column
                    'status': 'active' if routine_row[6] else 'inactive',  # active column
                    'total_activities': total_activities,
                    'completed_activities': completed_activities,
                    'progress_percentage': round(progress_percentage, 1),
                    'current_activity': current_activity,
                    'current_activity_index': current_activity_index,
                    'started_at': routine_row[8],  # created_at
                    'activities': [
                        {
                            'name': activity.get('name', f'Activity {i+1}'),
                            'description': activity.get('description', ''),
                            'completed': activity.get('completed', False),
                            'index': i
                        }
                        for i, activity in enumerate(activities)
                    ]
                }
            except (json.JSONDecodeError, TypeError, IndexError) as e:
                logger.error(f"Error parsing routine {routine_id} activities: {e}")
                return {
                    'routine_id': routine_id,
                    'routine_name': routine_row[2] if len(routine_row) > 2 else 'Unknown Routine',
                    'status': 'error',
                    'total_activities': 0,
                    'completed_activities': 0,
                    'progress_percentage': 0,
                    'current_activity': None,
                    'current_activity_index': 0,
                    'started_at': routine_row[8] if len(routine_row) > 8 else None,
                    'activities': []
                }
    
    # Helper methods
    def _row_to_child(self, row) -> Child:
        """Convert database row to Child object."""
        return Child(
            id=row[0],
            name=row[1],
            age=row[2],
            communication_level=CommunicationLevel(row[3]),
            interests=json.loads(row[4]) if row[4] else [],
            special_needs=json.loads(row[5]) if row[5] else [],
            preferences=json.loads(row[6]) if row[6] else {},
            profile_picture=row[7],
            created_at=datetime.fromisoformat(row[8]) if row[8] else None,
            updated_at=datetime.fromisoformat(row[9]) if row[9] else None
        )
    
    def _safe_routine_status(self, status_value):
        """Safely convert status value to RoutineStatus enum."""
        if isinstance(status_value, int):
            # Handle legacy integer values
            status_map = {
                0: RoutineStatus.INACTIVE,
                1: RoutineStatus.ACTIVE,
                2: RoutineStatus.COMPLETED,
                3: RoutineStatus.PAUSED
            }
            return status_map.get(status_value, RoutineStatus.INACTIVE)
        elif isinstance(status_value, str):
            try:
                return RoutineStatus(status_value)
            except ValueError:
                return RoutineStatus.INACTIVE
        else:
            return RoutineStatus.INACTIVE

    def _safe_activity_status(self, status_value):
        """Safely convert status value to ActivityStatus enum."""
        if isinstance(status_value, int):
            # Handle legacy integer values
            status_map = {
                0: ActivityStatus.NOT_STARTED,
                1: ActivityStatus.IN_PROGRESS,
                2: ActivityStatus.COMPLETED,
                3: ActivityStatus.SKIPPED
            }
            return status_map.get(status_value, ActivityStatus.NOT_STARTED)
        elif isinstance(status_value, str):
            try:
                return ActivityStatus(status_value)
            except ValueError:
                return ActivityStatus.NOT_STARTED
        else:
            return ActivityStatus.NOT_STARTED

    def _rows_to_routine(self, routine_row, activity_rows) -> Routine:
        """Convert database rows to Routine object."""
        activities = []
        for activity_row in activity_rows:
            activity = Activity(
                id=activity_row[0],
                name=activity_row[2], 
                description=activity_row[3] or "",
                estimated_duration=activity_row[5] or 5,
                visual_cue=activity_row[6] or "",
                audio_cue=activity_row[7] or "",
                instructions=json.loads(activity_row[8]) if activity_row[8] else [],
                status=self._safe_activity_status(activity_row[9]),
                completed_at=datetime.fromisoformat(activity_row[10]) if activity_row[10] else None,
                created_at=datetime.fromisoformat(activity_row[11]) if activity_row[11] else None
            )
            activities.append(activity)
        
        # Handle different routine table schemas
        if len(routine_row) >= 10:
            # New schema with more columns
            return Routine(
                id=routine_row[0],
                child_id=routine_row[1],
                name=routine_row[2],
                description=routine_row[3] if len(routine_row) > 3 else "",
                activities=activities,
                schedule_time=routine_row[4] if len(routine_row) > 4 else None,
                days_of_week=json.loads(routine_row[5]) if len(routine_row) > 5 and routine_row[5] else [],
                active=bool(routine_row[6]) if len(routine_row) > 6 else True,
                created_at=datetime.fromisoformat(routine_row[8]) if len(routine_row) > 8 and routine_row[8] else None,
                updated_at=datetime.fromisoformat(routine_row[9]) if len(routine_row) > 9 and routine_row[9] else None
            )
        else:
            # Fallback for older/simpler schema
            return Routine(
                id=routine_row[0],
                child_id=routine_row[1],
                name=routine_row[2],
                description="",
                activities=activities,
                schedule_time=None,
                days_of_week=[],
                active=True,
                created_at=None,
                updated_at=None
            )
