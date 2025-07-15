#!/usr/bin/env python3
"""
Test script to verify current activity display in communication
"""

import asyncio
import sys
import os
import requests
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.routine_manager import RoutineManager
from database.db_manager import DatabaseManager

async def test_current_activity_display():
    """Test that current activity is displayed in all communications."""
    print("🎯 Testing Current Activity Display in Communication")
    print("=" * 60)
    
    # Initialize components
    db = DatabaseManager()
    routine_manager = RoutineManager(db)
    
    child_id = 1
    
    # Create a test routine
    print("\n1️⃣ Creating test routine...")
    routine = await routine_manager.create_routine(
        child_id=child_id,
        name="Current Activity Test Routine",
        activities=["Wake Up", "Get Dressed", "Eat Breakfast"],
        schedule_time="09:00",
        days_of_week=["Monday"]
    )
    routine_id = routine.id
    print(f"✅ Created routine ID: {routine_id}")
    
    # Start the routine
    print("\n2️⃣ Starting routine...")
    success = await routine_manager.start_routine(routine_id)
    print(f"✅ Routine started: {success}")
    
    # Test various chat messages and check if current activity is displayed
    test_messages = [
        "Hello Rainbow Bridge!",
        "How are you today?",
        "I'm feeling happy",
        "Can you help me?",
        "I want to play"
    ]
    
    print(f"\n3️⃣ Testing chat messages for current activity display...")
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n   3.{i}: Testing message: '{message}'")
        
        try:
            # Send chat message to API
            chat_data = {
                'child_id': child_id,
                'message': message,
                'communication_type': 'text'
            }
            
            response = requests.post(
                "http://localhost:8000/api/chat",
                data=chat_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result.get('text', '')
                current_context = result.get('current_activity_context')
                
                print(f"      📝 AI Response: {ai_response[:100]}...")
                
                if current_context:
                    current_activity = current_context.get('current_activity')
                    if current_activity:
                        print(f"      🎯 Current Activity Found: {current_activity['name']}")
                        print(f"      📊 Progress: {current_context.get('progress_percentage', 0)}%")
                        
                        # Check if current activity is mentioned in response
                        if current_activity['name'].lower() in ai_response.lower():
                            print(f"      ✅ Current activity mentioned in response!")
                        else:
                            print(f"      ⚠️  Current activity not mentioned in response")
                    else:
                        print(f"      ⚠️  No current activity found in context")
                else:
                    print(f"      ⚠️  No current activity context in response")
            else:
                print(f"      ❌ API error: {response.status_code}")
                
        except Exception as e:
            print(f"      ❌ Error: {e}")
    
    # Now complete an activity and test again
    print(f"\n4️⃣ Completing first activity and testing again...")
    completion_success = await routine_manager.complete_activity(routine_id, "Wake Up")
    print(f"✅ Activity completed: {completion_success}")
    
    # Test one more message to see updated current activity
    print(f"\n   Testing message after activity completion...")
    try:
        chat_data = {
            'child_id': child_id,
            'message': "What should I do next?",
            'communication_type': 'text'
        }
        
        response = requests.post(
            "http://localhost:8000/api/chat",
            data=chat_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result.get('text', '')
            current_context = result.get('current_activity_context')
            
            print(f"      📝 AI Response: {ai_response[:100]}...")
            
            if current_context:
                current_activity = current_context.get('current_activity')
                if current_activity:
                    print(f"      🎯 New Current Activity: {current_activity['name']}")
                    print(f"      📊 Progress: {current_context.get('progress_percentage', 0)}%")
                    
                    if current_activity['name'].lower() in ai_response.lower():
                        print(f"      ✅ Updated current activity mentioned in response!")
                    else:
                        print(f"      ⚠️  Updated current activity not mentioned in response")
        else:
            print(f"      ❌ API error: {response.status_code}")
            
    except Exception as e:
        print(f"      ❌ Error: {e}")
    
    print(f"\n5️⃣ Final routine status...")
    final_routine = await routine_manager.get_routine(routine_id)
    completed_count = sum(1 for a in final_routine.activities if a.completed)
    total_count = len(final_routine.activities)
    
    print(f"📊 Progress: {(completed_count/total_count)*100:.0f}% ({completed_count}/{total_count} completed)")
    
    print(f"\n🎯 Current Activity Display Test Complete!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_current_activity_display())
