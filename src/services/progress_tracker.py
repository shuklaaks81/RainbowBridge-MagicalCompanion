"""
Progress tracking service for Rainbow Bridge
Handles activity logging, milestone tracking, and progress analytics.
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging

from src.models.entities import ActivityLog, Milestone, Interaction
from src.services.database_core import DatabaseCore

logger = logging.getLogger(__name__)


class ProgressTracker:
    """Service for tracking child progress and achievements."""
    
    def __init__(self, db_core: DatabaseCore):
        self.db_core = db_core
    
    async def log_activity_completion(self, activity_log: ActivityLog) -> int:
        """Log an activity completion."""
        return await self.db_core.get_last_insert_id("""
            INSERT INTO activity_logs (
                child_id, routine_id, activity_id, activity_name,
                completed_at, duration_minutes, notes, satisfaction_level
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            activity_log.child_id, activity_log.routine_id, activity_log.activity_id,
            activity_log.activity_name, activity_log.completed_at.isoformat(),
            activity_log.duration_minutes, activity_log.notes,
            activity_log.satisfaction_level
        ))
    
    async def log_interaction(self, interaction: Interaction) -> int:
        """Log a communication interaction."""
        return await self.db_core.get_last_insert_id("""
            INSERT INTO interactions (
                child_id, message, ai_response, communication_type,
                context, routine_id, activity_id, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            interaction.child_id, interaction.message, interaction.ai_response,
            interaction.communication_type, json.dumps(interaction.context),
            interaction.routine_id, interaction.activity_id,
            interaction.timestamp.isoformat()
        ))
    
    async def add_milestone(self, milestone: Milestone) -> int:
        """Add a new milestone achievement."""
        return await self.db_core.get_last_insert_id("""
            INSERT INTO milestones (
                child_id, title, description, category,
                achieved_at, data
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            milestone.child_id, milestone.title, milestone.description,
            milestone.category, milestone.achieved_at.isoformat(),
            json.dumps(milestone.data)
        ))
    
    async def get_child_progress_summary(self, child_id: int, days: int = 7) -> Dict[str, Any]:
        """Get comprehensive progress summary for a child."""
        
        # Date range for analysis
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Get activity completions
        activity_rows = await self.db_core.execute_query("""
            SELECT activity_name, completed_at, duration_minutes, satisfaction_level
            FROM activity_logs 
            WHERE child_id = ? AND completed_at >= ?
            ORDER BY completed_at DESC
        """, (child_id, start_date.isoformat()))
        
        # Get recent milestones
        milestone_rows = await self.db_core.execute_query("""
            SELECT title, category, achieved_at, data
            FROM milestones 
            WHERE child_id = ? AND achieved_at >= ?
            ORDER BY achieved_at DESC
        """, (child_id, start_date.isoformat()))
        
        # Get interaction count
        interaction_rows = await self.db_core.execute_query("""
            SELECT COUNT(*) FROM interactions 
            WHERE child_id = ? AND timestamp >= ?
        """, (child_id, start_date.isoformat()))
        
        # Calculate statistics
        total_activities = len(activity_rows)
        avg_satisfaction = 0
        if activity_rows:
            satisfactions = [row[3] for row in activity_rows if row[3] is not None]
            avg_satisfaction = sum(satisfactions) / len(satisfactions) if satisfactions else 0
        
        # Group activities by day
        daily_activities = {}
        for row in activity_rows:
            date_key = datetime.fromisoformat(row[1]).date().isoformat()
            if date_key not in daily_activities:
                daily_activities[date_key] = 0
            daily_activities[date_key] += 1
        
        # Recent achievements
        recent_milestones = []
        for row in milestone_rows:
            recent_milestones.append({
                'title': row[0],
                'category': row[1],
                'achieved_at': row[2],
                'data': json.loads(row[3]) if row[3] else {}
            })
        
        return {
            'child_id': child_id,
            'period_days': days,
            'summary': {
                'total_activities_completed': total_activities,
                'average_satisfaction': round(avg_satisfaction, 1),
                'total_interactions': interaction_rows[0][0] if interaction_rows else 0,
                'milestones_achieved': len(recent_milestones),
                'daily_activity_average': round(total_activities / days, 1)
            },
            'daily_breakdown': daily_activities,
            'recent_milestones': recent_milestones[:5],  # Last 5 milestones
            'activity_details': [
                {
                    'name': row[0],
                    'completed_at': row[1],
                    'duration_minutes': row[2],
                    'satisfaction_level': row[3]
                } for row in activity_rows[:10]  # Last 10 activities
            ]
        }
    
    async def get_routine_completion_stats(self, child_id: int, routine_id: int = None) -> Dict[str, Any]:
        """Get routine completion statistics."""
        
        # Base query for routine completions
        if routine_id:
            activity_rows = await self.db_core.execute_query("""
                SELECT r.name as routine_name, al.activity_name, al.completed_at,
                       al.duration_minutes, al.satisfaction_level
                FROM activity_logs al
                JOIN routines r ON al.routine_id = r.id
                WHERE al.child_id = ? AND al.routine_id = ?
                ORDER BY al.completed_at DESC
            """, (child_id, routine_id))
        else:
            activity_rows = await self.db_core.execute_query("""
                SELECT r.name as routine_name, al.activity_name, al.completed_at,
                       al.duration_minutes, al.satisfaction_level
                FROM activity_logs al
                JOIN routines r ON al.routine_id = r.id
                WHERE al.child_id = ?
                ORDER BY al.completed_at DESC
            """, (child_id,))
        
        # Group by routine
        routine_stats = {}
        for row in activity_rows:
            routine_name = row[0]
            if routine_name not in routine_stats:
                routine_stats[routine_name] = {
                    'total_completions': 0,
                    'avg_duration': 0,
                    'avg_satisfaction': 0,
                    'last_completed': None,
                    'activities': []
                }
            
            routine_stats[routine_name]['total_completions'] += 1
            routine_stats[routine_name]['activities'].append({
                'name': row[1],
                'completed_at': row[2],
                'duration': row[3],
                'satisfaction': row[4]
            })
            
            if not routine_stats[routine_name]['last_completed']:
                routine_stats[routine_name]['last_completed'] = row[2]
        
        # Calculate averages
        for routine_name, stats in routine_stats.items():
            activities = stats['activities']
            if activities:
                durations = [a['duration'] for a in activities if a['duration']]
                satisfactions = [a['satisfaction'] for a in activities if a['satisfaction']]
                
                stats['avg_duration'] = round(sum(durations) / len(durations), 1) if durations else 0
                stats['avg_satisfaction'] = round(sum(satisfactions) / len(satisfactions), 1) if satisfactions else 0
        
        return routine_stats
    
    async def get_streak_information(self, child_id: int) -> Dict[str, Any]:
        """Get activity streak information for motivation."""
        
        # Get recent activity completions (last 30 days)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        activity_rows = await self.db_core.execute_query("""
            SELECT DATE(completed_at) as completion_date, COUNT(*) as daily_count
            FROM activity_logs 
            WHERE child_id = ? AND completed_at >= ?
            GROUP BY DATE(completed_at)
            ORDER BY completion_date DESC
        """, (child_id, start_date.isoformat()))
        
        if not activity_rows:
            return {
                'current_streak': 0,
                'longest_streak': 0,
                'total_active_days': 0,
                'streak_type': 'none'
            }
        
        # Calculate current streak
        current_streak = 0
        today = datetime.now().date()
        
        # Check if there's activity today or yesterday (give some flexibility)
        recent_dates = set()
        for row in activity_rows:
            completion_date = datetime.fromisoformat(row[0]).date()
            recent_dates.add(completion_date)
        
        # Calculate current streak
        check_date = today
        while check_date in recent_dates:
            current_streak += 1
            check_date -= timedelta(days=1)
        
        # If no activity today, check if yesterday was the last day
        if current_streak == 0 and (today - timedelta(days=1)) in recent_dates:
            check_date = today - timedelta(days=1)
            while check_date in recent_dates:
                current_streak += 1
                check_date -= timedelta(days=1)
        
        # Calculate longest streak
        longest_streak = 0
        temp_streak = 0
        all_dates = sorted(recent_dates, reverse=True)
        
        if all_dates:
            for i, date in enumerate(all_dates):
                if i == 0:
                    temp_streak = 1
                else:
                    prev_date = all_dates[i-1]
                    if (prev_date - date).days == 1:
                        temp_streak += 1
                    else:
                        longest_streak = max(longest_streak, temp_streak)
                        temp_streak = 1
            longest_streak = max(longest_streak, temp_streak)
        
        # Determine streak type for encouragement
        streak_type = 'none'
        if current_streak >= 7:
            streak_type = 'amazing'
        elif current_streak >= 3:
            streak_type = 'good'
        elif current_streak >= 1:
            streak_type = 'starting'
        
        return {
            'current_streak': current_streak,
            'longest_streak': longest_streak,
            'total_active_days': len(recent_dates),
            'streak_type': streak_type,
            'recent_activity_dates': [date.isoformat() for date in sorted(recent_dates, reverse=True)[:7]]
        }
