"""
Unified Processing System

This module provides a unified processing system that integrates
both transcription and LLM processing in a seamless way.
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any, Union
import os

from core.transcriber import WhisperTranscriber
from core.llm import LLMProcessor


@dataclass
class ProcessingResult:
    """
    Container for processing results.
    
    This class holds the results of both transcription and optional LLM processing.
    
    Attributes
    ----------
    transcription : str
        The transcribed text.
    llm_response : Optional[str]
        The LLM response, if LLM processing was performed.
    llm_processed : bool
        Whether LLM processing was performed.
    """
    transcription: str
    llm_response: Optional[str] = None
    llm_processed: bool = False
    
    def get_formatted_output(self) -> str:
        """
        Get a formatted output combining transcription and LLM response.
        
        Returns
        -------
        str
            Formatted output string.
        """
        if not self.llm_processed or not self.llm_response:
            return self.transcription
        
        return f"Transcription:\n{self.transcription}\n\nLLM Response:\n{self.llm_response}"


class UnifiedProcessor:
    """
    Unified processor for transcription and LLM processing.
    
    This class combines WhisperTranscriber and LLMProcessor to provide
    a seamless processing pipeline, with optional LLM processing.
    """
    
    def __init__(self, api_key: str = None, whisper_model: str = "whisper-1", 
                 llm_model: str = "gpt-3.5-turbo"):
        """
        Initialize the UnifiedProcessor.
        
        Parameters
        ----------
        api_key : str, optional
            OpenAI API key, by default None. If None, tries to get from environment.
        whisper_model : str, optional
            Whisper model to use, by default "whisper-1".
        llm_model : str, optional
            LLM model to use, by default "gpt-3.5-turbo".
            
        Raises
        ------
        ValueError
            If no API key is provided and none is found in environment variables.
        """
        # Get API key from parameter or environment variable
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        
        if not self.api_key:
            raise ValueError("API key is required. Provide it directly or set OPENAI_API_KEY environment variable.")
        
        # Initialize components
        self.transcriber = WhisperTranscriber(api_key=self.api_key, model=whisper_model)
        self.llm_processor = LLMProcessor(api_key=self.api_key, model=llm_model)
        
        # Processing state
        self.llm_enabled = False
    
    def enable_llm(self, enabled: bool = True) -> None:
        """
        Enable or disable LLM processing.
        
        Parameters
        ----------
        enabled : bool, optional
            Whether to enable LLM processing, by default True.
        """
        self.llm_enabled = enabled
    
    def is_llm_enabled(self) -> bool:
        """
        Check if LLM processing is enabled.
        
        Returns
        -------
        bool
            Whether LLM processing is enabled.
        """
        return self.llm_enabled
    
    def set_api_key(self, api_key: str) -> None:
        """
        Set a new API key for all processors.
        
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
        self.transcriber.set_api_key(api_key)
        self.llm_processor.set_api_key(api_key)
    
    # Transcriber delegation methods
    def set_whisper_model(self, model: str) -> None:
        """Set the Whisper model."""
        self.transcriber.set_model(model)
    
    def add_custom_vocabulary(self, vocabulary: Union[str, List[str]]) -> None:
        """Add custom vocabulary for transcription."""
        self.transcriber.add_custom_vocabulary(vocabulary)
    
    def clear_custom_vocabulary(self) -> None:
        """Clear custom vocabulary for transcription."""
        self.transcriber.clear_custom_vocabulary()
    
    def add_transcription_instruction(self, instructions: Union[str, List[str]]) -> None:
        """Add system instructions for transcription."""
        self.transcriber.add_system_instruction(instructions)
    
    def clear_transcription_instructions(self) -> None:
        """Clear system instructions for transcription."""
        self.transcriber.clear_system_instructions()
    
    # LLM processor delegation methods
    def set_llm_model(self, model: str) -> None:
        """Set the LLM model."""
        self.llm_processor.set_model(model)
    
    def add_llm_instruction(self, instructions: Union[str, List[str]]) -> None:
        """Add system instructions for LLM processing."""
        self.llm_processor.add_system_instruction(instructions)
    
    def clear_llm_instructions(self) -> None:
        """Clear system instructions for LLM processing."""
        self.llm_processor.clear_system_instructions()
    
    def process(self, audio_file: str, language: Optional[str] = None) -> ProcessingResult:
        """
        Process an audio file with transcription and optional LLM processing.
        
        Parameters
        ----------
        audio_file : str
            Path to the audio file to process.
        language : Optional[str], optional
            Language code (e.g., "en", "ja"), or None for auto-detection, by default None.
            
        Returns
        -------
        ProcessingResult
            Processing result containing transcription and optional LLM response.
        """
        # First, perform transcription
        transcription = self.transcriber.transcribe(audio_file, language)
        
        # Create result object
        result = ProcessingResult(transcription=transcription)
        
        # If LLM is enabled, process the transcription
        if self.llm_enabled:
            try:
                llm_response = self.llm_processor.process(transcription)
                result.llm_response = llm_response
                result.llm_processed = True
            except Exception as e:
                print(f"LLM processing error: {e}")
                # Still return the transcription even if LLM processing fails
                result.llm_response = f"Error in LLM processing: {str(e)}"
                result.llm_processed = False
        
        return result
