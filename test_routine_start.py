#!/usr/bin/env python3
"""
🧪 Test Routine Starting
=======================

Test the routine starting functionality to debug the error.
"""

import asyncio
import sys
import os
import aiohttp

async def test_routine_start():
    """Test starting routines"""
    print("🧪 Testing routine start functionality...")
    
    try:
        # First, list available routines
        async with aiohttp.ClientSession() as session:
            print("📋 Getting available routines...")
            async with session.get('http://localhost:8000/child/1') as response:
                if response.status == 200:
                    html = await response.text()
                    # Look for routine IDs in the HTML (simple parsing)
                    import re
                    routine_matches = re.findall(r'routine-(\d+)', html)
                    if routine_matches:
                        routine_id = routine_matches[0]
                        print(f"✅ Found routine ID: {routine_id}")
                        
                        # Try to start this routine
                        print(f"🚀 Testing start routine {routine_id}...")
                        start_data = {
                            'routine_id': routine_id,
                            'child_id': '1'
                        }
                        
                        async with session.post('http://localhost:8000/api/routine/start', data=start_data) as start_response:
                            print(f"📊 Status: {start_response.status}")
                            response_text = await start_response.text()
                            print(f"📄 Response: {response_text[:200]}...")
                            
                            if start_response.status == 200:
                                print("✅ Routine start successful!")
                            else:
                                print(f"❌ Routine start failed: {start_response.status}")
                    else:
                        print("❌ No routines found in dashboard")
                else:
                    print(f"❌ Could not load dashboard: {response.status}")
    
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_routine_start())
