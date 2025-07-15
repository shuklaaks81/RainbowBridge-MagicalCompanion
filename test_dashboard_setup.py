#!/usr/bin/env python3
"""
🌈 Quick Test: Today's Routines MCP Integration
==============================================

This script creates test data and verifies the MCP integration is working
with the child dashboard.
"""

import asyncio
import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def setup_test_data():
    """Set up test data for the dashboard"""
    print("🌈 Setting up test data for Today's Routines...")
    
    try:
        from database.db_manager import DatabaseManager
        from core.routine_manager import RoutineManager
        
        # Initialize components
        db_manager = DatabaseManager("special_kids.db")  # Use the main database
        await db_manager.initialize()
        routine_manager = RoutineManager(db_manager)
        
        # Check if we have any children
        children = await db_manager.get_all_children()
        
        if not children:
            # Create a test child
            child_data = {
                "name": "Alex",
                "age": 8,
                "communication_level": "visual_and_text",
                "preferences": '{"visual_support": true, "routine_focus": true, "interests": ["drawing", "music", "reading"]}'
            }
            child_id = await db_manager.create_child(child_data)
            print(f"✅ Created test child: Alex (ID: {child_id})")
        else:
            child_id = children[0]["id"]
            print(f"✅ Using existing child: {children[0]['name']} (ID: {child_id})")
        
        # Check existing routines
        existing_routines = await routine_manager.get_child_routines(child_id)
        print(f"📋 Found {len(existing_routines)} existing routine(s)")
        
        # Create sample routines if none exist
        if len(existing_routines) < 3:
            sample_routines = [
                {
                    "name": "Morning Routine",
                    "activities": ["Wake up and stretch", "Brush teeth", "Get dressed", "Eat breakfast", "Pack school bag"],
                    "schedule_time": "07:30",
                    "days_of_week": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
                },
                {
                    "name": "After School Routine",
                    "activities": ["Put away school things", "Wash hands", "Have snack", "Rest time", "Homework"],
                    "schedule_time": "15:30",
                    "days_of_week": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
                },
                {
                    "name": "Bedtime Routine",
                    "activities": ["Take bath", "Put on pajamas", "Brush teeth", "Read story", "Quiet time"],
                    "schedule_time": "20:00",
                    "days_of_week": ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
                }
            ]
            
            for routine_data in sample_routines:
                # Check if this routine already exists
                routine_exists = any(r.get("name") == routine_data["name"] for r in existing_routines)
                
                if not routine_exists:
                    routine = await routine_manager.create_routine(
                        child_id=child_id,
                        name=routine_data["name"],
                        activities=routine_data["activities"],
                        schedule_time=routine_data["schedule_time"],
                        days_of_week=routine_data["days_of_week"]
                    )
                    
                    if routine:
                        print(f"✅ Created routine: {routine.name}")
                    else:
                        print(f"❌ Failed to create routine: {routine_data['name']}")
        
        # Get final routine count
        final_routines = await routine_manager.get_child_routines(child_id)
        print(f"📊 Total routines available: {len(final_routines)}")
        
        print(f"\n🌈 Test setup complete!")
        print(f"🔗 Visit: http://localhost:8000/child/{child_id}")
        print(f"💡 Test the following features:")
        print(f"   1. Click ▶️ 'Start' on any routine")
        print(f"   2. Click ✨ 'Create New Routine'")
        print(f"   3. Type in chat: 'I want to create a morning routine'")
        print(f"   4. Type in chat: 'Start my morning routine'")
        
        return child_id
        
    except Exception as e:
        print(f"❌ Setup failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def print_test_instructions():
    """Print testing instructions"""
    print("\n" + "="*60)
    print("🧪 MCP INTEGRATION TESTING GUIDE")
    print("="*60)
    
    print(f"\n📱 DASHBOARD TESTING:")
    print(f"   1. Open the child dashboard (URL provided above)")
    print(f"   2. Look for 'Today's Routines' section in the right panel")
    print(f"   3. You should see routines with ▶️ Start and 👁️ View buttons")
    print(f"   4. Click ▶️ Start - it should trigger MCP and add message to chat")
    print(f"   5. Click ✨ Create New Routine - should guide you in chat")
    
    print(f"\n💬 CHAT TESTING:")
    print(f"   1. Type: 'I want to create a morning routine'")
    print(f"      → Should get guidance for routine creation")
    print(f"   2. Type: 'Start my morning routine'")
    print(f"      → Should get MCP-powered routine starting response")
    print(f"   3. Type: 'I finished brushing my teeth'")
    print(f"      → Should acknowledge activity completion")
    
    print(f"\n🔍 WHAT TO LOOK FOR:")
    print(f"   ✅ Routines display with enhanced UI")
    print(f"   ✅ Start buttons trigger chat messages")
    print(f"   ✅ Create button provides chat guidance")
    print(f"   ✅ Natural language creates routine intent")
    print(f"   ✅ MCP routing works (check responses)")
    print(f"   ✅ Visual progress indicators appear")

async def main():
    """Run the test setup"""
    child_id = await setup_test_data()
    
    if child_id:
        print_test_instructions()
        print(f"\n🚀 Ready to test! Application is running at http://localhost:8000")
        print(f"🎯 Direct link to child dashboard: http://localhost:8000/child/{child_id}")
    else:
        print(f"\n❌ Setup failed - check the errors above")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n👋 Setup interrupted")
    except Exception as e:
        print(f"\n❌ Error: {e}")
