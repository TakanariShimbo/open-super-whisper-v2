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

import asyncio
import base64
import json
from contextlib import AsyncExitStack
from typing import Any, Callable

from agents import Agent, Runner, WebSearchTool, set_default_openai_key
from agents.mcp import MCPServerStdio
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

        self._model_id = self.DEFAULT_MODEL_ID
        self._system_instruction: str = "You are a helpful assistant."
        self._web_search_enabled: bool = False
        self._mcp_servers_json_str: str = r"{}"

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

        # Update model ID and clear agent if the model ID is different
        if self._model_id != model_id:
            self._model_id = model_id

    def set_system_instruction(self, instruction: str) -> None:
        """
        Set system instruction to control agent behavior.

        Parameters
        ----------
        instruction : str
            Instruction string.
        """
        # Update system instruction and clear agent if the instruction is different
        if self._system_instruction != instruction:
            self._system_instruction = instruction

    def set_mcp_servers_json_str(self, json_str: str) -> None:
        """
        Set the MCP servers JSON string.

        Parameters
        ----------
        json_str : str
            MCP servers JSON string.

        Raises
        ------
        ValueError
            If the MCP servers JSON string is invalid.
        """
        self.check_mcp_servers_json_str(json_str)

        # Update MCP servers JSON string and clear agent if the value is different
        if self._mcp_servers_json_str != json_str:
            self._mcp_servers_json_str = json_str

    def set_web_search_enabled(self, is_enabled: bool) -> None:
        """
        Set whether to enable web search.

        Parameters
        ----------
        is_enabled : bool
            Whether to enable web search.
        """
        # Update web search enabled and clear agent if the value is different
        if self._web_search_enabled != is_enabled:
            self._web_search_enabled = is_enabled

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

        # Check if model supports web search
        if self._web_search_enabled and not LLMModelManager.check_web_search_supported(self._model_id):
            raise ValueError(
                f"Model {self._model_id} does not support web search."
            )

        async with AsyncExitStack() as stack:
            # Create MCP servers
            mcp_servers_params = json.loads(self._mcp_servers_json_str)
            mcp_servers: list[MCPServerStdio] = []
            for name, params in mcp_servers_params.items():
                server = await stack.enter_async_context(
                    MCPServerStdio(
                        name=name,
                        params=params,
                        client_session_timeout_seconds=30,
                    )
                )
                await server.list_tools()
                mcp_servers.append(server)

            # Create agent
            agent = Agent(
                name="Assistant",
                instructions=self._system_instruction,
                model=self._model_id,
                tools=[WebSearchTool()] if self._web_search_enabled else [],
                mcp_servers=mcp_servers,
            )

            # Run the agent and get response
            result = await Runner.run(agent, input=input_data)
            response = result.final_output

        # Wait for MCP servers to cleanup
        await asyncio.sleep(1)

        return response

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

        # Check if model supports web search
        if self._web_search_enabled and not LLMModelManager.check_web_search_supported(self._model_id):
            raise ValueError(
                f"Model {self._model_id} does not support web search."
            )

        async with AsyncExitStack() as stack:
            # Create MCP servers
            params_dict = json.loads(self._mcp_servers_json_str)
            mcp_servers: list[MCPServerStdio] = []
            for _, params in params_dict.items():
                server = await stack.enter_async_context(
                    MCPServerStdio(
                        params=params,
                        client_session_timeout_seconds=30,
                    )
                )
                await server.list_tools()
                mcp_servers.append(server)

            # Create agent
            agent = Agent(
                name="Assistant",
                instructions=self._system_instruction,
                model=self._model_id,
                tools=[WebSearchTool()] if self._web_search_enabled else [],
                mcp_servers=mcp_servers,
            )

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

        # Wait for MCP servers to cleanup
        await asyncio.sleep(1)

        return full_response

    def shutdown(self) -> None:
        """
        Shutdown the LLMProcessor.
        """
        pass

    @staticmethod
    def check_mcp_servers_json_str(json_str: str) -> None:
        """
        Check if the MCP servers JSON string is valid.

        Parameters
        ----------
        json_str : str
            MCP servers JSON string.

        Raises
        ------
        ValueError
            If the MCP servers JSON string is invalid.
        """
        try:
            mcp_servers = json.loads(json_str)
            if not isinstance(mcp_servers, dict):
                raise AssertionError(f"MCP servers must be a dict.")

            mcp_servers_params = mcp_servers.get("mcpServers", {})
            if not isinstance(mcp_servers_params, dict):
                raise AssertionError(f"MCP servers must be a dict.")

            for name, params in mcp_servers_params.items():
                if not isinstance(name, str):
                    raise AssertionError(f"MCP server 'name' must be a string.")
                if not isinstance(params, dict):
                    raise AssertionError(f"MCP server 'params' must be a dict.")
                if params.get("command", None) is None:
                    raise AssertionError(f"MCP server 'command' must be set.")
                if params.get("args", None) is None:
                    raise AssertionError(f"MCP server 'args' must be set.")
        except (json.JSONDecodeError, AssertionError) as e:
            raise ValueError(str(e))