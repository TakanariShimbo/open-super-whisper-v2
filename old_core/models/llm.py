"""
LLM Model Data Model

This module provides data structures and utilities for managing OpenAI LLM model data
throughout the application. It centralizes model definitions and provides
a consistent interface for accessing model information.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, ClassVar, Any


@dataclass
class OpenAILLMModel:
    """
    OpenAI LLM model data model.
    
    This class represents an OpenAI LLM (Large Language Model) with its properties
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
        return f"OpenAILLMModel(id='{self.id}', name='{self.name}')"


class OpenAILLMModelManager:
    """
    Manager for OpenAI LLM model data.
    
    This class provides methods to access and manage OpenAI LLM model data.
    It maintains a list of supported models and provides utilities
    for lookup and validation.
    """
    
    # Define supported models
    # This list represents models that are currently available through the OpenAI API
    # Last updated: April 2025
    _SUPPORTED_LLM_MODELS: ClassVar[List[OpenAILLMModel]] = [
        # GPT-4.1 Series
        OpenAILLMModel(
            id="gpt-4.1",
            name="GPT-4.1",
            description="Advanced model with superior coding, instruction following, and 1M token context support",
            performance_tier="advanced",
            supports_image=True,
            is_default=True
        ),
        OpenAILLMModel(
            id="gpt-4o",
            name="GPT-4o",
            description="Versatile omni model with balanced text and image processing capabilities",
            performance_tier="standard",
            supports_image=True
        ),
        # o-Series reasoning models
        # OpenAILLMModel(
        #     id="o3",
        #     name="O3",
        #     description="Premium reasoning model specialized for complex problem-solving and tool use",
        #     performance_tier="premium",
        #     supports_image=True
        # ),
        OpenAILLMModel(
            id="o1",
            name="O1",
            description="Base reasoning model designed for practical problem solving",
            performance_tier="advanced",
            supports_image=True
        )
    ]
    
    # Create a lookup dictionary for efficient access by ID
    _LLM_MODEL_ID_MAP: ClassVar[Dict[str, OpenAILLMModel]] = {
        model.id: model for model in _SUPPORTED_LLM_MODELS
    }
    
    @classmethod
    def get_available_models(cls) -> List[OpenAILLMModel]:
        """
        Get all available supported models.
        
        Returns
        -------
        List[OpenAILLMModel]
            List of all supported models that are currently available.
        """
        return cls._SUPPORTED_LLM_MODELS.copy()
    
    @classmethod
    def find_model_by_id(cls, model_id: str) -> Optional[OpenAILLMModel]:
        """
        Find a model by its ID.
        
        Parameters
        ----------
        model_id : str
            Model ID to look up.
            
        Returns
        -------
        Optional[OpenAILLMModel]
            Model object if found, None otherwise.
        """
        return cls._LLM_MODEL_ID_MAP.get(model_id)
    
    @classmethod
    def get_default_model(cls) -> OpenAILLMModel:
        """
        Get the default model.
        
        Returns
        -------
        OpenAILLMModel
            Default model object.
            
        Notes
        -----
        Returns the first model flagged as default. If no model is flagged as default,
        returns the first model in the list.
        """
        for model in cls._SUPPORTED_LLM_MODELS:
            if model.is_default:
                return model
        # Fallback to first model if no default is marked
        return cls._SUPPORTED_LLM_MODELS[0]
               
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
        model = cls.find_model_by_id(model_id)
        return model.supports_image if model else False

    @classmethod
    def to_api_format(cls) -> List[Dict[str, str]]:
        """
        Convert models to API format.
        
        Returns
        -------
        List[Dict[str, str]]
            List of dictionaries with model information (id, name, description).
            
        Examples
        --------
        >>> OpenAILLMModelManager.to_api_format()
        [{'id': 'gpt-4.1', 'name': 'GPT-4.1', 'description': '...'}, ...]
        """
        return [
            {
                "id": model.id,
                "name": model.name,
                "description": model.description
            }
            for model in cls._SUPPORTED_LLM_MODELS
        ]
