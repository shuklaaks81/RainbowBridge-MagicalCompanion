#!/usr/bin/env python3
"""Sync routine sessions with actual activity completion status."""

import asyncio
import aiosqlite
import json

async def sync_routine_sessions():
    """Update routine sessions to match actual activity completion from JSON."""
    
    async with aiosqlite.connect("special_kids.db") as db:
        print("=== Syncing Routine Sessions with Activity Status ===\n")
        
        # Get all in-progress routine sessions
        cursor = await db.execute("""
            SELECT rs.id, rs.routine_id, rs.child_id, rs.current_activity, rs.total_activities, rs.status, rs.progress,
                   r.name, r.activities
            FROM routine_sessions rs
            JOIN routines r ON rs.routine_id = r.id
            WHERE rs.status = 'in_progress'
            ORDER BY rs.child_id, rs.routine_id
        """)
        sessions = await cursor.fetchall()
        
        for session_data in sessions:
            session_id, routine_id, child_id, current_activity, total_activities, status, progress, routine_name, activities_json = session_data
            
            print(f"Session {session_id}: {routine_name}")
            print(f"  Current state: activity {current_activity}/{total_activities}, {progress}% progress")
            
            try:
                activities = json.loads(activities_json) if activities_json else []
                actual_total = len(activities)
                completed_count = sum(1 for a in activities if a.get('completed', False))
                actual_progress = (completed_count / actual_total * 100) if actual_total > 0 else 0
                
                # Find current activity index (first incomplete activity)
                current_activity_index = 0
                current_activity_name = "Unknown"
                
                for i, activity in enumerate(activities):
                    if not activity.get('completed', False):
                        current_activity_index = i
                        current_activity_name = activity.get('name', f'Activity {i+1}')
                        break
                
                # If all activities are completed
                if completed_count == actual_total:
                    print(f"  -> All activities completed! Marking session as completed")
                    await db.execute("""
                        UPDATE routine_sessions 
                        SET status = 'completed', 
                            progress = 100.0, 
                            current_activity = ?,
                            completed_at = CURRENT_TIMESTAMP
                        WHERE id = ?
                    """, (actual_total - 1, session_id))
                else:
                    print(f"  -> Actual progress: {completed_count}/{actual_total} ({actual_progress:.1f}%)")
                    print(f"  -> Current activity: {current_activity_index} - {current_activity_name}")
                    
                    await db.execute("""
                        UPDATE routine_sessions 
                        SET current_activity = ?, 
                            total_activities = ?,
                            progress = ?
                        WHERE id = ?
                    """, (current_activity_index, actual_total, actual_progress, session_id))
                
            except (json.JSONDecodeError, TypeError) as e:
                print(f"  -> Error parsing activities: {e}")
            
            print()
        
        await db.commit()
        
        # Show final state
        print("=== Final State ===")
        cursor = await db.execute("""
            SELECT rs.id, rs.routine_id, rs.child_id, rs.current_activity, rs.total_activities, rs.status, rs.progress,
                   r.name, c.name as child_name
            FROM routine_sessions rs
            JOIN routines r ON rs.routine_id = r.id
            JOIN children c ON rs.child_id = c.id
            ORDER BY rs.child_id, rs.routine_id
        """)
        sessions = await cursor.fetchall()
        
        for session_data in sessions:
            session_id, routine_id, child_id, current_activity, total_activities, status, progress, routine_name, child_name = session_data
            print(f"Session {session_id}: {child_name} - {routine_name}")
            print(f"  Status: {status}, Activity: {current_activity}/{total_activities}, Progress: {progress}%")
        
        print("\n✅ Routine sessions synchronized!")

if __name__ == "__main__":
    asyncio.run(sync_routine_sessions())
