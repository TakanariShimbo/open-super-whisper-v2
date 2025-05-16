"""
Hotkey Dialog Factory

This module provides a factory for creating hotkey dialog instances,
following the factory design pattern to centralize dialog creation logic.
"""

from ..dialogs.hotkey_dialog import HotkeyDialog


class HotkeyDialogFactory:
    """
    Factory class for creating hotkey dialog instances.
    
    This class provides methods to create properly configured hotkey
    dialog instances with their controllers, following the MVC pattern.
    """
    
    @staticmethod
    def create_dialog(
        parent=None, 
        current_hotkey: str = ""
    ) -> HotkeyDialog:
        """
        Create a hotkey dialog instance.
        
        This method creates a new hotkey dialog with its controller,
        properly configured and ready to use.
        
        Parameters
        ----------
        parent : QWidget, optional
            Parent widget for the dialog, by default None
        current_hotkey : str, optional
            Current hotkey value, by default ""
            
        Returns
        -------
        HotkeyDialog
            The created hotkey dialog instance
        """
        # Create a hotkey dialog with the controller
        dialog = HotkeyDialog(
            parent=parent,
            current_hotkey=current_hotkey
        )
        
        return dialog
