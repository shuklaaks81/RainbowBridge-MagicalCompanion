#!/usr/bin/env python3
"""
🌈 Simple Routine Creation Test
==============================

Create a simple routine to test MCP integration.
"""

import asyncio
import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def create_simple_routine():
    """Create a simple test routine"""
    print("🌈 Creating simple test routine...")
    
    try:
        from database.db_manager import DatabaseManager
        from core.routine_manager import Routine, Activity
        from datetime import datetime
        
        # Initialize components
        db_manager = DatabaseManager("special_kids.db")
        await db_manager.initialize()
        
        # Create test activities using the proper Activity class
        activities = [
            Activity(
                name="Wake up", 
                duration_minutes=5, 
                description="Start your day",
                visual_cue="sunrise",
                instructions=["Get out of bed", "Stretch your arms"],
                sensory_considerations=["Gentle wake-up music"]
            ),
            Activity(
                name="Brush teeth", 
                duration_minutes=5, 
                description="Brush your teeth for 2 minutes",
                visual_cue="toothbrush",
                instructions=["Get toothbrush", "Apply toothpaste", "Brush for 2 minutes"],
                sensory_considerations=["Soft-bristled toothbrush"]
            ),
            Activity(
                name="Get dressed", 
                duration_minutes=10, 
                description="Put on your clothes",
                visual_cue="clothes",
                instructions=["Choose clothes", "Put on shirt", "Put on pants"],
                sensory_considerations=["Comfortable fabric"]
            ),
            Activity(
                name="Eat breakfast", 
                duration_minutes=20, 
                description="Have a healthy breakfast",
                visual_cue="food",
                instructions=["Sit at table", "Eat slowly", "Drink water"],
                sensory_considerations=["Favorite foods available"]
            )
        ]
        
        # Create routine object
        routine = Routine(
            id=None,  # Will be set by database
            child_id=1,
            name="Test Morning Routine",
            activities=activities,
            schedule_time="08:00",
            days_of_week=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
            active=True,
            created_at=datetime.now()
        )
        
        # Save using the proper method
        routine_id = await db_manager.save_routine(routine)
        
        print(f"✅ Created routine: {routine.name} (ID: {routine_id})")
        
        # Verify it was created
        saved_routine = await db_manager.get_routine(routine_id)
        if saved_routine:
            print(f"✅ Verified routine creation: {saved_routine.get('name')}")
        else:
            print("❌ Could not verify routine creation")
        
        return routine_id
        
    except Exception as e:
        print(f"❌ Failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

async def main():
    """Main test function"""
    routine_id = await create_simple_routine()
    
    if routine_id:
        print(f"\n🎉 SUCCESS! Test routine created.")
        print(f"🔗 Test at: http://localhost:8000/child/1")
        print(f"📋 Look for 'Test Morning Routine' in Today's Routines section")
        print(f"🧪 Test these MCP features:")
        print(f"   1. Click ▶️ Start button")
        print(f"   2. Click ✨ Create New Routine")
        print(f"   3. Type: 'Start my test morning routine'")
    else:
        print(f"\n❌ Test setup failed")

if __name__ == "__main__":
    asyncio.run(main())
