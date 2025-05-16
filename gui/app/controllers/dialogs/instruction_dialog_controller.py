"""
Instruction Dialog Controller

This module provides the controller component for the instruction dialog in the Super Whisper application.
It mediates between the instruction dialog view and model.
"""

from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot

from core.stt.stt_lang_model import STTLangModel
from core.stt.stt_model import STTModel
from core.llm.llm_model import LLMModel
from core.pipelines.instruction_set import InstructionSet

from ...models.dialogs.instruction_dialog_model import InstructionDialogModel
from ...models.hotkey_model import HotkeyModel


class InstructionDialogController(QObject):
    """
    Controller for the instruction dialog.
    
    This class mediates between the instruction dialog view and model,
    handling user interactions and updating the model and view accordingly.
    
    Attributes
    ----------
    instruction_set_added : pyqtSignal
        Signal emitted when an instruction set is added
    instruction_set_updated : pyqtSignal
        Signal emitted when an instruction set is updated
    instruction_set_deleted : pyqtSignal
        Signal emitted when an instruction set is deleted
    instruction_set_renamed : pyqtSignal
        Signal emitted when an instruction set is renamed
    instruction_set_selected : pyqtSignal
        Signal emitted when an instruction set is selected
    hotkey_conflict : pyqtSignal
        Signal emitted when there is a hotkey conflict
    operation_result : pyqtSignal
        Signal emitted with the result of an operation
    """
    
    # Define signals
    instruction_set_added = pyqtSignal(InstructionSet)
    instruction_set_updated = pyqtSignal(InstructionSet)
    instruction_set_deleted = pyqtSignal(str)  # Name of deleted set
    instruction_set_renamed = pyqtSignal(str, str)  # Old name, new name
    instruction_set_selected = pyqtSignal(InstructionSet)
    hotkey_conflict = pyqtSignal(str, str)  # Conflicting hotkey, set name with conflict
    operation_result = pyqtSignal(bool, str)  # Success/failure, message
    
    def __init__(self, 
                 dialog_model: InstructionDialogModel,
                 hotkey_model: HotkeyModel | None = None,
                 parent_controller: QObject | None = None):
        """
        Initialize the InstructionDialogController.
        
        Parameters
        ----------
        dialog_model : InstructionDialogModel
            The model for the instruction dialog
        hotkey_model : HotkeyModel | None, optional
            The model for hotkey management, by default None
        parent_controller : QObject, optional
            The parent controller, typically AppController
        """
        super().__init__()
        
        # Store models
        self._dialog_model = dialog_model
        self._hotkey_model = hotkey_model
        self._parent_controller = parent_controller
        
        # Connect model signals
        self._connect_model_signals()
        
        # Currently selected set name
        self._selected_set_name = ""
    
    def _connect_model_signals(self) -> None:
        """
        Connect signals from the models.
        """
        # Connect dialog model signals
        self._dialog_model.instruction_set_added.connect(self._on_instruction_set_added)
        self._dialog_model.instruction_set_updated.connect(self._on_instruction_set_updated)
        self._dialog_model.instruction_set_deleted.connect(self._on_instruction_set_deleted)
        self._dialog_model.instruction_set_renamed.connect(self._on_instruction_set_renamed)
        self._dialog_model.hotkey_updated.connect(self._on_hotkey_updated)
    
    @pyqtSlot(InstructionSet)
    def _on_instruction_set_added(self, instruction_set: InstructionSet) -> None:
        """
        Handle instruction set added event.
        
        Parameters
        ----------
        instruction_set : InstructionSet
            The added instruction set
        """
        # Forward signal to view
        self.instruction_set_added.emit(instruction_set)
        
        # Register hotkey if set has one
        if instruction_set.hotkey and self._hotkey_model:
            success = self._hotkey_model.register_hotkey(instruction_set.hotkey)
            if not success:
                self.hotkey_conflict.emit(instruction_set.hotkey, "")
    
    @pyqtSlot(InstructionSet)
    def _on_instruction_set_updated(self, instruction_set: InstructionSet) -> None:
        """
        Handle instruction set updated event.
        
        Parameters
        ----------
        instruction_set : InstructionSet
            The updated instruction set
        """
        # Forward signal to view
        self.instruction_set_updated.emit(instruction_set)
    
    @pyqtSlot(str)
    def _on_instruction_set_deleted(self, name: str) -> None:
        """
        Handle instruction set deleted event.
        
        Parameters
        ----------
        name : str
            Name of the deleted set
        """
        # Forward signal to view
        self.instruction_set_deleted.emit(name)
        
        # If this was the selected set, clear selection
        if name == self._selected_set_name:
            self._selected_set_name = ""
    
    @pyqtSlot(str, str)
    def _on_instruction_set_renamed(self, old_name: str, new_name: str) -> None:
        """
        Handle instruction set renamed event.
        
        Parameters
        ----------
        old_name : str
            Old name of the set
        new_name : str
            New name of the set
        """
        # Forward signal to view
        self.instruction_set_renamed.emit(old_name, new_name)
        
        # Update selected set name if it was renamed
        if old_name == self._selected_set_name:
            self._selected_set_name = new_name
    
    @pyqtSlot(str, str)
    def _on_hotkey_updated(self, set_name: str, hotkey: str) -> None:
        """
        Handle hotkey updated event.
        
        Parameters
        ----------
        set_name : str
            Name of the set whose hotkey was updated
        hotkey : str
            The new hotkey
        """
        # Register new hotkey if not empty
        if hotkey and self._hotkey_model:
            # Check for conflicts first
            conflicting_set = self._dialog_model.get_set_by_hotkey(hotkey)
            if conflicting_set and conflicting_set.name != set_name:
                # Emit hotkey conflict signal
                self.hotkey_conflict.emit(hotkey, conflicting_set.name)
                return
            
            # Register the hotkey
            self._hotkey_model.register_hotkey(hotkey)
    
    def get_all_sets(self) -> list[InstructionSet]:
        """
        Get all instruction sets.
        
        Returns
        -------
        list[InstructionSet]
            List of all instruction sets
        """
        return self._dialog_model.get_all_sets()
    
    def get_set_by_name(self, name: str) -> InstructionSet | None:
        """
        Get an instruction set by name.
        
        Parameters
        ----------
        name : str
            Name of the instruction set to find
            
        Returns
        -------
        InstructionSet | None
            The instruction set with the specified name, or None if not found
        """
        return self._dialog_model.get_set_by_name(name)
    
    def select_set(self, name: str) -> bool:
        """
        Select an instruction set by name.
        
        Parameters
        ----------
        name : str
            Name of the instruction set to select
            
        Returns
        -------
        bool
            True if successful, False if the set doesn't exist
        """
        instruction_set = self._dialog_model.get_set_by_name(name)
        if not instruction_set:
            return False
        
        self._selected_set_name = name
        self.instruction_set_selected.emit(instruction_set)
        return True
    
    def get_selected_set(self) -> InstructionSet | None:
        """
        Get the currently selected instruction set.
        
        Returns
        -------
        InstructionSet | None
            The currently selected instruction set, or None if none selected
        """
        if not self._selected_set_name:
            return None
        
        return self._dialog_model.get_set_by_name(self._selected_set_name)
    
    def add_set(self, name: str) -> bool:
        """
        Add a new instruction set with default settings.
        
        Parameters
        ----------
        name : str
            Name for the new instruction set
            
        Returns
        -------
        bool
            True if successful, False if a set with the name already exists
        """
        # Check if name already exists
        if self._dialog_model.get_set_by_name(name):
            self.operation_result.emit(False, f"An instruction set named '{name}' already exists.")
            return False
        
        # Add set with default settings
        result = self._dialog_model.add_set(name)
        
        if result:
            self.operation_result.emit(True, f"Instruction set '{name}' created successfully.")
        else:
            self.operation_result.emit(False, f"Failed to create instruction set '{name}'.")
        
        return result
    
    def update_set(self, name: str, **kwargs) -> bool:
        """
        Update an existing instruction set.
        
        Parameters
        ----------
        name : str
            Name of the instruction set to update
        **kwargs : dict
            Keyword arguments with properties to update
            
        Returns
        -------
        bool
            True if successful, False if the set doesn't exist
        """
        # Check if set exists
        if not self._dialog_model.get_set_by_name(name):
            self.operation_result.emit(False, f"Instruction set '{name}' does not exist.")
            return False
        
        # Update the set
        result = self._dialog_model.update_set(name, **kwargs)
        
        if result:
            self.operation_result.emit(True, f"Instruction set '{name}' updated successfully.")
        else:
            self.operation_result.emit(False, f"Failed to update instruction set '{name}'.")
        
        return result
    
    def delete_set(self, name: str) -> bool:
        """
        Delete an instruction set.
        
        Parameters
        ----------
        name : str
            Name of the instruction set to delete
            
        Returns
        -------
        bool
            True if successful, False if the set doesn't exist or is the last one
        """
        # Check if set exists
        if not self._dialog_model.get_set_by_name(name):
            self.operation_result.emit(False, f"Instruction set '{name}' does not exist.")
            return False
        
        # Check if this is the last set
        if len(self._dialog_model.get_all_sets()) <= 1:
            self.operation_result.emit(False, "Cannot delete the last instruction set.")
            return False
        
        # Delete the set
        result = self._dialog_model.delete_set(name)
        
        if result:
            self.operation_result.emit(True, f"Instruction set '{name}' deleted successfully.")
        else:
            self.operation_result.emit(False, f"Failed to delete instruction set '{name}'.")
        
        return result
    
    def rename_set(self, old_name: str, new_name: str) -> bool:
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
        # Check if old name exists
        if not self._dialog_model.get_set_by_name(old_name):
            self.operation_result.emit(False, f"Instruction set '{old_name}' does not exist.")
            return False
        
        # Check if new name already exists
        if self._dialog_model.get_set_by_name(new_name):
            self.operation_result.emit(False, f"An instruction set named '{new_name}' already exists.")
            return False
        
        # Rename the set
        result = self._dialog_model.rename_set(old_name, new_name)
        
        if result:
            self.operation_result.emit(True, f"Instruction set renamed from '{old_name}' to '{new_name}' successfully.")
        else:
            self.operation_result.emit(False, f"Failed to rename instruction set from '{old_name}' to '{new_name}'.")
        
        return result
    
    def update_hotkey(self, set_name: str, hotkey: str) -> bool:
        """
        Update the hotkey for an instruction set.
        
        Parameters
        ----------
        set_name : str
            Name of the instruction set
        hotkey : str
            New hotkey string
            
        Returns
        -------
        bool
            True if successful, False otherwise
        """
        # Check if set exists
        if not self._dialog_model.get_set_by_name(set_name):
            self.operation_result.emit(False, f"Instruction set '{set_name}' does not exist.")
            return False
        
        # Check for conflicts
        if hotkey:
            conflicting_set = self._dialog_model.get_set_by_hotkey(hotkey)
            if conflicting_set and conflicting_set.name != set_name:
                self.hotkey_conflict.emit(hotkey, conflicting_set.name)
                return False
        
        # Update the hotkey
        result = self._dialog_model.update_set(set_name, hotkey=hotkey)
        
        if result:
            if hotkey:
                self.operation_result.emit(True, f"Hotkey for '{set_name}' set to '{hotkey}' successfully.")
            else:
                self.operation_result.emit(True, f"Hotkey for '{set_name}' cleared successfully.")
        else:
            self.operation_result.emit(False, f"Failed to update hotkey for '{set_name}'.")
        
        return result
    
    def get_available_languages(self) -> list[STTLangModel]:
        """
        Get available languages for speech recognition.
        
        Returns
        -------
        list[STTLangModel]
            List of available language objects
        """
        return self._dialog_model.get_available_languages()
    
    def get_available_stt_models(self) -> list[STTModel]:
        """
        Get available speech recognition models.
        
        Returns
        -------
        list[STTModel]
            List of available STT model objects
        """
        return self._dialog_model.get_available_stt_models()
    
    def get_available_llm_models(self) -> list[LLMModel]:
        """
        Get available LLM models.
        
        Returns
        -------
        list[LLMModel]
            List of available LLM model objects
        """
        return self._dialog_model.get_available_llm_models()
    
    def check_image_input_supported(self, model_id: str) -> bool:
        """
        Check if an LLM model supports image input.
        
        Parameters
        ----------
        model_id : str
            ID of the LLM model to check
            
        Returns
        -------
        bool
            True if the model supports image input, False otherwise
        """
        return self._dialog_model.check_image_input_supported(model_id)
