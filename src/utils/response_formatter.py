"""
Response Formatter utility for Rainbow Bridge
Handles formatting and enhancing AI responses.
"""

import re
from typing import Dict, Any, Optional
from src.models.entities import Child


class ResponseFormatter:
    """Utility class for formatting AI responses."""
    
    def __init__(self):
        self.rainbow_emojis = ["🌈", "✨", "🎯", "🎉", "🌟", "💫", "🎨", "🦄"]
        self.encouragement_phrases = [
            "You're doing amazing!",
            "What a superstar!",
            "Fantastic work!",
            "You're incredible!",
            "So proud of you!",
            "You're a rainbow warrior!"
        ]
    
    def format_response(
        self, 
        ai_response: str, 
        child: Child, 
        context: Dict[str, Any],
        routine_action: Optional[str] = None
    ) -> str:
        """Format an AI response with appropriate enhancements."""
        
        # Clean and normalize the response
        formatted_response = self._clean_response(ai_response)
        
        # Add current activity context if needed
        if context.get('has_active_routine'):
            formatted_response = self._ensure_current_activity_context(
                formatted_response, context
            )
        
        # Enhance completion responses
        if routine_action == 'complete_activity':
            formatted_response = self._enhance_completion_response(
                formatted_response, context
            )
        
        # Add visual enhancements
        formatted_response = self._add_visual_enhancements(formatted_response)
        
        # Ensure appropriate length
        formatted_response = self._ensure_appropriate_length(formatted_response)
        
        return formatted_response
    
    def _clean_response(self, response: str) -> str:
        """Clean and normalize the AI response."""
        
        # Remove extra whitespace
        response = re.sub(r'\s+', ' ', response.strip())
        
        # Remove duplicate punctuation
        response = re.sub(r'[.]{2,}', '.', response)
        response = re.sub(r'[!]{2,}', '!', response)
        response = re.sub(r'[?]{2,}', '?', response)
        
        # Ensure proper capitalization
        if response and not response[0].isupper():
            response = response[0].upper() + response[1:]
        
        return response
    
    def _ensure_current_activity_context(
        self, 
        response: str, 
        context: Dict[str, Any]
    ) -> str:
        """Ensure current activity context is included in the response."""
        
        current_activity = context.get('current_activity')
        if not current_activity:
            return response
        
        activity_name = current_activity['name']
        
        # Check if current activity is already mentioned
        activity_pattern = rf"🎯\s*\*?\*?Current Activity:?\*?\*?\s*{re.escape(activity_name)}"
        if re.search(activity_pattern, response, re.IGNORECASE):
            return response
        
        # Add current activity context
        activity_context = f"\n\n🎯 **Current Activity:** {activity_name}"
        
        # Add progress information
        progress = context.get('progress_percentage', 0)
        remaining = context.get('remaining_activities', 0)
        
        if remaining > 0:
            activity_context += f"\n📊 Progress: {progress}% ({remaining} activities remaining)"
        
        return response + activity_context
    
    def _enhance_completion_response(
        self, 
        response: str, 
        context: Dict[str, Any]
    ) -> str:
        """Enhance responses for activity completions."""
        
        # Add celebration if not already present
        celebration_indicators = ["🎉", "fantastic", "amazing", "great job", "wonderful"]
        has_celebration = any(indicator in response.lower() for indicator in celebration_indicators)
        
        if not has_celebration:
            response = "🎉 " + response
        
        # Add encouragement
        import random
        encouragement = random.choice(self.encouragement_phrases)
        if encouragement.lower() not in response.lower():
            response += f" {encouragement}"
        
        return response
    
    def _add_visual_enhancements(self, response: str) -> str:
        """Add appropriate visual enhancements to the response."""
        
        # Add rainbow emoji if not present
        if "🌈" not in response and len(response) > 20:
            # Add at the beginning or end based on content
            if response.endswith("!") or response.endswith("."):
                response = "🌈 " + response
            else:
                response += " 🌈"
        
        # Ensure magical elements for positive responses
        positive_words = ["great", "amazing", "wonderful", "fantastic", "good"]
        if any(word in response.lower() for word in positive_words):
            if "✨" not in response:
                response += " ✨"
        
        return response
    
    def _ensure_appropriate_length(self, response: str) -> str:
        """Ensure the response is an appropriate length."""
        
        # Maximum length for child-friendly responses
        max_length = 200
        
        if len(response) > max_length:
            # Truncate at the last complete sentence
            sentences = response.split('.')
            truncated = ""
            
            for sentence in sentences:
                if len(truncated + sentence + ".") <= max_length:
                    truncated += sentence + "."
                else:
                    break
            
            if truncated:
                response = truncated.strip()
            else:
                # Fallback: hard truncate with ellipsis
                response = response[:max_length-3] + "..."
        
        return response
    
    def format_routine_status(self, context: Dict[str, Any]) -> str:
        """Format routine status information."""
        
        if not context.get('has_active_routine'):
            return ""
        
        status_text = f"\n\n📅 **{context.get('routine_name', 'Routine')}**"
        status_text += f"\n📊 Progress: {context.get('progress_percentage', 0)}%"
        status_text += f"\n✅ Completed: {context.get('completed_activities', 0)}/{context.get('total_activities', 0)}"
        
        current_activity = context.get('current_activity')
        if current_activity:
            status_text += f"\n🎯 Current: {current_activity['name']}"
        
        return status_text
    
    def format_suggestions(self, suggestions: list) -> str:
        """Format suggestions for the user."""
        
        if not suggestions:
            return ""
        
        formatted = "\n\n💡 **Suggestions:**"
        for i, suggestion in enumerate(suggestions[:3], 1):
            formatted += f"\n{i}. {suggestion}"
        
        return formatted
    
    def format_error_response(self, error_type: str = "general") -> str:
        """Format a friendly error response."""
        
        error_responses = {
            "general": "I'm having a little trouble right now, but I'm still here to help! 🌈",
            "routine": "I couldn't find that routine, but let's try something else! ✨",
            "activity": "I'm not sure about that activity, but you're doing great! 🎯",
            "ai": "My AI helper is taking a short break, but I can still chat with you! 💫"
        }
        
        return error_responses.get(error_type, error_responses["general"])
