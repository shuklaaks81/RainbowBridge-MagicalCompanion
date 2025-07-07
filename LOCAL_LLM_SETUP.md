# 🌈 Local LLM Setup Guide for Rainbow Bridge

This guide helps you set up local Large Language Models (LLMs) for **Rainbow Bridge Magical Companion**, providing enhanced privacy and offline functionality for your special kids assistant.

## 🎯 Why Use Local LLMs?

- **🔒 Privacy**: All data stays on your device
- **📱 Offline**: Works without internet connection
- **⚡ Performance**: Faster responses (with proper hardware)
- **💰 Cost**: No API fees after initial setup
- **🎛️ Control**: Full control over AI behavior

## 🚀 Quick Setup (Recommended)

### Option 1: Automated Setup Script
```bash
# Run the automated setup
python quick_setup_ollama.py
```

### Option 2: Manual Ollama Setup
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama service
ollama serve

# Download recommended model (in a new terminal)
ollama pull llama2:7b-chat

# Enable local mode
echo "LOCAL_MODE=True" >> .env
```

### Option 3: Complete Setup with Dependencies
```bash
# Run the full setup script
./setup_local_llm.sh
```

## 🛠️ Supported Local LLM Providers

### 1. Ollama (⭐ Recommended)
- **Best for**: Beginners, ease of use
- **Models**: llama2, mistral, codellama, neural-chat
- **Setup**: Automatic with our scripts
- **URL**: http://localhost:11434

### 2. LocalAI
- **Best for**: OpenAI API compatibility
- **Models**: Various GGML/GGUF models
- **Setup**: Manual installation required
- **URL**: http://localhost:8080

### 3. Hugging Face Transformers
- **Best for**: Direct Python integration
- **Models**: Any transformers-compatible model
- **Setup**: Automatic with pip install
- **Resource**: High memory usage

### 4. Text Generation WebUI
- **Best for**: Advanced users, web interface
- **Models**: Wide variety of models
- **Setup**: Manual installation required
- **URL**: http://localhost:5000

## 📋 System Requirements

### Minimum Requirements
- **RAM**: 8GB (for 7B models)
- **Storage**: 10GB free space
- **CPU**: Modern multi-core processor
- **OS**: Linux, macOS, or Windows with WSL

### Recommended Requirements
- **RAM**: 16GB+ (for better performance)
- **GPU**: NVIDIA GPU with 8GB+ VRAM (optional but faster)
- **Storage**: SSD with 20GB+ free space
- **Network**: For initial model downloads

## 🎯 Recommended Models for Special Kids Assistant

### Ollama Models (ordered by recommendation)

1. **llama2:7b-chat** ⭐ Best Overall
   ```bash
   ollama pull llama2:7b-chat
   ```
   - Excellent balance of quality and performance
   - Child-friendly responses
   - Good instruction following

2. **mistral:7b-instruct** ⚡ Fastest
   ```bash
   ollama pull mistral:7b-instruct
   ```
   - Very fast responses
   - Efficient memory usage
   - Good for simple interactions

3. **neural-chat:7b** 💬 Best for Conversations
   ```bash
   ollama pull neural-chat:7b
   ```
   - Optimized for dialogue
   - Natural conversation flow
   - Good emotional understanding

4. **codellama:7b-instruct** 📝 Most Structured
   ```bash
   ollama pull codellama:7b-instruct
   ```
   - Excellent at following structured prompts
   - Good for routine-based responses
   - Clear, organized outputs

## ⚙️ Configuration

### Environment Variables (.env.local)
```bash
# Enable local LLM mode
LOCAL_MODE=True

# Primary provider
PRIMARY_LOCAL_LLM=ollama

# Ollama settings
OLLAMA_ENABLED=True
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2:7b-chat

# Fallback to OpenAI if local fails
FALLBACK_TO_OPENAI=True

# Child safety
CHILD_SAFE_MODE=True
ENABLE_CONTENT_FILTERING=True
```

## 🧪 Testing Your Setup

### Quick Test
```bash
# Test all LLM providers
python test_local_llm.py
```

### Manual Testing
1. Start Rainbow Bridge: `python main.py`
2. Open: http://localhost:8000
3. Click "LLM Settings"
4. Use "Test Connectivity" button

### API Testing
```bash
# Test Ollama directly
curl http://localhost:11434/api/generate -d '{
  "model": "llama2:7b-chat",
  "prompt": "Hello! Please respond with a friendly greeting for a child.",
  "stream": false
}'
```

## 🔧 Troubleshooting

### Common Issues

#### Ollama Not Starting
```bash
# Check if already running
ps aux | grep ollama

# Kill existing processes
pkill ollama

# Start fresh
ollama serve
```

#### Model Not Found
```bash
# List available models
ollama list

# Pull missing model
ollama pull llama2:7b-chat
```

#### Memory Issues
```bash
# Check available RAM
free -h

# Use smaller model
ollama pull llama2:7b-chat-q4_0  # Quantized version
```

#### Permission Issues
```bash
# Fix Ollama permissions
sudo chown -R $USER ~/.ollama
```

### Performance Optimization

#### For Limited RAM (8GB)
```bash
# Use quantized models
ollama pull llama2:7b-chat-q4_0
```

#### For GPU Acceleration
```bash
# Install CUDA support (NVIDIA)
# Ollama automatically uses GPU if available
nvidia-smi  # Check GPU status
```

## 🎮 Using the Web Interface

### LLM Management Dashboard
1. Open Rainbow Bridge: http://localhost:8000
2. Click "LLM Settings" card
3. View provider status
4. Switch between local/cloud modes
5. Test connectivity

### Features
- **Real-time status**: Monitor all providers
- **One-click switching**: Local ↔ Cloud modes
- **Connectivity testing**: Verify all providers work
- **Auto-refresh**: Status updates every 30 seconds

## 🔄 Switching Between Modes

### Via Web Interface
1. Go to http://localhost:8000/admin/llm
2. Click "Switch to Local Mode" or "Switch to Cloud Mode"

### Via Environment
```bash
# Enable local mode
LOCAL_MODE=True

# Disable local mode (use OpenAI)
LOCAL_MODE=False
```

### Via API
```bash
# Switch to local
curl -X POST http://localhost:8000/api/llm/switch -d "mode=local"

# Switch to cloud
curl -X POST http://localhost:8000/api/llm/switch -d "mode=cloud"
```

## 📊 Performance Comparison

| Model | Size | RAM Usage | Speed | Quality | Best For |
|-------|------|-----------|-------|---------|----------|
| llama2:7b-chat | 3.8GB | 8GB+ | Medium | High | General use |
| mistral:7b-instruct | 4.1GB | 8GB+ | Fast | High | Quick responses |
| neural-chat:7b | 3.8GB | 8GB+ | Medium | High | Conversations |
| llama2:13b-chat | 7.3GB | 16GB+ | Slow | Very High | Quality priority |

## 🚨 Safety Features

### Child Safety Mode
- **Content filtering**: Blocks inappropriate responses
- **Positive reinforcement**: Encourages supportive language
- **Context awareness**: Maintains child-appropriate context

### Privacy Protection
- **Local processing**: No data leaves your device
- **No logging**: Conversations not stored externally
- **Secure**: No external API calls when in local mode

## 🆘 Getting Help

### Documentation
- **Main README**: Project overview and setup
- **This Guide**: Local LLM specifics
- **Code Comments**: Inline documentation

### Testing Tools
- `test_local_llm.py`: Comprehensive testing
- `quick_setup_ollama.py`: Quick Ollama setup
- `setup_local_llm.sh`: Full environment setup

### Common Commands
```bash
# Check status
python -c "from core.ai_assistant import SpecialKidsAI; ai = SpecialKidsAI(); print(ai.get_llm_status())"

# Restart Ollama
pkill ollama && ollama serve

# Check logs
tail -f ~/.ollama/logs/server.log
```

## 🌟 Next Steps

1. **Start with Ollama**: Easiest to set up
2. **Test thoroughly**: Use our testing tools
3. **Monitor performance**: Check RAM/CPU usage
4. **Experiment with models**: Try different options
5. **Share feedback**: Help improve the system

---

**🌈 Remember**: The goal is to provide the best possible experience for children with communication needs. Local LLMs offer privacy and control, but the most important thing is that the system works reliably for the kids using it!

Happy coding with Rainbow Bridge! ✨
