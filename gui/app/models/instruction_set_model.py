"""
Instruction Set Model

This module provides the model component for managing instruction sets
in the Super Whisper application.
"""

from PyQt6.QtCore import QObject, pyqtSignal

from core.pipelines.instruction_set import InstructionSet
from ..managers.instruction_sets_manager import InstructionSetsManager


class InstructionSetModel(QObject):
    """
    Model for managing instruction sets.
    
    This class encapsulates the core InstructionManager functionality and
    provides a Qt-friendly interface with signals for instruction set events.
    
    Attributes
    ----------
    instruction_sets_changed : pyqtSignal
        Signal emitted when the collection of instruction sets changes
    selected_set_changed : pyqtSignal
        Signal emitted when the selected instruction set changes
    """
    
    # Define signals
    selected_set_changed = pyqtSignal(InstructionSet)
    
    def __init__(self):
        """
        Initialize the InstructionSetModel.
        """
        super().__init__()
        
        # Initialize instruction manager
        self._instruction_sets_manager = InstructionSetsManager.get_instance()
        
    def save_to_settings(self) -> None:
        """
        Save instruction sets to QSettings.
        """
        self._instruction_sets_manager.save_to_settings()
        
    def load_from_settings(self) -> None:
        """
        Load instruction sets from QSettings.
        """
        self._instruction_sets_manager.load_from_settings()
    
    def get_all_sets(self) -> list[InstructionSet]:
        """
        Get all instruction sets.
        
        Returns
        -------
        list[InstructionSet]
            List of all instruction sets
        """
        return self._instruction_sets_manager.get_all_sets()
    
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
        return self._instruction_sets_manager.find_set_by_name(name)
    
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
        return self._instruction_sets_manager.find_set_by_hotkey(hotkey)
    
    def get_selected_set(self) -> InstructionSet | None:
        """
        Get the currently selected instruction set.
        
        Returns
        -------
        InstructionSet | None
            The currently selected instruction set, or None if none selected
        """
        return self._instruction_sets_manager.get_selected_set()
    
    def get_selected_set_name(self) -> str:
        """
        Get the name of the currently selected instruction set.
        
        Returns
        -------
        str
            The name of the currently selected instruction set, or an empty string
        """
        return self._instruction_sets_manager.get_selected_set_name()
    
    def set_selected_set_name(self, name: str) -> bool:
        """
        Set the selected instruction set by name.
        
        Parameters
        ----------
        name : str
            Name of the instruction set to select
            
        Returns
        -------
        bool
            True if successful, False if the named set doesn't exist
        """
        is_success = self._instruction_sets_manager.set_selected_set_name(name)
        if not is_success:
            return False
        
        # Emit the selected set changed signal
        self.selected_set_changed.emit(self._instruction_sets_manager.get_selected_set())
        
        return True
