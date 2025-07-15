#!/usr/bin/env python3
"""
Azure OpenAI Test Script for Rainbow Bridge Magical Companion
Test the Azure OpenAI integration to ensure it's working correctly.
"""

import os
import sys
import asyncio
import logging
from dotenv import load_dotenv

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.ai_assistant import SpecialKidsAI

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_azure_openai():
    """Test Azure OpenAI integration."""
    
    print("🌈 Rainbow Bridge - Azure OpenAI Integration Test")
    print("=" * 50)
    
    # Check configuration
    use_azure = os.getenv("USE_AZURE_OPENAI", "False").lower() == "true"
    azure_key = os.getenv("AZURE_OPENAI_API_KEY")
    azure_endpoint = os.getenv("ENDPOINT_URL") or os.getenv("AZURE_OPENAI_ENDPOINT")
    deployment_name = os.getenv("DEPLOYMENT_NAME") or os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    local_mode = os.getenv("LOCAL_MODE", "False").lower() == "true"
    
    print(f"Local Mode: {local_mode}")
    print(f"Use Azure OpenAI: {use_azure}")
    print(f"Azure API Key: {'✓ Set' if azure_key and azure_key != 'REPLACE_WITH_YOUR_KEY_VALUE_HERE' else '✗ Not set'}")
    print(f"Azure Endpoint: {'✓ Set' if azure_endpoint and 'aistatrter.openai.azure.com' in azure_endpoint else '✗ Not set'}")
    print(f"Deployment Name: {'✓ Set' if deployment_name else '✗ Not set'}")
    print()
    
    if not use_azure:
        print("❌ Azure OpenAI is not enabled. Set USE_AZURE_OPENAI=True in .env file")
        return False
    
    if not azure_key or azure_key == "REPLACE_WITH_YOUR_KEY_VALUE_HERE":
        print("❌ Azure OpenAI API key is not properly configured")
        return False
    
    if not azure_endpoint or not ('aistatrter.openai.azure.com' in azure_endpoint):
        print("❌ Azure OpenAI endpoint is not properly configured")
        print(f"   Current endpoint: {azure_endpoint}")
        print("   Expected endpoint should contain: aistatrter.openai.azure.com")
        return False
    
    try:
        # Initialize the AI assistant
        print("🔧 Initializing Rainbow Bridge AI Assistant...")
        ai_assistant = SpecialKidsAI()
        
        if not ai_assistant.client:
            print("❌ Failed to initialize AI client")
            return False
        
        if not ai_assistant.use_azure:
            print("❌ Azure OpenAI is not being used by the AI assistant")
            return False
        
        print("✅ AI Assistant initialized successfully")
        print(f"   Using Azure OpenAI: {ai_assistant.use_azure}")
        print(f"   Deployment Name: {ai_assistant.deployment_name}")
        print()
        
        # Test a simple message
        print("🧪 Testing AI communication...")
        test_message = "Hello! I'm feeling a bit sad today."
        
        response = await ai_assistant.process_message(
            message=test_message,
            child_id=1,
            communication_type="text",
            child_preferences={
                "visual_support": True,
                "routine_focus": True,
                "interests": ["colors", "rainbows"]
            }
        )
        
        print(f"📝 Test Message: {test_message}")
        print(f"🌈 AI Response: {response.get('text', 'No response text')}")
        print(f"😊 Emotion: {response.get('emotion', 'Unknown')}")
        print(f"🎨 Visual Cues: {', '.join(response.get('visual_cues', []))}")
        print(f"🔗 LLM Source: {response.get('llm_source', 'Unknown')}")
        print()
        
        if response.get('llm_source') == 'azure_openai':
            print("✅ Azure OpenAI is working correctly!")
            return True
        else:
            print(f"❌ Expected 'azure_openai' but got '{response.get('llm_source')}'")
            return False
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        logger.exception("Test failed with exception")
        return False

async def main():
    """Main test function."""
    success = await test_azure_openai()
    
    if success:
        print("\n🎉 Azure OpenAI integration test PASSED!")
        print("   Your Rainbow Bridge application is ready to use Azure OpenAI")
    else:
        print("\n❌ Azure OpenAI integration test FAILED!")
        print("   Please check your configuration and try again")
        
        print("\n📋 Configuration checklist:")
        print("   1. Set USE_AZURE_OPENAI=True in .env")
        print("   2. Set AZURE_OPENAI_API_KEY to your actual API key")
        print("   3. Set AZURE_OPENAI_ENDPOINT to your Azure resource endpoint")
        print("   4. Set AZURE_OPENAI_DEPLOYMENT_NAME to your deployment name")
        print("   5. Set LOCAL_MODE=False in .env")
    
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
