"""
Speech-to-Text Processor

This module provides a complete implementation for speech-to-text processing.
Includes support for processing large audio files by splitting them into smaller chunks.
"""

import os
import time
from pathlib import Path

import openai

from .stt_model_manager import STTModelManager
from .audio_chunker import AudioChunker


class STTProcessor:
    """
    Implementation of speech-to-text processing.
    
    This class provides methods to transcribe audio files using
    speech-to-text APIs, with support for custom vocabulary, transcription instructions,
    and language selection.
        
    Examples
    --------
    Basic transcription:
    
    >>> from core.api.api_client_factory import APIClientFactory
    >>> is_successful, client = APIClientFactory.create_client("your_api_key")
    >>> processor = STTProcessor(client)
    >>> transcription = processor.transcribe_file_with_chunks("recording.wav")
    >>> print(transcription[:100])
    Hello, welcome to the meeting. Today we'll be discussing the quarterly results...
    
    Using custom vocabulary:
    
    >>> from core.api.api_client_factory import APIClientFactory
    >>> is_successful, client = APIClientFactory.create_client("your_api_key")
    >>> processor = STTProcessor(client)
    >>> processor.set_custom_vocabulary("PyTorch, TensorFlow, scikit-learn, BERT")
    >>> transcription = processor.transcribe_file_with_chunks("tech_talk.wav")
    """

    # Use model manager for available models
    AVAILABLE_MODELS = STTModelManager.to_api_format()
    DEFAULT_MODEL_ID = STTModelManager.get_default_model().id
    MAX_RETRIES = 2
    REQUEST_TIMEOUT = 60  # seconds
    CONTEXT_MAX_WORDS = 20  # Maximum words to include from previous context
    
    def __init__(self, client: openai.OpenAI):
        """
        Initialize the STTProcessor.
        
        Parameters
        ----------
        client : openai.OpenAI
            API client to use.
        """
        self._client = client
        self._model_id = self.DEFAULT_MODEL_ID
        self._custom_vocabulary: str = ""
        self._system_instruction: str = ""
    
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
        # Basic validation that model exists
        available_models = [model["id"] for model in self.AVAILABLE_MODELS]
        if model_id not in available_models:
            available_model_names = ", ".join(available_models[:5]) + "..."
            raise ValueError(f"Unknown model ID: {model_id}. Available models include: {available_model_names}")
            
        self._model_id = model_id
    
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
        self._custom_vocabulary = vocabulary
    
    def clear_custom_vocabulary(self) -> None:
        """
        Clear custom vocabulary.
        
        This removes the previously set custom vocabulary from the processor.
        """
        self._custom_vocabulary = ""
    
    def set_system_instruction(self, instruction: str) -> None:
        """
        Set system instruction to control transcription behavior.
        
        Parameters
        ----------
        instruction : str
            Instruction string.
        """
        self._system_instruction = instruction
    
    def clear_system_instruction(self) -> None:
        """
        Clear system instruction.
        
        This removes the previously set instruction from the processor.
        """
        self._system_instruction = ""
    
    def _create_system_prompt(self, context: str | None = None) -> str | None:
        """
        Create a system prompt with vocabulary, instruction, and optional context.
        
        Parameters
        ----------
        context : str, optional
            Context from previous transcription, by default None
        
        Returns
        -------
        str | None
            Combined prompt string, or None if no parts exist.
        """
        prompt_parts = []
        
        # Add custom vocabulary
        if self._custom_vocabulary:
            prompt_parts.append(f"Vocabulary: {self._custom_vocabulary}")
        
        # Add system instruction
        if self._system_instruction:
            prompt_parts.append(f"Instructions: {self._system_instruction}")
            
        # Add context if provided
        if context:
            prompt_parts.append(f"Context: {context}")
        
        # Return None if no parts, otherwise join with space
        return None if not prompt_parts else " ".join(prompt_parts)
    
    def _build_transcription_params(self, language: str | None = None, 
                                    context: str | None = None) -> dict[str, str]:
        """
        Build parameters for transcription API call.
        
        Parameters
        ----------
        language : str | None, optional
            Language code, by default None
        context : str | None, optional
            Context from previous chunk, by default None
            
        Returns
        -------
        dict[str, str]
            Dictionary of parameters for API call
        """
        # Build base parameters
        params = {
            "model": self._model_id,
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
    
    def _transcribe_with_api(self, file_path: str, params: dict[str, str], 
                           retry_count: int = 0) -> str:
        """
        Make API call to transcribe audio file.
        
        Parameters
        ----------
        file_path : str
            Path to audio file
        params : dict[str, str]
            Parameters for API call
        retry_count : int, optional
            Current retry attempt, by default 0
            
        Returns
        -------
        str
            Transcription result
            
        Raises
        ------
        openai.APIError
            If the API call fails after all retries
        """
        try:
            with open(file_path, "rb") as audio_file:
                response = self._client.audio.transcriptions.create(
                    file=audio_file,
                    **params
                )
            
            return str(response)
            
        except (openai.APIError, openai.APITimeoutError) as e:
            # Handle retries
            if retry_count < self.MAX_RETRIES:
                # Exponential backoff
                backoff_time = 2 ** retry_count
                time.sleep(backoff_time)
                return self._transcribe_with_api(file_path, params, retry_count + 1)
            else:
                # Reached max retries, re-raise the exception
                raise
    
    def _extract_context(self, transcription: str, max_words: int = CONTEXT_MAX_WORDS) -> str:
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
    
    def _combine_chunk_transcriptions(self, transcriptions: list[str]) -> str:
        """
        Combine multiple chunk transcriptions into a single coherent text.
        
        Parameters
        ----------
        transcriptions : list[str]
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
    
    def transcribe_file_with_chunks(self, audio_file_path: str, language: str | None = None) -> str:
        """
        Transcribe an audio file.
        
        This method handles audio files of any size, automatically applying chunking
        for processing.
        
        Parameters
        ----------
        audio_file_path : str
            Path to the audio file to transcribe.
        language : str | None, optional
            Language code (e.g., "en", "ja"), or None for auto-detection.
            
        Returns
        -------
        str
            Transcribed text.
            
        Raises
        ------
        FileNotFoundError
            If the audio file doesn't exist.
        ValueError
            If the file has an unsupported format.
        """
        
        # Validate file
        path = Path(audio_file_path)
        if not path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_file_path}")

        # Get file size for logging only
        file_size_mb = os.path.getsize(audio_file_path) / (1024 * 1024)
        print(f"Processing file: {file_size_mb:.2f}MB")
        
        # Chunk audio file
        chunker = AudioChunker()
        
        try:
            # Split into chunks
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
            
            # Clean up temporary files
            chunker.remove_temp_chunks()
            
            return result
            
        except Exception as e:
            # Clean up temporary files on error too
            try:
                chunker.remove_temp_chunks()
            except:
                pass
            
            # Re-raise the exception
            raise
