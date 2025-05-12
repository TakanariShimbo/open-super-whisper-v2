"""
Status Indicator Controller

This module provides the controller component for the status indicator window,
following the MVC architecture.
"""

from PyQt6.QtCore import QObject, pyqtSlot

from ...models.widgets.status_indicator_model import StatusIndicatorModel
from ...views.widgets.status_indicator import StatusIndicatorWindow
from ...utils.settings_manager import SettingsManager


class StatusIndicatorController(QObject):
    """
    Controller for the status indicator.
    
    This class handles interactions between the status indicator view and model.
    It updates the view based on state changes in the model and responds to user
    interactions with the view.
    """
    
    def __init__(self, model: StatusIndicatorModel, parent=None) -> None:
        """
        Initialize the controller.
        
        Parameters
        ----------
        model : StatusIndicatorModel
            The model component for the status indicator
        parent : QObject, optional
            Parent object, by default None
        """
        super().__init__(parent)
        
        # Store model reference
        self.model = model
        
        # Get settings manager
        self.settings_manager = SettingsManager.instance()
        
        # Create view
        self.view = StatusIndicatorWindow()
        
        # Connect model signals to update view
        self.model.mode_changed.connect(self.on_mode_changed)
        self.model.timer_updated.connect(self.on_timer_updated)
        self.model.visibility_changed.connect(self.on_visibility_changed)
        
    @pyqtSlot(int)
    def on_mode_changed(self, mode: int) -> None:
        """
        Handle mode changes from the model.
        
        Parameters
        ----------
        mode : int
            The new mode value
        """
        self.view.set_mode(mode)
        
    @pyqtSlot(str)
    def on_timer_updated(self, time_str: str) -> None:
        """
        Handle timer updates from the model.
        
        Parameters
        ----------
        time_str : str
            The new time string
        """
        self.view.update_timer(time_str)
        
    @pyqtSlot(bool)
    def on_visibility_changed(self, visible: bool) -> None:
        """
        Handle visibility changes from the model.
        
        Parameters
        ----------
        visible : bool
            Whether the indicator should be visible
        """
        # Only show indicator if settings allow it
        indicator_visible_setting = self.settings_manager.get_indicator_visible()
        
        if visible and indicator_visible_setting:
            self.view.show()
        else:
            self.view.hide()
            
    def set_mode(self, mode: int) -> None:
        """
        Set the indicator mode.
        
        Parameters
        ----------
        mode : int
            Mode constant (MODE_RECORDING, MODE_PROCESSING, MODE_COMPLETED, MODE_CANCELLED)
        """
        self.model.set_mode(mode)
        
    def update_timer(self, elapsed_time: float = None) -> None:
        """
        Update the timer display.
        
        Parameters
        ----------
        elapsed_time : float, optional
            Elapsed time in seconds, by default uses model's tracking
        """
        self.model.update_timer(elapsed_time)
        
    def show_indicator(self) -> None:
        """
        Show the status indicator window.
        """
        self.model.set_visible(True)
        
    def hide_indicator(self) -> None:
        """
        Hide the status indicator window.
        """
        self.model.set_visible(False)
        
    def start_recording(self) -> None:
        """
        Start recording mode and timer.
        """
        self.model.start_recording()
        
    def start_processing(self) -> None:
        """
        Start processing mode.
        """
        self.model.start_processing()
        
    def complete_processing(self) -> None:
        """
        Set completion mode.
        """
        self.model.complete_processing()
        
    def cancel_processing(self) -> None:
        """
        Set cancelled mode.
        """
        self.model.cancel_processing()
