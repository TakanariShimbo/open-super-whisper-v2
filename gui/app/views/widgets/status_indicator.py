"""
Status Indicator Window

This module provides a floating window that displays the current status of recording.
It is designed to work with the MVC architecture and single responsibility principle.
"""

from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QFrame
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QPalette, QColor, QShowEvent, QMouseEvent


class StatusIndicatorWindow(QWidget):
    """
    Floating indicator window for recording, processing, and completion status.
    
    This window shows the current status of recording, transcription,
    and provides visual feedback to the user.
    """
    
    # Status constants
    MODE_RECORDING = 1
    MODE_PROCESSING = 2
    MODE_COMPLETED = 3
    MODE_CANCELLED = 4
    
    def __init__(self, parent=None) -> None:
        """
        Initialize the StatusIndicatorWindow.
        
        Parameters
        ----------
        parent : QWidget, optional
            Parent widget, by default None
        """
        super().__init__(parent, Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        
        # Set window properties
        self.setMinimumSize(120, 60)
        self.setMaximumSize(200, 100)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Set initial mode
        self._current_mode = self.MODE_RECORDING
        
        # Init UI
        self._init_ui()
        
        # Position window in bottom right corner of screen
        self._update_position()
    
    def _init_ui(self) -> None:
        """
        Initialize user interface.
        """
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Create frame for background
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.Box)
        frame.setLineWidth(1)
        frame.setMidLineWidth(0)
        
        # Set background color
        palette = frame.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(30, 30, 30, 220))
        frame.setAutoFillBackground(True)
        frame.setPalette(palette)
        
        # Frame layout
        frame_layout = QVBoxLayout(frame)
        
        # Status text
        self.status_label = QLabel("Recording...")
        self.status_label.setStyleSheet("color: #ff5f5f; font-weight: bold;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Timer text
        self.timer_label = QLabel("00:00")
        self.timer_label.setStyleSheet("color: white;")
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Add to layout
        frame_layout.addWidget(self.status_label)
        frame_layout.addWidget(self.timer_label)
        
        # Add frame to main layout
        main_layout.addWidget(frame)
        
        # Update indicator based on initial mode
        self._update_indicator()
    
    def _update_position(self) -> None:
        """
        Update window position to bottom right corner of screen.
        """
        desktop = self.screen().availableGeometry()
        self.move(desktop.width() - self.width() - 20, desktop.height() - self.height() - 60)
    
    def _update_indicator(self) -> None:
        """
        Update the indicator visuals based on current mode.
        """
        if self._current_mode == self.MODE_RECORDING:
            self.status_label.setText("Recording...")
            self.status_label.setStyleSheet("color: #ff5f5f; font-weight: bold;")
        elif self._current_mode == self.MODE_PROCESSING:
            self.status_label.setText("Processing...")
            self.status_label.setStyleSheet("color: #999999; font-weight: bold;")
            self.timer_label.setText("")
        elif self._current_mode == self.MODE_COMPLETED:
            self.status_label.setText("Completed!")
            self.status_label.setStyleSheet("color: #5fff5f; font-weight: bold;")
            self.timer_label.setText("")
        elif self._current_mode == self.MODE_CANCELLED:
            self.status_label.setText("Cancelled!")
            self.status_label.setStyleSheet("color: #ff9f3f; font-weight: bold;")
            self.timer_label.setText("")
    
    @pyqtSlot(int)
    def set_mode(self, mode: int) -> None:
        """
        Set the current mode of the indicator.
        
        Parameters
        ----------
        mode : int
            Mode constant (MODE_RECORDING, MODE_PROCESSING, MODE_COMPLETE, MODE_CANCELLED)
        """
        self._current_mode = mode
        self._update_indicator()
    
    @pyqtSlot(str)
    def update_timer(self, time_str: str) -> None:
        """
        Update the timer display.
        
        Parameters
        ----------
        time_str : str
            Time string to display (e.g. "00:15")
        """
        self.timer_label.setText(time_str)
    
    def showEvent(self, event: QShowEvent) -> None:
        """
        Handle show event by updating position.
        """
        super().showEvent(event)
        self._update_position()
        
    def mousePressEvent(self, event: QMouseEvent) -> None:
        """
        Handle mouse press events for dragging the window.
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_start_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """
        Handle mouse move events for dragging the window.
        """
        if event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_start_position)
            event.accept()
