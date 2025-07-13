#!/usr/bin/env python3
"""
🌈 Rainbow Bridge - Routine Creation Interaction Sample
=====================================================

This script demonstrates how children can create routines using natural language
through the Rainbow Bridge MCP integration. The interactions are designed to be
child-friendly and follow the sensory-friendly design principles.
"""

import asyncio
import sys
import os
import json
from datetime import datetime

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.ai_assistant import SpecialKidsAI
from core.routine_manager import RoutineManager
from database.db_manager import DatabaseManager

class RoutineCreationDemo:
    def __init__(self):
        self.db_manager = None
        self.routine_manager = None
        self.ai_assistant = None
        self.child_id = 1  # Demo child
        
    async def initialize(self):
        """Initialize all components"""
        print("🌈 Initializing Rainbow Bridge components...")
        
        # Initialize database
        self.db_manager = DatabaseManager("demo_routines.db")
        await self.db_manager.initialize()
        print("✅ Database ready")
        
        # Initialize routine manager
        self.routine_manager = RoutineManager(self.db_manager)
        print("✅ Routine manager ready")
        
        # Initialize AI assistant with MCP
        self.ai_assistant = SpecialKidsAI(self.db_manager)
        print("✅ AI assistant with MCP ready")
        
        # Create demo child profile if not exists
        await self.ensure_demo_child()
        
    async def ensure_demo_child(self):
        """Ensure we have a demo child profile"""
        try:
            # Try to get existing child
            children = await self.db_manager.get_children()
            if not children:
                # Create demo child
                child_data = {
                    "name": "Alex",
                    "age": 8,
                    "communication_level": "visual_and_text",
                    "preferences": {
                        "favorite_color": "blue",
                        "interests": ["drawing", "music", "reading"]
                    }
                }
                child_id = await self.db_manager.create_child_profile(
                    child_data["name"],
                    child_data["age"],
                    child_data["communication_level"],
                    json.dumps(child_data["preferences"])
                )
                self.child_id = child_id
                print(f"✅ Created demo child: {child_data['name']} (ID: {child_id})")
            else:
                self.child_id = children[0]["id"]
                print(f"✅ Using existing child: {children[0]['name']} (ID: {self.child_id})")
        except Exception as e:
            print(f"⚠️  Using default child ID: {e}")

    async def demonstrate_routine_creation(self):
        """Demonstrate various ways to create routines"""
        print("\n" + "="*60)
        print("🎨 ROUTINE CREATION INTERACTION SAMPLES")
        print("="*60)
        
        # Sample interactions that children might have
        sample_interactions = [
            {
                "title": "Morning Routine Creation",
                "child_message": "I want to create a morning routine to help me get ready for school",
                "description": "Child wants to establish a structured morning routine"
            },
            {
                "title": "Bedtime Routine Creation", 
                "child_message": "Can you help me make a bedtime routine? I want to sleep better",
                "description": "Child seeks help with sleep preparation routine"
            },
            {
                "title": "Learning Activities Routine",
                "child_message": "I need a routine for my learning time with drawing and reading",
                "description": "Child wants to organize learning activities"
            },
            {
                "title": "Calm Down Routine",
                "child_message": "Create a routine to help me feel calm when I'm upset",
                "description": "Child needs emotional regulation support"
            },
            {
                "title": "Weekend Fun Routine",
                "child_message": "I want to make a fun routine for Saturday mornings",
                "description": "Child wants to structure enjoyable weekend activities"
            }
        ]
        
        for i, interaction in enumerate(sample_interactions, 1):
            await self.simulate_interaction(i, interaction)
            print("\n" + "-"*50)
            await asyncio.sleep(1)  # Pause between interactions
    
    async def simulate_interaction(self, number, interaction):
        """Simulate a single routine creation interaction"""
        print(f"\n🎯 INTERACTION {number}: {interaction['title']}")
        print(f"📝 Context: {interaction['description']}")
        print(f"💬 Child says: \"{interaction['child_message']}\"")
        
        try:
            # Process the message through AI assistant
            print("\n🤖 Rainbow Bridge AI is thinking...")
            response = await self.ai_assistant.get_response(
                message=interaction['child_message'],
                child_id=self.child_id,
                context={"interaction_type": "routine_creation"}
            )
            
            print(f"🌈 Rainbow Bridge responds:")
            print(f"   {response}")
            
            # Check if a routine was actually created
            routines = await self.routine_manager.get_child_routines(self.child_id)
            latest_routine = routines[-1] if routines else None
            
            if latest_routine:
                await self.display_created_routine(latest_routine)
            else:
                print("💡 Note: This would guide the child through routine creation steps")
                
        except Exception as e:
            print(f"❌ Interaction error: {str(e)}")
            # Show what would happen in a perfect scenario
            await self.show_expected_outcome(interaction)
    
    async def display_created_routine(self, routine):
        """Display details of a created routine"""
        print(f"\n✨ ROUTINE CREATED SUCCESSFULLY!")
        print(f"   📋 Name: {routine.name}")
        print(f"   🎯 Activities: {', '.join(routine.activities)}")
        print(f"   ⏰ Time: {routine.schedule_time}")
        print(f"   📅 Days: {', '.join(routine.days_of_week)}")
        print(f"   🆔 Routine ID: {routine.id}")
    
    async def show_expected_outcome(self, interaction):
        """Show what the expected outcome would be"""
        print(f"\n💭 EXPECTED INTERACTION FLOW:")
        
        if "morning routine" in interaction['child_message'].lower():
            print("   1. 🌅 'What time do you usually wake up?'")
            print("   2. 🥣 'What do you need to do to get ready?'")
            print("   3. 🎒 'Let's add: Wake up → Brush teeth → Get dressed → Eat breakfast → Pack bag'")
            print("   4. ✅ 'Your morning routine is ready! Want to try it tomorrow?'")
            
        elif "bedtime" in interaction['child_message'].lower():
            print("   1. 🌙 'What time do you like to go to bed?'")
            print("   2. 📚 'What helps you feel sleepy and calm?'")
            print("   3. 🛁 'Let's add: Bath → Brush teeth → Read story → Quiet time → Sleep'")
            print("   4. ✅ 'Your bedtime routine will help you sleep better!'")
            
        elif "learning" in interaction['child_message'].lower():
            print("   1. 📖 'How long do you like to learn each day?'")
            print("   2. 🎨 'I see you like drawing and reading!'")
            print("   3. ⏰ 'Let's make: 15 min reading → 15 min drawing → 10 min break'")
            print("   4. ✅ 'This routine will make learning fun!'")
            
        elif "calm" in interaction['child_message'].lower():
            print("   1. 😌 'Tell me what makes you feel better when upset'")
            print("   2. 🫁 'Let's try: Deep breaths → Count to 10 → Think happy thoughts'")
            print("   3. 🎵 'Maybe add soft music or a comfort item?'")
            print("   4. ✅ 'This routine will help you feel calm and safe!'")
            
        else:
            print("   1. 🤔 'That sounds like a great routine idea!'")
            print("   2. 📝 'Let's break it down into small steps'")
            print("   3. 🎯 'When would you like to do this routine?'")
            print("   4. ✅ 'Perfect! Your routine is ready to use!'")

    async def demonstrate_routine_usage(self):
        """Show how routines are used after creation"""
        print("\n" + "="*60)
        print("🚀 USING CREATED ROUTINES")
        print("="*60)
        
        # Get existing routines for demo
        routines = await self.routine_manager.get_child_routines(self.child_id)
        
        if routines:
            routine = routines[0]  # Use first routine
            print(f"📋 Demo with routine: {routine.name}")
            
            usage_examples = [
                f"Start my {routine.name.lower()}",
                f"I finished {routine.activities[0] if routine.activities else 'the first step'}",
                f"How am I doing with my {routine.name.lower()}?",
                "I need help with my routine"
            ]
            
            for example in usage_examples:
                print(f"\n💬 Child: \"{example}\"")
                print(f"🌈 Expected response: Supportive guidance and progress tracking")
        else:
            print("💡 No routines found - would show routine usage examples here")

    async def show_visual_elements(self):
        """Demonstrate the visual elements that support routine creation"""
        print("\n" + "="*60)
        print("🎨 VISUAL SUPPORT ELEMENTS")
        print("="*60)
        
        print("🖼️  Visual Cards Available:")
        visual_cards = [
            "✅ Checkmark (completion)",
            "⏰ Clock (time/schedule)", 
            "🌅 Sunrise (morning)",
            "🌙 Moon (bedtime)",
            "📚 Book (reading)",
            "🎨 Art (creative time)",
            "🍽️ Plate (meals)",
            "🛁 Bath (hygiene)",
            "😊 Happy face (positive reinforcement)"
        ]
        
        for card in visual_cards:
            print(f"   {card}")
        
        print("\n🎯 Interface Features:")
        features = [
            "Large, clear buttons for easy interaction",
            "Calm color scheme (blues, greens, soft pastels)",
            "Simple icons and symbols",
            "Progress indicators and celebration animations",
            "Voice support for text-to-speech",
            "Customizable visual preferences"
        ]
        
        for feature in features:
            print(f"   • {feature}")

    async def cleanup(self):
        """Clean up demo resources"""
        print(f"\n🧹 Demo completed! Demo database: demo_routines.db")
        print("💡 In production, all routine data is saved and available for the child")

async def main():
    """Run the complete routine creation demonstration"""
    print("🌈✨ RAINBOW BRIDGE ROUTINE CREATION DEMO ✨🌈")
    print("="*60)
    print("This demo shows how children can create routines using natural language")
    print("through the Rainbow Bridge MCP integration system.")
    print("="*60)
    
    demo = RoutineCreationDemo()
    
    try:
        # Initialize all components
        await demo.initialize()
        
        # Run the demonstration
        await demo.demonstrate_routine_creation()
        await demo.demonstrate_routine_usage()
        await demo.show_visual_elements()
        
        print("\n" + "="*60)
        print("🎉 DEMO COMPLETE!")
        print("="*60)
        print("The Rainbow Bridge system now supports:")
        print("✅ Natural language routine creation")
        print("✅ Child-friendly interaction patterns")
        print("✅ Visual and sensory-friendly design")
        print("✅ Progress tracking and celebration")
        print("✅ Personalized routine management")
        print("\n🌈 Ready to help children build better routines!")
        
    except Exception as e:
        print(f"❌ Demo error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        await demo.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
