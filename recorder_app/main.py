#!/usr/bin/env python3
"""
Recorder Application

This module serves as the entry point for a simple recording application built with PyQt6.
It demonstrates MVC architecture with a focus on audio recording functionality using
the core audio recorder and hotkey manager modules.

The application allows users to start and stop recording with both UI controls and hotkeys.
"""
import sys
from PyQt6.QtWidgets import QApplication
from .app.views.main_window import MainWindow

def launch_recorder_app() -> None:
    """
    Launch the recorder application.
    
    This function initializes the QApplication, creates the main window,
    and starts the event loop.
    """
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    launch_recorder_app()
