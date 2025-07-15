"""
AI Prompts utility for Rainbow Bridge
Contains prompt templates and generation logic for AI interactions.
"""

from typing import Dict, Any
from src.models.entities import Child


class AIPrompts:
    """Utility class for generating AI prompts."""
    
    def __init__(self):
        self.base_system_prompt = """
You are Rainbow Bridge, a magical AI companion specially designed for special needs children, 
particularly those with autism and communication challenges. Your mission is to create joyful, 
colorful communication experiences that celebrate every child's unique journey.

CORE PERSONALITY:
- 🌈 Magical, patient, and eternally optimistic
- 🎨 Use colorful language and rainbow/star emojis
- 💝 Celebrate every small achievement enthusiastically
- 🤗 Always encouraging and supportive
- 📚 Make learning feel like an adventure

COMMUNICATION STYLE:
- Use simple, clear language appropriate for the child's level
- Include visual emojis and symbols
- Keep responses warm but concise
- Always validate feelings and efforts
- Make every interaction feel special and magical

ROUTINE SUPPORT:
- When a routine is active, ALWAYS mention the current activity
- Provide gentle guidance and encouragement
- Celebrate completions with enthusiasm
- Help break down tasks into manageable steps
"""
    
    def get_system_prompt(self, child: Child, context: Dict[str, Any]) -> str:
        """Generate a system prompt customized for the child and context."""
        
        prompt = self.base_system_prompt
        
        # Add child-specific information
        if child:
            prompt += f"\n\nCHILD PROFILE:"
            prompt += f"\n- Name: {child.name}"
            prompt += f"\n- Age: {child.age}"
            prompt += f"\n- Communication Level: {child.communication_level.value}"
            
            if child.interests:
                prompt += f"\n- Interests: {', '.join(child.interests)}"
            
            if child.special_needs:
                prompt += f"\n- Special Considerations: {', '.join(child.special_needs)}"
        
        # Add context information
        if context.get('has_active_routine'):
            prompt += f"\n\nCURRENT ROUTINE CONTEXT:"
            prompt += f"\n- Routine: {context.get('routine_name', 'Unknown')}"
            prompt += f"\n- Progress: {context.get('progress_percentage', 0)}%"
            prompt += f"\n- Completed: {context.get('completed_activities', 0)}/{context.get('total_activities', 0)} activities"
            
            current_activity = context.get('current_activity')
            if current_activity:
                prompt += f"\n- Current Activity: {current_activity['name']}"
                prompt += f"\n\nIMPORTANT: ALWAYS include the current activity name in your response!"
                prompt += f"\nFormat: 🎯 **Current Activity:** {current_activity['name']}"
        
        prompt += "\n\nRemember: Be magical, encouraging, and always include current activity context when relevant!"
        
        return prompt
    
    def get_user_prompt(
        self, 
        message: str, 
        mcp_result: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> str:
        """Generate a user prompt with message analysis."""
        
        prompt = f"Child's message: \"{message}\""
        
        # Add MCP analysis results
        if mcp_result:
            intent = mcp_result.get('intent', 'general_chat')
            prompt += f"\n\nMessage Analysis:"
            prompt += f"\n- Intent: {intent}"
            
            if mcp_result.get('completion_detected'):
                prompt += f"\n- Completion detected: Yes"
                
                extracted_activity = mcp_result.get('extracted_activity')
                if extracted_activity:
                    prompt += f"\n- Activity mentioned: {extracted_activity}"
                    prompt += f"\n\nThe child has completed '{extracted_activity}'! Celebrate this achievement!"
            
            confidence = mcp_result.get('confidence', 0)
            if confidence > 0.5:
                prompt += f"\n- Confidence: High ({confidence:.1f})"
        
        # Add response instructions based on context
        if context.get('has_active_routine'):
            current_activity = context.get('current_activity')
            if current_activity:
                prompt += f"\n\nResponse Requirements:"
                prompt += f"\n- MUST include: 🎯 **Current Activity:** {current_activity['name']}"
                prompt += f"\n- Encourage progress on current activity"
                prompt += f"\n- Use magical, colorful language"
        
        return prompt
    
    def get_completion_celebration_prompt(
        self, 
        activity_name: str, 
        next_activity: str = None
    ) -> str:
        """Generate a celebration prompt for activity completion."""
        
        prompt = f"🎉 The child just completed '{activity_name}'! Create a magical celebration response that:"
        prompt += f"\n- Enthusiastically celebrates the achievement"
        prompt += f"\n- Uses rainbow and star emojis"
        prompt += f"\n- Acknowledges their hard work"
        
        if next_activity:
            prompt += f"\n- Gently introduces the next activity: '{next_activity}'"
            prompt += f"\n- MUST include: 🎯 **Current Activity:** {next_activity}"
        else:
            prompt += f"\n- Celebrates completing the entire routine!"
        
        prompt += f"\n\nMake it feel like a magical moment! 🌈✨"
        
        return prompt
    
    def get_help_prompt(self, child: Child, context: Dict[str, Any]) -> str:
        """Generate a prompt for help requests."""
        
        prompt = "The child is asking for help. Provide:"
        prompt += "\n- Gentle, encouraging guidance"
        prompt += "\n- Break down any tasks into simple steps"
        prompt += "\n- Use visual language and emojis"
        prompt += "\n- Remind them they're doing great"
        
        if context.get('has_active_routine'):
            current_activity = context.get('current_activity')
            if current_activity:
                prompt += f"\n- Focus help on current activity: {current_activity['name']}"
                prompt += f"\n- MUST include: 🎯 **Current Activity:** {current_activity['name']}"
        
        return prompt
    
    def get_routine_start_prompt(self, routine_name: str) -> str:
        """Generate a prompt for routine start celebrations."""
        
        prompt = f"The child is starting their '{routine_name}' routine! Create a magical start message that:"
        prompt += f"\n- Celebrates the beginning with enthusiasm"
        prompt += f"\n- Uses colorful, encouraging language"
        prompt += f"\n- Makes them excited about the routine"
        prompt += f"\n- Uses rainbow emojis and magical elements"
        prompt += f"\n\nMake starting this routine feel like the beginning of a wonderful adventure! 🌈✨"
        
        return prompt
