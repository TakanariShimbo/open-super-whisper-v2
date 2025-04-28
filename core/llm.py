"""
LLM Processing Interface

This module provides a complete implementation for the OpenAI API to process text using LLMs.
"""

import base64
import os
from typing import List, Dict, Any, Optional, Union
import openai

# Import model data from core.models
from core.models.llm import LLMModelManager


class LLMProcessor:
    """
    Implementation of OpenAI LLM API text processing.
    
    This class provides methods to process text using large language models 
    through the OpenAI API, with support for different models and custom instructions.
    """
    
    # Use model manager for available models
    AVAILABLE_MODELS = LLMModelManager.to_api_format()
    
    def __init__(self, api_key: str = None, model: str = "gpt-4o"):
        """
        Initialize the LLMProcessor.
        
        Parameters
        ----------
        api_key : str, optional
            OpenAI API key, by default None. If None, tries to get from environment.
        model : str, optional
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
        
        # Set model and initialize instructions
        self.model = model
        self.system_instructions: List[str] = []
    
    @classmethod
    def get_available_models(cls) -> List[Dict[str, str]]:
        """
        Get a list of available LLM models.
        
        Returns
        -------
        List[Dict[str, str]]
            List of dictionaries with model information (id, name, description).
        """
        return cls.AVAILABLE_MODELS
    
    def set_model(self, model: str) -> None:
        """
        Set the LLM model to use.
        
        Parameters
        ----------
        model : str
            Model ID to use for processing.
        """
        self.model = model
    
    def add_system_instruction(self, instructions: Union[str, List[str]]) -> None:
        """
        Add system instructions to control LLM behavior.
        
        Parameters
        ----------
        instructions : Union[str, List[str]]
            Instruction or list of instruction strings.
        """
        if isinstance(instructions, str):
            instructions = [instructions]
        self.system_instructions.extend(instructions)
    
    def clear_system_instructions(self) -> None:
        """Clear all system instructions."""
        self.system_instructions = []
    
    def get_system_instructions(self) -> List[str]:
        """
        Get the current list of system instructions.
        
        Returns
        -------
        List[str]
            List of instruction strings.
        """
        return self.system_instructions
    
    def _build_system_message(self) -> str:
        """
        Build a system message with instructions.
        
        Returns
        -------
        str
            Combined system message, or a default message if no instructions exist.
        """
        if not self.system_instructions:
            return "You are a helpful assistant. Process the following transcribed text."
        
        return " ".join(self.system_instructions)
    
    def process(self, text: str, image_data: bytes = None) -> str:
        """
        Process text and optionally an image using GPT-4o.
        
        Parameters
        ----------
        text : str
            Text to process.
        image_data : bytes, optional
            Image data in bytes format, by default None.
            
        Returns
        -------
        str
            LLM response.
            
        Raises
        ------
        Exception
            If processing fails.
        """
        try:
            system_message = self._build_system_message()
            
            # Prepare user content
            if image_data is not None:
                # Convert image bytes to base64 string
                base64_image = base64.b64encode(image_data).decode('utf-8')
                
                # Create user content with both text and image using the format for GPT-4o
                user_content = [
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
                user_content = [{"type": "text", "text": text}]
            
            # Make API call
            response = self.client.chat.completions.create(
                model=self.model,
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
            
        except Exception as e:
            error_msg = f"Error occurred during LLM processing: {str(e)}"
            print(error_msg)
            return f"Error: {str(e)}"
    
    def get_api_key(self) -> str:
        """
        Get the current API key.
        
        Returns
        -------
        str
            The current API key.
        """
        return self.api_key
    
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
