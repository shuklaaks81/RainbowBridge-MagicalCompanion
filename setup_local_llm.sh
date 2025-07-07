#!/bin/bash

# Local LLM Setup Script for Special Kids Assistant
# This script helps you set up and configure local LLM providers

set -e

echo "🌈 Rainbow Bridge - Local LLM Setup 🌈"
echo "======================================"
echo

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check system requirements
check_requirements() {
    print_step "Checking system requirements..."
    
    # Check RAM
    total_ram=$(free -g | awk 'NR==2{print $2}')
    if [ "$total_ram" -lt 8 ]; then
        print_warning "You have ${total_ram}GB RAM. 8GB or more is recommended for 7B models."
    else
        print_success "RAM check passed: ${total_ram}GB available"
    fi
    
    # Check Python version
    if command -v python3 &> /dev/null; then
        python_version=$(python3 --version | cut -d' ' -f2)
        print_success "Python version: $python_version"
    else
        print_error "Python 3 is required but not installed."
        exit 1
    fi
    
    # Check pip
    if command -v pip3 &> /dev/null; then
        print_success "pip3 is available"
    else
        print_error "pip3 is required but not installed."
        exit 1
    fi
}

# Install Ollama
install_ollama() {
    print_step "Installing Ollama..."
    
    if command -v ollama &> /dev/null; then
        print_success "Ollama is already installed"
        return 0
    fi
    
    # Download and install Ollama
    curl -fsSL https://ollama.ai/install.sh | sh
    
    if command -v ollama &> /dev/null; then
        print_success "Ollama installed successfully"
        
        # Start Ollama service
        print_step "Starting Ollama service..."
        ollama serve &
        sleep 5
        
        # Download recommended model
        print_step "Downloading recommended model (llama2:7b-chat)..."
        print_warning "This may take a while (3-4GB download)..."
        ollama pull llama2:7b-chat
        
        print_success "Ollama setup complete!"
    else
        print_error "Failed to install Ollama"
        return 1
    fi
}

# Install Python dependencies for local LLMs
install_python_deps() {
    print_step "Installing Python dependencies for local LLMs..."
    
    # Create requirements file for local LLM dependencies
    cat > requirements_local_llm.txt << EOF
# Local LLM Dependencies
aiohttp>=3.8.0
requests>=2.28.0
transformers>=4.21.0
torch>=1.12.0
tokenizers>=0.13.0
accelerate>=0.21.0
sentencepiece>=0.1.97
EOF
    
    # Install dependencies
    pip3 install -r requirements_local_llm.txt
    
    print_success "Python dependencies installed"
}

# Configure environment
configure_environment() {
    print_step "Configuring environment..."
    
    # Copy local LLM environment template
    if [ ! -f ".env" ]; then
        cp .env.example .env
        print_success "Created .env file from template"
    fi
    
    # Update .env with local LLM settings
    sed -i 's/LOCAL_MODE=False/LOCAL_MODE=True/' .env
    sed -i 's/OLLAMA_ENABLED=True/OLLAMA_ENABLED=True/' .env
    
    print_success "Environment configured for local LLM mode"
}

# Test local LLM setup
test_setup() {
    print_step "Testing local LLM setup..."
    
    # Test Ollama connection
    if curl -s http://localhost:11434/api/tags > /dev/null; then
        print_success "Ollama is running and accessible"
    else
        print_warning "Ollama service may not be running. Start it with: ollama serve"
    fi
    
    # Test Python imports
    python3 -c "import aiohttp, requests, transformers; print('Python dependencies OK')" 2>/dev/null
    if [ $? -eq 0 ]; then
        print_success "Python dependencies are working"
    else
        print_error "Python dependencies test failed"
    fi
}

# Main setup function
main() {
    echo "This script will help you set up local LLM providers for the Special Kids Assistant."
    echo "Choose an option:"
    echo "1. Full setup (Ollama + Python dependencies)"
    echo "2. Install Ollama only"
    echo "3. Install Python dependencies only"
    echo "4. Test existing setup"
    echo "5. Exit"
    echo
    
    read -p "Enter your choice (1-5): " choice
    
    case $choice in
        1)
            check_requirements
            install_ollama
            install_python_deps
            configure_environment
            test_setup
            ;;
        2)
            check_requirements
            install_ollama
            ;;
        3)
            install_python_deps
            ;;
        4)
            test_setup
            ;;
        5)
            echo "Exiting..."
            exit 0
            ;;
        *)
            print_error "Invalid choice. Please run the script again."
            exit 1
            ;;
    esac
    
    echo
    echo "🌈 Setup Complete! 🌈"
    echo "===================="
    echo
    echo "Next steps:"
    echo "1. Make sure Ollama is running: ollama serve"
    echo "2. Set LOCAL_MODE=True in your .env file"
    echo "3. Run the Special Kids Assistant: python main.py"
    echo
    echo "Available Ollama models:"
    echo "- llama2:7b-chat (recommended, installed)"
    echo "- mistral:7b-instruct (fast, download with: ollama pull mistral:7b-instruct)"
    echo "- codellama:7b-instruct (structured, download with: ollama pull codellama:7b-instruct)"
    echo
    echo "For more information, visit: https://ollama.ai"
}

# Run main function
main
