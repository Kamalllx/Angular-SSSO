import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
    GOOGLE_CALENDAR_CREDENTIALS = os.environ.get('GOOGLE_CALENDAR_CREDENTIALS')
    
    # MCP Server configurations
    MCP_CALENDAR_URL = "stdio://python mcp_servers.py"
    MCP_BROWSER_URL = "stdio://python mcp_servers.py"
    MCP_FILESYSTEM_URL = "stdio://python mcp_servers.py"
    
    # Study session defaults
    DEFAULT_STUDY_DURATION = 25  # minutes (Pomodoro)
    DEFAULT_BREAK_DURATION = 5   # minutes
    LONG_BREAK_DURATION = 15     # minutes
    
    # Data storage
    DATA_DIR = "data"
    STUDY_SESSIONS_FILE = os.path.join(DATA_DIR, "study_sessions.json")
    USER_PREFERENCES_FILE = os.path.join(DATA_DIR, "user_preferences.json")
    CALENDAR_EVENTS_FILE = os.path.join(DATA_DIR, "calendar_events.json")
    
    # API Configuration
    CORS_ORIGINS = [
        'http://localhost:4200',
        'http://127.0.0.1:4200', 
        'http://localhost:8080',
        'http://127.0.0.1:8080'
    ]
    
    # Application settings
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    TESTING = False
    
    # Rate limiting (requests per minute)
    RATE_LIMIT = 100
    
    # Session timeout (minutes)
    SESSION_TIMEOUT = 480  # 8 hours max
    
    # File upload settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = os.path.join(DATA_DIR, "uploads")
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.path.join(DATA_DIR, "app.log")
