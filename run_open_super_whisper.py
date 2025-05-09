#!/usr/bin/env python3
"""
Open Super Whisper App Runner

This script runs the Open Super Whisper application.
"""

import sys
import os

# Add the project root to the path so we can import the package
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

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

from gui.main import start_application


if __name__ == "__main__":
    start_application()
