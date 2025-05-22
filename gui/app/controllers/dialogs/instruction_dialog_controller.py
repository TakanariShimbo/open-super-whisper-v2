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


class InstructionDialogController(QObject):
    """
    Controller for the instruction dialog.

    This class mediates between the instruction dialog view and model,
    handling user interactions and business logic.

    Attributes
    -------
    instruction_set_added : pyqtSignal(InstructionSet)
        Signal emitted when an instruction set is added
    instruction_set_updated : pyqtSignal(InstructionSet)
        Signal emitted when an instruction set is updated
    instruction_set_deleted : pyqtSignal(str)
        Signal emitted when an instruction set is deleted
    instruction_set_renamed : pyqtSignal(str, str)
        Signal emitted when an instruction set is renamed
    instruction_set_selected : pyqtSignal(InstructionSet)
        Signal emitted when an instruction set is selected
    hotkey_conflict : pyqtSignal(str, str)
        Signal emitted when there is a hotkey conflict
    operation_result : pyqtSignal(bool, str)
        Signal emitted with the result of an operation
    """

    # Define signals
    instruction_set_added = pyqtSignal(InstructionSet)
    instruction_set_updated = pyqtSignal(InstructionSet)
    instruction_set_deleted = pyqtSignal(str)  # Name of deleted set
    instruction_set_renamed = pyqtSignal(str, str)  # Old name, new name
    instruction_set_selected = pyqtSignal(InstructionSet)
    operation_result = pyqtSignal(bool, str)  # Success/failure, message

    def __init__(self, instruction_dialog: QObject | None = None) -> None:
        """
        Initialize the InstructionDialogController.

        Parameters
        ----------
        instruction_dialog : QObject | None, optional
            The parent object, by default None
        """
        super().__init__(parent=instruction_dialog)

        # Create model
        self._model = InstructionDialogModel()

        # Connect model signals
        self._connect_model_signals()

        # Currently selected set name
        self._selected_set_name = ""

    def _connect_model_signals(self) -> None:
        """
        Connect signals from the model.
        """
        self._model.instruction_set_added.connect(self._handle_instruction_set_added)
        self._model.instruction_set_updated.connect(self._handle_instruction_set_updated)
        self._model.instruction_set_deleted.connect(self._handle_instruction_set_deleted)
        self._model.instruction_set_renamed.connect(self._handle_instruction_set_renamed)
        self._model.hotkey_updated.connect(self._handle_hotkey_updated)

    @pyqtSlot(InstructionSet)
    def _handle_instruction_set_added(self, instruction_set: InstructionSet) -> None:
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
        if instruction_set.hotkey:
            self._model.register_hotkey(hotkey=instruction_set.hotkey)

    @pyqtSlot(InstructionSet)
    def _handle_instruction_set_updated(self, instruction_set: InstructionSet) -> None:
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
    def _handle_instruction_set_deleted(self, name: str) -> None:
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
    def _handle_instruction_set_renamed(self, old_name: str, new_name: str) -> None:
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

    @pyqtSlot(str)
    def _handle_hotkey_updated(self, hotkey: str) -> None:
        """
        Handle hotkey updated event.

        Parameters
        ----------
        hotkey : str
            The new hotkey
        """
        # Register new hotkey if not empty
        if hotkey:
            # Register the hotkey
            self._model.register_hotkey(hotkey=hotkey)

    def get_all_sets(self) -> list[InstructionSet]:
        """
        Get all instruction sets.

        Returns
        -------
        list[InstructionSet]
            List of all instruction sets
        """
        return self._model.get_all_sets()

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
        return self._model.get_set_by_name(name=name)

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
        instruction_set = self._model.get_set_by_name(name=name)
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

        return self._model.get_set_by_name(name=self._selected_set_name)

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
        if self._model.get_set_by_name(name=name):
            self.operation_result.emit(False, f"An instruction set named '{name}' already exists.")
            return False

        # Add set with default settings
        result = self._model.add_set(name=name)

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
        if not self._model.get_set_by_name(name=name):
            self.operation_result.emit(False, f"Instruction set '{name}' does not exist.")
            return False

        # Update the set
        result = self._model.update_set(name=name, **kwargs)

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
        if not self._model.get_set_by_name(name=name):
            self.operation_result.emit(False, f"Instruction set '{name}' does not exist.")
            return False

        # Check if this is the last set
        if len(self._model.get_all_sets()) <= 1:
            self.operation_result.emit(False, "Cannot delete the last instruction set.")
            return False

        # Delete the set
        result = self._model.delete_set(name=name)

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
        if not self._model.get_set_by_name(name=old_name):
            self.operation_result.emit(False, f"Instruction set '{old_name}' does not exist.")
            return False

        # Check if new name already exists
        if self._model.get_set_by_name(name=new_name):
            self.operation_result.emit(False, f"An instruction set named '{new_name}' already exists.")
            return False

        # Rename the set
        result = self._model.rename_set(old_name=old_name, new_name=new_name)

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
        if not self._model.get_set_by_name(name=set_name):
            self.operation_result.emit(False, f"Instruction set '{set_name}' does not exist.")
            return False

        # Update the hotkey
        result = self._model.update_set(name=set_name, hotkey=hotkey)

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
        return self._model.get_available_languages()

    def get_available_stt_models(self) -> list[STTModel]:
        """
        Get available speech recognition models.

        Returns
        -------
        list[STTModel]
            List of available STT model objects
        """
        return self._model.get_available_stt_models()

    def get_available_llm_models(self) -> list[LLMModel]:
        """
        Get available LLM models.

        Returns
        -------
        list[LLMModel]
            List of available LLM model objects
        """
        return self._model.get_available_llm_models()

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
        return self._model.check_image_input_supported(model_id=model_id)

    def start_listening(self) -> bool:
        """
        Start listening for hotkeys.

        Returns
        -------
        bool
            True if listening started successfully, False otherwise
        """
        return self._model.start_listening()

    def stop_listening(self) -> bool:
        """
        Stop listening for hotkeys.

        Returns
        -------
        bool
            True if listening stopped successfully, False otherwise
        """
        return self._model.stop_listening()
