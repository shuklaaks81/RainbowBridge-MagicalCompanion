#!/usr/bin/env python3
"""
Rainbow Bridge - Smart Schedule Demo

This demo showcases the enhanced AI-powered smart schedule feature
and other capabilities of the Rainbow Bridge system for autistic children.
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Dict, Any

# Import our core modules
from core.ai_assistant import SpecialKidsAI
from core.routine_mcp_client import RoutineMCPClient, create_routine_mcp_client
from database.db_manager import DatabaseManager

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RainbowBridgeDemo:
    """Demo class to showcase Rainbow Bridge features."""
    
    def __init__(self):
        self.db_manager = None
        self.ai_assistant = None
        self.mcp_client = None
        self.child_id = 1  # Demo child ID
    
    async def setup(self):
        """Initialize all components for the demo."""
        print("🌈 Setting up Rainbow Bridge Demo...")
        
        # Initialize database
        self.db_manager = DatabaseManager()
        await self.db_manager.initialize()
        print("✅ Database initialized")
        
        # Initialize AI assistant (will auto-detect MCP server)
        self.ai_assistant = SpecialKidsAI()
        print("✅ AI Assistant initialized")
        
        # Create demo child record if it doesn't exist
        await self._create_demo_child()
        print("✅ Demo child profile created")
        
        print("🌈 Rainbow Bridge Demo is ready!")
        print("=" * 60)
    
    async def _create_demo_child(self):
        """Create a demo child profile."""
        try:
            # Check if child exists
            query = "SELECT id FROM children WHERE id = ?"
            result = await self.db_manager.fetch_one(query, (self.child_id,))
            
            if not result:
                # Create demo child
                insert_query = """
                INSERT INTO children (id, name, age, communication_level, preferences) 
                VALUES (?, ?, ?, ?, ?)
                """
                preferences = json.dumps({
                    "visual_support": True,
                    "routine_focus": True,
                    "sensory_sensitive": True,
                    "interests": ["drawing", "music", "animals", "colors"]
                })
                
                await self.db_manager.execute(
                    insert_query, 
                    (self.child_id, "Alex", 8, "moderate", preferences)
                )
                logger.info("Created demo child profile")
        except Exception as e:
            logger.warning(f"Demo child setup: {e}")
    
    async def run_demo(self):
        """Run the complete Rainbow Bridge demo."""
        await self.setup()
        
        print("\n🎨 Welcome to Rainbow Bridge - Magical Companion Demo! 🌈")
        print("This demo showcases AI-powered schedule generation for autistic children")
        print("=" * 60)
        
        demos = [
            ("💬 Basic AI Communication", self.demo_basic_communication),
            ("🕐 Smart Schedule Generation", self.demo_smart_schedule),
            ("📅 Routine Management", self.demo_routine_management),
            ("🎯 Activity Completion", self.demo_activity_completion),
            ("🔧 System Status Check", self.demo_system_status),
        ]
        
        for title, demo_func in demos:
            print(f"\n{title}")
            print("-" * 50)
            try:
                await demo_func()
                print("✅ Demo completed successfully")
            except Exception as e:
                print(f"❌ Demo error: {e}")
                logger.error(f"Demo error in {title}: {e}")
            
            # Pause between demos
            await asyncio.sleep(1)
        
        print("\n🌈 Demo completed! Thank you for exploring Rainbow Bridge! ✨")
    
    async def demo_basic_communication(self):
        """Demo basic AI communication capabilities."""
        test_messages = [
            "Hi, I'm feeling happy today!",
            "I want to draw something colorful",
            "I'm feeling a bit overwhelmed"
        ]
        
        for message in test_messages:
            print(f"\n👦 Child says: '{message}'")
            
            response = await self.ai_assistant.process_message(
                message=message,
                child_id=self.child_id,
                communication_type="text"
            )
            
            print(f"🌈 Rainbow Bridge: {response['text']}")
            print(f"😊 Emotion: {response['emotion']}")
            print(f"🎨 Visual cues: {', '.join(response['visual_cues'])}")
            print(f"💡 Suggested actions: {', '.join(response['suggested_actions'])}")
    
    async def demo_smart_schedule(self):
        """Demo the new smart schedule generation feature."""
        schedule_requests = [
            {
                "message": "Can you plan my morning with calm activities?",
                "time": "morning",
                "preferences": ["calm", "quiet"],
                "energy": "low"
            },
            {
                "message": "I want to do fun activities this afternoon",
                "time": "afternoon", 
                "preferences": ["fun", "creative"],
                "energy": "high"
            },
            {
                "message": "Help me schedule some drawing and music time",
                "time": "evening",
                "preferences": ["drawing", "music"],
                "energy": "medium"
            }
        ]
        
        for req in schedule_requests:
            print(f"\n👦 Child says: '{req['message']}'")
            
            # Test smart schedule generation
            schedule = await self.ai_assistant.generate_smart_schedule(
                child_id=self.child_id,
                time_of_day=req["time"],
                preferences=req["preferences"],
                energy_level=req["energy"]
            )
            
            if schedule["success"]:
                print(f"🌈 Rainbow Bridge generated a magical schedule!")
                print(f"📋 Schedule for {req['time']} (energy: {req['energy']}):")
                
                for i, activity in enumerate(schedule["activities"], 1):
                    print(f"  {i}. {activity['name']} ({activity['duration']})")
                    print(f"     {activity['description']}")
                
                print(f"\n✨ Full AI Response:")
                print(f"   {schedule['schedule_text'][:200]}...")
            else:
                print(f"❌ Schedule generation failed: {schedule.get('error', 'Unknown error')}")
    
    async def demo_routine_management(self):
        """Demo routine management through MCP client."""
        # Test routine-related messages
        routine_messages = [
            "I want to create a morning routine",
            "Show me my routines", 
            "Start my bedtime routine",
            "I need help with my schedule"
        ]
        
        for message in routine_messages:
            print(f"\n👦 Child says: '{message}'")
            
            response = await self.ai_assistant.process_message(
                message=message,
                child_id=self.child_id,
                communication_type="text"
            )
            
            print(f"🌈 Rainbow Bridge: {response['text']}")
            
            if "routine_action" in response:
                print(f"🎯 Routine action detected: {response['routine_action']}")
                print(f"🔧 LLM source: {response['llm_source']}")
    
    async def demo_activity_completion(self):
        """Demo activity completion functionality."""
        # First create a sample routine
        print("\n📝 Creating a sample routine for demo...")
        
        try:
            # Create a simple routine
            routine_data = {
                "name": "Demo Afternoon Routine",
                "activities": [
                    {"name": "Reading Time", "duration": "15 minutes"},
                    {"name": "Drawing Activity", "duration": "20 minutes"},
                    {"name": "Calm Down Time", "duration": "10 minutes"}
                ],
                "time_of_day": "afternoon"
            }
            
            # Test activity completion
            completion_messages = [
                "I finished reading",
                "Done with drawing", 
                "Completed calm time"
            ]
            
            for message in completion_messages:
                print(f"\n👦 Child says: '{message}'")
                
                response = await self.ai_assistant.process_message(
                    message=message,
                    child_id=self.child_id,
                    communication_type="text"
                )
                
                print(f"🌈 Rainbow Bridge: {response['text']}")
                if "routine_action" in response:
                    print(f"🎯 Action: {response['routine_action']}")
        
        except Exception as e:
            print(f"Activity completion demo: {e}")
    
    async def demo_system_status(self):
        """Demo system status and capabilities."""
        print("\n🔍 Checking Rainbow Bridge system status...")
        
        # Check LLM status
        llm_status = self.ai_assistant.get_llm_status()
        print(f"🤖 Local mode: {llm_status['local_mode']}")
        print(f"☁️  OpenAI available: {llm_status['openai_available']}")
        print(f"🔄 Fallback enabled: {llm_status['fallback_enabled']}")
        
        if llm_status['available_providers']:
            print(f"🏠 Local providers: {', '.join(llm_status['available_providers'])}")
        
        # Test connectivity
        print("\n🌐 Testing LLM connectivity...")
        try:
            connectivity = await self.ai_assistant.test_llm_connectivity()
            
            for provider, status in connectivity['local_providers'].items():
                status_icon = "✅" if status['available'] else "❌"
                print(f"{status_icon} {provider}: {status.get('error', 'OK')}")
            
            openai_status = connectivity['openai']
            openai_icon = "✅" if openai_status['available'] else "❌"
            print(f"{openai_icon} OpenAI: {openai_status.get('error', 'OK')}")
            
        except Exception as e:
            print(f"❌ Connectivity test failed: {e}")
    
    async def interactive_demo(self):
        """Run an interactive demo where you can type messages."""
        await self.setup()
        
        print("\n🎨 Interactive Rainbow Bridge Demo! 🌈")
        print("Type messages to chat with Rainbow Bridge (type 'quit' to exit)")
        print("Try these example commands:")
        print("  - 'Plan my morning with calm activities'")
        print("  - 'I want to create a bedtime routine'")
        print("  - 'Help me schedule drawing time'")
        print("  - 'I finished my homework'")
        print("=" * 60)
        
        while True:
            try:
                message = input("\n👦 You: ").strip()
                
                if message.lower() in ['quit', 'exit', 'bye']:
                    print("🌈 Goodbye! Thanks for using Rainbow Bridge! ✨")
                    break
                
                if not message:
                    continue
                
                print("🌈 Rainbow Bridge is thinking...")
                
                response = await self.ai_assistant.process_message(
                    message=message,
                    child_id=self.child_id,
                    communication_type="text"
                )
                
                print(f"\n🌈 Rainbow Bridge: {response['text']}")
                print(f"😊 Emotion: {response['emotion']}")
                print(f"🎨 Visual cues: {', '.join(response['visual_cues'])}")
                
                if response.get('routine_action'):
                    print(f"🎯 Routine action: {response['routine_action']}")
                
                if 'activities' in response and response.get('activities'):
                    print("📋 Generated activities:")
                    for i, activity in enumerate(response['activities'], 1):
                        print(f"  {i}. {activity.get('name', 'Activity')} ({activity.get('duration', '15 min')})")
                
            except KeyboardInterrupt:
                print("\n🌈 Goodbye! Thanks for using Rainbow Bridge! ✨")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

async def main():
    """Main demo function."""
    demo = RainbowBridgeDemo()
    
    print("🌈 Rainbow Bridge Demo Options:")
    print("1. Run full automated demo")
    print("2. Run interactive demo")
    print("3. Quick smart schedule test")
    
    try:
        choice = input("\nChoose option (1-3): ").strip()
        
        if choice == "1":
            await demo.run_demo()
        elif choice == "2":
            await demo.interactive_demo()
        elif choice == "3":
            await demo.setup()
            print("\n🕐 Quick Smart Schedule Test")
            schedule = await demo.ai_assistant.generate_smart_schedule(
                child_id=1,
                time_of_day="morning",
                preferences=["calm", "creative"],
                energy_level="medium"
            )
            
            if schedule["success"]:
                print("✅ Smart schedule generated!")
                print(f"📋 Activities: {len(schedule['activities'])} generated")
                for activity in schedule["activities"]:
                    print(f"  • {activity['name']} ({activity['duration']})")
            else:
                print(f"❌ Failed: {schedule.get('error')}")
        else:
            print("Running full demo by default...")
            await demo.run_demo()
    
    except KeyboardInterrupt:
        print("\n🌈 Demo cancelled. Goodbye! ✨")
    except Exception as e:
        print(f"❌ Demo error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
