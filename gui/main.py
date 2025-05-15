"""
Open Super Whisper App

Main entry point for the Open Super Whisper application.
"""

import sys

from PyQt6.QtWidgets import QApplication

from .app.controllers.app_controller import AppController
from .app.views.factories.api_key_dialog_factory import APIKeyDialogFactory
from .app.views.main_window import MainWindow
from .app.manager.icon_manager import IconManager
from .app.manager.settings_manager import SettingsManager


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
    icon_manager = IconManager.instance()
    app.setWindowIcon(icon_manager.get_app_icon())
    
    # Initialize settings manager
    SettingsManager.instance()
    
    # Check for API key and show dialog if not available
    settings_manager = SettingsManager.instance()
    has_valid_api_key = settings_manager.has_valid_api_key()
    
    # If no API key is available or it's invalid, prompt for one
    if not has_valid_api_key:
        # Create and show initial API key dialog
        dialog = APIKeyDialogFactory.create_initial_dialog(None)
        
        if not dialog.exec():
            print("Application exiting: No API key provided.")
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
