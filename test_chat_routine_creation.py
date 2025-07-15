#!/usr/bin/env python3
"""
🧪 Test Chat Routine Creation
============================

Test the chat system's ability to create routines.
"""

import asyncio
import sys
import os
import json

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_chat_routine_creation():
    """Test routine creation through chat"""
    print("🧪 Testing chat routine creation...")
    
    try:
        from core.ai_assistant import SpecialKidsAI
        from core.routine_manager import RoutineManager
        from database.db_manager import DatabaseManager
        from core.routine_mcp_server import create_routine_mcp_server
        
        # Initialize components
        db_manager = DatabaseManager("special_kids.db")
        await db_manager.initialize()
        
        routine_manager = RoutineManager(db_manager)
        routine_mcp_server = create_routine_mcp_server(routine_manager, db_manager)
        ai_assistant = SpecialKidsAI(routine_mcp_server)
        
        # Test messages that should create routines
        test_messages = [
            "I want to create a morning routine",
            "Can you help me make a bedtime routine?",
            "Create a new routine for getting ready",
            "I need a routine called 'Homework Time'",
            "Schedule a routine for after school"
        ]
        
        for i, message in enumerate(test_messages, 1):
            print(f"\n🧪 Test {i}: '{message}'")
            
            response = await ai_assistant.process_message(
                message=message,
                child_id=1,
                communication_type="text",
                child_preferences={"visual_support": True, "routine_focus": True}
            )
            
            print(f"Response: {response.get('text', 'No response')}")
            print(f"Visual cues: {response.get('visual_cues', [])}")
            print(f"LLM source: {response.get('llm_source', 'unknown')}")
            
            if 'routine_action' in response:
                print(f"✅ Routine action detected: {response['routine_action']}")
            else:
                print("❌ No routine action detected")
        
        # Test a specific routine creation
        print(f"\n🧪 Specific Test: Direct routine creation")
        response = await ai_assistant.process_message(
            message="Create a routine called 'Afternoon Fun Time' for 3pm",
            child_id=1,
            communication_type="text"
        )
        
        print(f"Response: {response.get('text', 'No response')}")
        print(f"Success: {'routine_action' in response}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_chat_routine_creation())
