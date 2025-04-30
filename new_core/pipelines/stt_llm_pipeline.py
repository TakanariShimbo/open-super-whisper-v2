"""
Speech-to-Text and LLM Processing Pipeline

This module provides a unified processing pipeline that integrates
both speech-to-text transcription and LLM processing in a seamless way.
"""

import os
from typing import Optional, List, Union, Callable
import openai

from ..stt.stt_processor import STTProcessor
from ..llm.llm_processor import LLMProcessor
from .pipeline_result import PipelineResult


class STTLLMPipeline:
    """
    Unified pipeline for speech-to-text and LLM processing.
    
    This class combines STTProcessor and LLMProcessor to provide
    a seamless processing pipeline, with optional LLM processing.
    """
    
    def __init__(self, api_key: str = None, stt_model_id: str = "gpt-4o-transcribe", llm_model_id: str = "gpt-4o"):
        """
        Initialize the STTLLMPipeline.
        
        Parameters
        ----------
        api_key : str, optional
            API key, by default None. If None, tries to get from environment.
        stt_model_id : str, optional
            Speech-to-text model to use, by default "gpt-4o-transcribe".
        llm_model_id : str, optional
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
        self.stt_processor = STTProcessor(api_key=self.api_key, model_id=stt_model_id)
        self.llm_processor = LLMProcessor(api_key=self.api_key, model_id=llm_model_id)
        
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
        self.stt_processor.set_api_key(api_key)
        self.llm_processor.set_api_key(api_key)
    
    # STT processor delegation methods
    def set_stt_model(self, model_id: str) -> None:
        """Set the speech-to-text model."""
        self.stt_processor.set_model(model_id)
    
    def add_custom_vocabulary(self, vocabulary: Union[str, List[str]]) -> None:
        """Add custom vocabulary for transcription."""
        self.stt_processor.add_custom_vocabulary(vocabulary)
    
    def clear_custom_vocabulary(self) -> None:
        """Clear custom vocabulary for transcription."""
        self.stt_processor.clear_custom_vocabulary()
    
    def add_transcription_instruction(self, instructions: Union[str, List[str]]) -> None:
        """Add system instructions for transcription."""
        self.stt_processor.add_transcription_instruction(instructions)
    
    def clear_transcription_instructions(self) -> None:
        """Clear system instructions for transcription."""
        self.stt_processor.clear_transcription_instructions()
    
    # LLM processor delegation methods
    def set_llm_model(self, model_id: str) -> None:
        """Set the LLM model."""
        self.llm_processor.set_model(model_id)
    
    def add_llm_instruction(self, instructions: Union[str, List[str]]) -> None:
        """Add system instructions for LLM processing."""
        self.llm_processor.add_system_instruction(instructions)
    
    def clear_llm_instructions(self) -> None:
        """Clear system instructions for LLM processing."""
        self.llm_processor.clear_system_instructions()
    
    def process(self, audio_file_path: str, language: Optional[str] = None, 
                clipboard_text: Optional[str] = None, clipboard_image: Optional[bytes] = None,
                stream_callback: Optional[Callable[[str], None]] = None) -> PipelineResult:
        """
        Process an audio file with transcription and optional LLM processing.
        
        Parameters
        ----------
        audio_file_path : str
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
        PipelineResult
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
            If rate limits are exceeded.
        Exception
            For any other unexpected errors during processing.
        """
        # Check if file exists
        if not os.path.exists(audio_file_path):
            error_msg = f"Audio file not found: {audio_file_path}"
            print(error_msg)
            raise FileNotFoundError(error_msg)
        
        try:
            # Perform transcription - handles both small and large files
            transcription = self.stt_processor.transcribe(audio_file_path, language)
            
            # Create result object
            result = PipelineResult(transcription=transcription)
            
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
                            llm_response = self.llm_processor.process_with_stream(prompt, stream_callback, clipboard_image)
                        else:
                            # Process text only with streaming
                            llm_response = self.llm_processor.process_with_stream(prompt, stream_callback)
                    else:
                        # Use non-streaming API
                        if clipboard_image:
                            # Process with image
                            llm_response = self.llm_processor.process_text(prompt, clipboard_image)
                        else:
                            # Process text only
                            llm_response = self.llm_processor.process_text(prompt)
                    
                    result.llm_response = llm_response
                    result.llm_processed = True
                except openai.AuthenticationError as e:
                    error_msg = f"API authentication error: {str(e)}"
                    print(error_msg)
                    result.llm_response = error_msg
                    result.llm_processed = False
                except openai.RateLimitError as e:
                    error_msg = f"API rate limit exceeded: {str(e)}"
                    print(error_msg)
                    result.llm_response = error_msg
                    result.llm_processed = False
                except openai.BadRequestError as e:
                    error_msg = f"API request was invalid: {str(e)}"
                    print(error_msg)
                    result.llm_response = error_msg
                    result.llm_processed = False
                except openai.APIError as e:
                    error_msg = f"API error: {str(e)}"
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
