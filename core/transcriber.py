"""
Whisper Transcription Interface

This module provides a complete implementation for the OpenAI Whisper API to transcribe audio.
Includes support for transcribing large audio files by splitting them into smaller chunks.
"""

import os
import json
from pathlib import Path
import openai
from typing import List, Dict, Any, Optional, Union

# Import chunking and progress tracking modules
from core.audio_chunker import AudioChunker
from core.progress_tracker import TranscriptionProgressTracker

# Import model data from core.models
from core.models.whisper import WhisperModelManager


class WhisperTranscriber:
    """
    Implementation of OpenAI Whisper API transcription.
    
    This class provides methods to transcribe audio files using the
    OpenAI Whisper API, with support for custom vocabulary, system instructions,
    and language selection.
    """
    
    # Use model manager for available models
    AVAILABLE_MODELS = WhisperModelManager.to_api_format()
    
    def __init__(self, api_key: str = None, model: str = "whisper-1"):
        """
        Initialize the WhisperTranscriber.
        
        Parameters
        ----------
        api_key : str, optional
            OpenAI API key, by default None. If None, tries to get from environment.
        model : str, optional
            Whisper model to use, by default "whisper-1".
            
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
        
        # Set model and initialize custom vocabulary and instructions
        self.model = model
        self.custom_vocabulary: List[str] = []
        self.system_instructions: List[str] = []
    
    @classmethod
    def get_available_models(cls) -> List[Dict[str, str]]:
        """
        Get a list of available Whisper models.
        
        Returns
        -------
        List[Dict[str, str]]
            List of dictionaries with model information (id, name, description).
        """
        return cls.AVAILABLE_MODELS
    
    def set_model(self, model: str) -> None:
        """
        Set the Whisper model to use.
        
        Parameters
        ----------
        model : str
            Model ID to use for transcription.
        """
        self.model = model
    
    def add_custom_vocabulary(self, vocabulary: Union[str, List[str]]) -> None:
        """
        Add custom vocabulary to improve transcription accuracy.
        
        Parameters
        ----------
        vocabulary : Union[str, List[str]]
            Custom vocabulary word/phrase or list of words/phrases.
        """
        if isinstance(vocabulary, str):
            vocabulary = [vocabulary]
        self.custom_vocabulary.extend(vocabulary)
    
    def clear_custom_vocabulary(self) -> None:
        """Clear all custom vocabulary."""
        self.custom_vocabulary = []
    
    def get_custom_vocabulary(self) -> List[str]:
        """
        Get the current custom vocabulary list.
        
        Returns
        -------
        List[str]
            List of custom vocabulary items.
        """
        return self.custom_vocabulary
    
    def add_system_instruction(self, instructions: Union[str, List[str]]) -> None:
        """
        Add system instructions to control transcription behavior.
        
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
    
    def _build_prompt(self) -> Optional[str]:
        """
        Build a prompt with vocabulary and instructions.
        
        Returns
        -------
        Optional[str]
            Combined prompt string, or None if no vocabulary or instructions exist.
        """
        prompt_parts = []
        
        # Add custom vocabulary
        if self.custom_vocabulary:
            prompt_parts.append("Vocabulary: " + ", ".join(self.custom_vocabulary))
        
        # Add system instructions
        if self.system_instructions:
            prompt_parts.append("Instructions: " + ". ".join(self.system_instructions))
        
        # Return None if no parts, otherwise join with space
        return None if not prompt_parts else " ".join(prompt_parts)
    
    def transcribe(self, audio_file: str, language: Optional[str] = None, 
                  response_format: str = "text") -> Union[str, Dict]:
        """
        Transcribe an audio file using OpenAI's Whisper API.
        
        Parameters
        ----------
        audio_file : str
            Path to the audio file to transcribe.
        language : Optional[str], optional
            Language code (e.g., "en", "ja"), or None for auto-detection.
        response_format : str, optional
            Response format: "text", "json", "verbose_json", or "vtt".
            
        Returns
        -------
        Union[str, Dict]
            Transcribed text or dictionary depending on response_format.
            
        Raises
        ------
        Exception
            If transcription fails.
        """
        try:
            # Check if file exists
            audio_path = Path(audio_file)
            if not audio_path.exists():
                raise FileNotFoundError(f"Audio file not found: {audio_file}")
            
            # Build API call parameters
            params = {
                "model": self.model,
                "response_format": response_format,
            }
            
            # Add language if specified
            if language:
                params["language"] = language
                
            # Add custom prompt if available
            prompt = self._build_prompt()
            if prompt:
                params["prompt"] = prompt
            
            # Make API call
            with open(audio_path, "rb") as audio:
                response = self.client.audio.transcriptions.create(
                    file=audio,
                    **params
                )
                
            # Process response based on format
            if response_format == "json" or response_format == "verbose_json":
                return json.loads(str(response))
            else:
                return str(response)
        
        except Exception as e:
            error_msg = f"Error occurred during transcription: {str(e)}"
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
    
    def transcribe_large_file(self, audio_file: str, language: Optional[str] = None, 
                           response_format: str = "text") -> Union[str, Dict]:
        """
        Transcribe a large audio file by splitting it into smaller chunks.
        Handles files larger than the OpenAI API's 25MB limit.
        
        Parameters
        ----------
        audio_file : str
            Path to the audio file to transcribe.
        language : Optional[str], optional
            Language code (e.g., "en", "ja"), or None for auto-detection.
        response_format : str, optional
            Response format: "text", "json", "verbose_json", or "vtt".
            
        Returns
        -------
        Union[str, Dict]
            Transcribed text or dictionary depending on response_format.
            
        Raises
        ------
        Exception
            If transcription fails.
        """
        try:
            # Check if file exists
            audio_path = Path(audio_file)
            if not audio_path.exists():
                raise FileNotFoundError(f"Audio file not found: {audio_file}")
            
            # Check file size in MB
            file_size_mb = os.path.getsize(audio_file) / (1024 * 1024)
            
            # If file is under 25MB, process it directly with standard method
            if file_size_mb <= 25:
                print(f"File size is {file_size_mb:.2f}MB, processing directly...")
                return self.transcribe(audio_file, language, response_format)
            
            print(f"File size is {file_size_mb:.2f}MB, splitting into chunks...")
            
            # Initialize audio chunker and progress tracker
            chunker = AudioChunker()
            progress_tracker = TranscriptionProgressTracker()
            
            # If this file has already been fully processed, return the merged result
            if progress_tracker.is_completed():
                print("Found completed transcription in progress file, returning cached result...")
                return self._merge_transcriptions(list(progress_tracker.get_all_results().values()))
            
            # Split audio file into chunks
            chunk_paths = chunker.split_audio_file(audio_file)
            if not chunk_paths:
                raise ValueError("Failed to split audio file into chunks")
                
            print(f"Split into {len(chunk_paths)} chunks, starting transcription...")
            
            transcriptions = []
            
            # Process each chunk
            for i, chunk_path in enumerate(chunk_paths):
                # Check if this chunk has already been processed
                if progress_tracker.is_chunk_processed(chunk_path):
                    print(f"Chunk {i+1}/{len(chunk_paths)} already processed, using cached result...")
                    transcriptions.append(progress_tracker.get_chunk_result(chunk_path))
                    continue
                
                print(f"Processing chunk {i+1}/{len(chunk_paths)}...")
                
                # Use previous chunk's end as context for better continuity
                prompt = self._build_prompt()
                if i > 0 and transcriptions:
                    # Extract last few words from previous transcription
                    last_transcript = transcriptions[-1]
                    words = last_transcript.split()
                    # Use up to 20 last words as context
                    context = " ".join(words[-20:]) if len(words) > 20 else last_transcript
                    
                    # Combine with any existing prompt
                    if prompt:
                        prompt = f"{prompt} Context: {context}"
                    else:
                        prompt = f"Context: {context}"
                
                # Process the chunk
                params = {
                    "model": self.model,
                    "response_format": "text",  # Always use text for chunks
                }
                
                if language:
                    params["language"] = language
                    
                if prompt:
                    params["prompt"] = prompt
                
                try:
                    with open(chunk_path, "rb") as audio:
                        response = self.client.audio.transcriptions.create(
                            file=audio,
                            **params
                        )
                    
                    chunk_result = str(response)
                    
                    # Save result and add to list
                    transcriptions.append(chunk_result)
                    progress_tracker.save_chunk_result(chunk_path, chunk_result)
                    
                except Exception as e:
                    print(f"Error processing chunk {i+1}: {str(e)}")
                    # Continue with next chunk even if this one fails
            
            # Merge transcriptions
            if not transcriptions:
                raise ValueError("No chunks were successfully transcribed")
                
            merged_result = self._merge_transcriptions(transcriptions)
            
            # Mark as completed and clean up
            progress_tracker.mark_completed()
            
            # Only clean up chunks if the entire process completed successfully
            if all(progress_tracker.is_chunk_processed(chunk) for chunk in chunk_paths):
                chunker.cleanup_chunks()
            
            # Format the result according to requested response_format
            if response_format == "text":
                return merged_result
            elif response_format in ["json", "verbose_json"]:
                return {"text": merged_result}
            elif response_format == "vtt":
                # Simple conversion to VTT format
                lines = merged_result.split(". ")
                vtt_output = "WEBVTT\n\n"
                for i, line in enumerate(lines):
                    if line.strip():
                        vtt_output += f"{i*5:02d}:00.000 --> {i*5+5:02d}:00.000\n{line.strip()}.\n\n"
                return vtt_output
            else:
                return merged_result
            
        except Exception as e:
            error_msg = f"Error occurred during large file transcription: {str(e)}"
            print(error_msg)
            return f"Error: {str(e)}"
    
    def _merge_transcriptions(self, transcriptions: List[str]) -> str:
        """
        Merge multiple chunk transcriptions into a single coherent text.
        
        Parameters
        ----------
        transcriptions : List[str]
            List of transcription results from individual chunks
            
        Returns
        -------
        str
            Merged transcription text
        """
        if not transcriptions:
            return ""
            
        # Simple joining with space between chunks
        # This could be enhanced with more sophisticated text processing
        # to improve the flow between chunks
        merged_text = " ".join(transcriptions)
        
        # Clean up any double spaces that might have been introduced
        merged_text = " ".join(merged_text.split())
        
        return merged_text
