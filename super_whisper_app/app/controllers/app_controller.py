"""
Application Controller Module

This module provides the AppController class, which serves as the mediator
between the view and model components of the application architecture.
"""

from typing import Optional, Callable
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot, QSettings

from super_whisper_app.app.models.thread_manager import ThreadManager
from super_whisper_app.app.models.hotkey_manager import HotkeyModel
from super_whisper_app.app.models.instruction_set_manager import InstructionSetManagerModel
from super_whisper_app.app.models.pipeline_worker import PipelineWorker

from core.pipelines.pipeline import Pipeline
from core.pipelines.pipeline_result import PipelineResult


class AppController(QObject):
    """
    Controller class for the application.
    
    This class serves as a mediator between the view and model components
    of the application architecture. It handles user interactions from the view,
    delegates tasks to appropriate models, and updates the view with results.
    
    Attributes
    ----------
    task_progress : pyqtSignal
        Signal emitted when task progress updates
    processing_result : pyqtSignal
        Signal emitted when a processing result is available
    stream_update : pyqtSignal
        Signal emitted when a streaming chunk is available
    task_started : pyqtSignal
        Signal emitted when a task starts
    task_finished : pyqtSignal
        Signal emitted when a task finishes
    hotkey_changed : pyqtSignal
        Signal emitted when a hotkey changes
    instruction_sets_changed : pyqtSignal
        Signal emitted when instruction sets change
    selected_set_changed : pyqtSignal
        Signal emitted when the selected instruction set changes
    """
    
    # Signals for communicating with the view
    task_progress = pyqtSignal(int)
    processing_result = pyqtSignal(PipelineResult)
    stream_update = pyqtSignal(str)
    task_started = pyqtSignal()
    task_finished = pyqtSignal()
    hotkey_changed = pyqtSignal(str)
    instruction_sets_changed = pyqtSignal()
    selected_set_changed = pyqtSignal(str)
    
    def __init__(self, settings: QSettings) -> None:
        """
        Initialize the AppController.
        
        Parameters
        ----------
        settings : QSettings
            Application settings for storing/retrieving data
        """
        super().__init__()
        
        # Store settings
        self._settings = settings
        
        # Initialize thread manager
        self._thread_manager = ThreadManager()
        
        # Initialize hotkey model
        self._hotkey_model = HotkeyModel()
        
        # Connect hotkey signal to handler
        self._hotkey_model.hotkey_triggered.connect(self._handle_hotkey_triggered)
        
        # Initialize instruction set manager
        self._instruction_set_manager = InstructionSetManagerModel(settings)
        
        # Connect instruction set signals
        self._instruction_set_manager.sets_changed.connect(
            lambda: self.instruction_sets_changed.emit()
        )
        self._instruction_set_manager.selected_set_changed.connect(
            lambda name: self.selected_set_changed.emit(name)
        )
        
        # Pipeline and worker (will be created when API key is set)
        self._pipeline: Optional[Pipeline] = None
        self._pipeline_worker: Optional[PipelineWorker] = None
        
        # Recording state
        self._is_recording = False
        self._current_audio_file = None
        
        # Initialize pipeline with API key if available
        api_key = self.get_api_key()
        if api_key:
            self._initialize_pipeline(api_key)
    
    def _initialize_pipeline(self, api_key: str) -> bool:
        """
        Initialize the pipeline with the given API key.
        
        Parameters
        ----------
        api_key : str
            The API key to use
            
        Returns
        -------
        bool
            True if pipeline was initialized successfully, False otherwise
        """
        try:
            # Create pipeline with API key
            self._pipeline = Pipeline(api_key=api_key)
            
            # Apply selected instruction set if exists
            self.apply_selected_instruction_set()
            
            return True
        except Exception as e:
            self._pipeline = None
            return False
    
    def set_api_key(self, api_key: str) -> bool:
        """
        Set the API key for the pipeline.
        
        Parameters
        ----------
        api_key : str
            The API key to set
            
        Returns
        -------
        bool
            True if API key was set successfully, False otherwise
        """
        # Save API key to settings
        self._settings.setValue("api_key", api_key)
        
        # Initialize pipeline with the new API key
        result = self._initialize_pipeline(api_key)
            
        return result
    
    def get_api_key(self) -> str:
        """
        Get the current API key.
        
        Returns
        -------
        str
            The current API key, or empty string if not set
        """
        return self._settings.value("api_key", "")
    
    def apply_selected_instruction_set(self) -> bool:
        """
        Apply the selected instruction set to the pipeline.
        
        Returns
        -------
        bool
            True if successful, False otherwise
        """
        if not self._pipeline:
            return False
        
        # Get selected instruction set
        instruction_set = self._instruction_set_manager.get_selected_set()
        if not instruction_set:
            return False
        
        # Apply to pipeline
        self._pipeline.apply_instruction_set(instruction_set)
        
        return True
    
    def start_recording(self) -> bool:
        """
        Start recording audio.
        
        Returns
        -------
        bool
            True if recording started successfully, False otherwise
        """        
        # Check if we have a pipeline
        if not self._pipeline:
            # Try to initialize pipeline if we have an API key
            api_key = self.get_api_key()
            if api_key:
                if not self._initialize_pipeline(api_key):
                    return False
            else:
                return False
            
        if self._is_recording:
            return False
        
        try:
            # Check if we need a worker - create it if we don't have one or need a new one
            if not self._pipeline_worker:
                self._pipeline_worker = PipelineWorker(self._pipeline)
                # Connect worker signals
                self._pipeline_worker.progress_updated.connect(self.task_progress.emit)
                self._pipeline_worker.processing_complete.connect(self._handle_processing_complete)
                self._pipeline_worker.stream_chunk.connect(self.stream_update.emit)
            
            # Start recording
            self._pipeline.start_recording()
            self._is_recording = True
            
            # Emit signal
            self.task_started.emit()
            
            return True
        except Exception as e:
            return False
    
    def stop_recording(self) -> None:
        """
        Stop recording and start processing.
        
        This method stops the recording and starts the processing task
        in a background thread.
        """
        if not self._pipeline or not self._is_recording:
            return
        
        # Stop recording
        audio_file = self._pipeline.stop_recording()
        self._is_recording = False
        
        # Signal that recording task is finished (regardless of processing)
        self.task_finished.emit()
        
        # Store audio file
        self._current_audio_file = audio_file
        
        if audio_file:
            # Start processing
            self._process_audio_file(audio_file)
    
    def _process_audio_file(self, audio_file: str) -> None:
        """
        Process an audio file using the pipeline.
        
        Parameters
        ----------
        audio_file : str
            Path to the audio file to process
        """
        if not self._pipeline:
            return
        
        # Get language from selected instruction set
        language = None
        instruction_set = self._instruction_set_manager.get_selected_set()
        if instruction_set:
            language = instruction_set.stt_language
        
        # Create a new pipeline worker for each processing task
        pipeline_worker = PipelineWorker(self._pipeline)
        
        # Connect worker signals
        pipeline_worker.progress_updated.connect(self.task_progress.emit)
        pipeline_worker.processing_complete.connect(self._handle_processing_complete)
        pipeline_worker.stream_chunk.connect(self.stream_update.emit)
        
        # Set parameters in worker
        pipeline_worker.set_processing_parameters(audio_file, language)
        
        # Store the current worker for reference
        self._pipeline_worker = pipeline_worker
        
        # Run worker in thread
        self._thread_manager.run_worker_in_thread(pipeline_worker)
    
    def toggle_recording(self) -> None:
        """
        Toggle recording state.
        
        If recording is in progress, stop it. Otherwise, start recording.
        """
        if self._is_recording:
            self.stop_recording()
        else:
            self.start_recording()
    
    @pyqtSlot(str)
    def _handle_hotkey_triggered(self, hotkey: str) -> None:
        """
        Handle hotkey trigger event from the hotkey model.
        
        Parameters
        ----------
        hotkey : str
            The hotkey that was triggered
        """
        # Check if it's a task hotkey
        if hotkey == self._hotkey_model.task_hotkey:
            self.toggle_recording()
            return
        
        # Check if it's an instruction set hotkey
        instruction_set = self._instruction_set_manager.get_set_by_hotkey(hotkey)
        if instruction_set:
            # Set as selected
            self._instruction_set_manager.set_selected(instruction_set.name)
            
            # If not recording, start recording
            if not self._is_recording:
                self.start_recording()
            # If recording and this is the active set, stop recording
            elif self._instruction_set_manager.get_selected_set_name() == instruction_set.name:
                self.stop_recording()
    
    def set_task_hotkey(self, hotkey: str) -> bool:
        """
        Set the hotkey for controlling tasks.
        
        Parameters
        ----------
        hotkey : str
            The hotkey string to set
            
        Returns
        -------
        bool
            True if the hotkey was set successfully, False otherwise
        """
        try:
            self._hotkey_model.task_hotkey = hotkey
            self.hotkey_changed.emit(hotkey)
            return True
        except ValueError:
            return False
    
    def get_task_hotkey(self) -> str:
        """
        Get the current task hotkey.
        
        Returns
        -------
        str
            The current task hotkey or empty string if not set
        """
        return self._hotkey_model.task_hotkey or ""
    
    def get_instruction_sets(self) -> list:
        """
        Get all instruction sets.
        
        Returns
        -------
        list
            List of instruction sets
        """
        return self._instruction_set_manager.get_all_sets()
    
    def get_selected_instruction_set(self) -> Optional[object]:
        """
        Get the currently selected instruction set.
        
        Returns
        -------
        Optional[object]
            The selected instruction set, or None if not found
        """
        return self._instruction_set_manager.get_selected_set()
    
    def set_selected_instruction_set(self, name: str) -> bool:
        """
        Set the selected instruction set.
        
        Parameters
        ----------
        name : str
            Name of the instruction set to select
            
        Returns
        -------
        bool
            True if successful, False otherwise
        """
        result = self._instruction_set_manager.set_selected(name)
        if result:
            self.apply_selected_instruction_set()
        return result
    
    def create_instruction_set(self, name: str) -> bool:
        """
        Create a new instruction set.
        
        Parameters
        ----------
        name : str
            Name of the new instruction set
            
        Returns
        -------
        bool
            True if successful, False otherwise
        """
        return self._instruction_set_manager.create_set(name)
    
    def delete_instruction_set(self, name: str) -> bool:
        """
        Delete an instruction set.
        
        Parameters
        ----------
        name : str
            Name of the instruction set to delete
            
        Returns
        -------
        bool
            True if successful, False otherwise
        """
        return self._instruction_set_manager.delete_set(name)
    
    def rename_instruction_set(self, old_name: str, new_name: str) -> bool:
        """
        Rename an instruction set.
        
        Parameters
        ----------
        old_name : str
            Current name of the instruction set
        new_name : str
            New name for the instruction set
            
        Returns
        -------
        bool
            True if successful, False otherwise
        """
        return self._instruction_set_manager.rename_set(old_name, new_name)
    
    def update_instruction_set(self, name: str, vocabulary: str = None, instructions: str = None,
                           stt_language: str = None, stt_model: str = None,
                           llm_enabled: bool = None, llm_model: str = None,
                           llm_instructions: str = None, llm_clipboard_text_enabled: bool = None,
                           llm_clipboard_image_enabled: bool = None, hotkey: str = None) -> bool:
        """
        Update an instruction set.
        
        Parameters
        ----------
        name : str
            Name of the instruction set to update
        vocabulary : str, optional
            Custom vocabulary for speech-to-text
        instructions : str, optional
            System instructions for speech-to-text
        stt_language : str, optional
            Language code for speech-to-text
        stt_model : str, optional
            Speech-to-text model ID
        llm_enabled : bool, optional
            Whether LLM processing is enabled
        llm_model : str, optional
            LLM model ID
        llm_instructions : str, optional
            System instructions for LLM
        llm_clipboard_text_enabled : bool, optional
            Whether to include clipboard text in LLM input
        llm_clipboard_image_enabled : bool, optional
            Whether to include clipboard images in LLM input
        hotkey : str, optional
            Hotkey string for quick activation
            
        Returns
        -------
        bool
            True if successful, False otherwise
        """
        # Create kwargs dictionary with only the provided parameters
        kwargs = {}
        if vocabulary is not None:
            kwargs["stt_vocabulary"] = vocabulary
        if instructions is not None:
            kwargs["stt_instructions"] = instructions
        if stt_language is not None:
            kwargs["stt_language"] = stt_language
        if stt_model is not None:
            kwargs["stt_model"] = stt_model
        if llm_enabled is not None:
            kwargs["llm_enabled"] = llm_enabled
        if llm_model is not None:
            kwargs["llm_model"] = llm_model
        if llm_instructions is not None:
            kwargs["llm_instructions"] = llm_instructions
        if llm_clipboard_text_enabled is not None:
            kwargs["llm_clipboard_text_enabled"] = llm_clipboard_text_enabled
        if llm_clipboard_image_enabled is not None:
            kwargs["llm_clipboard_image_enabled"] = llm_clipboard_image_enabled
        if hotkey is not None:
            kwargs["hotkey"] = hotkey
            
        # Update set
        result = self._instruction_set_manager.update_set(name, **kwargs)
        if result and name == self._instruction_set_manager.get_selected_set_name():
            self.apply_selected_instruction_set()
        return result
    
    @pyqtSlot(PipelineResult)
    def _handle_processing_complete(self, result: PipelineResult) -> None:
        """
        Handle processing completion from the pipeline worker.
        
        This method forwards the processing result to the view
        and ensures that any necessary cleanup is performed.
        
        Parameters
        ----------
        result : PipelineResult
            The processing result
        """
        # Forward the result to the view
        self.processing_result.emit(result)
        
        # Cleanup any worker thread resources if needed
        if "worker" in self._thread_manager._threads:
            thread, worker = self._thread_manager._threads["worker"]

            # If the thread is still running, force cleanup
            if thread.isRunning():
                # First, signal the thread to quit
                thread.quit()
                # Wait a bit for thread termination
                if not thread.wait(500):
                    # If it doesn't quit, terminate it forcefully
                    thread.terminate()
                    thread.wait(500)
    
    def cleanup(self) -> None:
        """
        Clean up resources.
        
        This method should be called when the application is closing.
        """
        # Clean up hotkey model
        self._hotkey_model.cleanup()
        
        # Clean up thread manager
        self._thread_manager.release_thread_resources()
