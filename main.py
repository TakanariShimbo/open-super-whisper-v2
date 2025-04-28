#!/usr/bin/env python
"""
Open Super Whisper - Main Entry Point

This is the main entry point for the application.
"""

import os
import sys

# Add ffmpeg to path before any imports
def add_ffmpeg_to_path():
    """Add ffmpeg to the system PATH if it's not already there"""
    current_path = os.environ.get('PATH', '')
    
    # Add ffmpeg/bin path from the project root directory
    project_ffmpeg_bin = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ffmpeg", "bin")
    
    if os.path.exists(project_ffmpeg_bin) and project_ffmpeg_bin not in current_path:
        os.environ['PATH'] = project_ffmpeg_bin + os.pathsep + current_path
        print(f"Added {project_ffmpeg_bin} to PATH for ffmpeg")

# Add ffmpeg to PATH immediately
add_ffmpeg_to_path()

# Import after PATH is set
from gui.main import main

if __name__ == "__main__":
    main()
