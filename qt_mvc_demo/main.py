#!/usr/bin/env python3
"""
PyQt6 MVC Application Demo with System Tray Support

This module demonstrates a Model-View-Controller (MVC) architecture using PyQt6.
It shows how to properly separate UI logic from business logic and how to
manage background tasks using threads for responsive UI applications.

The application now includes system tray functionality, allowing it to run
in the background while maintaining accessibility through the system tray icon.
This provides a better user experience for applications that need to continue
running even when the main window is closed.

The module serves as the main entry point for the demo application, initializing
the QApplication and launching the main window.
"""
import sys

from PyQt6.QtWidgets import QApplication

from .app.views.main_window import MainWindow


def launch_qt_mvc_app() -> None:
    """Launch the Qt MVC demo application.
    
    This function serves as the main entry point for the Qt MVC demo application.
    It initializes the QApplication, creates the main window, and starts the
    event loop. The application will continue running in the system tray even
    when the main window is closed.
    """
    app = QApplication(sys.argv)
    
    # Allow the application to run even when the last window is closed
    app.setQuitOnLastWindowClosed(False)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    launch_qt_mvc_app()
