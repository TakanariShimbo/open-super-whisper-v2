"""
LLM Model Manager

This module provides functionality for managing LLM model information,
including model selection, validation, and information retrieval.
"""

from typing import ClassVar

from .llm_model import LLMModel


class LLMModelManager:
    """
    Manager for LLM model data.

    This class provides methods to access and manage LLM model data.
    It maintains a list of supported models and provides utilities
    for lookup and validation.
    """

    # Define supported models
    # This list represents models that are currently available through the API
    # Last updated: April 2025
    _SUPPORTED_LLM_MODELS: ClassVar[list[LLMModel]] = [
        # GPT-4 Series
        LLMModel(
            id="gpt-4.1",
            name="GPT-4.1",
            description="Advanced model with superior coding, instruction following, and 1M token context support",
            performance_tier="advanced",
            supports_image=True,
            is_default=True,
        ),
        LLMModel(
            id="gpt-4o",
            name="GPT-4o",
            description="Versatile omni model with balanced text and image processing capabilities",
            performance_tier="standard",
            supports_image=True,
        ),
        # o-Series reasoning models
        LLMModel(
            id="o3",
            name="O3",
            description="Advanced reasoning model designed for practical problem solving",
            performance_tier="advanced",
            supports_image=True,
        ),
        LLMModel(
            id="o1",
            name="O1",
            description="Base reasoning model designed for practical problem solving",
            performance_tier="advanced",
            supports_image=True,
        ),
    ]

    # Create a lookup dictionary for efficient access by ID
    _LLM_MODEL_ID_MAP: ClassVar[dict[str, LLMModel]] = {model.id: model for model in _SUPPORTED_LLM_MODELS}

    @classmethod
    def get_available_models(cls) -> list[LLMModel]:
        """
        Get all available supported models.

        Returns
        -------
        list[LLMModel]
            List of all supported models that are currently available.
        """
        return cls._SUPPORTED_LLM_MODELS.copy()

    @classmethod
    def find_model_by_id(cls, model_id: str) -> LLMModel | None:
        """
        Find a model by its ID.

        Parameters
        ----------
        model_id : str
            Model ID to look up.

        Returns
        -------
        LLMModel | None
            Model object if found, None otherwise.
        """
        return cls._LLM_MODEL_ID_MAP.get(model_id)

    @classmethod
    def get_default_model(cls) -> LLMModel:
        """
        Get the default model.

        Returns
        -------
        LLMModel
            The default model.

        Raises
        ------
        ValueError
            If no default model is found.
        """
        for model in cls._SUPPORTED_LLM_MODELS:
            if model.is_default:
                return model
        raise ValueError("No default model found")

    @classmethod
    def check_image_input_supported(cls, model_id: str) -> bool:
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
        model = cls.find_model_by_id(model_id=model_id)
        return model.supports_image if model else False

    @classmethod
    def to_api_format(cls) -> list[dict[str, str]]:
        """
        Convert models to API format.

        Returns
        -------
        list[dict[str, str]]
            List of dictionaries with model information (id, name, description).

        Examples
        --------
        >>> LLMModelManager.to_api_format()
        [{'id': 'gpt-4.1', 'name': 'GPT-4.1', 'description': '...'}, ...]
        """
        return [
            {
                "id": model.id,
                "name": model.name,
                "description": model.description,
            }
            for model in cls._SUPPORTED_LLM_MODELS
        ]
