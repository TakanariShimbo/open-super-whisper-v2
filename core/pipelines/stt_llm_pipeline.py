"""
Speech-to-Text and LLM Processing Pipeline

This module provides a unified processing pipeline that integrates
both speech-to-text transcription and LLM processing in a seamless way.
"""

# Standard library imports
from typing import Optional, Callable

# Local application imports
from ..stt.stt_processor import STTProcessor
from ..llm.llm_processor import LLMProcessor
from ..recorder.audio_recorder import AudioRecorder
from ..utils.instruction_set import InstructionSet
from .pipeline_result import PipelineResult


class STTLLMPipeline:
    """
    Unified pipeline for STT and LLM processing.
    
    This class combines STTProcessor and LLMProcessor to provide
    a seamless processing pipeline, with optional LLM processing.
    """
    
    def __init__(self, api_key):
        """
        Initialize the STTLLMPipeline.
        
        Parameters
        ----------
        api_key : str
            API key.
            
        Raises
        ------
        ValueError
            If no API key is provided and none is found in environment variables.
        """
        # Initialize components
        self.stt_processor = STTProcessor(api_key=api_key)
        self.llm_processor = LLMProcessor(api_key=api_key)
        self.audio_recorder = AudioRecorder()
        
        # Processing state
        self.is_llm_processing_enabled = False
    
    @property
    def is_recording(self) -> bool:
        """Check if the audio recorder is currently recording."""
        return self.audio_recorder.is_recording
    
    def enable_llm_processing(self, enabled: bool = True) -> None:
        """
        Enable or disable LLM processing.
        
        Parameters
        ----------
        enabled : bool, optional
            Whether to enable LLM processing, by default True.
        """
        self.is_llm_processing_enabled = enabled

    def apply_instruction_set(self, selected_set: InstructionSet) -> None:
        """Apply an instruction set to the pipeline."""
        # Apply vocabulary
        self.stt_processor.clear_custom_vocabulary()
        self.stt_processor.set_custom_vocabulary(selected_set.stt_vocabulary)
        
        # Apply transcription instructions
        self.stt_processor.clear_system_instruction()
        self.stt_processor.set_system_instruction(selected_set.stt_instructions)
        
        # Set whisper model
        if selected_set.stt_model:
            self.stt_processor.set_model(selected_set.stt_model)
        
        # LLM settings
        self.enable_llm_processing(selected_set.llm_enabled)
        
        # Set LLM model
        if selected_set.llm_model:
            self.llm_processor.set_model(selected_set.llm_model)
        
        # Apply LLM instructions
        self.llm_processor.clear_system_instruction()
        self.llm_processor.set_system_instruction(selected_set.llm_instructions)
        
    def start_recording(self) -> None:
        """Start recording audio from the microphone."""
        self.audio_recorder.start_recording()

    def stop_recording(self) -> str:
        """Stop recording and return the audio file path."""
        return self.audio_recorder.stop_recording()
        
    def stop_recording_and_process(
            self,
            language: Optional[str] = None,
            clipboard_text: Optional[str] = None,
            clipboard_image: Optional[bytes] = None,
            stream_callback: Optional[Callable[[str], None]] = None,
        ) -> PipelineResult:
        """Stop recording and immediately process the recorded audio."""
        if not self.audio_recorder.is_recording:
            raise RuntimeError("No recording is in progress.")
        
        # Stop recording and get the audio file path
        audio_file = self.audio_recorder.stop_recording()
        
        if not audio_file:
            raise RuntimeError("Failed to save recording.")
        
        # Process the audio file
        return self.process(audio_file, language, clipboard_text, clipboard_image, stream_callback)
    
    def _prepare_prompt(self, transcription: str, clipboard_text: Optional[str] = None, 
                        clipboard_image: Optional[bytes] = None) -> str:
        """Prepare the prompt for LLM processing based on available inputs."""
        # Start with just the transcription
        prompt = transcription
        
        # Add clipboard text if provided
        if clipboard_text and not clipboard_image:
            prompt = f"Clipboard Content:\n{clipboard_text}\n\nTranscription:\n{transcription}"
        
        # Add image context if there's an image but no clipboard text
        if not clipboard_text and clipboard_image:
            prompt = f"Analyze this image along with the following.\n\nTranscription:\n{transcription}"

        # Add both clipboard text and image context if both are provided
        if clipboard_text and clipboard_image:
            prompt = f"Analyze this image along with the following.\n\nClipboard Content:\n{clipboard_text}\n\nTranscription:\n{transcription}"
        
        return prompt
    
    def _process_with_text(self, prompt: str, clipboard_image: Optional[bytes] = None,
                           stream_callback: Optional[Callable[[str], None]] = None) -> str:
        """Process text through LLM with appropriate method based on parameters."""
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
    
    def process(
        self, 
        audio_file_path: str, 
        language: Optional[str] = None, 
        clipboard_text: Optional[str] = None, 
        clipboard_image: Optional[bytes] = None,
        stream_callback: Optional[Callable[[str], None]] = None,
    ) -> PipelineResult:
        """Process an audio file with transcription and optional LLM processing."""
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