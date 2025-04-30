"""
GUI Application Entry Point

This module provides the entry point for starting the GUI application.
"""

import os
import sys

from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QStyle
from PyQt6.QtGui import QIcon

from gui.resources.config import AppConfig
from gui.resources.labels import AppLabels
from gui.utils.resource_helper import getResourcePath
from gui.dialogs.simple_message_dialog import SimpleMessageDialog
from gui.windows import MainWindow


def start_application():
    """
    Application entry point.
    
    Initialize the application, set up the main window, and run the event loop.
    Can start minimized if command line arguments specify.
    
    Returns
    -------
    int
        Application exit code.
    """
    app = QApplication(sys.argv)
    
    # Set application icon
    icon_path = getResourcePath(AppConfig.ICON_PATH)
    
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    else:
        # Use standard icon if icon file is not found
        app_icon = QApplication.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay)
        app.setWindowIcon(app_icon)
        print(f"Warning: Application icon file not found: {icon_path}")
    
    # High DPI scaling is enabled by default in PyQt6
    
    # Check if system tray is supported
    if not QSystemTrayIcon.isSystemTrayAvailable():
        SimpleMessageDialog.show_message(None, AppLabels.MAIN_SYSTEM_TRAY_ERROR_TITLE , AppLabels.MAIN_SYSTEM_TRAY_ERROR_MESSAGE, SimpleMessageDialog.ERROR)
        sys.exit(1)
    
    # Prevent application from exiting when last window is closed
    app.setQuitOnLastWindowClosed(False)
    
    # Create and show main window
    window = MainWindow()
    
    # Show hotkey information on first run
    settings = window.settings
    if not settings.contains("first_run_done"):
        SimpleMessageDialog.show_message(
            window, 
            AppLabels.MAIN_HOTKEY_INFO_TITLE, 
            AppLabels.MAIN_HOTKEY_INFO_MESSAGE,
            SimpleMessageDialog.INFO
        )
        settings.setValue("first_run_done", True)
    
    # Show window (default to tray minimized)
    if '--minimized' in sys.argv or '-m' in sys.argv:
        # Start minimized to tray
        pass
    else:
        window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    start_application()
