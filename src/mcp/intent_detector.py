"""
Intent detection service for Rainbow Bridge
Handles intent detection and message analysis using MCP patterns.
"""

import re
from typing import Dict, List, Optional, Any
from datetime import datetime
from difflib import SequenceMatcher
import logging

logger = logging.getLogger(__name__)


class IntentDetector:
    """Service for detecting user intents and extracting information from messages."""
    
    def __init__(self):
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
        
        self.start_routine_phrases = [
            "start", "begin", "let's start", "let's begin", "time to start",
            "ready to start", "ready to begin", "can we start"
        ]
    
    def detect_completion_intent(self, message: str) -> bool:
        """Detect if the message indicates activity completion."""
        normalized = message.lower().strip()
        
        # Check for explicit completion phrases
        for phrase in self.completion_phrases:
            if phrase in normalized:
                return True
        
        # Check for activity completion patterns
        for pattern in self.general_activity_patterns:
            if re.search(pattern, normalized):
                return True
        
        return False
    
    def detect_start_routine_intent(self, message: str) -> bool:
        """Detect if the message indicates wanting to start a routine."""
        normalized = message.lower().strip()
        
        for phrase in self.start_routine_phrases:
            if phrase in normalized:
                return True
        
        # Check for routine-specific start patterns
        routine_start_patterns = [
            r"(start|begin|do)\s+(my\s+)?(morning|evening|bedtime|daily)\s+(routine|activities)",
            r"ready\s+for\s+(morning|evening|bedtime|daily)",
            r"time\s+for\s+(morning|evening|bedtime|daily)"
        ]
        
        for pattern in routine_start_patterns:
            if re.search(pattern, normalized):
                return True
        
        return False
    
    def extract_activity_from_message(self, message: str, context: Dict[str, Any]) -> Optional[str]:
        """Extract activity name from the message."""
        normalized = message.lower().strip()
        
        # If there's an active routine, try to match against its activities
        if context.get('has_active_routine'):
            current_routine = context.get('current_routine')
            if current_routine and current_routine.get('activities'):
                activity_names = [a['name'] for a in current_routine['activities']]
                
                # Try exact word matching first
                for activity_name in activity_names:
                    activity_words = activity_name.lower().split()
                    if any(word in normalized for word in activity_words):
                        return activity_name
                
                # Try fuzzy matching
                best_match = self.fuzzy_match_activity(normalized, activity_names)
                if best_match:
                    return best_match
        
        # Extract from general activity patterns
        for pattern in self.general_activity_patterns:
            match = re.search(pattern, normalized)
            if match:
                return self._normalize_extracted_activity(match.group())
        
        return None
    
    def extract_routine_name_from_message(self, message: str, available_routines: List[str]) -> Optional[str]:
        """Extract routine name from start routine message."""
        normalized = message.lower().strip()
        
        # Try exact matching first
        for routine_name in available_routines:
            if routine_name.lower() in normalized:
                return routine_name
        
        # Try fuzzy matching
        return self.fuzzy_match_routine_name(normalized, available_routines)
    
    def fuzzy_match_activity(self, activity_input: str, activity_list: List[str]) -> Optional[str]:
        """Find the best matching activity using fuzzy string matching."""
        if not activity_list:
            return None
        
        best_match = None
        best_ratio = 0.5  # Minimum threshold
        
        for activity in activity_list:
            # Try matching against full activity name
            ratio = SequenceMatcher(None, activity_input.lower(), activity.lower()).ratio()
            if ratio > best_ratio:
                best_ratio = ratio
                best_match = activity
            
            # Try matching against individual words
            activity_words = activity.lower().split()
            input_words = activity_input.lower().split()
            
            for activity_word in activity_words:
                for input_word in input_words:
                    if len(activity_word) > 3 and len(input_word) > 3:
                        ratio = SequenceMatcher(None, input_word, activity_word).ratio()
                        if ratio > 0.7 and ratio > best_ratio:
                            best_ratio = ratio
                            best_match = activity
        
        return best_match
    
    def fuzzy_match_routine_name(self, routine_input: str, routine_list: List[str]) -> Optional[str]:
        """Find the best matching routine using fuzzy string matching."""
        if not routine_list:
            return None
        
        best_match = None
        best_ratio = 0.6  # Higher threshold for routines
        
        for routine in routine_list:
            ratio = SequenceMatcher(None, routine_input.lower(), routine.lower()).ratio()
            if ratio > best_ratio:
                best_ratio = ratio
                best_match = routine
            
            # Check if routine name contains key words from input
            routine_words = routine.lower().split()
            input_words = routine_input.lower().split()
            
            common_words = set(routine_words) & set(input_words)
            if len(common_words) > 0 and len(common_words) / len(routine_words) > 0.5:
                if len(common_words) / len(routine_words) > best_ratio:
                    best_ratio = len(common_words) / len(routine_words)
                    best_match = routine
        
        return best_match
    
    def determine_intent(
        self, 
        message: str, 
        completion_detected: bool,
        extracted_activity: Optional[str],
        context: Dict[str, Any]
    ) -> str:
        """Determine the primary intent from the message."""
        
        # Priority order for intent detection
        if completion_detected and extracted_activity:
            return 'complete_activity'
        elif completion_detected and context.get('has_active_routine'):
            return 'complete_activity'
        elif self.detect_start_routine_intent(message):
            return 'start_routine'
        elif extracted_activity and context.get('has_active_routine'):
            return 'activity_inquiry'
        else:
            return 'general_chat'
    
    def calculate_confidence(
        self, 
        message: str, 
        completion_detected: bool,
        extracted_activity: Optional[str]
    ) -> float:
        """Calculate confidence score for intent detection."""
        confidence = 0.3  # Base confidence
        
        # Boost for explicit completion phrases
        if completion_detected:
            confidence += 0.4
        
        # Boost for extracted activity
        if extracted_activity:
            confidence += 0.3
        
        # Boost for clear intent indicators
        clear_indicators = ["done", "finished", "start", "begin", "complete"]
        for indicator in clear_indicators:
            if indicator in message.lower():
                confidence += 0.2
                break
        
        return min(confidence, 1.0)
    
    def _normalize_extracted_activity(self, extracted_text: str) -> str:
        """Normalize extracted activity text to a standard format."""
        # Remove "i" and common prefixes
        normalized = re.sub(r'^i\s+', '', extracted_text.lower())
        normalized = re.sub(r'^(got|get|take|took|did|do)\s+', '', normalized)
        
        # Convert past tense to present/gerund form for consistency
        replacements = {
            'woke up': 'wake up',
            'got up': 'get up', 
            'got dressed': 'get dressed',
            'ate': 'eat',
            'had breakfast': 'eat breakfast',
            'had lunch': 'eat lunch',
            'had dinner': 'eat dinner',
            'brushed teeth': 'brush teeth',
            'brushed my teeth': 'brush teeth',
            'washed hands': 'wash hands',
            'washed my hands': 'wash hands',
            'took a shower': 'take a shower',
            'took a bath': 'take a bath'
        }
        
        for old, new in replacements.items():
            if old in normalized:
                normalized = normalized.replace(old, new)
                break
        
        return normalized.title()
