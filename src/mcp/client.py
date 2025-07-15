"""
MCP (Model Context Protocol) Client for Rainbow Bridge
Handles communication with MCP servers for routine management and intent detection.
"""

import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import re
from difflib import SequenceMatcher

from src.models.entities import Routine, Activity, RoutineStatus, ActivityStatus
from src.services.database import DatabaseService
from config.settings import config

logger = logging.getLogger(__name__)


class MCPClient:
    """Client for communicating with MCP servers and handling intent detection."""
    
    def __init__(self, database_service: DatabaseService):
        self.db = database_service
        self.mcp_config = config.mcp
        
        # Intent detection patterns
        self.completion_phrases = [
            "done", "finished", "complete", "completed", "all done",
            "i'm done", "i finished", "i completed", "i'm finished",
            "that's done", "got it done", "all finished"
        ]
        
        self.general_activity_patterns = [
            r"i\s+(woke up|got up|wake up)",
            r"i\s+(got dressed|dressed|put on clothes)",
            r"i\s+(ate|eat|had)\s+(breakfast|lunch|dinner|food)",
            r"i\s+(brushed|brush)\s+(teeth|my teeth)",
            r"i\s+(washed|wash)\s+(hands|face|my hands|my face)",
            r"i\s+(took|take)\s+a\s+(shower|bath)",
            r"i\s+(did|do)\s+(homework|work|exercise)"
        ]
    
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
            completion_detected = self._detect_completion_intent(normalized_message)
            
            # Extract activity from message
            extracted_activity = None
            if completion_detected or context.get('has_active_routine'):
                extracted_activity = await self._extract_activity_from_message(
                    normalized_message, context
                )
            
            # Determine intent
            intent = self._determine_intent(
                normalized_message, completion_detected, 
                extracted_activity, context
            )
            
            # Build result
            result = {
                'intent': intent,
                'completion_detected': completion_detected,
                'extracted_activity': extracted_activity,
                'confidence': self._calculate_confidence(
                    normalized_message, completion_detected, extracted_activity
                ),
                'processing_timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"MCP processed message: {message} -> {result}")
            return result
            
        except Exception as e:
            logger.error(f"MCP processing error: {e}")
            return {
                'intent': 'general_chat',
                'completion_detected': False,
                'extracted_activity': None,
                'confidence': 0.0,
                'error': str(e)
            }
    
    def _detect_completion_intent(self, message: str) -> bool:
        """Detect if the message indicates task completion."""
        
        # Check for explicit completion phrases
        for phrase in self.completion_phrases:
            if phrase in message:
                return True
        
        # Check for general activity patterns
        for pattern in self.general_activity_patterns:
            if re.search(pattern, message):
                return True
        
        # Check for past tense verbs indicating completion
        past_tense_patterns = [
            r"\b\w+ed\b",  # Regular past tense
            r"\b(went|did|had|got|took|made|ate|drank|wore|saw)\b"  # Irregular past tense
        ]
        
        for pattern in past_tense_patterns:
            if re.search(pattern, message):
                return True
        
        return False
    
    async def _extract_activity_from_message(
        self, 
        message: str, 
        context: Dict[str, Any]
    ) -> Optional[str]:
        """Extract activity name from the message using fuzzy matching."""
        
        if not context.get('has_active_routine'):
            return None
        
        routine_id = context.get('routine_id')
        if not routine_id:
            return None
        
        # Get routine activities
        routine = await self.db.get_routine(routine_id)
        if not routine:
            return None
        
        activity_names = [activity.name for activity in routine.activities]
        
        # Direct keyword matching
        extracted_activity = self._match_activity_keywords(message, activity_names)
        if extracted_activity:
            return extracted_activity
        
        # Fuzzy matching
        best_match = self._fuzzy_match_activity(message, activity_names)
        if best_match:
            return best_match
        
        # Current activity fallback
        current_activity = context.get('current_activity')
        if current_activity and self._is_referring_to_current_activity(message):
            return current_activity['name']
        
        return None
    
    def _match_activity_keywords(self, message: str, activity_names: List[str]) -> Optional[str]:
        """Match activities using keyword extraction."""
        
        # Extract key words from message
        words = re.findall(r'\b\w+\b', message.lower())
        
        for activity_name in activity_names:
            activity_words = re.findall(r'\b\w+\b', activity_name.lower())
            
            # Check if any activity words are in the message
            for activity_word in activity_words:
                if len(activity_word) > 3:  # Ignore short words
                    for word in words:
                        if activity_word in word or word in activity_word:
                            return activity_name
        
        return None
    
    def _fuzzy_match_activity(self, message: str, activity_names: List[str]) -> Optional[str]:
        """Use fuzzy matching to find the best activity match."""
        
        best_match = None
        best_score = 0.0
        threshold = 0.3
        
        for activity_name in activity_names:
            # Calculate similarity
            score = SequenceMatcher(None, message, activity_name.lower()).ratio()
            
            # Check individual words
            message_words = message.split()
            activity_words = activity_name.lower().split()
            
            for msg_word in message_words:
                for act_word in activity_words:
                    word_score = SequenceMatcher(None, msg_word, act_word).ratio()
                    score = max(score, word_score)
            
            if score > best_score and score > threshold:
                best_score = score
                best_match = activity_name
        
        logger.debug(f"Fuzzy match for '{message}': {best_match} (score: {best_score})")
        return best_match
    
    def _is_referring_to_current_activity(self, message: str) -> bool:
        """Check if the message is referring to the current activity."""
        
        current_references = [
            "this", "that", "it", "current", "now", "doing"
        ]
        
        for ref in current_references:
            if ref in message:
                return True
        
        return False
    
    def _determine_intent(
        self, 
        message: str, 
        completion_detected: bool, 
        extracted_activity: Optional[str],
        context: Dict[str, Any]
    ) -> str:
        """Determine the intent based on analysis results."""
        
        if completion_detected and extracted_activity:
            return 'complete_activity'
        
        if "start" in message and ("routine" in message or "begin" in message):
            return 'start_routine'
        
        if "create" in message and "routine" in message:
            return 'create_routine'
        
        if any(word in message for word in ["help", "stuck", "don't know"]):
            return 'request_help'
        
        return 'general_chat'
    
    def _calculate_confidence(
        self, 
        message: str, 
        completion_detected: bool, 
        extracted_activity: Optional[str]
    ) -> float:
        """Calculate confidence score for the intent detection."""
        
        confidence = 0.0
        
        # Base confidence for completion detection
        if completion_detected:
            confidence += 0.5
        
        # Boost confidence if activity was extracted
        if extracted_activity:
            confidence += 0.3
        
        # Boost for explicit phrases
        for phrase in self.completion_phrases:
            if phrase in message:
                confidence += 0.2
                break
        
        return min(confidence, 1.0)
    
    async def complete_activity(self, routine_id: int, activity_name: str) -> Dict[str, Any]:
        """Complete an activity in a routine and return detailed result."""
        
        try:
            routine = await self.db.get_routine(routine_id)
            if not routine:
                return {'success': False, 'error': 'Routine not found'}
            
            # Find the activity to complete
            activity_to_complete = None
            activity_index = -1
            
            # First, try to find by exact name match
            for i, activity in enumerate(routine.activities):
                if activity.name.lower().strip() == activity_name.lower().strip():
                    activity_to_complete = activity
                    activity_index = i
                    break
            
            # If not found, try fuzzy matching
            if not activity_to_complete:
                best_match = self._fuzzy_match_activity(activity_name, 
                    [a.name for a in routine.activities])
                if best_match:
                    for i, activity in enumerate(routine.activities):
                        if activity.name == best_match:
                            activity_to_complete = activity
                            activity_index = i
                            break
            
            # If still not found, try current activity
            if not activity_to_complete and routine.current_activity_index < len(routine.activities):
                current_activity = routine.activities[routine.current_activity_index]
                if current_activity.status != ActivityStatus.COMPLETED:
                    activity_to_complete = current_activity
                    activity_index = routine.current_activity_index
            
            if not activity_to_complete:
                return {
                    'success': False, 
                    'error': f'Activity "{activity_name}" not found or already completed'
                }
            
            # Mark activity as completed in database
            await self.db.update_activity_status(
                activity_to_complete.id, 
                'completed', 
                datetime.now()
            )
            
            # Update local status
            activity_to_complete.status = ActivityStatus.COMPLETED
            activity_to_complete.completed_at = datetime.now()
            
            # Calculate new progress
            completed_count = sum(
                1 for a in routine.activities 
                if a.status == ActivityStatus.COMPLETED or a.id == activity_to_complete.id
            )
            total_count = len(routine.activities)
            progress_percentage = (completed_count / total_count * 100)
            
            # Determine next activity and update routine
            next_activity = None
            next_activity_index = routine.current_activity_index
            
            if completed_count >= total_count:
                # All activities completed
                await self.db.update_routine_status(routine_id, 'completed')
                routine.status = RoutineStatus.COMPLETED
                routine.completed_at = datetime.now()
            else:
                # Find next incomplete activity
                for i in range(activity_index + 1, len(routine.activities)):
                    if routine.activities[i].status != ActivityStatus.COMPLETED:
                        next_activity = routine.activities[i]
                        next_activity_index = i
                        break
                
                # Update routine's current activity index
                await self.db.update_routine_status(routine_id, 'active', next_activity_index)
                routine.current_activity_index = next_activity_index
            
            # Log activity completion
            from src.models.entities import ActivityLog
            activity_log = ActivityLog(
                child_id=routine.child_id,
                routine_id=routine.id,
                activity_id=activity_to_complete.id,
                activity_name=activity_to_complete.name,
                completed_at=datetime.now(),
                duration_minutes=5  # Default duration, could be calculated
            )
            await self.db.log_activity_completion(activity_log)
            
            result = {
                'success': True,
                'completed_activity': {
                    'name': activity_to_complete.name,
                    'index': activity_index
                },
                'next_activity': {
                    'name': next_activity.name,
                    'index': next_activity_index
                } if next_activity else None,
                'progress': {
                    'completed_count': completed_count,
                    'total_count': total_count,
                    'percentage': round(progress_percentage, 1),
                    'remaining_count': total_count - completed_count
                },
                'routine_completed': completed_count >= total_count,
                'routine_status': routine.status.value
            }
            
            logger.info(f"Activity completed: {activity_to_complete.name} ({completed_count}/{total_count})")
            return result
            
        except Exception as e:
            logger.error(f"Error completing activity: {e}")
            return {'success': False, 'error': str(e)}
    
    async def start_routine(self, child_id: int, routine_name: str) -> Dict[str, Any]:
        """Start a routine for a child with proper state management."""
        
        try:
            routines = await self.db.get_child_routines(child_id)
            
            # Find routine by name (fuzzy matching if needed)
            routine_to_start = None
            for routine in routines:
                if routine.name.lower().strip() == routine_name.lower().strip():
                    routine_to_start = routine
                    break
            
            # Try fuzzy matching if exact match not found
            if not routine_to_start:
                best_match = self._fuzzy_match_routine_name(routine_name, [r.name for r in routines])
                if best_match:
                    routine_to_start = next(r for r in routines if r.name == best_match)
            
            if not routine_to_start:
                return {
                    'success': False,
                    'error': f'Routine "{routine_name}" not found'
                }
            
            # Stop any other active routines for this child
            for routine in routines:
                if routine.status == RoutineStatus.ACTIVE and routine.id != routine_to_start.id:
                    await self.db.update_routine_status(routine.id, 'inactive')
            
            # Start the routine in database
            await self.db.update_routine_status(routine_to_start.id, 'active', 0)
            
            # Reset all activities in database
            for activity in routine_to_start.activities:
                await self.db.update_activity_status(activity.id, 'not_started')
                activity.status = ActivityStatus.NOT_STARTED
                activity.completed_at = None
            
            # Update local routine object
            routine_to_start.status = RoutineStatus.ACTIVE
            routine_to_start.started_at = datetime.now()
            routine_to_start.current_activity_index = 0
            
            first_activity = routine_to_start.activities[0] if routine_to_start.activities else None
            
            result = {
                'success': True,
                'routine': {
                    'id': routine_to_start.id,
                    'name': routine_to_start.name,
                    'status': 'active'
                },
                'first_activity': {
                    'name': first_activity.name,
                    'index': 0
                } if first_activity else None,
                'total_activities': len(routine_to_start.activities),
                'started_at': routine_to_start.started_at.isoformat()
            }
            
            logger.info(f"Routine started: {routine_name} for child {child_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error starting routine: {e}")
            return {'success': False, 'error': str(e)}
    
    def _fuzzy_match_routine_name(self, routine_name: str, available_routines: List[str]) -> Optional[str]:
        """Fuzzy match routine names."""
        from difflib import SequenceMatcher
        
        best_match = None
        best_score = 0.0
        threshold = 0.6
        
        for available_routine in available_routines:
            score = SequenceMatcher(None, routine_name.lower(), available_routine.lower()).ratio()
            if score > best_score and score > threshold:
                best_score = score
                best_match = available_routine
        
        return best_match
