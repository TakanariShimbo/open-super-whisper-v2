"""
PyQt6 System Tray Module

This module implements a system tray icon for the application, allowing it to
run in the background while maintaining accessibility through the system tray.

The SystemTray class provides functionality for showing and hiding the application
window, as well as properly quitting the application. It follows the single 
responsibility principle by handling only system tray related functionality.
"""
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import Qt, pyqtSignal


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
    """
    
    # Define signals for communication with the main window
    show_window_signal = pyqtSignal()
    hide_window_signal = pyqtSignal()
    quit_application_signal = pyqtSignal()
    
    def __init__(self, icon_path: str) -> None:
        """
        Initialize the SystemTray.
        
        Creates a system tray icon with a context menu and connects signals.
        
        Parameters
        ----------
        icon_path : str
            Path to the icon file to be displayed in the system tray
        """
        super().__init__()
        
        # Set the icon
        self.setIcon(QIcon(icon_path))
        self.setToolTip("Qt MVC Demo")
        
        # Create the tray menu
        self._create_tray_menu()
        
        # Connect tray icon signals
        self.activated.connect(self._handle_tray_icon_activated)
        
    def _create_tray_menu(self) -> None:
        """
        Create the context menu for the system tray icon.
        
        This method sets up the menu items for showing/hiding the application
        window and for quitting the application.
        """
        # Create the menu
        self.tray_menu = QMenu()
        
        # Create actions
        self.show_action = QAction("Show Window")
        self.hide_action = QAction("Hide Window")
        self.quit_action = QAction("Quit")
        
        # Connect action signals
        self.show_action.triggered.connect(self._on_show_window)
        self.hide_action.triggered.connect(self._on_hide_window)
        self.quit_action.triggered.connect(self._on_quit_application)
        
        # Add actions to menu
        self.tray_menu.addAction(self.show_action)
        self.tray_menu.addAction(self.hide_action)
        self.tray_menu.addSeparator()
        self.tray_menu.addAction(self.quit_action)
        
        # Set the menu
        self.setContextMenu(self.tray_menu)
    
    def _on_show_window(self) -> None:
        """Handle show window action."""
        self.show_window_signal.emit()
        
    def _on_hide_window(self) -> None:
        """Handle hide window action."""
        self.hide_window_signal.emit()
        
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
