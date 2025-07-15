#!/usr/bin/env python3
"""
Rainbow Bridge Click Test

Simple test to verify routine starting via click button functionality.
"""

import requests
import json
import time

def test_click_routine_start():
    """Test clicking start routine button."""
    base_url = "http://localhost:8000"
    
    print("🌈 Testing Click-based Routine Starting...")
    
    # Test for both children
    for child_id, child_name in [(1, "Ananya"), (2, "Emma")]:
        print(f"\n🧒 Testing click functionality for {child_name}...")
        
        try:
            # Simulate the click by calling start-routine endpoint
            response = requests.post(
                f"{base_url}/api/child/{child_id}/start-routine",
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Click start successful for {child_name}")
                print(f"   Response: {result}")
                
                # Check if session was created
                time.sleep(1)
                sessions_response = requests.get(f"{base_url}/api/child/{child_id}/active-sessions")
                if sessions_response.status_code == 200:
                    sessions = sessions_response.json()
                    if sessions:
                        print(f"✅ Active session created: {sessions[0].get('current_activity_name', 'Unknown')}")
                    else:
                        print("❌ No active session found after click")
                else:
                    print("❌ Could not check active sessions")
            else:
                print(f"❌ Click failed for {child_name}: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error testing {child_name}: {str(e)}")

if __name__ == "__main__":
    test_click_routine_start()
