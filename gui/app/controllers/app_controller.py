"""
App Controller

This module provides the main controller component for the Super Whisper application,
coordinating between models and views.
"""

import sys

from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import QMessageBox

from core.pipelines.pipeline_result import PipelineResult
from core.pipelines.instruction_set import InstructionSet

from ..models.pipeline_model import PipelineModel
from ..models.instruction_set_model import InstructionSetModel
from ..models.hotkey_model import HotkeyModel
from ..models.dialogs.instruction_dialog_model import InstructionDialogModel
from ..controllers.dialogs.instruction_dialog_controller import InstructionDialogController
from ..views.factories.api_key_dialog_factory import APIKeyDialogFactory
from ..views.factories.status_indicator_factory import StatusIndicatorFactory
from ..views.dialogs.instruction_dialog import InstructionDialog
from ..utils.clipboard_utils import ClipboardUtils
from ..utils.settings_manager import SettingsManager


class AppController(QObject):
    """
    Main application controller.
    
    This class serves as the central coordinator between the user interface (view)
    and the application's models. It processes user input from the view, interacts
    with the models, and updates the view with results.
    
    Attributes
    ----------
    recording_started : pyqtSignal
        Signal emitted when recording starts
    recording_stopped : pyqtSignal
        Signal emitted when recording stops
    processing_started : pyqtSignal
        Signal emitted when audio processing starts
    processing_complete : pyqtSignal
        Signal emitted when processing completes with results
    processing_cancelled : pyqtSignal
        Signal emitted when processing is cancelled
    processing_state_changed : pyqtSignal
        Signal emitted when processing state changes (is_processing)
    status_update : pyqtSignal
        Signal emitted when there's a status update for the UI
    instruction_set_activated : pyqtSignal
        Signal emitted when an instruction set is activated
    hotkey_triggered : pyqtSignal
        Signal emitted when a hotkey is triggered
    llm_stream_update : pyqtSignal
        Signal emitted when a streaming chunk is received from the LLM
    """
    
    # Define signals for view communication
    recording_started = pyqtSignal()
    recording_stopped = pyqtSignal()
    processing_started = pyqtSignal()
    processing_complete = pyqtSignal(PipelineResult)
    processing_cancelled = pyqtSignal()
    processing_state_changed = pyqtSignal(bool)  # is_processing
    status_update = pyqtSignal(str, int)  # message, timeout
    instruction_set_activated = pyqtSignal(InstructionSet)
    hotkey_triggered = pyqtSignal(str)
    llm_stream_update = pyqtSignal(str)  # Signal for streaming LLM updates
    
    def __init__(self) -> None:
        """
        Initialize the AppController.
        """
        super().__init__()
        
        # Store settings manager for model initialization
        self._settings_manager = SettingsManager.instance()
        
        # Initialize models
        self._init_models()
        
        # Set up model connections
        self._setup_model_connections()
    
    @property
    def is_recording(self) -> bool:
        """
        Check if recording is in progress.
        
        Returns
        -------
        bool
            True if recording is in progress, False otherwise
        """
        return self._pipeline_model.is_recording if hasattr(self, '_pipeline_model') else False
    
    @property
    def is_processing(self) -> bool:
        """
        Check if audio processing is in progress.
        
        Returns
        -------
        bool
            True if processing is in progress, False otherwise
        """
        return self._pipeline_model.is_processing if hasattr(self, '_pipeline_model') else False
    
    def _init_models(self) -> None:
        """
        Initialize the application models.
        
        Note: The APIKeyController has already validated the API key, so we can assume
        it's valid here. However, we still check initialization status to be safe.
        """
        # Get API key from settings manager
        api_key = self._settings_manager.get_api_key()
        
        # Initialize models
        self._pipeline_model = PipelineModel(api_key)
        
        # Verify that pipeline was initialized successfully
        if not self._pipeline_model.is_initialized:
            QMessageBox.critical(
                None,
                "Initialization Error",
                "Failed to initialize pipeline with the provided API key. The application will now exit."
            )
            sys.exit(1)
            
        self._instruction_set_model = InstructionSetModel()
        self._hotkey_model = HotkeyModel()
        
        # Create status indicator view using factory and get controller
        status_indicator_view = StatusIndicatorFactory.create_status_indicator()
        self._status_indicator_controller = status_indicator_view.get_controller()
    
    def _setup_model_connections(self) -> None:
        """
        Set up connections between models and controller.
        """
        # Pipeline model connections
        self._pipeline_model.processing_started.connect(self.processing_started)
        self._pipeline_model.processing_complete.connect(self._handle_processing_complete)
        self._pipeline_model.processing_cancelled.connect(self._handle_processing_cancelled)
        self._pipeline_model.processing_state_changed.connect(self._handle_processing_state_change)
        self._pipeline_model.processing_error.connect(
            lambda error: self.status_update.emit(f"Error: {error}", 3000)
        )
        self._pipeline_model.llm_stream_chunk.connect(self._handle_llm_stream_chunk)
        
        # Instruction set model connections
        self._instruction_set_model.selected_set_changed.connect(
            self.instruction_set_activated
        )
        
        # Hotkey model connections
        self._hotkey_model.hotkey_triggered.connect(self._handle_hotkey_triggered)
    
    @pyqtSlot(str)
    def _handle_llm_stream_chunk(self, chunk: str) -> None:
        """
        Handle streaming chunks from the LLM processor.
        
        Parameters
        ----------
        chunk : str
            The text chunk from the LLM stream
        """
        # Forward the stream chunk to any listening views
        self.llm_stream_update.emit(chunk)
        
    @pyqtSlot(bool)
    def _handle_processing_state_change(self, is_processing: bool) -> None:
        """
        Handle changes in processing state.
        
        Parameters
        ----------
        is_processing : bool
            Whether processing is currently active
        """
        self.processing_state_changed.emit(is_processing)
        
    @pyqtSlot(PipelineResult)
    def _handle_processing_complete(self, result: PipelineResult) -> None:
        """
        Handle processing completion.
        
        Parameters
        ----------
        result : PipelineResult
            The result of the processing
        """
        # Set status indicator to complete mode
        self._status_indicator_controller.complete_processing()
        
        # Check if auto-clipboard is enabled and copy results if needed
        if self._settings_manager.get_auto_clipboard():
            # Copy the most appropriate output to clipboard
            if result.is_llm_processed and result.llm_output:
                # If LLM was processed, copy LLM output
                ClipboardUtils.set_text(result.llm_output)
                self.status_update.emit("LLM output copied to clipboard", 2000)
            elif result.stt_output:
                # Otherwise, copy STT output
                ClipboardUtils.set_text(result.stt_output)
                self.status_update.emit("STT output copied to clipboard", 2000)
        
        # Disable recording mode for hotkeys
        self._hotkey_model.change_filter_mode(False)

        # Forward the signal to views
        self.processing_complete.emit(result)
        
    @pyqtSlot()
    def _handle_processing_cancelled(self) -> None:
        """
        Handle processing cancellation.
        """
        # Set status indicator to cancelled mode
        self._status_indicator_controller.cancel_processing()
        
        # Forward the signal to views
        self.processing_cancelled.emit()
    
    @pyqtSlot(str)
    def _handle_hotkey_triggered(self, hotkey: str) -> None:
        """
        Handle hotkey trigger events.
        
        Parameters
        ----------
        hotkey : str
            The hotkey that was triggered
        """
        # Emit the hotkey_triggered signal for view to handle
        self.hotkey_triggered.emit(hotkey)
        
        # Get the instruction set associated with this hotkey
        instruction_set = self._instruction_set_model.get_set_by_hotkey(hotkey)
        
        if not instruction_set:
            return
        
        if self.is_processing:
            # If we're processing, this might be a cancel request
            self.cancel_processing()
        elif self.is_recording:
            # If we're recording, this might be a stop request
            self.stop_recording()
        else:
            # Not recording or processing, so this is a start request with the selected instruction set
            self._instruction_set_model.set_selected(instruction_set.name)
            self.start_recording_with_hotkey(hotkey)
    
    def initialize_with_api_key(self, api_key: str) -> bool:
        """
        Initialize or reinitialize the pipeline with an API key.
        
        Parameters
        ----------
        api_key : str
            The API key to use
            
        Returns
        -------
        bool
            True if initialization was successful, False otherwise
        """
        result = self._pipeline_model.initialize_pipeline(api_key)
        
        if result:
            # Save API key to settings manager
            self._settings_manager.set_api_key(api_key)
            
            # Apply the selected instruction set if available
            selected_set = self._instruction_set_model.get_selected_set()
            if selected_set:
                self._pipeline_model.apply_instruction_set(selected_set)
            
        return result
    
    def get_instruction_sets(self) -> list[InstructionSet]:
        """
        Get all available instruction sets.
        
        Returns
        -------
        list[InstructionSet]
            List of all instruction sets
        """
        return self._instruction_set_model.get_all_sets()
    
    def get_selected_instruction_set(self) -> InstructionSet | None:
        """
        Get the currently selected instruction set.
        
        Returns
        -------
        InstructionSet | None
            The currently selected instruction set, or None if none selected
        """
        return self._instruction_set_model.get_selected_set()
    
    def select_instruction_set(self, name: str) -> bool:
        """
        Select an instruction set by name.
        
        Parameters
        ----------
        name : str
            The name of the instruction set to select
            
        Returns
        -------
        bool
            True if successful, False if the named set doesn't exist
        """
        return self._instruction_set_model.set_selected(name)
    
    def register_hotkey(self, hotkey: str, handler_id: str) -> bool:
        """
        Register a global hotkey.
        
        Parameters
        ----------
        hotkey : str
            The hotkey string to register (e.g., "ctrl+shift+r")
        handler_id : str
            Unique ID for the hotkey handler
            
        Returns
        -------
        bool
            True if registration was successful, False otherwise
        """
        result = self._hotkey_model.register_hotkey(hotkey, handler_id)
        
        # If successful and not already listening, start listening
        if result and not self._hotkey_model.is_filter_mode:
            self._hotkey_model.start_listening()
            
        return result
    
    def toggle_recording(self) -> bool:
        """
        Toggle recording state.
        
        If recording is in progress, it stops recording.
        If processing is in progress, it cancels processing (only if initiated via UI, not via hotkey).
        If not recording or processing, it starts recording.
        """
        # If processing is active, cancel it (this is from UI, not hotkey, so allowed)
        if self.is_processing:
            return self.cancel_processing()
            
        # Otherwise toggle recording
        if self.is_recording:
            self.stop_recording()
        else:
            self.start_recording()
    
    def start_recording(self) -> bool:
        """
        Start recording audio.
        
        Returns
        -------
        bool
            True if recording started successfully, False otherwise
        """
        if self.is_recording or self.is_processing:
            return False
            
        # Apply selected instruction set if available
        selected_set = self._instruction_set_model.get_selected_set()
        if selected_set:
            self._pipeline_model.apply_instruction_set(selected_set)
            
        if self._pipeline_model.start_recording():
            # Set recording mode for hotkeys (no active hotkey in this case)
            self._hotkey_model.change_filter_mode(True)
            
            # Start status indicator in recording mode
            self._status_indicator_controller.start_recording()
            
            # Emit recording started signal
            self.recording_started.emit()
            
            return True
        else:
            return False
    
    def start_recording_with_hotkey(self, hotkey: str) -> bool:
        """
        Start recording audio with a specific hotkey as the trigger.
        
        Parameters
        ----------
        hotkey : str
            The hotkey that triggered recording
            
        Returns
        -------
        bool
            True if recording started successfully, False otherwise
        """
        if self.is_recording or self.is_processing:
            return False
            
        # Apply selected instruction set if available
        selected_set = self._instruction_set_model.get_set_by_hotkey(hotkey)
        if selected_set:
            self._instruction_set_model.set_selected(selected_set.name)
            self._pipeline_model.apply_instruction_set(selected_set)
            
        if self._pipeline_model.start_recording():
            # Set recording mode for hotkeys with the active hotkey
            self._hotkey_model.change_filter_mode(True, hotkey)
            
            # Start status indicator in recording mode
            self._status_indicator_controller.start_recording()
            
            # Emit recording started signal
            self.recording_started.emit()
            
            return True
        else:
            return False
    
    def stop_recording(self) -> bool:
        """
        Stop recording audio and begin processing.
        
        Returns
        -------
        bool
            True if recording was stopped successfully, False otherwise
        """
        if not self.is_recording:
            return False
            
        # Stop recording
        audio_file = self._pipeline_model.stop_recording()
        
        # Update status indicator to processing mode
        self._status_indicator_controller.start_processing()
        
        # Emit recording stopped signal
        self.recording_stopped.emit()
        
        # Process the audio if we have a file
        if audio_file:
            # Get language from selected instruction set
            language = None
            selected_set = self._instruction_set_model.get_selected_set()
            if selected_set:
                language = selected_set.stt_language
            
            # Get clipboard content (text and image)
            clipboard_text, clipboard_image = None, None
            if selected_set and selected_set.llm_enabled:
                # Only get clipboard if LLM is enabled in the instruction set
                clipboard_text, clipboard_image = ClipboardUtils.get_content()
            
                if not selected_set.llm_clipboard_text_enabled:
                    clipboard_text = None
                if not selected_set.llm_clipboard_image_enabled:
                    clipboard_image = None
                
                print(f"Retrieved clipboard content: Text: {'Yes' if clipboard_text else 'No'}, " f"Image: {'Yes' if clipboard_image else 'No'}")
                
            # Process the audio with clipboard content asynchronously
            self._pipeline_model.process_audio(audio_file, language, clipboard_text, clipboard_image)
            
        return True
    
    def cancel_processing(self) -> bool:
        """
        Cancel the current processing task if one is in progress.
        
        Returns
        -------
        bool
            True if cancellation was initiated, False if no processing to cancel
        """
        if not self.is_processing:
            return False
            
        # Cancel processing through pipeline model
        result = self._pipeline_model.cancel_processing()
        
        if result:
            # Show cancelled status in indicator
            self._status_indicator_controller.cancel_processing()
            
            self.status_update.emit("Processing cancelled", 3000)
            
        # Disable recording mode for hotkeys
        self._hotkey_model.change_filter_mode(False)
        
        return result
    
    def shutdown(self) -> None:
        """
        Clean up resources when the application is shutting down.
        """
        # Stop hotkey listening
        self._hotkey_model.stop_listening()
        
        # If still recording, stop it
        if self.is_recording:
            self.stop_recording()
        
        # If still processing, cancel it
        if self.is_processing:
            self.cancel_processing()
    
    def create_instruction_dialog(self, parent=None) -> InstructionDialog:
        """
        Create and return an instruction dialog.
        
        This method creates an instruction dialog with its own controller,
        but connected to the app's instruction set model.
        
        Parameters
        ----------
        parent : QWidget, optional
            Parent widget for the dialog, by default None
            
        Returns
        -------
        InstructionDialog
            The created instruction dialog
        """
        # Create instruction dialog model passing the app's instruction set model
        dialog_model = InstructionDialogModel(self._instruction_set_model)
        
        # Create instruction dialog controller
        dialog_controller = InstructionDialogController(
            dialog_model=dialog_model,
            hotkey_model=self._hotkey_model,
            parent_controller=self
        )
        
        # Create instruction dialog view
        dialog = InstructionDialog(dialog_controller, parent)
        
        return dialog
    
    def show_api_key_settings(self, parent=None) -> bool:
        """
        Show the API key settings dialog.
        
        This method creates and displays an API key settings dialog,
        allowing the user to update their API key.
        
        Parameters
        ----------
        parent : QWidget, optional
            Parent widget for the dialog, by default None
            
        Returns
        -------
        bool
            True if the API key was successfully updated, False otherwise
        """
        # Create and show the API key settings dialog through factory
        dialog = APIKeyDialogFactory.create_settings_dialog(parent)
        
        # Show dialog and handle result
        result = dialog.exec()
        
        if result:
            # Dialog was accepted, emit status update
            self.status_update.emit("API key updated successfully", 3000)
            
            # Get the new API key
            api_key = self._settings_manager.get_api_key()
            
            # Reinitialize pipeline with the new API key
            if self.initialize_with_api_key(api_key):
                return True
        
        return False
