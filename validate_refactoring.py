#!/usr/bin/env python3
"""
Simple validation script for refactored Rainbow Bridge architecture
"""

print("🌈 Validating Rainbow Bridge Refactored Architecture")
print("=" * 50)

try:
    # Test core database imports
    print("Testing database core...")
    from src.services.database_core import DatabaseCore
    print("✅ DatabaseCore imported")
    
    from src.services.routine_manager import RoutineManager
    print("✅ RoutineManager imported")
    
    from src.services.progress_tracker import ProgressTracker
    print("✅ ProgressTracker imported")
    
    from src.services.child_manager import ChildManager
    print("✅ ChildManager imported")
    
    # Test main database service
    from src.services.database import DatabaseService
    print("✅ DatabaseService imported")
    
except ImportError as e:
    print(f"❌ Database import error: {e}")

try:
    # Test MCP components
    print("\nTesting MCP components...")
    from src.mcp.intent_detector import IntentDetector
    print("✅ IntentDetector imported")
    
    from src.mcp.routine_actions import RoutineActionHandler
    print("✅ RoutineActionHandler imported")
    
    from src.mcp.client import MCPClient
    print("✅ MCPClient imported")
    
except ImportError as e:
    print(f"❌ MCP import error: {e}")

try:
    # Test response formatter
    print("\nTesting response formatter...")
    from src.utils.response_formatter import ResponseFormatter
    print("✅ ResponseFormatter imported")
    
except ImportError as e:
    print(f"❌ Response formatter import error: {e}")

print("\n🎉 Import validation completed!")
print("\nRefactoring Summary:")
print("📦 Database service split into 4 specialized modules")
print("📦 MCP client split into 3 focused components")
print("📦 Enhanced response formatter with dynamic messaging")
print("📦 Improved modular architecture for scalability")
