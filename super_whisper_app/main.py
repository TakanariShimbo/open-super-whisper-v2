#!/usr/bin/env python3
"""
Super Whisper App - Main Entry Point

This module serves as the entry point for the Super Whisper application.
It initializes the PyQt application and launches the main window.
"""

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QCoreApplication, Qt

from super_whisper_app.app.views.main_window import MainWindow

def main():
    """
    Main application entry point.
    
    Sets up the Qt application, applies high-DPI settings,
    and initializes the main window.
    """
    # Set application info
    QCoreApplication.setApplicationName("Super Whisper App")
    QCoreApplication.setOrganizationName("Super Whisper")
    
    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    # Create application
    app = QApplication(sys.argv)
    
    # Create and show main window
    main_window = MainWindow()
    main_window.show()
    
    # Start event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
