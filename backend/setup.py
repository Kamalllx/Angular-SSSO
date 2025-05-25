#!/usr/bin/env python3
"""
Setup script for Smart Study Orchestrator Backend
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path

def install_dependencies():
    """Install required dependencies"""
    print("Installing dependencies...")
    
    try:
        # Install core dependencies
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Core dependencies installed")
        
        # Try to install optional dependencies
        optional_deps = [
            "groq",
            "psutil", 
            "selenium"
        ]
        
        for dep in optional_deps:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
                print(f"✅ Optional dependency installed: {dep}")
            except subprocess.CalledProcessError:
                print(f"⚠️  Failed to install optional dependency: {dep}")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def setup_environment():
    """Setup environment and configuration"""
    print("Setting up environment...")
    
    # Create data directory
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    print("✅ Data directory created")
    
    # Create .env file if it doesn't exist
    env_file = Path(".env")
    if not env_file.exists():
        env_content = """# Smart Study Orchestrator Configuration

# Groq API Configuration (Optional - for AI features)
GROQ_API_KEY=your_groq_api_key_here

# Flask Configuration
SECRET_KEY=your_secret_key_here
FLASK_ENV=development
FLASK_DEBUG=
