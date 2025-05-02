"""
Speech-to-Text and LLM Processing Pipeline

This module provides a unified processing pipeline that integrates
both speech-to-text transcription and LLM processing in a seamless way.
"""

import os
from typing import Optional, Callable

from ..stt.stt_processor import STTProcessor
from ..llm.llm_processor import LLMProcessor
from .pipeline_result import PipelineResult


class STTLLMPipeline:
    """
    Unified pipeline for speech-to-text and LLM processing.
    
    This class combines STTProcessor and LLMProcessor to provide
    a seamless processing pipeline, with optional LLM processing.
    """
    
    def __init__(self, api_key, stt_model_id: str = "gpt-4o-transcribe", llm_model_id: str = "gpt-4o"):
        """
        Initialize the STTLLMPipeline.
        
        Parameters
        ----------
        api_key : str
            API key.
        stt_model_id : str, optional
            Speech-to-text model to use, by default "gpt-4o-transcribe".
        llm_model_id : str, optional
            LLM model to use, by default "gpt-4o".
            
        Raises
        ------
        ValueError
            If no API key is provided and none is found in environment variables.
        """
        # Initialize components
        self.stt_processor = STTProcessor(api_key=api_key, model_id=stt_model_id)
        self.llm_processor = LLMProcessor(api_key=api_key, model_id=llm_model_id)
        
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
    
    # STT processor delegation methods
    def set_stt_model(self, model_id: str) -> None:
        """Set the speech-to-text model."""
        self.stt_processor.set_model(model_id)
    
    def set_custom_vocabulary(self, vocabulary: str) -> None:
        """
        Set custom vocabulary for transcription.
        
        Parameters
        ----------
        vocabulary : str
            Custom vocabulary words/phrases.
        """
        self.stt_processor.set_custom_vocabulary(vocabulary)
    
    def clear_custom_vocabulary(self) -> None:
        """Clear custom vocabulary for transcription."""
        self.stt_processor.clear_custom_vocabulary()
    
    def set_transcription_instruction(self, instruction: str) -> None:
        """
        Set system instruction for transcription.
        
        Parameters
        ----------
        instruction : str
            Instruction for transcription.
        """
        self.stt_processor.set_system_instruction(instruction)
    
    def clear_transcription_instruction(self) -> None:
        """Clear system instruction for transcription."""
        self.stt_processor.clear_system_instruction()
    
    # LLM processor delegation methods
    def set_llm_model(self, model_id: str) -> None:
        """Set the LLM model."""
        self.llm_processor.set_model(model_id)
    
    def set_llm_instruction(self, instruction: str) -> None:
        """
        Set system instruction for LLM processing.
        
        Parameters
        ----------
        instruction : str
            Instruction for LLM.
        """
        self.llm_processor.set_system_instruction(instruction)
    
    def clear_llm_instruction(self) -> None:
        """Clear system instruction for LLM processing."""
        self.llm_processor.clear_system_instruction()
    
    def _prepare_prompt(self, transcription: str, clipboard_text: Optional[str] = None, 
                        clipboard_image: Optional[bytes] = None) -> str:
        """
        Prepare the prompt for LLM processing based on available inputs.
        
        Parameters
        ----------
        transcription : str
            Transcribed text from audio.
        clipboard_text : Optional[str], optional
            Text from clipboard, by default None.
        clipboard_image : Optional[bytes], optional
            Image data from clipboard, by default None.
            
        Returns
        -------
        str
            Formatted prompt for LLM.
        """
        # Start with just the transcription
        prompt = transcription
        
        # Add clipboard text if provided
        if clipboard_text:
            prompt = f"Clipboard Content:\n{clipboard_text}\n\nTranscription:\n{transcription}"
        
        # Add image context if there's an image but no clipboard text
        if clipboard_image and not clipboard_text:
            prompt = f"Analyze this image along with the following transcription:\n\n{transcription}"
        
        return prompt
    
    def _process_with_text(self, prompt: str, clipboard_image: Optional[bytes] = None,
                           stream_callback: Optional[Callable[[str], None]] = None) -> str:
        """
        Process text through LLM with appropriate method based on parameters.
        
        Parameters
        ----------
        prompt : str
            Text prompt to process.
        clipboard_image : Optional[bytes], optional
            Image data to include in processing, by default None.
        stream_callback : Optional[Callable[[str], None]], optional
            Callback for streaming responses, by default None.
            
        Returns
        -------
        str
            LLM response.
        """
        # Determine if we're using streaming
        if stream_callback:
            if clipboard_image:
                return self.llm_processor.process_text_with_stream(prompt, stream_callback, clipboard_image)
            else:
                return self.llm_processor.process_text_with_stream(prompt, stream_callback)
        else:
            if clipboard_image:
                return self.llm_processor.process_text(prompt, clipboard_image)
            else:
                return self.llm_processor.process_text(prompt)
    
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
        """
        # Perform transcription
        transcription = self.stt_processor.transcribe_file_with_chunks(audio_file_path, language)
        
        # Create result object
        result = PipelineResult(transcription=transcription)
        
        # If LLM is enabled, process the transcription
        if self.is_llm_processing_enabled:
            # Prepare the prompt
            prompt = self._prepare_prompt(transcription, clipboard_text, clipboard_image)
            
            # Process with LLM
            llm_response = self._process_with_text(prompt, clipboard_image, stream_callback)
            
            # Update result
            result.llm_response = llm_response
            result.llm_processed = True
        
        return result