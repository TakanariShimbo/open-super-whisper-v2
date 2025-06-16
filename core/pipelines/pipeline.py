"""
Speech-to-Text and LLM Processing Pipeline

This module provides a unified processing pipeline that integrates
both speech-to-text transcription and LLM processing in a seamless way.
"""

from typing import Callable
import asyncio

from ..api.api_checker import APIChecker
from ..stt.stt_processor import STTProcessor
from ..llm.llm_processor import LLMProcessor
from ..recorder.audio_recorder import AudioRecorder
from .instruction_set import InstructionSet
from .pipeline_result import PipelineResult


class Pipeline:
    """
    Unified pipeline for STT and LLM processing.

    This class combines STTProcessor and LLMProcessor to provide
    a seamless processing pipeline, with optional LLM processing.
    """

    def __init__(self, openai_api_key: str) -> None:
        """
        Initialize the Pipeline.

        Parameters
        ----------
        openai_api_key : str
            OpenAI API key.

        Raises
        ------
        ValueError
            If no API key is provided and none is found in environment variables.
        """
        # Verify api key and create client
        is_valid = APIChecker.check_openai_api_key(openai_api_key=openai_api_key)
        if not is_valid:
            raise ValueError("Invalid OpenAI API key. Please provide a valid API key.")

        # Initialize components
        self._stt_processor = STTProcessor(openai_api_key=openai_api_key)
        self._llm_processor = LLMProcessor(openai_api_key=openai_api_key)
        self._audio_recorder = AudioRecorder()

        # Processing state flag
        self._is_llm_processing_enabled = False
        self._current_set_name = ""

    @property
    def is_recording(self) -> bool:
        """Check if the audio recorder is currently recording."""
        return self._audio_recorder.is_recording

    def _set_llm_processing(self, enabled: bool = True) -> None:
        """
        Enable or disable LLM processing.

        Parameters
        ----------
        enabled : bool, optional
            Whether to enable LLM processing, by default True.
        """
        self._is_llm_processing_enabled = enabled

    def apply_instruction_set(self, selected_set: InstructionSet) -> None:
        """
        Apply an instruction set to the pipeline.

        Parameters
        ----------
        selected_set : InstructionSet
            The instruction set to apply.
        """
        # Apply vocabulary
        self._stt_processor.set_custom_vocabulary(vocabulary=selected_set.stt_vocabulary)

        # Apply STT instructions
        self._stt_processor.set_system_instruction(instruction=selected_set.stt_instructions)

        # Set whisper model
        self._stt_processor.set_model(model_id=selected_set.stt_model)

        # Set language
        self._stt_processor.set_language(language_code=selected_set.stt_language)

        # LLM settings
        self._set_llm_processing(enabled=selected_set.llm_enabled)

        # Set LLM model
        self._llm_processor.set_model(model_id=selected_set.llm_model)

        # Apply LLM instructions
        self._llm_processor.set_system_instruction(instruction=selected_set.llm_instructions)

        # Apply MCP servers
        self._llm_processor.set_mcp_servers_json_str(json_str=selected_set.llm_mcp_servers_json_str)

        # Apply LLM web search
        self._llm_processor.set_web_search_enabled(is_enabled=selected_set.llm_web_search_enabled)

        # Update current set name
        self._current_set_name = selected_set.name

    def start_recording(self) -> None:
        """
        Start recording audio from the microphone.
        """
        self._audio_recorder.start_recording()

    def stop_recording(self) -> str:
        """
        Stop recording and return the audio file path.

        Returns
        -------
        str
            The path to the audio file.
        """
        return self._audio_recorder.stop_recording()

    def _prepare_prompt(
        self,
        stt_output: str,
        clipboard_text: str | None = None,
    ) -> str:
        """
        Prepare the prompt for LLM processing based on available inputs.

        Parameters
        ----------
        stt_output : str
            The transcription output from STT.
        clipboard_text : str | None, optional
            The text to be added to the clipboard, by default None.

        Returns
        -------
        str
            The prepared prompt.
        """
        # Start with just the STT output
        prompt = f"<speech_to_text>\n{stt_output}\n</speech_to_text>"

        # Add clipboard text if provided
        if clipboard_text:
            prompt = f"<clipboard_text>\n{clipboard_text}\n</clipboard_text>\n\n{prompt}"

        return prompt

    def _process_with_text(
        self,
        prompt: str,
        clipboard_image: bytes | None = None,
        stream_callback: Callable[[str], None] | None = None,
    ) -> str:
        """
        Process text through LLM with appropriate method based on parameters.

        Parameters
        ----------
        prompt : str
            The prompt to process.
        clipboard_image : bytes | None, optional
            The image to be added to the clipboard, by default None.
        stream_callback : Callable[[str], None] | None, optional
            A callback function to handle streaming responses, by default None.

        Returns
        -------
        str
            The processed text.
        """
        # Determine if we're using streaming
        if stream_callback:
            if clipboard_image:
                return asyncio.run(self._llm_processor.process_text_with_stream(
                    text=prompt,
                    callback=stream_callback,
                    image_data=clipboard_image,
                ))
            else:
                return asyncio.run(self._llm_processor.process_text_with_stream(
                    text=prompt,
                    callback=stream_callback,
                ))
        else:
            if clipboard_image:
                return asyncio.run(self._llm_processor.process_text(
                    text=prompt,
                    image_data=clipboard_image,
                ))
            else:
                return asyncio.run(self._llm_processor.process_text(text=prompt))

    def process(
        self,
        audio_file_path: str,
        clipboard_text: str | None = None,
        clipboard_image: bytes | None = None,
        stream_callback: Callable[[str], None] | None = None,
    ) -> PipelineResult:
        """
        Process an audio file with STT output and optional LLM processing.

        Parameters
        ----------
        audio_file_path : str
            The path to the audio file to process.
        clipboard_text : str | None, optional
            The text to be added to the clipboard, by default None.
        clipboard_image : bytes | None, optional
            The image to be added to the clipboard, by default None.
        stream_callback : Callable[[str], None] | None, optional
            A callback function to handle streaming responses, by default None.

        Returns
        -------
        PipelineResult
            The result of the pipeline processing.
        """
        # Perform STT
        stt_output = self._stt_processor.transcribe_file_with_chunks(audio_file_path=audio_file_path)

        # Create result object
        result = PipelineResult(stt_output=stt_output)

        # If LLM is enabled, process the STT output
        if self._is_llm_processing_enabled:
            # Prepare the prompt
            prompt = self._prepare_prompt(
                stt_output=stt_output,
                clipboard_text=clipboard_text,
            )

            # Process with LLM
            llm_output = self._process_with_text(
                prompt=prompt,
                clipboard_image=clipboard_image,
                stream_callback=stream_callback,
            )

            # Update result
            result.llm_output = llm_output
            result.is_llm_processed = True

        return result

    def shutdown(self) -> None:
        """
        Shutdown the pipeline.
        """
        self._llm_processor.shutdown()