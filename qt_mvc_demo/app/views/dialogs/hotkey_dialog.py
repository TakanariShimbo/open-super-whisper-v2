"""
Hotkey Dialog for Qt MVC Demo

This module provides a dialog for setting the task control hotkey
in the Qt MVC demonstration application.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QDialogButtonBox, QGridLayout, QMessageBox
)
from PyQt6.QtCore import Qt, QEvent
from PyQt6.QtGui import QKeySequence

class HotkeyDialog(QDialog):
    """
    Dialog for setting the task control hotkey.
    
    This dialog allows users to define a custom hotkey combination
    for starting and stopping tasks.
    
    Attributes
    ----------
    hotkey : str
        The current hotkey string
    hotkey_input : QLineEdit
        Input field for displaying and capturing the hotkey
    """
    
    def __init__(self, parent=None, current_hotkey=""):
        """
        Initialize the HotkeyDialog.
        
        Parameters
        ----------
        parent : QWidget, optional
            Parent widget, by default None
        current_hotkey : str, optional
            Current hotkey string, by default ""
        """
        super().__init__(parent)
        
        self.hotkey = current_hotkey
        self.current_keys = set()
        
        # Store original hotkey for safe restoration
        self.original_hotkey = current_hotkey
        
        # Set up UI
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        # Set dialog properties
        self.setWindowTitle("Task Hotkey Setup")
        self.setMinimumWidth(400)
        
        # Create layout
        layout = QVBoxLayout(self)
        
        # Create grid for form
        form_layout = QGridLayout()
        
        # Add description
        description = QLabel(
            "Set a hotkey combination for starting and stopping tasks. "
            "When a task is not running, the hotkey will start a task. "
            "When a task is running, the same hotkey will stop it."
        )
        description.setWordWrap(True)
        
        # Create hotkey input
        hotkey_label = QLabel("Hotkey:")
        self.hotkey_input = QLineEdit(self.hotkey)
        self.hotkey_input.setPlaceholderText("Press key combination...")
        self.hotkey_input.setReadOnly(True)
        
        # Make the input field receive key events
        self.hotkey_input.installEventFilter(self)
        
        # Reset button
        reset_button = QPushButton("Clear")
        reset_button.clicked.connect(self.reset_hotkey)
        
        # Add to grid layout
        form_layout.addWidget(description, 0, 0, 1, 3)
        form_layout.addWidget(hotkey_label, 1, 0)
        form_layout.addWidget(self.hotkey_input, 1, 1)
        form_layout.addWidget(reset_button, 1, 2)
        
        # Add hotkey examples
        examples_label = QLabel("Examples: ctrl+shift+t, alt+x, ctrl+alt+s")
        examples_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        form_layout.addWidget(examples_label, 2, 0, 1, 3)
        
        # Add button box
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        # Add layouts to main layout
        layout.addLayout(form_layout)
        layout.addWidget(button_box)
    
    def eventFilter(self, obj, event):
        """
        Event filter to capture key presses.
        
        Parameters
        ----------
        obj : QObject
            Object that received the event.
        event : QEvent
            Event that was received.
            
        Returns
        -------
        bool
            Whether the event was handled.
        """
        if obj == self.hotkey_input and event.type() == QEvent.Type.KeyPress:
            self.handle_key_press(event)
            return True
        
        return super().eventFilter(obj, event)
    
    def handle_key_press(self, event):
        """
        Handle key press events.
        
        Parameters
        ----------
        event : QKeyEvent
            Key press event.
        """
        # Ignore standalone modifier keys (Ctrl, Alt, Shift)
        key = event.key()
        if key in (Qt.Key.Key_Control, Qt.Key.Key_Alt, Qt.Key.Key_Shift, Qt.Key.Key_Meta):
            return
        
        # Get modifier keys
        modifiers = event.modifiers()
        
        # Build hotkey string
        parts = []
        
        if modifiers & Qt.KeyboardModifier.ControlModifier:
            parts.append("ctrl")
        
        if modifiers & Qt.KeyboardModifier.AltModifier:
            parts.append("alt")
        
        if modifiers & Qt.KeyboardModifier.ShiftModifier:
            parts.append("shift")
        
        if modifiers & Qt.KeyboardModifier.MetaModifier:
            parts.append("meta")
        
        # Add the key itself (convert to string)
        key_text = QKeySequence(key).toString().lower()
        
        # Only add if it's not already included in the modifiers
        if key_text not in parts:
            parts.append(key_text)
        
        # Create hotkey string
        hotkey_str = "+".join(parts)
        
        # Update input
        self.hotkey_input.setText(hotkey_str)
        self.hotkey = hotkey_str
    
    def reset_hotkey(self):
        """Reset the hotkey field."""
        self.hotkey_input.clear()
        self.hotkey = ""
    
    def get_hotkey(self):
        """
        Get the hotkey string.
        
        Returns
        -------
        str
            The hotkey combination as a string.
        """
        return self.hotkey
    
    def accept(self):
        """
        Handle dialog acceptance with validation.
        
        This method is called when the OK button is clicked.
        It validates the hotkey before accepting the dialog.
        """
        # Validate hotkey before accepting
        if not self.hotkey:
            QMessageBox.warning(
                self,
                "Invalid Hotkey",
                "Please define a hotkey combination before confirming.",
                QMessageBox.StandardButton.Ok
            )
            return
        
        # Accept the dialog
        super().accept()
    
    def reject(self):
        """
        Handle dialog rejection.
        
        This method is called when the Cancel button is clicked.
        It restores the original hotkey before rejecting the dialog.
        """
        # Restore original hotkey
        self.hotkey = self.original_hotkey
        
        # Call parent class method
        super().reject()
