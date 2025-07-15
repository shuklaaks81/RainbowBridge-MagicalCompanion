# 🌈✨ Rainbow Bridge: Magical Companion ✨🌈

**Where Every Child's Voice Shines Bright!** 

A revolutionary, magical AI companion specially crafted for special needs children, particularly those with autism and communication challenges. Rainbow Bridge transforms learning and communication into joyful, colorful adventures that celebrate every unique child's journey.

> *"Building bridges to brighter tomorrows, one rainbow at a time!"* 🌈

🎯 **Mission**: Empowering special needs children through magical, AI-powered communication tools that turn challenges into colorful adventures!

## ✨ What Makes Rainbow Bridge Special

### � **Colorful Communication Adventures**
- **Magical AI Companion**: Uses advanced AI optimized for joyful, patient communication
- **Visual Rainbow Cards**: Extensive library of colorful visual cards, symbols, and communication sequences
- **Creative Expression**: Multiple ways to share thoughts, feelings, and ideas
- **Routine Magic**: Structured daily adventures with visual, colorful schedules
- **Growth Celebration**: Tracks and celebrates every wonderful step forward

### � **Rainbow Design Principles**
- **Colorful & Joyful**: Bright, engaging interface that sparks imagination
- **Predictable Adventures**: Consistent, comfortable interaction patterns
- **Visual-First Magic**: Beautiful images, symbols, and visual cues throughout
- **Celebration Focus**: Every achievement is a rainbow moment worth celebrating
- **Personal Journey**: Adapts to each child's unique communication style and interests

## Technology Stack

- **Backend**: Python, FastAPI, SQLite
- **AI Integration**: Azure OpenAI (GPT-3.5-turbo-instruct) with local LLM fallback
- **MCP Architecture**: Model Context Protocol for extensible tool integration
- **Frontend**: HTML, CSS, JavaScript (Vanilla)
- **Database**: SQLite with async support (aiosqlite)
- **Image Processing**: PIL (Pillow) for custom visual cards
- **Protocol**: WebSocket support for real-time interactions

## 🚀 **Quick Start Your Magical Journey**

1. **Clone the Magic** ✨
   ```bash
   git clone https://github.com/yourusername/RainbowBridge-MagicalCompanion.git
   cd RainbowBridge-MagicalCompanion
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```

5. **Initialize the database**
   ```bash
   python -c "import asyncio; from database.db_manager import DatabaseManager; asyncio.run(DatabaseManager().initialize())"
   ```

6. **Start the application**
   ```bash
   python main.py
   ```

7. **Try the demo** ✨
   ```bash
   python demo_fresh_setup.py
   ```

The application will be available at `http://localhost:8000`

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```

5. **Initialize the database**
   ```bash
   python -c "import asyncio; from database.db_manager import DatabaseManager; asyncio.run(DatabaseManager().initialize())"
   ```

## Usage

### Starting the Application

```bash
python main.py
```

The application will be available at `http://localhost:8000`

### First Time Setup

1. **Create a Child Profile**
   - Navigate to the home page
   - Click "Create Child Profile"
   - Fill in the child's information including:
     - Name and age
     - Communication level
     - Interests and special considerations

2. **Access the Dashboard**
   - Select the child from the home page
   - Access their personalized dashboard

### Key Features Usage

#### AI Chat Assistant
- **Text Communication**: Type messages to interact with the AI
- **Visual Communication**: Select visual cards to communicate
- **Audio Support**: Record audio messages (coming soon)

#### Routine Management 🎨
- **Natural Language Routine Creation**: Simply ask "Create a morning routine" in chat
- **Smart Routine Suggestions**: AI-powered activity recommendations based on time and mood
- **Interactive Routine Sessions**: Start routines through chat with step-by-step guidance
- **Progress Tracking**: Real-time activity completion with encouraging feedback
- **MCP Integration**: Advanced Model Context Protocol for seamless chat-based routine management
- **Current Activity Display**: Always shows the current activity name in all communications during active routines
- **General Phrase Recognition**: Understands natural expressions like "I'm done", "finished", or "completed that"

**Example Interactions:**
```
Child: "I want to create a bedtime routine"
AI: 🌈 Wonderful! I'll help you create a colorful bedtime routine! ✨

Child: "What routines do I have?"
AI: 🌈 Here are all your wonderful routines! ✨

Child: "Start my morning routine"
AI: 🌈 Let's start your 'Morning Routine'! This is going to be wonderful! ✨
Current Activity: Brushing Teeth

Child: "I'm done" or "finished that"
AI: 🎉 Amazing job completing 'Brushing Teeth'! You're doing wonderful! 
Current Activity: Getting Dressed ✨

Child: "all done"
AI: 🎉 Fantastic work on 'Getting Dressed'! What a superstar! 
Current Activity: Eating Breakfast ✨
```

#### Progress Tracking
- **Real-time Monitoring**: Track communication improvements
- **Milestone Achievements**: Celebrate developmental milestones
- **Caregiver Insights**: Detailed reports for caregivers and therapists

## API Endpoints

### Child Management
- `POST /api/child` - Create a new child profile
- `GET /api/children` - Get all children
- `GET /child/{child_id}` - Get child dashboard

### Communication
- `POST /api/chat` - Send message to AI assistant
- `GET /api/visual-cards` - Get available visual cards
- `POST /api/upload-image` - Upload custom visual cards

### Routines
- `POST /api/routine` - Create a new routine
- `GET /api/routine/{routine_id}` - Get routine details
- `POST /api/routine/start` - Start a routine session

### Progress
- `GET /api/progress/{child_id}` - Get child's progress report
- `GET /api/progress/{child_id}/detailed` - Get detailed progress analytics

## Configuration

### AI Model Configuration
The AI assistant is configured with specific prompts optimized for autism spectrum communication:

- **Simple Language**: Uses clear, concise language
- **Patience**: Provides patient, encouraging responses
- **Visual Support**: Suggests visual aids when helpful
- **Routine Focus**: Relates responses to familiar activities
- **Positive Reinforcement**: Celebrates achievements and progress

### Database Schema
- **Children**: Stores child profiles and preferences
- **Interactions**: Logs all communication interactions
- **Routines**: Manages daily routines and activities
- **Milestones**: Tracks developmental milestones
- **Progress**: Historical progress data

## 🛠️ MCP Architecture & Extensibility

Rainbow Bridge uses the **Model Context Protocol (MCP)** for seamless integration of AI tools and capabilities:

### MCP Server Components
- **Routine Management Server**: Handles all routine-related operations through natural language
- **Tool Registry**: Extensible architecture for adding new capabilities
- **Intent Detection**: Smart pattern matching for user requests
- **Child-Friendly Responses**: Consistent, encouraging communication style

### Available MCP Tools
1. **create_routine**: Natural language routine creation
2. **get_child_routines**: Retrieve and display user routines  
3. **start_routine**: Begin routine sessions with guidance
4. **complete_activity**: Track progress and show next steps with current activity context
5. **get_routine_suggestions**: AI-powered activity recommendations
6. **update_routine**: Modify existing routine parameters

### Enhanced Features ✨
- **Current Activity Context**: Always displays the current activity name in communications during active routines
- **Natural Language Intent Detection**: Recognizes general completion phrases like "I'm done", "finished", "all done"
- **Intelligent Activity Extraction**: Uses fuzzy matching to understand activity references in natural language
- **Real-time Progress Updates**: Immediate feedback and next activity guidance with visual cues

### Extensibility
The MCP architecture makes it easy to add new features:
- Create new MCP servers for different domains (learning, social skills, etc.)
- Add new tools to existing servers
- Integrate with external services and APIs
- Maintain consistent child-friendly interaction patterns

## Testing & Demo Scripts

### Available Demo Scripts
- **`demo_fresh_setup.py`**: Complete demo showcasing current activity display and natural language completion
- **`test_final_general.py`**: Tests general phrase recognition and completion detection
- **`test_current_activity_display.py`**: Validates current activity context in all communications
- **`debug_completion_trace.py`**: Debug script for tracing completion workflow

### Running Tests
```bash
# Run the comprehensive demo
python demo_fresh_setup.py

# Test general phrase recognition
python test_final_general.py

# Test current activity display
python test_current_activity_display.py
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow the sensory-friendly design principles
- Test all features with accessibility in mind
- Ensure AI responses are appropriate for the target audience
- Add comprehensive logging for debugging
- Include proper error handling

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please contact [your-email@example.com] or create an issue in the repository.

## Acknowledgments

- Special thanks to autism spectrum families and therapists who provided input
- OpenAI for providing the language model technology
- The autism community for inspiration and guidance

## Roadmap

### Upcoming Features
- [ ] Voice recognition and text-to-speech
- [ ] Multi-language support
- [ ] Tablet/mobile app versions
- [ ] Advanced progress analytics
- [ ] Integration with therapy tools
- [ ] Caregiver mobile notifications
- [ ] Expanded visual card library
- [ ] Social story creation tools

### Version History
- **v1.0.0**: Initial release with core features
- **v1.1.0**: Enhanced visual communication tools
- **v1.2.0**: Advanced progress tracking
- **v1.3.0**: Current activity display and natural language completion detection
- **v2.0.0**: Mobile app integration (planned)

## Technical Details

### Security Considerations
- All user data is stored locally
- No personal information is sent to OpenAI
- Secure API key management
- Input validation and sanitization

### Performance Optimization
- Async database operations
- Efficient image processing
- Optimized AI API calls
- Caching for frequently accessed data

### Accessibility Features
- WCAG 2.1 AA compliance
- High contrast modes
- Large text options
- Keyboard navigation support
- Screen reader compatibility
