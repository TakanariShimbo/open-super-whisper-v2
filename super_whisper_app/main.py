"""
Super Whisper App

Main entry point for the Super Whisper application.
"""

import sys

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QSettings

from super_whisper_app.app.controllers.app_controller import AppController
from super_whisper_app.app.controllers.dialogs.api_key_controller import APIKeyController
from super_whisper_app.app.views.main_window import MainWindow

def main() -> int:
    """
    Main entry point for the Super Whisper app.
    
    This function initializes the application, loads settings,
    creates the controller and view, and starts the application event loop.
    
    The application will only start if a valid API key is provided.

    Returns
    -------
    int
        The exit code of the application
    """
    # Create the application
    app = QApplication(sys.argv)
    app.setApplicationName("OpenSuperWhisper")
    app.setOrganizationName("OpenSuperWhisper")
    
    # Initialize settings
    settings = QSettings()
    
    # Create API key controller and ensure a valid API key
    api_key_controller = APIKeyController(settings)
    
    if not api_key_controller.ensure_valid_api_key():
        print("Application exiting: No valid API key provided.")
        return 1
    
    # Create the main app controller with validated API key
    controller = AppController(settings)
    
    # Create the main window
    main_window = MainWindow(controller, settings)
    main_window.show()
    
    # Start the event loop
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
