"""
Speech-to-Text Processor

This module provides a complete implementation for speech-to-text processing.
Includes support for processing large audio files by splitting them into smaller chunks.
"""

# Standard library imports
import os
from pathlib import Path
from typing import List, Dict, Optional

# Third-party imports
import openai

# Local application imports
from .stt_model_manager import STTModelManager
from .audio_chunker import AudioChunker


class STTProcessor:
    """
    Implementation of speech-to-text processing.
    
    This class provides methods to transcribe audio files using
    speech-to-text APIs, with support for custom vocabulary, transcription instructions,
    and language selection.
    
    Attributes
    ----------
    api_key : str
        The API key used for authentication
    client : openai.OpenAI
        The client instance used for API requests
    model_id : str
        The model to use for transcription
    custom_vocabulary : str
        Domain-specific vocabulary to improve transcription accuracy
    system_instruction : str
        Instruction to control transcription behavior
    """

    # Use model manager for available models
    AVAILABLE_MODELS = STTModelManager.to_api_format()
    
    def __init__(self, api_key: str, model_id: str = "gpt-4o-transcribe"):
        """
        Initialize the STTProcessor.
        
        Parameters
        ----------
        api_key : str
            API key.
        model_id : str, optional
            Model to use, by default "gpt-4o-transcribe".
            
        Raises
        ------
        ValueError
            If API key is invalid.
        """
        # Set API key
        is_valid = self.set_api_key(api_key)
        if not is_valid:
            raise ValueError("Invalid API key. Please provide a valid API key.")
        
        # Set model and initialize custom vocabulary and instruction
        self.model_id = model_id
        self.custom_vocabulary: str = ""
        self.system_instruction: str = ""
    
    def set_api_key(self, api_key: str) -> bool:
        """
        Set a new API key.
        
        Parameters
        ----------
        api_key : str
            New API key to use.
            
        Returns
        -------
        bool
            True if the API key is valid, False otherwise.
        """
        client = openai.OpenAI(api_key=api_key)
        try:
            client.models.list()
        except openai.APIConnectionError:
            return False

        self.api_key = api_key
        self.client = client
        return True
    
    def set_model(self, model_id: str) -> None:
        """
        Set the model to use.
        
        Parameters
        ----------
        model_id : str
            Model ID to use for transcription.
            
        Notes
        -----
        The model must be one of the supported models that can be obtained 
        from the STTModelManager.
        """
        self.model_id = model_id
    
    def set_custom_vocabulary(self, vocabulary: str) -> None:
        """
        Set custom vocabulary to improve transcription accuracy.
        
        Parameters
        ----------
        vocabulary : str
            Custom vocabulary words/phrases.
            
        Notes
        -----
        This is particularly useful for domain-specific vocabulary, proper nouns,
        or technical terms that may not be properly recognized by default.
        """
        self.custom_vocabulary = vocabulary
    
    def clear_custom_vocabulary(self) -> None:
        """
        Clear custom vocabulary.
        
        This removes the previously set custom vocabulary from the processor.
        """
        self.custom_vocabulary = ""
    
    def set_system_instruction(self, instruction: str) -> None:
        """
        Set system instruction to control transcription behavior.
        
        Parameters
        ----------
        instruction : str
            Instruction string.
            
        Notes
        -----
        This instruction guides the model on how to transcribe the audio.
        Examples include formatting preferences, handling of specific content,
        or guidance on transcription style.
        """
        self.system_instruction = instruction
    
    def clear_system_instruction(self) -> None:
        """
        Clear system instruction.
        
        This removes the previously set instruction from the processor.
        """
        self.system_instruction = ""
    
    def _create_system_prompt(self, context: Optional[str] = None) -> Optional[str]:
        """
        Create a system prompt with vocabulary, instruction, and optional context.
        
        Parameters
        ----------
        context : str, optional
            Context from previous transcription, by default None
        
        Returns
        -------
        Optional[str]
            Combined prompt string, or None if no parts exist.
        """
        prompt_parts = []
        
        # Add custom vocabulary
        if self.custom_vocabulary:
            prompt_parts.append(f"Vocabulary: {self.custom_vocabulary}")
        
        # Add system instruction
        if self.system_instruction:
            prompt_parts.append(f"Instructions: {self.system_instruction}")
            
        # Add context if provided
        if context:
            prompt_parts.append(f"Context: {context}")
        
        # Return None if no parts, otherwise join with space
        return None if not prompt_parts else " ".join(prompt_parts)
    
    def _build_transcription_params(self, language: Optional[str] = None, 
                                    context: Optional[str] = None) -> Dict[str, str]:
        """
        Build parameters for transcription API call.
        
        Parameters
        ----------
        language : Optional[str], optional
            Language code, by default None
        context : Optional[str], optional
            Context from previous chunk, by default None
            
        Returns
        -------
        Dict
            Dictionary of parameters for API call
        """
        # Build base parameters
        params = {
            "model": self.model_id,
            "response_format": "text",
        }
        
        # Add language if specified
        if language:
            params["language"] = language
        
        # Add prompt if available (with context if provided)
        prompt = self._create_system_prompt(context)
        if prompt:
            params["prompt"] = prompt
            
        return params
    
    def _transcribe_with_api(self, file_path: str, params: Dict[str, str]) -> str:
        """
        Make API call to transcribe audio file.
        
        Parameters
        ----------
        file_path : str
            Path to audio file
        params : Dict
            Parameters for API call
            
        Returns
        -------
        str
            Transcription result
        """
        with open(file_path, "rb") as audio_file:
            response = self.client.audio.transcriptions.create(
                file=audio_file,
                **params
            )
        
        return str(response)
    
    def _extract_context(self, transcription: str, max_words: int = 20) -> str:
        """
        Extract context from previous transcription.
        
        Parameters
        ----------
        transcription : str
            Previous transcription text
        max_words : int, optional
            Maximum number of words to use, by default 20
            
        Returns
        -------
        str
            Context string
        """
        words = transcription.split()
        return " ".join(words[-max_words:]) if len(words) > max_words else transcription
    
    def _combine_chunk_transcriptions(self, transcriptions: List[str]) -> str:
        """
        Combine multiple chunk transcriptions into a single coherent text.
        
        Parameters
        ----------
        transcriptions : List[str]
            List of transcription results from individual chunks
            
        Returns
        -------
        str
            Combined transcription text
        """
        if not transcriptions:
            return ""
            
        # Simple joining with space between chunks
        merged_text = " ".join(transcriptions)
        
        # Clean up any double spaces that might have been introduced
        merged_text = " ".join(merged_text.split())
        
        return merged_text    
    
    def transcribe_file_with_chunks(self, audio_file_path: str, language: Optional[str] = None) -> str:
        """
        Transcribe an audio file.
        
        This method handles audio files of any size, automatically applying chunking
        for processing.
        
        Parameters
        ----------
        audio_file_path : str
            Path to the audio file to transcribe.
        language : Optional[str], optional
            Language code (e.g., "en", "ja"), or None for auto-detection.
            
        Returns
        -------
        str
            Transcribed text.
        """
        # Validate file
        path = Path(audio_file_path)

        # Get file size for logging only
        file_size_mb = os.path.getsize(audio_file_path) / (1024 * 1024)
        print(f"Processing file: {file_size_mb:.2f}MB")
        
        # Chunk audio file
        chunker = AudioChunker()
        chunks = chunker.chunk_audio_file(str(path))
        print(f"Processing {len(chunks)} chunks...")
        
        # Process all chunks
        transcriptions = []
        
        for i, chunk_path in enumerate(chunks):            
            print(f"Processing chunk {i+1}/{len(chunks)}...")
            
            # Get context from previous chunk if available
            context = None
            if i > 0 and transcriptions:
                context = self._extract_context(transcriptions[-1])
            
            # Process chunk
            params = self._build_transcription_params(language, context)
            result = self._transcribe_with_api(chunk_path, params)
            
            # Store result
            transcriptions.append(result)
        
        # Combine results
        result = self._combine_chunk_transcriptions(transcriptions)
        
        return result
