"""
Hotkey Dialog Model

This module provides the model component for the hotkey dialog,
handling the data and business logic related to hotkey management.
"""

from PyQt6.QtCore import QObject, pyqtSignal

from ...managers.keyboard_manager import KeyboardManager


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
    
    # Define signals
    hotkey_changed = pyqtSignal(str)
    hotkey_captured = pyqtSignal(str)
    validation_failed = pyqtSignal(str)  # error_message
    
    def __init__(self, current_hotkey: str = "") -> None:
        """
        Initialize the HotkeyDialogModel.
        
        Parameters
        ----------
        current_hotkey : str, optional
            Initial hotkey value, by default ""
        """
        super().__init__()
        
        # Store the current and original hotkey values
        self._hotkey = current_hotkey
        self._original_hotkey = current_hotkey
        
        # Create key state tracker for capturing key combinations
        self._keyboard_manager = KeyboardManager.get_instance()
    
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
    
    def start_capturing(self) -> None:
        """
        Start capturing keyboard inputs.
        
        This method activates the key state tracker to monitor key combinations.
        """
        self._keyboard_manager.start_monitoring()
    
    def stop_capturing(self) -> None:
        """
        Stop capturing keyboard inputs.
        
        This method stops the key state tracker from monitoring key combinations.
        """
        self._keyboard_manager.stop_monitoring()
    
    def capture_keys(self) -> None:
        """
        Capture and process the key combination.
        
        This method reads the keys from the key state tracker,
        formats them into a hotkey string, and updates the model.
        """
        # Get the key combination from the tracker
        keys_list = self._keyboard_manager.capture_last_keys()
        
        # If no keys are pressed, don't update
        if not keys_list:
            return
            
        # Create hotkey string (e.g., "ctrl+shift+a")
        hotkey_string = "+".join(keys_list)
        
        # Update the model
        self.set_hotkey(hotkey_string)
        
        # Emit the captured signal
        self.hotkey_captured.emit(hotkey_string)
    
    def validate_hotkey(self, conflict_checker=None) -> bool:
        """
        Validate the current hotkey.
        
        Parameters
        ----------
        conflict_checker : callable, optional
            Function that checks if a hotkey conflicts with existing hotkeys
            Should take a hotkey string and return None if no conflict,
            or a message string if there is a conflict
            
        Returns
        -------
        bool
            True if the hotkey is valid, False otherwise
        """
        # Empty hotkey is valid (means no hotkey assigned)
        if not self._hotkey:
            return True
        
        # Parse with the KeyFormatter to ensure it's a valid format
        parsed_hotkey = self._keyboard_manager.parse_hotkey_string(self._hotkey)
        if parsed_hotkey is None:
            self.validation_failed.emit(f"Invalid hotkey format: {self._hotkey}")
            return False
        
        # Check for conflicts if a checker function is provided
        if conflict_checker and self._hotkey != self._original_hotkey:
            conflict_message = conflict_checker(self._hotkey)
            if conflict_message:
                self.validation_failed.emit(conflict_message)
                return False
        return True
    
    def reset(self) -> None:
        """
        Reset the hotkey to empty.
        """
        self.set_hotkey("")
    
    def restore_original(self) -> None:
        """
        Restore the original hotkey value.
        
        This is typically used when canceling changes.
        """
        self.set_hotkey(self._original_hotkey)
    
    def save(self) -> None:
        """
        Save the current hotkey as the new original value.
        
        This is typically called when changes are accepted.
        """
        self._original_hotkey = self._hotkey
