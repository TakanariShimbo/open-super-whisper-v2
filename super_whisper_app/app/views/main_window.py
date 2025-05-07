"""
Main Window Module

This module provides the MainWindow class, which is the main view component
of the application's user interface. It implements the main window with
all its controls, displays, and interaction elements.
"""

import os
import sys
from typing import Optional

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QFormLayout,
    QPushButton, QLabel, QProgressBar, QTextEdit, QMessageBox, QComboBox,
    QTabWidget, QToolBar, QDialog, QApplication, QStyle, QDialogButtonBox, 
    QLineEdit, QInputDialog, QStatusBar, QSystemTrayIcon
)
from PyQt6.QtCore import Qt, pyqtSlot, QSettings, QSize, QCoreApplication
from PyQt6.QtGui import QIcon, QAction, QCloseEvent

from super_whisper_app.app.controllers.app_controller import AppController
from super_whisper_app.app.views.tray.system_tray import SystemTray
from core.pipelines.pipeline_result import PipelineResult


class APIKeyDialog(QDialog):
    """
    Dialog for entering an API key.
    
    This dialog provides a simple form for the user to enter an API key
    and save it to the application settings.
    """
    
    def __init__(self, parent=None, current_key=None):
        """
        Initialize the APIKeyDialog.
        
        Parameters
        ----------
        parent : QWidget, optional
            Parent widget, by default None
        current_key : str, optional
            Current API key, by default None
        """
        super().__init__(parent)
        
        # Store current key
        self._current_key = current_key if current_key else ""
        
        # Setup UI
        self._init_ui()
    
    def _init_ui(self):
        """
        Initialize the user interface.
        """
        # Set window properties
        self.setWindowTitle("API Key")
        self.setMinimumWidth(400)
        
        # Create layout
        layout = QVBoxLayout(self)
        
        # Add info label
        info_label = QLabel("Enter your API key:")
        layout.addWidget(info_label)
        
        # Add API key input
        self.api_key_input = QLineEdit()
        self.api_key_input.setText(self._current_key)
        layout.addWidget(self.api_key_input)
        
        # Add button box
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def get_api_key(self):
        """
        Get the entered API key.
        
        Returns
        -------
        str
            The API key entered by the user
        """
        return self.api_key_input.text().strip()


class MainWindow(QMainWindow):
    """
    Main application window.
    
    This class implements the main window of the application, including
    the user interface elements, controls, and interaction with the controller.
    """
    
    def __init__(self):
        """
        Initialize the MainWindow.
        
        Sets up the user interface and connects signals/slots.
        """
        super().__init__()
        
        # Initialize settings
        self._settings = QSettings(
            QCoreApplication.organizationName(),
            QCoreApplication.applicationName()
        )
        
        # Initialize controller
        self._controller = AppController(self._settings)
        
        # Set up UI
        self._setup_ui()
        
        # Connect controller signals
        self._connect_controller_signals()
        
        # Set up system tray
        self._setup_system_tray()
        
        # Flag to track if application is closing
        self._is_closing = False
        
        # Check if API key is set
        if not self._controller.get_api_key():
            # Show API key dialog
            self._show_api_key_dialog()
    
    def _setup_ui(self):
        """
        Set up the user interface.
        
        This method initializes all UI components, including the window size,
        layout, controls, and status indicators.
        """
        # Set window properties
        self.setWindowTitle("Super Whisper App")
        self.setMinimumSize(800, 600)
        
        # Set window icon
        icon_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
            "assets", "icon.png"
        )
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        else:
            # Use standard icon if icon file not found
            self.setWindowIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Create toolbar
        self._create_toolbar()
        
        # Create control panel
        control_panel = QWidget()
        control_layout = QGridLayout(control_panel)
        
        # Add recording button
        self._record_button = QPushButton("Start Recording")
        self._record_button.setMinimumHeight(50)
        self._record_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._record_button.clicked.connect(self._handle_record_button)
        control_layout.addWidget(self._record_button, 0, 0, 2, 1)
        
        # Create form for settings
        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)
        
        # Add instruction set selector
        self._instruction_sets_label = QLabel("Instruction Set:")
        self._instruction_sets_combo = QComboBox()
        self._instruction_sets_combo.setMinimumWidth(200)
        self._instruction_sets_combo.currentIndexChanged.connect(self._handle_instruction_set_changed)
        form_layout.addRow(self._instruction_sets_label, self._instruction_sets_combo)
        
        # Add form to control layout
        control_layout.addWidget(form_widget, 0, 1, 2, 5)
        
        # Set column stretching
        control_layout.setColumnStretch(0, 1)  # Recording button column
        control_layout.setColumnStretch(1, 3)  # Form column
        
        # Add control panel to main layout
        main_layout.addWidget(control_panel)
        
        # Create tab widget for output
        self._tab_widget = QTabWidget()
        
        # Transcription tab
        transcription_tab = QWidget()
        transcription_layout = QVBoxLayout(transcription_tab)
        
        transcription_label = QLabel("Transcription Output:")
        transcription_layout.addWidget(transcription_label)
        
        self._transcription_text = QTextEdit()
        self._transcription_text.setPlaceholderText("Transcription will appear here...")
        self._transcription_text.setReadOnly(False)  # Allow editing
        self._transcription_text.setMinimumHeight(250)
        transcription_layout.addWidget(self._transcription_text)
        
        # LLM output tab
        llm_tab = QWidget()
        llm_layout = QVBoxLayout(llm_tab)
        
        llm_label = QLabel("LLM Output:")
        llm_layout.addWidget(llm_label)
        
        self._llm_text = QTextEdit()
        self._llm_text.setPlaceholderText("LLM analysis will appear here...")
        self._llm_text.setReadOnly(False)  # Allow editing
        self._llm_text.setMinimumHeight(250)
        llm_layout.addWidget(self._llm_text)
        
        # Add tabs to tab widget
        self._tab_widget.addTab(transcription_tab, "Transcription")
        self._tab_widget.addTab(llm_tab, "LLM Analysis")
        
        # Add tab widget to main layout
        main_layout.addWidget(self._tab_widget, 1)
        
        # Set up status bar
        self._status_bar = QStatusBar()
        self.setStatusBar(self._status_bar)
        
        # Add recording indicator to status bar
        self._recording_indicator = QLabel("Not Recording")
        self._status_bar.addPermanentWidget(self._recording_indicator)
        
        # Add progress bar to status bar
        self._progress_bar = QProgressBar()
        self._progress_bar.setRange(0, 100)
        self._progress_bar.setValue(0)
        self._progress_bar.setMaximumWidth(150)
        self._status_bar.addPermanentWidget(self._progress_bar)
        
        # Set initial status
        self._status_bar.showMessage("Ready")
        
        # Populate instruction sets combo
        self._populate_instruction_sets_combo()
    
    def _create_toolbar(self):
        """
        Create the application toolbar.
        
        This method creates a toolbar with actions for API key settings,
        instruction set management, and application exit.
        """
        self._toolbar = QToolBar("Main Toolbar")
        self._toolbar.setMovable(False)
        self._toolbar.setFloatable(False)
        self._toolbar.setIconSize(QSize(24, 24))
        
        # API key settings
        api_action = QAction("API Key Settings", self)
        api_action.triggered.connect(self._show_api_key_dialog)
        self._toolbar.addAction(api_action)
        
        self._toolbar.addSeparator()
        
        # Instruction sets management
        instruction_sets_action = QAction("Manage Instruction Sets", self)
        instruction_sets_action.triggered.connect(self._show_instruction_sets_dialog)
        self._toolbar.addAction(instruction_sets_action)
        
        self._toolbar.addSeparator()
        
        # Copy to clipboard actions
        copy_transcription_action = QAction("Copy Transcription", self)
        copy_transcription_action.triggered.connect(self._copy_transcription_to_clipboard)
        self._toolbar.addAction(copy_transcription_action)
        
        copy_llm_action = QAction("Copy LLM Output", self)
        copy_llm_action.triggered.connect(self._copy_llm_to_clipboard)
        self._toolbar.addAction(copy_llm_action)
        
        self._toolbar.addSeparator()
        
        # Exit action
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self._quit_application)
        self._toolbar.addAction(exit_action)
        
        self.addToolBar(self._toolbar)
    
    def _setup_system_tray(self):
        """
        Set up the system tray icon.
        
        This method creates a system tray icon with a context menu and
        connects signals for showing/hiding the window and exiting the
        application.
        """
        # Get icon path
        icon_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
            "assets", "icon.png"
        )
        
        # Create system tray
        self._system_tray = SystemTray(icon_path)
        
        # Connect signals
        self._system_tray.show_window_signal.connect(self._show_window)
        self._system_tray.hide_window_signal.connect(self._hide_window)
        self._system_tray.quit_application_signal.connect(self._quit_application)
        self._system_tray.recording_signal.connect(self._handle_record_button)
        
        # Show tray icon
        self._system_tray.show()
    
    def _connect_controller_signals(self):
        """
        Connect signals from the controller to slots in the view.
        
        This method connects signals from the controller for handling
        task progress, results, and other events.
        """
        # Connect task signals
        self._controller.task_progress.connect(self._update_progress)
        self._controller.processing_result.connect(self._handle_processing_result)
        self._controller.stream_update.connect(self._handle_stream_update)
        self._controller.task_started.connect(self._handle_task_started)
        self._controller.task_finished.connect(self._handle_task_finished)
        
        # Connect instruction set signals
        self._controller.instruction_sets_changed.connect(self._populate_instruction_sets_combo)
        self._controller.selected_set_changed.connect(self._update_selected_instruction_set)
    
    def _populate_instruction_sets_combo(self):
        """
        Populate the instruction sets combo box.
        
        This method populates the instruction sets combo box with
        the available instruction sets from the controller.
        """
        # Block signals to prevent triggering the currentIndexChanged event
        self._instruction_sets_combo.blockSignals(True)
        
        # Clear existing items
        self._instruction_sets_combo.clear()
        
        # Get instruction sets from controller
        instruction_sets = self._controller.get_instruction_sets()
        
        # Add sets to combo box
        for instruction_set in instruction_sets:
            self._instruction_sets_combo.addItem(instruction_set.name)
        
        # Get selected set from controller
        selected_set = self._controller.get_selected_instruction_set()
        if selected_set:
            # Find index of selected set
            index = self._instruction_sets_combo.findText(selected_set.name)
            if index >= 0:
                self._instruction_sets_combo.setCurrentIndex(index)
        
        # Unblock signals
        self._instruction_sets_combo.blockSignals(False)
    
    def _update_selected_instruction_set(self, name):
        """
        Update the selected instruction set in the combo box.
        
        Parameters
        ----------
        name : str
            Name of the selected instruction set
        """
        # Find index of selected set
        index = self._instruction_sets_combo.findText(name)
        if index >= 0:
            # Block signals to prevent recursion
            self._instruction_sets_combo.blockSignals(True)
            self._instruction_sets_combo.setCurrentIndex(index)
            self._instruction_sets_combo.blockSignals(False)
    
    def _show_api_key_dialog(self):
        """
        Show the API key dialog.
        
        This method displays a dialog for entering and saving an API key.
        """
        # Get current API key
        current_key = self._controller.get_api_key()
        
        # Create dialog
        dialog = APIKeyDialog(self, current_key)
        
        # Show dialog and process result
        if dialog.exec():
            # Get API key from dialog
            api_key = dialog.get_api_key()
            
            # Set API key in controller
            if self._controller.set_api_key(api_key):
                self._status_bar.showMessage("API key saved", 3000)
            else:
                QMessageBox.warning(
                    self,
                    "API Key Error",
                    "Invalid API key. Please enter a valid API key."
                )
    
    def _show_instruction_sets_dialog(self):
        """
        Show the instruction sets management dialog.
        
        This method displays a dialog for managing instruction sets,
        including creating, editing, and deleting sets.
        """
        from super_whisper_app.app.views.dialogs.instruction_sets_dialog import InstructionSetsDialog
        
        dialog = InstructionSetsDialog(self, self._controller)
        dialog.exec()
    
    def _handle_record_button(self):
        """
        Handle the record button click.
        
        This method toggles recording start/stop when the record button is clicked.
        """
        # Toggle recording
        self._controller.toggle_recording()
    
    def _handle_instruction_set_changed(self, index):
        """
        Handle instruction set selection change.
        
        Parameters
        ----------
        index : int
            Index of the selected instruction set
        """
        if index >= 0:
            # Get selected set name
            set_name = self._instruction_sets_combo.itemText(index)
            
            # Set selected set in controller
            self._controller.set_selected_instruction_set(set_name)
    
    @pyqtSlot(int)
    def _update_progress(self, value):
        """
        Update the progress bar.
        
        Parameters
        ----------
        value : int
            Progress value (0-100)
        """
        self._progress_bar.setValue(value)
    
    @pyqtSlot(PipelineResult)
    def _handle_processing_result(self, result):
        """
        Handle processing result.
        
        Parameters
        ----------
        result : PipelineResult
            The processing result containing transcription and optional LLM response
        """
        # Update transcription text
        self._transcription_text.setText(result.transcription)
        
        # Update LLM text if available
        if result.llm_processed and result.llm_response:
            self._llm_text.setText(result.llm_response)
            
            # Switch to LLM tab
            self._tab_widget.setCurrentIndex(1)
        else:
            self._llm_text.clear()
            
            # Switch to transcription tab
            self._tab_widget.setCurrentIndex(0)
        
        # Update status
        self._status_bar.showMessage("Processing complete", 3000)
    
    @pyqtSlot(str)
    def _handle_stream_update(self, chunk):
        """
        Handle streaming update from LLM.
        
        Parameters
        ----------
        chunk : str
            Text chunk from streaming response
        """
        # Get current text
        current_text = self._llm_text.toPlainText()
        
        # Append new chunk
        new_text = current_text + chunk
        self._llm_text.setText(new_text)
        
        # Move cursor to end
        cursor = self._llm_text.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self._llm_text.setTextCursor(cursor)
    
    @pyqtSlot()
    def _handle_task_started(self):
        """
        Handle task start event.
        
        This method updates the UI to reflect that a task is in progress.
        """
        # Update recording button text
        self._record_button.setText("Stop Recording")
        
        # Update recording indicator
        self._recording_indicator.setText("Recording")
        
        # Update status
        self._status_bar.showMessage("Recording in progress...")
        
        # Update system tray
        self._system_tray.update_recording_state(True)
    
    @pyqtSlot()
    def _handle_task_finished(self):
        """
        Handle task completion event.
        
        This method updates the UI to reflect that a task is complete.
        """
        # Update recording button text
        self._record_button.setText("Start Recording")
        
        # Update recording indicator
        self._recording_indicator.setText("Not Recording")
        
        # Update status
        self._status_bar.showMessage("Processing in progress...")
        
        # Update system tray
        self._system_tray.update_recording_state(False)
    
    def _copy_transcription_to_clipboard(self):
        """
        Copy transcription text to clipboard.
        """
        QApplication.clipboard().setText(self._transcription_text.toPlainText())
        self._status_bar.showMessage("Transcription copied to clipboard", 2000)
    
    def _copy_llm_to_clipboard(self):
        """
        Copy LLM output text to clipboard.
        """
        QApplication.clipboard().setText(self._llm_text.toPlainText())
        self._status_bar.showMessage("LLM output copied to clipboard", 2000)
    
    def _show_window(self):
        """
        Show and activate the window.
        """
        self.showNormal()
        self.activateWindow()
    
    def _hide_window(self):
        """
        Hide the window.
        """
        self.hide()
    
    def _quit_application(self):
        """
        Quit the application.
        
        This method shows a confirmation dialog and quits the application
        if confirmed.
        """
        reply = QMessageBox.question(
            self,
            "Exit Confirmation",
            "Are you sure you want to exit?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Set closing flag
            self._is_closing = True
            
            # Clean up resources
            self._controller.cleanup()
            
            # Hide tray icon
            self._system_tray.hide()
            
            # Exit application
            QApplication.quit()
    
    def closeEvent(self, event: QCloseEvent):
        """
        Handle window close event.
        
        Parameters
        ----------
        event : QCloseEvent
            The close event
        """
        if not self._is_closing:
            # Minimize to tray instead of closing
            event.ignore()
            self._hide_window()
            
            # Show notification
            self._system_tray.showMessage(
                "Super Whisper App",
                "Application is still running in the system tray.",
                QSystemTrayIcon.MessageIcon.Information,
                2000
            )
        else:
            # Actually close the window
            event.accept()
