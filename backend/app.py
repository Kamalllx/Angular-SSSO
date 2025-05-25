from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from datetime import datetime, timedelta
import asyncio
import json
import uuid
import os

from config import Config
from models import StudySession, StudyPlan
from utils import load_json_data, save_json_data, initialize_data_files
from flask_cors import CORS
# Add this after the imports and before create_app()
import sys
import platform

def check_admin_permissions():
    """Check if running with admin permissions for website blocking"""
    if platform.system() == "Windows":
        try:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    else:  # Linux/macOS
        return os.geteuid() == 0

def warn_about_permissions():
    """Warn user about permissions needed for website blocking"""
    if not check_admin_permissions():
        print("\n" + "="*60)
        print("⚠️  WARNING: Website blocking requires administrator privileges")
        print("🔧 For full functionality:")
        if platform.system() == "Windows":
            print("   - Run Command Prompt as Administrator")
            print("   - Then run: python run.py")
        else:
            print("   - Run with: sudo python run.py")
        print("   - Website blocking will be disabled without admin rights")
        print("="*60)
        return False
    else:
        print("✅ Running with administrator privileges - all features available")
        return True


def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config.from_object(Config)
    
    # Enable CORS for Angular frontend
    CORS(app, origins=['http://localhost:4200', 'http://127.0.0.1:4200', 'http://localhost:8080'])
    
    # Create data directory if it doesn't exist
    os.makedirs(app.config['DATA_DIR'], exist_ok=True)
    
    # Initialize data files
    initialize_data_files()
    
    # Import and initialize services AFTER app creation
    from services import GroqService, StudyAnalyzer, CalendarService, mcp_service
    
    # Create service instances
    groq_service = GroqService()
    study_analyzer = StudyAnalyzer()
    calendar_service = CalendarService()
    
    # Root route for testing
    @app.route('/')
    def index():
        return jsonify({
            "message": "Smart Study Orchestrator API is running!",
            "version": "1.0.0",
            "endpoints": {
                "study": "/api/study/*",
                "calendar": "/api/calendar/*"
            }
        })
    
    # Health check route
    @app.route('/health')
    def health_check():
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.now().isoformat()
        })
    
    # Status endpoint
    @app.route('/api/status')
    def get_status():
        return jsonify({
            "status": "running",
            "mcp_connected": mcp_service.connected,
            "mock_mode": getattr(mcp_service, 'mock_mode', False),
            "groq_available": groq_service.groq_available,
            "timestamp": datetime.now().isoformat()
        })
    
    # Test all endpoints
    @app.route('/api/test-all')
    def test_all_endpoints():
        return jsonify({
            "message": "All endpoints test",
            "backend_status": "running",
            "mcp_status": "connected" if mcp_service.connected else "mock_mode",
            "timestamp": datetime.now().isoformat(),
            "test_endpoints": {
                "study_routes": "/api/study/test",
                "calendar_routes": "/api/calendar/test",
                "health_check": "/health"
            }
        })
    
    # =============================================================================
    # STUDY ROUTES
    # =============================================================================
    
    @app.route('/api/study/test')
    def test_study_routes():
        """Test route to verify study routes are working"""
        return jsonify({
            "message": "Study routes are working!",
            "available_endpoints": [
                "GET /api/study/sessions",
                "POST /api/study/session", 
                "POST /api/study/session/<id>/start",
                "POST /api/study/session/<id>/end",
                "POST /api/study/plan",
                "GET /api/study/analytics",
                "POST /api/study/block-websites",
                "GET /api/study/session/<id>",
                "GET|POST /api/study/preferences"
            ]
        })
    
    @app.route('/api/study/sessions', methods=['GET'])
    def get_study_sessions():
        """Get all study sessions"""
        try:
            sessions_data = load_json_data(Config.STUDY_SESSIONS_FILE)
            return jsonify(sessions_data), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/api/study/session', methods=['POST'])
    def create_study_session():
        """Create a new study session"""
        try:
            data = request.get_json()
            
            # Validate required fields
            if not data.get('subject'):
                return jsonify({"error": "Subject is required"}), 400
            
            # Create session object
            session = StudySession(
                id=str(uuid.uuid4()),
                subject=data['subject'],
                duration_minutes=data.get('duration', Config.DEFAULT_STUDY_DURATION),
                start_time=None,  # Will be set when session starts
                goals=data.get('goals', []),
                notes=data.get('notes', ''),
                distractions=0,
                breaks_taken=0
            )
            
            # Load existing sessions
            sessions_data = load_json_data(Config.STUDY_SESSIONS_FILE)
            sessions_data.append(session.to_dict())
            
            # Save updated sessions
            save_json_data(Config.STUDY_SESSIONS_FILE, sessions_data)
            
            return jsonify(session.to_dict()), 201
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/api/study/session/<session_id>/start', methods=['POST'])
    def start_study_session(session_id):
        """Start a study session"""
        try:
            # Load sessions
            sessions_data = load_json_data(Config.STUDY_SESSIONS_FILE)
            
            # Find and update session
            session_found = False
            for session_dict in sessions_data:
                if session_dict['id'] == session_id:
                    session_dict['start_time'] = datetime.now().isoformat()
                    session_found = True
                    break
            
            if not session_found:
                return jsonify({"error": "Session not found"}), 404
            
            # Save updated sessions
            save_json_data(Config.STUDY_SESSIONS_FILE, sessions_data)
            
            return jsonify({"message": "Session started successfully", "session_id": session_id}), 200
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/api/study/session/<session_id>/end', methods=['POST'])
    def end_study_session(session_id):
        """End a study session"""
        try:
            data = request.get_json()
            
            # Load sessions
            sessions_data = load_json_data(Config.STUDY_SESSIONS_FILE)
            
            # Find and update session
            session_found = False
            for session_dict in sessions_data:
                if session_dict['id'] == session_id:
                    session_dict['end_time'] = datetime.now().isoformat()
                    session_dict['completed_goals'] = data.get('completed_goals', [])
                    session_dict['focus_score'] = data.get('focus_score', 0)
                    session_dict['notes'] = data.get('notes', '')
                    session_dict['distractions'] = data.get('distractions', 0)
                    session_dict['breaks_taken'] = data.get('breaks_taken', 0)
                    session_found = True
                    break
            
            if not session_found:
                return jsonify({"error": "Session not found"}), 404
            
            # Save updated sessions
            save_json_data(Config.STUDY_SESSIONS_FILE, sessions_data)
            
            return jsonify({"message": "Session ended successfully", "session_id": session_id}), 200
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/api/study/plan', methods=['POST'])
    def generate_study_plan():
        """Generate AI-powered study plan"""
        try:
            data = request.get_json()
            
            subject = data.get('subject', '')
            duration = data.get('duration', Config.DEFAULT_STUDY_DURATION)
            goals = data.get('goals', [])
            
            if not subject:
                return jsonify({"error": "Subject is required"}), 400
            
            # Generate plan using Groq AI
            plan = groq_service.generate_study_plan(subject, duration, goals)
            
            return jsonify(plan), 200
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/api/study/analytics', methods=['GET'])
    def get_study_analytics():
        """Get study analytics and insights"""
        try:
            # Load sessions
            sessions_data = load_json_data(Config.STUDY_SESSIONS_FILE)
            
            # Generate analytics
            analytics = study_analyzer.generate_analytics(sessions_data)
            
            # Get AI insights
            ai_insights = groq_service.analyze_study_pattern(sessions_data)
            
            # Combine analytics
            result = {
                "weekly_stats": analytics.get("weekly_stats", {}),
                "productivity_trends": ai_insights.get("productivity_trends", {}),
                "recommendations": ai_insights.get("recommendations", {}),
                "focus_insights": ai_insights.get("focus_insights", {})
            }
            
            return jsonify(result), 200
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/api/study/block-websites', methods=['POST'])
    def block_websites():
        """Block distracting websites using MCP"""
        try:
            data = request.get_json()
            websites = data.get('websites', [])
            duration = data.get('duration', Config.DEFAULT_STUDY_DURATION)
            
            if not websites:
                return jsonify({"error": "No websites specified"}), 400
            
            # Use MCP service to block websites
            if mcp_service.connected:
                # Run async function in sync context
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    result = loop.run_until_complete(
                        mcp_service.block_distracting_websites(websites, duration)
                    )
                    loop.close()
                    return jsonify(result), 200
                except Exception as e:
                    # Fallback to mock response
                    return jsonify({
                        "success": True, 
                        "blocked_count": len(websites),
                        "message": f"Mock blocking {len(websites)} websites",
                        "mock_mode": True
                    }), 200
            else:
                return jsonify({
                    "success": True, 
                    "blocked_count": len(websites),
                    "message": f"Mock blocking {len(websites)} websites",
                    "mock_mode": True
                }), 200
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/api/study/session/<session_id>', methods=['GET'])
    def get_study_session(session_id):
        """Get specific study session"""
        try:
            sessions_data = load_json_data(Config.STUDY_SESSIONS_FILE)
            
            for session in sessions_data:
                if session['id'] == session_id:
                    return jsonify(session), 200
            
            return jsonify({"error": "Session not found"}), 404
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/api/study/preferences', methods=['GET', 'POST'])
    def handle_user_preferences():
        """Get or update user preferences"""
        try:
            if request.method == 'GET':
                preferences = load_json_data(Config.USER_PREFERENCES_FILE)
                return jsonify(preferences), 200
            
            elif request.method == 'POST':
                data = request.get_json()
                save_json_data(Config.USER_PREFERENCES_FILE, data)
                return jsonify({"message": "Preferences updated successfully"}), 200
                
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    # =============================================================================
    # CALENDAR ROUTES
    # =============================================================================
    
    @app.route('/api/calendar/test')
    def test_calendar_routes():
        """Test route to verify calendar routes are working"""
        return jsonify({
            "message": "Calendar routes are working!",
            "available_endpoints": [
                "GET /api/calendar/events",
                "POST /api/calendar/event",
                "GET|PUT|DELETE /api/calendar/event/<id>",
                "POST /api/calendar/schedule-break",
                "POST /api/calendar/sync"
            ]
        })
    
    @app.route('/api/calendar/events', methods=['GET'])
    def get_calendar_events():
        """Get calendar events"""
        try:
            date = request.args.get('date')  # Optional date filter
            events = calendar_service.get_events(date)
            return jsonify(events), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/api/calendar/event', methods=['POST'])
    def create_calendar_event():
        """Create a new calendar event"""
        try:
            data = request.get_json()
            
            # Validate required fields
            required_fields = ['title', 'start_time', 'duration']
            for field in required_fields:
                if field not in data:
                    return jsonify({"error": f"{field} is required"}), 400
            
            title = data['title']
            start_time = data['start_time']
            duration = data['duration']
            description = data.get('description', '')
            
            # Create event using MCP service
            if mcp_service.connected:
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    result = loop.run_until_complete(
                        mcp_service.create_calendar_event(title, start_time, duration)
                    )
                    loop.close()
                    
                    if result.get('success'):
                        return jsonify({
                            "message": "Calendar event created successfully",
                            "event_id": result.get('event_id')
                        }), 201
                    else:
                        return jsonify({"error": result.get('error')}), 500
                except Exception as e:
                    # Fallback to local calendar service
                    event_id = calendar_service.create_event(title, start_time, duration, description)
                    return jsonify({
                        "message": "Calendar event created (local)",
                        "event_id": event_id
                    }), 201
            else:
                # Fallback to local calendar service
                event_id = calendar_service.create_event(title, start_time, duration, description)
                return jsonify({
                    "message": "Calendar event created (local)",
                    "event_id": event_id
                }), 201
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/api/calendar/event/<event_id>', methods=['GET', 'PUT', 'DELETE'])
    def handle_calendar_event(event_id):
        """Get, update, or delete a calendar event"""
        try:
            if request.method == 'GET':
                event = calendar_service.get_event(event_id)
                if event:
                    return jsonify(event), 200
                else:
                    return jsonify({"error": "Event not found"}), 404
            
            elif request.method == 'PUT':
                data = request.get_json()
                success = calendar_service.update_event(event_id, **data)
                if success:
                    return jsonify({"message": "Event updated successfully"}), 200
                else:
                    return jsonify({"error": "Event not found"}), 404
            
            elif request.method == 'DELETE':
                success = calendar_service.delete_event(event_id)
                if success:
                    return jsonify({"message": "Event deleted successfully"}), 200
                else:
                    return jsonify({"error": "Event not found"}), 404
        
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/api/calendar/schedule-break', methods=['POST'])
    def schedule_study_break():
        """Schedule study breaks automatically"""
        try:
            data = request.get_json()
            
            study_duration = data.get('study_duration', 25)
            break_duration = data.get('break_duration', 5)
            start_time = data.get('start_time', datetime.now().isoformat())
            
            # Use local calendar service for scheduling
            result = calendar_service.schedule_breaks(study_duration, break_duration, start_time)
            
            return jsonify(result), 200
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/api/calendar/sync', methods=['POST'])
    def sync_calendar():
        """Sync with external calendar services"""
        try:
            result = calendar_service.sync_external_calendar()
            return jsonify(result), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    return app
