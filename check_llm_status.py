#!/usr/bin/env python3
"""
Local LLM Status Checker
Monitors the status of Ollama and available models for the Rainbow Bridge application.
"""

import subprocess
import requests
import json
from datetime import datetime

def run_command(command):
    """Run a shell command and return the output."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return False, "", str(e)

def check_ollama_service():
    """Check if Ollama service is running."""
    success, stdout, stderr = run_command("pgrep ollama")
    return success and stdout

def check_ollama_api():
    """Check if Ollama API is responding."""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        return response.status_code == 200, response.json() if response.status_code == 200 else None
    except Exception as e:
        return False, str(e)

def get_available_models():
    """Get list of available models from Ollama."""
    success, stdout, stderr = run_command("ollama list")
    if success:
        lines = stdout.split('\n')[1:]  # Skip header
        models = []
        for line in lines:
            if line.strip():
                parts = line.split()
                if len(parts) >= 3:
                    models.append({
                        'name': parts[0],
                        'id': parts[1],
                        'size': parts[2],
                        'modified': ' '.join(parts[3:]) if len(parts) > 3 else 'Unknown'
                    })
        return True, models
    return False, stderr

def check_model_status(model_name="llama2:7b-chat"):
    """Check if a specific model is available and ready."""
    success, models = get_available_models()
    if success:
        for model in models:
            if model['name'] == model_name:
                return True, model
    return False, None

def test_model_generation(model_name="llama2:7b-chat"):
    """Test if model can generate responses."""
    try:
        cmd = f'curl -X POST http://localhost:11434/api/generate -H "Content-Type: application/json" -d \'{{"model": "{model_name}", "prompt": "Hello", "stream": false}}\''
        success, stdout, stderr = run_command(cmd)
        if success and stdout:
            try:
                response = json.loads(stdout)
                return True, response.get('response', 'No response field')
            except json.JSONDecodeError:
                return False, "Invalid JSON response"
        return False, stderr or "No response"
    except Exception as e:
        return False, str(e)

def main():
    """Main status check function."""
    print("🌈 Rainbow Bridge - Local LLM Status Check")
    print("=" * 50)
    print(f"⏰ Check Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Check Ollama service
    print("🔧 Ollama Service Status:")
    if check_ollama_service():
        print("  ✅ Ollama service is running")
    else:
        print("  ❌ Ollama service is not running")
        print("  💡 Try: ollama serve")
        return

    # Check Ollama API
    print("\n🌐 Ollama API Status:")
    api_success, api_data = check_ollama_api()
    if api_success:
        print("  ✅ Ollama API is responding")
    else:
        print(f"  ❌ Ollama API is not responding: {api_data}")
        return

    # Check available models
    print("\n📦 Available Models:")
    models_success, models = get_available_models()
    if models_success:
        if models:
            for model in models:
                print(f"  📋 {model['name']}")
                print(f"     ID: {model['id']}")
                print(f"     Size: {model['size']}")
                print(f"     Modified: {model['modified']}")
                print()
        else:
            print("  ⚠️  No models available yet")
            print("  💡 Run: ollama pull llama2:7b-chat")
    else:
        print(f"  ❌ Error listing models: {models}")

    # Check specific model
    print("\n🎯 Target Model (llama2:7b-chat):")
    model_success, model_info = check_model_status()
    if model_success:
        print(f"  ✅ Model is available")
        print(f"  📊 Size: {model_info['size']}")
        print(f"  🕒 Modified: {model_info['modified']}")
        
        # Test model generation
        print("\n🧪 Model Generation Test:")
        test_success, response = test_model_generation()
        if test_success:
            print("  ✅ Model is responding")
            print(f"  💬 Sample response: {response[:100]}...")
        else:
            print(f"  ❌ Model test failed: {response}")
    else:
        print("  ⏳ Model is not available yet (still downloading or not pulled)")
        print("  💡 Check download progress with: ollama ps")

    print("\n" + "=" * 50)
    print("🚀 Ready for Rainbow Bridge when all checks pass!")

if __name__ == "__main__":
    main()
