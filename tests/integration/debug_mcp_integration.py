#!/usr/bin/env python3
"""
🔍 Debug MCP Integration
======================

Debug why MCP routine creation isn't triggering.
"""

import asyncio
import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def debug_mcp_integration():
    """Debug MCP integration step by step"""
    print("🔍 Debugging MCP integration...")
    
    try:
        from core.ai_assistant import SpecialKidsAI
        from core.routine_manager import RoutineManager
        from database.db_manager import DatabaseManager
        from core.routine_mcp_server import create_routine_mcp_server
        from core.routine_mcp_client import RoutineMCPClient
        
        # Initialize components
        db_manager = DatabaseManager("special_kids.db")
        await db_manager.initialize()
        
        routine_manager = RoutineManager(db_manager)
        routine_mcp_server = create_routine_mcp_server(routine_manager, db_manager)
        
        print(f"✅ MCP Server created: {type(routine_mcp_server)}")
        
        # Test MCP Client directly
        mcp_client = RoutineMCPClient(routine_mcp_server)
        print(f"✅ MCP Client created: {type(mcp_client)}")
        
        # Test intent detection
        test_message = "I want to create a morning routine"
        intent = await mcp_client.detect_routine_intent(test_message, 1)
        print(f"🧪 Intent detection for '{test_message}': {intent}")
        
        if intent:
            print(f"✅ Intent detected: {intent['intent']}")
            
            # Test handling the intent
            result = await mcp_client.handle_routine_request(intent)
            print(f"🧪 MCP result: success={result.success}, content='{result.content[:100]}...'")
        else:
            print("❌ No intent detected")
        
        # Test AI Assistant MCP integration
        ai_assistant = SpecialKidsAI(routine_mcp_server)
        print(f"✅ AI Assistant created with MCP: {ai_assistant.routine_mcp_client is not None}")
        
        # Test direct routine creation phrases
        test_phrases = [
            "create routine",
            "new routine", 
            "make routine",
            "I need a routine called 'Test Routine'"
        ]
        
        for phrase in test_phrases:
            intent = await mcp_client.detect_routine_intent(phrase, 1)
            print(f"Phrase: '{phrase}' -> Intent: {intent is not None}")
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_mcp_integration())
