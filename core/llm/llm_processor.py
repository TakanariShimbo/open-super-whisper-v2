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
import os
from contextlib import AsyncExitStack
from typing import Any, Callable, Union, Literal

from agents import Agent, Runner, WebSearchTool, set_default_openai_key
from agents.mcp import MCPServerStdio, MCPServerSse, MCPServerStreamableHttp
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
        """
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

    def _validate_input(self, text: str) -> None:
        """
        Validate text input.

        Parameters
        ----------
        text : str
            Text to validate.

        Raises
        ------
        ValueError
            If the text input is empty or invalid.
        """
        if not text or not isinstance(text, str):
            raise ValueError("Text input must be a non-empty string.")

    def _prepare_input(self, text: str, image_data: bytes | None = None) -> str | list[dict[str, Any]]:
        """
        Prepare input data for the agent.

        Parameters
        ----------
        text : str
            Text prompt.
        image_data : bytes | None, optional
            Image data in bytes format, by default None.

        Returns
        -------
        str | list[dict[str, Any]]
            Formatted input for the agent.

        Raises
        ------
        ValueError
            If the model does not support image inputs.
        """
        if image_data is not None:
            # Check if model supports images
            if not LLMModelManager.check_image_input_supported(model_id=self._model_id):
                raise ValueError(
                    f"Model {self._model_id} does not support image inputs."
                )
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
        else:
            return text

    def _validate_capabilities(self, mcp_servers_params: dict[str, dict[str, Any]]) -> None:
        """
        Validate that the model supports the configured capabilities.

        Parameters
        ----------
        mcp_servers_params : dict[str, dict[str, Any]]
            Parsed MCP server parameters.

        Raises
        ------
        ValueError
            If the model does not support web search or MCP servers when enabled.
        """
        # Check if model supports web search
        if self._web_search_enabled and not LLMModelManager.check_web_search_supported(model_id=self._model_id):
            raise ValueError(
                f"Model {self._model_id} does not support web search."
            )

        # Check if model supports MCP servers
        if len(mcp_servers_params) > 0 and not LLMModelManager.check_mcp_servers_supported(model_id=self._model_id):
            raise ValueError(
                f"Model {self._model_id} does not support MCP servers."
            )

    def _build_server(self, name: str, params: dict[str, Any]) -> Union[MCPServerStdio, MCPServerSse, MCPServerStreamableHttp]:
        """
        Build appropriate MCP server based on configuration.
        
        Parameters
        ----------
        name : str
            Server name.
        params : dict[str, Any]
            Server parameters.
            
        Returns
        -------
        Union[MCPServerStdio, MCPServerSse, MCPServerStreamableHttp]
            Configured MCP server instance.
        """
        timeout = params.get("timeout", 30)
        
        # Build stdio server
        if "command" in params:
            stdio_params: dict[str, Any] = {
                "command": params["command"],
            }
            if params.get("args"):
                stdio_params["args"] = params["args"]
            if params.get("env"):
                stdio_params["env"] = params["env"]
            if params.get("cwd"):
                stdio_params["cwd"] = params["cwd"]
            
            return MCPServerStdio(
                name=name,
                params=stdio_params,
                client_session_timeout_seconds=timeout,
            )
        
        # Build HTTP-based server
        server_type: Literal["sse", "stream", "http", "streamable-http"] = params["type"]
        http_params: dict[str, Any] = {
            "url": params["url"],
        }
        if params.get("headers"):
            http_params["headers"] = params["headers"]
        
        if server_type == "sse":
            return MCPServerSse(
                name=name,
                params=http_params,
                client_session_timeout_seconds=timeout,
            )
        else:
            return MCPServerStreamableHttp(
                name=name,
                params=http_params,
                client_session_timeout_seconds=timeout,
            )

    async def _create_mcp_servers(self, stack: AsyncExitStack, mcp_servers_params: dict[str, dict[str, Any]]) -> list[Union[MCPServerStdio, MCPServerSse, MCPServerStreamableHttp]]:
        """
        Create MCP servers within an async context.

        Parameters
        ----------
        stack : AsyncExitStack
            Async context stack for managing server lifecycles.
        mcp_servers_params : dict[str, dict[str, Any]]
            Parsed MCP server parameters.

        Returns
        -------
        list[Union[MCPServerStdio, MCPServerSse, MCPServerStreamableHttp]]
            List of created MCP servers.
        """
        mcp_servers: list[Union[MCPServerStdio, MCPServerSse, MCPServerStreamableHttp]] = []
        
        for name, params in mcp_servers_params.items():
            server = self._build_server(name=name, params=params)
            await stack.enter_async_context(server)
            mcp_servers.append(server)
            
        return mcp_servers

    def _create_agent(self, mcp_servers: list[Union[MCPServerStdio, MCPServerSse, MCPServerStreamableHttp]]) -> Agent:
        """
        Create an Agent instance with configured settings.

        Parameters
        ----------
        mcp_servers : list[Union[MCPServerStdio, MCPServerSse, MCPServerStreamableHttp]]
            List of MCP servers to attach to the agent.

        Returns
        -------
        Agent
            Configured agent instance.
        """
        return Agent(
            name="Assistant",
            instructions=self._system_instruction,
            model=self._model_id,
            tools=[WebSearchTool()] if self._web_search_enabled else [],
            mcp_servers=mcp_servers,
        )

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
        self._validate_input(text=text)

        # Prepare input data
        input_data = self._prepare_input(text=text, image_data=image_data)

        # Parse MCP servers configuration once
        mcp_servers_params = self.parse_mcp_servers_json(json_str=self._mcp_servers_json_str)
        
        # Validate capabilities
        self._validate_capabilities(mcp_servers_params=mcp_servers_params)

        async with AsyncExitStack() as stack:
            # Create MCP servers
            mcp_servers = await self._create_mcp_servers(stack=stack, mcp_servers_params=mcp_servers_params)

            # Create agent
            agent = self._create_agent(mcp_servers=mcp_servers)

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
        self._validate_input(text=text)

        # Prepare input data
        input_data = self._prepare_input(text=text, image_data=image_data)

        # Parse MCP servers configuration once
        mcp_servers_params = self.parse_mcp_servers_json(json_str=self._mcp_servers_json_str)
        
        # Validate capabilities
        self._validate_capabilities(mcp_servers_params=mcp_servers_params)

        async with AsyncExitStack() as stack:
            # Create MCP servers
            mcp_servers = await self._create_mcp_servers(stack=stack, mcp_servers_params=mcp_servers_params)

            # Create agent
            agent = self._create_agent(mcp_servers=mcp_servers)

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
    def _expand_env(obj: Any) -> Any:
        """
        Recursively expand environment variables in configuration objects.
        
        This method processes strings, lists, and dictionaries to expand any
        environment variables using the ${VAR} or $VAR syntax.
        
        Parameters
        ----------
        obj : Any
            The configuration object to process. Can be a string, list, dict,
            or any other type.
            
        Returns
        -------
        Any
            The processed object with environment variables expanded.
            - Strings: Environment variables are expanded using os.path.expandvars
            - Lists: Each element is recursively processed
            - Dicts: Each value is recursively processed
            - Other types: Returned unchanged
            
        Examples
        --------
        >>> os.environ['HOME'] = '/home/user'
        >>> LLMProcessor._expand_env('${HOME}/config')
        '/home/user/config'
        
        >>> LLMProcessor._expand_env({'path': '${HOME}', 'items': ['$USER', 'test']})
        {'path': '/home/user', 'items': ['username', 'test']}
        """
        if isinstance(obj, str):
            return os.path.expandvars(obj)
        if isinstance(obj, list):
            return [LLMProcessor._expand_env(x) for x in obj]
        if isinstance(obj, dict):
            return {k: LLMProcessor._expand_env(v) for k, v in obj.items()}
        return obj


    @staticmethod
    def _validate_server_config(name: str, params: dict[str, Any]) -> None:
        """
        Validate server configuration.
        
        Parameters
        ----------
        name : str
            Server name.
        params : dict[str, Any]
            Server parameters.
            
        Raises
        ------
        ValueError
            If configuration is invalid.
        """
        http_types = {"sse", "stream", "http", "streamable-http"}
        allowed_types = {"stdio"} | http_types
        
        server_type = params.get("type")
        
        # Validate stdio type
        if "command" in params:
            if not isinstance(params["command"], str):
                raise ValueError(f'Server "{name}": "command" must be a string.')
            args = params.get("args")
            if args is not None and not isinstance(args, list):
                raise ValueError(f'Server "{name}": "args" must be a list.')
            if server_type and server_type != "stdio":
                raise ValueError(f'Server "{name}": type must be "stdio" or omitted for command-based servers.')
        
        # Validate HTTP/SSE type
        elif "url" in params:
            if not isinstance(params["url"], str):
                raise ValueError(f'Server "{name}": "url" must be a string.')
            if server_type not in http_types:
                raise ValueError(
                    f'Server "{name}": url servers require type '
                    f'"sse" or "stream"/"http"/"streamable-http".'
                )
        else:
            raise ValueError(
                f'Server "{name}" needs "command" (stdio) or "url" (HTTP/SSE).'
            )
        
        # Validate server type is allowed
        if server_type and server_type not in allowed_types:
            raise ValueError(
                f'Server "{name}": unknown type "{server_type}". Allowed: {allowed_types}'
            )
        
        # Validate optional fields
        if "headers" in params and not isinstance(params["headers"], dict):
            raise ValueError(f'Server "{name}": "headers" must be an object.')
        if "env" in params and not isinstance(params["env"], dict):
            raise ValueError(f'Server "{name}": "env" must be an object.')
        if "cwd" in params and params.get("cwd") is not None and not isinstance(params["cwd"], str):
            raise ValueError(f'Server "{name}": "cwd" must be a string.')

    @staticmethod
    def parse_mcp_servers_json(json_str: str) -> dict[str, dict[str, Any]]:
        """
        Parse the MCP servers JSON string into a dictionary of parameters.

        Parameters
        ----------
        json_str : str
            MCP servers JSON string.

        Returns
        -------
        dict[str, dict[str, Any]]
            MCP servers parameters.

        Raises
        ------
        ValueError
            If the MCP servers JSON string is invalid.
        """
        try:
            root = json.loads(json_str)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON: {exc}") from None

        if not isinstance(root, dict):
            raise ValueError("Root must be an object.")

        original_mcp_servers = root.get("mcpServers", {})
        if not isinstance(original_mcp_servers, dict):
            raise ValueError('"mcpServers" must be an object.')

        mcp_servers: dict[str, dict[str, Any]] = {}
        for name, params in original_mcp_servers.items():
            if not isinstance(name, str):
                raise ValueError("Server names must be strings.")
            if not isinstance(params, dict):
                raise ValueError(f'Server "{name}" must be an object.')
            
            # Skip disabled servers
            if params.get("enabled", True) is False:
                continue
            
            # Validate server type and connection
            LLMProcessor._validate_server_config(name=name, params=params)
            
            # Expand environment variables
            mcp_servers[name] = LLMProcessor._expand_env(obj=params)

        return mcp_servers
