# Rainbow Bridge API Documentation

## Overview
Rainbow Bridge provides a comprehensive API for managing children's profiles, routines, communication, and progress tracking. The application integrates Model Context Protocol (MCP) for advanced AI-powered routine management through natural language.

## Base URL
```
http://localhost:8000
```

## Authentication
Currently, no authentication is required for local development. Future versions will include secure authentication for production deployments.

## Core Endpoints

### Children Management

#### Get All Children
```http
GET /api/children
```
**Response:**
```json
[
  {
    "id": 1,
    "name": "Alex",
    "age": 8,
    "communication_level": "verbal",
    "interests": ["drawing", "music"],
    "special_needs": ["autism", "sensory_processing"],
    "preferences": {
      "communication_style": "visual",
      "favorite_colors": ["blue", "green"]
    }
  }
]
```

#### Create Child Profile
```http
POST /api/child
```
**Request Body:**
```json
{
  "name": "Alex",
  "age": 8,
  "communication_level": "verbal",
  "interests": ["drawing", "music"],
  "special_needs": ["autism"],
  "preferences": {
    "communication_style": "visual"
  }
}
```

#### Get Child Details
```http
GET /api/child/{child_id}
```

### Communication & Chat

#### Chat with AI Assistant
```http
POST /api/chat
```
**Request Body:**
```json
{
  "message": "I want to create a morning routine",
  "child_id": 1,
  "session_id": "optional-session-id"
}
```

**Response:**
```json
{
  "response": "🌈 Wonderful! I'll help you create a colorful morning routine! ✨",
  "session_id": "generated-session-id",
  "intent_detected": "create_routine",
  "mcp_tool_used": "create_routine"
}
```

#### Get Visual Cards
```http
GET /api/visual-cards
```
**Response:**
```json
[
  {
    "name": "happy",
    "path": "/static/images/visual_cards/happy.png",
    "category": "emotions"
  },
  {
    "name": "eat",
    "path": "/static/images/visual_cards/eat.png", 
    "category": "activities"
  }
]
```

### Routine Management (MCP-Powered)

The routine management system is powered by MCP (Model Context Protocol) and can be accessed through natural language via the chat interface or direct API calls.

#### Natural Language Examples
Through the chat interface (`/api/chat`), users can interact with routines using natural language:

- `"Create a morning routine"` → Triggers routine creation workflow
- `"What routines do I have?"` → Lists all user routines
- `"Start my bedtime routine"` → Begins routine session
- `"I completed brushing teeth"` → Marks activity as done

#### Direct API Access

#### Get Child Routines
```http
GET /api/routines/{child_id}
```
**Response:**
```json
[
  {
    "id": 1,
    "name": "Morning Routine",
    "schedule_time": "08:00",
    "days_of_week": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
    "activities": [
      {
        "name": "Brush teeth",
        "duration_minutes": 5,
        "description": "Brush your teeth with your favorite toothpaste",
        "visual_cue": "🦷",
        "completed": false
      }
    ],
    "active": true
  }
]
```

#### Create Routine
```http
POST /api/routine
```
**Request Body:**
```json
{
  "child_id": 1,
  "name": "Evening Routine",
  "activities": ["Bath time", "Story time", "Sleep"],
  "schedule_time": "19:00",
  "days_of_week": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
}
```

#### Start Routine Session
```http
POST /api/routine/{routine_id}/start
```
**Response:**
```json
{
  "session_id": 123,
  "current_activity": {
    "name": "Brush teeth",
    "description": "Brush your teeth with your favorite toothpaste",
    "duration_minutes": 5
  },
  "progress": "1/3 activities"
}
```

#### Complete Activity
```http
POST /api/routine/{routine_id}/complete-activity
```
**Request Body:**
```json
{
  "activity_name": "Brush teeth"
}
```

### Progress Tracking

#### Get Child Progress
```http
GET /api/progress/{child_id}
```

#### Log Interaction
```http
POST /api/interaction
```
**Request Body:**
```json
{
  "child_id": 1,
  "interaction_type": "chat",
  "content": "Hello!",
  "response": "Hi there! 🌈",
  "success": true,
  "emotion_detected": "happy"
}
```

## MCP Integration Details

### MCP Server Tools
The application includes a comprehensive MCP server (`core/routine_mcp_server.py`) with these tools:

1. **create_routine**
   - Creates new routines through natural language
   - Supports routine types: morning, bedtime, learning, calming, custom
   - Extracts schedule times and activity preferences

2. **get_child_routines**
   - Retrieves all routines for a specific child
   - Returns child-friendly formatted responses

3. **start_routine**
   - Begins a routine session
   - Provides step-by-step activity guidance
   - Tracks session progress

4. **complete_activity**
   - Marks activities as completed
   - Shows next activity in sequence
   - Provides encouraging feedback

5. **get_routine_suggestions**
   - AI-generated activity suggestions
   - Based on time of day and child's mood
   - Personalized recommendations

6. **update_routine**
   - Modifies existing routine parameters
   - Supports partial updates

### Intent Detection
The MCP client (`core/routine_mcp_client.py`) detects routine intents from natural language:

**Supported Intent Patterns:**
- **create_routine**: "create routine", "new routine", "make routine"
- **get_routines**: "my routines", "show routines", "what routines"
- **start_routine**: "start", "begin", "do routine"
- **complete_activity**: "done", "finished", "completed"
- **get_suggestions**: "what should i do", "suggest activities"

## Error Handling

All endpoints return appropriate HTTP status codes:
- `200`: Success
- `400`: Bad Request (invalid input)
- `404`: Not Found
- `500`: Internal Server Error

**Error Response Format:**
```json
{
  "error": "Error description",
  "details": "Additional error details",
  "timestamp": "2025-07-12T10:30:00Z"
}
```

## Rate Limiting
Currently no rate limiting is implemented for local development. Production deployments should implement appropriate rate limiting.

## WebSocket Support
The application supports WebSocket connections for real-time updates:
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/{child_id}');
```

## Child-Friendly Design Principles
All API responses follow Rainbow Bridge's design principles:
- **Encouraging Language**: Positive, supportive responses
- **Visual Elements**: Emoji and visual cues in text responses
- **Predictable Patterns**: Consistent response formats
- **Celebration Focus**: Achievement recognition and encouragement
