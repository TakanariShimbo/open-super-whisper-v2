"""
API Key Management Model

This module provides functionality for API key validation and management.
"""

from core.api.api_client_factory import APIClientFactory
from ...utils.settings_manager import SettingsManager


class APIKeyModel:
    """
    Model for API key management.
    
    This class encapsulates the functionality related to API key validation,
    storage, and retrieval.
    """
    
    def __init__(self) -> None:
        """
        Initialize the API Key Model.
        """
        self._settings_manager = SettingsManager.instance()
    
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
        return self._settings_manager.get_api_key()
    
    def set_api_key(self, api_key: str) -> None:
        """
        Store an API key.
        
        Parameters
        ----------
        api_key : str
            The API key to store
        """
        self._settings_manager.set_api_key(api_key)
    
    def clear_api_key(self) -> None:
        """
        Clear the stored API key.
        """
        self._settings_manager.clear_api_key()
