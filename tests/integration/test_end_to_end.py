#!/usr/bin/env python3
"""
Final comprehensive test for routine completion workflow
"""

import asyncio
import sys
import requests
import json
import time

async def test_end_to_end_routine_workflow():
    """Test complete end-to-end routine workflow from creation to completion."""
    
    print("🌈 RainbowBridge End-to-End Routine Workflow Test")
    print("=" * 60)
    
    # Step 1: Create a fresh routine
    print("\n1️⃣  Creating a fresh routine...")
    
    api_data = {
        "child_id": 1,
        "routine_name": "End-to-End Test Routine",
        "activities": "wake up,get dressed,eat breakfast",
        "schedule_time": "07:00"
    }
    
    routine_id = None
    try:
        response = requests.post(
            "http://localhost:8000/api/routine",
            data=api_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                routine_id = result['routine_id']
                print(f"✅ Fresh routine created! Routine ID: {routine_id}")
            else:
                print(f"❌ Routine creation failed: {result}")
                return
        else:
            print(f"❌ API request failed with status {response.status_code}: {response.text}")
            return
            
    except Exception as e:
        print(f"❌ Routine creation error: {e}")
        return
    
    # Step 2: Test chat-based completion ONLY (no direct API)
    print(f"\n2️⃣  Testing pure chat-based completion workflow...")
    
    completion_messages = [
        "I woke up!",
        "I got dressed",
        "I finished eating breakfast"
    ]
    
    for i, message in enumerate(completion_messages, 1):
        print(f"\n   2.{i}: Child says: '{message}'")
        
        try:
            chat_data = {
                "child_id": 1,
                "message": message,
                "communication_type": "text"
            }
            
            response = requests.post(
                "http://localhost:8000/api/chat",
                data=chat_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code == 200:
                result = response.json()
                routine_action = result.get("routine_action", "none")
                ai_response = result.get("text", "No response")
                
                if routine_action == "complete_activity":
                    print(f"   ✅ Activity completion detected!")
                    print(f"      AI Response: {ai_response}")
                else:
                    print(f"   ⚠️  Different action: {routine_action}")
                    print(f"      AI Response: {ai_response}")
                    
            else:
                print(f"   ❌ Chat request failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Chat completion error: {e}")
        
        # Small delay
        time.sleep(0.5)
    
    # Step 3: Check final status
    print(f"\n3️⃣  Checking final routine status...")
    
    try:
        response = requests.get(f"http://localhost:8000/api/routine/{routine_id}/status")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Final routine status:")
            print(f"   Routine Name: {result.get('name', 'Unknown')}")
            print(f"   Total Activities: {result.get('total_activities', 'Unknown')}")
            print(f"   Completed Activities: {result.get('completed_activities', 'Unknown')}")
            print(f"   Progress: {result.get('progress_percentage', 'Unknown')}%")
            print(f"   Status: {result.get('status', 'Unknown')}")
            print(f"   Current Activity: {result.get('current_activity', 'None')}")
        else:
            print(f"❌ Status request failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Status check error: {e}")
    
    print("\n🏁 End-to-end routine workflow test completed!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_end_to_end_routine_workflow())
