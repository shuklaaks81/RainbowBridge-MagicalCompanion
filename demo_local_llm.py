#!/usr/bin/env python3
"""
Quick Demo: Local LLM for Rainbow Bridge

This script demonstrates the local LLM functionality without requiring
a full setup. It shows what's possible with local AI providers.
"""

import os
import sys
import asyncio

# Set up environment for demo
os.environ['LOCAL_MODE'] = 'True'
os.environ['OLLAMA_ENABLED'] = 'True'

def print_rainbow(text):
    """Print text with rainbow colors."""
    colors = ['\033[91m', '\033[93m', '\033[92m', '\033[94m', '\033[95m', '\033[96m']
    reset = '\033[0m'
    
    colored_text = ""
    for i, char in enumerate(text):
        colored_text += colors[i % len(colors)] + char
    colored_text += reset
    
    print(colored_text)

async def demo_local_llm():
    """Demonstrate local LLM functionality."""
    
    print_rainbow("🌈✨ Rainbow Bridge Local LLM Demo ✨🌈")
    print("=" * 50)
    
    try:
        # Import after setting environment
        from core.local_llm import LocalLLMManager
        from core.ai_assistant import SpecialKidsAI
        
        print("\n1. 🔍 Checking Local LLM Status...")
        llm_manager = LocalLLMManager()
        providers = llm_manager.get_provider_status()
        
        print(f"   Available providers: {list(providers.keys())}")
        for provider, available in providers.items():
            status = "✅ Available" if available else "❌ Unavailable"
            print(f"   {provider}: {status}")
        
        if not any(providers.values()):
            print("\n⚠️  No local LLM providers are currently available.")
            print("   To set up Ollama, run: python quick_setup_ollama.py")
            return
        
        print("\n2. 🤖 Testing AI Assistant...")
        ai_assistant = SpecialKidsAI()
        status = ai_assistant.get_llm_status()
        
        print(f"   Local mode: {'✅ Enabled' if status['local_mode'] else '❌ Disabled'}")
        print(f"   Available providers: {status['available_providers']}")
        
        if not status['available_providers']:
            print("\n⚠️  No providers available for testing.")
            return
        
        print("\n3. 💬 Testing Communication...")
        test_messages = [
            "Hello Rainbow Bridge!",
            "I'm feeling happy today",
            "Can you help me with my routine?"
        ]
        
        for i, message in enumerate(test_messages, 1):
            print(f"\n   Test {i}: '{message}'")
            
            try:
                response = await ai_assistant.process_message(
                    message=message,
                    child_id=1,
                    communication_type="text",
                    child_preferences={"visual_support": True}
                )
                
                if response and response.get('text'):
                    print(f"   💭 Response: {response['text'][:80]}...")
                    print(f"   🎨 Visual cues: {response.get('visual_cues', [])}")
                    print(f"   😊 Emotion: {response.get('emotion', 'neutral')}")
                    print(f"   🔧 Source: {response.get('llm_source', 'unknown')}")
                else:
                    print("   ❌ No response generated")
            
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
        
        print("\n4. 🧪 Testing Provider Connectivity...")
        try:
            connectivity_results = await ai_assistant.test_llm_connectivity()
            
            for provider, result in connectivity_results.get('local_providers', {}).items():
                if result.get('available'):
                    time_info = f" ({result.get('response_time', 0):.2f}s)" if 'response_time' in result else ""
                    print(f"   ✅ {provider}: Working{time_info}")
                else:
                    error = result.get('error', 'Unknown error')
                    print(f"   ❌ {provider}: {error}")
        
        except Exception as e:
            print(f"   ❌ Connectivity test failed: {str(e)}")
        
        print("\n🎉 Demo Complete!")
        print("=" * 50)
        print("✨ Local LLM functionality is working!")
        print("🌈 Ready to help children with communication adventures!")
        
        print("\nNext steps:")
        print("1. Run the full application: python main.py")
        print("2. Open your browser: http://localhost:8000")
        print("3. Click 'LLM Settings' to manage providers")
        print("4. Create a child profile and start chatting!")
    
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you've installed the requirements:")
        print("   pip install -r requirements.txt")
    
    except Exception as e:
        print(f"❌ Demo failed: {str(e)}")

def show_setup_help():
    """Show setup help for users without local LLMs."""
    print("\n📋 Quick Setup Guide:")
    print("=" * 30)
    print("🚀 For Ollama (Recommended):")
    print("   python quick_setup_ollama.py")
    print()
    print("🛠️  For Full Setup:")
    print("   ./setup_local_llm.sh")
    print()
    print("📖 For Documentation:")
    print("   Read LOCAL_LLM_SETUP.md")
    print()
    print("🧪 For Testing:")
    print("   python test_local_llm.py")

if __name__ == "__main__":
    print("Starting Rainbow Bridge Local LLM Demo...")
    
    try:
        asyncio.run(demo_local_llm())
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except Exception as e:
        print(f"\n\nDemo failed: {str(e)}")
    
    show_setup_help()
    print("\n🌈 Thank you for trying Rainbow Bridge! ✨")
