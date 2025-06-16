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

    _SUPPORTED_LLM_MODELS: ClassVar[list[LLMModel]] = [
        #
        # OpenAI
        #
        LLMModel(
            id="gpt-4.1",
            name="GPT-4.1",
            description="Advanced model with superior coding, instruction following, and 1M token context support",
            performance_tier="advanced",
            provider="openai",
            supports_image=True,
            supports_web_search=True,
            supports_mcp_servers=True,
            is_default=True,
        ),
        LLMModel(
            id="gpt-4o",
            name="GPT-4o",
            description="Versatile omni model with balanced text and image processing capabilities",
            performance_tier="standard",
            provider="openai",
            supports_image=True,
            supports_web_search=True,
            supports_mcp_servers=True,
        ),
        LLMModel(
            id="o3",
            name="O3",
            description="Advanced reasoning model designed for practical problem solving",
            performance_tier="advanced",
            provider="openai",
            supports_image=True,
            supports_web_search=False,
            supports_mcp_servers=True,
        ),
        LLMModel(
            id="o1",
            name="O1",
            description="Base reasoning model designed for practical problem solving",
            performance_tier="advanced",
            provider="openai",
            supports_image=True,
            supports_web_search=False,
            supports_mcp_servers=True,
        ),
        #
        # Anthropic
        #
        LLMModel(
            id="litellm/anthropic/claude-opus-4-20250514",
            name="Claude 4 Opus",
            description="Most capable and intelligent Claude model, setting new standards in complex reasoning",
            performance_tier="advanced",
            provider="anthropic",
            supports_image=True,
            supports_web_search=False,
            supports_mcp_servers=True,
        ),
        LLMModel(
            id="litellm/anthropic/claude-sonnet-4-20250514",
            name="Claude 4 Sonnet",
            description="High-performance model with exceptional reasoning and efficiency",
            performance_tier="standard",
            provider="anthropic",
            supports_image=True,
            supports_web_search=False,
            supports_mcp_servers=True,
        ),
        #
        # Gemini
        #
        LLMModel(
            id="litellm/gemini/gemini-2.5-pro-preview-06-05",
            name="Gemini 2.5 Pro",
            description="Most intelligent Gemini model",
            performance_tier="advanced",
            provider="gemini",
            supports_image=True,
            supports_web_search=False,
            supports_mcp_servers=True,
        ),
        LLMModel(
            id="litellm/gemini/gemini-2.5-flash-preview-05-20",
            name="Gemini 2.5 Flash",
            description="Fast Gemini model",
            performance_tier="standard",
            provider="gemini",
            supports_image=True,
            supports_web_search=False,
            supports_mcp_servers=True,
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
    def check_web_search_supported(cls, model_id: str) -> bool:
        """
        Check if a model supports web search.

        Parameters
        ----------
        model_id : str
            Model ID to check.

        Returns
        -------
        bool
            True if the model supports web search, False otherwise.
        """
        model = cls.find_model_by_id(model_id=model_id)
        return model.supports_web_search if model else False
    
    @classmethod
    def check_mcp_servers_supported(cls, model_id: str) -> bool:
        """
        Check if a model supports MCP servers.

        Parameters
        ----------
        model_id : str
            Model ID to check.

        Returns
        -------
        bool
            True if the model supports MCP servers, False otherwise.
        """
        model = cls.find_model_by_id(model_id=model_id)
        return model.supports_mcp_servers if model else False

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
