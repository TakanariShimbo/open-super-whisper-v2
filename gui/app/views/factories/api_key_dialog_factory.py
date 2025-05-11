"""
API Key Dialog Factory

This module provides a factory for creating API key dialog instances,
following the factory design pattern to centralize dialog creation logic.
"""

from ..dialogs.api_key_dialog import APIKeyDialog


class APIKeyDialogFactory:
    """
    Factory class for creating API key dialog instances.
    
    This class provides methods to create properly configured API key
    dialog instances with their controllers, following the MVC pattern.
    """
    
    @staticmethod
    def _create_dialog(parent=None, initial_message=None) -> APIKeyDialog:
        """
        Create a generic API key dialog instance.
        
        This method creates a new API key dialog with its controller,
        properly configured and ready to use.
        
        Parameters
        ----------
        parent : QWidget, optional
            Parent widget for the dialog, by default None
        initial_message : str, optional
            Initial message to display in the dialog, by default None
            
        Returns
        -------
        APIKeyDialog
            The created API key dialog instance
        """        
        # Create an API key dialog
        dialog = APIKeyDialog(parent, initial_message)
        
        return dialog
    
    @classmethod
    def create_initial_dialog(cls, parent=None) -> APIKeyDialog:
        """
        Create an API key dialog for initial application setup.
        
        This method creates a dialog with appropriate messages for first-time
        setup when no API key is available.
        
        Parameters
        ----------
        parent : QWidget, optional
            Parent widget for the dialog, by default None
            
        Returns
        -------
        APIKeyDialog
            The created API key dialog instance
        """
        initial_message = "Welcome to Open Super Whisper! Please enter your OpenAI API key to get started."
        return cls._create_dialog(parent, initial_message)
    
    @classmethod
    def create_settings_dialog(cls, parent=None) -> APIKeyDialog:
        """
        Create an API key dialog for settings/update.
        
        This method creates a dialog with appropriate messages for updating
        an existing API key from the settings menu.
        
        Parameters
        ----------
        parent : QWidget, optional
            Parent widget for the dialog, by default None
            
        Returns
        -------
        APIKeyDialog
            The created API key dialog instance
        """
        initial_message = "Update your API key or enter a new one if needed."
        return cls._create_dialog(parent, initial_message)
