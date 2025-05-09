"""
Settings Dialog Controller

This module provides the controller component for the settings dialog,
mediating between the model and view.
"""

from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot

from ...models.dialogs.settings_dialog_model import SettingsDialogModel
from ...utils.audio_manager import AudioManager


class SettingsDialogController(QObject):
    """
    Controller for the settings dialog.
    
    This class mediates between the settings dialog view and model,
    handling user interactions and updating the model and view accordingly.
    
    Attributes
    ----------
    sound_enabled_changed : pyqtSignal
        Signal emitted when sound enabled setting changes
    indicator_visible_changed : pyqtSignal
        Signal emitted when indicator visibility setting changes
    auto_clipboard_changed : pyqtSignal
        Signal emitted when auto clipboard setting changes
    """
    
    # Define signals for view communication
    sound_enabled_changed = pyqtSignal(bool)
    indicator_visible_changed = pyqtSignal(bool)
    auto_clipboard_changed = pyqtSignal(bool)
    
    def __init__(self, parent_controller: QObject | None = None) -> None:
        """
        Initialize the SettingsDialogController.
        
        Parameters
        ----------
        parent_controller : QObject | None, optional
            The parent controller, by default None
        """
        super().__init__()
        
        # Create model
        self._dialog_model = SettingsDialogModel()
        self._parent_controller = parent_controller
        
        # Connect model signals
        self._connect_model_signals()
    
    def _connect_model_signals(self) -> None:
        """
        Connect signals from the model to controller handlers.
        """
        self._dialog_model.sound_enabled_changed.connect(self._on_sound_enabled_changed)
        self._dialog_model.indicator_visible_changed.connect(self._on_indicator_visible_changed)
        self._dialog_model.auto_clipboard_changed.connect(self._on_auto_clipboard_changed)
    
    @pyqtSlot(bool)
    def _on_sound_enabled_changed(self, enabled: bool) -> None:
        """
        Handle sound enabled change from the model.
        
        Parameters
        ----------
        enabled : bool
            New sound enabled value
        """
        # Forward signal to view
        self.sound_enabled_changed.emit(enabled)
    
    @pyqtSlot(bool)
    def _on_indicator_visible_changed(self, visible: bool) -> None:
        """
        Handle indicator visibility change from the model.
        
        Parameters
        ----------
        visible : bool
            New indicator visibility value
        """
        # Forward signal to view
        self.indicator_visible_changed.emit(visible)
    
    @pyqtSlot(bool)
    def _on_auto_clipboard_changed(self, enabled: bool) -> None:
        """
        Handle auto clipboard change from the model.
        
        Parameters
        ----------
        enabled : bool
            New auto clipboard value
        """
        # Forward signal to view
        self.auto_clipboard_changed.emit(enabled)
    
    def get_sound_enabled(self) -> bool:
        """
        Get current sound enabled setting.
        
        Returns
        -------
        bool
            True if sound is enabled, False otherwise
        """
        return self._dialog_model.sound_enabled
    
    def set_sound_enabled(self, enabled: bool) -> None:
        """
        Set sound enabled setting.
        
        Parameters
        ----------
        enabled : bool
            True to enable sound, False to disable
        """
        self._dialog_model.sound_enabled = enabled
    
    def get_indicator_visible(self) -> bool:
        """
        Get current indicator visibility setting.
        
        Returns
        -------
        bool
            True if indicator should be visible, False otherwise
        """
        return self._dialog_model.indicator_visible
    
    def set_indicator_visible(self, visible: bool) -> None:
        """
        Set indicator visibility setting.
        
        Parameters
        ----------
        visible : bool
            True to make indicator visible, False to hide
        """
        self._dialog_model.indicator_visible = visible
    
    def get_auto_clipboard(self) -> bool:
        """
        Get current auto clipboard setting.
        
        Returns
        -------
        bool
            True if auto-clipboard is enabled, False otherwise
        """
        return self._dialog_model.auto_clipboard
    
    def set_auto_clipboard(self, enabled: bool) -> None:
        """
        Set auto clipboard setting.
        
        Parameters
        ----------
        enabled : bool
            True to enable auto-clipboard, False to disable
        """
        self._dialog_model.auto_clipboard = enabled
    
    def save_settings(self) -> None:
        """
        Save current settings to persistent storage and update related components.
        """
        # Save settings to persistent storage
        self._dialog_model.save_settings()
        
        # Update AudioManager with new settings
        audio_manager = AudioManager.instance()
        audio_manager.set_enabled(self._dialog_model.sound_enabled)
    
    def cancel(self) -> None:
        """
        Cancel dialog and restore original settings.
        """
        self._dialog_model.restore_original()
