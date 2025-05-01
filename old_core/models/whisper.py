"""
OpenAI Whisper Model Data Model

This module provides data structures and utilities for managing OpenAI Whisper model data
throughout the application. It centralizes model definitions and provides
a consistent interface for accessing model information.

Models Evolution:
----------------
- whisper-1: Released in 2022, the original Whisper model with broad language support
- gpt-4o-mini-transcribe: Released in 2024, faster and more efficient model
- gpt-4o-transcribe: Released in 2024, highest accuracy model with enhanced capabilities
"""

from dataclasses import dataclass
from typing import List, Dict, ClassVar, Optional, Union, Any


@dataclass
class OpenAIWhisperModel:
    """
    OpenAI Whisper model data model.
    
    This class represents an OpenAI Whisper transcription model with its properties
    like ID, name, description, and other metadata.
    
    Attributes
    ----------
    id : str
        Model identifier used for API calls (e.g., "gpt-4o-transcribe").
    name : str
        Display name (e.g., "Whisper-1").
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
            OpenAIWhisperModel(id='model_id', name='model_name')
        """
        return f"OpenAIWhisperModel(id='{self.id}', name='{self.name}')"


class OpenAIWhisperModelManager:
    """
    Manager for OpenAI Whisper model data.
    
    This class provides methods to access and manage OpenAI Whisper model data.
    It maintains a list of supported models and provides utilities
    for lookup and validation.
    
    Models are organized by performance tiers:
    - standard: Base level models with good performance and efficiency
    - enhanced: Premium models with higher accuracy and advanced features
    """
    
    # Define supported models
    # This list represents models that are currently available through the OpenAI API
    _SUPPORTED_WHISPER_MODELS: ClassVar[List[OpenAIWhisperModel]] = [
        OpenAIWhisperModel(
            id="gpt-4o-transcribe",
            name="GPT-4o Transcribe",
            description="High-performance transcription model with enhanced accuracy and support for 100+ languages. Best for complex audio with multiple speakers or challenging environments.",
            performance_tier="enhanced",
            is_default=True
        ),
        OpenAIWhisperModel(
            id="gpt-4o-mini-transcribe",
            name="GPT-4o Mini Transcribe",
            description="Lightweight, fast transcription model with good accuracy and broad language support. Ideal for general purpose transcription with faster processing times.",
            performance_tier="standard"
        ),
        OpenAIWhisperModel(
            id="whisper-1",
            name="Whisper-1",
            description="Legacy transcription model with broad language support. Provides reliable transcription for clear audio recordings.",
            performance_tier="standard"
        )
    ]
    
    # Create a lookup dictionary for efficient access by ID
    _WHISPER_MODEL_ID_MAP: ClassVar[Dict[str, OpenAIWhisperModel]] = {
        model.id: model for model in _SUPPORTED_WHISPER_MODELS
    }
    
    @classmethod
    def get_available_models(cls) -> List[OpenAIWhisperModel]:
        """
        Get all supported OpenAI Whisper models.
        
        Returns
        -------
        List[OpenAIWhisperModel]
            List of all supported models.
        """
        return cls._SUPPORTED_WHISPER_MODELS.copy()
    
    @classmethod
    def to_api_format(cls) -> List[Dict[str, str]]:
        """
        Convert models to API format (compatible with the transcriber module).
        
        Returns
        -------
        List[Dict[str, str]]
            List of dictionaries with model information (id, name, description).
        """
        return [
            {
                "id": model.id,
                "name": model.name,
                "description": model.description
            }
            for model in cls._SUPPORTED_WHISPER_MODELS
        ]
