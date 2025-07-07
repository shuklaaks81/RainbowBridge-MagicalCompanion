#!/usr/bin/env python3
"""
Initialize the Special Kids Assistant application database and setup.
"""

import asyncio
import os
import sys
import logging
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from database.db_manager import DatabaseManager

async def initialize_app():
    """Initialize the application database and setup."""
    print("� Initializing Rainbow Bridge...")
    
    # Create required directories
    directories = [
        "static/images/visual_cards",
        "static/custom_cards", 
        "static/generated_cards",
        "logs"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    # Initialize database
    try:
        db_manager = DatabaseManager()
        await db_manager.initialize()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize database: {e}")
        return False
    
    # Check environment variables
    required_env_vars = ["OPENAI_API_KEY"]
    missing_vars = []
    
    for var in required_env_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"⚠️  Warning: Missing environment variables: {', '.join(missing_vars)}")
        print("   Please create a .env file with your OpenAI API key")
        print("   Copy .env.example to .env and fill in your API key")
    else:
        print("✅ Environment variables configured")
    
    print("\n� Rainbow Bridge initialized successfully!")
    print("🎨 Your magical communication companion is ready!")
    print("\nTo start the application:")
    print("   python main.py")
    print("\nThe application will be available at http://localhost:8000")
    
    return True

if __name__ == "__main__":
    asyncio.run(initialize_app())
