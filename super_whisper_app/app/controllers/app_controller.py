"""
App Controller

This module provides the main controller component for the Super Whisper application,
coordinating between models and views.
"""

import sys
from typing import Optional, Callable
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot, QSettings
from PyQt6.QtWidgets import QMessageBox

from ..models.pipeline_model import PipelineModel
from ..models.instruction_set_model import InstructionSetModel
from ..models.hotkey_model import HotkeyModel
from ..models.dialogs.instruction_dialog_model import InstructionDialogModel
from ..controllers.dialogs.instruction_dialog_controller import InstructionDialogController
from ..controllers.dialogs.api_key_controller import APIKeyController
from ..views.dialogs.instruction_dialog import InstructionDialog
from core.pipelines.pipeline_result import PipelineResult
from core.pipelines.instruction_set import InstructionSet

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
    status_update : pyqtSignal
        Signal emitted when there's a status update for the UI
    instruction_set_activated : pyqtSignal
        Signal emitted when an instruction set is activated
    hotkey_triggered : pyqtSignal
        Signal emitted when a hotkey is triggered
    """
    
    # Define signals for view communication
    recording_started = pyqtSignal()
    recording_stopped = pyqtSignal()
    processing_started = pyqtSignal()
    processing_complete = pyqtSignal(PipelineResult)
    status_update = pyqtSignal(str, int)  # message, timeout
    instruction_set_activated = pyqtSignal(InstructionSet)
    hotkey_triggered = pyqtSignal(str)
    
    def __init__(self, settings: QSettings):
        """
        Initialize the AppController.
        
        Parameters
        ----------
        settings : QSettings
            Application settings object for persistence
        """
        super().__init__()
        
        # Store settings for model initialization
        self._settings = settings
        
        # Initialize models
        self._init_models()
        
        # Set up model connections
        self._setup_model_connections()
        
        # For tracking recording state
        self._is_recording = False
    
    def _init_models(self):
        """
        Initialize the application models.
        
        Note: The APIKeyController has already validated the API key, so we can assume
        it's valid here. However, we still check initialization status to be safe.
        """
        # Get API key from settings
        api_key = self._settings.value("api_key", "")
        
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
            
        self._instruction_set_model = InstructionSetModel(self._settings)
        self._hotkey_model = HotkeyModel()
    
    def _setup_model_connections(self):
        """
        Set up connections between models and controller.
        """
        # Pipeline model connections
        self._pipeline_model.processing_started.connect(self.processing_started)
        self._pipeline_model.processing_complete.connect(self.processing_complete)
        self._pipeline_model.processing_error.connect(
            lambda error: self.status_update.emit(f"Error: {error}", 3000)
        )
        
        # Instruction set model connections
        self._instruction_set_model.selected_set_changed.connect(
            self.instruction_set_activated
        )
        
        # Hotkey model connections
        self._hotkey_model.hotkey_triggered.connect(self._handle_hotkey_triggered)
    
    @pyqtSlot(str)
    def _handle_hotkey_triggered(self, hotkey: str):
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
            
        # If we're recording, this might be a stop request
        if self._is_recording:
            # If this is the same hotkey that started recording, stop recording
            if hotkey == self._hotkey_model.get_active_recording_hotkey():
                self.stop_recording()
        else:
            # Not recording, so this is a start request with the selected instruction set
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
            # Save API key to settings
            self._settings.setValue("api_key", api_key)
            self._settings.sync()
            
            # Apply the selected instruction set if available
            selected_set = self._instruction_set_model.get_selected_set()
            if selected_set:
                self._pipeline_model.apply_instruction_set(selected_set)
            
        return result
    
    def get_instruction_sets(self):
        """
        Get all available instruction sets.
        
        Returns
        -------
        List[InstructionSet]
            List of all instruction sets
        """
        return self._instruction_set_model.get_all_sets()
    
    def get_selected_instruction_set(self) -> Optional[InstructionSet]:
        """
        Get the currently selected instruction set.
        
        Returns
        -------
        Optional[InstructionSet]
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
        if result and not self._hotkey_model.is_recording_mode_active:
            self._hotkey_model.start_listening()
            
        return result
    
    def toggle_recording(self):
        """
        Toggle recording state.
        
        If recording is in progress, it stops recording.
        If not recording, it starts recording.
        """
        if self._is_recording:
            self.stop_recording()
        else:
            self.start_recording()
    
    def start_recording(self):
        """
        Start recording audio.
        
        Returns
        -------
        bool
            True if recording started successfully, False otherwise
        """
        if self._is_recording:
            return False
            
        # Apply selected instruction set if available
        selected_set = self._instruction_set_model.get_selected_set()
        if selected_set:
            self._pipeline_model.apply_instruction_set(selected_set)
            
        # Start recording
        if self._pipeline_model.start_recording():
            self._is_recording = True
            
            # Set recording mode for hotkeys (no active hotkey in this case)
            self._hotkey_model.set_recording_mode(True)
            
            # Emit recording started signal
            self.recording_started.emit()
            
            return True
        else:
            return False
    
    def start_recording_with_hotkey(self, hotkey: str):
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
        if self._is_recording:
            return False
            
        # Apply selected instruction set if available
        selected_set = self._instruction_set_model.get_selected_set()
        if selected_set:
            self._pipeline_model.apply_instruction_set(selected_set)
            
        # Start recording
        if self._pipeline_model.start_recording():
            self._is_recording = True
            
            # Set recording mode for hotkeys with the active hotkey
            self._hotkey_model.set_recording_mode(True, hotkey)
            
            # Emit recording started signal
            self.recording_started.emit()
            
            return True
        else:
            return False
    
    def stop_recording(self):
        """
        Stop recording audio and begin processing.
        
        Returns
        -------
        bool
            True if recording was stopped successfully, False otherwise
        """
        if not self._is_recording:
            return False
            
        # Stop recording
        audio_file = self._pipeline_model.stop_recording()
        
        # Update state
        self._is_recording = False
        
        # Disable recording mode for hotkeys
        self._hotkey_model.set_recording_mode(False)
        
        # Emit recording stopped signal
        self.recording_stopped.emit()
        
        # Process the audio if we have a file
        if audio_file:
            # Get language from selected instruction set
            language = None
            selected_set = self._instruction_set_model.get_selected_set()
            if selected_set:
                language = selected_set.stt_language
                
            # Process the audio
            self._pipeline_model.process_audio(audio_file, language)
            
        return True
    
    def shutdown(self):
        """
        Clean up resources when the application is shutting down.
        """
        # Stop hotkey listening
        self._hotkey_model.stop_listening()
        
        # If still recording, stop it
        if self._is_recording:
            self.stop_recording()
    
    def create_instruction_dialog(self, parent=None):
        """
        Create and return an instruction dialog.
        
        This method creates an instruction dialog with its own model and controller,
        but connected to the app's instruction set model and hotkey model.
        
        Parameters
        ----------
        parent : QWidget, optional
            Parent widget for the dialog, by default None
            
        Returns
        -------
        InstructionDialog
            The created instruction dialog
        """
        # Create instruction dialog model
        dialog_model = InstructionDialogModel(self._settings)
        
        # Create instruction dialog controller
        dialog_controller = InstructionDialogController(
            dialog_model=dialog_model,
            hotkey_model=self._hotkey_model,
            parent_controller=self
        )
        
        # Create instruction dialog view
        dialog = InstructionDialog(dialog_controller, parent)
        
        # Connect dialog controller signals to app controller methods
        dialog_controller.instruction_set_added.connect(self._on_instruction_set_changed)
        dialog_controller.instruction_set_updated.connect(self._on_instruction_set_changed)
        dialog_controller.instruction_set_deleted.connect(self._on_instruction_set_changed)
        dialog_controller.instruction_set_renamed.connect(self._on_instruction_set_renamed)
        
        return dialog
    
    def _on_instruction_set_changed(self, instruction_set):
        """
        Handle instruction set change events from the dialog.
        
        This method updates the app's instruction set model with changes
        made in the instruction dialog.
        
        Parameters
        ----------
        instruction_set : InstructionSet
            The changed instruction set
        """
        # Find if this set exists in the main model
        existing_set = self._instruction_set_model.get_set_by_name(instruction_set.name)
        
        if existing_set:
            # Update existing set
            self._instruction_set_model.update_set(instruction_set.name, instruction_set)
        else:
            # Add new set
            self._instruction_set_model.add_set(instruction_set)
    
    def _on_instruction_set_renamed(self, old_name, new_name):
        """
        Handle instruction set rename events from the dialog.
        
        This method updates the app's instruction set model when a set is renamed
        in the instruction dialog.
        
        Parameters
        ----------
        old_name : str
            The old name of the instruction set
        new_name : str
            The new name of the instruction set
        """
        # Check if the old name exists in the main model
        if self._instruction_set_model.get_set_by_name(old_name):
            # Rename the set
            self._instruction_set_model.rename_set(old_name, new_name)
    
    def show_api_key_settings(self, parent=None):
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
        # Create API key controller
        api_key_controller = APIKeyController(self._settings)
        
        # Connect signals for status updates
        api_key_controller.api_key_validated.connect(
            lambda key: self.status_update.emit("API key updated successfully", 3000)
        )
        
        # Get current API key to pre-fill the dialog
        current_api_key = self._settings.value("api_key", "")
        
        # Show the API key dialog in settings mode
        initial_message = "Update your API key or enter a new one if needed."
        if api_key_controller.prompt_for_api_key(parent, initial_message, True):
            # Get the new API key
            api_key = self._settings.value("api_key", "")
            
            # Reinitialize pipeline with the new API key
            if self.initialize_with_api_key(api_key):
                return True
            
        return False
