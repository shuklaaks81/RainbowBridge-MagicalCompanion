"""
Database Manager - Handles all data persistence for the Special Kids Assistant

This module manages SQLite database operations for storing child profiles,
interactions, routines, progress data, and milestones.
"""

import sqlite3
import aiosqlite
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import asdict
import logging

from core.routine_manager import Routine, Activity
from core.progress_tracker import Interaction, Milestone

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages all database operations for the Special Kids Assistant."""
    
    def __init__(self, db_path: str = "special_kids.db"):
        self.db_path = db_path
    
    async def initialize(self):
        """Initialize the database with required tables."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
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
                        profile_picture TEXT DEFAULT 'default.svg',  -- Profile picture filename
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
                        activities TEXT NOT NULL,  -- JSON array of activities
                        schedule_time TEXT NOT NULL,
                        days_of_week TEXT NOT NULL,  -- JSON array
                        active BOOLEAN DEFAULT TRUE,
                        total_activities INTEGER DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (child_id) REFERENCES children (id)
                    )
                """)
                
                # Interactions table
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS interactions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        child_id INTEGER NOT NULL,
                        interaction_type TEXT NOT NULL,
                        content TEXT NOT NULL,
                        response TEXT NOT NULL,
                        success BOOLEAN NOT NULL,
                        duration_seconds INTEGER,
                        emotion_detected TEXT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (child_id) REFERENCES children (id)
                    )
                """)
                
                # Milestones table
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS milestones (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        child_id INTEGER NOT NULL,
                        category TEXT NOT NULL,
                        description TEXT NOT NULL,
                        achieved BOOLEAN DEFAULT FALSE,
                        achieved_date TIMESTAMP,
                        target_date TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (child_id) REFERENCES children (id)
                    )
                """)
                
                # Routine sessions table
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS routine_sessions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        routine_id INTEGER NOT NULL,
                        child_id INTEGER NOT NULL,
                        started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        completed_at TIMESTAMP,
                        current_activity INTEGER DEFAULT 0,
                        total_activities INTEGER NOT NULL,
                        status TEXT DEFAULT 'in_progress',  -- in_progress, completed, abandoned
                        progress REAL DEFAULT 0.0,
                        FOREIGN KEY (routine_id) REFERENCES routines (id),
                        FOREIGN KEY (child_id) REFERENCES children (id)
                    )
                """)
                
                # Activity completions table
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS activity_completions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        child_id INTEGER NOT NULL,
                        activity_name TEXT NOT NULL,
                        completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        duration_seconds INTEGER,
                        difficulty_rating INTEGER,  -- 1-5 scale
                        enjoyment_rating INTEGER,  -- 1-5 scale
                        FOREIGN KEY (child_id) REFERENCES children (id)
                    )
                """)
                
                # Activity logs table (for detailed activity tracking)
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS activity_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        child_id INTEGER NOT NULL,
                        routine_id INTEGER,
                        activity_name TEXT NOT NULL,
                        action TEXT NOT NULL,  -- started, completed, skipped
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        notes TEXT,
                        FOREIGN KEY (child_id) REFERENCES children (id),
                        FOREIGN KEY (routine_id) REFERENCES routines (id)
                    )
                """)
                
                # Progress snapshots table (for historical tracking)
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS progress_snapshots (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        child_id INTEGER NOT NULL,
                        snapshot_date DATE NOT NULL,
                        communication_score REAL,
                        routine_adherence REAL,
                        learning_engagement REAL,
                        social_interaction REAL,
                        overall_progress REAL,
                        notes TEXT,
                        FOREIGN KEY (child_id) REFERENCES children (id)
                    )
                """)
                
                await db.commit()
                
                # Add profile_picture column if it doesn't exist (migration)
                try:
                    await db.execute("""
                        ALTER TABLE children ADD COLUMN profile_picture TEXT DEFAULT 'default.svg'
                    """)
                    await db.commit()
                    logger.info("Added profile_picture column to children table")
                except Exception:
                    # Column already exists, ignore
                    pass
                
                logger.info("Database initialized successfully")
        
        except Exception as e:
            logger.error(f"Failed to initialize database: {str(e)}")
            raise
    
    async def create_child(self, child_data: Dict[str, Any]) -> int:
        """Create a new child profile."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("""
                    INSERT INTO children (name, age, communication_level, interests, special_needs, preferences)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    child_data["name"],
                    child_data["age"],
                    child_data["communication_level"],
                    json.dumps(child_data.get("interests", [])),
                    json.dumps(child_data.get("special_needs", [])),
                    json.dumps(child_data.get("preferences", {}))
                ))
                
                child_id = cursor.lastrowid
                await db.commit()
                
                logger.info(f"Created child profile: {child_data['name']} (ID: {child_id})")
                return child_id
        
        except Exception as e:
            logger.error(f"Failed to create child: {str(e)}")
            raise

    async def fetch_all(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Execute a query and return all results as a list of dictionaries."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                cursor = await db.execute(query, params)
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Failed to fetch all rows: {str(e)}")
            return []

    async def fetch_one(self, query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
        """Execute a query and return one result as a dictionary."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                cursor = await db.execute(query, params)
                row = await cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"Failed to fetch one row: {str(e)}")
            return None

    async def execute_query(self, query: str, params: tuple = ()) -> bool:
        """Execute a query and return success status."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(query, params)
                await db.commit()
                return True
        except Exception as e:
            logger.error(f"Failed to execute query: {str(e)}")
            return False
    
    async def get_child(self, child_id: int) -> Optional[Dict[str, Any]]:
        """Get a child's profile by ID."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                cursor = await db.execute("""
                    SELECT * FROM children WHERE id = ?
                """, (child_id,))
                
                row = await cursor.fetchone()
                if row:
                    child_data = dict(row)
                    child_data["interests"] = json.loads(child_data.get("interests", "[]"))
                    child_data["special_needs"] = json.loads(child_data.get("special_needs", "[]"))
                    child_data["preferences"] = json.loads(child_data.get("preferences", "{}"))
                    return child_data
                
                return None
        
        except Exception as e:
            logger.error(f"Failed to get child {child_id}: {str(e)}")
            return None
    
    async def save_routine(self, routine: Routine) -> int:
        """Save a routine to the database."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Convert activities to JSON
                activities_json = json.dumps([asdict(activity) for activity in routine.activities])
                days_json = json.dumps(routine.days_of_week)
                
                cursor = await db.execute("""
                    INSERT INTO routines (
                        child_id, name, activities, schedule_time, days_of_week, active, total_activities, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    routine.child_id,
                    routine.name,
                    activities_json,
                    routine.schedule_time,
                    days_json,
                    routine.active,
                    len(routine.activities),  # total_activities count
                    routine.created_at or datetime.now()
                ))
                
                await db.commit()
                return cursor.lastrowid
                
        except Exception as e:
            logger.error(f"Failed to save routine: {str(e)}")
            raise
    
    async def get_routine(self, routine_id: int) -> Optional[Dict]:
        """Get a routine by ID."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                cursor = await db.execute("""
                    SELECT * FROM routines WHERE id = ?
                """, (routine_id,))
                
                row = await cursor.fetchone()
                if row:
                    routine_dict = dict(row)
                    # Parse JSON fields
                    routine_dict["activities"] = json.loads(routine_dict["activities"])
                    routine_dict["days_of_week"] = json.loads(routine_dict["days_of_week"])
                    return routine_dict
                
                return None
                
        except Exception as e:
            logger.error(f"Failed to get routine {routine_id}: {str(e)}")
            return None
    
    async def get_routines_by_child(self, child_id: int) -> List[Dict]:
        """Get all routines for a specific child."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                cursor = await db.execute("""
                    SELECT * FROM routines WHERE child_id = ? ORDER BY created_at DESC
                """, (child_id,))
                
                rows = await cursor.fetchall()
                routines = []
                
                for row in rows:
                    routine_dict = dict(row)
                    # Parse JSON fields
                    routine_dict["activities"] = json.loads(routine_dict["activities"])
                    routine_dict["days_of_week"] = json.loads(routine_dict["days_of_week"])
                    routines.append(routine_dict)
                
                return routines
                
        except Exception as e:
            logger.error(f"Failed to get routines for child {child_id}: {str(e)}")
            return []
    
    async def update_routine(self, routine_id: int, routine_data: Dict) -> bool:
        """Update a routine in the database."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Convert activities to JSON if present
                if "activities" in routine_data:
                    routine_data["activities"] = json.dumps(routine_data["activities"])
                if "days_of_week" in routine_data:
                    routine_data["days_of_week"] = json.dumps(routine_data["days_of_week"])
                
                # Build dynamic update query
                fields = ", ".join([f"{key} = ?" for key in routine_data.keys()])
                values = list(routine_data.values()) + [routine_id]
                
                await db.execute(f"""
                    UPDATE routines SET {fields}, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, values)
                
                await db.commit()
                return True
                
        except Exception as e:
            logger.error(f"Failed to update routine {routine_id}: {str(e)}")
            return False
    
    async def create_routine_session(self, session_data: Dict) -> int:
        """Create a new routine session."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("""
                    INSERT INTO routine_sessions (
                        routine_id, child_id, started_at, current_activity, total_activities, status, progress
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    session_data["routine_id"],
                    session_data["child_id"],
                    session_data["started_at"],
                    session_data["current_activity"],
                    session_data["total_activities"],
                    session_data["status"],
                    session_data["progress"]
                ))
                
                await db.commit()
                return cursor.lastrowid
                
        except Exception as e:
            logger.error(f"Failed to create routine session: {str(e)}")
            raise
    
    async def update_routine_session(self, session_id: int, updates: Dict) -> bool:
        """Update a routine session."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Build dynamic update query
                fields = ", ".join([f"{key} = ?" for key in updates.keys()])
                values = list(updates.values()) + [session_id]
                
                await db.execute(f"""
                    UPDATE routine_sessions SET {fields}
                    WHERE id = ?
                """, values)
                
                await db.commit()
                return True
                
        except Exception as e:
            logger.error(f"Failed to update routine session {session_id}: {str(e)}")
            return False
    
    async def get_active_routine_sessions(self, child_id: int) -> List[Dict]:
        """Get active routine sessions for a child."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                cursor = await db.execute("""
                    SELECT rs.*, r.name as routine_name
                    FROM routine_sessions rs
                    JOIN routines r ON rs.routine_id = r.id
                    WHERE rs.child_id = ? AND rs.completed_at IS NULL
                    ORDER BY rs.started_at DESC
                """, (child_id,))
                
                rows = await cursor.fetchall()
                sessions = []
                
                for row in rows:
                    sessions.append({
                        "id": row[0],
                        "routine_id": row[1],
                        "child_id": row[2],
                        "started_at": row[3],
                        "completed_at": row[4],
                        "current_activity": row[5],
                        "total_activities": row[6],
                        "status": row[7],
                        "progress": row[8],
                        "routine_name": row[9]
                    })
                
                return sessions
                
        except Exception as e:
            logger.error(f"Failed to get active routine sessions for child {child_id}: {str(e)}")
            return []

    async def get_routine_activities(self, routine_id: int) -> List[Dict]:
        """Get activities for a specific routine."""
        try:
            routine_data = await self.get_routine(routine_id)
            if routine_data and "activities" in routine_data:
                return routine_data["activities"]
            return []
        except Exception as e:
            logger.error(f"Failed to get activities for routine {routine_id}: {str(e)}")
            return []

    async def get_child_routines(self, child_id: int) -> List[Dict]:
        """Get all routines for a child (alias for get_routines_by_child)."""
        return await self.get_routines_by_child(child_id)

    async def update_routine_activity_status(self, routine_id: int, activity_index: int, completed: bool) -> bool:
        """Update the completion status of an activity in a routine."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Get current routine
                cursor = await db.execute("""
                    SELECT activities FROM routines WHERE id = ?
                """, (routine_id,))
                
                row = await cursor.fetchone()
                if not row:
                    return False
                
                # Parse activities and update the status
                activities = json.loads(row[0])
                if 0 <= activity_index < len(activities):
                    activities[activity_index]["completed"] = completed
                    
                    # Save back to database
                    await db.execute("""
                        UPDATE routines SET activities = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE id = ?
                    """, (json.dumps(activities), routine_id))
                    
                    await db.commit()
                    return True
                
                return False
                
        except Exception as e:
            logger.error(f"Failed to update activity status: {str(e)}")
            return False
    
    async def log_activity_completion(self, child_id: int, activity_name: str, routine_id: int = None, completed_at: datetime = None) -> bool:
        """Log an activity completion."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT INTO activity_logs (
                        child_id, activity_name, routine_id, completed_at
                    ) VALUES (?, ?, ?, ?)
                """, (
                    child_id,
                    activity_name,
                    routine_id,
                    completed_at or datetime.now()
                ))
                
                await db.commit()
                return True
                
        except Exception as e:
            logger.error(f"Failed to log activity completion: {str(e)}")
            return False
    
    async def get_interactions_by_date_range(
        self,
        child_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> List[Interaction]:
        """Get interactions for a child within a date range."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                cursor = await db.execute("""
                    SELECT * FROM interactions 
                    WHERE child_id = ? AND timestamp BETWEEN ? AND ?
                    ORDER BY timestamp DESC
                """, (child_id, start_date.isoformat(), end_date.isoformat()))
                
                rows = await cursor.fetchall()
                interactions = []
                
                for row in rows:
                    interaction_data = dict(row)
                    interaction = Interaction(
                        id=interaction_data["id"],
                        child_id=interaction_data["child_id"],
                        interaction_type=interaction_data["interaction_type"],
                        content=interaction_data["content"],
                        response=interaction_data["response"],
                        success=interaction_data["success"],
                        duration_seconds=interaction_data["duration_seconds"],
                        emotion_detected=interaction_data["emotion_detected"],
                        timestamp=datetime.fromisoformat(interaction_data["timestamp"])
                    )
                    interactions.append(interaction)
                
                return interactions
        
        except Exception as e:
            logger.error(f"Failed to get interactions: {str(e)}")
            return []
    
    async def get_recent_interactions(self, child_id: int, days: int = 7) -> List[Interaction]:
        """Get recent interactions for a child."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        return await self.get_interactions_by_date_range(child_id, start_date, end_date)
    
    async def save_milestone(self, milestone: Milestone) -> int:
        """Save a milestone to the database."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("""
                    INSERT INTO milestones (child_id, category, description, achieved, achieved_date, target_date)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    milestone.child_id,
                    milestone.category,
                    milestone.description,
                    milestone.achieved,
                    milestone.achieved_date.isoformat() if milestone.achieved_date else None,
                    milestone.target_date.isoformat() if milestone.target_date else None
                ))
                
                milestone_id = cursor.lastrowid
                await db.commit()
                
                return milestone_id
        
        except Exception as e:
            logger.error(f"Failed to save milestone: {str(e)}")
            raise
    
    async def get_child_milestones(self, child_id: int) -> List[Milestone]:
        """Get all milestones for a child."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                cursor = await db.execute("""
                    SELECT * FROM milestones WHERE child_id = ?
                    ORDER BY created_at DESC
                """, (child_id,))
                
                rows = await cursor.fetchall()
                milestones = []
                
                for row in rows:
                    milestone_data = dict(row)
                    milestone = Milestone(
                        id=milestone_data["id"],
                        child_id=milestone_data["child_id"],
                        category=milestone_data["category"],
                        description=milestone_data["description"],
                        achieved=milestone_data["achieved"],
                        achieved_date=datetime.fromisoformat(milestone_data["achieved_date"]) if milestone_data["achieved_date"] else None,
                        target_date=datetime.fromisoformat(milestone_data["target_date"]) if milestone_data["target_date"] else None
                    )
                    milestones.append(milestone)
                
                return milestones
        
        except Exception as e:
            logger.error(f"Failed to get milestones for child {child_id}: {str(e)}")
            return []
    
    async def save_interaction(self, interaction: Interaction) -> int:
        """Save an interaction to the database."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("""
                    INSERT INTO interactions (child_id, interaction_type, content, response, success, duration_seconds, emotion_detected, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    interaction.child_id,
                    interaction.interaction_type,
                    interaction.content,
                    interaction.response,
                    interaction.success,
                    interaction.duration_seconds,
                    interaction.emotion_detected,
                    interaction.timestamp.isoformat()
                ))
                
                interaction_id = cursor.lastrowid
                await db.commit()
                
                return interaction_id
        
        except Exception as e:
            logger.error(f"Failed to save interaction: {str(e)}")
            raise
    
    async def save_progress_snapshot(
        self,
        child_id: int,
        snapshot_date: datetime,
        communication_score: float,
        routine_adherence: float,
        learning_engagement: float,
        social_interaction: float,
        overall_progress: float,
        notes: Optional[str] = None
    ):
        """Save a progress snapshot for historical tracking."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT OR REPLACE INTO progress_snapshots 
                    (child_id, snapshot_date, communication_score, routine_adherence, 
                     learning_engagement, social_interaction, overall_progress, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    child_id,
                    snapshot_date.date().isoformat(),
                    communication_score,
                    routine_adherence,
                    learning_engagement,
                    social_interaction,
                    overall_progress,
                    notes
                ))
                
                await db.commit()
        
        except Exception as e:
            logger.error(f"Failed to save progress snapshot: {str(e)}")
            raise
    
    async def get_progress_history(
        self,
        child_id: int,
        days: int = 90
    ) -> List[Dict[str, Any]]:
        """Get progress history for a child."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                end_date = datetime.now().date()
                start_date = end_date - timedelta(days=days)
                
                cursor = await db.execute("""
                    SELECT * FROM progress_snapshots 
                    WHERE child_id = ? AND snapshot_date BETWEEN ? AND ?
                    ORDER BY snapshot_date DESC
                """, (child_id, start_date.isoformat(), end_date.isoformat()))
                
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
        
        except Exception as e:
            logger.error(f"Failed to get progress history: {str(e)}")
            return []
    
    async def get_all_children(self) -> List[Dict[str, Any]]:
        """Get all children profiles."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                cursor = await db.execute("""
                    SELECT id, name, age, communication_level, created_at FROM children
                    ORDER BY name
                """)
                
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
        
        except Exception as e:
            logger.error(f"Failed to get all children: {str(e)}")
            return []
