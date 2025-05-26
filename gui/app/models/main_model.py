"""
Main Model

This module provides the consolidated model component for the Open Super Whisper application,
combining functionality of hotkey, instruction set, and pipeline models.
"""

from PyQt6.QtCore import QObject, pyqtSignal, QThread, pyqtSlot

from core.pipelines.pipeline import Pipeline
from core.pipelines.pipeline_result import PipelineResult
from core.pipelines.instruction_set import InstructionSet

from ..managers.keyboard_manager import KeyboardManager
from ..managers.instruction_sets_manager import InstructionSetsManager
from ..managers.settings_manager import SettingsManager


class LabelManager:
    """
    Manages application labels for internationalization support.
    """

    ALL_LABELS = {
        "English": {
            "pipeline_not_initialized": "Pipeline not initialized",
            "error_starting_recording": "Error starting recording: {error}",
            "error_stopping_recording": "Error stopping recording: {error}",
            "processing_already_in_progress": "Processing already in progress",
            "error_processing_audio": "Error processing audio: {error}",
            "processing_failed": "Processing failed: {error}",
            "error_setting_selected_instruction_set": "Error setting selected instruction set: {name}",
            "error_applying_instruction_set": "Error applying instruction set: {error}",
        },
        "Japanese": {
            "pipeline_not_initialized": "パイプラインが初期化されていません",
            "error_starting_recording": "録音開始時のエラー: {error}",
            "error_stopping_recording": "録音停止時のエラー: {error}",
            "processing_already_in_progress": "既に処理中です",
            "error_processing_audio": "音声処理中のエラー: {error}",
            "processing_failed": "処理に失敗しました: {error}",
            "error_setting_selected_instruction_set": "選択したインストラクションセットの設定エラー: {name}",
            "error_applying_instruction_set": "インストラクションセット適用時のエラー: {error}",
        },
        # Future: Add other languages here
    }

    def __init__(self) -> None:
        # load language from settings manager
        settings_manager = SettingsManager.instance()
        language = settings_manager.get_language()

        # set labels based on language
        self._labels = self.ALL_LABELS[language]

    @property
    def pipeline_not_initialized(self) -> str:
        return self._labels["pipeline_not_initialized"]

    @property
    def error_starting_recording(self) -> str:
        return self._labels["error_starting_recording"]

    @property
    def error_stopping_recording(self) -> str:
        return self._labels["error_stopping_recording"]

    @property
    def processing_already_in_progress(self) -> str:
        return self._labels["processing_already_in_progress"]

    @property
    def error_processing_audio(self) -> str:
        return self._labels["error_processing_audio"]

    @property
    def processing_failed(self) -> str:
        return self._labels["processing_failed"]

    @property
    def error_setting_selected_instruction_set(self) -> str:
        return self._labels["error_setting_selected_instruction_set"]

    @property
    def error_applying_instruction_set(self) -> str:
        return self._labels["error_applying_instruction_set"]


class ProcessingThread(QThread):
    """
    Thread for processing audio files asynchronously.

    This class is used to process audio files in a separate thread to
    prevent the UI from freezing during processing.

    Attributes
    ----------
    completed: pyqtSignal
        Signal for handling completion of processing
    failed: pyqtSignal
        Signal for handling failure of processing
    progress: pyqtSignal
        Signal for handling streaming progress updates
    """

    #
    # Signals
    #
    completed = pyqtSignal(object)
    failed = pyqtSignal(str)
    progress = pyqtSignal(str)

    def __init__(
        self,
        pipeline: Pipeline,
        audio_file_path: str,
        language: str | None = None,
        clipboard_text: str | None = None,
        clipboard_image: bytes | None = None,
        main_window: QObject | None = None,
    ) -> None:
        """
        Initialize with processing parameters.

        Parameters
        ----------
        pipeline: Pipeline
            The pipeline to use for processing
        audio_file_path: str
            The path to the audio file to process
        language: str | None
            The language to use for processing
        clipboard_text: str | None
            The text to use for processing
        clipboard_image: bytes | None
            The image to use for processing
        main_window: QObject | None
            The parent object
        """
        super().__init__(parent=main_window)
        self.pipeline = pipeline
        self.audio_file_path = audio_file_path
        self.language = language
        self.clipboard_text = clipboard_text
        self.clipboard_image = clipboard_image

    #
    # Thread Methods
    #
    def run(self) -> None:
        """
        Execute the processing task.
        """
        try:
            # Process the audio file with streaming updates
            result = self.pipeline.process(
                audio_file_path=self.audio_file_path,
                language=self.language,
                clipboard_text=self.clipboard_text,
                clipboard_image=self.clipboard_image,
                stream_callback=self.progress.emit,
            )
            self.completed.emit(result)
        except Exception as e:
            self.failed.emit(str(e))


class MainModel(QObject):
    """
    Consolidated model for the main application.

    This class combines functionality from hotkey, instruction set, and pipeline models
    to provide a unified interface for the controller.

    Attributes
    ----------
    processing_error: pyqtSignal
        Signal emitted when an error occurs during processing
    processing_started: pyqtSignal
        Signal emitted when processing starts
    processing_complete: pyqtSignal
        Signal emitted when processing completes
    processing_cancelled: pyqtSignal
        Signal emitted when processing is cancelled
    streaming_llm_chunk: pyqtSignal
        Signal emitted when a chunk is received from the LLM stream
    instruction_set_activated: pyqtSignal
        Signal emitted when an instruction set is activated
    """

    #
    # Signals
    #
    # Pipeline signals
    processing_error = pyqtSignal(str)
    processing_started = pyqtSignal()
    processing_completed = pyqtSignal(PipelineResult)
    processing_cancelled = pyqtSignal()
    streaming_llm_chunk = pyqtSignal(str)

    # Instruction set signals
    instruction_set_activated = pyqtSignal(str)

    # Hotkey signals
    hotkey_triggered = pyqtSignal(str)

    def __init__(
        self,
        api_key: str,
        main_window: QObject | None = None,
    ) -> None:
        """
        Initialize the main model.

        Parameters
        ----------
        api_key: str
            The API key to use for the pipeline
        main_window: QObject | None, optional
            The parent object, by default None
        """
        super().__init__(parent=main_window)
        self._main_window = main_window

        # Store references to managers
        self._settings_manager = SettingsManager.instance()
        self._keyboard_manager = KeyboardManager.get_instance()
        self._instruction_sets_manager = InstructionSetsManager.get_instance()

        # Initialize label manager for internationalization
        self._label_manager = LabelManager()

        # Initialize pipeline components
        self._pipeline = Pipeline(api_key=api_key)
        self._processor = None

        # Connect signals
        self._connect_manager_signals()

    #
    # Manager Signals
    #
    def _connect_manager_signals(self) -> None:
        """
        Connect signals from managers to model handlers.
        """
        # Connect keyboard manager signals
        self._keyboard_manager.hotkey_triggered.connect(self._handle_hotkey_triggered)

    #
    # Manager Events
    #
    @pyqtSlot(str)
    def _handle_hotkey_triggered(self, hotkey: str) -> None:
        """
        Handle hotkey triggered events from the keyboard manager.

        Parameters
        ----------
        hotkey: str
            The hotkey that was triggered
        """
        # Forward the hotkey triggered signal
        self.hotkey_triggered.emit(hotkey)

    #
    # Model Methods (Pipeline)
    #
    @property
    def is_recording(self) -> bool:
        """
        Check if recording is in progress.

        Returns
        -------
        bool
            True if recording is in progress, False otherwise
        """
        return self._pipeline.is_recording

    @property
    def is_processing(self) -> bool:
        """
        Check if audio processing is in progress.

        Returns
        -------
        bool
            True if audio processing is in progress, False otherwise
        """
        return self._processor is not None

    def reinit_pipeline(self, api_key: str) -> None:
        """
        Reinitialize the pipeline with a new API key.

        Parameters
        ----------
        api_key: str
            The new API key to use
        """
        self._pipeline = Pipeline(api_key=api_key)

    def start_recording(self) -> bool:
        """
        Start recording audio.

        Returns
        -------
        bool
            True if recording started successfully, False otherwise
        """
        if not self._pipeline:
            self.processing_error.emit(self._label_manager.pipeline_not_initialized)
            return False
        try:
            self._pipeline.start_recording()
            return True
        except Exception as e:
            self.processing_error.emit(self._label_manager.error_starting_recording.format(error=str(e)))
            return False

    def stop_recording(self) -> str | None:
        """
        Stop recording audio and return the file path.

        Returns
        -------
        str | None
            The file path of the recorded audio, or None if an error occurs
        """
        if not self._pipeline or not self._pipeline.is_recording:
            return None
        try:
            return self._pipeline.stop_recording()
        except Exception as e:
            self.processing_error.emit(self._label_manager.error_stopping_recording.format(error=str(e)))
            return None

    def process_audio(
        self,
        audio_file_path: str,
        language: str | None = None,
        clipboard_text: str | None = None,
        clipboard_image: bytes | None = None,
    ) -> bool:
        """
        Process an audio file through the pipeline asynchronously.

        Parameters
        ----------
        audio_file_path: str
            The path to the audio file to process
        language: str | None
            The language to use for processing
        clipboard_text: str | None
            The text to use for processing
        clipboard_image: bytes | None
            The image to use for processing

        Returns
        -------
        bool
            True if processing started successfully, False otherwise
        """
        if not self._pipeline:
            self.processing_error.emit(self._label_manager.pipeline_not_initialized)
            return False

        if self.is_processing:
            self.processing_error.emit(self._label_manager.processing_already_in_progress)
            return False

        try:
            # Update state
            self.processing_started.emit()

            # Create and configure worker thread
            self._processor = ProcessingThread(
                pipeline=self._pipeline,
                audio_file_path=audio_file_path,
                language=language,
                clipboard_text=clipboard_text,
                clipboard_image=clipboard_image,
                main_window=self._main_window,
            )

            # Connect signals
            self._processor.completed.connect(self._on_processing_completed)
            self._processor.failed.connect(self._on_processing_failed)
            self._processor.progress.connect(self.streaming_llm_chunk)

            # Start processing
            self._processor.start()
            return True

        except Exception as e:
            self.processing_error.emit(self._label_manager.error_processing_audio.format(error=str(e)))
            self._processor = None
            return False

    def _on_processing_completed(self, result: PipelineResult) -> None:
        """
        Handle successful completion of processing.

        Parameters
        ----------
        result: PipelineResult
            The result of the processing
        """
        if self._processor:
            self._processor.deleteLater()
            self._processor = None

        self.processing_completed.emit(result)

    def _on_processing_failed(self, error: str) -> None:
        """
        Handle processing failure.

        Parameters
        ----------
        error: str
            The error message
        """
        if self._processor:
            self._processor.deleteLater()
            self._processor = None

        self.processing_error.emit(self._label_manager.processing_failed.format(error=error))

    def cancel_processing(self) -> bool:
        """
        Cancel the current processing task if one is running.

        Returns
        -------
        bool
            True if processing is cancelled, False otherwise
        """
        if not self.is_processing:
            return False

        # Terminate and clean up
        self._processor.terminate()
        self._processor.wait(1000)
        self._processor.deleteLater()
        self._processor = None

        # Update state
        self.processing_cancelled.emit()

        return True

    #
    # Model Methods (Instruction Sets)
    #
    def get_instruction_sets(self) -> list[InstructionSet]:
        """
        Get all available instruction sets.

        Returns
        -------
        list[InstructionSet]
            List of all instruction sets
        """
        return self._instruction_sets_manager.get_all_sets()

    def get_instruction_set_by_name(self, name: str) -> InstructionSet | None:
        """
        Get an instruction set by name.

        Parameters
        ----------
        name: str
            Name of the instruction set to find

        Returns
        -------
        InstructionSet | None
            The instruction set with the specified name, or None if not found
        """
        return self._instruction_sets_manager.find_set_by_name(name=name)

    def get_instruction_set_by_hotkey(self, hotkey: str) -> InstructionSet | None:
        """
        Get an instruction set by hotkey.

        Parameters
        ----------
        hotkey: str
            Hotkey string to match

        Returns
        -------
        InstructionSet | None
            The instruction set with the specified hotkey, or None if not found
        """
        return self._instruction_sets_manager.find_set_by_hotkey(hotkey=hotkey)

    def get_selected_instruction_set(self) -> InstructionSet | None:
        """
        Get the currently selected instruction set.

        Returns
        -------
        InstructionSet | None
            The currently selected instruction set, or None if none selected
        """
        return self._instruction_sets_manager.get_selected_set()

    def get_selected_instruction_set_name(self) -> str:
        """
        Get the name of the currently selected instruction set.

        Returns
        -------
        str
            The name of the currently selected instruction set, or an empty string
        """
        return self._instruction_sets_manager.get_selected_set_name()

    def set_selected_instruction_set(self, name: str) -> bool:
        """
        Set the selected instruction set by name.

        Parameters
        ----------
        name: str
            Name of the instruction set to select

        Returns
        -------
        bool
            True if successful, False if the named set doesn't exist
        """
        # Set the selected instruction set
        is_success = self._instruction_sets_manager.set_selected_set_name(instruction_set_name=name)
        if not is_success:
            self.processing_error.emit(self._label_manager.error_setting_selected_instruction_set.format(name=name))
            return False

        # Apply the instruction set to the pipeline
        selected_set = self.get_selected_instruction_set()
        if selected_set:
            try:
                self._pipeline.apply_instruction_set(selected_set=selected_set)
            except Exception as e:
                self.processing_error.emit(self._label_manager.error_applying_instruction_set.format(error=str(e)))
                return False

        # Emit the instruction set activated signal
        self.instruction_set_activated.emit(name)

        return True

    #
    # Model Methods (Hotkeys)
    #
    @property
    def is_filter_mode(self) -> bool:
        """
        Check if filter mode is active for hotkeys.

        Returns
        -------
        bool
            True if filter mode is active, False otherwise
        """
        return self._keyboard_manager.is_filter_mode

    def get_active_hotkey(self) -> str | None:
        """
        Get the active hotkey.

        Returns
        -------
        str | None
            The active hotkey, or None if not in filter mode
        """
        return self._keyboard_manager.get_active_hotkey()

    def enable_filtered_mode_and_start_listening(self, active_hotkey: str = "") -> None:
        """
        Enable filtered mode with the active hotkey.

        In filter mode, only the active hotkey is enabled and all other hotkeys are filtered out.

        Parameters
        ----------
        active_hotkey: str, optional
            The hotkey that triggered filter mode, by default ""
        """
        self._keyboard_manager.enable_filtered_mode_and_start_listening(active_hotkey=active_hotkey)

    def disable_filtered_mode_and_start_listening(self) -> None:
        """
        Disable filtered mode.

        When disabled, all hotkeys are enabled again.
        """
        self._keyboard_manager.disable_filtered_mode_and_start_listening()

    def register_hotkey(self, hotkey: str) -> bool:
        """
        Register a hotkey.

        Parameters
        ----------
        hotkey: str
            Hotkey string to register

        Returns
        -------
        bool
            True if registration was successful, False otherwise
        """
        result = self._keyboard_manager.register_hotkey(hotkey=hotkey)

        # If successful and not already listening, start listening
        if result and not self._keyboard_manager.is_filter_mode:
            self._keyboard_manager.start_listening()

        return result

    def unregister_hotkey(self, hotkey: str) -> bool:
        """
        Unregister a hotkey.

        Parameters
        ----------
        hotkey: str
            Hotkey string to unregister

        Returns
        -------
        bool
            True if unregistration was successful, False otherwise
        """
        return self._keyboard_manager.unregister_hotkey(hotkey=hotkey)

    def start_listening_for_hotkeys(self) -> bool:
        """
        Start listening for hotkeys.

        Returns
        -------
        bool
            True if listening started successfully, False otherwise
        """
        return self._keyboard_manager.start_listening()

    def stop_listening_for_hotkeys(self) -> bool:
        """
        Stop listening for hotkeys.

        Returns
        -------
        bool
            True if listening was stopped, False if it wasn't active
        """
        return self._keyboard_manager.stop_listening()

    def get_all_registered_hotkeys(self) -> list[str]:
        """
        Get a list of all registered hotkeys.

        Returns
        -------
        list[str]
            List of registered hotkey strings
        """
        return self._keyboard_manager.get_all_registered_hotkeys()

    #
    # Model Methods (Cleanup)
    #
    def shutdown(self) -> None:
        """
        Clean up resources when the application is shutting down.
        """
        # Stop hotkey listening
        self.stop_listening_for_hotkeys()

        # If still recording, stop it
        if self.is_recording:
            self.stop_recording()

        # If still processing, cancel it
        if self.is_processing:
            self.cancel_processing()
