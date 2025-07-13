#!/usr/bin/env python3
"""
Azure OpenAI Deployment Finder
Quick script to help find the correct deployment name for your Azure OpenAI resource.
"""

import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_deployment_name(deployment_name):
    """Test a specific deployment name."""
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
    
    url = f"{endpoint}openai/deployments/{deployment_name}/chat/completions?api-version={api_version}"
    
    headers = {
        "Content-Type": "application/json",
        "api-key": api_key
    }
    
    data = {
        "messages": [{"role": "user", "content": "Hello!"}],
        "max_tokens": 10
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            return True, "Success"
        elif response.status_code == 404:
            return False, "Deployment not found"
        elif response.status_code == 401:
            return False, "Authentication failed"
        else:
            return False, f"Error {response.status_code}: {response.text[:100]}"
    
    except requests.exceptions.RequestException as e:
        return False, f"Connection error: {str(e)}"

def main():
    print("🔍 Azure OpenAI Deployment Name Finder")
    print("=" * 40)
    
    # Check configuration
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    
    if not endpoint or not api_key:
        print("❌ Missing Azure OpenAI configuration")
        print("   Please ensure AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY are set")
        return
    
    print(f"Endpoint: {endpoint}")
    print(f"Testing common deployment names...\n")
    
    # Common deployment names to test
    common_names = [
        "gpt-4",
        "gpt-4-32k", 
        "gpt-4-1106-preview",
        "gpt-4-turbo",
        "gpt-35-turbo",
        "gpt-35-turbo-16k",
        "text-davinci-003",
        "text-davinci-002"
    ]
    
    successful_deployments = []
    
    for name in common_names:
        print(f"Testing '{name}'...", end=" ")
        success, message = test_deployment_name(name)
        
        if success:
            print(f"✅ {message}")
            successful_deployments.append(name)
        else:
            print(f"❌ {message}")
    
    print(f"\n📋 Results:")
    if successful_deployments:
        print(f"✅ Found {len(successful_deployments)} working deployment(s):")
        for name in successful_deployments:
            print(f"   - {name}")
        
        print(f"\n🔧 To use the first working deployment, update your .env file:")
        print(f"AZURE_OPENAI_DEPLOYMENT_NAME={successful_deployments[0]}")
        
    else:
        print("❌ No working deployments found with common names.")
        print("\n💡 Manual steps:")
        print("1. Go to https://oai.azure.com/")
        print("2. Navigate to 'Deployments' in the left sidebar")
        print("3. Copy the exact deployment name")
        print("4. Update AZURE_OPENAI_DEPLOYMENT_NAME in your .env file")
    
    print(f"\n🧪 You can also test a custom deployment name:")
    custom_name = input("Enter deployment name to test (or press Enter to skip): ").strip()
    
    if custom_name:
        print(f"Testing '{custom_name}'...", end=" ")
        success, message = test_deployment_name(custom_name)
        
        if success:
            print(f"✅ {message}")
            print(f"\n🎉 Great! Update your .env file with:")
            print(f"AZURE_OPENAI_DEPLOYMENT_NAME={custom_name}")
        else:
            print(f"❌ {message}")

if __name__ == "__main__":
    main()
