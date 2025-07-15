#!/usr/bin/env python3
"""
Test with more specific completion language
"""

import requests
import time

def test_specific_completion_language():
    """Test completion with more specific language patterns."""
    
    print("🌈 Testing Specific Completion Language")
    print("=" * 50)
    
    # Create a test routine
    api_data = {
        "child_id": 1,
        "routine_name": "Specific Language Test",
        "activities": "brush teeth,wash hands,put on shoes",
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
            print(f"✅ Test routine created! ID: {routine_id}")
        else:
            print(f"❌ Failed to create routine")
            return
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # Test different completion language patterns
    completion_tests = [
        ("I finished brushing my teeth", "brush teeth"),
        ("I completed washing my hands", "wash hands"), 
        ("I'm done putting on my shoes", "put on shoes"),
        ("I finished brushing teeth", "brush teeth"),  # without 'my'
        ("Done with washing hands", "wash hands"),     # shorter form
        ("I put on shoes", "put on shoes")             # without 'finished'
    ]
    
    for i, (message, expected_activity) in enumerate(completion_tests, 1):
        print(f"\n{i}️⃣  Testing: '{message}' (expecting: {expected_activity})")
        
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
                    print(f"      AI Response: {ai_response[:100]}...")
                else:
                    print(f"   ⚠️  No activity completion detected (action: {routine_action})")
                    print(f"      AI Response: {ai_response[:100]}...")
                    
            else:
                print(f"   ❌ Request failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        time.sleep(0.3)
    
    # Check final status
    print(f"\n🔍 Final routine status:")
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
    test_specific_completion_language()
