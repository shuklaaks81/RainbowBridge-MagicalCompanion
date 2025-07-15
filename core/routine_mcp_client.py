"""
MCP Client Integration for Rainbow Bridge AI Assistant

This module integrates MCP server functionality into the AI assistant,
allowing c            # Look for descriptive words before or after "routine"
            if before_routine and len(before_routine[-1]) > 2:
                params["routine_name"] = f"{before_routine[-1].title()} Routine"
            elif after_routine and len(after_routine[0]) > 2:
                params["routine_name"] = f"{after_routine[0].title()} Routine"
        
        return paramsased routine management.
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
    
    async def call_tool(self, tool_name: str, parameters: Dict[str, Any]) -> MCPToolResult:
        """Call an MCP tool with the given parameters."""
        try:
            if tool_name not in self.available_tools:
                return MCPToolResult(
                    success=False,
                    content="🌈 That's not something I can help with right now! ✨",
                    error=f"Tool {tool_name} not available"
                )
            
            # Route to appropriate handler
            return await self.handle_routine_request(parameters)
            
        except Exception as e:
            logger.error(f"Error calling tool {tool_name}: {str(e)}")
            return MCPToolResult(
                success=False,
                content="🌈 Something went colorfully wrong! Let's try again! ✨",
                error=str(e)
            )
    
    async def _get_current_activity_context(self, child_id: int) -> Optional[Dict[str, Any]]:
        """Get current activity context for enhanced communication."""
        try:
            from database.db_manager import DatabaseManager
            db = DatabaseManager()
            
            # Get active routine sessions
            active_sessions = await db.get_active_routine_sessions(child_id)
            if not active_sessions:
                return None
            
            # Get the most recent active routine
            routine_id = active_sessions[0]['routine_id']
            routine_name = active_sessions[0].get('routine_name', 'your routine')
            
            # Get routine details to find current activity
            routine_data = await db.get_routine(routine_id)
            if not routine_data:
                return None
            
            activities = routine_data.get("activities", [])
            total_activities = len(activities)
            completed_count = sum(1 for activity in activities if activity.get("completed", False))
            progress_percentage = round((completed_count / total_activities) * 100) if total_activities > 0 else 0
            
            # Find current activity (first incomplete one)
            current_activity = None
            next_activity = None
            current_activity_index = None
            
            for i, activity in enumerate(activities):
                if not activity.get("completed", False):
                    current_activity = activity
                    current_activity_index = i
                    # Get next activity if available
                    if i + 1 < len(activities):
                        next_activity = activities[i + 1]
                    break
            
            return {
                "routine_id": routine_id,
                "routine_name": routine_name,
                "current_activity": current_activity,
                "current_activity_index": current_activity_index,
                "next_activity": next_activity,
                "total_activities": total_activities,
                "completed_count": completed_count,
                "progress_percentage": progress_percentage,
                "remaining_activities": total_activities - completed_count
            }
            
        except Exception as e:
            logger.error(f"Failed to get current activity context: {e}")
            return None
    
    async def detect_routine_intent(self, message: str, child_id: int) -> Optional[Dict[str, Any]]:
        """Detect if a message contains routine-related intent."""
        message_lower = message.lower()
        logger.info(f"DEBUG: Analyzing message for routine intent: '{message}' (child_id: {child_id})")
        
        # Check for active sessions first
        active_sessions = await self._get_active_sessions(child_id)
        has_active_sessions = len(active_sessions) > 0
        logger.info(f"DEBUG: Active sessions found: {len(active_sessions)}")
        
        # Enhanced intent patterns for routine management with AI suggestions
        intent_patterns = {
            "create_routine": [
                "create routine", "new routine", "make routine", 
                "add routine", "schedule", "plan activities", "want to create",
                "help me make", "need a routine", "set up routine", "build routine",
                "create schedule", "make schedule", "plan my day", "organize activities"
            ],
            "get_routines": [
                "my routines", "show routines", "what routines", "list routines",
                "see my schedule", "what activities", "show my schedule"
            ],
            "start_routine": [
                "start routine", "begin routine", "do routine", "time for routine",
                "ready for routine", "let's start routine", "begin my routine",
                "start my", "begin my", "do my", "time for my", "ready for my",
                "morning routine", "evening routine", "bedtime routine", "homework routine"
            ],
            "complete_activity": [
                # Traditional completion phrases
                "done", "finished", "completed", "did it", "finished with",
                "I'm done", "just finished", "complete", "mark done",
                "activity done", "task done", "step done",
                
                # Natural general phrases special kids use
                "I woke up", "woke up", "got up", "wake up",
                "I got dressed", "got dressed", "put on clothes", "clothes on",
                "I ate", "ate breakfast", "ate lunch", "ate dinner", "eating",
                "I brushed", "brushed teeth", "teeth clean", "teeth brushed",
                "I washed", "washed hands", "hands clean", "washed face",
                "I took a bath", "bath time", "took bath", "had a bath",
                "I put on", "shoes on", "put shoes", "wearing shoes",
                "I read", "reading done", "book finished", "story done",
                "I played", "playing done", "game over", "finished playing",
                "I did homework", "homework done", "school work done",
                "I cleaned", "room clean", "toys away", "cleaned up",
                "I went to bed", "bedtime", "in bed", "sleeping time",
                
                # Simple action statements
                "teeth", "hands", "face", "shoes", "clothes", "breakfast", 
                "lunch", "dinner", "bath", "shower", "book", "homework",
                "toys", "bed", "sleep",
                
                # Present tense (happening now)
                "doing", "working on", "at", "with",
                
                # Past simple forms
                "went", "had", "took", "made", "came", "saw",
                
                # Child-friendly expressions
                "all clean", "all done", "ready", "good", "finished that",
                "that's done", "yay", "hooray", "I did good"
            ],
            "get_suggestions": [
                "what should i do", "activity ideas", "suggest", "what activities",
                "help me choose", "what's next", "what can i do", "suggest activities",
                "recommend", "ideas for", "activities for", "help me find"
            ],
            "smart_schedule": [
                "plan my morning", "plan my evening", "plan my day", "what should I do today",
                "help me organize", "create my schedule", "best activities for me",
                "activities for today", "what's good for", "schedule suggestions",
                "auto create", "smart routine", "ai suggestions", "best routine"
            ]
        }
        
        # If there are active sessions, prioritize activity completion over routine creation
        detected_intent = None  # Initialize variable
        
        if has_active_sessions:
            # Look for activity completion patterns first
            for pattern in intent_patterns["complete_activity"]:
                if pattern in message_lower:
                    intent_data = {
                        "intent": "complete_activity",
                        "confidence": 0.9,
                        "child_id": child_id,
                        "message": message,
                        "active_sessions": active_sessions
                    }
                    intent_data.update(self._extract_activity_name(message))
                    return intent_data
            
            # Check for explicit routine creation even with active sessions
            for pattern in intent_patterns["create_routine"]:
                if pattern in message_lower:
                    logger.info(f"DEBUG: Matched routine creation pattern '{pattern}' even with active sessions")
                    detected_intent = "create_routine"
                    break
            
            # Check if they're trying to start another routine
            if not detected_intent and any(pattern in message_lower for pattern in ["start", "begin"]):
                # This might be starting a new routine or continuing current one
                detected_intent = "start_routine"
            elif not detected_intent:
                # Default to activity completion context when sessions are active and no other intent found
                detected_intent = "complete_activity"
                intent_data = {
                    "intent": detected_intent,
                    "confidence": 0.7,
                    "child_id": child_id,
                    "message": message,
                    "active_sessions": active_sessions
                }
                intent_data.update(self._extract_activity_name(message))
                return intent_data
        
        # Continue with normal intent detection if not already detected
        if not detected_intent:
            # First, try exact phrase matching
            for intent, patterns in intent_patterns.items():
                for pattern in patterns:
                    if pattern in message_lower:
                        detected_intent = intent
                        logger.info(f"DEBUG: Matched pattern '{pattern}' for intent '{intent}'")
                        break
                if detected_intent:
                    break
            
            # If no exact match, try more flexible word-based matching for routine intents
            if not detected_intent:
                words = message_lower.split()
                
                # Check for routine starting keywords
                start_words = ["start", "begin", "do", "time"]
                routine_words = ["routine", "morning", "evening", "bedtime", "homework"]
                
                if any(start_word in words for start_word in start_words) and any(routine_word in words for routine_word in routine_words):
                    detected_intent = "start_routine"
                    logger.info(f"DEBUG: Matched flexible start routine pattern for: '{message}'")
                
                # Check for activity completion keywords
                completion_words = ["done", "finished", "completed", "did", "complete"]
                activity_words = ["activity", "task", "step", "it"]
                
                if any(comp_word in words for comp_word in completion_words):
                    if any(act_word in words for act_word in activity_words) or len(words) <= 3:
                        detected_intent = "complete_activity"
                        logger.info(f"DEBUG: Matched flexible completion pattern for: '{message}'")
                
                # Check for routine creation keywords
                create_words = ["create", "make", "new", "add", "build"]
                if any(create_word in words for create_word in create_words) and any(routine_word in words for routine_word in routine_words):
                    detected_intent = "create_routine"
                    logger.info(f"DEBUG: Matched flexible creation pattern for: '{message}'")
        
        if not detected_intent:
            logger.info(f"DEBUG: No intent patterns matched for message: '{message}'")
            return None
        
        # Extract parameters based on intent
        intent_data = {
            "intent": detected_intent,
            "confidence": 0.8,
            "child_id": child_id,
            "message": message,
            "active_sessions": active_sessions if has_active_sessions else []
        }
        
        # Add current activity context for enhanced communication
        current_context = await self._get_current_activity_context(child_id)
        if current_context:
            intent_data["current_activity_context"] = current_context
        
        # Extract specific parameters
        if detected_intent == "create_routine":
            intent_data.update(self._extract_create_routine_params(message))
        elif detected_intent == "complete_activity":
            intent_data.update(self._extract_activity_name(message))
        elif detected_intent == "start_routine":
            intent_data.update(self._extract_routine_name(message))
        elif detected_intent == "smart_schedule":
            intent_data.update(self._extract_smart_schedule_params(message))
        
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
        time_pattern = r'(\d{1,2}):(\d{2})|(\d{1,2})\s*(am|pm|AM|PM)'
        time_match = re.search(time_pattern, message.lower())
        if time_match:
            if time_match.group(1) and time_match.group(2):
                # Format: HH:MM
                hour = int(time_match.group(1))
                minute = int(time_match.group(2))
                params["schedule_time"] = f"{hour:02d}:{minute:02d}"
            elif time_match.group(3) and time_match.group(4):
                # Format: H am/pm
                hour = int(time_match.group(3))
                period = time_match.group(4).lower()
                if period == "pm" and hour != 12:
                    hour += 12
                elif period == "am" and hour == 12:
                    hour = 0
                params["schedule_time"] = f"{hour:02d}:00"
        
        # Extract routine name
        import re
        
        # Look for quoted routine names
        quote_pattern = r'["\']([^"\']+)["\']'
        quote_match = re.search(quote_pattern, message)
        if quote_match:
            params["routine_name"] = quote_match.group(1)
        elif "called" in message.lower():
            # Original "called" extraction
            name_start = message.lower().find("called") + 6
            name_end = message.find(" ", name_start)
            if name_end == -1:
                name_end = len(message)
            params["routine_name"] = message[name_start:name_end].strip(' "\'')
        elif "routine" in message.lower():
            # Try to extract words before or after "routine"
            routine_idx = message.lower().find("routine")
            before_routine = message[:routine_idx].strip().split()
            after_routine = message[routine_idx + 7:].strip().split()
            
            # Look for descriptive words before "routine"
            if before_routine and len(before_routine[-1]) > 2:
                params["routine_name"] = f"{before_routine[-1].title()} Routine"
            elif after_routine and len(after_routine[0]) > 2:
                params["routine_name"] = f"{after_routine[0].title()} Routine"
        
        return params
    
    def _extract_activity_name(self, message: str) -> Dict[str, Any]:
        """Extract activity name from completion message using intelligent mapping for special kids."""
        message_lower = message.lower().strip()
        
        # Enhanced activity mapping for natural phrases special kids use
        activity_mappings = {
            # Morning routine activities
            "wake up": ["woke up", "wake up", "got up", "getting up", "awake", "morning"],
            "brush teeth": ["brush", "brushing", "teeth", "brushed teeth", "brushed", "tooth", "toothbrush", "clean teeth"],
            "wash face": ["wash face", "washed face", "washing face", "face clean", "clean face", "face", "wash"],
            "wash hands": ["wash hands", "washed hands", "washing hands", "hands clean", "clean hands", "hands"],
            "get dressed": ["got dressed", "get dressed", "getting dressed", "put on clothes", "clothes on", "dressed", "dress", "dressing", "clothes"],
            "eat breakfast": ["ate breakfast", "eat breakfast", "eating breakfast", "breakfast", "morning food", "ate", "food"],
            "take shower": ["took shower", "take shower", "taking shower", "shower", "showered", "bath", "bathing", "took bath"],
            
            # Daily activities
            "do homework": ["did homework", "do homework", "doing homework", "homework", "school work", "study", "studying", "read", "reading"],
            "play": ["played", "play", "playing", "game", "games", "fun", "toy", "toys"],
            "clean room": ["cleaned room", "clean room", "cleaning room", "room clean", "tidy", "tidying", "cleanup", "clean up"],
            "eat lunch": ["ate lunch", "eat lunch", "eating lunch", "lunch", "lunch time", "noon food"],
            "eat dinner": ["ate dinner", "eat dinner", "eating dinner", "dinner", "dinner time", "evening food", "supper"],
            "take medicine": ["took medicine", "take medicine", "taking medicine", "medicine", "medication", "pills", "vitamin"],
            
            # Evening routine activities
            "put on pajamas": ["put on pajamas", "pajamas on", "pjs", "nightclothes", "sleeping clothes", "bedtime clothes"],
            "read book": ["read book", "reading book", "read", "book", "story", "story time", "reading time"],
            "go to bed": ["went to bed", "go to bed", "going to bed", "bed", "bedtime", "sleep", "sleeping", "sleepy"],
            
            # Personal care
            "comb hair": ["combed hair", "comb hair", "combing hair", "hair", "brush hair", "fix hair"],
            "put on shoes": ["put on shoes", "shoes on", "wearing shoes", "shoes", "socks", "socks on"],
            "use bathroom": ["used bathroom", "use bathroom", "bathroom", "potty", "toilet", "pee", "poop"],
            
            # Learning activities
            "practice writing": ["practiced writing", "practice writing", "writing", "write", "wrote", "letters", "words"],
            "do math": ["did math", "do math", "doing math", "math", "numbers", "counting", "count"],
            "art time": ["did art", "do art", "art", "drawing", "draw", "coloring", "color", "paint", "painting"],
            "music time": ["music", "singing", "sing", "song", "dance", "dancing", "listen", "listening"],
            
            # Physical activities
            "exercise": ["exercised", "exercise", "exercising", "workout", "move", "moving", "walk", "walking"],
            "go outside": ["went outside", "go outside", "going outside", "outside", "park", "playground", "fresh air"],
            
            # Chores and responsibilities
            "feed pet": ["fed pet", "feed pet", "feeding pet", "dog", "cat", "fish", "pet", "animal"],
            "water plants": ["watered plants", "water plants", "watering plants", "plants", "flowers", "garden"],
            "help cook": ["helped cook", "help cook", "helping cook", "cooking", "cook", "kitchen", "recipe"],
            
            # Social activities
            "call family": ["called family", "call family", "calling family", "phone", "video call", "talk", "family"],
            "play with friends": ["played with friends", "play with friends", "friends", "friend", "social", "together"],
            
            # Self-care and calming
            "deep breathing": ["deep breathing", "breathing", "breathe", "calm", "relax", "meditation"],
            "quiet time": ["quiet time", "quiet", "rest", "resting", "peaceful", "still", "calm down"],
            "sensory break": ["sensory break", "break", "overwhelmed", "too much", "need space", "alone time"]
        }
        
        # First, try exact phrase matching
        for activity, phrases in activity_mappings.items():
            for phrase in phrases:
                if phrase in message_lower:
                    return {"activity_name": activity}
        
        # Then try word-based matching for more flexible recognition
        words = message_lower.split()
        for activity, phrases in activity_mappings.items():
            for phrase in phrases:
                phrase_words = phrase.split()
                # Check if all words from the phrase appear in the message
                if len(phrase_words) == 1:
                    if phrase_words[0] in words:
                        return {"activity_name": activity}
                elif len(phrase_words) == 2:
                    if all(word in message_lower for word in phrase_words):
                        return {"activity_name": activity}
        
        # Fallback: Look for any completion patterns and extract what follows
        completion_patterns = [
            ("done with", 9),
            ("finished with", 13),
            ("completed", 9),
            ("did", 3),
            ("done", 4),
            ("finished", 8)
        ]
        
        for pattern, pattern_len in completion_patterns:
            if pattern in message_lower:
                # Find the phrase position
                phrase_start = message_lower.find(pattern)
                phrase_end = phrase_start + pattern_len
                
                # Extract everything after the phrase
                after_phrase = message[phrase_end:].strip()
                
                # Clean up the activity name
                if after_phrase:
                    # Remove common words and punctuation
                    activity_name = after_phrase.replace("the", "").replace("my", "").strip()
                    activity_name = activity_name.split('.')[0].split('!')[0].split('?')[0].split(',')[0]
                    activity_name = activity_name.strip()
                    
                    # Only accept if it looks like a real activity
                    if activity_name and len(activity_name) > 2:
                        # Check if it's a meaningful activity word
                        activity_clean = activity_name.lower()
                        skip_words = ["sure", "that", "this", "well", "good", "okay", "yes", "now", "just", "really"]
                        if activity_clean not in skip_words:
                            return {"activity_name": activity_name}
        
        # If no specific activity found, but message indicates completion, return the whole message as context
        completion_indicators = ["done", "finished", "completed", "did", "good", "ready", "all clean"]
        if any(indicator in message_lower for indicator in completion_indicators):
            return {"activity_name": message.strip(), "general_completion": True}
        
        return {}
    
    def _extract_routine_name(self, message: str) -> Dict[str, Any]:
        """Extract routine name from start message."""
        # Look for routine identifiers
        words = message.split()
        for i, word in enumerate(words):
            if word.lower() in ["routine", "schedule"] and i > 0:
                return {"routine_name": words[i-1]}
        
        # Also look for "my" followed by words before "routine"
        if "my" in message.lower():
            my_index = -1
            for i, word in enumerate(words):
                if word.lower() == "my":
                    my_index = i
                    break
            
            if my_index >= 0 and my_index + 1 < len(words):
                # Extract everything between "my" and potentially "routine"
                routine_words = []
                for j in range(my_index + 1, len(words)):
                    if words[j].lower() in ["routine", "schedule"]:
                        break
                    routine_words.append(words[j])
                
                if routine_words:
                    return {"routine_name": " ".join(routine_words)}
        
        return {}
    
    def _extract_smart_schedule_params(self, message: str) -> Dict[str, Any]:
        """Extract parameters for smart schedule generation."""
        import re
        from datetime import datetime
        
        params = {}
        message_lower = message.lower()
        
        # Extract time of day
        time_of_day = "any"
        if any(word in message_lower for word in ["morning", "am", "breakfast"]):
            time_of_day = "morning"
        elif any(word in message_lower for word in ["afternoon", "lunch", "midday"]):
            time_of_day = "afternoon"  
        elif any(word in message_lower for word in ["evening", "dinner", "night", "pm"]):
            time_of_day = "evening"
        elif any(word in message_lower for word in ["bedtime", "sleep", "before bed"]):
            time_of_day = "bedtime"
        
        params["time_of_day"] = time_of_day
        
        # Extract activity preferences
        activity_preferences = []
        if any(word in message_lower for word in ["calm", "quiet", "relax", "peaceful"]):
            activity_preferences.append("calming")
        if any(word in message_lower for word in ["active", "movement", "exercise", "play"]):
            activity_preferences.append("active")
        if any(word in message_lower for word in ["learning", "educational", "study", "practice"]):
            activity_preferences.append("educational")
        if any(word in message_lower for word in ["creative", "art", "draw", "make"]):
            activity_preferences.append("creative")
        if any(word in message_lower for word in ["sensory", "texture", "feel", "touch"]):
            activity_preferences.append("sensory")
        
        params["activity_preferences"] = activity_preferences
        
        # Extract duration preferences
        duration = "medium"  # default
        if any(word in message_lower for word in ["quick", "short", "brief", "few minutes"]):
            duration = "short"
        elif any(word in message_lower for word in ["long", "extended", "detailed", "thorough"]):
            duration = "long"
        
        params["duration"] = duration
        
        # Extract mood/energy level
        energy_level = "medium"
        if any(word in message_lower for word in ["tired", "low energy", "exhausted", "sleepy"]):
            energy_level = "low"
        elif any(word in message_lower for word in ["energetic", "excited", "active", "high energy"]):
            energy_level = "high"
        
        params["energy_level"] = energy_level
        
        # Extract specific activity mentions
        mentioned_activities = []
        activity_keywords = [
            "breakfast", "lunch", "dinner", "snack", "eating",
            "brush teeth", "shower", "bath", "wash hands",
            "homework", "reading", "study", "practice",
            "play", "games", "toys", "outside",
            "music", "dance", "sing", "instruments",
            "art", "draw", "color", "paint", "craft",
            "exercise", "walk", "stretch", "yoga"
        ]
        
        for activity in activity_keywords:
            if activity in message_lower:
                mentioned_activities.append(activity)
        
        params["mentioned_activities"] = mentioned_activities
        
        return params
    
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
            elif intent == "smart_schedule":
                return await self._handle_smart_schedule(intent_data)
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
            routine_name = intent_data.get("routine_name")
            
            # First get the child's routines to find the one to start
            routines_result = await self._handle_get_routines(child_id)
            
            if not routines_result.success:
                return MCPToolResult(
                    success=False,
                    content="🌈 I couldn't find your routines. Let's create one first! ✨",
                    error="Failed to get routines"
                )
            
            # Parse the routines from the result to find matching routine
            routine_id = None
            
            if routine_name:
                # Try to find routine by name (case-insensitive partial match)
                routine_name_lower = routine_name.lower()
                
                # Get the routines list through MCP server
                try:
                    routines_args = {"child_id": child_id}
                    routines_mcp_result = await self.mcp_server._get_child_routines(routines_args)
                    
                    if routines_mcp_result.content:
                        # Parse the routine data to find matching routine
                        import json
                        try:
                            routines_data = json.loads(routines_mcp_result.content[0].text)
                            routines = routines_data.get("routines", [])
                            
                            for routine in routines:
                                if routine_name_lower in routine.get("name", "").lower():
                                    routine_id = routine.get("id")
                                    break
                        except (json.JSONDecodeError, KeyError, IndexError):
                            # If parsing fails, try a simple approach
                            pass
                except:
                    pass
            
            # Default to active routine if no specific routine found
            if routine_id is None:
                # Try to get active routine from sessions
                try:
                    from database.db_manager import DatabaseManager
                    db = DatabaseManager()
                    active_sessions = await db.get_active_routine_sessions(child_id)
                    if active_sessions:
                        # Use the most recently started active session
                        routine_id = active_sessions[0]['routine_id']
                        print(f"DEBUG: Using active routine ID {routine_id} for completion")
                    else:
                        print(f"WARNING: No active routine sessions found for child {child_id}")
                        routine_id = None  # Don't default to routine 1
                except Exception as e:
                    print(f"ERROR: Failed to get active sessions: {e}")
                    routine_id = None
                
            args = {
                "child_id": child_id,
                "routine_id": routine_id
            }
            
            result = await self.mcp_server._start_routine(args)
            
            return MCPToolResult(
                success=True,
                content=result.content[0].text if result.content else "Routine started!"
            )
            
        except Exception as e:
            logger.error(f"Error starting routine: {str(e)}")
            return MCPToolResult(
                success=False,
                content="🌈 Let's start your routine adventure! ✨",
                error=str(e)
            )
    
    async def _handle_complete_activity(self, intent_data: Dict[str, Any]) -> MCPToolResult:
        """Handle activity completion request."""
        try:
            child_id = intent_data["child_id"]
            activity_name = intent_data.get("activity_name")
            
            if not activity_name:
                return MCPToolResult(
                    success=False,
                    content="🌈 I'm not sure which activity you completed. Can you tell me more specifically? ✨",
                    error="No activity name provided"
                )
            
            # Get active routine from sessions
            routine_id = None
            try:
                from database.db_manager import DatabaseManager
                db = DatabaseManager()
                active_sessions = await db.get_active_routine_sessions(child_id)
                if active_sessions:
                    routine_id = active_sessions[0]['routine_id']
                    print(f"DEBUG: Using active routine ID {routine_id} for activity completion")
                else:
                    return MCPToolResult(
                        success=False,
                        content="🌈 It looks like you don't have an active routine right now. Would you like to start one? ✨",
                        error="No active routine found"
                    )
            except Exception as e:
                print(f"ERROR: Failed to get active routine: {e}")
                return MCPToolResult(
                    success=False,
                    content="🌈 Let me help you with your routine! ✨",
                    error=f"Database error: {e}"
                )
            
            args = {
                "child_id": child_id,
                "routine_id": routine_id,
                "activity_name": activity_name
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
    
    async def _handle_smart_schedule(self, intent_data: Dict[str, Any]) -> MCPToolResult:
        """Handle smart schedule generation request using AI."""
        try:
            child_id = intent_data["child_id"]
            message = intent_data["message"]
            
            # Extract smart schedule parameters
            time_of_day = intent_data.get("time_of_day", "any")
            activity_preferences = intent_data.get("activity_preferences", [])
            duration = intent_data.get("duration", "medium")
            energy_level = intent_data.get("energy_level", "medium")
            mentioned_activities = intent_data.get("mentioned_activities", [])
            
            # Get child's existing routines for context
            from database.db_manager import DatabaseManager
            db = DatabaseManager()
            existing_routines = await db.get_child_routines(child_id)
            
            # Create AI prompt for smart schedule generation
            ai_prompt = self._create_smart_schedule_prompt(
                time_of_day, activity_preferences, duration, 
                energy_level, mentioned_activities, existing_routines, message
            )
            
            # Generate AI suggestions using the assistant's AI client
            from core.ai_assistant import SpecialKidsAI
            
            # Create a temporary AI instance to generate suggestions
            ai_assistant = SpecialKidsAI()
            
            # Generate smart activity suggestions
            ai_response = await ai_assistant._use_openai(ai_prompt, ai_assistant.system_prompt)
            
            # Parse and format the AI response
            formatted_response = self._format_smart_schedule_response(ai_response, time_of_day)
            
            return MCPToolResult(
                success=True,
                content=formatted_response
            )
            
        except Exception as e:
            logger.error(f"Smart schedule generation error: {str(e)}")
            return MCPToolResult(
                success=False,
                content="🌈 Let me create a magical schedule for you! I'll suggest some wonderful activities based on what you like! ✨",
                error=str(e)
            )
    
    def _create_smart_schedule_prompt(self, time_of_day: str, preferences: List[str], 
                                    duration: str, energy_level: str, mentioned_activities: List[str],
                                    existing_routines: List, original_message: str) -> str:
        """Create an AI prompt for smart schedule generation."""
        
        prompt = f"""
        Create a personalized daily schedule for an autistic child based on these preferences:
        
        Original request: "{original_message}"
        Time of day: {time_of_day}
        Activity preferences: {', '.join(preferences) if preferences else 'balanced mix'}
        Duration preference: {duration}
        Energy level: {energy_level}
        Mentioned activities: {', '.join(mentioned_activities) if mentioned_activities else 'none specified'}
        
        Consider these guidelines for autistic children:
        - Predictable, structured routines
        - Clear transitions between activities
        - Sensory-friendly activities
        - Visual supports and clear instructions
        - Balance of preferred and new activities
        - Calming activities for regulation
        
        Create 4-6 activities with:
        1. Activity name
        2. Duration (5-30 minutes based on preference)
        3. Simple description
        4. Why it's good for this time/preference
        
        Format as a friendly, encouraging response from Rainbow Bridge.
        """
        
        return prompt
    
    def _format_smart_schedule_response(self, ai_response: str, time_of_day: str) -> str:
        """Format the AI response into a structured, child-friendly format."""
        
        # Add Rainbow Bridge personality and visual elements
        formatted = f"🌈✨ Here's your magical {time_of_day} schedule, created just for you! ✨🌈\n\n"
        formatted += ai_response
        formatted += f"\n\n🌟 Remember, you can always adjust these activities to make them perfect for you! 🌟"
        formatted += f"\n💫 Would you like me to create a routine with these activities? 💫"
        
        return formatted
    
    async def _get_active_sessions(self, child_id: int) -> List[Dict]:
        """Get active routine sessions for a child."""
        try:
            # Use raw SQL to get active sessions
            import aiosqlite
            async with aiosqlite.connect("special_kids.db") as db:
                db.row_factory = aiosqlite.Row
                cursor = await db.execute("""
                    SELECT rs.*, r.name as routine_name 
                    FROM routine_sessions rs
                    JOIN routines r ON rs.routine_id = r.id
                    WHERE rs.child_id = ? AND rs.status = 'in_progress'
                    ORDER BY rs.started_at DESC
                """, (child_id,))
                
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
                
        except Exception as e:
            logger.error(f"Failed to get active sessions: {str(e)}")
            return []

# Global client instance
routine_mcp_client = None

def create_routine_mcp_client(routine_mcp_server) -> RoutineMCPClient:
    """Create and return the routine MCP client instance."""
    global routine_mcp_client
    routine_mcp_client = RoutineMCPClient(routine_mcp_server)
    return routine_mcp_client
