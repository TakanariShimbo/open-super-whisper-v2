#!/usr/bin/env python3
"""
PyQt6 MVC Application Demo

This module demonstrates a Model-View-Controller (MVC) architecture using PyQt6.
It shows how to properly separate UI logic from business logic and how to
manage background tasks using threads for responsive UI applications.

The module serves as the main entry point for the demo application, initializing
the QApplication and launching the main window.

Examples
--------
To run the demo application:
    python main.py

See Also
--------
app.controllers.app_controller : Contains the application controller logic
app.models.thread_manager : Manages worker threads
app.models.task_worker : Implements the worker for background tasks
app.views.main_window : Implements the main application window
"""
import sys
from PyQt6.QtWidgets import QApplication
from .app.views.main_window import MainWindow

def launch_qt_mvc_app() -> None:
    """Launch the Qt MVC demo application.
    
    This function serves as the main entry point for the Qt MVC demo application.
    It initializes the QApplication, creates the main window, and starts the
    event loop.
    
    Parameters
    ----------
    None
    
    Returns
    -------
    None
        Although this function calls sys.exit(), it's marked as returning None for
        simplicity in this educational demonstration.
    
    Examples
    --------
    >>> launch_qt_mvc_app()
    # Starts the application and enters the Qt event loop
    """
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    launch_qt_mvc_app()
