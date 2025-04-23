"""
Status Indicator Widget Module

This module provides a floating status indicator that shows the current
status of recording and transcription.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QApplication
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QPalette, QFont, QScreen
import sys


class StatusIndicatorWindow(QWidget):
    """
    A small floating window that indicates the current recording or
    transcription status.
    
    This widget appears on top of other windows to provide feedback
    about the current recording or transcription status, even when
    the main application window is minimized or in the background.
    """
    
    # Status modes
    MODE_RECORDING = 0
    MODE_TRANSCRIBING = 1
    MODE_TRANSCRIBED = 2
    
    def __init__(self):
        """
        Initialize the StatusIndicatorWindow.
        """
        super().__init__()
        
        # Window properties
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(200, 100)
        
        # Position the widget in the top-right corner of the screen
        self.position_widget()
        
        # Current mode
        self.current_mode = self.MODE_RECORDING
        
        # Create the layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Create the status label
        self.status_label = QLabel("Recording")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(self.status_label)
        
        # Create the timer label
        self.timer_label = QLabel("00:00")
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.timer_label.setFont(QFont("Arial", 14))
        layout.addWidget(self.timer_label)
        
        # Auto-hide timer for transcription complete mode
        self.auto_hide_timer = QTimer(self)
        self.auto_hide_timer.setSingleShot(True)
        self.auto_hide_timer.timeout.connect(self.hide)
        
        # Set initial mode
        self.set_mode(self.MODE_RECORDING)
    
    def position_widget(self):
        """
        Position the widget in the top-right corner of the screen.
        """
        screen = QApplication.primaryScreen().geometry()
        
        # Calculate position (top-right with 20px margin)
        x = screen.width() - self.width() - 20
        y = 20
        
        self.move(x, y)
    
    def set_mode(self, mode):
        """
        Set the display mode of the indicator.
        
        Parameters
        ----------
        mode : int
            One of MODE_RECORDING, MODE_TRANSCRIBING, MODE_TRANSCRIBED.
        """
        self.current_mode = mode
        
        # Update based on mode
        if mode == self.MODE_RECORDING:
            self.status_label.setText("Recording")
            self.setStyleSheet("""
                background-color: rgba(255, 0, 0, 180);
                color: white;
                border-radius: 10px;
            """)
            # Reset timer if auto-hide timer was running
            if self.auto_hide_timer.isActive():
                self.auto_hide_timer.stop()
                
        elif mode == self.MODE_TRANSCRIBING:
            self.status_label.setText("Transcribing")
            self.setStyleSheet("""
                background-color: rgba(0, 0, 255, 180);
                color: white;
                border-radius: 10px;
            """)
            self.timer_label.setText("")
            # Reset timer if auto-hide timer was running
            if self.auto_hide_timer.isActive():
                self.auto_hide_timer.stop()
                
        elif mode == self.MODE_TRANSCRIBED:
            self.status_label.setText("Transcription Complete")
            self.setStyleSheet("""
                background-color: rgba(0, 128, 0, 180);
                color: white;
                border-radius: 10px;
            """)
            self.timer_label.setText("")
            # Auto-hide after 3 seconds
            self.auto_hide_timer.start(3000)
    
    def update_timer(self, time_str):
        """
        Update the displayed timer value.
        
        Parameters
        ----------
        time_str : str
            The time string to display (format: "MM:SS").
        """
        self.timer_label.setText(time_str)
    
    def showEvent(self, event):
        """
        Overridden show event to ensure proper positioning.
        
        Parameters
        ----------
        event : QShowEvent
            The show event.
        """
        super().showEvent(event)
        # Ensure proper positioning when shown
        self.position_widget()


# For standalone testing
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    widget = StatusIndicatorWindow()
    widget.show()
    
    # Test different modes with a timer
    def change_mode():
        current_mode = widget.current_mode
        next_mode = (current_mode + 1) % 3
        widget.set_mode(next_mode)
        if next_mode == StatusIndicatorWindow.MODE_RECORDING:
            # Update timer for recording mode
            widget.update_timer("01:23")
    
    timer = QTimer()
    timer.timeout.connect(change_mode)
    timer.start(2000)  # Change mode every 2 seconds
    
    sys.exit(app.exec())
