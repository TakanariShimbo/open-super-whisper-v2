"""
LLM Processing Module using OpenAI Agents SDK

This module provides a complete implementation for processing text using the OpenAI Agents SDK,
with support for:
- Text and image inputs  
- Streaming and non-streaming responses
- Custom system instructions
- Multiple model support
- Comprehensive error handling
- Async/await patterns

The primary class (LLMProcessor) handles all communication with the LLM using
the modern Agents SDK approach.
"""

import base64
from typing import Any, Callable

from agents import Agent, Runner, set_default_openai_key
from openai.types.responses import ResponseTextDeltaEvent

from .llm_model_manager import LLMModelManager


class LLMProcessor:
    """
    Implementation for processing text and images using OpenAI Agents SDK.

    This class provides a comprehensive interface to LLM capabilities using the
    modern Agents SDK with:
    - Text and multimodal (text+image) input support
    - Both streaming and non-streaming response options
    - Customizable system instructions for controlling agent behavior
    - Support for all available chat completion models
    - Robust error handling
    - Async/await patterns for better performance

    The processor uses the Agents SDK's Agent and Runner classes to handle
    all aspects of communication with the LLM.

    Examples
    --------
    Basic text processing:

    >>> processor = LLMProcessor(api_key="your_api_key")
    >>> response = await processor.process_text("Summarize the benefits of AI assistants.")
    >>> print(response)
    AI assistants offer several benefits: 1. 24/7 availability...

    With custom system instruction:

    >>> processor = LLMProcessor(api_key="your_api_key")
    >>> processor.set_system_instruction("Respond in bullet points format.")
    >>> response = await processor.process_text("What are the key features of Python?")
    >>> print(response)
    • Dynamic typing
    • Interpreted language
    • Extensive standard library
    • ...

    Streaming response with callback:

    >>> async def print_chunk(chunk):
    ...     print(chunk, end="", flush=True)
    >>>
    >>> processor = LLMProcessor(api_key="your_api_key")
    >>> await processor.process_text_with_stream(
    ...     "Explain quantum computing",
    ...     callback=print_chunk
    ... )
    Quantum computing is a type of computing that...
    """

    # Use model manager for available models
    AVAILABLE_MODELS = LLMModelManager.to_api_format()
    DEFAULT_MODEL_ID = LLMModelManager.get_default_model().id

    def __init__(self, api_key: str) -> None:
        """
        Initialize the LLMProcessor with API key.

        Parameters
        ----------
        api_key : str
            OpenAI API key for authentication.
        """
        # Set the API key globally for the Agents SDK
        set_default_openai_key(api_key)
        
        self._agent: Agent | None = None
        self._model_id = self.DEFAULT_MODEL_ID
        self._system_instruction: str = "You are a helpful assistant."

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
        # Validate that model exists
        model = LLMModelManager.find_model_by_id(model_id)
        if not model:
            available_models = [m["id"] for m in self.AVAILABLE_MODELS]
            available_model_names = ", ".join(available_models[:5]) + "..."
            raise ValueError(
                f"Unknown model ID: {model_id}. Available models include: {available_model_names}"
            )

        self._model_id = model_id
        # Reset agent to force recreation with new model
        self._agent = None

    def set_system_instruction(self, instruction: str) -> None:
        """
        Set system instruction to control agent behavior.

        Parameters
        ----------
        instruction : str
            Instruction string.
        """
        self._system_instruction = instruction
        # Reset agent to force recreation with new instruction
        self._agent = None

    def clear_system_instruction(self) -> None:
        """
        Clear the system instruction and reset to default.
        """
        self._system_instruction = "You are a helpful assistant."
        # Reset agent to force recreation
        self._agent = None

    def _get_or_create_agent(self) -> Agent:
        """
        Get existing agent or create a new one with current settings.

        Returns
        -------
        Agent
            Configured Agent instance.
        """
        if self._agent is None:
            self._agent = Agent(
                name="Assistant",
                instructions=self._system_instruction,
                model=self._model_id,
            )
        return self._agent

    def _format_image_input(self, text: str, image_data: bytes) -> list[dict[str, Any]]:
        """
        Format text and image data into the input format expected by Agents SDK.

        Parameters
        ----------
        text : str
            Text prompt.
        image_data : bytes
            Image data in bytes format.

        Returns
        -------
        list[dict[str, Any]]
            Formatted input for the agent.
        """
        # Convert image bytes to base64 string
        base64_image = base64.b64encode(image_data).decode("utf-8")
        
        # Format according to Agents SDK expectations
        return [
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_image",
                        "detail": "auto",
                        "image_url": f"data:image/jpeg;base64,{base64_image}",
                    }
                ],
            },
            {
                "role": "user", 
                "content": text,
            },
        ]

    async def process_text(
        self,
        text: str,
        image_data: bytes | None = None,
    ) -> str:
        """
        Process text and optionally an image using the configured agent.

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

        # Get or create agent
        agent = self._get_or_create_agent()

        # Format input based on whether image is included
        if image_data is not None:
            # Check if model supports images
            if not LLMModelManager.check_image_input_supported(self._model_id):
                raise ValueError(
                    f"Model {self._model_id} does not support image inputs."
                )
            input_data = self._format_image_input(text, image_data)
        else:
            input_data = text

        # Run the agent and get response
        result = await Runner.run(agent, input=input_data)
        return result.final_output

    async def process_text_with_stream(
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


        # Get or create agent
        agent = self._get_or_create_agent()

        # Format input based on whether image is included
        if image_data is not None:
            # Check if model supports images
            if not LLMModelManager.check_image_input_supported(self._model_id):
                raise ValueError(
                    f"Model {self._model_id} does not support image inputs."
                )
            input_data = self._format_image_input(text, image_data)
        else:
            input_data = text

        # Run the agent with streaming
        result = Runner.run_streamed(agent, input=input_data)
        full_response = ""

        # Process streaming events
        async for event in result.stream_events():
            if event.type == "raw_response_event" and isinstance(
                event.data, ResponseTextDeltaEvent
            ):
                chunk = event.data.delta
                if chunk:
                    full_response += chunk
                    if callback:
                        callback(chunk)

        return full_response

    def shutdown(self) -> None:
        """
        Shutdown the LLMProcessor.
        """
        self._agent = None
