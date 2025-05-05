#!/usr/bin/env python3
"""
PyQt6 MVC Demo Entry Point

This script serves as the main entry point for running the Qt MVC demo 
application from the project root directory. It sets up the Python path
to include the current directory, imports the main module, and launches
the application.

The script is designed to allow easy execution of the demo without having
to be in the specific module directory, making it more user-friendly for
demonstration purposes.

Examples
--------
Run the application from the project root:

    $ python run_qt_mvc_demo.py

See Also
--------
qt_mvc_demo.main : The main module of the MVC demo application
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
