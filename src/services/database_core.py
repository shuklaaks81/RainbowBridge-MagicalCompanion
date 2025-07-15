"""
Database core operations for Rainbow Bridge
Handles database initialization and basic CRUD operations.
"""

import sqlite3
import aiosqlite
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import asdict
import logging

from src.models.entities import (
    Child, Routine, Activity, Interaction, Milestone, 
    ActivityLog, VisualCard, CommunicationLevel, 
    ActivityStatus, RoutineStatus
)

logger = logging.getLogger(__name__)


class DatabaseCore:
    """Core database operations and table management."""
    
    def __init__(self, db_path: str = "special_kids.db"):
        self.db_path = db_path
    
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
                category TEXT DEFAULT 'daily',
                activities TEXT,  -- JSON array of activity objects
                status TEXT DEFAULT 'inactive',
                current_activity_index INTEGER DEFAULT 0,
                scheduled_time TEXT,
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
                type TEXT DEFAULT 'task',
                sequence_order INTEGER NOT NULL,
                estimated_duration INTEGER DEFAULT 5,
                instructions TEXT,
                visual_aids TEXT,  -- JSON array
                status TEXT DEFAULT 'pending',
                completed_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
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
                activity_id INTEGER,
                routine_id INTEGER,
                name TEXT NOT NULL,
                description TEXT,
                image_path TEXT,
                category TEXT DEFAULT 'general',
                usage_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (activity_id) REFERENCES activities (id),
                FOREIGN KEY (routine_id) REFERENCES routines (id)
            )
        """)
    
    async def execute_query(self, query: str, params: Tuple = ()) -> List[Tuple]:
        """Execute a SELECT query and return results."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(query, params)
            return await cursor.fetchall()
    
    async def execute_update(self, query: str, params: Tuple = ()) -> int:
        """Execute an INSERT/UPDATE/DELETE query and return affected rows."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(query, params)
            await db.commit()
            return cursor.rowcount
    
    async def get_last_insert_id(self, query: str, params: Tuple = ()) -> int:
        """Execute an INSERT query and return the last inserted ID."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(query, params)
            await db.commit()
            return cursor.lastrowid
