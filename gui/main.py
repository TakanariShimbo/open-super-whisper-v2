"""
Open Super Whisper App

Main entry point for the Open Super Whisper application.
"""

import sys

from PyQt6.QtWidgets import QApplication

from .app.views.factories.api_key_dialog_factory import APIKeyDialogFactory
from .app.views.factories.main_window_factory import MainWindowFactory
from .app.managers.icon_manager import IconManager
from .app.managers.settings_manager import SettingsManager


def start_application() -> int:
    """
    Main entry point for the Open Super Whisper app.

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
    if not settings_manager.has_valid_api_key():
        # Create and show initial API key dialog
        dialog = APIKeyDialogFactory.create_initial_dialog()

        if not dialog.exec():
            print("Application exiting: No API key provided.")
            return 1

    # Create the main window using the factory
    main_window = MainWindowFactory.create_window()
    main_window.show()

    # Start the event loop
    return app.exec()


if __name__ == "__main__":
    sys.exit(status=start_application())
