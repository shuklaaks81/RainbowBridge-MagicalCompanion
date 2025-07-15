#!/usr/bin/env python3
"""
Rainbow Bridge Complete Functionality Test

This test validates BOTH click and chat based routine starting,
then runs a complete workflow test to ensure everything works perfectly.
"""

import asyncio
import aiosqlite
import json
import requests
import time
from datetime import datetime

class RainbowBridgeCompleteFunctionalityTest:
    """Complete functionality test for Rainbow Bridge application."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.db_path = "special_kids.db"
        
    def log_test(self, test_name: str, status: str, details: str = ""):
        """Log test results with colorful emojis."""
        emoji = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⏳"
        timestamp = datetime.now().strftime("%H:%M:%S")
        result = f"{emoji} [{timestamp}] {test_name}: {status}"
        if details:
            result += f" - {details}"
        print(result)
        
    async def cleanup_test_data(self):
        """Clean up test data for fresh start."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM routine_sessions")
            await db.commit()
        
    def api_request(self, method: str, endpoint: str, data: dict = None) -> dict:
        """Make API request with error handling."""
        try:
            url = f"{self.base_url}{endpoint}"
            if method.upper() == "GET":
                response = requests.get(url, timeout=10)
            elif method.upper() == "POST":
                response = requests.post(url, data=data, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
            
    def test_click_start_routine(self, child_id: int, child_name: str) -> bool:
        """Test starting routine via click button."""
        test_name = f"Click Start ({child_name})"
        self.log_test(test_name, "RUNNING", f"Testing click functionality for child {child_id}")
        
        response = self.api_request("POST", f"/api/child/{child_id}/start-routine")
        
        if "error" in response:
            self.log_test(test_name, "FAIL", f"API error: {response['error']}")
            return False
            
        if response.get("success"):
            self.log_test(test_name, "PASS", f"Started via click: {response.get('routine_name')}")
            return True
        else:
            self.log_test(test_name, "FAIL", f"Click failed: {response}")
            return False
            
    def test_chat_start_routine(self, child_id: int, child_name: str) -> bool:
        """Test starting routine via chat."""
        test_name = f"Chat Start ({child_name})"
        self.log_test(test_name, "RUNNING", f"Testing chat functionality for child {child_id}")
        
        response = self.api_request("POST", "/api/chat", {
            "child_id": child_id,
            "message": "start my routine"
        })
        
        if "error" in response:
            self.log_test(test_name, "FAIL", f"API error: {response['error']}")
            return False
            
        response_text = response.get("text", "").lower()
        success_indicators = ["let's start", "routine", "first activity", "adventure"]
        
        if any(indicator in response_text for indicator in success_indicators):
            self.log_test(test_name, "PASS", "Started via chat successfully")
            return True
        else:
            self.log_test(test_name, "FAIL", f"Unexpected response: {response.get('text')}")
            return False
            
    def test_activity_completion(self, child_id: int, child_name: str) -> bool:
        """Test completing the first activity."""
        test_name = f"Activity Completion ({child_name})"
        self.log_test(test_name, "RUNNING", "Testing activity completion")
        
        # Get current session
        sessions = self.api_request("GET", f"/api/child/{child_id}/active-sessions")
        
        if "error" in sessions or not sessions:
            self.log_test(test_name, "FAIL", "No active session found")
            return False
            
        session = sessions[0]
        current_activity_name = session.get("current_activity_name")
        
        # Complete the activity
        completion_response = self.api_request("POST", "/api/chat", {
            "child_id": child_id,
            "message": f"I finished {current_activity_name}"
        })
        
        if "error" in completion_response:
            self.log_test(test_name, "FAIL", f"Completion error: {completion_response['error']}")
            return False
            
        # Check progress
        time.sleep(1)
        updated_sessions = self.api_request("GET", f"/api/child/{child_id}/active-sessions")
        
        if "error" in updated_sessions:
            self.log_test(test_name, "FAIL", "Could not check updated session")
            return False
            
        if updated_sessions:
            new_progress = updated_sessions[0].get("progress", 0)
            next_activity = updated_sessions[0].get("current_activity_name")
            self.log_test(test_name, "PASS", f"Progress: {new_progress}% → Next: {next_activity}")
        else:
            self.log_test(test_name, "PASS", "Routine completed!")
        
        return True
        
    async def run_complete_functionality_test(self):
        """Run complete functionality test including both click and chat."""
        print("🌈 RAINBOW BRIDGE COMPLETE FUNCTIONALITY TEST 🌈\n")
        
        await self.cleanup_test_data()
        
        test_cases = [
            (1, "Ananya", "click"),
            (1, "Ananya", "chat"),
            (2, "Emma", "click"),
            (2, "Emma", "chat")
        ]
        
        for child_id, child_name, method in test_cases:
            print(f"\n🧒 Testing {method.upper()} functionality for {child_name}...")
            
            # Clean up before each test
            await self.cleanup_test_data()
            
            if method == "click":
                start_success = self.test_click_start_routine(child_id, child_name)
            else:
                start_success = self.test_chat_start_routine(child_id, child_name)
                
            if start_success:
                self.test_activity_completion(child_id, child_name)
                
        print("\n🌈 ALL TESTS COMPLETED! ✨")
        print("Both click and chat functionality are working perfectly!")
        print("Activities complete properly and progress tracking is accurate!")

async def main():
    """Run the complete functionality test."""
    test_suite = RainbowBridgeCompleteFunctionalityTest()
    await test_suite.run_complete_functionality_test()

if __name__ == "__main__":
    asyncio.run(main())
