"""
API Key Management Model

This module provides functionality for API key validation and management.
"""

from PyQt6.QtCore import QObject

from core.api.api_client_factory import APIClientFactory

from ...manager.settings_manager import SettingsManager


class APIKeyDialogModel(QObject):
    """
    Model for API key dialog.
    
    This class encapsulates the functionality related to API key validation,
    storage, and retrieval.
    """
    
    def __init__(self) -> None:
        """
        Initialize the API Key Model.
        """
        super().__init__()
        
        self._settings_manager = SettingsManager.instance()
        
        # Load current API key
        self._api_key = self._settings_manager.get_api_key()
        
        # Store original value to support cancel operation
        self._original_api_key = self._api_key
    
    def validate_api_key(self, api_key: str) -> bool:
        """
        Validate an API key using the API client factory.
        
        Parameters
        ----------
        api_key : str
            The API key to validate
            
        Returns
        -------
        bool
            True if the API key is valid, False otherwise
        """
        is_successful, _ = APIClientFactory.create_client(api_key)
        return is_successful
    
    def get_api_key(self) -> str:
        """
        Get the current API key value.
        
        Returns
        -------
        str
            The current API key, or an empty string if none is set
        """
        return self._api_key
    
    def set_api_key(self, api_key: str) -> None:
        """
        Set the API key value.
        
        Parameters
        ----------
        api_key : str
            The API key to set
        """
        if self._api_key != api_key:
            self._api_key = api_key
    
    def save_api_key(self) -> None:
        """
        Save current API key to persistent storage.
        """
        self._settings_manager.set_api_key(self._api_key)
        
        # Update original value
        self._original_api_key = self._api_key
    
    def restore_original(self) -> None:
        """
        Restore original API key (cancel changes).
        """
        if self._api_key != self._original_api_key:
            self._api_key = self._original_api_key
