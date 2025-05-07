#!/usr/bin/env python3
"""
Run Super Whisper App

This script launches the Super Whisper application.
"""

import sys
import os

# Configure ffmpeg environment before any imports
def setup_ffmpeg_environment():
    """Set up the ffmpeg environment by adding ffmpeg to the system PATH if it's not already there"""
    current_path = os.environ.get('PATH', '')
    # Add ffmpeg/bin path from the project root directory
    project_ffmpeg_bin = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ffmpeg", "bin")
    if os.path.exists(project_ffmpeg_bin) and project_ffmpeg_bin not in current_path:
        os.environ['PATH'] = project_ffmpeg_bin + os.pathsep + current_path
        print(f"Added {project_ffmpeg_bin} to PATH for ffmpeg")

# Set up ffmpeg environment immediately
setup_ffmpeg_environment()

# Add the project root directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from super_whisper_app.main import main

if __name__ == "__main__":
    main()
