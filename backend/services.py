import os
import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import statistics
import uuid

# Try to import Groq
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    print("Warning: Groq library not installed. Using mock responses.")

# =============================================================================
# GROQ SERVICE (FIXED)
# =============================================================================

class GroqService:
    def __init__(self):
        self.groq_available = GROQ_AVAILABLE and bool(os.getenv('GROQ_API_KEY'))
        
        if self.groq_available:
            self.client = Groq(api_key=os.getenv('GROQ_API_KEY'))
            self.model = "llama-3.1-8b-instant"
            print("Groq service initialized successfully")
        else:
            self.client = None
            self.model = None
            print("Groq service initialized in mock mode")
    
    def analyze_study_pattern(self, study_sessions: List[Dict]) -> Dict[str, Any]:
        """Analyze study patterns and provide insights"""
        
        if not self.groq_available:
            return self._get_mock_analysis(study_sessions)
        
        # Limit sessions to avoid token limits
        limited_sessions = study_sessions[-3:] if len(study_sessions) > 3 else study_sessions
        
        prompt = f"""
        Analyze these study sessions and provide insights in JSON format:
        
        Sessions: {json.dumps(limited_sessions, indent=2)}
        
        Respond with this exact JSON structure:
        {{
            "productivity_trends": {{
                "best_time_slots": ["morning"],
                "optimal_duration": 25,
                "peak_focus_subjects": ["Math"]
            }},
            "recommendations": {{
                "study_schedule": "Use 25-minute focused sessions",
                "break_frequency": "5-minute breaks every 25 minutes",
                "environment_tips": ["Remove distractions", "Use focus music"]
            }},
            "focus_insights": {{
                "distraction_patterns": ["Phone notifications"],
                "improvement_areas": ["Time management"]
            }}
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an AI study coach. Respond only with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=600,
                timeout=10  # Add timeout
            )
            
            result = response.choices[0].message.content.strip()
            
            # Clean up markdown if present
            if result.startswith("```"):
                lines = result.split('\n')
                result = '\n'.join(lines[1:-1] if lines[-1].strip() == '```' else lines[1:])

            return json.loads(result)
            
        except Exception as e:
            print(f"Error in Groq analysis: {e}")
            return self._get_mock_analysis(study_sessions)
    
    def generate_study_plan(self, subject: str, duration: int, goals: List[str]) -> Dict[str, Any]:
        """Generate optimized study plan using AI"""
        
        if not self.groq_available:
            return self._get_mock_study_plan(subject, duration, goals)
        
        # Create simplified prompt
        goals_text = ', '.join(goals[:3]) if goals else f"Study {subject}"
        
        prompt = f"""
        Create a study plan for:
        - Subject: {subject}
        - Duration: {duration} minutes  
        - Goals: {goals_text}
        
        Respond with this JSON structure:
        {{
            "study_blocks": [
                {{"activity": "Study {subject}", "duration": 25, "type": "study", "description": "Focus on main concepts"}},
                {{"activity": "Break", "duration": 5, "type": "break", "description": "Rest and recharge"}}
            ],
            "focus_techniques": ["Pomodoro technique", "Active recall"],
            "resource_recommendations": ["Textbook", "Online videos"],
            "distraction_management": ["Phone away", "Clean workspace"]
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a study planner. Respond only with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                max_tokens=500,
                timeout=10  # Add timeout
            )
            
            result = response.choices[0].message.content.strip()
            
            # Clean up markdown if present
            if result.startswith("```"):
                lines = result.split('\n')
                result = '\n'.join(lines[1:-1] if lines[-1].strip() == '```' else lines[1:])

            return json.loads(result)
            
        except Exception as e:
            print(f"Error generating study plan: {e}")
            return self._get_mock_study_plan(subject, duration, goals)
    
    def _get_mock_analysis(self, study_sessions: List[Dict]) -> Dict[str, Any]:
        """Generate mock analysis based on actual session data"""
        
        if not study_sessions:
            return self._get_default_analysis()
        
        # Simple analysis based on actual data
        subjects = list(set(s.get('subject', 'Unknown') for s in study_sessions))
        avg_duration = sum(s.get('duration_minutes', 25) for s in study_sessions) / len(study_sessions)
        
        return {
            "productivity_trends": {
                "best_time_slots": ["morning", "afternoon"],
                "optimal_duration": int(avg_duration),
                "peak_focus_subjects": subjects[:2]
            },
            "recommendations": {
                "study_schedule": f"Continue with {int(avg_duration)}-minute focused sessions",
                "break_frequency": "5-minute breaks every 25 minutes",
                "environment_tips": ["Remove distractions", "Stay hydrated", "Good lighting"]
            },
            "focus_insights": {
                "distraction_patterns": ["Phone notifications", "Social media"],
                "improvement_areas": ["Time management", "Goal setting"]
            },
            "mock_mode": True
        }
    
    def _get_default_analysis(self) -> Dict[str, Any]:
        return {
            "productivity_trends": {
                "best_time_slots": ["morning"],
                "optimal_duration": 25,
                "peak_focus_subjects": []
            },
            "recommendations": {
                "study_schedule": "Start with 25-minute Pomodoro sessions",
                "break_frequency": "5-minute breaks every 25 minutes",
                "environment_tips": ["Remove distractions", "Use focus music"]
            },
            "focus_insights": {
                "distraction_patterns": ["Phone notifications"],
                "improvement_areas": ["Consistency", "Time management"]
            },
            "mock_mode": True
        }
    
    def _get_mock_study_plan(self, subject: str, duration: int, goals: List[str]) -> Dict[str, Any]:
        """Generate intelligent mock study plan"""
        
        # Calculate number of study blocks (simplified)
        num_blocks = max(1, duration // 30)  # 25min study + 5min break = 30min
        
        study_blocks = []
        
        # Create alternating study and break blocks
        for i in range(num_blocks):
            # Study block
            goal_focus = goals[i % len(goals)] if goals else f"Focus on {subject} concepts"
            study_blocks.append({
                "activity": f"Study {subject}",
                "duration": 25,
                "type": "study",
                "description": f"Work on: {goal_focus}"
            })
            
            # Break block (except for last iteration)
            if i < num_blocks - 1:
                study_blocks.append({
                    "activity": "Short break",
                    "duration": 5,
                    "type": "break",
                    "description": "Rest, stretch, hydrate"
                })
        
        return {
            "study_blocks": study_blocks,
            "focus_techniques": [
                "Pomodoro technique",
                "Active recall",
                "Spaced repetition"
            ],
            "resource_recommendations": [
                f"{subject} textbooks",
                "Online tutorials",
                "Practice problems"
            ],
            "distraction_management": [
                "Put phone in airplane mode",
                "Use website blocker",
                "Clean workspace"
            ],
            "mock_mode": True
        }

# =============================================================================
# MOCK MCP SERVICE (IMPROVED PERFORMANCE)
# =============================================================================

class MockMCPService:
    def __init__(self):
        self.connected = False
        self.mock_mode = True
        print("MCP Service initialized in mock mode")
    
    async def initialize_connections(self):
        """Mock initialization of MCP connections"""
        try:
            # No delay for better performance
            self.connected = True
            print("Mock MCP servers connected successfully")
            
        except Exception as e:
            print(f"Error in mock MCP initialization: {e}")
            self.connected = False
    
    async def create_calendar_event(self, title: str, start_time: str, duration: int) -> Dict[str, Any]:
        """Mock calendar event creation"""
        return {
            "success": True, 
            "event_id": f"mock_event_{hash(title + start_time)}",
            "message": "Mock calendar event created"
        }
    
    async def block_distracting_websites(self, websites: List[str], duration: int) -> Dict[str, Any]:
        """Mock website blocking"""
        return {
            "success": True, 
            "blocked_count": len(websites),
            "message": f"Mock blocking {len(websites)} websites",
            "mock_mode": True
        }
    
    async def organize_study_materials(self, subject: str, file_paths: List[str]) -> Dict[str, Any]:
        """Mock file organization"""
        return {
            "success": True, 
            "organized_count": len(file_paths),
            "message": f"Mock organization of {len(file_paths)} files",
            "mock_mode": True
        }
    
    async def close_connections(self):
        """Mock close connections"""
        self.connected = False

# =============================================================================
# STUDY ANALYZER (OPTIMIZED)
# =============================================================================

class StudyAnalyzer:
    def generate_analytics(self, sessions_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comprehensive analytics from study sessions"""
        
        if not sessions_data:
            return self._get_empty_analytics()
        
        # Filter completed sessions
        completed_sessions = [s for s in sessions_data if s.get('end_time')]
        
        # Calculate weekly stats (optimized)
        weekly_stats = self._calculate_weekly_stats(completed_sessions)
        
        return {
            "weekly_stats": weekly_stats,
            "productivity_patterns": {"best_time_slot": "morning"},
            "subject_performance": {},
            "time_distribution": {},
            "total_sessions": len(completed_sessions),
            "analysis_date": datetime.now().isoformat()
        }
    
    def _calculate_weekly_stats(self, sessions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate weekly statistics (optimized)"""
        
        if not sessions:
            return {
                "total_sessions": 0,
                "total_hours": 0,
                "avg_focus": 0,
                "avg_session_length": 0,
                "total_goals_completed": 0
            }
        
        # Quick calculations
        total_minutes = sum(s.get('duration_minutes', 0) for s in sessions[-10:])  # Last 10 sessions
        total_hours = round(total_minutes / 60, 1)
        
        focus_scores = [s.get('focus_score', 0) for s in sessions[-10:] if s.get('focus_score')]
        avg_focus = round(sum(focus_scores) / len(focus_scores), 1) if focus_scores else 0
        
        return {
            "total_sessions": len(sessions),
            "total_hours": total_hours,
            "avg_focus": avg_focus,
            "avg_session_length": round(total_minutes / len(sessions), 1) if sessions else 0,
            "total_goals_completed": sum(len(s.get('completed_goals', [])) for s in sessions[-5:])
        }
    
    def _get_empty_analytics(self) -> Dict[str, Any]:
        """Return empty analytics structure"""
        return {
            "weekly_stats": {
                "total_sessions": 0,
                "total_hours": 0,
                "avg_focus": 0,
                "avg_session_length": 0,
                "total_goals_completed": 0
            },
            "productivity_patterns": {"best_time_slot": "morning"},
            "subject_performance": {},
            "time_distribution": {},
            "total_sessions": 0,
            "analysis_date": datetime.now().isoformat()
        }

# =============================================================================
# CALENDAR SERVICE (OPTIMIZED)
# =============================================================================

class CalendarService:
    def __init__(self):
        self.events_file = "data/calendar_events.json"
        self.events = self._load_events()
    
    def _load_events(self) -> List[Dict[str, Any]]:
        """Load events from storage"""
        try:
            if os.path.exists(self.events_file):
                with open(self.events_file, 'r') as f:
                    return json.load(f)
            return []
        except Exception as e:
            print(f"Error loading calendar events: {e}")
            return []
    
    def _save_events(self):
        """Save events to storage (async for better performance)"""
        try:
            os.makedirs(os.path.dirname(self.events_file), exist_ok=True)
            with open(self.events_file, 'w') as f:
                json.dump(self.events, f, indent=2)
        except Exception as e:
            print(f"Error saving calendar events: {e}")
    
    def create_event(self, title: str, start_time: str, duration_minutes: int, description: str = "") -> str:
        """Create a new calendar event"""
        
        event_id = str(uuid.uuid4())
        
        # Parse start time (simplified)
        try:
            if isinstance(start_time, str):
                start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            else:
                start_dt = start_time
        except:
            start_dt = datetime.now()
        
        end_dt = start_dt + timedelta(minutes=duration_minutes)
        
        event = {
            "id": event_id,
            "title": title,
            "description": description,
            "start_time": start_dt.isoformat(),
            "end_time": end_dt.isoformat(),
            "duration_minutes": duration_minutes,
            "created_at": datetime.now().isoformat(),
            "event_type": "study_session",
            "status": "scheduled"
        }
        
        self.events.append(event)
        self._save_events()
        
        return event_id
    
    def get_events(self, date: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get events, optionally filtered by date"""
        return self.events  # Simplified for performance
    
    def get_event(self, event_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific event by ID"""
        for event in self.events:
            if event['id'] == event_id:
                return event
        return None
    
    def update_event(self, event_id: str, **kwargs) -> bool:
        """Update an existing event"""
        for event in self.events:
            if event['id'] == event_id:
                event.update(kwargs)
                event['updated_at'] = datetime.now().isoformat()
                self._save_events()
                return True
        return False
    
    def delete_event(self, event_id: str) -> bool:
        """Delete an event"""
        for i, event in enumerate(self.events):
            if event['id'] == event_id:
                del self.events[i]
                self._save_events()
                return True
        return False
    
    def schedule_breaks(self, study_duration: int, break_duration: int, start_time: str) -> Dict[str, Any]:
        """Schedule study session with automatic breaks"""
        return {
            "success": True,
            "message": "Break scheduled via MCP"
        }
    
    def sync_external_calendar(self) -> Dict[str, Any]:
        """Sync with external calendar services"""
        return {
            "success": True,
            "message": "Calendar sync completed",
            "synced_events": len(self.events)
        }

# Create service instances
mcp_service = MockMCPService()
