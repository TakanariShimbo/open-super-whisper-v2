"""
System Tray Module

This module implements a system tray icon for the Super Whisper application,
allowing it to run in the background while maintaining accessibility.
"""

import os

from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QStyle, QApplication
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import pyqtSignal

from ...utils.icon_manager import IconManager


class SystemTray(QSystemTrayIcon):
    """
    System tray icon class that provides background operation capabilities.
    
    This class manages a system tray icon and its context menu, allowing the user
    to control the application's visibility and to properly exit the application.
    
    Attributes
    ----------
    show_window_signal : pyqtSignal
        Signal emitted when the user wants to show the application window
    hide_window_signal : pyqtSignal
        Signal emitted when the user wants to hide the application window
    quit_application_signal : pyqtSignal
        Signal emitted when the user wants to quit the application
    toggle_recording_signal : pyqtSignal
        Signal emitted when the user wants to toggle recording
    """
    
    # Define signals for communication with the main window
    show_window_signal = pyqtSignal()
    hide_window_signal = pyqtSignal()
    quit_application_signal = pyqtSignal()
    toggle_recording_signal = pyqtSignal()
    
    def __init__(self, icon_path: str = None) -> None:
        """
        Initialize the SystemTray.
        
        Creates a system tray icon with a context menu and connects signals.
        
        Parameters
        ----------
        icon_path : str, optional
            Path to the icon file to be displayed in the system tray
        """
        super().__init__()
        
        # Set the icon
        self._set_icon(icon_path)
        
        self.setToolTip("Super Whisper App")
        
        # Create the tray menu
        self._create_tray_menu()
        
        # Connect tray icon signals
        self.activated.connect(self._handle_tray_icon_activated)
    
    def _set_icon(self, icon_path: str = None) -> None:
        """
        Set the system tray icon.
        
        If the specified icon_path doesn't exist or is None, 
        falls back to a standard system icon.
        
        Parameters
        ----------
        icon_path : str, optional
            Path to the icon file
        """
        icon = None
        
        # Try to use the specified icon if provided and exists
        if icon_path and os.path.exists(icon_path):
            icon = QIcon(icon_path)
        
        # If no valid icon, use a standard system icon
        if not icon or icon.isNull():
            try:
                # Try to use IconManager as fallback
                icon_manager = IconManager()
                icon = icon_manager.get_app_icon()
            except Exception:
                # Fallback to system icon if IconManager is not available
                icon = QApplication.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay)
        
        self.setIcon(icon)
    
    def _create_tray_menu(self) -> None:
        """
        Create the context menu for the system tray icon.
        
        This method sets up the menu items for showing/hiding the application
        window and for quitting the application.
        """
        # Create the menu
        self._tray_menu = QMenu()
        
        # Create actions
        self._show_action = QAction("Show Window")
        self._hide_action = QAction("Hide Window")
        
        # Create record action
        self._record_action = QAction("Start Recording")
        
        self._quit_action = QAction("Quit")
        
        # Connect action signals
        self._show_action.triggered.connect(self._on_show_window)
        self._hide_action.triggered.connect(self._on_hide_window)
        self._record_action.triggered.connect(self._on_toggle_recording)
        self._quit_action.triggered.connect(self._on_quit_application)
        
        # Add actions to menu
        self._tray_menu.addAction(self._show_action)
        self._tray_menu.addAction(self._hide_action)
        self._tray_menu.addSeparator()
        self._tray_menu.addAction(self._record_action)
        self._tray_menu.addSeparator()
        self._tray_menu.addAction(self._quit_action)
        
        # Set the menu
        self.setContextMenu(self._tray_menu)
    
    def _on_show_window(self) -> None:
        """Handle show window action."""
        self.show_window_signal.emit()
        
    def _on_hide_window(self) -> None:
        """Handle hide window action."""
        self.hide_window_signal.emit()
    
    def _on_toggle_recording(self) -> None:
        """Handle toggle recording action."""
        self.toggle_recording_signal.emit()
        
    def _on_quit_application(self) -> None:
        """Handle quit application action."""
        self.quit_application_signal.emit()
    
    def _handle_tray_icon_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        """
        Handle activation of the tray icon.
        
        This method determines what action to take when the tray icon is clicked,
        depending on the activation reason.
        
        Parameters
        ----------
        reason : QSystemTrayIcon.ActivationReason
            The reason for the activation (e.g., click, double-click, etc.)
        """
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            # Single click - toggle window visibility
            self.show_window_signal.emit()
            
    def update_recording_status(self, is_recording: bool) -> None:
        """
        Update the recording action text based on recording status.
        
        Parameters
        ----------
        is_recording : bool
            True if recording is in progress, False otherwise
        """
        if is_recording:
            self._record_action.setText("Stop Recording")
        else:
            self._record_action.setText("Start Recording")
