# 🌈 Rainbow Bridge Demos - Quick Reference

## Available Demo Scripts

### 1. `test_system.py` - System Component Test ⚡
**Use for:** Verifying all components work without API keys
```bash
/home/amit-shukla/RainbowBridge-MagicalCompanion/venv/bin/python test_system.py
```
- ✅ Tests all core modules
- ✅ No API keys required
- ✅ Fast execution
- ✅ Shows component status

### 2. `quick_demo.py` - Smart Schedule Demo 🚀
**Use for:** Testing AI-powered smart schedule generation
```bash
/home/amit-shukla/RainbowBridge-MagicalCompanion/venv/bin/python quick_demo.py
```
- ✅ Smart schedule generation
- ✅ Multiple scenarios (morning, afternoon, evening)
- ✅ AI communication examples
- ⚠️ Requires AI API keys (OpenAI or Azure OpenAI)

### 3. `demo_smart_schedule.py` - Full System Demo 🎯
**Use for:** Complete system exploration with interactive mode
```bash
/home/amit-shukla/RainbowBridge-MagicalCompanion/venv/bin/python demo_smart_schedule.py
```
- ✅ Complete system initialization
- ✅ Database setup with demo child
- ✅ Interactive chat mode
- ✅ All features demonstrated
- ⚠️ Requires AI API keys

## Quick Start Commands

### Check System Status (No AI keys needed)
```bash
cd /home/amit-shukla/RainbowBridge-MagicalCompanion
/home/amit-shukla/RainbowBridge-MagicalCompanion/venv/bin/python test_system.py
```

### Test Smart Schedule Feature
```bash
cd /home/amit-shukla/RainbowBridge-MagicalCompanion

# Set up AI credentials first (choose one):
export OPENAI_API_KEY="your_key_here"
# OR
export USE_AZURE_OPENAI="true"
export AZURE_OPENAI_API_KEY="your_key"
export ENDPOINT_URL="your_endpoint" 
export DEPLOYMENT_NAME="your_deployment"

# Run demo
/home/amit-shukla/RainbowBridge-MagicalCompanion/venv/bin/python quick_demo.py
```

### Interactive Chat Mode
```bash
/home/amit-shukla/RainbowBridge-MagicalCompanion/venv/bin/python demo_smart_schedule.py
# Choose option 2 for interactive mode
```

## Example Smart Schedule Requests to Try

### For Interactive Mode:
- "Plan my morning with calm activities"
- "I want creative activities for this afternoon"
- "Help me schedule drawing and music time"
- "Create a bedtime routine with quiet activities"
- "I want to do fun activities when I have high energy"

### What You'll See:
```
👦 You: Plan my morning with calm activities

🌈 Rainbow Bridge: 🌈 Good morning, my wonderful friend! Let's create a peaceful and colorful morning routine that will help you start your day feeling calm and happy! ✨

📋 Generated activities:
  1. Deep Breathing Exercise (10 minutes)
  2. Quiet Reading Time (15 minutes)  
  3. Gentle Stretching (10 minutes)
  4. Calm Music Listening (15 minutes)

😊 Emotion: encouraging
🎨 Visual cues: rainbow, sparkles, calm
🎯 Routine action: smart_schedule
```

## Features Demonstrated

### ✅ Smart Schedule Generation
- AI understands natural language requests
- Generates autism-friendly activities
- Considers time of day, energy level, preferences
- Provides structured, predictable schedules

### ✅ Intent Detection & Routing
- Detects routine-related requests automatically
- Routes between AI assistant and routine manager
- Maintains context across interactions

### ✅ Autism-Friendly Design
- Sensory-friendly activity suggestions
- Clear, simple language
- Visual cues and emotional support
- Positive reinforcement patterns

### ✅ System Integration
- Model Context Protocol (MCP) for routine management
- Local LLM + Cloud AI hybrid approach
- SQLite database with session management
- Comprehensive error handling

## Troubleshooting

### If you see "No module named 'openai'":
```bash
cd /home/amit-shukla/RainbowBridge-MagicalCompanion
source venv/bin/activate
pip install openai fastapi uvicorn aiofiles aiosqlite
```

### If demos don't work:
1. Check component status: `python test_system.py`
2. Verify AI credentials are set
3. Check internet connection for cloud AI
4. Review error messages in output

### If you want to use local LLM instead:
```bash
# Set up Ollama (if not already done)
bash setup_local_llm.sh

# Enable local mode
export LOCAL_MODE="true"

# Run demos (no API keys needed)
python quick_demo.py
```

## Next Steps

1. **Start with system test**: `python test_system.py`
2. **Try quick demo**: `python quick_demo.py` 
3. **Explore interactive mode**: `python demo_smart_schedule.py`
4. **Read the full guide**: `DEMO_GUIDE.md`
5. **Explore the codebase**: Check `core/ai_assistant.py` for implementation details

## Success Indicators

✅ **Working correctly if you see:**
- "Smart schedule generated!" messages
- Multiple activities listed with durations
- Autism-friendly, encouraging language from Rainbow Bridge
- Proper intent detection for routine requests

❌ **Issues if you see:**
- API key errors → Set up OpenAI/Azure credentials
- Import errors → Run `pip install -r requirements.txt`
- Database errors → Check file permissions
- "No AI response" → Check internet connection

Happy exploring! 🌈✨
