#!/usr/bin/env python3
"""
Quick demo script to set up fresh data and test current activity display
"""

import asyncio
import sys
import os
import requests
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.routine_manager import RoutineManager
from database.db_manager import DatabaseManager

async def setup_fresh_demo():
    """Set up fresh demo data and test current activity display."""
    print("🌈 Setting up Fresh Rainbow Bridge Demo")
    print("=" * 50)
    
    # Initialize components
    db = DatabaseManager()
    routine_manager = RoutineManager(db)
    
    print("\n1️⃣ Creating demo child profile...")
    try:
        # Create a child profile directly in database
        child_data = {
            "name": "Emma",
            "age": 8,
            "communication_level": "moderate",
            "interests": ["art", "music", "reading"],
            "special_needs": ["autism", "sensory_sensitive"],
            "preferences": {
                "visual_support": True,
                "routine_focus": True,
                "sensory_sensitive": True
            }
        }
        
        child_id = await db.create_child_profile(child_data)
        print(f"✅ Created child profile: Emma (ID: {child_id})")
    except Exception as e:
        print(f"⚠️  Using default child ID 1: {e}")
        child_id = 1
    
    print("\n2️⃣ Creating morning routine...")
    routine = await routine_manager.create_routine(
        child_id=child_id,
        name="Emma's Morning Routine",
        activities=["Wake Up Gently", "Get Dressed", "Eat Breakfast", "Brush Teeth"],
        schedule_time="08:00",
        days_of_week=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    )
    routine_id = routine.id
    print(f"✅ Created routine: {routine.name} (ID: {routine_id})")
    
    print("\n3️⃣ Starting the routine...")
    success = await routine_manager.start_routine(routine_id)
    print(f"✅ Routine started: {success}")
    
    print(f"\n4️⃣ Testing current activity display in chat...")
    
    # Test messages to show current activity display
    test_messages = [
        "Hello Rainbow Bridge!",
        "How are you today?", 
        "I need some help",
        "What should I do?",
        "I'm feeling happy"
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n   4.{i}: Testing: '{message}'")
        
        try:
            # Send chat message
            response = requests.post(
                "http://localhost:8000/api/chat",
                data={
                    'child_id': child_id,
                    'message': message,
                    'communication_type': 'text'
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_text = result.get('text', '')
                current_context = result.get('current_activity_context')
                
                print(f"       🤖 AI Response: {ai_text[:80]}...")
                
                if current_context and current_context.get('current_activity'):
                    current_activity = current_context['current_activity']
                    progress = current_context.get('progress_percentage', 0)
                    print(f"       🎯 Current Activity: {current_activity['name']}")
                    print(f"       📊 Progress: {progress}%")
                    print(f"       ✅ Current activity displayed in response!")
                else:
                    print(f"       ⚠️  No current activity context found")
            else:
                print(f"       ❌ API Error: {response.status_code}")
                
        except Exception as e:
            print(f"       ❌ Error: {e}")
    
    print(f"\n5️⃣ Testing activity completion with general phrases...")
    
    completion_phrases = [
        "I woke up",
        "Got dressed", 
        "Ate my breakfast"
    ]
    
    for i, phrase in enumerate(completion_phrases, 1):
        print(f"\n   5.{i}: Testing completion: '{phrase}'")
        
        try:
            response = requests.post(
                "http://localhost:8000/api/chat",
                data={
                    'child_id': child_id,
                    'message': phrase,
                    'communication_type': 'text'
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_text = result.get('text', '')
                routine_action = result.get('routine_action')
                current_context = result.get('current_activity_context')
                
                print(f"       🤖 AI Response: {ai_text[:80]}...")
                print(f"       🔧 Routine Action: {routine_action}")
                
                if current_context:
                    progress = current_context.get('progress_percentage', 0)
                    remaining = current_context.get('remaining_activities', 0)
                    print(f"       📊 Progress: {progress}% ({remaining} activities remaining)")
                    
                if routine_action == "complete_activity":
                    print(f"       ✅ Activity completion detected and processed!")
                else:
                    print(f"       ⚠️  No activity completion detected")
                    
        except Exception as e:
            print(f"       ❌ Error: {e}")
    
    print(f"\n6️⃣ Final routine status...")
    try:
        response = requests.get(f"http://localhost:8000/api/routine/{routine_id}/status")
        if response.status_code == 200:
            status = response.json()
            progress = status.get('progress_percentage', 0)
            completed = status.get('completed_activities', 0)
            total = status.get('total_activities', 0)
            current_activity = status.get('current_activity')
            
            print(f"📊 Final Progress: {progress}% ({completed}/{total} completed)")
            if current_activity:
                print(f"🎯 Next Activity: {current_activity}")
            else:
                print(f"🎉 All activities completed!")
                
    except Exception as e:
        print(f"❌ Status check error: {e}")
    
    print(f"\n🌈 Fresh Demo Setup Complete!")
    print("=" * 50)
    print(f"👶 Child: Emma (ID: {child_id})")
    print(f"📅 Routine: Emma's Morning Routine (ID: {routine_id})")
    print(f"🎯 Features: Current activity display in all communications")
    print(f"🗣️  Natural language: 'I woke up', 'Got dressed', etc.")
    print(f"🌐 Access: http://localhost:8000")

if __name__ == "__main__":
    asyncio.run(setup_fresh_demo())
