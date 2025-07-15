#!/usr/bin/env python3
"""
Quick test for one general phrase
"""

import requests
import json

def quick_test():
    """Quick test for general phrase."""
    
    print("🔍 Quick General Phrase Test")
    print("=" * 40)
    
    # Test a simple general phrase
    chat_data = {
        "child_id": 1,
        "message": "I woke up",
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
            print(f"Message: 'I woke up'")
            print(f"Routine Action: {result.get('routine_action', 'none')}")
            print(f"Intent Detected: {result.get('intent_detected', 'none')}")
            print(f"LLM Source: {result.get('llm_source', 'none')}")
            print(f"Response: {result.get('text', 'No response')}")
        else:
            print(f"Failed: {response.status_code}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    quick_test()
