"""
OpenAI Whisper Transcription Interface

This module provides a complete implementation for the OpenAI Whisper API to transcribe audio.
Includes support for transcribing large audio files by splitting them into smaller chunks.
"""

import os
import json
from pathlib import Path
import openai
from typing import List, Dict, Optional, Union

# Import model data from old_core.models
from old_core.models.whisper import OpenAIWhisperModelManager

# Import chunking and progress tracking modules
from old_core.audio_chunker import AudioChunker
from old_core.progress_tracker import ChunkProgressTracker


class OpenAIWhisperTranscriber:
    """
    Implementation of OpenAI Whisper API transcription.
    
    This class provides methods to transcribe audio files using the
    OpenAI Whisper API, with support for custom terminology, transcription instructions,
    and language selection.
    
    Attributes
    ----------
    openai_api_key : str
        The OpenAI API key used for authentication
    openai_client : openai.OpenAI
        The OpenAI client instance used for API requests
    whisper_model : str
        The Whisper model to use for transcription
    custom_terminology : List[str]
        List of domain-specific terminology to improve transcription accuracy
    whisper_system_instructions : List[str]
        List of instructions to control transcription behavior
    """
    
    # Use model manager for available models
    AVAILABLE_MODELS = OpenAIWhisperModelManager.to_api_format()
    
    def __init__(self, openai_api_key: str = None, whisper_model: str = "gpt-4o-transcribe"):
        """
        Initialize the OpenAIWhisperTranscriber.
        
        Parameters
        ----------
        openai_api_key : str, optional
            OpenAI API key, by default None. If None, tries to get from environment.
        whisper_model : str, optional
            Whisper model to use, by default "gpt-4o-transcribe".
            
        Raises
        ------
        ValueError
            If no API key is provided and none is found in environment variables.
        """
        # Get API key from parameter or environment variable
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        
        if not self.openai_api_key:
            raise ValueError("API key is required. Provide it directly or set OPENAI_API_KEY environment variable.")
        
        # Initialize OpenAI client
        self.openai_client = openai.OpenAI(api_key=self.openai_api_key)
        
        # Set model and initialize custom terminology and instructions
        self.whisper_model = whisper_model
        self.custom_terminology: List[str] = []
        self.whisper_system_instructions: List[str] = []

    def set_whisper_model(self, whisper_model: str) -> None:
        """
        Set the Whisper model to use.
        
        Parameters
        ----------
        whisper_model : str
            Model ID to use for transcription.
            
        Notes
        -----
        The model must be one of the supported models that can be obtained 
        using get_supported_whisper_models().
        """
        self.whisper_model = whisper_model
    
    def add_custom_terminology(self, terminology: Union[str, List[str]]) -> None:
        """
        Add custom terminology to improve transcription accuracy.
        
        Parameters
        ----------
        terminology : Union[str, List[str]]
            Custom terminology word/phrase or list of words/phrases.
            
        Notes
        -----
        This is particularly useful for domain-specific vocabulary, proper nouns,
        or technical terms that may not be properly recognized by default.
        """
        if isinstance(terminology, str):
            terminology = [terminology]
        self.custom_terminology.extend(terminology)
    
    def clear_custom_terminology(self) -> None:
        """
        Clear all custom terminology.
        
        This removes all previously added custom terminology from the transcriber.
        """
        self.custom_terminology = []
    
    
    def add_transcription_instruction(self, instructions: Union[str, List[str]]) -> None:
        """
        Add transcription instructions to control transcription behavior.
        
        Parameters
        ----------
        instructions : Union[str, List[str]]
            Instruction or list of instruction strings.
            
        Notes
        -----
        These instructions guide the Whisper model on how to transcribe the audio.
        Examples include formatting preferences, handling of specific content,
        or guidance on transcription style.
        """
        if isinstance(instructions, str):
            instructions = [instructions]
        self.whisper_system_instructions.extend(instructions)
    
    def clear_transcription_instructions(self) -> None:
        """
        Clear all transcription instructions.
        
        This removes all previously added instructions from the transcriber.
        """
        self.whisper_system_instructions = []
    
    def get_transcription_instructions(self) -> List[str]:
        """
        Get the current list of transcription instructions.
        
        Returns
        -------
        List[str]
            List of instruction strings.
        """
        return self.whisper_system_instructions
    
    def _create_whisper_system_prompt(self) -> Optional[str]:
        """
        Create a system prompt with terminology and instructions.
        
        Returns
        -------
        Optional[str]
            Combined prompt string, or None if no terminology or instructions exist.
            
        Notes
        -----
        This internal method combines custom terminology and system instructions
        into a single prompt string that can be sent to the Whisper API.
        """
        prompt_parts = []
        
        # Add custom terminology
        if self.custom_terminology:
            prompt_parts.append("Vocabulary: " + ", ".join(self.custom_terminology))
        
        # Add system instructions
        if self.whisper_system_instructions:
            prompt_parts.append("Instructions: " + ". ".join(self.whisper_system_instructions))
        
        # Return None if no parts, otherwise join with space
        return None if not prompt_parts else " ".join(prompt_parts)
    
    def transcribe(self, audio_file: str, language: Optional[str] = None, 
                  response_format: str = "text") -> Union[str, Dict]:
        """
        Transcribe an audio file using OpenAI's Whisper API.
        
        This method automatically handles files of any size by splitting larger files 
        into smaller chunks when necessary, and then seamlessly combining the results.
        
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
        FileNotFoundError
            If the audio file does not exist.
        ValueError
            If the audio file cannot be chunked or no chunks were transcribed.
        Exception
            If an unexpected error occurs during transcription.
        
        Notes
        -----
        Files larger than 25MB are automatically split into chunks, transcribed
        separately, and then recombined into a coherent transcript.
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
                
                # Build API call parameters
                params = {
                    "model": self.whisper_model,
                    "response_format": response_format,
                }
                
                # Add language if specified
                if language:
                    params["language"] = language
                    
                # Add custom prompt if available
                prompt = self._create_whisper_system_prompt()
                if prompt:
                    params["prompt"] = prompt
                
                # Make API call
                with open(audio_path, "rb") as audio_file_handle:
                    response = self.openai_client.audio.transcriptions.create(
                        file=audio_file_handle,
                        **params
                    )
                    
                # Process response based on format
                if response_format == "json" or response_format == "verbose_json":
                    return json.loads(str(response))
                else:
                    return str(response)
            
            print(f"File size is {file_size_mb:.2f}MB, splitting into chunks...")
            
            # Initialize audio chunker and progress tracker (memory-only implementation)
            chunker = AudioChunker()
            progress_tracker = ChunkProgressTracker()
            
            # Split audio file into chunks
            audio_chunk_file_paths = chunker.chunk_audio_file(audio_file)
            if not audio_chunk_file_paths:
                raise ValueError("Failed to split audio file into chunks")
                
            print(f"Split into {len(audio_chunk_file_paths)} chunks, starting transcription...")
            
            transcriptions = []
            
            # Process each chunk
            for i, chunk_path in enumerate(audio_chunk_file_paths):
                # Check if this chunk has already been processed
                if progress_tracker.has_chunk_been_processed(chunk_path):
                    print(f"Chunk {i+1}/{len(audio_chunk_file_paths)} already processed, using cached result...")
                    transcriptions.append(progress_tracker.retrieve_chunk_result(chunk_path))
                    continue
                
                print(f"Processing chunk {i+1}/{len(audio_chunk_file_paths)}...")
                
                # Use previous chunk's end as context for better continuity
                prompt = self._create_whisper_system_prompt()
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
                    "model": self.whisper_model,
                    "response_format": "text",  # Always use text for chunks
                }
                
                if language:
                    params["language"] = language
                    
                if prompt:
                    params["prompt"] = prompt
                
                try:
                    with open(chunk_path, "rb") as audio_file_handle:
                        response = self.openai_client.audio.transcriptions.create(
                            file=audio_file_handle,
                            **params
                        )
                    
                    chunk_result = str(response)
                    
                    # Save result and add to list
                    transcriptions.append(chunk_result)
                    progress_tracker.store_chunk_result(chunk_path, chunk_result)
                    
                except Exception as api_error:
                    print(f"Error processing chunk {i+1}: {str(api_error)}")
                    # Continue with next chunk even if this one fails
            
            # Combine transcriptions
            if not transcriptions:
                raise ValueError("No chunks were successfully transcribed")
                
            merged_result = self._combine_chunk_transcriptions(transcriptions)
            
            # Only clean up chunks if all chunks were successfully processed
            if all(progress_tracker.has_chunk_been_processed(chunk) for chunk in audio_chunk_file_paths):
                chunker.remove_temp_chunks()
            
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
            
        except Exception as error:
            error_msg = f"Error occurred during transcription: {str(error)}"
            print(error_msg)
            return f"Error: {str(error)}"
    
    def get_openai_api_key(self) -> str:
        """
        Get the current OpenAI API key.
        
        Returns
        -------
        str
            The current OpenAI API key.
        """
        return self.openai_api_key
    
    def set_openai_api_key(self, openai_api_key: str) -> None:
        """
        Set a new OpenAI API key.
        
        Parameters
        ----------
        openai_api_key : str
            New OpenAI API key to use.
            
        Raises
        ------
        ValueError
            If API key is empty.
            
        Notes
        -----
        This updates both the stored API key and reinitializes the OpenAI client
        with the new key.
        """
        if not openai_api_key:
            raise ValueError("API key cannot be empty")
        
        self.openai_api_key = openai_api_key
        # Update the client with the new API key
        self.openai_client = openai.OpenAI(api_key=self.openai_api_key)
    
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
            
        Notes
        -----
        This method performs basic text merging and cleanup to create a coherent
        transcript from individual chunks. Future versions may implement more
        sophisticated text processing for improved flow between chunks.
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
