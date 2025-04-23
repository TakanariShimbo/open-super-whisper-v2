"""
Simple Message Dialog Module

This module provides a simplified message dialog for showing various types
of messages like information, warnings, and errors.
"""

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon


class SimpleMessageDialog:
    """
    A utility class for displaying simple message dialogs.
    
    This class provides static methods to show different types of message
    dialogs (information, warning, error) without having to create a
    dialog instance manually each time.
    """
    
    # Message types
    INFO = 0
    WARNING = 1
    ERROR = 2
    
    @staticmethod
    def show_message(parent, title: str, message: str, message_type: int = INFO) -> None:
        """
        Show a message dialog with the specified title, message, and type.
        
        Parameters
        ----------
        parent : QWidget
            The parent widget for the dialog.
        title : str
            The dialog window title.
        message : str
            The message to display.
        message_type : int, optional
            The type of message to show (INFO, WARNING, ERROR), by default INFO.
            
        Returns
        -------
        None
        """
        # Create the dialog
        dialog = QDialog(parent)
        dialog.setWindowTitle(title)
        
        # Set window flags for a modal dialog
        dialog.setWindowFlags(dialog.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
        dialog.setMinimumWidth(350)
        
        # Create the layout
        layout = QVBoxLayout(dialog)
        
        # Create message label
        message_label = QLabel(message)
        message_label.setWordWrap(True)
        layout.addWidget(message_label)
        
        # Create button layout
        button_layout = QHBoxLayout()
        button_layout.addStretch(1)
        
        # Create OK button
        ok_button = QPushButton("OK")
        ok_button.setDefault(True)
        ok_button.clicked.connect(dialog.accept)
        button_layout.addWidget(ok_button)
        
        layout.addLayout(button_layout)
        dialog.setLayout(layout)
        
        # Set window icon based on message type
        if message_type == SimpleMessageDialog.WARNING:
            dialog.setWindowIcon(dialog.style().standardIcon(dialog.style().StandardPixmap.SP_MessageBoxWarning))
        elif message_type == SimpleMessageDialog.ERROR:
            dialog.setWindowIcon(dialog.style().standardIcon(dialog.style().StandardPixmap.SP_MessageBoxCritical))
        else:
            dialog.setWindowIcon(dialog.style().standardIcon(dialog.style().StandardPixmap.SP_MessageBoxInformation))
        
        # Execute the dialog
        dialog.exec()
