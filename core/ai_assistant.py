"""
AI Assistant for Special Kids - Core AI Processing Module

This module handles all AI interactions using OpenAI's GPT-4 model,
specifically configured for autism spectrum communication patterns.
"""

import os
import openai
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from .local_llm import LocalLLMManager, LocalLLMResponse

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
    
    def __init__(self):
        # Initialize local LLM manager
        self.local_llm = LocalLLMManager()
        self.use_local_mode = os.getenv("LOCAL_MODE", "False").lower() == "true"
        
        # Initialize OpenAI client (for fallback or primary use)
        self.client = None
        openai_api_key = os.getenv("OPENAI_API_KEY")
        
        if openai_api_key and openai_api_key != "your_openai_api_key_here":
            try:
                self.client = openai.OpenAI(api_key=openai_api_key)
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI client: {e}")
        
        if not self.use_local_mode and not self.client:
            logger.warning("Neither local LLM nor OpenAI is available. Some features may not work.")
        
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
            
            return {
                "text": ai_text,
                "visual_cues": visual_cues,
                "emotion": emotion,
                "confidence": 0.85,
                "suggested_actions": actions,
                "communication_type": "text",
                "llm_source": "local" if self.use_local_mode else "openai"
            }
        
        except Exception as e:
            logger.error(f"Text processing error: {str(e)}")
            return self._get_fallback_response()
    
    async def _use_openai(self, message: str, system_prompt: str) -> str:
        """Use OpenAI API for text generation."""
        if not self.client:
            raise Exception("OpenAI client not available")
        
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
        """Process audio-based communication."""
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
        """Suggest visual cues based on the conversation context."""
        visual_cues = []
        
        # Basic visual cues based on content
        if any(word in input_message.lower() for word in ["happy", "good", "like"]):
            visual_cues.append("happy_face")
        
        if any(word in input_message.lower() for word in ["sad", "upset", "don't like"]):
            visual_cues.append("comfort_hug")
        
        if any(word in ai_response.lower() for word in ["great", "good job", "well done"]):
            visual_cues.append("thumbs_up")
        
        if any(word in ai_response.lower() for word in ["try", "practice"]):
            visual_cues.append("practice_icon")
        
        # Default encouraging visual cue
        if not visual_cues:
            visual_cues.append("friendly_robot")
        
        return visual_cues
    
    def _suggest_actions(self, input_message: str, ai_response: str) -> List[str]:
        """Suggest follow-up actions based on the conversation."""
        actions = []
        
        if any(word in input_message.lower() for word in ["routine", "schedule"]):
            actions.append("view_routine")
        
        if any(word in input_message.lower() for word in ["learn", "practice"]):
            actions.append("start_activity")
        
        if any(word in ai_response.lower() for word in ["picture", "show"]):
            actions.append("show_pictures")
        
        # Default action
        if not actions:
            actions.append("continue_chat")
        
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
