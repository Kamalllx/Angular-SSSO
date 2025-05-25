import json
import os
from typing import Any, Dict, List
from datetime import datetime

def load_json_data(file_path: str) -> List[Dict[str, Any]]:
    """Load JSON data from file, return empty list if file doesn't exist"""
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        return []
    except Exception as e:
        print(f"Error loading JSON data from {file_path}: {e}")
        return []

def save_json_data(file_path: str, data: Any) -> bool:
    """Save JSON data to file"""
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        return True
    except Exception as e:
        print(f"Error saving JSON data to {file_path}: {e}")
        return False

def initialize_data_files():
    """Initialize required data files with default structure"""
    
    # Initialize study sessions file
    sessions_file = "data/study_sessions.json"
    if not os.path.exists(sessions_file):
        save_json_data(sessions_file, [])
    
    # Initialize user preferences file
    preferences_file = "data/user_preferences.json"
    if not os.path.exists(preferences_file):
        default_preferences = {
            "default_study_duration": 25,
            "default_break_duration": 5,
            "preferred_study_times": ["09:00", "14:00", "19:00"],
            "distracting_websites": [
                "facebook.com",
                "twitter.com", 
                "youtube.com",
                "instagram.com",
                "reddit.com"
            ],
            "focus_techniques": [
                "Pomodoro Technique",
                "Time blocking",
                "Active recall"
            ],
            "notifications_enabled": True,
            "auto_block_websites": True,
            "created_at": datetime.now().isoformat()
        }
        save_json_data(preferences_file, default_preferences)
    
    # Initialize calendar events file
    calendar_file = "data/calendar_events.json"
    if not os.path.exists(calendar_file):
        save_json_data(calendar_file, [])
    
    print("Data files initialized successfully")

def format_duration(minutes: int) -> str:
    """Format duration in minutes to human readable format"""
    if minutes < 60:
        return f"{minutes} minutes"
    else:
        hours = minutes // 60
        remaining_minutes = minutes % 60
        if remaining_minutes == 0:
            return f"{hours} hour{'s' if hours > 1 else ''}"
        else:
            return f"{hours} hour{'s' if hours > 1 else ''} {remaining_minutes} minutes"

def calculate_focus_score(session_data: Dict[str, Any]) -> int:
    """Calculate focus score based on session metrics"""
    
    # Base score
    score = 100
    
    # Deduct points for distractions
    distractions = session_data.get('distractions', 0)
    score -= distractions * 10
    
    # Deduct points for excessive breaks
    breaks = session_data.get('breaks_taken', 0)
    expected_breaks = session_data.get('duration_minutes', 25) // 25  # One break per 25 minutes
    if breaks > expected_breaks:
        score -= (breaks - expected_breaks) * 5
    
    # Bonus for completing goals
    goals = len(session_data.get('goals', []))
    completed_goals = len(session_data.get('completed_goals', []))
    if goals > 0:
        completion_rate = completed_goals / goals
        score += completion_rate * 20
    
    # Ensure score is between 0 and 100
    return max(0, min(100, score))

def validate_session_data(data: Dict[str, Any]) -> tuple[bool, str]:
    """Validate study session data"""
    
    required_fields = ['subject', 'duration_minutes']
    
    for field in required_fields:
        if field not in data:
            return False, f"Missing required field: {field}"
    
    # Validate duration
    duration = data.get('duration_minutes', 0)
    if not isinstance(duration, int) or duration <= 0:
        return False, "Duration must be a positive integer"
    
    if duration > 480:  # 8 hours
        return False, "Duration cannot exceed 8 hours"
    
    # Validate subject
    subject = data.get('subject', '').strip()
    if not subject:
        return False, "Subject cannot be empty"
    
    # Validate goals if provided
    goals = data.get('goals', [])
    if goals and not isinstance(goals, list):
        return False, "Goals must be a list"
    
    return True, "Valid"

def get_study_statistics(sessions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Get basic study statistics"""
    
    if not sessions:
        return {
            "total_sessions": 0,
            "total_study_time": 0,
            "average_session_length": 0,
            "total_goals": 0,
            "completed_goals": 0,
            "completion_rate": 0
        }
    
    completed_sessions = [s for s in sessions if s.get('end_time')]
    
    total_sessions = len(completed_sessions)
    total_minutes = sum(s.get('duration_minutes', 0) for s in completed_sessions)
    average_length = total_minutes / total_sessions if total_sessions > 0 else 0
    
    total_goals = sum(len(s.get('goals', [])) for s in completed_sessions)
    completed_goals = sum(len(s.get('completed_goals', [])) for s in completed_sessions)
    completion_rate = (completed_goals / total_goals * 100) if total_goals > 0 else 0
    
    return {
        "total_sessions": total_sessions,
        "total_study_time": total_minutes,
        "average_session_length": round(average_length, 1),
        "total_goals": total_goals,
        "completed_goals": completed_goals,
        "completion_rate": round(completion_rate, 1)
    }

def clean_old_sessions(max_age_days: int = 30):
    """Clean up old session data"""
    try:
        from config import Config
        sessions_data = load_json_data(Config.STUDY_SESSIONS_FILE)
        
        cutoff_date = datetime.now() - datetime.timedelta(days=max_age_days)
        
        # Filter sessions newer than cutoff date
        filtered_sessions = []
        for session in sessions_data:
            if session.get('start_time'):
                session_date = datetime.fromisoformat(session['start_time'])
                if session_date >= cutoff_date:
                    filtered_sessions.append(session)
        
        save_json_data(Config.STUDY_SESSIONS_FILE, filtered_sessions)
        print(f"Cleaned {len(sessions_data) - len(filtered_sessions)} old sessions")
        
    except Exception as e:
        print(f"Error cleaning old sessions: {e}")

def export_data_backup(backup_dir: str = "backups"):
    """Create backup of all data"""
    try:
        from config import Config
        import shutil
        
        # Create backup directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(backup_dir, f"backup_{timestamp}")
        os.makedirs(backup_path, exist_ok=True)
        
        # Copy data files
        data_files = [
            Config.STUDY_SESSIONS_FILE,
            Config.USER_PREFERENCES_FILE,
            "data/calendar_events.json"
        ]
        
        for file_path in data_files:
            if os.path.exists(file_path):
                filename = os.path.basename(file_path)
                shutil.copy2(file_path, os.path.join(backup_path, filename))
        
        print(f"Data backup created at: {backup_path}")
        return backup_path
        
    except Exception as e:
        print(f"Error creating backup: {e}")
        return None

def get_system_health() -> Dict[str, Any]:
    """Get system health information"""
    try:
        import psutil
        
        # Memory usage
        memory = psutil.virtual_memory()
        
        # Disk usage
        disk = psutil.disk_usage('/')
        
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        
        return {
            "memory_usage_percent": memory.percent,
            "disk_usage_percent": disk.percent,
            "cpu_usage_percent": cpu_percent,
            "available_memory_gb": round(memory.available / (1024**3), 2),
            "free_disk_gb": round(disk.free / (1024**3), 2),
            "status": "healthy" if memory.percent < 80 and disk.percent < 90 else "warning"
        }
    except ImportError:
        return {
            "status": "unknown",
            "message": "psutil not installed"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
