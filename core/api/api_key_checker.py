"""
API Key Checker Module

This module provides functionality for checking if an API key is valid.
"""

import openai
import anthropic
from google import genai


class APIKeyChecker:
    """
    Class for checking if an API key is valid.

    This class provides a method to check if an API key is valid.

    Examples
    --------
    Checking an OpenAI API key:

    >>> is_valid = APIChecker.check_openai_api_key("your_openai_api_key")
    >>> if is_valid:
    ...     print("API key is valid")
    ... else:
    ...     print("API key is invalid")
    """

    @staticmethod
    def check_openai_api_key(openai_api_key: str) -> bool:
        """
        Check if an OpenAI API key is valid.

        Parameters
        ----------
        openai_api_key : str
            The OpenAI API key to check.

        Returns
        -------
        bool
            True if the API key is valid, False otherwise
        """
        try:
            # Create the client
            client = openai.OpenAI(api_key=openai_api_key)

            # Verify the client works by listing models
            client.models.list()

            return True
        except Exception:
            return False

    @staticmethod
    def check_anthropic_api_key(anthropic_api_key: str) -> bool:
        """
        Check if an Anthropic API key is valid.

        Parameters
        ----------
        anthropic_api_key : str
            The Anthropic API key to check.

        Returns
        -------
        bool
            True if the API key is valid, False otherwise
        """
        try:
            # Create the client
            client = anthropic.Anthropic(api_key=anthropic_api_key)
            
            # Verify the client works by listing models
            client.models.list()
            
            return True
        except Exception:
            return False

    @staticmethod
    def check_gemini_api_key(gemini_api_key: str) -> bool:
        """
        Check if a Gemini API key is valid.

        Parameters
        ----------
        gemini_api_key : str
            The Gemini API key to check.

        Returns
        -------
        bool
            True if the API key is valid, False otherwise
        """
        try:
            # Configure the API key
            client = genai.Client(api_key=gemini_api_key)
            
            # List models to verify API key
            client.models.list()

            return True
        except Exception:
            return False
