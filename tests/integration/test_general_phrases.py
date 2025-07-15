#!/usr/bin/env python3
"""
Test script for enhanced general phrase handling for special kids
"""

import asyncio
import sys
import requests
import json
import time

async def test_general_phrase_handling():
    """Test the enhanced general phrase handling for special kids."""
    
    print("🌈 Testing Enhanced General Phrase Handling for Special Kids")
    print("=" * 70)
    
    # Create a test routine with typical activities
    print("\n1️⃣  Creating test routine with common activities...")
    
    api_data = {
        "child_id": 1,
        "routine_name": "Morning Routine for General Phrases Test",
        "activities": "wake up,brush teeth,get dressed,eat breakfast",
        "schedule_time": "07:30"
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
            print(f"❌ API request failed: {response.status_code}")
            return
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # Test general phrases that special kids might use
    print(f"\n2️⃣  Testing natural, general phrases...")
    
    test_phrases = [
        # Very general activity statements
        ("I woke up", "wake up"),
        ("Got dressed", "get dressed"), 
        ("Ate breakfast", "eat breakfast"),
        ("Teeth clean", "brush teeth"),
        
        # Even more general/simple
        ("Clothes on", "get dressed"),
        ("Food done", "eat breakfast"),
        ("Teeth good", "brush teeth"),
        ("Up now", "wake up"),
        
        # Single word completions
        ("Dressed", "get dressed"),
        ("Breakfast", "eat breakfast"),
        ("Teeth", "brush teeth"),
        ("Awake", "wake up"),
        
        # Child-like expressions
        ("All done eating", "eat breakfast"),
        ("Good teeth", "brush teeth"),
        ("Ready clothes", "get dressed"),
        ("Morning time", "wake up"),
        
        # Present tense (happening now)
        ("Getting dressed", "get dressed"),
        ("Eating breakfast", "eat breakfast"),
        ("Brushing teeth", "brush teeth"),
        
        # Simple past without "I"
        ("Woke up", "wake up"),
        ("Brushed", "brush teeth"),
        ("Ate", "eat breakfast")
    ]
    
    success_count = 0
    total_tests = len(test_phrases)
    
    for i, (phrase, expected_activity) in enumerate(test_phrases, 1):
        print(f"\n   2.{i}: Testing '{phrase}' (expecting: {expected_activity})")
        
        try:
            chat_data = {
                "child_id": 1,
                "message": phrase,
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
                    print(f"      AI Response: {ai_response[:120]}...")
                    success_count += 1
                else:
                    print(f"   ⚠️  No completion detected (action: {routine_action})")
                    print(f"      AI Response: {ai_response[:120]}...")
                    
            else:
                print(f"   ❌ Request failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        time.sleep(0.2)  # Small delay
    
    # Test some achievement-sharing phrases
    print(f"\n3️⃣  Testing achievement sharing phrases...")
    
    achievement_phrases = [
        "I did good",
        "All done",
        "Ready now", 
        "Good job me",
        "Finished",
        "Yay me"
    ]
    
    achievement_success = 0
    
    for i, phrase in enumerate(achievement_phrases, 1):
        print(f"\n   3.{i}: Testing achievement phrase '{phrase}'")
        
        try:
            chat_data = {
                "child_id": 1,
                "message": phrase,
                "communication_type": "text"
            }
            
            response = requests.post(
                "http://localhost:8000/api/chat",
                data=chat_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code == 200:
                result = response.json()
                intent_detected = result.get("intent_detected", "none")
                ai_response = result.get("text", "No response")
                
                if intent_detected == "achievement_sharing" or "proud" in ai_response.lower() or "great job" in ai_response.lower():
                    print(f"   ✅ Achievement sharing detected!")
                    print(f"      AI Response: {ai_response[:120]}...")
                    achievement_success += 1
                else:
                    print(f"   ⚠️  Intent: {intent_detected}")
                    print(f"      AI Response: {ai_response[:120]}...")
                    
            else:
                print(f"   ❌ Request failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        time.sleep(0.2)
    
    # Check final routine status
    print(f"\n4️⃣  Checking routine completion status...")
    try:
        response = requests.get(f"http://localhost:8000/api/routine/{routine_id}/status")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Final status:")
            print(f"   Progress: {result.get('progress_percentage', 0)}%")
            print(f"   Completed: {result.get('completed_activities', 0)}/{result.get('total_activities', 0)}")
            print(f"   Status: {result.get('status', 'unknown')}")
        else:
            print(f"❌ Status check failed")
    except Exception as e:
        print(f"❌ Status error: {e}")
    
    # Summary
    print(f"\n🎯 Test Results Summary:")
    print(f"   Activity completion detection: {success_count}/{total_tests} ({(success_count/total_tests)*100:.1f}%)")
    print(f"   Achievement sharing detection: {achievement_success}/{len(achievement_phrases)} ({(achievement_success/len(achievement_phrases))*100:.1f}%)")
    
    if success_count >= total_tests * 0.7:  # 70% success rate
        print(f"   ✅ EXCELLENT: System handles general phrases well!")
    elif success_count >= total_tests * 0.5:  # 50% success rate
        print(f"   ⚠️  GOOD: System partially handles general phrases")
    else:
        print(f"   ❌ NEEDS IMPROVEMENT: Low general phrase detection")
    
    print("\n🏁 General phrase handling test completed!")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(test_general_phrase_handling())
