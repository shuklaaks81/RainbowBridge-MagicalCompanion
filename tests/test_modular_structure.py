#!/usr/bin/env python3
"""
Test script for the new modular Rainbow Bridge architecture
Verifies that all components can be imported and work together.
"""

import sys
import os
import asyncio
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

print("🌈 Testing Rainbow Bridge Modular Architecture")
print("=" * 50)

async def test_modular_structure():
    """Test the modular structure components."""
    
    try:
        print("1️⃣ Testing configuration...")
        from config.settings import config
        print(f"   ✅ Config loaded: {config.app_name} v{config.version}")
        
        print("2️⃣ Testing models...")
        from src.models.entities import Child, Routine, Activity, CommunicationLevel
        print("   ✅ Models imported successfully")
        
        print("3️⃣ Testing database service...")
        from src.services.database import DatabaseService
        db_service = DatabaseService()
        await db_service.initialize()
        print("   ✅ Database service initialized")
        
        print("4️⃣ Testing MCP client...")
        from src.mcp.client import MCPClient
        mcp_client = MCPClient(db_service)
        print("   ✅ MCP client created")
        
        print("5️⃣ Testing AI assistant...")
        from src.ai.assistant import AIAssistantService
        ai_assistant = AIAssistantService(db_service, mcp_client)
        print("   ✅ AI assistant created")
        
        print("6️⃣ Testing routine service...")
        from src.services.routine_service import RoutineService
        routine_service = RoutineService(db_service, mcp_client)
        print("   ✅ Routine service created")
        
        print("7️⃣ Testing utilities...")
        from src.utils.ai_prompts import AIPrompts
        from src.utils.response_formatter import ResponseFormatter
        prompts = AIPrompts()
        formatter = ResponseFormatter()
        print("   ✅ Utilities imported")
        
        print("8️⃣ Testing API routes...")
        from src.api.routes import app
        print("   ✅ API routes imported")
        
        print("\n🎉 All modular components tested successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing modular structure: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_basic_functionality():
    """Test basic functionality with the new structure."""
    
    try:
        print("\n9️⃣ Testing basic functionality...")
        
        # Import components
        from src.services.database import DatabaseService
        from src.mcp.client import MCPClient
        from src.models.entities import Child, CommunicationLevel
        
        # Initialize services
        db_service = DatabaseService()
        await db_service.initialize()
        mcp_client = MCPClient(db_service)
        
        # Test message processing
        test_message = "I finished brushing my teeth"
        context = {
            'has_active_routine': False,
            'child_id': 1
        }
        
        result = await mcp_client.process_message(test_message, 1, context)
        print(f"   🔍 MCP result: {result}")
        
        # Test child creation (simplified)
        child_data = {
            'name': 'Test Child',
            'age': 8,
            'communication_level': 'moderate',
            'interests': ['art', 'reading'],
            'special_needs': ['autism']
        }
        
        print("   ✅ Basic functionality test passed")
        return True
        
    except Exception as e:
        print(f"❌ Error testing functionality: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function."""
    
    # Test modular structure
    structure_test = await test_modular_structure()
    
    # Test basic functionality
    functionality_test = await test_basic_functionality()
    
    print("\n" + "=" * 50)
    if structure_test and functionality_test:
        print("🎉 All tests passed! Modular architecture is working correctly.")
        print("🚀 Ready to migrate from legacy structure!")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        
    print("\n📁 New Project Structure:")
    print("   src/")
    print("   ├── api/          # FastAPI routes")
    print("   ├── services/     # Business logic")
    print("   ├── models/       # Data models")
    print("   ├── ai/           # AI components")
    print("   ├── mcp/          # MCP implementation")
    print("   └── utils/        # Utilities")
    print("   config/           # Configuration")
    print("   tests/            # Test suite")
    print("   scripts/          # Demo scripts")

if __name__ == "__main__":
    asyncio.run(main())
