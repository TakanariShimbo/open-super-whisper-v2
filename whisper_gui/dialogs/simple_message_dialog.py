"""
Simple Message Dialog

This module provides a simple message dialog for displaying information,
warnings, and errors to the user.
"""

from PyQt6.QtWidgets import QMessageBox


class SimpleMessageDialog:
    """
    Simple message dialog utility.
    
    This class provides static methods to show various types of message
    dialogs (information, warning, error) to the user.
    """
    
    # Message types
    INFO = QMessageBox.Icon.Information
    WARNING = QMessageBox.Icon.Warning
    ERROR = QMessageBox.Icon.Critical
    
    @staticmethod
    def show_message(parent, title, message, icon=QMessageBox.Icon.Information):
        """
        Show a message dialog.
        
        Parameters
        ----------
        parent : QWidget
            Parent widget for the dialog.
        title : str
            Dialog title.
        message : str
            Message to display.
        icon : QMessageBox.Icon, optional
            Icon to show, by default QMessageBox.Icon.Information
            
        Returns
        -------
        int
            QMessageBox dialog result.
        """
        msg_box = QMessageBox(parent)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(icon)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        return msg_box.exec()
    
    @staticmethod
    def show_confirmation(parent, title, message, default_yes=True):
        """
        Show a confirmation dialog with Yes/No buttons.
        
        Parameters
        ----------
        parent : QWidget
            Parent widget for the dialog.
        title : str
            Dialog title.
        message : str
            Message to display.
        default_yes : bool, optional
            Whether "Yes" is the default button, by default True
            
        Returns
        -------
        bool
            True if "Yes" was clicked, False otherwise.
        """
        msg_box = QMessageBox(parent)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Icon.Question)
        msg_box.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if default_yes:
            msg_box.setDefaultButton(QMessageBox.StandardButton.Yes)
        else:
            msg_box.setDefaultButton(QMessageBox.StandardButton.No)
        
        return msg_box.exec() == QMessageBox.StandardButton.Yes
