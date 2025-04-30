#!/usr/bin/env python
"""
Open Super Whisper - Application Entry Point

This is the main entry point for the application.
"""

import os
import sys

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

# Import after PATH is set
from gui.gui_app import start_application

if __name__ == "__main__":
    start_application()
