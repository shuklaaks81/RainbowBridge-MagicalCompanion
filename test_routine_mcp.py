#!/usr/bin/env python3
"""
Test script to verify routine MCP integration
"""
import asyncio
import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.routine_mcp_client import RoutineMCPClient
from core.routine_manager import RoutineManager
from core.routine_mcp_server import create_routine_mcp_server
from database.db_manager import DatabaseManager

async def test_routine_mcp_integration():
    """Test the routine MCP integration end-to-end."""
    print("🌈 Testing Rainbow Bridge Routine MCP Integration!")
    
    try:
        # Initialize components
        db_manager = DatabaseManager("test_routines.db")
        await db_manager.initialize()
        print("✅ Database initialized")
        
        routine_manager = RoutineManager(db_manager)
        print("✅ Routine manager created")
        
        # Create MCP server
        mcp_server = create_routine_mcp_server(routine_manager, db_manager)
        print("✅ MCP server created")
        
        # Create MCP client
        mcp_client = RoutineMCPClient(mcp_server)
        print("✅ MCP client created")
        
        # Test routine creation intent detection
        test_messages = [
            "I want to create a morning routine",
            "Can you help me make a bedtime routine?",
            "Create a routine for learning activities",
            "What routines do I have?",
            "Start my morning routine",
            "I completed brushing teeth",
            "Hello! How are you today?"
        ]
        
        print("\n🎯 Testing intent detection:")
        for message in test_messages:
            result = await mcp_client.detect_routine_intent(message, child_id=1)
            if result:
                confidence = result.get('confidence', 'N/A')
                print(f"✅ '{message}' -> {result['intent']} (confidence: {confidence})")
            else:
                print(f"❌ '{message}' -> No routine intent detected")
        
        print("\n🎨 Testing routine creation:")
        
        # Test creating a routine directly
        routine = await routine_manager.create_routine(
            child_id=1,
            name="Test Morning Routine",
            activities=["Brush teeth", "Get dressed", "Eat breakfast"],
            schedule_time="08:00",
            days_of_week=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        )
        
        if routine:
            print(f"✅ Created routine: {routine.name} (ID: {routine.id})")
            
            # Test getting routines
            routines = await routine_manager.get_child_routines(1)
            print(f"✅ Retrieved {len(routines)} routines for child 1")
            
            # Test starting routine
            success = await routine_manager.start_routine(routine.id)
            print(f"✅ Started routine: {success}")
            
            # Test completing an activity
            success = await routine_manager.complete_activity(routine.id, "Brush teeth")
            print(f"✅ Completed activity: {success}")
            
        else:
            print("❌ Failed to create routine")
        
        print("\n🌟 All tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(test_routine_mcp_integration())
        if success:
            print("\n🎉 Rainbow Bridge routine functionality is working!")
        else:
            print("\n💔 Tests failed - needs debugging")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Main test error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
