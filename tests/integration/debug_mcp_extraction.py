#!/usr/bin/env python3
"""
Debug what activity names the MCP client extracts from general phrases
"""

import sys
import os
sys.path.append('/Users/amitshukla/Desktop/AI Assistant/RainbowBridge-MagicalCompanion')

from core.routine_mcp_client import RoutineMCPClient

def debug_mcp_extraction():
    """Debug what the MCP client extracts from general phrases."""
    
    print("🔍 Debug MCP Client Activity Extraction")
    print("=" * 50)
    
    # Create a mock MCP client (without server for this test)
    class MockMCPServer:
        pass
    
    client = RoutineMCPClient(MockMCPServer())
    
    # Test phrases and see what gets extracted
    test_phrases = [
        "I woke up",
        "Got dressed", 
        "Ate breakfast",
        "Teeth clean",
        "Clothes on",
        "Brushed"
    ]
    
    print("Testing activity extraction from general phrases:")
    
    for phrase in test_phrases:
        print(f"\nPhrase: '{phrase}'")
        
        # Extract activity name using the private method
        extraction_result = client._extract_activity_name(phrase)
        
        if extraction_result:
            activity_name = extraction_result.get('activity_name', 'None')
            general_completion = extraction_result.get('general_completion', False)
            
            print(f"   Extracted: '{activity_name}'")
            if general_completion:
                print(f"   (General completion detected)")
        else:
            print(f"   No activity extracted")

if __name__ == "__main__":
    debug_mcp_extraction()
