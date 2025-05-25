import os
import asyncio
import json
import platform
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import statistics
import uuid

# Google Calendar API imports
try:
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    GOOGLE_CALENDAR_AVAILABLE = True
except ImportError:
    GOOGLE_CALENDAR_AVAILABLE = False
    print("Warning: Google Calendar API not installed. Run: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")

# Try to import Groq
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    print("Warning: Groq library not installed. Using mock responses.")

# =============================================================================
# REAL GOOGLE CALENDAR SERVICE
# =============================================================================

class GoogleCalendarService:
    def __init__(self):
        self.SCOPES = ['https://www.googleapis.com/auth/calendar']
        self.service = None
        self.credentials_file = 'creds.json'
        self.token_file = 'token.json'
        
        if GOOGLE_CALENDAR_AVAILABLE:
            self.authenticate()
        else:
            print("Google Calendar API not available - using mock mode")
    
    def authenticate(self):
        """Authenticate with Google Calendar API"""
        creds = None
        
        # Check if token file exists
        if os.path.exists(self.token_file):
            creds = Credentials.from_authorized_user_file(self.token_file, self.SCOPES)
        
        # If there are no valid credentials, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    print(f"Error refreshing credentials: {e}")
                    creds = None
            
            if not creds:
                if os.path.exists(self.credentials_file):
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_file, self.SCOPES)
                    creds = flow.run_local_server(port=8001)
                else:
                    print(f"Error: {self.credentials_file} not found!")
                    return False
            
            # Save credentials for next run
            with open(self.token_file, 'w') as token:
                token.write(creds.to_json())
        
        try:
            self.service = build('calendar', 'v3', credentials=creds)
            print("✅ Google Calendar API authenticated successfully")
            return True
        except Exception as e:
            print(f"Error building calendar service: {e}")
            return False
    
    def create_event(self, title: str, start_time: str, duration_minutes: int, description: str = "") -> Dict[str, Any]:
        """Create a real Google Calendar event"""
        if not self.service:
            return {"success": False, "error": "Calendar service not authenticated"}
        
        try:
            # Parse start time
            start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            end_dt = start_dt + timedelta(minutes=duration_minutes)
            
            event = {
                'summary': title,
                'description': description,
                'start': {
                    'dateTime': start_dt.isoformat(),
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': end_dt.isoformat(),
                    'timeZone': 'UTC',
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'popup', 'minutes': 10},
                    ],
                },
            }
            
            # Create event in primary calendar
            created_event = self.service.events().insert(calendarId='primary', body=event).execute()
            
            return {
                "success": True,
                "event_id": created_event['id'],
                "event_link": created_event.get('htmlLink', ''),
                "message": "Real Google Calendar event created successfully"
            }
            
        except Exception as e:
            print(f"Error creating Google Calendar event: {e}")
            return {"success": False, "error": str(e)}
    
    def get_events(self, days_ahead: int = 7) -> List[Dict]:
        """Get events from Google Calendar"""
        if not self.service:
            return []
        
        try:
            now = datetime.utcnow().isoformat() + 'Z'
            end_time = (datetime.utcnow() + timedelta(days=days_ahead)).isoformat() + 'Z'
            
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=now,
                timeMax=end_time,
                maxResults=10,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            formatted_events = []
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                formatted_events.append({
                    'id': event['id'],
                    'title': event.get('summary', 'No Title'),
                    'start_time': start,
                    'description': event.get('description', ''),
                    'link': event.get('htmlLink', '')
                })
            
            return formatted_events
            
        except Exception as e:
            print(f"Error getting Google Calendar events: {e}")
            return []

# =============================================================================
# REAL WEBSITE BLOCKING SERVICE
# =============================================================================

class WebsiteBlockingService:
    def __init__(self):
        self.hosts_file = self._get_hosts_file_path()
        self.blocked_sites = set()
        self.block_marker = "# Smart Study Orchestrator - START"
        self.block_end_marker = "# Smart Study Orchestrator - END"
        
    def _get_hosts_file_path(self) -> str:
        """Get the hosts file path for the current OS"""
        if platform.system() == "Windows":
            return r"C:\Windows\System32\drivers\etc\hosts"
        else:  # Linux/macOS
            return "/etc/hosts"
    
    def _backup_hosts_file(self):
        """Create a backup of the hosts file"""
        backup_path = f"{self.hosts_file}.backup"
        try:
            import shutil
            shutil.copy2(self.hosts_file, backup_path)
            return True
        except Exception as e:
            print(f"Error backing up hosts file: {e}")
            return False
    
    def _read_hosts_file(self) -> List[str]:
        """Read the current hosts file"""
        try:
            with open(self.hosts_file, 'r') as f:
                return f.readlines()
        except PermissionError:
            print("❌ Permission denied. Run as administrator/sudo to block websites.")
            return []
        except Exception as e:
            print(f"Error reading hosts file: {e}")
            return []
    
    def _write_hosts_file(self, lines: List[str]) -> bool:
        """Write to the hosts file"""
        try:
            with open(self.hosts_file, 'w') as f:
                f.writelines(lines)
            
            # Flush DNS cache
            self._flush_dns_cache()
            return True
        except PermissionError:
            print("❌ Permission denied. Run as administrator/sudo to modify hosts file.")
            return False
        except Exception as e:
            print(f"Error writing hosts file: {e}")
            return False
    
    def _flush_dns_cache(self):
        """Flush DNS cache to make changes take effect immediately"""
        try:
            if platform.system() == "Windows":
                subprocess.run(["ipconfig", "/flushdns"], check=True, capture_output=True)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["sudo", "dscacheutil", "-flushcache"], check=True, capture_output=True)
            elif platform.system() == "Linux":
                # Try different methods for different Linux distributions
                try:
                    subprocess.run(["sudo", "systemctl", "restart", "systemd-resolved"], check=True, capture_output=True)
                except:
                    try:
                        subprocess.run(["sudo", "/etc/init.d/networking", "restart"], check=True, capture_output=True)
                    except:
                        pass
            print("✅ DNS cache flushed")
        except Exception as e:
            print(f"Warning: Could not flush DNS cache: {e}")
    
    def block_websites(self, websites: List[str], duration_minutes: int) -> Dict[str, Any]:
        """Block websites by modifying hosts file"""
        if not websites:
            return {"success": False, "error": "No websites specified"}
        
        # Create backup first
        if not self._backup_hosts_file():
            print("Warning: Could not create hosts file backup")
        
        # Read current hosts file
        lines = self._read_hosts_file()
        if not lines:
            return {"success": False, "error": "Could not read hosts file. Run as administrator/sudo."}
        
        # Remove any existing blocks first
        self.unblock_websites()
        
        # Re-read after cleanup
        lines = self._read_hosts_file()
        
        # Add new blocks
        block_entries = [f"\n{self.block_marker}\n"]
        for website in websites:
            # Block both with and without www
            block_entries.append(f"127.0.0.1 {website}\n")
            block_entries.append(f"127.0.0.1 www.{website}\n")
            self.blocked_sites.add(website)
        
        block_entries.append(f"{self.block_end_marker}\n")
        
        # Add blocks to hosts file
        lines.extend(block_entries)
        
        if self._write_hosts_file(lines):
            print(f"✅ Blocked {len(websites)} websites: {', '.join(websites)}")
            
            # Schedule unblocking (in a real app, you'd use a proper scheduler)
            # For now, just return success
            return {
                "success": True,
                "blocked_count": len(websites),
                "blocked_sites": list(websites),
                "duration_minutes": duration_minutes,
                "message": f"Successfully blocked {len(websites)} websites",
                "note": f"Websites will remain blocked until manually unblocked or system restart"
            }
        else:
            return {"success": False, "error": "Failed to modify hosts file. Check permissions."}
    
    def unblock_websites(self) -> Dict[str, Any]:
        """Remove website blocks from hosts file"""
        print("🔓 Starting website unblock process...")
        
        lines = self._read_hosts_file()
        if not lines:
            return {"success": False, "error": "Could not read hosts file"}
        
        # Remove lines between our markers
        new_lines = []
        skip_lines = False
        removed_lines = 0
        
        for line in lines:
            if self.block_marker in line:
                skip_lines = True
                continue
            elif self.block_end_marker in line:
                skip_lines = False
                continue
            
            if skip_lines:
                removed_lines += 1
            else:
                new_lines.append(line)
        
        if self._write_hosts_file(new_lines):
            print(f"✅ Removed {removed_lines} blocked website entries")
            self.blocked_sites.clear()
            return {
                "success": True, 
                "message": f"Unblocked all websites ({removed_lines} entries removed)",
                "removed_entries": removed_lines
            }
        else:
            return {"success": False, "error": "Failed to modify hosts file"}

    
    def get_blocked_websites(self) -> List[str]:
        """Get currently blocked websites"""
        return list(self.blocked_sites)

# =============================================================================
# ENHANCED GROQ SERVICE (with better error handling)
# =============================================================================

class GroqService:
    def __init__(self):
        self.groq_available = GROQ_AVAILABLE and bool(os.getenv('GROQ_API_KEY'))
        
        if self.groq_available:
            self.client = Groq(api_key=os.getenv('GROQ_API_KEY'))
            self.model = "llama-3.1-8b-instant"
            print("✅ Groq AI service initialized successfully")
        else:
            self.client = None
            self.model = None
            print("⚠️  Groq AI service initialized in mock mode (add GROQ_API_KEY for real AI)")
    
    def analyze_study_pattern(self, study_sessions: List[Dict]) -> Dict[str, Any]:
        """Analyze study patterns using real AI or intelligent mock"""
        
        if not self.groq_available:
            print("🤖 Using intelligent mock analysis (set GROQ_API_KEY for real AI)")
            return self._get_intelligent_mock_analysis(study_sessions)
        
        # Real AI analysis
        print("🤖 Using real Groq AI for analysis")
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
                timeout=15
            )
            
            result = response.choices[0].message.content.strip()
            
            # Clean up markdown if present
            if result.startswith('```'):
                lines = result.split('\n')
                result = '\n'.join(lines[1:-1] if lines[-1].strip() == '```' else lines[1:])

            parsed_result = json.loads(result)
            parsed_result["ai_mode"] = "real"
            return parsed_result
            
        except Exception as e:
            print(f"⚠️  Real AI analysis failed: {e}")
            print("🤖 Falling back to intelligent mock analysis")
            return self._get_intelligent_mock_analysis(study_sessions)
    
    def generate_study_plan(self, subject: str, duration: int, goals: List[str]) -> Dict[str, Any]:
        """Generate study plan using real AI or intelligent mock"""
        
        if not self.groq_available:
            print("🤖 Using intelligent mock study plan (set GROQ_API_KEY for real AI)")
            return self._get_intelligent_mock_study_plan(subject, duration, goals)
        
        # Real AI study plan generation
        print("🤖 Using real Groq AI for study plan generation")
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
                timeout=15
            )
            
            result = response.choices[0].message.content.strip()
            
            # Clean up markdown if present
            if result.startswith('```'):
                lines = result.split('\n')
                result = '\n'.join(lines[1:-1] if lines[-1].strip() == '```' else lines[1:])

            parsed_result = json.loads(result)
            parsed_result["ai_mode"] = "real"
            return parsed_result
            
        except Exception as e:
            print(f"⚠️  Real AI study plan failed: {e}")
            print("🤖 Falling back to intelligent mock study plan")
            return self._get_intelligent_mock_study_plan(subject, duration, goals)
    
    def _get_intelligent_mock_analysis(self, study_sessions: List[Dict]) -> Dict[str, Any]:
        """Generate intelligent mock analysis based on actual session data"""
        
        if not study_sessions:
            return self._get_default_analysis()
        
        # Analyze actual data for intelligent responses
        subjects = list(set(s.get('subject', 'Unknown') for s in study_sessions))
        avg_duration = sum(s.get('duration_minutes', 25) for s in study_sessions) / len(study_sessions)
        
        # Generate time-based recommendations
        current_hour = datetime.now().hour
        if 6 <= current_hour < 12:
            best_time = "morning"
        elif 12 <= current_hour < 18:
            best_time = "afternoon"
        else:
            best_time = "evening"
        
        return {
            "productivity_trends": {
                "best_time_slots": [best_time, "morning"],
                "optimal_duration": int(avg_duration),
                "peak_focus_subjects": subjects[:2]
            },
            "recommendations": {
                "study_schedule": f"Based on your {len(study_sessions)} sessions, continue with {int(avg_duration)}-minute focused sessions",
                "break_frequency": "Take a 5-minute break every 25 minutes to maintain focus",
                "environment_tips": ["Turn off notifications", "Use noise-canceling headphones", "Keep water nearby"]
            },
            "focus_insights": {
                "distraction_patterns": ["Digital distractions", "Multitasking"],
                "improvement_areas": ["Consistent scheduling", "Goal specificity"]
            },
            "ai_mode": "intelligent_mock"
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
                "environment_tips": ["Create a dedicated study space", "Use focus music"]
            },
            "focus_insights": {
                "distraction_patterns": ["Phone notifications"],
                "improvement_areas": ["Building study habits", "Time management"]
            },
            "ai_mode": "default_mock"
        }
    
    def _get_intelligent_mock_study_plan(self, subject: str, duration: int, goals: List[str]) -> Dict[str, Any]:
        """Generate intelligent mock study plan"""
        
        # Calculate study blocks based on Pomodoro technique
        num_pomodoros = max(1, duration // 30)  # 25min study + 5min break = 30min
        
        study_blocks = []
        
        for i in range(num_pomodoros):
            # Study block
            goal_focus = goals[i % len(goals)] if goals else f"Focus on {subject} fundamentals"
            
            study_blocks.append({
                "activity": f"Study {subject}",
                "duration": 25,
                "type": "study",
                "description": f"Work on: {goal_focus}"
            })
            
            # Break block (except for last iteration)
            if i < num_pomodoros - 1:
                study_blocks.append({
                    "activity": "Short break",
                    "duration": 5,
                    "type": "break",
                    "description": "Rest, stretch, hydrate"
                })
        
        # Subject-specific recommendations
        subject_lower = subject.lower()
        if "math" in subject_lower:
            focus_techniques = ["Work through practice problems", "Use spaced repetition", "Explain concepts aloud"]
            resources = ["Textbook exercises", "Khan Academy", "Practice problem sets"]
        elif "science" in subject_lower:
            focus_techniques = ["Visual diagrams", "Concept mapping", "Laboratory practice"]
            resources = ["Scientific journals", "Lab manuals", "Educational videos"]
        elif "language" in subject_lower:
            focus_techniques = ["Flashcards", "Speaking practice", "Immersion techniques"]
            resources = ["Language apps", "Native speaker content", "Grammar guides"]
        else:
            focus_techniques = ["Active reading", "Note-taking", "Self-testing"]
            resources = ["Course materials", "Online lectures", "Study guides"]
        
        return {
            "study_blocks": study_blocks,
            "focus_techniques": focus_techniques,
            "resource_recommendations": resources,
            "distraction_management": [
                "Put phone in airplane mode",
                "Use website blocker",
                "Clean, organized workspace",
                "Inform others of study time"
            ],
            "ai_mode": "intelligent_mock"
        }

# =============================================================================
# REAL MCP SERVICE (combining real implementations)
# =============================================================================

class RealMCPService:
    def __init__(self):
        self.calendar_service = GoogleCalendarService()
        self.website_blocker = WebsiteBlockingService()
        self.connected = True
        self.mock_mode = not (GOOGLE_CALENDAR_AVAILABLE and self.calendar_service.service)
        
        if self.mock_mode:
            print("⚠️  MCP Service running in partial mock mode (some features unavailable)")
        else:
            print("✅ MCP Service initialized with real integrations")
    
    async def initialize_connections(self):
        """Initialize all MCP connections"""
        try:
            self.connected = True
            print("✅ Real MCP services connected successfully")
        except Exception as e:
            print(f"Error in MCP initialization: {e}")
            self.connected = False
    
    async def create_calendar_event(self, title: str, start_time: str, duration: int) -> Dict[str, Any]:
        """Create real calendar event"""
        print(f"🗓️  Creating real Google Calendar event: {title}")
        
        if self.calendar_service.service:
            result = self.calendar_service.create_event(title, start_time, duration)
            return result
        else:
            return {
                "success": False,
                "error": "Google Calendar service not available",
                "fallback": "Event not created - check Google Calendar setup"
            }
    
    async def block_distracting_websites(self, websites: List[str], duration: int) -> Dict[str, Any]:
        """Block websites using real system-level blocking"""
        print(f"🚫 Blocking {len(websites)} websites at system level")
        
        result = self.website_blocker.block_websites(websites, duration)
        return result
    
    async def unblock_websites(self) -> Dict[str, Any]:
        """Unblock all websites"""
        print("🔓 Unblocking all websites")
        return self.website_blocker.unblock_websites()
    
    async def get_blocked_websites(self) -> List[str]:
        """Get list of currently blocked websites"""
        return self.website_blocker.get_blocked_websites()
    
    async def close_connections(self):
        """Close MCP connections"""
        print("🔌 Closing MCP connections")
        self.connected = False

# =============================================================================
# STUDY ANALYZER (keeping existing implementation)
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
# CALENDAR SERVICE (using real Google Calendar)
# =============================================================================

class CalendarService:
    def __init__(self):
        self.google_calendar = GoogleCalendarService()
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
        """Save events to storage"""
        try:
            os.makedirs(os.path.dirname(self.events_file), exist_ok=True)
            with open(self.events_file, 'w') as f:
                json.dump(self.events, f, indent=2)
        except Exception as e:
            print(f"Error saving calendar events: {e}")
    
    def create_event(self, title: str, start_time: str, duration_minutes: int, description: str = "") -> str:
        """Create event in both Google Calendar and local storage"""
        
        # Try to create in Google Calendar first
        google_result = self.google_calendar.create_event(title, start_time, duration_minutes, description)
        
        event_id = str(uuid.uuid4())
        
        # Parse start time
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
            "status": "scheduled",
            "google_calendar_id": google_result.get("event_id") if google_result.get("success") else None,
            "google_calendar_link": google_result.get("event_link") if google_result.get("success") else None
        }
        
        self.events.append(event)
        self._save_events()
        
        if google_result.get("success"):
            print(f"✅ Event created in Google Calendar: {google_result.get('event_link', '')}")
        
        return event_id
    
    def get_events(self, date: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get events from both local storage and Google Calendar"""
        local_events = self.events.copy()
        
        # Try to get Google Calendar events
        google_events = self.google_calendar.get_events()
        
        # Merge events (avoiding duplicates)
        all_events = local_events.copy()
        
        for g_event in google_events:
            # Check if this Google event is already in local storage
            exists = any(
                event.get('google_calendar_id') == g_event['id'] 
                for event in local_events
            )
            
            if not exists:
                # Add Google event to the list
                all_events.append({
                    "id": f"google_{g_event['id']}",
                    "title": g_event['title'],
                    "start_time": g_event['start_time'],
                    "description": g_event['description'],
                    "event_type": "google_calendar",
                    "google_calendar_id": g_event['id'],
                    "google_calendar_link": g_event.get('link', '')
                })
        
        return all_events
    
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
        try:
            start_dt = datetime.fromisoformat(start_time)
            
            # Create study session event
            study_event_id = self.create_event(
                title="Study Session",
                start_time=start_dt.isoformat(),
                duration_minutes=study_duration,
                description="Focused study time"
            )
            
            # Create break event
            break_start = start_dt + timedelta(minutes=study_duration)
            break_event_id = self.create_event(
                title="Study Break",
                start_time=break_start.isoformat(),
                duration_minutes=break_duration,
                description="Take a break and recharge"
            )
            
            return {
                "success": True,
                "study_event_id": study_event_id,
                "break_event_id": break_event_id,
                "message": "Study session and break scheduled successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def sync_external_calendar(self) -> Dict[str, Any]:
        """Sync with Google Calendar"""
        try:
            google_events = self.google_calendar.get_events()
            return {
                "success": True,
                "message": "Google Calendar sync completed",
                "synced_events": len(google_events),
                "events": google_events
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

# Create service instances with real implementations
mcp_service = RealMCPService()
