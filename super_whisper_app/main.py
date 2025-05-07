"""
Super Whisper App

Main entry point for the Super Whisper application.
"""

import sys
import os

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QSettings

from super_whisper_app.app.controllers.app_controller import AppController
from super_whisper_app.app.views.main_window import MainWindow

def main():
    """
    Main entry point for the Super Whisper app.
    
    This function initializes the application, loads settings,
    creates the controller and view, and starts the application event loop.
    """
    # Create the application
    app = QApplication(sys.argv)
    app.setApplicationName("SuperWhisper")
    app.setOrganizationName("OpenSuperWhisper")
    
    # Initialize settings
    settings = QSettings()
    
    # Create the controller
    controller = AppController(settings)
    
    # Create the main window
    main_window = MainWindow(controller, settings)
    main_window.show()
    
    # Start the event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
