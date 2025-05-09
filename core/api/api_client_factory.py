"""
API Client Factory Module

This module provides functionality for creating API clients.
It centralizes the client creation logic to avoid code duplication across
different components that need to interact with external APIs.
"""

import openai


class APIClientFactory:
    """
    Factory class for API client creation.
    
    This class provides static methods to create API clients with
    proper error handling for connection issues.
    
    Examples
    --------
    Creating an API client:
    
    >>> is_successful, client = APIClientFactory.create_client("your_api_key")
    >>> if is_successful:
    ...     print("Client created successfully!")
    ...     # Use the client for API calls
    ... else:
    ...     print("Failed to create client")
    """
    
    @staticmethod
    def create_client(api_key: str) -> tuple[bool, openai.OpenAI | None]:
        """
        Create an API client with the provided API key.
        
        Parameters
        ----------
        api_key : str
            The API key to use for client creation.
            
        Returns
        -------
        Tuple[bool, openai.OpenAI | None]
            A tuple containing:
            - Boolean indicating if the client was created successfully
            - Client object if successful, None otherwise
        """
        try:
            # Create the client
            client = openai.OpenAI(api_key=api_key)
            
            # Verify the client works by listing models
            client.models.list()
            
            # Return success and the client
            return True, client
        except Exception:
            # Any exception indicates an issue with client creation
            return False, None
