#!/usr/bin/env python3
"""
Sample PyQt6 application demonstrating UI/logic separation and thread management.
"""
import sys
from PyQt6.QtWidgets import QApplication
from .app.views.main_window import MainWindow

def launch_qt_mvc_app():
    """Main application entry point to launch the Qt MVC demo application."""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    launch_qt_mvc_app()
