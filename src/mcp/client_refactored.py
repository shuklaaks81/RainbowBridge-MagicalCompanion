"""
MCP (Model Context Protocol) Client for Rainbow Bridge
Handles communication with MCP servers for routine management and intent detection.
"""

import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from src.services.database import DatabaseService
from src.mcp.intent_detector import IntentDetector
from src.mcp.routine_actions import RoutineActionHandler
from config.settings import config

logger = logging.getLogger(__name__)


class MCPClient:
    """Client for communicating with MCP servers and handling intent detection."""
    
    def __init__(self, database_service: DatabaseService):
        self.db = database_service
        self.intent_detector = IntentDetector()
        self.routine_handler = RoutineActionHandler(database_service)
        self.mcp_config = config.mcp
    
    async def process_message(
        self, 
        message: str, 
        child_id: int, 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process a message and detect intents using MCP tools."""
        
        try:
            # Normalize message
            normalized_message = message.lower().strip()
            
            # Detect completion intent
            completion_detected = self.intent_detector.detect_completion_intent(normalized_message)
            
            # Extract activity from message
            extracted_activity = None
            if completion_detected or context.get('has_active_routine'):
                extracted_activity = await self._extract_activity_from_message(
                    normalized_message, context
                )
            
            # Determine intent
            intent = self.intent_detector.determine_intent(
                normalized_message, completion_detected, 
                extracted_activity, context
            )
            
            # Build result
            result = {
                'intent': intent,
                'completion_detected': completion_detected,
                'extracted_activity': extracted_activity,
                'confidence': self.intent_detector.calculate_confidence(
                    normalized_message, completion_detected, extracted_activity
                ),
                'processing_timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"Processed message: intent={intent}, confidence={result['confidence']}")
            return result
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return {
                'intent': 'general_chat',
                'completion_detected': False,
                'extracted_activity': None,
                'confidence': 0.1,
                'error': str(e),
                'processing_timestamp': datetime.now().isoformat()
            }
    
    async def complete_activity(self, routine_id: int, activity_name: str) -> Dict[str, Any]:
        """Complete an activity in a routine and return detailed result."""
        return await self.routine_handler.complete_activity(routine_id, activity_name)
    
    async def start_routine(self, child_id: int, routine_name: str) -> Dict[str, Any]:
        """Start a routine for a child with proper state management."""
        return await self.routine_handler.start_routine(child_id, routine_name)
    
    async def get_routine_status(self, routine_id: int) -> Dict[str, Any]:
        """Get current status and progress of a routine."""
        return await self.routine_handler.get_routine_status(routine_id)
    
    async def pause_routine(self, routine_id: int) -> Dict[str, Any]:
        """Pause an active routine."""
        return await self.routine_handler.pause_routine(routine_id)
    
    async def resume_routine(self, routine_id: int) -> Dict[str, Any]:
        """Resume a paused routine."""
        return await self.routine_handler.resume_routine(routine_id)
    
    async def get_available_routines(self, child_id: int) -> Dict[str, Any]:
        """Get list of available routines for a child."""
        
        try:
            routines = await self.db.get_child_routines(child_id)
            
            routine_list = []
            for routine in routines:
                routine_info = {
                    'id': routine.id,
                    'name': routine.name,
                    'description': routine.description,
                    'category': routine.category,
                    'status': routine.status.value,
                    'total_activities': len(routine.activities),
                    'scheduled_time': routine.scheduled_time
                }
                
                # Add progress information if routine is active
                if routine.status.value == 'active':
                    progress = await self.db.get_routine_progress(routine.id)
                    routine_info['progress'] = progress
                
                routine_list.append(routine_info)
            
            return {
                'success': True,
                'routines': routine_list,
                'total_count': len(routine_list)
            }
            
        except Exception as e:
            logger.error(f"Error getting available routines: {e}")
            return {'success': False, 'error': str(e)}
    
    async def get_activity_suggestions(self, child_id: int, context: Dict[str, Any]) -> List[str]:
        """Get activity suggestions based on context and child profile."""
        
        try:
            suggestions = []
            
            # Get child's active routine
            active_routine = await self.db.get_active_routine(child_id)
            
            if active_routine:
                # Suggest next activity in routine
                if active_routine.current_activity_index < len(active_routine.activities):
                    current_activity = active_routine.activities[active_routine.current_activity_index]
                    suggestions.append(f"Continue with: {current_activity.name}")
                
                # Suggest upcoming activities
                for i in range(active_routine.current_activity_index + 1, 
                             min(active_routine.current_activity_index + 3, len(active_routine.activities))):
                    activity = active_routine.activities[i]
                    suggestions.append(f"Coming up: {activity.name}")
            
            else:
                # Suggest starting a routine
                routines = await self.db.get_child_routines(child_id)
                if routines:
                    # Suggest most recent or popular routines
                    for routine in routines[:3]:
                        suggestions.append(f"Start: {routine.name}")
            
            # Add general encouragement if no specific suggestions
            if not suggestions:
                suggestions = [
                    "Take a deep breath and relax",
                    "Do some stretching exercises",
                    "Practice counting to 10"
                ]
            
            return suggestions[:5]  # Limit to 5 suggestions
            
        except Exception as e:
            logger.error(f"Error getting activity suggestions: {e}")
            return ["Let's try something fun together!"]
    
    async def _extract_activity_from_message(
        self, 
        message: str, 
        context: Dict[str, Any]
    ) -> Optional[str]:
        """Extract activity name from message using context."""
        return self.intent_detector.extract_activity_from_message(message, context)
    
    async def get_mcp_health_status(self) -> Dict[str, Any]:
        """Get health status of MCP components."""
        
        try:
            # Test database connection
            children = await self.db.get_all_children()
            db_status = "healthy"
        except Exception as e:
            db_status = f"error: {str(e)}"
        
        return {
            'status': 'healthy' if db_status == 'healthy' else 'degraded',
            'components': {
                'database': db_status,
                'intent_detector': 'healthy',
                'routine_handler': 'healthy'
            },
            'timestamp': datetime.now().isoformat()
        }
