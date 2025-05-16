"""
Instruction Sets Manager

This module provides the manager component for managing instruction sets
in the Super Whisper application.
"""

from core.pipelines.instruction_set import InstructionSet
from core.pipelines.instruction_sets_manager import InstructionSetsManager as CoreInstructionSetsManager
from ..managers.settings_manager import SettingsManager


class InstructionSetsManager:
    """
    Manager for managing instruction sets.

    This class provides a manager for managing instruction sets.
    """
    
    # Singleton instance
    _instance = None

    @classmethod
    def get_instance(cls) -> "InstructionSetsManager":
        """
        Get the singleton instance of the InstructionSetsManager.

        Returns
        -------
        InstructionSetsManager
            The singleton instance of the InstructionSetsManager.
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def __init__(self):
        """
        Initialize the InstructionSetsManager.

        Raises
        ------
        Exception
            If the InstructionSetsManager is already instantiated.
        """
        if self._instance is not None:
            raise Exception("InstructionSetsManager is a singleton class and cannot be instantiated directly.")

        self._instance = self
        
        # Initialize instruction sets manager
        self._instruction_sets_manager = CoreInstructionSetsManager()
        
        # Store settings manager for persistence
        self._settings_manager = SettingsManager.instance()
        
        # Track selected instruction set
        self._selected_set_name = ""
        
        # Load data and ensure valid state
        self.load_from_settings()
    
    def find_set_by_name(self, name: str) -> InstructionSet | None:
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
    
    def find_set_by_hotkey(self, hotkey: str) -> InstructionSet | None:
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
        if not self._selected_set_name:
            return None
            
        return self._instruction_sets_manager.find_set_by_name(self._selected_set_name)
    
    def get_selected_set_name(self) -> str:
        """
        Get the name of the currently selected instruction set.
        
        Returns
        -------
        str
            The name of the currently selected instruction set, or an empty string
        """
        return self._selected_set_name
    
    def set_selected_set_name(self, instruction_set_name: str) -> bool:
        """
        Set the selected instruction set by name.
        
        Parameters
        ----------
        instruction_set_name : str
            Name of the instruction set to select
            
        Returns
        -------
        bool
            True if successful, False if the named set doesn't exist
        """
        instruction_set = self._instruction_sets_manager.find_set_by_name(instruction_set_name)
        if not instruction_set:
            return False
            
        self._selected_set_name = instruction_set_name
        self._save_to_settings()
        
        return True
    
    def add_set(self, instruction_set: InstructionSet) -> bool:
        """
        Add a new instruction set.
        
        Parameters
        ----------
        instruction_set : InstructionSet
            The instruction set to add.
            
        Returns
        -------
        bool
            True if set was added, False if a set with the same name already exists.
        """
        return self._instruction_sets_manager.add_set(instruction_set)
        
    def delete_set(self, name: str) -> bool:
        """
        Delete an instruction set.
        
        Parameters
        ----------
        name : str
            Name of the instruction set to delete.
            
        Returns
        -------
        bool
            True if set was deleted, False if name doesn't exist or if it's the last set.
        """
        return self._instruction_sets_manager.delete_set(name)
    
    def rename_set(self, old_name: str, new_name: str) -> bool:
        """
        Rename an instruction set.
        
        Parameters
        ----------
        old_name : str
            Current name of the instruction set.
        new_name : str
            New name for the instruction set.
            
        Returns
        -------
        bool
            True if set was renamed, False if old name doesn't
            exist or new name already exists.
        """        
        return self._instruction_sets_manager.rename_set(old_name, new_name)
    
    def get_all_sets(self) -> list[InstructionSet]:
        """
        Get all instruction sets.
        
        Returns
        -------
        list[InstructionSet]
            List of all instruction sets
        """
        return self._instruction_sets_manager.get_all_sets()
    
    def _load_data_from_settings(self) -> None:
        """
        Load instruction sets data from settings.
        
        This method loads raw data from settings without enforcing state validity.
        """
        # Try to load instruction sets
        serialized_data = self._settings_manager.get_instruction_sets()
        if serialized_data:
            try:
                self._instruction_sets_manager.import_from_dict(serialized_data)
            except Exception as e:
                print(f"Failed to load instruction sets from settings: {e}")
                
        # Load selected set name without validation
        self._selected_set_name = self._settings_manager.get_selected_instruction_set()
    
    def _ensure_valid_state(self) -> None:
        """
        Ensure the manager is in a valid state.
        """
        # Create default set if none exist
        has_instruction_sets = self._instruction_sets_manager.get_all_sets()
        if not has_instruction_sets:
            default_set = InstructionSet.get_default()
            self._instruction_sets_manager.add_set(default_set)
        
        # Ensure a valid selection
        is_valid_selection = (self._selected_set_name and self._instruction_sets_manager.find_set_by_name(self._selected_set_name))           
        if not is_valid_selection:
            self._selected_set_name = self._instruction_sets_manager.get_all_sets()[0].name
    
    def _save_to_settings(self) -> None:
        """
        Save instruction sets to settings.
        
        This is an internal method that persists the model's state to settings.
        """
        # Save instruction sets
        serialized_data = self._instruction_sets_manager.export_to_dict()
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
        # Load data from settings
        self._load_data_from_settings()

        # Ensure valid state and save to settings
        self._ensure_valid_state()
        self._save_to_settings()