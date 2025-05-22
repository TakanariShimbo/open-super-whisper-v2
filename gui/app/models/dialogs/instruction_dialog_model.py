"""
Instruction Dialog Model

This module provides the model component for the instruction dialog in the Super Whisper application.
It handles the data management for instruction sets using the core InstructionSetsManager.
"""

from PyQt6.QtCore import QObject, pyqtSignal

from core.pipelines.instruction_set import InstructionSet
from core.stt.stt_lang_model import STTLangModel
from core.stt.stt_model import STTModel
from core.llm.llm_model import LLMModel
from core.stt.stt_lang_model_manager import STTLangModelManager
from core.stt.stt_model_manager import STTModelManager
from core.llm.llm_model_manager import LLMModelManager

from ...managers.instruction_sets_manager import InstructionSetsManager
from ...managers.keyboard_manager import KeyboardManager


class InstructionDialogModel(QObject):
    """
    Model for the instruction dialog.

    This class encapsulates the data management for the instruction dialog,
    providing methods to manipulate instruction sets and their properties.

    Attributes
    -------
    instruction_set_added : pyqtSignal(str)
        Signal emitted when an instruction set is added
    instruction_set_deleted : pyqtSignal(str)
        Signal emitted when an instruction set is deleted
    instruction_set_renamed : pyqtSignal(str, str)
        Signal emitted when an instruction set is renamed
    hotkey_updated : pyqtSignal(str, str)
        Signal emitted when a hotkey is updated
    """

    # Define signals
    instruction_set_added = pyqtSignal(str)  # Name of added set
    instruction_set_deleted = pyqtSignal(str)  # Name of deleted set
    instruction_set_renamed = pyqtSignal(str, str)  # Old name, new name
    hotkey_updated = pyqtSignal(str)  # Hotkey

    def __init__(self, instruction_dialog: QObject | None = None) -> None:
        """
        Initialize the InstructionDialogModel.

        Parameters
        ----------
        instruction_dialog : QObject, optional
            Parent object, by default None
        """
        super().__init__(parent=instruction_dialog)

        # Get managers
        self._keyboard_manager = KeyboardManager.get_instance()
        self._instruction_manager = InstructionSetsManager.get_instance()

    def register_hotkey(self, hotkey: str) -> bool:
        """
        Register a hotkey.

        Parameters
        ----------
        hotkey : str
            The hotkey to register

        Returns
        -------
        bool
            True if registration was successful, False otherwise
        """
        return self._keyboard_manager.register_hotkey(hotkey=hotkey)

    def start_listening(self) -> bool:
        """
        Start listening for hotkeys.

        Returns
        -------
        bool
            True if listening started successfully, False otherwise
        """
        return self._keyboard_manager.start_listening()

    def stop_listening(self) -> bool:
        """
        Stop listening for hotkeys.

        Returns
        -------
        bool
            True if listening stopped successfully, False otherwise
        """
        return self._keyboard_manager.stop_listening()

    def get_all_sets(self) -> list[InstructionSet]:
        """
        Get all instruction sets.

        Returns
        -------
        list[InstructionSet]
            List of all instruction sets
        """
        return self._instruction_manager.get_all_sets()

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
        return self._instruction_manager.find_set_by_name(name=name)

    def get_set_by_hotkey(self, hotkey: str) -> InstructionSet | None:
        """
        Get an instruction set by hotkey.

        Parameters
        ----------
        hotkey : str
            Hotkey string to match

        Returns
        -------
        InstructionSet | None
            The instruction set with the specified hotkey, or None if not found
        """
        return self._instruction_manager.find_set_by_hotkey(hotkey=hotkey)

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
        # Create a new instruction set with default settings
        instruction_set = InstructionSet.get_default()
        instruction_set.name = name

        # Add the set
        result = self._instruction_manager.add_set(instruction_set=instruction_set)

        if result:
            # Save changes
            self._instruction_manager.save_to_settings()

            # Emit signal
            self.instruction_set_added.emit(name)

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
        # Get the instruction set
        instruction_set = self._instruction_manager.find_set_by_name(name=name)
        if not instruction_set:
            return False

        # Update the set
        instruction_set.update(**kwargs)

        # Save changes
        self._instruction_manager.save_to_settings()

        # Emit hotkey updated signal if hotkey was updated
        if "hotkey" in kwargs:
            self.hotkey_updated.emit(kwargs["hotkey"])

        return True

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
        # Delete the set
        result = self._instruction_manager.delete_set(name=name)

        if result:
            # Save changes
            self._instruction_manager.save_to_settings()

            # Emit signal
            self.instruction_set_deleted.emit(name)

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
        # Rename the set
        result = self._instruction_manager.rename_set(old_name=old_name, new_name=new_name)

        if result:
            # Save changes
            self._instruction_manager.save_to_settings()

            # Emit signal
            self.instruction_set_renamed.emit(old_name, new_name)

        return result

    def get_available_stt_languages(self) -> list[STTLangModel]:
        """
        Get available languages for speech recognition.

        Returns
        -------
        list[STTLangModel]
            List of available language objects
        """
        return STTLangModelManager.get_available_languages()

    def get_available_stt_models(self) -> list[STTModel]:
        """
        Get available speech recognition models.

        Returns
        -------
        list[STTModel]
            List of available STT model objects
        """
        return STTModelManager.get_available_models()

    def get_available_llm_models(self) -> list[LLMModel]:
        """
        Get available LLM models.

        Returns
        -------
        list[LLMModel]
            List of available LLM model objects
        """
        return LLMModelManager.get_available_models()

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
        return LLMModelManager.check_image_input_supported(model_id=model_id)
