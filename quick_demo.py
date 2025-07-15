#!/usr/bin/env python3
"""
Quick Demo: Smart Schedule Feature

A simple script to test the AI-powered smart schedule generation.
"""

import asyncio
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.ai_assistant import SpecialKidsAI

async def quick_demo():
    """Quick demo of smart schedule generation."""
    print("🌈 Rainbow Bridge - Smart Schedule Quick Demo")
    print("=" * 50)
    
    # Initialize AI assistant
    print("🤖 Initializing AI Assistant...")
    ai = SpecialKidsAI()
    
    # Test different schedule scenarios
    scenarios = [
        {
            "description": "Morning calm activities",
            "time": "morning",
            "preferences": ["calm", "quiet", "reading"],
            "energy": "low"
        },
        {
            "description": "Afternoon creative time", 
            "time": "afternoon",
            "preferences": ["creative", "drawing", "music"],
            "energy": "high"
        },
        {
            "description": "Evening wind-down",
            "time": "evening", 
            "preferences": ["calm", "relaxing"],
            "energy": "low"
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n🎯 Scenario {i}: {scenario['description']}")
        print(f"   Time: {scenario['time']} | Energy: {scenario['energy']}")
        print(f"   Preferences: {', '.join(scenario['preferences'])}")
        print("-" * 40)
        
        try:
            # Generate smart schedule
            result = await ai.generate_smart_schedule(
                child_id=1,
                time_of_day=scenario["time"],
                preferences=scenario["preferences"],
                energy_level=scenario["energy"]
            )
            
            if result["success"]:
                print("✅ Smart schedule generated!")
                print(f"📋 Generated {len(result['activities'])} activities:")
                
                for j, activity in enumerate(result["activities"], 1):
                    print(f"  {j}. {activity['name']}")
                    print(f"     Duration: {activity['duration']}")
                    print(f"     Description: {activity['description']}")
                    print()
                
                # Show a portion of the AI response
                ai_response = result["schedule_text"]
                if len(ai_response) > 200:
                    ai_response = ai_response[:200] + "..."
                print(f"🌈 AI Response: {ai_response}")
                
            else:
                print(f"❌ Failed to generate schedule: {result.get('error', 'Unknown error')}")
        
        except Exception as e:
            print(f"❌ Error in scenario {i}: {e}")
        
        print("\n" + "=" * 50)
    
    print("🌈 Quick demo completed! ✨")

async def test_basic_messages():
    """Test basic message processing with routine detection."""
    print("\n🗣️  Testing Basic Message Processing")
    print("=" * 40)
    
    ai = SpecialKidsAI()
    
    test_messages = [
        "Can you help me plan my morning?",
        "I want to create a bedtime routine", 
        "Schedule some drawing time for me",
        "I finished my homework",
        "I'm feeling excited today!"
    ]
    
    for message in test_messages:
        print(f"\n👦 Child: '{message}'")
        
        try:
            response = await ai.process_message(
                message=message,
                child_id=1,
                communication_type="text"
            )
            
            print(f"🌈 Rainbow Bridge: {response['text']}")
            print(f"😊 Emotion: {response['emotion']}")
            
            if response.get('routine_action'):
                print(f"🎯 Routine Action: {response['routine_action']}")
            
            if response.get('llm_source'):
                print(f"🔧 Source: {response['llm_source']}")
                
        except Exception as e:
            print(f"❌ Error processing message: {e}")

async def main():
    """Main function with options."""
    print("🌈 Rainbow Bridge Quick Demo Options:")
    print("1. Smart Schedule Generation Demo")
    print("2. Basic Message Processing Demo") 
    print("3. Both demos")
    
    try:
        choice = input("\nChoose option (1-3, or Enter for option 1): ").strip()
        
        if choice == "2":
            await test_basic_messages()
        elif choice == "3":
            await quick_demo()
            await test_basic_messages()
        else:
            # Default to smart schedule demo
            await quick_demo()
            
    except KeyboardInterrupt:
        print("\n🌈 Demo cancelled. Goodbye! ✨")
    except Exception as e:
        print(f"❌ Demo error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
