"""
MCP Client Integration for Rainbow Bridge AI Assistant

This module integrates MCP server functionality into the AI assistant,
allowing chat-based routine management.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class MCPToolResult:
    """Result from an MCP tool call."""
    success: bool
    content: str
    error: Optional[str] = None

class RoutineMCPClient:
    """Client for interacting with the routine MCP server."""
    
    def __init__(self, routine_mcp_server):
        self.mcp_server = routine_mcp_server
        self.available_tools = [
            "create_routine",
            "get_child_routines", 
            "start_routine",
            "complete_activity",
            "get_routine_suggestions",
            "update_routine"
        ]
    
    async def detect_routine_intent(self, message: str, child_id: int) -> Optional[Dict[str, Any]]:
        """Detect if a message contains routine-related intent."""
        message_lower = message.lower()
        
        # Intent patterns for routine management
        intent_patterns = {
            "create_routine": [
                "create routine", "new routine", "make routine", "start routine",
                "add routine", "schedule", "plan activities"
            ],
            "get_routines": [
                "my routines", "show routines", "what routines", "list routines",
                "see my schedule", "what activities"
            ],
            "start_routine": [
                "start", "begin", "do routine", "time for", "ready for"
            ],
            "complete_activity": [
                "done", "finished", "completed", "did it", "finished with"
            ],
            "get_suggestions": [
                "what should i do", "activity ideas", "suggest", "what activities",
                "help me choose", "what's next"
            ]
        }
        
        detected_intent = None
        for intent, patterns in intent_patterns.items():
            if any(pattern in message_lower for pattern in patterns):
                detected_intent = intent
                break
        
        if not detected_intent:
            return None
        
        # Extract parameters based on intent
        intent_data = {
            "intent": detected_intent,
            "confidence": 0.8,  # Simple confidence score
            "child_id": child_id,
            "message": message
        }
        
        # Extract specific parameters
        if detected_intent == "create_routine":
            intent_data.update(self._extract_create_routine_params(message))
        elif detected_intent == "complete_activity":
            intent_data.update(self._extract_activity_name(message))
        elif detected_intent == "start_routine":
            intent_data.update(self._extract_routine_name(message))
        
        return intent_data
    
    def _extract_create_routine_params(self, message: str) -> Dict[str, Any]:
        """Extract parameters for creating a routine."""
        params = {}
        
        # Look for routine types
        routine_types = ["morning", "bedtime", "learning", "calming", "evening"]
        for routine_type in routine_types:
            if routine_type in message.lower():
                params["routine_type"] = routine_type
                break
        else:
            params["routine_type"] = "custom"
        
        # Look for time mentions
        import re
        time_pattern = r'(\d{1,2}):(\d{2})|(\d{1,2})\s*(am|pm)'
        time_match = re.search(time_pattern, message.lower())
        if time_match:
            if time_match.group(1) and time_match.group(2):
                params["schedule_time"] = f"{time_match.group(1)}:{time_match.group(2)}"
            elif time_match.group(3) and time_match.group(4):
                hour = int(time_match.group(3))
                if time_match.group(4) == "pm" and hour != 12:
                    hour += 12
                elif time_match.group(4) == "am" and hour == 12:
                    hour = 0
                params["schedule_time"] = f"{hour:02d}:00"
        
        # Extract routine name
        if "called" in message.lower():
            name_start = message.lower().find("called") + 6
            name_end = message.find(" ", name_start)
            if name_end == -1:
                name_end = len(message)
            params["routine_name"] = message[name_start:name_end].strip(' "\'')
        
        return params
    
    def _extract_activity_name(self, message: str) -> Dict[str, Any]:
        """Extract activity name from completion message."""
        # Look for common completion phrases
        completion_phrases = ["done with", "finished", "completed", "did"]
        
        for phrase in completion_phrases:
            if phrase in message.lower():
                start_idx = message.lower().find(phrase) + len(phrase)
                # Extract the activity name after the phrase
                activity_part = message[start_idx:].strip()
                if activity_part:
                    return {"activity_name": activity_part.split()[0]}
        
        # Fallback: try to extract meaningful words
        words = message.split()
        for word in words:
            if len(word) > 3 and word.lower() not in ["done", "finished", "completed"]:
                return {"activity_name": word}
        
        return {}
    
    def _extract_routine_name(self, message: str) -> Dict[str, Any]:
        """Extract routine name from start message."""
        # Look for routine identifiers
        words = message.split()
        for i, word in enumerate(words):
            if word.lower() in ["routine", "schedule"] and i > 0:
                return {"routine_name": words[i-1]}
        
        return {}
    
    async def handle_routine_request(self, intent_data: Dict[str, Any]) -> MCPToolResult:
        """Handle a routine-related request using MCP tools."""
        try:
            intent = intent_data["intent"]
            child_id = intent_data["child_id"]
            
            if intent == "create_routine":
                return await self._handle_create_routine(intent_data)
            elif intent == "get_routines":
                return await self._handle_get_routines(child_id)
            elif intent == "start_routine":
                return await self._handle_start_routine(intent_data)
            elif intent == "complete_activity":
                return await self._handle_complete_activity(intent_data)
            elif intent == "get_suggestions":
                return await self._handle_get_suggestions(intent_data)
            else:
                return MCPToolResult(
                    success=False,
                    content="🌈 I'm not sure how to help with that routine request. Can you try asking differently? ✨",
                    error="Unknown intent"
                )
                
        except Exception as e:
            logger.error(f"Error handling routine request: {str(e)}")
            return MCPToolResult(
                success=False,
                content="🌈 Something went colorfully wrong! Let's try again! ✨",
                error=str(e)
            )
    
    async def _handle_create_routine(self, intent_data: Dict[str, Any]) -> MCPToolResult:
        """Handle routine creation request."""
        try:
            # Prepare arguments for MCP tool
            args = {
                "child_id": intent_data["child_id"],
                "routine_name": intent_data.get("routine_name", "My New Routine"),
                "routine_type": intent_data.get("routine_type", "custom"),
                "schedule_time": intent_data.get("schedule_time", "09:00")
            }
            
            # If no routine name provided, ask for it
            if args["routine_name"] == "My New Routine":
                return MCPToolResult(
                    success=False,
                    content="🌈 I'd love to create a routine for you! What would you like to call your new routine? ✨"
                )
            
            # Call MCP tool
            result = await self.mcp_server._create_routine(args)
            
            return MCPToolResult(
                success=True,
                content=result.content[0].text if result.content else "Routine created!"
            )
            
        except Exception as e:
            return MCPToolResult(
                success=False,
                content="🌈 I had trouble creating your routine, but let's try again! ✨",
                error=str(e)
            )
    
    async def _handle_get_routines(self, child_id: int) -> MCPToolResult:
        """Handle get routines request."""
        try:
            args = {"child_id": child_id}
            result = await self.mcp_server._get_child_routines(args)
            
            return MCPToolResult(
                success=True,
                content=result.content[0].text if result.content else "No routines found."
            )
            
        except Exception as e:
            return MCPToolResult(
                success=False,
                content="🌈 Let me look for your routines! ✨",
                error=str(e)
            )
    
    async def _handle_start_routine(self, intent_data: Dict[str, Any]) -> MCPToolResult:
        """Handle start routine request."""
        try:
            child_id = intent_data["child_id"]
            
            # First get the child's routines to find the one to start
            routines_result = await self._handle_get_routines(child_id)
            
            # For now, start the first available routine
            # In a real implementation, you'd parse the routine name or ask the user
            args = {
                "child_id": child_id,
                "routine_id": 1  # This should be dynamically determined
            }
            
            result = await self.mcp_server._start_routine(args)
            
            return MCPToolResult(
                success=True,
                content=result.content[0].text if result.content else "Routine started!"
            )
            
        except Exception as e:
            return MCPToolResult(
                success=False,
                content="🌈 Let's start your routine adventure! ✨",
                error=str(e)
            )
    
    async def _handle_complete_activity(self, intent_data: Dict[str, Any]) -> MCPToolResult:
        """Handle activity completion request."""
        try:
            args = {
                "child_id": intent_data["child_id"],
                "routine_id": 1,  # This should be dynamically determined
                "activity_name": intent_data.get("activity_name", "activity")
            }
            
            result = await self.mcp_server._complete_activity(args)
            
            return MCPToolResult(
                success=True,
                content=result.content[0].text if result.content else "Great job!"
            )
            
        except Exception as e:
            return MCPToolResult(
                success=False,
                content="🌈 Wonderful job on your activity! ✨",
                error=str(e)
            )
    
    async def _handle_get_suggestions(self, intent_data: Dict[str, Any]) -> MCPToolResult:
        """Handle routine suggestions request."""
        try:
            from datetime import datetime
            current_time = datetime.now().strftime("%H:%M")
            
            args = {
                "child_id": intent_data["child_id"],
                "time_of_day": current_time,
                "child_mood": "neutral"
            }
            
            result = await self.mcp_server._get_routine_suggestions(args)
            
            return MCPToolResult(
                success=True,
                content=result.content[0].text if result.content else "Here are some activity ideas!"
            )
            
        except Exception as e:
            return MCPToolResult(
                success=False,
                content="🌈 Let me think of some colorful activities for you! ✨",
                error=str(e)
            )

# Global client instance
routine_mcp_client = None

def create_routine_mcp_client(routine_mcp_server) -> RoutineMCPClient:
    """Create and return the routine MCP client instance."""
    global routine_mcp_client
    routine_mcp_client = RoutineMCPClient(routine_mcp_server)
    return routine_mcp_client
