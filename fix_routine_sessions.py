#!/usr/bin/env python3
"""Fix routine sessions to reflect actual activity completion status."""

import asyncio
import aiosqlite
import json

async def fix_routine_sessions():
    """Update routine sessions to match activity completion status."""
    async with aiosqlite.connect("special_kids.db") as db:
        # Get all in-progress routine sessions
        cursor = await db.execute("""
            SELECT rs.id, rs.routine_id, rs.current_activity, r.activities 
            FROM routine_sessions rs
            JOIN routines r ON rs.routine_id = r.id
            WHERE rs.status = 'in_progress'
        """)
        sessions = await cursor.fetchall()
        
        for session_id, routine_id, current_activity, activities_json in sessions:
            print(f"Checking session {session_id} for routine {routine_id}")
            
            try:
                activities = json.loads(activities_json) if activities_json else []
                total_activities = len(activities)
                completed_activities = sum(1 for act in activities if act.get('completed', False))
                progress = (completed_activities / total_activities * 100) if total_activities > 0 else 0
                
                print(f"  Activities: {completed_activities}/{total_activities} completed ({progress:.1f}%)")
                
                if completed_activities == total_activities:
                    # All activities completed - mark session as completed
                    print(f"  -> Marking session as completed")
                    await db.execute("""
                        UPDATE routine_sessions 
                        SET status = 'completed', 
                            progress = 100.0, 
                            current_activity = ?,
                            completed_at = CURRENT_TIMESTAMP
                        WHERE id = ?
                    """, (total_activities - 1, session_id))
                else:
                    # Find first incomplete activity
                    next_activity_index = 0
                    for i, activity in enumerate(activities):
                        if not activity.get('completed', False):
                            next_activity_index = i
                            break
                    
                    print(f"  -> Updating current activity to {next_activity_index}, progress to {progress:.1f}%")
                    await db.execute("""
                        UPDATE routine_sessions 
                        SET current_activity = ?, 
                            progress = ?
                        WHERE id = ?
                    """, (next_activity_index, progress, session_id))
                
            except (json.JSONDecodeError, TypeError) as e:
                print(f"  Error parsing activities: {e}")
        
        await db.commit()
        print("Routine sessions updated successfully!")

if __name__ == "__main__":
    asyncio.run(fix_routine_sessions())
