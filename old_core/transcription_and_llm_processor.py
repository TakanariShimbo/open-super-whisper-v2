"""
Transcription and LLM Processing System

This module provides a unified processing system that integrates
both transcription and LLM processing in a seamless way.
"""

from dataclasses import dataclass
from typing import Optional, List, Union, Callable
import os
import openai

from old_core.transcriber import OpenAIWhisperTranscriber
from old_core.llm_processor import OpenAILLMProcessor


@dataclass
class TranscriptionAndLLMResult:
    """
    Container for transcription and LLM processing results.
    
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
    
    def get_combined_output(self) -> str:
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


class TranscriptionAndLLMProcessor:
    """
    Unified processor for transcription and LLM processing.
    
    This class combines WhisperTranscriber and OpenAILLMProcessor to provide
    a seamless processing pipeline, with optional LLM processing.
    """
    
    def __init__(self, openai_api_key: str = None, whisper_model: str = "gpt-4o-transcribe", llm_model: str = "gpt-4o"):
        """
        Initialize the TranscriptionAndLLMProcessor.
        
        Parameters
        ----------
        openai_api_key : str, optional
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
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        
        if not self.openai_api_key:
            raise ValueError("API key is required. Provide it directly or set OPENAI_API_KEY environment variable.")
        
        # Initialize components
        self.whisper_transcriber = OpenAIWhisperTranscriber(openai_api_key=self.openai_api_key, whisper_model=whisper_model)
        self.openai_llm_processor = OpenAILLMProcessor(openai_api_key=self.openai_api_key, llm_model=llm_model)
        
        # Processing state
        self.is_llm_processing_enabled = False
    
    def enable_llm_processing(self, enabled: bool = True) -> None:
        """
        Enable or disable LLM processing.
        
        Parameters
        ----------
        enabled : bool, optional
            Whether to enable LLM processing, by default True.
        """
        self.is_llm_processing_enabled = enabled
    
    def set_openai_api_key(self, api_key: str) -> None:
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
        
        self.openai_api_key = api_key
        self.whisper_transcriber.set_openai_api_key(api_key)
        self.openai_llm_processor.set_openai_api_key(api_key)
    
    # Transcriber delegation methods
    def set_whisper_model(self, model: str) -> None:
        """Set the Whisper model."""
        self.whisper_transcriber.set_whisper_model(model)
    
    def add_custom_vocabulary(self, vocabulary: Union[str, List[str]]) -> None:
        """Add custom vocabulary for transcription."""
        self.whisper_transcriber.add_custom_terminology(vocabulary)
    
    def clear_custom_vocabulary(self) -> None:
        """Clear custom vocabulary for transcription."""
        self.whisper_transcriber.clear_custom_terminology()
    
    def add_transcription_instruction(self, instructions: Union[str, List[str]]) -> None:
        """Add system instructions for transcription."""
        self.whisper_transcriber.add_transcription_instruction(instructions)
    
    def clear_transcription_instructions(self) -> None:
        """Clear system instructions for transcription."""
        self.whisper_transcriber.clear_transcription_instructions()
    
    # LLM processor delegation methods
    def set_llm_model(self, model: str) -> None:
        """Set the LLM model."""
        self.openai_llm_processor.set_model(model)
    
    def add_llm_instruction(self, instructions: Union[str, List[str]]) -> None:
        """Add system instructions for LLM processing."""
        self.openai_llm_processor.add_system_instruction(instructions)
    
    def clear_llm_instructions(self) -> None:
        """Clear system instructions for LLM processing."""
        self.openai_llm_processor.clear_system_instructions()
    
    def process_transcription_and_llm(self, audio_file: str, language: Optional[str] = None, 
                clipboard_text: Optional[str] = None, clipboard_image: Optional[bytes] = None,
                stream_callback: Optional[Callable[[str], None]] = None) -> TranscriptionAndLLMResult:
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
        TranscriptionResult
            Processing result containing transcription and optional LLM response.
            
        Raises
        ------
        FileNotFoundError
            If the audio file does not exist.
        ValueError
            If the API key is invalid or other input validation fails.
        openai.AuthenticationError
            If the API key is invalid or authentication fails.
        openai.RateLimitError
            If OpenAI's rate limits are exceeded.
        Exception
            For any other unexpected errors during processing.
        """
        # Check if file exists
        if not os.path.exists(audio_file):
            error_msg = f"Audio file not found: {audio_file}"
            print(error_msg)
            raise FileNotFoundError(error_msg)
        
        try:
            # Perform transcription - now transcribe() handles both small and large files
            transcription = self.whisper_transcriber.transcribe(audio_file, language)
            
            # Create result object
            result = TranscriptionAndLLMResult(transcription=transcription)
            
            # If LLM is enabled, process the transcription
            if self.is_llm_processing_enabled:
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
                            llm_response = self.openai_llm_processor.process_with_stream(prompt, stream_callback, clipboard_image)
                        else:
                            # Process text only with streaming
                            llm_response = self.openai_llm_processor.process_with_stream(prompt, stream_callback)
                    else:
                        # Use non-streaming API
                        if clipboard_image:
                            # Process with image
                            llm_response = self.openai_llm_processor.process_with_llm(prompt, clipboard_image)
                        else:
                            # Process text only
                            llm_response = self.openai_llm_processor.process_with_llm(prompt)
                    
                    result.llm_response = llm_response
                    result.llm_processed = True
                except openai.AuthenticationError as e:
                    error_msg = f"OpenAI API authentication error: {str(e)}"
                    print(error_msg)
                    result.llm_response = error_msg
                    result.llm_processed = False
                except openai.RateLimitError as e:
                    error_msg = f"OpenAI API rate limit exceeded: {str(e)}"
                    print(error_msg)
                    result.llm_response = error_msg
                    result.llm_processed = False
                except openai.BadRequestError as e:
                    error_msg = f"OpenAI API request was invalid: {str(e)}"
                    print(error_msg)
                    result.llm_response = error_msg
                    result.llm_processed = False
                except openai.APIError as e:
                    error_msg = f"OpenAI API error: {str(e)}"
                    print(error_msg)
                    result.llm_response = error_msg
                    result.llm_processed = False
                except Exception as e:
                    error_msg = f"LLM processing error: {str(e)}"
                    print(error_msg)
                    # Still return the transcription even if LLM processing fails
                    result.llm_response = error_msg
                    result.llm_processed = False
            
            return result
        except Exception as e:
            error_msg = f"Error during transcription processing: {str(e)}"
            print(error_msg)
            raise
