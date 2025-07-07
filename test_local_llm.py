#!/usr/bin/env python3
"""
Local LLM Test Script for Special Kids Assistant

This script tests the local LLM functionality and provides diagnostics.
"""

import asyncio
import os
import sys
import json
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.local_llm import LocalLLMManager
from core.ai_assistant import SpecialKidsAI

def print_header(title):
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(f"🌈 {title} 🌈")
    print(f"{'='*60}")

def print_status(status, message):
    """Print a status message with color coding."""
    colors = {
        'SUCCESS': '\033[92m',
        'WARNING': '\033[93m',
        'ERROR': '\033[91m',
        'INFO': '\033[94m'
    }
    reset = '\033[0m'
    color = colors.get(status, '')
    print(f"{color}[{status}]{reset} {message}")

async def test_local_llm_providers():
    """Test individual local LLM providers."""
    print_header("Testing Local LLM Providers")
    
    # Initialize the local LLM manager
    llm_manager = LocalLLMManager()
    
    # Test each provider
    providers = llm_manager.get_provider_status()
    
    if not providers:
        print_status('WARNING', 'No local LLM providers configured')
        return False
    
    test_prompt = "Hello! Please respond with a simple, friendly greeting for a child."
    system_prompt = "You are Rainbow Bridge, a friendly assistant for children. Keep responses short and cheerful."
    
    success_count = 0
    
    for provider_name, is_available in providers.items():
        print(f"\n📝 Testing {provider_name}...")
        
        if not is_available:
            print_status('ERROR', f'{provider_name} is not available')
            continue
        
        try:
            # Test the provider
            provider = llm_manager.providers[provider_name]
            response = await provider.generate(
                prompt=test_prompt,
                system_prompt=system_prompt,
                max_tokens=50,
                temperature=0.7
            )
            
            if response.success:
                print_status('SUCCESS', f'{provider_name} is working!')
                print(f"  Response: {response.text[:100]}...")
                print(f"  Model: {response.model}")
                print(f"  Processing time: {response.processing_time:.2f}s")
                success_count += 1
            else:
                print_status('ERROR', f'{provider_name} failed: {response.error}')
        
        except Exception as e:
            print_status('ERROR', f'{provider_name} error: {str(e)}')
    
    return success_count > 0

async def test_ai_assistant():
    """Test the AI assistant with local LLM integration."""
    print_header("Testing AI Assistant Integration")
    
    # Initialize AI assistant
    ai_assistant = SpecialKidsAI()
    
    # Get LLM status
    status = ai_assistant.get_llm_status()
    
    print("🔍 LLM Status:")
    print(f"  Local mode: {status['local_mode']}")
    print(f"  OpenAI available: {status['openai_available']}")
    print(f"  Available providers: {status['available_providers']}")
    print(f"  Fallback enabled: {status['fallback_enabled']}")
    
    if not status['available_providers'] and not status['openai_available']:
        print_status('ERROR', 'No LLM providers available')
        return False
    
    # Test message processing
    test_messages = [
        "Hello Rainbow Bridge!",
        "I'm feeling happy today",
        "Can you help me with my daily routine?",
        "I want to learn something new"
    ]
    
    print("\n📨 Testing message processing...")
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n  Test {i}: '{message}'")
        
        try:
            response = await ai_assistant.process_message(
                message=message,
                child_id=1,
                communication_type="text"
            )
            
            if response:
                print_status('SUCCESS', 'Message processed successfully')
                print(f"    Response: {response['text'][:100]}...")
                print(f"    Visual cues: {response['visual_cues']}")
                print(f"    Emotion: {response['emotion']}")
                print(f"    LLM source: {response.get('llm_source', 'unknown')}")
            else:
                print_status('ERROR', 'No response generated')
        
        except Exception as e:
            print_status('ERROR', f'Processing failed: {str(e)}')
    
    return True

async def run_connectivity_test():
    """Run connectivity test for all providers."""
    print_header("Connectivity Test")
    
    ai_assistant = SpecialKidsAI()
    
    try:
        results = await ai_assistant.test_llm_connectivity()
        
        print("🔗 Local Providers:")
        for provider, result in results['local_providers'].items():
            if result['available']:
                print_status('SUCCESS', f'{provider}: Available (response time: {result.get("response_time", "N/A")}s)')
            else:
                print_status('ERROR', f'{provider}: {result.get("error", "Unavailable")}')
        
        print("\n🌐 OpenAI:")
        openai_result = results['openai']
        if openai_result['available']:
            print_status('SUCCESS', 'OpenAI: Available')
            print(f"  Sample response: {openai_result.get('response', 'N/A')}")
        else:
            print_status('ERROR', f'OpenAI: {openai_result.get("error", "Unavailable")}')
    
    except Exception as e:
        print_status('ERROR', f'Connectivity test failed: {str(e)}')

def show_configuration():
    """Show current configuration."""
    print_header("Current Configuration")
    
    config_vars = [
        'LOCAL_MODE',
        'PRIMARY_LOCAL_LLM',
        'OLLAMA_ENABLED',
        'OLLAMA_BASE_URL',
        'OLLAMA_MODEL',
        'LOCALAI_ENABLED',
        'HF_ENABLED',
        'FALLBACK_TO_OPENAI',
        'CHILD_SAFE_MODE'
    ]
    
    print("📋 Environment Variables:")
    for var in config_vars:
        value = os.getenv(var, 'Not set')
        print(f"  {var}: {value}")

def show_recommendations():
    """Show setup recommendations."""
    print_header("Setup Recommendations")
    
    print("💡 For optimal performance:")
    print("  1. Use Ollama with llama2:7b-chat model (good balance)")
    print("  2. Ensure at least 8GB RAM for 7B models")
    print("  3. Set LOCAL_MODE=True in .env for local-only operation")
    print("  4. Keep FALLBACK_TO_OPENAI=True for reliability")
    print("  5. Enable CHILD_SAFE_MODE=True for content filtering")
    print()
    print("🚀 Quick setup:")
    print("  1. Run: ./setup_local_llm.sh")
    print("  2. Or manually: ollama serve && ollama pull llama2:7b-chat")
    print("  3. Set LOCAL_MODE=True in .env")
    print("  4. Run: python test_local_llm.py")

async def main():
    """Main test function."""
    print_header("Rainbow Bridge - Local LLM Test Suite")
    print(f"Test started at: {datetime.now()}")
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    load_dotenv('.env.local')  # Load local LLM config
    
    # Show configuration
    show_configuration()
    
    # Test local LLM providers
    local_success = await test_local_llm_providers()
    
    # Test AI assistant integration
    ai_success = await test_ai_assistant()
    
    # Run connectivity test
    await run_connectivity_test()
    
    # Show recommendations
    show_recommendations()
    
    # Summary
    print_header("Test Summary")
    
    if local_success and ai_success:
        print_status('SUCCESS', 'All tests passed! Local LLM is ready to use.')
    elif local_success:
        print_status('WARNING', 'Local LLM providers work, but AI assistant integration has issues.')
    elif ai_success:
        print_status('WARNING', 'AI assistant works, but local LLM providers need attention.')
    else:
        print_status('ERROR', 'Tests failed. Please check your configuration.')
    
    print(f"\nTest completed at: {datetime.now()}")
    print("🌈 Thank you for using Rainbow Bridge! 🌈")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
    except Exception as e:
        print(f"\n\nTest failed with error: {str(e)}")
        sys.exit(1)
