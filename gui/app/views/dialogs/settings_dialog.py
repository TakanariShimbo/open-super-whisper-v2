"""
Settings Dialog View

This module provides the view component for the settings dialog in the Open Super Whisper application.
It allows users to configure application preferences like sound, indicator visibility, and auto-clipboard.
"""

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QWidget, QCheckBox, QDialogButtonBox, QGroupBox, QGridLayout, QComboBox, QLabel
from PyQt6.QtCore import pyqtSlot
from PyQt6.QtGui import QCloseEvent

from ...controllers.dialogs.settings_dialog_controller import SettingsDialogController
from ...managers.settings_manager import SettingsManager


class LabelManager:
    """
    Manages application labels for internationalization support.
    """

    ALL_LABELS = {
        "English": {
            "window_title": "Settings",
            "group_title": "Application Settings",
            "sound_checkbox": "Enable sound notifications",
            "sound_tooltip": "Play sounds when recording starts/stops and processing completes",
            "indicator_checkbox": "Show status indicator",
            "indicator_tooltip": "Show a visual indicator during recording and processing",
            "clipboard_checkbox": "Automatically copy results to clipboard",
            "clipboard_tooltip": "Copy transcription results to clipboard when processing completes",
            "language_label": "Language:",
            "language_tooltip": "Select the application language",
        },
        # Future: Add other languages here
    }

    def __init__(self) -> None:
        # load language from settings manager
        settings_manager = SettingsManager.instance()
        language = settings_manager.get_language()

        # set labels based on language
        self._labels = self.ALL_LABELS[language]

    @property
    def window_title(self) -> str:
        return self._labels["window_title"]

    @property
    def group_title(self) -> str:
        return self._labels["group_title"]

    @property
    def sound_checkbox(self) -> str:
        return self._labels["sound_checkbox"]

    @property
    def sound_tooltip(self) -> str:
        return self._labels["sound_tooltip"]

    @property
    def indicator_checkbox(self) -> str:
        return self._labels["indicator_checkbox"]

    @property
    def indicator_tooltip(self) -> str:
        return self._labels["indicator_tooltip"]

    @property
    def clipboard_checkbox(self) -> str:
        return self._labels["clipboard_checkbox"]

    @property
    def clipboard_tooltip(self) -> str:
        return self._labels["clipboard_tooltip"]

    @property
    def language_label(self) -> str:
        return self._labels["language_label"]

    @property
    def language_tooltip(self) -> str:
        return self._labels["language_tooltip"]


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

        # Initialize label manager
        self._label_manager = LabelManager()

        # Create controller
        self._controller = SettingsDialogController(settings_dialog=self)

        # Set up UI
        self._init_ui()

        # Initialize UI states from controller
        self._update_ui_elements()

        # Connect controller signals
        self._connect_controller_signals()

    #
    # UI Setup
    #
    def _init_ui(self) -> None:
        """
        Initialize the dialog UI components.
        """
        # Set dialog properties
        self.setWindowTitle(self._label_manager.window_title)
        self.setMinimumWidth(450)

        # Create main layout
        layout = QVBoxLayout(self)

        # Create settings group box
        settings_group = QGroupBox(self._label_manager.group_title)
        settings_layout = QGridLayout(settings_group)

        # Sound toggle
        self.sound_checkbox = QCheckBox(self._label_manager.sound_checkbox)
        self.sound_checkbox.setToolTip(self._label_manager.sound_tooltip)
        self.sound_checkbox.toggled.connect(self._on_toggle_sound)

        # Indicator visibility toggle
        self.indicator_checkbox = QCheckBox(self._label_manager.indicator_checkbox)
        self.indicator_checkbox.setToolTip(self._label_manager.indicator_tooltip)
        self.indicator_checkbox.toggled.connect(self._on_toggle_indicator)

        # Auto clipboard toggle
        self.clipboard_checkbox = QCheckBox(self._label_manager.clipboard_checkbox)
        self.clipboard_checkbox.setToolTip(self._label_manager.clipboard_tooltip)
        self.clipboard_checkbox.toggled.connect(self._on_toggle_clipboard)

        # Language selection
        language_label = QLabel(self._label_manager.language_label)
        self.language_combobox = QComboBox()
        self.language_combobox.addItems(self._controller.get_available_languages())
        self.language_combobox.setToolTip(self._label_manager.language_tooltip)
        self.language_combobox.currentTextChanged.connect(self._on_language_changed)

        # Add widgets to grid layout
        settings_layout.addWidget(self.sound_checkbox, 0, 0, 1, 2)
        settings_layout.addWidget(self.indicator_checkbox, 1, 0, 1, 2)
        settings_layout.addWidget(self.clipboard_checkbox, 2, 0, 1, 2)
        settings_layout.addWidget(language_label, 3, 0)
        settings_layout.addWidget(self.language_combobox, 3, 1)

        # Add button box
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self._on_accept)
        button_box.rejected.connect(self._on_reject)

        # Add elements to main layout
        layout.addWidget(settings_group)
        layout.addWidget(button_box)

    def _update_ui_elements(self) -> None:
        """
        Update the UI elements to reflect the current settings.
        """
        # Block signals from the UI elements
        self.sound_checkbox.blockSignals(True)
        self.indicator_checkbox.blockSignals(True)
        self.clipboard_checkbox.blockSignals(True)
        self.language_combobox.blockSignals(True)

        # Set checkbox states
        self.sound_checkbox.setChecked(self._controller.get_sound_enabled())
        self.indicator_checkbox.setChecked(self._controller.get_indicator_visible())
        self.clipboard_checkbox.setChecked(self._controller.get_auto_clipboard())

        # Set language selection
        self.language_combobox.setCurrentText(self._controller.get_language())

        # Unblock signals from the UI elements
        self.sound_checkbox.blockSignals(False)
        self.indicator_checkbox.blockSignals(False)
        self.clipboard_checkbox.blockSignals(False)
        self.language_combobox.blockSignals(False)

    #
    # Controller Signals
    #
    def _connect_controller_signals(self) -> None:
        """
        Connect signals from the controller.
        """
        # Connect the controller's settings_updated signal to refresh the entire view
        self._controller.settings_updated.connect(self._handle_settings_updated)

    #
    # Controller Events
    #
    @pyqtSlot()
    def _handle_settings_updated(self) -> None:
        """
        Handle settings updated event.
        """
        self._update_ui_elements()

    #
    # UI Events
    #
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

    @pyqtSlot(str)
    def _on_language_changed(self, language: str) -> None:
        """
        Handle language selection change.

        Parameters
        ----------
        language : str
            The selected language name
        """
        self._controller.set_language(language=language)

    #
    # Open/Close Events
    #
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
