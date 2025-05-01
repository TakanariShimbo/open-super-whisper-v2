"""
Whisper GUI Package

This package provides the graphical user interface for the Whisper transcription application.
"""

from gui.windows import MainWindow
from old_core.hotkeys import HotkeyManager

__all__ = [
    'MainWindow',
    'HotkeyManager'
]
