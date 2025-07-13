#!/usr/bin/env python3
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def simple_test():
    try:
        print("Testing imports...")
        from database.db_manager import DatabaseManager
        print("✅ DatabaseManager imported")
        
        from core.routine_manager import RoutineManager  
        print("✅ RoutineManager imported")
        
        db_manager = DatabaseManager("test_simple.db")
        await db_manager.initialize()
        print("✅ Database initialized")
        
        routine_manager = RoutineManager(db_manager)
        print("✅ RoutineManager created")
        
        print("🎉 Basic setup works!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(simple_test())
