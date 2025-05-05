#!/usr/bin/env python3
"""
Entry point for Qt MVC demo application.
This file allows the application to be run from the project root directory.
"""
import sys
import os

# Add the current directory to the Python path if it's not already there
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Import without running module code first
import qt_mvc_demo

# Main entry point
if __name__ == "__main__":
    # Import our application components
    import qt_mvc_demo.main as qt_demo
    
    # Run the application launcher from the module
    qt_demo.launch_qt_mvc_app()
