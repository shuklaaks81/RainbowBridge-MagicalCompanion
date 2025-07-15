"""
Child management service for Rainbow Bridge
Handles child profile operations and related data management.
"""

import json
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging

from src.models.entities import Child, CommunicationLevel, VisualCard
from src.services.database_core import DatabaseCore

logger = logging.getLogger(__name__)


class ChildManager:
    """Service for managing child profiles and related operations."""
    
    def __init__(self, db_core: DatabaseCore):
        self.db_core = db_core
    
    async def get_child_profile(self, child_id: int) -> Optional[Child]:
        """Get a child profile by ID."""
        rows = await self.db_core.execute_query(
            "SELECT * FROM children WHERE id = ?", (child_id,)
        )
        
        if not rows:
            return None
        
        row = rows[0]
        return Child(
            id=row[0],
            name=row[1],
            age=row[2],
            communication_level=CommunicationLevel(row[3]),
            interests=json.loads(row[4]) if row[4] else [],
            created_at=datetime.fromisoformat(row[5]) if row[5] else None,
            updated_at=datetime.fromisoformat(row[6]) if row[6] else None
        )
    
    async def create_child_profile(self, child: Child) -> int:
        """Create a new child profile."""
        return await self.db_core.get_last_insert_id("""
            INSERT INTO children (
                name, age, communication_level, interests,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """, (
            child.name, child.age, child.communication_level.value,
            json.dumps(child.interests)
        ))
    
    async def update_child_profile(self, child_id: int, updates: Dict[str, Any]) -> bool:
        """Update a child profile with the given changes."""
        
        # Build dynamic update query
        set_clauses = []
        params = []
        
        for field, value in updates.items():
            if field in ['name', 'age', 'communication_level']:
                set_clauses.append(f"{field} = ?")
                params.append(value)
            elif field == 'interests':
                set_clauses.append("interests = ?")
                params.append(json.dumps(value))
        
        if not set_clauses:
            return False
        
        set_clauses.append("updated_at = CURRENT_TIMESTAMP")
        params.append(child_id)
        
        query = f"UPDATE children SET {', '.join(set_clauses)} WHERE id = ?"
        
        await self.db_core.execute_update(query, tuple(params))
        return True
    
    async def get_all_children(self) -> List[Child]:
        """Get all child profiles."""
        rows = await self.db_core.execute_query(
            "SELECT * FROM children ORDER BY created_at DESC"
        )
        
        children = []
        for row in rows:
            child = Child(
                id=row[0],
                name=row[1],
                age=row[2],
                communication_level=CommunicationLevel(row[3]),
                interests=json.loads(row[4]) if row[4] else [],
                created_at=datetime.fromisoformat(row[5]) if row[5] else None,
                updated_at=datetime.fromisoformat(row[6]) if row[6] else None
            )
            children.append(child)
        
        return children
    
    async def delete_child_profile(self, child_id: int) -> bool:
        """Delete a child profile and all related data."""
        
        # Delete in order to respect foreign key constraints
        tables_to_clean = [
            "activity_logs",
            "interactions", 
            "milestones",
            "visual_cards",
            "activities",
            "routines"
        ]
        
        for table in tables_to_clean:
            if table in ["activities", "visual_cards"]:
                # These reference routines, need to delete via routine_id
                await self.db_core.execute_update(f"""
                    DELETE FROM {table} WHERE routine_id IN (
                        SELECT id FROM routines WHERE child_id = ?
                    )
                """, (child_id,))
            else:
                await self.db_core.execute_update(
                    f"DELETE FROM {table} WHERE child_id = ?", (child_id,)
                )
        
        # Finally delete the child profile
        rows_affected = await self.db_core.execute_update(
            "DELETE FROM children WHERE id = ?", (child_id,)
        )
        
        return rows_affected > 0
    
    async def get_child_visual_cards(self, child_id: int) -> List[VisualCard]:
        """Get visual cards associated with a child's routines."""
        rows = await self.db_core.execute_query("""
            SELECT vc.* FROM visual_cards vc
            LEFT JOIN routines r ON vc.routine_id = r.id
            WHERE r.child_id = ? OR vc.routine_id IS NULL
            ORDER BY vc.usage_count DESC, vc.created_at DESC
        """, (child_id,))
        
        visual_cards = []
        for row in rows:
            card = VisualCard(
                id=row[0],
                activity_id=row[1],
                routine_id=row[2],
                name=row[3],
                description=row[4] or "",
                image_path=row[5] or "",
                category=row[6] or "general",
                usage_count=row[7] or 0,
                created_at=datetime.fromisoformat(row[8]) if row[8] else None
            )
            visual_cards.append(card)
        
        return visual_cards
    
    async def create_visual_card(self, visual_card: VisualCard) -> int:
        """Create a new visual card."""
        return await self.db_core.get_last_insert_id("""
            INSERT INTO visual_cards (
                activity_id, routine_id, name, description,
                image_path, category, usage_count, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (
            visual_card.activity_id, visual_card.routine_id,
            visual_card.name, visual_card.description,
            visual_card.image_path, visual_card.category,
            visual_card.usage_count
        ))
    
    async def increment_card_usage(self, card_id: int) -> bool:
        """Increment the usage count for a visual card."""
        rows_affected = await self.db_core.execute_update(
            "UPDATE visual_cards SET usage_count = usage_count + 1 WHERE id = ?",
            (card_id,)
        )
        return rows_affected > 0
    
    async def get_child_context_summary(self, child_id: int) -> Dict[str, Any]:
        """Get a comprehensive context summary for a child."""
        
        # Get child profile
        child = await self.get_child_profile(child_id)
        if not child:
            return {}
        
        # Get recent interactions count
        interaction_rows = await self.db_core.execute_query("""
            SELECT COUNT(*) FROM interactions 
            WHERE child_id = ? AND timestamp >= datetime('now', '-7 days')
        """, (child_id,))
        
        # Get routine count and status
        routine_rows = await self.db_core.execute_query("""
            SELECT COUNT(*) as total, 
                   SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) as active
            FROM routines WHERE child_id = ?
        """, (child_id,))
        
        # Get recent milestones
        milestone_rows = await self.db_core.execute_query("""
            SELECT COUNT(*) FROM milestones 
            WHERE child_id = ? AND achieved_at >= datetime('now', '-30 days')
        """, (child_id,))
        
        total_routines = routine_rows[0][0] if routine_rows else 0
        active_routines = routine_rows[0][1] if routine_rows else 0
        recent_interactions = interaction_rows[0][0] if interaction_rows else 0
        recent_milestones = milestone_rows[0][0] if milestone_rows else 0
        
        return {
            'child_profile': {
                'id': child.id,
                'name': child.name,
                'age': child.age,
                'communication_level': child.communication_level.value,
                'interests': child.interests
            },
            'activity_summary': {
                'total_routines': total_routines,
                'active_routines': active_routines,
                'recent_interactions': recent_interactions,
                'recent_milestones': recent_milestones
            },
            'last_updated': datetime.now().isoformat()
        }
