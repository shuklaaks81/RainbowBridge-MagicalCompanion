#!/usr/bin/env python3
"""
Debug script to trace activity completion issues
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.routine_manager import RoutineManager
from core.routine_mcp_client import RoutineMCPClient
from core.routine_mcp_server import RoutineMCPServer
from database.db_manager import DatabaseManager
import logging

# Set up detailed logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def debug_activity_completion():
    """Debug the activity completion process step by step."""
    print("🔍 Debugging Activity Completion Process")
    print("=" * 60)
    
    # Initialize components
    db = DatabaseManager()
    routine_manager = RoutineManager(db)
    mcp_server = RoutineMCPServer(routine_manager, db)
    mcp_client = RoutineMCPClient(mcp_server)
    
    # Create a test routine
    print("\n1️⃣ Creating test routine...")
    activities = ["Wake Up", "Get Dressed", "Eat Breakfast"]
    
    routine = await routine_manager.create_routine(
        child_id=1,
        name="Morning Routine",
        activities=activities,
        schedule_time="08:00",
        days_of_week=["Monday"]
    )
    routine_id = routine.id
    print(f"✅ Created routine ID: {routine_id}")
    
    # Start the routine
    print("\n2️⃣ Starting routine...")
    success = await routine_manager.start_routine(routine_id)
    print(f"✅ Routine started: {success}")
    
    # Check active sessions
    print("\n3️⃣ Checking active sessions...")
    active_sessions = await db.get_active_routine_sessions(1)
    print(f"Active sessions: {active_sessions}")
    
    # Test activity extraction and completion
    test_phrases = [
        "I woke up",
        "Got dressed", 
        "Ate breakfast"
    ]
    
    for phrase in test_phrases:
        print(f"\n4️⃣ Testing phrase: '{phrase}'")
        
        # Test intent detection
        intent_result = await mcp_client.detect_routine_intent(phrase, 1)
        print(f"📍 Intent detected: {intent_result}")
        
        if intent_result and intent_result.get("intent") == "complete_activity":
            activity_name = intent_result.get("activity_name")
            print(f"📝 Extracted activity: '{activity_name}'")
            
            # Get current routine to see available activities
            current_routine = await routine_manager.get_routine(routine_id)
            available_activities = [a.name for a in current_routine.activities]
            print(f"🎯 Available activities: {available_activities}")
            
            # Test the completion directly
            success = await routine_manager.complete_activity(routine_id, activity_name)
            print(f"✅ Direct completion result: {success}")
            
            # Test through MCP
            try:
                mcp_result = await mcp_client.call_tool("complete_activity", intent_result)
                print(f"🔧 MCP completion result: {mcp_result}")
            except Exception as e:
                print(f"❌ MCP completion error: {e}")
        
        print("-" * 40)
    
    # Check final status
    print("\n5️⃣ Final routine status...")
    final_routine = await routine_manager.get_routine(routine_id)
    completed_count = sum(1 for a in final_routine.activities if a.completed)
    total_count = len(final_routine.activities)
    progress = (completed_count / total_count) * 100 if total_count > 0 else 0
    
    print(f"📊 Progress: {progress}% ({completed_count}/{total_count} completed)")
    for i, activity in enumerate(final_routine.activities):
        status = "✅" if activity.completed else "⏳"
        print(f"   {status} {activity.name}")

if __name__ == "__main__":
    asyncio.run(debug_activity_completion())
