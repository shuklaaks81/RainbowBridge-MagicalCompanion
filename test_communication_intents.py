#!/usr/bin/env python3
"""
Test Enhanced Communication Intent Detection

This script tests the new communication intent detection system to ensure
it properly matches various types of child communication patterns.
"""

import asyncio
import os
import sys
import logging
from typing import Dict, Any

# Set up path to import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.ai_assistant import SpecialKidsAI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CommunicationIntentTester:
    """Test the enhanced communication intent detection system."""
    
    def __init__(self):
        self.ai_assistant = SpecialKidsAI()
        
    def get_test_messages(self) -> Dict[str, list]:
        """Get test messages categorized by expected intent."""
        return {
            "emotional_expression": [
                "I feel sad today",
                "I'm really happy!",
                "I'm angry about this",
                "I feel scared",
                "I'm so excited!",
                "I'm tired and cranky",
                "I feel upset",
                "I'm feeling good today"
            ],
            "need_expression": [
                "I'm hungry",
                "I need help with this",
                "I want water",
                "I need to go to the bathroom",
                "Can you help me?",
                "I'm thirsty",
                "I need a break",
                "Help me please"
            ],
            "social_communication": [
                "Hello!",
                "Thank you so much",
                "Goodbye for now",
                "Please help me",
                "Yes, I want that",
                "No, I don't like it",
                "Hi there!",
                "Sorry about that"
            ],
            "learning_request": [
                "What is this?",
                "How do I do this?",
                "Can you teach me?",
                "I want to learn about animals",
                "Show me how to draw",
                "Explain this to me",
                "What does this mean?",
                "Help me understand"
            ],
            "activity_interest": [
                "I want to play games",
                "Can we draw together?",
                "I like music",
                "Let's play outside",
                "I want to read books",
                "Can we have fun?",
                "I love playing with toys",
                "Let's do something fun"
            ],
            "sensory_feedback": [
                "This is too loud",
                "The light is too bright",
                "This feels rough",
                "It's too noisy here",
                "I like soft things",
                "This sound is nice",
                "The room is too hot",
                "I need quiet time"
            ],
            "confusion_difficulty": [
                "I don't understand",
                "This is too hard",
                "I'm confused",
                "I can't do this",
                "I'm stuck",
                "This is difficult",
                "I don't know how",
                "Help, I'm lost"
            ],
            "achievement_sharing": [
                "I did it!",
                "Look what I made!",
                "I finished my homework",
                "I completed the puzzle",
                "I'm proud of myself",
                "I accomplished this",
                "I succeeded!",
                "I made something cool"
            ]
        }
    
    async def test_intent_detection(self):
        """Test intent detection for various message types."""
        print("🌈 Testing Enhanced Communication Intent Detection\n")
        
        test_messages = self.get_test_messages()
        
        # Test each category
        for category, messages in test_messages.items():
            print(f"\n📋 Testing {category.replace('_', ' ').title()} Messages:")
            print("=" * 60)
            
            for message in messages:
                try:
                    # Test intent detection
                    intent_result = await self.ai_assistant._detect_communication_intent(message, child_id=1)
                    
                    if intent_result:
                        primary_intent = intent_result["primary_intent"]
                        print(f"✅ Message: '{message}'")
                        print(f"   Intent: {primary_intent['intent']}")
                        print(f"   Confidence: {primary_intent['confidence']:.2f}")
                        print(f"   Visual Cues: {primary_intent['visual_cues']}")
                        print(f"   Response Type: {primary_intent['response_type']}")
                        
                        # Check if multiple intents detected
                        if intent_result["has_multiple_intents"]:
                            print(f"   Secondary Intents: {len(intent_result['secondary_intents'])}")
                        
                        # Test response generation
                        response = await self.ai_assistant._generate_intent_based_response(intent_result, message)
                        print(f"   Response: {response['text'][:100]}...")
                        print()
                    else:
                        print(f"❌ Message: '{message}'")
                        print(f"   No intent detected")
                        print()
                        
                except Exception as e:
                    print(f"❌ Error testing '{message}': {str(e)}")
                    print()
    
    async def test_full_processing(self):
        """Test full message processing with enhanced intent detection."""
        print("\n🔄 Testing Full Message Processing\n")
        
        test_messages = [
            "I'm feeling really sad today",
            "Can you help me with my homework?",
            "I want to play games!",
            "This room is too loud for me",
            "I finished my art project!"
        ]
        
        for message in test_messages:
            try:
                print(f"🎯 Processing: '{message}'")
                result = await self.ai_assistant.process_message(
                    message=message,
                    child_id=1,
                    communication_type="text"
                )
                
                print(f"   Response: {result['text']}")
                print(f"   Visual Cues: {result['visual_cues']}")
                print(f"   Emotion: {result['emotion']}")
                print(f"   Confidence: {result['confidence']:.2f}")
                print(f"   Actions: {result['suggested_actions']}")
                print(f"   LLM Source: {result.get('llm_source', 'unknown')}")
                print()
                
            except Exception as e:
                print(f"❌ Error processing '{message}': {str(e)}")
                print()
    
    async def run_tests(self):
        """Run all communication intent tests."""
        print("🌈 Rainbow Bridge - Enhanced Communication Intent Testing 🌈")
        print("=" * 70)
        
        try:
            await self.test_intent_detection()
            await self.test_full_processing()
            
            print("\n✅ All communication intent tests completed!")
            print("🌈 Enhanced intent detection is ready for better communication! ✨")
            
        except Exception as e:
            print(f"\n❌ Test failed with error: {str(e)}")
            logger.error(f"Test error: {str(e)}")

async def main():
    """Main test function."""
    tester = CommunicationIntentTester()
    await tester.run_tests()

if __name__ == "__main__":
    asyncio.run(main())
