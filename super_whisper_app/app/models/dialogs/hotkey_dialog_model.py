"""
Hotkey Dialog Model

This module provides the model component for the hotkey dialog, handling the data
and business logic related to hotkey management.
"""

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QKeySequence


class HotkeyDialogModel(QObject):
    """
    Model for the hotkey dialog.
    
    This class handles the data and business logic for the hotkey dialog,
    including storing the current hotkey, validating inputs, and managing state.
    
    Attributes
    ----------
    hotkey_changed : pyqtSignal
        Signal emitted when the hotkey is changed
    hotkey_valid : pyqtSignal
        Signal emitted when a hotkey is validated
    hotkey_invalid : pyqtSignal
        Signal emitted when a hotkey is invalid
    """
    
    # Define signals for controller communication
    hotkey_changed = pyqtSignal(str)
    hotkey_valid = pyqtSignal(str)
    hotkey_invalid = pyqtSignal(str, str)  # hotkey, error_message
    
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
    
    @property
    def hotkey(self) -> str:
        """
        Get the current hotkey.
        
        Returns
        -------
        str
            The current hotkey as a string.
        """
        return self._hotkey
    
    @hotkey.setter
    def hotkey(self, value: str) -> None:
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
    def original_hotkey(self) -> str:
        """
        Get the original hotkey value.
        
        Returns
        -------
        str
            The original hotkey as a string.
        """
        return self._original_hotkey
    
    def reset(self) -> None:
        """
        Reset the hotkey to empty.
        """
        self.hotkey = ""
    
    def restore_original(self) -> None:
        """
        Restore the original hotkey value.
        """
        self.hotkey = self._original_hotkey
    
    def validate_hotkey(self) -> bool:
        """
        Validate the current hotkey.
        
        Returns
        -------
        bool
            True if the hotkey is valid, False otherwise
        """
        # Check if the hotkey is empty
        if not self._hotkey:
            self.hotkey_invalid.emit("", "Hotkey cannot be empty.")
            return False
        
        # Check for valid key sequence (optional, can be extended)
        try:
            # Try to parse the hotkey string as a QKeySequence
            # This validates that it's a valid key sequence format
            sequence = QKeySequence(self._hotkey)
            if sequence.isEmpty():
                self.hotkey_invalid.emit(self._hotkey, "Invalid hotkey sequence.")
                return False
        except Exception as e:
            self.hotkey_invalid.emit(self._hotkey, f"Invalid hotkey format: {str(e)}")
            return False
        
        # Hotkey is valid
        self.hotkey_valid.emit(self._hotkey)
        return True
    
    def create_hotkey_string(self, key: int, modifiers: int) -> str:
        """
        Create a hotkey string from key and modifiers.
        
        Parameters
        ----------
        key : int
            The key code
        modifiers : int
            The modifier flags
            
        Returns
        -------
        str
            The hotkey string in the format "modifier1+modifier2+key"
        """
        # This is simplified from the original implementation
        from PyQt6.QtCore import Qt
        
        parts = []
        
        # Add modifiers
        if modifiers & Qt.KeyboardModifier.ControlModifier:
            parts.append("ctrl")
        
        if modifiers & Qt.KeyboardModifier.AltModifier:
            parts.append("alt")
        
        if modifiers & Qt.KeyboardModifier.ShiftModifier:
            parts.append("shift")
        
        if modifiers & Qt.KeyboardModifier.MetaModifier:
            parts.append("meta")
        
        # Add the key itself
        key_text = QKeySequence(key).toString().lower()
        
        # Only add if it's not already included in the modifiers
        if key_text not in parts:
            parts.append(key_text)
        
        # Create hotkey string
        return "+".join(parts)
