#!/usr/bin/env python3
"""
Debug script to check environment variables
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("🔍 Environment Variables Debug")
print("=" * 40)

# Check all relevant environment variables
env_vars = [
    "USE_AZURE_OPENAI",
    "LOCAL_MODE",
    "AZURE_OPENAI_API_KEY",
    "ENDPOINT_URL",
    "DEPLOYMENT_NAME", 
    "AZURE_OPENAI_ENDPOINT",
    "AZURE_OPENAI_DEPLOYMENT_NAME",
    "AZURE_OPENAI_API_VERSION"
]

for var in env_vars:
    value = os.getenv(var)
    if value:
        # Mask API key for security
        if "API_KEY" in var and len(value) > 10:
            display_value = value[:10] + "..." + value[-5:]
        else:
            display_value = value
        print(f"{var}: {display_value}")
    else:
        print(f"{var}: NOT SET")

print("\n📋 Azure OpenAI Configuration Priority:")
print(f"subscription_key: {os.getenv('AZURE_OPENAI_API_KEY', 'REPLACE_WITH_YOUR_KEY_VALUE_HERE')[:10]}...")
print(f"endpoint: {os.getenv('ENDPOINT_URL', 'https://aistatrter.openai.azure.com/')}")
print(f"deployment: {os.getenv('DEPLOYMENT_NAME', 'gpt-35-turbo-instruct')}")
