"""
Settings Dialog View

This module provides the view component for the settings dialog in the Open Super Whisper application.
It allows users to configure application preferences like sound, indicator visibility, and auto-clipboard.
"""

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QWidget, QCheckBox, QDialogButtonBox, QGroupBox, QGridLayout
from PyQt6.QtCore import pyqtSlot
from PyQt6.QtGui import QCloseEvent
from ...controllers.dialogs.settings_dialog_controller import SettingsDialogController


class SettingsDialog(QDialog):
    """
    Dialog for configuring application settings.

    This dialog allows users to adjust various settings like:
    - Sound notifications on/off
    - Status indicator visibility
    - Automatic clipboard copy after processing
    """

    def __init__(self, main_window: QWidget | None = None) -> None:
        """
        Initialize the SettingsDialog.

        Parameters
        ----------
        main_window : QWidget, optional
            Parent widget, by default None
        """
        super().__init__(parent=main_window)

        # Create controller
        self._controller = SettingsDialogController(settings_dialog=self)

        # Set up UI
        self._init_ui()

        # Connect controller signals
        self._connect_controller_signals()

        # Initialize UI states from controller
        self._update_ui_from_settings()

    def _init_ui(self) -> None:
        """
        Initialize the dialog UI components.
        """
        # Set dialog properties
        self.setWindowTitle("Settings")
        self.setMinimumWidth(450)

        # Create main layout
        layout = QVBoxLayout(self)

        # Create settings group box
        settings_group = QGroupBox("Application Settings")
        settings_layout = QGridLayout(settings_group)

        # Sound toggle
        self.sound_checkbox = QCheckBox("Enable sound notifications")
        self.sound_checkbox.setToolTip("Play sounds when recording starts/stops and processing completes")
        self.sound_checkbox.toggled.connect(self._on_toggle_sound)

        # Indicator visibility toggle
        self.indicator_checkbox = QCheckBox("Show status indicator")
        self.indicator_checkbox.setToolTip("Show a visual indicator during recording and processing")
        self.indicator_checkbox.toggled.connect(self._on_toggle_indicator)

        # Auto clipboard toggle
        self.clipboard_checkbox = QCheckBox("Automatically copy results to clipboard")
        self.clipboard_checkbox.setToolTip("Copy transcription results to clipboard when processing completes")
        self.clipboard_checkbox.toggled.connect(self._on_toggle_clipboard)

        # Add checkboxes to grid layout
        settings_layout.addWidget(self.sound_checkbox, 0, 0)
        settings_layout.addWidget(self.indicator_checkbox, 1, 0)
        settings_layout.addWidget(self.clipboard_checkbox, 2, 0)

        # Add button box
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self._on_accept)
        button_box.rejected.connect(self._on_reject)

        # Add elements to main layout
        layout.addWidget(settings_group)
        layout.addWidget(button_box)

    def _connect_controller_signals(self) -> None:
        """
        Connect signals from the controller.
        """
        # Connect the controller's settings_updated signal to refresh the entire view
        self._controller.settings_updated.connect(self._handle_settings_updated)

    def _update_ui_from_settings(self) -> None:
        """
        Update UI controls to reflect current settings.
        """
        # Block signals to prevent feedback loops
        self.sound_checkbox.blockSignals(True)
        self.indicator_checkbox.blockSignals(True)
        self.clipboard_checkbox.blockSignals(True)

        # Set checkbox states
        self.sound_checkbox.setChecked(self._controller.get_sound_enabled())
        self.indicator_checkbox.setChecked(self._controller.get_indicator_visible())
        self.clipboard_checkbox.setChecked(self._controller.get_auto_clipboard())

        # Unblock signals
        self.sound_checkbox.blockSignals(False)
        self.indicator_checkbox.blockSignals(False)
        self.clipboard_checkbox.blockSignals(False)

    @pyqtSlot()
    def _handle_settings_updated(self) -> None:
        """
        Handle settings updated event.
        """
        self._update_ui_from_settings()

    @pyqtSlot(bool)
    def _on_toggle_sound(self, enabled: bool) -> None:
        """
        Handle sound checkbox toggle.

        Parameters
        ----------
        enabled : bool
            New checkbox state
        """
        self._controller.set_sound_enabled(enabled=enabled)

    @pyqtSlot(bool)
    def _on_toggle_indicator(self, visible: bool) -> None:
        """
        Handle indicator checkbox toggle.

        Parameters
        ----------
        visible : bool
            New checkbox state
        """
        self._controller.set_indicator_visible(visible=visible)

    @pyqtSlot(bool)
    def _on_toggle_clipboard(self, enabled: bool) -> None:
        """
        Handle clipboard checkbox toggle.

        Parameters
        ----------
        enabled : bool
            New checkbox state
        """
        self._controller.set_auto_clipboard(enabled=enabled)

    @pyqtSlot()
    def _on_accept(self) -> None:
        """
        Handle dialog acceptance.
        """
        # Save settings
        self._controller.save_settings()

        # Accept the dialog
        super().accept()

    @pyqtSlot()
    def _on_reject(self) -> None:
        """
        Handle dialog rejection.
        """
        # Restore original settings
        self._controller.cancel()

        # Reject the dialog
        super().reject()

    def closeEvent(self, event: QCloseEvent) -> None:
        """
        Handle dialog close event.

        Parameters
        ----------
        event : QCloseEvent
            Close event
        """
        # Restore original settings
        self._controller.cancel()

        # Call parent class method
        super().closeEvent(event)
