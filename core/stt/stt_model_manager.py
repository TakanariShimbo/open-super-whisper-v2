"""
Speech-to-Text Model Manager

This module provides functionality for managing speech-to-text model information,
including model selection, validation, and information retrieval.
"""

from typing import ClassVar

from .stt_model import STTModel


class STTModelManager:
    """
    Manager for speech-to-text model data.
    
    This class provides methods to access and manage speech-to-text model data.
    It maintains a list of supported models and provides utilities
    for lookup and validation.
    
    Models are organized by performance tiers:
    - standard: Base level models with good performance and efficiency
    - enhanced: Premium models with higher accuracy and advanced features
    """
    
    # Define supported models
    # This list represents models that are currently available through the API
    _SUPPORTED_STT_MODELS: ClassVar[list[STTModel]] = [
        STTModel(
            id="gpt-4o-transcribe",
            name="GPT-4o Transcribe",
            description="High-performance transcription model with enhanced accuracy and support for 100+ languages. Best for complex audio with multiple speakers or challenging environments.",
            performance_tier="enhanced",
            is_default=True
        ),
        STTModel(
            id="gpt-4o-mini-transcribe",
            name="GPT-4o Mini Transcribe",
            description="Lightweight, fast transcription model with good accuracy and broad language support. Ideal for general purpose transcription with faster processing times.",
            performance_tier="standard"
        ),
        STTModel(
            id="whisper-1",
            name="Whisper-1",
            description="Legacy transcription model with broad language support. Provides reliable transcription for clear audio recordings.",
            performance_tier="standard"
        )
    ]
    
    # Create a lookup dictionary for efficient access by ID
    _STT_MODEL_ID_MAP: ClassVar[dict[str, STTModel]] = {
        model.id: model for model in _SUPPORTED_STT_MODELS
    }
    
    @classmethod
    def get_available_models(cls) -> list[STTModel]:
        """
        Get all supported speech-to-text models.
        
        Returns
        -------
        list[STTModel]
            List of all supported models.
        """
        return cls._SUPPORTED_STT_MODELS.copy()
    
    @classmethod
    def get_default_model(cls) -> STTModel:
        """
        Get the default model.

        Returns
        -------
        STTModel
            The default model.

        Raises
        ------
        ValueError
            If no default model is found.
        """
        for model in cls._SUPPORTED_STT_MODELS:
            if model.is_default:
                return model
        raise ValueError("No default model found")
    
    @classmethod
    def to_api_format(cls) -> list[dict[str, str]]:
        """
        Convert models to API format.
        
        Returns
        -------
        list[dict[str, str]]
            List of dictionaries with model information (id, name, description).
        """
        return [
            {
                "id": model.id,
                "name": model.name,
                "description": model.description
            }
            for model in cls._SUPPORTED_STT_MODELS
        ]
