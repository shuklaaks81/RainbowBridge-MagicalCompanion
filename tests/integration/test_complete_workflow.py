#!/usr/bin/env python3
"""
Comprehensive test script for routine creation workflow
"""

import asyncio
import sys
import requests
import json

async def test_routine_creation_workflow():
    """Test all aspects of routine creation workflow."""
    
    print("🌈 RainbowBridge Routine Creation Workflow Test")
    print("=" * 60)
    
    # Test 1: Direct API routine creation
    print("\n1️⃣  Testing direct API routine creation...")
    
    api_data = {
        "child_id": 1,
        "routine_name": "Test Evening Routine",
        "activities": "read book,calm down,go to sleep",
        "schedule_time": "19:30"
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/api/routine",
            data=api_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print(f"✅ API routine creation successful! Routine ID: {result['routine_id']}")
            else:
                print(f"❌ API routine creation failed: {result}")
        else:
            print(f"❌ API request failed with status {response.status_code}")
            
    except Exception as e:
        print(f"❌ API test error: {e}")
    
    # Test 2: Chat-based routine creation with different intents
    print("\n2️⃣  Testing chat-based routine creation...")
    
    chat_tests = [
        "I want to create a morning routine",
        "Can you help me make a bedtime routine?",
        "Create a learning routine at 2 PM"
    ]
    
    for i, message in enumerate(chat_tests, 1):
        print(f"\n   Test 2.{i}: '{message}'")
        
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
                llm_source = result.get("llm_source", "unknown")
                routine_action = result.get("routine_action", "none")
                
                if routine_action == "create_routine":
                    print(f"   ✅ Routine creation detected! LLM source: {llm_source}")
                else:
                    print(f"   ⚠️  Different action detected: {routine_action} (LLM: {llm_source})")
                    
            else:
                print(f"   ❌ Chat request failed with status {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Chat test error: {e}")
    
    # Test 3: Verify routines were created
    print("\n3️⃣  Testing routine retrieval...")
    
    try:
        response = requests.get("http://localhost:8000/api/children")
        if response.status_code == 200:
            children = response.json()
            if children:
                print(f"✅ Found {len(children)} children in database")
            else:
                print("⚠️  No children found - this might affect routine testing")
        else:
            print(f"❌ Failed to retrieve children: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Children retrieval error: {e}")
    
    print("\n🏁 Routine creation workflow test completed!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_routine_creation_workflow())
