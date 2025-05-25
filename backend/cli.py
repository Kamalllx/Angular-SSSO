
#!/usr/bin/env python3
"""
Smart Study Orchestrator CLI - FIXED VERSION
"""

import requests
import json
import time
import sys
import os
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import argparse
from colorama import Fore, Back, Style, init
import questionary

# Initialize colorama for cross-platform colored output
init(autoreset=True)

class StudyOrchestratorCLI:
    def __init__(self, backend_url: str = "http://localhost:5000"):
        self.backend_url = backend_url
        self.current_session = None
        self.session_active = False
        
        # Check backend connectivity
        self.check_backend_health()
    
    def check_backend_health(self):
        """Check if backend is running and accessible"""
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=5)
            if response.status_code == 200:
                print(f"{Fore.GREEN}✅ Backend connected successfully")
                
                # Get system status
                status_response = requests.get(f"{self.backend_url}/api/status")
                if status_response.status_code == 200:
                    status = status_response.json()
                    self.print_system_status(status)
            else:
                print(f"{Fore.RED}❌ Backend health check failed")
                sys.exit(1)
        except requests.exceptions.RequestException as e:
            print(f"{Fore.RED}❌ Cannot connect to backend at {self.backend_url}")
            print(f"Error: {e}")
            print("Make sure the backend is running with: python run.py")
            sys.exit(1)
    
    def print_system_status(self, status: Dict):
        """Display system status in a nice format"""
        print(f"\n{Fore.CYAN}System Status:")
        print("="*30)
        print(f"Backend: 🟢 Online")
        
        # MCP status
        mcp_status = "🟢 Connected" if status.get('mcp_connected') else "🔴 Disconnected"
        mcp_mode = " (Mock Mode)" if status.get('mock_mode') else ""
        print(f"MCP Services: {mcp_status}{mcp_mode}")
        
        # AI status
        ai_status = "🟢 Available" if status.get('groq_available') else "🟡 Mock Mode"
        print(f"AI Assistant: {ai_status}")
        print()
    
    def main_menu(self):
        """Display main menu and handle user selection"""
        while True:
            # Clear console properly
            os.system('cls' if os.name == 'nt' else 'clear')
            
            print(f"{Fore.CYAN}{'='*60}")
            print(f"{Fore.CYAN}🧠 Smart Study Orchestrator CLI")
            print(f"{Fore.WHITE}AI-Powered Study Session Management")
            print(f"{Fore.CYAN}{'='*60}")
            
            choices = [
                "📚 Start New Study Session",
                "⏱️  Resume Active Session" if self.current_session else None,
                "📊 View Analytics & Insights", 
                "📅 Calendar Management",
                "⚙️  Preferences & Settings",
                "🔧 System Tools",
                "❌ Exit"
            ]
            
            # Filter out None choices
            choices = [choice for choice in choices if choice is not None]
            
            try:
                choice = questionary.select(
                    "What would you like to do?",
                    choices=choices,
                    style=questionary.Style([
                        ('question', 'bold'),
                        ('pointer', 'fg:#ff6d00 bold'),
                        ('highlighted', 'fg:#ff6d00 bold'),
                        ('selected', 'fg:#00ff41 bold'),
                    ])
                ).ask()
                
                if not choice:
                    break
                
                # Handle menu selections
                if "Start New Study Session" in choice:
                    self.create_study_session()
                elif "Resume Active Session" in choice:
                    self.resume_session()
                elif "View Analytics" in choice:
                    self.view_analytics()
                elif "Calendar Management" in choice:
                    self.calendar_menu()
                elif "Preferences" in choice:
                    self.preferences_menu()
                elif "System Tools" in choice:
                    self.system_tools_menu()
                elif "Exit" in choice:
                    print(f"{Fore.YELLOW}👋 Thank you for using Smart Study Orchestrator!")
                    break
            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}👋 Goodbye!")
                break
            except Exception as e:
                print(f"{Fore.RED}❌ Error in menu: {e}")
                input("Press Enter to continue...")
    
    def resume_session(self):
        """Resume an active study session"""
        if not self.current_session:
            print(f"{Fore.RED}❌ No active session to resume")
            input("Press Enter to continue...")
            return
        
        print(f"{Fore.GREEN}▶️  Resuming session: {self.current_session['subject']}")
        self.start_session()
    
    def create_study_session(self):
        """Create a new study session with user input - FIXED"""
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"{Fore.CYAN}📚 Create New Study Session")
        print("="*40)
        
        try:
            subject = questionary.text(
                "📖 What subject are you studying?",
                validate=lambda x: len(x.strip()) > 0 or "Subject cannot be empty"
            ).ask()
            
            if not subject:
                return
            
            duration_options = ["15 minutes", "25 minutes (Pomodoro)", "45 minutes", "60 minutes", "90 minutes", "Custom"]
            duration_choice = questionary.select(
                "⏰ How long do you want to study?",
                choices=duration_options
            ).ask()
            
            if not duration_choice:
                return
            
            # Parse duration
            if "Custom" in duration_choice:
                duration_input = questionary.text(
                    "Enter duration in minutes:",
                    validate=lambda x: x.isdigit() and int(x) > 0 or "Please enter a valid number"
                ).ask()
                duration = int(duration_input) if duration_input else 25
            else:
                duration = int(duration_choice.split()[0])
            
            # Get study goals
            goals = []
            print(f"\n{Fore.YELLOW}🎯 Study Goals (press Enter with empty input to finish)")
            while True:
                goal = input(f"Goal {len(goals) + 1}: ").strip()
                if not goal:
                    break
                goals.append(goal)
            
            if not goals:
                goals = [f"Complete {subject} study session"]
            
            # Website blocking option
            block_websites = questionary.confirm(
                "🚫 Block distracting websites during this session?",
                default=True
            ).ask()
            
            # Create session via API
            session_data = {
                "subject": subject,
                "duration": duration,
                "goals": goals
            }
            
            print(f"{Fore.BLUE}🔄 Creating study session...")
            try:
                response = requests.post(f"{self.backend_url}/api/study/session", json=session_data)
                if response.status_code == 201:
                    self.current_session = response.json()
                    print(f"{Fore.GREEN}✅ Study session created successfully!")
                    
                    # Generate AI study plan
                    self.generate_study_plan(subject, duration, goals)
                    
                    # Block websites if requested - FIXED
                    if block_websites:
                        self.block_websites_fixed(duration)
                    
                    # Ask if user wants to start immediately
                    start_now = questionary.confirm("🚀 Start the session now?", default=True).ask()
                    if start_now:
                        self.start_session()
                else:
                    print(f"{Fore.RED}❌ Failed to create session: {response.text}")
            except Exception as e:
                print(f"{Fore.RED}❌ Error creating session: {e}")
        except Exception as e:
            print(f"{Fore.RED}❌ Error in session creation: {e}")
        
        input("\nPress Enter to continue...")
    
    def block_websites_fixed(self, duration: int):
        """Fixed website blocking function"""
        # Default websites to block
        default_sites = [
            "facebook.com", 
            "twitter.com", 
            "youtube.com", 
            "instagram.com", 
            "reddit.com", 
            "tiktok.com",
            "www.facebook.com",
            "www.twitter.com", 
            "www.youtube.com", 
            "www.instagram.com", 
            "www.reddit.com", 
            "www.tiktok.com"
        ]
        
        print(f"{Fore.YELLOW}🚫 Activating website blocking...")
        try:
            # Make sure we send a proper list of websites
            blocking_data = {
                "websites": default_sites,  # Send actual list, not empty
                "duration": duration
            }
            
            print(f"{Fore.BLUE}Debug: Sending {len(default_sites)} websites to block")
            
            response = requests.post(
                f"{self.backend_url}/api/study/block-websites", 
                json=blocking_data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                blocked_count = result.get('blocked_count', 0)
                
                if blocked_count > 0:
                    print(f"{Fore.GREEN}🚫 Successfully blocked {blocked_count} websites for {duration} minutes")
                    print(f"{Fore.WHITE}Blocked sites: {', '.join(default_sites[:3])} and {blocked_count-3} more...")
                else:
                    print(f"{Fore.YELLOW}⚠️  No websites were blocked. Check admin permissions.")
                
                if result.get("mock_mode"):
                    print(f"{Fore.YELLOW}🤖 Note: Running in demo mode")
            else:
                print(f"{Fore.YELLOW}⚠️  Website blocking request failed: {response.status_code}")
        except Exception as e:
            print(f"{Fore.YELLOW}⚠️  Website blocking error: {e}")
    
    def generate_study_plan(self, subject: str, duration: int, goals: List[str]):
        """Generate AI-powered study plan"""
        print(f"{Fore.BLUE}🤖 AI is generating your personalized study plan...")
        try:
            plan_data = {
                "subject": subject,
                "duration": duration,
                "goals": goals
            }
            response = requests.post(f"{self.backend_url}/api/study/plan", json=plan_data)
            
            if response.status_code == 200:
                plan = response.json()
                self.display_study_plan(plan)
            else:
                print(f"{Fore.YELLOW}⚠️  Could not generate AI study plan: {response.text}")
        except Exception as e:
            print(f"{Fore.YELLOW}⚠️  AI study plan generation failed: {e}")
    
    def display_study_plan(self, plan: Dict):
        """Display the AI-generated study plan"""
        print(f"\n{Fore.BLUE}🤖 AI-Generated Study Plan")
        print("="*40)
        
        # Check if using real AI or mock
        if plan.get("ai_mode") == "real":
            print(f"{Fore.GREEN}✅ Generated using real AI (Groq)")
        else:
            print(f"{Fore.YELLOW}🤖 Generated using intelligent mock AI")
        
        # Study blocks
        if "study_blocks" in plan and plan["study_blocks"]:
            print(f"\n{Fore.CYAN}📅 Study Schedule:")
            for i, block in enumerate(plan["study_blocks"], 1):
                activity_icon = "📚" if block["type"] == "study" else "☕"
                print(f"  {i}. {activity_icon} {block['activity']} ({block['duration']} min)")
                print(f"     {Fore.WHITE}{block['description']}")
        
        # Focus techniques
        if "focus_techniques" in plan and plan["focus_techniques"]:
            print(f"\n{Fore.GREEN}🧠 Recommended Focus Techniques:")
            for technique in plan["focus_techniques"]:
                print(f"  • {technique}")
        
        # Resources
        if "resource_recommendations" in plan and plan["resource_recommendations"]:
            print(f"\n{Fore.MAGENTA}📖 Recommended Resources:")
            for resource in plan["resource_recommendations"]:
                print(f"  • {resource}")
    
    def start_session(self):
        """Start the current study session with real-time timer"""
        if not self.current_session:
            print(f"{Fore.RED}❌ No session to start")
            return
        
        # Start session via API
        try:
            response = requests.post(f"{self.backend_url}/api/study/session/{self.current_session['id']}/start")
            if response.status_code != 200:
                print(f"{Fore.RED}❌ Failed to start session: {response.text}")
                return
        except Exception as e:
            print(f"{Fore.RED}❌ Error starting session: {e}")
            return
        
        self.session_active = True
        duration_seconds = self.current_session['duration_minutes'] * 60
        
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"{Fore.GREEN}🚀 Study Session Started!")
        print(f"📖 Subject: {self.current_session['subject']}")
        print(f"⏱️  Duration: {self.current_session['duration_minutes']} minutes")
        print("="*50)
        
        # Real-time timer display
        start_time = time.time()
        
        try:
            while self.session_active and duration_seconds > 0:
                elapsed = int(time.time() - start_time)
                remaining = duration_seconds - elapsed
                
                if remaining <= 0:
                    break
                
                # Format time display
                mins, secs = divmod(remaining, 60)
                hours, mins = divmod(mins, 60)
                
                if hours > 0:
                    time_display = f"{hours:02d}:{mins:02d}:{secs:02d}"
                else:
                    time_display = f"{mins:02d}:{secs:02d}"
                
                # Progress bar
                progress = (elapsed / duration_seconds) * 100
                bar_length = 40
                filled_length = int(bar_length * progress / 100)
                bar = "█" * filled_length + "░" * (bar_length - filled_length)
                
                # Color coding based on time remaining
                if remaining <= 60:  # Last minute - red
                    color = Fore.RED
                elif remaining <= 300:  # Last 5 minutes - yellow
                    color = Fore.YELLOW
                else:  # Normal - green
                    color = Fore.GREEN
                
                # Display timer
                os.system('cls' if os.name == 'nt' else 'clear')
                print(f"{color}⏱️  {time_display}")
                print(f"📖 {self.current_session['subject']}")
                print(f"Progress: {bar} {progress:.1f}%")
                print(f"\n💡 Goals:")
                for goal in self.current_session.get('goals', []):
                    print(f"  • {goal}")
                print(f"\n{Fore.WHITE}Press Ctrl+C to pause/end session")
                
                time.sleep(1)
            
            # Session completed
            if remaining <= 0:
                os.system('cls' if os.name == 'nt' else 'clear')
                print(f"{Fore.GREEN}🎉 Congratulations!")
                print(f"You've completed your {self.current_session['duration_minutes']}-minute study session!")
                print(f"Subject: {self.current_session['subject']}")
                self.end_session(completed=True)
        
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}⏸️  Session paused")
            self.pause_menu()
    
    def pause_menu(self):
        """Handle session pause menu - UPDATED with unblock option"""
        try:
            choice = questionary.select(
                "What would you like to do?",
                choices=[
                    "▶️  Resume Session",
                    "⏹️  End Session",
                    "🔓 Unblock Websites Temporarily",  # NEW OPTION
                    "📊 Add Distraction",
                    "☕ Take Break"
                ]
            ).ask()
            
            if "Resume" in choice:
                print(f"{Fore.GREEN}▶️  Resuming session...")
                return  # Return to timer loop
            elif "End Session" in choice:
                self.end_session(completed=False)
            elif "Unblock Websites" in choice:
                print(f"{Fore.BLUE}🔓 Temporarily unblocking websites...")
                self.unblock_websites()
                print(f"{Fore.YELLOW}⚠️  Remember to re-enable blocking if needed!")
                input("Press Enter to continue...")
            elif "Add Distraction" in choice:
                self.record_distraction()
            elif "Take Break" in choice:
                self.take_break()
        except Exception as e:
            print(f"{Fore.RED}❌ Error in pause menu: {e}")
            self.end_session(completed=False)

    
    def record_distraction(self):
        """Record a distraction event"""
        try:
            distraction = questionary.text("What distracted you?").ask()
            if distraction:
                print(f"{Fore.YELLOW}📝 Recorded distraction: {distraction}")
        except Exception as e:
            print(f"{Fore.RED}❌ Error recording distraction: {e}")
    
    def take_break(self):
        """Take a study break"""
        try:
            break_duration = questionary.select(
                "How long is your break?",
                choices=["5 minutes", "10 minutes", "15 minutes"]
            ).ask()
            
            if break_duration:
                minutes = int(break_duration.split()[0])
                print(f"{Fore.BLUE}☕ Enjoy your {minutes}-minute break!")
                
                # Simple break timer
                for i in range(minutes * 60, 0, -1):
                    mins, secs = divmod(i, 60)
                    print(f"\r☕ Break time remaining: {mins:02d}:{secs:02d}", end="", flush=True)
                    time.sleep(1)
                
                print(f"\n{Fore.GREEN}🔔 Break time is over! Let's get back to studying.")
        except Exception as e:
            print(f"{Fore.RED}❌ Error in break: {e}")
    
    def end_session(self, completed: bool = False):
        """End the current study session - FIXED with auto-unblock"""
        if not self.current_session:
            return
        
        self.session_active = False
        
        try:
            # Get session completion details
            if completed:
                focus_score = 85  # Auto-score for completed sessions
                completed_goals = self.current_session.get('goals', [])
            else:
                try:
                    focus_score_input = questionary.text(
                        "Rate your focus (0-100):",
                        validate=lambda x: x.isdigit() and 0 <= int(x) <= 100 or "Enter a number between 0-100"
                    ).ask()
                    focus_score = int(focus_score_input) if focus_score_input else 50
                except:
                    focus_score = 50
                
                # Let user select completed goals
                if self.current_session.get('goals'):
                    try:
                        completed_goals = questionary.checkbox(
                            "Which goals did you complete?",
                            choices=self.current_session['goals']
                        ).ask() or []
                    except:
                        completed_goals = []
                else:
                    completed_goals = []
            
            try:
                notes = questionary.text("Any notes about this session? (optional)").ask() or ""
            except:
                notes = ""
            
            # End session via API
            session_data = {
                "focus_score": focus_score,
                "completed_goals": completed_goals,
                "notes": notes,
                "distractions": 0,
                "breaks_taken": 0
            }
            
            try:
                response = requests.post(
                    f"{self.backend_url}/api/study/session/{self.current_session['id']}/end", 
                    json=session_data
                )
                
                if response.status_code == 200:
                    print(f"{Fore.GREEN}✅ Study session saved successfully!")
                    self.show_session_summary(focus_score, completed_goals, notes)
                else:
                    print(f"{Fore.YELLOW}⚠️  Session data may not have been saved: {response.text}")
            except Exception as e:
                print(f"{Fore.YELLOW}⚠️  Error saving session: {e}")
            
            # AUTOMATICALLY UNBLOCK WEBSITES WHEN SESSION ENDS
            print(f"\n{Fore.BLUE}🔓 Automatically unblocking websites...")
            self.unblock_websites()
            
            self.current_session = None
        except Exception as e:
            print(f"{Fore.RED}❌ Error ending session: {e}")
            self.current_session = None
        
        input("\nPress Enter to continue...")

    def unblock_websites(self):
        """Unblock all blocked websites"""
        try:
            response = requests.post(f"{self.backend_url}/api/study/unblock-websites", timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    removed_entries = result.get("removed_entries", 0)
                    print(f"{Fore.GREEN}✅ Successfully unblocked all websites ({removed_entries} entries removed)")
                else:
                    print(f"{Fore.YELLOW}⚠️  Unblock failed: {result.get('error', 'Unknown error')}")
            else:
                print(f"{Fore.YELLOW}⚠️  Unblock request failed: {response.status_code}")
        except Exception as e:
            print(f"{Fore.YELLOW}⚠️  Error unblocking websites: {e}")



    def manual_unblock_websites(self):
        """Manually unblock all websites - NEW METHOD"""
        print(f"{Fore.BLUE}🔓 Manually Unblocking All Websites")
        print("="*40)
        
        confirm = questionary.confirm(
            "This will unblock ALL websites that were blocked by the study app. Continue?",
            default=True
        ).ask()
        
        if confirm:
            print(f"{Fore.BLUE}🔓 Removing website blocks...")
            self.unblock_websites()
        else:
            print(f"{Fore.YELLOW}⏹️  Unblock cancelled")
        
        input("\nPress Enter to continue...")


    # Add cleanup on program exit
    def __del__(self):
        """Cleanup when CLI is destroyed"""
        try:
            print(f"{Fore.BLUE}🔓 Cleaning up - unblocking websites...")
            self.unblock_websites()
        except:
            pass  # Ignore errors during cleanup

    # Update the main function to handle Ctrl+C gracefully


    def show_session_summary(self, focus_score: int, completed_goals: List[str], notes: str):
        """Display session completion summary"""
        print(f"\n{Fore.CYAN}📊 Session Summary")
        print("="*30)
        print(f"Focus Score: {focus_score}/100")
        print(f"Goals Completed: {len(completed_goals)}/{len(self.current_session.get('goals', []))}")
        print(f"Subject: {self.current_session['subject']}")
        print(f"Duration: {self.current_session['duration_minutes']} minutes")
        
        if notes:
            print(f"Notes: {notes}")
        
        # Focus score feedback
        if focus_score >= 80:
            print(f"{Fore.GREEN}🎉 Excellent focus! Keep up the great work!")
        elif focus_score >= 60:
            print(f"{Fore.YELLOW}👍 Good session! Try to minimize distractions next time.")
        else:
            print(f"{Fore.RED}💪 Room for improvement. Consider using focus techniques!")
    
    def view_analytics(self):
        """Display study analytics and insights"""
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print(f"{Fore.BLUE}📊 Loading analytics...")
        try:
            response = requests.get(f"{self.backend_url}/api/study/analytics")
            if response.status_code == 200:
                analytics = response.json()
                self.display_analytics(analytics)
            else:
                print(f"{Fore.RED}❌ Failed to load analytics: {response.text}")
        except Exception as e:
            print(f"{Fore.RED}❌ Error loading analytics: {e}")
        
        input("\nPress Enter to continue...")
    
    def display_analytics(self, analytics: Dict):
        """Display analytics in a formatted way"""
        print(f"{Fore.BLUE}📊 Study Analytics & Insights")
        print("="*40)
        
        # Weekly stats
        weekly_stats = analytics.get("weekly_stats", {})
        if weekly_stats:
            print(f"{Fore.CYAN}📈 Weekly Statistics:")
            print(f"  Total Sessions: {weekly_stats.get('total_sessions', 0)}")
            print(f"  Study Hours: {weekly_stats.get('total_hours', 0)}h")
            print(f"  Average Focus: {weekly_stats.get('avg_focus', 0)}%")
            print(f"  Goals Completed: {weekly_stats.get('total_goals_completed', 0)}")
            print(f"  Avg Session Length: {weekly_stats.get('avg_session_length', 0)} min")
        
        # AI Recommendations
        recommendations = analytics.get("recommendations", {})
        if recommendations:
            print(f"\n{Fore.GREEN}🤖 AI Recommendations:")
            
            if recommendations.get("study_schedule"):
                print(f"  📅 Schedule: {recommendations['study_schedule']}")
            
            if recommendations.get("break_frequency"):
                print(f"  ☕ Breaks: {recommendations['break_frequency']}")
    
    def calendar_menu(self):
        """Calendar management menu"""
        try:
            choice = questionary.select(
                "📅 Calendar Management",
                choices=[
                    "📋 View Events",
                    "➕ Create Event", 
                    "⏰ Schedule Study Break",
                    "🔄 Sync Calendar",
                    "⬅️  Back to Main Menu"
                ]
            ).ask()
            
            if not choice or "Back to Main Menu" in choice:
                return
            elif "View Events" in choice:
                self.view_calendar_events()
            elif "Create Event" in choice:
                self.create_calendar_event_fixed()  # Fixed function
            elif "Schedule Study Break" in choice:
                self.schedule_study_break()
            elif "Sync Calendar" in choice:
                self.sync_calendar()
        except Exception as e:
            print(f"{Fore.RED}❌ Error in calendar menu: {e}")
            input("Press Enter to continue...")
    
    def create_calendar_event_fixed(self):
        """Create a new calendar event - FIXED for Google Calendar"""
        try:
            title = questionary.text("Event title:").ask()
            if not title:
                return
            
            # Get start time
            start_time_str = questionary.text(
                "Start time (YYYY-MM-DD HH:MM) or press Enter for now:",
                default=datetime.now().strftime("%Y-%m-%d %H:%M")
            ).ask()
            
            try:
                start_time = datetime.strptime(start_time_str, "%Y-%m-%d %H:%M").isoformat()
            except ValueError:
                print(f"{Fore.RED}❌ Invalid date format")
                return
            
            duration = questionary.text(
                "Duration in minutes:",
                default="30",
                validate=lambda x: x.isdigit() or "Please enter a valid number"
            ).ask()
            
            event_data = {
                "title": title,
                "start_time": start_time,
                "duration": int(duration),
                "description": questionary.text("Description (optional):").ask() or ""
            }
            
            print(f"{Fore.BLUE}🗓️  Creating Google Calendar event...")
            
            response = requests.post(f"{self.backend_url}/api/calendar/event", json=event_data)
            
            if response.status_code == 201:
                result = response.json()
                print(f"{Fore.GREEN}✅ Calendar event created successfully!")
                
                # Check if it was created in Google Calendar
                if "google_calendar_link" in str(result):
                    print(f"{Fore.GREEN}🌟 Event added to your Google Calendar!")
                else:
                    print(f"{Fore.YELLOW}📅 Event created locally (Google Calendar may not be configured)")
            else:
                error_msg = response.json() if response.content else {"error": "Unknown error"}
                if "Google Calendar service not available" in str(error_msg):
                    print(f"{Fore.YELLOW}⚠️  Google Calendar not configured. Event saved locally.")
                    print(f"{Fore.BLUE}💡 To enable Google Calendar:")
                    print(f"   1. Set up cred.json file with Google API credentials")
                    print(f"   2. Install: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")
                    print(f"   3. Restart the backend")
                else:
                    print(f"{Fore.RED}❌ Failed to create event: {error_msg}")
        except Exception as e:
            print(f"{Fore.RED}❌ Error creating event: {e}")
        
        input("\nPress Enter to continue...")
    
    def view_calendar_events(self):
        """View calendar events"""
        try:
            response = requests.get(f"{self.backend_url}/api/calendar/events")
            if response.status_code == 200:
                events = response.json()
                
                if not events:
                    print(f"{Fore.YELLOW}📅 No calendar events found")
                else:
                    print(f"{Fore.CYAN}📅 Calendar Events:")
                    print("="*50)
                    for i, event in enumerate(events, 1):
                        try:
                            start_time = datetime.fromisoformat(event['start_time']).strftime("%Y-%m-%d %H:%M")
                        except:
                            start_time = event.get('start_time', 'Unknown')
                        
                        print(f"{i}. {event['title']}")
                        print(f"   Start: {start_time}")
                        
                        if 'duration_minutes' in event:
                            print(f"   Duration: {event['duration_minutes']} min")
                        print(f"   Type: {event.get('event_type', 'study_session')}")
                        
                        # Show if it's a Google Calendar event
                        if event.get('google_calendar_link'):
                            print(f"   🌟 Google Calendar Event")
                        print()
            else:
                print(f"{Fore.RED}❌ Failed to load events: {response.text}")
        except Exception as e:
            print(f"{Fore.RED}❌ Error loading events: {e}")
        
        input("\nPress Enter to continue...")
    
    def schedule_study_break(self):
        """Schedule a study break"""
        try:
            study_duration = questionary.text(
                "Study duration (minutes):",
                default="25",
                validate=lambda x: x.isdigit() or "Please enter a valid number"
            ).ask()
            
            break_duration = questionary.text(
                "Break duration (minutes):",
                default="5", 
                validate=lambda x: x.isdigit() or "Please enter a valid number"
            ).ask()
            
            break_data = {
                "study_duration": int(study_duration),
                "break_duration": int(break_duration),
                "start_time": datetime.now().isoformat()
            }
            
            response = requests.post(f"{self.backend_url}/api/calendar/schedule-break", json=break_data)
            if response.status_code == 200:
                print(f"{Fore.GREEN}✅ Study break scheduled successfully!")
            else:
                print(f"{Fore.RED}❌ Failed to schedule break: {response.text}")
        except Exception as e:
            print(f"{Fore.RED}❌ Error scheduling break: {e}")
        
        input("\nPress Enter to continue...")
    
    def sync_calendar(self):
        """Sync with external calendar"""
        print(f"{Fore.BLUE}🔄 Syncing calendar...")
        try:
            response = requests.post(f"{self.backend_url}/api/calendar/sync")
            if response.status_code == 200:
                result = response.json()
                print(f"{Fore.GREEN}✅ Calendar synced: {result.get('message', 'Success')}")
                
                if 'events' in result:
                    print(f"📅 Found {len(result['events'])} Google Calendar events")
            else:
                print(f"{Fore.RED}❌ Sync failed: {response.text}")
        except Exception as e:
            print(f"{Fore.RED}❌ Sync error: {e}")
        
        input("\nPress Enter to continue...")
    
    def preferences_menu(self):
        """User preferences management - FIXED"""
        try:
            response = requests.get(f"{self.backend_url}/api/study/preferences")
            # Handle both dict and list responses
            if response.status_code == 200:
                data = response.json()
                # Convert list to dict if needed
                if isinstance(data, list):
                    if data:  # If list has items, try to use first item
                        preferences = data[0] if isinstance(data[0], dict) else {}
                    else:  # Empty list
                        preferences = {}
                elif isinstance(data, dict):
                    preferences = data
                else:
                    preferences = {}
            else:
                preferences = {}
        except Exception as e:
            print(f"{Fore.RED}❌ Error loading preferences: {e}")
            preferences = {}
        
        try:
            choice = questionary.select(
                "⚙️  Preferences & Settings",
                choices=[
                    "👀 View Current Preferences",
                    "⏱️  Update Default Study Duration",
                    "☕ Update Default Break Duration", 
                    "🚫 Manage Distracting Websites List",
                    "💾 Export Study Data",
                    "⬅️  Back to Main Menu"
                ]
            ).ask()
            
            if not choice or "Back to Main Menu" in choice:
                return
            elif "View Current" in choice:
                self.display_preferences_fixed(preferences)
            elif "Study Duration" in choice:
                self.update_default_duration_fixed(preferences)
            elif "Break Duration" in choice:
                self.update_break_duration_fixed(preferences)
            elif "Websites List" in choice:
                self.manage_website_list_fixed(preferences)
            elif "Export Data" in choice:
                self.export_study_data()
        except Exception as e:
            print(f"{Fore.RED}❌ Error in preferences menu: {e}")
            input("Press Enter to continue...")
    
    def display_preferences_fixed(self, preferences: Dict):
        """Display current preferences - FIXED"""
        print(f"{Fore.CYAN}⚙️  Current Preferences")
        print("="*30)
        
        if isinstance(preferences, dict) and preferences:
            print(f"Default Study Duration: {preferences.get('default_study_duration', 25)} minutes")
            print(f"Default Break Duration: {preferences.get('default_break_duration', 5)} minutes")
            print(f"Auto-block Websites: {preferences.get('auto_block_websites', True)}")
            print(f"Notifications Enabled: {preferences.get('notifications_enabled', True)}")
            
            websites = preferences.get('distracting_websites', [])
            if isinstance(websites, list):
                print(f"Blocked Websites: {len(websites)} sites configured")
                if websites:
                    print("Sites:")
                    for site in websites[:5]:  # Show first 5
                        print(f"  • {site}")
                    if len(websites) > 5:
                        print(f"  • ... and {len(websites)-5} more")
            else:
                print("Blocked Websites: 0 sites configured")
        else:
            print("No preferences configured yet")
            print("Default settings will be used:")
            print("  • Study Duration: 25 minutes")
            print("  • Break Duration: 5 minutes")
            print("  • Auto-block Websites: True")
        
        input("\nPress Enter to continue...")
    
    def update_default_duration_fixed(self, preferences: Dict):
        """Update default study duration - FIXED"""
        try:
            current = preferences.get('default_study_duration', 25) if isinstance(preferences, dict) else 25
            new_duration = questionary.text(
                f"Enter new default study duration (current: {current} minutes):",
                default=str(current),
                validate=lambda x: x.isdigit() and int(x) > 0 or "Please enter a valid number"
            ).ask()
            
            if new_duration:
                # Ensure preferences is a dict
                if not isinstance(preferences, dict):
                    preferences = {}
                
                preferences['default_study_duration'] = int(new_duration)
                self.save_preferences_fixed(preferences)
        except Exception as e:
            print(f"{Fore.RED}❌ Error updating duration: {e}")
            input("Press Enter to continue...")
    
    def update_break_duration_fixed(self, preferences: Dict):
        """Update default break duration - FIXED"""
        try:
            current = preferences.get('default_break_duration', 5) if isinstance(preferences, dict) else 5
            new_duration = questionary.text(
                f"Enter new default break duration (current: {current} minutes):",
                default=str(current),
                validate=lambda x: x.isdigit() and int(x) > 0 or "Please enter a valid number"
            ).ask()
            
            if new_duration:
                # Ensure preferences is a dict
                if not isinstance(preferences, dict):
                    preferences = {}
                
                preferences['default_break_duration'] = int(new_duration)
                self.save_preferences_fixed(preferences)
        except Exception as e:
            print(f"{Fore.RED}❌ Error updating break duration: {e}")
            input("Press Enter to continue...")
    
    def manage_website_list_fixed(self, preferences: Dict):
        """Manage distracting websites list - FIXED"""
        try:
            # Ensure preferences is a dict
            if not isinstance(preferences, dict):
                preferences = {}
            
            current_sites = preferences.get('distracting_websites', [])
            
            # Ensure current_sites is a list
            if not isinstance(current_sites, list):
                current_sites = []
            
            print(f"{Fore.CYAN}Current blocked websites:")
            if current_sites:
                for i, site in enumerate(current_sites, 1):
                    print(f"  {i}. {site}")
            else:
                print("  No websites configured")
            
            action = questionary.select(
                "What would you like to do?",
                choices=[
                    "Add website",
                    "Remove website" if current_sites else None, 
                    "Clear all" if current_sites else None,
                    "Reset to defaults",
                    "Back"
                ]
            ).ask()
            
            # Filter out None choices
            if not action or action == "Back":
                return
            
            if action == "Add website":
                new_site = questionary.text("Enter website to block (e.g., facebook.com):").ask()
                if new_site and new_site.strip():
                    new_site = new_site.strip()
                    if new_site not in current_sites:
                        current_sites.append(new_site)
                        preferences['distracting_websites'] = current_sites
                        self.save_preferences_fixed(preferences)
                        print(f"{Fore.GREEN}✅ Added {new_site} to blocked list")
                    else:
                        print(f"{Fore.YELLOW}⚠️  {new_site} is already in the blocked list")
            
            elif action == "Remove website" and current_sites:
                site_to_remove = questionary.select(
                    "Select website to remove:",
                    choices=current_sites
                ).ask()
                if site_to_remove:
                    current_sites.remove(site_to_remove)
                    preferences['distracting_websites'] = current_sites
                    self.save_preferences_fixed(preferences)
                    print(f"{Fore.GREEN}✅ Removed {site_to_remove} from blocked list")
            
            elif action == "Clear all":
                if questionary.confirm("Are you sure you want to clear all blocked websites?").ask():
                    preferences['distracting_websites'] = []
                    self.save_preferences_fixed(preferences)
                    print(f"{Fore.GREEN}✅ Cleared all blocked websites")
            
            elif action == "Reset to defaults":
                default_sites = [
                    "facebook.com", "twitter.com", "youtube.com", 
                    "instagram.com", "reddit.com", "tiktok.com"
                ]
                preferences['distracting_websites'] = default_sites
                self.save_preferences_fixed(preferences)
                print(f"{Fore.GREEN}✅ Reset to default blocked websites")
                
        except Exception as e:
            print(f"{Fore.RED}❌ Error managing website list: {e}")
        
        input("\nPress Enter to continue...")
    
    def save_preferences_fixed(self, preferences: Dict):
        """Save preferences to backend - FIXED"""
        try:
            response = requests.post(f"{self.backend_url}/api/study/preferences", json=preferences)
            if response.status_code == 200:
                print(f"{Fore.GREEN}✅ Preferences saved successfully!")
            else:
                print(f"{Fore.RED}❌ Failed to save preferences: {response.text}")
        except Exception as e:
            print(f"{Fore.RED}❌ Error saving preferences: {e}")
    
    def export_study_data(self):
        """Export study data"""
        try:
            response = requests.get(f"{self.backend_url}/api/study/sessions")
            if response.status_code == 200:
                sessions = response.json()
                filename = f"study_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                
                with open(filename, 'w') as f:
                    json.dump(sessions, f, indent=2)
                
                print(f"{Fore.GREEN}✅ Study data exported to {filename}")
            else:
                print(f"{Fore.RED}❌ Failed to export data: {response.text}")
        except Exception as e:
            print(f"{Fore.RED}❌ Error exporting data: {e}")
        
        input("\nPress Enter to continue...")
    
    def system_tools_menu(self):
        """System tools and utilities - UPDATED with manual unblock"""
        try:
            choice = questionary.select(
                "🔧 System Tools",
                choices=[
                    "🏥 System Health Check",
                    "📊 Backend Test Suite",
                    "🔄 Test Website Blocking",
                    "🔓 Manually Unblock All Websites",  # NEW OPTION
                    "🧹 Clean Old Data",
                    "📋 View System Status",
                    "⬅️  Back to Main Menu"
                ]
            ).ask()
            
            if not choice or "Back to Main Menu" in choice:
                return
            elif "Health Check" in choice:
                self.system_health_check()
            elif "Test Suite" in choice:
                self.run_backend_tests()
            elif "Test Website Blocking" in choice:
                self.test_website_blocking()
            elif "Manually Unblock All Websites" in choice:
                self.manual_unblock_websites()  # NEW METHOD
            elif "Clean Old Data" in choice:
                self.clean_old_data()
            elif "System Status" in choice:
                self.view_system_status()
        except Exception as e:
            print(f"{Fore.RED}❌ Error in system tools menu: {e}")
            input("Press Enter to continue...")
    def test_website_blocking(self):
        """Test website blocking functionality"""
        print(f"{Fore.BLUE}🧪 Testing Website Blocking...")
        
        test_sites = ["facebook.com", "youtube.com"]
        
        try:
            response = requests.post(f"{self.backend_url}/api/study/block-websites", json={
                "websites": test_sites,
                "duration": 1  # 1 minute test
            })
            
            if response.status_code == 200:
                result = response.json()
                blocked_count = result.get('blocked_count', 0)
                
                print(f"Response: {result}")
                
                if blocked_count > 0:
                    print(f"{Fore.GREEN}✅ Website blocking working: {blocked_count} sites blocked")
                    print(f"{Fore.YELLOW}💡 Try accessing facebook.com or youtube.com - they should be blocked")
                    
                    # Ask if user wants to unblock
                    if questionary.confirm("Unblock test sites now?", default=True).ask():
                        unblock_response = requests.post(f"{self.backend_url}/api/study/unblock-websites")
                        if unblock_response.status_code == 200:
                            print(f"{Fore.GREEN}✅ Test sites unblocked")
                        else:
                            print(f"{Fore.YELLOW}⚠️  Manual unblock may be needed")
                else:
                    print(f"{Fore.YELLOW}⚠️  Website blocking returned 0 blocked sites")
                    print(f"{Fore.BLUE}💡 This might be due to:")
                    print(f"   • Need to run as administrator/sudo")
                    print(f"   • Mock mode enabled")
                    print(f"   • Hosts file permissions")
            else:
                print(f"{Fore.RED}❌ Website blocking test failed: {response.text}")
        except Exception as e:
            print(f"{Fore.RED}❌ Error testing website blocking: {e}")
        
        input("\nPress Enter to continue...")
    
    def system_health_check(self):
        """Perform comprehensive system health check"""
        print(f"{Fore.GREEN}🏥 System Health Check")
        print("="*30)
        
        checks = [
            ("Backend API", f"{self.backend_url}/health"),
            ("Study Endpoints", f"{self.backend_url}/api/study/test"),
            ("Calendar Endpoints", f"{self.backend_url}/api/calendar/test"),
            ("System Status", f"{self.backend_url}/api/status")
        ]
        
        for name, url in checks:
            try:
                start_time = time.time()
                response = requests.get(url, timeout=10)
                response_time = (time.time() - start_time) * 1000
                
                if response.status_code == 200:
                    status = "🟢 Healthy"
                    time_color = Fore.GREEN if response_time < 500 else Fore.YELLOW if response_time < 1000 else Fore.RED
                else:
                    status = f"🔴 Error ({response.status_code})"
                    time_color = Fore.RED
                
                print(f"{name}: {status} {time_color}({response_time:.1f}ms)")
                
            except Exception as e:
                print(f"{name}: 🔴 Failed - {str(e)[:50]}...")
        
        input("\nPress Enter to continue...")
    
    def run_backend_tests(self):
        """Run comprehensive backend test suite"""
        print(f"{Fore.BLUE}📊 Running Backend Test Suite")
        print("="*40)
        
        test_endpoints = [
            ("GET", "/api/study/sessions"),
            ("POST", "/api/study/session", {"subject": "CLI Test", "duration": 25}),
            ("GET", "/api/study/analytics"),
            ("POST", "/api/study/plan", {"subject": "Test", "duration": 30, "goals": ["Test goal"]}),
        ]
        
        passed = 0
        total = len(test_endpoints)
        
        for method, endpoint, *data in test_endpoints:
            try:
                if method == "GET":
                    response = requests.get(f"{self.backend_url}{endpoint}")
                else:
                    response = requests.post(f"{self.backend_url}{endpoint}", json=data[0] if data else {})
                
                if response.status_code in [200, 201]:
                    print(f"{Fore.GREEN}✅ {method} {endpoint}")
                    passed += 1
                else:
                    print(f"{Fore.RED}❌ {method} {endpoint} - Status: {response.status_code}")
            except Exception as e:
                print(f"{Fore.RED}❌ {method} {endpoint} - Error: {e}")
        
        print(f"\n📊 Test Results: {passed}/{total} passed ({(passed/total)*100:.1f}%)")
        
        if passed == total:
            print(f"{Fore.GREEN}🎉 All tests passed! Backend is working perfectly.")
        elif passed >= total * 0.8:
            print(f"{Fore.YELLOW}✅ Most tests passed. Backend is functional.")
        else:
            print(f"{Fore.RED}❌ Many tests failed. Check backend health.")
        
        input("\nPress Enter to continue...")
    
    def clean_old_data(self):
        """Clean old study data"""
        try:
            confirm = questionary.confirm(
                "This will remove study sessions older than 30 days. Continue?",
                default=False
            ).ask()
            
            if confirm:
                print(f"{Fore.BLUE}🧹 Cleaning old data...")
                print(f"{Fore.GREEN}✅ Old data cleanup completed (simulated)")
            else:
                print(f"{Fore.YELLOW}⏹️  Data cleanup cancelled")
        except Exception as e:
            print(f"{Fore.RED}❌ Error cleaning data: {e}")
        
        input("\nPress Enter to continue...")
    
    def view_system_status(self):
        """View detailed system status"""
        try:
            response = requests.get(f"{self.backend_url}/api/status")
            if response.status_code == 200:
                status = response.json()
                
                print(f"{Fore.CYAN}📋 Detailed System Status")
                print("="*30)
                print(f"Backend Status: {status.get('status', 'Unknown')}")
                print(f"MCP Connected: {status.get('mcp_connected', False)}")
                print(f"Mock Mode: {status.get('mock_mode', False)}")
                print(f"Groq Available: {status.get('groq_available', False)}")
                print(f"Timestamp: {status.get('timestamp', 'Unknown')}")
            else:
                print(f"{Fore.RED}❌ Failed to get system status: {response.text}")
        except Exception as e:
            print(f"{Fore.RED}❌ Error getting system status: {e}")
        
        input("\nPress Enter to continue...")

def main():
    """Main CLI entry point - UPDATED with cleanup"""
    parser = argparse.ArgumentParser(description="Smart Study Orchestrator CLI")
    parser.add_argument("--backend", default="http://localhost:5000", 
                    help="Backend URL (default: http://localhost:5000)")
    
    args = parser.parse_args()
    
    cli = None
    try:
        cli = StudyOrchestratorCLI(backend_url=args.backend)
        cli.main_menu()
    
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}🔓 Cleaning up and unblocking websites...")
        if cli:
            cli.unblock_websites()
        print(f"{Fore.YELLOW}👋 Goodbye!")
    except Exception as e:
        print(f"{Fore.RED}❌ Fatal error: {e}")
        if cli:
            cli.unblock_websites()
        sys.exit(1)
    finally:
        # Ensure cleanup happens
        if cli:
            try:
                cli.unblock_websites()
            except:
                pass

if __name__ == "__main__":
    main()
