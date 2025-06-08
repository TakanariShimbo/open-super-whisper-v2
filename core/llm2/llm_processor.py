"""
LLM Processing Module

This module provides a complete implementation for processing text using the LLM API,
with support for:
- Text and image inputs
- Streaming and non-streaming responses
- Custom system instructions
- Multiple model support
- Comprehensive error handling

The primary class (LLMProcessor) handles all communication with the LLM API,
including authentication, request formatting, and response processing.
"""

import base64
import time
from typing import Any, Callable

import openai

from .llm_model_manager import LLMModelManager


class LLMProcessor:
    """
    Implementation of API for processing text and images with large language models.

    This class provides a comprehensive interface to LLM capabilities with:
    - Text and multimodal (text+image) input support
    - Both streaming and non-streaming response options
    - Customizable system instructions for controlling model behavior
    - Support for all available chat completion models
    - Robust error handling for API-specific errors

    The processor handles all aspects of communication with the API including
    authentication, content formatting, and response processing. It provides both
    direct methods for immediate use and generator-based methods for more
    advanced integration scenarios.

    Examples
    --------
    Basic text processing:

    >>> from core.api.api_client_factory import APIClientFactory
    >>> is_successful, client = APIClientFactory.create_client("your_api_key")
    >>> processor = LLMProcessor(client)
    >>> response = processor.process_text("Summarize the benefits of AI assistants.")
    >>> print(response)
    AI assistants offer several benefits: 1. 24/7 availability...

    With custom system instruction:

    >>> from core.api.api_client_factory import APIClientFactory
    >>> is_successful, client = APIClientFactory.create_client("your_api_key")
    >>> processor = LLMProcessor(client)
    >>> processor.set_system_instruction("Respond in bullet points format.")
    >>> response = processor.process_text("What are the key features of Python?")
    >>> print(response)
    • Dynamic typing
    • Interpreted language
    • Extensive standard library
    • ...

    Streaming response with callback:

    >>> def print_chunk(chunk):
    ...     print(chunk, end="", flush=True)
    >>>
    >>> from core.api.api_client_factory import APIClientFactory
    >>> is_successful, client = APIClientFactory.create_client("your_api_key")
    >>> processor = LLMProcessor(client)
    >>> processor.process_text_with_stream(
    ...     "Explain quantum computing",
    ...     callback=print_chunk
    ... )
    Quantum computing is a type of computing that...
    """

    # Use model manager for available models
    AVAILABLE_MODELS = LLMModelManager.to_api_format()
    DEFAULT_MODEL_ID = LLMModelManager.get_default_model().id
    REQUEST_TIMEOUT = 60  # seconds
    MAX_RETRIES = 2

    def __init__(self, client: openai.OpenAI) -> None:
        """
        Initialize the LLMProcessor.

        Parameters
        ----------
        client : openai.OpenAI
            API client to use.
        """
        self._client = client
        self._model_id = self.DEFAULT_MODEL_ID
        self._system_instruction: str = ""

    def set_model(self, model_id: str) -> None:
        """
        Set the LLM model to use.

        Parameters
        ----------
        model_id : str
            Model ID to use for processing.

        Raises
        ------
        ValueError
            If the model ID is not in the list of available models.
        """
        # Basic validation that model exists
        available_models = [model["id"] for model in self.AVAILABLE_MODELS]
        if model_id not in available_models:
            available_model_names = ", ".join(available_models[:5]) + "..."
            raise ValueError(f"Unknown model ID: {model_id}. Available models include: {available_model_names}")

        self._model_id = model_id

    def set_system_instruction(self, instruction: str) -> None:
        """
        Set system instruction to control LLM behavior.

        Parameters
        ----------
        instruction : str
            Instruction string.
        """
        self._system_instruction = instruction

    def clear_system_instruction(self) -> None:
        """
        Clear the system instruction.
        """
        self._system_instruction = ""

    def _create_llm_system_message(self) -> str:
        """
        Get the system message with instruction for the LLM.

        Returns
        -------
        str
            System message, or a default message if no instruction exists.
        """
        if not self._system_instruction:
            return "You are a helpful assistant."

        return self._system_instruction

    def _format_user_content(
        self,
        text: str,
        image_data: bytes | None = None,
    ) -> list[dict[str, Any]]:
        """
        Format user content into the structure required by the API, including optional image data.

        Parameters
        ----------
        text : str
            Text to process.
        image_data : bytes | None, optional
            Image data in bytes format, by default None.

        Returns
        -------
        list[dict[str, Any]]
            Formatted user content for the API.
        """
        if image_data is not None:
            # Convert image bytes to base64 string
            base64_image = base64.b64encode(image_data).decode("utf-8")

            # Create user content with both text and image using the format for GPT-4o
            return [
                {"type": "text", "text": text},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}},
            ]
        else:
            # Text-only content can also use the array format for consistency
            return [
                {"type": "text", "text": text},
            ]

    def _create_api_messages(
        self,
        text: str,
        image_data: bytes | None = None,
    ) -> list[dict[str, Any]]:
        """
        Create formatted messages for API call.

        Parameters
        ----------
        text : str
            Text to process.
        image_data : bytes | None, optional
            Image data in bytes format, by default None.

        Returns
        -------
        list[dict[str, Any]]
            Formatted messages for API call.
        """
        system_message = self._create_llm_system_message()
        user_content = self._format_user_content(text=text, image_data=image_data)

        return [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_content},
        ]

    def _make_api_call(
        self,
        messages: list[dict[str, Any]],
        stream: bool = False,
        retry_count: int = 0,
    ) -> Any:
        """
        Make API call to the LLM service.

        Parameters
        ----------
        messages : list[dict[str, Any]]
            Formatted messages for API call.
        stream : bool, optional
            Whether to stream the response, by default False.
        retry_count : int, optional
            Current retry attempt, by default 0.

        Returns
        -------
        Any
            API response object.

        Raises
        ------
        openai.APIError
            If the API call fails after all retries.
        """
        try:
            # Make the API call
            response = self._client.chat.completions.create(
                model=self._model_id,
                messages=messages,
                stream=stream,
                timeout=self.REQUEST_TIMEOUT,
            )
            return response

        except (openai.APIError, openai.APITimeoutError) as e:
            # Handle retries
            if retry_count < self.MAX_RETRIES:
                # Exponential backoff
                backoff_time = 2**retry_count
                time.sleep(backoff_time)
                return self._make_api_call(
                    messages=messages,
                    stream=stream,
                    retry_count=retry_count + 1,
                )
            else:
                raise

    def _process_standard_response(self, response: Any) -> str:
        """
        Process standard (non-streaming) API response.

        Parameters
        ----------
        response : Any
            API response object.

        Returns
        -------
        str
            Extracted text content from response.
        """
        result = ""
        if response.choices and len(response.choices) > 0:
            result = response.choices[0].message.content
        else:
            result = "No response generated."
        return result

    def _process_streaming_response(
        self,
        response_stream: Any,
        callback: Callable[[str], None] | None = None,
    ) -> str:
        """
        Process streaming API response.

        Parameters
        ----------
        response_stream : Any
            Streaming API response.
        callback : Callable[[str], None] | None, optional
            Function to call with each response chunk, by default None.

        Returns
        -------
        str
            Complete LLM response (all chunks combined).
        """
        full_response = ""

        for chunk in response_stream:
            # Extract content from the chunk
            if chunk.choices and len(chunk.choices) > 0:
                # Get delta content (may be None)
                content = chunk.choices[0].delta.content

                # Skip if no content in this chunk
                if content is None:
                    continue

                # Append to full response
                full_response += content

                # Call callback if provided
                if callback:
                    callback(content)

        return full_response

    def process_text(
        self,
        text: str,
        image_data: bytes | None = None,
    ) -> str:
        """
        Process text and optionally an image using the configured LLM.

        Parameters
        ----------
        text : str
            Text to process through the LLM.
        image_data : bytes, optional
            Image data in bytes format, by default None.

        Returns
        -------
        str
            The complete text response from the LLM.

        Raises
        ------
        ValueError
            If the text input is empty or invalid.
        """
        # Validate input
        if not text or not isinstance(text, str):
            raise ValueError("Text input must be a non-empty string.")

        # Create messages
        messages = self._create_api_messages(text=text, image_data=image_data)

        # Make API call
        response = self._make_api_call(messages=messages)

        # Process response
        return self._process_standard_response(response=response)

    def process_text_with_stream(
        self,
        text: str,
        callback: Callable[[str], None] | None = None,
        image_data: bytes | None = None,
    ) -> str:
        """
        Process text through the LLM with streaming responses, optionally with an image.

        Parameters
        ----------
        text : str
            Text to process.
        callback : Callable[[str], None] | None, optional
            Function to call with each response chunk, by default None.
        image_data : bytes | None, optional
            Image data in bytes format, by default None.

        Returns
        -------
        str
            Complete LLM response (all chunks combined).

        Raises
        ------
        ValueError
            If the text input is empty or invalid.
        """
        # Validate input
        if not text or not isinstance(text, str):
            raise ValueError("Text input must be a non-empty string.")

        # Create messages
        messages = self._create_api_messages(text=text, image_data=image_data)

        # Make API call with streaming
        response_stream = self._make_api_call(messages=messages, stream=True)

        # Process streaming response
        return self._process_streaming_response(response_stream=response_stream, callback=callback)
