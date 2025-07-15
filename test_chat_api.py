#!/usr/bin/env python3
"""
🧪 End-to-End Chat Test
======================

Test creating routines through the actual chat API.
"""

import asyncio
import sys
import os
import json
import aiohttp

async def test_chat_api():
    """Test the actual chat API endpoint"""
    print("🧪 Testing actual chat API endpoint...")
    
    try:
        async with aiohttp.ClientSession() as session:
            # Test routine creation through chat API
            test_data = {
                'child_id': '1',
                'message': 'I want to create a evening routine',
                'communication_type': 'text'
            }
            
            async with session.post('http://localhost:8000/api/chat', data=test_data) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ Chat API Response:")
                    print(f"   Text: {result.get('text', 'No text')[:100]}...")
                    print(f"   LLM Source: {result.get('llm_source', 'unknown')}")
                    print(f"   Visual Cues: {result.get('visual_cues', [])}")
                    
                    if result.get('llm_source') == 'mcp_routine':
                        print(f"🎉 SUCCESS: MCP routine creation working via chat API!")
                    else:
                        print(f"⚠️  Chat working but not using MCP routing")
                else:
                    print(f"❌ Chat API error: {response.status}")
                    text = await response.text()
                    print(f"Error: {text}")
    
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_chat_api())
