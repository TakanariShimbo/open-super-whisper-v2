"""
LLM Model Data Model

This module provides data structures and utilities for managing LLM model data
throughout the application. It centralizes model definitions and provides
a consistent interface for accessing model information.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any, ClassVar


@dataclass
class LLMModel:
    """
    LLM model data model.
    
    This class represents an LLM (Large Language Model) with its properties
    like ID, name, description, and other metadata.
    
    Attributes
    ----------
    id : str
        Model identifier used for API calls (e.g., "gpt-4-turbo").
    name : str
        Display name (e.g., "GPT-4 Turbo").
    description : str
        Description of the model's capabilities and characteristics.
    performance_tier : str
        Performance category (e.g., "standard", "advanced").
    supports_image : bool
        Whether the model supports image inputs, by default False.
    is_default : bool
        Whether this is the default model, by default False.
    """
    id: str
    name: str
    description: str
    performance_tier: str
    supports_image: bool = False
    is_default: bool = False
    
    def __str__(self) -> str:
        """Return the display name of the model."""
        return self.name
    
    def __repr__(self) -> str:
        """Return a string representation of the model."""
        return f"LLMModel(id='{self.id}', name='{self.name}')"


class LLMModelManager:
    """
    Manager for LLM model data.
    
    This class provides methods to access and manage LLM model data.
    It maintains a list of supported models and provides utilities
    for lookup and validation.
    """
    
    # Define supported models
    # This list represents models that are currently available through the OpenAI API
    _MODELS: ClassVar[List[LLMModel]] = [
        # GPT-4.1 Series
        LLMModel(
            id="gpt-4.1",
            name="GPT-4.1",
            description="Premium model with superior coding, instruction following, and 1M token context support",
            performance_tier="advanced",
            supports_image=True,
            is_default=True
        ),
        LLMModel(
            id="gpt-4o",
            name="GPT-4o",
            description="Versatile omni model with balanced text and image processing capabilities",
            performance_tier="standard",
            supports_image=True
        ),
        # o-Series reasoning models
        # LLMModel(
        #     id="o3",
        #     name="O3",
        #     description="Advanced reasoning model specialized for complex problem-solving and tool use",
        #     performance_tier="premium",
        #     supports_image=True
        # ),
        LLMModel(
            id="o1",
            name="O1",
            description="Base reasoning model designed for practical problem solving",
            performance_tier="advanced",
            supports_image=True
        )
    ]
    
    # Create a lookup dictionary for efficient access by ID
    _MODEL_DICT: ClassVar[Dict[str, LLMModel]] = {
        model.id: model for model in _MODELS
    }
    
    @classmethod
    def get_models(cls) -> List[LLMModel]:
        """
        Get all supported models.
        
        Returns
        -------
        List[LLMModel]
            List of all supported models.
        """
        return cls._MODELS.copy()
    
    @classmethod
    def get_model_by_id(cls, model_id: str) -> Optional[LLMModel]:
        """
        Get a model by its ID.
        
        Parameters
        ----------
        model_id : str
            Model ID to look up.
            
        Returns
        -------
        Optional[LLMModel]
            Model object if found, None otherwise.
        """
        return cls._MODEL_DICT.get(model_id)
    
    @classmethod
    def get_default_model(cls) -> LLMModel:
        """
        Get the default model.
        
        Returns
        -------
        LLMModel
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
    def get_models_by_tier(cls, tier: str) -> List[LLMModel]:
        """
        Get models by performance tier.
        
        Parameters
        ----------
        tier : str
            Performance tier to filter by.
            
        Returns
        -------
        List[LLMModel]
            List of models in the specified tier.
        """
        return [model for model in cls._MODELS if model.performance_tier == tier]
    
    @classmethod
    def supports_image_input(cls, model_id: str) -> bool:
        """
        Check if a model supports image input.
        
        Parameters
        ----------
        model_id : str
            Model ID to check.
            
        Returns
        -------
        bool
            True if the model supports image input, False otherwise.
        """
        model = cls.get_model_by_id(model_id)
        return model.supports_image if model else False
        
    @classmethod
    def to_api_format(cls) -> List[Dict[str, str]]:
        """
        Convert models to API format.
        
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
