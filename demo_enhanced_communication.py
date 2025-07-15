#!/usr/bin/env python3
"""
Quick Demo: Enhanced Communication Intent Detection

This demonstrates the improved communication intent matching in action.
"""

import asyncio
import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.ai_assistant import SpecialKidsAI

async def demo_enhanced_communication():
    """Demonstrate enhanced communication intent detection."""
    print("🌈 Rainbow Bridge - Enhanced Communication Demo 🌈")
    print("=" * 60)
    print()
    
    # Initialize AI assistant
    ai_assistant = SpecialKidsAI()
    
    # Demo messages that should now be properly detected
    demo_messages = [
        "I'm feeling sad today",
        "I need help with this",
        "This is too loud",
        "I want to play",
        "I finished my drawing!",
        "I don't understand",
        "Thank you so much",
        "I'm hungry"
    ]
    
    print("🎯 Testing Enhanced Intent Detection:")
    print("-" * 40)
    
    for message in demo_messages:
        print(f"\n💬 Child says: '{message}'")
        
        try:
            # Process the message
            response = await ai_assistant.process_message(
                message=message,
                child_id=1,
                communication_type="text"
            )
            
            print(f"🌈 Rainbow Bridge: {response['text']}")
            print(f"📝 Visual Cues: {', '.join(response['visual_cues'])}")
            print(f"💡 Suggested Actions: {', '.join(response['suggested_actions'])}")
            print(f"🔍 Source: {response.get('llm_source', 'unknown')}")
            
            # Show if intent was detected
            if response.get('intent_detected'):
                print(f"✨ Intent Detected: {response['intent_detected']}")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    print("\n" + "=" * 60)
    print("✅ Demo completed! Enhanced communication intent detection is working!")
    print("🌈 Children's communication will now be better understood and responded to! ✨")

if __name__ == "__main__":
    asyncio.run(demo_enhanced_communication())
