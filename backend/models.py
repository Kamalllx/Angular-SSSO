from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import json

@dataclass
class StudySession:
    id: str
    subject: str
    duration_minutes: int
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    goals: Optional[List[str]] = None
    completed_goals: Optional[List[str]] = None
    focus_score: Optional[int] = None
    notes: str = ""
    distractions: int = 0
    breaks_taken: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'subject': self.subject,
            'duration_minutes': self.duration_minutes,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'goals': self.goals or [],
            'completed_goals': self.completed_goals or [],
            'focus_score': self.focus_score,
            'notes': self.notes,
            'distractions': self.distractions,
            'breaks_taken': self.breaks_taken
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StudySession':
        return cls(
            id=data['id'],
            subject=data['subject'],
            duration_minutes=data['duration_minutes'],
            start_time=datetime.fromisoformat(data['start_time']) if data.get('start_time') else None,
            end_time=datetime.fromisoformat(data['end_time']) if data.get('end_time') else None,
            goals=data.get('goals', []),
            completed_goals=data.get('completed_goals', []),
            focus_score=data.get('focus_score'),
            notes=data.get('notes', ''),
            distractions=data.get('distractions', 0),
            breaks_taken=data.get('breaks_taken', 0)
        )

@dataclass
class StudyPlan:
    subject: str
    total_duration: int
    break_intervals: List[int]
    goals: List[str]
    priority_level: int
    optimal_time_slots: List[str]
    required_resources: List[str]
    distraction_blockers: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'subject': self.subject,
            'total_duration': self.total_duration,
            'break_intervals': self.break_intervals,
            'goals': self.goals,
            'priority_level': self.priority_level,
            'optimal_time_slots': self.optimal_time_slots,
            'required_resources': self.required_resources,
            'distraction_blockers': self.distraction_blockers
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StudyPlan':
        return cls(
            subject=data['subject'],
            total_duration=data['total_duration'],
            break_intervals=data['break_intervals'],
            goals=data['goals'],
            priority_level=data['priority_level'],
            optimal_time_slots=data['optimal_time_slots'],
            required_resources=data['required_resources'],
            distraction_blockers=data['distraction_blockers']
        )

@dataclass
class CalendarEvent:
    id: str
    title: str
    start_time: datetime
    end_time: datetime
    description: str = ""
    event_type: str = "study_session"
    status: str = "scheduled"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'title': self.title,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(),
            'description': self.description,
            'event_type': self.event_type,
            'status': self.status
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CalendarEvent':
        return cls(
            id=data['id'],
            title=data['title'],
            start_time=datetime.fromisoformat(data['start_time']),
            end_time=datetime.fromisoformat(data['end_time']),
            description=data.get('description', ''),
            event_type=data.get('event_type', 'study_session'),
            status=data.get('status', 'scheduled')
        )

@dataclass
class UserPreferences:
    default_study_duration: int = 25
    default_break_duration: int = 5
    preferred_study_times: List[str] = None
    distracting_websites: List[str] = None
    focus_techniques: List[str] = None
    notifications_enabled: bool = True
    auto_block_websites: bool = True
    
    def __post_init__(self):
        if self.preferred_study_times is None:
            self.preferred_study_times = ["09:00", "14:00", "19:00"]
        if self.distracting_websites is None:
            self.distracting_websites = [
                "facebook.com", "twitter.com", "youtube.com", 
                "instagram.com", "reddit.com"
            ]
        if self.focus_techniques is None:
            self.focus_techniques = [
                "Pomodoro Technique", "Time blocking", "Active recall"
            ]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'default_study_duration': self.default_study_duration,
            'default_break_duration': self.default_break_duration,
            'preferred_study_times': self.preferred_study_times,
            'distracting_websites': self.distracting_websites,
            'focus_techniques': self.focus_techniques,
            'notifications_enabled': self.notifications_enabled,
            'auto_block_websites': self.auto_block_websites
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserPreferences':
        return cls(
            default_study_duration=data.get('default_study_duration', 25),
            default_break_duration=data.get('default_break_duration', 5),
            preferred_study_times=data.get('preferred_study_times'),
            distracting_websites=data.get('distracting_websites'),
            focus_techniques=data.get('focus_techniques'),
            notifications_enabled=data.get('notifications_enabled', True),
            auto_block_websites=data.get('auto_block_websites', True)
        )

@dataclass
class Analytics:
    total_sessions: int
    total_study_time: int
    average_focus_score: float
    best_subject: str
    productivity_trend: str
    weekly_goal_completion: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'total_sessions': self.total_sessions,
            'total_study_time': self.total_study_time,
            'average_focus_score': self.average_focus_score,
            'best_subject': self.best_subject,
            'productivity_trend': self.productivity_trend,
            'weekly_goal_completion': self.weekly_goal_completion
        }
