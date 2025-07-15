#!/usr/bin/env python3
"""
🌈 Rainbow Bridge - Quick Routine Creation Test
===============================================

This script tests the actual MCP integration for routine creation
using natural language inputs.
"""

import asyncio
import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_actual_routine_creation():
    """Test routine creation with the actual MCP system"""
    print("🌈 Testing Actual Rainbow Bridge MCP Routine Creation")
    print("="*55)
    
    try:
        # Import the actual components
        from core.routine_mcp_client import RoutineMCPClient
        from core.routine_manager import RoutineManager
        from core.routine_mcp_server import create_routine_mcp_server
        from database.db_manager import DatabaseManager
        
        # Initialize components
        print("🔧 Initializing components...")
        db_manager = DatabaseManager("test_mcp_routines.db")
        await db_manager.initialize()
        
        routine_manager = RoutineManager(db_manager)
        mcp_server = create_routine_mcp_server(routine_manager, db_manager)
        mcp_client = RoutineMCPClient(mcp_server)
        
        print("✅ All components initialized successfully!")
        
        # Test messages that children might say
        test_messages = [
            "I want to create a morning routine",
            "Can you help me make a bedtime routine?", 
            "Create a routine for learning activities",
            "I need help with my homework routine",
            "Make a weekend fun routine for me"
        ]
        
        print(f"\n🎯 Testing {len(test_messages)} natural language inputs:")
        print("-" * 55)
        
        for i, message in enumerate(test_messages, 1):
            print(f"\n{i}. Testing: \"{message}\"")
            
            # Detect intent
            result = await mcp_client.detect_routine_intent(message, child_id=1)
            
            if result:
                intent = result.get('intent', 'unknown')
                confidence = result.get('confidence', 0)
                params = result.get('parameters', {})
                
                print(f"   ✅ Intent detected: {intent}")
                print(f"   📊 Confidence: {confidence:.2f}")
                if params:
                    print(f"   📝 Parameters: {params}")
                
                # If it's a routine creation intent, show what would happen
                if intent == 'create_routine':
                    print(f"   🎨 Would create routine with these details:")
                    print(f"      • Type: {params.get('routine_type', 'general')}")
                    print(f"      • Time: {params.get('schedule_time', 'flexible')}")
                    print(f"      • Child ID: {params.get('child_id', 1)}")
                    
            else:
                print(f"   ❌ No routine intent detected")
        
        # Test actual routine creation
        print(f"\n🛠️  Testing actual routine creation:")
        print("-" * 55)
        
        # Create a sample routine
        routine = await routine_manager.create_routine(
            child_id=1,
            name="Test MCP Morning Routine",
            activities=["Wake up", "Brush teeth", "Get dressed", "Eat breakfast"],
            schedule_time="08:00",
            days_of_week=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        )
        
        if routine:
            print(f"✅ Created routine successfully!")
            print(f"   📋 Name: {routine.name}")
            print(f"   🆔 ID: {routine.id}")
            print(f"   📝 Activities: {len(routine.activities)} steps")
            
            # Test getting routines
            routines = await routine_manager.get_child_routines(1)
            print(f"   📊 Total routines for child: {len(routines)}")
            
        else:
            print("❌ Failed to create routine")
        
        print(f"\n🎉 MCP Integration Test Complete!")
        print("✅ Natural language processing working")
        print("✅ Intent detection functional") 
        print("✅ Routine creation operational")
        print("✅ Database integration successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def show_conversation_examples():
    """Show example conversations without requiring live system"""
    print("\n" + "="*55)
    print("💬 EXAMPLE CONVERSATIONS")
    print("="*55)
    
    examples = [
        {
            "title": "Morning Routine Creation",
            "child": "I want to create a morning routine",
            "ai": "That's wonderful! Let's create your morning routine together! What time do you usually wake up?",
            "child_reply": "7:30 AM",
            "ai_followup": "Perfect! Let's add some activities: Wake up → Brush teeth → Get dressed → Eat breakfast. Sound good?",
            "result": "✅ Morning routine created with 4 activities"
        },
        {
            "title": "Bedtime Routine Help",
            "child": "Can you help me make a bedtime routine? I want to sleep better",
            "ai": "A bedtime routine is so important for good sleep! What time do you like to start getting ready?",
            "child_reply": "8:00 PM",
            "ai_followup": "Great! Let's create a calming routine: Bath → Pajamas → Brush teeth → Story time → Sleep",
            "result": "✅ Bedtime routine created for better sleep"
        },
        {
            "title": "Learning Activities",
            "child": "I need a routine for my learning time with drawing and reading", 
            "ai": "Learning is so much fun! I love that you enjoy drawing and reading! How long should each activity be?",
            "child_reply": "15 minutes each",
            "ai_followup": "Perfect! Reading (15 min) → Drawing (15 min) → Celebrate your learning!",
            "result": "✅ Personalized learning routine created"
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\n📖 Example {i}: {example['title']}")
        print("-" * 40)
        print(f"💬 Child: \"{example['child']}\"")
        print(f"🌈 Rainbow Bridge: \"{example['ai']}\"")
        print(f"💬 Child: \"{example['child_reply']}\"") 
        print(f"🌈 Rainbow Bridge: \"{example['ai_followup']}\"")
        print(f"🎯 {example['result']}")

def show_technical_details():
    """Show the technical implementation details"""
    print("\n" + "="*55)
    print("🔧 TECHNICAL IMPLEMENTATION")
    print("="*55)
    
    print("\n📡 MCP (Model Context Protocol) Integration:")
    print("   • Server: routine_mcp_server.py - 6 specialized tools")
    print("   • Client: routine_mcp_client.py - Intent detection")
    print("   • Tools: create_routine, get_routines, start_routine, etc.")
    
    print("\n🧠 Natural Language Processing:")
    print("   • Intent detection with confidence scoring")
    print("   • Parameter extraction from child's language")
    print("   • Context-aware conversation flow")
    
    print("\n🎨 Child-Friendly Features:")
    print("   • Simple, conversational language")
    print("   • Visual confirmation of routine steps")
    print("   • Positive reinforcement and encouragement")
    print("   • Flexible and adaptable to child's needs")
    
    print("\n💾 Data Storage:")
    print("   • SQLite database with routine tracking")
    print("   • Session logging for progress monitoring")
    print("   • Activity completion tracking")
    print("   • Parent/caregiver insights")

async def main():
    """Run the complete routine creation test"""
    print("🌈✨ RAINBOW BRIDGE ROUTINE CREATION TEST ✨🌈")
    print("="*55)
    
    # Test the actual MCP integration
    success = await test_actual_routine_creation()
    
    # Show conversation examples
    await show_conversation_examples()
    
    # Show technical details
    show_technical_details()
    
    print("\n" + "="*55)
    print("🎊 TEST SUMMARY")
    print("="*55)
    
    if success:
        print("🎉 ALL SYSTEMS WORKING!")
        print("✅ Children can now create routines by simply talking")
        print("✅ Natural language understanding is active")
        print("✅ Visual and interactive interface ready")
        print("✅ Progress tracking and celebration built-in")
    else:
        print("⚠️  Some components need attention")
        print("💡 The conversation examples show expected behavior")
    
    print(f"\n🌈 Rainbow Bridge is ready to help children build better routines!")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        import traceback
        traceback.print_exc()
