"""
Instruction Set Model

This module provides the model component for managing instruction sets
in the Super Whisper application.
"""

from typing import List, Optional, Dict, Any
from PyQt6.QtCore import QObject, pyqtSignal, QSettings

from core.pipelines.instruction_set import InstructionSet
from core.pipelines.instruction_manager import InstructionManager

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
    
    def __init__(self, settings: Optional[QSettings] = None):
        """
        Initialize the InstructionSetModel.
        
        Parameters
        ----------
        settings : QSettings, optional
            QSettings object for storing instruction sets, by default None
        """
        super().__init__()
        
        # Initialize instruction manager
        self._instruction_manager = InstructionManager()
        
        # Store settings for persistence
        self._settings = settings
        
        # Track selected instruction set
        self._selected_set_name = ""
        
        # Load instruction sets from settings if available
        self._load_from_settings()
        
        # Add default instruction set if none exist
        if not self._instruction_manager.get_all_sets():
            default_set = InstructionSet(name="Default")
            self._instruction_manager.add_set(default_set)
            self._selected_set_name = "Default"
    
    def _load_from_settings(self):
        """
        Load instruction sets from QSettings.
        """
        if not self._settings:
            return
            
        # Try to load instruction sets
        serialized_data = self._settings.value("instruction_sets")
        if serialized_data:
            try:
                self._instruction_manager.import_from_dict(serialized_data)
            except Exception:
                # If loading fails, we'll start with an empty manager
                pass
                
        # Load selected set name
        self._selected_set_name = self._settings.value("selected_instruction_set", "")
        
        # Ensure selected set exists
        if self._selected_set_name:
            if not self._instruction_manager.find_set_by_name(self._selected_set_name):
                # Selected set doesn't exist, reset to first available
                sets = self._instruction_manager.get_all_sets()
                if sets:
                    self._selected_set_name = sets[0].name
                else:
                    self._selected_set_name = ""
    
    def _save_to_settings(self):
        """
        Save instruction sets to QSettings.
        """
        if not self._settings:
            return
            
        # Save instruction sets
        serialized_data = self._instruction_manager.export_to_dict()
        self._settings.setValue("instruction_sets", serialized_data)
        
        # Save selected set
        self._settings.setValue("selected_instruction_set", self._selected_set_name)
        
        # Sync settings to disk
        self._settings.sync()
    
    def get_all_sets(self) -> List[InstructionSet]:
        """
        Get all instruction sets.
        
        Returns
        -------
        List[InstructionSet]
            List of all instruction sets
        """
        return self._instruction_manager.get_all_sets()
    
    def get_set_by_name(self, name: str) -> Optional[InstructionSet]:
        """
        Get an instruction set by name.
        
        Parameters
        ----------
        name : str
            Name of the instruction set to find
            
        Returns
        -------
        Optional[InstructionSet]
            The instruction set with the specified name, or None if not found
        """
        return self._instruction_manager.find_set_by_name(name)
    
    def get_set_by_hotkey(self, hotkey: str) -> Optional[InstructionSet]:
        """
        Get an instruction set by hotkey.
        
        Parameters
        ----------
        hotkey : str
            Hotkey string to match
            
        Returns
        -------
        Optional[InstructionSet]
            The instruction set with the specified hotkey, or None if not found
        """
        return self._instruction_manager.find_set_by_hotkey(hotkey)
    
    def get_selected_set(self) -> Optional[InstructionSet]:
        """
        Get the currently selected instruction set.
        
        Returns
        -------
        Optional[InstructionSet]
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
    
    def add_set(self, instruction_set: InstructionSet) -> bool:
        """
        Add a new instruction set.
        
        Parameters
        ----------
        instruction_set : InstructionSet
            The instruction set to add
            
        Returns
        -------
        bool
            True if successful, False if a set with the same name already exists
        """
        result = self._instruction_manager.add_set(instruction_set)
        if result:
            self._save_to_settings()
            self.instruction_sets_changed.emit()
            
        return result
    
    def update_set(self, name: str, updated_set: InstructionSet) -> bool:
        """
        Update an existing instruction set.
        
        Parameters
        ----------
        name : str
            Name of the instruction set to update
        updated_set : InstructionSet
            New instruction set data
            
        Returns
        -------
        bool
            True if successful, False if the set doesn't exist
        """
        # This is a bit of a workaround since InstructionManager doesn't have an update method
        # We delete the existing set and add the updated one
        existing_set = self._instruction_manager.find_set_by_name(name)
        if not existing_set:
            return False
            
        # Don't allow deleting if it's the last set
        sets = self._instruction_manager.get_all_sets()
        if len(sets) <= 1:
            return False
            
        # Delete old set first (the manager prohibits two sets with the same name)
        self._instruction_manager.delete_set(name)
        
        # Add updated set
        result = self._instruction_manager.add_set(updated_set)
        
        # Update selected set name if it was updated
        if result and self._selected_set_name == name:
            self._selected_set_name = updated_set.name
            
        self._save_to_settings()
        self.instruction_sets_changed.emit()
        
        # If this was the selected set, emit the change signal
        if result and (self._selected_set_name == updated_set.name):
            self.selected_set_changed.emit(updated_set)
            
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
        # Check if the set exists
        existing_set = self._instruction_manager.find_set_by_name(name)
        if not existing_set:
            return False
            
        # Get all sets first to potentially select another one
        sets = self._instruction_manager.get_all_sets()
        
        # Don't allow deleting if it's the last set 
        # (although InstructionManager already prevents this)
        if len(sets) <= 1:
            return False
            
        # Delete the set
        result = self._instruction_manager.delete_set(name)
        
        if result:
            # If we deleted the selected set, select another one
            if self._selected_set_name == name:
                # Find a different set to select
                remaining_sets = self._instruction_manager.get_all_sets()
                if remaining_sets:
                    self._selected_set_name = remaining_sets[0].name
                    self.selected_set_changed.emit(remaining_sets[0])
                else:
                    self._selected_set_name = ""
                    
            self._save_to_settings()
            self.instruction_sets_changed.emit()
            
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
        result = self._instruction_manager.rename_set(old_name, new_name)
        
        if result:
            # Update selected set name if it was renamed
            if self._selected_set_name == old_name:
                self._selected_set_name = new_name
                
            self._save_to_settings()
            self.instruction_sets_changed.emit()
            
            # If this was the selected set, emit the change signal
            if self._selected_set_name == new_name:
                self.selected_set_changed.emit(
                    self._instruction_manager.find_set_by_name(new_name)
                )
                
        return result
