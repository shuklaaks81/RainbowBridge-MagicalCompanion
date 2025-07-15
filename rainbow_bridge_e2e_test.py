#!/usr/bin/env python3
"""
Rainbow Bridge End-to-End Workflow Test Suite

This comprehensive test suite validates the complete routine workflow:
1. Starting routines (chat & click)
2. Activity completion and progression
3. Progress tracking and reporting
4. Routine completion detection
5. Real-time updates and synchronization

Test Features:
- Colorful Rainbow-themed activity names
- Child-specific age-appropriate activities
- Complete workflow validation
- Progress verification at each step
- Error handling and edge cases
"""

import asyncio
import aiosqlite
import json
import requests
import time
from datetime import datetime
from typing import Dict, List, Any

class RainbowBridgeE2ETestSuite:
    """Comprehensive end-to-end test suite for Rainbow Bridge application."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.db_path = "special_kids.db"
        self.test_results = []
        
    def log_test(self, test_name: str, status: str, details: str = ""):
        """Log test results with colorful emojis."""
        emoji = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⏳"
        timestamp = datetime.now().strftime("%H:%M:%S")
        result = f"{emoji} [{timestamp}] {test_name}: {status}"
        if details:
            result += f" - {details}"
        print(result)
        self.test_results.append({
            "test": test_name,
            "status": status,
            "details": details,
            "timestamp": timestamp
        })
        
    async def setup_rainbow_themed_routines(self):
        """Create beautiful rainbow-themed routines for testing."""
        self.log_test("Setup", "RUNNING", "Creating rainbow-themed routines...")
        
        # Ananya's Rainbow Morning Adventure (13-year-old)
        ananya_activities = [
            {
                "name": "🌅 Sunrise Awakening",
                "duration_minutes": 10,
                "description": "Gentle awakening with rainbow morning light",
                "visual_cue": "sunrise",
                "instructions": [
                    "Open curtains to let rainbow light in",
                    "Take 3 deep breaths",
                    "Stretch like a colorful butterfly"
                ],
                "sensory_considerations": ["gradual lighting", "gentle sounds"],
                "completed": False
            },
            {
                "name": "💎 Crystal Clear Hygiene",
                "duration_minutes": 20,
                "description": "Sparkling clean morning routine",
                "visual_cue": "sparkles",
                "instructions": [
                    "Brush teeth until they sparkle",
                    "Wash face with gentle rainbow bubbles",
                    "Style hair for the day"
                ],
                "sensory_considerations": ["soft textures", "pleasant scents"],
                "completed": False
            },
            {
                "name": "🦄 Magical Outfit Selection",
                "duration_minutes": 15,
                "description": "Choose your magical outfit for the day",
                "visual_cue": "clothes",
                "instructions": [
                    "Check the weather rainbow",
                    "Pick comfortable magical clothes",
                    "Add a touch of your favorite color"
                ],
                "sensory_considerations": ["soft fabrics", "comfortable fit"],
                "completed": False
            },
            {
                "name": "🍓 Berry Rainbow Breakfast",
                "duration_minutes": 25,
                "description": "Nourishing rainbow breakfast feast",
                "visual_cue": "rainbow",
                "instructions": [
                    "Prepare colorful healthy breakfast",
                    "Eat mindfully and taste the rainbow",
                    "Clean up your magical kitchen space"
                ],
                "sensory_considerations": ["colorful foods", "pleasant tastes"],
                "completed": False
            },
            {
                "name": "🎒 Adventure Pack Preparation",
                "duration_minutes": 15,
                "description": "Pack for your daily adventure",
                "visual_cue": "backpack",
                "instructions": [
                    "Check your magical schedule",
                    "Pack rainbow supplies",
                    "Gather books and dreams"
                ],
                "sensory_considerations": ["organized space", "completion satisfaction"],
                "completed": False
            }
        ]
        
        # Emma's Gentle Rainbow Journey (7-year-old)
        emma_activities = [
            {
                "name": "🌸 Flower Power Wake-Up",
                "duration_minutes": 10,
                "description": "Gentle flower-powered morning start",
                "visual_cue": "flower",
                "instructions": [
                    "Listen to soft morning bird songs",
                    "Stretch like a blooming flower",
                    "Smile at the new day"
                ],
                "sensory_considerations": ["soft sounds", "gentle movements"],
                "completed": False
            },
            {
                "name": "👗 Princess Rainbow Dressing",
                "duration_minutes": 15,
                "description": "Get dressed like a rainbow princess",
                "visual_cue": "princess",
                "instructions": [
                    "Pick your favorite rainbow outfit",
                    "Put on clothes step by step",
                    "Look in the mirror and smile"
                ],
                "sensory_considerations": ["soft materials", "step-by-step process"],
                "completed": False
            },
            {
                "name": "🥞 Magical Pancake Breakfast",
                "duration_minutes": 20,
                "description": "Enjoy magical rainbow pancakes",
                "visual_cue": "pancakes",
                "instructions": [
                    "Sit at your special breakfast spot",
                    "Eat yummy rainbow pancakes slowly",
                    "Drink magical morning milk"
                ],
                "sensory_considerations": ["familiar foods", "comfortable seating"],
                "completed": False
            },
            {
                "name": "🪥 Sparkle Tooth Brushing",
                "duration_minutes": 10,
                "description": "Make teeth sparkle like stars",
                "visual_cue": "star",
                "instructions": [
                    "Use soft rainbow toothbrush",
                    "Brush for the magic 2 minutes",
                    "Rinse with sparkling water"
                ],
                "sensory_considerations": ["gentle brushing", "mild flavors"],
                "completed": False
            },
            {
                "name": "🎈 Balloon School Bag Packing",
                "duration_minutes": 10,
                "description": "Pack your balloon-light school bag",
                "visual_cue": "balloon",
                "instructions": [
                    "Find your rainbow homework",
                    "Pack your magical lunch",
                    "Get your favorite school supplies"
                ],
                "sensory_considerations": ["light materials", "colorful organization"],
                "completed": False
            }
        ]
        
        async with aiosqlite.connect(self.db_path) as db:
            # Update Ananya's routine
            await db.execute("""
                UPDATE routines 
                SET name = 'Ananya''s Rainbow Morning Adventure',
                    activities = ?,
                    total_activities = 5
                WHERE id = 1
            """, (json.dumps(ananya_activities),))
            
            # Update Emma's routine  
            await db.execute("""
                UPDATE routines 
                SET name = 'Emma''s Gentle Rainbow Journey',
                    activities = ?,
                    total_activities = 5
                WHERE id = 2
            """, (json.dumps(emma_activities),))
            
            await db.commit()
            
        self.log_test("Setup", "PASS", "Rainbow-themed routines created successfully!")
        
    async def cleanup_test_data(self):
        """Clean up test data for fresh start."""
        self.log_test("Cleanup", "RUNNING", "Cleaning test data...")
        
        async with aiosqlite.connect(self.db_path) as db:
            # Remove all routine sessions
            await db.execute("DELETE FROM routine_sessions")
            await db.commit()
            
        self.log_test("Cleanup", "PASS", "Test data cleaned successfully!")
        
    def api_request(self, method: str, endpoint: str, data: Dict = None) -> Dict:
        """Make API request with error handling."""
        try:
            url = f"{self.base_url}{endpoint}"
            if method.upper() == "GET":
                response = requests.get(url, timeout=10)
            elif method.upper() == "POST":
                response = requests.post(url, data=data, timeout=10)
            else:
                raise ValueError(f"Unsupported method: {method}")
                
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
            
    async def test_routine_starting_via_chat(self, child_id: int, child_name: str):
        """Test starting routine through chat interface."""
        test_name = f"Chat Routine Start ({child_name})"
        self.log_test(test_name, "RUNNING", f"Testing chat-based routine start for child {child_id}...")
        
        # Test chat command
        chat_response = self.api_request("POST", "/api/chat", {
            "child_id": child_id,
            "message": "start my morning routine"
        })
        
        if "error" in chat_response:
            self.log_test(test_name, "FAIL", f"API error: {chat_response['error']}")
            return False
            
        # Check for success indicators
        success_indicators = [
            "Let's start your",
            "routine!",
            "First Activity",
            "adventure"
        ]
        
        response_text = chat_response.get("text", "").lower()
        if any(indicator.lower() in response_text for indicator in success_indicators):
            self.log_test(test_name, "PASS", "Routine started successfully via chat!")
            return True
        else:
            self.log_test(test_name, "FAIL", f"Unexpected response: {chat_response.get('text', 'No text')}")
            return False
            
    async def test_active_session_creation(self, child_id: int, child_name: str):
        """Test that active session was created properly."""
        test_name = f"Active Session Creation ({child_name})"
        self.log_test(test_name, "RUNNING", f"Checking active session for child {child_id}...")
        
        # Get active sessions
        sessions = self.api_request("GET", f"/api/child/{child_id}/active-sessions")
        
        if "error" in sessions:
            self.log_test(test_name, "FAIL", f"API error: {sessions['error']}")
            return None
            
        if not sessions or len(sessions) == 0:
            self.log_test(test_name, "FAIL", "No active sessions found")
            return None
            
        session = sessions[0]
        expected_fields = ["id", "routine_id", "current_activity", "progress", "current_activity_name"]
        
        for field in expected_fields:
            if field not in session:
                self.log_test(test_name, "FAIL", f"Missing field: {field}")
                return None
                
        # Verify initial state
        if session["current_activity"] != 0:
            self.log_test(test_name, "FAIL", f"Expected current_activity=0, got {session['current_activity']}")
            return None
            
        if session["progress"] != 0.0:
            self.log_test(test_name, "FAIL", f"Expected progress=0.0, got {session['progress']}")
            return None
            
        self.log_test(test_name, "PASS", f"Active session created correctly: {session['current_activity_name']}")
        return session
        
    async def test_activity_completion_workflow(self, child_id: int, child_name: str, session: Dict):
        """Test complete activity workflow progression."""
        test_name = f"Activity Workflow ({child_name})"
        self.log_test(test_name, "RUNNING", f"Testing complete activity workflow for child {child_id}...")
        
        try:
            activities = json.loads(session["activities"])
        except:
            self.log_test(test_name, "FAIL", "Could not parse activities JSON")
            return False
            
        total_activities = len(activities)
        routine_id = session["routine_id"]
        
        # Complete each activity one by one
        for i, activity in enumerate(activities):
            activity_name = activity["name"]
            step_test = f"Complete Activity {i+1}/{total_activities}"
            self.log_test(step_test, "RUNNING", f"Completing: {activity_name}")
            
            # Complete the activity via chat
            completion_response = self.api_request("POST", "/api/chat", {
                "child_id": child_id,
                "message": f"I finished {activity_name}",
                "routine_id": routine_id,
                "current_activity": activity_name
            })
            
            if "error" in completion_response:
                self.log_test(step_test, "FAIL", f"API error: {completion_response['error']}")
                return False
                
            # Check updated session state
            time.sleep(1)  # Allow for sync
            updated_sessions = self.api_request("GET", f"/api/child/{child_id}/active-sessions")
            
            if "error" in updated_sessions:
                self.log_test(step_test, "FAIL", f"Session check error: {updated_sessions['error']}")
                return False
                
            # Verify progression
            expected_progress = ((i + 1) / total_activities) * 100
            
            if i == total_activities - 1:
                # Last activity - routine should be completed
                if len(updated_sessions) > 0:
                    self.log_test(step_test, "FAIL", "Routine should be completed but session still active")
                    return False
                else:
                    self.log_test(step_test, "PASS", f"Routine completed! {activity_name} was final activity")
            else:
                # Middle activity - check progress
                if len(updated_sessions) == 0:
                    self.log_test(step_test, "FAIL", "Session disappeared unexpectedly")
                    return False
                    
                current_session = updated_sessions[0]
                actual_progress = current_session["progress"]
                
                if abs(actual_progress - expected_progress) > 1.0:  # Allow 1% tolerance
                    self.log_test(step_test, "FAIL", f"Progress mismatch: expected {expected_progress}%, got {actual_progress}%")
                    return False
                    
                next_activity_name = current_session["current_activity_name"]
                self.log_test(step_test, "PASS", f"Progress: {actual_progress}% → Next: {next_activity_name}")
                
        self.log_test(test_name, "PASS", "Complete activity workflow successful!")
        return True
        
    async def test_routine_completion_detection(self, child_id: int, child_name: str):
        """Test that routine completion is properly detected."""
        test_name = f"Routine Completion ({child_name})"
        self.log_test(test_name, "RUNNING", f"Verifying routine completion for child {child_id}...")
        
        # Check no active sessions
        sessions = self.api_request("GET", f"/api/child/{child_id}/active-sessions")
        
        if "error" in sessions:
            self.log_test(test_name, "FAIL", f"API error: {sessions['error']}")
            return False
            
        if len(sessions) > 0:
            self.log_test(test_name, "FAIL", f"Expected no active sessions, found {len(sessions)}")
            return False
            
        # Check database for completed session
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                SELECT rs.status, rs.progress, rs.completed_at
                FROM routine_sessions rs
                WHERE rs.child_id = ?
                ORDER BY rs.started_at DESC
                LIMIT 1
            """, (child_id,))
            result = await cursor.fetchone()
            
            if not result:
                self.log_test(test_name, "FAIL", "No routine session found in database")
                return False
                
            status, progress, completed_at = result
            
            if status != "completed":
                self.log_test(test_name, "FAIL", f"Expected status='completed', got '{status}'")
                return False
                
            if progress != 100.0:
                self.log_test(test_name, "FAIL", f"Expected progress=100.0, got {progress}")
                return False
                
            if not completed_at:
                self.log_test(test_name, "FAIL", "Missing completion timestamp")
                return False
                
        self.log_test(test_name, "PASS", f"Routine properly marked as completed at {completed_at}")
        return True
        
    async def test_fresh_routine_restart(self, child_id: int, child_name: str):
        """Test starting a fresh routine after completion."""
        test_name = f"Fresh Restart ({child_name})"
        self.log_test(test_name, "RUNNING", f"Testing fresh routine restart for child {child_id}...")
        
        # Start routine again
        start_success = await self.test_routine_starting_via_chat(child_id, child_name)
        if not start_success:
            self.log_test(test_name, "FAIL", "Could not restart routine")
            return False
            
        # Verify fresh state
        sessions = self.api_request("GET", f"/api/child/{child_id}/active-sessions")
        
        if "error" in sessions or len(sessions) == 0:
            self.log_test(test_name, "FAIL", "No session created on restart")
            return False
            
        session = sessions[0]
        
        if session["current_activity"] != 0 or session["progress"] != 0.0:
            self.log_test(test_name, "FAIL", "Session not fresh on restart")
            return False
            
        self.log_test(test_name, "PASS", "Fresh routine restart successful!")
        return True
        
    def print_test_summary(self):
        """Print colorful test summary."""
        print("\n" + "="*60)
        print("🌈 RAINBOW BRIDGE E2E TEST SUMMARY 🌈")
        print("="*60)
        
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t["status"] == "PASS"])
        failed_tests = len([t for t in self.test_results if t["status"] == "FAIL"])
        
        print(f"📊 Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"🎯 Success Rate: {(passed_tests/total_tests*100):.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if result["status"] == "FAIL":
                    print(f"   • {result['test']}: {result['details']}")
                    
        print("\n🌈 Test completed! ✨")
        
    async def run_complete_test_suite(self):
        """Run the complete end-to-end test suite."""
        print("🌈 Starting Rainbow Bridge E2E Test Suite! ✨\n")
        
        try:
            # Setup
            await self.cleanup_test_data()
            await self.setup_rainbow_themed_routines()
            
            # Test both children
            for child_id, child_name in [(1, "Ananya"), (2, "Emma")]:
                print(f"\n🧒 Testing workflow for {child_name} (Child {child_id})...")
                
                # Test 1: Start routine via chat
                start_success = await self.test_routine_starting_via_chat(child_id, child_name)
                if not start_success:
                    continue
                    
                # Test 2: Check active session creation
                session = await self.test_active_session_creation(child_id, child_name)
                if not session:
                    continue
                    
                # Test 3: Complete activity workflow
                workflow_success = await self.test_activity_completion_workflow(child_id, child_name, session)
                if not workflow_success:
                    continue
                    
                # Test 4: Verify routine completion
                completion_success = await self.test_routine_completion_detection(child_id, child_name)
                if not completion_success:
                    continue
                    
                # Test 5: Test fresh restart
                await self.test_fresh_routine_restart(child_id, child_name)
                
        except Exception as e:
            self.log_test("Test Suite", "FAIL", f"Unexpected error: {str(e)}")
            
        finally:
            self.print_test_summary()

async def main():
    """Run the Rainbow Bridge E2E Test Suite."""
    test_suite = RainbowBridgeE2ETestSuite()
    await test_suite.run_complete_test_suite()

if __name__ == "__main__":
    asyncio.run(main())
