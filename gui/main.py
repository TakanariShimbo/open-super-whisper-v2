"""
Open Super Whisper App

Main entry point for the Open Super Whisper application.
"""

import sys

from PyQt6.QtWidgets import QApplication

from .app.controllers.app_controller import AppController
from .app.controllers.dialogs.api_key_controller import APIKeyController
from .app.views.main_window import MainWindow
from .app.utils.icon_manager import IconManager
from .app.utils.settings_manager import SettingsManager


def start_application() -> int:
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
    
    # Set application icon using the IconManager
    icon_manager = IconManager()
    app.setWindowIcon(icon_manager.get_app_icon())
    
    # Initialize settings manager
    SettingsManager.instance()
    
    # Create API key controller and ensure a valid API key
    api_key_controller = APIKeyController()
    
    if not api_key_controller.ensure_valid_api_key():
        print("Application exiting: No valid API key provided.")
        return 1
    
    # Create the main app controller with validated API key
    controller = AppController()
    
    # Create the main window
    main_window = MainWindow(controller)
    main_window.show()
    
    # Start the event loop
    return app.exec()

if __name__ == "__main__":
    sys.exit(start_application())
