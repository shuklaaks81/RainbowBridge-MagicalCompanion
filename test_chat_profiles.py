#!/usr/bin/env python3
"""
🧪 Test Chat with Profile Pictures
=================================

Test the enhanced chat interface with user names and profile pictures.
"""

import asyncio
import aiohttp

async def test_chat_with_profiles():
    """Test chat functionality with profile pictures"""
    print("🧪 Testing enhanced chat with profile pictures...")
    
    try:
        async with aiohttp.ClientSession() as session:
            # Test a simple chat message
            test_data = {
                'child_id': '1',
                'message': 'Hello Rainbow Bridge! I love the new look!',
                'communication_type': 'text'
            }
            
            async with session.post('http://localhost:8000/api/chat', data=test_data) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ Chat API Response:")
                    print(f"   Text: {result.get('text', 'No text')[:100]}...")
                    print(f"   Visual Cues: {result.get('visual_cues', [])}")
                    print(f"🎉 Chat with profiles should be working!")
                    print(f"🌈 Visit http://localhost:8000/child/1 to see the new profile pictures!")
                else:
                    print(f"❌ Chat API error: {response.status}")
    
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_chat_with_profiles())
