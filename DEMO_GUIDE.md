# Rainbow Bridge Demo Guide

## Overview
This guide demonstrates the enhanced Rainbow Bridge system with AI-powered smart schedule generation for autistic children.

## Available Demos

### 1. Quick Demo (`quick_demo.py`)
**Best for:** Quick testing of core features

```bash
python quick_demo.py
```

**Features demonstrated:**
- ✅ Smart schedule generation with different scenarios
- ✅ Basic AI communication and routine detection
- ✅ Emotion detection and visual cue suggestions
- ✅ Multiple time-of-day scenarios (morning, afternoon, evening)

### 2. Comprehensive Demo (`demo_smart_schedule.py`)
**Best for:** Full system testing and exploration

```bash
python demo_smart_schedule.py
```

**Features demonstrated:**
- ✅ Complete system initialization
- ✅ Database setup with demo child profile
- ✅ AI-powered smart schedule generation
- ✅ Routine management through MCP client
- ✅ Activity completion tracking
- ✅ System status and connectivity testing
- ✅ Interactive chat mode

## Smart Schedule Feature Examples

### Example 1: Morning Calm Activities
```python
# User request: "Can you plan my morning with calm activities?"
# Parameters extracted:
{
    "time_of_day": "morning",
    "preferences": ["calm", "quiet"],
    "energy_level": "low"
}

# AI generates activities like:
1. Deep Breathing Exercise (10 minutes)
2. Quiet Reading Time (15 minutes)  
3. Gentle Stretching (10 minutes)
4. Calm Music Listening (15 minutes)
```

### Example 2: Creative Afternoon
```python
# User request: "I want to do fun creative activities this afternoon"
# Parameters extracted:
{
    "time_of_day": "afternoon", 
    "preferences": ["fun", "creative"],
    "energy_level": "high"
}

# AI generates activities like:
1. Colorful Drawing Session (20 minutes)
2. Creative Building Blocks (25 minutes)
3. Musical Instrument Play (15 minutes)
4. Imaginative Story Time (20 minutes)
```

## Key Features Demonstrated

### 🤖 AI-Powered Schedule Generation
- Natural language understanding of schedule requests
- Personalized activity suggestions based on:
  - Time of day
  - Child's energy level  
  - Mentioned preferences
  - Autism-specific considerations

### 🎯 Intent Detection & Routing
- Automatic detection of routine-related requests
- Smart routing between AI assistant and MCP routine manager
- Context-aware responses

### 🌈 Autism-Friendly Design
- Sensory-friendly activity suggestions
- Predictable structure and clear transitions
- Visual cues and emotional support
- Positive reinforcement patterns

### 🔧 System Integration
- Model Context Protocol (MCP) for routine management
- Local LLM + Cloud AI hybrid approach
- Database integration with session management
- Comprehensive error handling

## Running the Demos

### Prerequisites
```bash
# Ensure your environment is set up
pip install -r requirements.txt

# Optional: Set up local LLM (Ollama)
bash setup_local_llm.sh

# Configure AI credentials (choose one):
# Option 1: OpenAI
export OPENAI_API_KEY="your_key_here"

# Option 2: Azure OpenAI  
export USE_AZURE_OPENAI="true"
export AZURE_OPENAI_API_KEY="your_key"
export ENDPOINT_URL="your_endpoint"
export DEPLOYMENT_NAME="your_deployment"
```

### Quick Start
```bash
# Simplest demo
python quick_demo.py

# Interactive mode
python demo_smart_schedule.py
# Choose option 2 for interactive chat
```

### Demo Scenarios to Try

#### Smart Schedule Requests
- "Plan my morning with calm activities"
- "I want creative activities for this afternoon"  
- "Help me schedule drawing and music time"
- "Create a bedtime routine with quiet activities"

#### Routine Management
- "I want to create a morning routine"
- "Show me my routines"
- "Start my bedtime routine"  
- "I finished reading time"

#### General Communication
- "I'm feeling happy today!"
- "I want to draw something colorful"
- "I'm feeling overwhelmed"
- "Can you help me with my schedule?"

## Understanding the Output

### Smart Schedule Response Format
```python
{
    "success": True,
    "schedule_text": "🌈 Rainbow Bridge response with magical language",
    "activities": [
        {
            "name": "Activity Name",
            "description": "Child-friendly description", 
            "duration": "15 minutes",
            "visual_cue": "activity_icon"
        }
    ],
    "time_of_day": "morning",
    "preferences": ["calm", "creative"],
    "energy_level": "medium"
}
```

### AI Response Format
```python
{
    "text": "Rainbow Bridge response text",
    "visual_cues": ["rainbow", "sparkles", "happy_face"],
    "emotion": "encouraging", 
    "confidence": 0.95,
    "suggested_actions": ["create_routine", "start_activity"],
    "communication_type": "text",
    "llm_source": "mcp_routine" | "local" | "openai",
    "routine_action": "smart_schedule" | "create_routine" | etc.
}
```

## Troubleshooting

### Common Issues

1. **No AI response**: Check API keys and internet connection
2. **Local LLM not working**: Run `python check_llm_status.py`
3. **Database errors**: Ensure SQLite permissions and disk space
4. **MCP errors**: Check if routine management is properly initialized

### Debug Commands
```bash
# Check system status
python -c "
import asyncio
from core.ai_assistant import SpecialKidsAI
async def test():
    ai = SpecialKidsAI()
    status = ai.get_llm_status()
    print(status)
asyncio.run(test())
"

# Test database connection
python -c "
import asyncio  
from database.db_manager import DatabaseManager
async def test():
    db = DatabaseManager()
    await db.initialize()
    print('Database OK')
asyncio.run(test())
"
```

## Next Steps

After running the demos:

1. **Explore the code**: Look at `core/ai_assistant.py` for AI logic
2. **Customize prompts**: Modify system prompts for different behaviors
3. **Add activities**: Extend the activity database
4. **Create new intents**: Add more routine management capabilities
5. **Integrate with UI**: Connect to the web interface

## Demo Success Indicators

✅ **Smart Schedule Working**: AI generates 4-6 appropriate activities
✅ **Intent Detection Working**: Routine requests are properly routed  
✅ **Personalization Working**: Activities match time/energy/preferences
✅ **AI Communication Working**: Responses are autism-friendly and encouraging
✅ **System Integration Working**: MCP client and database function properly

Enjoy exploring Rainbow Bridge! 🌈✨
