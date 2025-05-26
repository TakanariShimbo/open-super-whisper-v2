"""
System Tray Module

This module implements a system tray icon for the Open Super Whisper application,
allowing it to run in the background while maintaining accessibility.
"""

from typing import Literal

from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QWidget
from PyQt6.QtGui import QAction
from PyQt6.QtCore import pyqtSignal, pyqtSlot

from ...managers.icon_manager import IconManager
from ...managers.settings_manager import SettingsManager


class LabelManager:
    """
    Manages application labels for internationalization support in System Tray.
    """

    ALL_LABELS = {
        "English": {
            # Tooltip
            "app_tooltip": "Open Super Whisper",
            # Menu Actions
            "show_window": "Show Window",
            "hide_window": "Hide Window",
            "start_recording": "Start Recording",
            "stop_recording": "Stop Recording",
            "cancel_processing": "Cancel Processing",
            "quit_application": "Quit Application",
        },
        "Japanese": {
            # Tooltip
            "app_tooltip": "Open Super Whisper",
            # Menu Actions
            "show_window": "ウィンドウ表示",
            "hide_window": "ウィンドウ非表示",
            "start_recording": "録音開始",
            "stop_recording": "録音停止",
            "cancel_processing": "処理キャンセル",
            "quit_application": "アプリ終了",
        },
        # Future: Add other languages here
    }

    def __init__(self) -> None:
        # Load language from settings manager
        settings_manager = SettingsManager.instance()
        language = settings_manager.get_language()

        # Set labels based on language
        self._labels = self.ALL_LABELS[language]

    # Tooltip
    @property
    def app_tooltip(self) -> str:
        return self._labels["app_tooltip"]

    # Menu Actions
    @property
    def show_window(self) -> str:
        return self._labels["show_window"]

    @property
    def hide_window(self) -> str:
        return self._labels["hide_window"]

    @property
    def start_recording(self) -> str:
        return self._labels["start_recording"]

    @property
    def stop_recording(self) -> str:
        return self._labels["stop_recording"]

    @property
    def cancel_processing(self) -> str:
        return self._labels["cancel_processing"]

    @property
    def quit_application(self) -> str:
        return self._labels["quit_application"]


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

    def __init__(
        self,
        main_window: QWidget | None = None,
    ) -> None:
        """
        Initialize the SystemTray.

        Parameters
        ----------
        main_window : QWidget, optional
            The main window of the application
        """
        super().__init__(parent=main_window)

        # Initialize label manager
        self._label_manager = LabelManager()

        # Initialize managers
        self._icon_manager = IconManager.instance()

        # Set the icon
        self._set_icon()

        self.setToolTip(self._label_manager.app_tooltip)

        # Create the tray menu
        self._create_tray_menu()

    #
    # UI Setup
    #
    def _set_icon(self) -> None:
        """
        Set the system tray icon.
        """
        icon = self._icon_manager.get_app_icon()
        self.setIcon(icon)

    def _create_tray_menu(self) -> None:
        """
        Create the context menu for the system tray icon.
        """
        # Create the menu
        self._tray_menu = QMenu()

        # Create actions
        self._show_action = QAction(self._label_manager.show_window)
        self._show_action.triggered.connect(self._on_show_window)

        self._hide_action = QAction(self._label_manager.hide_window)
        self._hide_action.triggered.connect(self._on_hide_window)

        # Create record action
        self._record_action = QAction(self._label_manager.start_recording)
        self._record_action.triggered.connect(self._on_toggle_recording)

        self._quit_action = QAction(self._label_manager.quit_application)
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

        # Connect tray icon signals
        self.activated.connect(self._handle_tray_icon_activated)

    #
    # UI Events
    #
    @pyqtSlot()
    def _on_show_window(self) -> None:
        """
        Handle show window action.
        """
        self.show_window_signal.emit()

    @pyqtSlot()
    def _on_hide_window(self) -> None:
        """
        Handle hide window action.
        """
        self.hide_window_signal.emit()

    @pyqtSlot()
    def _on_toggle_recording(self) -> None:
        """
        Handle toggle recording action.
        """
        self.toggle_recording_signal.emit()

    @pyqtSlot()
    def _on_quit_application(self) -> None:
        """
        Handle quit application action.
        """
        self.quit_application_signal.emit()

    @pyqtSlot(QSystemTrayIcon.ActivationReason)
    def _handle_tray_icon_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        """
        Handle activation of the tray icon.

        Parameters
        ----------
        reason : QSystemTrayIcon.ActivationReason
            The reason for the activation (e.g., click, double-click, etc.)
        """
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            # Single click - toggle window visibility
            self.show_window_signal.emit()

    #
    # Controller Methods
    #
    def update_recording_status(self, status: Literal["start_recording", "stop_recording", "cancel_processing"]) -> None:
        """
        Update the recording action text based on recording status.

        Parameters
        ----------
        status : Literal["start_recording", "stop_recording", "cancel_processing"]
            The status of the recording
        """
        if status == "start_recording":
            self._record_action.setText(self._label_manager.start_recording)
        elif status == "stop_recording":
            self._record_action.setText(self._label_manager.stop_recording)
        elif status == "cancel_processing":
            self._record_action.setText(self._label_manager.cancel_processing)
