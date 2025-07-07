#!/usr/bin/env python3
"""
Simple Ollama Setup for Rainbow Bridge
This script helps quickly set up Ollama for local LLM usage.
"""

import os
import sys
import subprocess
import time
import requests
import json

def print_step(message):
    print(f"🌈 {message}")

def print_success(message):
    print(f"✅ {message}")

def print_error(message):
    print(f"❌ {message}")

def run_command(command, check=True):
    """Run a shell command and return the result."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=check)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return False, "", str(e)

def check_ollama_installed():
    """Check if Ollama is installed."""
    success, _, _ = run_command("which ollama", check=False)
    return success

def install_ollama():
    """Install Ollama."""
    print_step("Installing Ollama...")
    
    if check_ollama_installed():
        print_success("Ollama is already installed!")
        return True
    
    # Download and install Ollama
    success, stdout, stderr = run_command("curl -fsSL https://ollama.ai/install.sh | sh")
    
    if success:
        print_success("Ollama installed successfully!")
        return True
    else:
        print_error(f"Failed to install Ollama: {stderr}")
        return False

def start_ollama():
    """Start Ollama service."""
    print_step("Starting Ollama service...")
    
    # Check if already running
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            print_success("Ollama is already running!")
            return True
    except:
        pass
    
    # Start Ollama in background
    success, _, _ = run_command("ollama serve > /dev/null 2>&1 &", check=False)
    
    # Wait for it to start
    print_step("Waiting for Ollama to start...")
    for i in range(10):
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            if response.status_code == 200:
                print_success("Ollama service started!")
                return True
        except:
            pass
        time.sleep(2)
    
    print_error("Failed to start Ollama service")
    return False

def download_model(model_name="llama2:7b-chat"):
    """Download a recommended model."""
    print_step(f"Downloading {model_name} model...")
    print("⏳ This may take a few minutes (3-4GB download)...")
    
    success, stdout, stderr = run_command(f"ollama pull {model_name}")
    
    if success:
        print_success(f"Model {model_name} downloaded successfully!")
        return True
    else:
        print_error(f"Failed to download model: {stderr}")
        return False

def test_ollama():
    """Test Ollama functionality."""
    print_step("Testing Ollama...")
    
    try:
        # Test basic connectivity
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code != 200:
            print_error("Ollama API not responding")
            return False
        
        # Test model generation
        test_prompt = {
            "model": "llama2:7b-chat",
            "prompt": "Hello! Please respond with just 'Hello there!'",
            "stream": False
        }
        
        response = requests.post(
            "http://localhost:11434/api/generate",
            json=test_prompt,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print_success("Ollama test successful!")
            print(f"Test response: {result.get('response', 'No response')[:50]}...")
            return True
        else:
            print_error(f"Ollama test failed: HTTP {response.status_code}")
            return False
    
    except Exception as e:
        print_error(f"Ollama test failed: {str(e)}")
        return False

def update_env_file():
    """Update .env file to enable local mode."""
    print_step("Updating environment configuration...")
    
    env_file = ".env"
    
    # Read current .env file
    env_lines = []
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            env_lines = f.readlines()
    
    # Update or add LOCAL_MODE=True
    local_mode_found = False
    for i, line in enumerate(env_lines):
        if line.startswith('LOCAL_MODE='):
            env_lines[i] = 'LOCAL_MODE=True\n'
            local_mode_found = True
            break
    
    if not local_mode_found:
        env_lines.append('LOCAL_MODE=True\n')
    
    # Write back to file
    with open(env_file, 'w') as f:
        f.writelines(env_lines)
    
    print_success("Environment file updated!")

def main():
    print("🌈✨ Rainbow Bridge - Quick Ollama Setup ✨🌈")
    print("=" * 50)
    
    # Check system
    print_step("Checking system requirements...")
    
    # Check if running on Linux/Mac
    if sys.platform.startswith('win'):
        print_error("This script is for Linux/Mac. For Windows, please install Ollama manually from https://ollama.ai")
        return
    
    # Install Ollama
    if not install_ollama():
        return
    
    # Start Ollama
    if not start_ollama():
        return
    
    # Download model
    if not download_model():
        return
    
    # Test functionality
    if not test_ollama():
        return
    
    # Update environment
    update_env_file()
    
    print("\n🎉 Setup Complete! 🎉")
    print("=" * 50)
    print("✅ Ollama is installed and running")
    print("✅ llama2:7b-chat model is downloaded")
    print("✅ Local mode is enabled")
    print("\nNext steps:")
    print("1. Run: python main.py")
    print("2. Open: http://localhost:8000")
    print("3. Click 'LLM Settings' to manage AI providers")
    print("4. Test with: python test_local_llm.py")
    print("\n🌈 Happy chatting with Rainbow Bridge! 🌈")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup interrupted by user.")
    except Exception as e:
        print_error(f"Setup failed: {str(e)}")
        sys.exit(1)
