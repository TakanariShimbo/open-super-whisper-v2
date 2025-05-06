#!/usr/bin/env python3
"""
Run Recorder Application Script

This script provides a simple way to launch the recorder application.
"""
import sys
import os

# Main entry point
if __name__ == "__main__":
    # Add the current directory to the Python path if it's not already there
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    
    # Import our application components
    from recorder_app.main import launch_recorder_app
    
    # Run the application launcher from the module
    launch_recorder_app()
