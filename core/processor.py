"""
Unified Processing System

This module provides a unified processing system that integrates
both transcription and LLM processing in a seamless way.
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any, Union, Callable, Generator, Tuple
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
    
    def __init__(self, api_key: str = None, whisper_model: str = "gpt-4o-transcribe", llm_model: str = "gpt-4o"):
        """
        Initialize the UnifiedProcessor.
        
        Parameters
        ----------
        api_key : str, optional
            OpenAI API key, by default None. If None, tries to get from environment.
        whisper_model : str, optional
            Whisper model to use, by default "gpt-4o-transcribe".
        llm_model : str, optional
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
    
    def process(self, audio_file: str, language: Optional[str] = None, 
             clipboard_text: Optional[str] = None, clipboard_image: Optional[bytes] = None,
             stream_callback: Optional[Callable[[str], None]] = None) -> ProcessingResult:
        """
        Process an audio file with transcription and optional LLM processing.
        
        Parameters
        ----------
        audio_file : str
            Path to the audio file to process.
        language : Optional[str], optional
            Language code (e.g., "en", "ja"), or None for auto-detection, by default None.
        clipboard_text : Optional[str], optional
            Text from clipboard to include in LLM input, by default None.
        clipboard_image : Optional[bytes], optional
            Image data from clipboard to include in LLM input, by default None.
        stream_callback : Optional[Callable[[str], None]], optional
            Callback function for streaming LLM responses, by default None.
            If None, non-streaming API will be used.
            
        Returns
        -------
        ProcessingResult
            Processing result containing transcription and optional LLM response.
        """
        # Check if file exists
        if not os.path.exists(audio_file):
            error_msg = f"Audio file not found: {audio_file}"
            print(error_msg)
            return ProcessingResult(transcription=f"Error: {error_msg}")
        
        # Perform transcription - now transcribe() handles both small and large files
        transcription = self.transcriber.transcribe(audio_file, language)
        
        # Create result object
        result = ProcessingResult(transcription=transcription)
        
        # If LLM is enabled, process the transcription
        if self.llm_enabled:
            try:
                # Combine transcription with clipboard content if provided
                llm_input = transcription
                
                # Add clipboard text if provided
                if clipboard_text:
                    llm_input = f"Clipboard Content:\n{clipboard_text}\n\nTranscription:\n{transcription}"
                
                # Prepare prompt based on inputs
                if clipboard_image:
                    # If we have both clipboard text and image
                    if clipboard_text:
                        prompt = llm_input
                    else:
                        # Just transcription with image
                        prompt = f"Analyze this image along with the following transcription:\n\n{transcription}"
                else:
                    prompt = llm_input
                
                # Process with or without streaming based on callback
                if stream_callback:
                    # Use streaming API with callback
                    if clipboard_image:
                        # Process with image and streaming
                        llm_response = self.llm_processor.process_stream(prompt, stream_callback, clipboard_image)
                    else:
                        # Process text only with streaming
                        llm_response = self.llm_processor.process_stream(prompt, stream_callback)
                else:
                    # Use non-streaming API
                    if clipboard_image:
                        # Process with image
                        llm_response = self.llm_processor.process(prompt, clipboard_image)
                    else:
                        # Process text only
                        llm_response = self.llm_processor.process(prompt)
                
                result.llm_response = llm_response
                result.llm_processed = True
            except Exception as e:
                print(f"LLM processing error: {e}")
                # Still return the transcription even if LLM processing fails
                result.llm_response = f"Error in LLM processing: {str(e)}"
                result.llm_processed = False
        
        return result
        
    def process_with_stream_generator(self, audio_file: str, language: Optional[str] = None,
                                     clipboard_text: Optional[str] = None, 
                                     clipboard_image: Optional[bytes] = None) -> Tuple[ProcessingResult, Optional[Generator[str, None, None]]]:
        """
        Process an audio file with transcription and optional LLM processing, returning a streaming generator.
        
        Parameters
        ----------
        audio_file : str
            Path to the audio file to process.
        language : Optional[str], optional
            Language code (e.g., "en", "ja"), or None for auto-detection, by default None.
        clipboard_text : Optional[str], optional
            Text from clipboard to include in LLM input, by default None.
        clipboard_image : Optional[bytes], optional
            Image data from clipboard to include in LLM input, by default None.
            
        Returns
        -------
        Tuple[ProcessingResult, Optional[Generator[str, None, None]]]
            A tuple containing:
            - The initial processing result with transcription
            - A generator for streaming LLM response chunks (or None if LLM is disabled)
        """
        # Check if file exists
        if not os.path.exists(audio_file):
            error_msg = f"Audio file not found: {audio_file}"
            print(error_msg)
            return ProcessingResult(transcription=f"Error: {error_msg}"), None
        
        # Perform transcription
        transcription = self.transcriber.transcribe(audio_file, language)
        
        # Create result object
        result = ProcessingResult(transcription=transcription)
        
        # If LLM is enabled, prepare streaming generator
        if self.llm_enabled:
            try:
                # Combine transcription with clipboard content if provided
                llm_input = transcription
                
                # Add clipboard text if provided
                if clipboard_text:
                    llm_input = f"Clipboard Content:\n{clipboard_text}\n\nTranscription:\n{transcription}"
                
                # Prepare prompt based on inputs
                if clipboard_image:
                    # If we have both clipboard text and image
                    if clipboard_text:
                        prompt = llm_input
                    else:
                        # Just transcription with image
                        prompt = f"Analyze this image along with the following transcription:\n\n{transcription}"
                else:
                    prompt = llm_input
                
                # Get streaming generator
                if clipboard_image:
                    generator = self.llm_processor.get_stream_generator(prompt, clipboard_image)
                else:
                    generator = self.llm_processor.get_stream_generator(prompt)
                
                # Mark as LLM processed
                result.llm_processed = True
                
                # Return result and generator
                return result, generator
                
            except Exception as e:
                print(f"LLM processing error: {e}")
                # Still return the transcription even if LLM processing fails
                result.llm_response = f"Error in LLM processing: {str(e)}"
                result.llm_processed = False
                return result, None
        
        # LLM not enabled, return result with no generator
        return result, None
