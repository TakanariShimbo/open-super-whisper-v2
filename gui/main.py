"""
Open Super Whisper App

Main entry point for the Open Super Whisper application.
"""

import sys

from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QSharedMemory

from .app.managers.icon_manager import IconManager
from .app.managers.settings_manager import SettingsManager
from .app.views.factories.api_key_dialog_factory import APIKeyDialogFactory
from .app.views.factories.main_window_factory import MainWindowFactory


class LabelManager:
    """
    Manages application labels for internationalization support.
    """

    ALL_LABELS = {
        "English": {
            "already_running_title": "Application already running",
            "already_running_message": "Please check the application tray for the icon.",
            "no_api_key_title": "No API key provided",
            "no_api_key_message": "Please provide a valid API key to wake up the application.",
        },
        # Future: Add other languages here
    }

    def __init__(self) -> None:
        # load language from settings manager
        settings_manager = SettingsManager.instance()
        language = settings_manager.get_language()

        # set labels based on language
        self._labels = self.ALL_LABELS[language]

    @property
    def already_running_title(self) -> str:
        return self._labels["already_running_title"]

    @property
    def already_running_message(self) -> str:
        return self._labels["already_running_message"]

    @property
    def no_api_key_title(self) -> str:
        return self._labels["no_api_key_title"]

    @property
    def no_api_key_message(self) -> str:
        return self._labels["no_api_key_message"]


class SingleInstance:
    """
    Ensures only one instance of the application is running using Qt shared memory.
    """

    def __init__(self, app_name: str = "OpenSuperWhisper") -> None:
        """
        Initialize the single instance checker.

        Parameters
        ----------
        app_name : str
            Unique name for the application instance
        """
        self.app_name = app_name
        self._shared_memory = None
        self._is_running = self._check_instance()

    def _check_instance(self) -> bool:
        """
        Check if another instance is already running.

        Returns
        -------
        bool
            True if another instance is running, False otherwise
        """
        try:
            self._shared_memory = QSharedMemory(self.app_name)

            if self._shared_memory.attach():
                # Shared memory already exists - another instance is running
                return True
            else:
                # Create only 1 byte shared memory segment to indicate that the application is running
                self._shared_memory.create(1)
                return False
        except Exception:
            return True  # Assume another instance is running on error

    def is_running(self) -> bool:
        """
        Check if another instance is already running.

        Returns
        -------
        bool
            True if another instance is running, False otherwise
        """
        return self._is_running

    def cleanup(self) -> None:
        """
        Clean up shared memory resources.
        """
        if self._shared_memory and not self._is_running:
            try:
                self._shared_memory.detach()
            except Exception:
                pass

    def __del__(self) -> None:
        """
        Destructor to ensure cleanup when object is destroyed.
        """
        self.cleanup()


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
    # Check if another instance is already running
    single_instance = SingleInstance("OpenSuperWhisper")

    try:
        # Create the application
        app = QApplication(sys.argv)
        app.setApplicationName("OpenSuperWhisper")
        app.setOrganizationName("OpenSuperWhisper")

        # Initialize label manager
        label_manager = LabelManager()

        # Set application icon using the IconManager
        icon_manager = IconManager.instance()
        app.setWindowIcon(icon_manager.get_app_icon())

        if single_instance.is_running():
            QMessageBox.critical(
                None,
                label_manager.already_running_title,
                label_manager.already_running_message,
            )
            return 1

        # Check for API key and show dialog if not available
        settings_manager = SettingsManager.instance()
        if not settings_manager.has_valid_api_key():
            # Create and show initial API key dialog
            dialog = APIKeyDialogFactory.create_initial_dialog()

            if not dialog.exec():
                QMessageBox.critical(
                    None,
                    label_manager.no_api_key_title,
                    label_manager.no_api_key_message,
                )
                return 1

        # Create the main window using the factory
        main_window = MainWindowFactory.create_window()
        main_window.show()

        # Start the event loop
        return app.exec()

    finally:
        # Ensure cleanup
        single_instance.cleanup()


if __name__ == "__main__":
    sys.exit(status=start_application())
