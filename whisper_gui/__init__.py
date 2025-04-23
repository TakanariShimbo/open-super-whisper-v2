"""
Whisper GUI Package

This package provides the graphical user interface for the Whisper transcription application.
"""

from whisper_gui.windows import MainWindow
from whisper_core.hotkeys import HotkeyManager

__all__ = [
    'MainWindow',
    'HotkeyManager'
]
