#!/usr/bin/env python3
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_routine_creation():
    try:
        from database.db_manager import DatabaseManager
        from core.routine_manager import RoutineManager
        
        print("🌈 Testing routine creation...")
        
        db_manager = DatabaseManager("test_routine_creation.db")
        await db_manager.initialize()
        print("✅ Database initialized")
        
        routine_manager = RoutineManager(db_manager)
        print("✅ RoutineManager created")
        
        # Test creating a routine
        routine = await routine_manager.create_routine(
            child_id=1,
            name="Test Morning Routine",
            activities=["Brush teeth", "Get dressed", "Eat breakfast"],
            schedule_time="08:00",
            days_of_week=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        )
        
        if routine:
            print(f"✅ Created routine: {routine.name} (ID: {routine.id})")
        else:
            print("❌ Failed to create routine")
            
        # Test getting routines
        try:
            routines = await routine_manager.get_child_routines(1)
            print(f"✅ Retrieved {len(routines)} routines for child 1")
        except Exception as e:
            print(f"❌ Error getting routines: {e}")
        
        print("🎉 Routine creation test completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_routine_creation())
