"""
LLM Model Data Model

This module provides data structures and utilities for managing LLM model data
throughout the application. It centralizes model definitions and provides
a consistent interface for accessing model information.
"""

from dataclasses import dataclass


@dataclass
class LLMModel:
    """
    LLM model data model.
    
    This class represents a LLM (Large Language Model) with its properties
    like ID, name, description, and other metadata.
    
    Attributes
    ----------
    id : str
        Model identifier used for API calls (e.g., "gpt-4.1").
    name : str
        Display name (e.g., "GPT-4.1").
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
            LLMModel(id='model_id', name='model_name')
        """
        return f"LLMModel(id='{self.id}', name='{self.name}')"
