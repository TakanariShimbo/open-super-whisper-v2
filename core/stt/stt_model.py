"""
Speech-to-Text Model Data Model

This module provides data structures and utilities for managing speech-to-text model data
throughout the application. It centralizes model definitions and provides
a consistent interface for accessing model information.
"""

from dataclasses import dataclass


@dataclass
class STTModel:
    """
    Speech-to-text model data model.

    This class represents a speech-to-text transcription model with its properties
    like ID, name, description, and other metadata.

    Attributes
    ----------
    id : str
        Model identifier used for API calls (e.g., "gpt-4o-transcribe").
    name : str
        Display name (e.g., "GPT-4o Transcribe").
    description : str
        Description of the model's capabilities and characteristics.
    performance_tier : str
        Performance category (e.g., "standard", "enhanced").
    is_default : bool
        Whether this is the default model, by default False.
    """

    id: str
    name: str
    description: str
    performance_tier: str
    is_default: bool = False

    def __str__(self) -> str:
        """
        Return the display name of the model.

        Returns
        -------
        str
            The display name of the model.
        """
        return self.name

    def __repr__(self) -> str:
        """
        Return a string representation of the model.

        Returns
        -------
        str
            A string representation of the model in the format:
            STTModel(id='model_id', name='model_name')
        """
        return f"STTModel(id='{self.id}', name='{self.name}')"
