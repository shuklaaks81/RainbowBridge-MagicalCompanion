"""
Data models for Rainbow Bridge
Contains all data models, schemas, and database entities.
"""

from dataclasses import dataclass, field
from datetime import datetime, time
from typing import List, Dict, Optional, Any
from enum import Enum


class CommunicationLevel(Enum):
    """Communication level options for children."""
    EMERGING = "emerging"
    DEVELOPING = "developing"
    MODERATE = "moderate"
    ADVANCED = "advanced"


class ActivityStatus(Enum):
    """Status options for activities."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"


class RoutineStatus(Enum):
    """Status options for routines."""
    INACTIVE = "inactive"
    ACTIVE = "active"
    COMPLETED = "completed"
    PAUSED = "paused"


@dataclass
class Child:
    """Child profile model."""
    id: Optional[int] = None
    name: str = ""
    age: int = 0
    communication_level: CommunicationLevel = CommunicationLevel.EMERGING
    interests: List[str] = field(default_factory=list)
    special_needs: List[str] = field(default_factory=list)
    preferences: Dict[str, Any] = field(default_factory=dict)
    profile_picture: str = "default.svg"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class Activity:
    """Activity model for routines."""
    id: Optional[int] = None
    name: str = ""
    description: str = ""
    estimated_duration: int = 5  # minutes
    visual_cue: Optional[str] = None
    audio_cue: Optional[str] = None
    instructions: List[str] = field(default_factory=list)
    status: ActivityStatus = ActivityStatus.NOT_STARTED
    completed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None


@dataclass
class Routine:
    """Routine model containing multiple activities."""
    id: Optional[int] = None
    child_id: int = 0
    name: str = ""
    description: str = ""
    activities: List[Activity] = field(default_factory=list)
    schedule_time: Optional[time] = None
    days_of_week: List[str] = field(default_factory=list)
    status: RoutineStatus = RoutineStatus.INACTIVE
    current_activity_index: int = 0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class Interaction:
    """Interaction log model."""
    id: Optional[int] = None
    child_id: int = 0
    message: str = ""
    ai_response: str = ""
    communication_type: str = "text"  # text, visual, audio
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: Optional[datetime] = None
    routine_id: Optional[int] = None
    activity_id: Optional[int] = None


@dataclass
class Milestone:
    """Milestone achievement model."""
    id: Optional[int] = None
    child_id: int = 0
    title: str = ""
    description: str = ""
    category: str = ""  # communication, routine, social, etc.
    achieved_at: Optional[datetime] = None
    data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProgressReport:
    """Progress report model."""
    child_id: int
    start_date: datetime
    end_date: datetime
    total_interactions: int = 0
    routines_completed: int = 0
    milestones_achieved: int = 0
    communication_improvements: Dict[str, Any] = field(default_factory=dict)
    routine_adherence: float = 0.0
    engagement_score: float = 0.0


@dataclass
class ActivityLog:
    """Activity completion log model."""
    id: Optional[int] = None
    child_id: int = 0
    routine_id: int = 0
    activity_id: int = 0
    activity_name: str = ""
    completed_at: datetime = field(default_factory=datetime.now)
    duration_minutes: Optional[int] = None
    notes: str = ""
    satisfaction_level: Optional[int] = None  # 1-5 scale


@dataclass
class VisualCard:
    """Visual communication card model."""
    id: Optional[int] = None
    name: str = ""
    category: str = ""
    image_path: str = ""
    description: str = ""
    keywords: List[str] = field(default_factory=list)
    is_custom: bool = False
    child_id: Optional[int] = None
    created_at: Optional[datetime] = None


@dataclass
class ChatContext:
    """Chat context for maintaining conversation state."""
    child_id: int
    current_routine_id: Optional[int] = None
    current_activity_index: int = 0
    communication_mode: str = "text"
    last_interaction: Optional[datetime] = None
    context_data: Dict[str, Any] = field(default_factory=dict)


# API Response Models
@dataclass
class APIResponse:
    """Base API response model."""
    success: bool = True
    message: str = ""
    data: Any = None
    error: Optional[str] = None


@dataclass
class ChatResponse:
    """Chat API response model."""
    message: str
    text: str
    visual_cards: List[Dict[str, Any]] = field(default_factory=list)
    audio_response: Optional[str] = None
    routine_action: Optional[str] = None
    current_activity_context: Optional[Dict[str, Any]] = None
    suggestions: List[str] = field(default_factory=list)


@dataclass
class RoutineStatusResponse:
    """Routine status API response model."""
    routine_id: int
    name: str
    status: str
    progress_percentage: float
    current_activity: Optional[str]
    completed_activities: int
    total_activities: int
    started_at: Optional[str] = None
    estimated_completion: Optional[str] = None
