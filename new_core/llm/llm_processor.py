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
import os
from typing import List, Dict, Any, Optional, Callable
import openai

# Import model data
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
    """
    
    # Use model manager for available models
    AVAILABLE_MODELS = LLMModelManager.to_api_format()
    
    def __init__(self, api_key: str = None, model_id: str = "gpt-4o"):
        """
        Initialize the LLMProcessor.
        
        Parameters
        ----------
        api_key : str, optional
            API key, by default None. If None, tries to get from environment.
        model_id : str, optional
            LLM model to use, by default "gpt-4o".
            
        Raises
        ------
        ValueError
            If no API key is provided and none is found in environment variables.
        """
        # Get API key from parameter or environment variable
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        
        if not self.api_key:
            raise ValueError("API key is required. Provide it directly or set OPENAI_API_KEY environment variable.")
        
        # Initialize OpenAI client
        self.client = openai.OpenAI(api_key=self.api_key)
        
        # Set model and initialize instruction
        self.model_id = model_id
        self.system_instruction: str = ""
    
    def set_model(self, model_id: str) -> None:
        """
        Set the LLM model to use.
        
        Parameters
        ----------
        model_id : str
            Model ID to use for processing.
        """
        self.model_id = model_id
    
    def set_system_instruction(self, instruction: str) -> None:
        """
        Set system instruction to control LLM behavior.
        
        Parameters
        ----------
        instruction : str
            Instruction string.
        """
        self.system_instruction = instruction
    
    def clear_system_instruction(self) -> None:
        """Clear the system instruction."""
        self.system_instruction = ""
    
    def _create_llm_system_message(self) -> str:
        """
        Get the system message with instruction for the LLM.
        
        Returns
        -------
        str
            System message, or a default message if no instruction exists.
        """
        if not self.system_instruction:
            return "You are a helpful assistant. Process the following transcribed text."
        
        return self.system_instruction
    
    def _format_user_content(self, text: str, image_data: Optional[bytes] = None) -> List[Dict[str, Any]]:
        """
        Format user content into the structure required by the API, including optional image data.
        
        Parameters
        ----------
        text : str
            Text to process.
        image_data : bytes, optional
            Image data in bytes format, by default None.
            
        Returns
        -------
        List[Dict[str, Any]]
            Formatted user content for the API.
        """
        if image_data is not None:
            # Convert image bytes to base64 string
            base64_image = base64.b64encode(image_data).decode('utf-8')
            
            # Create user content with both text and image using the format for GPT-4o
            return [
                {"type": "text", "text": text},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                }
            ]
        else:
            # Text-only content can also use the array format for consistency
            return [{"type": "text", "text": text}]
    
    def process_text(self, text: str, image_data: bytes = None) -> str:
        """
        Process text and optionally an image using the configured LLM.
        
        This method sends the provided text (and optional image) to the API
        for processing with the currently configured model. It handles creating the
        appropriate system message and formatting the user content.
        
        Parameters
        ----------
        text : str
            Text to process through the LLM. This can be a prompt, question, or
            any text content you want the LLM to respond to.
            Example: "Summarize the following transcription: {...}"
        image_data : bytes, optional
            Image data in bytes format that will be sent alongside the text.
            This must be raw image bytes that can be base64 encoded.
            Example: open("image.jpg", "rb").read()
            By default None.
            
        Returns
        -------
        str
            The complete text response from the LLM.
            Example: "Based on the provided transcription, the main points are..."
            
        Raises
        ------
        ValueError
            If the text input is empty or invalid.
        """
        if not text or not isinstance(text, str):
            raise ValueError("Text input must be a non-empty string")

        system_message = self._create_llm_system_message()
        
        # Format user content
        user_content = self._format_user_content(text, image_data)
        
        # Make API call
        response = self.client.chat.completions.create(
            model=self.model_id,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_content}
            ]
        )
        
        # Extract and return the response text
        if response.choices and len(response.choices) > 0:
            return response.choices[0].message.content
        else:
            return "No response generated."
    
    def process_text_with_stream(self, text: str, callback: Optional[Callable[[str], None]] = None, 
                            image_data: Optional[bytes] = None) -> str:
        """
        Process text through the LLM with streaming responses, optionally with an image.
        
        Parameters
        ----------
        text : str
            Text to process.
        callback : Optional[Callable[[str], None]], optional
            Function to call with each response chunk, by default None.
            If None, chunks are accumulated and the final result is returned.
        image_data : bytes, optional
            Image data in bytes format, by default None.
            
        Returns
        -------
        str
            Complete LLM response (all chunks combined).
        """
        if not text or not isinstance(text, str):
            raise ValueError("Text input must be a non-empty string")
        
        system_message = self._create_llm_system_message()
        
        # Format user content
        user_content = self._format_user_content(text, image_data)
        
        # Make streaming API call
        response_stream = self.client.chat.completions.create(
            model=self.model_id,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_content}
            ],
            stream=True
        )
        
        # Process streaming response
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
    
    def set_api_key(self, api_key: str) -> None:
        """
        Set a new API key.
        
        Parameters
        ----------
        api_key : str
            New API key to use.
            
        Raises
        ------
        ValueError
            If API key is empty.
        """
        if not api_key:
            raise ValueError("API key cannot be empty")
        
        self.api_key = api_key
        # Update the client with the new API key
        self.client = openai.OpenAI(api_key=self.api_key)