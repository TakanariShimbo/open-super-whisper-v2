"""
System Tray Module

This module provides the SystemTray class for implementing system tray
functionality in the application.
"""

import os
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import pyqtSignal, QObject


class SystemTray(QSystemTrayIcon):
    """
    System tray icon for the application.
    
    This class provides a system tray icon with a context menu
    that allows the user to show/hide the main window or exit the
    application.
    
    Attributes
    ----------
    show_window_signal : pyqtSignal
        Signal emitted when the user requests to show the main window
    hide_window_signal : pyqtSignal
        Signal emitted when the user requests to hide the main window
    quit_application_signal : pyqtSignal
        Signal emitted when the user requests to quit the application
    recording_signal : pyqtSignal
        Signal emitted when the user requests to toggle recording
    """
    
    # Signals
    show_window_signal = pyqtSignal()
    hide_window_signal = pyqtSignal()
    quit_application_signal = pyqtSignal()
    recording_signal = pyqtSignal()
    
    def __init__(self, icon_path: str):
        """
        Initialize the SystemTray.
        
        Parameters
        ----------
        icon_path : str
            Path to the icon file to use for the tray icon
        """
        # Check if icon file exists
        if not os.path.exists(icon_path):
            # Use a fallback icon
            icon = QApplication.style().standardIcon(
                QApplication.style().StandardPixmap.SP_MediaPlay
            )
        else:
            # Use the specified icon
            icon = QIcon(icon_path)
        
        # Initialize tray with icon
        super().__init__(icon)
        
        # Set tooltip
        self.setToolTip("Super Whisper App")
        
        # Create context menu
        self._create_context_menu()
        
        # Connect activation signal
        self.activated.connect(self._handle_activation)
    
    def _create_context_menu(self):
        """
        Create the context menu for the tray icon.
        
        This menu provides options to show/hide the main window,
        start/stop recording, and exit the application.
        """
        menu = QMenu()
        
        # Show/hide action
        self.show_action = menu.addAction("Show Window")
        self.show_action.triggered.connect(self.show_window_signal.emit)
        
        # Add separator
        menu.addSeparator()
        
        # Toggle recording action
        self.record_action = menu.addAction("Start/Stop Recording")
        self.record_action.triggered.connect(self.recording_signal.emit)
        
        # Add separator
        menu.addSeparator()
        
        # Exit action
        exit_action = menu.addAction("Exit")
        exit_action.triggered.connect(self.quit_application_signal.emit)
        
        # Set context menu
        self.setContextMenu(menu)
    
    def _handle_activation(self, reason):
        """
        Handle tray icon activation.
        
        Parameters
        ----------
        reason : QSystemTrayIcon.ActivationReason
            The reason for activation
        """
        # Toggle window visibility on left click
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            # Emit show window signal
            self.show_window_signal.emit()
    
    def update_recording_state(self, is_recording: bool):
        """
        Update the tray icon based on recording state.
        
        Parameters
        ----------
        is_recording : bool
            Whether recording is in progress
        """
        if is_recording:
            self.record_action.setText("Stop Recording")
        else:
            self.record_action.setText("Start Recording")
