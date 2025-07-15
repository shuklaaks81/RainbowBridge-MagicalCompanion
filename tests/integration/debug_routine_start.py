#!/usr/bin/env python3
"""
🔍 Debug Routine Start Issue
============================

Deep dive into what's failing in routine start.
"""

import asyncio
import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def debug_routine_start():
    """Debug exactly where routine start is failing"""
    print("🔍 Debugging routine start issue...")
    
    try:
        from core.routine_manager import RoutineManager
        from database.db_manager import DatabaseManager
        
        # Initialize components
        db_manager = DatabaseManager("special_kids.db")
        await db_manager.initialize()
        
        routine_manager = RoutineManager(db_manager)
        
        # Test with routine ID 15
        routine_id = 15
        
        print(f"🧪 Testing routine ID: {routine_id}")
        
        # Step 1: Test database get_routine
        print("1️⃣ Testing db_manager.get_routine()...")
        routine_data = await db_manager.get_routine(routine_id)
        if routine_data:
            print(f"   ✅ Database returned: {type(routine_data)}")
            print(f"   📊 Data keys: {routine_data.keys()}")
            print(f"   📛 Name: {routine_data.get('name')}")
            print(f"   👶 Child ID: {routine_data.get('child_id')}")
            print(f"   🎯 Activities count: {len(routine_data.get('activities', []))}")
        else:
            print("   ❌ Database returned None")
            return
        
        # Step 2: Test routine_manager.get_routine
        print("\n2️⃣ Testing routine_manager.get_routine()...")
        try:
            routine_obj = await routine_manager.get_routine(routine_id)
            if routine_obj:
                print(f"   ✅ Routine manager returned: {type(routine_obj)}")
                print(f"   📛 Name: {routine_obj.name}")
                print(f"   👶 Child ID: {routine_obj.child_id}")
                print(f"   🎯 Activities count: {len(routine_obj.activities)}")
            else:
                print("   ❌ Routine manager returned None")
                return
        except Exception as e:
            print(f"   ❌ Routine manager failed: {e}")
            import traceback
            traceback.print_exc()
            return
        
        # Step 3: Test create_routine_session
        print("\n3️⃣ Testing create_routine_session()...")
        from datetime import datetime
        session_data = {
            "routine_id": routine_id,
            "child_id": routine_obj.child_id,
            "started_at": datetime.now(),
            "current_activity": 0,
            "status": "in_progress",
            "progress": 0
        }
        
        try:
            session_id = await db_manager.create_routine_session(session_data)
            print(f"   ✅ Session created: {session_id}")
        except Exception as e:
            print(f"   ❌ Session creation failed: {e}")
            import traceback
            traceback.print_exc()
            return
        
        # Step 4: Test full start_routine
        print("\n4️⃣ Testing full start_routine()...")
        try:
            result = await routine_manager.start_routine(routine_id)
            print(f"   📊 Result: {result}")
            if result:
                print("   ✅ start_routine succeeded!")
            else:
                print("   ❌ start_routine returned False")
        except Exception as e:
            print(f"   ❌ start_routine failed: {e}")
            import traceback
            traceback.print_exc()
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_routine_start())
