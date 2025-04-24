"""
GUI Application Entry Point

This module provides the main entry point for starting the GUI application.
"""

import os
import sys

from PyQt6.QtWidgets import QApplication, QMessageBox, QSystemTrayIcon, QStyle
from PyQt6.QtGui import QIcon

from gui.resources.config import AppConfig
from gui.resources.labels import AppLabels
from gui.utils.resource_helper import getResourcePath


def main():
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
    icon_path = getResourcePath("assets/icon.png")
    
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
        QMessageBox.critical(None, AppLabels.ERROR_TITLE, AppLabels.ERROR_SYSTEM_TRAY)
        sys.exit(1)
    
    # Prevent application from exiting when last window is closed
    app.setQuitOnLastWindowClosed(False)
    
    # Import MainWindow here to avoid circular imports
    from gui.windows import MainWindow
    
    # Create and show main window
    window = MainWindow()
    
    # Show hotkey information on first run
    settings = window.settings
    if not settings.contains("first_run_done"):
        hotkey = settings.value("hotkey", AppConfig.DEFAULT_HOTKEY)
        QMessageBox.information(
            window, 
            AppLabels.HOTKEY_INFO_TITLE, 
            AppLabels.HOTKEY_INFO_MESSAGE.format(hotkey)
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
    main()
