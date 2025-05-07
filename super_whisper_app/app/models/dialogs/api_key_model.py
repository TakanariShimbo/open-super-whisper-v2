"""
API Key Management Model

This module provides functionality for API key validation and management.
"""

from PyQt6.QtCore import QSettings

from core.api.api_client_factory import APIClientFactory


class APIKeyModel:
    """
    Model for API key management.
    
    This class encapsulates the functionality related to API key validation,
    storage, and retrieval.
    """
    
    def __init__(self, settings: QSettings) -> None:
        """
        Initialize the API Key Model.
        
        Parameters
        ----------
        settings : QSettings
            Application settings for persistent storage
        """
        self._settings = settings
    
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
        Get the stored API key.
        
        Returns
        -------
        str
            The stored API key, or an empty string if none is stored
        """
        return self._settings.value("api_key", "")
    
    def set_api_key(self, api_key: str) -> None:
        """
        Store an API key.
        
        Parameters
        ----------
        api_key : str
            The API key to store
        """
        self._settings.setValue("api_key", api_key)
        self._settings.sync()
    
    def clear_api_key(self) -> None:
        """
        Clear the stored API key.
        """
        self._settings.remove("api_key")
        self._settings.sync()
    
    def has_valid_api_key(self) -> bool:
        """
        Check if a valid API key is stored.
        
        Returns
        -------
        bool
            True if a valid API key is stored, False otherwise
        """
        api_key = self.get_api_key()
        if not api_key:
            return False
        return self.validate_api_key(api_key)
