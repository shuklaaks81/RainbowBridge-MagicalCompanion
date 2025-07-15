"""
AI Assistant for Special Kids - Core AI Processing Module

This module handles all AI interactions using OpenAI's GPT-4 model,
specifically configured for autism spectrum communication patterns.
"""

import os
import openai
import json
import random
import re
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from .local_llm import LocalLLMManager, LocalLLMResponse

# Azure OpenAI imports
try:
    from openai import AzureOpenAI
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False
    AzureOpenAI = None

# MCP Client import
try:
    from .routine_mcp_client import RoutineMCPClient, create_routine_mcp_client
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    RoutineMCPClient = None

logger = logging.getLogger(__name__)

@dataclass
class AIResponse:
    """Structure for AI response data."""
    text: str
    visual_cues: List[str]
    emotion: str
    confidence: float
    suggested_actions: List[str]

class SpecialKidsAI:
    """AI Assistant specialized for autistic children communication."""
    
    def __init__(self, routine_mcp_server=None):
        # Initialize local LLM manager
        self.local_llm = LocalLLMManager()
        self.use_local_mode = os.getenv("LOCAL_MODE", "False").lower() == "true"
        
        # Initialize MCP client for routine management
        self.routine_mcp_client = None
        if routine_mcp_server and MCP_AVAILABLE:
            self.routine_mcp_client = create_routine_mcp_client(routine_mcp_server)
            logger.info("MCP client for routines initialized successfully")
        
        # Initialize AI client (Azure OpenAI or OpenAI)
        self.client = None
        self.use_azure = os.getenv("USE_AZURE_OPENAI", "False").lower() == "true"
        
        if self.use_azure and AZURE_AVAILABLE:
            # Initialize Azure OpenAI client
            try:
                # Use your preferred variable names
                subscription_key = os.getenv("AZURE_OPENAI_API_KEY")
                endpoint = os.getenv("ENDPOINT_URL")
                deployment = os.getenv("DEPLOYMENT_NAME")
                azure_api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
                
                if subscription_key and endpoint and deployment:
                    self.client = AzureOpenAI(
                        api_key=subscription_key,
                        azure_endpoint=endpoint,
                        api_version=azure_api_version
                    )
                    self.deployment_name = deployment
                    logger.info(f"Azure OpenAI client initialized successfully with endpoint: {endpoint}")
                    logger.info(f"Using deployment: {deployment}")
                else:
                    logger.warning(f"Azure OpenAI credentials incomplete - key: {'✓' if subscription_key else '✗'}, endpoint: {'✓' if endpoint else '✗'}, deployment: {'✓' if deployment else '✗'}")
            except Exception as e:
                logger.warning(f"Failed to initialize Azure OpenAI client: {e}")
        else:
            # Initialize standard OpenAI client (fallback)
            openai_api_key = os.getenv("OPENAI_API_KEY")
            
            if openai_api_key and openai_api_key != "your_openai_api_key_here":
                try:
                    self.client = openai.OpenAI(api_key=openai_api_key)
                    logger.info("Standard OpenAI client initialized successfully")
                except Exception as e:
                    logger.warning(f"Failed to initialize OpenAI client: {e}")
        
        if not self.use_local_mode and not self.client:
            logger.warning("Neither local LLM nor cloud AI is available. Some features may not work.")
        
        self.model = os.getenv("MODEL_NAME", "gpt-4")
        self.max_tokens = int(os.getenv("MAX_TOKENS", "150"))
        self.temperature = float(os.getenv("TEMPERATURE", "0.7"))
        
        # System prompt optimized for autism spectrum communication
        self.system_prompt = """
        You are Rainbow Bridge, a magical and colorful companion for children with communication adventures.
        
        RAINBOW BRIDGE PERSONALITY:
        - You are warm, encouraging, and full of colorful energy
        - You speak in a friendly, magical way that makes communication fun
        - You celebrate every small step like it's a wonderful achievement
        - You use colorful metaphors and gentle, playful language
        - You are patient and understanding, never rushing or pressuring
        
        COMMUNICATION GUIDELINES:
        - Use simple, clear language with short sentences
        - Be patient, encouraging, and consistent
        - Make communication feel like a fun adventure or game
        - Use positive reinforcement and celebrate small achievements
        - Support visual and non-verbal communication
        - Create a magical, safe space for expression
        
        RESPONSE STYLE:
        - Keep responses brief and focused
        - Use encouraging, magical tone
        - Suggest colorful visual aids when helpful
        - Provide routine-based guidance like a friendly guide
        - Include sensory considerations with gentleness
        
        EMOTIONAL SUPPORT:
        - Recognize and validate emotions like a caring friend
        - Provide comfort during difficult moments
        - Use calming, colorful language during stress
        - Celebrate progress and effort with rainbow enthusiasm
        
        Always respond as Rainbow Bridge - a magical companion that makes communication feel like a colorful adventure full of possibilities.
        """
    
    async def process_message(
        self,
        message: str,
        child_id: int,
        communication_type: str = "text",
        child_preferences: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Process a message from a child and generate an appropriate response.
        
        Args:
            message: The child's input message
            child_id: Unique identifier for the child
            communication_type: Type of communication (text, image, audio)
            child_preferences: Child's communication preferences and settings
        
        Returns:
            Dict containing AI response with text, visual cues, and actions
        """
        try:
            # Customize prompt based on child preferences
            customized_prompt = self._customize_prompt(child_preferences)
            
            # Process different communication types
            if communication_type == "image":
                return await self._process_image_message(message, child_id, customized_prompt)
            elif communication_type == "audio":
                return await self._process_audio_message(message, child_id, customized_prompt)
            else:
                return await self._process_text_message(message, child_id, customized_prompt)
        
        except Exception as e:
            logger.error(f"AI processing error: {str(e)}")
            return self._get_fallback_response()
    
    def _customize_prompt(self, child_preferences: Optional[Dict]) -> str:
        """Customize the system prompt based on child preferences."""
        prompt = self.system_prompt
        
        if child_preferences:
            # Add specific instructions based on child's needs
            if child_preferences.get("visual_support", True):
                prompt += "\n- Always suggest visual aids and symbols to support understanding"
            
            if child_preferences.get("routine_focus", True):
                prompt += "\n- Relate responses to daily routines and familiar activities"
            
            if child_preferences.get("sensory_sensitive", False):
                prompt += "\n- Be extra mindful of sensory sensitivities in suggestions"
            
            interests = child_preferences.get("interests", [])
            if interests:
                prompt += f"\n- Incorporate these interests when possible: {', '.join(interests)}"
        
        return prompt
    
    async def _process_text_message(
        self,
        message: str,
        child_id: int,
        system_prompt: str
    ) -> Dict[str, Any]:
        """Process text-based communication using local or cloud LLM."""
        try:
            # Get current activity context first to enhance all communications
            current_activity_context = None
            if self.routine_mcp_client:
                current_activity_context = await self.routine_mcp_client._get_current_activity_context(child_id)
            
            # First check if this is a routine-related request
            if self.routine_mcp_client:
                logger.info(f"Checking routine intent for message: '{message}' (child_id: {child_id})")
                routine_intent = await self.routine_mcp_client.detect_routine_intent(message, child_id)
                if routine_intent:
                    logger.info(f"Detected routine intent: {routine_intent['intent']}")
                    mcp_result = await self.routine_mcp_client.handle_routine_request(routine_intent)
                    
                    if mcp_result.success:
                        # Return MCP response with routine-specific visual cues
                        return {
                            "text": mcp_result.content,
                            "visual_cues": self._get_routine_visual_cues(routine_intent["intent"]),
                            "emotion": "encouraging",
                            "confidence": 0.95,
                            "suggested_actions": self._get_routine_actions(routine_intent["intent"]),
                            "communication_type": "text",
                            "llm_source": "mcp_routine",
                            "routine_action": routine_intent["intent"],
                            "current_activity_context": current_activity_context
                        }
                else:
                    logger.info(f"No routine intent detected for: '{message}'")
            
            # Check for broader communication intents if no routine intent found
            communication_intent = await self._detect_communication_intent(message, child_id)
            if communication_intent:
                logger.info(f"Detected communication intent: {communication_intent['primary_intent']['intent']}")
                intent_response = await self._generate_intent_based_response(communication_intent, message, current_activity_context)
                return intent_response
            
            ai_text = ""
            
            # Try local LLM first if enabled
            if self.use_local_mode:
                local_response = await self.local_llm.generate_response(
                    prompt=message,
                    system_prompt=system_prompt,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature
                )
                
                if local_response.success:
                    ai_text = local_response.text
                    logger.info(f"Used local LLM: {local_response.model} (processing time: {local_response.processing_time:.2f}s)")
                else:
                    logger.warning(f"Local LLM failed: {local_response.error}")
                    # Fall back to OpenAI if available and enabled
                    if self.client and os.getenv("FALLBACK_TO_OPENAI", "True").lower() == "true":
                        ai_text = await self._use_openai(message, system_prompt)
                    else:
                        return self._get_fallback_response("Local LLM unavailable and no fallback configured")
            else:
                # Use OpenAI directly
                if self.client:
                    ai_text = await self._use_openai(message, system_prompt)
                else:
                    return self._get_fallback_response("No LLM provider available")
            
            # Analyze the response for additional context
            emotion = self._detect_emotion(ai_text)
            visual_cues = self._suggest_visual_cues(message, ai_text)
            actions = self._suggest_actions(message, ai_text)
            
            # Add current activity context to the response if available
            if current_activity_context and current_activity_context.get("current_activity"):
                current_activity = current_activity_context["current_activity"]
                routine_name = current_activity_context.get("routine_name", "your routine")
                progress = current_activity_context.get("progress_percentage", 0)
                
                # Enhance AI response with current activity information
                activity_context = f"\n\n🎯 **Current Activity:** {current_activity['name']}\n"
                activity_context += f"📝 {current_activity.get('description', 'Working on this activity')}\n"
                activity_context += f"🌈 Routine: {routine_name} ({progress}% complete)"
                
                ai_text += activity_context
            
            return {
                "text": ai_text,
                "visual_cues": visual_cues,
                "emotion": emotion,
                "confidence": 0.85,
                "suggested_actions": actions,
                "communication_type": "text",
                "llm_source": "local" if self.use_local_mode else ("azure_openai" if self.use_azure else "openai"),
                "current_activity_context": current_activity_context
            }
        
        except Exception as e:
            logger.error(f"Text processing error: {str(e)}")
            return self._get_fallback_response()
    
    async def _use_openai(self, message: str, system_prompt: str) -> str:
        """Use OpenAI API (Azure or standard) for text generation."""
        if not self.client:
            raise Exception("AI client not available")
        
        try:
            if self.use_azure:
                # Check if this is a completion model (like gpt-35-turbo-instruct) or chat model
                is_completion_model = "instruct" in self.deployment_name.lower()
                
                if is_completion_model:
                    # Use completions endpoint for instruct models
                    # Combine system prompt and user message
                    combined_prompt = f"{system_prompt}\n\nUser: {message}\nAssistant:"
                    
                    response = self.client.completions.create(
                        model=self.deployment_name,
                        prompt=combined_prompt,
                        max_tokens=self.max_tokens,
                        temperature=self.temperature,
                        stop=["User:", "\n\n"]
                    )
                    return response.choices[0].text.strip()
                else:
                    # Use chat completions endpoint for chat models
                    response = self.client.chat.completions.create(
                        model=self.deployment_name,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": message}
                        ],
                        max_tokens=self.max_tokens,
                        temperature=self.temperature
                    )
                    return response.choices[0].message.content
            else:
                # Use standard OpenAI chat completions
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": message}
                    ],
                    max_tokens=self.max_tokens,
                    temperature=self.temperature
                )
                return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"AI API call failed: {str(e)}")
            raise Exception(f"Failed to get AI response: {str(e)}")
    
    async def _process_image_message(
        self,
        message: str,
        child_id: int,
        system_prompt: str
    ) -> Dict[str, Any]:
        """Process image-based communication."""
        # For now, provide a supportive response for image communication
        return {
            "text": "What a wonderful colorful picture you shared with Rainbow Bridge! 🌈✨ That makes my colors sparkle!",
            "visual_cues": ["rainbow", "sparkles", "happy_face", "star"],
            "emotion": "encouraging",
            "confidence": 0.9,
            "suggested_actions": ["show_more", "talk_about_it"],
            "communication_type": "image"
        }
    
    async def _process_audio_message(
        self,
        message: str,
        child_id: int,
        system_prompt: str
    ) -> Dict[str, Any]:
        """Process audio-based communication"""
        # For now, provide a supportive response for audio communication
        return {
            "text": "I love hearing your voice! It adds beautiful colors to Rainbow Bridge! 🌈🎵",
            "visual_cues": ["rainbow", "listening", "musical_note", "heart"],
            "emotion": "attentive",
            "confidence": 0.8,
            "suggested_actions": ["keep_talking", "use_pictures"],
            "communication_type": "audio"
        }
    
    def _detect_emotion(self, text: str) -> str:
        """Detect the emotional tone of the AI response."""
        emotion_keywords = {
            "happy": ["great", "wonderful", "awesome", "good job", "well done"],
            "encouraging": ["try", "practice", "keep going", "you can do it"],
            "calm": ["okay", "it's alright", "take time", "no worries"],
            "excited": ["amazing", "fantastic", "brilliant", "incredible"]
        }
        
        text_lower = text.lower()
        for emotion, keywords in emotion_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                return emotion
        
        return "neutral"
    
    def _suggest_visual_cues(self, input_message: str, ai_response: str) -> List[str]:
        """Suggest enhanced visual cues based on the conversation context."""
        visual_cues = []
        input_lower = input_message.lower()
        response_lower = ai_response.lower()
        
        # Emotional expression visual cues
        if any(word in input_lower for word in ["happy", "good", "great", "excited", "love", "like"]):
            visual_cues.extend(["happy_face", "star", "rainbow"])
        
        if any(word in input_lower for word in ["sad", "upset", "crying", "hurt", "bad"]):
            visual_cues.extend(["comfort_hug", "heart", "rainbow"])
        
        if any(word in input_lower for word in ["angry", "mad", "frustrated"]):
            visual_cues.extend(["calm", "breathing", "comfort_hug"])
        
        if any(word in input_lower for word in ["scared", "afraid", "worried"]):
            visual_cues.extend(["comfort_hug", "safety", "heart"])
        
        if any(word in input_lower for word in ["tired", "sleepy", "exhausted"]):
            visual_cues.extend(["rest", "calm", "moon"])
        
        # Need expression visual cues
        if any(word in input_lower for word in ["hungry", "eat", "food"]):
            visual_cues.extend(["food", "apple", "plate"])
        
        if any(word in input_lower for word in ["thirsty", "drink", "water"]):
            visual_cues.extend(["water", "cup", "drink"])
        
        if any(word in input_lower for word in ["bathroom", "potty", "toilet"]):
            visual_cues.extend(["bathroom", "checkmark"])
        
        if any(word in input_lower for word in ["help", "stuck", "can't"]):
            visual_cues.extend(["helping_hand", "support", "rainbow"])
        
        # Activity and learning visual cues
        if any(word in input_lower for word in ["play", "game", "fun"]):
            visual_cues.extend(["play_icon", "star", "rainbow"])
        
        if any(word in input_lower for word in ["learn", "teach", "show", "how"]):
            visual_cues.extend(["lightbulb", "book", "thinking"])
        
        if any(word in input_lower for word in ["draw", "color", "art"]):
            visual_cues.extend(["art", "paintbrush", "rainbow"])
        
        if any(word in input_lower for word in ["music", "song", "sing"]):
            visual_cues.extend(["musical_note", "speaker", "heart"])
        
        # Achievement and celebration visual cues
        if any(word in response_lower for word in ["great", "good job", "well done", "amazing", "proud"]):
            visual_cues.extend(["thumbs_up", "trophy", "celebration"])
        
        if any(word in input_lower for word in ["did it", "finished", "done", "completed"]):
            visual_cues.extend(["checkmark", "star", "celebration"])
        
        # Sensory and comfort visual cues
        if any(word in input_lower for word in ["loud", "noise", "bright", "too much"]):
            visual_cues.extend(["calm", "quiet", "adjusting"])
        
        if any(word in input_lower for word in ["quiet", "soft", "gentle"]):
            visual_cues.extend(["calm", "peaceful", "heart"])
        
        # Social interaction visual cues
        if any(word in input_lower for word in ["hello", "hi", "hey"]):
            visual_cues.extend(["friendly_wave", "rainbow", "smile"])
        
        if any(word in input_lower for word in ["thank you", "thanks"]):
            visual_cues.extend(["heart", "grateful", "rainbow"])
        
        if any(word in input_lower for word in ["please"]):
            visual_cues.extend(["polite", "heart", "star"])
        
        # Response-based visual cues
        if any(word in response_lower for word in ["practice", "try", "attempt"]):
            visual_cues.extend(["practice_icon", "star", "encouragement"])
        
        if any(word in response_lower for word in ["rainbow", "colorful", "magical"]):
            visual_cues.extend(["rainbow", "sparkles", "magic_wand"])
        
        if any(word in response_lower for word in ["step", "slowly", "together"]):
            visual_cues.extend(["step_by_step", "partnership", "support"])
        
        # Remove duplicates and limit to 3-4 visual cues to avoid overwhelming
        visual_cues = list(dict.fromkeys(visual_cues))[:4]
        
        # Default encouraging visual cues if none found
        if not visual_cues:
            visual_cues = ["rainbow", "friendly_robot", "heart"]
        
        return visual_cues
    
    def _suggest_actions(self, input_message: str, ai_response: str) -> List[str]:
        """Suggest enhanced follow-up actions based on the conversation context."""
        actions = []
        input_lower = input_message.lower()
        response_lower = ai_response.lower()
        
        # Routine and schedule actions
        if any(word in input_lower for word in ["routine", "schedule", "activities"]):
            actions.append("view_routine")
        
        if any(word in input_lower for word in ["create", "make", "new routine"]):
            actions.append("create_routine")
        
        if any(word in input_lower for word in ["start", "begin", "ready"]):
            actions.append("start_activity")
        
        # Learning and educational actions
        if any(word in input_lower for word in ["learn", "teach", "show me", "how to"]):
            actions.append("start_learning")
        
        if any(word in input_lower for word in ["practice", "try", "work on"]):
            actions.append("practice_skill")
        
        if any(word in input_lower for word in ["what is", "explain", "tell me"]):
            actions.append("get_explanation")
        
        # Emotional support actions
        if any(word in input_lower for word in ["sad", "upset", "angry", "frustrated"]):
            actions.append("emotional_support")
        
        if any(word in input_lower for word in ["scared", "worried", "afraid"]):
            actions.append("comfort_activity")
        
        if any(word in input_lower for word in ["calm", "relax", "breathe"]):
            actions.append("calming_activity")
        
        # Physical needs actions
        if any(word in input_lower for word in ["hungry", "eat", "food"]):
            actions.append("meal_time")
        
        if any(word in input_lower for word in ["thirsty", "drink", "water"]):
            actions.append("drink_water")
        
        if any(word in input_lower for word in ["tired", "sleepy", "rest"]):
            actions.append("rest_time")
        
        if any(word in input_lower for word in ["bathroom", "potty"]):
            actions.append("bathroom_break")
        
        # Activity and play actions
        if any(word in input_lower for word in ["play", "game", "fun"]):
            actions.append("play_activity")
        
        if any(word in input_lower for word in ["draw", "color", "art"]):
            actions.append("creative_activity")
        
        if any(word in input_lower for word in ["music", "song", "listen"]):
            actions.append("music_activity")
        
        if any(word in input_lower for word in ["outside", "walk", "fresh air"]):
            actions.append("outdoor_activity")
        
        # Social and communication actions
        if any(word in input_lower for word in ["talk", "tell", "share"]):
            actions.append("continue_conversation")
        
        if any(word in input_lower for word in ["friends", "social", "others"]):
            actions.append("social_activity")
        
        # Visual and sensory actions
        if any(word in response_lower for word in ["picture", "show", "visual", "image"]):
            actions.append("show_pictures")
        
        if any(word in input_lower for word in ["loud", "bright", "too much", "overwhelming"]):
            actions.append("sensory_adjustment")
        
        if any(word in input_lower for word in ["quiet", "soft", "gentle"]):
            actions.append("quiet_activity")
        
        # Achievement and progress actions
        if any(word in input_lower for word in ["finished", "done", "completed"]):
            actions.append("celebrate_achievement")
        
        if any(word in response_lower for word in ["progress", "improvement", "learning"]):
            actions.append("track_progress")
        
        # Help and support actions
        if any(word in input_lower for word in ["help", "stuck", "difficult", "hard"]):
            actions.append("get_help")
        
        if any(word in input_lower for word in ["don't understand", "confused"]):
            actions.append("break_down_steps")
        
        # Remove duplicates and limit to 3 actions to avoid overwhelming
        actions = list(dict.fromkeys(actions))[:3]
        
        # Default action if none found
        if not actions:
            actions = ["continue_conversation", "show_pictures", "start_activity"]
        
        return actions
    
    def _get_fallback_response(self, error_msg: Optional[str] = None) -> Dict[str, Any]:
        """Provide a safe fallback response when AI processing fails."""
        if error_msg:
            logger.warning(f"Fallback response triggered: {error_msg}")
        
        return {
            "text": "I'm Rainbow Bridge, and I'm here for you! Let's try our colorful adventure again! 🌈✨",
            "visual_cues": ["rainbow", "friendly_robot", "heart"],
            "emotion": "supportive",
            "confidence": 1.0,
            "suggested_actions": ["try_again", "use_pictures"],
            "communication_type": "fallback"
        }
    
    async def generate_routine_suggestions(
        self,
        child_id: int,
        current_activities: List[str],
        time_of_day: str
    ) -> List[Dict[str, Any]]:
        """Generate routine suggestions based on current activities and time."""
        try:
            prompt = f"""
            Suggest 3 appropriate activities for an autistic child's routine.
            Current activities: {', '.join(current_activities)}
            Time of day: {time_of_day}
            
            Focus on:
            - Sensory-friendly activities
            - Predictable structure
            - Visual supports
            - Calming transitions
            
            Provide simple, clear activity descriptions.
            """
            
            response = None
            
            # Try local LLM first if available
            if self.use_local_mode:
                local_response = await self.local_llm.generate_response(
                    prompt=prompt,
                    system_prompt=self.system_prompt,
                    max_tokens=200,
                    temperature=0.6
                )
                
                if local_response.success:
                    suggestions_text = local_response.text
                else:
                    # Fall back to OpenAI if available
                    if self.client:
                        response = self.client.chat.completions.create(
                            model=self.model,
                            messages=[
                                {"role": "system", "content": self.system_prompt},
                                {"role": "user", "content": prompt}
                            ],
                            max_tokens=200,
                            temperature=0.6
                        )
                        suggestions_text = response.choices[0].message.content
                    else:
                        raise Exception("No LLM provider available")
            else:
                # Use OpenAI directly
                if self.client:
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=[
                            {"role": "system", "content": self.system_prompt},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=200,
                        temperature=0.6
                    )
                    suggestions_text = response.choices[0].message.content
                else:
                    raise Exception("OpenAI client not available")
            
            # If we used OpenAI, get the text from response
            if response and not self.use_local_mode:
                suggestions_text = response.choices[0].message.content
            suggestions = self._parse_routine_suggestions(suggestions_text)
            
            return suggestions
        
        except Exception as e:
            logger.error(f"Routine suggestion error: {str(e)}")
            return [
                {
                    "title": "Quiet Time",
                    "description": "Take a few minutes to relax and breathe",
                    "duration": "10 minutes",
                    "visual_cue": "meditation"
                }
            ]
    
    async def generate_smart_schedule(
        self,
        child_id: int,
        time_of_day: str,
        preferences: List[str] = None,
        energy_level: str = "medium",
        duration: str = "medium"
    ) -> Dict[str, Any]:
        """Generate an AI-powered smart schedule for a child."""
        try:
            preferences = preferences or []
            
            # Create comprehensive prompt for smart schedule
            prompt = f"""
You are Rainbow Bridge, a magical companion. Create a simple activity schedule for an autistic child.

Parameters:
- Time: {time_of_day}
- Preferences: {', '.join(preferences) if preferences else 'variety'}
- Energy: {energy_level}

You MUST respond in exactly this format:

1. [Activity Name]
Duration: [X] minutes
[Simple description]

2. [Activity Name]  
Duration: [X] minutes
[Simple description]

3. [Activity Name]
Duration: [X] minutes
[Simple description]

4. [Activity Name]
Duration: [X] minutes
[Simple description]

Make activities appropriate for {time_of_day} time with {energy_level} energy level.
Each activity should be 5-20 minutes.
Keep descriptions simple and encouraging.
Focus on autism-friendly activities: predictable, sensory-friendly, calming.

Example format:
1. Deep Breathing
Duration: 10 minutes
Take slow, calm breaths

Start your response with the numbered list immediately.
            """
            
            # Generate AI response
            try:
                ai_text = await self._use_openai(prompt, self.system_prompt)
            except Exception as e:
                logger.error(f"AI generation failed: {e}")
                # Provide a structured fallback response
                ai_text = f"""
🌈 Hello my wonderful friend! Let me create some magical {time_of_day} activities for you! ✨

Here are wonderful activities for you:

1. Calm Breathing Exercise
Duration: 10 minutes
Take slow, peaceful breaths with Rainbow Bridge

2. Creative Art Time
Duration: 15 minutes
Draw, color, or create something beautiful

3. Gentle Movement
Duration: 10 minutes
Stretch or move your body in a way that feels good

4. Quiet Time Activity
Duration: 15 minutes
Choose a peaceful activity you enjoy

🌈 These activities are specially chosen for your {energy_level} energy level! Have a wonderful time! ✨
                """
            
            # Parse the response into structured format
            activities = self._parse_smart_schedule(ai_text)
            
            return {
                "success": True,
                "schedule_text": ai_text,
                "activities": activities,
                "time_of_day": time_of_day,
                "preferences": preferences,
                "energy_level": energy_level
            }
            
        except Exception as e:
            logger.error(f"Smart schedule generation error: {str(e)}")
            
            # Provide a comprehensive fallback schedule
            fallback_activities = []
            
            if time_of_day == "morning":
                fallback_activities = [
                    {"name": "Gentle Wake-Up Breathing", "description": "Take 5 slow, deep breaths to start your day peacefully", "duration": "5 minutes", "visual_cue": "breathing"},
                    {"name": "Morning Stretches", "description": "Gentle stretches to wake up your body", "duration": "10 minutes", "visual_cue": "stretching"},
                    {"name": "Breakfast Preparation", "description": "Help prepare or eat a healthy breakfast", "duration": "20 minutes", "visual_cue": "food"},
                    {"name": "Daily Planning", "description": "Look at your schedule and plan your day", "duration": "10 minutes", "visual_cue": "calendar"}
                ]
            elif time_of_day == "afternoon":
                fallback_activities = [
                    {"name": "Creative Art Time", "description": "Draw, paint, or create something colorful", "duration": "20 minutes", "visual_cue": "art"},
                    {"name": "Active Play", "description": "Move your body with fun physical activity", "duration": "15 minutes", "visual_cue": "play"},
                    {"name": "Snack Break", "description": "Enjoy a healthy snack and hydrate", "duration": "10 minutes", "visual_cue": "snack"},
                    {"name": "Learning Activity", "description": "Explore something new or practice a skill", "duration": "20 minutes", "visual_cue": "learning"}
                ]
            else:  # evening
                fallback_activities = [
                    {"name": "Quiet Reading", "description": "Read a favorite book or story", "duration": "15 minutes", "visual_cue": "reading"},
                    {"name": "Calming Music", "description": "Listen to peaceful, soothing music", "duration": "10 minutes", "visual_cue": "music"},
                    {"name": "Bedtime Routine", "description": "Prepare for sleep with calming activities", "duration": "20 minutes", "visual_cue": "sleep"},
                    {"name": "Gratitude Reflection", "description": "Think about good things from your day", "duration": "5 minutes", "visual_cue": "heart"}
                ]
            
            # Adjust activities based on energy level
            if energy_level == "low":
                fallback_activities = [act for act in fallback_activities if "quiet" in act["description"].lower() or "calm" in act["description"].lower()][:3]
            elif energy_level == "high":
                fallback_activities = [act for act in fallback_activities if "active" in act["description"].lower() or "creative" in act["description"].lower()][:4]
            
            return {
                "success": False,
                "schedule_text": f"🌈 Rainbow Bridge created some wonderful {time_of_day} activities for you! Even when magic needs a moment, we always have beautiful activities ready! ✨",
                "activities": fallback_activities,
                "error": str(e),
                "fallback_used": True
            }
    
    def _parse_smart_schedule(self, schedule_text: str) -> List[Dict[str, Any]]:
        """Parse AI-generated smart schedule into structured activities."""
        activities = []
        lines = schedule_text.split('\n')
        
        current_activity = {}
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            # Skip empty lines and decorative lines
            if not line or line.startswith('🌈') or line.startswith('=') or len(line) < 3:
                i += 1
                continue
            
            # Look for numbered activity patterns (1., 2., etc.)
            activity_match = re.match(r'^(\d+)\.?\s*(.+)', line)
            if activity_match:
                # Save previous activity if exists
                if current_activity.get('name'):
                    activities.append(current_activity)
                
                # Start new activity
                activity_name = activity_match.group(2).strip()
                current_activity = {
                    'name': activity_name[:50],
                    'description': activity_name[:100],  # Use name as default description
                    'duration': "15 minutes",
                    'visual_cue': self._get_visual_cue_for_activity(activity_name)
                }
                
                # Look ahead for duration and description in next few lines
                j = i + 1
                while j < len(lines) and j < i + 5:  # Look ahead max 5 lines
                    next_line = lines[j].strip()
                    
                    if not next_line:
                        j += 1
                        continue
                    
                    # Check if we hit the next activity
                    if re.match(r'^\d+\.', next_line):
                        break
                    
                    # Check for duration
                    if 'duration' in next_line.lower():
                        duration_match = re.search(r'(\d+)\s*(?:minutes?|mins?)', next_line)
                        if duration_match:
                            current_activity['duration'] = f"{duration_match.group(1)} minutes"
                    
                    # Check for description (substantial line that's not duration)
                    elif len(next_line) > 10 and 'duration' not in next_line.lower() and not next_line.startswith('🌈'):
                        current_activity['description'] = next_line[:100]
                    
                    j += 1
                
                i = j - 1  # Adjust main loop index
            
            i += 1
        
        # Add the last activity
        if current_activity.get('name'):
            activities.append(current_activity)
        
        # If we didn't parse any activities, try a simpler approach
        if not activities:
            activities = self._simple_parse_activities(schedule_text)
        
        # Final fallback activities if all parsing fails
        if not activities:
            activities = self._get_fallback_activities()
        
        return activities[:6]  # Return maximum 6 activities
    
    def _simple_parse_activities(self, text: str) -> List[Dict[str, Any]]:
        """Simple backup parsing method."""
        activities = []
        
        # Look for any lines that might be activities
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            
            # Skip empty lines and decorative content
            if not line or line.startswith('🌈') or len(line) < 5:
                continue
            
            # Look for numbered items or bullet points
            if re.match(r'^[\d\-\*\•]\s*', line) or any(keyword in line.lower() for keyword in ['time', 'activity', 'exercise', 'reading', 'play']):
                activity_name = re.sub(r'^[\d\-\*\•\.]\s*', '', line)
                activities.append({
                    'name': activity_name[:50],
                    'description': activity_name[:100],
                    'duration': "15 minutes",
                    'visual_cue': self._get_visual_cue_for_activity(activity_name)
                })
        
        return activities[:4]
    
    def _get_visual_cue_for_activity(self, activity_name: str) -> str:
        """Get appropriate visual cue based on activity name."""
        activity_lower = activity_name.lower()
        
        if any(word in activity_lower for word in ['breath', 'calm', 'relax']):
            return "meditation"
        elif any(word in activity_lower for word in ['read', 'book', 'story']):
            return "reading"
        elif any(word in activity_lower for word in ['draw', 'art', 'creative', 'paint']):
            return "creative"
        elif any(word in activity_lower for word in ['stretch', 'move', 'exercise']):
            return "movement"
        elif any(word in activity_lower for word in ['music', 'listen', 'song']):
            return "music"
        elif any(word in activity_lower for word in ['play', 'game', 'fun']):
            return "play"
        else:
            return "activity_icon"
    
    def _get_fallback_activities(self) -> List[Dict[str, Any]]:
        """Get fallback activities when parsing completely fails."""
        return [
            {
                "name": "Calm Down Time",
                "description": "Take deep breaths and relax with Rainbow Bridge",
                "duration": "10 minutes",
                "visual_cue": "meditation"
            },
            {
                "name": "Creative Fun Time",
                "description": "Choose a colorful activity you enjoy",
                "duration": "15 minutes", 
                "visual_cue": "creative"
            },
            {
                "name": "Gentle Movement",
                "description": "Move your body in a way that feels good",
                "duration": "10 minutes",
                "visual_cue": "movement"
            }
        ]
    
    def _parse_routine_suggestions(self, suggestions_text: str) -> List[Dict[str, Any]]:
        """Parse AI-generated routine suggestions into structured format."""
        # Simple parsing - in a real implementation, this would be more sophisticated
        suggestions = []
        lines = suggestions_text.split('\n')
        
        for line in lines:
            if line.strip() and not line.startswith('-'):
                suggestions.append({
                    "title": line.strip()[:50],
                    "description": line.strip(),
                    "duration": "15 minutes",
                    "visual_cue": "activity_icon"
                })
        
        return suggestions[:3]  # Return maximum 3 suggestions
    
    def get_llm_status(self) -> Dict[str, Any]:
        """Get status information about available LLM providers."""
        status = {
            "local_mode": self.use_local_mode,
            "openai_available": self.client is not None,
            "local_providers": self.local_llm.get_provider_status(),
            "available_providers": self.local_llm.get_available_providers(),
            "fallback_enabled": os.getenv("FALLBACK_TO_OPENAI", "True").lower() == "true"
        }
        return status
    
    def switch_to_local_mode(self) -> bool:
        """Switch to local LLM mode if providers are available."""
        if self.local_llm.get_available_providers():
            self.use_local_mode = True
            logger.info("Switched to local LLM mode")
            return True
        else:
            logger.warning("No local LLM providers available")
            return False
    
    def switch_to_cloud_mode(self) -> bool:
        """Switch to cloud LLM mode if OpenAI is available."""
        if self.client:
            self.use_local_mode = False
            logger.info("Switched to cloud LLM mode")
            return True
        else:
            logger.warning("OpenAI client not available")
            return False
    
    async def test_llm_connectivity(self) -> Dict[str, Any]:
        """Test connectivity to all available LLM providers."""
        test_results = {
            "local_providers": {},
            "openai": {"available": False, "error": None}
        }
        
        # Test local providers
        test_prompt = "Hello, please respond with a simple greeting."
        test_system = "You are a friendly assistant. Keep responses short."
        
        for provider_name in self.local_llm.providers:
            provider = self.local_llm.providers[provider_name]
            try:
                if provider.is_available():
                    response = await provider.generate(test_prompt, test_system, 50, 0.7)
                    test_results["local_providers"][provider_name] = {
                        "available": response.success,
                        "response_time": response.processing_time,
                        "error": response.error
                    }
                else:
                    test_results["local_providers"][provider_name] = {
                        "available": False,
                        "error": "Provider not available"
                    }
            except Exception as e:
                test_results["local_providers"][provider_name] = {
                    "available": False,
                    "error": str(e)
                }
        
        # Test OpenAI
        if self.client:
            try:
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": test_prompt}],
                    max_tokens=20
                )
                test_results["openai"] = {
                    "available": True,
                    "response": response.choices[0].message.content[:50] + "...",
                    "error": None
                }
            except Exception as e:
                test_results["openai"] = {
                    "available": False,
                    "error": str(e)
                }
        
        return test_results
    
    def _get_routine_visual_cues(self, intent: str) -> List[str]:
        """Get visual cues specific to routine actions."""
        routine_visual_cues = {
            "create_routine": ["calendar", "clock", "star", "rainbow"],
            "get_routines": ["list", "calendar", "activities", "rainbow"],
            "start_routine": ["play", "start", "arrow_right", "sparkles"],
            "complete_activity": ["checkmark", "star", "trophy", "celebration"],
            "get_suggestions": ["lightbulb", "question", "thinking", "rainbow"],
            "smart_schedule": ["magic_wand", "sparkles", "calendar", "rainbow", "clock", "star"]
        }
        
        return routine_visual_cues.get(intent, ["rainbow", "friendly_robot"])
    
    def _get_routine_actions(self, intent: str) -> List[str]:
        """Get suggested actions for routine intents."""
        routine_actions = {
            "create_routine": ["create_routine", "view_templates", "schedule_time"],
            "get_routines": ["view_routines", "start_routine", "edit_routine"],
            "start_routine": ["begin_activity", "view_steps", "get_help"],
            "complete_activity": ["next_activity", "view_progress", "celebrate"],
            "get_suggestions": ["create_routine", "try_activity", "explore_more"],
            "smart_schedule": ["create_routine", "customize_schedule", "start_activity", "save_schedule"]
        }
        
        return routine_actions.get(intent, ["continue_chat"])
    
    async def _detect_communication_intent(self, message: str, child_id: int) -> Dict[str, Any]:
        """
        Detect broader communication intents beyond just routines.
        This handles emotional, social, educational, and general communication patterns.
        """
        message_lower = message.lower().strip()
        detected_intents = []
        
        # Communication intent patterns for autistic children
        intent_patterns = {
            "emotional_expression": {
                "patterns": [
                    "i feel", "i'm feeling", "feeling", "i am", "i'm sad", "i'm happy", 
                    "i'm angry", "i'm scared", "i'm excited", "i'm tired", "i'm frustrated",
                    "upset", "mad", "good", "bad", "okay", "fine", "not good"
                ],
                "confidence": 0.85,
                "visual_cues": ["heart", "rainbow", "comfort_hug"],
                "response_type": "emotional_support"
            },
            "need_expression": {
                "patterns": [
                    "i need", "i want", "can i have", "i'm hungry", "i'm thirsty", 
                    "bathroom", "toilet", "tired", "sleepy", "help me", "i need help",
                    "can you help", "hungry", "thirsty", "potty"
                ],
                "confidence": 0.90,
                "visual_cues": ["helping_hand", "checkmark", "heart"],
                "response_type": "need_fulfillment"
            },
            "social_communication": {
                "patterns": [
                    "hello", "hi", "hey", "goodbye", "bye", "thank you", "thanks",
                    "please", "sorry", "excuse me", "yes", "no", "maybe", "i don't know"
                ],
                "confidence": 0.80,
                "visual_cues": ["friendly_wave", "smile", "thumbs_up"],
                "response_type": "social_interaction"
            },
            "learning_request": {
                "patterns": [
                    "what is", "how do", "can you teach", "i want to learn", "explain",
                    "tell me about", "what does", "why", "how", "show me", "help me understand"
                ],
                "confidence": 0.85,
                "visual_cues": ["lightbulb", "book", "thinking"],
                "response_type": "educational_support"
            },
            "activity_interest": {
                "patterns": [
                    "want to play", "can we play", "i like", "favorite", "fun", "game",
                    "toy", "book", "music", "draw", "color", "outside", "park"
                ],
                "confidence": 0.80,
                "visual_cues": ["play_icon", "star", "rainbow"],
                "response_type": "activity_engagement"
            },
            "sensory_feedback": {
                "patterns": [
                    "too loud", "too bright", "too much", "quiet", "loud", "bright",
                    "dark", "hot", "cold", "soft", "hard", "texture", "sound", "noise"
                ],
                "confidence": 0.90,
                "visual_cues": ["calm", "comfort", "adjusting"],
                "response_type": "sensory_support"
            },
            "confusion_difficulty": {
                "patterns": [
                    "i don't understand", "confused", "hard", "difficult", "too hard",
                    "i can't", "don't know how", "stuck", "help", "lost"
                ],
                "confidence": 0.85,
                "visual_cues": ["helping_hand", "patience", "step_by_step"],
                "response_type": "guidance_support"
            },
            "achievement_sharing": {
                "patterns": [
                    "i did it", "look what i did", "finished", "completed", "done",
                    "proud", "good job", "success", "accomplished", "made"
                ],
                "confidence": 0.85,
                "visual_cues": ["celebration", "trophy", "star", "thumbs_up"],
                "response_type": "celebration_support"
            }
        }
        
        # Analyze message for each intent type
        for intent_type, intent_data in intent_patterns.items():
            for pattern in intent_data["patterns"]:
                if pattern in message_lower:
                    detected_intents.append({
                        "intent": intent_type,
                        "confidence": intent_data["confidence"],
                        "pattern_matched": pattern,
                        "visual_cues": intent_data["visual_cues"],
                        "response_type": intent_data["response_type"],
                        "child_id": child_id,
                        "original_message": message
                    })
                    break  # Only match one pattern per intent type
        
        # If multiple intents detected, prioritize by confidence and context
        if detected_intents:
            # Sort by confidence (highest first)
            detected_intents.sort(key=lambda x: x["confidence"], reverse=True)
            primary_intent = detected_intents[0]
            
            # Add secondary intents if they're strong enough
            secondary_intents = [intent for intent in detected_intents[1:] if intent["confidence"] > 0.75]
            
            return {
                "primary_intent": primary_intent,
                "secondary_intents": secondary_intents,
                "has_multiple_intents": len(detected_intents) > 1,
                "total_intents_detected": len(detected_intents)
            }
        
        return None

    async def _generate_intent_based_response(self, intent_data: Dict[str, Any], message: str, current_activity_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate a response based on detected communication intent."""
        primary_intent = intent_data["primary_intent"]
        intent_type = primary_intent["intent"]
        response_type = primary_intent["response_type"]
        
        # Generate contextual responses based on intent
        response_templates = {
            "emotional_support": [
                "I can hear that you're feeling {emotion}. That's completely okay! 🌈",
                "Thank you for sharing your feelings with me. You're being so brave! 💚",
                "Feelings are like colors in a rainbow - they're all important! Let's talk about it. 🌈"
            ],
            "need_fulfillment": [
                "I understand you need {need}. Let me help you with that! 🤗",
                "It's great that you told me what you need! That's excellent communication! ⭐",
                "Let's work together to help you feel better. You did the right thing by asking! 💪"
            ],
            "social_interaction": [
                "Hello there, wonderful friend! 🌈 I'm so happy to talk with you!",
                "Thank you for being so polite! You have excellent manners! ✨",
                "I love chatting with you! You're such a great communicator! 😊"
            ],
            "educational_support": [
                "What a fantastic question! I love when you're curious about learning! 📚",
                "You're such a wonderful learner! Let me help you understand that. 🌟",
                "Great question! Learning new things is like collecting colorful gems! 💎"
            ],
            "activity_engagement": [
                "That sounds like so much fun! I love your enthusiasm! 🎉",
                "What a wonderful activity choice! You have great ideas! ⭐",
                "Playing and having fun is so important! You're making great choices! 🌈"
            ],
            "sensory_support": [
                "I understand that doesn't feel comfortable for you. Let's find a better way! 🤗",
                "Thank you for telling me about that. Your comfort is very important! 💚",
                "Everyone has different sensory needs, and yours matter! Let's adjust things. ✨"
            ],
            "guidance_support": [
                "It's perfectly okay to find things challenging sometimes! Let's break it down together. 🌟",
                "You're so smart for asking for help! That takes courage! 💪",
                "Every expert was once a beginner. Let's take it step by step! 🌈"
            ],
            "celebration_support": [
                "WOW! Look at what you accomplished! I'm so proud of you! 🎉",
                "You did such an amazing job! That deserves a celebration! 🌟",
                "What a fantastic achievement! You should feel so proud of yourself! 🏆"
            ]
        }
        
        # Select appropriate response template
        templates = response_templates.get(response_type, response_templates["social_interaction"])
        selected_template = random.choice(templates)
        
        # Personalize the response based on the message content
        personalized_response = self._personalize_response(selected_template, message, primary_intent)
        
        # Add current activity context to the response if available
        if current_activity_context and current_activity_context.get("current_activity"):
            current_activity = current_activity_context["current_activity"]
            routine_name = current_activity_context.get("routine_name", "your routine")
            progress = current_activity_context.get("progress_percentage", 0)
            
            # Enhance response with current activity information
            activity_context = f"\n\n🎯 **Current Activity:** {current_activity['name']}\n"
            activity_context += f"📝 {current_activity.get('description', 'Working on this activity')}\n"
            activity_context += f"🌈 Routine: {routine_name} ({progress}% complete)"
            
            personalized_response += activity_context
        
        return {
            "text": personalized_response,
            "visual_cues": primary_intent["visual_cues"],
            "emotion": "encouraging",
            "confidence": primary_intent["confidence"],
            "suggested_actions": self._get_intent_actions(intent_type),
            "communication_type": "text",
            "intent_detected": intent_type,
            "response_type": response_type,
            "llm_source": "intent_based",
            "current_activity_context": current_activity_context
        }

    def _personalize_response(self, template: str, message: str, intent: Dict[str, Any]) -> str:
        """Personalize response template based on message content."""
        message_lower = message.lower()
        
        # Extract key words for personalization
        if "{emotion}" in template:
            emotions = ["happy", "sad", "angry", "excited", "tired", "frustrated", "scared"]
            detected_emotion = next((emotion for emotion in emotions if emotion in message_lower), "that way")
            template = template.replace("{emotion}", detected_emotion)
        
        if "{need}" in template:
            needs = ["help", "food", "water", "bathroom", "rest", "break"]
            detected_need = next((need for need in needs if need in message_lower), "something")
            template = template.replace("{need}", detected_need)
        
        # For achievement sharing, extract what they accomplished from natural language
        if intent.get("intent") == "achievement_sharing":
            # Enhanced activity recognition from general statements
            activities = {
                "getting dressed": ["dressed", "clothes", "shirt", "pants", "socks", "shoes"],
                "eating": ["ate", "breakfast", "lunch", "dinner", "food", "hungry"],
                "brushing teeth": ["brush", "teeth", "tooth", "clean"],
                "washing": ["wash", "clean", "hands", "face", "bath", "shower"],
                "waking up": ["wake", "woke", "up", "morning", "awake"],
                "playing": ["play", "game", "toy", "fun"],
                "homework": ["homework", "study", "read", "book", "school"],
                "cleaning": ["clean", "tidy", "organize", "room"],
                "going to bed": ["bed", "sleep", "tired", "bedtime", "pajamas"]
            }
            
            detected_activity = "something wonderful"
            for activity, keywords in activities.items():
                if any(keyword in message_lower for keyword in keywords):
                    detected_activity = activity
                    break
            
            # Make the response more specific and encouraging
            if "what a fantastic achievement" in template.lower():
                return f"🌟 Wow! You did such a great job with {detected_activity}! That's a big accomplishment! I'm so proud of how you're growing and learning! 🎉"
            elif "look at what you accomplished" in template.lower():
                return f"🎉 Look at you go! {detected_activity.title()} - that's amazing! You're getting so good at taking care of yourself! 🌈"
        
        return template

    def _get_intent_actions(self, intent_type: str) -> List[str]:
        """Get suggested actions based on intent type."""
        action_map = {
            "emotional_expression": ["Take deep breaths", "Talk about feelings", "Use calming activities"],
            "need_expression": ["Address immediate need", "Check comfort level", "Offer alternatives"],
            "social_interaction": ["Continue conversation", "Practice social skills", "Engage in interaction"],
            "learning_request": ["Provide explanation", "Use visual aids", "Break down information"],
            "activity_interest": ["Explore activity options", "Plan activity time", "Gather materials"],
            "sensory_feedback": ["Adjust environment", "Offer sensory tools", "Check comfort"],
            "guidance_support": ["Break down steps", "Provide encouragement", "Offer different approach"],
            "achievement_sharing": ["Celebrate success", "Acknowledge effort", "Share pride"]
        }
        
        return action_map.get(intent_type, ["Continue conversation", "Provide support"])
