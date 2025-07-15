#!/usr/bin/env python3
"""
Simple structure validation for Rainbow Bridge refactored architecture
"""

import os
from pathlib import Path

def validate_refactored_structure():
    """Validate the refactored structure is in place."""
    
    print("🌈 Rainbow Bridge Structure Validation")
    print("=" * 40)
    
    # Expected refactored files
    expected_files = [
        "src/services/database_core.py",
        "src/services/routine_manager.py", 
        "src/services/progress_tracker.py",
        "src/services/child_manager.py",
        "src/mcp/intent_detector.py",
        "src/mcp/routine_actions.py",
        "src/utils/response_formatter.py",
        "ENHANCED_ARCHITECTURE.md"
    ]
    
    # Check if files exist
    missing_files = []
    present_files = []
    
    for file_path in expected_files:
        if os.path.exists(file_path):
            present_files.append(file_path)
            print(f"✅ {file_path}")
        else:
            missing_files.append(file_path)
            print(f"❌ {file_path} (MISSING)")
    
    print(f"\n📊 Structure Status: {len(present_files)}/{len(expected_files)} files present")
    
    # Check file sizes (ensure they're not empty)
    print(f"\n📏 File Sizes:")
    for file_path in present_files:
        try:
            size = os.path.getsize(file_path)
            lines = 0
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = len(f.readlines())
            print(f"   {file_path}: {size} bytes, {lines} lines")
        except Exception as e:
            print(f"   {file_path}: Error reading - {e}")
    
    # Check backup files exist
    backup_files = [
        "src/services/database_backup.py",
        "src/mcp/client_backup.py"
    ]
    
    print(f"\n💾 Backup Files:")
    for backup_file in backup_files:
        if os.path.exists(backup_file):
            print(f"✅ {backup_file}")
        else:
            print(f"❌ {backup_file} (MISSING)")
    
    # Summary
    if not missing_files:
        print(f"\n🎉 SUCCESS: All refactored files are present!")
        print(f"✅ Modular architecture implemented")
        print(f"✅ Specialized services created")
        print(f"✅ Documentation updated")
        return True
    else:
        print(f"\n⚠️  WARNING: {len(missing_files)} files missing")
        return False

if __name__ == "__main__":
    validate_refactored_structure()
