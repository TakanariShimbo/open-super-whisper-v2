"""
Instruction Set Manager Module

This module provides the InstructionSetManagerModel class for managing
instruction sets in the application.
"""

from typing import List, Optional, Dict, Any
from PyQt6.QtCore import QObject, pyqtSignal, QSettings

from core.pipelines.instruction_manager import InstructionManager
from core.pipelines.instruction_set import InstructionSet


class InstructionSetManagerModel(QObject):
    """
    Model for managing instruction sets.
    
    This class provides functionality for managing instruction sets,
    including creating, updating, deleting, and selecting sets.
    It also handles persistence of sets to settings.
    
    Attributes
    ----------
    sets_changed : pyqtSignal
        Signal emitted when instruction sets change
    selected_set_changed : pyqtSignal
        Signal emitted when the selected set changes
    """
    
    # Signals
    sets_changed = pyqtSignal()
    selected_set_changed = pyqtSignal(str)
    
    def __init__(self, settings: QSettings) -> None:
        """
        Initialize the InstructionSetManagerModel.
        
        Parameters
        ----------
        settings : QSettings
            Settings object to store/retrieve instruction sets
        """
        super().__init__()
        
        # Store settings
        self._settings = settings
        
        # Core instruction manager
        self._core_manager = InstructionManager()
        
        # Selected set name
        self._selected_set_name = ""
        
        # Load instruction sets from settings
        self._load_from_settings()
        
        # If no sets, create default
        if not self._core_manager.get_all_sets():
            self._create_default_set()
    
    def _create_default_set(self) -> None:
        """
        Create a default instruction set.
        """
        # Create default set
        default_set = InstructionSet(name="Default")
        self._core_manager.add_set(default_set)
        
        # Set as selected
        self._selected_set_name = "Default"
        
        # Save to settings
        self._save_to_settings()
        
        # Emit signals
        self.sets_changed.emit()
        self.selected_set_changed.emit("Default")
    
    def _load_from_settings(self) -> None:
        """
        Load instruction sets from settings.
        """
        # Get from settings
        prefix = "InstructionSets"
        self._settings.beginGroup(prefix)
        
        # Load selected set
        selected_set = self._settings.value("SelectedSet", "")
        
        # Load sets
        sets_data = self._settings.value("Sets", [])
        
        self._settings.endGroup()
        
        # Convert to dict for core manager
        data = {"sets": sets_data}
        
        # Load into core manager
        self._core_manager.import_from_dict(data)
        
        # Set selected set if it exists
        if selected_set and self._core_manager.find_set_by_name(selected_set):
            self._selected_set_name = selected_set
        elif self._core_manager.get_all_sets():
            # Default to first set if selected set doesn't exist
            self._selected_set_name = self._core_manager.get_all_sets()[0].name
    
    def _save_to_settings(self) -> None:
        """
        Save instruction sets to settings.
        """
        data = self._core_manager.export_to_dict()
        
        # Save to settings
        prefix = "InstructionSets"
        self._settings.beginGroup(prefix)
        
        # Remove any existing sets first
        self._settings.remove("")
        
        # Save selected set
        self._settings.setValue("SelectedSet", self._selected_set_name)
        
        # Save sets
        self._settings.setValue("Sets", data["sets"])
        
        self._settings.endGroup()
        self._settings.sync()
    
    def get_all_sets(self) -> List[InstructionSet]:
        """
        Get all instruction sets.
        
        Returns
        -------
        List[InstructionSet]
            List of all instruction sets
        """
        return self._core_manager.get_all_sets()
    
    def get_set_by_name(self, name: str) -> Optional[InstructionSet]:
        """
        Get an instruction set by name.
        
        Parameters
        ----------
        name : str
            Name of the instruction set to get
        
        Returns
        -------
        Optional[InstructionSet]
            The instruction set, or None if not found
        """
        return self._core_manager.find_set_by_name(name)
    
    def get_set_by_hotkey(self, hotkey: str) -> Optional[InstructionSet]:
        """
        Get an instruction set by hotkey.
        
        Parameters
        ----------
        hotkey : str
            Hotkey of the instruction set to get
        
        Returns
        -------
        Optional[InstructionSet]
            The instruction set, or None if not found
        """
        return self._core_manager.find_set_by_hotkey(hotkey)
    
    def get_selected_set_name(self) -> str:
        """
        Get the name of the currently selected instruction set.
        
        Returns
        -------
        str
            Name of the selected instruction set
        """
        return self._selected_set_name
    
    def get_selected_set(self) -> Optional[InstructionSet]:
        """
        Get the currently selected instruction set.
        
        Returns
        -------
        Optional[InstructionSet]
            The selected instruction set, or None if not found
        """
        return self._core_manager.find_set_by_name(self._selected_set_name)
    
    def set_selected(self, name: str) -> bool:
        """
        Set the selected instruction set.
        
        Parameters
        ----------
        name : str
            Name of the instruction set to select
        
        Returns
        -------
        bool
            True if successful, False if name doesn't exist
        """
        # Check if set exists
        if not self._core_manager.find_set_by_name(name):
            return False
        
        # Set selected
        self._selected_set_name = name
        
        # Save to settings
        self._save_to_settings()
        
        # Emit signal
        self.selected_set_changed.emit(name)
        
        return True
    
    def create_set(self, name: str) -> bool:
        """
        Create a new instruction set.
        
        Parameters
        ----------
        name : str
            Name of the new instruction set
        
        Returns
        -------
        bool
            True if successful, False if name already exists
        """
        # Create new set
        new_set = InstructionSet(name=name)
        
        # Add to manager
        result = self._core_manager.add_set(new_set)
        
        if result:
            # Save to settings
            self._save_to_settings()
            
            # Emit signal
            self.sets_changed.emit()
        
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
            True if successful, False if name doesn't exist or last set
        """
        # Delete from manager
        result = self._core_manager.delete_set(name)
        
        if result:
            # If deleting the selected set, select another one
            if name == self._selected_set_name:
                sets = self._core_manager.get_all_sets()
                if sets:
                    self._selected_set_name = sets[0].name
                else:
                    self._selected_set_name = ""
            
            # Save to settings
            self._save_to_settings()
            
            # Emit signals
            self.sets_changed.emit()
            if sets:
                self.selected_set_changed.emit(self._selected_set_name)
        
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
            True if successful, False if old name doesn't exist or new name exists
        """
        # Rename in manager
        result = self._core_manager.rename_set(old_name, new_name)
        
        if result:
            # Update selected set name if it was renamed
            if old_name == self._selected_set_name:
                self._selected_set_name = new_name
                self.selected_set_changed.emit(new_name)
            
            # Save to settings
            self._save_to_settings()
            
            # Emit signal
            self.sets_changed.emit()
        
        return result
    
    def update_set(self, name: str, **kwargs) -> bool:
        """
        Update an instruction set.
        
        Parameters
        ----------
        name : str
            Name of the instruction set to update
        **kwargs
            Keyword arguments to update in the instruction set
            
        Returns
        -------
        bool
            True if successful, False if name doesn't exist
        """
        # Get the set
        instruction_set = self._core_manager.find_set_by_name(name)
        
        if not instruction_set:
            return False
        
        # Update the set
        instruction_set.update(**kwargs)
        
        # Save to settings
        self._save_to_settings()
        
        # Emit signal
        self.sets_changed.emit()
        
        return True
