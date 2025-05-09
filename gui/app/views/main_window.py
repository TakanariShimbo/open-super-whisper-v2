"""
Main Window View

This module provides the main application window for the Super Whisper application,
implementing the view component of the MVC architecture.
"""

import sys

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QPushButton, 
    QLabel, QTextEdit, QComboBox,
    QGridLayout, QFormLayout, QTabWidget, QStatusBar,
    QMessageBox, QSystemTrayIcon
)
from PyQt6.QtCore import Qt, pyqtSlot, QSettings, QTimer
from PyQt6.QtGui import QAction, QCloseEvent

from core.pipelines.pipeline_result import PipelineResult
from core.pipelines.instruction_set import InstructionSet

from ..controllers.app_controller import AppController
from ..utils.icon_manager import IconManager
from ..utils.clipboard_utils import ClipboardUtils
from ..utils.audio_manager import AudioManager
from .tray.system_tray import SystemTray

class MainWindow(QMainWindow):
    """
    Main application window.
    
    This class represents the main user interface for the Super Whisper application.
    It presents the recording controls, transcription output, and application settings.
    
    Attributes
    ----------
    controller : AppController
        The application controller that manages the business logic
    """
    
    def __init__(self, controller: AppController, settings: QSettings):
        """
        Initialize the MainWindow.
        
        Parameters
        ----------
        controller : AppController
            The application controller
        settings : QSettings
            The application settings
        """
        super().__init__()
        
        # Store references
        self.controller = controller
        self.settings = settings
        
        # Get settings
        self.api_key = settings.value("api_key", "")
        
        # Initialize icon manager
        self.icon_manager = IconManager()
        
        # Initialize audio manager
        self.audio_manager = AudioManager(settings)
        
        # Set application icon
        self.setWindowIcon(self.icon_manager.get_app_icon())
        
        # Flag to track if the application is actually closing
        self._is_closing = False
        
        # Set up UI
        self.setup_ui()
        
        # Set up system tray
        self.setup_system_tray()
        
        # Connect signals from controller
        self.connect_controller_signals()
        
        # Check API key
        if not self.api_key:
            QTimer.singleShot(100, self.show_api_key_dialog)
        
        # Register instruction set hotkeys
        self.register_instruction_set_hotkeys()
    
    def setup_ui(self):
        """
        Set up the user interface.
        """
        # Set window properties
        self.setWindowTitle("Super Whisper App")
        self.setMinimumSize(700, 500)
        
        # Create central widget and main layout
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        
        # Create toolbar
        self.create_toolbar()
        
        # Create control panel
        control_panel = QWidget()
        control_layout = QGridLayout(control_panel)
        
        # Record button
        self.record_button = QPushButton("Start Recording")
        self.record_button.setMinimumHeight(50)
        self.record_button.clicked.connect(self.on_record_button_click)
        
        # Instruction set selection
        instruction_set_form = QWidget()
        form_layout = QFormLayout(instruction_set_form)
        
        instruction_set_label = QLabel("Instruction Set:")
        self.instruction_set_combo = QComboBox()
        self.instruction_set_combo.setMinimumWidth(200)
        self.instruction_set_combo.currentIndexChanged.connect(self.on_instruction_set_changed)
        form_layout.addRow(instruction_set_label, self.instruction_set_combo)
        
        # Add to layout
        control_layout.addWidget(self.record_button, 0, 0, 2, 1)
        control_layout.addWidget(instruction_set_form, 0, 1, 2, 5)
        control_layout.setColumnStretch(0, 1)
        control_layout.setColumnStretch(1, 3)
        
        main_layout.addWidget(control_panel)
        
        # Create tab widget for outputs
        self.tab_widget = QTabWidget()
        
        # Transcription tab
        transcription_tab = QWidget()
        transcription_layout = QVBoxLayout(transcription_tab)
        
        transcription_label = QLabel("Transcription Output:")
        transcription_layout.addWidget(transcription_label)
        
        self.transcription_text = QTextEdit()
        self.transcription_text.setPlaceholderText("Transcription will appear here...")
        self.transcription_text.setReadOnly(False)  # Allow editing
        transcription_layout.addWidget(self.transcription_text)
        
        # LLM output tab (if LLM is enabled in instruction set)
        llm_tab = QWidget()
        llm_layout = QVBoxLayout(llm_tab)
        
        llm_label = QLabel("LLM Output:")
        llm_layout.addWidget(llm_label)
        
        self.llm_text = QTextEdit()
        self.llm_text.setPlaceholderText("LLM processing output will appear here...")
        self.llm_text.setReadOnly(False)  # Allow editing
        llm_layout.addWidget(self.llm_text)
        
        # Add tabs
        self.tab_widget.addTab(transcription_tab, "Transcription")
        self.tab_widget.addTab(llm_tab, "LLM Output")
        
        main_layout.addWidget(self.tab_widget, 1)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Status indicator
        self.status_indicator = QLabel("Ready")
        self.status_bar.addPermanentWidget(self.status_indicator)
        
        # Set central widget
        self.setCentralWidget(central_widget)
        
        # Populate instruction sets combo
        self.populate_instruction_set_combo()
    
    def setup_system_tray(self):
        """
        Set up the system tray icon.
        """
        # Get the icon path from the icon manager
        icon_path = self.icon_manager.get_icon_path("app")
        
        # Create system tray with the icon
        self.system_tray = SystemTray(icon_path)
        
        # Connect system tray signals
        self.system_tray.show_window_signal.connect(self.show_window)
        self.system_tray.hide_window_signal.connect(self.hide_window)
        self.system_tray.quit_application_signal.connect(self.quit_application)
        self.system_tray.toggle_recording_signal.connect(self.on_record_button_click)
        
        # Show system tray icon
        self.system_tray.show()
    
    def create_toolbar(self):
        """
        Create the application toolbar.
        """
        self.toolbar = self.addToolBar("Main Toolbar")
        self.toolbar.setMovable(False)
        
        # API key action
        api_action = QAction("API Key Settings", self)
        api_action.triggered.connect(self.show_api_key_dialog)
        self.toolbar.addAction(api_action)
        
        # Instruction sets action
        instruction_sets_action = QAction("Manage Instruction Sets", self)
        instruction_sets_action.triggered.connect(self.show_instruction_sets_dialog)
        self.toolbar.addAction(instruction_sets_action)
        
        self.toolbar.addSeparator()
        
        # Copy actions
        copy_transcription_action = QAction("Copy Transcription", self)
        copy_transcription_action.triggered.connect(self.copy_transcription)
        self.toolbar.addAction(copy_transcription_action)
        
        copy_llm_action = QAction("Copy LLM Output", self)
        copy_llm_action.triggered.connect(self.copy_llm)
        self.toolbar.addAction(copy_llm_action)
        
        self.toolbar.addSeparator()
        
        # Exit action
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.quit_application)
        self.toolbar.addAction(exit_action)
    
    def connect_controller_signals(self):
        """
        Connect signals from the controller to the view slots.
        """
        # Recording signals
        self.controller.recording_started.connect(self.on_recording_started)
        self.controller.recording_stopped.connect(self.on_recording_stopped)
        
        # Processing signals
        self.controller.processing_started.connect(self.on_processing_started)
        self.controller.processing_complete.connect(self.on_processing_complete)
        self.controller.processing_cancelled.connect(self.on_processing_cancelled)
        self.controller.processing_state_changed.connect(self.on_processing_state_changed)
        
        # Status update signal
        self.controller.status_update.connect(self.update_status)
        
        # Instruction set activation signal
        self.controller.instruction_set_activated.connect(self.on_instruction_set_activated)
        
        # Hotkey triggered signal
        self.controller.hotkey_triggered.connect(self.on_hotkey_triggered)
    
    def populate_instruction_set_combo(self):
        """
        Populate the instruction set combo box with available instruction sets.
        """
        self.instruction_set_combo.blockSignals(True)
        self.instruction_set_combo.clear()
        
        # Add all instruction sets
        for instruction_set in self.controller.get_instruction_sets():
            self.instruction_set_combo.addItem(instruction_set.name)
            
            # Add tooltip with hotkey if available
            if instruction_set.hotkey:
                self.instruction_set_combo.setItemData(
                    self.instruction_set_combo.count() - 1,
                    f"Hotkey: {instruction_set.hotkey}",
                    Qt.ItemDataRole.ToolTipRole
                )
        
        # Select the currently selected instruction set
        selected_set = self.controller.get_selected_instruction_set()
        if selected_set:
            index = self.instruction_set_combo.findText(selected_set.name)
            if index >= 0:
                self.instruction_set_combo.setCurrentIndex(index)
        
        self.instruction_set_combo.blockSignals(False)
    
    def register_instruction_set_hotkeys(self):
        """
        Register hotkeys for all instruction sets.
        """
        for instruction_set in self.controller.get_instruction_sets():
            if instruction_set.hotkey:
                handler_id = f"instruction_set_{instruction_set.name}"
                self.controller.register_hotkey(instruction_set.hotkey, handler_id)
    
    def show_api_key_dialog(self):
        """
        Show dialog for API key entry.
        
        This method uses the API key controller to show a user-friendly dialog
        for entering and validating an API key.
        """
        # Use the controller's API key settings method
        if self.controller.show_api_key_settings(self):
            # Update the stored API key
            self.api_key = self.settings.value("api_key", "")
        else:
            # If initializing with a new API key failed
            if not self.api_key:
                # If we still don't have an API key, show a message
                QMessageBox.critical(
                    self, "API Key Required", 
                    "A valid API key is required to use this application."
                )
    
    @pyqtSlot()
    def on_record_button_click(self):
        """
        Handle the record button click event.
        """
        self.controller.toggle_recording()
    
    @pyqtSlot()
    def on_recording_started(self):
        """
        Handle the recording started event.
        """
        self.record_button.setText("Stop Recording")
        self.status_indicator.setText("Recording...")
        
        # Update system tray recording status
        self.system_tray.update_recording_status(True)
        
        # Play recording start sound
        self.audio_manager.play_start_recording()
    
    @pyqtSlot()
    def on_recording_stopped(self):
        """
        Handle the recording stopped event.
        """
        # Don't update button text here since we might be going into processing state
        self.status_indicator.setText("Processing...")
        
        # Update system tray recording status
        self.system_tray.update_recording_status(False)
        
        # Play recording stop sound
        self.audio_manager.play_stop_recording()
    
    @pyqtSlot()
    def on_processing_started(self):
        """
        Handle the processing started event.
        """
        self.record_button.setText("Cancel Processing")
        self.status_indicator.setText("Processing...")
        # Disable instruction set selection during processing
        self.instruction_set_combo.setEnabled(False)
    
    @pyqtSlot(bool)
    def on_processing_state_changed(self, is_processing: bool):
        """
        Handle changes in processing state.
        
        Parameters
        ----------
        is_processing : bool
            Whether processing is currently active
        """
        if is_processing:
            # Processing started
            self.record_button.setText("Cancel Processing")
            self.status_indicator.setText("Processing...")
            # Disable instruction set selection during processing
            self.instruction_set_combo.setEnabled(False)
        else:
            # Processing stopped
            self.record_button.setText("Start Recording")
            self.status_indicator.setText("Ready")
            # Re-enable instruction set selection
            self.instruction_set_combo.setEnabled(True)
    
    @pyqtSlot()
    def on_processing_cancelled(self):
        """
        Handle processing cancelled event.
        """
        self.record_button.setText("Start Recording")
        self.status_indicator.setText("Cancelled")
        # Re-enable instruction set selection
        self.instruction_set_combo.setEnabled(True)

        # Play cancel processing sound
        self.audio_manager.play_cancel_processing()
    
    @pyqtSlot(PipelineResult)
    def on_processing_complete(self, result: PipelineResult):
        """
        Handle the processing complete event.
        
        Parameters
        ----------
        result : PipelineResult
            The result of the processing
        """
        # Update the transcription text
        self.transcription_text.setText(result.transcription)
        
        # Update the LLM text if LLM was processed
        if result.llm_processed and result.llm_response:
            self.llm_text.setText(result.llm_response)
            self.tab_widget.setCurrentIndex(1)  # Switch to LLM tab
        else:
            self.llm_text.clear()
            self.tab_widget.setCurrentIndex(0)  # Switch to transcription tab
        
        # Reset button state and status indicator
        self.record_button.setText("Start Recording")
        self.status_indicator.setText("Ready")
        # Re-enable instruction set selection
        self.instruction_set_combo.setEnabled(True)
        
        # Play completion sound
        self.audio_manager.play_complete_processing()
    
    @pyqtSlot(str, int)
    def update_status(self, message: str, timeout: int = 0):
        """
        Update the status bar message.
        
        Parameters
        ----------
        message : str
            The message to display
        timeout : int, optional
            Timeout in milliseconds, 0 means no timeout, by default 0
        """
        self.status_bar.showMessage(message, timeout)
    
    @pyqtSlot(InstructionSet)
    def on_instruction_set_activated(self, instruction_set: InstructionSet):
        """
        Handle instruction set activation.
        
        Parameters
        ----------
        instruction_set : InstructionSet
            The activated instruction set
        """
        # Update the combo box
        self.instruction_set_combo.blockSignals(True)
        index = self.instruction_set_combo.findText(instruction_set.name)
        if index >= 0:
            self.instruction_set_combo.setCurrentIndex(index)
        self.instruction_set_combo.blockSignals(False)
        
        # Show status message
        self.status_bar.showMessage(f"Instruction set activated: {instruction_set.name}", 3000)
    
    @pyqtSlot(str)
    def on_hotkey_triggered(self, hotkey: str):
        """
        Handle hotkey trigger event.
        
        Parameters
        ----------
        hotkey : str
            The hotkey that was triggered
        """
        # The controller will handle the actual logic, this is for UI feedback
        self.status_bar.showMessage(f"Hotkey triggered: {hotkey}", 2000)
    
    @pyqtSlot(int)
    def on_instruction_set_changed(self, index: int):
        """
        Handle instruction set selection change.
        
        Parameters
        ----------
        index : int
            The index of the selected item
        """
        if index < 0:
            return
            
        # Get the selected instruction set name
        name = self.instruction_set_combo.itemText(index)
        
        # Set the selected instruction set
        self.controller.select_instruction_set(name)
    
    def copy_transcription(self):
        """
        Copy the transcription text to the clipboard.
        """
        ClipboardUtils.set_text(self.transcription_text.toPlainText())
        self.status_bar.showMessage("Transcription copied to clipboard", 2000)
    
    def copy_llm(self):
        """
        Copy the LLM output text to the clipboard.
        """
        ClipboardUtils.set_text(self.llm_text.toPlainText())
        self.status_bar.showMessage("LLM output copied to clipboard", 2000)

    def show_instruction_sets_dialog(self):
        """
        Show the instruction sets management dialog.
        
        This method creates and shows the instruction sets dialog,
        using the controller to create the dialog.
        """
        # Create dialog using controller
        dialog = self.controller.create_instruction_dialog(self)
        
        # Show the dialog
        dialog.exec()
        
        # After dialog is closed, refresh instruction sets combo
        self.populate_instruction_set_combo()
        
        # Show status message
        self.status_bar.showMessage("Instruction sets updated", 2000)
    
    @pyqtSlot()
    def show_window(self):
        """
        Show and activate the application window.
        """
        self.showNormal()
        self.activateWindow()
    
    @pyqtSlot()
    def hide_window(self):
        """
        Hide the application window.
        """
        self.hide()
    
    def quit_application(self):
        """
        Completely exit the application.
        """
        reply = QMessageBox.question(
            self, 
            'Quit Application',
            'Are you sure you want to quit the application?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Set closing flag
            self._is_closing = True
            
            # Hide the system tray icon
            if hasattr(self, 'system_tray'):
                self.system_tray.hide()
            
            # Shut down the controller cleanly
            self.controller.shutdown()
            
            # Exit application
            sys.exit(0)
    
    def closeEvent(self, event: QCloseEvent):
        """
        Handle window close event.
        
        Parameters
        ----------
        event : QCloseEvent
            The close event
        """
        # If not actually closing (just minimizing to tray)
        if not self._is_closing:
            event.ignore()
            self.hide_window()
            
            # Show a notification message
            self.system_tray.showMessage(
                "Super Whisper App",
                "The application is still running in the background. "
                "Click the tray icon to restore.",
                QSystemTrayIcon.MessageIcon.Information,
                3000
            )
        else:
            # Actually closing
            event.accept()
