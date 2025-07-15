#!/usr/bin/env python3
"""
Test multiple general phrases quickly
"""

import requests
import time

def test_multiple_phrases():
    """Test multiple general phrases."""
    
    print("🌈 Testing Multiple General Phrases")
    print("=" * 50)
    
    phrases = [
        "I woke up",
        "Got dressed", 
        "Ate breakfast",
        "Teeth clean",
        "Clothes on",
        "Brushed"
    ]
    
    for phrase in phrases:
        print(f"\nTesting: '{phrase}'")
        
        chat_data = {
            "child_id": 1,
            "message": phrase,
            "communication_type": "text"
        }
        
        try:
            response = requests.post(
                "http://localhost:8000/api/chat",
                data=chat_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code == 200:
                result = response.json()
                routine_action = result.get('routine_action', 'none')
                intent_detected = result.get('intent_detected', 'none')
                
                if routine_action == "complete_activity":
                    print(f"   ✅ DETECTED as activity completion!")
                elif intent_detected == "achievement_sharing":
                    print(f"   ✅ DETECTED as achievement sharing!")
                else:
                    print(f"   ⚠️  Action: {routine_action}, Intent: {intent_detected}")
                    
            else:
                print(f"   ❌ Failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        time.sleep(0.3)

if __name__ == "__main__":
    test_multiple_phrases()
