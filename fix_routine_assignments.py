#!/usr/bin/env python3
"""Fix routine assignments to match children correctly."""

import asyncio
import aiosqlite
import json

async def fix_routine_assignments():
    """Fix routine assignments and create appropriate routines for each child."""
    
    async with aiosqlite.connect("special_kids.db") as db:
        
        # First, let's see what we have
        print("=== Current State ===")
        cursor = await db.execute("SELECT id, name, age FROM children")
        children = await cursor.fetchall()
        print("Children:")
        for child in children:
            print(f"  {child[0]}: {child[1]} (age {child[2]})")
        
        cursor = await db.execute("SELECT id, child_id, name FROM routines")
        routines = await cursor.fetchall()
        print("\nRoutines:")
        for routine in routines:
            print(f"  {routine[0]}: {routine[2]} (child_id: {routine[1]})")
        
        print("\n=== Fixing Assignments ===")
        
        # Fix routine 1: Change name to match Ananya
        print("1. Updating routine 1 name to 'Ananya's Morning Routine'")
        await db.execute("""
            UPDATE routines 
            SET name = 'Ananya''s Morning Routine'
            WHERE id = 1 AND child_id = 1
        """)
        
        # Fix routine 2: Create Emma's routine by updating routine 2
        print("2. Updating routine 2 to be Emma's routine")
        await db.execute("""
            UPDATE routines 
            SET name = 'Emma''s Morning Routine', child_id = 2
            WHERE id = 2
        """)
        
        # Create Emma's activities JSON (age-appropriate for 7-year-old)
        emma_activities = [
            {
                "name": "Wake Up Gently",
                "duration_minutes": 10,
                "description": "Gentle wake-up with soft music or lighting",
                "visual_cue": "sunrise",
                "instructions": ["Turn on soft light", "Play calming music", "Give child time to adjust"],
                "sensory_considerations": ["gradual lighting", "low volume sounds"],
                "completed": False
            },
            {
                "name": "Get Dressed",
                "duration_minutes": 15,
                "description": "Put on school clothes",
                "visual_cue": "clothes",
                "instructions": ["Choose clothes together", "Put on underwear first", "Then shirt and pants", "Shoes last"],
                "sensory_considerations": ["soft fabrics", "loose fitting", "no scratchy tags"],
                "completed": False
            },
            {
                "name": "Eat Breakfast",
                "duration_minutes": 20,
                "description": "Healthy breakfast time",
                "visual_cue": "food",
                "instructions": ["Sit at table", "Eat slowly", "Drink milk or juice"],
                "sensory_considerations": ["familiar foods", "comfortable seating"],
                "completed": False
            },
            {
                "name": "Brush Teeth",
                "duration_minutes": 10,
                "description": "Brush teeth for 2 minutes",
                "visual_cue": "toothbrush",
                "instructions": ["Use soft toothbrush", "Brush for 2 minutes", "Rinse mouth"],
                "sensory_considerations": ["mild toothpaste", "soft bristles"],
                "completed": False
            },
            {
                "name": "Pack School Bag",
                "duration_minutes": 10,
                "description": "Get ready for school",
                "visual_cue": "backpack",
                "instructions": ["Check homework", "Pack lunch", "Get books"],
                "sensory_considerations": ["organize items", "check list"],
                "completed": False
            }
        ]
        
        # Update Emma's routine with age-appropriate activities
        await db.execute("""
            UPDATE routines 
            SET activities = ?, total_activities = 5
            WHERE id = 2
        """, (json.dumps(emma_activities),))
        
        # Create Ananya's activities JSON (age-appropriate for 13-year-old)
        ananya_activities = [
            {
                "name": "Wake Up",
                "duration_minutes": 10,
                "description": "Wake up and stretch",
                "visual_cue": "sunrise",
                "instructions": ["Turn off alarm", "Stretch for 2 minutes", "Open curtains"],
                "sensory_considerations": ["gradual lighting", "gentle sounds"],
                "completed": True
            },
            {
                "name": "Personal Hygiene",
                "duration_minutes": 20,
                "description": "Morning hygiene routine",
                "visual_cue": "bathroom",
                "instructions": ["Wash face", "Brush teeth", "Comb hair", "Apply deodorant"],
                "sensory_considerations": ["gentle products", "organized space"],
                "completed": True
            },
            {
                "name": "Get Dressed",
                "duration_minutes": 15,
                "description": "Choose and put on clothes",
                "visual_cue": "clothes",
                "instructions": ["Check weather", "Choose appropriate clothes", "Get dressed"],
                "sensory_considerations": ["comfortable fabrics", "weather appropriate"],
                "completed": False
            },
            {
                "name": "Breakfast",
                "duration_minutes": 25,
                "description": "Healthy breakfast",
                "visual_cue": "food",
                "instructions": ["Prepare or heat breakfast", "Eat mindfully", "Clean up"],
                "sensory_considerations": ["nutritious foods", "quiet environment"],
                "completed": False
            },
            {
                "name": "School Preparation",
                "duration_minutes": 15,
                "description": "Get ready for school",
                "visual_cue": "backpack",
                "instructions": ["Check schedule", "Pack bag", "Gather supplies"],
                "sensory_considerations": ["organized materials", "check list"],
                "completed": False
            }
        ]
        
        # Update Ananya's routine
        await db.execute("""
            UPDATE routines 
            SET activities = ?, total_activities = 5
            WHERE id = 1
        """, (json.dumps(ananya_activities),))
        
        # Fix routine sessions - update child assignments
        print("3. Fixing routine session assignments")
        
        # Move routine session for routine 2 to Emma (child_id = 2)
        await db.execute("""
            UPDATE routine_sessions 
            SET child_id = 2
            WHERE routine_id = 2
        """)
        
        await db.commit()
        
        print("\n=== Final State ===")
        cursor = await db.execute("""
            SELECT r.id, r.child_id, r.name, c.name as child_name, r.total_activities
            FROM routines r 
            JOIN children c ON r.child_id = c.id
            ORDER BY r.child_id, r.id
        """)
        routines = await cursor.fetchall()
        print("Fixed Routines:")
        for routine in routines:
            print(f"  Routine {routine[0]}: {routine[2]} -> {routine[3]} ({routine[4]} activities)")
        
        cursor = await db.execute("""
            SELECT rs.id, rs.routine_id, rs.child_id, rs.status, r.name, c.name
            FROM routine_sessions rs 
            JOIN routines r ON rs.routine_id = r.id 
            JOIN children c ON rs.child_id = c.id
            ORDER BY rs.child_id, rs.id
        """)
        sessions = await cursor.fetchall()
        print("\nFixed Sessions:")
        for session in sessions:
            print(f"  Session {session[0]}: {session[4]} -> {session[5]} ({session[3]})")
        
        print("\n✅ Routine assignments fixed successfully!")

if __name__ == "__main__":
    asyncio.run(fix_routine_assignments())
