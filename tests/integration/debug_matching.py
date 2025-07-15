#!/usr/bin/env python3
"""
Debug the activity matching process
"""

import requests
import json

def debug_activity_matching():
    """Debug what's happening with activity matching."""
    
    print("🔍 Debug Activity Matching Process")
    print("=" * 50)
    
    # 1. Create a routine and see what activities it has
    print("\n1️⃣  Creating routine and checking activities...")
    api_data = {
        "child_id": 1,
        "routine_name": "Debug Test Routine",
        "activities": "wake up,get dressed,eat breakfast",
        "schedule_time": "08:00"
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
            routine_id = result['routine_id']
            print(f"✅ Routine created! ID: {routine_id}")
        else:
            print(f"❌ Failed to create routine: {response.text}")
            return
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # 2. Check what activities are actually stored
    print(f"\n2️⃣  Checking routine activities...")
    try:
        response = requests.get(f"http://localhost:8000/api/routine/{routine_id}/status")
        if response.status_code == 200:
            result = response.json()
            activities = result.get('activities', [])
            print(f"✅ Stored activities:")
            for i, activity in enumerate(activities):
                activity_name = activity.get('name', 'Unknown')
                print(f"   {i+1}. '{activity_name}'")
        else:
            print(f"❌ Status check failed")
            return
    except Exception as e:
        print(f"❌ Status error: {e}")
        return
    
    # 3. Try direct API completion
    print(f"\n3️⃣  Testing direct API completion...")
    test_completions = ["wake up", "get dressed", "eat breakfast"]
    
    for activity in test_completions:
        print(f"\nTesting direct completion of '{activity}':")
        
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
                success = result.get('success', False)
                progress = result.get('progress', 0)
                message = result.get('mcp_message', 'No message')
                
                print(f"   Success: {success}")
                print(f"   Progress: {progress}%")
                print(f"   Message: {message}")
            else:
                print(f"   ❌ Failed: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # 4. Check final status
    print(f"\n4️⃣  Final status check...")
    try:
        response = requests.get(f"http://localhost:8000/api/routine/{routine_id}/status")
        if response.status_code == 200:
            result = response.json()
            print(f"   Progress: {result.get('progress_percentage', 0)}%")
            print(f"   Completed: {result.get('completed_activities', 0)}/{result.get('total_activities', 0)}")
        else:
            print(f"   ❌ Status check failed")
    except Exception as e:
        print(f"   ❌ Status error: {e}")

if __name__ == "__main__":
    debug_activity_matching()
