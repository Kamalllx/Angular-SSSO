from app import create_app
import asyncio
from services import mcp_service
from datetime import datetime
import os

app = create_app()

# Set startup time for health checks
app.config['STARTUP_TIME'] = datetime.now().isoformat()
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

# Add this call in your run.py file

def initialize_services():
    """Initialize services when the app starts"""
    print("Initializing Smart Study Orchestrator...")
    has_admin = warn_about_permissions()

    # Initialize MCP connections (non-blocking)
    try:
        # Create new event loop to avoid conflicts
        if hasattr(asyncio, 'get_event_loop'):
            try:
                loop = asyncio.get_event_loop()
                if loop.is_closed():
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
        else:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
        # Run the initialization
        loop.run_until_complete(mcp_service.initialize_connections())
        print("MCP services initialized successfully")
        
    except Exception as e:
        print(f"Warning: MCP services failed to initialize: {e}")
        print("Application will continue with mock functionality")
    
    print("Smart Study Orchestrator is ready!")

if __name__ == '__main__':
    print("Starting Smart Study Orchestrator Backend...")
    print("=" * 50)
    print("Backend will be available at: http://localhost:5000")
    print("API endpoints will be at: http://localhost:5000/api/")
    print("Status endpoint: http://localhost:5000/api/status")
    print("Health check: http://localhost:5000/health")
    print("=" * 50)
    
    # Call initialize_services before running the app
    initialize_services()
    
    app.run(debug=True, host='0.0.0.0', port=5000)
