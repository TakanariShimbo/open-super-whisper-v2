"""
Whisper Model Data Model

This module provides data structures and utilities for managing Whisper model data
throughout the application. It centralizes model definitions and provides
a consistent interface for accessing model information.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any, ClassVar


@dataclass
class WhisperModel:
    """
    Whisper model data model.
    
    This class represents a Whisper transcription model with its properties
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
        """Return the display name of the model."""
        return self.name
    
    def __repr__(self) -> str:
        """Return a string representation of the model."""
        return f"WhisperModel(id='{self.id}', name='{self.name}')"


class WhisperModelManager:
    """
    Manager for Whisper model data.
    
    This class provides methods to access and manage Whisper model data.
    It maintains a list of supported models and provides utilities
    for lookup and validation.
    """
    
    # Define supported models
    # This list represents models that are currently available through the OpenAI API
    _MODELS: ClassVar[List[WhisperModel]] = [
        WhisperModel(
            id="gpt-4o-transcribe",
            name="GPT-4o Transcribe",
            description="High-performance transcription model with enhanced accuracy",
            performance_tier="enhanced",
            is_default=True
        ),
        WhisperModel(
            id="gpt-4o-mini-transcribe",
            name="GPT-4o Mini Transcribe",
            description="Lightweight, fast transcription model with good accuracy",
            performance_tier="standard"
        ),
        WhisperModel(
            id="whisper-1",
            name="Whisper-1",
            description="Legacy transcription model with broad language support",
            performance_tier="standard"
        )
    ]
    
    # Create a lookup dictionary for efficient access by ID
    _MODEL_DICT: ClassVar[Dict[str, WhisperModel]] = {
        model.id: model for model in _MODELS
    }
    
    @classmethod
    def get_models(cls) -> List[WhisperModel]:
        """
        Get all supported models.
        
        Returns
        -------
        List[WhisperModel]
            List of all supported models.
        """
        return cls._MODELS.copy()
    
    @classmethod
    def get_model_by_id(cls, model_id: str) -> Optional[WhisperModel]:
        """
        Get a model by its ID.
        
        Parameters
        ----------
        model_id : str
            Model ID to look up.
            
        Returns
        -------
        Optional[WhisperModel]
            Model object if found, None otherwise.
        """
        return cls._MODEL_DICT.get(model_id)
    
    @classmethod
    def get_default_model(cls) -> WhisperModel:
        """
        Get the default model.
        
        Returns
        -------
        WhisperModel
            Default model object.
        """
        for model in cls._MODELS:
            if model.is_default:
                return model
        # Fallback to first model if no default is marked
        return cls._MODELS[0]
    
    @classmethod
    def is_valid_id(cls, model_id: str) -> bool:
        """
        Check if a model ID is valid.
        
        Parameters
        ----------
        model_id : str
            Model ID to validate.
            
        Returns
        -------
        bool
            True if the ID is valid, False otherwise.
        """
        return model_id in cls._MODEL_DICT
    
    @classmethod
    def get_model_display_name(cls, model_id: str) -> str:
        """
        Get the display name for a model ID.
        
        Parameters
        ----------
        model_id : str
            Model ID.
            
        Returns
        -------
        str
            Display name of the model, or "Unknown" if not found.
        """
        model = cls.get_model_by_id(model_id)
        return model.name if model else "Unknown"
    
    @classmethod
    def get_models_by_tier(cls, tier: str) -> List[WhisperModel]:
        """
        Get models by performance tier.
        
        Parameters
        ----------
        tier : str
            Performance tier to filter by.
            
        Returns
        -------
        List[WhisperModel]
            List of models in the specified tier.
        """
        return [model for model in cls._MODELS if model.performance_tier == tier]
    
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
            for model in cls._MODELS
        ]
