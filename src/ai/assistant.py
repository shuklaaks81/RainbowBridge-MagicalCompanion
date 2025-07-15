"""
AI Assistant service for Rainbow Bridge
Handles AI-powered communication and response generation.
"""

import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

from src.models.entities import Child, ChatResponse, ChatContext
from src.services.database import DatabaseService
from src.mcp.client import MCPClient
from src.utils.ai_prompts import AIPrompts
from src.utils.response_formatter import ResponseFormatter
from config.settings import config

logger = logging.getLogger(__name__)


class AIAssistantService:
    """Service for handling AI-powered communication and assistance."""
    
    def __init__(self, database_service: DatabaseService, mcp_client: MCPClient):
        self.db = database_service
        self.mcp_client = mcp_client
        self.prompts = AIPrompts()
        self.formatter = ResponseFormatter()
        
        # AI configuration
        self.ai_config = config.ai
        self.max_tokens = self.ai_config.max_tokens
        self.temperature = self.ai_config.temperature
    
    async def process_message(
        self, 
        child_id: int, 
        message: str, 
        communication_type: str = "text",
        context: Optional[Dict[str, Any]] = None
    ) -> ChatResponse:
        """Process a message from a child and generate an appropriate response."""
        
        try:
            # Get child profile
            child = await self.db.get_child_profile(child_id)
            if not child:
                raise ValueError(f"Child profile not found: {child_id}")
            
            # Get current routine context
            current_context = await self._get_current_context(child_id)
            
            # Merge with any passed context
            if context:
                current_context.update(context)
            
            # Detect intent and extract information using MCP
            mcp_result = await self.mcp_client.process_message(
                message, child_id, current_context
            )
            
            # Handle routine actions if detected (do this first to get updated context)
            routine_action_result = None
            if mcp_result.get('intent') in ['complete_activity', 'start_routine']:
                routine_action_result = await self._handle_routine_action(
                    child_id, mcp_result, current_context
                )
            
            # Get updated context after any routine actions
            updated_context = await self._get_current_context(child_id)
            
            # Generate AI response with enhanced context
            ai_response = await self._generate_ai_response(
                child, message, updated_context, mcp_result, routine_action_result
            )
            
            # Format the response
            formatted_response = self.formatter.format_response(
                ai_response, 
                child, 
                updated_context,
                routine_action_result
            )
            
            # Log the interaction
            await self._log_interaction(
                child_id, message, formatted_response, 
                communication_type, updated_context, mcp_result
            )
            
            return ChatResponse(
                message=formatted_response,
                text=formatted_response,
                routine_action=routine_action_result.get('action') if routine_action_result else None,
                current_activity_context=updated_context,
                suggestions=self._generate_suggestions(child, updated_context)
            )
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return ChatResponse(
                message="I'm having trouble understanding right now. Let me try again! 🌈",
                text="I'm having trouble understanding right now. Let me try again! 🌈",
                error=str(e)
            )
    
    async def _get_current_context(self, child_id: int) -> Dict[str, Any]:
        """Get the current context for a child including active routines with accurate progress."""
        
        # Get routine progress from database
        routines = await self.db.get_child_routines(child_id)
        active_routine = next(
            (r for r in routines if r.status.value == 'active'), None
        )
        
        context = {
            'child_id': child_id,
            'has_active_routine': active_routine is not None,
            'progress_percentage': 0,
            'remaining_activities': 0
        }
        
        if active_routine:
            # Get accurate progress from database
            progress_data = await self.db.get_routine_progress(active_routine.id)
            
            current_activity = progress_data.get('current_activity')
            
            context.update({
                'routine_id': active_routine.id,
                'routine_name': active_routine.name,
                'current_activity': current_activity,
                'progress_percentage': progress_data.get('progress_percentage', 0),
                'completed_activities': progress_data.get('completed_activities', 0),
                'total_activities': progress_data.get('total_activities', 0),
                'remaining_activities': progress_data.get('total_activities', 0) - progress_data.get('completed_activities', 0),
                'activities_list': progress_data.get('activities', [])
            })
        
        return context
    
    async def _generate_ai_response(
        self, 
        child: Child, 
        message: str, 
        context: Dict[str, Any],
        mcp_result: Dict[str, Any],
        routine_action_result: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate an AI response using the configured AI service with enhanced context."""
        
        # Build the prompt with routine action results
        system_prompt = self.prompts.get_system_prompt(child, context)
        user_prompt = self.prompts.get_user_prompt(message, mcp_result, context, routine_action_result)
        
        # Get AI response based on configuration
        if self.ai_config.use_local_llm:
            return await self._get_local_llm_response(system_prompt, user_prompt)
        else:
            return await self._get_openai_response(system_prompt, user_prompt)
    
    async def _get_openai_response(self, system_prompt: str, user_prompt: str) -> str:
        """Get response from OpenAI API."""
        try:
            from openai import AsyncOpenAI
            
            if not self.ai_config.openai_api_key:
                raise ValueError("OpenAI API key not configured")
            
            # Initialize the new OpenAI client
            client = AsyncOpenAI(api_key=self.ai_config.openai_api_key)
            
            # Use the new chat completions API
            response = await client.chat.completions.create(
                model=self.ai_config.openai_model or "gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return "I'm having trouble with my AI right now. Let me help you anyway! 🌈"
    
    async def _get_local_llm_response(self, system_prompt: str, user_prompt: str) -> str:
        """Get response from local LLM."""
        try:
            import aiohttp
            
            async with aiohttp.ClientSession() as session:
                payload = {
                    "model": self.ai_config.local_llm_model,
                    "prompt": f"{system_prompt}\n\nUser: {user_prompt}\nAssistant:",
                    "max_tokens": self.max_tokens,
                    "temperature": self.temperature
                }
                
                async with session.post(
                    f"{self.ai_config.local_llm_url}/api/generate",
                    json=payload
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get('response', '').strip()
                    else:
                        raise Exception(f"Local LLM API error: {response.status}")
                        
        except Exception as e:
            logger.error(f"Local LLM error: {e}")
            return "I'm having trouble with my local AI. Let me help you anyway! 🌈"
    
    async def _handle_routine_action(
        self, 
        child_id: int, 
        mcp_result: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Handle routine-related actions with detailed results."""
        
        intent = mcp_result.get('intent')
        
        if intent == 'complete_activity':
            activity_name = mcp_result.get('extracted_activity')
            routine_id = context.get('routine_id')
            
            if routine_id and activity_name:
                completion_result = await self.mcp_client.complete_activity(
                    routine_id, activity_name
                )
                
                if completion_result.get('success'):
                    return {
                        'action': 'complete_activity',
                        'result': completion_result
                    }
                else:
                    return {
                        'action': 'complete_activity_failed',
                        'error': completion_result.get('error')
                    }
        
        elif intent == 'start_routine':
            routine_name = mcp_result.get('extracted_routine')
            if routine_name:
                start_result = await self.mcp_client.start_routine(
                    child_id, routine_name
                )
                
                if start_result.get('success'):
                    return {
                        'action': 'start_routine',
                        'result': start_result
                    }
                else:
                    return {
                        'action': 'start_routine_failed',
                        'error': start_result.get('error')
                    }
        
        return None
    
    async def _log_interaction(
        self,
        child_id: int,
        message: str,
        ai_response: str,
        communication_type: str,
        context: Dict[str, Any],
        mcp_result: Dict[str, Any]
    ):
        """Log the interaction to the database."""
        
        try:
            from src.models.entities import Interaction
            
            interaction = Interaction(
                child_id=child_id,
                message=message,
                ai_response=ai_response,
                communication_type=communication_type,
                context={
                    'mcp_result': mcp_result,
                    'current_context': context
                },
                routine_id=context.get('routine_id'),
                activity_id=context.get('current_activity', {}).get('id')
            )
            
            await self.db.log_interaction(interaction)
            
        except Exception as e:
            logger.error(f"Failed to log interaction: {e}")
    
    def _generate_suggestions(
        self, 
        child: Child, 
        context: Dict[str, Any]
    ) -> List[str]:
        """Generate helpful suggestions based on context."""
        
        suggestions = []
        
        if context.get('has_active_routine'):
            current_activity = context.get('current_activity')
            if current_activity:
                suggestions.extend([
                    f"Let me know when you finish {current_activity['name']}!",
                    "Need help with your current activity?",
                    "You're doing great! Keep going!"
                ])
        else:
            suggestions.extend([
                "Would you like to start a routine?",
                "Tell me about your day!",
                "What would you like to do?"
            ])
        
        return suggestions[:3]  # Limit to 3 suggestions
