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
    
    async def complete_activity(self, routine_id: int, activity_name: str) -> bool:
        """Complete an activity in a routine."""
        
        try:
            routine = await self.db.get_routine(routine_id)
            if not routine:
                return False
            
            # Find the activity to complete
            activity_to_complete = None
            for i, activity in enumerate(routine.activities):
                if activity.name.lower() == activity_name.lower():
                    activity_to_complete = activity
                    break
            
            if not activity_to_complete:
                # Try fuzzy matching
                best_match = self._fuzzy_match_activity(activity_name, 
                    [a.name for a in routine.activities])
                if best_match:
                    activity_to_complete = next(
                        a for a in routine.activities if a.name == best_match
                    )
            
            if not activity_to_complete:
                logger.warning(f"Activity not found: {activity_name}")
                return False
            
            # Mark activity as completed
            activity_to_complete.status = ActivityStatus.COMPLETED
            activity_to_complete.completed_at = datetime.now()
            
            # Update routine progress
            completed_count = sum(
                1 for a in routine.activities 
                if a.status == ActivityStatus.COMPLETED
            )
            
            if completed_count >= len(routine.activities):
                routine.status = RoutineStatus.COMPLETED
                routine.completed_at = datetime.now()
            else:
                # Update current activity index
                for i, activity in enumerate(routine.activities):
                    if activity.status != ActivityStatus.COMPLETED:
                        routine.current_activity_index = i
                        break
            
            # Log activity completion
            from src.models.entities import ActivityLog
            activity_log = ActivityLog(
                child_id=routine.child_id,
                routine_id=routine.id,
                activity_id=activity_to_complete.id,
                activity_name=activity_to_complete.name,
                completed_at=datetime.now()
            )
            await self.db.log_activity_completion(activity_log)
            
            logger.info(f"Activity completed: {activity_name} in routine {routine_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error completing activity: {e}")
            return False
    
    async def start_routine(self, child_id: int, routine_name: str) -> bool:
        """Start a routine for a child."""
        
        try:
            routines = await self.db.get_child_routines(child_id)
            
            # Find routine by name
            routine_to_start = None
            for routine in routines:
                if routine.name.lower() == routine_name.lower():
                    routine_to_start = routine
                    break
            
            if not routine_to_start:
                logger.warning(f"Routine not found: {routine_name}")
                return False
            
            # Start the routine
            routine_to_start.status = RoutineStatus.ACTIVE
            routine_to_start.started_at = datetime.now()
            routine_to_start.current_activity_index = 0
            
            # Reset all activities
            for activity in routine_to_start.activities:
                activity.status = ActivityStatus.NOT_STARTED
                activity.completed_at = None
            
            logger.info(f"Routine started: {routine_name} for child {child_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error starting routine: {e}")
            return False
