"""
Main entry point for Rainbow Bridge application
Uses the new modular architecture.
"""

import asyncio
import logging
import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import uvicorn
from src.api.routes import app
from src.services.database import DatabaseService
from config.settings import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/rainbow_bridge.log', mode='a')
    ]
)

logger = logging.getLogger(__name__)


async def initialize_application():
    """Initialize the application components."""
    
    logger.info("🌈 Initializing Rainbow Bridge Application...")
    
    try:
        # Ensure logs directory exists
        os.makedirs('logs', exist_ok=True)
        
        # Initialize database
        db_service = DatabaseService()
        await db_service.initialize()
        logger.info("✅ Database initialized successfully")
        
        # Additional initialization can go here
        logger.info("✅ Application initialization complete")
        
    except Exception as e:
        logger.error(f"❌ Application initialization failed: {e}")
        raise


def main():
    """Main entry point."""
    
    print("🌈✨ Starting Rainbow Bridge: Magical Companion ✨🌈")
    print(f"Version: {config.version}")
    print(f"Environment: {'Development' if config.api.debug else 'Production'}")
    print("=" * 60)
    
    # Initialize application
    asyncio.run(initialize_application())
    
    # Start the server
    logger.info(f"🚀 Starting server on {config.api.host}:{config.api.port}")
    print(f"🌐 Access the application at: http://localhost:{config.api.port}")
    print("🎯 Press Ctrl+C to stop the server")
    print("=" * 60)
    
    uvicorn.run(
        app,
        host=config.api.host,
        port=config.api.port,
        log_level="info",
        reload=config.api.reload
    )


if __name__ == "__main__":
    main()
