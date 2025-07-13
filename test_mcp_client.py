#!/usr/bin/env python3
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_mcp_client():
    try:
        print("🌈 Testing MCP Client...")
        
        from database.db_manager import DatabaseManager
        from core.routine_manager import RoutineManager
        from core.routine_mcp_server import create_routine_mcp_server
        from core.routine_mcp_client import RoutineMCPClient
        
        print("✅ All imports successful")
        
        db_manager = DatabaseManager("test_mcp.db")
        await db_manager.initialize()
        print("✅ Database initialized")
        
        routine_manager = RoutineManager(db_manager)
        print("✅ RoutineManager created")
        
        # Create MCP server
        mcp_server = create_routine_mcp_server(routine_manager, db_manager)
        print("✅ MCP server created")
        
        # Create MCP client
        mcp_client = RoutineMCPClient(mcp_server)
        print("✅ MCP client created")
        
        # Test intent detection
        test_messages = [
            "What routines do I have?",
            "Start my morning routine",
            "I completed brushing teeth"
        ]
        
        for message in test_messages:
            try:
                result = await mcp_client.detect_routine_intent(message, child_id=1)
                if result:
                    print(f"✅ '{message}' -> {result['intent']}")
                else:
                    print(f"❌ '{message}' -> No intent detected")
            except Exception as e:
                print(f"❌ Error with '{message}': {e}")
        
        print("🎉 MCP client test completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_mcp_client())
