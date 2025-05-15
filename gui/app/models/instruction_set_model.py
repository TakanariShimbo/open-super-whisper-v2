"""
Instruction Set Model

This module provides the model component for managing instruction sets
in the Super Whisper application.
"""

from PyQt6.QtCore import QObject, pyqtSignal

from core.pipelines.instruction_set import InstructionSet
from core.pipelines.instruction_manager import InstructionManager
from ..manager.settings_manager import SettingsManager


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
    instruction_sets_changed = pyqtSignal()
    selected_set_changed = pyqtSignal(InstructionSet)
    
    def __init__(self):
        """
        Initialize the InstructionSetModel.
        """
        super().__init__()
        
        # Initialize instruction manager
        self._instruction_manager = InstructionManager()
        
        # Store settings manager for persistence
        self._settings_manager = SettingsManager.instance()
        
        # Track selected instruction set
        self._selected_set_name = ""
        
        # Load data and ensure valid state
        self.load_from_settings()
        
        # Save settings after initialization to ensure persistence
        self.save_to_settings()
    
    def _load_data_from_settings(self) -> None:
        """
        Load instruction sets data from settings.
        
        This method loads raw data from settings without enforcing state validity.
        """
        if not self._settings_manager:
            return
            
        # Try to load instruction sets
        serialized_data = self._settings_manager.get_instruction_sets()
        if serialized_data:
            try:
                self._instruction_manager.import_from_dict(serialized_data)
            except Exception as e:
                print(f"Failed to load instruction sets from settings: {e}")
                
        # Load selected set name without validation
        self._selected_set_name = self._settings_manager.get_selected_instruction_set()
    
    def _ensure_valid_state(self) -> None:
        """
        Ensure the model is in a valid state.
        
        This method ensures:
        1. At least one instruction set exists (creates Default if needed)
        2. A valid selection is made
        """
        # Get current instruction sets
        instruction_sets = self._instruction_manager.get_all_sets()
        
        # Create default set if none exist
        if not instruction_sets:
            default_set = InstructionSet(name="Default")
            self._instruction_manager.add_set(default_set)
            instruction_sets = [default_set]
        
        # Ensure a valid selection
        valid_selection = (self._selected_set_name and 
                          self._instruction_manager.find_set_by_name(self._selected_set_name))
                          
        if not valid_selection:
            self._selected_set_name = instruction_sets[0].name
    
    def _save_to_settings(self) -> None:
        """
        Save instruction sets to settings.
        
        This is an internal method that persists the model's state to settings.
        """
        if not self._settings_manager:
            return
            
        # Save instruction sets
        serialized_data = self._instruction_manager.export_to_dict()
        self._settings_manager.set_instruction_sets(serialized_data)
        
        # Save selected set
        self._settings_manager.set_selected_instruction_set(self._selected_set_name)
        
    def save_to_settings(self) -> None:
        """
        Save instruction sets to QSettings.
        """
        self._save_to_settings()
        
    def load_from_settings(self) -> None:
        """
        Load instruction sets from QSettings.
        """
        self._load_data_from_settings()
        self._ensure_valid_state()
    
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
            
        return self._instruction_manager.find_set_by_name(self._selected_set_name)
    
    def get_selected_set_name(self) -> str:
        """
        Get the name of the currently selected instruction set.
        
        Returns
        -------
        str
            The name of the currently selected instruction set, or an empty string
        """
        return self._selected_set_name
    
    def set_selected(self, name: str) -> bool:
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
        instruction_set = self._instruction_manager.find_set_by_name(name)
        if not instruction_set:
            return False
            
        self._selected_set_name = name
        self._save_to_settings()
        
        # Emit the selected set changed signal
        self.selected_set_changed.emit(instruction_set)
        
        return True
