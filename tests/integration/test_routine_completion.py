#!/usr/bin/env python3
"""
Test script to debug routine completion workflow
"""

import asyncio
import sys
import requests
import json
import time

async def test_routine_completion_workflow():
    """Test routine completion workflow step by step."""
    
    print("🌈 RainbowBridge Routine Completion Workflow Test")
    print("=" * 60)
    
    # Step 1: Create a test routine
    print("\n1️⃣  Creating a test routine...")
    
    api_data = {
        "child_id": 1,
        "routine_name": "Test Completion Routine",
        "activities": "brush teeth,wash face,put on pajamas",
        "schedule_time": "20:00"
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
                print(f"✅ Test routine created! Routine ID: {routine_id}")
            else:
                print(f"❌ Routine creation failed: {result}")
                return
        else:
            print(f"❌ API request failed with status {response.status_code}: {response.text}")
            return
            
    except Exception as e:
        print(f"❌ Routine creation error: {e}")
        return
    
    # Step 2: Start the routine session
    print(f"\n2️⃣  Starting routine session for routine {routine_id}...")
    
    try:
        start_data = {
            "routine_id": routine_id,
            "child_id": 1
        }
        
        response = requests.post(
            "http://localhost:8000/api/routine/start",
            data=start_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print(f"✅ Routine session started!")
                print(f"   Current activity: {result.get('current_activity', 'Unknown')}")
            else:
                print(f"❌ Failed to start routine: {result}")
        else:
            print(f"❌ Start routine request failed with status {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Start routine error: {e}")
    
    # Step 3: Test activity completion
    print(f"\n3️⃣  Testing activity completion...")
    
    activities_to_complete = ["brush teeth", "wash face", "put on pajamas"]
    
    for i, activity in enumerate(activities_to_complete, 1):
        print(f"\n   3.{i}: Completing activity '{activity}'...")
        
        try:
            complete_data = {
                "activity_name": activity,
                "child_id": 1
            }
            
            response = requests.post(
                f"http://localhost:8000/api/routine/{routine_id}/complete-activity",
                data=complete_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    print(f"   ✅ Activity '{activity}' completed!")
                    print(f"      Progress: {result.get('progress', 'Unknown')}%")
                    print(f"      MCP Message: {result.get('mcp_message', 'No message')}")
                else:
                    print(f"   ❌ Failed to complete activity: {result}")
                    print(f"      Error: {result.get('error', 'Unknown error')}")
            else:
                print(f"   ❌ Complete activity request failed with status {response.status_code}")
                print(f"      Response: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Activity completion error: {e}")
        
        # Small delay between activities
        time.sleep(0.5)
    
    # Step 4: Test chat-based completion
    print(f"\n4️⃣  Testing chat-based activity completion...")
    
    chat_completion_tests = [
        "I finished brushing my teeth",
        "Done with washing my face",
        "I completed putting on pajamas"
    ]
    
    for i, message in enumerate(chat_completion_tests, 1):
        print(f"\n   4.{i}: Testing chat message: '{message}'")
        
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
                    print(f"   ✅ Activity completion detected in chat!")
                    print(f"      AI Response: {ai_response}")
                else:
                    print(f"   ⚠️  Chat action: {routine_action}")
                    print(f"      AI Response: {ai_response}")
                    
            else:
                print(f"   ❌ Chat request failed with status {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Chat completion test error: {e}")
    
    # Step 5: Check routine status after completions
    print(f"\n5️⃣  Checking final routine status...")
    
    try:
        response = requests.get(f"http://localhost:8000/api/routine/{routine_id}/status")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Routine status retrieved:")
            print(f"   Total activities: {result.get('total_activities', 'Unknown')}")
            print(f"   Completed activities: {result.get('completed_activities', 'Unknown')}")
            print(f"   Progress: {result.get('progress_percentage', 'Unknown')}%")
        else:
            print(f"❌ Status request failed with status {response.status_code}")
            
    except Exception as e:
        print(f"❌ Status check error: {e}")
    
    print("\n🏁 Routine completion workflow test completed!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_routine_completion_workflow())
