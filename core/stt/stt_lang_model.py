"""
Speech-to-Text Language Model

This module provides data structures for representing language options
in speech-to-text processing throughout the application.
"""

from dataclasses import dataclass


@dataclass
class STTLangModel:
    """
    Speech-to-text language model data.

    This class represents a language with its essential properties for
    speech-to-text processing.

    Attributes
    ----------
    code : str
        ISO 639-1 language code (e.g., "en", "ja").
    name : str
        Display name in English (e.g., "English", "Japanese").
    """

    code: str
    name: str

    def __str__(self) -> str:
        """
        Return the display name of the language.

        Returns
        -------
        str
            The display name of the language.
        """
        return self.name

    def __repr__(self) -> str:
        """
        Return a string representation of the language.

        Returns
        -------
        str
            A string representation of the language in the format:
            STTLangModel(code='lang_code', name='lang_name')
        """
        return f"STTLangModel(code='{self.code}', name='{self.name}')"
