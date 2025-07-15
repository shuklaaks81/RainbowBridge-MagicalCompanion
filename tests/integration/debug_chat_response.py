#!/usr/bin/env python3
"""
Test script to debug chat response content
"""

import requests
import json

def test_chat_response_debug():
    """Debug the chat response to see what's in the 'text' field."""
    
    print("🔍 Debug Chat Response Content")
    print("=" * 50)
    
    # Test a simple message first
    simple_test = {
        "child_id": 1,
        "message": "Hello Rainbow Bridge!",
        "communication_type": "text"
    }
    
    print("1️⃣  Testing simple message...")
    
    try:
        response = requests.post(
            "http://localhost:8000/api/chat",
            data=simple_test,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Simple message response:")
            print(f"   Response keys: {list(result.keys())}")
            print(f"   Text field: '{result.get('text', 'MISSING')}'")
            print(f"   Text type: {type(result.get('text'))}")
            print(f"   Text length: {len(result.get('text', ''))}")
        else:
            print(f"❌ Simple message failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Simple message error: {e}")
    
    # Test a routine completion message
    print("\n2️⃣  Testing routine completion message...")
    
    completion_test = {
        "child_id": 1,
        "message": "I finished brushing my teeth",
        "communication_type": "text"
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/api/chat",
            data=completion_test,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Routine completion response:")
            print(f"   Response keys: {list(result.keys())}")
            print(f"   Text field: '{result.get('text', 'MISSING')}'")
            print(f"   Text type: {type(result.get('text'))}")
            print(f"   Text length: {len(result.get('text', ''))}")
            print(f"   LLM Source: {result.get('llm_source', 'MISSING')}")
            print(f"   Routine Action: {result.get('routine_action', 'MISSING')}")
            print(f"   Full response:")
            print(f"   {json.dumps(result, indent=2)}")
        else:
            print(f"❌ Routine completion failed: {response.status_code}")
            print(f"   Response text: {response.text}")
            
    except Exception as e:
        print(f"❌ Routine completion error: {e}")

if __name__ == "__main__":
    test_chat_response_debug()
