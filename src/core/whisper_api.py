"""
Whisper API Transcription Interface

This module provides an interface for the OpenAI Whisper API to transcribe audio.
"""

from typing import List, Dict, Any, Optional


class WhisperTranscriber:
    """
    Interface for OpenAI Whisper API transcription.
    
    This class provides methods to transcribe audio files using the
    OpenAI Whisper API, with support for custom vocabulary, system instructions,
    and language selection.
    """
    
    def __init__(self, api_key: str = None, model: str = "gpt-4o-transcribe"):
        """
        Initialize the WhisperTranscriber.
        
        Parameters
        ----------
        api_key : str, optional
            OpenAI API key, by default None.
        model : str, optional
            Whisper model to use, by default "gpt-4o-transcribe".
            
        Raises
        ------
        ValueError
            If no API key is provided and none is found in environment variables.
        """
        if not api_key:
            raise ValueError("API key is required")
        
        self.api_key = api_key
        self.model = model
        self.custom_vocabulary: List[str] = []
        self.system_instructions: List[str] = []
    
    @staticmethod
    def get_available_models() -> List[Dict[str, str]]:
        """
        Get a list of available Whisper models.
        
        Returns
        -------
        List[Dict[str, str]]
            List of dictionaries with model information (id, name, description).
        """
        return [
            {
                "id": "whisper-1",
                "name": "Whisper-1",
                "description": "Original open-source Whisper model"
            },
            {
                "id": "gpt-4o-transcribe",
                "name": "GPT-4o Transcribe",
                "description": "High-performance transcription model"
            },
            {
                "id": "gpt-4o-mini-transcribe",
                "name": "GPT-4o Mini Transcribe",
                "description": "Lightweight and fast transcription model"
            }
        ]
    
    def set_model(self, model: str) -> None:
        """
        Set the Whisper model to use.
        
        Parameters
        ----------
        model : str
            Model ID to use for transcription.
        """
        self.model = model
    
    def add_custom_vocabulary(self, vocabulary: List[str]) -> None:
        """
        Add custom vocabulary to improve transcription accuracy.
        
        Parameters
        ----------
        vocabulary : List[str]
            List of custom vocabulary words or phrases.
        """
        self.custom_vocabulary.extend(vocabulary)
    
    def clear_custom_vocabulary(self) -> None:
        """Clear all custom vocabulary."""
        self.custom_vocabulary = []
    
    def add_system_instruction(self, instructions: List[str]) -> None:
        """
        Add system instructions to control transcription behavior.
        
        Parameters
        ----------
        instructions : List[str]
            List of instruction strings.
        """
        self.system_instructions.extend(instructions)
    
    def clear_system_instructions(self) -> None:
        """Clear all system instructions."""
        self.system_instructions = []
    
    def transcribe(self, audio_file: str, language: Optional[str] = None) -> str:
        """
        Transcribe an audio file.
        
        Parameters
        ----------
        audio_file : str
            Path to the audio file to transcribe.
        language : Optional[str], optional
            Language code to use, or None for auto-detection, by default None.
            
        Returns
        -------
        str
            Transcribed text.
            
        Raises
        ------
        Exception
            If transcription fails.
        """
        # This is a placeholder implementation - the actual API call
        # would be implemented here in a real application
        
        # For simulation purposes
        file_base = audio_file.split("/")[-1]
        lang_str = f"in {language}" if language else "with auto-detection"
        voc_str = f"with {len(self.custom_vocabulary)} vocabulary items" if self.custom_vocabulary else ""
        inst_str = f"with {len(self.system_instructions)} instructions" if self.system_instructions else ""
        
        return (
            f"Simulated transcription of {file_base} using {self.model} {lang_str} {voc_str} {inst_str}. "
            "This is a placeholder for the actual transcription API integration."
        )
    
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
