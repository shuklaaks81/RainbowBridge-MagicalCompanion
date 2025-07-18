"""
Progress Tracker - Monitors and analyzes child development progress

This module tracks learning progress, communication improvements,
routine adherence, and generates insights for caregivers.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import json
import logging
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict

logger = logging.getLogger(__name__)

@dataclass
class Interaction:
    """Represents a single interaction with the child."""
    id: Optional[int]
    child_id: int
    interaction_type: str  # chat, routine, activity, learning
    content: str
    response: str
    success: bool
    duration_seconds: Optional[int]
    emotion_detected: Optional[str]
    timestamp: datetime

@dataclass
class Milestone:
    """Represents a developmental milestone."""
    id: Optional[int]
    child_id: int
    category: str  # communication, social, learning, routine
    description: str
    achieved: bool
    achieved_date: Optional[datetime]
    target_date: Optional[datetime]

@dataclass
class ProgressReport:
    """Comprehensive progress report for a child."""
    child_id: int
    report_period: str
    communication_score: float
    routine_adherence: float
    learning_engagement: float
    social_interaction: float
    overall_progress: float
    achievements: List[str]
    areas_for_improvement: List[str]
    recommendations: List[str]

class ProgressTracker:
    """Tracks and analyzes child development progress."""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.milestone_templates = self._load_milestone_templates()
    
    def _load_milestone_templates(self) -> Dict[str, List[Dict]]:
        """Load developmental milestone templates."""
        return {
            "communication": [
                {
                    "description": "Uses 5+ visual symbols consistently",
                    "category": "communication",
                    "difficulty": "beginner"
                },
                {
                    "description": "Responds to simple questions with gestures",
                    "category": "communication",
                    "difficulty": "beginner"
                },
                {
                    "description": "Initiates communication using preferred method",
                    "category": "communication",
                    "difficulty": "intermediate"
                },
                {
                    "description": "Expresses needs clearly using multiple modalities",
                    "category": "communication",
                    "difficulty": "advanced"
                }
            ],
            "routine": [
                {
                    "description": "Follows 3-step morning routine independently",
                    "category": "routine",
                    "difficulty": "beginner"
                },
                {
                    "description": "Transitions between activities with visual cues",
                    "category": "routine",
                    "difficulty": "beginner"
                },
                {
                    "description": "Completes full daily routine with minimal prompts",
                    "category": "routine",
                    "difficulty": "intermediate"
                },
                {
                    "description": "Adapts routine when unexpected changes occur",
                    "category": "routine",
                    "difficulty": "advanced"
                }
            ],
            "learning": [
                {
                    "description": "Engages with learning activity for 10+ minutes",
                    "category": "learning",
                    "difficulty": "beginner"
                },
                {
                    "description": "Demonstrates understanding through actions",
                    "category": "learning",
                    "difficulty": "beginner"
                },
                {
                    "description": "Applies learned skills in new situations",
                    "category": "learning",
                    "difficulty": "intermediate"
                },
                {
                    "description": "Shows initiative in learning activities",
                    "category": "learning",
                    "difficulty": "advanced"
                }
            ],
            "social": [
                {
                    "description": "Makes eye contact during interactions",
                    "category": "social",
                    "difficulty": "beginner"
                },
                {
                    "description": "Shows interest in others' activities",
                    "category": "social",
                    "difficulty": "beginner"
                },
                {
                    "description": "Engages in parallel play activities",
                    "category": "social",
                    "difficulty": "intermediate"
                },
                {
                    "description": "Initiates social interactions appropriately",
                    "category": "social",
                    "difficulty": "advanced"
                }
            ]
        }
    
    async def log_interaction(
        self,
        child_id: int,
        interaction_type: str,
        content: str,
        response: str,
        success: bool,
        duration_seconds: Optional[int] = None,
        emotion_detected: Optional[str] = None
    ) -> int:
        """Log a new interaction with the child."""
        try:
            interaction = Interaction(
                id=None,
                child_id=child_id,
                interaction_type=interaction_type,
                content=content,
                response=response,
                success=success,
                duration_seconds=duration_seconds,
                emotion_detected=emotion_detected,
                timestamp=datetime.now()
            )
            
            interaction_id = await self.db_manager.save_interaction(interaction)
            
            # Check if this interaction triggers any milestone achievements
            await self._check_milestone_achievements(child_id, interaction)
            
            logger.info(f"Logged interaction for child {child_id}: {interaction_type}")
            return interaction_id
        
        except Exception as e:
            logger.error(f"Failed to log interaction: {str(e)}")
            raise
    
    async def _check_milestone_achievements(self, child_id: int, interaction: Interaction):
        """Check if recent interactions indicate milestone achievements."""
        try:
            # Get recent interactions to analyze patterns
            recent_interactions = await self.db_manager.get_recent_interactions(
                child_id, days=7
            )
            
            # Analyze communication patterns
            if interaction.interaction_type == "chat":
                await self._analyze_communication_milestones(child_id, recent_interactions)
            
            # Analyze routine adherence
            elif interaction.interaction_type == "routine":
                await self._analyze_routine_milestones(child_id, recent_interactions)
            
            # Analyze learning engagement
            elif interaction.interaction_type == "learning":
                await self._analyze_learning_milestones(child_id, recent_interactions)
        
        except Exception as e:
            logger.error(f"Failed to check milestones: {str(e)}")
    
    async def _analyze_communication_milestones(
        self,
        child_id: int,
        interactions: List[Interaction]
    ):
        """Analyze communication milestones based on recent interactions."""
        communication_interactions = [
            i for i in interactions if i.interaction_type == "chat"
        ]
        
        if len(communication_interactions) >= 5:
            success_rate = sum(1 for i in communication_interactions if i.success) / len(communication_interactions)
            
            # Check for consistent communication milestone
            if success_rate >= 0.8:
                await self._award_milestone(
                    child_id,
                    "communication",
                    "Uses communication system consistently"
                )
        
        # Check for emotional expression milestone
        emotional_interactions = [
            i for i in communication_interactions if i.emotion_detected
        ]
        
        if len(emotional_interactions) >= 3:
            await self._award_milestone(
                child_id,
                "communication",
                "Expresses emotions through communication"
            )
    
    async def _analyze_routine_milestones(
        self,
        child_id: int,
        interactions: List[Interaction]
    ):
        """Analyze routine-related milestones."""
        routine_interactions = [
            i for i in interactions if i.interaction_type == "routine"
        ]
        
        if len(routine_interactions) >= 3:
            success_rate = sum(1 for i in routine_interactions if i.success) / len(routine_interactions)
            
            if success_rate >= 0.9:
                await self._award_milestone(
                    child_id,
                    "routine",
                    "Follows routine consistently"
                )
    
    async def _analyze_learning_milestones(
        self,
        child_id: int,
        interactions: List[Interaction]
    ):
        """Analyze learning-related milestones."""
        learning_interactions = [
            i for i in interactions if i.interaction_type in ["learning", "activity"]
        ]
        
        # Check for sustained engagement
        long_interactions = [
            i for i in learning_interactions 
            if i.duration_seconds and i.duration_seconds >= 600  # 10+ minutes
        ]
        
        if len(long_interactions) >= 2:
            await self._award_milestone(
                child_id,
                "learning",
                "Sustains attention in learning activities"
            )
    
    async def _award_milestone(
        self,
        child_id: int,
        category: str,
        description: str
    ):
        """Award a milestone to a child if not already achieved."""
        try:
            # Check if milestone already exists
            existing_milestones = await self.db_manager.get_child_milestones(child_id)
            
            for milestone in existing_milestones:
                if milestone.description == description and milestone.achieved:
                    return  # Already achieved
            
            # Create new milestone
            milestone = Milestone(
                id=None,
                child_id=child_id,
                category=category,
                description=description,
                achieved=True,
                achieved_date=datetime.now(),
                target_date=None
            )
            
            await self.db_manager.save_milestone(milestone)
            logger.info(f"Awarded milestone to child {child_id}: {description}")
        
        except Exception as e:
            logger.error(f"Failed to award milestone: {str(e)}")
    
    async def get_child_progress(self, child_id: int) -> Dict[str, Any]:
        """Get current progress overview for a child."""
        try:
            # Get recent interactions (last 30 days)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            
            interactions = await self.db_manager.get_interactions_by_date_range(
                child_id, start_date, end_date
            )
            
            # Calculate progress metrics
            communication_score = self._calculate_communication_score(interactions)
            routine_adherence = self._calculate_routine_adherence(interactions)
            learning_engagement = self._calculate_learning_engagement(interactions)
            
            # Get achieved milestones
            milestones = await self.db_manager.get_child_milestones(child_id)
            achieved_milestones = [m for m in milestones if m.achieved]
            
            # Generate progress summary
            progress_data = {
                "child_id": child_id,
                "period": "Last 30 days",
                "communication_score": communication_score,
                "routine_adherence": routine_adherence,
                "learning_engagement": learning_engagement,
                "overall_progress": (communication_score + routine_adherence + learning_engagement) / 3,
                "total_interactions": len(interactions),
                "achieved_milestones": len(achieved_milestones),
                "recent_achievements": [
                    m.description for m in achieved_milestones[-5:]  # Last 5 achievements
                ],
                "improvement_areas": self._identify_improvement_areas(
                    communication_score, routine_adherence, learning_engagement
                )
            }
            
            return progress_data
        
        except Exception as e:
            logger.error(f"Failed to get child progress: {str(e)}")
            return {}
    
    def _calculate_communication_score(self, interactions: List[Interaction]) -> float:
        """Calculate communication progress score (0-100)."""
        communication_interactions = [
            i for i in interactions if i.interaction_type == "chat"
        ]
        
        if not communication_interactions:
            return 0.0
        
        # Base score on success rate
        success_rate = sum(1 for i in communication_interactions if i.success) / len(communication_interactions)
        base_score = success_rate * 70  # Up to 70 points for success rate
        
        # Bonus points for emotional expression
        emotional_interactions = sum(
            1 for i in communication_interactions if i.emotion_detected
        )
        emotion_bonus = min(emotional_interactions * 3, 20)  # Up to 20 bonus points
        
        # Bonus for consistency (daily interactions)
        days_with_interaction = len(set(i.timestamp.date() for i in communication_interactions))
        consistency_bonus = min(days_with_interaction, 10)  # Up to 10 bonus points
        
        return min(base_score + emotion_bonus + consistency_bonus, 100.0)
    
    def _calculate_routine_adherence(self, interactions: List[Interaction]) -> float:
        """Calculate routine adherence score (0-100)."""
        routine_interactions = [
            i for i in interactions if i.interaction_type == "routine"
        ]
        
        if not routine_interactions:
            return 0.0
        
        # Success rate for routine completion
        success_rate = sum(1 for i in routine_interactions if i.success) / len(routine_interactions)
        
        # Bonus for regular routine engagement
        days_with_routines = len(set(i.timestamp.date() for i in routine_interactions))
        consistency_bonus = min(days_with_routines * 2, 20)
        
        return min(success_rate * 80 + consistency_bonus, 100.0)
    
    def _calculate_learning_engagement(self, interactions: List[Interaction]) -> float:
        """Calculate learning engagement score (0-100)."""
        learning_interactions = [
            i for i in interactions if i.interaction_type in ["learning", "activity"]
        ]
        
        if not learning_interactions:
            return 0.0
        
        # Base score on engagement success
        success_rate = sum(1 for i in learning_interactions if i.success) / len(learning_interactions)
        base_score = success_rate * 60
        
        # Bonus for sustained attention (duration-based)
        sustained_sessions = sum(
            1 for i in learning_interactions 
            if i.duration_seconds and i.duration_seconds >= 300  # 5+ minutes
        )
        duration_bonus = min(sustained_sessions * 5, 25)
        
        # Bonus for frequency
        frequency_bonus = min(len(learning_interactions), 15)
        
        return min(base_score + duration_bonus + frequency_bonus, 100.0)
    
    def _identify_improvement_areas(
        self,
        communication_score: float,
        routine_adherence: float,
        learning_engagement: float
    ) -> List[str]:
        """Identify areas that need improvement."""
        improvement_areas = []
        
        if communication_score < 60:
            improvement_areas.append("Communication skills need more practice")
        
        if routine_adherence < 70:
            improvement_areas.append("Routine consistency could be improved")
        
        if learning_engagement < 65:
            improvement_areas.append("Learning activities could be more engaging")
        
        return improvement_areas
    
    async def generate_detailed_report(
        self,
        child_id: int,
        days: int = 30
    ) -> ProgressReport:
        """Generate a detailed progress report."""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            interactions = await self.db_manager.get_interactions_by_date_range(
                child_id, start_date, end_date
            )
            
            milestones = await self.db_manager.get_child_milestones(child_id)
            
            # Calculate detailed metrics
            communication_score = self._calculate_communication_score(interactions)
            routine_adherence = self._calculate_routine_adherence(interactions)
            learning_engagement = self._calculate_learning_engagement(interactions)
            social_interaction = self._calculate_social_interaction_score(interactions)
            
            overall_progress = (
                communication_score + routine_adherence + 
                learning_engagement + social_interaction
            ) / 4
            
            # Generate achievements list
            recent_achievements = [
                m.description for m in milestones 
                if m.achieved and m.achieved_date and 
                m.achieved_date >= start_date
            ]
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                communication_score, routine_adherence, 
                learning_engagement, social_interaction
            )
            
            report = ProgressReport(
                child_id=child_id,
                report_period=f"Last {days} days",
                communication_score=communication_score,
                routine_adherence=routine_adherence,
                learning_engagement=learning_engagement,
                social_interaction=social_interaction,
                overall_progress=overall_progress,
                achievements=recent_achievements,
                areas_for_improvement=self._identify_improvement_areas(
                    communication_score, routine_adherence, learning_engagement
                ),
                recommendations=recommendations
            )
            
            return report
        
        except Exception as e:
            logger.error(f"Failed to generate detailed report: {str(e)}")
            raise
    
    def _calculate_social_interaction_score(self, interactions: List[Interaction]) -> float:
        """Calculate social interaction score based on engagement patterns."""
        # For now, base this on positive emotional responses and interaction frequency
        positive_interactions = [
            i for i in interactions 
            if i.emotion_detected in ["happy", "excited", "calm", "encouraging"]
        ]
        
        if not interactions:
            return 0.0
        
        positive_ratio = len(positive_interactions) / len(interactions)
        return min(positive_ratio * 100, 100.0)
    
    def _generate_recommendations(
        self,
        communication_score: float,
        routine_adherence: float,
        learning_engagement: float,
        social_interaction: float
    ) -> List[str]:
        """Generate personalized recommendations based on scores."""
        recommendations = []
        
        if communication_score < 70:
            recommendations.append(
                "Increase visual communication supports and practice daily communication routines"
            )
        
        if routine_adherence < 75:
            recommendations.append(
                "Use more visual schedules and provide advance notice of routine changes"
            )
        
        if learning_engagement < 70:
            recommendations.append(
                "Try shorter learning sessions with more frequent breaks and incorporate special interests"
            )
        
        if social_interaction < 60:
            recommendations.append(
                "Create more opportunities for positive social interactions in comfortable settings"
            )
        
        # Always include a positive recommendation
        recommendations.append(
            "Continue celebrating small achievements and maintaining consistent, patient support"
        )
        
        return recommendations
    
    async def get_detailed_progress(self, child_id: int) -> Dict[str, Any]:
        """Get comprehensive progress data including charts and analytics."""
        try:
            # Get basic progress
            basic_progress = await self.get_child_progress(child_id)
            
            # Get detailed report
            detailed_report = await self.generate_detailed_report(child_id)
            
            # Get trend data for the last 90 days
            trend_data = await self._get_progress_trends(child_id, 90)
            
            return {
                "basic_progress": basic_progress,
                "detailed_report": asdict(detailed_report),
                "trends": trend_data,
                "next_milestones": await self._get_next_milestones(child_id)
            }
        
        except Exception as e:
            logger.error(f"Failed to get detailed progress: {str(e)}")
            return {}
    
    async def _get_progress_trends(self, child_id: int, days: int) -> Dict[str, List]:
        """Get progress trends over time."""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Get weekly progress data
            weekly_data = []
            current_date = start_date
            
            while current_date < end_date:
                week_end = current_date + timedelta(days=7)
                week_interactions = await self.db_manager.get_interactions_by_date_range(
                    child_id, current_date, week_end
                )
                
                weekly_data.append({
                    "week": current_date.strftime("%Y-%m-%d"),
                    "communication": self._calculate_communication_score(week_interactions),
                    "routine": self._calculate_routine_adherence(week_interactions),
                    "learning": self._calculate_learning_engagement(week_interactions),
                    "total_interactions": len(week_interactions)
                })
                
                current_date = week_end
            
            return {
                "weekly_progress": weekly_data,
                "improvement_trend": self._calculate_trend_direction(weekly_data)
            }
        
        except Exception as e:
            logger.error(f"Failed to get progress trends: {str(e)}")
            return {}
    
    def _calculate_trend_direction(self, weekly_data: List[Dict]) -> str:
        """Calculate overall trend direction (improving, declining, stable)."""
        if len(weekly_data) < 2:
            return "insufficient_data"
        
        # Compare first half with second half
        mid_point = len(weekly_data) // 2
        first_half_avg = np.mean([
            w["communication"] + w["routine"] + w["learning"] 
            for w in weekly_data[:mid_point]
        ])
        second_half_avg = np.mean([
            w["communication"] + w["routine"] + w["learning"] 
            for w in weekly_data[mid_point:]
        ])
        
        diff = second_half_avg - first_half_avg
        
        if diff > 10:
            return "improving"
        elif diff < -10:
            return "declining"
        else:
            return "stable"
    
    async def _get_next_milestones(self, child_id: int) -> List[Dict]:
        """Get suggested next milestones for the child."""
        try:
            current_milestones = await self.db_manager.get_child_milestones(child_id)
            achieved_descriptions = {m.description for m in current_milestones if m.achieved}
            
            # Suggest next milestones from templates
            suggestions = []
            
            for category, templates in self.milestone_templates.items():
                for template in templates:
                    if template["description"] not in achieved_descriptions:
                        suggestions.append({
                            "category": category,
                            "description": template["description"],
                            "difficulty": template["difficulty"],
                            "estimated_timeline": self._estimate_milestone_timeline(
                                template["difficulty"]
                            )
                        })
                        break  # One suggestion per category
            
            return suggestions[:4]  # Return top 4 suggestions
        
        except Exception as e:
            logger.error(f"Failed to get next milestones: {str(e)}")
            return []
    
    def _estimate_milestone_timeline(self, difficulty: str) -> str:
        """Estimate timeline for achieving a milestone based on difficulty."""
        timelines = {
            "beginner": "2-4 weeks",
            "intermediate": "1-2 months",
            "advanced": "2-4 months"
        }
        return timelines.get(difficulty, "4-8 weeks")

    async def get_child_milestones(self, child_id: int) -> List[Dict[str, Any]]:
        """Get all milestones for a child."""
        try:
            query = """
                SELECT id, child_id, category, description, achieved, achieved_date, target_date
                FROM milestones 
                WHERE child_id = ?
                ORDER BY achieved DESC, target_date ASC
            """
            
            milestones = await self.db_manager.fetch_all(query, (child_id,))
            
            result = []
            for milestone in milestones:
                milestone_dict = dict(milestone)
                # Convert date strings to datetime objects if needed
                if milestone_dict['achieved_date']:
                    milestone_dict['achieved_date'] = datetime.fromisoformat(milestone_dict['achieved_date'])
                if milestone_dict['target_date']:
                    milestone_dict['target_date'] = datetime.fromisoformat(milestone_dict['target_date'])
                result.append(milestone_dict)
            
            # If no milestones exist, create some default ones
            if not result:
                await self._create_default_milestones(child_id)
                return await self.get_child_milestones(child_id)
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting milestones for child {child_id}: {str(e)}")
            return []

    async def get_recent_interactions(self, child_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent interactions for a child."""
        try:
            query = """
                SELECT id, child_id, interaction_type, content, response, success, 
                       duration_seconds, emotion_detected, timestamp
                FROM interactions 
                WHERE child_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """
            
            interactions = await self.db_manager.fetch_all(query, (child_id, limit))
            
            result = []
            for interaction in interactions:
                interaction_dict = dict(interaction)
                # Convert timestamp string to datetime object if needed
                if isinstance(interaction_dict['timestamp'], str):
                    interaction_dict['timestamp'] = datetime.fromisoformat(interaction_dict['timestamp'])
                result.append(interaction_dict)
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting recent interactions for child {child_id}: {str(e)}")
            return []

    async def get_child_statistics(self, child_id: int) -> Dict[str, Any]:
        """Get statistics for a child."""
        try:
            # Get basic interaction counts
            total_messages_query = """
                SELECT COUNT(*) as count FROM interactions 
                WHERE child_id = ? AND interaction_type = 'chat'
            """
            total_messages = await self.db_manager.fetch_one(total_messages_query, (child_id,))
            
            successful_communications_query = """
                SELECT COUNT(*) as count FROM interactions 
                WHERE child_id = ? AND interaction_type = 'chat' AND success = 1
            """
            successful_communications = await self.db_manager.fetch_one(successful_communications_query, (child_id,))
            
            # Get routine statistics
            routines_started_query = """
                SELECT COUNT(DISTINCT routine_id) as count FROM routine_sessions 
                WHERE child_id = ?
            """
            routines_started = await self.db_manager.fetch_one(routines_started_query, (child_id,))
            
            routines_completed_query = """
                SELECT COUNT(*) as count FROM routine_sessions 
                WHERE child_id = ? AND status = 'completed'
            """
            routines_completed = await self.db_manager.fetch_one(routines_completed_query, (child_id,))
            
            # Get learning statistics
            learning_sessions_query = """
                SELECT COUNT(*) as count FROM interactions 
                WHERE child_id = ? AND interaction_type = 'learning'
            """
            learning_sessions = await self.db_manager.fetch_one(learning_sessions_query, (child_id,))
            
            return {
                "total_messages": total_messages['count'] if total_messages else 0,
                "successful_communications": successful_communications['count'] if successful_communications else 0,
                "routines_started": routines_started['count'] if routines_started else 0,
                "routines_completed": routines_completed['count'] if routines_completed else 0,
                "learning_sessions": learning_sessions['count'] if learning_sessions else 0,
                "skills_practiced": learning_sessions['count'] if learning_sessions else 0  # Placeholder
            }
            
        except Exception as e:
            logger.error(f"Error getting statistics for child {child_id}: {str(e)}")
            return {
                "total_messages": 0,
                "successful_communications": 0,
                "routines_started": 0,
                "routines_completed": 0,
                "learning_sessions": 0,
                "skills_practiced": 0
            }

    async def generate_insights(self, child_id: int) -> List[Dict[str, str]]:
        """Generate AI insights for a child's progress."""
        try:
            # Get recent progress data
            progress = await self.get_child_progress(child_id)
            interactions = await self.get_recent_interactions(child_id, limit=20)
            milestones = await self.get_child_milestones(child_id)
            
            insights = []
            
            # Communication insights
            if progress['communication_score'] >= 80:
                insights.append({
                    "type": "Communication Success",
                    "text": f"Excellent communication progress! {child_id}'s communication skills are developing wonderfully. Keep encouraging expressive interactions! 🌟"
                })
            elif progress['communication_score'] >= 60:
                insights.append({
                    "type": "Communication Growth",
                    "text": f"Good communication development! Focus on expanding vocabulary and encouraging longer interactions for continued growth. 📈"
                })
            else:
                insights.append({
                    "type": "Communication Support",
                    "text": f"Let's focus on building communication confidence! Try using more visual cues and positive reinforcement during interactions. 💪"
                })
            
            # Routine insights
            if progress['routine_adherence'] >= 80:
                insights.append({
                    "type": "Routine Excellence",
                    "text": f"Amazing routine adherence! Consistent routines are building great habits and structure. Consider adding new routine challenges! 🏆"
                })
            elif progress['routine_adherence'] >= 60:
                insights.append({
                    "type": "Routine Building",
                    "text": f"Solid routine progress! Try breaking down complex routines into smaller, achievable steps for better success rates. 📅"
                })
            else:
                insights.append({
                    "type": "Routine Support",
                    "text": f"Routines take time to build! Focus on one simple routine at a time and celebrate small victories along the way. 🌈"
                })
            
            # Learning insights
            if progress['learning_engagement'] >= 80:
                insights.append({
                    "type": "Learning Champion",
                    "text": f"Outstanding learning engagement! This curiosity and engagement will lead to amazing growth. Explore new learning topics! 🎓"
                })
            elif progress['learning_engagement'] >= 60:
                insights.append({
                    "type": "Learning Progress",
                    "text": f"Great learning momentum! Try incorporating more interactive and hands-on learning activities for enhanced engagement. ✨"
                })
            else:
                insights.append({
                    "type": "Learning Encouragement",
                    "text": f"Every learner has their own pace! Find topics that spark natural interest and build learning confidence gradually. 💡"
                })
            
            # Milestone insights
            achieved_milestones = len([m for m in milestones if m['achieved']])
            total_milestones = len(milestones)
            
            if achieved_milestones > 0:
                insights.append({
                    "type": "Milestone Achievement",
                    "text": f"Wonderful progress with {achieved_milestones} milestones achieved! Each milestone represents real growth and development. 🎉"
                })
            
            # Recent activity insights
            if len(interactions) > 0:
                recent_success_rate = len([i for i in interactions if i['success']]) / len(interactions)
                if recent_success_rate >= 0.8:
                    insights.append({
                        "type": "Recent Success",
                        "text": f"Recent interactions show excellent success patterns! This consistency is building strong communication confidence. 🌟"
                    })
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating insights for child {child_id}: {str(e)}")
            return [{
                "type": "Welcome",
                "text": "Welcome to Rainbow Bridge! Start interacting to see personalized insights about your progress journey. 🌈"
            }]

    async def _create_default_milestones(self, child_id: int):
        """Create default milestones for a new child."""
        default_milestones = [
            {
                "category": "communication",
                "description": "First successful interaction with Rainbow Bridge",
                "achieved": False,
                "target_date": datetime.now() + timedelta(days=7)
            },
            {
                "category": "communication", 
                "description": "Send 10 messages using visual cues",
                "achieved": False,
                "target_date": datetime.now() + timedelta(days=14)
            },
            {
                "category": "routine",
                "description": "Complete first routine activity",
                "achieved": False,
                "target_date": datetime.now() + timedelta(days=7)
            },
            {
                "category": "routine",
                "description": "Complete a full routine session",
                "achieved": False,
                "target_date": datetime.now() + timedelta(days=21)
            },
            {
                "category": "social",
                "description": "Use positive social expressions (please, thank you)",
                "achieved": False,
                "target_date": datetime.now() + timedelta(days=14)
            },
            {
                "category": "learning",
                "description": "Engage in learning conversation with AI",
                "achieved": False,
                "target_date": datetime.now() + timedelta(days=10)
            }
        ]
        
        for milestone in default_milestones:
            query = """
                INSERT INTO milestones (child_id, category, description, achieved, target_date)
                VALUES (?, ?, ?, ?, ?)
            """
            await self.db_manager.execute_query(
                query, 
                (child_id, milestone['category'], milestone['description'], 
                 milestone['achieved'], milestone['target_date'].isoformat())
            )
