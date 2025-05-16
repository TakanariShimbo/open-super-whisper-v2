"""
Instruction Dialog Model

This module provides the model component for the instruction dialog in the Super Whisper application.
It handles the data management for instruction sets using the core InstructionManager.
"""

from PyQt6.QtCore import QObject, pyqtSignal

from core.pipelines.instruction_set import InstructionSet
from core.stt.stt_lang_model import STTLangModel
from core.stt.stt_model import STTModel
from core.llm.llm_model import LLMModel
from core.stt.stt_lang_model_manager import STTLangModelManager
from core.stt.stt_model_manager import STTModelManager
from core.llm.llm_model_manager import LLMModelManager

from ...models.instruction_set_model import InstructionSetModel


class InstructionDialogModel(QObject):
    """
    Model for the instruction dialog.
    
    This class encapsulates the data management for the instruction dialog,
    providing methods to manipulate instruction sets and their properties.
    It relies on InstructionSetModel for managing the actual instruction sets.
    
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
    hotkey_updated : pyqtSignal
        Signal emitted when a hotkey is updated
    """
    
    # Define signals
    instruction_set_added = pyqtSignal(InstructionSet)
    instruction_set_updated = pyqtSignal(InstructionSet)
    instruction_set_deleted = pyqtSignal(str)  # Name of deleted set
    instruction_set_renamed = pyqtSignal(str, str)  # Old name, new name
    hotkey_updated = pyqtSignal(str, str)  # Set name, hotkey
    
    def __init__(self, instruction_set_model: InstructionSetModel) -> None:
        """
        Initialize the InstructionDialogModel.
        
        Parameters
        ----------
        instruction_set_model : InstructionSetModel
            The main model for managing instruction sets
        """
        super().__init__()
        
        # Store instruction set model
        self._instruction_set_model = instruction_set_model
        
        # Get instruction manager from the model
        self._instruction_manager = instruction_set_model._instruction_manager
    
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
        return self._instruction_manager.find_set_by_name(name)
    
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
        return self._instruction_manager.find_set_by_hotkey(hotkey)
    
    def add_set(self, name: str, 
                stt_vocabulary: str = "", 
                stt_instructions: str = "",
                stt_language: str | None = None,
                stt_model: str = "gpt-4o-transcribe",
                llm_enabled: bool = False,
                llm_model: str = "gpt-4o",
                llm_instructions: str = "",
                llm_clipboard_text_enabled: bool = False,
                llm_clipboard_image_enabled: bool = False,
                hotkey: str = "") -> bool:
        """
        Add a new instruction set.
        
        Parameters
        ----------
        name : str
            Name for the new instruction set
        stt_vocabulary : str, optional
            Custom vocabulary for speech recognition, by default ""
        stt_instructions : str, optional
            System instructions for speech recognition, by default ""
        stt_language : str | None, optional
            Language code for speech recognition, by default None (auto-detect)
        stt_model : str, optional
            Model name for speech recognition, by default "gpt-4o-transcribe"
        llm_enabled : bool, optional
            Whether LLM processing is enabled, by default False
        llm_model : str, optional
            Model name for LLM processing, by default "gpt-4o"
        llm_instructions : str, optional
            System instructions for LLM, by default ""
        llm_clipboard_text_enabled : bool, optional
            Whether to include clipboard text in LLM input, by default False
        llm_clipboard_image_enabled : bool, optional
            Whether to include clipboard images in LLM input, by default False
        hotkey : str, optional
            Hotkey for quick activation, by default ""
            
        Returns
        -------
        bool
            True if successful, False if a set with the same name already exists
        """
        # Create a new instruction set
        instruction_set = InstructionSet(
            name=name,
            stt_vocabulary=stt_vocabulary,
            stt_instructions=stt_instructions,
            stt_language=stt_language,
            stt_model=stt_model,
            llm_enabled=llm_enabled,
            llm_model=llm_model,
            llm_instructions=llm_instructions,
            llm_clipboard_text_enabled=llm_clipboard_text_enabled,
            llm_clipboard_image_enabled=llm_clipboard_image_enabled,
            hotkey=hotkey
        )
        
        # Add the set
        result = self._instruction_manager.add_set(instruction_set)
        
        if result:
            # Save changes through the main model
            self._instruction_set_model.save_to_settings()
            
            # Emit signal
            self.instruction_set_added.emit(instruction_set)
            
            # Notify the main model
            self._instruction_set_model.instruction_sets_changed.emit()
        
        return result
    
    def update_set(self, name: str, 
                  stt_vocabulary: str | None = None, 
                  stt_instructions: str | None = None,
                  stt_language: str | None = None,
                  stt_model: str | None = None,
                  llm_enabled: bool | None = None,
                  llm_model: str | None = None,
                  llm_instructions: str | None = None,
                  llm_clipboard_text_enabled: bool | None = None,
                  llm_clipboard_image_enabled: bool | None = None,
                  hotkey: str | None = None) -> bool:
        """
        Update an existing instruction set.
        
        Parameters
        ----------
        name : str
            Name of the instruction set to update
        stt_vocabulary : str | None, optional
            Custom vocabulary for speech recognition, by default None (unchanged)
        stt_instructions : str | None, optional
            System instructions for speech recognition, by default None (unchanged)
        stt_language : str | None, optional
            Language code for speech recognition, by default None (unchanged)
        stt_model : str | None, optional
            Model name for speech recognition, by default None (unchanged)
        llm_enabled : bool | None, optional
            Whether LLM processing is enabled, by default None (unchanged)
        llm_model : str | None, optional
            Model name for LLM processing, by default None (unchanged)
        llm_instructions : str | None, optional
            System instructions for LLM, by default None (unchanged)
        llm_clipboard_text_enabled : bool | None, optional
            Whether to include clipboard text in LLM input, by default None (unchanged)
        llm_clipboard_image_enabled : bool | None, optional
            Whether to include clipboard images in LLM input, by default None (unchanged)
        hotkey : str | None, optional
            Hotkey for quick activation, by default None (unchanged)
            
        Returns
        -------
        bool
            True if successful, False if the set doesn't exist
        """
        # Get the instruction set
        instruction_set = self._instruction_manager.find_set_by_name(name)
        if not instruction_set:
            return False
        
        # Update the set
        instruction_set.update(
            stt_vocabulary=stt_vocabulary,
            stt_instructions=stt_instructions,
            stt_language=stt_language,
            stt_model=stt_model,
            llm_enabled=llm_enabled,
            llm_model=llm_model,
            llm_instructions=llm_instructions,
            llm_clipboard_text_enabled=llm_clipboard_text_enabled,
            llm_clipboard_image_enabled=llm_clipboard_image_enabled,
            hotkey=hotkey
        )
        
        # Save changes through the main model
        self._instruction_set_model.save_to_settings()
        
        # Emit hotkey updated signal if hotkey was updated
        if hotkey is not None:
            self.hotkey_updated.emit(name, hotkey)
        
        # Emit signal
        self.instruction_set_updated.emit(instruction_set)
        
        # Notify the main model
        self._instruction_set_model.instruction_sets_changed.emit()
        
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
        result = self._instruction_manager.delete_set(name)
        
        if result:
            # Save changes through the main model
            self._instruction_set_model.save_to_settings()
            
            # Emit signal
            self.instruction_set_deleted.emit(name)
            
            # Notify the main model
            self._instruction_set_model.instruction_sets_changed.emit()
        
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
            True if successful, False if the old set doesn't exist or the new name is already taken
        """
        # Rename the set
        result = self._instruction_manager.rename_set(old_name, new_name)
        
        if result:
            # Save changes through the main model
            self._instruction_set_model.save_to_settings()
            
            # Emit signal
            self.instruction_set_renamed.emit(old_name, new_name)
            
            # Notify the main model
            self._instruction_set_model.instruction_sets_changed.emit()
        
        return result
    
    def get_available_languages(self) -> list[STTLangModel]:
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
        return LLMModelManager.check_image_input_supported(model_id)
