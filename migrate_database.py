#!/usr/bin/env python3
"""
🔧 Database Migration Script
===========================

Add missing columns to existing database tables.
"""

import asyncio
import aiosqlite
import sys
import os

async def migrate_database():
    """Add missing columns to the routines table"""
    db_path = "special_kids.db"
    
    print("🔧 Starting database migration...")
    
    try:
        async with aiosqlite.connect(db_path) as db:
            print(f"📁 Connected to database: {db_path}")
            
            # Check if total_activities column exists
            cursor = await db.execute("PRAGMA table_info(routines)")
            columns = await cursor.fetchall()
            column_names = [col[1] for col in columns]
            
            print(f"📋 Current columns: {column_names}")
            
            # Add missing columns if they don't exist
            if 'total_activities' not in column_names:
                print("➕ Adding total_activities column...")
                await db.execute("ALTER TABLE routines ADD COLUMN total_activities INTEGER DEFAULT 0")
                await db.commit()
                print("✅ Added total_activities column")
            else:
                print("✅ total_activities column already exists")
            
            if 'updated_at' not in column_names:
                print("➕ Adding updated_at column...")
                await db.execute("ALTER TABLE routines ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
                await db.commit()
                print("✅ Added updated_at column")
            else:
                print("✅ updated_at column already exists")
            
            # Update existing routines to have correct total_activities count
            print("🔄 Updating total_activities for existing routines...")
            cursor = await db.execute("SELECT id, activities FROM routines")
            routines = await cursor.fetchall()
            
            for routine_id, activities_json in routines:
                try:
                    import json
                    activities = json.loads(activities_json)
                    activity_count = len(activities) if isinstance(activities, list) else 0
                    await db.execute(
                        "UPDATE routines SET total_activities = ? WHERE id = ?",
                        (activity_count, routine_id)
                    )
                except:
                    # If JSON parsing fails, default to 0
                    await db.execute(
                        "UPDATE routines SET total_activities = 0 WHERE id = ?",
                        (routine_id,)
                    )
            
            await db.commit()
            print("✅ Updated total_activities for all existing routines")
            
            # Show updated schema
            print("\n📋 Updated schema:")
            cursor = await db.execute("PRAGMA table_info(routines)")
            columns = await cursor.fetchall()
            for col in columns:
                print(f"   {col[1]} {col[2]}")
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(migrate_database())
