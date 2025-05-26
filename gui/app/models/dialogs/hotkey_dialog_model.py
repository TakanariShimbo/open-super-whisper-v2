"""
Hotkey Dialog Model

This module provides the model component for the hotkey dialog,
handling the data and business logic related to hotkey management.
"""

from PyQt6.QtCore import QObject, pyqtSignal

from ...managers.instruction_sets_manager import InstructionSetsManager
from ...managers.keyboard_manager import KeyboardManager
from ...managers.settings_manager import SettingsManager


class LabelManager:
    """
    Manages application labels for internationalization support.
    """

    ALL_LABELS = {
        "English": {
            "invalid_hotkey_format_message": "Invalid hotkey format: {hotkey}",
            "hotkey_already_used_message": "The hotkey '{hotkey}' is already used by instruction set '{conflicting_set_name}'.",
        },
        "Japanese": {
            "invalid_hotkey_format_message": "無効なホットキー形式: {hotkey}",
            "hotkey_already_used_message": "ホットキー '{hotkey}' はインストラクションセット '{conflicting_set_name}' で既に使用されています。",
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
    def invalid_hotkey_format_message(self) -> str:
        return self._labels["invalid_hotkey_format_message"]

    @property
    def hotkey_already_used_message(self) -> str:
        return self._labels["hotkey_already_used_message"]


class HotkeyDialogModel(QObject):
    """
    Model for the hotkey dialog.

    This class handles the data and business logic for hotkey configuration,
    including capturing, formatting, and validating hotkey combinations.

    Attributes
    ----------
    hotkey_changed : pyqtSignal
        Signal emitted when the hotkey value changes
    hotkey_captured : pyqtSignal
        Signal emitted when a new key combination is captured
    validation_failed : pyqtSignal
        Signal emitted when hotkey validation fails, with error message
    """

    #
    # Signals
    #
    hotkey_changed = pyqtSignal(str)
    hotkey_captured = pyqtSignal(str)
    validation_failed = pyqtSignal(str)  # error_message

    def __init__(
        self,
        current_hotkey: str = "",
        hotkey_dialog: QObject | None = None,
    ) -> None:
        """
        Initialize the HotkeyDialogModel.

        Parameters
        ----------
        current_hotkey : str, optional
            Initial hotkey value, by default ""
        hotkey_dialog : QObject | None, optional
            The parent object, by default None
        """
        super().__init__(parent=hotkey_dialog)

        # Store the current and original hotkey values
        self._hotkey = current_hotkey
        self._original_hotkey = current_hotkey

        # Create key state tracker for capturing key combinations
        self._instruction_sets_manager = InstructionSetsManager.get_instance()
        self._keyboard_manager = KeyboardManager.get_instance()

        # Initialize label manager for internationalization
        self._label_manager = LabelManager()

    #
    # Model Methods
    #
    @property
    def is_capturing(self) -> bool:
        """
        Check if key capture mode is active.

        Returns
        -------
        bool
            True if capturing key inputs, False otherwise
        """
        return self._keyboard_manager.is_monitoring

    def get_hotkey(self) -> str:
        """
        Get the current hotkey.

        Returns
        -------
        str
            The current hotkey string
        """
        return self._hotkey

    def set_hotkey(self, value: str) -> None:
        """
        Set the current hotkey.

        Parameters
        ----------
        value : str
            The new hotkey value
        """
        if self._hotkey != value:
            self._hotkey = value
            self.hotkey_changed.emit(value)

    def start_capturing(self) -> None:
        """
        Start capturing keyboard inputs.
        """
        self._keyboard_manager.start_monitoring()

    def stop_capturing(self) -> None:
        """
        Stop capturing keyboard inputs.
        """
        self._keyboard_manager.stop_monitoring()

    def capture_keys(self) -> None:
        """
        Capture and process the key combination.
        """
        # Get the key combination from the tracker
        keys_list = self._keyboard_manager.capture_last_keys()

        # If no keys are pressed, don't update
        if not keys_list:
            return

        # Create hotkey string (e.g., "ctrl+shift+a")
        hotkey_string = "+".join(keys_list)

        # Update the model
        self.set_hotkey(value=hotkey_string)

        # Emit the captured signal
        self.hotkey_captured.emit(hotkey_string)

    def _check_hotkey_conflict(self, hotkey: str) -> str | None:
        """
        Check if the hotkey conflicts with any existing hotkeys.

        Parameters
        ----------
        hotkey : str
            The hotkey to check for conflicts

        Returns
        -------
        str | None
            None if no conflict, or the name of the conflicting instruction set if there is a conflict
        """
        conflicting_set = self._instruction_sets_manager.find_set_by_hotkey(hotkey=hotkey)
        if conflicting_set:
            return conflicting_set.name
        return None

    def validate_hotkey(self) -> bool:
        """
        Validate the current hotkey.

        Returns
        -------
        bool
            True if the hotkey is valid, False otherwise
        """
        # Empty hotkey is valid (means no hotkey assigned)
        if not self._hotkey:
            return True

        # Parse with the KeyFormatter to ensure it's a valid format
        parsed_hotkey = self._keyboard_manager.parse_hotkey_string(hotkey_string=self._hotkey)
        if parsed_hotkey is None:
            self.validation_failed.emit(self._label_manager.invalid_hotkey_format_message.format(hotkey=self._hotkey))
            return False

        # Check for conflicts if a checker function is provided
        if self._hotkey != self._original_hotkey:
            conflicting_set_name = self._check_hotkey_conflict(hotkey=self._hotkey)
            if conflicting_set_name:
                self.validation_failed.emit(
                    self._label_manager.hotkey_already_used_message.format(hotkey=self._hotkey, conflicting_set_name=conflicting_set_name)
                )
                return False
        return True

    def reset(self) -> None:
        """
        Reset the hotkey to empty.
        """
        self.set_hotkey(value="")

    def restore_original(self) -> None:
        """
        Restore the original hotkey value.
        """
        self.set_hotkey(value=self._original_hotkey)

    def save(self) -> None:
        """
        Save the current hotkey as the new original value.
        """
        self._original_hotkey = self._hotkey
