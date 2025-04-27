"""
UI Updater Implementation

This module provides a class for safely updating UI elements
from different threads in a Qt application.
"""

from PyQt6.QtCore import QObject, pyqtSignal, Qt
from PyQt6.QtWidgets import QStatusBar, QLabel

class UIUpdater(QObject):
    """
    Class for centralized UI updates
    
    This class centralizes UI component updates and
    ensures thread-safe updates.
    """
    
    def __init__(self, status_bar: QStatusBar, recording_indicator: QLabel, 
                 recording_timer_label: QLabel):
        """
        Initialize UIUpdater
        
        Parameters
        ----------
        status_bar : QStatusBar
            Status bar
        recording_indicator : QLabel
            Recording status indicator
        recording_timer_label : QLabel
            Recording timer label
        """
        super().__init__()
        
        self.status_bar = status_bar
        self.recording_indicator = recording_indicator
        self.recording_timer_label = recording_timer_label
    
    def update_status(self, message: str, timeout: int = 0) -> None:
        """
        Update the status bar
        
        Parameters
        ----------
        message : str
            Message to display
        timeout : int, optional
            Display time (milliseconds), 0 for persistent display
        """
        self.status_bar.showMessage(message, timeout)
    
    def update_recording_indicator(self, text: str) -> None:
        """
        Update the recording status indicator
        
        Parameters
        ----------
        text : str
            Text to display for the recording status
        """
        self.recording_indicator.setText(text)
    
    def update_timer_label(self, time_str: str) -> None:
        """
        Update the timer label
        
        Parameters
        ----------
        time_str : str
            Time string to display (e.g., "00:15")
        """
        self.recording_timer_label.setText(time_str)
