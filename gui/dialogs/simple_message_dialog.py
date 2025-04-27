"""
Simple Message Dialog

This module provides a simple message dialog for displaying information,
warnings, and errors to the user with thread-safe implementation.
"""

from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import Qt


class SimpleMessageDialog:
    """
    Simple message dialog utility.
    
    This class provides static methods to show various types of message
    dialogs (information, warning, error) to the user.
    
    Thread Safety:
    --------------
    All dialog operations are executed in the main/UI thread using
    ThreadManager.run_in_main_thread when thread_manager is provided.
    Without thread_manager, methods operate synchronously in the calling thread.
    """
    
    # Message types
    INFO = QMessageBox.Icon.Information
    WARNING = QMessageBox.Icon.Warning
    ERROR = QMessageBox.Icon.Critical
    
    @staticmethod
    def show_message(parent, title, message, icon=QMessageBox.Icon.Information, thread_manager=None):
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
        thread_manager : ThreadManager, optional
            Thread manager for thread-safe operation. If provided, ensures the dialog
            is shown in the main/UI thread.
            
        Returns
        -------
        int
            QMessageBox dialog result (only when not using thread_manager).
        """
        # Define the actual dialog function
        def _show_dialog():
            msg_box = QMessageBox(parent)
            msg_box.setWindowTitle(title)
            msg_box.setText(message)
            msg_box.setIcon(icon)
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            return msg_box.exec()
        
        # Use thread manager if provided, otherwise execute directly
        if thread_manager:
            # Execute in the main thread
            thread_manager.run_in_main_thread(_show_dialog)
            return None  # Can't return result when using thread_manager
        else:
            # Execute directly (should only be called from main thread)
            return _show_dialog()
    
    @staticmethod
    def show_confirmation(parent, title, message, default_yes=True, thread_manager=None):
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
        thread_manager : ThreadManager, optional
            Thread manager for thread-safe operation. If provided, ensures the dialog
            is shown in the main/UI thread and returns the result via callback.
            
        Returns
        -------
        bool
            True if "Yes" was clicked, False otherwise.
            (Only when not using thread_manager)
        """
        # Define the actual dialog function
        def _show_confirmation():
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
        
        # Use thread manager if provided, otherwise execute directly
        if thread_manager:
            # Execute in the main thread
            thread_manager.run_in_main_thread(_show_confirmation)
            return None  # Can't return result when using thread_manager
        else:
            # Execute directly (should only be called from main thread)
            return _show_confirmation()
    
    @staticmethod
    def show_message_async(parent, title, message, callback=None, icon=QMessageBox.Icon.Information, thread_manager=None):
        """
        Show a message dialog asynchronously with optional callback for the result.
        
        Parameters
        ----------
        parent : QWidget
            Parent widget for the dialog.
        title : str
            Dialog title.
        message : str
            Message to display.
        callback : callable, optional
            Function to call with the dialog result.
        icon : QMessageBox.Icon, optional
            Icon to show, by default QMessageBox.Icon.Information
        thread_manager : ThreadManager, optional
            Thread manager for thread-safe operation. If not provided, falls back to
            synchronous show_message method.
        """
        if not thread_manager:
            # Fall back to synchronous method
            result = SimpleMessageDialog.show_message(parent, title, message, icon)
            if callback:
                callback(result)
            return
            
        # Define the dialog function with callback
        def _show_dialog_async():
            msg_box = QMessageBox(parent)
            msg_box.setWindowTitle(title)
            msg_box.setText(message)
            msg_box.setIcon(icon)
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            result = msg_box.exec()
            
            # Execute callback if provided
            if callback:
                callback(result)
        
        # Execute in the main thread
        thread_manager.run_in_main_thread(_show_dialog_async)
    
    @staticmethod
    def show_confirmation_async(parent, title, message, callback=None, default_yes=True, thread_manager=None):
        """
        Show a confirmation dialog asynchronously with optional callback for the result.
        
        Parameters
        ----------
        parent : QWidget
            Parent widget for the dialog.
        title : str
            Dialog title.
        message : str
            Message to display.
        callback : callable, optional
            Function to call with the dialog result (True/False).
        default_yes : bool, optional
            Whether "Yes" is the default button, by default True
        thread_manager : ThreadManager, optional
            Thread manager for thread-safe operation. If not provided, falls back to
            synchronous show_confirmation method.
        """
        if not thread_manager:
            # Fall back to synchronous method
            result = SimpleMessageDialog.show_confirmation(parent, title, message, default_yes)
            if callback:
                callback(result)
            return
            
        # Define the dialog function with callback
        def _show_confirmation_async():
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
            
            result = msg_box.exec() == QMessageBox.StandardButton.Yes
            
            # Execute callback if provided
            if callback:
                callback(result)
        
        # Execute in the main thread
        thread_manager.run_in_main_thread(_show_confirmation_async)
